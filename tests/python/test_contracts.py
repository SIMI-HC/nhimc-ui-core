import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_contracts import validate_contracts


ROOT = Path(__file__).resolve().parents[2]


class ContractTests(unittest.TestCase):
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

    def test_contract_validator_runs_as_a_script(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_contracts.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
