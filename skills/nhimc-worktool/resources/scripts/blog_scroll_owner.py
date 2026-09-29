"""Browser verification of the BLOG scroll-owner contract (Frame nhimc-blog 1.1.0).

The same long Content is built through the offline builder and through the Web Runtime for both scroll owners,
both themes and 375 / 768 / 1440px, then really scrolled in headless Chrome:

- main (default): the page does not scroll, Main scrolls, the SiteHeader is not sticky and stays transparent
- document: the page scrolls, the SiteHeader is sticky on an opaque --color-background surface with the
  --color-border-accent border and the canonical --shadow-lg, and anchors clear it
- never sticky + transparent; the header never overlaps Content; no horizontal page scroll
- the mobile menu and the help dialog keep working while scrolled
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
OWNERS = ("main", "document")
THEMES = ("light", "dark")
VIEWPORTS = ((375, 800), (768, 900), (1440, 900))
EPSILON = 1.0
TEXT_CONTRAST = 4.5
# The canonical transparent header (Main scroll) shows --muted (#737373) nav text on the #f4f7fa canvas: 4.41:1. The
# Frame is not redesigned here, so Main scroll asserts it does not get worse; the opaque document header must be AA.
CANONICAL_MAIN_CONTRAST = 4.4

MENU = (
    '[{"id":"news","label":"소식","icon":"home","href":"#news"},'
    '{"id":"notice","label":"공지","icon":"bell","href":"#notice"}]'
)


def _long_content() -> str:
    sections = "".join(
        f'<section id="sec-{index}"><h2>{index}번째 소식</h2>'
        + "".join(f"<p>{index}-{line} 병원 소식 본문입니다. 긴 콘텐츠를 실제로 스크롤해 헤더와 겹치지 않는지 확인합니다.</p>" for line in range(1, 9))
        + "</section>"
        for index in range(1, 7)
    )
    links = "".join(f'<a href="#sec-{index}">{index}번</a> ' for index in range(1, 7))
    return f'<main data-nhimc-role="content"><h1>병원 소식</h1><nav aria-label="바로가기">{links}</nav>{sections}</main>'


def fragment(owner: str, theme: str, runtime_url: str | None = None) -> str:
    head_script = f'<script src="{runtime_url}"></script>' if runtime_url else ""
    panels = (
        f'<section data-screen-panel="news">{_long_content()}</section>'
        '<section data-screen-panel="notice"><main data-nhimc-role="content"><h1>공지</h1><p>짧은 화면입니다.</p></main></section>'
    )
    return (
        f'<!doctype html><html lang="ko" data-theme="{theme}" data-frame="blog" data-scroll-owner="{owner}">'
        f'<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>병원 소식</title>{head_script}</head><body>'
        f'{panels}<script type="application/json" data-nhimc-menu>{MENU}</script></body></html>'
    )


def build_cells(root: Path, workspace: Path, viewports=VIEWPORTS, owners=OWNERS, themes=THEMES, modes=("offline", "web")) -> list[dict]:
    runtime_url = (root / "dist/nhimc-web.js").resolve().as_uri()
    cells: list[dict] = []
    for owner in owners:
        for theme in themes:
            folder = workspace / owner / theme
            folder.mkdir(parents=True, exist_ok=True)
            source = folder / "source.html"
            source.write_text(fragment(owner, theme), encoding="utf-8", newline="\n")
            paths = {}
            if "offline" in modes:
                paths["offline"] = build_single_html(root, source, folder / "index.html")
            if "web" in modes:
                web = folder / "web.html"
                web.write_text(fragment(owner, theme, runtime_url), encoding="utf-8", newline="\n")
                paths["web"] = web
            for mode, path in paths.items():
                for width, height in viewports:
                    cells.append({
                        "id": f"{owner}|{theme}|{mode}|{width}x{height}", "owner": owner, "theme": theme, "mode": mode,
                        "width": width, "height": height, "url": path.resolve().as_uri(),
                    })
    return cells


def measure(root: Path, cells: list[dict]) -> list[dict]:
    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix="nhimc-blog-matrix-") as folder:
        matrix = Path(folder) / "matrix.json"
        matrix.write_text(json.dumps({"cells": cells}, ensure_ascii=False), encoding="utf-8")
        completed = subprocess.run(
            ["node", str(root / "scripts/verify_blog_scroll_owner.mjs"), str(browser), str(matrix)],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=max(240, len(cells) * 12), check=False,
        )
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])["results"]
    except (IndexError, json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(f"blog scroll-owner measurement produced no report: {completed.stderr[-2000:]}") from error


def problems(cells: list[dict], results: list[dict]) -> list[str]:
    found: list[str] = []
    by_id = {result["id"]: result for result in results}
    for cell in cells:
        result = by_id.get(cell["id"], {})
        label = cell["id"]
        if result.get("error"):
            found.append(f"{label}: {result['error']}")
            continue

        def expect(condition: bool, message: str) -> None:
            if not condition:
                found.append(f"{label}: {message}")

        owner = cell["owner"]
        expect(result.get("owner") == owner, f"app-shell scroll owner is {result.get('owner')!r}")
        expect(result.get("position") != "sticky" or result.get("headerAlpha") == 1, "SiteHeader is sticky and transparent")
        expect(abs(result.get("headerHeight", 0) - 64) <= EPSILON, f"SiteHeader height is {result.get('headerHeight')}")
        expect(not result.get("pageOverflowX"), "the page scrolls horizontally")
        expect(result.get("scrollRange", 0) > 100, "the long Content did not produce a scroll range")
        expect(result.get("firstBelowHeader"), "the first Content block starts under the SiteHeader")
        expect(result.get("help", {}).get("open") and result["help"].get("closed"), "help dialog does not open and close")
        if cell["width"] < 768:
            drawer = result.get("drawer") or {}
            expect(drawer.get("visible") and drawer.get("coversHeader"), "mobile menu drawer is hidden behind the SiteHeader")
        if result.get("contrast") is not None:
            floor = TEXT_CONTRAST if cell["owner"] == "document" else CANONICAL_MAIN_CONTRAST
            expect(result["contrast"] >= floor, f"header text contrast {result['contrast']} < {floor}")
        for step in result.get("steps", []):
            expect(abs(step["headerTop"]) <= EPSILON, f"SiteHeader moved to top={step['headerTop']} at scroll {step['fraction']:.0%}")
            expect(step["headerOnTop"], f"Content is drawn over the SiteHeader at scroll {step['fraction']:.0%}")
            expect(not step["pageOverflowX"], f"horizontal page scroll at scroll {step['fraction']:.0%}")
            expect(step["contentTop"] >= result["headerHeight"] - EPSILON or owner == "document",
                   f"Main starts under the SiteHeader (top={step['contentTop']})")
        for anchor in result.get("anchors", []):
            expect(anchor["top"] >= anchor["headerBottom"] - EPSILON, f"anchor #{anchor['id']} lands under the SiteHeader (top={anchor['top']})")
        if owner == "main":
            expect(not result.get("pageScrolls"), "the page scrolls; Main must own the scroll")
            expect(result.get("mainScrolls"), "Main does not scroll")
            expect(abs(result.get("shellHeight", 0) - result.get("viewportHeight", 0)) <= EPSILON, "app-shell is not 100svh")
            expect(result.get("position") != "sticky", "SiteHeader is sticky in Main scroll")
            expect(result.get("headerAlpha") == 0, f"SiteHeader is not transparent ({result.get('headerBackground')})")
            expect(result.get("borderWidth") == 0, "SiteHeader has a border in Main scroll")
        else:
            expect(result.get("pageScrolls"), "the page does not scroll; the document must own the scroll")
            expect(not result.get("mainScrolls"), "Main still scrolls on its own")
            expect(result.get("position") == "sticky", f"SiteHeader is {result.get('position')}, not sticky")
            expect(result.get("headerAlpha") == 1, f"SiteHeader is not opaque ({result.get('headerBackground')})")
            expect(result.get("headerBackground") == _rgb(result.get("background", "")), "SiteHeader surface is not var(--color-background)")
            expect(result.get("borderWidth") == 1, f"SiteHeader border is {result.get('borderWidth')}px")
            expect(result.get("shadow") not in (None, "", "none"), "SiteHeader has no shadow")
            for step in result.get("steps", []):
                expect(step["fraction"] == 0 or step["scrollTop"] > 0, "the document did not scroll")
    return found


def _rgb(hex_color: str) -> str:
    value = hex_color.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    if len(value) != 6:
        return ""
    r, g, b = (int(value[index:index + 2], 16) for index in (0, 2, 4))
    return f"rgb({r}, {g}, {b})"


def run_blog_scroll_owner(root: Path = ROOT, viewports=VIEWPORTS) -> dict:
    root = root.resolve()
    with tempfile.TemporaryDirectory(prefix="nhimc-blog-") as folder:
        cells = build_cells(root, Path(folder), viewports)
        results = measure(root, cells)
    found = problems(cells, results)
    return {"cells": len(cells), "problems": found, "all_passed": not found}


if __name__ == "__main__":
    report = run_blog_scroll_owner()
    for item in report["problems"]:
        print(f"  {item}")
    print(f"blog scroll owner: {report['cells']} cells {'PASS' if report['all_passed'] else 'FAIL'}")
    raise SystemExit(0 if report["all_passed"] else 1)
