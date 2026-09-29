from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.run_python_tests import build_suite
from scripts.test_profiles import select_tests, slow_test
from scripts.verify_all import verification_checks
from scripts import verify_release as release_gate


ROOT = Path(__file__).resolve().parents[2]


class VerificationProfileTests(unittest.TestCase):
    def _suite(self):
        class FastCase(unittest.TestCase):
            def test_fast(self):
                pass

        @slow_test
        class SlowCase(unittest.TestCase):
            def test_slow(self):
                pass

        class MixedCase(unittest.TestCase):
            def test_fast(self):
                pass

            @slow_test
            def test_slow(self):
                pass

        loader = unittest.defaultTestLoader
        return unittest.TestSuite(
            loader.loadTestsFromTestCase(case)
            for case in (FastCase, SlowCase, MixedCase)
        )

    def test_quick_profile_excludes_marked_classes_and_methods(self):
        selected, excluded = select_tests(self._suite(), include_slow=False)
        self.assertEqual(2, selected.countTestCases())
        self.assertEqual(2, excluded)

    def test_full_profile_keeps_every_test(self):
        selected, excluded = select_tests(self._suite(), include_slow=True)
        self.assertEqual(4, selected.countTestCases())
        self.assertEqual(0, excluded)

    def test_quick_checks_keep_static_gates_and_remove_browser_gates(self):
        checks = verification_checks(ROOT, quick=True)
        labels = [label for label, _ in checks]
        self.assertEqual(
            [
                "python tests",
                "node tests",
                "contracts",
                "design rules",
                "public tree",
                "canonical snapshot",
                "skill resources sync",
            ],
            labels,
        )
        python_command = checks[0][1]
        self.assertEqual("quick", python_command[-1])
        self.assertFalse(any("browser" in label for label in labels))

    def test_full_checks_preserve_every_existing_gate(self):
        labels = [label for label, _ in verification_checks(ROOT)]
        self.assertEqual(14, len(labels))
        for label in (
            "canonical frame parity",
            "presentation safe area",
            "frame render",
            "browser",
            "skill resources sync",
        ):
            self.assertIn(label, labels)

    def test_repository_quick_suite_excludes_real_browser_tests(self):
        quick, excluded = build_suite(ROOT, "quick")
        full, full_excluded = build_suite(ROOT, "full")
        self.assertGreaterEqual(excluded, 20)
        self.assertEqual(0, full_excluded)
        self.assertEqual(full.countTestCases(), quick.countTestCases() + excluded)

    def test_release_uses_the_single_full_verification_entry_point(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            verify = mock.Mock(return_value=0)
            with (
                mock.patch.object(release_gate, "verify_all", verify),
                mock.patch.object(release_gate, "validate_contracts", return_value=[]),
                mock.patch.object(release_gate, "validate_design", return_value=[]),
                mock.patch.object(release_gate, "scan_public_tree", return_value=[]),
                mock.patch.object(release_gate, "compare_skill_resources", return_value=[]),
                mock.patch.object(release_gate, "expected_tag", return_value="v1.0.0"),
                mock.patch.object(release_gate, "tag_exists", return_value=True),
                mock.patch.object(release_gate, "unresolved_release_blockers", return_value=[]),
                mock.patch.object(release_gate, "REQUIRED_LEGAL", ()),
            ):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(0, release_gate.verify_release(root))
            verify.assert_called_once_with(root.resolve())


if __name__ == "__main__":
    unittest.main()
