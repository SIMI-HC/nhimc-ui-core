from pathlib import Path
import tempfile
import unittest

from scripts.skill_resources import MIRROR_ROOT, compare, iter_source_relative_paths


class IterSourceRelativePathsTests(unittest.TestCase):
    def setUp(self):
        self._temporaries: list[tempfile.TemporaryDirectory] = []

    def tearDown(self):
        for temporary in self._temporaries:
            temporary.cleanup()

    def _root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self._temporaries.append(temporary)
        return Path(temporary.name)

    def _write(self, root: Path, relative: str, data: bytes = b"x") -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def test_lists_files_under_each_source_dir_and_version(self):
        root = self._root()
        self._write(root, "registry/frames.json")
        self._write(root, "scripts/build_release.py")
        self._write(root, "guide/nhimc-design-guide.html")
        self._write(root, "vendor/nhimc-design/upstream.json")
        self._write(root, "VERSION")
        result = {path.as_posix() for path in iter_source_relative_paths(root)}
        self.assertEqual(
            result,
            {
                "registry/frames.json",
                "scripts/build_release.py",
                "guide/nhimc-design-guide.html",
                "vendor/nhimc-design/upstream.json",
                "VERSION",
            },
        )

    def test_excludes_pycache_and_pyc(self):
        root = self._root()
        self._write(root, "scripts/build_release.py")
        self._write(root, "scripts/__pycache__/build_release.cpython-312.pyc")
        self._write(root, "scripts/stale.pyc")
        result = {path.as_posix() for path in iter_source_relative_paths(root)}
        self.assertEqual(result, {"scripts/build_release.py"})


class CompareTests(unittest.TestCase):
    def setUp(self):
        self._temporaries: list[tempfile.TemporaryDirectory] = []

    def tearDown(self):
        for temporary in self._temporaries:
            temporary.cleanup()

    def _root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self._temporaries.append(temporary)
        return Path(temporary.name)

    def _write(self, root: Path, relative: str, data: bytes = b"x") -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def test_reports_missing_mirror_file(self):
        root = self._root()
        self._write(root, "VERSION", b"1.3.2\n")
        findings = compare(root)
        self.assertTrue(any(item.rule == "skill-resources.missing" for item in findings))

    def test_reports_mismatched_mirror_file(self):
        root = self._root()
        self._write(root, "VERSION", b"1.3.2\n")
        self._write(root, (MIRROR_ROOT / "VERSION").as_posix(), b"1.3.1\n")
        findings = compare(root)
        self.assertTrue(any(item.rule == "skill-resources.mismatch" for item in findings))

    def test_reports_orphan_mirror_file(self):
        root = self._root()
        self._write(root, "VERSION", b"1.3.2\n")
        self._write(root, (MIRROR_ROOT / "VERSION").as_posix(), b"1.3.2\n")
        self._write(root, (MIRROR_ROOT / "registry/deleted.json").as_posix(), b"{}")
        findings = compare(root)
        self.assertTrue(any(item.rule == "skill-resources.orphan" for item in findings))

    def test_clean_mirror_reports_nothing(self):
        root = self._root()
        self._write(root, "VERSION", b"1.3.2\n")
        self._write(root, (MIRROR_ROOT / "VERSION").as_posix(), b"1.3.2\n")
        self.assertEqual(compare(root), [])


if __name__ == "__main__":
    unittest.main()
