from pathlib import Path
import unittest

from scripts.derived_frames import _DUAL_CSS
from scripts.frame_patches import apply_frame_patches

ROOT = Path(__file__).resolve().parents[2]


class FrameFixTests(unittest.TestCase):
    def test_top_and_blog_hamburger_names_its_colour(self):
        for name in ("top", "blog"):
            layout = apply_frame_patches((ROOT / f"vendor/nhimc-design/layouts/{name}.html").read_bytes().decode("utf-8"))
            for rule in (".mobile-menu{display:none;", ".nav-drawer-head .close{", ".nav-drawer nav button{"):
                self.assertIn("background:transparent;color:var(--fg);", layout.split(rule, 1)[1][:90], f"{name} {rule}")

    def test_blog_header_is_symmetric_on_a_narrow_screen(self):
        layout = apply_frame_patches((ROOT / "vendor/nhimc-design/layouts/blog.html").read_bytes().decode("utf-8"))
        self.assertIn("padding-inline:var(--blog-edge) max(24px,calc(var(--blog-edge-raw) + var(--scrollbar-inline-size,10px)))", layout)

    def test_left_dual_drawer_keeps_its_labels(self):
        self.assertIn(".mobile-panel .nav-label{position:static;", _DUAL_CSS)


if __name__ == "__main__":
    unittest.main()
