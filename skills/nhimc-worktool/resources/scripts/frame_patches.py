"""NHIMC UI Core patches applied on top of the vendored canonical Frame layouts.

The vendor mirror stays byte-identical to the pinned upstream commit. Every consumer (offline builder,
Web Runtime, Design Guide previews, parity tests) applies the same patches through apply_frame_patches(), so a
frameVersion always means the same Frame.

1.0.0  the Ilsan Hospital logo tile (white border) uses an 8px radius instead of 10px/9px.
1.4.0  the white logo tile is removed altogether (no padding, white background, shadow or radius around the logo).
       LEFT and LEFT BLANK: the sidebar/shell colour fades from lighter (top) to darker (bottom) so the logo's blue block
       stays visible; no panel or border around the logo. LEFT BLANK keeps its canonical collapsed rail (toggle only).
       DEFAULT: the header divider gets 10px on each side (it sat 2px from the project name).
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
1.2.0  BLOG scroll owner. The scroll owner is a state of the one BLOG Frame (html[data-scroll-owner]), not a new
       layout variant:
       - "main" (default): app-shell is 100svh, the translucent SiteHeader is flex:none and Main scrolls.
       - "document": the page scrolls; the SiteHeader becomes sticky on the same translucent (40%) canvas surface with a
         backdrop blur, a --color-border-accent bottom border and the canonical --shadow-lg. Sticky + fully transparent is
         never produced.
         Anchors get a scroll-margin that clears the sticky header.
       The forced `background:transparent!important` theme rules on .site-header / .statusbar are removed; the header
       surface is now the semantic token --site-header-surface.
1.3.0  Menu icons (BLOG and TOP). The BLOG nav had no rule for its svg icons (TOP has 17px beside the label), so menu icons
       rendered at their intrinsic size over the label. BLOG now lays the icon out like TOP; the label is hidden below
       1024px as in TOP, and the menu buttons carry aria-label/title so an icon-only menu keeps an accessible name.
       The mobile drawer menu icons of BLOG and TOP (18px beside the label) were unsized too.
1.5.0  SiteHeader height 64px -> 56px. BLOG takes it from --site-header-height (so the sticky offset follows), TOP from
       .site-header and DEFAULT (top-left) from the first app-shell grid row, on desktop and mobile.
       Registry versions: BLOG 1.5.0, TOP and DEFAULT 1.4.0.
1.6.0  BLOG SiteHeader is translucent: --site-header-surface is the page canvas colour of each theme (#f4f7fa / #0a0a0a) at 40% alpha
       (rgba, no color-mix: the offline target Edge is 92) plus a 12px backdrop blur, in both scroll owners. The sticky
       document header keeps its border and shadow; only fully transparent sticky headers stay forbidden.
       Main now extends under the header (negative margin + header-height padding-top, header z-index 8) so scrolling
       content is really seen through the translucent header in both owners; with the Main scroll it used to sit below.
       Registry version: BLOG 1.6.0.
1.7.0  BLOG layout: Content is one centred column (--blog-width 1080px, also the Page primitive's --page-max) and the
       SiteHeader lines up with it: brand on the left, the menu pushed to the right next to the utilities. Registry
       version: BLOG 1.7.0.
1.2.0  PRESENTATION frames (presentation, presentation-vertical): the Ilsan Hospital logo (the TOP Frame's SVG, 32px) sits
       top-left on the same row as the help button. Registry versions: PRESENTATION and PRESENTATION VERTICAL 1.2.0.
"""
from __future__ import annotations

from pathlib import Path
import re

LOGO_SELECTORS = ("brand-asset", "hospital-brand-logo", "brand-mark")
# The canonical logo sits on a white rounded tile (padding, #fff, radius, shadow). The tile is removed: the logo is drawn
# as is, without a white border around it.
_LOGO_TILE = (
    (re.compile(r"padding:3px(?: 5px)?(?=[;}]|$)"), "padding:0"),
    (re.compile(r"background:#fff(?=[;}]|$)"), "background:transparent"),
    (re.compile(r"box-shadow:0 1px 4px rgba\(0,0,0,\.16\)"), "box-shadow:none"),
    (re.compile(r"border-radius:(?:8|9|10)px"), "border-radius:0"),
)
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


def _patch_logo_tile(layout: str) -> str:
    parts = layout.split("}")
    patched: list[str] = []
    for part in parts:
        if "{" in part:
            selector, body = part.rsplit("{", 1)
            if any(name in selector for name in LOGO_SELECTORS):
                for pattern, replacement in _LOGO_TILE:
                    body = pattern.sub(replacement, body)
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


# BLOG, TOP and DEFAULT (top-left) SiteHeader: the canonical 64px is cut to 56px (the same height as the mobile drawer head).
SITE_HEADER_HEIGHT = 56

SCROLL_OWNERS = ("main", "document")
BLOG_SCROLL_MARKER = "nhimc-blog-scroll-owner"
_BLOG_HEADER = re.compile(r"\.site-header\{flex:0 0 auto;height:64px;background:transparent")
_FORCED_TRANSPARENT = re.compile(r'\[data-theme="(?:light|dark)"\] \.(?:site-header|statusbar)\{background(?:-color)?:transparent!important\}\n?')
_DOCUMENT = 'html[data-scroll-owner="document"]'

# ponytail: the state lives on <html> so the root scroller can be freed without :has() (the offline target Edge is 92).
_BLOG_SCROLL_OWNER_RULES = f"""
/* {BLOG_SCROLL_MARKER}: main (default) keeps the app-shell at 100svh and Main scrolls; document lets the page scroll. */
.app-shell{{--site-header-height:{SITE_HEADER_HEIGHT}px;--site-header-surface:rgba(244,247,250,.4)}}
[data-theme="dark"] .app-shell{{--site-header-surface:rgba(10,10,10,.4)}}
.site-header{{flex:none;height:var(--site-header-height);background:var(--site-header-surface);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);position:relative;z-index:8}}
.content{{margin-top:calc(var(--site-header-height) * -1);padding-top:calc(var(--site-header-height) + 24px)}}
[id]{{scroll-margin-top:calc(var(--site-header-height) + 16px)}}
{_DOCUMENT},{_DOCUMENT} body{{height:auto;overflow:visible}}
{_DOCUMENT}{{scrollbar-gutter:stable;scrollbar-width:thin;scrollbar-color:var(--color-scrollbar-thumb) var(--color-scrollbar-track)}}
{_DOCUMENT} .app-shell{{height:auto;min-height:100vh;min-height:100svh}}
{_DOCUMENT} .site-header{{position:sticky;top:0;border-bottom:1px solid var(--color-border-accent);box-shadow:var(--shadow-lg)}}
{_DOCUMENT} .content{{flex:1 0 auto;overflow:visible}}
{_DOCUMENT} [id]{{scroll-margin-top:calc(var(--site-header-height) + 16px)}}
/* BLOG layout: one centred reading column; the header lines up with it (brand left, menu right, utilities last). */
.app-shell{{--blog-width:1080px;--page-max:var(--blog-width);--blog-edge:max(24px,calc((100% - var(--scrollbar-inline-size,10px) - var(--blog-width)) / 2))}}
{_DOCUMENT} .app-shell{{--blog-edge:max(24px,calc((100% - var(--blog-width)) / 2))}}
.content [data-nhimc-role="content"]{{padding-inline:0}}
.content{{grid-template-columns:minmax(0,var(--blog-width));justify-content:center}}
.site-header{{padding-inline:var(--blog-edge) calc(var(--blog-edge) + var(--scrollbar-inline-size,10px))}}
{_DOCUMENT} .site-header{{padding-inline:var(--blog-edge)}}
.spacer{{order:1}}
.topnav{{order:2;margin-left:0;margin-right:12px}}
.utility{{order:3}}
"""


def is_blog_layout(layout: str) -> bool:
    return 'class="topnav"' in layout and bool(_BLOG_HEADER.search(layout))


def _patch_blog_scroll_owner(layout: str) -> str:
    if not is_blog_layout(layout) or BLOG_SCROLL_MARKER in layout:
        return layout
    layout = _FORCED_TRANSPARENT.sub("", layout)
    # the theme block paints every <header> with the card surface; the SiteHeader is styled by its own token instead
    layout = re.sub(r'(\[data-theme="(?:light|dark)"\] )header,', r"\g<1>header:not(.site-header),", layout)
    end = layout.rindex("</style>")
    layout = layout[:end] + _BLOG_SCROLL_OWNER_RULES + layout[end:]
    return layout.replace("<html ", '<html data-scroll-owner="main" ', 1)


NAV_ICON_MARKER = "nhimc-nav-icons"
# The TOP Frame sizes its header menu icons (17px, label beside it). The BLOG copy of the same nav lost that rule, so a
# menu with icons rendered its svg at the intrinsic size (56px) over the label. Both frames also had no size rule for
# the icons of the mobile drawer menu (184px once opened). Same size and layout as the rest of the Frame system.
_HEADER_NAV_ICON_RULES = """.topnav button{display:flex;align-items:center;gap:7px}
.topnav button svg{width:17px;height:17px;display:block;flex:none}
"""
_DRAWER_NAV_ICON_RULES = """.nav-drawer nav button{display:flex;align-items:center;gap:10px}
.nav-drawer nav button svg{width:18px;height:18px;display:block;flex:none}
"""


def _patch_nav_icons(layout: str) -> str:
    if 'class="topnav"' not in layout or NAV_ICON_MARKER in layout:
        return layout
    rules = (_HEADER_NAV_ICON_RULES if is_blog_layout(layout) else "") + _DRAWER_NAV_ICON_RULES
    end = layout.rindex("</style>")
    return layout[:end] + f"\n/* {NAV_ICON_MARKER} */\n" + rules + layout[end:]


SIDEBAR_GRADIENT_MARKER = "nhimc-sidebar-gradient"
# Without the white tile the logo's own navy block melted into the flat navy sidebar. The sidebar/shell colour now fades
# from lighter (top, where the logo is) to darker (bottom) so the logo's blue stays visible. Translucent overlays on the
# sidebar token, so every colour theme keeps working. Desktop / tablet only: the mobile shell keeps its canvas.
_SIDEBAR_GRADIENT_RULES = """:root{--sidebar-gradient-top:rgba(255,255,255,.16);--sidebar-gradient-bottom:rgba(0,0,0,.26)}
[data-theme="dark"]{--sidebar-gradient-top:rgba(255,255,255,.07);--sidebar-gradient-bottom:rgba(0,0,0,.30)}
@media (min-width:768px){.app-shell{background-image:linear-gradient(180deg,var(--sidebar-gradient-top),var(--sidebar-gradient-bottom))}}
"""
DEFAULT_HEADER_MARKER = "nhimc-default-header-spacing"
# DEFAULT Frame: the divider between the logo and the project name sat 2px from each side; give it breathing room.
_DEFAULT_HEADER_RULES = ".header-divider{margin:0 10px}\n"


def _patch_sidebar_gradient(layout: str) -> str:
    if "sidebar-decor" not in layout or ".brand-asset" not in layout or SIDEBAR_GRADIENT_MARKER in layout:
        return layout
    end = layout.rindex("</style>")
    return layout[:end] + f"\n/* {SIDEBAR_GRADIENT_MARKER} */\n" + _SIDEBAR_GRADIENT_RULES + layout[end:]


def _patch_default_header_spacing(layout: str) -> str:
    if ".header-divider{" not in layout or DEFAULT_HEADER_MARKER in layout:
        return layout
    end = layout.rindex("</style>")
    return layout[:end] + f"\n/* {DEFAULT_HEADER_MARKER} */\n" + _DEFAULT_HEADER_RULES + layout[end:]


_TOP_HEADER = re.compile(r"(\.site-header\{flex:0 0 auto;)height:64px(;background:#fff)")
_DEFAULT_ROWS = "grid-template-rows:64px minmax(0,1fr) 28px"


def _patch_header_height(layout: str) -> str:
    """TOP sets the height on .site-header, DEFAULT on the first app-shell grid row; BLOG takes it from its scroll-owner token."""
    layout = _TOP_HEADER.sub(rf"\g<1>height:{SITE_HEADER_HEIGHT}px\g<2>", layout)
    return layout.replace(_DEFAULT_ROWS, f"grid-template-rows:{SITE_HEADER_HEIGHT}px minmax(0,1fr) 28px")


PRESENTATION_LOGO_MARKER = "nhimc-presentation-logo"
_TOP_LAYOUT = Path(__file__).resolve().parents[1] / "vendor/nhimc-design/layouts/top.html"
_LOGO_SVG = re.compile(r'<svg class="hospital-brand-logo".*?</svg>', re.DOTALL)
# Same row as the help button (.utility: top:20px, 40px buttons); the logo is the TOP Frame's own SVG, no tile.
_PRESENTATION_LOGO_RULES = f"""/* {PRESENTATION_LOGO_MARKER} */
.brand-logo{{position:absolute;top:20px;left:20px;height:40px;display:flex;align-items:center;z-index:6}}
.brand-logo .hospital-brand-logo{{width:auto;height:32px;display:block;flex:none}}
@media(max-width:767px){{.brand-logo .hospital-brand-logo{{height:26px}}}}
"""


def _patch_presentation_logo(layout: str) -> str:
    if not is_presentation_layout(layout) or PRESENTATION_LOGO_MARKER in layout:
        return layout
    logo = _LOGO_SVG.search(_TOP_LAYOUT.read_text(encoding="utf-8"))
    if logo is None:
        raise ValueError("hospital logo not found in the TOP layout")
    end = layout.rindex("</style>")
    layout = layout[:end] + _PRESENTATION_LOGO_RULES + layout[end:]
    return layout.replace('<div class="utility">', f'<div class="brand-logo">{logo.group(0)}</div><div class="utility">', 1)


def apply_frame_patches(layout: str) -> str:
    patched = _patch_nav_icons(_patch_blog_scroll_owner(_patch_presentation_logo(_patch_presentation_safe_area(_patch_logo_tile(layout)))))
    return _patch_header_height(_patch_default_header_spacing(_patch_sidebar_gradient(patched)))
