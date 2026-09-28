import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.canonical_templates import (
    get_template_contract,
    load_template_contracts,
    validate_template_catalog,
)
from scripts.generate_template_registry import (
    registry_is_current,
    render_template_registry,
    update_template_registry,
)


ROOT = Path(__file__).resolve().parents[2]


class CanonicalTemplateTests(unittest.TestCase):
    def setUp(self):
        self._temporaries: list[tempfile.TemporaryDirectory] = []

    def tearDown(self):
        for temporary in self._temporaries:
            temporary.cleanup()

    def copy_repo_fixture(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self._temporaries.append(temporary)
        root = Path(temporary.name)
        shutil.copytree(ROOT / "vendor", root / "vendor")
        return root

    def rewrite_catalog(self, root: Path, mutate) -> None:
        path = root / "vendor/nhimc-design/templates/catalog.yaml"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        mutate(catalog)
        path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")

    def test_loads_all_nine_selectable_templates(self):
        contracts = load_template_contracts(ROOT)
        self.assertEqual(9, len(contracts))
        self.assertEqual(
            "assets/templates/list/default.html",
            contracts["list-default"].asset,
        )
        self.assertEqual(
            ("left", "left-blank", "top", "blog", "top-left"),
            contracts["list-default"].shells,
        )

    def test_rejects_unknown_template_id(self):
        with self.assertRaisesRegex(
            ValueError, "unknown canonical Template: invented-grid"
        ):
            get_template_contract(ROOT, "invented-grid")

    def test_rejects_missing_required_component_registration(self):
        root = self.copy_repo_fixture()
        self.rewrite_catalog(
            root,
            lambda catalog: catalog["templates"][0]["required_components"].append(
                "InventedWidget"
            ),
        )
        self.assertIn("InventedWidget", "\n".join(validate_template_catalog(root)))

    def test_rejects_duplicate_ids_and_unsafe_asset_paths(self):
        root = self.copy_repo_fixture()

        def mutate(catalog):
            catalog["templates"][1]["id"] = catalog["templates"][0]["id"]
            catalog["templates"][0]["template"] = "../outside.html"

        self.rewrite_catalog(root, mutate)
        errors = "\n".join(validate_template_catalog(root))
        self.assertIn("duplicate Template id", errors)
        self.assertIn("outside canonical Template assets", errors)

    def test_rejects_unknown_shell_and_uncatalogued_asset(self):
        root = self.copy_repo_fixture()
        self.rewrite_catalog(
            root,
            lambda catalog: catalog["templates"][0]["shell"].append("invented"),
        )
        extra = root / "vendor/nhimc-design/assets/templates/list/extra.html"
        extra.write_text("<!doctype html>", encoding="utf-8")
        errors = "\n".join(validate_template_catalog(root))
        self.assertIn("unknown shell invented", errors)
        self.assertIn("uncatalogued Template asset", errors)

    def test_generated_registry_is_sorted_and_bound_to_full_commit(self):
        payload = json.loads(render_template_registry(ROOT))
        self.assertEqual(
            "08c45402eece8a7c55afc60385e8671c9f13081a",
            payload["upstreamCommit"],
        )
        self.assertEqual(
            sorted(item["id"] for item in payload["templates"]),
            [item["id"] for item in payload["templates"]],
        )

    def test_registry_update_changes_bytes_once_and_check_detects_drift(self):
        root = self.copy_repo_fixture()
        (root / "VERSION").write_text("2.0.0\n", encoding="utf-8")
        (root / "registry").mkdir()
        self.assertTrue(update_template_registry(root))
        self.assertFalse(update_template_registry(root))
        self.assertTrue(registry_is_current(root))
        (root / "registry/templates.json").write_text("{}\n", encoding="utf-8")
        self.assertFalse(registry_is_current(root))


if __name__ == "__main__":
    unittest.main()
