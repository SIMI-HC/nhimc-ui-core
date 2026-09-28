import argparse
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import threading


ROOT = Path(__file__).resolve().parents[1]
BROWSER_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]


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


def run_browser_tests(root: Path = ROOT, width: int = 390, height: int = 844) -> int:
    browser = find_browser()
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
    print(f"browser: {browser.name}")
    if 'name="nhimc-test-result" content="PASS"' in result.stdout:
        print("browser: PASS")
        return 0
    print("browser: FAIL")
    print(result.stdout[-4000:])
    if result.stderr:
        print(result.stderr[-2000:])
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run NHIMC browser tests")
    parser.add_argument("--width", type=int, default=390)
    parser.add_argument("--height", type=int, default=844)
    args = parser.parse_args()
    return run_browser_tests(width=args.width, height=args.height)


if __name__ == "__main__":
    raise SystemExit(main())
