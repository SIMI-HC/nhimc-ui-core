import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate_canonical_components import generate_components, parse_canonical_registry


ROOT = Path(__file__).resolve().parents[2]


class CanonicalComponentTests(unittest.TestCase):
    def test_generated_registry_contains_every_canonical_component(self):
        canonical = parse_canonical_registry(ROOT / "vendor/nhimc-design/components/registry.md")
        generated = json.loads((ROOT / "registry/components.json").read_text(encoding="utf-8"))["components"]

        self.assertEqual(49, len(canonical))
        self.assertEqual([item.id for item in canonical], [item["id"] for item in generated])

    def test_each_generated_component_points_to_canonical_specimen(self):
        showcase = ROOT / "vendor/nhimc-design/components/showcase.html"
        source = showcase.read_bytes().decode("utf-8")
        digest = hashlib.sha256(showcase.read_bytes()).hexdigest()
        components = json.loads((ROOT / "registry/components.json").read_text(encoding="utf-8"))["components"]

        for component in components:
            with self.subTest(component=component["id"]):
                self.assertEqual("vendor/nhimc-design/components/showcase.html", component["canonicalSource"])
                self.assertEqual(digest, component["canonicalDigest"])
                self.assertIn(component["markup"], source)

    def test_generation_is_deterministic_and_emits_exact_showcase_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            first = generate_components(ROOT, output_root=target)
            before = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}
            second = generate_components(ROOT, output_root=target)
            after = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}

        self.assertEqual(first, second)
        self.assertEqual(before, after)
        self.assertEqual(49, first["count"])
        self.assertTrue(before[Path("src/generated/components/components.css")])
        self.assertTrue(before[Path("src/generated/components/components.js")])


if __name__ == "__main__":
    unittest.main()
