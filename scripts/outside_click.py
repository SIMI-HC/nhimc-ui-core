"""Browser regression: clicking outside the help sheet or the mobile menu closes it, on every Frame with those controls.

Real mouse clicks (Input.dispatchMouseEvent) on the offline artifact of left, left-blank, top, top-left and blog at
1440px (help) and 390px (help + mobile menu): clicking inside the sheet keeps it open, clicking outside closes it, and
the in-page drawer (.nav-backdrop) resets nav-open / aria-expanded.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_single_html import build_single_html
from scripts.frame_render import fragment
from scripts.run_browser_tests import find_browser

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ("left", "left-blank", "top", "top-left", "blog")
VIEWPORTS = ((1440, 900), (390, 844))


def build_cells(root: Path, workspace: Path, frames=FRAMES, viewports=VIEWPORTS) -> list[dict]:
    cells: list[dict] = []
    for frame in frames:
        folder = workspace / frame
        folder.mkdir(parents=True, exist_ok=True)
        source = folder / "source.html"
        source.write_text(fragment(frame, "light", "nhimc-default"), encoding="utf-8", newline="\n")
        page = build_single_html(root, source, folder / "index.html")
        for width, height in viewports:
            cells.append({"id": f"{frame}|{width}", "frame": frame, "width": width, "height": height, "url": page.resolve().as_uri()})
    return cells


def measure(root: Path, cells: list[dict]) -> list[dict]:
    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix="nhimc-outside-click-matrix-") as folder:
        matrix = Path(folder) / "matrix.json"
        matrix.write_text(json.dumps({"cells": cells}, ensure_ascii=False), encoding="utf-8")
        completed = subprocess.run(
            ["node", str(root / "scripts/verify_outside_click.mjs"), str(browser), str(matrix)],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=max(240, len(cells) * 20), check=False,
        )
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])["results"]
    except (IndexError, json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(f"outside click measurement produced no report: {completed.stderr[-2000:]}") from error


def problems(results: list[dict]) -> list[str]:
    found: list[str] = []
    for result in results:
        if result.get("error"):
            found.append(f"{result['id']}: {result['error']}")
        found.extend(f"{result['id']}: {item}" for item in result.get("problems", []))
    return found


def run_outside_click(root: Path = ROOT, **options) -> dict:
    root = root.resolve()
    with tempfile.TemporaryDirectory(prefix="nhimc-outside-click-") as folder:
        cells = build_cells(root, Path(folder), **options)
        results = measure(root, cells)
    found = problems(results)
    return {"cells": len(cells), "problems": found, "all_passed": not found}


if __name__ == "__main__":
    report = run_outside_click()
    for item in report["problems"]:
        print(f"  {item}")
    print(f"outside click: {report['cells']} cells {'PASS' if report['all_passed'] else 'FAIL'}")
    raise SystemExit(0 if report["all_passed"] else 1)
