from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import re

from scripts.frame_patches import apply_frame_patches


ID = re.compile(r"^[a-z][a-z0-9-]*$")
SAFE_FRAGMENT = re.compile(r"^#[a-z][a-z0-9-]*$")
ROLE_OPEN = re.compile(r'<(?P<tag>[a-z][a-z0-9]*)\b[^>]*\bdata-nhimc-role="(?P<role>[^"]+)"[^>]*>', re.IGNORECASE)
FRAME_FILES = {
    "nhimc-default": "left.html",
    "left": "left.html",
    "nhimc-left-blank": "left-blank.html",
    "left-blank": "left-blank.html",
    "nhimc-top": "top.html",
    "top": "top.html",
    "nhimc-top-left": "top-left.html",
    "top-left": "top-left.html",
    "nhimc-presentation": "presentation.html",
    "presentation": "presentation.html",
    "nhimc-presentation-vertical": "presentation-vertical.html",
    "presentation-vertical": "presentation-vertical.html",
    "nhimc-blog": "blog.html",
    "blog": "blog.html",
}


@dataclass(frozen=True)
class MenuItem:
    id: str
    label: str
    icon: str
    href: str
    children: tuple["MenuItem", ...] = ()


@dataclass(frozen=True)
class FramePayload:
    project_title: str
    menu: tuple[MenuItem, ...]
    active_id: str
    content_html: str
    status_text: str = "준비됨 · 오프라인 문서"
    status_state: str = "ready"
    theme: str = "light"
    business_script: str = ""


def _replace_role_contents(document: str, role: str, contents: str) -> str:
    matches = [match for match in ROLE_OPEN.finditer(document) if match.group("role") == role]
    if len(matches) != 1:
        raise ValueError(f"{role} anchor must occur exactly once")
    opening = matches[0]
    closing = re.search(rf"</{re.escape(opening.group('tag'))}\s*>", document[opening.end():], re.IGNORECASE)
    if not closing:
        raise ValueError(f"{role} anchor must have a closing tag")
    close_start = opening.end() + closing.start()
    return document[:opening.end()] + contents + document[close_start:]


def _icon_ids(sprite: str) -> set[str]:
    return set(re.findall(r'<symbol\s+id="([a-z0-9-]+)"', sprite))


def _validate_payload(payload: FramePayload, icon_ids: set[str]) -> None:
    if payload.theme not in {"light", "dark"}:
        raise ValueError("theme must be light or dark")
    if payload.status_state not in {"ready", "warning", "error", "processing"}:
        raise ValueError("invalid status state")
    if not ID.fullmatch(payload.active_id):
        raise ValueError("active_id must be a safe identifier")
    if re.search(r"<script\b", payload.content_html, re.IGNORECASE):
        raise ValueError("content_html cannot contain script elements")
    seen: set[str] = set()

    def visit(items: tuple[MenuItem, ...]) -> None:
        for item in items:
            if not ID.fullmatch(item.id) or item.id in seen:
                raise ValueError("menu id must be unique and safe")
            seen.add(item.id)
            if item.icon not in icon_ids:
                raise ValueError(f"unknown canonical icon: {item.icon}")
            if item.href != f"#{item.id}" or not SAFE_FRAGMENT.fullmatch(item.href):
                raise ValueError("menu href must be a safe fragment matching its id")
            visit(item.children)

    visit(payload.menu)
    if payload.active_id not in seen:
        raise ValueError("active_id must identify a menu item")


def _menu_items(items: tuple[MenuItem, ...], active_id: str, *, mode: str) -> str:
    rendered: list[str] = []
    for item in items:
        current = ' aria-current="page"' if item.id == active_id else ""
        icon = (
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'<use href="#{escape(item.icon, quote=True)}"></use></svg>'
        )
        label = escape(item.label)
        if mode == "side":
            rendered.append(
                f'<a class="nav-link" href="{escape(item.href, quote=True)}" data-menu-id="{item.id}" '
                f'data-screen-target="{item.id}"{current}><span class="nav-chip">{icon}</span>'
                f'<span class="nav-label">{label}</span></a>'
            )
        elif mode == "dots":
            rendered.append(
                f'<button type="button" data-menu-id="{item.id}" data-screen-target="{item.id}"'
                f'{current} aria-label="{label}"></button>'
            )
        else:
            rendered.append(
                f'<button type="button" data-menu-id="{item.id}" data-screen-target="{item.id}"{current}>'
                f'{icon}<span class="label">{label}</span></button>'
            )
        if item.children:
            rendered.append(_menu_items(item.children, active_id, mode=mode))
    return "".join(rendered)


def _replace_navigation(document: str, payload: FramePayload, frame_kind: str) -> str:
    mode = "dots" if frame_kind.startswith("presentation") else "side" if frame_kind in {"left", "left-blank", "top-left"} else "top"
    nav_pattern = re.compile(
        r'(<nav\b[^>]*data-nhimc-navigation-source="manifest"[^>]*data-navigation-view="(?P<view>desktop|mobile)"[^>]*>)(.*?)(</nav\s*>)',
        re.IGNORECASE | re.DOTALL,
    )
    matches = list(nav_pattern.finditer(document))
    if not matches:
        raise ValueError("navigation manifest anchor must occur at least once")

    def replacement(match: re.Match[str]) -> str:
        view = match.group("view").lower()
        items = _menu_items(payload.menu, payload.active_id, mode=mode if view == "desktop" else "top")
        if mode == "side" and view == "desktop":
            items = f'<div class="nav-list">{items}</div>'
        elif mode == "side":
            items = '<div class="nav-list"></div>'
        return match.group(1) + items + match.group(4)

    return nav_pattern.sub(replacement, document)


def _replace_project_title(document: str, title: str) -> str:
    safe = escape(title)
    patterns = [
        re.compile(r'(<strong\s+class="site-title">).*?(</strong>)', re.DOTALL),
        re.compile(r'(<button\s+class="brand-group"[^>]*>.*?<span>).*?(</span>)', re.DOTALL),
    ]
    for pattern in patterns:
        if pattern.search(document):
            return pattern.sub(lambda match: match.group(1) + safe + match.group(2), document, count=1)
    return document


def render_layout(
    layout: str,
    payload: FramePayload,
    *,
    icon_ids: set[str],
    sprite: str = "",
    runtime_js: str = "window.NhimcCanonicalFrame=Object.freeze({});",
    frame_kind: str = "left",
) -> str:
    _validate_payload(payload, icon_ids)
    rendered = re.sub(
        r'(<html\b[^>]*\bdata-theme=")[^"]+("[^>]*>)',
        lambda match: match.group(1) + payload.theme + match.group(2),
        layout,
        count=1,
    )
    rendered = _replace_role_contents(rendered, "content-slot", payload.content_html)
    rendered = _replace_project_title(rendered, payload.project_title)
    rendered = _replace_navigation(rendered, payload, frame_kind)
    if 'data-nhimc-role="statusbar"' in rendered:
        status = (
            '<span class="status-message"><span class="status-dot" '
            f'data-status="{payload.status_state}" aria-hidden="true"></span>'
            f'<span>{escape(payload.status_text)}</span></span>'
        )
        rendered = _replace_role_contents(rendered, "statusbar", status)
    scripts = list(re.finditer(r"<script>.*?</script\s*>", rendered, re.IGNORECASE | re.DOTALL))
    if len(scripts) != 1:
        raise ValueError("canonical runtime script must occur exactly once")
    script = f"<script>\n{runtime_js}\n{payload.business_script}\n</script>"
    rendered = rendered[: scripts[0].start()] + script + rendered[scripts[0].end() :]
    if sprite:
        hidden_sprite = sprite.replace("<svg ", '<svg hidden aria-hidden="true" style="display:none" ', 1)
        rendered = rendered.replace("</body>", hidden_sprite + "\n</body>", 1)
    return rendered


def render_canonical_frame(root: Path, frame_id: str, payload: FramePayload) -> str:
    root = root.resolve()
    try:
        filename = FRAME_FILES[frame_id]
    except KeyError as error:
        raise ValueError(f"unknown canonical frame: {frame_id}") from error
    layout = apply_frame_patches((root / "vendor/nhimc-design/layouts" / filename).read_text(encoding="utf-8"))
    sprite = (root / "vendor/nhimc-design/icons/nhimc-icons.svg").read_text(encoding="utf-8")
    runtime = (root / "src/generated/frame/frame-runtime.js").read_text(encoding="utf-8")
    return render_layout(
        layout,
        payload,
        icon_ids=_icon_ids(sprite),
        sprite=sprite,
        runtime_js=runtime,
        frame_kind=Path(filename).stem,
    )
