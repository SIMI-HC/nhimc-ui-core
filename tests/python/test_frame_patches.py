from pathlib import Path
import re
import unittest

from scripts.canonical_frame import FRAME_FILES, render_canonical_frame, FramePayload, MenuItem
from scripts import frame_patches
from scripts.frame_patches import LOGO_SELECTORS, apply_frame_patches

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
    def test_logo_has_no_white_tile_in_every_frame_that_has_one(self):
        checked = 0
        for name in sorted(set(FRAME_FILES.values())):
            patched = frame_patches._patch_logo_tile((LAYOUTS / name).read_text(encoding="utf-8"))
            for rule in patched.split("}"):
                if "{" not in rule:
                    continue
                selector, body = rule.rsplit("{", 1)
                if not any(logo in selector for logo in LOGO_SELECTORS):
                    continue
                checked += 1
                self.assertNotRegex(body, r"background:#fff(?=[;}]|$)", (name, selector))
                self.assertNotRegex(body, r"padding:3px", (name, selector))
                self.assertNotIn("box-shadow:0 1px 4px", body, (name, selector))
                self.assertNotRegex(body, r"border-radius:(?:8|9|10)px", (name, selector))
        self.assertGreaterEqual(checked, 5)

    def test_patch_only_touches_logo_rules(self):
        original = (LAYOUTS / "left.html").read_text(encoding="utf-8")
        patched = frame_patches._patch_logo_tile(original)
        changed = [(a, b) for a, b in zip(original.split("}"), patched.split("}")) if a != b]
        self.assertEqual(2, len(changed))
        for before, _ in changed:
            self.assertTrue(any(logo in before.rsplit("{", 1)[0] for logo in LOGO_SELECTORS), before[-80:])

    def test_sidebar_logo_sits_on_a_translucent_panel_and_left_blank_keeps_its_mark_when_collapsed(self):
        for name in ("left.html", "left-blank.html"):
            patched = apply_frame_patches((LAYOUTS / name).read_text(encoding="utf-8"))
            added = patched.split(frame_patches.SIDEBAR_LOGO_MARKER)[1].split("</style>")[0]
            self.assertIn("background:var(--color-sidebar-brand-18)", added, name)
            self.assertNotIn("#fff", added, name)
        for name in ("top.html", "top-left.html", "blog.html", "presentation.html"):
            patched = apply_frame_patches((LAYOUTS / name).read_text(encoding="utf-8"))
            self.assertNotIn(frame_patches.SIDEBAR_LOGO_MARKER, patched, name)
        blank = apply_frame_patches((LAYOUTS / "left-blank.html").read_text(encoding="utf-8"))
        self.assertNotIn(".is-collapsed .brand-logo{display:none}", blank)
        self.assertIn(".is-collapsed .brand-logo .brand-mark{opacity:1;visibility:visible}", blank)

    def test_rendered_frame_and_web_runtime_use_the_patched_layout(self):
        payload = FramePayload(
            project_title="시험", menu=(MenuItem("home", "홈", "home", "#home"),), active_id="home",
            content_html="<main data-nhimc-role=\"content\"></main>",
        )
        html = render_canonical_frame(ROOT, "left", payload)
        self.assertNotRegex(html, r"\.brand \.brand-asset\{[^}]*(?:background:#fff|padding:3px 5px|box-shadow:0 1px)")
        runtime = (ROOT / "dist/nhimc-web.js").read_text(encoding="utf-8")
        self.assertNotIn("brand-asset{position:absolute;left:6px;top:50%;transform:translateY(-50%);display:block;width:auto;max-width:calc(100% - 12px);height:36px;padding:3px 5px;background:#fff", runtime)


if __name__ == "__main__":
    unittest.main()
