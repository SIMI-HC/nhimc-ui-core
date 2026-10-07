# NHIMC UI Core 시작

**문서 버전: 2.3.7** — 이 문서가 곧 저장소의 버전입니다(릴리스마다 함께 올라갑니다). 사용자 프롬프트는 `START.md`를 가리키고, `START.md`가 최신 릴리스 태그 주소로 이 문서를 읽게 합니다.

**먼저 지킬 규칙**
- 이 문서를 읽으려고 `git clone`/`git pull`을 하지 않습니다. 로컬에 사본이 있어도 raw URL로 다시 읽습니다.
- 작업 폴더에 저장소를 클론하지 않습니다(유일한 예외는 “웹에서 URL 없는 완성 HTML을 다운로드 파일로 주기” 절 참고).
- 설치·등록은 공식 플러그인 경로만 쓰고, 등록 전에 사용자에게 먼저 묻습니다.
- 원격 버전은 `registry/project.json`의 `projectVersion`을 raw로 확인합니다.

이 파일은 모든 AI 환경의 단일 진입점입니다. 이후 절차는 아래 "준비 절차"를 그대로 따릅니다.

플러그인·스킬 이름은 `nhimc-worktool`이며, 이미 설치돼 있으면 이 저장소 버전으로 갱신하고 없으면 새로 준비합니다.

사용자는 처음 한 번 다음처럼 요청합니다.

```text
https://raw.githack.com/SIMI-HC/nhimc-ui-core/main/START.md
이 파일만 읽고 NHIMC UI Core를 준비해줘. (git clone 금지)
```

그다음에는 자연어 요구만 받습니다.

```text
이송업무 관리 화면 만들어줘.
```

별도의 설치 명령을 사용자에게 묻지 마세요.

## 준비 절차 (항상 이 순서로, 사본이 남아 있어도 생략하지 않습니다)

이전 대화나 샌드박스에 저장소 사본·스킬·**플러그인 설치본**이 남아 있어도 **아래 1~9를 건너뛰지 않습니다.** 여기서 “사본”은 저장소 클론뿐 아니라 마켓플레이스로 설치한 플러그인 설치본, 스킬 업로드본도 포함합니다. 사본이 있다는 이유만으로 준비를 생략하지 않습니다.

**필수 리소스**: 어떤 설치 경로든 `<루트>`로 쓰려면 `registry/`, `scripts/`, `guide/`, `skills/`, `vendor/`, `VERSION` 6가지가 모두 있어야 합니다. 전체 저장소를 설치하는 플러그인 경로는 이 6가지가 저장소 루트에 그대로 있습니다. Codex의 “스킬만 업로드” 같은 경량 경로는 `skills/nhimc-worktool/`만 설치될 수 있으므로, 그 경우 나머지 5가지는 `skills/nhimc-worktool/resources/`(레포에 미리 미러링되어 있음) 아래에서 찾습니다.

**웹 채팅에서는 등록 여부를 묻지 않고 바로 `WEB_BOOTSTRAP`으로 갑니다.** claude.ai, ChatGPT, Gemini 같은 웹 채팅은 코드 실행 도구(샌드박스 셸)가 있어도 사용자의 컴퓨터가 아닙니다. 그 안에서 `claude plugin …` 같은 설치 명령을 제안하거나 실행해도 사용자 환경에는 아무 영향이 없으므로, 3~7단계를 건너뛰고 `WEB_BOOTSTRAP`으로 확정한 뒤 8·9단계로 갑니다(스킬 업로드는 사용자가 원할 때 직접 하며 묻지 않습니다). 등록 여부를 묻는 것은 사용자의 컴퓨터에서 도는 Claude Code · Codex · Gemini CLI(실제 `claude`/`codex`/`gemini` 명령과 플러그인 경로가 있는 환경)뿐입니다.

1. **raw `bootstrap.md` 읽기.** `https://raw.githack.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md`를 읽습니다(클론 아님). 지금 읽고 있는 이 문서가 그 결과입니다.
2. **원격 버전 확인.** 셸이 있고 github.com에 접근할 수 있으면 `git ls-remote --tags --sort=-v:refname https://github.com/SIMI-HC/nhimc-ui-core.git "v*"`(클론 아님)의 맨 위 태그가 원격 최신 버전입니다. 이 문서의 `문서 버전`과 같으면 그대로 따르고, 다르면 `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/<최신 태그>/bootstrap.md`를 읽어 그 문서를 따릅니다(태그 주소는 내용이 바뀌지 않습니다). 셸이 없으면 이 문서의 `문서 버전`을 `문서 기준`으로 쓰되 보고에는 `확인 못함(문서 기준 v…)`이라고 씁니다. `VERSION`·`main` 주소는 웹 AI 서비스에서 옛 복사본(예: 2.0.2)이 올 수 있어 읽지 않습니다. 확인하지 못한 경우 이후 어떤 설치본도 “최신”이라고 말하지 않습니다.
3. **설치된 `nhimc-worktool` 검색.** 이 환경의 플러그인 목록·스킬 목록·확장 목록에서 `nhimc-worktool`을 찾습니다. Claude Code는 `~/.claude/plugins/cache/<마켓플레이스>/nhimc-worktool/<버전>/`이며, 다른 환경은 그 환경의 플러그인/스킬 목록에서 설치 경로를 확인합니다.
4. **설치본이 있으면 버전과 필수 리소스를 검증.** 찾은 설치 경로를 `<루트>` 후보로 놓고 위 “필수 리소스” 6가지가 모두 있는지 확인합니다(직접 있거나, `skills/nhimc-worktool/resources/` 아래에 미러로 있으면 됨).
   - 모두 있고 로컬 버전이 2단계의 원격과 같거나 더 새로우면: 이 설치본을 `<루트>`로 확정하고 8단계로 갑니다.
   - 모두 있고 원격이 더 새로우면: 5단계로 가되 “업데이트할지” 질문합니다.
   - **하나라도 빠지면**: 이 설치본은 `<루트>` 후보에서 제외합니다. **클론으로 대체하지 않습니다.** 이 환경에 다른 등록 경로(예: 스킬 업로드 말고 정식 플러그인)가 더 있으면 3단계로 돌아가 확인하고, 없으면 5단계에서 “완전한 경로로 다시 등록할지”를 묻습니다.
5. **미등록이거나 불완전하면 공식 등록 가능 여부를 확인하고 사용자에게 묻습니다.** 이 환경이 지원하는 공식 등록 경로(플러그인 마켓플레이스를 우선하고, 그다음 스킬 업로드, 확장 순)가 있으면 **등록(또는 완전한 경로로 재등록)할지 사용자에게 먼저 묻습니다.** 자동 설치나 비공식 우회(클론 포함)를 하지 않습니다. 등록 경로가 없거나 사용자가 거절하면 `WEB_BOOTSTRAP`으로 확정하고 8단계로 건너뜁니다(이 경우도 작업 폴더에 클론하지 않습니다. 로컬 셸이 있고 사용자가 실제 검증된 산출물을 원하면 “웹에서 URL 없는 완성 HTML을 다운로드 파일로 주기”의 임시 경로 clone 예외를 씁니다).
6. **승인 시 공식 경로로 설치·업데이트합니다.** Claude Code는 `claude plugin marketplace add SIMI-HC/nhimc-ui-core` 다음 `claude plugin install nhimc-worktool@nhimc-worktool-marketplace`(업데이트는 `claude plugin marketplace update nhimc-worktool-marketplace` 다음 `claude plugin update nhimc-worktool@nhimc-worktool-marketplace`)입니다. 다른 환경은 그 환경의 공식 명령을 씁니다. 어떤 경우에도 `git clone`/`git pull`로 대신하지 않습니다.
7. **새 설치 경로를 `<루트>`로 설정하고 필수 리소스를 재검증합니다.** 6단계에서 설치·업데이트된 경로에 6가지 리소스가 모두 있는지 다시 확인합니다. 빠졌으면 “설치 패키지가 불완전하다”고 정확히 보고하고 `WEB_BOOTSTRAP`으로 폴백합니다(작업 폴더에 클론하지 않습니다).
8. **Design Guide를 표출합니다.** 처음 준비했거나 2단계에서 “원격이 더 새로움”으로 판정했을 때만 아래 “준비 완료 후: Design Guide 열기”대로 엽니다. 파일은 `<루트>/guide/nhimc-design-guide.html`(또는 스킬 전용 설치는 `<루트>/resources/guide/nhimc-design-guide.html`)입니다. 이미 최신이면 다시 열지 않고 링크만 한 줄로 알려 줍니다.
9. **결과를 보고합니다.** `platform`, `projectVersion`, `defaultFrame`, `defaultTheme`, `installationMode`에 더해 `최신 확인 결과`(갱신함/이미 최신/확인 못함), `스킬·플러그인 상태`(등록됨/업데이트함/업데이트 안 함/미등록·미지원/불완전), `Design Guide`(열었음/링크 전달/생략: 이미 최신)를 함께 씁니다. `최신 확인 결과`에는 어떻게 확인했는지(`git ls-remote` 직접 확인 + 읽은 태그 주소 / `문서 기준`)를 함께 씁니다.

## 준비 완료 후: Design Guide 열기

준비 절차 8단계에서 `<루트>/guide/nhimc-design-guide.html`을 사용자에게 엽니다(설치본이 있으면 클론하지 않고 그 설치 경로 — 필요하면 `resources/guide/` 아래 — 의 파일을 엽니다. 처음 준비하거나 버전이 갱신됐을 때는 생략하지 않습니다). 설치 가이드, 사용법, 프롬프트 만들기, Frame·Component·Icon 미리보기가 들어 있는 단일 오프라인 HTML입니다.

1. 로컬 셸이 있으면 기본 브라우저로 엽니다: Windows `start "" "<루트>\guide\nhimc-design-guide.html"`(또는 `<루트>\open-guide.cmd`), macOS `open "<루트>/guide/nhimc-design-guide.html"`, Linux `xdg-open "<루트>/guide/nhimc-design-guide.html"`.
2. 열 수 없으면(명령 실패, GUI 없음, 웹 환경) 사용자가 바로 열 수 있는 **클릭 링크**로 전달합니다. 이 링크는 브라우저에서 화면으로 열립니다(HTML로 제공되는 정적 호스팅). 답변에는 아래 형식 그대로 **한 줄**로 씁니다.

   ```text
   디자인 가이드: https://rawcdn.githack.com/SIMI-HC/nhimc-ui-core/v2.3.7/guide/nhimc-design-guide.html
   ```

   링크 형식 규칙: `디자인 가이드: ` 뒤에 전체 주소를 한 줄로 씁니다. 주소 안에 공백이나 줄바꿈을 넣지 않고, 끝의 `.html`을 빼지 않으며, 답변에서는 코드 블록이나 백틱으로 감싸지 않고 그대로 클릭되는 일반 텍스트로 둡니다(위 상자는 예시입니다).

   주소의 태그 숫자(`v2.3.7`)는 1단계에서 읽은 원격 `VERSION`에 맞춥니다. 링크를 열 수 없는 환경이면 `https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@v2.3.7/guide/nhimc-design-guide.html` 는 텍스트로 제공되므로 소스가 보이는 것이 정상이며, 이 경우 그 내용을 `nhimc-design-guide.html`로 저장해서 열도록 안내합니다. 파일을 첨부·저장할 수 있는 환경이면 `guide/nhimc-design-guide.html`을 그대로 첨부합니다.
3. 실제로 열었을 때만 “열었다”고 말하고, 못 열었으면 “다운로드 파일로 전달했다”고 정확히 말합니다.

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

## BLOG Frame 스크롤 소유자 (`blog`, Frame 1.1.0)

스크롤 소유자는 새 Layout이 아니라 **BLOG Frame 안의 상태**입니다. `<html data-scroll-owner="main|document">`(웹 실행은 `<nhimc-frame data-scroll-owner>`도 가능)로 고르고, 없으면 `main`입니다.

- `main`(기본): app-shell은 `100svh`, SiteHeader는 `flex:none`(sticky 아님, 반투명), **Main(`.content`)만 스크롤**합니다.
- `document`: 문서 전체가 스크롤합니다. SiteHeader는 sticky로 바뀌고 **반투명 + blur**(`--site-header-surface` 캔버스색(`#f4f7fa`/`#0a0a0a`) 40% 불투명 + `backdrop-filter: blur(12px)`, `border-bottom: 1px solid var(--color-border-accent)`, 정본 `--shadow-lg`)입니다. sticky + 완전 투명 조합은 만들지 않습니다.
- 앵커(`#id`)는 sticky 헤더 높이를 반영한 `scroll-margin-top`으로 이동합니다. 페이지에서 따로 보정하지 않습니다.
- 헤더 색은 `!important`가 아니라 토큰(`--site-header-surface`)으로 제어합니다. 로고·내비게이션·도움말·모바일 메뉴·Footer는 두 상태에서 같습니다.
- 소유자 전환은 `document.documentElement.dataset.scrollOwner`만 바꾸면 됩니다.

## 프롬프트 힌트 해석

사용자 요청에 다음 줄이 있으면(Design Guide의 “프롬프트 만들기” 결과) 그대로 따릅니다. 값 뒤의 ` — 이름`은 설명이므로 무시하고 첫 토큰만 id로 씁니다.

- `frame: <id>` → 저작 원본 `<html data-frame="<id>">` (`left`, `left-blank`, `left-dual`, `top`, `top-left`, `presentation`, `presentation-vertical`, `blog`). `frame:` 줄이 없으면 `(미선택 - AI 추천)`과 똑같이 취급해, 업무에 맞춰 AI가 고릅니다. 단 AI 추천은 `left`/`left-blank`를 고르지 않고 `top-left`(=DEFAULT Frame)·`top` 중에서 고르며(애매하면 `top-left`), 소식·콘텐츠형 화면이면 `blog`도 가능합니다. `left-dual`(아이콘 레일+하위 메뉴 패널을 둔 2단계 메뉴용 LEFT)도 후보지만 가장 후순위입니다 — 메뉴가 2단계이고 하위 화면이 많아 `top-left`·`top`으로 담기 어려울 때만 고릅니다. 이 규칙은 `rules/layout.md`의 자동 선택 순서(마지막 폴백 LEFT, blog 제외)보다 우선합니다(vendor 파일은 그대로 두므로 여기서 덮어씁니다), `presentation`/`presentation-vertical`은 PPT·발표·슬라이드용일 때만 고릅니다. `nhimc-default`는 레지스트리 내부 id일 뿐이며 `frame:` 값으로 쓰지 않습니다 — 사용자가 "디폴트로 해줘"라고 명시하면 `left`를 뜻합니다.
- `scroll-owner: <main|document>` → BLOG 전용. `<html data-scroll-owner="document">`. 없으면 `main`. 아래 “BLOG Frame 스크롤 소유자” 참고.
- `theme: <id>` → `<html data-theme-color="<id>">` (`nhimc-default`, `mint`, `pear`, `apricot`, `neutral`, `color-mix`). 라이트/다크는 `data-theme="light|dark"`.
- `requirements: …` → 화면 요구사항. 메뉴와 Page 구성은 이 내용에서 AI가 판단합니다.
- 값이 `(미선택 - AI 추천)`이면 업무에 맞춰 AI가 고릅니다. `frame:` 줄을 생략했을 때도 같습니다. `theme:` 줄을 생략하면 기본 테마 `nhimc-default`(NHIMC 기본)를 씁니다.

## 상태 판정

- `READY`: 이 호스트에서 `scripts/build_verified_artifact.py`를 호출하고 검증된 `index.html` 다운로드까지 시험했습니다.
- `WEB_BOOTSTRAP`: 저장소와 Skill만 읽을 수 있는 `context-only` 상태입니다.
- `UNSUPPORTED`: 저장소 또는 Skill을 읽을 수 없습니다.

특히 ChatGPT Web은 callable Builder Bridge의 `verified-builder-bridge-connected-and-download-tested` capability가 확인될 때만 `READY`입니다. 저장소 URL, 매니페스트 또는 Library 항목만 존재하면 `WEB_BOOTSTRAP`입니다.

## 기본 산출물 계약

1. Template은 없습니다. Component Registry(`registry/components.json`)를 먼저 검색해 기존 Component를 그대로 재사용하고, 여백·격자는 Layout Primitive(`registry/layouts.json`)로 맞춥니다.
2. `<nhimc-frame data-frame="left" ...>` 안에 `main[data-nhimc-role="content"]` 하나와 메뉴 JSON만 둡니다. Frame·Header·Left 메뉴는 다시 만들지 않습니다.
3. 메뉴, Page, 검색조건, Table 열, Card 구성은 업무 요구에 따라 자유롭게 정합니다.
4. capable host에서는 `scripts/build_verified_artifact.py`로 최종화합니다.
5. 브라우저 영수증과 정확히 일치하는 오프라인 `index.html` 하나만 다운로드로 전달합니다.
6. 저작 원본(`source.html`)은 사용자 프로젝트 폴더가 아닌 **임시 위치**(Claude Code: 세션 scratchpad 또는 OS 임시 폴더)에 저장합니다. 빌더 `--input`은 임시 경로, `--output`만 사용자 폴더의 `index.html`입니다. 빌드 뒤 출력 폴더에 `index.html` 외 파일이 없는지 확인하고 있으면 삭제하거나 임시 위치로 옮깁니다. 사용자가 “원본도 보관해줘”라고 명시한 경우에만 원본을 출력 폴더에 둡니다.
7. 결과 보고에는 최종 산출물 경로(`index.html`)만 쓰고 원본 경로는 쓰지 않습니다.

별도 `app.js`, CSS, 이미지, Font, receipt, README, asset 폴더는 최종 전달물이 아닙니다. 저작용 원본을 완성 파일로 첨부하면 안 됩니다.

빌더나 정확한 브라우저 검증을 실행할 수 없으면 `context-only`라고 명확히 알립니다. 수작업 HTML을 정본 완성품이라고 주장하거나 사용자에게 Python 실행을 떠넘기지 마세요.

유지보수 진단 시에만 다음 명령을 사용합니다.

```powershell
python scripts/build_verified_artifact.py --input <임시 경로>/source.html --output <사용자 폴더>/index.html
```

## 메뉴와 Page는 AI가 정합니다

Frame은 그대로 복사되고, AI는 **메뉴 JSON**과 **Page(Content)** 두 영역만 채웁니다.

1. 업무 요구를 보고 필요한 메뉴와 Page 수를 판단합니다. 메뉴는 `<script type="application/json" data-nhimc-menu>[{"id":"items","label":"품목 관리","icon":"hospital","href":"#items"}]</script>` 형식이며 그룹은 `children`(최대 3단)으로 표현합니다. `icon`은 `vendor/nhimc-design/icons/nhimc-icons.svg`에 있는 이름만 씁니다(`dashboard`, `list`, `users`, `settings`, `calendar`, `bar-chart`, `hospital`, `ambulance` 등). 메뉴 `id`는 될 수 있으면 아이콘 이름과 겹치지 않게 짓습니다(빌더가 이 둘을 서로 다른 네임스페이스로 렌더링하므로 겹쳐도 깨지지는 않지만, 겹치지 않는 편이 더 명확합니다). 업무에 맞는 아이콘이 등록 목록에 없으면 비슷한 다른 아이콘으로 임의 대체하지 말고 사용자에게 알린 뒤, 승인받으면 `scripts/add_canonical_icon.py`(Core 아이콘 추가 절차, 아래 참고)로 새 아이콘을 등록하고 씁니다.
2. 메뉴 항목마다 Page 하나를 같은 순서로 만듭니다. `id`와 `href="#id"`가 일치해야 합니다.
3. Page가 하나면 `<main data-nhimc-role="content">…</main>` 하나만 둡니다. 둘 이상이면 각각 `<section data-screen-panel="메뉴id"><main data-nhimc-role="content">…</main></section>`로 감쌉니다. 메뉴 클릭 시 화면 전환과 현재 메뉴 표시는 Frame이 처리하므로 직접 만들지 않습니다.
4. 각 Page는 등록 Component와 Layout Primitive(`nhimc-page-header`, `nhimc-toolbar`, `nhimc-grid`, `nhimc-form-grid`, `nhimc-card`, …)만으로 채웁니다. Page마다 구성(검색·표·카드·폼·차트·탭)은 자유입니다.

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

## Core 아이콘 추가 절차

`vendor/nhimc-design/icons/nhimc-icons.svg`는 상위 저장소의 고정 commit과 바이트 동일한 미러라 직접 고치지 않습니다. 업무에 맞는 아이콘이 등록 목록에 없으면:

1. 비슷한 다른 아이콘으로 임의 대체하지 말고, 어떤 아이콘이 필요한지 사용자에게 알리고 승인을 받습니다.
2. 승인되면 `python scripts/add_canonical_icon.py --id <새-id> --label "<한글 라벨>" --category <카테고리> --svg '<내부 SVG 마크업>'`로 `src/generated/icons/core-icons.svg`(Core 소유 오버레이)에 추가합니다. `viewBox="0 0 24 24"`, `stroke-width=2`, round cap/join, `currentColor`(내부 요소에 `fill`/`stroke`를 직접 넣지 않음) 규격은 스크립트가 검증하며, 어기면 그 자리에서 FAIL합니다. 이 오버레이는 정본 스프라이트와 빌드 시점에 합쳐지므로 벤더 파일은 그대로입니다.
3. `python scripts/update_integrity.py --frame nhimc-default --frame-version <다음 버전>`으로 오버레이 파일의 등록 해시를 갱신합니다.
4. 새 아이콘은 `src/guide/upstream/gallery-data.json`(Design Guide 아이콘 미리보기)에도 자동으로 함께 등록됩니다.

## 웹에서 “URL 없는 완성 HTML”을 다운로드 파일로 주기 (코드 실행이 되는 경우)

웹 AI라도 **코드 실행(샌드박스)과 GitHub 접근이 되면** 오프라인 빌더로 CSS·스크립트·폰트가 모두 든 단일 `index.html`을 직접 만들어 **다운로드 파일로 첨부**합니다. 이때 AI가 파일 내용을 손으로 써서 붙이지 않고 반드시 빌더를 실행합니다.

1. 빌더 위치 `<루트>`를 정합니다. 설치본이 있고 필수 리소스가 모두 있으면 **클론하지 않고** 그 설치 경로의 `scripts/`(또는 `resources/scripts/`)를 그대로 실행합니다(결과물만 작업 폴더에 씁니다). 설치본이 없거나 불완전하고, 공식 등록도 불가능하거나 사용자가 거절했는데 로컬 셸에서 실제 검증된 산출물이 필요할 때만 **임시/scratch 경로에** `git clone https://github.com/SIMI-HC/nhimc-ui-core.git`로 받습니다. `source.html`과 같은 임시 위치(세션 scratchpad 또는 OS 임시 폴더)를 쓰고, **사용자 작업 폴더에는 절대 clone하지 않습니다.**
2. 저작 원본(Content 조각 또는 `nhimc-frame` 문서)을 **임시 위치의 `source.html`로 저장합니다**(사용자 프로젝트 폴더에 두지 않습니다). `<script src>`(Web Runtime 줄)는 넣지 않습니다.
3. Chromium이 있으면 `python <루트>/scripts/build_verified_artifact.py --input <임시 경로>/source.html --output <사용자 폴더>/index.html`로 브라우저 검증까지 마칩니다. 없으면 `python <루트>/scripts/build_single_html.py --input <임시 경로>/source.html --output <사용자 폴더>/index.html`로 만들고 “브라우저 검증은 하지 못했다”고 알립니다.
4. 만들어진 `index.html`을 다운로드 파일로 첨부합니다(외부 URL 없음, 인터넷 없이 열림). 첨부·보고에는 `index.html`만 쓰고 원본은 첨부·언급하지 않습니다.

코드 실행이나 GitHub 접근이 안 되면 아래 Web Runtime 방식을 씁니다. 이 방식은 미리보기일 뿐이며 URL 없는 파일을 자동으로 만들어 주지 않으므로, 완성 파일이 필요하면 Claude Code · Codex · Gemini CLI 같은 로컬 환경에서 다시 요청하도록 안내합니다.

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
2. 메뉴 `icon`은 `vendor/nhimc-design/icons/nhimc-icons.svg`에 있는 이름만 씁니다. 메뉴 JSON은 생략하면 제목 한 개짜리 메뉴가 됩니다.
3. 인터넷과 외부 `<script src>`를 허용하는 호스트에서만 동작합니다. 막힌 호스트에서는 완성 파일을 만들 수 없다고 알리고, 오프라인 `index.html`이 필요하면 Claude Code · Codex · Gemini CLI 같은 로컬 환경에서 다시 요청하도록 안내합니다.
4. Web Runtime은 미리보기만 합니다(인터넷 필요, 아무 파일도 자동으로 저장하지 않습니다). 브라우저 검증을 거친 오프라인 `index.html`이 필요하면 저작용 원본을 그대로 전달하지 말고 Claude Code · Codex · Gemini CLI 같은 로컬 환경에서 위 “코드 실행이 되는 경우” 절차로 다시 만들도록 안내합니다.
