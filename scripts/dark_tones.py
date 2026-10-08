"""Static dark-mode tones for Accent cards and the primary button (generated from the theme catalog).

The accent chips are fixed pastels. On a dark card they glare, so in dark mode the card head keeps 22% of the pastel over the
card colour and the outline 28%; the primary button keeps 60% of the theme's primary over the card (75% on hover); its text is light, or the theme's
dark button text where that reads better (Mint and Neutral have light primaries). The values are mixed channel by channel here instead of with CSS color-mix(): the offline target Edge is 92.

theme_color_css() (scripts/theme_colors.py) appends dark_tone_css() to the theme CSS of every build, so the hex values live
with the other generated theme colours and not in src/layouts/primitives.css (design rule: no hard-coded colour there).
"""
from __future__ import annotations

import json
from pathlib import Path

CATALOG = Path("vendor/nhimc-design/tokens/themes/catalog.yaml")
DARK_CARD = "#171717"
LIGHT_TEXT = "#fafafa"  # dark --color-foreground
HEAD, LINE = 22, 28
SOFT, SOFT_HOVER = 60, 75
DEFAULT_THEME = "nhimc-default"
ACCENTS = ("sky", "pear", "apricot", "yellow", "purple", "pink", "amber")
BASE_CHIPS = ("sky", "pear", "apricot", "yellow")
# purple, pink and amber chips exist in Color Mix only; elsewhere they look like these (same fallback as the light rules)
FALLBACK = {"purple": "sky", "pink": "apricot", "amber": "yellow"}
CHIP_FOREGROUND = "#14253A"  # text on a chip in a theme without --color-accent-*-foreground (fixed in light and dark)
COLOR_MIX = "color-mix"


def _channels(value: str) -> list[int]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    return [int(value[index : index + 2], 16) for index in (0, 2, 4)]


def _luminance(value: str) -> float:
    linear = [channel / 255 for channel in _channels(value)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in linear]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
    high, low = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def mix(top: str, base: str, percent: int) -> str:
    """percent% of top over base, channel by channel, rounded half up (JavaScript Math.round)."""
    top_rgb, base_rgb = _channels(top), _channels(base)
    parts = [int(a * percent / 100 + b * (100 - percent) / 100 + 0.5) for a, b in zip(top_rgb, base_rgb)]
    return "#" + "".join(f"{part:02x}" for part in parts)


def _themes(root: Path) -> dict[str, dict]:
    data = json.loads((root / CATALOG).read_text(encoding="utf-8"))
    return {theme["id"]: theme for theme in data["themes"] if theme.get("selectable")}


def _chips(root: Path) -> dict[str, str]:
    tokens = _themes(root)[COLOR_MIX]["tokens"]["light"]
    return {name: tokens[f"chip-{name}"] for name in ACCENTS}


def chip_css(root: Path) -> str:
    """The accent chips (fixed pastels in light and dark) for every theme. Only Color Mix carried them, so a card with
    data-nhimc-accent had no colour (and a black outline) in the other themes. purple, pink and amber stay Color Mix only."""
    chips = _chips(root)
    values = ";".join(f"--color-chip-{name}:{chips[name]}" for name in BASE_CHIPS)
    return f":root{{{values};--color-chip-foreground:{CHIP_FOREGROUND}}}"


def accent_css(root: Path) -> str:
    chips = _chips(root)
    tones = {name: (mix(chips[name], DARK_CARD, HEAD), mix(chips[name], DARK_CARD, LINE)) for name in ACCENTS}

    def rule(selector: str, name: str, source: str, *, foreground: bool) -> str:
        surface, line = tones[source]
        extra = ";--nhimc-accent-foreground:var(--color-card-foreground)" if foreground else ""
        return f'{selector} [data-nhimc-accent="{name}"]{{--nhimc-accent-surface:{surface};--nhimc-accent-line:{line}{extra}}}'

    lines = [rule('[data-theme="dark"]', name, FALLBACK.get(name, name), foreground=True) for name in ACCENTS]
    lines += [rule(f'[data-theme-color="{COLOR_MIX}"][data-theme="dark"]', name, name, foreground=False) for name in FALLBACK]
    return "\n".join(lines)


def primary_css(root: Path) -> str:
    lines = []
    for theme_id, theme in _themes(root).items():
        primary = theme["tokens"]["dark"]["primary"]
        soft = mix(primary, DARK_CARD, SOFT)
        dark_text = theme["tokens"]["dark"]["primary-foreground"]
        # light text on the toned button unless the theme's own (dark) button text reads better (Mint and Neutral have light primaries)
        text = LIGHT_TEXT if contrast(soft, LIGHT_TEXT) >= contrast(soft, dark_text) else dark_text
        selector = '[data-theme="dark"]' if theme_id == DEFAULT_THEME else f'[data-theme-color="{theme_id}"][data-theme="dark"]'
        lines.append(
            f"{selector}{{--nhimc-primary-soft:{soft};--nhimc-primary-soft-hover:{mix(primary, DARK_CARD, SOFT_HOVER)};--nhimc-primary-soft-foreground:{text}}}"
        )
    lines.append(
        '[data-theme="dark"] .btn.primary{border-color:var(--nhimc-primary-soft);background:var(--nhimc-primary-soft);color:var(--nhimc-primary-soft-foreground)}'
    )
    lines.append(
        '[data-theme="dark"] .btn.primary:hover:not(:disabled){border-color:var(--nhimc-primary-soft-hover);background:var(--nhimc-primary-soft-hover)}'
    )
    return "\n".join(lines)


def dark_tone_css(root: Path) -> str:
    return "\n".join((chip_css(root), accent_css(root), primary_css(root)))
