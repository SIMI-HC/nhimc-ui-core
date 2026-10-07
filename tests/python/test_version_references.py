from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
# every pinned release reference: jsDelivr "nhimc-ui-core@v2.3.0/", githack ".../nhimc-ui-core/v2.3.0/"
PINNED = re.compile(r"nhimc-ui-core(?:@|/)v(\d+\.\d+\.\d+)(?=/)")
SKIPPED = {"CHANGELOG.md"}
PROMPT_FILES = ("README.md", "bootstrap.md", "guide/nhimc-design-guide.html", "guide/nhimc-design-guide-easy.html")


class VersionReferenceTests(unittest.TestCase):
    def test_every_pinned_release_reference_matches_version(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\n")
        stale = []
        for name in filter(None, tracked):
            path = ROOT / name
            if path.name in SKIPPED or name.startswith(("vendor/", "tests/")) or path.suffix not in {".md", ".json", ".html", ".js", ".py", ".cmd"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            stale += [f"{name}: v{found}" for found in PINNED.findall(text) if found != version]
        self.assertEqual([], stale, f"pinned references must equal VERSION {version}")

    def test_first_prompt_is_one_version_free_url(self):
        # users paste one fixed URL (the refs/heads/main form dodges a stale cache some web AIs keep for .../main/bootstrap.md)
        alias = "https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/refs/heads/main/bootstrap.md"
        for name in PROMPT_FILES:
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn(alias, text, name)
            self.assertNotIn("bootstrap.md?v=", text, name)
            self.assertNotIn("VERSION?v=", text, name)


if __name__ == "__main__":
    unittest.main()
