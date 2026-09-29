from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import hashlib
from html.parser import HTMLParser
import json
import os
import re
import sys
import tempfile
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.canonical_frame import FramePayload, MenuItem, render_canonical_frame
from scripts.content_rules import validate_content
from scripts.theme_colors import DEFAULT_THEME_COLOR, theme_color_css, theme_color_ids
from scripts.validate_contracts import validate_contracts

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TAG = re.compile(r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.I | re.S)
STYLE_TAG = re.compile(r"<style\b[^>]*>(?P<body>.*?)</style>", re.I | re.S)
FRAME_TAG = re.compile(r"<nhimc-frame\b(?P<attrs>[^>]*)>(?P<body>.*?)</nhimc-frame\s*>", re.I | re.S)
ATTRIBUTE = r"\b{name}\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\"'=<>`]+))"
COLOR = re.compile(r"#[0-9a-f]{3,8}\b|(?:rgb|rgba|hsl|hsla)\(\s*[^)]*\)", re.I)
ASSET_REFERENCE = re.compile(r"['\"]([^'\"]+\.(?:svg|woff2?|ttf|otf)(?:#[^'\"]*)?)['\"]", re.I)
COMPLETION_TAG = re.compile(
    r'<script\b(?=[^>]*\bid\s*=\s*["\']nhimc-completion-manifest["\'])'
    r'(?=[^>]*\btype\s*=\s*["\']application/json["\'])[^>]*>(?P<body>.*?)</script\s*>',
    re.I | re.S,
)


@dataclass(frozen=True)
class AuthoringScreen:
    screen_id: str
    content_html: str


def _attribute(tag: str, name: str) -> str | None:
    match = re.search(ATTRIBUTE.format(name=re.escape(name)), tag, re.I | re.S)
    return next((value for value in match.groups() if value is not None), "") if match else None


class _HtmlInventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag.lower(), {key.lower(): value for key, value in attrs}))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def _inventory(html: str) -> _HtmlInventory:
    parser = _HtmlInventory()
    parser.feed(html)
    return parser


def _data_url(payload: bytes, media_type: str) -> str:
    return f"data:{media_type};base64,{base64.b64encode(payload).decode('ascii')}"


def _upstream(root: Path) -> tuple[dict, dict[str, str]]:
    manifest = json.loads((root / "vendor/nhimc-design/upstream.json").read_text(encoding="utf-8"))
    return manifest, {item["destination"]: item["sha256"] for item in manifest["files"]}


def _verified_vendor_bytes(root: Path, relative: str, digests: dict[str, str]) -> bytes:
    expected = digests.get(relative)
    if not expected:
        raise ValueError(f"canonical asset is not pinned: {relative}")
    payload = (root / relative).read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError(f"canonical asset digest mismatch: {relative}")
    return payload


def _font_css(root: Path, digests: dict[str, str], base_url: str | None = None) -> str:
    latin_range = (
        "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, "
        "U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, "
        "U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
    )
    faces = []
    for weight in (300, 400, 700):
        for subset in ("latin", "korean"):
            relative = f"vendor/nhimc-design/fonts/noto-sans-kr-{subset}-{weight}.woff2"
            payload = _verified_vendor_bytes(root, relative, digests)
            # Offline artifacts embed the font; the Web Runtime references the same verified file by URL.
            source = _data_url(payload, "font/woff2") if base_url is None else f"{base_url}/{Path(relative).name}"
            range_rule = f"\n  unicode-range: {latin_range};" if subset == "latin" else ""
            faces.append(
                "@font-face {\n"
                '  font-family: "Noto Sans KR";\n'
                "  font-style: normal;\n"
                f"  font-weight: {weight};\n"
                "  font-display: swap;\n"
                f'  src: url("{source}") format("woff2");{range_rule}\n'
                "}"
            )
    return "\n\n".join(faces)


def _strip_core_imports(script: str) -> str:
    if re.search(r"(^|[;\n])\s*import\s", script):
        raise ValueError("business script cannot import runtime sidecars")
    forbidden = {
        "dynamic import": r"\bimport\s*\(",
        "network request": r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(",
        "beacon request": r"\bnavigator\s*\.\s*sendBeacon\s*\(",
        "worker resource": r"\b(?:Worker|SharedWorker)\s*\(",
        "service worker": r"\bserviceWorker\s*\.\s*register\s*\(",
    }
    for label, pattern in forbidden.items():
        if re.search(pattern, script, re.I):
            raise ValueError(f"business script contains a forbidden {label}")
    return script.strip()


def _validate_business_input(root: Path, source: Path, html: str) -> None:
    if COMPLETION_TAG.search(html):
        raise ValueError("source already contains a completed artifact manifest")
    if re.search(r"data-nhimc-core\s*=|name\s*=\s*['\"]nhimc-core-version", html, re.I):
        raise ValueError("source already contains an embedded NHIMC Core")
    if STYLE_TAG.search(html):
        raise ValueError("business HTML cannot contain authored style blocks")
    if re.search(r"(?:\.style\.|style\.setProperty|insertRule|adoptedStyleSheets|\.shadowRoot)", html, re.I):
        raise ValueError("business HTML cannot inject or override protected styles")
    if COLOR.search(html):
        raise ValueError("business HTML cannot hard-code color values")
    if re.search(r"\bdata-nhimc-standalone-ready\b", html, re.I):
        raise ValueError("business HTML cannot use the reserved standalone marker")

    inventory = _inventory(html)
    if sum(tag == "nhimc-frame" for tag, _ in inventory.tags) != 1:
        raise ValueError("business HTML must contain exactly one shared nhimc-frame")
    protected = {"frame-shell", "sidebar", "brand", "navigation", "collapse", "workspace", "header", "mobile-brand", "product-name", "statusbar", "mobile-dialog", "mobile-panel", "mobile-head"}
    for tag, attrs in inventory.tags:
        copied = protected & set((attrs.get("class") or "").split())
        if copied:
            raise ValueError(f"business HTML copies protected frame chrome: {sorted(copied)[0]}")
        if tag == "script":
            script_type = (attrs.get("type") or "").lower()
            is_menu = script_type == "application/json" and "data-nhimc-menu" in attrs
            if script_type != "module" and "data-nhimc-business" not in attrs and not is_menu:
                raise ValueError("business HTML cannot contain classic or unowned scripts")
        if tag == "meta" and (attrs.get("http-equiv") or "").lower() == "refresh":
            raise ValueError("business HTML cannot contain meta refresh")
        if tag == "link" and "stylesheet" in (attrs.get("rel") or "").lower():
            raise ValueError("business HTML cannot load stylesheets")
        if tag == "a" and (href := attrs.get("href")) and not href.startswith("#"):
            raise ValueError(f"business HTML contains a non-offline link: {href}")

    assets = json.loads((root / "registry/assets.json").read_text(encoding="utf-8"))["assets"]
    registered = {(root / item["path"]).resolve() for item in assets}
    for match in ASSET_REFERENCE.finditer(html):
        value = match.group(1)
        if value.startswith("data:"):
            continue
        asset_path = value.split("#", 1)[0].replace("\\", "/")
        resolved = (source.parent / asset_path).resolve()
        registered_candidate = (root / re.sub(r"^(?:\.\./)+", "", asset_path)).resolve()
        if resolved not in registered and registered_candidate not in registered:
            raise ValueError(f"business HTML references an unregistered asset: {value}")


def _extract_scripts(html: str) -> tuple[str, list[dict], str]:
    menu_payloads: list[list[dict]] = []
    business: list[str] = []

    def replace(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        script_type = (_attribute(attrs, "type") or "").lower()
        if script_type == "application/json" and re.search(r"\bdata-nhimc-menu\b", attrs, re.I):
            try:
                parsed = json.loads(match.group("body"))
            except json.JSONDecodeError as error:
                raise ValueError("navigation manifest is not valid JSON") from error
            if not isinstance(parsed, list):
                raise ValueError("navigation manifest must be a JSON array")
            menu_payloads.append(parsed)
            return ""
        if script_type == "module" or re.search(r"\bdata-nhimc-business\b", attrs, re.I):
            if _attribute(attrs, "src"):
                raise ValueError("business scripts must be inline in canonical authoring input")
            business.append(match.group("body"))
            return ""
        return match.group(0)

    stripped = SCRIPT_TAG.sub(replace, html)
    if len(menu_payloads) != 1:
        raise ValueError("business HTML must contain exactly one data-nhimc-menu manifest")
    return stripped, menu_payloads[0], _strip_core_imports("\n".join(business))


def _menu_items(raw: list[dict]) -> tuple[MenuItem, ...]:
    def convert(item: object) -> MenuItem:
        if not isinstance(item, dict):
            raise ValueError("navigation items must be objects")
        try:
            item_id, label, icon, href = item["id"], item["label"], item["icon"], item["href"]
        except KeyError as error:
            raise ValueError(f"navigation item is missing {error.args[0]}") from error
        children = item.get("children", [])
        if not all(isinstance(value, str) for value in (item_id, label, icon, href)) or not isinstance(children, list):
            raise ValueError("navigation item fields have invalid types")
        return MenuItem(item_id, label, icon, href, tuple(convert(child) for child in children))

    return tuple(convert(item) for item in raw)


def _frame_kind(value: str) -> str:
    return {"nhimc-default": "left", "nhimc-left-blank": "left-blank"}.get(
        value, value.removeprefix("nhimc-")
    )


def _menu_ids(raw: list[dict]) -> list[str]:
    ids: list[str] = []

    def visit(items: list[dict]) -> None:
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                ids.append(item["id"])
                children = item.get("children", [])
                if isinstance(children, list):
                    visit(children)

    visit(raw)
    return ids


def _balanced_elements(html: str, tag: str, marker: str) -> list[tuple[str, str]]:
    token = re.compile(rf"</?{re.escape(tag)}\b[^>]*>", re.I | re.S)
    tokens = list(token.finditer(html))
    results: list[tuple[str, str]] = []
    for index, opening in enumerate(tokens):
        if opening.group(0).startswith("</") or _attribute(opening.group(0), marker) is None:
            continue
        depth = 1
        for closing in tokens[index + 1 :]:
            depth += -1 if closing.group(0).startswith("</") else 1
            if depth == 0:
                results.append(
                    (opening.group(0), html[opening.end() : closing.start()])
                )
                break
        else:
            raise ValueError(f"unbalanced authoring <{tag}> element")
    return results


def _content_roots(html: str) -> list[str]:
    roots: list[str] = []
    for opening, body in _balanced_elements(html, "main", "data-nhimc-role"):
        if _attribute(opening, "data-nhimc-role") == "content":
            roots.append(f"{opening}{body}</main>")
    return roots


def _authoring_menu(source_html: str) -> list[dict]:
    payloads = []
    for match in SCRIPT_TAG.finditer(source_html):
        attrs = match.group("attrs")
        if (_attribute(attrs, "type") or "").lower() == "application/json" and re.search(
            r"\bdata-nhimc-menu\b", attrs, re.I
        ):
            try:
                payloads.append(json.loads(match.group("body")))
            except json.JSONDecodeError as error:
                raise ValueError("navigation manifest is not valid JSON") from error
    if len(payloads) != 1 or not isinstance(payloads[0], list):
        raise ValueError("business HTML must contain exactly one data-nhimc-menu manifest")
    return payloads[0]


def parse_authoring_screens(
    source_html: str, root: Path = ROOT
) -> tuple[AuthoringScreen, ...]:
    frame = FRAME_TAG.search(source_html)
    if not frame:
        raise ValueError("business HTML must contain exactly one shared nhimc-frame")
    frame_id = _frame_kind(_attribute(frame.group("attrs"), "data-frame") or "left")
    menu_ids = _menu_ids(_authoring_menu(source_html))
    if not menu_ids or len(menu_ids) != len(set(menu_ids)):
        raise ValueError("navigation screen ids must be present and unique")

    panels = _balanced_elements(frame.group("body"), "section", "data-screen-panel")
    screens: list[AuthoringScreen] = []
    if panels:
        for opening, body in panels:
            screen_id = _attribute(opening, "data-screen-panel") or ""
            roots = _content_roots(body)
            if len(roots) != 1:
                raise ValueError(f"screen {screen_id} must contain exactly one content root")
            screens.append(AuthoringScreen(screen_id, roots[0]))
    else:
        roots = _content_roots(frame.group("body"))
        if len(roots) != 1:
            raise ValueError("single-screen authoring must contain exactly one content root")
        remainder = frame.group("body").replace(roots[0], "", 1)
        remainder = SCRIPT_TAG.sub("", remainder)
        if re.sub(r"<!--.*?-->", "", remainder, flags=re.S).strip():
            raise ValueError("single-screen authoring contains markup outside its content root")
        screens.append(AuthoringScreen(menu_ids[0], roots[0]))

    if [screen.screen_id for screen in screens] != menu_ids:
        raise ValueError("navigation and screen panel ids must have a 1:1 binding in manifest order")
    for screen in screens:
        validate_content(root, screen.content_html)
    return tuple(screens)


def inspect_completion_manifest(html: str) -> dict:
    matches = list(COMPLETION_TAG.finditer(html))
    if len(matches) != 1:
        raise ValueError("HTML is not a completed artifact")
    try:
        manifest = json.loads(matches[0].group("body"))
    except json.JSONDecodeError as error:
        raise ValueError("completion manifest is not valid JSON") from error
    required = {
        "artifactType",
        "schemaVersion",
        "coreVersion",
        "upstreamCommit",
        "frameId",
        "screens",
        "themeId",
        "bundleSha256",
        "runtimeSha256",
        "sidecarCount",
        "verificationRequired",
    }
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError("completion manifest has an invalid schema")
    if manifest["artifactType"] != "nhimc-single-html" or manifest["schemaVersion"] != 4:
        raise ValueError("completion manifest has an invalid artifact identity")
    if manifest["sidecarCount"] != 0 or manifest["verificationRequired"] is not True:
        raise ValueError("completion manifest does not require verified standalone delivery")
    if not isinstance(manifest["screens"], list) or not manifest["screens"]:
        raise ValueError("completion manifest has no screens")
    for digest in ("bundleSha256", "runtimeSha256"):
        if not isinstance(manifest[digest], str) or not re.fullmatch(r"[0-9a-f]{64}", manifest[digest]):
            raise ValueError(f"completion manifest has an invalid {digest}")
    return manifest


def _parse_authoring(
    html: str,
    raw_menu: list[dict],
    business_script: str,
    screens: tuple[AuthoringScreen, ...],
) -> tuple[str, FramePayload]:
    match = FRAME_TAG.search(html)
    if not match:
        raise ValueError("shared nhimc-frame contents could not be parsed")
    attrs = match.group("attrs")
    menu = _menu_items(raw_menu)
    if not menu:
        raise ValueError("navigation manifest cannot be empty")
    theme_match = re.search(r"<html\b[^>]*(?:data-theme|data-nhimc-theme)=[\"'](?:nhimc-)?(light|dark)[\"']", html, re.I)
    if len(screens) == 1:
        content_html = screens[0].content_html
    else:
        content_html = "".join(
            f'<section id="screen-{screen.screen_id}" data-screen-panel="{screen.screen_id}"'
            f'{"" if index == 0 else " hidden"}>{screen.content_html}</section>'
            for index, screen in enumerate(screens)
        )
    return (_attribute(attrs, "data-frame") or "left"), FramePayload(
        project_title=_attribute(attrs, "data-project-title") or "국민건강보험 일산병원",
        menu=menu,
        active_id=_attribute(attrs, "data-active-id") or menu[0].id,
        content_html=content_html,
        status_text="준비됨 · 오프라인 문서",
        theme=theme_match.group(1).lower() if theme_match else "light",
        business_script=business_script,
        scroll_owner=_attribute(attrs, "data-scroll-owner") or "main",
    )


def _component_controller(root: Path) -> str:
    script = (root / "src/generated/components/components.js").read_text(encoding="utf-8")
    script = script.replace("document.querySelector('[data-input-demo]').addEventListener", "document.querySelector('[data-input-demo]')?.addEventListener")
    return script.replace("document.querySelector('[data-select-demo]').addEventListener", "document.querySelector('[data-select-demo]')?.addEventListener")


def _runtime_business(root: Path, business_script: str, runtime_token: str) -> str:
    return f"""
const nhimcStandaloneErrors = [];
window.addEventListener('error', event => {{
  nhimcStandaloneErrors.push(String(event.message || event.error || 'runtime error'));
  document.documentElement.removeAttribute('data-nhimc-standalone-ready');
}});
window.addEventListener('unhandledrejection', event => {{
  nhimcStandaloneErrors.push(String(event.reason || 'unhandled rejection'));
  document.documentElement.removeAttribute('data-nhimc-standalone-ready');
}});
{_component_controller(root)}
{business_script}
window.addEventListener('load', () => setTimeout(() => {{
  const resources = performance.getEntriesByType('resource').map(entry => entry.name);
  const shell = document.querySelector('[data-nhimc-role="app-shell"]');
  if (nhimcStandaloneErrors.length || !shell || document.fonts.size < 6 ||
      resources.some(name => !name.startsWith('data:'))) return;
  document.documentElement.setAttribute('data-nhimc-standalone-ready', {json.dumps(runtime_token)});
}}, 500), {{ once: true }});
""".strip()


def _validate_standalone(html: str) -> None:
    if re.search(r"<html\b[^>]*\bdata-nhimc-standalone-ready\b", html, re.I):
        raise ValueError("standalone output contains a spoofed runtime marker")
    forbidden = {
        "authoring frame": r"<nhimc-frame\b",
        "external script": r"<script\b[^>]*\bsrc\s*=",
        "external stylesheet": r"<link\b[^>]*\brel\s*=\s*['\"][^'\"]*stylesheet",
        "module script": r"<script\b[^>]*\btype\s*=\s*['\"]module['\"]",
        "module URL": r"\bimport\.meta\b",
        "CSS import": r"@import\b",
        "Unicode hamburger substitute": "☰",
        "Unicode collapse substitute": "‹",
    }
    for label, pattern in forbidden.items():
        if re.search(pattern, html, re.I):
            raise ValueError(f"standalone output contains {label}")
    document_markup = SCRIPT_TAG.sub("", html)
    for style in STYLE_TAG.finditer(document_markup):
        for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", style.group("body"), re.I):
            value = match.group(2).strip()
            if not value.startswith(("data:", "#")):
                raise ValueError(f"standalone output contains an external CSS URL: {value}")
    for name, attrs in _inventory(document_markup).tags:
        if "srcset" in attrs:
            raise ValueError("standalone output cannot contain srcset")
        for attribute in ("src", "poster"):
            if (value := attrs.get(attribute)) is not None and not value.startswith("data:"):
                raise ValueError(f"standalone output contains external {attribute}: {value}")
        if name == "object" and (value := attrs.get("data")) and not value.startswith("data:"):
            raise ValueError(f"standalone output contains external object data: {value}")
        if name in {"form", "button", "input"}:
            for attribute in ("action", "formaction"):
                if attrs.get(attribute):
                    raise ValueError(f"standalone output contains external {attribute}: {attrs[attribute]}")
        if name == "base" and "href" in attrs:
            raise ValueError("standalone output cannot change its base URL")


def normalize_authoring(source_html: str) -> str:
    """Wrap a Content-only fragment (main[data-nhimc-role=content]) into a full authoring document.

    Web AI hosts cannot run the builder, so they hand over only the Content. The Frame,
    Font, Icon and Theme always come from the builder, never from the fragment.
    """
    if FRAME_TAG.search(source_html) or COMPLETION_TAG.search(source_html):
        return source_html
    panels = _balanced_elements(source_html, "section", "data-screen-panel")
    if panels:
        roots = ["".join(f"{opening}{body}</section>" for opening, body in panels)]
        heading_source = panels[0][1]
    else:
        roots = _content_roots(source_html)
        if len(roots) != 1:
            raise ValueError("fragment must contain exactly one content root")
        heading_source = roots[0]
    title_match = re.search(r"<title>(.*?)</title>", source_html, re.I | re.S)
    heading = re.search(r"<h1\b[^>]*>(.*?)</h1>", heading_source, re.I | re.S)
    raw_title = (title_match or heading).group(1) if (title_match or heading) else "NHIMC"
    title = re.sub(r"<[^>]+>|[<>&\"']", "", raw_title).strip() or "NHIMC"
    menu = None
    scripts: list[str] = []
    for match in SCRIPT_TAG.finditer(source_html):
        attrs = match.group("attrs")
        if (_attribute(attrs, "type") or "").lower() == "application/json" and re.search(r"\bdata-nhimc-menu\b", attrs, re.I):
            menu = match.group(0)
        else:
            scripts.append(match.group(0))
    if menu is None:
        menu = (
            '<script type="application/json" data-nhimc-menu>'
            + json.dumps([{"id": "main", "label": title, "icon": "hospital", "href": "#main"}], ensure_ascii=False)
            + "</script>"
        )
    menu_ids = _menu_ids(_authoring_menu(menu))
    html_tag = re.search(r"<html\b[^>]*>", source_html, re.I)
    html_attrs = html_tag.group(0) if html_tag else ""
    frame = re.sub(r"[^a-z0-9-]", "", (_attribute(html_attrs, "data-frame") or "left").lower()) or "left"
    theme = "dark" if (_attribute(html_attrs, "data-theme") or "").lower() == "dark" else "light"
    color = re.sub(r"[^a-z0-9-]", "", (_attribute(html_attrs, "data-theme-color") or "").lower())
    color_attr = f' data-theme-color="{color}"' if color else ""
    owner = re.sub(r"[^a-z]", "", (_attribute(html_attrs, "data-scroll-owner") or "").lower())
    owner_attr = f' data-scroll-owner="{owner}"' if owner else ""
    return (
        f'<!doctype html><html lang="ko" data-theme="{theme}"{color_attr}><head><meta charset="utf-8">'
        f"<title>{title}</title></head><body>"
        f'<nhimc-frame id="app-frame" data-frame="{frame}" data-project-title="{title}" data-active-id="{menu_ids[0]}"{owner_attr}>'
        f"{roots[0]}</nhimc-frame>{menu}{''.join(scripts)}</body></html>"
    )


def build_single_html(root: Path, source: Path, output: Path) -> Path:
    root, source, output = root.resolve(), source.resolve(), output.resolve()
    if validate_contracts(root):
        raise ValueError("Core contract validation failed before standalone bundling")
    source_html = normalize_authoring(source.read_text(encoding="utf-8"))
    _validate_business_input(root, source, source_html)
    screens = parse_authoring_screens(source_html, root)
    stripped, raw_menu, business_script = _extract_scripts(source_html)
    frame_id, payload = _parse_authoring(stripped, raw_menu, business_script, screens)

    upstream, digests = _upstream(root)
    layout_name = _frame_kind(frame_id)
    _verified_vendor_bytes(root, f"vendor/nhimc-design/layouts/{layout_name}.html", digests)
    _verified_vendor_bytes(root, "vendor/nhimc-design/icons/nhimc-icons.svg", digests)
    font_css = _font_css(root, digests)
    component_css = (root / "src/generated/components/components.css").read_text(encoding="utf-8")
    primitives_css = (root / "src/layouts/primitives.css").read_text(encoding="utf-8")
    theme_css = theme_color_css(root)
    layout_css = primitives_css + "\n" + theme_css + "\n"
    color_match = re.search(r"<html\b[^>]*\bdata-theme-color=[\"']([a-z0-9-]+)[\"']", stripped, re.I)
    theme_color = color_match.group(1) if color_match else DEFAULT_THEME_COLOR
    if theme_color not in theme_color_ids(root):
        raise ValueError(f"unknown theme color: {theme_color}; use one of {', '.join(theme_color_ids(root))}")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    semantic = "\0".join((version, upstream["commit"], frame_id, payload.content_html, json.dumps(raw_menu, ensure_ascii=False, sort_keys=True), business_script, component_css, font_css, layout_css))
    runtime_token = hashlib.sha256(semantic.encode("utf-8")).hexdigest()
    payload = FramePayload(**{**payload.__dict__, "business_script": _runtime_business(root, business_script, runtime_token)})
    html = render_canonical_frame(root, frame_id, payload)
    if theme_color != DEFAULT_THEME_COLOR:
        html = re.sub(r"(<html\b)", rf'\1 data-theme-color="{theme_color}"', html, count=1, flags=re.I)

    title_match = re.search(r"<title>(.*?)</title>", source_html, re.I | re.S)
    if title_match:
        title = re.sub(r"[<>&]", "", title_match.group(1)).strip()
        html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.I | re.S)
    bundle_hash = hashlib.sha256((component_css + font_css + layout_css).encode("utf-8")).hexdigest()
    runtime_hash = hashlib.sha256(payload.business_script.encode("utf-8")).hexdigest()
    completion = {
        "artifactType": "nhimc-single-html",
        "schemaVersion": 4,
        "coreVersion": version,
        "upstreamCommit": upstream["commit"],
        "frameId": frame_id,
        "screens": [
            {"screenId": screen.screen_id}
            for screen in screens
        ],
        "themeId": f"nhimc-{payload.theme}",
        "bundleSha256": bundle_hash,
        "runtimeSha256": runtime_hash,
        "sidecarCount": 0,
        "verificationRequired": True,
    }
    completion_json = json.dumps(
        completion, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).replace("</", "<\\/")
    policy = (
        "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
        "img-src data:; font-src data:; media-src data:; connect-src 'none'; "
        "object-src 'none'; frame-src 'none'; worker-src 'none'; base-uri 'none'; "
        "form-action 'none'"
    )
    head = (
        f'<meta http-equiv="Content-Security-Policy" content="{policy}">\n'
        f'<meta name="nhimc-core-version" content="{version}">\n'
        f'<meta name="nhimc-upstream-commit" content="{upstream["commit"][:12]}">\n'
        f'<meta name="nhimc-core-bundle-sha256" content="{bundle_hash}">\n'
        f'<meta name="nhimc-runtime-token" content="{runtime_token}">\n'
        f'<style data-nhimc-component-bundle="canonical">\n{component_css.replace("</style", "<\\/style")}\n</style>\n'
        f'<style data-nhimc-font-bundle="canonical">\n{font_css}\n</style>\n'
        f'<style data-nhimc-layout-bundle="primitives">\n{primitives_css.replace("</style", "<\\/style")}\n</style>\n'
        f'<script id="nhimc-completion-manifest" type="application/json">{completion_json}</script>'
    )
    html, count = re.subn(r"(<head\b[^>]*>)", lambda match: f"{match.group(1)}\n{head}", html, count=1, flags=re.I)
    if count != 1:
        raise ValueError("canonical frame is missing its head")
    # Theme colour overlays must come after the Frame's own [data-theme] token blocks. Both have the same
    # specificity, so the later one wins; at the head start the Frame's default colours overrode the theme.
    theme_block = f'<style data-nhimc-theme-color-bundle="canonical">\n{theme_css.replace("</style", "<\\/style")}\n</style>\n'
    html, count = re.subn(r"</head\s*>", lambda match: theme_block + match.group(0), html, count=1, flags=re.I)
    if count != 1:
        raise ValueError("canonical frame is missing its head end")
    _validate_standalone(html)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
        ) as temporary:
            temporary.write(html)
            temporary.flush()
            temporary_name = temporary.name
        exact_html = Path(temporary_name).read_text(encoding="utf-8")
        _validate_standalone(exact_html)
        inspect_completion_manifest(exact_html)
        os.replace(temporary_name, output)
        temporary_name = None
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one offline canonical NHIMC HTML artifact")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = build_single_html(ROOT, args.input, args.output)
    except (OSError, ValueError) as error:
        print(f"single HTML build failed: {error}", file=sys.stderr)
        return 1
    print(f"single HTML artifact: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
