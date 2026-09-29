import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

from scripts import blog_scroll_owner as gate
from scripts import canonical_frame, frame_patches
from scripts.canonical_frame import FRAME_FILES, FramePayload, MenuItem, render_canonical_frame
from scripts.frame_patches import BLOG_SCROLL_MARKER, apply_frame_patches
from scripts.test_profiles import slow_test

ROOT = Path(__file__).resolve().parents[2]
LAYOUTS = ROOT / "vendor/nhimc-design/layouts"


def _payload(owner: str = "main") -> FramePayload:
    return FramePayload(
        project_title="시험", menu=(MenuItem("news", "소식", "home", "#news"),), active_id="news",
        content_html='<main data-nhimc-role="content"><h1 id="top">소식</h1></main>', scroll_owner=owner,
    )


def _rules(css: str) -> list[tuple[str, str]]:
    return [tuple(rule.rsplit("{", 1)) for rule in css.split("}") if "{" in rule]


class BlogScrollOwnerStaticTests(unittest.TestCase):
    def setUp(self):
        self.blog = apply_frame_patches((LAYOUTS / "blog.html").read_text(encoding="utf-8"))

    def test_only_the_blog_frame_gets_the_scroll_owner_state(self):
        for name in sorted(set(FRAME_FILES.values())):
            patched = apply_frame_patches((LAYOUTS / name).read_text(encoding="utf-8"))
            self.assertEqual(name == "blog.html", BLOG_SCROLL_MARKER in patched, name)
        self.assertEqual(7, len(set(FRAME_FILES.values())), "the scroll owner must not add a layout variant")

    def test_default_is_main_scroll_with_a_100svh_shell_and_a_flex_none_header(self):
        self.assertRegex(self.blog, r'<html data-scroll-owner="main" ')
        self.assertIn("height:100svh", self.blog)
        rules = dict((selector.strip(), body) for selector, body in _rules(self.blog))
        self.assertIn("flex:none", rules[".site-header"])
        self.assertRegex(rules[".content"], r"flex:1;min-height:0;overflow:auto")

    def test_no_forced_transparent_styles_remain(self):
        self.assertNotIn("transparent!important", self.blog)
        self.assertNotIn("transparent !important", self.blog)
        self.assertIn("header:not(.site-header)", self.blog)

    def test_document_state_is_opaque_sticky_bordered_and_shadowed_by_tokens(self):
        rules = {selector.strip(): body for selector, body in _rules(self.blog)}
        header = rules['html[data-scroll-owner="document"] .site-header']
        self.assertIn("position:sticky", header)
        self.assertIn("border-bottom:1px solid var(--color-border-accent)", header)
        self.assertIn("box-shadow:var(--shadow-lg)", header)
        self.assertIn("--site-header-surface:var(--color-background)", rules['html[data-scroll-owner="document"] .app-shell'])
        self.assertIn("--shadow-lg:", self.blog, "the canonical shadow token must exist in the Frame")
        self.assertIn("scroll-margin-top:calc(var(--site-header-height) + 16px)", rules['html[data-scroll-owner="document"] [id]'])

    def test_sticky_is_never_combined_with_a_transparent_surface(self):
        for selector, body in _rules(self.blog):
            if "position:sticky" in body:
                self.assertNotIn("transparent", body, selector)
                self.assertNotRegex(body, r"background(?:-color)?:none", selector)

    def test_header_and_footer_contracts_are_untouched(self):
        original = (LAYOUTS / "blog.html").read_text(encoding="utf-8")
        body = lambda text: text[text.index("<body>"):]
        self.assertEqual(body(apply_frame_patches(original)), body(original))

    def test_patch_is_idempotent(self):
        self.assertEqual(self.blog, apply_frame_patches(self.blog))


class BlogScrollOwnerRenderTests(unittest.TestCase):
    def test_main_is_the_default_owner(self):
        self.assertIn('<html data-scroll-owner="main"', render_canonical_frame(ROOT, "blog", _payload()))

    def test_document_owner_is_set_on_the_root_and_nowhere_else(self):
        html = render_canonical_frame(ROOT, "blog", _payload("document"))
        self.assertIn('<html data-scroll-owner="document"', html)
        self.assertEqual(1, html.count('data-scroll-owner="document"') - html.count('html[data-scroll-owner="document"]'))

    def test_other_frames_reject_the_document_owner_and_bad_values_are_refused(self):
        with self.assertRaises(ValueError):
            render_canonical_frame(ROOT, "left", _payload("document"))
        with self.assertRaises(ValueError):
            render_canonical_frame(ROOT, "blog", _payload("body"))

    def test_registry_records_the_new_frame_version_and_state(self):
        frame = next(item for item in json.loads((ROOT / "registry/frames.json").read_text(encoding="utf-8"))["frames"] if item["id"] == "nhimc-blog")
        self.assertEqual("1.4.0", frame["version"])
        self.assertEqual(["main", "document"], frame["scrollOwners"]["states"])
        self.assertEqual("main", frame["scrollOwners"]["default"])


@slow_test
class BlogScrollOwnerBrowserTests(unittest.TestCase):
    def test_main_and_document_scroll_at_375_768_and_1440_in_light_and_dark(self):
        report = gate.run_blog_scroll_owner(ROOT)
        self.assertEqual([], report["problems"])
        self.assertEqual(24, report["cells"])

    def test_document_regression_fails_without_the_patch_so_the_gate_is_real(self):
        with mock.patch.object(canonical_frame, "apply_frame_patches", frame_patches._patch_logo_tile):
            with tempfile.TemporaryDirectory() as folder:
                cells = gate.build_cells(ROOT, Path(folder), viewports=((1440, 900),), themes=("light",), modes=("offline",))
                found = gate.problems(cells, gate.measure(ROOT, cells))
        self.assertTrue(any(item.startswith("document|") and "scroll" in item for item in found), found)


if __name__ == "__main__":
    unittest.main()
