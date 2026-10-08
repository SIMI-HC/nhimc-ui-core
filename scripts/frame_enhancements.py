"""Browser verification of the Frame enhancements (every Frame except PRESENTATION), built offline and as a Web Runtime page:

- scroll-to-top button: hidden at the top, shown after scrolling, reachable, returns to the top, hides again
- data-tip tooltip: shown with the tip text inside the viewport, hidden on pointer out
- count-up ends on the written number; card motion exists and is off for prefers-reduced-motion: reduce
- dark mode: the accent card head / outline and the primary button use the generated tones in every theme colour, readable
- help sheet takes half the screen (288px on a phone); the BLOG column is 1560px wide on a wide screen
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
from scripts.dark_tones import DARK_CARD, HEAD, LINE, SOFT, _chips, _themes, mix
from scripts.run_browser_tests import find_browser

ROOT = Path(__file__).resolve().parents[1]
FRAMES = (("blog", "main"), ("blog", "document"), ("top", "main"), ("top-left", "main"), ("left", "main"))
WEB_FRAMES = (("blog", "main"), ("top-left", "main"))
THEMES = ("light", "dark")
VIEWPORTS = ((1920, 1000), (375, 800))
EPSILON = 2.0
HELP_EPSILON = 10.0  # vw can include or exclude the page scrollbar (BLOG document scroll)
TEXT_CONTRAST = 4.5

CONTENT = (
    '<main data-nhimc-role="content">'
    '<section class="nhimc-page-header" data-nhimc-role="page-header" data-nhimc-component="PageHeader"><div><h1>이송 현황</h1>'
    '<p>오늘 접수된 이송 요청을 조회합니다.</p></div><div class="nhimc-actions"><button class="btn primary" type="button" data-nhimc-component="Button">이송 요청 등록</button></div></section>'
    '<div class="nhimc-grid nhimc-stat-grid">'
    '<section class="card nhimc-card nhimc-stat" data-nhimc-accent="sky" data-nhimc-component="Stat"><div class="nhimc-card-head"><strong>전체 요청</strong></div>'
    '<div class="nhimc-card-body nhimc-stat-body"><p class="nhimc-stat-value">1,284<span class="nhimc-stat-unit">건</span></p><small class="nhimc-stat-note">오늘 접수</small></div></section>'
    '<section class="card nhimc-card nhimc-stat" data-nhimc-accent="pear" data-nhimc-component="Stat"><div class="nhimc-card-head"><strong>완료</strong></div>'
    '<div class="nhimc-card-body nhimc-stat-body"><p class="nhimc-stat-value">96.5<span class="nhimc-stat-unit">%</span></p><small class="nhimc-stat-note">처리율</small></div></section>'
    "</div>"
    '<section class="card nhimc-card" data-nhimc-accent="sky" data-nhimc-component="ContentCard"><div class="nhimc-card-head"><strong>조회 조건</strong></div>'
    '<div class="nhimc-card-body"><p>이송일과 상태를 고릅니다. <span class="badge ok" data-tip="이송이 끝나 도착 확인까지 마친 요청입니다" data-nhimc-component="Badge">완료</span></p></div></section>'
    + "".join(
        f'<section class="card nhimc-card" data-nhimc-component="ContentCard"><div class="nhimc-card-head"><strong>{index}번째 목록</strong></div>'
        + '<div class="nhimc-card-body">'
        + ('<div class="nhimc-scroll"><table data-nhimc-component="Table" aria-label="목록"><thead><tr><th scope="col">부서</th><th scope="col" class="nhimc-num">수량</th></tr></thead>'
           '<tbody><tr><td>내과</td><td class="nhimc-num">1,284</td></tr></tbody></table></div>' if index == 1 else "")
        + "".join(f"<p>{index}-{line} 긴 화면을 실제로 스크롤해 맨 위로 버튼과 모션을 확인합니다.</p>" for line in range(1, 7))
        + "</div></section>"
        for index in range(1, 9)
    )
    + "</main>"
)


def fragment(frame: str, owner: str, theme: str, runtime_url: str | None = None) -> str:
    head_script = f'<script src="{runtime_url}"></script>' if runtime_url else ""
    scroll = f' data-scroll-owner="{owner}"' if frame == "blog" else ""
    return (
        f'<!doctype html><html lang="ko" data-theme="{theme}" data-frame="{frame}"{scroll}>'
        f'<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>이송 현황</title>{head_script}</head>'
        f'<body><section data-screen-panel="status">{CONTENT}</section>'
        '<section data-screen-panel="notes"><main data-nhimc-role="content"><h1>공지</h1><p>짧은 화면입니다.</p></main></section>'
        '<script type="application/json" data-nhimc-menu>[{"id":"status","label":"현황","icon":"list","href":"#status"},{"id":"notes","label":"공지","icon":"bell","href":"#notes"}]</script>'
        "</body></html>"
    )


def expected_tones(root: Path) -> dict:
    sky = _chips(root)["sky"]
    return {
        "headDark": mix(sky, DARK_CARD, HEAD),
        "lineDark": mix(sky, DARK_CARD, LINE),
        "pastel": sky.lower(),
        "soft": {
            ("nhimc-default" if theme_id == "nhimc-default" else theme_id): mix(theme["tokens"]["dark"]["primary"], DARK_CARD, SOFT)
            for theme_id, theme in _themes(root).items()
        },
    }


def build_cells(root: Path, workspace: Path) -> list[dict]:
    runtime_url = (root / "dist/nhimc-web.js").resolve().as_uri()
    cells: list[dict] = []
    for frame, owner in FRAMES:
        for theme in THEMES:
            folder = workspace / frame / owner / theme
            folder.mkdir(parents=True, exist_ok=True)
            source = folder / "source.html"
            source.write_text(fragment(frame, owner, theme), encoding="utf-8", newline="\n")
            paths = {"offline": build_single_html(root, source, folder / "index.html")}
            if (frame, owner) in WEB_FRAMES:
                web = folder / "web.html"
                web.write_text(fragment(frame, owner, theme, runtime_url), encoding="utf-8", newline="\n")
                paths["web"] = web
            for mode, path in paths.items():
                for width, height in VIEWPORTS:
                    if mode == "web" and width < 768:
                        continue
                    cells.append({
                        "id": f"{frame}|{owner}|{theme}|{mode}|{width}x{height}", "frame": frame, "owner": owner, "theme": theme,
                        "mode": mode, "width": width, "height": height, "url": path.resolve().as_uri(),
                    })
    return cells


def measure(root: Path, cells: list[dict]) -> list[dict]:
    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix="nhimc-enhance-matrix-") as folder:
        matrix = Path(folder) / "matrix.json"
        matrix.write_text(json.dumps({"cells": cells}, ensure_ascii=False), encoding="utf-8")
        completed = subprocess.run(
            ["node", str(root / "scripts/verify_frame_enhancements.mjs"), str(browser), str(matrix)],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=max(300, len(cells) * 14), check=False,
        )
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])["results"]
    except (IndexError, json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(f"frame enhancement measurement produced no report: {completed.stderr[-2000:]}") from error


def problems(cells: list[dict], results: list[dict], expected: dict) -> list[str]:
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

        phone = cell["width"] < 768
        fab = result.get("fab", {})
        expect(fab.get("exists"), "no scroll-to-top button")
        expect(fab.get("hiddenAtTop"), "scroll-to-top button is shown at the top")
        expect(fab.get("shownScrolled"), "scroll-to-top button does not appear after scrolling")
        expect(fab.get("reachable"), "scroll-to-top button is covered by other content")
        expect(fab.get("returnedTop"), "scroll-to-top button does not return to the top")
        expect(fab.get("hiddenAgain"), "scroll-to-top button stays after returning to the top")
        expect(bool(fab.get("label")), "scroll-to-top button has no accessible name")
        box = fab.get("box") or {}
        right, bottom = (16, 44) if phone else (28, 56)
        expect(abs(box.get("right", -99) - right) <= EPSILON and abs(box.get("bottom", -99) - bottom) <= EPSILON, f"scroll-to-top button is at right={box.get('right')} bottom={box.get('bottom')}")
        expect(abs(box.get("width", 0) - 44) <= EPSILON, "scroll-to-top button is not 44px")
        tip = result.get("tip", {})
        expect(tip.get("target"), "the fixture has no data-tip element")
        expect(tip.get("shown") and tip.get("text") == tip.get("expected"), "data-tip tooltip is not shown with its text")
        expect(tip.get("inViewport"), "data-tip tooltip leaves the viewport")
        expect(tip.get("hiddenAfter"), "data-tip tooltip stays after the pointer leaves")
        stat = result.get("stat", {})
        expect(stat.get("after") == stat.get("text"), f"count-up ends on {stat.get('after')!r}, not {stat.get('text')!r}")
        expect(result.get("motion", {}).get("animation") == "nhimc-rise", f"cards do not rise in (animation {result.get('motion', {}).get('animation')!r})")
        expect(result.get("reducedMotion", {}).get("animation") == "none", "cards still animate under prefers-reduced-motion: reduce")
        expect(not result.get("pageOverflowX"), "the page scrolls horizontally")
        table = result.get("table", {})
        expect(table.get("headRight") and table.get("cellRight"), "numeric table cells (class nhimc-num) are not right aligned")
        expect("tabular-nums" in (table.get("numeric") or ""), "numeric table cells do not use equal-width digits")
        hover = result.get("navHover")
        if cell["frame"] in ("blog", "top") and not phone:
            expect(bool(hover) and hover.get("hovered"), "the menu button is not hovered by the real mouse")
            if hover and hover.get("hovered"):
                expect(hover.get("background") not in ("rgba(0, 0, 0, 0)", "transparent"), "menu hover paints no background")
                shadow = hover.get("shadow") or ""
                if hover.get("paddingLeft", 99) < 4:  # BLOG: no horizontal padding, so the background is widened 12px per side
                    expect("-12px 0px 0px 0px" in shadow and " 12px 0px 0px 0px" in shadow, f"menu hover is not widened 12px per side ({shadow!r})")
                else:
                    expect(shadow == "none", f"menu hover is widened although the button has padding ({shadow!r})")

        tones = {entry["colour"]: entry for entry in result.get("tones", [])}
        for colour, entry in tones.items():
            if cell["theme"] == "dark":
                expect(entry.get("headBackground") == expected["headDark"], f"dark {colour}: accent head is {entry.get('headBackground')}, not {expected['headDark']}")
                expect(entry.get("outline") == expected["lineDark"], f"dark {colour}: accent outline is {entry.get('outline')}, not {expected['lineDark']}")
                expect(entry.get("headContrast", 0) >= TEXT_CONTRAST, f"dark {colour}: accent head text contrast {entry.get('headContrast')}")
                expect(entry.get("buttonBackground") == expected["soft"][colour], f"dark {colour}: primary button is {entry.get('buttonBackground')}, not {expected['soft'][colour]}")
                expect(entry.get("buttonBorder") == entry.get("buttonBackground"), f"dark {colour}: primary button border differs from its background")
                expect(entry.get("buttonContrast", 0) >= TEXT_CONTRAST, f"dark {colour}: primary button text contrast {entry.get('buttonContrast')}")
            else:
                # every theme colours an accent card (it was Color Mix only: white head and a black outline elsewhere)
                expect(entry.get("headBackground") == expected["pastel"], f"light {colour}: accent head is {entry.get('headBackground')}, not the pastel {expected['pastel']}")
                expect(entry.get("outline") == expected["pastel"], f"light {colour}: accent outline is {entry.get('outline')}, not the pastel {expected['pastel']}")
                expect(entry.get("headContrast", 0) >= TEXT_CONTRAST, f"light {colour}: accent head text contrast {entry.get('headContrast')}")
                expect(entry.get("buttonBackground") != expected["soft"][colour], "light mode shows the dark button tone")

        width = result.get("contentWidth")
        if cell["frame"] == "blog":
            if phone:
                expect(width is not None and width <= cell["width"], f"BLOG column is {width}px on a {cell['width']}px screen")
            else:
                expect(width is not None and 1500 <= width <= 1560 + EPSILON, f"BLOG column is {width}px on a {cell['width']}px screen, not 1560px")
        help_width = result.get("helpWidth")
        expect(help_width is not None, "help sheet did not open")
        if help_width is not None:
            wanted = 288 if phone else cell["width"] / 2
            expect(abs(help_width - wanted) <= HELP_EPSILON, f"help sheet is {help_width}px wide, not {wanted}px")
    return found


def run_frame_enhancements(root: Path = ROOT) -> dict:
    expected = expected_tones(root)
    with tempfile.TemporaryDirectory(prefix="nhimc-enhance-") as folder:
        cells = build_cells(root, Path(folder))
        results = measure(root, cells)
    found = problems(cells, results, expected)
    return {"cells": len(cells), "problems": found, "all_passed": not found}


if __name__ == "__main__":
    report = run_frame_enhancements()
    for item in report["problems"]:
        print(f"  {item}")
    print(f"frame enhancements: {report['cells']} cells {'PASS' if report['all_passed'] else 'FAIL'}")
    raise SystemExit(0 if report["all_passed"] else 1)
