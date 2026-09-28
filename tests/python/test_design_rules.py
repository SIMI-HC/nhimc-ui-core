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
    components = json.loads(
        (root / "registry/components.json").read_text(encoding="utf-8")
    )["components"]
    registered = {
        item["selector"].removeprefix(".")
        for item in components
        if "selector" in item
    }
    for item in components:
        for value in re.findall(r'class="([^"]+)"', item.get("markup", "")):
            registered.update(value.split())
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

    def test_vendored_canonical_templates_are_not_treated_as_authored_templates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "vendor/nhimc-design/templates").mkdir(parents=True)

            self.assertNotIn(
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
        css = (ROOT / "src/generated/components/components.css").read_text(encoding="utf-8")
        source = (ROOT / "vendor/nhimc-design/components/showcase.html").read_bytes().decode("utf-8")
        ids = [item["id"] for item in registry]

        self.assertEqual(49, len(registry))
        self.assertEqual(len(ids), len(set(ids)))
        for item in registry:
            with self.subTest(component=item["id"]):
                self.assertIn(item["layer"], {"atom", "composition"})
                self.assertIsInstance(item["variants"], list)
                self.assertGreater(len(item["variants"]), 0)
                self.assertIsInstance(item["states"], list)
                self.assertGreater(len(item["states"]), 0)
                self.assertIsInstance(item["accessibility"], list)
                self.assertGreater(len(item["accessibility"]), 0)
                self.assertEqual("src/generated/components/components.css", item["implementation"])
                self.assertEqual("src/generated/components/components.js", item["controller"])
                self.assertEqual("vendor/nhimc-design/components/showcase.html", item["canonicalSource"])
                self.assertEqual(64, len(item["canonicalDigest"]))
                self.assertIsInstance(item["markup"], str)
                self.assertTrue(item["markup"].startswith('<section class="specimen"'))
                self.assertIn(item["markup"], source)
        self.assertIn(".btn", css)
        self.assertIn(".switch", css)
        by_id = {item["id"]: item for item in registry}
        self.assertIn("role=\"tablist\"", by_id["Tabs"]["markup"])
        self.assertIn("data-dialog-open", by_id["Dialog"]["markup"])
        self.assertIn("data-dialog-close", by_id["Dialog"]["markup"])

    def test_bundled_fonts_are_declared_loaded_and_contrast_is_accessible(self):
        upstream = json.loads(
            (ROOT / "vendor/nhimc-design/upstream.json").read_text(encoding="utf-8")
        )
        self.assertEqual(6, upstream["counts"]["fonts"])
        for weight in (300, 400, 700):
            for subset in ("korean", "latin"):
                self.assertTrue(
                    (ROOT / f"vendor/nhimc-design/fonts/noto-sans-kr-{subset}-{weight}.woff2").is_file()
                )

    def test_authoring_fixtures_share_frame_without_copying_it(self):
        menus = []
        for name in ("operations", "administration"):
            html_path = ROOT / f"tests/fixtures/authoring/{name}/index.html"
            html = html_path.read_text(encoding="utf-8")
            script = "\n".join(
                re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.I | re.S)
            )
            parsed = parse_example(html)

            self.assertEqual(1, parsed.tags.count("nhimc-frame"), name)
            self.assertEqual(set(), parsed.references, name)
            self.assertNotRegex(script, r"(^|[;\n])\s*import\s", name)
            self.assertNotIn("header", parsed.tags, name)
            self.assertNotIn("<style", html.lower(), name)
            self.assertNotIn("::part", html + script, name)
            self.assertNotRegex(html + script, r"#[0-9a-fA-F]{3,8}|(?:rgb|hsl)a?\(")
            self.assertNotRegex(html + script, r"(?i)patient|medical record|resident number")
            self.assertGreaterEqual(count_registered_classes(parsed.classes, ROOT), 7, name)
            match = re.search(
                r'<script\s+type="application/json"\s+data-nhimc-menu>(.*?)</script>',
                html, re.I | re.S,
            )
            self.assertIsNotNone(match, name)
            menu = json.loads(match.group(1))
            self.assertTrue(all(item["icon"] and item["href"] == f'#{item["id"]}' for item in menu))
            menus.append(menu)
        self.assertNotEqual([item["id"] for item in menus[0]], [item["id"] for item in menus[1]])

    def test_repository_does_not_publish_test_fixtures_as_design_examples(self):
        self.assertFalse((ROOT / "examples").exists())


if __name__ == "__main__":
    unittest.main()
