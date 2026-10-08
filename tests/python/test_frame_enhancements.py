from pathlib import Path
import json
import re
import unittest

from scripts import dark_tones, frame_patches
from scripts.canonical_frame import FramePayload, MenuItem, render_canonical_frame
from scripts.theme_colors import theme_color_css

ROOT = Path(__file__).resolve().parents[2]
NON_PRESENTATION = ("left", "left-blank", "left-dual", "top", "top-left", "blog")
SIGNATURE = "nhimc-scroll-top"


def _real_payload() -> FramePayload:
    from tests.python.test_presentation_safe_area import _payload

    return _payload()


class FrameEnhancementTests(unittest.TestCase):
    def test_every_frame_but_presentation_runs_the_enhancement_runtime(self):
        for frame in NON_PRESENTATION:
            html = render_canonical_frame(ROOT, frame, _real_payload())
            self.assertIn(SIGNATURE, html, frame)
            self.assertEqual(1, html.count("<script>"), frame)
        for frame in ("presentation", "presentation-vertical"):
            self.assertNotIn(SIGNATURE, render_canonical_frame(ROOT, frame, _real_payload()), frame)

    def test_web_runtime_carries_the_same_enhancement_runtime(self):
        runtime = (ROOT / "dist/nhimc-web.js").read_text(encoding="utf-8")
        self.assertIn("enhanceRuntime", runtime)
        self.assertIn(SIGNATURE, runtime)

    def test_help_sheet_is_half_the_screen_without_the_620px_cap(self):
        for name in ("blog", "top", "top-left", "left", "left-blank", "presentation", "presentation-vertical"):
            layout = frame_patches.apply_frame_patches((ROOT / f"vendor/nhimc-design/layouts/{name}.html").read_text(encoding="utf-8"))
            self.assertNotIn(frame_patches.HELP_WIDTH_OLD, layout, name)
            self.assertIn(frame_patches.HELP_WIDTH_NEW, layout, name)
        self.assertEqual(layout, frame_patches.apply_frame_patches(layout))

    def test_blog_column_is_wide_by_default(self):
        layout = frame_patches.apply_frame_patches((ROOT / "vendor/nhimc-design/layouts/blog.html").read_text(encoding="utf-8"))
        self.assertIn("--blog-width:1560px", layout)
        self.assertNotIn("--blog-width:1080px", layout)

    def test_enhancement_runtime_is_protected_by_the_frame_digests(self):
        frames = json.loads((ROOT / "registry/frames.json").read_text(encoding="utf-8"))["frames"]
        for frame in frames:
            paths = [item["path"] for item in frame["protectedFiles"]]
            if frame["id"].startswith("nhimc-presentation"):
                self.assertNotIn("src/frames/enhance-runtime.js", paths, frame["id"])
            else:
                self.assertIn("src/frames/enhance-runtime.js", paths, frame["id"])

    def test_runtime_has_no_motion_when_the_user_asks_for_reduced_motion(self):
        script = (ROOT / "src/frames/enhance-runtime.js").read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion: reduce", script)
        self.assertIn("calm ? 'auto' : 'smooth'", script)
        css = (ROOT / "src/layouts/primitives.css").read_text(encoding="utf-8")
        block = css[css.index("/* nhimc-motion:begin */") : css.index("/* nhimc-motion:end */")]
        opening = "@media(prefers-reduced-motion:no-preference){"
        inside_end = block.index("\n}\n", block.index(opening))
        outside = block[: block.index(opening)] + block[inside_end:]
        self.assertNotRegex(outside.replace("@keyframes", ""), r"(animation|transition)\s*:", "motion declared outside the reduced-motion media query")
        self.assertIn("animation:nhimc-rise", block[block.index(opening) : inside_end])

    def test_primitives_hold_no_hard_coded_colour_for_the_enhancements(self):
        css = (ROOT / "src/layouts/primitives.css").read_text(encoding="utf-8")
        block = css[css.index("/* nhimc-motion:begin */") : css.index("/* nhimc-motion:end */")]
        self.assertNotRegex(block, r"#[0-9a-fA-F]{3,8}\b")
        self.assertIn("var(--color-primary)", block)


class MenuHoverAndNumericColumnTests(unittest.TestCase):
    SHADOW = "box-shadow:-12px 0 0 var(--color-secondary),12px 0 0 var(--color-secondary)"

    def test_only_blog_widens_the_menu_hover_because_only_its_buttons_have_no_padding(self):
        patched = {
            name: frame_patches.apply_frame_patches((ROOT / f"vendor/nhimc-design/layouts/{name}.html").read_text(encoding="utf-8"))
            for name in ("blog", "top")
        }
        self.assertIn(self.SHADOW, patched["blog"])
        self.assertNotIn(self.SHADOW, patched["top"])
        self.assertIn("padding:9px 0", patched["blog"])  # the reason: the BLOG menu button carries no horizontal padding

    def test_the_hover_shadow_fades_with_the_other_header_effects(self):
        css = (ROOT / "src/layouts/primitives.css").read_text(encoding="utf-8")
        self.assertIn("transition:background-color .16s ease-out,color .16s ease-out,box-shadow .16s ease-out", css)

    def test_numeric_columns_have_one_class_for_th_and_td(self):
        css = (ROOT / "src/layouts/primitives.css").read_text(encoding="utf-8")
        self.assertIn("th.nhimc-num,td.nhimc-num{text-align:right;font-variant-numeric:tabular-nums}", css)
        for name in ("bootstrap.md", "skills/nhimc-worktool/SKILL.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn('class="nhimc-num"', text, name)
            self.assertIn('style="text-align:right"', text, name)  # named only to say it is not to be used


class DarkToneTests(unittest.TestCase):
    def test_mix_matches_the_channel_wise_rounding_of_the_reference_script(self):
        # values worked out with the app script this was taken from: mixHex(chip, card, pct) = round(c*pct/100 + card*(100-pct)/100)
        self.assertEqual("#3e4348", dark_tones.mix("#C7E1F5", "#171717", 22))
        self.assertEqual("#485055", dark_tones.mix("#C7E1F5", "#171717", 28))
        self.assertEqual("#496d92", dark_tones.mix("#6BA6E4", "#171717", 60))

    def test_every_theme_gets_a_readable_primary_button_in_dark(self):
        css = dark_tones.primary_css(ROOT)
        themes = dark_tones._themes(ROOT)
        self.assertEqual(len(themes) + 2, len(css.splitlines()))
        for theme_id, theme in themes.items():
            soft = dark_tones.mix(theme["tokens"]["dark"]["primary"], dark_tones.DARK_CARD, dark_tones.SOFT)
            self.assertIn(f"--nhimc-primary-soft:{soft};", css, theme_id)
            text = re.search(rf'{"" if theme_id == "nhimc-default" else re.escape(theme_id)}[^{{]*\{{--nhimc-primary-soft:{soft};[^}}]*--nhimc-primary-soft-foreground:(#[0-9A-Fa-f]{{6}})', css)
            self.assertIsNotNone(text, theme_id)
            self.assertGreaterEqual(dark_tones.contrast(soft, text.group(1)), 4.5, theme_id)

    def test_every_theme_has_the_base_accent_chips_and_dark_tones_follow_the_light_fallbacks(self):
        chips = dark_tones.chip_css(ROOT)
        for name in dark_tones.BASE_CHIPS:
            self.assertIn(f"--color-chip-{name}:", chips)
        self.assertNotIn("chip-purple", chips)  # purple, pink and amber stay Color Mix only
        css = dark_tones.accent_css(ROOT)
        self.assertEqual(len(dark_tones.ACCENTS) + len(dark_tones.FALLBACK), len(css.splitlines()))
        for name in dark_tones.ACCENTS:
            self.assertIn(f'[data-theme="dark"] [data-nhimc-accent="{name}"]{{', css)
        for name in dark_tones.FALLBACK:
            self.assertIn(f'[data-theme-color="color-mix"][data-theme="dark"] [data-nhimc-accent="{name}"]{{', css)

    def test_theme_css_ships_the_tones_and_the_card_rules_read_them(self):
        css = theme_color_css(ROOT)
        self.assertIn("--nhimc-primary-soft", css)
        self.assertIn("--color-chip-sky:", css)
        self.assertIn("--nhimc-accent-line", css)
        primitives = (ROOT / "src/layouts/primitives.css").read_text(encoding="utf-8")
        self.assertIn("border-color:var(--nhimc-accent-line,var(--nhimc-accent-surface))", primitives)

    def test_dark_card_is_the_frames_dark_card_colour(self):
        layout = (ROOT / "vendor/nhimc-design/layouts/blog.html").read_text(encoding="utf-8")
        dark = layout[layout.index('[data-theme="dark"]{') :][:900]
        self.assertIn(f"--color-card:{dark_tones.DARK_CARD}", dark)


if __name__ == "__main__":
    unittest.main()
