import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.add_canonical_icon import add_canonical_icon
from scripts.icon_overlay import OVERLAY_PATH, icon_ids_in

ROOT = Path(__file__).resolve().parents[2]


class AddCanonicalIconTests(unittest.TestCase):
    def _fixture_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / OVERLAY_PATH).parent.mkdir(parents=True, exist_ok=True)
        (root / OVERLAY_PATH).write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")
        gallery_source = ROOT / "src/guide/upstream/gallery-data.json"
        gallery_target = root / "src/guide/upstream/gallery-data.json"
        gallery_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(gallery_source, gallery_target)
        return root

    def test_adds_the_symbol_and_the_gallery_entry(self):
        root = self._fixture_root()
        add_canonical_icon(
            root,
            icon_id="stretcher",
            label="이송 침대",
            category="이송",
            inner_svg='<rect x="2" y="10" width="20" height="6" rx="1"/>',
            updated_at="2026-09-29T00:00:00+09:00",
        )
        overlay = (root / OVERLAY_PATH).read_text(encoding="utf-8")
        self.assertIn("stretcher", icon_ids_in(overlay))
        gallery = json.loads((root / "src/guide/upstream/gallery-data.json").read_text(encoding="utf-8"))
        entry = next(item for item in gallery["icons"] if item["id"] == "stretcher")
        self.assertEqual("이송 침대", entry["label"])
        self.assertEqual("이송", entry["category"])
        self.assertEqual("sky", entry["tone"])

    def test_rejects_unknown_tone(self):
        root = self._fixture_root()
        with self.assertRaisesRegex(ValueError, "unknown tone"):
            add_canonical_icon(
                root,
                icon_id="stretcher",
                label="이송 침대",
                category="이송",
                inner_svg="<rect/>",
                tone="not-a-real-tone",
                updated_at="2026-09-29T00:00:00+09:00",
            )

    def test_rejects_a_style_contract_violation(self):
        root = self._fixture_root()
        with self.assertRaisesRegex(ValueError, "style contract"):
            add_canonical_icon(
                root,
                icon_id="stretcher",
                label="이송 침대",
                category="이송",
                inner_svg='<rect fill="#000"/>',
                updated_at="2026-09-29T00:00:00+09:00",
            )


if __name__ == "__main__":
    unittest.main()
