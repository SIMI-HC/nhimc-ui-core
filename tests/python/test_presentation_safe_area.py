import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import canonical_frame, frame_patches
from scripts import presentation_safe_area as psa
from scripts.artifact_delivery import build_and_verify
from scripts.canonical_frame import FRAME_FILES

ROOT = Path(__file__).resolve().parents[2]
LAYOUTS = ROOT / "vendor/nhimc-design/layouts"
PRESENTATION_FRAMES = ("nhimc-presentation", "nhimc-presentation-vertical")


class PresentationSafeAreaTests(unittest.TestCase):
    def test_content_never_overlaps_header_or_controller_and_oversized_content_is_detected(self):
        report = psa.run_presentation_safe_area(ROOT)
        self.assertEqual([], report["problems"])
        self.assertEqual(48, report["cells"])

    def test_the_checks_catch_the_original_bug_when_the_safe_area_patch_is_missing(self):
        with mock.patch.object(canonical_frame, "apply_frame_patches", frame_patches._patch_logo_radius):
            with tempfile.TemporaryDirectory() as folder:
                cells = psa.build_cells(ROOT, Path(folder), viewports=((1440, 900), (390, 844)), frames=("presentation",), themes=("light",))
                cells = [cell for cell in cells if cell["mode"] == "offline"]
                found = psa.problems(cells, psa.measure(ROOT, cells))
        self.assertTrue(any("overlaps" in item or "starts above the Header" in item for item in found), found)

    def test_only_presentation_layouts_receive_the_safe_area(self):
        for name in sorted(set(FRAME_FILES.values())):
            raw = (LAYOUTS / name).read_text(encoding="utf-8")
            patched = frame_patches.apply_frame_patches(raw)
            if name.startswith("presentation"):
                self.assertIn(frame_patches.SAFE_AREA_MARKER, patched, name)
                self.assertIn("--presentation-safe-top", patched, name)
            else:
                # left, left-blank, top, top-left and blog get exactly the logo radius patch and nothing else
                self.assertEqual(frame_patches._patch_logo_radius(raw), patched, name)
                self.assertNotIn(frame_patches.SAFE_AREA_MARKER, patched, name)

    def test_presentation_patch_is_idempotent_and_keeps_controller_rules(self):
        raw = (LAYOUTS / "presentation.html").read_text(encoding="utf-8")
        once = frame_patches.apply_frame_patches(raw)
        self.assertEqual(once, frame_patches.apply_frame_patches(once))
        # Controller, Header and Branding rules are untouched: the patch only appends a block at the end of the style.
        cut = raw.rindex("</style>")
        self.assertEqual(raw[:cut], once[:cut])
        self.assertEqual(raw[cut:], once[len(once) - (len(raw) - cut):])

    def test_registry_states_the_presentation_contract(self):
        frames = {item["id"]: item for item in json.loads((ROOT / "registry/frames.json").read_text(encoding="utf-8"))["frames"]}
        for frame_id in PRESENTATION_FRAMES:
            owns = frames[frame_id]["owns"]
            for name in ("branding", "presentation-header", "presentation-controller", "content-safe-area", "content-boundary"):
                self.assertIn(name, owns, frame_id)
            self.assertEqual("1.0.1", frames[frame_id]["version"])
        for frame_id, frame in frames.items():
            if frame_id not in PRESENTATION_FRAMES:
                self.assertEqual("1.0.0", frame["version"], frame_id)

    def test_web_runtime_carries_the_same_safe_area(self):
        runtime = (ROOT / "dist/nhimc-web.js").read_text(encoding="utf-8")
        self.assertEqual(2, runtime.count("nhimc-presentation-safe-area: "))
        self.assertIn("--presentation-safe-inline", runtime)

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
