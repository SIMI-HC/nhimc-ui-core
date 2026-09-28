import tempfile
import json
import unittest
from pathlib import Path

from scripts.validate_design import validate_design


ROOT = Path(__file__).resolve().parents[2]


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


if __name__ == "__main__":
    unittest.main()
