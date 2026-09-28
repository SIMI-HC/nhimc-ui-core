import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.nhimc_upstream import EXPECTED_COUNTS, VENDOR_PREFIX
from scripts.sync_nhimc_design import sync_snapshot
from scripts.verify_nhimc_design_sync import verify_snapshot


ROOT = Path(__file__).resolve().parents[2]
LAYOUTS = (
    "blog.html",
    "left-blank.html",
    "left.html",
    "presentation-vertical.html",
    "presentation.html",
    "top-left.html",
    "top.html",
)
LOGOS = tuple(f"logo-{index}.svg" for index in range(9))
FONTS = tuple(f"font-{index}.woff2" for index in range(6))


class NhimcDesignSyncTests(unittest.TestCase):
    def setUp(self):
        self._temporaries: list[tempfile.TemporaryDirectory] = []

    def tearDown(self):
        for temporary in self._temporaries:
            temporary.cleanup()

    def _temporary_path(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self._temporaries.append(temporary)
        return Path(temporary.name)

    def _write(self, root: Path, relative: str, data: bytes) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def _run_git(self, root: Path, *arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result.stdout.strip()

    def _canonical_git_fixture(self) -> tuple[Path, Path]:
        source = self._temporary_path() / "nhimc-worktool"
        root = self._temporary_path() / "core"
        source.mkdir(parents=True)
        root.mkdir(parents=True)

        for name in LAYOUTS:
            self._write(
                source,
                f"assets/layouts/{name}",
                f'<!doctype html><main data-nhimc-role="content-slot">{name}</main>\r\n'.encode(),
            )
        self._write(source, "assets/icons/nhimc-icons.svg", b"<svg><symbol id=\"menu\"/></svg>\r\n")
        self._write(source, "assets/components/showcase.html", b"<!doctype html><title>Components</title>\r\n")
        registry_rows = [
            "| id | purpose |\r\n",
            "|---|---|\r\n",
            *[f"| Component{index} | Purpose {index} |\r\n" for index in range(49)],
        ]
        self._write(source, "components/registry.md", "".join(registry_rows).encode())
        self._write(source, "components/icons.md", b"# Icons\r\n")
        self._write(source, "patterns/catalog.md", b"# Patterns\r\n")
        self._write(source, "rules/layout.md", b"# Layout\r\n")
        self._write(source, "tokens/themes/catalog.yaml", b"themes: []\r\n")
        self._write(source, "templates/catalog.yaml", b"templates: []\r\n")
        for name in LOGOS:
            self._write(source, f"docs/design-docs/assets/logo/{name}", b"<svg/>\r\n")
        for name in FONTS:
            self._write(source, f"docs/design-docs/assets/font/{name}", b"woff2-fixture-" + name.encode())
        self._write(
            source,
            "docs/design-docs/assets/fonts.css",
            b'@font-face { font-family: "Noto Sans KR"; }\r\n',
        )

        self._run_git(source, "init")
        self._run_git(source, "config", "user.email", "test@example.com")
        self._run_git(source, "config", "user.name", "NHIMC Test")
        self._run_git(source, "add", ".")
        self._run_git(source, "commit", "-m", "canonical fixture")
        return source, root

    def test_sync_rejects_non_git_source(self):
        source = self._temporary_path()
        root = self._temporary_path()
        with self.assertRaisesRegex(ValueError, "Git worktree"):
            sync_snapshot(source, root, expected_commit=None)

    def test_sync_rejects_source_path_outside_worktree(self):
        repository, root = self._canonical_git_fixture()
        outside = self._temporary_path()
        with self.assertRaisesRegex(ValueError, "Git worktree"):
            sync_snapshot(outside, root, expected_commit=None)
        self.assertTrue((repository / ".git").is_dir())

    def test_sync_rejects_dirty_allowlisted_source_without_replacing_snapshot(self):
        source, root = self._canonical_git_fixture()
        sync_snapshot(source, root, expected_commit=None)
        manifest_path = root / VENDOR_PREFIX / "upstream.json"
        before = manifest_path.read_bytes()
        (source / "assets/layouts/left.html").write_text("dirty", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "modified canonical source"):
            sync_snapshot(source, root, expected_commit=None)

        self.assertEqual(before, manifest_path.read_bytes())

    def test_sync_rejects_unexpected_commit(self):
        source, root = self._canonical_git_fixture()
        with self.assertRaisesRegex(ValueError, "source commit"):
            sync_snapshot(source, root, expected_commit="0" * 40)
        self.assertFalse((root / VENDOR_PREFIX).exists())

    def test_sync_copies_only_allowlisted_paths_and_records_byte_digests(self):
        source, root = self._canonical_git_fixture()
        self._write(source, "references/private.txt", b"must-not-copy")

        manifest = sync_snapshot(source, root, expected_commit=None)

        destinations = {item["destination"] for item in manifest["files"]}
        self.assertNotIn("vendor/nhimc-design/references/private.txt", destinations)
        self.assertEqual(EXPECTED_COUNTS, manifest["counts"])
        self.assertEqual(
            json.loads((root / VENDOR_PREFIX / "upstream.json").read_text(encoding="utf-8")),
            manifest,
        )
        for item in manifest["files"]:
            data = (root / item["destination"]).read_bytes()
            self.assertEqual(item["bytes"], len(data))
            self.assertEqual(item["sha256"], hashlib.sha256(data).hexdigest())

    def test_sync_preserves_crlf_bytes(self):
        source, root = self._canonical_git_fixture()
        expected = b"line1\r\nline2\r\n"
        path = source / "rules/layout.md"
        path.write_bytes(expected)
        self._run_git(source, "add", "rules/layout.md")
        self._run_git(source, "commit", "-m", "record CRLF")

        sync_snapshot(source, root, expected_commit=None)

        self.assertEqual(expected, (root / VENDOR_PREFIX / "rules/layout.md").read_bytes())

    def test_verify_snapshot_detects_tampering_and_extra_files(self):
        source, root = self._canonical_git_fixture()
        sync_snapshot(source, root, expected_commit=None)
        self.assertEqual([], verify_snapshot(root))

        (root / VENDOR_PREFIX / "layouts/left.html").write_text("tampered", encoding="utf-8")
        self._write(root / VENDOR_PREFIX, "extra.txt", b"extra")
        rules = {finding.rule for finding in verify_snapshot(root)}

        self.assertIn("upstream.digest", rules)
        self.assertIn("upstream.extra-file", rules)


class RepositoryCanonicalSnapshotTests(unittest.TestCase):
    def test_repository_contains_complete_pinned_snapshot(self):
        manifest_path = ROOT / VENDOR_PREFIX / "upstream.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(
            "08c45402eece8a7c55afc60385e8671c9f13081a", manifest["commit"]
        )
        self.assertEqual(EXPECTED_COUNTS, manifest["counts"])
        self.assertEqual([], verify_snapshot(ROOT))

    def test_repository_vendor_paths_disable_line_ending_conversion(self):
        result = subprocess.run(
            ["git", "check-attr", "text", "--", "vendor/nhimc-design/layouts/left.html"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )

        self.assertTrue(result.stdout.rstrip().endswith("text: unset"), result.stdout)
        diff_result = subprocess.run(
            ["git", "check-attr", "diff", "--", "vendor/nhimc-design/layouts/left.html"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        self.assertTrue(
            diff_result.stdout.rstrip().endswith("diff: unset"), diff_result.stdout
        )


if __name__ == "__main__":
    unittest.main()
