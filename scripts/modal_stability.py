"""Browser regression: opening a dialog must not move the page behind it.

Every Frame with a scrolling page (long Content, so a vertical scrollbar exists) is built offline and opened in each
installed Chrome / Edge. The help sheet (and the mobile menu where there is one) is opened with the page at the top and
scrolled; the header and the first card must keep exactly the same x, y and width, and the page must keep its scroll
position, while the dialog is open and again after it is closed. BLOG is measured with both scroll owners.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_single_html import build_single_html
from scripts.run_browser_tests import BROWSER_PATHS

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("left", ""), ("left-blank", ""), ("left-dual", ""), ("top", ""), ("top-left", ""),
    ("blog", "main"), ("blog", "document"),
)
CHROME_PATHS = (
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
)
VIEWPORTS = ((1440, 900), (1024, 768), (390, 844))
MENU = (
    '[{"id":"overview","label":"업무 현황","icon":"home","href":"#overview"},'
    '{"id":"requests","label":"요청 목록","icon":"list","href":"#requests"}]'
)


def browsers() -> dict[str, Path]:
    """Every installed Chrome / Edge; NHIMC_BROWSER_PATH (if set) is used alone."""
    override = os.environ.get("NHIMC_BROWSER_PATH")
    candidates = [Path(override)] if override else [*BROWSER_PATHS, *CHROME_PATHS, *(Path(found) for name in ("google-chrome", "chromium", "microsoft-edge") if (found := shutil.which(name)))]
    found: dict[str, Path] = {}
    for path in candidates:
        if path.is_file():
            found.setdefault("edge" if "edge" in path.name.lower() else "chrome", path.resolve())
    return found


def _page(identifier: str, title: str) -> str:
    cards = "".join(
        f'<section class="card nhimc-card" data-nhimc-component="ContentCard"><p>{title} 카드 {index}. '
        "폭이 줄면 이 글줄이 다시 접히고 카드 높이가 달라집니다. 폭이 줄면 이 글줄이 다시 접히고 카드 높이가 달라집니다.</p></section>"
        for index in range(40)
    )
    return f'<section data-screen-panel="{identifier}"><main data-nhimc-role="content"><h1>{title}</h1>{cards}</main></section>'


def fragment(frame: str, owner: str) -> str:
    attribute = f' data-scroll-owner="{owner}"' if owner == "document" else ""
    pages = _page("overview", "업무 현황") + _page("requests", "요청 목록")
    return (
        f'<!doctype html><html lang="ko" data-theme="light" data-frame="{frame}"{attribute}>'
        '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>업무 화면</title></head><body>{pages}"
        f'<script type="application/json" data-nhimc-menu>{MENU}</script></body></html>'
    )


def build_cells(root: Path, workspace: Path, cases=CASES, viewports=VIEWPORTS) -> list[dict]:
    cells: list[dict] = []
    for frame, owner in cases:
        name = f"{frame}-{owner}" if owner else frame
        folder = workspace / name
        folder.mkdir(parents=True, exist_ok=True)
        source = folder / "source.html"
        source.write_text(fragment(frame, owner), encoding="utf-8", newline="\n")
        page = build_single_html(root, source, folder / "index.html")
        for width, height in viewports:
            cells.append({"id": f"{name}|{width}", "width": width, "height": height, "url": page.resolve().as_uri()})
    return cells


def measure(root: Path, browser: Path, cells: list[dict]) -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="nhimc-modal-stability-matrix-") as folder:
        matrix = Path(folder) / "matrix.json"
        matrix.write_text(json.dumps({"cells": cells}, ensure_ascii=False), encoding="utf-8")
        completed = subprocess.run(
            ["node", str(root / "scripts/verify_modal_stability.mjs"), str(browser), str(matrix)],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=max(300, len(cells) * 25), check=False,
        )
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])["results"]
    except (IndexError, json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(f"modal stability measurement produced no report: {completed.stderr[-2000:]}") from error


def problems(label: str, results: list[dict]) -> list[str]:
    found: list[str] = []
    for result in results:
        if result.get("error"):
            found.append(f"{label} {result['id']}: {result['error']}")
        found.extend(f"{label} {result['id']}: {item}" for item in result.get("problems", []))
    return found


def run_modal_stability(root: Path = ROOT, **options) -> dict:
    root = root.resolve()
    installed = browsers()
    if not installed:
        raise RuntimeError("no Chrome or Edge found; set NHIMC_BROWSER_PATH")
    found: list[str] = []
    with tempfile.TemporaryDirectory(prefix="nhimc-modal-stability-") as folder:
        cells = build_cells(root, Path(folder), **options)
        for label, browser in installed.items():
            found.extend(problems(label, measure(root, browser, cells)))
    return {"browsers": sorted(installed), "cells": len(cells), "problems": found, "all_passed": not found}


if __name__ == "__main__":
    report = run_modal_stability()
    for item in report["problems"]:
        print(f"  {item}")
    print(f"modal stability: {report['cells']} cells x {', '.join(report['browsers'])} {'PASS' if report['all_passed'] else 'FAIL'}")
    raise SystemExit(0 if report["all_passed"] else 1)
