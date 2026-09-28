import argparse
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_single_html import _inventory, _validate_standalone, build_single_html
from scripts.canonical_frame import FramePayload, MenuItem, render_canonical_frame


ROOT = Path(__file__).resolve().parents[1]
BROWSER_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]
DEFAULT_VIEWPORTS = ((1440, 900), (1024, 768), (390, 844))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


@contextmanager
def local_server(root: Path):
    handler = lambda *args, **kwargs: QuietHandler(  # noqa: E731
        *args, directory=str(root), **kwargs
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def find_browser() -> Path:
    for path in BROWSER_PATHS:
        if path.is_file():
            return path
    raise FileNotFoundError("Chrome or Edge was not found in a standard location")


def _run_browser_test(browser: Path, root: Path, width: int, height: int) -> int:
    with local_server(root) as port:
        url = f"http://127.0.0.1:{port}/tests/browser/runner.html"
        result = subprocess.run(
            [
                str(browser),
                "--headless",
                "--disable-gpu",
                "--disable-extensions",
                "--no-first-run",
                "--force-prefers-reduced-motion=reduce",
                "--virtual-time-budget=4000",
                f"--window-size={width},{height}",
                "--dump-dom",
                url,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    print(f"browser: {browser.name} {width}x{height}")
    if 'name="nhimc-test-result" content="PASS"' in result.stdout:
        print("browser: PASS")
        return 0
    print("browser: FAIL")
    print(result.stdout[-4000:])
    if result.stderr:
        print(result.stderr[-2000:])
    return 1


def _canonical_payload() -> FramePayload:
    menu = (
        MenuItem("clinical-criteria", "진료과 기준", "hospital", "#clinical-criteria"),
        MenuItem("lab-values", "검사 수치", "flask", "#lab-values"),
        MenuItem("stopped-medications", "중단 약물", "ban", "#stopped-medications"),
        MenuItem("notices", "시행·검진 공지", "megaphone", "#notices"),
    )
    panels = "".join(
        f'<section data-screen-panel="{item.id}"{"" if index == 0 else " hidden"}><h1>{item.label}</h1></section>'
        for index, item in enumerate(menu)
    )
    return FramePayload(
        project_title="프로젝트명",
        menu=menu,
        active_id=menu[0].id,
        content_html=panels,
    )


def _run_canonical_parity(browser: Path, root: Path, width: int, height: int) -> int:
    with tempfile.TemporaryDirectory(prefix="NHIMC canonical parity ") as folder:
        test_root = Path(folder)
        probe = (root / "tests/browser/canonical-parity.js").read_text(encoding="utf-8")
        source = (root / "vendor/nhimc-design/layouts/left.html").read_text(encoding="utf-8")
        adapted = render_canonical_frame(root, "left", _canonical_payload())
        (test_root / "canonical-source.html").write_text(
            source.replace("</body>", f"<script>{probe}</script></body>", 1), encoding="utf-8"
        )
        (test_root / "canonical-adapted.html").write_text(
            adapted.replace("</body>", f"<script>{probe}</script></body>", 1), encoding="utf-8"
        )

        def dump(port: int, filename: str, theme: str, adapted_flag: bool) -> tuple[dict | None, subprocess.CompletedProcess]:
            result = subprocess.run(
                [
                    str(browser), "--headless", "--disable-gpu", "--disable-extensions",
                    "--no-first-run", "--force-prefers-reduced-motion=reduce",
                    "--virtual-time-budget=3000", f"--window-size={width},{height}",
                    "--dump-dom",
                    f"http://127.0.0.1:{port}/{filename}?theme={theme}&adapted={int(adapted_flag)}",
                ],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=30, check=False,
            )
            match = re.search(
                r'<script id="nhimc-parity-data" type="application/json">(.*?)</script>',
                result.stdout,
                re.DOTALL,
            )
            return (json.loads(match.group(1)) if match else None, result)

        with local_server(test_root) as port:
            runs = []
            for theme in ("light", "dark"):
                source_data, source_result = dump(port, "canonical-source.html", theme, False)
                adapted_data, adapted_result = dump(port, "canonical-adapted.html", theme, True)
                runs.append((theme, source_data, adapted_data, source_result, adapted_result))
    print(f"canonical parity: {browser.name} {width}x{height}")
    failures = []
    for theme, source_data, adapted_data, source_result, adapted_result in runs:
        if source_data is None or adapted_data is None:
            failures.append(f"{theme}: snapshot marker missing")
        elif source_data["snapshot"] != adapted_data["snapshot"]:
            failures.append(f"{theme}: protected frame snapshot differs")
        elif not adapted_data["behavior"]:
            failures.append(f"{theme}: {adapted_data['error']}")
    if not failures:
        print("canonical parity: PASS")
        return 0
    print("canonical parity: FAIL")
    for failure in failures:
        print(f"- {failure}")
    last = runs[-1]
    if last[4].stderr:
        print(last[4].stderr[-2000:])
    return 1


def run_canonical_parity(root: Path = ROOT, viewports=DEFAULT_VIEWPORTS) -> int:
    browser = find_browser()
    for width, height in viewports:
        result = _run_canonical_parity(browser, root, width, height)
        if result:
            return result
    return 0


def _run_canonical_components(browser: Path, root: Path, width: int, height: int) -> int:
    with local_server(root) as port:
        result = subprocess.run(
            [
                str(browser), "--headless", "--disable-gpu", "--disable-extensions",
                "--no-first-run", "--force-prefers-reduced-motion=reduce",
                "--virtual-time-budget=5000", f"--window-size={width},{height}",
                "--dump-dom", f"http://127.0.0.1:{port}/tests/browser/canonical-components.html",
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30, check=False,
        )
    print(f"canonical components: {browser.name} {width}x{height}")
    if 'name="nhimc-canonical-components-result" content="PASS"' in result.stdout:
        print("canonical components: PASS (49)")
        return 0
    print("canonical components: FAIL")
    failure_match = re.search(r'data-failures="([^"]*)"', result.stdout)
    if failure_match:
        print(f"component failures: {failure_match.group(1)}")
    print(result.stdout[-5000:])
    if result.stderr:
        print(result.stderr[-2000:])
    return 1


def run_canonical_components(root: Path = ROOT, viewports=DEFAULT_VIEWPORTS) -> int:
    browser = find_browser()
    for width, height in viewports:
        result = _run_canonical_components(browser, root, width, height)
        if result:
            return result
    return 0


def _run_standalone_artifact(browser: Path, output: Path) -> int:
    output = output.resolve()
    try:
        html = output.read_text(encoding="utf-8")
        _validate_standalone(html)
    except (OSError, ValueError) as error:
        print(f"standalone file: FAIL ({error})")
        return 1
    if 'name="nhimc-core-version"' not in html:
        print("standalone file: FAIL (artifact is not finalized)")
        return 1
    tags = _inventory(html).tags
    role_count = lambda role: sum(attrs.get("data-nhimc-role") == role for _, attrs in tags)
    static_contract = {
        "canonical app shell": role_count("app-shell") == 1,
        "canonical content slot": role_count("content-slot") == 1,
        "upstream provenance": bool(re.search(
            r'<meta\s+name="nhimc-upstream-commit"\s+content="[0-9a-f]{12}">', html
        )),
        "six embedded font faces": html.count("@font-face") == 6,
        "canonical component bundle": 'data-nhimc-component-bundle="canonical"' in html,
        "SVG frame controls": 'id="sidebarToggle"' in html and 'id="mobileMenuOpen"' in html,
        "no Unicode control substitutes": "☰" not in html and "‹" not in html,
    }
    failures = [label for label, passed in static_contract.items() if not passed]
    if failures:
        print(f"standalone file: FAIL ({', '.join(failures)})")
        return 1
    token_match = re.search(
        r'<meta\s+name="nhimc-runtime-token"\s+content="([0-9a-f]{64})">', html
    )
    if not token_match:
        print("standalone file: FAIL (runtime integrity token is missing)")
        return 1
    result = subprocess.run(
        [
            "node",
            str(ROOT / "scripts/verify_standalone_browser.mjs"),
            str(browser),
            output.as_uri(),
            token_match.group(1),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    print(f"standalone artifact: {output}")
    print(f"standalone file: {browser.name} file:// offline")
    if result.returncode == 0:
        print("standalone file: PASS")
        return 0
    print("standalone file: FAIL")
    print(result.stdout[-5000:])
    if result.stderr:
        print(result.stderr[-2000:])
    return 1


def _run_standalone_browser_test(browser: Path, root: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="NHIMC offline ") as folder:
        output = Path(folder) / "download result" / "nhimc-worktool.html"
        build_single_html(
            root, root / "tests/fixtures/authoring/operations/index.html", output
        )
        return _run_standalone_artifact(browser, output)


def run_browser_tests(
    root: Path = ROOT,
    viewports: tuple[tuple[int, int], ...] = DEFAULT_VIEWPORTS,
    include_standalone: bool = True,
) -> int:
    browser = find_browser()
    for width, height in viewports:
        result = _run_browser_test(browser, root, width, height)
        if result:
            return result
    if include_standalone:
        return _run_standalone_browser_test(browser, root)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run NHIMC browser tests")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--standalone-only", action="store_true")
    parser.add_argument("--standalone-file", type=Path)
    parser.add_argument("--canonical-parity-only", action="store_true")
    parser.add_argument("--canonical-components-only", action="store_true")
    args = parser.parse_args()
    if (args.width is None) != (args.height is None):
        parser.error("--width and --height must be supplied together")
    modes = sum(bool(item) for item in (
        args.standalone_only, args.standalone_file, args.canonical_parity_only,
        args.canonical_components_only,
    ))
    if modes > 1:
        parser.error("standalone and canonical parity modes are mutually exclusive")
    browser = find_browser()
    if args.standalone_file:
        return _run_standalone_artifact(browser, args.standalone_file)
    if args.standalone_only:
        return _run_standalone_browser_test(browser, ROOT)
    viewports = DEFAULT_VIEWPORTS if args.width is None else ((args.width, args.height),)
    if args.canonical_parity_only:
        return run_canonical_parity(viewports=viewports)
    if args.canonical_components_only:
        return run_canonical_components(viewports=viewports)
    return run_browser_tests(viewports=viewports)


if __name__ == "__main__":
    raise SystemExit(main())
