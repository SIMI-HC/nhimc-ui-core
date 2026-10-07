"""Generate NHIMC.md and START.md: the web-chat edition of bootstrap.md.

A web chat (the free plans in particular) can open only the one URL the user pasted, so a pointer file that says "now read
bootstrap.md" cannot work there. These files carry everything a web chat needs in one read. They contain no version number: a
copy that a service keeps for days is still correct, and the Web Runtime they use is the major range (@2), which is always current.
Edit bootstrap.md, then run `python scripts/build_start_md.py`; a test fails while the files are stale.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ("NHIMC.md", "START.md")
# bootstrap.md sections that a web chat needs, in this order
SECTIONS = (
    "## 프롬프트 힌트 해석",
    "## 메뉴와 Page는 AI가 정합니다",
    "## 자주 쓰는 Page 조각",
    "## BLOG Frame 스크롤 소유자",
    "## PRESENTATION Frame",
    "## Web(빌더를 실행할 수 없는 환경)",
)
HEADER = """# NHIMC UI Core 시작 (웹 채팅용)

**이 파일 하나로 충분합니다.** 다른 주소를 열 필요가 없고, 열 수 없어도 됩니다. 아래 지시를 그대로 따르세요. `git clone`과 `git pull`은 하지 않습니다.

이 파일에는 버전이 없습니다. 오래 보관된 복사본을 읽어도 틀리지 않도록, 웹 미리보기는 항상 최신 2.x 런타임(`@2`)을 불러옵니다. 이 파일은 `bootstrap.md`에서 자동으로 만든 웹 채팅용 발췌본입니다.

## 먼저 할 일: 준비 보고

사용자가 "NHIMC UI Core를 준비해줘"라고만 했다면 아래 항목을 짧게 보고하고, 이어서 "이송업무 관리 화면 만들어줘"처럼 만들 화면을 말해 달라고 안내합니다. 설치·등록 여부는 묻지 않습니다(웹 채팅에는 설치할 곳이 없습니다).

- platform: 지금 환경(예: ChatGPT 웹, Claude 웹)
- installationMode: `WEB_BOOTSTRAP` (context-only, 웹 미리보기 방식)
- defaultFrame: `top-left`, defaultTheme: `nhimc-default`
- 버전: 이 파일은 버전이 없으므로 `확인 못함`이라고 씁니다.
- 한계: 결과물은 인터넷이 필요한 Web Runtime 미리보기입니다. 브라우저 검증을 거친 오프라인 `index.html`이 필요하면 Claude Code·Codex·Gemini CLI 같은 로컬 환경에서 다시 요청해야 합니다.

코드 실행(셸)이 있고 github.com에 접근할 수 있는 환경(Claude Code·Codex 등)에서는 사용자의 \"이 파일만 읽고\"와 어긋나지 않게, 이 파일이 직접 안내하는 대로 이 발췌본 대신 전체 지침을 따릅니다. `git ls-remote --tags --sort=-v:refname https://github.com/SIMI-HC/nhimc-ui-core.git "v*"`(클론 아님)의 맨 위 태그가 최신 릴리스이고, `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/<태그>/bootstrap.md`가 내용이 바뀌지 않는 전체 지침입니다.
"""


def render(root: Path = ROOT) -> str:
    parts = re.split(r"(?m)^(?=## )", (root / "bootstrap.md").read_text(encoding="utf-8").replace("\r\n", "\n"))
    chosen = []
    for prefix in SECTIONS:
        match = [part for part in parts if part.startswith(prefix)]
        if len(match) != 1:
            raise ValueError(f"bootstrap.md must have exactly one section starting with {prefix!r}")
        chosen.append(match[0].rstrip() + "\n")
    body = "\n".join(chosen)
    body = re.sub(r", Frame \d+\.\d+\.\d+", "", body)  # a frame version in a heading is a version number
    body = body.replace("위 “코드 실행이 되는 경우” 절차로", "로컬 빌더(`scripts/build_verified_artifact.py`)로")
    # a web chat cannot open the icon sprite or run the icon tool, so the file lists the registered names itself
    body = body.replace("`vendor/nhimc-design/icons/nhimc-icons.svg`에 있는 이름만", "아래 “등록된 아이콘” 목록에 있는 이름만")
    body = re.sub(
        r"사용자에게 알린 뒤, 승인받으면 `scripts/add_canonical_icon\.py`\([^)]*\)로 새 아이콘을 등록하고 씁니다\.",
        "그 사실을 사용자에게 알리고 목록에서 가장 가까운 것을 씁니다(웹에서는 아이콘을 추가할 수 없습니다).",
        body,
    )
    sprite = (root / "vendor/nhimc-design/icons/nhimc-icons.svg").read_text(encoding="utf-8")
    names = re.findall(r'<symbol[^>]*\bid="([^"]+)"', sprite)
    icons = "## 등록된 아이콘 (메뉴 `icon`에는 이 이름만)\n\n" + " ".join(f"`{name}`" for name in names) + "\n"
    return HEADER + "\n" + body.replace("## 자주 쓰는 Page 조각", icons + "\n## 자주 쓰는 Page 조각", 1)


def main() -> int:
    text = render()
    for name in OUTPUTS:
        (ROOT / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"{name}: {len(text)} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
