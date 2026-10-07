import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from scripts.build_single_html import build_single_html
from scripts.build_web_runtime import build_web_runtime
from scripts.run_browser_tests import find_browser
from scripts.test_profiles import slow_test

ROOT = Path(__file__).resolve().parents[2]
WEB_FIXTURE = ROOT / "tests/fixtures/web/index.html"


def _dump(browser: Path, url: str) -> str:
    with tempfile.TemporaryDirectory() as profile:
        result = subprocess.run(
            [
                str(browser), "--headless", "--disable-gpu", "--no-first-run",
                f"--user-data-dir={profile}", "--virtual-time-budget=8000",
                "--allow-file-access-from-files", "--dump-dom", url,
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120, check=False,
        )
    return result.stdout


def _frame_markup(dom: str) -> str:
    """Frame structure only: drop scripts, sprite, head, status text and inline runtime state."""
    body = dom[dom.index("<body") :]
    body = re.sub(r"<script\b.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<svg hidden.*?</svg>", "", body, flags=re.S)
    body = re.sub(r"준비됨 · (?:오프라인 문서|웹 실행)", "STATUS", body)
    return re.sub(r"\s+", " ", body)


class WebRuntimeTests(unittest.TestCase):
    def test_committed_runtime_matches_canonical_sources(self):
        committed = (ROOT / "dist/nhimc-web.js").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            for name in ("src", "registry", "vendor", "VERSION"):
                source = ROOT / name
                target = temporary / name
                if source.is_dir():
                    __import__("shutil").copytree(source, target)
                else:
                    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8", newline="")
            generated = build_web_runtime(temporary).read_text(encoding="utf-8")
        self.assertEqual(committed, generated, "run python scripts/build_web_runtime.py")

    @slow_test
    def test_runtime_frame_matches_offline_builder_frame(self):
        browser = find_browser()
        with tempfile.TemporaryDirectory() as folder:
            built = Path(folder) / "index.html"
            build_single_html(ROOT, ROOT / "tests/fixtures/authoring/transport-management/index.html", built)
            offline = _frame_markup(_dump(browser, built.resolve().as_uri()))
        web = _frame_markup(_dump(browser, WEB_FIXTURE.resolve().as_uri()))
        self.assertIn('data-nhimc-role="app-shell"', web)
        self.assertEqual(offline, web)

    @slow_test
    def test_runtime_multi_page_frame_matches_offline_builder_frame(self):
        browser = find_browser()
        with tempfile.TemporaryDirectory() as folder:
            built = Path(folder) / "index.html"
            build_single_html(ROOT, ROOT / "tests/fixtures/authoring/multi-page/index.html", built)
            offline = _frame_markup(_dump(browser, built.resolve().as_uri()))
        web = _frame_markup(_dump(browser, (ROOT / "tests/fixtures/web/multi-page.html").resolve().as_uri()))
        self.assertIn('data-menu-id="orders"', web)
        self.assertEqual(offline, web)

    @slow_test
    def test_runtime_accepts_every_page_inside_one_main_like_the_per_page_form(self):
        # the common AI slip: one outer <main data-nhimc-role="content"> holding all data-screen-panel sections
        browser = find_browser()
        runtime = (ROOT / "dist/nhimc-web.js").resolve().as_uri()
        source = (ROOT / "tests/fixtures/web/multi-page.html").read_text(encoding="utf-8").replace("../../../dist/nhimc-web.js", runtime)
        slip = source.replace('"><main data-nhimc-role="content">', '">').replace("</main></section>", "</section>")
        slip = slip.replace('<section data-screen-panel="dashboard">', '<main data-nhimc-role="content"><section data-screen-panel="dashboard">', 1)
        slip = slip.replace("</section>\n</nhimc-frame>", "</section></main>\n</nhimc-frame>", 1)
        self.assertNotEqual(source, slip)
        with tempfile.TemporaryDirectory() as folder:
            correct, tolerated = Path(folder) / "correct.html", Path(folder) / "slip.html"
            correct.write_text(source, encoding="utf-8")
            tolerated.write_text(slip, encoding="utf-8")
            expected = _frame_markup(_dump(browser, correct.resolve().as_uri()))
            actual_dom = _dump(browser, tolerated.resolve().as_uri())
        self.assertNotIn("화면을 만들지 못했습니다", actual_dom)
        self.assertIn('data-menu-id="orders"', actual_dom)
        self.assertEqual(expected, _frame_markup(actual_dom))

    @slow_test
    def test_runtime_flags_a_class_without_a_style_and_stays_quiet_otherwise(self):
        browser = find_browser()
        runtime = (ROOT / "dist/nhimc-web.js").resolve().as_uri()

        def page(markup: str) -> str:
            return (f'<!doctype html><html lang="ko" data-theme="light"><head><meta charset="utf-8"><script src="{runtime}"></script></head>'
                    f'<body><main data-nhimc-role="content">{markup}</main></body></html>')

        cases = {
            "bad.html": page('<section class="metrics"><article class="card metric"><strong>24</strong></article></section>'),
            "good.html": page('<section class="card nhimc-card"><div class="nhimc-card-head"><strong>제목</strong></div><div class="nhimc-card-body">내용</div></section>'),
        }
        with tempfile.TemporaryDirectory() as folder:
            doms = {}
            for name, html in cases.items():
                target = Path(folder) / name
                target.write_text(html, encoding="utf-8")
                doms[name] = _dump(browser, target.resolve().as_uri())
        self.assertIn("스타일이 없는 클래스를 썼습니다", doms["bad.html"])
        self.assertIn("<code>metrics, metric</code>", doms["bad.html"])
        self.assertIn('data-nhimc-role="app-shell"', doms["bad.html"])
        self.assertNotIn("스타일이 없는 클래스를 썼습니다", doms["good.html"])

    @slow_test
    def test_runtime_failure_tells_the_user_what_to_do(self):
        browser = find_browser()
        runtime = (ROOT / "dist/nhimc-web.js").resolve().as_uri()
        page = f'<!doctype html><html lang="ko" data-theme="light"><head><meta charset="utf-8"><script src="{runtime}"></script></head><body><main>no role</main></body></html>'
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "broken.html"
            target.write_text(page, encoding="utf-8")
            dom = _dump(browser, target.resolve().as_uri())
        self.assertIn("화면을 만들지 못했습니다", dom)
        self.assertIn("NHIMC UI Core: Content must contain main[data-nhimc-role=", dom)
        self.assertIn("규칙에 맞게 다시 만들어줘", dom)

    @slow_test
    def test_runtime_top_frame_and_theme_color_match_offline_builder(self):
        browser = find_browser()
        with tempfile.TemporaryDirectory() as folder:
            built = Path(folder) / "index.html"
            build_single_html(ROOT, ROOT / "tests/fixtures/authoring/top-mint/index.html", built)
            offline_dom = _dump(browser, built.resolve().as_uri())
        web_dom = _dump(browser, (ROOT / "tests/fixtures/web/top-mint.html").resolve().as_uri())
        for dom in (offline_dom, web_dom):
            self.assertIn('data-theme-color="mint"', dom[:400])
            self.assertIn('data-menu-id="wards"', dom)
        self.assertEqual(_frame_markup(offline_dom), _frame_markup(web_dom))
        self.assertNotEqual(_frame_markup(web_dom), "")

    @slow_test
    def test_runtime_page_opened_from_a_korean_file_name_logs_no_console_errors(self):
        browser = find_browser()
        runtime = (ROOT / "dist/nhimc-web.js").resolve().as_uri()
        with tempfile.TemporaryDirectory() as folder:
            for fixture in ("index.html", "multi-page.html", "top-mint.html"):
                source = (ROOT / "tests/fixtures/web" / fixture).read_text(encoding="utf-8")
                page = Path(folder) / f"이송업무-관리-{fixture}"
                page.write_text(source.replace("../../../dist/nhimc-web.js", runtime), encoding="utf-8")
                result = subprocess.run(
                    ["node", str(ROOT / "scripts/probe_console.mjs"), str(browser), page.resolve().as_uri()],
                    capture_output=True, text=True, encoding="utf-8", timeout=120, check=False,
                )
                report = json.loads(result.stdout.strip().splitlines()[-1])
                self.assertTrue(report["shell"], fixture)
                self.assertEqual([], report["messages"], fixture)

    def test_runtime_is_small_and_loads_fonts_by_verified_url(self):
        runtime = (ROOT / "dist/nhimc-web.js").read_text(encoding="utf-8")
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertNotRegex(runtime, r"data:font/woff2;base64,[A-Za-z0-9+/]{100}")
        self.assertLess(len(runtime.encode("utf-8")), 1_500_000)
        base = f"https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@v{version}/vendor/nhimc-design/fonts"
        self.assertIn(base, runtime)
        for weight in (300, 400, 700):
            for subset in ("latin", "korean"):
                name = f"noto-sans-kr-{subset}-{weight}.woff2"
                self.assertIn(f"{base}/{name}", runtime)
                self.assertTrue((ROOT / "vendor/nhimc-design/fonts" / name).is_file(), name)
        # the page stays hidden until the Frame replaces the Content, and is always revealed
        self.assertIn("root.style.visibility = 'hidden'", runtime)
        self.assertGreaterEqual(runtime.count("reveal()"), 3)

    @slow_test
    def test_head_placed_script_renders_the_frame_and_reveals_the_page(self):
        browser = find_browser()
        with tempfile.TemporaryDirectory() as folder:
            page = Path(folder) / "head.html"
            source = (ROOT / "tests/fixtures/web/index.html").read_text(encoding="utf-8")
            page.write_text(source.replace("../../../dist/nhimc-web.js", (ROOT / "dist/nhimc-web.js").resolve().as_uri()), encoding="utf-8")
            self.assertLess(source.index("nhimc-web.js"), source.index("<body>"))
            result = subprocess.run(
                ["node", str(ROOT / "scripts/probe_console.mjs"), str(browser), page.resolve().as_uri()],
                capture_output=True, text=True, encoding="utf-8", timeout=120, check=False,
            )
            report = json.loads(result.stdout.strip().splitlines()[-1])
            self.assertTrue(report["shell"])
            self.assertEqual([], report["messages"])

    @slow_test
    def test_saved_offline_html_is_self_contained_and_opens_without_network(self):
        browser = find_browser()
        runtime = (ROOT / "dist/nhimc-web.js").resolve().as_uri()
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "web.html"
            source.write_text(
                (ROOT / "tests/fixtures/web/multi-page.html").read_text(encoding="utf-8").replace("../../../dist/nhimc-web.js", runtime),
                encoding="utf-8",
            )
            saved = Path(folder) / "저장본.html"
            first = subprocess.run(
                ["node", str(ROOT / "scripts/probe_console.mjs"), str(browser), source.resolve().as_uri(), "--export", str(saved)],
                capture_output=True, text=True, encoding="utf-8", timeout=180, check=False,
            )
            self.assertTrue(json.loads(first.stdout.strip().splitlines()[-1])["shell"])
            html = saved.read_text(encoding="utf-8")
            self.assertNotRegex(html, r"<script\b[^>]*\bsrc=")
            self.assertIn('data-nhimc-role="app-shell"', html)
            self.assertIn('data-screen-panel="orders"', html)
            if "data:font/woff2" in html:
                self.assertNotRegex(html, r"https://[^\"')]+\.woff2")
            second = subprocess.run(
                ["node", str(ROOT / "scripts/probe_console.mjs"), str(browser), saved.resolve().as_uri(), "--offline"],
                capture_output=True, text=True, encoding="utf-8", timeout=120, check=False,
            )
            report = json.loads(second.stdout.strip().splitlines()[-1])
            self.assertTrue(report["shell"])
            self.assertEqual([], report["messages"])

    @slow_test
    def test_runtime_rejects_forbidden_content(self):
        browser = find_browser()
        with tempfile.TemporaryDirectory() as folder:
            page = Path(folder) / "bad.html"
            page.write_text(
                '<!doctype html><html><head><meta charset="utf-8"></head><body>'
                '<main data-nhimc-role="content"><style>body{}</style></main>'
                f'<script src="{(ROOT / "dist/nhimc-web.js").resolve().as_uri()}"></script></body></html>',
                encoding="utf-8",
            )
            dom = _dump(browser, page.resolve().as_uri())
        self.assertIn("NHIMC UI Core:", dom)
        self.assertNotIn('data-nhimc-role="app-shell"', dom)


if __name__ == "__main__":
    unittest.main()
