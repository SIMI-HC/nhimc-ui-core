from pathlib import Path
import re
import unittest

from scripts.content_rules import validate_content

ROOT = Path(__file__).resolve().parents[2]


def _content(markup: str) -> str:
    return f'<main data-nhimc-role="content">{markup}</main>'


class ContentClassTests(unittest.TestCase):
    def test_an_unstyled_class_is_rejected_with_the_registered_replacement(self):
        markup = _content('<section class="metrics"><article class="card metric"><span>전체</span><strong>24</strong></article></section>')
        with self.assertRaises(ValueError) as caught:
            validate_content(ROOT, markup)
        message = str(caught.exception)
        self.assertIn("metric, metrics", message)
        self.assertIn("nhimc-stat", message)

    def test_the_classes_of_the_registered_primitives_pass(self):
        markup = _content(
            '<div class="nhimc-grid nhimc-stat-grid"><section class="card nhimc-card nhimc-stat" data-nhimc-accent="sky" data-nhimc-component="Stat">'
            '<div class="nhimc-card-head"><strong>전체 요청</strong></div>'
            '<div class="nhimc-card-body nhimc-stat-body"><p class="nhimc-stat-value">37<span class="nhimc-stat-unit">건</span></p>'
            '<small class="nhimc-stat-note">오늘 접수</small></div></section></div>'
        )
        validate_content(ROOT, markup)

    def test_every_authoring_fixture_uses_only_styled_classes(self):
        for fixture in sorted((ROOT / "tests/fixtures/authoring").glob("*/index.html")):
            html = fixture.read_text(encoding="utf-8")
            for content in re.findall(r'<main data-nhimc-role="content".*?</main>', html, re.S):
                validate_content(ROOT, content)


class DocumentedSnippetTests(unittest.TestCase):
    def test_every_page_snippet_in_the_docs_passes_the_content_rules(self):
        for name in ("bootstrap.md", "skills/nhimc-worktool/SKILL.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            section = text.split("## 자주 쓰는 Page 조각", 1)[1].split("## Core 아이콘 추가 절차", 1)[0]
            blocks = re.findall(r"```html\n(.*?)```", section, re.S)
            self.assertGreaterEqual(len(blocks), 2, name)
            for block in blocks:
                validate_content(ROOT, _content(block))


if __name__ == "__main__":
    unittest.main()
