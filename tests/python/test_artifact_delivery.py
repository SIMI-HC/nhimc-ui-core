import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.artifact_delivery import (
    VerifiedArtifact,
    build_and_verify,
    deliver_verified_artifact,
    load_matching_receipt,
)
from scripts.test_profiles import slow_test


ROOT = Path(__file__).resolve().parents[2]


@slow_test
class ArtifactDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._baseline_folder = tempfile.TemporaryDirectory()
        cls.baseline = build_and_verify(
            ROOT,
            ROOT / "tests/fixtures/authoring/operations/index.html",
            Path(cls._baseline_folder.name),
        )

    @classmethod
    def tearDownClass(cls):
        cls._baseline_folder.cleanup()

    def setUp(self):
        self._folder = tempfile.TemporaryDirectory()
        self.folder = Path(self._folder.name)
        artifact = self.folder / "work" / "index.html"
        receipt = self.folder / "work" / "index.receipt.json"
        artifact.parent.mkdir()
        shutil.copyfile(self.baseline.html_path, artifact)
        shutil.copyfile(self.baseline.receipt_path, receipt)
        proof = load_matching_receipt(artifact, receipt)
        self.verified = VerifiedArtifact(
            artifact, receipt, proof.artifact_sha256, proof.artifact_bytes,
            self.baseline.manifest,
        )

    def tearDown(self):
        self._folder.cleanup()

    def test_delivery_requires_matching_external_receipt(self):
        self.verified.html_path.write_text(
            self.verified.html_path.read_text(encoding="utf-8") + "\n<!-- changed -->",
            encoding="utf-8",
        )
        destination = self.folder / "download" / "index.html"
        with self.assertRaisesRegex(
            ValueError, "artifact digest does not match browser receipt"
        ):
            deliver_verified_artifact(self.verified, destination)
        self.assertFalse(destination.exists())

    def test_delivery_returns_only_index_html(self):
        destination = self.folder / "download" / "index.html"
        result = deliver_verified_artifact(self.verified, destination)
        self.assertEqual(result, destination)
        self.assertEqual(["index.html"], [path.name for path in destination.parent.iterdir()])

    def test_directory_destination_is_normalized_to_index_html(self):
        destination = self.folder / "download"
        destination.mkdir()
        result = deliver_verified_artifact(self.verified, destination)
        self.assertEqual(destination / "index.html", result)

        renamed = self.folder / "renamed.html"
        result = deliver_verified_artifact(self.verified, renamed)
        self.assertEqual(self.folder / "index.html", result)

    def test_rejects_changed_receipt_digest_and_byte_count(self):
        for field, value, message in (
            ("artifactSha256", "0" * 64, "artifact digest"),
            ("artifactBytes", 1, "artifact byte count"),
        ):
            with self.subTest(field=field):
                payload = json.loads(self.verified.receipt_path.read_text(encoding="utf-8"))
                payload[field] = value
                self.verified.receipt_path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    load_matching_receipt(
                        self.verified.html_path, self.verified.receipt_path
                    )
                shutil.copyfile(self.baseline.receipt_path, self.verified.receipt_path)

    def test_rejects_authoring_source_missing_manifest_and_absent_receipt(self):
        authoring = ROOT / "tests/fixtures/authoring/operations/index.html"
        with self.assertRaisesRegex(ValueError, "not a completed artifact"):
            load_matching_receipt(authoring, self.verified.receipt_path)
        missing = self.folder / "missing.receipt.json"
        with self.assertRaisesRegex(ValueError, "browser receipt is missing"):
            load_matching_receipt(self.verified.html_path, missing)

    def test_cli_prints_one_json_summary_and_delivers_only_index_html(self):
        destination = self.folder / "download" / "requested-name.html"
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_verified_artifact.py",
                "--input",
                "tests/fixtures/authoring/operations/index.html",
                "--output",
                str(destination),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertEqual(1, len(lines))
        summary = json.loads(lines[0])
        self.assertEqual("PASS", summary["status"])
        self.assertEqual("index.html", summary["filename"])
        delivered = self.folder / "download" / "index.html"
        self.assertTrue(delivered.is_file())
        self.assertEqual(["index.html"], [path.name for path in delivered.parent.iterdir()])


if __name__ == "__main__":
    unittest.main()
