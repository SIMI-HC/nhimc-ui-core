from pathlib import Path
import unittest

from scripts import modal_stability as gate
from scripts.frame_patches import apply_frame_patches
from scripts.test_profiles import slow_test

ROOT = Path(__file__).resolve().parents[2]
LAYOUTS = ROOT / "vendor/nhimc-design/layouts"


class ModalStabilityStaticTests(unittest.TestCase):
    def setUp(self):
        self.blog = apply_frame_patches((LAYOUTS / "blog.html").read_text(encoding="utf-8"))

    def test_document_scroll_ignores_a_page_scroll_lock(self):
        document = 'html[data-scroll-owner="document"]'
        self.assertIn(document + "{overflow-y:auto!important}", self.blog)
        self.assertIn(document + " body{overflow:visible!important}", self.blog)

    def test_scroll_margin_applies_to_content_anchors_only(self):
        # a margin on every [id] made focusing the sticky header's help button scroll the page by 63px
        self.assertNotRegex(self.blog, r"(?<![\w\]\) ])\[id\]\{scroll-margin-top")
        self.assertIn(".content [id]{scroll-margin-top", self.blog)

    def test_matrix_covers_every_scrolling_frame_and_both_blog_owners(self):
        self.assertEqual(
            {("left", ""), ("left-blank", ""), ("left-dual", ""), ("top", ""), ("top-left", ""), ("blog", "main"), ("blog", "document")},
            set(gate.CASES),
        )


@slow_test
class ModalStabilityBrowserTests(unittest.TestCase):
    def test_help_sheet_and_mobile_menu_do_not_move_the_page_in_every_installed_browser(self):
        report = gate.run_modal_stability(ROOT)
        self.assertEqual([], report["problems"])
        self.assertEqual(len(gate.CASES) * len(gate.VIEWPORTS), report["cells"])


if __name__ == "__main__":
    unittest.main()
