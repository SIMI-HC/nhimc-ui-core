"""Formal procedure for adding a Core-owned icon not yet in the vendor sprite.

Appends a validated <symbol> to src/generated/icons/core-icons.svg (merged into the vendor
sprite at build time by scripts.icon_overlay.merged_sprite) and a matching preview entry to
src/guide/upstream/gallery-data.json, so the Design Guide's icon library stays in sync.
Does not touch vendor/nhimc-design/icons/nhimc-icons.svg, which is a byte-identical upstream
mirror (see scripts/icon_overlay.py).

Usage:
    python scripts/add_canonical_icon.py --id stretcher --label "이송 침대" --category 이송 \\
        --svg '<rect x="2" y="10" width="20" height="6" rx="1"/><path d="M6 16v3M18 16v3"/>' \\
        [--svg-file path/to/paths.svg] [--tone sky] [--updated-at 2026-09-29T00:00:00+09:00]

After running, refresh the registered digest for the overlay file:
    python scripts/update_integrity.py --frame nhimc-default --frame-version <next-version>
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.icon_overlay import append_symbol

GALLERY_DATA = Path("src/guide/upstream/gallery-data.json")
VALID_TONES = ("apricot", "destructive", "pear", "pink", "purple", "sky", "success", "warning", "yellow")


def _append_gallery_entry(root: Path, *, icon_id: str, label: str, category: str, inner_svg: str, updated_at: str, tone: str) -> None:
    path = root / GALLERY_DATA
    data = json.loads(path.read_text(encoding="utf-8"))
    if any(item["id"] == icon_id for item in data["icons"]):
        raise ValueError(f"gallery-data.json already lists an icon id: {icon_id}")
    data["icons"].append(
        {"id": icon_id, "label": label, "category": category, "svg": inner_svg, "updatedAt": updated_at, "tone": tone}
    )
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def add_canonical_icon(
    root: Path,
    *,
    icon_id: str,
    label: str,
    category: str,
    inner_svg: str,
    tone: str = "sky",
    updated_at: str | None = None,
) -> None:
    root = root.resolve()
    if tone not in VALID_TONES:
        raise ValueError(f"unknown tone: {tone}; use one of {', '.join(VALID_TONES)}")
    updated_at = updated_at or datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    append_symbol(root, icon_id=icon_id, label=label, category=category, inner_svg=inner_svg, updated_at=updated_at)
    _append_gallery_entry(root, icon_id=icon_id, label=label, category=category, inner_svg=inner_svg, updated_at=updated_at, tone=tone)


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a Core-owned icon to the overlay sprite and Design Guide preview")
    parser.add_argument("--id", required=True, dest="icon_id")
    parser.add_argument("--label", required=True, help="Korean display label, e.g. 이송 침대")
    parser.add_argument("--category", required=True, help="Korean category, matching an existing icon category")
    parser.add_argument("--svg", help="inner SVG markup (paths/rects/etc, no <svg> or <symbol> wrapper)")
    parser.add_argument("--svg-file", type=Path, help="file containing the inner SVG markup instead of --svg")
    parser.add_argument("--tone", default="sky", choices=VALID_TONES)
    parser.add_argument("--updated-at", default=None, help="ISO 8601 timestamp; defaults to now")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    if not args.svg and not args.svg_file:
        parser.error("one of --svg or --svg-file is required")
    inner_svg = args.svg or args.svg_file.read_text(encoding="utf-8")
    add_canonical_icon(
        args.root,
        icon_id=args.icon_id,
        label=args.label,
        category=args.category,
        inner_svg=inner_svg,
        tone=args.tone,
        updated_at=args.updated_at,
    )
    print(f"icon added: {args.icon_id} (remember to run scripts/update_integrity.py to refresh its digest)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
