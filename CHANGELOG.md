# 변경 이력

## [1.2.1] - 2026-09-29

- Web Runtime: “오프라인 HTML 저장” 버튼을 없애고, Frame이 갖춰지면 오프라인 HTML을 자동으로 저장합니다. `window.nhimcExportHtml()`은 그대로 남아 있습니다.

## [1.2.0] - 2026-09-29

- **Presentation Base Contract** (`presentation`, `presentation-vertical`, Frame 1.1.0). 두 Frame은 방향(슬라이드 이동 축, 방향키, Flow 방향)만 다르고 나머지는 같은 계약과 같은 코드를 씁니다.
  - 공통 Runtime `src/presentation/presentation-runtime.js`: 상위 정본 Presentation 스크립트(슬라이드 생명주기, transition, prev/next, 점, 키보드, 테마, 도움말)에서 방향만 매개변수로 뺀 것입니다. 이전에는 범용 Runtime이 슬라이드 animation 없이 `hidden`만 바꿔서 전환 애니메이션이 사라져 있었습니다.
  - Frame이 슬라이드 요소(`section.slide[data-screen-panel]`)를 소유합니다. 오프라인 빌더와 Web Runtime이 Content를 그 안에 넣습니다.
  - Content는 Safe Area의 시각적 중앙에 놓입니다. 정본 `.slide`(중앙 정렬 flex, transition)의 padding을 Header·Controller가 차지하는 공간으로 잡고 스크롤바 gutter를 양쪽에 예약합니다. 페이지가 위치를 보정할 필요가 없습니다.
  - Layout Primitive 추가: `PresentationContent`(자동 배치), `PresentationHero`, `PresentationFlow`. 발표용 Content 규칙(한 슬라이드 = 핵심 메시지 하나, 60~75%)을 `bootstrap.md`와 `SKILL.md`에 명시했습니다.
  - `registry/frames.json`: 공통 계약(`baseContracts.presentation`)과 두 Frame의 `extends`, `owns`(header, controller, safe area, center, transition, navigation, runtime)를 명시했습니다.
- 검증 게이트 확장: 두 Frame × light/dark × 데스크톱·900×600·좁은 세로 × 오프라인/Web Runtime 결과를 측정합니다(48칸). Safe Area 침범, 중앙 정렬, 초과 감지, 전환 클래스, prev/next·점·방향키, 두 Frame의 Header·Theme·Branding·Controller·timing 동일성, 라이트·다크 대비.
- Design Guide: 두 Presentation Frame을 가로 발표/세로 발표로 구분해 설명하고 공통 기능을 함께 보여 줍니다.

## [1.1.1] - 2026-09-29

- **PRESENTATION Frame(`presentation`, `presentation-vertical`) Content Safe Area** (Frame 1.0.1). 원인: Header(도움말·테마 버튼)와 Controller(슬라이드 점·화살표)가 전체 화면을 덮는 Content 슬롯 위에 떠 있어 AI Content가 그 아래로 들어갔습니다. `scripts/frame_patches.py`가 콘텐츠 슬롯을 컨트롤이 차지하는 공간만큼 안쪽으로 들이고(Frame 소유 CSS 변수 `--presentation-safe-*`) Content는 그 안에서만 스크롤합니다. 개별 화면에 margin/padding을 넣을 필요가 없습니다. 다른 Frame은 바뀌지 않습니다.
- Web Runtime(`dist/nhimc-web.js`)도 같은 패치를 씁니다.
- 검증: 오프라인 빌더와 Web Runtime 결과를 두 PRESENTATION Frame × light/dark × 데스크톱·좁은 세로 화면에서 측정(`scripts/presentation_safe_area.py`)하고, 지나치게 긴 Content가 Safe Area 초과로 감지되며 Header·Controller 위치는 그대로인지 확인합니다. `verify_all`과 `verify_release`에 게이트를 추가했습니다.
- 정확한 완료 검증(`build_verified_artifact`)이 Frame별 기대값을 쓰도록 고쳤습니다. 이전에는 LEFT 계열만 통과하고 top·top-left·blog·presentation은 실패했습니다. PRESENTATION 산출물은 16:9 캔버스에서 모든 페이지가 Safe Area에 들어가는지도 확인합니다.
- Design Guide: “정본 보기” 버튼(GitHub의 해당 릴리스 정본 파일)을 되살렸고, 프롬프트에서 버전 확인 문구를 뺐습니다(`bootstrap.md`가 담당).
- `bootstrap.md`: 스킬·플러그인이 등록돼 있지 않으면 사용자에게 먼저 묻고, 등록돼 있고 더 새 버전이 있으면 스킬·플러그인도 함께 업데이트합니다.

## [1.1.0] - 2026-09-29

- Web Runtime 화면 오른쪽 아래에 “오프라인 HTML 저장” 버튼을 추가했습니다. 누르면 CSS·스크립트·폰트를 모두 안에 넣은 단일 HTML 파일을 내려받으며(외부 URL·`<script src>` 없음), 인터넷 없이 열립니다. 저장 버튼은 저장된 파일에 포함되지 않습니다.
- 저장한 파일을 네트워크를 막은 브라우저에서 열어 Frame이 정상 표시되고 콘솔 오류가 없는지 테스트에 추가했습니다.

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
