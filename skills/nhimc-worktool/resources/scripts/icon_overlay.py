"""Core-owned icon overlay.

vendor/nhimc-design/icons/nhimc-icons.svg is a byte-identical mirror of an upstream commit
(verified by scripts/verify_nhimc_design_sync.py); it cannot be hand-edited here. When a
Core-authored icon is needed before it exists upstream, it is added to this overlay file
instead and merged into the vendor sprite at build time (see merged_sprite). This is the
same "Core owns the divergence until upstream catches up" pattern scripts/frame_patches.py
uses for Frame behavior.
"""
from __future__ import annotations

from pathlib import Path
import re

OVERLAY_PATH = Path("src/generated/icons/core-icons.svg")
REQUIRED_VIEWBOX = "0 0 24 24"
REQUIRED_DATA_ATTRIBUTES = ("data-label", "data-category", "data-updated-at")
SYMBOL_OPEN = re.compile(r"<symbol\b(?P<attrs>[^>]*)>(?P<body>.*?)</symbol>", re.DOTALL)


def icon_ids_in(sprite: str) -> set[str]:
    return set(re.findall(r'<symbol\s+id="([a-z0-9-]+)"', sprite))


def _attribute(attrs: str, name: str) -> str | None:
    match = re.search(rf'\b{re.escape(name)}="([^"]*)"', attrs)
    return match.group(1) if match else None


def validate_symbol(symbol_xml: str) -> list[str]:
    """Returns style-contract violations for one <symbol>...</symbol> block; [] means it is clean.

    The contract (24x24 viewBox, stroke-width 2, round cap/join, currentColor, no fill) is enforced
    by the shared wrapper <svg> every menu icon renders through (scripts/canonical_frame.py's
    _menu_items); a symbol only needs to not override it, so children must carry no fill/stroke.
    """
    match = SYMBOL_OPEN.search(symbol_xml)
    if not match:
        return ["not a well-formed <symbol>...</symbol> block"]
    attrs, body = match.group("attrs"), match.group("body")
    findings: list[str] = []
    icon_id = _attribute(attrs, "id")
    if not icon_id or not re.fullmatch(r"[a-z0-9-]+", icon_id):
        findings.append("symbol id must be a safe lowercase identifier")
    view_box = _attribute(attrs, "viewBox")
    if view_box != REQUIRED_VIEWBOX:
        findings.append(f'viewBox must be "{REQUIRED_VIEWBOX}", found {view_box!r}')
    for name in REQUIRED_DATA_ATTRIBUTES:
        if _attribute(attrs, name) is None:
            findings.append(f"missing required attribute: {name}")
    if re.search(r'\bfill="(?!none")[^"]*"', body):
        findings.append("child elements must not hardcode fill (inherits currentColor from the wrapper)")
    if re.search(r'\bstroke="[^"]*"', body):
        findings.append("child elements must not hardcode stroke (inherits currentColor from the wrapper)")
    return findings


def _svg_body(source: str) -> str:
    match = re.search(r"<svg\b[^>]*>(.*)</svg\s*>", source, re.DOTALL)
    if not match:
        raise ValueError("not a well-formed <svg>...</svg> document")
    return match.group(1)


def merged_sprite(root: Path, vendor_sprite: str) -> str:
    """The vendor sprite with any Core-owned overlay symbols appended before </svg>."""
    overlay_path = root / OVERLAY_PATH
    if not overlay_path.is_file():
        return vendor_sprite
    overlay_body = _svg_body(overlay_path.read_text(encoding="utf-8")).strip()
    if not overlay_body:
        return vendor_sprite
    return vendor_sprite.replace("</svg>", overlay_body + "</svg>", 1)


def validate_overlay(root: Path) -> list[str]:
    overlay_path = root / OVERLAY_PATH
    if not overlay_path.is_file():
        return []
    findings: list[str] = []
    seen: set[str] = set()
    for match in SYMBOL_OPEN.finditer(overlay_path.read_text(encoding="utf-8")):
        symbol_id = _attribute(match.group("attrs"), "id") or "(missing id)"
        for finding in validate_symbol(match.group(0)):
            findings.append(f"{symbol_id}: {finding}")
        if symbol_id in seen:
            findings.append(f"{symbol_id}: duplicate symbol id in overlay")
        seen.add(symbol_id)
    return findings


def append_symbol(
    root: Path,
    *,
    icon_id: str,
    label: str,
    category: str,
    inner_svg: str,
    updated_at: str,
) -> None:
    root = root.resolve()
    overlay_path = root / OVERLAY_PATH
    overlay_text = overlay_path.read_text(encoding="utf-8") if overlay_path.is_file() else '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
    if icon_id in icon_ids_in(overlay_text):
        raise ValueError(f"icon id already exists in the overlay: {icon_id}")
    vendor_sprite_path = root / "vendor/nhimc-design/icons/nhimc-icons.svg"
    if vendor_sprite_path.is_file() and icon_id in icon_ids_in(vendor_sprite_path.read_text(encoding="utf-8")):
        raise ValueError(f"icon id is already used by a vendor icon: {icon_id}")
    symbol = (
        f'<symbol id="{icon_id}" viewBox="{REQUIRED_VIEWBOX}" data-label="{label}" '
        f'data-category="{category}" data-updated-at="{updated_at}">{inner_svg}</symbol>'
    )
    findings = validate_symbol(symbol)
    if findings:
        raise ValueError(f"new icon violates the style contract: {'; '.join(findings)}")
    overlay_path.parent.mkdir(parents=True, exist_ok=True)
    overlay_path.write_text(overlay_text.replace("</svg>", symbol + "</svg>", 1), encoding="utf-8", newline="\n")
