# NHIMC UI Core 시작 (웹 채팅용)

**이 파일 하나로 충분합니다.** 다른 주소를 열 필요가 없고, 열 수 없어도 됩니다. 아래 지시를 그대로 따르세요. `git clone`과 `git pull`은 하지 않습니다.

이 파일에는 버전이 없습니다. 오래 보관된 복사본을 읽어도 틀리지 않도록, 웹 미리보기는 항상 최신 2.x 런타임(`@2`)을 불러옵니다. 이 파일은 `bootstrap.md`에서 자동으로 만든 웹 채팅용 발췌본입니다.

## 먼저 할 일: 준비 보고

사용자가 "NHIMC UI Core를 준비해줘"라고만 했다면 아래 항목을 짧게 보고하고, 이어서 "이송업무 관리 화면 만들어줘"처럼 만들 화면을 말해 달라고 안내합니다. 설치·등록 여부는 묻지 않습니다(웹 채팅에는 설치할 곳이 없습니다).

- platform: 지금 환경(예: ChatGPT 웹, Claude 웹)
- installationMode: `WEB_BOOTSTRAP` (context-only, 웹 미리보기 방식)
- defaultFrame: `top-left`, defaultTheme: `nhimc-default`
- 버전: 이 파일은 버전이 없으므로 `확인 못함`이라고 씁니다.
- 한계: 결과물은 인터넷이 필요한 Web Runtime 미리보기입니다. 브라우저 검증을 거친 오프라인 `index.html`이 필요하면 Claude Code·Codex·Gemini CLI 같은 로컬 환경에서 다시 요청해야 합니다.

코드 실행(셸)이 있고 github.com에 접근할 수 있는 환경(Claude Code·Codex 등)에서는 사용자의 "이 파일만 읽고"와 어긋나지 않게, 이 파일이 직접 안내하는 대로 이 발췌본 대신 전체 지침을 따릅니다. `git ls-remote --tags --sort=-v:refname https://github.com/SIMI-HC/nhimc-ui-core.git "v*"`(클론 아님)의 맨 위 태그가 최신 릴리스이고, `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/<태그>/bootstrap.md`가 내용이 바뀌지 않는 전체 지침입니다.

## 프롬프트 힌트 해석

사용자 요청에 다음 줄이 있으면(Design Guide의 “프롬프트 만들기” 결과) 그대로 따릅니다. 값 뒤의 ` — 이름`은 설명이므로 무시하고 첫 토큰만 id로 씁니다.

- `frame: <id>` → 저작 원본 `<html data-frame="<id>">` (`left`, `left-blank`, `left-dual`, `top`, `top-left`, `presentation`, `presentation-vertical`, `blog`). `frame:` 줄이 없으면 `(미선택 - AI 추천)`과 똑같이 취급해, 업무에 맞춰 AI가 고릅니다. 단 AI 추천은 `left`/`left-blank`를 고르지 않고 `top-left`(=DEFAULT Frame)·`top` 중에서 고르며(애매하면 `top-left`), 소식·콘텐츠형 화면이면 `blog`도 가능합니다. `left-dual`(아이콘 레일+하위 메뉴 패널을 둔 2단계 메뉴용 LEFT)도 후보지만 가장 후순위입니다 — 메뉴가 2단계이고 하위 화면이 많아 `top-left`·`top`으로 담기 어려울 때만 고릅니다. `presentation`/`presentation-vertical`은 PPT·발표·슬라이드용일 때만 고릅니다. `nhimc-default`는 레지스트리 내부 id일 뿐이며 `frame:` 값으로 쓰지 않습니다 — 사용자가 "디폴트로 해줘"라고 명시하면 `left`를 뜻합니다.
- `scroll-owner: <main|document>` → BLOG 전용. `<html data-scroll-owner="document">`. 없으면 `main`. 아래 “BLOG Frame 스크롤 소유자” 참고.
- `theme: <id>` → `<html data-theme-color="<id>">` (`nhimc-default`, `mint`, `pear`, `apricot`, `neutral`, `color-mix`). 라이트/다크는 `data-theme="light|dark"`.
- `requirements: …` → 화면 요구사항. 메뉴와 Page 구성은 이 내용에서 AI가 판단합니다.
- 값이 `(미선택 - AI 추천)`이면 업무에 맞춰 AI가 고릅니다. `frame:` 줄을 생략했을 때도 같습니다. `theme:` 줄을 생략하면 기본 테마 `nhimc-default`(NHIMC 기본)를 씁니다.

## 메뉴와 Page는 AI가 정합니다

Frame은 그대로 복사되고, AI는 **메뉴 JSON**과 **Page(Content)** 두 영역만 채웁니다.

1. 업무 요구를 보고 필요한 메뉴와 Page 수를 판단합니다. 메뉴는 `<script type="application/json" data-nhimc-menu>[{"id":"items","label":"품목 관리","icon":"hospital","href":"#items"}]</script>` 형식이며 그룹은 `children`(최대 3단)으로 표현합니다. `icon`은 아래 “등록된 아이콘” 목록에 있는 이름만 씁니다(`dashboard`, `list`, `users`, `settings`, `calendar`, `bar-chart`, `hospital`, `ambulance` 등). 메뉴 `id`는 될 수 있으면 아이콘 이름과 겹치지 않게 짓습니다(빌더가 이 둘을 서로 다른 네임스페이스로 렌더링하므로 겹쳐도 깨지지는 않지만, 겹치지 않는 편이 더 명확합니다). 업무에 맞는 아이콘이 등록 목록에 없으면 비슷한 다른 아이콘으로 임의 대체하지 말고 그 사실을 사용자에게 알리고 목록에서 가장 가까운 것을 씁니다(웹에서는 아이콘을 추가할 수 없습니다).
2. 메뉴 항목마다 Page 하나를 같은 순서로 만듭니다. `id`와 `href="#id"`가 일치해야 합니다.
3. Page가 하나면 `<main data-nhimc-role="content">…</main>` 하나만 둡니다. 둘 이상이면 각각 `<section data-screen-panel="메뉴id"><main data-nhimc-role="content">…</main></section>`로 감쌉니다. 메뉴 클릭 시 화면 전환과 현재 메뉴 표시는 Frame이 처리하므로 직접 만들지 않습니다.
4. 각 Page는 등록 Component와 Layout Primitive(`nhimc-page-header`, `nhimc-toolbar`, `nhimc-grid`, `nhimc-form-grid`, `nhimc-card`, …)만으로 채웁니다. Page마다 구성(검색·표·카드·폼·차트·탭)은 자유입니다.

## 등록된 아이콘 (메뉴 `icon`에는 이 이름만)

`menu` `panel-left` `home` `dashboard` `grid` `list` `more-horizontal` `more-vertical` `chevron-left` `chevron-right` `chevron-up` `chevron-down` `arrow-left` `arrow-right` `arrow-up` `arrow-down` `expand` `collapse` `plus` `minus` `x` `check` `search` `filter` `refresh` `undo` `redo` `edit` `trash` `copy` `save` `download` `upload` `file` `file-text` `folder` `folder-open` `archive` `printer` `paperclip` `image` `user` `users` `user-plus` `user-check` `badge-id` `lock` `unlock` `key` `shield` `shield-check` `eye` `eye-off` `settings` `sliders` `power` `log-in` `log-out` `help-circle` `info` `check-circle` `x-circle` `alert-circle` `alert-triangle` `bell` `bell-off` `clock` `calendar` `calendar-check` `history` `timer` `mail` `send` `message` `phone` `megaphone` `link` `external-link` `building` `hospital` `stethoscope` `heart-pulse` `activity` `pill` `syringe` `flask` `thermometer` `bed` `ambulance` `clipboard` `clipboard-list` `table` `database` `bar-chart` `line-chart` `pie-chart` `trend-up` `trend-down` `wifi` `server` `monitor` `smartphone` `sun` `moon` `palette` `star` `bookmark` `tag` `map-pin` `briefcase` `award` `flag` `ban`

## 자주 쓰는 Page 조각 (복사해서 값만 바꿉니다)

목록 Page의 표 카드는 이 구조를 그대로 씁니다. 페이지 이동은 반드시 `nav.pages`(정본 Pagination)를 쓰고, 버튼에 `btn` 클래스를 직접 붙이지 않습니다.

```html
<section class="card nhimc-card" data-nhimc-component="ContentCard">
  <div class="nhimc-card-head"><strong>이송 요청 목록</strong>
    <div class="nhimc-card-head-end"><span>총 37건</span><button class="btn" type="button" data-nhimc-component="Button">새로고침</button></div>
  </div>
  <div class="nhimc-scroll"><table data-nhimc-component="Table" aria-label="이송 요청 목록">…</table></div>
  <div class="nhimc-pagination" data-nhimc-role="pagination" data-nhimc-component="PaginationArea">
    <nav class="pages" data-nhimc-component="Pagination" aria-label="페이지 이동"><button type="button" aria-label="이전 페이지">이전</button><button type="button" class="on" aria-current="page">1</button><button type="button">2</button><button type="button" aria-label="다음 페이지">다음</button></nav>
  </div>
</section>
```

- 제목과 건수·버튼이 한 줄이면 `nhimc-card-head`(카드 안) 또는 `nhimc-toolbar`+`nhimc-toolbar-end`(카드 밖)를 씁니다. 직접 `display:flex`를 쓰지 않습니다.
- 구역을 색으로 구분하려면 `<section class="card nhimc-card" data-nhimc-accent="sky">`처럼 속성 하나만 붙입니다(`sky`·`pear`·`apricot`·`yellow`·`purple`·`pink`·`amber`). 카드 머리와 테두리, `<dialog class="dialog-box">`의 머리, `badge`(필수·선택 표시)에 같은 방식으로 쓰며 `style="background:…"` 인라인 색은 쓰지 않습니다. 분류용 강조일 뿐 주요 버튼은 계속 `btn primary`입니다. `purple`·`pink`·`amber`는 `theme: color-mix`에서만 고유 색이고, 다른 테마에서는 `sky`·`apricot`·`yellow` 색으로 대신 보입니다.
- 상태 표시는 `badge ok|warn|bad`, 버튼은 `btn primary|ghost|ghost-subtle`, 검색 필드는 `label.field`입니다.
- `nhimc-scroll` 안 `table`의 최소 너비는 기본이 컨테이너 폭(`--table-min: 100%`)입니다. 열이 많아 넓게 둬야 하면 `<div class="nhimc-scroll" style="--table-min:640px">`처럼 지정합니다(`nhimc-grid`의 `--grid-min`과 같은 방식). 짧은 표를 좁은 카드에 넣을 때 불필요한 가로 스크롤이 생기지 않도록 지정하지 않은 기본값을 그대로 둡니다.

화면 위쪽의 제목 줄·검색 조건·핵심 수치는 아래 조각을 그대로 씁니다. **클래스를 새로 만들지 않습니다.**

```html
<div class="nhimc-page-header">
  <div><h1>이송 현황</h1><p>오늘 접수된 이송 요청을 조회합니다.</p></div>
  <div class="nhimc-actions"><button class="btn primary" type="button" data-nhimc-component="Button">이송 요청 등록</button></div>
</div>

<section class="card nhimc-card" data-nhimc-component="ContentCard SearchFilter">
  <div class="nhimc-card-head"><strong>조회 조건</strong></div>
  <div class="nhimc-card-body">
    <div class="nhimc-toolbar">
      <label class="field"><span>이송일</span><input type="date"></label>
      <label class="field"><span>환자명</span><input type="text" placeholder="환자명 입력"></label>
      <label class="field"><span>이송상태</span><select><option>전체</option><option>대기</option><option>완료</option></select></label>
      <div class="nhimc-toolbar-end"><button class="btn ghost" type="button" data-nhimc-component="Button">초기화</button><button class="btn primary" type="button" data-nhimc-component="Button">조회</button></div>
    </div>
  </div>
</section>

<div class="nhimc-grid nhimc-stat-grid">
  <section class="card nhimc-card nhimc-stat" data-nhimc-accent="sky" data-nhimc-component="Stat">
    <div class="nhimc-card-head"><strong>전체 요청</strong></div>
    <div class="nhimc-card-body nhimc-stat-body"><p class="nhimc-stat-value">37<span class="nhimc-stat-unit">건</span></p><small class="nhimc-stat-note">오늘 접수</small></div>
  </section>
</div>
```

- **클래스는 한 묶음입니다. 조각의 클래스를 줄이거나 바꾸지 않습니다.** 카드는 항상 `card nhimc-card`, 버튼은 항상 `btn`(강조는 `btn primary`), 입력은 `label.field`, 핵심 수치 격자는 `nhimc-grid nhimc-stat-grid`입니다. 한쪽만 쓰면 테두리·배경·버튼 모양이 빠져 밋밋하게 나옵니다.
- 핵심 수치 카드(MetricOverview)는 위 `nhimc-stat` 조각만 씁니다(2~4개를 `nhimc-grid nhimc-stat-grid`에 나란히). `.metric`·`.metrics`처럼 클래스를 지어내면 스타일이 없어 글자가 붙어 보이고, 빌더는 거부하며 웹 미리보기는 경고를 띄웁니다. 카드 안 본문은 `nhimc-card-body`에 넣습니다.
- 검색 조건은 `nhimc-toolbar` 안에 `label.field`를 나란히 두고 버튼은 `nhimc-toolbar-end`로 오른쪽에 둡니다(`nhimc-form-grid`는 여러 줄짜리 입력 폼용입니다). 제목 줄의 버튼은 `nhimc-page-header` 안의 `nhimc-actions`입니다.
- 표의 칸은 줄바꿈하지 않고 표가 `nhimc-scroll` 안에서 가로로 스크롤됩니다. 설명처럼 긴 글을 줄바꿈해야 하는 칸에만 `class="nhimc-wrap"`을 붙입니다.
- 등록되지 않은 CSS 클래스는 쓰지 않습니다. 자주 틀리는 것: `card-head`→`nhimc-card-head`, `fields`→`nhimc-toolbar`, `actions`→`nhimc-actions`, `table-wrap`→`nhimc-scroll`, `title`→`nhimc-page-header`, `badge warning`·`badge secondary`→`badge warn`·`ok`·`bad`.

## BLOG Frame 스크롤 소유자 (`blog`)

스크롤 소유자는 새 Layout이 아니라 **BLOG Frame 안의 상태**입니다. `<html data-scroll-owner="main|document">`(웹 실행은 `<nhimc-frame data-scroll-owner>`도 가능)로 고르고, 없으면 `main`입니다.

- `main`(기본): app-shell은 `100svh`, SiteHeader는 `flex:none`(sticky 아님, 반투명), **Main(`.content`)만 스크롤**합니다.
- `document`: 문서 전체가 스크롤합니다. SiteHeader는 sticky로 바뀌고 **반투명 + blur**(`--site-header-surface` 캔버스색(`#f4f7fa`/`#0a0a0a`) 40% 불투명 + `backdrop-filter: blur(12px)`, `border-bottom: 1px solid var(--color-border-accent)`, 정본 `--shadow-lg`)입니다. sticky + 완전 투명 조합은 만들지 않습니다.
- 앵커(`#id`)는 sticky 헤더 높이를 반영한 `scroll-margin-top`으로 이동합니다. 페이지에서 따로 보정하지 않습니다.
- 헤더 색은 `!important`가 아니라 토큰(`--site-header-surface`)으로 제어합니다. 로고·내비게이션·도움말·모바일 메뉴·Footer는 두 상태에서 같습니다.
- 소유자 전환은 `document.documentElement.dataset.scrollOwner`만 바꾸면 됩니다.

## PRESENTATION Frame (`presentation`, `presentation-vertical`) — 공통 계약

`presentation`(가로 발표)과 `presentation-vertical`(세로 발표)은 **방향만 다르고 하나의 Presentation Base Contract를 따릅니다.** 공통 Runtime(`src/presentation/presentation-runtime.js`)과 Frame 패치(`scripts/frame_patches.py`)가 두 Frame에 같은 코드로 적용되며, 방향에 따라 달라지는 것은 슬라이드 이동 방향, 방향키(가로 ←/→, 세로 ↑/↓), 흐름(Flow) 방향뿐입니다.

- Frame이 소유하고 AI가 만들거나 고치지 않는 것: Header, Controller(점·화살표), Branding·Logo·favicon, Theme, Font, Icon, Safe Area, 슬라이드 요소, animation·transition, navigation, Runtime.
- Frame은 Header·Controller 밖에 **Content Safe Area**를 제공하고 Content를 그 안 **시각적 중앙**에 놓습니다. AI는 `main[data-nhimc-role="content"]`만 작성합니다.
- 헤더·컨트롤러를 피하려는 `margin`·`padding`·`position:absolute/fixed`·`translate`·`100vh` 계산·높이 숫자는 쓰지 않습니다. 사용자에게 “헤더와 컨트롤러를 피해서 작성하라”는 별도 프롬프트를 요구하지 않습니다.
- 슬라이드 전환·active 상태·prev/next·점·키보드는 Runtime이 처리합니다. Content에 `@keyframes`, `transition` 재정의, `display`·active class를 바꾸는 스크립트를 넣지 않습니다.

Content 작성 규칙(발표용):

1. 한 슬라이드에 핵심 메시지 하나. 제목 + 핵심 내용, 본문은 짧게, 포인트는 3~5개 이내.
2. `PresentationHero`(제목·부제 `.nhimc-presentation-hero`)와 `PresentationFlow`(단계·흐름 `ol.nhimc-presentation-flow`; presentation은 가로, presentation-vertical은 세로로 Frame이 방향을 정함)를 우선 씁니다. Content 루트는 Frame이 `PresentationContent`로 자동 배치합니다.
3. Hero message, Process flow, Key points, Comparison, Summary, Closing message 구조를 쓰고 ContentCard·Toolbar·FormGrid·Table·Pagination·SearchFilter는 최소로 씁니다. Form·Pagination·SearchFilter는 쓰지 않습니다.
4. 핵심 Content는 Safe Area 높이의 약 60~75%에 둡니다. 넘치면 ① 문장 축약 ② 항목 수 감소 ③ Card 수 감소 ④ 다음 슬라이드로 분리 순서로 줄입니다. 스크롤되는 슬라이드는 기본값이 아닙니다. 한 화면(16:9)에 들어가지 않으면 검증이 Safe Area 초과를 알리므로 반드시 줄이거나 나눕니다.

생성 순서: ① Frame 확인 ② Presentation Runtime 확인 ③ Layout Registry(`registry/layouts.json`) 확인 ④ Presentation Primitive 사용 ⑤ Content만 작성 ⑥ Safe Area 중앙 정렬 확인 ⑦ animation·navigation 보존 확인 ⑧ overflow 검사.

## Web(빌더를 실행할 수 없는 환경): 프롬프트 안에서 끝내기

`WEB_BOOTSTRAP / context-only`에서는 Frame을 직접 만들지 않고 **Web Runtime**을 씁니다. HTML 파일 하나만 작성합니다.

```html
<!doctype html>
<html lang="ko" data-theme="light">
<head><meta charset="utf-8"><title>화면 제목</title>
<script src="https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@2/dist/nhimc-web.js"></script>
</head>
<body>
<main data-nhimc-role="content">…등록 Component와 Layout Primitive만…</main>
<script type="application/json" data-nhimc-menu>[{"id":"main","label":"메뉴","icon":"hospital","href":"#main"}]</script>
</body></html>
```

화면이 둘 이상이면(메뉴 항목이 2개 이상) **화면마다** `<section data-screen-panel="메뉴id"><main data-nhimc-role="content">…</main></section>`로 감쌉니다. 바깥에 `<main>` 하나를 두고 그 안에 화면을 모으지 않습니다(Runtime이 이 흔한 실수는 고쳐 주지만 정해진 형태는 아래입니다). 메뉴 항목 수와 화면 수, 순서가 같아야 합니다.

```html
<body>
<section data-screen-panel="orders"><main data-nhimc-role="content">…주문 화면…</main></section>
<section data-screen-panel="items"><main data-nhimc-role="content">…품목 화면…</main></section>
<script type="application/json" data-nhimc-menu>[{"id":"orders","label":"주문","icon":"list","href":"#orders"},{"id":"items","label":"품목","icon":"hospital","href":"#items"}]</script>
</body>
```

1. `<script src>`는 반드시 `<head>`에 둡니다(본문 끝에 두면 Frame이 늦게 씌워져 스타일 없는 화면이 잠깐 보입니다). 주소의 `@2`는 jsDelivr가 최신 2.x 릴리스로 연결하는 형태라 릴리스마다 바꾸지 않으며, 옛 문서 복사본을 읽어도 최신 Runtime이 쓰입니다. `<nhimc-frame>`, `<style>`, 폰트, 아이콘, 로고, 자체 Frame은 넣지 않습니다. Runtime이 로드될 때 정본 Frame·Font·Icon·Logo·Theme을 씌웁니다.
2. 메뉴 `icon`은 위 “등록된 아이콘” 목록에 있는 이름만 씁니다. 메뉴 JSON은 생략하면 제목 한 개짜리 메뉴가 됩니다.
3. 인터넷과 외부 `<script src>`를 허용하는 호스트에서만 동작합니다. 막힌 호스트에서는 완성 파일을 만들 수 없다고 알리고, 오프라인 `index.html`이 필요하면 Claude Code · Codex · Gemini CLI 같은 로컬 환경에서 다시 요청하도록 안내합니다.
4. Web Runtime은 미리보기만 합니다(인터넷 필요, 아무 파일도 자동으로 저장하지 않습니다). 브라우저 검증을 거친 오프라인 `index.html`이 필요하면 저작용 원본을 그대로 전달하지 말고 Claude Code · Codex · Gemini CLI 같은 로컬 환경에서 로컬 빌더(`scripts/build_verified_artifact.py`)로 다시 만들도록 안내합니다.
