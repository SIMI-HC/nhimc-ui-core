# 변경 이력

## [1.4.0] - 2026-09-29

- **메뉴 id가 아이콘 이름과 같으면 아이콘이 안 보이던 결함 수정** (Frame: left 1.2.2). 원인: 여러 Page가 있는 화면에서 빌더가 각 Page를 감싸는 `<section>`에 메뉴 `id`를 그대로 HTML `id` 속성으로 썼는데(`scripts/build_single_html.py`), 아이콘 스프라이트에도 같은 이름의 `<symbol id="...">`가 있어 문서에 같은 `id`가 두 번 생겼습니다. 메뉴 아이콘의 `<use href="#id">`는 브라우저 규칙상 문서 순서상 먼저 나오는 요소(스프라이트보다 앞서 삽입되는 `<section>`)로 해석되어, `<symbol>`이 아니라 화면 Page 컨테이너를 가리키며 아이콘이 렌더되지 않았습니다. 빌더와 기존 브라우저 검증은 이 충돌을 확인하지 않아 PASS로 통과했습니다.
  - `scripts/build_single_html.py`, `scripts/canonical_frame.py`(Page 컨테이너 id, PRESENTATION 단일 슬라이드 id), `src/web/nhimc-web.template.js`(Web Runtime의 동일 로직)가 이제 실제 HTML `id`에 `screen-<메뉴id>` 네임스페이스를 씁니다. 메뉴 `href="#id"` 저작 규약과 런타임의 `[data-screen-panel]`/`[data-menu-id]` 기반 화면 전환은 그대로입니다(런타임은 `id`나 `href`로 화면을 찾지 않고 항상 이 속성들로 찾습니다).
  - `canonical_frame.render_layout()`과 Web Runtime 둘 다 최종 문서에 중복 `id`가 남아 있으면 어떤 경우든 명확한 오류로 빌드를 막습니다(이 종류의 결함 전체에 대한 이중 안전장치).
  - 회귀 테스트: `tests/python/test_single_html.py`가 기존 `tests/fixtures/authoring/multi-page/index.html`(메뉴 id·아이콘이 모두 "dashboard")로 실제 재현 조건을 검증하고, 실제 Chrome으로도 확인했습니다.
- **브라우저 검증 강화**: `scripts/verify_standalone_browser.mjs`(최종 산출물 검증)가 문서 전체의 중복 `id`와, 메뉴 아이콘의 `<use href="#...">`가 실제 `<symbol>`로 해석되고 화면에 보이는 아이콘이 0 크기가 아닌지 확인합니다(숨겨진 모바일 메뉴 사본처럼 원래 화면에 없는 아이콘은 크기 검사에서 제외). `scripts/verify_frame_render.mjs`/`scripts/frame_render.py`(left·top·top-left·blog × 테마 × 뷰포트 504칸 행렬)도 각 메뉴 아이콘이 `<symbol>`로 해석되는지 함께 측정·게이트합니다.
- **Core 아이콘 추가 절차 신설**: `vendor/nhimc-design/icons/nhimc-icons.svg`는 상위 저장소 고정 commit과 바이트 동일한 미러라 직접 편집할 수 없어, 등록되지 않은 아이콘이 필요할 때 정식 경로가 없었습니다. `scripts/icon_overlay.py`가 Core 소유 오버레이(`src/generated/icons/core-icons.svg`, 기본은 비어 있음)를 빌드 시점에 정본 스프라이트와 합칩니다(`scripts/frame_patches.py`가 Frame 동작 괴리를 다루는 것과 같은 패턴). 모든 symbol은 스타일 규격(`viewBox="0 0 24 24"`, 내부 요소에 `fill`/`stroke`를 직접 넣지 않아 공용 아이콘 래퍼의 `currentColor`를 그대로 상속, `data-label`·`data-category`·`data-updated-at` 필수)을 추가 시점과 `validate_design.py` 실행 시점 모두에서 검증하며, 벤더 아이콘과 겹치는 id는 거부합니다. `scripts/add_canonical_icon.py`가 정식 추가 절차이며, symbol 추가와 함께 `src/guide/upstream/gallery-data.json`(Design Guide 아이콘 미리보기)에도 같은 항목을 추가합니다. `registry/assets.json`에 오버레이 파일의 protected 항목을 등록했습니다.
- `bootstrap.md`·`SKILL.md`: 메뉴 id를 아이콘 이름과 겹치지 않게 짓도록 안내하고(구조적으로는 이제 겹쳐도 깨지지 않지만 명확성을 위해 권장), 맞는 아이콘이 없으면 임의로 비슷한 아이콘을 쓰지 말고 사용자에게 알린 뒤 승인받아 Core 아이콘 추가 절차로 추가하도록 명시했습니다.

## [1.3.2] - 2026-09-29

- **도움말 패널·모바일 메뉴가 바깥 클릭으로 닫히지 않던 결함 수정** (Frame: left·left-blank·top-left 1.2.0, top 1.3.0, blog 1.4.0). 원인: 실제 빌드에 들어가는 `src/generated/frame/frame-runtime.js`에 바깥 클릭 처리가 없었습니다(정본 Frame 인라인 스크립트에는 있지만 빌드는 그 스크립트를 이 런타임으로 교체합니다). 그래서 X 버튼과 Esc만 닫혔습니다. 이제 도움말·모바일 dialog는 패널 밖(backdrop) 클릭 시 닫히고, TOP·BLOG의 `.nav-backdrop` 클릭은 `nav-open`을 해제하고 메뉴 버튼의 `aria-expanded`를 `false`로 되돌립니다. Web Runtime(`dist/nhimc-web.js`)에도 같이 들어갑니다.
  - 회귀 테스트: `scripts/outside_click.py`(`run_browser_tests.py --outside-click-only`, `verify_all`, `verify_release`)가 left·left-blank·top·top-left·blog에서 실제 마우스 클릭으로 도움말 열기 → 안쪽 클릭(유지) → 바깥 클릭(닫힘), 390px에서 메뉴 열기 → 바깥/backdrop 클릭 → 닫힘·`aria-expanded` 복귀를 확인합니다. 수정 전 런타임에서는 5개 Frame 모두 실패합니다.
- **최종 산출물은 `index.html` 하나만 남기기**: 저작 원본(`source.html`)을 사용자 프로젝트 폴더의 결과물 옆에 저장하던 문제. `SKILL.md`(필수 순서 6번, “전달 경계”)와 `bootstrap.md`(“기본 산출물 계약”, “웹에서 URL 없는 완성 HTML”)에 원본은 임시 위치(Claude Code: 세션 scratchpad 또는 OS 임시 폴더)에 두고 `--input`만 임시 경로, `--output`만 사용자 폴더의 `index.html`로 주며, 빌드 뒤 출력 폴더에 다른 파일이 있으면 삭제하거나 임시 위치로 옮기고, 사용자가 “원본도 보관해줘”라고 명시할 때만 원본을 출력 폴더에 두며, 결과 보고에는 `index.html` 경로만 쓴다고 명시했습니다. `build_verified_artifact.py`는 출력 폴더에 `index.html` 외 항목이 있으면 stderr로 경고합니다(자동 삭제 없음).
- **플러그인을 이미 설치했는데도 AI가 저장소를 작업 폴더에 클론하던 문제 수정** (`bootstrap.md` “준비 절차”, `SKILL.md` “준비 절차 요약”). 플러그인 캐시에 저장소 전체(registry·scripts·guide·SKILL·vendor)가 들어 있어 클론은 불필요하고 작업 폴더만 어지러워졌습니다.
  - `git clone`/`git pull`은 **스킬·플러그인이 설치돼 있지 않을 때만** 합니다(2단계, “웹에서 URL 없는 완성 HTML” 1단계).
  - 플러그인이 설치돼 있으면 클론하지 않고 원격 raw `VERSION`만 읽어 비교하며, registry·scripts·guide·SKILL은 플러그인 설치 경로 `<루트>`(Claude Code: `~/.claude/plugins/cache/<마켓플레이스>/nhimc-worktool/<버전>/`)에서 읽습니다. 빌더도 설치 경로의 `scripts/`를 실행하고 결과물만 작업 폴더에 둡니다.
  - 새 버전이면 업데이트 여부를 먼저 묻고, 승인하면 공식 경로(Claude Code: `claude plugin marketplace update` + `claude plugin update`)로 갱신합니다. 클론으로 대신하지 않습니다.
  - Design Guide도 클론이 아니라 `<루트>/guide/nhimc-design-guide.html`을 엽니다.
  - “사본이 남아 있어도 1~5를 생략하지 않는다”는 문구는 유지하되, 사본에 플러그인 설치본(플러그인 캐시)을 포함한다고 명시했습니다.

## [1.3.1] - 2026-09-29

- **일산병원 로고의 흰색 테두리(타일) 제거** (Frame: left·left-blank·top-left 1.1.0, top 1.2.0, blog 1.3.0). 로고 뒤 흰색 둥근 배경, 안쪽 여백(3px 5px), 그림자, 모서리 반경을 모두 없애 로고 그림 그대로 보입니다. 펼친 가로 로고와 접힌 레일의 단독형 마크 모두 적용됩니다. 벤더 미러는 그대로 두고 `scripts/frame_patches.py`가 오프라인 빌더·Web Runtime·Design Guide에 공통 적용합니다. 로고 크기는 타일 안쪽 여백만큼(높이 36px 안에서 30px → 36px) 커집니다.
- 타일을 없애자 라이트 테마의 남색 사이드바에서 로고의 남색 블록이 배경에 묻혀 경계가 안 보였습니다. 흰 선 대신 LEFT·LEFT BLANK 사이드바 로고 뒤에 사이드바 토큰 `--color-sidebar-brand-18`의 반투명 패널(활성 메뉴 행과 같은 옅은 면)을 사방 패딩 3px, 모서리 3px로 깔았습니다. 흰색이 아니고 라이트·다크 모두 같은 토큰으로 자동 전환됩니다. LEFT BLANK를 접은 레일은 정본 그대로(접기 버튼만, 로고 마크 없음)입니다.

## [1.3.0] - 2026-09-29

- **로컬 빌더·Web Runtime Frame 렌더링 결함 수정** (Frame: blog 1.2.0, top 1.1.0).
  - 테마 색이 적용되지 않던 문제: `[data-theme-color="pear"]` 등 Theme 덮어쓰기 CSS가 `<head>` 맨 앞에 들어가 Frame 자체의 `[data-theme="light"]{--color-primary:#003d94…}`(같은 우선순위, 나중 것이 이김)에 덮였습니다. 라이트 모드에서 mint·pear·apricot·neutral이 모두 남색으로 나왔고 **로컬 빌더와 Web Runtime 두 경로 모두, 모든 Frame**에서 같았습니다(다크는 선택자가 더 구체적이라 정상). Theme 덮어쓰기를 `</head>` 직전의 별도 `<style data-nhimc-theme-color-bundle>`로 옮겼습니다(`build_single_html.py`, `build_web_runtime.py`, `nhimc-web.template.js`).
  - 메뉴 아이콘이 크게 렌더되던 문제: BLOG 헤더 메뉴에는 svg 크기 규칙이 없어(TOP은 17px) 1440px에서 56px로 라벨을 덮었고, BLOG·TOP의 모바일 Drawer 메뉴 아이콘도 크기 규칙이 없어 열면 184px였습니다. `scripts/frame_patches.py`가 BLOG 헤더 아이콘(17px, 라벨 옆)과 BLOG·TOP Drawer 아이콘(18px)을 정합니다. `.topnav button span.label{display:none}`(1024px 미만 아이콘 모드)은 TOP과 같은 의도이며, 아이콘만 남는 메뉴 버튼이 이름을 잃지 않도록 메뉴 버튼에 `aria-label`·`title`을 넣었습니다.
  - 검증: `scripts/frame_render.py`가 모든 Frame × Theme 6종 × 라이트/다크 × 1440/768/375px × 로컬 빌더/Web Runtime = 504칸에서 계산된 `--color-primary`·주요 Button 색, 메뉴 아이콘 크기·라벨 겹침·접근 가능한 이름, 가로 스크롤을 측정합니다(`--frame-render-only`, `verify_all`, `verify_release`). 완료 검증(`verify_standalone_browser.mjs`)도 선택한 테마의 `--color-primary`와 메뉴 아이콘 상한(24px)을 확인하므로, 예전처럼 PASS인데 화면이 깨진 산출물이 나오지 않습니다.
- Marketplace 등록 파일 추가: `.claude-plugin/marketplace.json`(Claude Code)과 `.agents/plugins/marketplace.json`(Codex). 저장소에 마켓플레이스 파일이 없어 `marketplace add`가 404 / "Marketplace file not found"로 실패하던 문제입니다.

- **BLOG Frame 스크롤 소유자** (`blog`, Frame 1.1.0). 원인: BLOG 헤더의 투명은 테마 블록의 `background-color: transparent !important`로만 유지되어, 문서 스크롤 화면에서 헤더를 sticky로 바꾸면 투명한 채 콘텐츠와 겹쳤습니다. `scripts/frame_patches.py` 1.2.0이 스크롤 소유자를 BLOG Frame 안의 상태(`<html data-scroll-owner="main|document">`)로 추가했습니다. 새 Layout variant는 만들지 않았습니다.
  - `main`(기본): app-shell `100svh`, SiteHeader `flex:none`, Main(`.content`)만 스크롤하고 헤더는 투명을 유지합니다.
  - `document`: 문서가 스크롤하고 SiteHeader는 sticky + 불투명(`--color-background`) + `--color-border-accent` 하단 경계 + 정본 `--shadow-lg`입니다. 앵커는 `scroll-margin-top`으로 헤더를 피합니다. 모바일 Drawer(z-index 10)는 헤더(8) 위에 그대로 열립니다.
  - `!important` 투명 강제 규칙(`.site-header`, `.statusbar`)을 제거하고 헤더 배경은 토큰 `--site-header-surface`로 제어합니다. `<header>`에 카드 surface를 강제하던 규칙은 `header:not(.site-header)`로 한정해 도움말 Dialog 헤더는 그대로입니다.
  - 선택은 `<html data-scroll-owner>` 또는 `<nhimc-frame data-scroll-owner>`이며 BLOG 외 Frame은 `document`를 거부합니다. `:has()`를 쓰지 않아 구형 Edge에서도 동작합니다.
  - 검증: `scripts/blog_scroll_owner.py`가 main/document × light/dark × 375/768/1440px × 오프라인/Web Runtime 24칸에서 긴 콘텐츠를 실제로 스크롤해 헤더 고정·불투명·겹침·앵커·모바일 메뉴·도움말·가로 스크롤을 측정합니다. `verify_all`, `verify_release`에 게이트를 추가했고 회귀 테스트는 `tests/python/test_blog_scroll_owner.py`입니다.
  - vendor(`vendor/nhimc-design`)는 바이트 동일 미러라 고치지 않았습니다. 상위 catalog·layout 규칙 문서에는 이 상태가 없으므로 NhimcDesign 정본에 반영될 때까지 Core 문서(`bootstrap.md`, `SKILL.md`, Design Guide)가 기준입니다.

## [1.2.2] - 2026-09-29

- Web Runtime: 1.2.1에서 넣은 "Frame이 갖춰지면 오프라인 HTML을 자동 저장" 동작을 되돌렸습니다. 페이지를 열거나 새로고침할 때마다 파일이 반복해서 다운로드되는 문제가 있었습니다. 이제 Web Runtime은 순수 미리보기이며 아무 것도 자동으로 저장하지 않습니다. `window.nhimcExportHtml()`은 도구용으로 남아 있습니다. 외부 링크 없는 진짜 오프라인 파일은 로컬 환경(Claude Code · Codex · Gemini CLI)에서 `build_verified_artifact.py` / `build_single_html.py`로 만듭니다.

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
