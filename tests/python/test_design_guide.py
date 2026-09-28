from pathlib import Path
import json
import re
import tempfile
import unittest

from scripts.build_design_guide import build_guide

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "guide/nhimc-design-guide.html"


def _data(html: str) -> dict:
    start = html.index("window.NHIMC_DESIGN_GALLERY = Object.freeze(") + len("window.NHIMC_DESIGN_GALLERY = Object.freeze(")
    end = html.index(");\n</script>", start)
    return json.loads(html[start:end].replace("<\\/", "</"))


class DesignGuideTests(unittest.TestCase):
    def test_committed_guide_matches_its_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            for name in ("src", "vendor", "registry", "VERSION"):
                source = ROOT / name
                target = temporary / name
                if source.is_dir():
                    __import__("shutil").copytree(source, target)
                else:
                    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8", newline="")
            rebuilt = build_guide(temporary).read_text(encoding="utf-8")
        self.assertEqual(GUIDE.read_text(encoding="utf-8"), rebuilt, "run python scripts/build_design_guide.py")

    def test_guide_is_single_offline_html_without_templates(self):
        html = GUIDE.read_text(encoding="utf-8")
        head = html[: html.index("window.NHIMC_DESIGN_GALLERY")]
        self.assertNotRegex(head, r'<link\b[^>]*rel="stylesheet"')
        self.assertNotRegex(head, r"<script\b[^>]*\bsrc=")
        self.assertNotRegex(head, r'(?:src|href)="(?:assets|\.\./)')
        data = _data(html)
        self.assertEqual({"frame", "component"}, {item["type"] for item in data["items"]})
        self.assertNotIn("template", data["counts"])
        self.assertFalse([key for key in data["documents"] if "/templates/" in key])
        self.assertNotIn('data-filter="template"', head)

    def test_guide_has_install_and_usage_menu_and_project_prompt(self):
        html = GUIDE.read_text(encoding="utf-8")
        self.assertIn('id="installView"', html)
        self.assertIn('id="galleryView"', html)
        self.assertIn('data-view="install"', html)
        self.assertIn("nhimc-worktool", html)
        self.assertNotIn('id="sectionUsage"', html)
        self.assertEqual(1, html.count('id="installPrompt"'))
        header = html[html.index('<header class="gallery-header">') : html.index("</header>")]
        self.assertLess(header.index('class="brand"'), header.index('id="viewNav"'))
        self.assertLess(header.index('id="viewNav"'), header.index('id="themeToggle"'))
        self.assertIn("https://github.com/SIMI-HC/nhimc-ui-core.git", html)
        self.assertIn("bootstrap.md만 읽고 NHIMC UI Core를 준비해줘.", html)
        self.assertNotIn("NHIMC Worktool 스킬로", html)
        self.assertIn("frame: ${builderState.frame", html)
        self.assertIn("theme: ${builderState.theme", html)
        self.assertNotIn('lines.push("template', html)

    def test_bootstrap_opens_guide_and_falls_back_to_download(self):
        text = (ROOT / "bootstrap.md").read_text(encoding="utf-8")
        for phrase in ("guide/nhimc-design-guide.html", "다운로드", "open-guide.cmd", "frame: <id>", "theme: <id>"):
            self.assertIn(phrase, text)
        self.assertTrue((ROOT / "open-guide.cmd").is_file())
        project = json.loads((ROOT / "registry/project.json").read_text(encoding="utf-8"))
        self.assertEqual("guide/nhimc-design-guide.html", project["designGuide"])
        self.assertTrue((ROOT / project["designGuide"]).is_file())

    def test_guide_links_use_the_release_tag_and_a_host_that_renders_html(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for relative in ("bootstrap.md", "README.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(
                f"https://rawcdn.githack.com/SIMI-HC/nhimc-ui-core/v{version}/guide/nhimc-design-guide.html", text, relative
            )
        bootstrap = (ROOT / "bootstrap.md").read_text(encoding="utf-8")
        self.assertIn("클릭 링크", bootstrap)
        self.assertIn(f"@v{version}/guide/nhimc-design-guide.html", bootstrap)

    def test_prompt_frame_and_theme_ids_are_supported_by_the_builder(self):
        from scripts.canonical_frame import FRAME_FILES
        from scripts.theme_colors import theme_color_ids

        data = _data(GUIDE.read_text(encoding="utf-8"))
        frames = {item["id"] for item in data["items"] if item["type"] == "frame"}
        self.assertTrue(frames <= set(FRAME_FILES), frames - set(FRAME_FILES))
        self.assertEqual({theme["id"] for theme in data["themes"]}, set(theme_color_ids(ROOT)))
        self.assertTrue(re.search(r"bootstrap\.md", GUIDE.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
