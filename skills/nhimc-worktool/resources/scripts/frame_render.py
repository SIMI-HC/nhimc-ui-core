"""Browser verification of what a built Frame really renders, for every Frame x Theme x mode x viewport x build path.

The same three-page Content (menu with icons, a primary Button) is built through the local builder (offline
index.html) and through the Web Runtime, opened in headless Chrome and measured:

- the selected theme colour is the one that is actually computed (--color-primary and the primary Button), so a
  stylesheet order bug (Frame defaults overriding the theme overlay) is caught
- every menu icon on screen has a bounded size, stays inside its button, does not overlap its label and has an
  accessible name
- no horizontal page scroll
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
from scripts.canonical_frame import FRAME_FILES
from scripts.run_browser_tests import find_browser
from scripts.theme_colors import DEFAULT_THEME_COLOR, theme_color_ids

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ("left", "left-blank", "left-dual", "top", "top-left", "presentation", "presentation-vertical", "blog")
MODES = ("light", "dark")
VIEWPORTS = ((1440, 900), (768, 900), (375, 800))
PATHS = ("offline", "web")
MAX_ICON = 24.0

MENU = (
    '[{"id":"overview","label":"업무 현황","icon":"home","href":"#overview"},'
    '{"id":"requests","label":"요청 목록","icon":"list","href":"#requests"},'
    '{"id":"create","label":"요청 등록","icon":"plus","href":"#create"}]'
)


def _page(identifier: str, title: str) -> str:
    return (
        f'<section data-screen-panel="{identifier}"><main data-nhimc-role="content">'
        f"<h1>{title}</h1><p>대표 화면입니다.</p>"
        '<button class="btn primary" type="button" data-nhimc-component="Button">주요 행동</button>'
        "</main></section>"
    )


def fragment(frame: str, mode: str, theme: str, runtime_url: str | None = None) -> str:
    color = "" if theme == DEFAULT_THEME_COLOR else f' data-theme-color="{theme}"'
    head_script = f'<script src="{runtime_url}"></script>' if runtime_url else ""
    pages = _page("overview", "업무 현황") + _page("requests", "요청 목록") + _page("create", "요청 등록")
    return (
        f'<!doctype html><html lang="ko" data-theme="{mode}" data-frame="{frame}"{color}>'
        '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>업무 화면</title>{head_script}</head><body>{pages}"
        f'<script type="application/json" data-nhimc-menu>{MENU}</script></body></html>'
    )


def build_cells(
    root: Path, workspace: Path, *, frames=FRAMES, themes=None, modes=MODES, viewports=VIEWPORTS, paths=PATHS, shots: Path | None = None,
) -> list[dict]:
    themes = tuple(themes or theme_color_ids(root))
    runtime_url = (root / "dist/nhimc-web.js").resolve().as_uri()
    cells: list[dict] = []
    for frame in frames:
        for theme in themes:
            for mode in modes:
                folder = workspace / frame / theme / mode
                folder.mkdir(parents=True, exist_ok=True)
                source = folder / "source.html"
                source.write_text(fragment(frame, mode, theme), encoding="utf-8", newline="\n")
                built = {}
                if "offline" in paths:
                    built["offline"] = build_single_html(root, source, folder / "index.html")
                if "web" in paths:
                    web = folder / "web.html"
                    web.write_text(fragment(frame, mode, theme, runtime_url), encoding="utf-8", newline="\n")
                    built["web"] = web
                for path_name, page in built.items():
                    for width, height in viewports:
                        cell = {
                            "id": f"{frame}|{theme}|{mode}|{path_name}|{width}", "frame": frame, "theme": theme, "mode": mode,
                            "path": path_name, "width": width, "height": height, "url": page.resolve().as_uri(),
                        }
                        if shots:
                            cell["shot"] = str(shots / (cell["id"].replace("|", "_") + ".png"))
                        cells.append(cell)
    return cells


def measure(root: Path, cells: list[dict]) -> list[dict]:
    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix="nhimc-frame-render-matrix-") as folder:
        matrix = Path(folder) / "matrix.json"
        matrix.write_text(json.dumps({"cells": cells}, ensure_ascii=False), encoding="utf-8")
        completed = subprocess.run(
            ["node", str(root / "scripts/verify_frame_render.mjs"), str(browser), str(matrix)],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=max(300, len(cells) * 6), check=False,
        )
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])["results"]
    except (IndexError, json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(f"frame render measurement produced no report: {completed.stderr[-2000:]}") from error


def expected_primaries(root: Path) -> dict[tuple[str, str], list[int]]:
    catalog = json.loads((root / "vendor/nhimc-design/tokens/themes/catalog.yaml").read_text(encoding="utf-8"))
    table: dict[tuple[str, str], list[int]] = {}
    for theme in catalog["themes"]:
        for mode in MODES:
            value = theme["tokens"].get(mode, {}).get("primary", "").lstrip("#")
            if len(value) == 6:
                table[(theme["id"], mode)] = [int(value[index:index + 2], 16) for index in (0, 2, 4)]
    return table


def expected_buttons(root: Path) -> dict[tuple[str, str], list[int]]:
    """The primary Button: the theme primary in light, the toned colour (scripts/dark_tones.py) in dark."""
    from scripts.dark_tones import DARK_CARD, SOFT, mix

    table = dict(expected_primaries(root))
    for (theme, mode), rgb in expected_primaries(root).items():
        if mode == "dark":
            soft = mix("#" + "".join(f"{part:02x}" for part in rgb), DARK_CARD, SOFT)
            table[(theme, mode)] = [int(soft[index:index + 2], 16) for index in (1, 3, 5)]
    return table


def cell_problems(cell: dict, result: dict, expected: dict[tuple[str, str], list[int]], buttons: dict[tuple[str, str], list[int]] | None = None) -> list[str]:
    label = cell["id"]
    if result.get("error"):
        return [f"{label}: {result['error']}"]
    found: list[str] = []
    want = expected.get((cell["theme"], cell["mode"]))
    if want:
        if result.get("primaryRgb") != want:
            found.append(f"{label}: theme colour not applied, --color-primary is {result.get('primaryToken')} (expected rgb{tuple(want)})")
        button = (buttons or expected).get((cell["theme"], cell["mode"]), want)
        if result.get("buttonRgb") != button:
            found.append(f"{label}: primary Button is rgb{tuple(result.get('buttonRgb') or ())}, expected rgb{tuple(button)}")
    if result.get("pageOverflowX"):
        found.append(f"{label}: the page scrolls horizontally")
    if not result.get("icons") and cell["frame"] not in {"presentation", "presentation-vertical"} and cell["width"] >= 768             and not (cell["frame"] == "left-dual" and cell["width"] < 1024):  # LEFT DUAL's rail is a drawer below 1024px
        found.append(f"{label}: no menu icon was measured")
    for icon in result.get("icons", []):
        if icon["width"] > MAX_ICON or icon["height"] > MAX_ICON:
            found.append(f"{label}: menu icon is {icon['width']:.0f}x{icon['height']:.0f}px (max {MAX_ICON:.0f})")
        if icon["overlapsLabel"]:
            found.append(f"{label}: menu icon overlaps its label")
        if not icon["insideOwner"]:
            found.append(f"{label}: menu icon spills outside its button")
        if not icon["named"]:
            found.append(f"{label}: icon-only menu button has no accessible name")
        if not icon["resolvesToSymbol"]:
            found.append(f"{label}: menu icon <use> does not resolve to an icon <symbol> (id collision or unknown icon)")
    return found


def problems(root: Path, cells: list[dict], results: list[dict]) -> list[str]:
    by_id = {result["id"]: result for result in results}
    expected = expected_primaries(root)
    buttons = expected_buttons(root)
    found: list[str] = []
    for cell in cells:
        found.extend(dict.fromkeys(cell_problems(cell, by_id.get(cell["id"], {"error": "no measurement"}), expected, buttons)))
    return found


def run_frame_render(root: Path = ROOT, **options) -> dict:
    root = root.resolve()
    with tempfile.TemporaryDirectory(prefix="nhimc-frame-render-") as folder:
        cells = build_cells(root, Path(folder), **options)
        results = measure(root, cells)
    found = problems(root, cells, results)
    return {"cells": len(cells), "problems": found, "all_passed": not found, "results": results}


if __name__ == "__main__":
    report = run_frame_render()
    for item in report["problems"]:
        print(f"  {item}")
    print(f"frame render: {report['cells']} cells {'PASS' if report['all_passed'] else 'FAIL'}")
    raise SystemExit(0 if report["all_passed"] else 1)
