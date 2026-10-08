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
    "## 등록된 아이콘",
    "## 자주 쓰는 Page 조각",
    "## BLOG Frame 스크롤 소유자",
    "## PRESENTATION Frame",
    "## Web(빌더를 실행할 수 없는 환경)",
)
HEADER = """# NHIMC UI Core 시작 (웹 채팅용)

**이 파일 하나로 충분합니다.** 다른 주소를 열 필요가 없고, 열 수 없어도 됩니다. 아래 지시를 그대로 따르세요. `git clone`과 `git pull`은 하지 않습니다.

이 파일에는 버전이 없습니다. 오래 보관된 복사본을 읽어도 틀리지 않도록, 웹 미리보기는 항상 최신 2.x 런타임(`@2`)을 불러옵니다. 이 파일은 `bootstrap.md`에서 자동으로 만든 웹 채팅용 발췌본입니다.

## 먼저 할 일: 준비 보고

사용자가 "NHIMC UI Core를 준비해줘"라고만 했다면 아래 형식으로 **5줄 이내로 짧게** 보고합니다. 점검 과정(어디서 읽었는지, 호출 한도, 인코딩 등)이나 내부 항목(`defaultFrame` 등)은 사용자가 묻기 전에는 쓰지 않습니다. 설치·등록 여부는 묻지 않습니다(웹 채팅에는 설치할 곳이 없습니다). 디자인 가이드 링크는 아래 주소 그대로 일반 텍스트로 쓰고 다른 주소로 바꾸지 않습니다.

```text
NHIMC UI Core 준비 완료
환경: <ChatGPT 웹 / Claude 웹 …> · 방식: 웹 미리보기
상태: 설치 없이 바로 사용할 수 있습니다.
디자인 가이드: https://simi-hc.github.io/nhimc-ui-core/guide/nhimc-design-guide.html
다음: 만들 화면을 말해 주세요. 예: "이송업무 관리 화면 만들어줘."
```

한계는 해당될 때만 한 줄로 덧붙입니다: 결과물은 인터넷이 필요한 Web Runtime 미리보기이고, 브라우저 검증을 거친 오프라인 `index.html`이 필요하면 Claude Code·Codex·Gemini CLI 같은 로컬 환경에서 다시 요청해야 합니다. 기본값은 Frame `top-left`, Theme `nhimc-default`입니다. 이 파일에는 버전이 없으므로 버전을 쓰지 않습니다.

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
    body = body.replace("이 규칙은 `rules/layout.md`의 자동 선택 순서(마지막 폴백 LEFT, blog 제외)보다 우선합니다(vendor 파일은 그대로 두므로 여기서 덮어씁니다), ", "")
    # a web chat cannot run the icon tool
    body = re.sub(
        r"사용자에게 알린 뒤, 승인받으면 `scripts/add_canonical_icon\.py`\([^)]*\)로 새 아이콘을 등록하고 씁니다\.",
        "그 사실을 사용자에게 알리고 목록에서 가장 가까운 것을 씁니다(웹에서는 아이콘을 추가할 수 없습니다).",
        body,
    )
    return HEADER + "\n" + body


def main() -> int:
    text = render()
    for name in OUTPUTS:
        (ROOT / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"{name}: {len(text)} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
