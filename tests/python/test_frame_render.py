from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import canonical_frame, frame_patches
from scripts import frame_render as gate
from scripts.build_single_html import build_single_html
from scripts.canonical_frame import FramePayload, MenuItem, render_canonical_frame
from scripts.test_profiles import slow_test

ROOT = Path(__file__).resolve().parents[2]
LAYOUTS = ROOT / "vendor/nhimc-design/layouts"


def _built(frame: str, theme: str, mode: str = "light") -> str:
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder) / "source.html"
        source.write_text(gate.fragment(frame, mode, theme), encoding="utf-8", newline="\n")
        return build_single_html(ROOT, source, Path(folder) / "index.html").read_text(encoding="utf-8")


class FrameRenderStaticTests(unittest.TestCase):
    def test_theme_overlay_comes_after_every_frame_theme_block(self):
        html = _built("blog", "pear")
        overlay = html.index('data-nhimc-theme-color-bundle="canonical"')
        self.assertGreater(overlay, html.index("data-nhimc-theme-default"), "the Frame default colours would override the theme")
        self.assertIn('[data-theme-color="pear"]{--color-primary:#627F33', html[overlay:])
        self.assertNotIn('[data-theme-color="pear"]{', html[:overlay])

    def test_web_runtime_places_the_theme_overlay_last_too(self):
        runtime = (ROOT / "dist/nhimc-web.js").read_text(encoding="utf-8")
        self.assertIn("data-nhimc-theme-color-bundle", runtime)
        self.assertIn("themeCss", runtime)

    def test_blog_gets_header_icon_rules_and_blog_and_top_get_drawer_icon_rules(self):
        header_rule = ".topnav button svg{width:17px;height:17px;display:block;flex:none}"
        for name, adds_header_rule in (("blog.html", True), ("top.html", False)):
            patched = frame_patches.apply_frame_patches((LAYOUTS / name).read_text(encoding="utf-8"))
            added = patched.split(frame_patches.NAV_ICON_MARKER)[1]
            self.assertEqual(adds_header_rule, header_rule in added, name)
            self.assertIn(".nav-drawer nav button svg{width:18px;height:18px", added, name)
        self.assertIn(header_rule, (LAYOUTS / "top.html").read_text(encoding="utf-8"), "TOP already sizes its header icons")

    def test_frames_without_a_topnav_are_not_touched_by_the_icon_patch(self):
        for name in ("left.html", "left-blank.html", "top-left.html", "presentation.html", "presentation-vertical.html"):
            patched = frame_patches.apply_frame_patches((LAYOUTS / name).read_text(encoding="utf-8"))
            self.assertNotIn(frame_patches.NAV_ICON_MARKER, patched, name)

    def test_icon_menu_buttons_keep_an_accessible_name(self):
        payload = FramePayload(
            project_title="시험", menu=(MenuItem("home", "업무 현황", "home", "#home"),), active_id="home",
            content_html='<main data-nhimc-role="content"></main>',
        )
        html = render_canonical_frame(ROOT, "blog", payload)
        self.assertRegex(html, r'<button type="button" data-menu-id="home"[^>]*aria-label="업무 현황" title="업무 현황"')
        runtime = (ROOT / "dist/nhimc-web.js").read_text(encoding="utf-8")
        self.assertIn("""' aria-label="' + label + '" title="' + label""", runtime)


@slow_test
class FrameRenderBrowserTests(unittest.TestCase):
    def test_theme_colour_and_menu_icons_render_on_both_paths(self):
        report = gate.run_frame_render(ROOT, frames=("top", "blog", "left"), themes=("nhimc-default", "pear", "neutral"))
        self.assertEqual([], report["problems"])
        self.assertEqual(3 * 3 * 2 * 3 * 2, report["cells"])

    def test_the_gate_catches_unsized_blog_icons_and_a_lost_theme_colour(self):
        with mock.patch.object(canonical_frame, "apply_frame_patches", frame_patches._patch_logo_tile):
            with tempfile.TemporaryDirectory() as folder:
                cells = gate.build_cells(ROOT, Path(folder), frames=("blog",), themes=("pear",), modes=("light",), viewports=((1440, 900),), paths=("offline",))
                found = gate.problems(ROOT, cells, gate.measure(ROOT, cells))
        self.assertTrue(any("menu icon is" in item for item in found), found)


if __name__ == "__main__":
    unittest.main()
