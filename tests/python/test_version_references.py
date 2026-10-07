from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
# every pinned release reference: jsDelivr "nhimc-ui-core@v2.3.0/", githack ".../nhimc-ui-core/v2.3.0/"
PINNED = re.compile(r"nhimc-ui-core(?:@|/)v(\d+\.\d+\.\d+)(?=/)")
# cache-busting query on the two raw URLs of the first prompt: ".../main/bootstrap.md?v=2.3.1", ".../main/VERSION?v=2.3.1"
CACHE_BUSTED = re.compile(r"/main/(?:bootstrap\.md|VERSION)\?v=(\d+\.\d+\.\d+)")
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
            stale += [f"{name}: v{found}" for found in PINNED.findall(text) + CACHE_BUSTED.findall(text) if found != version]
        self.assertEqual([], stale, f"pinned references must equal VERSION {version}")

    def test_first_prompt_gives_both_raw_urls_with_the_current_cache_buster(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for name in PROMPT_FILES:
            text = (ROOT / name).read_text(encoding="utf-8")
            for target in ("bootstrap.md", "VERSION"):
                self.assertIn(f"/main/{target}?v={version}", text, f"{name} must hand the AI /main/{target}?v={version}")


if __name__ == "__main__":
    unittest.main()
