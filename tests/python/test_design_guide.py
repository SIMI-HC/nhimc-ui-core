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
            for name in ("src", "vendor", "registry", "VERSION", "CHANGELOG.md"):
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
        self.assertIn("https://raw.githack.com/SIMI-HC/nhimc-ui-core/main/NHIMC.md", html)
        self.assertIn("이 파일만 읽고 NHIMC UI Core를 준비해줘. (git clone 금지)", html)
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

    def test_guide_header_shows_version_and_release_date_not_the_old_project_name(self):
        html = GUIDE.read_text(encoding="utf-8")
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        match = re.search(rf"^## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})", changelog, re.M)
        self.assertIsNotNone(match, "CHANGELOG.md has no entry for the current VERSION")
        self.assertIn(f"v{version} · 최종 업데이트 {match.group(1)}", html)
        self.assertNotIn("NhimcDesign", html)

    def test_guide_keeps_the_canonical_source_buttons_and_the_prompt_is_short(self):
        html = GUIDE.read_text(encoding="utf-8")
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIn("window.nhimcSourceUrl(item.source)", html)
        self.assertIn('textContent="정본 보기"', html)
        self.assertIn(f"https://github.com/SIMI-HC/nhimc-ui-core/blob/v{version}/", html)
        self.assertNotIn("#previewSource{display:none}", html)
        self.assertNotIn("이미 준비돼 있으면 원격 VERSION과 비교해", html)
        bootstrap = (ROOT / "bootstrap.md").read_text(encoding="utf-8")
        for phrase in ("원격 버전 확인", "git ls-remote --tags --sort=-v:refname", "사용자에게 먼저 묻습니다", "공식 경로로 설치·업데이트합니다", "Content Safe Area"):
            self.assertIn(phrase, bootstrap)
        self.assertIn("별도 프롬프트를 요구하지 않습니다", bootstrap)
        self.assertIn("## 준비 절차 (항상 이 순서로", bootstrap)
        for phrase in ("업데이트할지", "갱신함", "Design Guide를 표출합니다", "Design Guide`(열었음/링크 전달/생략: 이미 최신)"):
            self.assertIn(phrase, bootstrap)
        skill = (ROOT / "skills/nhimc-worktool/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("사용자에게 등록 여부를 묻기", skill)
        self.assertIn("Design Guide를 반드시 표출", skill)

    def test_guide_explains_the_two_presentation_frames_as_one_contract(self):
        data = _data(GUIDE.read_text(encoding="utf-8"))
        items = {item["id"]: item for item in data["items"]}
        self.assertIn("가로 발표", items["presentation"]["name"])
        self.assertIn("세로 발표", items["presentation-vertical"]["name"])
        for identifier in ("presentation", "presentation-vertical"):
            description = items[identifier]["description"]
            for phrase in ("공통 계약", "중앙 Content", "Slide animation", "Controller", "Theme", "Header", "Safe Area"):
                self.assertIn(phrase, description, identifier)
        self.assertIn("발표 Frame 두 가지, 계약은 하나", GUIDE.read_text(encoding="utf-8"))

    def test_guide_links_use_the_release_tag_and_a_host_that_renders_html(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for relative in ("bootstrap.md", "README.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(
                f"https://rawcdn.githack.com/SIMI-HC/nhimc-ui-core/v{version}/guide/nhimc-design-guide.html", text, relative
            )
        bootstrap = (ROOT / "bootstrap.md").read_text(encoding="utf-8")
        self.assertIn("클릭 링크", bootstrap)
        self.assertIn("디자인 가이드: https://rawcdn.githack.com/SIMI-HC/nhimc-ui-core/v{}/guide/nhimc-design-guide.html".format(version), bootstrap)
        self.assertIn("한 줄", bootstrap)
        self.assertIn(f"@v{version}/guide/nhimc-design-guide.html", bootstrap)

    def test_prompt_frame_and_theme_ids_are_supported_by_the_builder(self):
        from scripts.canonical_frame import ALL_FRAME_FILES as FRAME_FILES
        from scripts.theme_colors import theme_color_ids

        data = _data(GUIDE.read_text(encoding="utf-8"))
        frames = {item["id"] for item in data["items"] if item["type"] == "frame"}
        self.assertTrue(frames <= set(FRAME_FILES), frames - set(FRAME_FILES))
        self.assertEqual({theme["id"] for theme in data["themes"]}, set(theme_color_ids(ROOT)))
        self.assertTrue(re.search(r"bootstrap\.md", GUIDE.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
