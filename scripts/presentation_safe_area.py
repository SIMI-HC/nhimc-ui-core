"""Browser verification of the PRESENTATION Frame contract (Header / Content Safe Area / Controller).

Builds the same Content through the offline builder and through the Web Runtime, for both presentation
frames, both themes and desktop / narrow-portrait viewports, and measures the regions in headless Chrome.
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
from scripts.run_browser_tests import find_browser

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ("presentation", "presentation-vertical")
THEMES = ("light", "dark")
VIEWPORTS = ((1440, 900), (900, 600), (390, 844))
EPSILON = 1.0

MENU = (
    '[{"id":"today","label":"오늘 일정","icon":"calendar","href":"#today"},'
    '{"id":"week","label":"주간 일정","icon":"clock","href":"#week"}]'
)


def _rows(count: int) -> str:
    return "".join(
        f"<tr><td>{9 + index % 9:02d}:00</td><td>회의 {index + 1}</td><td>회의실 {index % 5 + 1}</td></tr>"
        for index in range(count)
    )


def _page(title: str, rows: int, cards: int) -> str:
    card_html = "".join(
        f'<div class="card" data-nhimc-component="Card"><strong>메모 {index + 1}</strong><p>시연용 일정 메모입니다.</p></div>'
        for index in range(cards)
    )
    return (
        '<main data-nhimc-role="content">'
        f'<section class="nhimc-page-header" data-nhimc-component="PageHeader"><div><h1>{title}</h1><p>시연용 일정입니다.</p></div></section>'
        '<section class="card nhimc-card" data-nhimc-component="ContentCard"><div class="nhimc-scroll">'
        '<table data-nhimc-component="Table"><caption>시연용 일정</caption><thead><tr><th scope="col">시간</th><th scope="col">일정</th><th scope="col">장소</th></tr></thead>'
        f"<tbody>{_rows(rows)}</tbody></table></div></section>"
        f'<div class="nhimc-grid" data-nhimc-component="Grid">{card_html}</div>'
        "</main>"
    )


def fragment(frame: str, theme: str, oversized: bool, runtime_url: str | None = None) -> str:
    rows, cards = (60, 24) if oversized else (3, 2)
    head_script = f'<script src="{runtime_url}"></script>' if runtime_url else ""
    return (
        f'<!doctype html><html lang="ko" data-theme="{theme}" data-frame="{frame}">'
        f'<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>일정 관리</title>{head_script}</head><body>'
        f'<section data-screen-panel="today">{_page("오늘 일정", rows, cards)}</section>'
        f'<section data-screen-panel="week">{_page("주간 일정", rows, cards)}</section>'
        f'<script type="application/json" data-nhimc-menu>{MENU}</script>'
        "</body></html>"
    )


def build_cells(root: Path, workspace: Path, viewports=VIEWPORTS, frames=FRAMES, themes=THEMES) -> list[dict]:
    runtime_url = (root / "dist/nhimc-web.js").resolve().as_uri()
    cells: list[dict] = []
    for frame in frames:
        for theme in themes:
            for oversized in (False, True):
                size = "oversized" if oversized else "normal"
                source = workspace / frame / theme / size / "source.html"
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text(fragment(frame, theme, oversized), encoding="utf-8", newline="\n")
                offline = source.parent / "index.html"
                build_single_html(root, source, offline)
                web = source.parent / "web.html"
                web.write_text(fragment(frame, theme, oversized, runtime_url), encoding="utf-8", newline="\n")
                for mode, path in (("offline", offline), ("web", web)):
                    for width, height in viewports:
                        cells.append(
                            {
                                "id": f"{frame}|{theme}|{mode}|{width}x{height}|{size}",
                                "frame": frame, "theme": theme, "mode": mode, "size": size,
                                "width": width, "height": height, "url": path.resolve().as_uri(),
                            }
                        )
    return cells


def measure(root: Path, cells: list[dict]) -> list[dict]:
    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix="nhimc-presentation-matrix-") as folder:
        matrix = Path(folder) / "matrix.json"
        matrix.write_text(json.dumps({"cells": cells}, ensure_ascii=False), encoding="utf-8")
        completed = subprocess.run(
            ["node", str(root / "scripts/verify_presentation_safe_area.mjs"), str(browser), str(matrix)],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=max(180, len(cells) * 6), check=False,
        )
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])["results"]
    except (IndexError, json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(f"presentation measurement produced no report: {completed.stderr[-2000:]}") from error


def _same(a: dict | None, b: dict | None) -> bool:
    if a is None or b is None:
        return a is b
    return all(abs(a[key] - b[key]) <= EPSILON for key in ("top", "bottom", "left", "right"))


def problems(cells: list[dict], results: list[dict]) -> list[str]:
    """Contract violations. The oversized cells must be detected as overflow, never hidden."""
    found: list[str] = []
    by_id = {result["id"]: result for result in results}
    for cell in cells:
        result = by_id.get(cell["id"], {})
        label = cell["id"]
        if result.get("error"):
            found.append(f"{label}: {result['error']}")
            continue
        if result.get("overlaps"):
            found.append(f"{label}: Content overlaps {', '.join(result['overlaps'])}")
        if result.get("covered"):
            found.append(f"{label}: Content covers {', '.join(result['covered'])}")
        if not result.get("insideCanvas"):
            found.append(f"{label}: Content leaves the presentation canvas")
        if result.get("documentOverflow"):
            found.append(f"{label}: the page scrolls outside the presentation canvas")
        if cell["frame"] == "presentation":
            panel = result.get("panel") or {}
            if panel.get("top", 0) < (result.get("headerBottom") or 0) - EPSILON:
                found.append(f"{label}: Content starts above the Header bottom")
            if panel.get("bottom", 0) > ((result.get("controls") or {}).get("dots") or {}).get("top", 1e9) + EPSILON:
                found.append(f"{label}: Content ends below the Controller top")
        if cell["size"] == "normal":
            if (result.get("overflowY") or 0) > EPSILON or (result.get("overflowX") or 0) > EPSILON:
                found.append(f"{label}: Content exceeds the Safe Area")
        else:
            if (result.get("overflowY") or 0) <= EPSILON:
                found.append(f"{label}: oversized Content was not detected as overflow")
            normal = by_id.get(label.replace("|oversized", "|normal"), {})
            for name, box in (result.get("controls") or {}).items():
                if not _same(box, (normal.get("controls") or {}).get(name)):
                    found.append(f"{label}: {name} moved because of Content")
    return found


def run_presentation_safe_area(root: Path = ROOT, viewports=VIEWPORTS) -> dict:
    root = root.resolve()
    with tempfile.TemporaryDirectory(prefix="nhimc-presentation-") as folder:
        cells = build_cells(root, Path(folder), viewports)
        results = measure(root, cells)
    found = problems(cells, results)
    return {"cells": len(cells), "problems": found, "all_passed": not found}


if __name__ == "__main__":
    report = run_presentation_safe_area()
    for item in report["problems"]:
        print(f"  {item}")
    print(f"presentation safe area: {report['cells']} cells {'PASS' if report['all_passed'] else 'FAIL'}")
    raise SystemExit(0 if report["all_passed"] else 1)
