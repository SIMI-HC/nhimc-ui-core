import tempfile
import unittest
from pathlib import Path

from scripts.validate_public import scan_public_tree
from scripts.verify_release import unresolved_release_blockers


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/public-safety"


class PublicSafetyTests(unittest.TestCase):
    def test_safe_fixture_has_no_findings(self):
        self.assertEqual([], scan_public_tree(FIXTURES, include={"safe.txt"}))

    def test_each_unsafe_fixture_reports_its_rule(self):
        expected = {
            "private-ip.txt": "public.private-network",
            "secret.txt": "public.possible-secret",
            "personal-data.txt": "public.personal-data",
            "internal-url.txt": "public.internal-url",
        }
        for filename, rule in expected.items():
            with self.subTest(filename=filename):
                rules = {
                    finding.rule
                    for finding in scan_public_tree(FIXTURES, include={filename})
                }
                self.assertIn(rule, rules)

    def test_url_credentials_are_blocked_without_echoing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.txt").write_text(
                "https" + "://" + "synthetic-user:synthetic-pass@example.org/path\n",
                encoding="utf-8",
            )
            findings = scan_public_tree(root)
            self.assertIn("public.url-credentials", {item.rule for item in findings})
            self.assertNotIn("synthetic-pass", repr(findings))

    def test_whole_tree_scan_skips_known_unsafe_fixtures(self):
        findings = scan_public_tree(ROOT)
        fixture_prefix = "tests/fixtures/public-safety/"
        self.assertFalse(any(item.path.startswith(fixture_prefix) for item in findings))

    def test_loopback_is_blocked_outside_explicit_local_test_tooling(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            address = ".".join(("127", "0", "0", "1"))
            (root / "config.txt").write_text(f"service={address}\n", encoding="utf-8")
            self.assertIn(
                "public.private-network",
                {item.rule for item in scan_public_tree(root)},
            )

    def test_asset_review_has_no_unresolved_blocker(self):
        blockers = unresolved_release_blockers(ROOT / "PUBLIC_ASSET_REVIEW.md")
        self.assertEqual([], blockers)

    def test_unchecked_blocker_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            review = Path(directory) / "review.md"
            review.write_text("- [ ] BLOCKING: ownership unknown\n", encoding="utf-8")
            self.assertEqual(["ownership unknown"], unresolved_release_blockers(review))


if __name__ == "__main__":
    unittest.main()
