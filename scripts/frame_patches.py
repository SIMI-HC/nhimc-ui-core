"""NHIMC UI Core patches applied on top of the vendored canonical Frame layouts.

The vendor mirror stays byte-identical to the pinned upstream commit. Every consumer (offline builder,
Web Runtime, Design Guide previews, parity tests) applies the same patches through apply_frame_patches(), so a
frameVersion always means the same Frame.

1.0.0  the Ilsan Hospital logo tile (white border) uses an 8px radius instead of 10px/9px.
1.0.1  PRESENTATION frames (presentation, presentation-vertical) own a Content Safe Area. Their Header
       (utility buttons) and Controller (slide dots and arrows) float above a full-bleed content slot, so AI
       Content ran under them.
1.1.0  Presentation Base Contract shared by both PRESENTATION frames; direction is the only difference:
       - Safe Area: the canonical slide (flex column, centred, animated) is padded by the space the Header and
         Controller occupy, so Content sits in the visual centre of the Safe Area. Content is never positioned
         by the page.
       - the scrollbar gutter is reserved on both edges so Content stays centred even when a slide scrolls.
       - the Frame names its direction (data-presentation-direction) and the flow direction variable
         (--presentation-flow-direction) used by the Presentation primitives.
       Slide lifecycle, transitions and navigation live in src/presentation/presentation-runtime.js.
"""
from __future__ import annotations

import re

LOGO_SELECTORS = ("brand-asset", "hospital-brand-logo", "brand-mark")
LOGO_RADIUS = "8px"
_OLD_RADIUS = re.compile(r"border-radius:(?:9|10)px")
_SLIDE_DOTS_COLUMN = re.compile(r"\.slide-dots\s*\{[^}]*flex-direction:\s*column")

SAFE_AREA_MARKER = "nhimc-presentation-safe-area"

# Sizes come from the Frame's own control rules: .utility (top/right 20px, 40px buttons),
# .slide-dots (20px from the edge, 26px thick pill) and .nav-arrow (20px from the edge, 48px; 8px and 38px
# below 768px). The last number is the breathing room between a control and Content.
_HORIZONTAL_SAFE_AREA = """
/* nhimc-presentation-safe-area: horizontal. Header = utility (top), Controller = slide dots (bottom) and arrows (sides). */
.app-shell{--presentation-flow-direction:row;--presentation-safe-top:calc(20px + 40px + 12px);--presentation-safe-bottom:calc(20px + 26px + 12px);--presentation-safe-inline:calc(20px + 48px + 12px)}
@media(max-width:767px){.app-shell{--presentation-safe-inline:calc(8px + 38px + 8px)}}
"""

_VERTICAL_SAFE_AREA = """
/* nhimc-presentation-safe-area: vertical. Header = utility (top right), Controller = prev/next arrows (top/bottom) and slide dots (right). */
.app-shell{--presentation-flow-direction:column;--presentation-safe-top:calc(20px + 48px + 12px);--presentation-safe-bottom:calc(20px + 48px + 12px);--presentation-safe-inline:calc(20px + 26px + 12px)}
@media(max-width:767px){.app-shell{--presentation-safe-top:calc(20px + 40px + 12px);--presentation-safe-bottom:calc(8px + 38px + 8px)}}
"""

# The canonical .slide is already a centred, animated, scrollable flex column. The Safe Area is its padding, so the
# slide (and its transition) still sweeps the whole canvas while Content stays clear of Header and Controller.
_SAFE_AREA_RULES = """.slide{padding:var(--presentation-safe-top) var(--presentation-safe-inline) var(--presentation-safe-bottom);scrollbar-gutter:stable both-edges}
"""


def _patch_logo_radius(layout: str) -> str:
    parts = layout.split("}")
    patched: list[str] = []
    for part in parts:
        if "{" in part:
            selector, body = part.rsplit("{", 1)
            if any(name in selector for name in LOGO_SELECTORS):
                body = _OLD_RADIUS.sub(f"border-radius:{LOGO_RADIUS}", body)
                part = selector + "{" + body
        patched.append(part)
    return "}".join(patched)


def is_presentation_layout(layout: str) -> bool:
    return 'class="slide-dots"' in layout and ".content-slot" in layout and 'data-nhimc-role="content-slot"' in layout


def _patch_presentation_safe_area(layout: str) -> str:
    if not is_presentation_layout(layout) or SAFE_AREA_MARKER in layout:
        return layout
    vertical = bool(_SLIDE_DOTS_COLUMN.search(layout))
    block = (_VERTICAL_SAFE_AREA if vertical else _HORIZONTAL_SAFE_AREA) + _SAFE_AREA_RULES
    end = layout.rindex("</style>")
    layout = layout[:end] + block + layout[end:]
    direction = "vertical" if vertical else "horizontal"
    return layout.replace('class="app-shell"', f'class="app-shell" data-presentation-direction="{direction}"', 1)


def apply_frame_patches(layout: str) -> str:
    return _patch_presentation_safe_area(_patch_logo_radius(layout))
