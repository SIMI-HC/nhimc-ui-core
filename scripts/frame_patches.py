"""NHIMC UI Core patches applied on top of the vendored canonical Frame layouts.

The vendor mirror stays byte-identical to the pinned upstream commit. Every consumer (offline builder,
Web Runtime, Design Guide previews) applies the same patches through this one function, so a frameVersion
always means the same Frame.

1.0.0: the Ilsan Hospital logo tile (white border) uses an 8px radius instead of 10px/9px.
"""
from __future__ import annotations

import re

LOGO_SELECTORS = ("brand-asset", "hospital-brand-logo", "brand-mark")
LOGO_RADIUS = "8px"
_OLD_RADIUS = re.compile(r"border-radius:(?:9|10)px")


def apply_frame_patches(layout: str) -> str:
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
