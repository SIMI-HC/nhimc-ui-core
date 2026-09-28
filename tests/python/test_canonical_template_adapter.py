from pathlib import Path
import unittest

from scripts.canonical_template_adapter import (
    adapt_canonical_template,
    inspect_content_root,
    scope_template_css,
    validate_authored_template_content,
)
from scripts.canonical_templates import get_template_contract, load_template_contracts


ROOT = Path(__file__).resolve().parents[2]


class CanonicalTemplateAdapterTests(unittest.TestCase):
    def test_extracts_list_default_content_and_scopes_css(self):
        contract = get_template_contract(ROOT, "list-default")
        bundle = adapt_canonical_template(ROOT, contract)
        self.assertEqual("list-default", bundle.template_id)
        self.assertIn('data-nhimc-role="content"', bundle.skeleton_html)
        self.assertIn('data-nhimc-template-root="list-default"', bundle.skeleton_html)
        self.assertIn(
            '[data-nhimc-template-root="list-default"] .toolbar',
            bundle.scoped_css,
        )
        self.assertNotIn("<html", bundle.skeleton_html.lower())
        self.assertNotIn(".sidebar", bundle.scoped_css)
        self.assertIn("PageHeader", bundle.components)
        self.assertIn("PaginationArea", bundle.components)

    def test_all_catalogued_templates_adapt_deterministically(self):
        contracts = load_template_contracts(ROOT)
        self.assertEqual(9, len(contracts))
        for template_id, contract in contracts.items():
            with self.subTest(template_id=template_id):
                first = adapt_canonical_template(ROOT, contract)
                second = adapt_canonical_template(ROOT, contract)
                self.assertEqual(first, second)
                self.assertRegex(first.source_sha256, r"^[0-9a-f]{64}$")
                self.assertTrue(set(contract.required_components) <= set(first.components))

    def test_scopes_grouped_nested_theme_and_pseudo_selectors(self):
        css = """
.toolbar, .field:hover::after { display:grid }
[data-theme="dark"] .card { color:white }
@media(max-width:767px){.toolbar{display:block}}
@supports(display:grid){.card > table{display:grid}}
@keyframes pulse{from{opacity:0}50%{opacity:.5}to{opacity:1}}
"""
        scoped = scope_template_css("list-default", css)
        root = '[data-nhimc-template-root="list-default"]'
        self.assertIn(f"{root} .toolbar", scoped)
        self.assertIn(f"{root} .field:hover::after", scoped)
        self.assertIn(f'[data-theme="dark"] {root} .card', scoped)
        self.assertIn(f"@media(max-width:767px){{{root} .toolbar", scoped)
        self.assertIn(f"@supports(display:grid){{{root} .card > table", scoped)
        self.assertIn("@keyframes pulse{from{opacity:0}50%{opacity:.5}to{opacity:1}}", scoped)

    def test_rejects_every_protected_frame_selector(self):
        selectors = (
            ":root",
            "html",
            "body",
            ".app-shell",
            ".sidebar",
            ".main",
            ".site-header",
            ".statusbar",
            ".dialog",
            "dialog",
            "#sidebarToggle",
            "#mobileMenuOpen",
            "#mobileMenuClose",
            "#helpDialog",
            '[data-nhimc-role="app-shell"]',
        )
        for selector in selectors:
            with self.subTest(selector=selector), self.assertRaisesRegex(
                ValueError, "protected Frame selector"
            ):
                scope_template_css("list-default", f".toolbar, {selector} {{display:grid}}")

    def test_rejects_malformed_external_and_font_css(self):
        cases = (
            ".card{background:url(sidecar.png)}",
            "@font-face{font-family:x;src:url(data:font/woff2;base64,AA)}",
            ".card{display:grid",
            "*{box-sizing:border-box}",
        )
        for css in cases:
            with self.subTest(css=css), self.assertRaises(ValueError):
                scope_template_css("list-default", css)

    def test_rejects_external_resources_in_inline_style(self):
        markup = (
            '<main data-nhimc-role="content" '
            'style="background:url(https://example.invalid/leak.png)"></main>'
        )
        with self.assertRaisesRegex(ValueError, "unsafe inline style"):
            inspect_content_root(markup)

    def test_authored_content_must_preserve_canonical_graph_and_components(self):
        contract = get_template_contract(ROOT, "list-default")
        canonical = adapt_canonical_template(ROOT, contract).skeleton_html
        validate_authored_template_content(ROOT, contract, canonical)

        missing_role = canonical.replace(' data-nhimc-role="search-filter"', "", 1)
        with self.assertRaisesRegex(
            ValueError, "Template list-default.*role search-filter"
        ):
            validate_authored_template_content(ROOT, contract, missing_role)

        missing_component = canonical.replace(
            ' data-nhimc-component="PageHeader"', "", 1
        )
        with self.assertRaisesRegex(
            ValueError, "Template list-default.*component PageHeader"
        ):
            validate_authored_template_content(ROOT, contract, missing_component)

        unknown_component = canonical.replace(
            'data-nhimc-component="PageHeader"',
            'data-nhimc-component="PageHeader InventedWidget"',
            1,
        )
        with self.assertRaisesRegex(
            ValueError, "Template list-default.*unknown component InventedWidget"
        ):
            validate_authored_template_content(ROOT, contract, unknown_component)

    def test_rejects_frame_owned_markup_inside_content(self):
        markup = (
            ROOT / "tests/fixtures/unsafe-authoring/template-frame-leak.html"
        ).read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "protected Frame role sidebar"):
            inspect_content_root(markup)


if __name__ == "__main__":
    unittest.main()
