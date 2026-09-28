# 변경 이력

## [1.0.1] - 2026-09-28

- Web Runtime의 “CSS가 늦게 로드되는 것처럼 보이는” 현상을 고쳤습니다. 원인은 3MB짜리 스크립트가 다 내려받아질 때까지 스타일 없는 Content가 먼저 보였기 때문입니다.
  - 폰트를 base64로 넣지 않고 같은 검증된 파일을 CDN URL로 불러오도록 해 스크립트를 3.1MB에서 0.9MB(압축 전송 약 0.3MB)로 줄였고, 폰트는 스크립트와 병렬로 미리 받기 시작합니다.
  - Frame이 씌워지기 전에는 페이지를 숨기고(`visibility:hidden`) 씌운 뒤 보여 주며, 오류가 나도 반드시 다시 보이게 합니다.
  - `<script src>`는 `<head>`에 두도록 안내를 바꿨습니다.
- 오프라인 `index.html`은 그대로 폰트를 안에 포함합니다(인터넷 없이 열림).

## [1.0.0] - 2026-09-28

첫 공개 릴리스입니다. NhimcDesign(NHIMC Worktool)을 GitHub로 옮긴 프로젝트이며 플러그인·스킬 이름은 기존과 같은 `nhimc-worktool`입니다.

- 정본 Frame 7종(left, left-blank, top, top-left, presentation, presentation-vertical, blog), Theme(light/dark + color 5종), Component 49종, 일산병원 로고·아이콘·Noto Sans KR을 정본 스냅샷(NhimcDesign `v1.3.29`, 커밋 `08c45402eece`)에서 가져와 고정했습니다.
- Template 없이 등록 Component와 Layout Primitive(Page, PageHeader, Section, Stack, Grid, FormGrid, Toolbar, FieldGroup, ContentCard)로 Content를 조합합니다. 메뉴와 Page는 AI가 정합니다.
- 일산병원 로고 타일(흰색 테두리) 모서리 반경은 8px입니다. 벤더 미러는 그대로 두고 `scripts/frame_patches.py` 한 곳에서 오프라인 빌더, Web Runtime, Design Guide 미리보기에 같은 패치를 적용합니다.
- 오프라인 빌더(`scripts/build_verified_artifact.py`)가 브라우저 검증을 거친 단일 `index.html`을 전달합니다.
- Web Runtime(`dist/nhimc-web.js`)으로 빌더를 실행할 수 없는 웹 AI도 Content와 `<script src>` 한 줄로 프롬프트 안에서 화면을 완성합니다(인터넷 필요).
- Design Guide(`guide/nhimc-design-guide.html`): 설치 가이드, 사용법, 프롬프트 만들기(`frame:` / `theme:` / `requirements:`), Frame·Component·Icon 미리보기. 복사가 막힌 환경에서는 프롬프트를 선택해 Ctrl+C로 복사하게 합니다.
- `bootstrap.md` 하나가 6개 환경(ChatGPT Web · Claude Web · Gemini Web · Codex · Claude Code · Gemini CLI)의 진입점입니다. 남아 있는 사본이 있어도 원격 `VERSION`과 비교해 최신일 때만 재준비를 생략합니다.
- 라이선스: 재배포·수정 금지(사용 허가만). 자세한 내용은 `LICENSE`를 참고하세요.
