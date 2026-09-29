from pathlib import Path
import tempfile
import unittest

from scripts.canonical_frame import FramePayload, MenuItem, render_canonical_frame
from scripts.icon_overlay import (
    OVERLAY_PATH,
    append_symbol,
    icon_ids_in,
    merged_sprite,
    validate_symbol,
)

ROOT = Path(__file__).resolve().parents[2]


class ValidateSymbolTests(unittest.TestCase):
    def test_accepts_a_symbol_that_follows_the_style_contract(self):
        symbol = (
            '<symbol id="stretcher" viewBox="0 0 24 24" data-label="이송 침대" '
            'data-category="이송" data-updated-at="2026-09-29T00:00:00+09:00">'
            '<rect x="2" y="10" width="20" height="6" rx="1"/><path d="M6 16v3M18 16v3"/>'
            "</symbol>"
        )
        self.assertEqual([], validate_symbol(symbol))

    def test_rejects_wrong_viewbox(self):
        symbol = (
            '<symbol id="stretcher" viewBox="0 0 32 32" data-label="이송 침대" '
            'data-category="이송" data-updated-at="2026-09-29T00:00:00+09:00">'
            "<rect/></symbol>"
        )
        findings = validate_symbol(symbol)
        self.assertTrue(any("viewBox" in item for item in findings))

    def test_rejects_a_hardcoded_fill_or_stroke_that_would_override_currentColor(self):
        symbol = (
            '<symbol id="stretcher" viewBox="0 0 24 24" data-label="이송 침대" '
            'data-category="이송" data-updated-at="2026-09-29T00:00:00+09:00">'
            '<rect fill="#000"/></symbol>'
        )
        findings = validate_symbol(symbol)
        self.assertTrue(any("fill" in item for item in findings))

    def test_rejects_missing_required_data_attributes(self):
        symbol = '<symbol id="stretcher" viewBox="0 0 24 24"><rect/></symbol>'
        findings = validate_symbol(symbol)
        self.assertTrue(any("data-label" in item for item in findings))
        self.assertTrue(any("data-category" in item for item in findings))
        self.assertTrue(any("data-updated-at" in item for item in findings))


class MergedSpriteTests(unittest.TestCase):
    def test_merges_overlay_symbols_into_the_vendor_sprite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / OVERLAY_PATH).parent.mkdir(parents=True, exist_ok=True)
            (root / OVERLAY_PATH).write_text(
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<symbol id="stretcher" viewBox="0 0 24 24" data-label="이송 침대" '
                'data-category="이송" data-updated-at="2026-09-29T00:00:00+09:00"><rect/></symbol>'
                "</svg>",
                encoding="utf-8",
            )
            vendor_sprite = (
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<symbol id="dashboard" viewBox="0 0 24 24"><rect/></symbol>'
                "</svg>"
            )
            merged = merged_sprite(root, vendor_sprite)
            self.assertEqual({"dashboard", "stretcher"}, icon_ids_in(merged))

    def test_empty_overlay_leaves_the_vendor_sprite_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            vendor_sprite = (
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<symbol id="dashboard" viewBox="0 0 24 24"><rect/></symbol>'
                "</svg>"
            )
            self.assertEqual({"dashboard"}, icon_ids_in(merged_sprite(root, vendor_sprite)))


class AppendSymbolTests(unittest.TestCase):
    def test_append_adds_the_symbol_and_rejects_a_duplicate_id(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / OVERLAY_PATH).parent.mkdir(parents=True, exist_ok=True)
            (root / OVERLAY_PATH).write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")
            append_symbol(
                root,
                icon_id="stretcher",
                label="이송 침대",
                category="이송",
                inner_svg='<rect x="2" y="10" width="20" height="6" rx="1"/>',
                updated_at="2026-09-29T00:00:00+09:00",
            )
            self.assertIn("stretcher", icon_ids_in((root / OVERLAY_PATH).read_text(encoding="utf-8")))
            with self.assertRaisesRegex(ValueError, "already exists"):
                append_symbol(
                    root,
                    icon_id="stretcher",
                    label="이송 침대2",
                    category="이송",
                    inner_svg="<rect/>",
                    updated_at="2026-09-29T00:00:00+09:00",
                )

    def test_append_rejects_an_id_already_used_by_a_vendor_icon(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / OVERLAY_PATH).parent.mkdir(parents=True, exist_ok=True)
            (root / OVERLAY_PATH).write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")
            vendor = root / "vendor/nhimc-design/icons"
            vendor.mkdir(parents=True)
            (vendor / "nhimc-icons.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<symbol id="dashboard" viewBox="0 0 24 24"><rect/></symbol></svg>',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "already used by a vendor icon"):
                append_symbol(
                    root,
                    icon_id="dashboard",
                    label="대시보드2",
                    category="탐색",
                    inner_svg="<rect/>",
                    updated_at="2026-09-29T00:00:00+09:00",
                )


class OverlayIntegrationTests(unittest.TestCase):
    def test_an_overlay_icon_is_accepted_as_a_valid_menu_icon_end_to_end(self):
        overlay_path = ROOT / OVERLAY_PATH
        original = overlay_path.read_text(encoding="utf-8")
        try:
            append_symbol(
                ROOT,
                icon_id="test-overlay-icon",
                label="테스트 아이콘",
                category="테스트",
                inner_svg='<rect x="4" y="4" width="16" height="16" rx="2"/>',
                updated_at="2026-09-29T00:00:00+09:00",
            )
            payload = FramePayload(
                project_title="시험",
                menu=(MenuItem("home", "업무 현황", "test-overlay-icon", "#home"),),
                active_id="home",
                content_html='<main data-nhimc-role="content"></main>',
            )
            html = render_canonical_frame(ROOT, "left", payload)
            self.assertIn('id="test-overlay-icon"', html)
            self.assertIn('href="#test-overlay-icon"', html)
        finally:
            overlay_path.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
