"""Generate dist/nhimc-web.js from the canonical sources.

The web runtime lets a web AI host finish in the chat: it writes Content plus one
<script src> tag, and the runtime wraps it in the canonical Frame at load time.
Every asset (Frame layout, Font, Icon sprite, Logo, Theme, Component CSS) is read
from the same single sources the offline builder uses. Nothing is authored here.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_single_html import _font_css, _upstream, _verified_vendor_bytes
from scripts.canonical_frame import FRAME_FILES
from scripts.frame_patches import apply_frame_patches
from scripts.theme_colors import theme_color_css, theme_color_ids

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path("src/web/nhimc-web.template.js")
OUTPUT = Path("dist/nhimc-web.js")
CDN_BASE = "https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core"


def build_web_runtime(root: Path = ROOT) -> Path:
    root = root.resolve()
    _, digests = _upstream(root)
    layouts = {
        Path(name).stem: apply_frame_patches(_verified_vendor_bytes(root, f"vendor/nhimc-design/layouts/{name}", digests).decode("utf-8"))
        for name in sorted(set(FRAME_FILES.values()))
    }
    sprite = _verified_vendor_bytes(root, "vendor/nhimc-design/icons/nhimc-icons.svg", digests).decode("utf-8")
    runtime = (root / "src/generated/frame/frame-runtime.js").read_text(encoding="utf-8")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    font_base = f"{CDN_BASE}@v{version}/vendor/nhimc-design/fonts"
    css = "\n".join(
        (
            (root / "src/generated/components/components.css").read_text(encoding="utf-8"),
            _font_css(root, digests, font_base),
            (root / "src/layouts/primitives.css").read_text(encoding="utf-8"),
            theme_color_css(root),
        )
    )
    data = {
        "version": version,
        "fontBase": font_base,
        "layouts": layouts,
        "themeColors": theme_color_ids(root),
        "sprite": sprite,
        "runtime": runtime,
        "css": css,
        "icons": sorted(set(re.findall(r'<symbol\s+id="([a-z0-9-]+)"', sprite))),
    }
    template = (root / TEMPLATE).read_text(encoding="utf-8")
    payload = "const D = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";"
    if "/*__DATA__*/" not in template:
        raise ValueError("web runtime template is missing its data anchor")
    output = root / OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace("/*__DATA__*/", payload, 1), encoding="utf-8", newline="\n")
    return output


def main() -> int:
    print(f"web runtime: {build_web_runtime()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
