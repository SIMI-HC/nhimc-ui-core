import argparse
from contextlib import contextmanager, redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_single_html import (
    _inventory,
    _validate_standalone,
    build_single_html,
    inspect_completion_manifest,
)
from scripts.canonical_frame import FramePayload, MenuItem, render_canonical_frame
from scripts.frame_patches import apply_frame_patches


ROOT = Path(__file__).resolve().parents[1]
BROWSER_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]
BROWSER_NAMES = (
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "microsoft-edge",
)
DEFAULT_VIEWPORTS = ((1440, 900), (1024, 768), (390, 844))
CANONICAL_FRAMES = (
    "left", "left-blank", "top", "top-left", "presentation",
    "presentation-vertical", "blog",
)


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
    override = os.environ.get("NHIMC_BROWSER_PATH")
    if override:
        candidate = Path(override).expanduser().resolve()
        if candidate.is_file():
            return candidate
        raise RuntimeError(
            f"NHIMC_BROWSER_PATH is not a browser file: {candidate}; "
            f"searched candidates: {', '.join(BROWSER_NAMES)}"
        )
    for path in BROWSER_PATHS:
        candidate = path.resolve()
        if candidate.is_file():
            return candidate
    for name in BROWSER_NAMES:
        if found := shutil.which(name):
            candidate = Path(found).resolve()
            if candidate.is_file():
                return candidate
    paths = ", ".join(str(path) for path in BROWSER_PATHS)
    raise RuntimeError(
        "browser not found; set NHIMC_BROWSER_PATH or install one of "
        f"{', '.join(BROWSER_NAMES)}; searched candidates: {paths}"
    )


def _run_browser_test(browser: Path, root: Path, width: int, height: int) -> int:
    return _run_canonical_components(browser, root, width, height)


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
        source = apply_frame_patches((root / "vendor/nhimc-design/layouts/left.html").read_text(encoding="utf-8"))
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


def run_parity_matrix(root: Path = ROOT, viewports=DEFAULT_VIEWPORTS) -> dict:
    root = root.resolve()
    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix="NHIMC all frame parity ") as folder:
        test_root = Path(folder)
        for frame in CANONICAL_FRAMES:
            source = root / "vendor/nhimc-design/layouts" / f"{frame}.html"
            (test_root / f"{frame}-source.html").write_text(
                apply_frame_patches(source.read_text(encoding="utf-8")), encoding="utf-8", newline="\n"
            )
            adapted = render_canonical_frame(root, frame, _canonical_payload())
            (test_root / f"{frame}-adapted.html").write_text(
                adapted, encoding="utf-8", newline="\n"
            )
        with local_server(test_root) as port:
            cells = [
                {
                    "frame": frame,
                    "width": width,
                    "height": height,
                    "theme": theme,
                    "sourceUrl": f"http://127.0.0.1:{port}/{frame}-source.html",
                    "adaptedUrl": f"http://127.0.0.1:{port}/{frame}-adapted.html",
                }
                for frame in CANONICAL_FRAMES
                for width, height in viewports
                for theme in ("light", "dark")
            ]
            config = test_root / "parity-config.json"
            config.write_text(json.dumps({"cells": cells}), encoding="utf-8")
            completed = subprocess.run(
                [
                    "node", str(root / "scripts/verify_canonical_parity.mjs"),
                    str(browser), str(config),
                ],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=240,
                check=False,
            )
    if completed.returncode:
        raise RuntimeError(completed.stderr or completed.stdout or "canonical parity runner failed")
    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as error:
        raise RuntimeError(f"canonical parity result is invalid: {completed.stdout[-2000:]}") from error
    results = payload.get("results", [])
    expected = len(CANONICAL_FRAMES) * len(viewports) * 2
    complete = len(results) == expected
    return {
        "frames": list(CANONICAL_FRAMES),
        "viewports": [f"{width}x{height}" for width, height in viewports],
        "results": results,
        "all_passed": complete and all(
            item.get("state") and item.get("pixels") and item.get("behavior")
            for item in results
        ),
    }


def _run_all_frame_parity(root: Path = ROOT, viewports=DEFAULT_VIEWPORTS) -> int:
    try:
        result = run_parity_matrix(root, viewports)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"canonical parity matrix: FAIL ({error})")
        return 1
    print(
        f"canonical parity matrix: {len(result['frames'])} frames x "
        f"{len(result['viewports'])} viewports x 2 themes"
    )
    if result["all_passed"]:
        print("canonical parity matrix: PASS")
        return 0
    print("canonical parity matrix: FAIL")
    for item in result["results"]:
        if not (item.get("state") and item.get("pixels") and item.get("behavior")):
            print(
                f"- {item.get('frame')} {item.get('viewport')} {item.get('theme')}: "
                f"state={item.get('state')} pixels={item.get('pixels')} "
                f"behavior={item.get('behavior')} {item.get('error', '')}"
            )
    return 1


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


FRAME_CONTROL_IDS = ("sidebarToggle", "mobileMenuOpen", "slidePrev", "slideNext", "themeToggle")


def _frame_expectations(root: Path, frame_id: str) -> dict:
    """What the exact verifier must find in an artifact of this Frame, read from the Frame layout itself."""
    from scripts.canonical_frame import FRAME_FILES
    from scripts.frame_patches import apply_frame_patches

    layout = apply_frame_patches(
        (root / "vendor/nhimc-design/layouts" / FRAME_FILES[frame_id]).read_text(encoding="utf-8")
    )
    return {
        "statusbar": 'data-nhimc-role="statusbar"' in layout,
        "controls": [name for name in FRAME_CONTROL_IDS if f'id="{name}"' in layout],
    }


def _expected_primary_rgb(root: Path, html: str) -> list[int] | None:
    """--color-primary the artifact must compute, from its own data-theme / data-theme-color and the theme catalog."""
    tag = re.search(r"<html[^>]*>", html, re.I)
    attrs = tag.group(0) if tag else ""
    mode = "dark" if re.search(r"data-theme=[\"']dark[\"']", attrs, re.I) else "light"
    color = re.search(r"data-theme-color=[\"']([a-z0-9-]+)[\"']", attrs, re.I)
    theme_id = color.group(1) if color else "nhimc-default"
    catalog = json.loads((root / "vendor/nhimc-design/tokens/themes/catalog.yaml").read_text(encoding="utf-8"))
    theme = next((item for item in catalog["themes"] if item["id"] == theme_id), None)
    value = (theme or {}).get("tokens", {}).get(mode, {}).get("primary", "").lstrip("#")
    return [int(value[index:index + 2], 16) for index in (0, 2, 4)] if len(value) == 6 else None


def _run_standalone_artifact(
    browser: Path, output: Path, receipt: Path | None = None, root: Path = ROOT
) -> int:
    output = output.resolve()
    if receipt is not None:
        receipt = receipt.resolve()
        receipt.unlink(missing_ok=True)
    try:
        html = output.read_text(encoding="utf-8")
        _validate_standalone(html)
    except (OSError, ValueError) as error:
        print(f"standalone file: FAIL ({error})")
        return 1
    if 'name="nhimc-core-version"' not in html:
        print("standalone file: FAIL (artifact is not finalized)")
        return 1
    try:
        expected = _frame_expectations(root, inspect_completion_manifest(html)["frameId"])
    except (ValueError, KeyError, OSError) as error:
        print(f"standalone file: FAIL ({error})")
        return 1
    expected["primaryRgb"] = _expected_primary_rgb(root, html)
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
        "SVG frame controls": all(f'id="{name}"' in html for name in expected["controls"]),
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
            str(root / "scripts/verify_standalone_browser.mjs"),
            str(browser),
            output.as_uri(),
            token_match.group(1),
            json.dumps(expected),
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
        if receipt is not None:
            try:
                report = json.loads(result.stdout.strip().splitlines()[-1])
                payload = output.read_bytes()
                proof = {
                    "schemaVersion": 1,
                    "artifactSha256": hashlib.sha256(payload).hexdigest(),
                    "artifactBytes": len(payload),
                    "runtimeToken": report["runtimeToken"],
                    "browserProduct": report["browserProduct"],
                    "browserVersion": report["browserVersion"],
                    "verifiedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                }
                receipt.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", newline="\n", delete=False,
                    dir=receipt.parent, prefix=f".{receipt.name}.", suffix=".tmp",
                ) as temporary:
                    json.dump(proof, temporary, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                    temporary.write("\n")
                    temporary_name = temporary.name
                os.replace(temporary_name, receipt)
            except (KeyError, IndexError, json.JSONDecodeError, OSError) as error:
                if receipt is not None:
                    receipt.unlink(missing_ok=True)
                print(f"standalone file: FAIL (receipt could not be written: {error})")
                return 1
        print("standalone file: PASS")
        return 0
    print("standalone file: FAIL")
    print(result.stdout[-5000:])
    if result.stderr:
        print(result.stderr[-2000:])
    try:
        overflow = json.loads(result.stdout.strip().splitlines()[-1])["state"].get("presentationOverflow") or []
    except (IndexError, KeyError, json.JSONDecodeError):
        overflow = []
    if overflow:
        print(
            "presentation Content exceeds the Safe Area on page(s): "
            + ", ".join(overflow)
            + " - shorten the Content or split it into more pages"
        )
    return 1


def run_exact_browser_verification(root: Path, artifact: Path, receipt: Path) -> None:
    browser = find_browser()
    output = io.StringIO()
    with redirect_stdout(output):
        result = _run_standalone_artifact(
            browser, artifact, receipt, root.resolve()
        )
    if result:
        detail = output.getvalue().strip().splitlines()
        suffix = f": {detail[-1]}" if detail else ""
        raise ValueError(f"exact browser verification failed{suffix}")


CONTENT_FIXTURES = ("transport-management", "operations", "administration", "multi-page", "ai-transfer", "top-mint")


def run_content_layout(
    root: Path = ROOT,
    viewports: tuple[tuple[int, int], ...] = DEFAULT_VIEWPORTS,
) -> dict:
    root = root.resolve()
    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix="nhimc-content-layout-") as folder:
        workspace = Path(folder)
        artifacts: dict[tuple[str, str], Path] = {}
        for name in CONTENT_FIXTURES:
            source_html = (root / "tests/fixtures/authoring" / name / "index.html").read_text(encoding="utf-8")
            for theme in ("light", "dark"):
                source = workspace / name / theme / "source.html"
                artifact = workspace / name / theme / "index.html"
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text(
                    source_html.replace('data-theme="light"', f'data-theme="{theme}"', 1),
                    encoding="utf-8", newline="\n",
                )
                build_single_html(root, source, artifact)
                artifacts[(name, theme)] = artifact
        cells = [
            {
                "name": name, "theme": theme, "width": width, "height": height,
                "artifactUrl": artifacts[(name, theme)].resolve().as_uri(),
            }
            for width, height in viewports
            for name in CONTENT_FIXTURES
            for theme in ("light", "dark")
        ]
        matrix = workspace / "matrix.json"
        matrix.write_text(
            json.dumps({"cells": cells}, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8", newline="\n",
        )
        completed = subprocess.run(
            ["node", str(root / "scripts/verify_content_layout.mjs"), str(browser), str(matrix)],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=max(120, len(cells) * 8), check=False,
        )
        try:
            report = json.loads(completed.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError) as error:
            raise RuntimeError(
                f"content layout verification produced no JSON report: {completed.stderr[-2000:]}"
            ) from error
        return report


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
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--canonical-parity-only", action="store_true")
    parser.add_argument("--canonical-components-only", action="store_true")
    parser.add_argument("--content-layout-only", action="store_true")
    parser.add_argument("--presentation-safe-area-only", action="store_true")
    parser.add_argument("--blog-scroll-owner-only", action="store_true")
    parser.add_argument("--frame-render-only", action="store_true")
    parser.add_argument("--all-frames", action="store_true")
    args = parser.parse_args()
    if (args.width is None) != (args.height is None):
        parser.error("--width and --height must be supplied together")
    modes = sum(bool(item) for item in (
        args.standalone_only, args.standalone_file, args.canonical_parity_only,
        args.canonical_components_only,
        args.content_layout_only,
        args.presentation_safe_area_only,
        args.blog_scroll_owner_only,
        args.frame_render_only,
    ))
    if modes > 1:
        parser.error("standalone and canonical parity modes are mutually exclusive")
    if args.all_frames and not args.canonical_parity_only:
        parser.error("--all-frames requires --canonical-parity-only")
    if args.receipt and not args.standalone_file:
        parser.error("--receipt requires --standalone-file")
    browser = find_browser()
    if args.standalone_file:
        return _run_standalone_artifact(browser, args.standalone_file, args.receipt)
    if args.standalone_only:
        return _run_standalone_browser_test(browser, ROOT)
    viewports = DEFAULT_VIEWPORTS if args.width is None else ((args.width, args.height),)
    if args.canonical_parity_only:
        if args.all_frames:
            return _run_all_frame_parity(viewports=viewports)
        return run_canonical_parity(viewports=viewports)
    if args.canonical_components_only:
        return run_canonical_components(viewports=viewports)
    if args.presentation_safe_area_only:
        from scripts.presentation_safe_area import run_presentation_safe_area

        report = run_presentation_safe_area(ROOT)
        for item in report["problems"]:
            print(f"  {item}")
        print(f"presentation safe area: {report['cells']} cells {'PASS' if report['all_passed'] else 'FAIL'}")
        return 0 if report["all_passed"] else 1
    if args.frame_render_only:
        from scripts.frame_render import run_frame_render

        report = run_frame_render(ROOT)
        for item in report["problems"]:
            print(f"  {item}")
        print(f"frame render: {report['cells']} cells {'PASS' if report['all_passed'] else 'FAIL'}")
        return 0 if report["all_passed"] else 1
    if args.blog_scroll_owner_only:
        from scripts.blog_scroll_owner import run_blog_scroll_owner

        report = run_blog_scroll_owner(ROOT)
        for item in report["problems"]:
            print(f"  {item}")
        print(f"blog scroll owner: {report['cells']} cells {'PASS' if report['all_passed'] else 'FAIL'}")
        return 0 if report["all_passed"] else 1
    if args.content_layout_only:
        report = run_content_layout(ROOT, viewports=viewports)
        for cell in report["results"]:
            for problem in cell["problems"]:
                print(f"  {cell['name']} {cell['theme']} {cell['viewport']}: {problem}")
        print(
            f"content layout: {len(report['results'])} cells "
            f"{'PASS' if report['all_passed'] else 'FAIL'}"
        )
        return 0 if report["all_passed"] else 1
    return run_browser_tests(viewports=viewports)


if __name__ == "__main__":
    raise SystemExit(main())
