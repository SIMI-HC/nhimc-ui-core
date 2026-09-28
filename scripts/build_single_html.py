import argparse
import base64
import hashlib
from html.parser import HTMLParser
import json
import re
import sys
from pathlib import Path


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validate_contracts import validate_contracts


ROOT = Path(__file__).resolve().parents[1]
CORE_STYLES = (
    "src/themes/nhimc-fonts.css",
    "src/themes/nhimc-light.css",
    "src/layouts/application.css",
    "src/layouts/primitives.css",
    "src/components/components.css",
)
LINK_TAG = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
SCRIPT_TAG = re.compile(r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.IGNORECASE | re.DOTALL)
STYLE_TAG = re.compile(r"<style\b[^>]*>(?P<body>.*?)</style>", re.IGNORECASE | re.DOTALL)
ATTRIBUTE = r"\b{name}\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\"'=<>`]+))"
COLOR = re.compile(r"#[0-9a-f]{3,8}\b|(?:rgb|rgba|hsl|hsla)\(\s*[^)]*\)", re.IGNORECASE)
ASSET_REFERENCE = re.compile(r"['\"]([^'\"]+\.(?:svg|woff2?|ttf|otf)(?:#[^'\"]*)?)['\"]", re.IGNORECASE)


def _attribute(tag: str, name: str) -> str | None:
    match = re.search(ATTRIBUTE.format(name=re.escape(name)), tag, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return next((value for value in match.groups() if value is not None), "")


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


def _data_url(path: Path, media_type: str) -> str:
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{payload}"


def _escape_style(text: str) -> str:
    return text.replace("</style", "<\\/style")


def _rewrite_font_urls(root: Path, css: str) -> str:
    def replace(match: re.Match[str]) -> str:
        name = Path(match.group(1)).name
        font = root / "src/assets/fonts" / name
        if not font.is_file():
            raise ValueError(f"font asset is missing: {name}")
        return f'url("{_data_url(font, "font/woff2")}")'

    rewritten = re.sub(r'url\(["\']?\.\./assets/fonts/([^"\')]+)["\']?\)', replace, css)
    if "../assets/fonts/" in rewritten:
        raise ValueError("font URL was not embedded")
    return rewritten


def _build_global_css(root: Path) -> str:
    chunks = []
    for relative in CORE_STYLES:
        text = (root / relative).read_text(encoding="utf-8")
        if relative.endswith("nhimc-fonts.css"):
            text = _rewrite_font_urls(root, text)
        chunks.append(f"/* {relative} */\n{text.strip()}")
    return "\n\n".join(chunks)


def _strip_core_imports(script: str) -> str:
    script = re.sub(
        r"^\s*import\s+['\"][^'\"]*src/frame/nhimc-frame\.js['\"]\s*;?\s*",
        "",
        script,
        flags=re.MULTILINE,
    )
    script = re.sub(
        r"\s*import\s*\{.*?\}\s*from\s*['\"][^'\"]*src/components/controllers\.js['\"]\s*;?",
        "",
        script,
        flags=re.DOTALL,
    )
    if re.search(r"(^|[;\n])\s*import\s", script):
        raise ValueError("business script contains an unsupported module import")
    forbidden_runtime = {
        "dynamic import": r"\bimport\s*\(",
        "network request": r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(",
        "beacon request": r"\bnavigator\s*\.\s*sendBeacon\s*\(",
        "worker resource": r"\b(?:Worker|SharedWorker)\s*\(",
        "service worker": r"\bserviceWorker\s*\.\s*register\s*\(",
    }
    for label, pattern in forbidden_runtime.items():
        if re.search(pattern, script, re.IGNORECASE):
            raise ValueError(f"business script contains a forbidden {label}")
    return script.strip()


def _validate_business_input(root: Path, source: Path, html: str) -> None:
    if re.search(r"data-nhimc-core\s*=|name\s*=\s*['\"]nhimc-core-version", html, re.IGNORECASE):
        raise ValueError("source already contains an embedded NHIMC Core")
    if STYLE_TAG.search(html) or re.search(r"\sstyle\s*=", html, re.IGNORECASE):
        raise ValueError("business HTML cannot contain local or inline styles")
    if re.search(
        r"(?:\.style\.|style\.setProperty|insertRule|adoptedStyleSheets|\.shadowRoot)",
        html,
        re.IGNORECASE,
    ):
        raise ValueError("business HTML cannot inject or override protected styles")
    if COLOR.search(html):
        raise ValueError("business HTML cannot hard-code color values")
    if re.search(r"\bdata-nhimc-standalone-ready\b", html, re.IGNORECASE):
        raise ValueError("business HTML cannot use the reserved standalone marker")

    inventory = _inventory(html)
    frames = [attrs for tag, attrs in inventory.tags if tag == "nhimc-frame"]
    if len(frames) != 1:
        raise ValueError("business HTML must contain exactly one shared nhimc-frame")
    protected_classes = {
        "frame-shell", "sidebar", "brand", "navigation", "collapse", "workspace",
        "header", "mobile-brand", "product-name", "statusbar", "mobile-dialog",
        "mobile-panel", "mobile-head",
    }
    for tag, attrs in inventory.tags:
        classes = set((attrs.get("class") or "").split())
        copied = protected_classes & classes
        if copied:
            raise ValueError(f"business HTML copies protected frame chrome: {sorted(copied)[0]}")
        if tag == "script":
            script_type = (attrs.get("type") or "").lower()
            if script_type != "module" and "data-nhimc-business" not in attrs:
                raise ValueError("business HTML cannot contain classic or unowned scripts")
        if tag == "meta" and (attrs.get("http-equiv") or "").lower() == "refresh":
            raise ValueError("business HTML cannot contain meta refresh")

    assets = json.loads((root / "registry/assets.json").read_text(encoding="utf-8"))["assets"]
    registered = {(root / item["path"]).resolve() for item in assets}
    for match in ASSET_REFERENCE.finditer(html):
        value = match.group(1)
        if value.startswith("data:"):
            continue
        asset_path = value.split("#", 1)[0].replace("\\", "/")
        resolved = (source.parent / asset_path).resolve()
        root_relative = re.sub(r"^(?:\.\./)+", "", asset_path)
        registered_candidate = (root / root_relative).resolve()
        if resolved not in registered and registered_candidate not in registered:
            raise ValueError(f"business HTML references an unregistered asset: {value}")


def _extract_business_script(source: Path, html: str) -> tuple[str, str]:
    scripts = []

    def replace(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        script_type = (_attribute(attrs, "type") or "").lower()
        src = _attribute(attrs, "src")
        if src:
            if script_type != "module":
                raise ValueError("external classic scripts cannot be bundled safely")
            script_path = (source.parent / src).resolve()
            if not script_path.is_file():
                raise ValueError(f"business script is missing: {src}")
            scripts.append(script_path.read_text(encoding="utf-8"))
            return ""
        if script_type == "module" or "data-nhimc-business" in attrs:
            scripts.append(match.group("body"))
            return ""
        return match.group(0)

    html = SCRIPT_TAG.sub(replace, html)
    return html, _strip_core_imports("\n".join(scripts))


def _build_core_script(root: Path, business_script: str, runtime_token: str) -> str:
    menu = (root / "src/frame/menu-model.js").read_text(encoding="utf-8")
    frame = (root / "src/frame/nhimc-frame.js").read_text(encoding="utf-8")
    controllers = (root / "src/components/controllers.js").read_text(encoding="utf-8")
    frame_css = (root / "src/frame/nhimc-frame.css").read_text(encoding="utf-8")
    logo = _data_url(root / "src/assets/branding/nhimc-logo.svg", "image/svg+xml")
    favicon = _data_url(root / "src/assets/branding/nhimc-favicon.svg", "image/svg+xml")

    menu = re.sub(r"\bexport\s+", "", menu)
    frame = re.sub(r"^import .*?;\s*", "", frame, count=1, flags=re.MULTILINE)
    frame = re.sub(r"\bexport\s+", "", frame)
    replacements = {
        "FRAME_STYLES": frame_css,
        "LOGO": logo,
        "FAVICON": favicon,
    }
    for name, value in replacements.items():
        frame, count = re.subn(
            rf"const {name} = .*?;",
            lambda _match, name=name, value=value: f"const {name} = {json.dumps(value)};",
            frame,
            count=1,
        )
        if count != 1:
            raise ValueError(f"frame bundle anchor is missing: {name}")
    frame, count = re.subn(
        r'<link rel="stylesheet" href="\$\{FRAME_STYLES\}">',
        r"<style>${FRAME_STYLES}</style>",
        frame,
        count=1,
    )
    if count != 1:
        raise ValueError("frame stylesheet template anchor is missing")
    controllers = re.sub(r"\bexport\s+", "", controllers)

    runtime_prelude = """
const nhimcStandaloneErrors = [];
window.addEventListener('error', (event) => {
  nhimcStandaloneErrors.push(String(event.message || event.error || 'runtime error'));
  document.documentElement.removeAttribute('data-nhimc-standalone-ready');
});
window.addEventListener('unhandledrejection', (event) => {
  nhimcStandaloneErrors.push(String(event.reason || 'unhandled rejection'));
  document.documentElement.removeAttribute('data-nhimc-standalone-ready');
});
"""
    runtime_check = f"""
window.addEventListener('load', () => setTimeout(() => {{
  const standaloneFrame = document.querySelector('nhimc-frame');
  const standaloneResources = performance.getEntriesByType('resource').map((entry) => entry.name);
  if (nhimcStandaloneErrors.length > 0 ||
      !standaloneFrame?.shadowRoot?.querySelector('style') ||
      standaloneResources.some((name) => !name.startsWith('data:'))) return;
  document.documentElement.setAttribute('data-nhimc-standalone-ready', {json.dumps(runtime_token)});
}}, 250), {{ once: true }});
"""
    bundle = "\n\n".join(
        (
            runtime_prelude.strip(),
            menu.strip(),
            frame.strip(),
            controllers.strip(),
            business_script,
            runtime_check.strip(),
        )
    )
    if re.search(r"(^|[;\n])\s*(?:import|export)\s", bundle):
        raise ValueError("module syntax remains in the standalone bundle")
    return f'(() => {{\n"use strict";\n{bundle}\n}})();'


def _remove_runtime_links(root: Path, html: str) -> tuple[str, str]:
    favicon = _data_url(root / "src/assets/branding/nhimc-favicon.svg", "image/svg+xml")
    allowed_style_names = {Path(item).name for item in CORE_STYLES}

    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        rel = (_attribute(tag, "rel") or "").lower()
        href = _attribute(tag, "href") or ""
        if "stylesheet" in rel:
            if Path(href).name not in allowed_style_names:
                raise ValueError(f"unregistered stylesheet cannot be bundled: {href}")
            return ""
        if "icon" in rel:
            return ""
        if href and not href.startswith(("#", "data:")):
            raise ValueError(f"external link resource cannot be bundled: {href}")
        return tag

    return LINK_TAG.sub(replace, html), favicon


def _embed_icon_sprite(root: Path, html: str) -> str:
    sprite = (root / "src/assets/icons/nhimc-icons.svg").read_text(encoding="utf-8")
    inner = re.sub(r"^\s*<svg\b[^>]*>|</svg>\s*$", "", sprite, flags=re.IGNORECASE)
    html = re.sub(r"(?:[^\"']*/)?nhimc-icons\.svg#", "#", html)
    hidden = f'<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" hidden>{inner}</svg>'
    return re.sub(r"(<body\b[^>]*>)", rf"\1\n  {hidden}", html, count=1, flags=re.IGNORECASE)


def _validate_standalone(html: str) -> None:
    if re.search(r"<html\b[^>]*\bdata-nhimc-standalone-ready\b", html, re.IGNORECASE):
        raise ValueError("standalone output contains a spoofed runtime marker")
    forbidden = {
        "external script": r"<script\b[^>]*\bsrc\s*=",
        "external stylesheet": r"<link\b[^>]*\brel\s*=\s*['\"][^'\"]*stylesheet",
        "module script": r"<script\b[^>]*\btype\s*=\s*['\"]module['\"]",
        "module URL": r"\bimport\.meta\b",
        "relative core path": r"\.\./\.\./src/",
        "CSS import": r"@import\b",
    }
    for label, pattern in forbidden.items():
        if re.search(pattern, html, re.IGNORECASE):
            raise ValueError(f"standalone output contains {label}")
    document_markup = SCRIPT_TAG.sub("", html)
    for style in STYLE_TAG.finditer(document_markup):
        for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", style.group("body"), re.IGNORECASE):
            value = match.group(2).strip()
            if not value.startswith(("data:", "#")):
                raise ValueError(f"standalone output contains an external CSS URL: {value}")
    for name, attrs in _inventory(document_markup).tags:
        if "srcset" in attrs:
            raise ValueError("standalone output cannot contain srcset")
        for attribute in ("src", "poster"):
            value = attrs.get(attribute)
            if value is not None and not value.startswith("data:"):
                raise ValueError(f"standalone output contains external {attribute}: {value}")
        if name == "object":
            value = attrs.get("data")
            if value is not None and not value.startswith("data:"):
                raise ValueError(f"standalone output contains external object data: {value}")
        if name in {"form", "button", "input"}:
            for attribute in ("action", "formaction"):
                value = attrs.get(attribute)
                if value:
                    raise ValueError(f"standalone output contains external {attribute}: {value}")
        if name == "base" and "href" in attrs:
            raise ValueError("standalone output cannot change its base URL")


def build_single_html(root: Path, source: Path, output: Path) -> Path:
    root = root.resolve()
    source = source.resolve()
    output = output.resolve()
    findings = validate_contracts(root)
    if findings:
        raise ValueError("Core contract validation failed before standalone bundling")

    html = source.read_text(encoding="utf-8")
    _validate_business_input(root, source, html)
    html, business_script = _extract_business_script(source, html)
    html, favicon = _remove_runtime_links(root, html)
    html = _embed_icon_sprite(root, html)
    css = _escape_style(_build_global_css(root))
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    runtime_token = hashlib.sha256(
        (version + "\0" + html + "\0" + css + "\0" + business_script).encode("utf-8")
    ).hexdigest()
    script = _build_core_script(root, business_script, runtime_token).replace(
        "</script", "<\\/script"
    )
    bundle_hash = hashlib.sha256((css + script).encode("utf-8")).hexdigest()
    head = (
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
        "script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; "
        "font-src data:; media-src data:; connect-src 'none'; object-src 'none'; "
        "frame-src 'none'; worker-src 'none'; base-uri 'none'; form-action 'none'\">\n"
        f'<meta name="nhimc-core-version" content="{version}">\n'
        f'<meta name="nhimc-core-bundle-sha256" content="{bundle_hash}">\n'
        f'<meta name="nhimc-runtime-token" content="{runtime_token}">\n'
        f'<link rel="icon" href="{favicon}" type="image/svg+xml">\n'
        f'<style data-nhimc-core="{version}">\n{css}\n</style>'
    )
    html, count = re.subn(
        r"(<head\b[^>]*>)",
        lambda match: f"{match.group(1)}\n{head}",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    if count != 1:
        raise ValueError("source HTML must contain <head>")
    html, count = re.subn(
        r"</body>",
        lambda _match: f'<script data-nhimc-core="{version}">\n{script}\n</script>\n</body>',
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    if count != 1:
        raise ValueError("source HTML must contain </body>")
    _validate_standalone(html)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8", newline="\n")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one offline NHIMC HTML artifact")
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
