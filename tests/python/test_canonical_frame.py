import re
import unittest
from pathlib import Path

from scripts.canonical_frame import FramePayload, MenuItem, render_canonical_frame, render_layout


ROOT = Path(__file__).resolve().parents[2]


def sample_payload(icon: str = "ambulance") -> FramePayload:
    return FramePayload(
        project_title="병원 이송업무",
        menu=(MenuItem("transport", "이송 현황", icon, "#transport"),),
        active_id="transport",
        content_html='<section data-screen-panel="transport"><h1>이송업무 관리</h1></section>',
    )


class CanonicalFrameTests(unittest.TestCase):
    def test_all_canonical_layouts_have_exactly_one_content_anchor(self):
        for path in sorted((ROOT / "vendor/nhimc-design/layouts").glob("*.html")):
            with self.subTest(layout=path.name):
                rendered = render_canonical_frame(ROOT, path.stem, sample_payload())
                self.assertEqual(
                    1,
                    len(re.findall(r'<[^>]+data-nhimc-role="content-slot"', rendered)),
                )
                self.assertIn("이송업무 관리", rendered)

    def test_only_business_owned_regions_change(self):
        source = (ROOT / "vendor/nhimc-design/layouts/left.html").read_text(encoding="utf-8")
        result = render_canonical_frame(ROOT, "left", sample_payload())

        self.assertEqual(source[: source.index("<body>")], result[: result.index("<body>")])
        self.assertIn('data-nhimc-role="app-shell"', result)
        self.assertIn('data-nhimc-role="sidebar"', result)
        self.assertIn('data-nhimc-role="site-header"', result)
        self.assertIn('data-nhimc-role="statusbar"', result)
        self.assertIn("이송업무 관리", result)

    def test_missing_or_duplicate_anchor_fails_closed(self):
        valid = '<main data-nhimc-role="content-slot">old</main>'
        for broken in ("<main>old</main>", valid + valid):
            with self.subTest(count=broken.count("content-slot")):
                with self.assertRaisesRegex(ValueError, "content-slot.*exactly once"):
                    render_layout(broken, sample_payload(), icon_ids={"ambulance"})

    def test_menu_icons_render_canonical_svg_use_elements(self):
        result = render_canonical_frame(ROOT, "left", sample_payload())
        self.assertIn('href="#ambulance"', result)
        self.assertNotIn("☰", result)
        self.assertNotIn("‹", result)

    def test_payload_rejects_unknown_icon_and_unsafe_menu_values(self):
        with self.assertRaisesRegex(ValueError, "unknown canonical icon"):
            render_canonical_frame(ROOT, "left", sample_payload("not-a-canonical-icon"))
        for href in ("https://example.com", "javascript:alert(1)", "/absolute"):
            payload = FramePayload(
                project_title="업무",
                menu=(MenuItem("transport", "이송", "ambulance", href),),
                active_id="transport",
                content_html="<p>content</p>",
            )
            with self.subTest(href=href):
                with self.assertRaisesRegex(ValueError, "safe fragment"):
                    render_canonical_frame(ROOT, "left", payload)

    def test_runtime_contract_is_embedded(self):
        result = render_canonical_frame(ROOT, "left", sample_payload())
        self.assertIn("window.NhimcCanonicalFrame", result)
        self.assertIn("setActive", result)
        self.assertIn("setStatus", result)
        self.assertIn("setTheme", result)


if __name__ == "__main__":
    unittest.main()
