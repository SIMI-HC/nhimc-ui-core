import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import shutil

from scripts.build_single_html import (
    build_single_html,
    inspect_completion_manifest,
    parse_authoring_screens,
)
from scripts.canonical_template_adapter import adapt_canonical_template
from scripts.canonical_templates import get_template_contract


ROOT = Path(__file__).resolve().parents[2]


class SingleHtmlArtifactTests(unittest.TestCase):
    def _run_builder(self, source: Path, output: Path):
        return subprocess.run(
            [
                sys.executable,
                "scripts/build_single_html.py",
                "--input",
                str(source),
                "--output",
                str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    @staticmethod
    def _document(fragment: str) -> str:
        content = adapt_canonical_template(
            ROOT, get_template_contract(ROOT, "list-default")
        ).skeleton_html
        return (
            "<!doctype html><html><head></head><body>"
            '<nhimc-frame id="app-frame" data-frame="left" '
            'data-template="list-default" data-project-title="일산병원 업무도구" '
            'data-active-id="ambulance">'
            f'{content}{fragment}</nhimc-frame>'
            '<script type="application/json" data-nhimc-menu>'
            '[{"id":"ambulance","label":"이송 현황","icon":"ambulance","href":"#ambulance"}]'
            '</script>'
            "</body></html>"
        )

    def test_v3_artifact_contains_template_bundle_and_completion_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            build_single_html(
                ROOT, ROOT / "tests/fixtures/authoring/operations/index.html", output
            )
            html = output.read_text(encoding="utf-8")
            manifest = inspect_completion_manifest(html)

            self.assertIn('data-nhimc-template-root="list-default"', html)
            self.assertIn('data-nhimc-template-bundle="list-default"', html)
            self.assertEqual("nhimc-single-html", manifest["artifactType"])
            self.assertEqual(3, manifest["schemaVersion"])
            self.assertEqual(
                [{"screenId": "ambulance", "templateId": "list-default"}],
                manifest["screens"],
            )
            self.assertEqual(0, manifest["sidecarCount"])
            self.assertIs(True, manifest["verificationRequired"])

    def test_rejects_bare_legacy_business_layout(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            with self.assertRaisesRegex(
                ValueError, "data-template.*registered canonical Template"
            ):
                build_single_html(
                    ROOT,
                    ROOT / "tests/fixtures/unsafe-authoring/bare-business-layout.html",
                    output,
                )
            self.assertFalse(output.exists())

    def test_completion_manifest_rejects_authoring_and_already_built_spoof(self):
        source = ROOT / "tests/fixtures/authoring/operations/index.html"
        with self.assertRaisesRegex(ValueError, "not a completed artifact"):
            inspect_completion_manifest(source.read_text(encoding="utf-8"))
        spoof = ROOT / "tests/fixtures/unsafe-authoring/already-built-artifact.html"
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            with self.assertRaisesRegex(ValueError, "already.*completed artifact"):
                build_single_html(ROOT, spoof, output)
            self.assertFalse(output.exists())

    def test_multiple_panels_bind_navigation_to_templates_in_order(self):
        source = (
            ROOT / "tests/fixtures/unsafe-authoring/mixed-screen-templates.html"
        ).read_text(encoding="utf-8")
        for template_id in ("list-default", "admin-master-detail"):
            skeleton = adapt_canonical_template(
                ROOT, get_template_contract(ROOT, template_id)
            ).skeleton_html
            source = source.replace(
                f'<main data-nhimc-role="content" data-nhimc-template-root="{template_id}"></main>',
                skeleton,
            )
        screens = parse_authoring_screens(source)
        self.assertEqual(
            [("ambulance", "list-default"), ("roles", "admin-master-detail")],
            [(screen.screen_id, screen.template_id) for screen in screens],
        )
        broken = source.replace('data-screen-panel="roles"', 'data-screen-panel="other"')
        with self.assertRaisesRegex(ValueError, "navigation.*panel.*1:1"):
            parse_authoring_screens(broken)

    def test_rejects_unknown_template_and_unsupported_frame_pair(self):
        valid = self._document("")
        with self.assertRaisesRegex(ValueError, "unknown canonical Template"):
            parse_authoring_screens(valid.replace("list-default", "invented-grid"))
        unsupported = valid.replace('data-frame="left"', 'data-frame="presentation"')
        with self.assertRaisesRegex(ValueError, "does not support Frame presentation"):
            parse_authoring_screens(unsupported)

    def test_builder_emits_one_self_contained_offline_html(self):
        with tempfile.TemporaryDirectory() as folder:
            output_dir = Path(folder) / "deliverable"
            output = output_dir / "index.html"
            output_dir.mkdir(parents=True)
            shutil.copyfile(ROOT / "tests/fixtures/authoring/operations/index.html", output)
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_single_html.py",
                    "--input",
                    str(output),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(["index.html"], [path.name for path in output_dir.iterdir()])

            html = output.read_text(encoding="utf-8")
            version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
            self.assertIn(f'name="nhimc-core-version" content="{version}"', html)
            self.assertIn('name="nhimc-upstream-commit" content="08c45402eece"', html)
            self.assertIn('data-nhimc-role="app-shell"', html)
            self.assertIn('href="#ambulance"', html)
            self.assertEqual(6, html.count("@font-face"))
            self.assertIn("data:font/woff2;base64,", html)
            self.assertIn('data-nhimc-component-bundle="canonical"', html)
            self.assertIn('<use href="#ambulance"></use>', html)
            self.assertIn("default-src 'none'", html)
            self.assertNotIn("<nhimc-frame", html)
            self.assertNotIn("customElements.define('nhimc-frame'", html)
            self.assertNotIn("☰", html)
            self.assertNotIn("‹", html)
            self.assertNotIn('rel="stylesheet"', html)
            self.assertNotIn('type="module"', html)
            self.assertNotIn("import.meta", html)
            self.assertNotIn(" from './", html)
            self.assertNotIn(" from '../../", html)
            self.assertNotIn('src="./app.js"', html)
            self.assertNotIn("../../src/", html)

    def test_builder_rejects_every_runtime_sidecar_or_network_form(self):
        cases = {
            "css-url": '<style>body{background:url(sidecar.png)}</style>',
            "css-import": '<style>@import "sidecar.css";</style>',
            "srcset": '<img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" srcset="sidecar.png 2x">',
            "poster": '<video poster="sidecar.png"></video>',
            "object": '<object data="sidecar.svg"></object>',
            "embed": '<embed src="sidecar.svg">',
            "dynamic-import": '<script type="module" data-nhimc-business>import("https://example.com/code.js")</script>',
            "fetch": '<script type="module" data-nhimc-business>fetch("sidecar.json")</script>',
        }
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, fragment in cases.items():
                with self.subTest(name=name):
                    source = root / f"{name}.html"
                    output = root / f"{name}-output.html"
                    source.write_text(
                        self._document(fragment),
                        encoding="utf-8",
                    )
                    result = self._run_builder(source, output)
                    self.assertNotEqual(0, result.returncode, name)
                    self.assertFalse(output.exists(), name)

    def test_builder_rejects_already_built_input_without_changing_it(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            shutil.copyfile(ROOT / "tests/fixtures/authoring/operations/index.html", output)
            first = self._run_builder(output, output)
            self.assertEqual(0, first.returncode, first.stderr)
            original = output.read_bytes()

            second = self._run_builder(output, output)

            self.assertNotEqual(0, second.returncode)
            self.assertIn("already contains a completed artifact manifest", second.stderr)
            self.assertEqual(original, output.read_bytes())

    def test_two_builds_from_same_source_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / "first.html"
            second = Path(folder) / "second.html"
            source = ROOT / "tests/fixtures/authoring/operations/index.html"
            first_result = self._run_builder(source, first)
            second_result = self._run_builder(source, second)

            self.assertEqual(0, first_result.returncode, first_result.stderr)
            self.assertEqual(0, second_result.returncode, second_result.stderr)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_builder_rejects_business_design_rule_bypasses(self):
        cases = {
            "inline-style": '<main style="color:red"></main>',
            "style-block": '<style>nhimc-frame{display:none}</style>',
            "style-injection": '<script type="module" data-nhimc-business>document.body.style.setProperty("--nhimc-color-primary", "red")</script>',
            "unregistered-icon": '<img src="custom-icon.svg">',
        }
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, fragment in cases.items():
                with self.subTest(name=name):
                    source = root / f"{name}.html"
                    output = root / f"{name}-output.html"
                    source.write_text(
                        self._document(fragment),
                        encoding="utf-8",
                    )
                    result = self._run_builder(source, output)
                    self.assertNotEqual(0, result.returncode, name)
                    self.assertFalse(output.exists(), name)

    def test_builder_rejects_parser_and_pre_csp_bypasses(self):
        cases = {
            "classic-script": '<script>fetch("https://example.com/leak")</script>',
            "meta-refresh": '<meta http-equiv=refresh content="0;url=https://example.com">',
            "unquoted-src": "<img src=sidecar.png>",
            "unquoted-srcset": "<img srcset=sidecar.png>",
            "unquoted-stylesheet": "<link rel=stylesheet href=sidecar.css>",
        }
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, fragment in cases.items():
                with self.subTest(name=name):
                    source = root / f"{name}.html"
                    output = root / f"{name}-output.html"
                    source.write_text(self._document(fragment), encoding="utf-8")
                    result = self._run_builder(source, output)
                    self.assertNotEqual(0, result.returncode, name)
                    self.assertFalse(output.exists(), name)

    def test_builder_requires_one_shared_frame_without_copied_chrome(self):
        cases = {
            "missing-frame": "<!doctype html><html><head></head><body><main>Work</main></body></html>",
            "multiple-frames": "<!doctype html><html><head></head><body><nhimc-frame></nhimc-frame><nhimc-frame></nhimc-frame></body></html>",
            "copied-sidebar": self._document('<aside class="sidebar">Copied</aside>'),
            "copied-statusbar": self._document('<footer class="statusbar">Copied</footer>'),
        }
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, html in cases.items():
                with self.subTest(name=name):
                    source = root / f"{name}.html"
                    output = root / f"{name}-output.html"
                    source.write_text(html, encoding="utf-8")
                    result = self._run_builder(source, output)
                    self.assertNotEqual(0, result.returncode, name)
                    self.assertFalse(output.exists(), name)

    def test_standalone_file_option_opens_the_actual_artifact(self):
        with tempfile.TemporaryDirectory(prefix="NHIMC 실제 산출물 ") as folder:
            output = Path(folder) / "index.html"
            result = self._run_builder(
                ROOT / "tests/fixtures/authoring/operations/index.html", output
            )
            self.assertEqual(0, result.returncode, result.stderr)

            browser = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_browser_tests.py",
                    "--standalone-file",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            self.assertEqual(0, browser.returncode, browser.stdout + browser.stderr)
            self.assertIn("standalone artifact:", browser.stdout)
            self.assertIn("index.html", browser.stdout)
            self.assertIn("standalone file: PASS", browser.stdout)

    def test_actual_artifact_browser_check_rejects_startup_errors_and_marker_spoof(self):
        cases = {
            "sync-error": 'throw new Error("business startup failed");',
            "async-error": 'setTimeout(() => { throw new Error("late startup failed"); }, 0);',
            "later-error": 'setTimeout(() => { throw new Error("later startup failed"); }, 600);',
            "marker-spoof": 'document.documentElement.setAttribute("data-nhimc-standalone-ready", "true");',
            "dynamic-spoof": """
const marker = ['data', 'nhimc', 'standalone', 'ready'].join('-');
const token = document.querySelector('meta[name="nhimc-runtime-token"]').content;
document.documentElement.setAttribute(marker, token);
throw new Error('spoofed startup failure');
""",
        }
        with tempfile.TemporaryDirectory(prefix="NHIMC broken artifact ") as folder:
            root = Path(folder)
            for name, code in cases.items():
                with self.subTest(name=name):
                    source = root / f"{name}-source.html"
                    output = root / f"{name}.html"
                    source.write_text(
                        self._document(
                            f'<script type="module" data-nhimc-business>{code}</script>'
                        ),
                        encoding="utf-8",
                    )
                    build = self._run_builder(source, output)
                    if name == "marker-spoof":
                        self.assertNotEqual(0, build.returncode)
                        self.assertFalse(output.exists())
                        continue
                    self.assertEqual(0, build.returncode, build.stderr)
                    browser = subprocess.run(
                        [
                            sys.executable,
                            "scripts/run_browser_tests.py",
                            "--standalone-file",
                            str(output),
                        ],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        check=False,
                    )
                    self.assertNotEqual(0, browser.returncode, name)
                    self.assertIn("standalone file: FAIL", browser.stdout)

    def test_actual_artifact_browser_check_rejects_sidecar_navigation(self):
        with tempfile.TemporaryDirectory(prefix="NHIMC sidecar navigation ") as folder:
            root = Path(folder)
            source = root / "source.html"
            output = root / "index.html"
            source.write_text(
                self._document(
                    """<script type="module" data-nhimc-business>
setTimeout(() => { location.href = 'sidecar.html'; }, 0);
</script>"""
                ),
                encoding="utf-8",
            )
            build = self._run_builder(source, output)
            self.assertEqual(0, build.returncode, build.stderr)
            (root / "sidecar.html").write_text(
                "<!doctype html><html><body>sidecar</body></html>", encoding="utf-8"
            )

            browser = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_browser_tests.py",
                    "--standalone-file",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            self.assertNotEqual(0, browser.returncode)
            self.assertIn("standalone file: FAIL", browser.stdout)

    def test_builder_refuses_unregistered_remote_runtime_resource(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.html"
            output = Path(folder) / "index.html"
            source.write_text(
                '<!doctype html><link rel="stylesheet" href="https://example.com/rogue.css">',
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_single_html.py",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_generated_html_runs_from_file_url_without_network(self):
        result = subprocess.run(
            [sys.executable, "scripts/run_browser_tests.py", "--standalone-only"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("standalone file: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
