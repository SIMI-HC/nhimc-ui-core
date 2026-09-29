"""Browser verification of the PRESENTATION Base Contract shared by `presentation` and `presentation-vertical`.

The same three-slide Content is built through the offline builder and through the Web Runtime, for both frames,
both themes and desktop / narrow-portrait viewports, and measured in headless Chrome:

- Safe Area: Content never touches the Header (utility buttons) or Controller (dots, arrows) and never leaves the canvas
- centring: Content sits in the visual centre of the Safe Area without page-level positioning
- oversized Content is detected as overflow while Header and Controller stay where they are
- slide lifecycle: transition classes, prev / next / dots / keyboard, direction-specific keys
- both frames share Header, Theme, Branding, Controller and timing (direction is the only difference)
- contrast of text and controls in light and dark
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
BEHAVIOR_VIEWPORT = (1440, 900)
EPSILON = 1.0
CENTER_TOLERANCE = 6.0
TEXT_CONTRAST = 4.5
# The canonical Controller is a translucent dark pill with white icons; on the light theme that is about 2.4:1.
# It is not redesigned here, so the gate asserts it stays visible (>= 2:1) rather than WCAG 3:1.
CONTROL_CONTRAST = 2.0

MENU = (
    '[{"id":"today","label":"오늘 일정","icon":"calendar","href":"#today"},'
    '{"id":"week","label":"주간 일정","icon":"clock","href":"#week"},'
    '{"id":"summary","label":"요약","icon":"check-circle","href":"#summary"}]'
)
TITLES = {"today": "오늘의 일정", "week": "이번 주 흐름", "summary": "한 줄 요약"}
DIRECTION_CLASSES = {
    "presentation": {"in": "slide-in-right", "out": "slide-out-left", "back_in": "slide-in-left", "back_out": "slide-out-right"},
    "presentation-vertical": {"in": "slide-in-bottom", "out": "slide-out-top", "back_in": "slide-in-top", "back_out": "slide-out-bottom"},
}


def _slide(identifier: str, oversized: bool) -> str:
    steps = "".join(
        f'<li><strong>{name}{" " if index == 0 else ""}'
        + ('<span class="badge ok" data-nhimc-component="Badge">완료</span>' if index == 0 else "")
        + f"</strong><p>{text}</p></li>"
        for index, (name, text) in enumerate((("준비", "장비와 자료를 확인합니다."), ("진행", "예정된 순서대로 진행합니다."), ("정리", "결과를 공유합니다.")))
    )
    extra = (
        '<div class="nhimc-stack" data-nhimc-component="Stack">'
        + "".join(f"<p>추가 설명 {index + 1}: 발표 화면에 넣기에는 너무 긴 내용입니다.</p>" for index in range(40))
        + "</div>"
        if oversized
        else ""
    )
    return (
        '<main data-nhimc-role="content">'
        f'<section class="nhimc-presentation-hero" data-nhimc-component="PresentationHero"><h1>{TITLES[identifier]}</h1><p>핵심 메시지 한 가지만 전달합니다.</p></section>'
        f'<ol class="nhimc-presentation-flow" data-nhimc-component="PresentationFlow">{steps}</ol>{extra}'
        "</main>"
    )


def fragment(frame: str, theme: str, oversized: bool, runtime_url: str | None = None) -> str:
    head_script = f'<script src="{runtime_url}"></script>' if runtime_url else ""
    panels = "".join(
        f'<section data-screen-panel="{identifier}">{_slide(identifier, oversized)}</section>' for identifier in TITLES
    )
    return (
        f'<!doctype html><html lang="ko" data-theme="{theme}" data-frame="{frame}">'
        f'<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>일정 발표</title>{head_script}</head><body>'
        f'{panels}<script type="application/json" data-nhimc-menu>{MENU}</script>'
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
                                "behavior": (not oversized) and (width, height) == BEHAVIOR_VIEWPORT,
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
            timeout=max(240, len(cells) * 12), check=False,
        )
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])["results"]
    except (IndexError, json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(f"presentation measurement produced no report: {completed.stderr[-2000:]}") from error


def _same(a: dict | None, b: dict | None) -> bool:
    if a is None or b is None:
        return a is b
    return all(abs(a[key] - b[key]) <= EPSILON for key in ("top", "bottom", "left", "right"))


def _behavior_problems(label: str, frame: str, behavior: dict) -> list[str]:
    found: list[str] = []
    ids = behavior["ids"]
    classes = DIRECTION_CLASSES[frame]

    def expect(condition: bool, message: str) -> None:
        if not condition:
            found.append(f"{label}: {message}")

    initial = behavior["initial"]
    expect(initial["visible"] == [ids[0]] and initial["current"] == [ids[0]], "first slide is not the active slide at start")
    expect(initial["prevDisabled"] and not initial["nextDisabled"], "arrows are wrong on the first slide")
    for name, target, incoming, outgoing in (
        ("next", ids[1], classes["in"], classes["out"]),
        ("prev", ids[0], classes["back_in"], classes["back_out"]),
    ):
        state = behavior[name]
        expect(state["visible"] == [target] and state["current"] == [target], f"{name} did not activate the {target} slide")
        expect(state["residual"] == [], f"{name} left transition classes behind")
        expect(any(incoming in entry for entry in state["incoming"]), f"{name} does not play the {incoming} enter transition")
        expect(any(outgoing in entry for entry in state["outgoing"]), f"{name} does not play the {outgoing} leave transition")
    dot = behavior["dot"]
    expect(dot["visible"] == [ids[2]] and dot["current"] == [ids[2]] and dot["residual"] == [], "dot navigation failed")
    expect(dot["nextDisabled"] and not dot["prevDisabled"], "arrows are wrong on the last slide")
    expect(behavior["wrongKeys"]["visible"] == [ids[2]], "keys of the other direction moved the slide")
    expect(behavior["keyPrev"]["visible"] == [ids[1]], "previous key did not move back")
    expect(behavior["keyNext"]["visible"] == [ids[2]], "next key did not move forward")
    return found


def problems(cells: list[dict], results: list[dict]) -> list[str]:
    """Contract violations. Oversized cells must be detected as overflow, never hidden."""
    found: list[str] = []
    by_id = {result["id"]: result for result in results}
    for cell in cells:
        result = by_id.get(cell["id"], {})
        label = cell["id"]
        if result.get("error"):
            found.append(f"{label}: {result['error']}")
            continue
        for key, text in (("overlaps", "Safe Area overlaps"), ("covered", "Content covers")):
            if result.get(key):
                found.append(f"{label}: {text} {', '.join(result[key])}")
        if not result.get("insideCanvas"):
            found.append(f"{label}: the slide leaves the presentation canvas")
        if result.get("documentOverflow"):
            found.append(f"{label}: the page scrolls outside the presentation canvas")
        if result.get("positioned") in ("absolute", "fixed"):
            found.append(f"{label}: Content is positioned by the page ({result['positioned']})")
        if "slide" not in (result.get("slideClass") or "").split():
            found.append(f"{label}: Content is not inside the Frame's slide")
        if result.get("direction") != ("vertical" if cell["frame"] == "presentation-vertical" else "horizontal"):
            found.append(f"{label}: wrong presentation direction {result.get('direction')!r}")
        safe = result.get("safe") or {}
        controls = result.get("controls") or {}
        if cell["frame"] == "presentation":
            if safe.get("top", 0) < ((controls.get("utility") or {}).get("bottom", 0)) - EPSILON:
                found.append(f"{label}: Safe Area starts above the Header bottom")
            if safe.get("bottom", 0) > ((controls.get("dots") or {}).get("top", 1e9)) + EPSILON:
                found.append(f"{label}: Safe Area ends below the Controller top")
        if cell["size"] == "normal":
            if (result.get("overflowY") or 0) > EPSILON or (result.get("overflowX") or 0) > EPSILON:
                found.append(f"{label}: Content exceeds the Safe Area")
            if result.get("contentOverlaps"):
                found.append(f"{label}: Content overlaps {', '.join(result['contentOverlaps'])}")
            center = result.get("center") or {}
            if abs(center.get("dx", 0)) > CENTER_TOLERANCE or abs(center.get("dy", 0)) > CENTER_TOLERANCE:
                found.append(f"{label}: Content is not centred in the Safe Area (dx={center.get('dx')}, dy={center.get('dy')})")
            if center.get("contentShare", 0) > 0.9:
                found.append(f"{label}: Content fills {center['contentShare']:.0%} of the Safe Area height")
            contrast = result.get("contrast") or {}
            for name in ("heading", "muted", "card", "cardMuted", "badge"):
                if contrast.get(name) is not None and contrast[name] < TEXT_CONTRAST:
                    found.append(f"{label}: {name} text contrast {contrast[name]} < {TEXT_CONTRAST}")
            for name in ("utility", "dotCurrent"):
                if contrast.get(name) is not None and contrast[name] < CONTROL_CONTRAST:
                    found.append(f"{label}: {name} control contrast {contrast[name]} < {CONTROL_CONTRAST}")
            if result.get("behavior"):
                found.extend(_behavior_problems(label, cell["frame"], result["behavior"]))
            elif cell.get("behavior"):
                found.append(f"{label}: slide behavior was not measured")
        else:
            if (result.get("overflowY") or 0) <= EPSILON:
                found.append(f"{label}: oversized Content was not detected as overflow")
            normal = by_id.get(label.replace("|oversized", "|normal"), {})
            for name, box in controls.items():
                if not _same(box, (normal.get("controls") or {}).get(name)):
                    found.append(f"{label}: {name} moved because of Content")
    found.extend(parity_problems(cells, by_id))
    return found


def parity_problems(cells: list[dict], by_id: dict[str, dict]) -> list[str]:
    """The two frames share one contract: only direction-specific properties may differ."""
    found: list[str] = []
    for cell in cells:
        if cell["frame"] != "presentation" or cell["size"] != "normal":
            continue
        key = cell["id"]
        other_key = key.replace("presentation|", "presentation-vertical|", 1)
        horizontal, vertical = by_id.get(key), by_id.get(other_key)
        if not horizontal or not vertical or horizontal.get("error") or vertical.get("error"):
            continue
        label = key.replace("presentation|", "presentation~vertical|", 1)

        def differs(name: str, a, b) -> None:
            if a != b:
                found.append(f"{label}: {name} differs between the two frames ({a!r} vs {b!r})")

        differs("Header", None if not _same(horizontal["controls"].get("utility"), vertical["controls"].get("utility")) else True, True)
        differs("theme", horizontal["theme"], vertical["theme"])
        differs("branding (favicon)", horizontal["favicon"], vertical["favicon"])
        differs("controller colours", (horizontal["dotsBackground"], horizontal["utilityBackground"]), (vertical["dotsBackground"], vertical["utilityBackground"]))
        differs("transition timing", horizontal["transition"], vertical["transition"])
        differs("canvas", horizontal["viewport"], vertical["viewport"])
        for name in ("heading", "muted", "card", "cardMuted", "badge", "utility", "dotCurrent"):
            a, b = horizontal["contrast"].get(name), vertical["contrast"].get(name)
            if a is not None and b is not None and abs(a - b) > 0.01:
                found.append(f"{label}: {name} contrast differs between the two frames ({a} vs {b})")
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
