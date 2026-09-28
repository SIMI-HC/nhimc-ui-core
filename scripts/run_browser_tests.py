import argparse
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_single_html import _validate_standalone, build_single_html


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
        build_single_html(root, root / "examples/operations/index.html", output)
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
    args = parser.parse_args()
    if (args.width is None) != (args.height is None):
        parser.error("--width and --height must be supplied together")
    if args.standalone_only and args.standalone_file:
        parser.error("--standalone-only and --standalone-file are mutually exclusive")
    browser = find_browser()
    if args.standalone_file:
        return _run_standalone_artifact(browser, args.standalone_file)
    if args.standalone_only:
        return _run_standalone_browser_test(browser, ROOT)
    viewports = DEFAULT_VIEWPORTS if args.width is None else ((args.width, args.height),)
    return run_browser_tests(viewports=viewports)


if __name__ == "__main__":
    raise SystemExit(main())
