import tempfile
import json
from html.parser import HTMLParser
import re
import unittest
from pathlib import Path

from scripts.validate_design import BASELINE_COMPONENT_IDS, validate_design


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


def _luminance(hex_color: str) -> float:
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first: str, second: str) -> float:
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


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

    def test_theme_cannot_declare_protected_frame_dimensions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            registry = json.loads((root / "registry/themes.json").read_text(encoding="utf-8"))
            registry["themes"][0]["tokens"].append("--nhimc-frame-sidebar-width")
            (root / "registry/themes.json").write_text(json.dumps(registry), encoding="utf-8")
            (root / "src/themes/nhimc-light.css").write_text(
                ":root { --nhimc-color-surface: #fff; --nhimc-frame-sidebar-width: 20rem; }",
                encoding="utf-8",
            )
            self.assertIn(
                "design.protected-frame-token",
                {item.rule for item in validate_design(root)},
            )

    def test_frame_overrides_and_example_component_css_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "src/components/override.css").write_text(
                "nhimc-frame { display: none; }", encoding="utf-8"
            )
            (root / "examples/demo").mkdir(parents=True)
            (root / "examples/demo/local.css").write_text(
                ".nhimc-button { padding: 1rem; }", encoding="utf-8"
            )
            rules = {item.rule for item in validate_design(root)}
            self.assertIn("design.frame-override", rules)
            self.assertIn("design.local-component-style", rules)

    def test_unregistered_font_and_icon_assets_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "src/components/asset.css").write_text(
                '.sample { font-family: "Rogue Font"; background-image: url("../assets/icons/rogue.svg"); }',
                encoding="utf-8",
            )
            (root / "examples/demo").mkdir(parents=True)
            (root / "examples/demo/index.html").write_text(
                '<img src="../../src/assets/icons/rogue.svg" alt="">',
                encoding="utf-8",
            )
            rules = {item.rule for item in validate_design(root)}
            self.assertIn("design.unregistered-font", rules)
            self.assertIn("design.unregistered-icon", rules)

    def test_new_component_requires_a_decision_record(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "registry/components.json").write_text(
                json.dumps({"baselineIds": ["new-widget"], "components": [{"id": "new-widget"}]}),
                encoding="utf-8",
            )
            self.assertIn(
                "design.missing-component-decision",
                {item.rule for item in validate_design(root)},
            )

    def test_example_inline_external_and_injected_styles_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            example = root / "examples/demo"
            example.mkdir(parents=True)
            (example / "index.html").write_text(
                '<link rel="stylesheet" href="https://fonts.example.org/font.css">'
                '<style>.local { padding: 1rem; }</style><div style="margin: 0"></div>'
                "<script>document.body.style.setProperty('--frame-sidebar', '99rem');</script>",
                encoding="utf-8",
            )
            rules = {item.rule for item in validate_design(root)}
            self.assertIn("design.example-inline-style", rules)
            self.assertIn("design.external-asset", rules)
            self.assertIn("design.example-style-injection", rules)

    def test_component_registry_entries_are_complete_and_implemented(self):
        registry = json.loads(
            (ROOT / "registry/components.json").read_text(encoding="utf-8")
        )["components"]
        css = (ROOT / "src/components/components.css").read_text(encoding="utf-8")
        ids = [item["id"] for item in registry]
        document = json.loads((ROOT / "registry/components.json").read_text(encoding="utf-8"))

        self.assertGreaterEqual(len(registry), 18)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), BASELINE_COMPONENT_IDS)
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
                self.assertIsInstance(item["markup"], str)
                self.assertTrue(item["markup"].startswith("<"))
                self.assertIn(item["selector"], css)
        by_id = {item["id"]: item for item in registry}
        self.assertIn("aria-controls", by_id["tabs"]["markup"])
        self.assertIn("role=\"tabpanel\"", by_id["tabs"]["markup"])
        self.assertIn("data-nhimc-dialog-open", by_id["dialog"]["markup"])
        self.assertIn("data-nhimc-dialog-close", by_id["dialog"]["markup"])

    def test_bundled_fonts_are_declared_loaded_and_contrast_is_accessible(self):
        font_css = (ROOT / "src/themes/nhimc-fonts.css").read_text(encoding="utf-8")
        self.assertEqual(6, font_css.count("@font-face"))
        for weight in (300, 400, 700):
            for subset in ("korean", "latin"):
                self.assertIn(f"noto-sans-kr-{subset}-{weight}.woff2", font_css)
        for relative in (
            "examples/operations/index.html",
            "examples/administration/index.html",
            "tests/browser/runner.html",
        ):
            self.assertIn("nhimc-fonts.css", (ROOT / relative).read_text(encoding="utf-8"))

        theme = (ROOT / "src/themes/nhimc-light.css").read_text(encoding="utf-8")
        values = dict(re.findall(r"(--nhimc-[a-z0-9-]+):\s*(#[0-9a-f]{6})", theme, re.I))
        self.assertGreaterEqual(contrast(values["--nhimc-color-focus"], values["--nhimc-color-surface"]), 3)
        self.assertGreaterEqual(contrast(values["--nhimc-color-focus"], values["--nhimc-color-canvas"]), 3)
        self.assertGreaterEqual(contrast(values["--nhimc-color-warning"], values["--nhimc-color-surface-subtle"]), 4.5)

    def test_examples_share_frame_without_copying_it(self):
        expected_imports = {
            "../../src/frame/nhimc-frame.js",
            "../../src/themes/nhimc-light.css",
            "../../src/themes/nhimc-fonts.css",
            "../../src/layouts/application.css",
            "../../src/layouts/primitives.css",
            "../../src/components/components.css",
        }
        menus = []
        for name in ("operations", "administration"):
            html_path = ROOT / f"examples/{name}/index.html"
            html = html_path.read_text(encoding="utf-8")
            script = "\n".join(
                re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.I | re.S)
            )
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
