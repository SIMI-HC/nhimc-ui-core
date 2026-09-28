import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.run_browser_tests import find_browser, run_template_parity


ROOT = Path(__file__).resolve().parents[2]


class TemplateParityTests(unittest.TestCase):
    def test_find_browser_prefers_explicit_environment_path(self):
        with tempfile.TemporaryDirectory() as folder:
            fake_browser = Path(folder) / "browser.exe"
            fake_browser.write_bytes(b"browser")
            with mock.patch.dict(
                os.environ, {"NHIMC_BROWSER_PATH": str(fake_browser)}
            ):
                self.assertEqual(fake_browser.resolve(), find_browser())

    def test_missing_browser_names_override_and_candidates(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch(
            "scripts.run_browser_tests.BROWSER_PATHS", ()
        ), mock.patch("scripts.run_browser_tests.shutil.which", return_value=None):
            with self.assertRaisesRegex(
                RuntimeError, "NHIMC_BROWSER_PATH.*google-chrome.*chromium"
            ):
                find_browser()

    def test_template_parity_requires_all_cells(self):
        result = run_template_parity(ROOT, viewports=((390, 844),))
        self.assertEqual(9 * 2, len(result["results"]))
        self.assertTrue(result["all_passed"], result)
        for cell in result["results"]:
            self.assertTrue(
                all(
                    cell[name]
                    for name in (
                        "structure", "responsive", "focus", "pixels",
                        "frameIsolation",
                    )
                ),
                cell,
            )


if __name__ == "__main__":
    unittest.main()
