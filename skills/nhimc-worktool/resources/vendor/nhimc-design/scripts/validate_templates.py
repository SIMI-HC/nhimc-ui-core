#!/usr/bin/env python3
"""Template Catalog와 Golden HTML의 경로·오프라인 의존성을 검증한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlparse


REQUIRED_FIELDS = {
    "id", "variant", "page_type", "purpose", "template", "features",
    "shell", "density", "content_contract", "required_components",
    "supported_states", "added_date", "updated_date", "updated_at",
}
OPTIONAL_FIELDS = {"optional_components", "selectable"}
LIST_FIELDS = {
    "features", "shell", "content_contract", "required_components", "optional_components",
    "supported_states",
}
LAYOUT_REQUIRED_FIELDS = {"id", "frame_id", "version", "label", "purpose", "asset", "selectable", "default", "supported_responsive_modes", "content_slot", "token_source", "related", "canonical_spec", "added_date", "updated_date", "updated_at"}
ROLE_PATH = re.compile(r"^[a-z][a-z0-9-]*(?:/[a-z][a-z0-9-]*)*$")
REGISTRY_ID = re.compile(r"^[A-Z][A-Za-z0-9]+$")
STATE_ID = re.compile(r"^[a-z][a-z0-9-]*$")
LAYOUT_ID = re.compile(r"^[a-z][a-z0-9-]*$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
REMOTE_SCHEMES = {"http", "https", "ftp", "ws", "wss"}
NETWORK_CODE = re.compile(
    r"\b(fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(|\bimport\s*\(", re.IGNORECASE
)
CSS_IMPORT = re.compile(r"@import\b", re.IGNORECASE)
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
BASE64_DATA_URI = re.compile(r"data:[^\s\"')>]*;base64,", re.IGNORECASE)
FONT_FACE = re.compile(r"@font-face\b", re.IGNORECASE)
FORBIDDEN_SHORT_TOKEN = re.compile(r"(?<![\w-])--(?:p|c|b|i)(?=\s*:|\s*\))")

GLYPH_ICON_CHARS = re.compile(
    r">([←-⇿⌀-⏿─-◿①-⓿☀-➿⬀-⯿]{1,2})\s*<"
)
GLYPH_ICON_EXCEPTIONS = {"•", "●", "○", "◦", "‣"}

THEME_REQUIRED_FIELDS = {"id", "label", "summary", "recommended_for", "selectable", "tokens"}
THEME_ID = re.compile(r"^[a-z][a-z0-9-]*$")
THEME_TOKEN_KEYS = {"primary", "primary-foreground", "ring", "primary-90", "primary-20"}
THEME_ACCENT_TOKEN_KEYS = {
    "chip-sky", "chip-pear", "chip-apricot", "chip-yellow", "chip-purple", "chip-pink", "chip-amber",
    "accent-sky-foreground", "accent-pear-foreground", "accent-apricot-foreground",
    "accent-yellow-foreground", "accent-purple-foreground", "accent-pink-foreground", "accent-amber-foreground",
}
HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
RGBA_COLOR = re.compile(r"^rgba\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*(0|1|0?\.\d+)\s*\)$")
THEME_PREVIEW_ASSET = "assets/themes/preview.html"


class DependencyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.dependencies: list[tuple[str, str, str]] = []
        self.tags: set[str] = set()
        self.stack: list[tuple[str, str | None]] = []
        self.role_paths: list[str] = []
        self.components: set[str] = set()
        self.elements: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        values = dict(attrs)
        self.elements.append((tag, values))
        role = values.get("data-nhimc-role")
        if role:
            ancestors = [item_role for _, item_role in self.stack if item_role]
            self.role_paths.append("/".join([*ancestors, role]))
        component_value = values.get("data-nhimc-component") or ""
        self.components.update(component_value.split())
        if tag == "script" and values.get("src"):
            self.dependencies.append((tag, "src", values["src"] or ""))
        elif tag == "link" and values.get("href"):
            self.dependencies.append((tag, "href", values["href"] or ""))
        elif tag in {"img", "iframe", "audio", "video", "source", "embed"} and values.get("src"):
            self.dependencies.append((tag, "src", values["src"] or ""))
        elif tag == "object" and values.get("data"):
            self.dependencies.append((tag, "data", values["data"] or ""))
        if tag not in VOID_TAGS:
            self.stack.append((tag, role))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def load_template_catalog(root: Path) -> dict:
    catalog_path = root / "templates" / "catalog.yaml"
    try:
        return json.loads(catalog_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"catalog 누락: {catalog_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"catalog.yaml은 JSON 호환 YAML이어야 합니다: {exc}") from exc


def validate_template_entry(entry: object, index: int) -> list[str]:
    if not isinstance(entry, dict):
        return [f"templates[{index}]가 객체가 아닙니다"]
    errors: list[str] = []
    missing = REQUIRED_FIELDS - entry.keys()
    extra = entry.keys() - REQUIRED_FIELDS - OPTIONAL_FIELDS
    if missing:
        errors.append(f"templates[{index}] 필드 누락: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"templates[{index}] 미지원 필드: {', '.join(sorted(extra))}")
    for field in ("added_date", "updated_date"):
        if field in entry and (not isinstance(entry[field], str) or not ISO_DATE.fullmatch(entry[field])):
            errors.append(f"templates[{index}].{field}는 YYYY-MM-DD 형식이어야 합니다")
    if all(isinstance(entry.get(field), str) and ISO_DATE.fullmatch(entry[field]) for field in ("added_date", "updated_date")) and entry["added_date"] > entry["updated_date"]:
        errors.append(f"templates[{index}].updated_date가 added_date보다 빠릅니다")
    if "updated_at" in entry and (not isinstance(entry["updated_at"], str) or not ISO_DATETIME.fullmatch(entry["updated_at"])):
        errors.append(f"templates[{index}].updated_at은 시간대가 포함된 ISO 8601 형식이어야 합니다")
    if isinstance(entry.get("updated_at"), str) and ISO_DATETIME.fullmatch(entry["updated_at"]) and entry.get("updated_date") != entry["updated_at"][:10]:
        errors.append(f"templates[{index}].updated_at 날짜가 updated_date와 다릅니다")
    if "selectable" in entry and not isinstance(entry["selectable"], bool):
        errors.append(f"templates[{index}].selectable은 boolean이어야 합니다")
    for field in ("id", "variant", "page_type", "purpose", "template", "density"):
        if field in entry and (not isinstance(entry[field], str) or not entry[field].strip()):
            errors.append(f"templates[{index}].{field}는 비어 있지 않은 문자열이어야 합니다")
    for field in LIST_FIELDS:
        if field not in entry and field in OPTIONAL_FIELDS:
            continue
        value = entry.get(field)
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
            errors.append(f"templates[{index}].{field}는 문자열이 든 비어 있지 않은 배열이어야 합니다")
    for field in ("required_components", "optional_components"):
        values = entry.get(field, [])
        for value in values:
            if not REGISTRY_ID.fullmatch(value):
                errors.append(f"templates[{index}].{field}의 ID 형식 오류: {value}")
    for value in entry.get("content_contract", []):
        if not ROLE_PATH.fullmatch(value):
            errors.append(f"templates[{index}].content_contract 경로 형식 오류: {value}")
        elif not value.startswith("content/"):
            errors.append(f"templates[{index}].content_contract는 content slot 내부만 참조해야 합니다: {value}")
    for value in entry.get("supported_states", []):
        if not STATE_ID.fullmatch(value):
            errors.append(f"templates[{index}].supported_states ID 형식 오류: {value}")
    states = entry.get("supported_states", [])
    for duplicate in sorted({value for value in states if states.count(value) > 1}):
        errors.append(f"templates[{index}].supported_states 중복 ID: {duplicate}")
    if states and "default" not in states:
        errors.append(f"templates[{index}].supported_states에 default가 필요합니다")
    return errors


def validate_layout_entry(entry: object, index: int) -> list[str]:
    if not isinstance(entry, dict):
        return [f"layouts[{index}]가 객체가 아닙니다"]
    errors: list[str] = []
    missing = LAYOUT_REQUIRED_FIELDS - entry.keys()
    extra = entry.keys() - LAYOUT_REQUIRED_FIELDS
    if missing:
        errors.append(f"layouts[{index}] 필드 누락: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"layouts[{index}] 미지원 필드: {', '.join(sorted(extra))}")
    for field in ("added_date", "updated_date"):
        if field in entry and (not isinstance(entry[field], str) or not ISO_DATE.fullmatch(entry[field])):
            errors.append(f"layouts[{index}].{field}는 YYYY-MM-DD 형식이어야 합니다")
    if all(isinstance(entry.get(field), str) and ISO_DATE.fullmatch(entry[field]) for field in ("added_date", "updated_date")) and entry["added_date"] > entry["updated_date"]:
        errors.append(f"layouts[{index}].updated_date가 added_date보다 빠릅니다")
    if "updated_at" in entry and (not isinstance(entry["updated_at"], str) or not ISO_DATETIME.fullmatch(entry["updated_at"])):
        errors.append(f"layouts[{index}].updated_at은 시간대가 포함된 ISO 8601 형식이어야 합니다")
    if isinstance(entry.get("updated_at"), str) and ISO_DATETIME.fullmatch(entry["updated_at"]) and entry.get("updated_date") != entry["updated_at"][:10]:
        errors.append(f"layouts[{index}].updated_at 날짜가 updated_date와 다릅니다")
    for field in ("frame_id", "label", "purpose", "asset", "content_slot", "token_source"):
        if field in entry and (not isinstance(entry[field], str) or not entry[field].strip()):
            errors.append(f"layouts[{index}].{field}는 비어 있지 않은 문자열이어야 합니다")
    if "id" in entry and (not isinstance(entry["id"], str) or not LAYOUT_ID.fullmatch(entry["id"])):
        errors.append(f"layouts[{index}].id 형식 오류: {entry.get('id')!r}")
    if "selectable" in entry and not isinstance(entry["selectable"], bool):
        errors.append(f"layouts[{index}].selectable은 boolean이어야 합니다")
    if "default" in entry and not isinstance(entry["default"], bool):
        errors.append(f"layouts[{index}].default는 boolean이어야 합니다")
    if "version" in entry and (not isinstance(entry["version"], int) or entry["version"] < 1):
        errors.append(f"layouts[{index}].version은 1 이상의 정수여야 합니다")
    frame_id = entry.get("frame_id", "")
    if not re.fullmatch(r"[a-z][a-z0-9-]*:v\d+", frame_id) or not frame_id.endswith(f":v{entry.get('version')}"):
        errors.append(f"layouts[{index}].frame_id는 <name>:v<version> 형식이어야 합니다")
    for field in ("supported_responsive_modes", "related"):
        values = entry.get(field)
        if not isinstance(values, list) or not values or not all(isinstance(value, str) and value for value in values):
            errors.append(f"layouts[{index}].{field}는 문자열이 든 비어 있지 않은 배열이어야 합니다")
    spec = entry.get("canonical_spec")
    required_spec = {"structure", "height", "content", "motion", "responsive"}
    if not isinstance(spec, dict) or not required_spec.issubset(spec):
        errors.append(f"layouts[{index}].canonical_spec 필수 항목 누락")
    elif spec.get("content", {}).get("scroll_owner") != "content-slot":
        errors.append(f"layouts[{index}].canonical_spec.content.scroll_owner는 content-slot이어야 합니다")
    return errors


def validate_layout_paths(root: Path, entries: list[dict]) -> list[str]:
    errors: list[str] = []
    logo_mark_path = root / "docs" / "design-docs" / "assets" / "logo" / "brandmark-solo-logo-1.svg"
    canonical_favicon = None
    if logo_mark_path.is_file():
        logo_svg = logo_mark_path.read_text(encoding="utf-8").strip()
        canonical_favicon = f'<link rel="icon" href="data:image/svg+xml,{quote(logo_svg, safe="")}">'
    for entry in entries:
        path, error = _safe_relative(root, entry["asset"], "assets/layouts")
        if error:
            errors.append(f"layouts.{entry['id']}: {error}")
        elif path is None or not path.is_file():
            errors.append(f"layouts.{entry['id']}: asset 누락: {entry['asset']}")
        else:
            source = path.read_text(encoding="utf-8")
            if canonical_favicon and canonical_favicon not in source:
                errors.append(f"layouts.{entry['id']}: canonical brandmark-solo-logo-1 파비콘 누락")
            if 'data-nhimc-role="content-slot"' not in source:
                errors.append(f"layouts.{entry['id']}: content-slot marker 누락")
            if source.count("--color-input:") < 2:
                errors.append(f"layouts.{entry['id']}: 라이트·다크 공통 Input token 계약 누락")
            for marker in ('id="printButton"', "window.print", "@media print"):
                if marker in source:
                    errors.append(f"layouts.{entry['id']}: canonical Frame에 선택 기능인 인쇄가 선탑재됨: {marker}")
            nav_structure = entry.get("canonical_spec", {}).get("structure", [])
            nav_markers = ['data-nhimc-navigation-source="manifest"', 'data-navigation-view="desktop"']
            if "site-header" in nav_structure or "sidebar" in nav_structure:
                nav_markers.append('data-navigation-view="mobile"')
            for marker in nav_markers:
                if marker not in source:
                    errors.append(f"layouts.{entry['id']}: navigation manifest binding marker 누락: {marker}")
            if entry["id"] == "top" and ".topnav button svg" not in source:
                errors.append("layouts.top: compact navigation icon contract 누락")
            if entry["id"] == "top" and "var(--primary)" in source:
                errors.append("layouts.top: Color Theme을 우회하는 legacy --primary 참조가 남아 있습니다")
            if entry["id"] == "top" and "display:grid;align-content:start;gap:16px" not in source:
                errors.append("layouts.top: content natural-height alignment contract 누락")
            for marker in ('id="helpDialog"', "help-in", "help-out", "theme-moon", "theme-sun"):
                if marker not in source:
                    errors.append(f"layouts.{entry['id']}: 공용 Help/Theme Frame marker 누락: {marker}")
            help_button = re.search(r'<button[^>]+id="helpOpen"[^>]*>\s*<svg(?P<attrs>[^>]*)>', source)
            if not help_button or not all(marker in help_button.group("attrs") for marker in ('stroke-linecap="round"', 'stroke-linejoin="round"')):
                errors.append(f"layouts.{entry['id']}: canonical round-cap QuestionCircle 도움말 아이콘 계약 누락")
            for marker in ('<circle cx="12" cy="12" r="9"/>', 'd="M9.8 9a2.3 2.3 0 1 1 3.3 2.1c-.8.4-1.1.9-1.1 1.9M12 17h.01"'):
                if marker not in source:
                    errors.append(f"layouts.{entry['id']}: canonical 공통 utility 아이콘 geometry 누락: {marker}")
            structure = entry.get("canonical_spec", {}).get("structure", [])
            if "site-header" in structure and 'd="M4 7h16M4 12h16M4 17h16"' not in source:
                errors.append(f"layouts.{entry['id']}: canonical 모바일 햄버거 아이콘 geometry 누락: d=\"M4 7h16M4 12h16M4 17h16\"")
            for marker in ("color-scheme:light", "color-scheme:dark"):
                if marker not in source:
                    errors.append(f"layouts.{entry['id']}: 명시적 Theme color-scheme 계약 누락: {marker}")
            if entry["id"] in {"left", "top", "top-left"}:
                for marker in ("--color-scrollbar-thumb:#9e9e9e", "--color-scrollbar-thumb:#6f6f6f", "scrollbar-gutter:stable", "::-webkit-scrollbar-thumb"):
                    if marker not in source:
                        errors.append(f"layouts.{entry['id']}: 공통 Scrollbar 컴포넌트 계약 누락: {marker}")
        if not (root / entry["token_source"].split("#", 1)[0]).is_file():
            errors.append(f"layouts.{entry['id']}: token_source 누락: {entry['token_source']}")
    return errors


def discover_layouts(root: Path) -> set[str]:
    base = root / "assets" / "layouts"
    return {path.relative_to(root).as_posix() for path in base.rglob("*.html")} if base.exists() else set()


def find_uncatalogued_layouts(root: Path, entries: list[dict]) -> list[str]:
    catalogued = {entry["asset"] for entry in entries}
    return [f"catalog 미등록 layout asset: {path}" for path in sorted(discover_layouts(root) - catalogued)]


def validate_layouts(root: Path, catalog: dict) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    raw_entries = catalog.get("layouts")
    if not isinstance(raw_entries, list) or not raw_entries:
        return [], ["catalog layouts는 비어 있지 않은 배열이어야 합니다"]
    for index, entry in enumerate(raw_entries):
        errors.extend(validate_layout_entry(entry, index))
    if errors:
        return [], errors
    entries: list[dict] = raw_entries
    ids = [entry["id"] for entry in entries]
    for duplicate in sorted({item for item in ids if ids.count(item) > 1}):
        errors.append(f"중복 layout id: {duplicate}")
    errors.extend(validate_layout_paths(root, entries))
    errors.extend(find_uncatalogued_layouts(root, entries))
    if len({entry["frame_id"] for entry in entries}) != len(entries):
        errors.append("중복 frame_id")
    if sum(1 for entry in entries if entry.get("default")) != 1:
        errors.append("default Frame은 정확히 하나여야 합니다")
    return entries, errors


def validate_shell_layout_references(entries: list[dict], layout_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        for unknown in sorted(set(entry.get("shell", [])) - layout_ids):
            errors.append(f"{entry['id']}: layouts에 없는 shell 참조: {unknown}")
    return errors


def _relative_luminance(hex_color: str) -> float:
    value = hex_color.lstrip("#")
    channels = [int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [component / 12.92 if component <= 0.03928 else ((component + 0.055) / 1.055) ** 2.4 for component in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(hex_a: str, hex_b: str) -> float:
    luminance_a, luminance_b = _relative_luminance(hex_a), _relative_luminance(hex_b)
    lighter, darker = max(luminance_a, luminance_b), min(luminance_a, luminance_b)
    return (lighter + 0.05) / (darker + 0.05)


def validate_theme_entry(entry: object, index: int) -> list[str]:
    if not isinstance(entry, dict):
        return [f"themes[{index}]가 객체가 아닙니다"]
    errors: list[str] = []
    missing = THEME_REQUIRED_FIELDS - entry.keys()
    extra = entry.keys() - THEME_REQUIRED_FIELDS
    if missing:
        errors.append(f"themes[{index}] 필드 누락: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"themes[{index}] 미지원 필드: {', '.join(sorted(extra))}")
    for field in ("label", "summary", "recommended_for"):
        if field in entry and (not isinstance(entry[field], str) or not entry[field].strip()):
            errors.append(f"themes[{index}].{field}는 비어 있지 않은 문자열이어야 합니다")
    if "id" in entry and (not isinstance(entry["id"], str) or not THEME_ID.fullmatch(entry["id"])):
        errors.append(f"themes[{index}].id 형식 오류: {entry.get('id')!r}")
    if "selectable" in entry and not isinstance(entry["selectable"], bool):
        errors.append(f"themes[{index}].selectable은 boolean이어야 합니다")
    theme_id = entry.get("id", f"#{index}")
    tokens = entry.get("tokens")
    if not isinstance(tokens, dict) or set(tokens) != {"light", "dark"}:
        errors.append(f"themes.{theme_id}.tokens는 light/dark 두 mode만 포함해야 합니다")
        return errors
    for mode, values in tokens.items():
        actual_keys = set(values) if isinstance(values, dict) else set()
        allowed_keys = THEME_TOKEN_KEYS | THEME_ACCENT_TOKEN_KEYS
        if not isinstance(values, dict) or not THEME_TOKEN_KEYS.issubset(actual_keys) or not actual_keys.issubset(allowed_keys):
            errors.append(
                f"themes.{theme_id}.tokens.{mode} 키는 기본 계약 {', '.join(sorted(THEME_TOKEN_KEYS))}를 포함하고 "
                f"선택 accent {', '.join(sorted(THEME_ACCENT_TOKEN_KEYS))}만 사용할 수 있습니다"
            )
            continue
        accent_keys = actual_keys & THEME_ACCENT_TOKEN_KEYS
        if accent_keys and accent_keys != THEME_ACCENT_TOKEN_KEYS:
            errors.append(
                f"themes.{theme_id}.tokens.{mode} accent는 전체 chip token을 한 묶음으로 정의해야 합니다"
            )
        for key in ("primary", "primary-foreground", "ring"):
            if not HEX_COLOR.fullmatch(values[key]):
                errors.append(f"themes.{theme_id}.tokens.{mode}.{key}는 #RRGGBB 형식이어야 합니다: {values[key]!r}")
        for key in ("primary-90", "primary-20"):
            if not RGBA_COLOR.fullmatch(values[key]):
                errors.append(f"themes.{theme_id}.tokens.{mode}.{key}는 rgba(r, g, b, a) 형식이어야 합니다: {values[key]!r}")
        for key in THEME_ACCENT_TOKEN_KEYS & actual_keys:
            if not HEX_COLOR.fullmatch(values[key]):
                errors.append(f"themes.{theme_id}.tokens.{mode}.{key}는 #RRGGBB 형식이어야 합니다: {values[key]!r}")
        if HEX_COLOR.fullmatch(values.get("primary", "")) and HEX_COLOR.fullmatch(values.get("primary-foreground", "")):
            ratio = _contrast_ratio(values["primary"], values["primary-foreground"])
            if ratio < 4.5:
                errors.append(
                    f"themes.{theme_id}.tokens.{mode}: primary/primary-foreground 대비 {ratio:.2f}:1"
                    " (WCAG AA 4.5:1 미달)"
                )
    return errors


def load_theme_catalog(root: Path) -> dict:
    path = root / "tokens" / "themes" / "catalog.yaml"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"theme catalog 누락: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"tokens/themes/catalog.yaml은 JSON 호환 YAML이어야 합니다: {exc}") from exc


def validate_no_theme_specific_assets(root: Path, theme_ids: set[str]) -> list[str]:
    if not theme_ids:
        return []
    pattern = re.compile(r"(?:^|[-_])(?:" + "|".join(re.escape(theme_id) for theme_id in theme_ids) + r")(?:[-_]|$)")
    errors: list[str] = []
    for base in (root / "assets" / "templates", root / "assets" / "layouts"):
        if not base.exists():
            continue
        for path in base.rglob("*.html"):
            if pattern.search(path.stem):
                errors.append(
                    f"Theme별 중복 Golden Asset 의심: {path.relative_to(root).as_posix()} (파일명에 theme id 포함)"
                )
    return errors


def validate_themes(root: Path) -> tuple[list[dict], list[str]]:
    try:
        catalog = load_theme_catalog(root)
    except ValueError as exc:
        return [], [str(exc)]
    errors: list[str] = []
    if set(catalog) != {"version", "themes"}:
        errors.append("theme catalog 최상위 필드는 version, themes만 허용합니다")
    if catalog.get("version") != 1:
        errors.append("theme catalog version은 1이어야 합니다")
    raw_entries = catalog.get("themes")
    if not isinstance(raw_entries, list) or not raw_entries:
        return [], errors + ["theme catalog themes는 비어 있지 않은 배열이어야 합니다"]
    for index, entry in enumerate(raw_entries):
        errors.extend(validate_theme_entry(entry, index))
    if errors:
        return [], errors
    entries: list[dict] = raw_entries
    ids = [entry["id"] for entry in entries]
    for duplicate in sorted({item for item in ids if ids.count(item) > 1}):
        errors.append(f"중복 theme id: {duplicate}")
    preview_path, error = _safe_relative(root, THEME_PREVIEW_ASSET, "assets/themes")
    if error:
        errors.append(error)
    elif preview_path is None or not preview_path.is_file():
        errors.append(f"theme preview asset 누락: {THEME_PREVIEW_ASSET}")
    errors.extend(validate_no_theme_specific_assets(root, set(ids)))
    return entries, errors


def load_registry_ids(root: Path) -> tuple[set[str], set[str]]:
    component_text = (root / "components" / "registry.md").read_text(encoding="utf-8")
    pattern_text = (root / "patterns" / "registry.md").read_text(encoding="utf-8")
    components = {
        match.group(1)
        for line in component_text.splitlines()
        if (match := re.match(r"^\|\s*([A-Z][A-Za-z0-9]+)\s*\|", line))
    }
    patterns = {
        match.group(1)
        for line in pattern_text.splitlines()
        if (match := re.match(r"^##\s+([A-Z][A-Za-z0-9]+)\s*$", line))
    }
    return components, patterns


def validate_component_registry_reference(root: Path) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    try:
        components, patterns = load_registry_ids(root)
    except OSError as exc:
        return set(), [f"Component/Pattern Registry 읽기 실패: {exc}"]
    if not components:
        errors.append("Component Registry에서 canonical ID를 찾지 못했습니다")
    if not patterns:
        errors.append("Pattern Registry에서 canonical ID를 찾지 못했습니다")
    return components | patterns, errors


def validate_required_components(entries: list[dict], known_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        required = entry["required_components"]
        optional = entry.get("optional_components", [])
        for field, values in (("required_components", required), ("optional_components", optional)):
            duplicates = sorted({value for value in values if values.count(value) > 1})
            for duplicate in duplicates:
                errors.append(f"{entry['id']}: {field} 중복 ID: {duplicate}")
            for unknown in sorted(set(values) - known_ids):
                errors.append(f"{entry['id']}: Registry에 없는 {field} ID: {unknown}")
        for overlap in sorted(set(required) & set(optional)):
            errors.append(f"{entry['id']}: required/optional 중복 ID: {overlap}")
    return errors


def validate_template_component_mapping(root: Path, entries: list[dict], known_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        path = root / entry["template"]
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        parser = DependencyParser()
        parser.feed(source)
        if 'data-nhimc-template-scope="content-only"' not in source:
            errors.append(f"{entry['id']}: content-only Template scope marker 누락")
        forbidden_roles = {"app-shell", "sidebar", "app-main", "site-header", "content-slot", "statusbar", "mobile-drawer"}
        leaked_roles = sorted(
            role for role_path in parser.role_paths for role in role_path.split("/") if role in forbidden_roles
        )
        if leaked_roles:
            errors.append(f"{entry['id']}: Template에 Frame 역할 포함: {', '.join(leaked_roles)}")
        top_level_roles = [role_path for role_path in parser.role_paths if "/" not in role_path]
        if top_level_roles != ["content"]:
            errors.append(f"{entry['id']}: Template 최상위 역할은 content 하나여야 합니다: {top_level_roles}")
        contract = entry["content_contract"]
        for duplicate in sorted({value for value in contract if contract.count(value) > 1}):
            errors.append(f"{entry['id']}: content_contract 중복 경로: {duplicate}")
        actual_positions = {}
        for index, role_path in enumerate(parser.role_paths):
            parts = role_path.split("/")
            if "content" in parts:
                actual_positions.setdefault("/".join(parts[parts.index("content"):]), index)
        missing_roles = [role_path for role_path in contract if role_path not in actual_positions]
        for role_path in missing_roles:
            errors.append(f"{entry['id']}: required content role 누락: {role_path}")
        positions = [actual_positions[role_path] for role_path in contract if role_path in actual_positions]
        if positions != sorted(positions):
            errors.append(f"{entry['id']}: content_contract 순서와 Template DOM 순서가 다릅니다")
        for component_id in sorted(set(entry["required_components"]) - parser.components):
            errors.append(f"{entry['id']}: Template component marker 누락: {component_id}")
        for component_id in sorted(parser.components - known_ids):
            errors.append(f"{entry['id']}: Template marker가 Registry 미등록 ID 참조: {component_id}")
        component_bindings = {
            "button": {"Button", "IconButton", "IconTextButton", "Tabs", "Pagination", "Dialog", "Sheet", "Drawer", "Switch", "ConfirmAction"},
            "select": {"Select"},
            "table": {"Table"},
            "textarea": {"Textarea"},
        }
        for tag, attributes in parser.elements:
            expected = component_bindings.get(tag)
            if tag == "input":
                input_type = (attributes.get("type") or "text").lower()
                expected = {"Checkbox"} if input_type == "checkbox" else {"Radio"} if input_type == "radio" else {"Input"}
            if not expected:
                continue
            bound = set((attributes.get("data-nhimc-component") or "").split())
            if not bound & expected:
                errors.append(
                    f"{entry['id']}: <{tag}>가 canonical Component에 직접 연결되지 않았습니다 "
                    f"(허용: {', '.join(sorted(expected))})"
                )
    return errors


def _safe_relative(root: Path, relative: str, prefix: str) -> tuple[Path | None, str | None]:
    normalized = relative.replace("\\", "/")
    if not normalized.startswith(prefix + "/") or Path(normalized).is_absolute() or ".." in Path(normalized).parts:
        return None, f"허용 범위 밖 경로: {relative}"
    resolved = (root / normalized).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None, f"정본 밖 경로: {relative}"
    return resolved, None


def validate_template_paths(root: Path, entries: list[dict]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        path, error = _safe_relative(root, entry["template"], "assets/templates")
        if error:
            errors.append(f"{entry['id']}: {error}")
        elif path is None or not path.is_file():
            errors.append(f"{entry['id']}: template 누락: {entry['template']}")
    return errors


def discover_templates(root: Path) -> set[str]:
    base = root / "assets" / "templates"
    return {path.relative_to(root).as_posix() for path in base.rglob("*.html")} if base.exists() else set()


def find_uncatalogued_templates(root: Path, entries: list[dict]) -> list[str]:
    catalogued = {entry["template"] for entry in entries}
    return [f"catalog 미등록 template: {path}" for path in sorted(discover_templates(root) - catalogued)]


def validate_assets(root: Path) -> list[str]:
    required = [
        "docs/design-docs/assets/fonts.css",
        "docs/design-docs/assets/font/noto-sans-kr-korean-400.woff2",
        "docs/design-docs/assets/logo/brandmark-solo-logo-1.svg",
        "docs/design-docs/assets/logo/brandmark-row-logo.svg",
    ]
    return [f"필수 asset 누락: {path}" for path in required if not (root / path).is_file()]


def _is_remote(value: str) -> bool:
    return urlparse(value.strip()).scheme.lower() in REMOTE_SCHEMES or value.strip().startswith("//")


def validate_html_dependencies(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    parser = DependencyParser()
    parser.feed(text)
    required_tags = {"html", "head", "body", "style"}
    if not text.lstrip().lower().startswith("<!doctype html>"):
        errors.append(f"{path}: <!doctype html> 누락")
    if not re.search(r"<html\b[^>]*\bdata-theme\s*=\s*['\"]light['\"]", text, re.IGNORECASE):
        errors.append(f"{path}: Golden Asset 기본 테마 계약 누락(data-theme=\"light\")")
    if not re.search(r"\[data-theme\s*=\s*['\"]dark['\"]\]", text, re.IGNORECASE):
        errors.append(f"{path}: Golden Asset 명시적 다크 테마 계약 누락([data-theme=\"dark\"])")
    if re.search(r"prefers-color-scheme\s*:", text, re.IGNORECASE):
        errors.append(f"{path}: Golden Asset은 OS 테마와 분리해야 합니다 — prefers-color-scheme 대신 data-theme만 사용합니다")
    for tag in sorted(required_tags - parser.tags):
        errors.append(f"{path}: <{tag}> 누락")
    for tag, attribute, value in parser.dependencies:
        if not value.startswith("data:"):
            errors.append(f"{path}: 외부/분리 의존성 금지: <{tag} {attribute}={value!r}>")
    if NETWORK_CODE.search(text):
        errors.append(f"{path}: 네트워크 JavaScript API 사용 금지")
    if CSS_IMPORT.search(text):
        errors.append(f"{path}: CSS @import 사용 금지")
    if BASE64_DATA_URI.search(text):
        errors.append(f"{path}: Golden Asset에 Base64/Data URI 바이너리 삽입 금지")
    if FONT_FACE.search(text):
        errors.append(f"{path}: Golden Asset HTML 내부 @font-face 금지 — 지정 font stack으로 폴백한다")
    if FORBIDDEN_SHORT_TOKEN.search(text):
        errors.append(f"{path}: 축약 CSS Token(--p/--c/--b/--i) 금지 — SSOT Semantic Token 이름을 쓴다")
    for _, value in CSS_URL.findall(text):
        if value and not value.startswith(("data:", "#")):
            errors.append(f"{path}: 외부/분리 CSS url() 금지: {value}")
    for match in re.findall(r"(?:src|href)\s*=\s*['\"]([^'\"]+)['\"]", text, re.IGNORECASE):
        if _is_remote(match):
            errors.append(f"{path}: 원격 URL 금지: {match}")
    for glyph in sorted({m.group(1) for m in GLYPH_ICON_CHARS.finditer(text)} - GLYPH_ICON_EXCEPTIONS):
        errors.append(
            f"{path}: 유니코드 글리프를 아이콘으로 사용 금지({glyph!r}) — components/icons.md의 SVG 아이콘을 쓴다"
        )
    return errors


def validate_catalog(root: Path, catalog: dict) -> tuple[list[dict], list[dict], list[str]]:
    errors: list[str] = []
    if set(catalog) != {"version", "input_schema", "templates", "layouts"}:
        errors.append("catalog 최상위 필드는 version, input_schema, layouts, templates만 허용합니다")
    if catalog.get("version") != 2:
        errors.append("catalog version은 2여야 합니다")
    input_schema = catalog.get("input_schema")
    required_input = {"allowed", "frame_aliases", "navigation_fields", "frame_owned", "content_owned"}
    if not isinstance(input_schema, dict) or set(input_schema) != required_input:
        errors.append("input_schema 필드가 Frame 사용자 입력 계약과 일치하지 않습니다")
    layout_entries, layout_errors = validate_layouts(root, catalog)
    errors.extend(layout_errors)
    raw_entries = catalog.get("templates")
    if not isinstance(raw_entries, list) or not raw_entries:
        return [], layout_entries, errors + ["catalog templates는 비어 있지 않은 배열이어야 합니다"]
    for index, entry in enumerate(raw_entries):
        errors.extend(validate_template_entry(entry, index))
    if errors:
        return [], layout_entries, errors
    entries: list[dict] = raw_entries
    ids = [entry["id"] for entry in entries]
    for duplicate in sorted({item for item in ids if ids.count(item) > 1}):
        errors.append(f"중복 template id: {duplicate}")
    errors.extend(validate_template_paths(root, entries))
    errors.extend(find_uncatalogued_templates(root, entries))
    errors.extend(validate_shell_layout_references(entries, {item["id"] for item in layout_entries}))
    known_ids, registry_errors = validate_component_registry_reference(root)
    errors.extend(registry_errors)
    errors.extend(validate_required_components(entries, known_ids))
    errors.extend(validate_template_component_mapping(root, entries, known_ids))
    return entries, layout_entries, errors


def validate_all(root: Path) -> list[str]:
    try:
        catalog = load_template_catalog(root)
    except ValueError as exc:
        return [str(exc)]
    entries, layout_entries, errors = validate_catalog(root, catalog)
    theme_entries, theme_errors = validate_themes(root)
    errors.extend(theme_errors)
    errors.extend(validate_assets(root))
    html_paths = {root / entry["template"] for entry in entries}
    html_paths.update(root / entry["asset"] for entry in layout_entries)
    html_paths.update((root / "assets" / "components").glob("*.html"))
    if theme_entries:
        html_paths.add(root / THEME_PREVIEW_ASSET)
    for path in sorted(html_paths):
        if path.is_file():
            errors.extend(validate_html_dependencies(path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate_all(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    catalog = load_template_catalog(args.root.resolve())
    theme_catalog = load_theme_catalog(args.root.resolve())
    print(f"OK template catalog entries={len(catalog['templates'])}")
    print(f"OK layout catalog entries={len(catalog['layouts'])}")
    print(f"OK theme catalog entries={len(theme_catalog['themes'])}")
    print("OK Frame Registry and Content Contracts match Template/Registry")
    print("OK Theme Semantic Token Contract and WCAG AA contrast")
    print("OK Golden HTML external runtime dependencies=0")
    print("OK Golden Asset Base64/Data URI binary=0 and embedded @font-face=0")
    print("OK Golden Asset forbidden short Semantic Token=0")
    print("OK Golden Asset glyph-as-icon usage=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
