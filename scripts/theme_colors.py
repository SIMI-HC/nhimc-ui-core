"""Theme color overlays generated from the canonical theme catalog (single source)."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.dark_tones import dark_tone_css

CATALOG = Path("vendor/nhimc-design/tokens/themes/catalog.yaml")
DEFAULT_THEME_COLOR = "nhimc-default"


def _themes(root: Path) -> list[dict]:
    data = json.loads((root / CATALOG).read_text(encoding="utf-8"))
    return [theme for theme in data["themes"] if theme.get("selectable")]


def theme_color_ids(root: Path) -> list[str]:
    return [theme["id"] for theme in _themes(root)]


def theme_color_css(root: Path) -> str:
    """[data-theme-color] overlays (the default theme needs none: its values are the base tokens) and the dark-mode accent / primary-button tones."""
    blocks: list[str] = []
    for theme in _themes(root):
        if theme["id"] == DEFAULT_THEME_COLOR:
            continue
        for mode in ("light", "dark"):
            tokens = theme["tokens"].get(mode)
            if not tokens:
                continue
            selector = f'[data-theme-color="{theme["id"]}"]' + ('[data-theme="dark"]' if mode == "dark" else "")
            body = ";".join(f"--color-{name}:{value}" for name, value in tokens.items())
            blocks.append(f"{selector}{{{body}}}")
    blocks.append(dark_tone_css(root))
    return "\n".join(blocks)
