#!/usr/bin/env python3
"""NHIMC 단일 HTML 산출물의 오프라인·자산·Semantic Token 계약을 검사한다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


BASE64_DATA_URI = re.compile(r"data:[^\s\"')>]*;base64,", re.IGNORECASE)
FONT_FACE = re.compile(r"@font-face\b", re.IGNORECASE)
REMOTE_ASSET = re.compile(
    r"(?:src|href)\s*=\s*[\"'](?:https?|ftp):|@import\s+(?:url\()?\s*[\"']?(?:https?|ftp):",
    re.IGNORECASE,
)
NETWORK_API = re.compile(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(")
FORBIDDEN_SHORT_TOKEN = re.compile(r"(?<![\w-])--(?:p|c|b|i)(?=\s*:|\s*\))")
FONT_STACK = re.compile(
    r"[\"']Noto Sans KR[\"']\s*,\s*[\"']Malgun Gothic[\"']\s*,\s*"
    r"[\"']Apple SD Gothic Neo[\"']\s*,\s*system-ui\s*,\s*sans-serif",
    re.IGNORECASE,
)
NAVIGATION_MANIFEST = re.compile(
    r"<script(?=[^>]*\bid=[\"']navigationManifest[\"'])[^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
NAVIGATION_VIEW = re.compile(
    r"<nav\b(?P<attrs>[^>]*)>(?P<body>.*?)</nav>",
    re.IGNORECASE | re.DOTALL,
)
SCREEN_TARGET_TAG = re.compile(r"<(?:a|button)\b[^>]*\bdata-screen-target=[\"'][^\"']+[\"'][^>]*>", re.IGNORECASE)
SCREEN_PANEL_TAG = re.compile(r"<[^>]+\bdata-screen-panel=[\"'][^\"']+[\"'][^>]*>", re.IGNORECASE)
HTML_ATTR = re.compile(r"([:\w-]+)\s*=\s*[\"']([^\"']*)[\"']")

SKILL_ROOT = Path(__file__).resolve().parents[1]
LOGO_ROW_ASSET = SKILL_ROOT / "docs" / "design-docs" / "assets" / "logo" / "brandmark-row-logo.svg"
LOGO_MARK_ASSET = SKILL_ROOT / "docs" / "design-docs" / "assets" / "logo" / "brandmark-solo-logo-1.svg"
ROW_LOGO_CLASSES = ("hospital-brand-logo", "brand-row")
MARK_LOGO_CLASS = "brand-mark"
SVG_BLOCK = re.compile(r"<svg\b(?P<attrs>[^>]*)>(?P<body>.*?)</svg>", re.IGNORECASE | re.DOTALL)
CSS_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
NAV_LINK_QUERY = re.compile(r"querySelectorAll\(\s*[\"']\.nav-link[\"']\s*\)", re.IGNORECASE)
NAV_LINK_TITLE = re.compile(
    r"querySelectorAll\(\s*[\"']\.nav-link[\"']\s*\)\.forEach\(\s*\w+\s*=>\s*\{[^}]*\.title\s*=", re.IGNORECASE
)


def _attrs(tag: str) -> dict[str, str]:
    return {name.lower(): value for name, value in HTML_ATTR.findall(tag)}


def validate_navigation(text: str) -> list[str]:
    errors: list[str] = []
    match = NAVIGATION_MANIFEST.search(text)
    if not match:
        return errors
    try:
        manifest = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        return [f"navigationManifest JSON이 올바르지 않습니다: {exc}"]
    if not isinstance(manifest, list) or not manifest:
        return ["navigationManifest는 한 개 이상의 화면 배열이어야 합니다"]
    ids = [item.get("screen_id") for item in manifest if isinstance(item, dict)]
    if len(ids) != len(manifest) or any(not isinstance(screen_id, str) or not screen_id for screen_id in ids):
        errors.append("navigationManifest의 모든 항목에 비어 있지 않은 screen_id가 필요합니다")
        return errors
    if len(ids) != len(set(ids)):
        errors.append("navigationManifest의 screen_id는 중복될 수 없습니다")
    active_ids = [item["screen_id"] for item in manifest if item.get("active") is True]
    if len(active_ids) != 1:
        errors.append("navigationManifest에는 active=true 화면이 정확히 하나여야 합니다")
    elif active_ids[0] != ids[0]:
        errors.append("자체 포함 신규 결과물은 navigationManifest 첫 항목이 active=true여야 합니다")

    views: dict[str, tuple[list[str], list[str]]] = {}
    for view_match in NAVIGATION_VIEW.finditer(text):
        container_attrs = _attrs("<nav " + view_match.group("attrs") + ">")
        view = container_attrs.get("data-navigation-view", "").lower()
        if view not in {"desktop", "mobile"}:
            continue
        tags = SCREEN_TARGET_TAG.findall(view_match.group("body"))
        targets = [_attrs(tag).get("data-screen-target", "") for tag in tags]
        active_targets = [
            _attrs(tag).get("data-screen-target", "")
            for tag in tags
            if _attrs(tag).get("aria-current") == "page"
        ]
        if not targets and container_attrs.get("data-navigation-clone") == "desktop" and "desktop" in views:
            targets, active_targets = views["desktop"]
        views[view] = (targets, active_targets)

    for view in ("desktop", "mobile"):
        if view not in views:
            errors.append(f"{view} navigation view가 없습니다")
            continue
        targets, active_targets = views[view]
        if targets != ids:
            errors.append(f"{view} 메뉴 screen_id·순서가 navigationManifest와 다릅니다")
        if active_ids and active_targets != active_ids:
            errors.append(f"{view} 활성 메뉴가 navigationManifest와 다릅니다")

    panel_tags = SCREEN_PANEL_TAG.findall(text)
    panel_ids = [_attrs(tag).get("data-screen-panel", "") for tag in panel_tags]
    if len(panel_ids) != len(ids) or set(panel_ids) != set(ids):
        errors.append("data-screen-panel의 screen_id가 navigationManifest와 1:1로 연결되지 않았습니다")
    visible_panel_ids = [
        _attrs(tag).get("data-screen-panel", "")
        for tag in panel_tags
        if not re.search(r"\bhidden(?:\s|=|>)", tag, re.IGNORECASE)
    ]
    if active_ids and visible_panel_ids != active_ids:
        errors.append("최초 표시 screen panel은 navigationManifest의 active 화면 하나와 같아야 합니다")
    return errors


def _normalize_svg_body(body: str) -> str:
    body = re.sub(r"<title\b[^>]*>.*?</title>", "", body, flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", "", body)


def _load_canonical_svg_body(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    match = SVG_BLOCK.search(text)
    return _normalize_svg_body(match.group("body")) if match else ""


def _find_svg_bodies_by_class(text: str, class_name: str) -> list[str]:
    bodies = []
    for match in SVG_BLOCK.finditer(text):
        if re.search(rf'class=["\'][^"\']*\b{re.escape(class_name)}\b[^"\']*["\']', match.group("attrs"), re.IGNORECASE):
            bodies.append(match.group("body"))
    return bodies


def validate_brand_logo(text: str) -> list[str]:
    errors: list[str] = []
    row_canonical = _load_canonical_svg_body(LOGO_ROW_ASSET)
    if row_canonical:
        for class_name in ROW_LOGO_CLASSES:
            for body in _find_svg_bodies_by_class(text, class_name):
                if _normalize_svg_body(body) != row_canonical:
                    errors.append(
                        "가로 병원 브랜드 로고가 정본 assets/logo/brandmark-row-logo.svg 원본과 일치하지 않습니다"
                        " — 손으로 재구성하지 말고 정본 SVG를 그대로 복사해야 합니다"
                    )
    mark_canonical = _load_canonical_svg_body(LOGO_MARK_ASSET)
    if mark_canonical:
        for body in _find_svg_bodies_by_class(text, MARK_LOGO_CLASS):
            if _normalize_svg_body(body) != mark_canonical:
                errors.append(
                    "접힌 사이드바 로고 마크가 정본 assets/logo/brandmark-solo-logo-1.svg 원본과 일치하지 않습니다"
                    " — 손으로 재구성하지 말고 정본 SVG를 그대로 복사해야 합니다"
                )
    return errors


def _help_dialog_rule_declarations(text: str) -> list[str]:
    declarations = []
    for selector, decl in CSS_RULE.findall(text):
        selector_lower = selector.lower()
        if "dialog" in selector_lower and "mobile" not in selector_lower and "backdrop" not in selector_lower:
            declarations.append(decl)
    return declarations


def validate_help_dialog(text: str) -> list[str]:
    errors: list[str] = []
    if 'id="helpDialog"' not in text and "id='helpDialog'" not in text:
        return errors
    declarations = _help_dialog_rule_declarations(text)
    if not any("var(--color-card)" in decl for decl in declarations):
        errors.append("도움말 Dialog는 정본과 같이 background:var(--color-card) 카드 표면을 사용해야 합니다")
    if not any("help-in" in decl for decl in declarations) or not any("help-out" in decl for decl in declarations):
        errors.append(
            "도움말 Dialog는 정본과 같이 help-in/help-out 슬라이드 애니메이션을 사용해야 합니다"
            " — 다이얼로그를 직접 다시 그리지 않는다"
        )
    return errors


def validate_nav_link_tooltip(text: str) -> list[str]:
    errors: list[str] = []
    if "is-collapsed" not in text or not NAV_LINK_QUERY.search(text):
        return errors
    if not NAV_LINK_TITLE.search(text):
        errors.append(
            "접힌 사이드바에서 .nav-link에 title 툴팁을 지정하는 정본 스크립트가 빠졌습니다"
            " — 아이콘만 남을 때 hover로 메뉴명을 읽을 수 있어야 합니다"
        )
    return errors


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if path.suffix.lower() != ".html":
        return ["결과물은 .html 한 파일이어야 합니다"]
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"파일을 찾을 수 없습니다: {path}"]
    except UnicodeDecodeError:
        return ["HTML은 UTF-8이어야 합니다"]

    checks = (
        ("<style", "CSS를 포함한 <style>이 없습니다"),
        ("<script", "최소 상호작용 JavaScript를 포함한 <script>가 없습니다"),
        ("<svg", "canonical inline SVG 아이콘이 없습니다"),
    )
    lower = text.lower()
    for needle, message in checks:
        if needle not in lower:
            errors.append(message)
    if BASE64_DATA_URI.search(text):
        errors.append("Base64/Data URI 바이너리를 포함하면 안 됩니다")
    if FONT_FACE.search(text):
        errors.append("HTML 내부 @font-face 또는 폰트 바이너리 내장을 사용하면 안 됩니다")
    if REMOTE_ASSET.search(text):
        errors.append("외부 런타임 CSS·JavaScript·이미지·폰트 참조를 사용하면 안 됩니다")
    if NETWORK_API.search(text):
        errors.append("오프라인 결과물에서 네트워크 API를 사용하면 안 됩니다")
    if FORBIDDEN_SHORT_TOKEN.search(text):
        errors.append("금지된 축약 Token(--p/--c/--b/--i)을 사용하면 안 됩니다")
    if not FONT_STACK.search(text):
        errors.append("NHIMC 지정 Font Stack을 정확히 선언해야 합니다")
    errors.extend(validate_navigation(text))
    errors.extend(validate_brand_logo(text))
    errors.extend(validate_help_dialog(text))
    errors.extend(validate_nav_link_tooltip(text))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    args = parser.parse_args()
    errors = validate(args.html.resolve())
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"OK NHIMC single HTML deliverable: {args.html.resolve()}")
    print("OK external runtime dependencies=0")
    print("OK Base64/Data URI binary=0 and embedded @font-face=0")
    print("OK forbidden short Semantic Token=0")
    print("OK navigation manifest/menu/screen binding")
    print("OK Frame-owned brand logo/help dialog/collapsed nav tooltip contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
