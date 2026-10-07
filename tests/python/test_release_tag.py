from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import release_tag
from scripts.release_tag import cdn_runtime_urls, create_and_push_tag, expected_tag, tag_exists


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, text=True, check=True
    )


class ReleaseTagTests(unittest.TestCase):
    def _repo(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "test@example.com")
        _git(root, "config", "user.name", "Test")
        (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
        _git(root, "add", "VERSION")
        _git(root, "commit", "-q", "-m", "initial")
        return root

    def test_expected_tag_is_v_prefixed_version(self):
        root = self._repo()
        self.assertEqual("v1.2.3", expected_tag(root))

    def test_tag_exists_is_false_before_tagging_and_true_after(self):
        root = self._repo()
        self.assertFalse(tag_exists(root, "v1.2.3"))
        _git(root, "tag", "v1.2.3")
        self.assertTrue(tag_exists(root, "v1.2.3"))

    def test_create_and_push_tag_creates_a_tag_at_head(self):
        with tempfile.TemporaryDirectory() as bare_folder:
            bare = Path(bare_folder) / "origin.git"
            _git(Path(bare_folder), "init", "-q", "--bare", str(bare))
            root = self._repo()
            _git(root, "remote", "add", "origin", str(bare))
            create_and_push_tag(root, "v1.2.3", remote="origin")
            self.assertTrue(tag_exists(root, "v1.2.3"))
            remote_tags = _git(root, "ls-remote", "--tags", "origin").stdout
            self.assertIn("refs/tags/v1.2.3", remote_tags)

    def test_create_and_push_tag_is_a_noop_when_already_correct(self):
        with tempfile.TemporaryDirectory() as bare_folder:
            bare = Path(bare_folder) / "origin.git"
            _git(Path(bare_folder), "init", "-q", "--bare", str(bare))
            root = self._repo()
            _git(root, "remote", "add", "origin", str(bare))
            create_and_push_tag(root, "v1.2.3", remote="origin")
            create_and_push_tag(root, "v1.2.3", remote="origin")
            self.assertTrue(tag_exists(root, "v1.2.3"))

    def test_create_and_push_tag_refuses_to_move_an_existing_tag(self):
        root = self._repo()
        _git(root, "tag", "v1.2.3")
        (root / "other.txt").write_text("x", encoding="utf-8")
        _git(root, "add", "other.txt")
        _git(root, "commit", "-q", "-m", "second")
        with self.assertRaisesRegex(ValueError, "already points at a different commit"):
            create_and_push_tag(root, "v1.2.3", remote="origin")


class CdnUrlTests(unittest.TestCase):
    def test_runtime_urls_are_the_pinned_tag_and_the_major_range(self):
        self.assertEqual(
            [
                "https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@v2.4.1/dist/nhimc-web.js",
                "https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@2/dist/nhimc-web.js",
            ],
            cdn_runtime_urls("2.4.1"),
        )


class RefreshCdnTests(unittest.TestCase):
    def _run(self, fetch):
        import tempfile
        import urllib.error
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "dist").mkdir()
            (Path(folder) / "dist/nhimc-web.js").write_bytes(b"runtime")
            with mock.patch.object(release_tag, "_get", fetch):
                return release_tag.refresh_cdn(Path(folder), "2.4.1", attempts=2, wait=0)

    def test_matching_bytes_are_fine(self):
        self.assertEqual([], self._run(lambda url, timeout: b"runtime"))

    def test_a_404_or_an_old_file_is_stale(self):
        import urllib.error
        def fetch(url, timeout):
            if "purge." in url:
                return b"{}"
            raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
        self.assertEqual(["stale", "stale"], [reason for _, reason in self._run(fetch)])

    def test_a_network_failure_is_unreachable_not_stale(self):
        import urllib.error
        def fetch(url, timeout):
            raise urllib.error.URLError("certificate verify failed")
        self.assertEqual(["unreachable", "unreachable"], [reason for _, reason in self._run(fetch)])


if __name__ == "__main__":
    unittest.main()
