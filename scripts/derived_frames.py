"""Frames derived from the vendored LEFT layout, so the vendor mirror stays byte-identical to upstream.

left-dual: LEFT with an icon rail (icon + label) and a second panel listing the selected group's screens.
The base layout is patched (apply_frame_patches) after the derivation, like every other Frame.
"""
from __future__ import annotations

from pathlib import Path

DERIVED_BASE = {"left-dual": "left"}
DUAL_RUNTIME = "src/frames/dual-runtime.js"

_DUAL_CSS = """
/* nhimc-left-dual: icon rail + group panel. The menu is rebuilt from the flat LEFT links by src/frames/dual-runtime.js. */
.app-shell{--rail-width:64px;--brand-row:56px;--panel-width:224px;grid-template-columns:calc(var(--rail-width) + var(--panel-width)) minmax(0,1fr);padding:0}
.sidebar{display:grid;grid-template-columns:var(--rail-width) var(--panel-width);grid-template-rows:var(--brand-row) minmax(0,1fr);padding:0;transition:grid-template-columns var(--motion-base) ease-in-out}
.sidebar-decor{display:none}
.sidebar>.brand{grid-area:1/1;height:var(--brand-row)}
.brand .brand-row{opacity:0;visibility:hidden}
.brand .brand-mark{width:36px;height:36px;max-width:36px;padding:0;border-radius:8px;box-shadow:none;opacity:1;visibility:visible}
.sidebar>.sidebar-nav{display:contents}
.rail-list{grid-area:2/1;display:flex;flex-direction:column;align-items:center;gap:14px;padding:20px 0;overflow-x:hidden;overflow-y:auto;scrollbar-width:none}
.rail-list::-webkit-scrollbar,.sub-group::-webkit-scrollbar{display:none}
.rail-link{width:44px;height:44px;display:grid;place-items:center;border-radius:12px;color:var(--color-sidebar-brand-foreground-70);text-decoration:none;transition:background var(--motion-fast) ease-in-out,color var(--motion-fast) ease-in-out}
.rail-link svg{width:22px;height:22px;display:block}
.rail-link:hover{background:var(--color-sidebar-brand-10);color:var(--color-sidebar-brand-foreground)}
.rail-link[aria-current="page"]{background:var(--color-sidebar-brand-18);color:var(--color-sidebar-brand-foreground)}
.rail-label{display:none}
.sub-lists{grid-area:1/2/3/3;position:relative;min-width:0;min-height:0;overflow:hidden;display:grid;grid-template-rows:minmax(0,1fr);background:var(--color-card);color:var(--color-card-foreground);border-right:1px solid var(--color-border);transition:opacity var(--motion-fast) ease-in-out,border-color var(--motion-base) ease-in-out}
.sub-group{width:var(--panel-width);min-height:0;padding:0 10px 12px;overflow-y:auto;scrollbar-width:none;display:grid;align-content:start;gap:2px}.sub-group[hidden]{display:none}
.sub-title{position:sticky;top:0;z-index:1;height:var(--header-height);margin:0 -10px 8px;padding:0 52px 0 20px;display:flex;align-items:center;background:var(--color-card);font-size:15px;font-weight:700}
.sub-lists>.collapse-button{position:absolute;top:6px;right:8px;z-index:2;display:inline-flex;color:inherit}
.sub-lists .nav-link{min-height:36px;padding:6px 12px;border-radius:8px}
.sub-lists .nav-link.is-nested{padding-left:28px}
.sub-lists .nav-link:hover,.sub-lists .nav-link[aria-current="page"]{background:var(--color-secondary)}
.sub-lists .nav-link[aria-current="page"]{font-weight:700}
.sub-lists .nav-chip{display:none}.sub-lists .nav-label{max-width:none}
.sidebar-inset{height:100vh;height:100svh;border:0;border-radius:0}
.app-shell.is-collapsed{grid-template-columns:var(--rail-width) minmax(0,1fr)}
.is-collapsed .sidebar{grid-template-columns:var(--rail-width) 0}
.is-collapsed .sub-lists{opacity:0;border-right-color:transparent;visibility:hidden;transition:opacity var(--motion-fast) ease-in-out,border-color var(--motion-base) ease-in-out,visibility 0s linear var(--motion-base)}
@media (max-height:760px){.rail-list{gap:6px;padding:12px 0}.rail-link{width:40px;height:40px}.rail-link svg{width:20px;height:20px}}
@media (max-width:1023px){.app-shell{grid-template-columns:minmax(0,1fr);background:var(--color-canvas)}body{background:var(--color-canvas)}.sidebar{display:none}.site-header{padding:0 10px}.mobile-menu{display:inline-flex}.utility span{display:none}.utility{width:36px;padding:0}.main{padding:20px 12px}.statusbar{padding:0 12px}}
"""

# Demo menu of the static preview: the link ids already in left.html, grouped under the first rail item.
_DEMO_CHILDREN = {"lab-values": "clinical-criteria", "stopped-medications": "clinical-criteria"}


def _insert(text: str, marker: str, addition: str) -> str:
    index = text.rindex(marker)
    return text[:index] + addition + text[index:]


def dual_runtime(root: Path | None = None) -> str:
    return ((root or Path(__file__).resolve().parents[1]) / DUAL_RUNTIME).read_text(encoding="utf-8")


def variant_runtime(kind: str, root: Path | None = None) -> str:
    return dual_runtime(root) if kind == "left-dual" else ""


def derive_layout(kind: str, base: str, *, root: Path | None = None) -> str:
    if kind == "left-dual":
        layout = base.replace('class="app-shell"', 'class="app-shell" data-frame-variant="dual"', 1)
        for child, parent in _DEMO_CHILDREN.items():
            layout = layout.replace(f'data-screen-target="{child}"', f'data-screen-target="{child}" data-parent-id="{parent}"', 1)
        layout = _insert(layout, "</style>", _DUAL_CSS)
        return _insert(layout, "</script>", "\n" + dual_runtime(root) + "\n")
    raise ValueError(f"not a derived frame: {kind}")
