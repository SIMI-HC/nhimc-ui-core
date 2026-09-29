import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

from scripts import canonical_frame, frame_patches
from scripts import presentation_safe_area as psa
from scripts.artifact_delivery import build_and_verify
from scripts.canonical_frame import (
    FRAME_FILES,
    FRAME_RUNTIME,
    FramePayload,
    MenuItem,
    presentation_slides,
    render_canonical_frame,
)

ROOT = Path(__file__).resolve().parents[2]
LAYOUTS = ROOT / "vendor/nhimc-design/layouts"
PRESENTATION_FRAMES = ("nhimc-presentation", "nhimc-presentation-vertical")


def _payload(content: str = "<main data-nhimc-role=\"content\"></main>") -> FramePayload:
    return FramePayload(
        project_title="시험",
        menu=(MenuItem("today", "오늘", "calendar", "#today"),),
        active_id="today",
        content_html=content,
    )


def _script(html: str) -> str:
    return re.findall(r"<script>(.*?)</script>", html, re.S)[-1]


class PresentationBaseContractTests(unittest.TestCase):
    def test_both_frames_pass_safe_area_centering_lifecycle_parity_and_contrast(self):
        report = psa.run_presentation_safe_area(ROOT)
        self.assertEqual([], report["problems"])
        self.assertEqual(48, report["cells"])

    def test_the_checks_catch_the_original_overlap_when_the_safe_area_patch_is_missing(self):
        with mock.patch.object(canonical_frame, "apply_frame_patches", frame_patches._patch_logo_radius):
            with tempfile.TemporaryDirectory() as folder:
                cells = psa.build_cells(ROOT, Path(folder), viewports=((1440, 900), (390, 844)), frames=("presentation",), themes=("light",))
                cells = [cell for cell in cells if cell["mode"] == "offline"]
                found = psa.problems(cells, psa.measure(ROOT, cells))
        self.assertTrue(any("Safe Area" in item or "centred" in item or "slide" in item for item in found), found)

    def test_the_checks_catch_lost_animation_when_the_frame_falls_back_to_the_generic_runtime(self):
        with mock.patch.object(canonical_frame, "PRESENTATION_RUNTIME", FRAME_RUNTIME):
            with tempfile.TemporaryDirectory() as folder:
                cells = psa.build_cells(ROOT, Path(folder), viewports=((1440, 900),), frames=("presentation",), themes=("light",))
                cells = [cell for cell in cells if cell["mode"] == "offline" and cell["size"] == "normal"]
                found = psa.problems(cells, psa.measure(ROOT, cells))
        self.assertTrue(any("transition" in item for item in found), found)

    def test_only_presentation_layouts_receive_the_base_contract(self):
        for name in sorted(set(FRAME_FILES.values())):
            raw = (LAYOUTS / name).read_text(encoding="utf-8")
            patched = frame_patches.apply_frame_patches(raw)
            if name.startswith("presentation"):
                self.assertIn(frame_patches.SAFE_AREA_MARKER, patched, name)
                self.assertIn("--presentation-safe-top", patched, name)
                direction = "vertical" if name == "presentation-vertical.html" else "horizontal"
                self.assertIn(f'data-presentation-direction="{direction}"', patched, name)
            else:
                # left, left-blank, top and top-left get exactly the logo radius patch and nothing else; blog adds only its scroll owner
                expected = frame_patches._patch_logo_radius(raw)
                if name == "blog.html":
                    expected = frame_patches._patch_blog_scroll_owner(expected)
                self.assertEqual(expected, patched, name)
                self.assertNotIn(frame_patches.SAFE_AREA_MARKER, patched, name)
                self.assertNotIn("presentation-direction", patched, name)

    def test_presentation_patch_is_idempotent_and_leaves_controller_header_and_branding_rules_alone(self):
        raw = (LAYOUTS / "presentation.html").read_text(encoding="utf-8")
        once = frame_patches.apply_frame_patches(raw)
        self.assertEqual(once, frame_patches.apply_frame_patches(once))
        restored = once.replace(' data-presentation-direction="horizontal"', "", 1)
        start = restored.index("\n/* " + frame_patches.SAFE_AREA_MARKER)
        cut = raw.rindex("</style>")
        self.assertEqual(raw[:cut], restored[:start])
        self.assertEqual(raw[cut:], restored[restored.index("</style>", start):])

    def test_both_frames_share_one_runtime_and_the_generic_frames_do_not_use_it(self):
        horizontal = _script(render_canonical_frame(ROOT, "presentation", _payload()))
        vertical = _script(render_canonical_frame(ROOT, "presentation-vertical", _payload()))
        self.assertEqual(horizontal, vertical)
        self.assertIn("presentationDirection", horizontal)
        self.assertIn("slide-in-right", horizontal)
        self.assertIn("slide-in-bottom", horizontal)
        left = _script(render_canonical_frame(ROOT, "left", _payload()))
        self.assertNotIn("presentationDirection", left)

    def test_the_frame_owns_the_slide_markup(self):
        single = presentation_slides('<main data-nhimc-role="content"></main>', _payload())
        self.assertEqual(
            '<section class="slide" id="today" data-screen-panel="today"><main data-nhimc-role="content"></main></section>', single
        )
        panels = presentation_slides('<section id="a" data-screen-panel="a"></section><section id="b" data-screen-panel="b" hidden></section>', _payload())
        self.assertEqual(2, panels.count('class="slide"'))
        self.assertEqual(panels, presentation_slides(panels, _payload()))
        html = render_canonical_frame(ROOT, "presentation", _payload())
        self.assertIn('class="slide"', html)
        self.assertNotIn('class="slide"', render_canonical_frame(ROOT, "left", _payload()))

    def test_registry_states_one_base_contract_for_both_frames(self):
        document = json.loads((ROOT / "registry/frames.json").read_text(encoding="utf-8"))
        frames = {item["id"]: item for item in document["frames"]}
        base = document["baseContracts"]["presentation"]
        self.assertEqual(list(PRESENTATION_FRAMES), base["frames"])
        self.assertEqual({"nhimc-presentation": "horizontal", "nhimc-presentation-vertical": "vertical"}, base["direction"])
        for frame_id in PRESENTATION_FRAMES:
            frame = frames[frame_id]
            self.assertEqual("presentation", frame["extends"])
            self.assertEqual(base["sharedRuntime"], frame["implementation"])
            self.assertEqual("1.1.0", frame["version"])
            for name in base["frameOwns"]:
                self.assertIn(name, frame["owns"], frame_id)
            for name in ("branding", "presentation-header", "presentation-controller", "content-safe-area", "content-center", "slide-transition", "slide-navigation"):
                self.assertIn(name, frame["owns"], frame_id)
            self.assertIn(base["sharedRuntime"], [item["path"] for item in frame["protectedFiles"]])
        for frame_id, frame in frames.items():
            if frame_id not in PRESENTATION_FRAMES:
                self.assertEqual("1.1.0" if frame_id == "nhimc-blog" else "1.0.0", frame["version"], frame_id)
                self.assertNotIn("extends", frame)

    def test_presentation_primitives_are_registered_and_styled(self):
        layouts = json.loads((ROOT / "registry/layouts.json").read_text(encoding="utf-8"))["primitives"]
        ids = {item["id"] for item in layouts}
        self.assertTrue({"PresentationContent", "PresentationHero", "PresentationFlow"} <= ids)
        css = (ROOT / "src/layouts/primitives.css").read_text(encoding="utf-8")
        for selector in (".slide>[data-nhimc-role=\"content\"]", ".nhimc-presentation-hero", ".nhimc-presentation-flow"):
            self.assertIn(selector, css)
        # the page never positions Presentation Content itself
        self.assertNotRegex(css.split("Presentation primitives")[1], r"position\s*:\s*(absolute|fixed)")

    def test_web_runtime_carries_the_same_contract(self):
        runtime = (ROOT / "dist/nhimc-web.js").read_text(encoding="utf-8")
        self.assertEqual(2, runtime.count("nhimc-presentation-safe-area: "))
        self.assertIn("--presentation-safe-inline", runtime)
        self.assertIn("presentationRuntime", runtime)
        self.assertIn("presentationDirection", runtime)

    def test_delivery_accepts_presentation_content_and_rejects_content_that_exceeds_the_safe_area(self):
        with tempfile.TemporaryDirectory() as folder:
            work = Path(folder)
            normal = work / "normal.html"
            normal.write_text(psa.fragment("presentation-vertical", "light", False), encoding="utf-8")
            verified = build_and_verify(ROOT, normal, work / "ok")
            self.assertTrue(verified.html_path.is_file())
            oversized = work / "oversized.html"
            oversized.write_text(psa.fragment("presentation", "light", True), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exceeds the Safe Area"):
                build_and_verify(ROOT, oversized, work / "bad")


if __name__ == "__main__":
    unittest.main()
