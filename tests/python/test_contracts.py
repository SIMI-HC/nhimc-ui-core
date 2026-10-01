import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.common import sha256_file
from scripts.update_integrity import refresh_integrity
from scripts.validate_contracts import check_integrity, validate_contracts


ROOT = Path(__file__).resolve().parents[2]


class ContractTests(unittest.TestCase):
    def test_readme_version_table_matches_the_registries(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        frames = json.loads((ROOT / "registry/frames.json").read_text(encoding="utf-8"))["frames"]
        upstream = json.loads((ROOT / "vendor/nhimc-design/upstream.json").read_text(encoding="utf-8"))
        self.assertIn(f"| 프로젝트(NHIMC UI Core) | `{version}` |", readme)
        self.assertIn(f"| Frame | `{frames[0]['version']}`", readme)
        self.assertIn(f"`{upstream['commit'][:12]}`", readme)
        self.assertIn(f"@v{version}", readme)

    def test_project_and_frame_contracts_are_version_3(self):
        self.assertEqual("2.1.0", (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        project = json.loads((ROOT / "registry/project.json").read_text(encoding="utf-8"))
        frames = json.loads((ROOT / "registry/frames.json").read_text(encoding="utf-8"))["frames"]
        self.assertEqual("2.1.0", project["projectVersion"])
        self.assertEqual(7, len(frames))
        self.assertEqual({"1.1.0", "1.3.0", "1.4.0", "1.5.0"}, {frame["version"] for frame in frames})

    def test_repository_contract_is_consistent(self):
        self.assertEqual([], validate_contracts(ROOT))

    def test_version_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "registry").mkdir()
            (root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            project = {
                "projectVersion": "9.9.9",
                "defaultFrame": "nhimc-default",
                "defaultTheme": "nhimc-light",
            }
            (root / "registry/project.json").write_text(
                json.dumps(project), encoding="utf-8"
            )

            findings = validate_contracts(root)

            self.assertIn(
                "contract.version-mismatch", {item.rule for item in findings}
            )

    def test_missing_registry_reference_is_reported(self):
        findings = validate_contracts(
            ROOT, required_override=["registry/missing.json"]
        )

        self.assertIn("contract.missing-file", {item.rule for item in findings})

    def test_default_artifact_builder_must_exist(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "registry").mkdir()
            (root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            (root / "registry/project.json").write_text(
                json.dumps(
                    {
                        "projectVersion": "1.0.0",
                        "defaultArtifact": {"builder": "scripts/missing.py"},
                    }
                ),
                encoding="utf-8",
            )

            findings = validate_contracts(
                root, required_override=["registry/project.json"]
            )

            self.assertIn(
                ("contract.missing-file", "scripts/missing.py"),
                {(item.rule, item.path) for item in findings},
            )

    def test_contract_validator_runs_as_a_script(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_contracts.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)

    def test_registered_asset_hashes_match_files(self):
        findings = validate_contracts(ROOT)
        self.assertNotIn(
            "contract.integrity-mismatch", {item.rule for item in findings}
        )
        assets = json.loads(
            (ROOT / "registry/assets.json").read_text(encoding="utf-8")
        )["assets"]
        self.assertGreaterEqual(len(assets), 3)
        self.assertTrue(all(len(asset["sha256"]) == 64 for asset in assets))
        self.assertTrue(all((ROOT / asset["path"]).is_file() for asset in assets))

    def test_protected_text_files_are_checked_out_with_lf(self):
        frames = json.loads(
            (ROOT / "registry/frames.json").read_text(encoding="utf-8")
        )["frames"]
        assets = json.loads(
            (ROOT / "registry/assets.json").read_text(encoding="utf-8")
        )["assets"]
        protected = {
            entry["path"]
            for frame in frames
            for entry in frame["protectedFiles"]
            if Path(entry["path"]).suffix in {".css", ".js", ".json", ".md", ".svg", ".txt"}
        }
        protected.update(
            asset["path"]
            for asset in assets
            if Path(asset["path"]).suffix in {".css", ".js", ".json", ".md", ".svg", ".txt"}
        )
        protected = {path for path in protected if not path.startswith("vendor/")}

        result = subprocess.run(
            ["git", "check-attr", "eol", "--", *sorted(protected)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertTrue(protected)
        self.assertTrue(
            all(line.endswith(": eol: lf") for line in result.stdout.splitlines()),
            result.stdout,
        )
        self.assertEqual(
            [],
            [path for path in sorted(protected) if b"\r\n" in (ROOT / path).read_bytes()],
            "Protected text files must use canonical LF bytes",
        )

    def test_changed_asset_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            asset = root / "logo.svg"
            asset.write_bytes(b"original")
            entries = [{"path": "logo.svg", "sha256": sha256_file(asset)}]
            asset.write_bytes(b"changed")

            findings = check_integrity(root, entries)

            self.assertEqual(
                ["contract.integrity-mismatch"], [item.rule for item in findings]
            )
            self.assertEqual("logo.svg", findings[0].path)

    def test_integrity_refresh_requires_exact_frame_version(self):
        with self.assertRaisesRegex(ValueError, "frame version confirmation"):
            refresh_integrity(ROOT, "nhimc-default", "9.9.9")


if __name__ == "__main__":
    unittest.main()
