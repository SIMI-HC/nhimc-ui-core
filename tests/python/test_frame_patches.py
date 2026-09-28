from pathlib import Path
import re
import unittest

from scripts.canonical_frame import FRAME_FILES, render_canonical_frame, FramePayload, MenuItem
from scripts.frame_patches import LOGO_RADIUS, LOGO_SELECTORS, apply_frame_patches

ROOT = Path(__file__).resolve().parents[2]
LAYOUTS = ROOT / "vendor/nhimc-design/layouts"


def _logo_radii(css: str) -> list[str]:
    radii: list[str] = []
    for rule in css.split("}"):
        if "{" not in rule:
            continue
        selector, body = rule.rsplit("{", 1)
        if any(name in selector for name in LOGO_SELECTORS):
            radii.extend(re.findall(r"border-radius:([^;}]+)", body))
    return radii


class FramePatchTests(unittest.TestCase):
    def test_logo_tile_radius_is_8px_in_every_frame_that_has_one(self):
        checked = 0
        for name in sorted(set(FRAME_FILES.values())):
            original = (LAYOUTS / name).read_text(encoding="utf-8")
            patched = apply_frame_patches(original)
            radii = [value for value in _logo_radii(patched) if value != "0"]
            self.assertTrue(all(value == LOGO_RADIUS for value in radii), (name, radii))
            checked += bool(radii)
        self.assertGreaterEqual(checked, 5)

    def test_patch_changes_nothing_but_the_logo_radius(self):
        original = (LAYOUTS / "left.html").read_text(encoding="utf-8")
        patched = apply_frame_patches(original)
        self.assertEqual(
            re.sub(r"border-radius:(?:8|9|10)px", "R", original),
            re.sub(r"border-radius:(?:8|9|10)px", "R", patched),
        )
        self.assertEqual(2, sum(1 for a, b in zip(original.split("}"), patched.split("}")) if a != b))

    def test_rendered_frame_and_web_runtime_use_the_patched_layout(self):
        payload = FramePayload(
            project_title="시험", menu=(MenuItem("home", "홈", "home", "#home"),), active_id="home",
            content_html="<main data-nhimc-role=\"content\"></main>",
        )
        html = render_canonical_frame(ROOT, "left", payload)
        self.assertIn(f"border-radius:{LOGO_RADIUS}", html)
        self.assertNotRegex(html, r"\.brand \.brand-asset\{[^}]*border-radius:10px")
        runtime = (ROOT / "dist/nhimc-web.js").read_text(encoding="utf-8")
        self.assertNotIn("brand-asset{position:absolute;left:6px;top:50%;transform:translateY(-50%);display:block;width:auto;max-width:calc(100% - 12px);height:36px;padding:3px 5px;background:#fff;border-radius:10px", runtime)


if __name__ == "__main__":
    unittest.main()
