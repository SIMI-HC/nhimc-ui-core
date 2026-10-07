"""Import and build the NHIMC Design Guide (single offline HTML).

  python scripts/build_design_guide.py --import-from <NhimcDesign>/.agents/skills/nhimc-worktool/docs/design-docs
      Refresh src/guide/upstream/* from the upstream Design Guide (drops the Template items).
  python scripts/build_design_guide.py
      Build guide/nhimc-design-guide.html from src/guide (Font and Logo come from the canonical assets).

The guide is adapted for NHIMC UI Core: no Template system, an install guide, a usage page and a
prompt builder that produces prompts for this project.
"""
from __future__ import annotations

import argparse
import base64
import copy
import json
from pathlib import Path
import re
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_single_html import _font_css, _upstream
from scripts.derived_frames import derive_layout
from scripts.frame_patches import apply_frame_patches

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_DIR = Path("src/guide/upstream")
OUTPUT = Path("guide/nhimc-design-guide.html")
REPO_URL = "https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/HEAD/bootstrap.md"
IMPORTED = ("design-guide.html", "design-guide.css", "design-tokens.css", "design-guide.js")


def import_upstream(root: Path, source: Path) -> None:
    target = root / UPSTREAM_DIR
    target.mkdir(parents=True, exist_ok=True)
    for name in IMPORTED:
        (target / name).write_text((source / name).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    raw = (source / "design-guide-data.js").read_text(encoding="utf-8")
    start = raw.index("Object.freeze(") + len("Object.freeze(")
    data = json.loads(raw[start : raw.rindex(")")])
    items = [item for item in data["items"] if item["type"] != "template"]
    used = {item["previewSource"] for item in items}
    data["items"] = items
    data["documents"] = {key: value for key, value in data["documents"].items() if key in used}
    data["counts"] = {key: value for key, value in data["counts"].items() if key != "template"}
    data["sources"] = [entry for entry in data["sources"] if "templates/" not in entry]
    (target / "gallery-data.json").write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8", newline="\n"
    )
    print(f"imported {len(items)} items, {len(data['documents'])} documents into {target}")


def _sub(text: str, pattern: str, replacement: str, *, count: int = 1, flags: int = re.S) -> str:
    result, made = re.subn(pattern, lambda _: replacement, text, count=count, flags=flags)
    if made < 1:
        raise ValueError(f"design guide patch did not apply: {pattern[:70]}")
    return result


def _replace(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"design guide patch did not apply: {old[:70]}")
    return text.replace(old, new)


def _data_uri(path: Path, media: str) -> str:
    return f"data:{media};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def _release_date(root: Path, version: str) -> str:
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(rf"^## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})", changelog, re.M)
    if not match:
        raise ValueError(f"CHANGELOG.md has no entry for version {version}")
    return match.group(1)


VIEW_NAV = (
    '<nav class="view-nav" id="viewNav" aria-label="화면 이동">'
    '<a href="#" data-view="gallery">Design Guide</a>'
    '<a href="#install" data-view="install">설치 가이드</a></nav>'
)


PRESENTATION_COPY = {
    "presentation": {
        "name": "PRESENTATION Frame (가로 발표)",
        "description": "가로 발표 Frame. 슬라이드가 좌우로 넘어가고 방향키는 ←/→입니다. presentation-vertical과 하나의 Presentation 공통 계약(중앙 Content, Slide animation, Controller, Theme, Header, Safe Area)을 따르며 방향만 다릅니다. AI는 Content만 작성합니다.",
    },
    "presentation-vertical": {
        "name": "PRESENTATION VERTICAL Frame (세로 발표)",
        "description": "세로 발표 Frame. 슬라이드가 위아래로 넘어가고 방향키는 ↑/↓입니다. presentation과 하나의 Presentation 공통 계약(중앙 Content, Slide animation, Controller, Theme, Header, Safe Area)을 따르며 방향만 다릅니다. AI는 Content만 작성합니다.",
    },
}


BUILDER_PROMPT_JS = """  function updateBuilderPrompt(){
    const frame=frameItems.find(item=>item.id===builderState.frame);
    const theme=builderState.theme?themeById.get(builderState.theme):null;
    const skipInstall=document.getElementById("builderSkipInstall").checked;
    const lines=[];
    if(!skipInstall){lines.push("__REPO__","이 파일만 읽고 NHIMC UI Core를 준비해줘. (git clone 금지)","준비가 끝나면 아래 조건으로 화면을 만들어줘.")}
    else{lines.push("NHIMC UI Core로 화면을 만들어줘.")}
    lines.push(`frame: ${builderState.frame||"(미선택 - AI 추천)"}${frame?` — ${frame.name}`:""}`);
    lines.push(`theme: ${builderState.theme||"(미선택 - AI 추천)"}${theme?` — ${theme.label}`:""}`);
    const requirement=builderRequirements.value.trim();
    lines.push(`requirements: ${requirement||"[여기에 원하는 화면 내용을 적어주세요]"}`);
    builderPrompt.textContent=lines.join("\\n");
    builderCopy.disabled=!(builderState.frame||builderState.theme||requirement);
  }"""

# Items this repo patches after the upstream sync; upstream's updatedAt would otherwise show a stale date.
UPDATED_AT = {
    "left": "2026-09-30T10:01:00+09:00",
    "left-blank": "2026-09-30T10:01:00+09:00",
    "top-left": "2026-10-01T16:00:00+09:00",
    "top": "2026-10-01T16:00:00+09:00",
    "blog": "2026-10-02T09:21:00+09:00",
    "left-dual": "2026-10-02T09:21:00+09:00",
    "presentation": "2026-10-02T09:21:00+09:00",
    "presentation-vertical": "2026-10-02T09:21:00+09:00",
    "Card": "2026-10-01T15:55:00+09:00",
    "Dialog": "2026-10-01T15:55:00+09:00",
    "Badge": "2026-10-01T15:55:00+09:00",
}

# Frames derived from LEFT (scripts/derived_frames.py). The Guide previews their derived layout; the item starts as a LEFT copy.
DERIVED_ITEMS = {
    "left-dual": {
        "name": "LEFT DUAL Frame",
        "title": "left-dual:v1",
        "description": "아이콘 레일(64px)과 선택한 그룹의 하위 화면 목록 패널(224px)을 나란히 두는 이중 사이드바 변형. 메뉴가 많고 2단계 구조인 리포트·관리 콘솔에 어울립니다. 1단계 메뉴가 레일, 그 하위 메뉴(children)가 패널에 나옵니다.",
        "variant": "sidebar-rail-plus-panel",
    },
}

SHOWCASE = "../../assets/components/showcase.html"
_SHOWCASE_PATCHES = (
    (
        '<div class="card"><strong>병동 운영 현황</strong><p>관련 정보를 하나의 surface에 묶습니다.</p></div>',
        '<div class="card"><strong>병동 운영 현황</strong><p>관련 정보를 하나의 surface에 묶습니다.</p></div>'
        '<div style="display:grid;gap:12px;margin-top:14px;text-align:left">'
        '<section class="card nhimc-card" data-nhimc-accent="sky"><div class="nhimc-card-head"><strong>1. 환자 정보</strong>'
        '<div class="nhimc-card-head-end"><span>필수 3건</span></div></div>'
        '<div class="nhimc-card-body"><p style="margin:0">머리와 테두리에 data-nhimc-accent 색을 입힌 ContentCard입니다.</p></div></section>'
        '<section class="card nhimc-card" data-nhimc-accent="pear"><div class="nhimc-card-head"><strong>2. 신청인</strong></div>'
        '<div class="nhimc-card-body"><p style="margin:0">sky · pear · apricot · yellow · purple · pink · amber</p></div></section></div>',
    ),
    ('<dialog class="dialog-box" aria-labelledby="dialogSpecimenTitle">', '<dialog class="dialog-box" data-nhimc-accent="sky" aria-labelledby="dialogSpecimenTitle">'),
    (
        '<span class="badge bad">오류</span></div></section>',
        '<span class="badge bad">오류</span><span class="badge" data-nhimc-accent="pink">필수</span>'
        '<span class="badge" data-nhimc-accent="pear">선택</span><span class="badge" data-nhimc-accent="sky">안내</span></div></section>',
    ),
)


def _patch_showcase(document: str, primitives_css: str, tokens_css: str) -> str:
    """Show the Core accent variants in the Card, Dialog and Badge specimens (upstream specimens carry none).

    The specimen document defines no chip colours, so the first (root) value of each chip token is copied in.
    """
    for old, new in _SHOWCASE_PATCHES:
        if document.count(old) != 1:
            raise ValueError(f"showcase patch did not apply: {old[:60]}")
        document = document.replace(old, new)
    chips = {}
    for name, value in re.findall(r"(--color-chip-[a-z]+):\s*(#[0-9a-fA-F]{6})", tokens_css):
        chips.setdefault(name, value)
    root = ":root{" + ";".join(f"{name}:{value}" for name, value in chips.items()) + "}"
    return document.replace("</head>", f"<style>{root}{primitives_css}</style></head>", 1)


def build_guide(root: Path) -> Path:
    root = root.resolve()
    upstream = root / UPSTREAM_DIR
    _, digests = _upstream(root)
    html = (upstream / "design-guide.html").read_text(encoding="utf-8")
    css = (upstream / "design-tokens.css").read_text(encoding="utf-8") + "\n" + (upstream / "design-guide.css").read_text(encoding="utf-8")
    script = (upstream / "design-guide.js").read_text(encoding="utf-8")
    gallery = json.loads((upstream / "gallery-data.json").read_text(encoding="utf-8"))
    left_item = next(item for item in gallery["items"] if item["id"] == "left")
    left_layout = gallery["documents"][left_item["source"]]
    for frame_id, copy_fields in DERIVED_ITEMS.items():
        source = f"../../assets/layouts/{frame_id}.html"
        gallery["documents"][source] = derive_layout(frame_id, left_layout, root=root)
        item = copy.deepcopy(left_item)
        item.update(
            id=frame_id, name=copy_fields["name"], title=copy_fields["title"], description=copy_fields["description"],
            source=source, previewSource=source, sourceHash=left_item["sourceHash"],
        )
        item["contract"]["variant"] = copy_fields["variant"]
        gallery["items"].append(item)
        gallery["counts"]["frame"] += 1
    gallery["documents"] = {
        key: apply_frame_patches(value) if "/layouts/" in key else value for key, value in gallery["documents"].items()
    }
    gallery["documents"][SHOWCASE] = _patch_showcase(
        gallery["documents"][SHOWCASE], (root / "src/layouts/primitives.css").read_text(encoding="utf-8"), css
    )
    for item in gallery["items"]:
        if item["id"] in PRESENTATION_COPY:
            item.update(PRESENTATION_COPY[item["id"]])
        if item["id"] == "blog":
            item["description"] = item["description"].replace("투명 SiteHeader", "반투명 SiteHeader")
        if item["id"] in UPDATED_AT:
            item["updatedAt"] = UPDATED_AT[item["id"]]
    gallery["items"].sort(key=lambda item: item["updatedAt"], reverse=True)  # newest Frame/Component first (stable)
    data = json.dumps(gallery, ensure_ascii=False, separators=(",", ":"))
    sections = (root / "src/guide/sections.html").read_text(encoding="utf-8")
    extra_css = (root / "src/guide/guide-extra.css").read_text(encoding="utf-8")
    extra_js = (root / "src/guide/guide-extra.js").read_text(encoding="utf-8")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    release_date = _release_date(root, version)
    source_base = f"https://github.com/SIMI-HC/nhimc-ui-core/blob/v{version}/"
    row = _data_uri(root / "vendor/nhimc-design/branding/brandmark-row-logo.svg", "image/svg+xml")
    solo = _data_uri(root / "vendor/nhimc-design/branding/brandmark-solo-logo-1.svg", "image/svg+xml")

    # ---- fonts: the canonical embedded Noto Sans KR only
    css = re.sub(r"@font-face\s*\{[^}]*assets/font/[^}]*\}", "", css)
    css = re.sub(r'^.*<link rel="stylesheet" href=.*\n', "", css, flags=re.M)
    if "assets/font/" in css:
        raise ValueError("design guide still references external font files")

    # ---- html
    html = _sub(html, r"<title>.*?</title>", "<title>NHIMC UI Core · Design Guide</title>")
    html = _sub(html, r'<link rel="icon"[^>]*>', f'<link rel="icon" href="{solo}">')
    html = _sub(html, r'<link rel="stylesheet" href="design-tokens.css">\s*<link rel="stylesheet" href="design-guide.css">', "")
    html = _sub(html, r'<script src="design-guide-data.js"></script>\s*<script src="design-guide.js"></script>', "")
    html = _replace(html, 'src="assets/logo/brandmark-row-logo.svg"', f'src="{row}"')
    html = _replace(html, "<small>NHIMC Design System</small>", f"<small>v{version} · 최종 업데이트 {release_date}</small>")
    html = _sub(html, r'<a class="brand" href="[^"]*"[^>]*>', '<a class="brand" href="#" aria-label="Design Guide 처음으로">')
    html = _sub(html, r'<nav class="doc-links".*?</nav>', VIEW_NAV)
    html = _replace(html, "NHIMC Design System의 Frame, Template, Component, Icon을 한눈에 확인할 수 있습니다.", "NHIMC UI Core의 Frame, Component, Icon을 한눈에 확인할 수 있습니다.")
    html = _replace(html, "프롬프트 만들기 — Layout·Theme 선택해서 바로 붙여넣을 프롬프트 추출하기", "프롬프트 만들기 — Layout·Theme 선택해서 바로 붙여넣을 프롬프트 추출하기")
    html = _replace(html, "Frame · Template · Component", "Frame · Component")
    html = _replace(html, "Layout Frame, Golden Template, 재사용 Component를 한 화면에서 확인합니다.", "Layout Frame과 재사용 Component를 한 화면에서 확인합니다.")
    html = _sub(html, r'<button type="button" class="filter" data-filter="template"[^>]*>Templates</button>\s*', "")
    html = _sub(html, r'\s*<a class="doc-inline-link"[^>]*>[^<]*</a>', "", count=20)
    html = re.sub(r"\s*·\s*(?=</p>)", "", html)
    html = _sub(
        html,
        r'<footer><a href="\.\./\.\./assets/icons/[^>]*>[^<]*</a></footer>',
        f'<footer><a href="{source_base}vendor/nhimc-design/icons/nhimc-icons.svg" target="_blank" rel="noopener">SVG 정본 보기</a></footer>',
    )
    html = _sub(
        html,
        r"Template은 참고용일 뿐이라 항상 AI 추천으로 고정됩니다\.",
        "선택한 값은 NHIMC UI Core에 그대로 전달됩니다. 선택하지 않으면 AI가 업무에 맞춰 추천합니다.",
    )
    footer = re.search(r'<footer class="builder-footer">', html)
    if not footer:
        raise ValueError("design guide patch did not apply: builder-footer")
    toggle = '<label class="builder-option-toggle"><input type="checkbox" id="builderSkipInstall"> 이 대화에 이미 설치했어요 · 설치 안내 빼기</label><p class="builder-copy-hint">아래 프롬프트를 <strong>프롬프트 복사</strong>로 복사해 AI 대화창에 그대로 붙여넣으세요. 새 대화라면 체크하지 마세요. 설치·준비 문구가 함께 들어갑니다.</p>'
    html = html[: footer.end()] + toggle + html[footer.end() :]
    hero_button = re.search(r'<button class="builder-open" id="builderOpen".*?</button>', html, re.S)
    if not hero_button:
        raise ValueError("design guide patch did not apply: builder-open")
    html = (
        html[: hero_button.start()]
        + '<div class="hero-actions">'
        + hero_button.group(0)
        + '<a class="builder-open builder-open-secondary" href="#install">설치 가이드 바로가기</a></div>'
        + html[hero_button.end() :]
    )
    html = _replace(html, '<main class="gallery-main">', '<main class="gallery-main" id="galleryView">')
    gallery_end = html.index("</main>") + len("</main>")
    html = html[:gallery_end] + "\n" + sections + "\n" + html[gallery_end:]

    for label, pattern in {
        "external stylesheet": r'<link\b[^>]*rel="stylesheet"',
        "external script": r"<script\b[^>]*\bsrc=",
        "relative asset": r'(?:src|href)="(?:assets|\.\./)',
    }.items():
        found = re.search(pattern, html)
        if found:
            raise ValueError(f"design guide contains {label}: {html[max(0, found.start() - 40):found.end() + 60]!r}")
    # ---- script
    script = _replace(script, 'const typeLabel={frame:"FRAME",template:"TEMPLATE",component:"COMPONENT",icon:"ICON"};', 'const typeLabel={frame:"FRAME",component:"COMPONENT",icon:"ICON"};')
    script = _replace(script, '["frame","template","component","icon"].map', '["frame","component","icon"].map')
    script = _replace(script, 'label:"SLOT · Template 삽입 영역"', 'label:"SLOT · Content 삽입 영역"')
    start = script.index("  function updateBuilderPrompt(){")
    end = script.index("  function openBuilderZoom")
    script = script[:start] + BUILDER_PROMPT_JS.replace("__REPO__", REPO_URL) + "\n" + script[end:]
    script = _replace(
        script,
        "builderRequirements.addEventListener(\"input\",updateBuilderPrompt);",
        "builderRequirements.addEventListener(\"input\",updateBuilderPrompt);document.getElementById(\"builderSkipInstall\").addEventListener(\"change\",updateBuilderPrompt);",
    )
    script = _replace(
        script,
        'builderCopyStatus.textContent=copied?"복사됐습니다.":"복사에 실패했습니다. 프롬프트를 직접 선택해 복사해주세요.";',
        'if(!copied&&window.nhimcSelectText)window.nhimcSelectText(builderPrompt);'
        'builderCopyStatus.textContent=copied?"복사됐습니다.":"이 환경은 복사 버튼이 막혀 있어요. 프롬프트를 선택해 두었으니 Ctrl+C(맥은 ⌘C)로 복사하세요.";',
    )
    script = _replace(
        script,
        'source.href=item.source;source.textContent="정본 열기";',
        'source.href=window.nhimcSourceUrl(item.source);source.textContent="정본 보기";',
    )
    script = script.replace("Template은 참고용일 뿐", "")

    payload = data.replace("</", "<\\/")
    body_scripts = (
        f"<script>\nwindow.NHIMC_DESIGN_GALLERY = Object.freeze({payload});\n</script>\n"
        f"<script>\n{script.replace('</script', '<\\/script')}\n</script>\n"
        f"<script>\nwindow.NHIMC_SOURCE_BASE={json.dumps(source_base)};\n{extra_js}\n</script>\n"
    )
    styles = (
        f'<meta name="nhimc-core-version" content="{version}">\n'
        f"<style>\n{_font_css(root, digests)}\n</style>\n"
        f"<style>\n{css}\n{extra_css}\n</style>\n"
    )
    html = html.replace("</head>", styles + "</head>", 1)
    html = html.replace("</body>", body_scripts + "</body>", 1)
    output = root / OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8", newline="\n")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Import and build the NHIMC Design Guide")
    parser.add_argument("--import-from", type=Path, help="upstream docs/design-docs directory")
    args = parser.parse_args()
    if args.import_from:
        import_upstream(ROOT, args.import_from)
    print(f"design guide: {build_guide(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
