import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from zipfile import ZipFile

from scripts.build_release import build_release


ROOT = Path(__file__).resolve().parents[2]


class ReleaseBuildTests(unittest.TestCase):
    @patch("scripts.build_release.verify_release", return_value=0)
    def test_public_archives_are_byte_reproducible(self, _gate):
        with tempfile.TemporaryDirectory() as folder:
            one = build_release(ROOT, Path(folder) / "one.zip")
            two = build_release(ROOT, Path(folder) / "two.zip")
            self.assertEqual(one.read_bytes(), two.read_bytes())

    @patch("scripts.build_release.verify_release", return_value=0)
    def test_archive_excludes_private_fixtures_and_generated_state(self, _gate):
        with tempfile.TemporaryDirectory() as folder:
            archive = build_release(ROOT, Path(folder) / "release.zip")
            with ZipFile(archive) as bundle:
                names = set(bundle.namelist())
            self.assertTrue(any(name.endswith("/README.md") for name in names))
            self.assertFalse(any("tests/fixtures/public-safety" in name for name in names))
            self.assertFalse(any("/.git/" in name or "/__pycache__/" in name for name in names))

    @patch("scripts.build_release.verify_release", return_value=0)
    def test_builder_runs_full_gate_against_archived_root(self, gate):
        with tempfile.TemporaryDirectory() as folder:
            build_release(ROOT, Path(folder) / "release.zip")
        gate.assert_called_once_with(root=ROOT.resolve(), run_full_verification=True)

    @patch("scripts.build_release.verify_release", return_value=1)
    def test_failed_gate_leaves_no_archive(self, _gate):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "release.zip"
            with self.assertRaises(RuntimeError):
                build_release(ROOT, output)
            self.assertFalse(output.exists())

    def test_readme_documents_support_without_claiming_publication(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for environment in (
            "ChatGPT Web",
            "Codex",
            "Claude Web",
            "Claude Code",
            "Gemini Web",
            "Gemini CLI",
        ):
            self.assertIn(environment, text)
        for status in ("READY", "WEB_BOOTSTRAP", "UNSUPPORTED"):
            self.assertIn(status, text)
        self.assertNotIn("examples/operations", text)
        self.assertNotIn("examples/administration", text)
        self.assertIn("PUBLIC_ASSET_REVIEW.md", text)
        self.assertIn("게시 작업은 별도 절차입니다", text)
        self.assertNotIn("already published", text.lower())


if __name__ == "__main__":
    unittest.main()
