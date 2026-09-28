import tempfile
import json
from html.parser import HTMLParser
import re
import unittest
from pathlib import Path

from scripts.validate_design import validate_design


ROOT = Path(__file__).resolve().parents[2]


class ExampleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.references = set()
        self.classes = set()

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        values = dict(attrs)
        for key in ("href", "src"):
            if values.get(key):
                self.references.add(values[key])
        self.classes.update(values.get("class", "").split())


def parse_example(text: str) -> ExampleParser:
    parser = ExampleParser()
    parser.feed(text)
    return parser


def extract_imports(script: str) -> set[str]:
    return set(re.findall(r"(?:from\s+)?['\"]([^'\"]+)['\"]", script))


def count_registered_classes(classes: set[str], root: Path) -> int:
    registered = {
        item["selector"].removeprefix(".")
        for item in json.loads(
            (root / "registry/components.json").read_text(encoding="utf-8")
        )["components"]
    }
    registered.update(
        {
            "nhimc-page", "nhimc-page-header", "nhimc-section", "nhimc-stack",
            "nhimc-grid", "nhimc-form-grid", "nhimc-toolbar", "nhimc-field-group",
            "nhimc-content-card",
        }
    )
    return len(classes & registered)


def extract_literal_menu_shape(script: str) -> tuple[int, int]:
    return (len(re.findall(r"\bid\s*:\s*['\"]", script)), len(re.findall(r"\bchildren\s*:", script)))


def make_minimal_design_root(root: Path) -> Path:
    (root / "src/themes").mkdir(parents=True)
    (root / "src/components").mkdir()
    (root / "registry").mkdir()
    (root / "registry/themes.json").write_text(
        '{"schemaVersion":1,"themes":[{"id":"nhimc-light",'
        '"file":"src/themes/nhimc-light.css",'
        '"tokens":["--nhimc-color-surface"]}]}\n',
        encoding="utf-8",
    )
    (root / "src/themes/nhimc-light.css").write_text(
        ':root { --nhimc-color-surface: #ffffff; }\n', encoding="utf-8"
    )
    return root


class DesignRuleTests(unittest.TestCase):
    def test_repository_obeys_design_rules(self):
        self.assertEqual([], validate_design(ROOT))

    def test_theme_rejects_unknown_token_and_selector(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "src/themes/nhimc-light.css").write_text(
                ".business-card { --unknown-color: #fff; }", encoding="utf-8"
            )

            rules = {item.rule for item in validate_design(root)}

            self.assertIn("design.theme-selector", rules)
            self.assertIn("design.unregistered-token", rules)

    def test_templates_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "templates").mkdir()

            self.assertIn(
                "design.template-system", {item.rule for item in validate_design(root)}
            )

    def test_hard_coded_color_outside_theme_is_rejected_case_insensitively(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "src/components/example.css").write_text(
                ".sample { color : #AABBCC; background: rgb(1, 2, 3); }",
                encoding="utf-8",
            )

            rules = [item.rule for item in validate_design(root)]

            self.assertEqual(2, rules.count("design.hard-coded-color"))

    def test_colors_inside_comments_are_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "src/components/example.css").write_text(
                "/* old color #AABBCC and rgb(1, 2, 3) */\n.sample { color: var(--nhimc-color-surface); }",
                encoding="utf-8",
            )

            self.assertEqual([], validate_design(root))

    def test_component_registry_entries_are_complete_and_implemented(self):
        registry = json.loads(
            (ROOT / "registry/components.json").read_text(encoding="utf-8")
        )["components"]
        css = (ROOT / "src/components/components.css").read_text(encoding="utf-8")
        ids = [item["id"] for item in registry]

        self.assertGreaterEqual(len(registry), 18)
        self.assertEqual(len(ids), len(set(ids)))
        for item in registry:
            with self.subTest(component=item["id"]):
                self.assertTrue(item["selector"].startswith(".nhimc-"))
                self.assertIsInstance(item["states"], list)
                self.assertGreater(len(item["states"]), 0)
                self.assertIsInstance(item["accessibility"], list)
                self.assertGreater(len(item["accessibility"]), 0)
                self.assertIsInstance(item["tokens"], list)
                self.assertGreater(len(item["tokens"]), 0)
                self.assertEqual("src/components/components.css", item["implementation"])
                self.assertTrue(item["exampleMarker"].startswith("component:"))
                self.assertIn(item["selector"], css)

    def test_examples_share_frame_without_copying_it(self):
        expected_imports = {
            "../../src/frame/nhimc-frame.js",
            "../../src/themes/nhimc-light.css",
            "../../src/layouts/primitives.css",
            "../../src/components/components.css",
        }
        menus = []
        for name in ("operations", "administration"):
            html_path = ROOT / f"examples/{name}/index.html"
            js_path = ROOT / f"examples/{name}/app.js"
            html = html_path.read_text(encoding="utf-8")
            script = js_path.read_text(encoding="utf-8")
            parsed = parse_example(html)

            self.assertEqual(1, parsed.tags.count("nhimc-frame"), name)
            self.assertTrue(
                expected_imports.issubset(parsed.references | extract_imports(script)),
                name,
            )
            self.assertNotIn("header", parsed.tags, name)
            self.assertNotIn("<style", html.lower(), name)
            self.assertNotIn("::part", html + script, name)
            self.assertNotRegex(html + script, r"#[0-9a-fA-F]{3,8}|(?:rgb|hsl)a?\(")
            self.assertNotRegex(html + script, r"(?i)patient|medical record|resident number")
            self.assertGreaterEqual(count_registered_classes(parsed.classes, ROOT), 7, name)
            menus.append(extract_literal_menu_shape(script))
        self.assertNotEqual(menus[0], menus[1])


if __name__ == "__main__":
    unittest.main()
