import re
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
        content = (
            '<main data-nhimc-role="content">'
            '<section class="nhimc-page-header" data-nhimc-component="PageHeader">'
            "<div><h1>이송 현황</h1></div></section></main>"
        )
        return (
            "<!doctype html><html><head></head><body>"
            '<nhimc-frame id="app-frame" data-frame="left" '
            'data-project-title="일산병원 업무도구" data-active-id="ambulance">'
            f"{content}{fragment}</nhimc-frame>"
            '<script type="application/json" data-nhimc-menu>'
            '[{"id":"ambulance","label":"이송 현황","icon":"ambulance","href":"#ambulance"}]'
            "</script>"
            "</body></html>"
        )

    def test_v4_artifact_contains_layout_bundle_and_completion_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            build_single_html(
                ROOT, ROOT / "tests/fixtures/authoring/operations/index.html", output
            )
            html = output.read_text(encoding="utf-8")
            manifest = inspect_completion_manifest(html)

            self.assertNotIn("data-nhimc-template", html)
            self.assertIn('data-nhimc-layout-bundle="primitives"', html)
            self.assertEqual("nhimc-single-html", manifest["artifactType"])
            self.assertEqual(4, manifest["schemaVersion"])
            self.assertEqual(
                [{"screenId": "ambulance"}],
                manifest["screens"],
            )
            self.assertEqual(0, manifest["sidecarCount"])
            self.assertIs(True, manifest["verificationRequired"])

    def test_rejects_bare_legacy_business_layout(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            with self.assertRaisesRegex(
                ValueError, "content root"
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

    def test_multiple_panels_bind_navigation_in_order(self):
        source = (
            ROOT / "tests/fixtures/unsafe-authoring/mixed-screen-panels.html"
        ).read_text(encoding="utf-8")
        screens = parse_authoring_screens(source)
        self.assertEqual(
            ["ambulance", "roles"], [screen.screen_id for screen in screens]
        )
        broken = source.replace('data-screen-panel="roles"', 'data-screen-panel="other"')
        with self.assertRaisesRegex(ValueError, "navigation.*panel.*1:1"):
            parse_authoring_screens(broken)

    def test_content_only_fragment_is_wrapped_by_the_builder(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            build_single_html(ROOT, ROOT / "tests/fixtures/authoring/fragment/index.html", output)
            html = output.read_text(encoding="utf-8")
            manifest = inspect_completion_manifest(html)
            self.assertEqual([{"screenId": "main"}], manifest["screens"])
            self.assertIn("재고 현황", html)
            self.assertIn("Noto Sans KR", html)
            self.assertIn('data-nhimc-role="app-shell"', html)

    def test_multi_page_menu_builds_one_panel_per_menu_item(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            build_single_html(ROOT, ROOT / "tests/fixtures/authoring/multi-page/index.html", output)
            html = output.read_text(encoding="utf-8")
            manifest = inspect_completion_manifest(html)
            self.assertEqual(
                [{"screenId": "dashboard"}, {"screenId": "items"}, {"screenId": "orders"}],
                manifest["screens"],
            )
            for menu_id in ("dashboard", "items", "orders"):
                self.assertIn(f'data-screen-panel="{menu_id}"', html)
                self.assertIn(f'data-menu-id="{menu_id}"', html)

    def test_menu_id_matching_an_icon_name_does_not_collide_with_its_symbol(self):
        # tests/fixtures/authoring/multi-page/index.html uses menu id "dashboard" with icon "dashboard":
        # the icon symbol's id and the panel's rendered id used to collide, so <use href="#dashboard">
        # resolved to the <section>, not the <symbol>, and the icon silently failed to render.
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            build_single_html(ROOT, ROOT / "tests/fixtures/authoring/multi-page/index.html", output)
            html = output.read_text(encoding="utf-8")
            occurrences = re.findall(r'<(\w+)\b[^>]*\sid="dashboard"', html)
            self.assertEqual(["symbol"], occurrences)

    def test_no_duplicate_ids_anywhere_in_the_built_artifact(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            build_single_html(ROOT, ROOT / "tests/fixtures/authoring/multi-page/index.html", output)
            html = output.read_text(encoding="utf-8")
            ids = re.findall(r'<\w+\b[^>]*\sid="([^"]+)"', html)
            duplicates = {value for value in ids if ids.count(value) > 1}
            self.assertEqual(set(), duplicates)

    def test_fragment_title_comes_from_the_page_heading_and_keeps_html_hints(self):
        from scripts.build_single_html import normalize_authoring

        wrapped = normalize_authoring(
            '<html data-frame="top" data-theme="dark" data-theme-color="mint"><body>'
            '<main data-nhimc-role="content"><h1>재고 현황</h1></main></body></html>'
        )
        self.assertIn("<title>재고 현황</title>", wrapped)
        self.assertIn('data-frame="top"', wrapped)
        self.assertIn('data-theme="dark"', wrapped)
        self.assertIn('data-theme-color="mint"', wrapped)

    def test_theme_color_is_applied_and_unknown_theme_color_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "index.html"
            build_single_html(ROOT, ROOT / "tests/fixtures/authoring/top-mint/index.html", output)
            html = output.read_text(encoding="utf-8")
            self.assertIn('data-theme-color="mint"', html[:200])
            self.assertIn('[data-theme-color="mint"]{--color-primary:#417F84', html)
            source = Path(folder) / "bad.html"
            source.write_text(
                (ROOT / "tests/fixtures/authoring/top-mint/index.html")
                .read_text(encoding="utf-8")
                .replace('data-theme-color="mint"', 'data-theme-color="neon"'),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unknown theme color: neon"):
                build_single_html(ROOT, source, Path(folder) / "bad-out.html")

    def test_rejects_templates_and_unknown_components(self):
        valid = self._document("")
        with self.assertRaisesRegex(ValueError, "Templates are not supported"):
            parse_authoring_screens(valid.replace('<nhimc-frame ', '<nhimc-frame data-template="list-default" ', 1).replace('<main data-nhimc-role="content">', '<main data-nhimc-role="content" data-nhimc-template-root="list-default">'))
        with self.assertRaisesRegex(ValueError, "unknown component InventedWidget"):
            parse_authoring_screens(valid.replace('data-nhimc-component="PageHeader"', 'data-nhimc-component="InventedWidget"'))

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
