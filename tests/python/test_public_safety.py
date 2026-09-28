import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.validate_public import scan_public_tree
from scripts.verify_release import unresolved_release_blockers, verify_release


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/public-safety"


class PublicSafetyTests(unittest.TestCase):
    def test_long_inline_asset_line_scans_without_quadratic_email_backtracking(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "asset.html").write_text(
                ("%3C" * 20_000), encoding="utf-8"
            )
            code = (
                "from pathlib import Path; "
                "from scripts.validate_public import scan_public_tree; "
                f"raise SystemExit(bool(scan_public_tree(Path({str(root)!r}))))"
            )
            completed = subprocess.run(
                [sys.executable, "-c", code],
                cwd=ROOT,
                timeout=2,
                check=False,
            )
            self.assertEqual(0, completed.returncode)

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

    def test_devtools_loopback_is_allowed_only_in_registered_browser_tooling(self):
        for relative in (
            "scripts/verify_standalone_browser.mjs",
            "scripts/verify_canonical_parity.mjs",
        ):
            findings = scan_public_tree(ROOT, include={relative})
            self.assertNotIn(
                "public.private-network", {item.rule for item in findings}, relative
            )

    def test_asset_review_has_no_unresolved_blocker(self):
        blockers = unresolved_release_blockers(ROOT / "PUBLIC_ASSET_REVIEW.md")
        self.assertEqual([], blockers)

    def test_unchecked_blocker_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            review = Path(directory) / "review.md"
            review.write_text("- [ ] BLOCKING: ownership unknown\n", encoding="utf-8")
            self.assertEqual(["ownership unknown"], unresolved_release_blockers(review))

    def test_sensitive_and_extensionless_text_files_are_scanned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text(
                "API" + '_KEY="synthetic-secret-value-123456"\n', encoding="utf-8"
            )
            (root / "service.conf").write_text(
                "host=db." + "internal\n", encoding="utf-8"
            )
            (root / "credentials").write_text(
                "pass" + "word=synthetic-password-123456\n", encoding="utf-8"
            )
            (root / "private.pem").write_text(
                "-----BEGIN " + "PRIVATE KEY-----\nsynthetic\n", encoding="utf-8"
            )
            rules = {item.rule for item in scan_public_tree(root)}
            self.assertIn("public.possible-secret", rules)
            self.assertIn("public.internal-host", rules)
            self.assertIn("public.private-key", rules)

    def test_single_label_internal_hosts_are_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "service.conf").write_text(
                "HOST=" + "intra" + "net\nCACHE=" + "local" + "host\n",
                encoding="utf-8",
            )
            self.assertIn(
                "public.internal-host", {item.rule for item in scan_public_tree(root)}
            )

    def test_unknown_binary_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "mystery.bin").write_bytes(b"\x00\x01unregistered")
            self.assertIn(
                "public.unknown-binary", {item.rule for item in scan_public_tree(root)}
            )
            (root / "rogue.woff2").write_bytes(b"synthetic-unregistered-font")
            self.assertIn(
                "public.unknown-binary", {item.rule for item in scan_public_tree(root)}
            )

    def test_release_validation_uses_requested_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text(
                "API" + '_KEY="synthetic-secret-value-123456"\n', encoding="utf-8"
            )
            with redirect_stdout(io.StringIO()):
                result = verify_release(root=root, run_full_verification=False)
            self.assertNotEqual(0, result)


if __name__ == "__main__":
    unittest.main()
