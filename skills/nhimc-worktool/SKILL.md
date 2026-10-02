---
name: nhimc-worktool
description: NHIMC UI Core(nhimc-worktool) 스킬. NHIMC 업무 화면을 정본 Frame 안에 등록 Component와 Layout Primitive로 조합하고 검증된 오프라인 index.html 하나로 전달할 때 사용합니다.
---

# NHIMC UI Core (nhimc-worktool)

저장소 루트에서 작업합니다. 정본 기준은 `vendor/nhimc-design/upstream.json`의 고정 commit과 v4 registry입니다. Template 시스템은 없습니다.

## 필수 순서

1. `registry/project.json`, `registry/frames.json`, `registry/themes.json`, `registry/components.json`, `registry/layouts.json`, `registry/assets.json`을 읽습니다.
2. 필요한 UI마다 Component Registry를 먼저 검색합니다. 동일 Component → 기존 Variant → 책임이 같으면 확장 → 마지막에만 신규 Component 순서입니다.
3. 저작 원본은 `<nhimc-frame data-frame="left" data-project-title="..." data-active-id="...">` 안에 `<main data-nhimc-role="content">` 하나만 둡니다. 메뉴는 `<script type="application/json" data-nhimc-menu>`에 JSON으로 선언합니다. Template 속성은 사용하지 않습니다.
4. Content는 Layout Primitive(`nhimc-page-header`, `nhimc-toolbar`, `nhimc-grid`, `nhimc-form-grid`, `nhimc-card`, `nhimc-stack`, `nhimc-section`, `nhimc-field-group`, `nhimc-scroll`, `nhimc-pagination`)와 등록 Component 마크업으로만 구성합니다. 화면 구성·메뉴·Page 수·검색조건·Table 열은 요구사항에 따라 자유롭게 판단합니다.
5. Component는 `registry/components.json`의 `markup`을 그대로 사용합니다(예: `btn primary`, `nav.pages`, `badge ok`, `label.field`). 필요한 곳에 `data-nhimc-component="이름"`을 표기합니다.
6. capable local host에서는 다음 명령으로 빌드·브라우저 검증·전달을 한 번에 수행합니다.

```powershell
python scripts/build_verified_artifact.py --input <임시 경로>/source.html --output <사용자 폴더>/index.html
```

   - 저작 원본(`source.html`)은 **사용자 프로젝트 폴더가 아닌 임시 위치**(Claude Code: 세션 scratchpad 또는 OS 임시 폴더)에 저장합니다. `--input`은 임시 경로, `--output`만 사용자 폴더의 `index.html`로 줍니다.
   - 빌드 후 출력 폴더에 `index.html` 외 파일이 없는지 확인하고, 있으면 삭제하거나 임시 위치로 옮깁니다.
   - 사용자가 “원본도 보관해줘”라고 **명시한 경우에만** 원본을 출력 폴더에 둡니다.

7. 실제로 전달된 파일이 하나의 `index.html`인지 확인한 뒤에만 “다운로드할 수 있게 만들었다”고 말합니다.

Frame, Theme, Logo, Navigation, Sidebar, 상태 표시줄, Component CSS, Icon sprite, Noto Sans KR Font를 수작업으로 복제하지 마세요. 임의 `<style>`, 외부 URL, fetch/import, sidecar 파일, 자체 Frame, `html`/`body`/`button`/`table` 전역 스타일 변경은 금지합니다.

## 메뉴와 Page는 AI가 정합니다

Frame은 그대로 복사되고, AI는 **메뉴 JSON**과 **Page(Content)** 두 영역만 채웁니다.

1. 업무 요구를 보고 필요한 메뉴와 Page 수를 판단합니다. 메뉴는 `<script type="application/json" data-nhimc-menu>[{"id":"items","label":"품목 관리","icon":"hospital","href":"#items"}]</script>` 형식이며 그룹은 `children`(최대 3단)으로 표현합니다. `icon`은 `vendor/nhimc-design/icons/nhimc-icons.svg`에 있는 이름만 씁니다(`dashboard`, `list`, `users`, `settings`, `calendar`, `bar-chart`, `hospital`, `ambulance` 등). 메뉴 `id`는 될 수 있으면 아이콘 이름과 겹치지 않게 짓습니다(빌더가 둘을 다른 네임스페이스로 렌더링해 겹쳐도 깨지지는 않지만 명확성을 위해 피합니다). 맞는 아이콘이 없으면 임의 대체하지 말고 사용자에게 알린 뒤, 승인받으면 아래 “Core 아이콘 추가 절차”로 추가합니다.
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
- `nhimc-scroll` 안 `table`의 최소 너비는 기본이 컨테이너 폭(`--table-min: 100%`)입니다. 열이 많아 넓게 둬야 하면 `<div class="nhimc-scroll" style="--table-min:640px">`처럼 지정합니다.

## Core 아이콘 추가 절차

`vendor/nhimc-design/icons/nhimc-icons.svg`는 바이트 동일 미러라 직접 고치지 않습니다. 필요한 아이콘이 없으면 사용자에게 먼저 알리고 승인받은 뒤 `python scripts/add_canonical_icon.py --id <새-id> --label "<라벨>" --category <카테고리> --svg '<내부 SVG>'`로 `src/generated/icons/core-icons.svg`(Core 오버레이)에 추가합니다. 스타일 규격(`viewBox="0 0 24 24"`, `currentColor` 상속을 위한 `fill`/`stroke` 미지정)을 어기면 스크립트가 FAIL합니다. 이어서 `python scripts/update_integrity.py --frame nhimc-default --frame-version <다음 버전>`으로 해시를 갱신합니다. `bootstrap.md`의 “Core 아이콘 추가 절차”를 따릅니다.

## 준비 절차 요약 (사본이 남아 있어도 생략 금지 — 플러그인 설치본·스킬 업로드본도 “사본”)

`bootstrap.md`의 “준비 절차”(9단계)를 순서대로 따릅니다: ① raw `bootstrap.md` 읽기 ② raw `VERSION` 확인(클론 아님) ③ 설치된 `nhimc-worktool` 검색 ④ 설치본이 있으면 버전과 필수 리소스(`registry/`, `scripts/`, `guide/`, `skills/`, `vendor/`, `VERSION`) 검증 — 리소스가 빠지면 클론으로 대체하지 않고 그 설치본을 후보에서 제외 ⑤ 미등록이거나 불완전하면 공식 등록 가능 여부를 확인하고 **클론을 고려하기 전에 먼저** 사용자에게 등록 여부를 묻기 ⑥ 승인 시 공식 경로로 설치·업데이트(Claude Code: `claude plugin marketplace add/update` + `claude plugin install/update`; 클론으로 대신하지 않음) ⑦ 새 설치 경로를 `<루트>`로 재확정하고 리소스 재검증 — 여전히 불완전하면 “설치 패키지가 불완전하다”고 보고하고 `WEB_BOOTSTRAP`으로 폴백(작업 폴더 클론 없음) ⑧ 처음 준비했거나 버전이 갱신됐으면 `<루트>/guide/nhimc-design-guide.html`(스킬 전용 설치는 `<루트>/resources/guide/`)로 Design Guide를 반드시 표출 ⑨ 최신 확인 결과·스킬/플러그인 상태·Design Guide 상태를 보고합니다.

**정상 절차에서는 `git clone`/`git pull`을 실행하지 않습니다.** 유일한 예외는 공식 등록이 불가능하거나 거절됐고 로컬 셸에서 실제 검증된 `index.html`이 필요한 경우이며, 이때도 사용자 작업 폴더가 아니라 `source.html`과 같은 **임시/scratch 경로**에만 clone합니다(`bootstrap.md`의 “웹에서 URL 없는 완성 HTML을 다운로드 파일로 주기” 참고).

## BLOG Frame 스크롤 소유자 (`blog`)

`<html data-scroll-owner="main|document">`(기본 `main`)는 새 Layout이 아니라 BLOG Frame 안의 상태입니다. `main`은 app-shell `100svh` + 투명 SiteHeader `flex:none` + Main(`.content`) 스크롤, `document`는 문서 스크롤 + sticky SiteHeader를 불투명 `--color-background` surface, `--color-border-accent` 하단 경계, 정본 `--shadow-lg`로 씁니다. sticky + 투명 조합과 `!important` 투명 강제는 쓰지 않으며, 앵커는 Frame이 `scroll-margin-top`으로 헤더를 피해 이동시킵니다.

## PRESENTATION Frame (`presentation`, `presentation-vertical`) — 공통 계약

두 Frame은 방향(슬라이드 이동·방향키·Flow)만 다르고 같은 Presentation Base Contract를 따릅니다. Frame이 Header·Controller·Branding·Theme·Font·Icon·Safe Area·슬라이드 요소·animation·transition·navigation·Runtime을 소유하고, AI는 `main[data-nhimc-role="content"]`만 작성합니다. Content는 Frame이 Safe Area의 시각적 중앙에 놓으므로 위치 보정용 margin/padding/position/translate/`100vh`/높이 숫자를 쓰지 않고, 사용자에게 헤더·컨트롤러를 피하라는 별도 프롬프트를 요구하지도 않습니다. animation·active 상태·navigation을 Content에서 다시 만들지 않습니다.

발표용 Content: 한 슬라이드 = 핵심 메시지 하나(제목 + 짧은 본문, 포인트 3~5개), `PresentationHero`·`PresentationFlow` 우선, ContentCard·Toolbar·FormGrid·Table 최소, Form·Pagination·SearchFilter 금지, Safe Area 높이의 60~75%. 넘치면 문장 축약 → 항목 감소 → Card 감소 → 슬라이드 분리 순서로 줄이며 스크롤 슬라이드는 기본값이 아닙니다.

생성 순서: Frame 확인 → Presentation Runtime 확인 → Layout Registry 확인 → Presentation Primitive 사용 → Content만 작성 → Safe Area 중앙 정렬 확인 → animation·navigation 보존 확인 → overflow 검사. 자세한 규칙은 `bootstrap.md`의 “PRESENTATION Frame — 공통 계약”을 따릅니다.

## Design Guide와 프롬프트 힌트

- 준비가 끝나면 `guide/nhimc-design-guide.html`을 열어 줍니다. 못 열면 `디자인 가이드: <전체 주소 .html까지, 한 줄, 코드 블록 없이>` 형식의 클릭 링크로 전달합니다(주소는 `bootstrap.md` 참고). 절차는 `bootstrap.md`의 “준비 완료 후: Design Guide 열기”를 따릅니다.
- 요청에 `frame:` / `theme:` / `requirements:` 줄이 있으면 각각 `<html data-frame>` / `<html data-theme-color>` / 화면 요구사항으로 반영합니다. `(미선택 - AI 추천)`이면 업무에 맞춰 고릅니다. 단 AI 추천은 `left`/`left-blank`를 고르지 않고 `top-left`(=DEFAULT Frame)·`top` 중에서 고르며(애매하면 `top-left`), 소식·콘텐츠형 화면이면 `blog`도 가능합니다. `left-dual`(아이콘 레일+하위 메뉴 패널을 둔 2단계 메뉴용 LEFT)도 후보지만 가장 후순위입니다 — 메뉴가 2단계이고 하위 화면이 많아 `top-left`·`top`으로 담기 어려울 때만 고릅니다. 이 규칙은 `rules/layout.md`의 자동 선택 순서(마지막 폴백 LEFT, blog 제외)보다 우선합니다(vendor 파일은 그대로 두므로 여기서 덮어씁니다), `presentation`/`presentation-vertical`은 PPT·발표·슬라이드용일 때만 고릅니다. `frame:` 줄이 없을 때도 같고(`left`로 고정하지 않음), `theme:` 줄이 없으면 `nhimc-default`를 씁니다.

## 웹에서도 코드 실행이 되면 완성 파일을 첨부

웹 AI라도 코드 실행과 GitHub 접근이 되면 저장소를 받아 `scripts/build_verified_artifact.py`(Chromium이 없으면 `scripts/build_single_html.py`, 검증 못 했다고 알림)로 URL 없는 단일 `index.html`을 만들어 다운로드 파일로 첨부합니다. 파일 내용을 손으로 써서 붙이지 않습니다. 코드 실행이 안 되면 아래 Web Runtime을 씁니다. 절차는 `bootstrap.md`의 “웹에서 URL 없는 완성 HTML을 다운로드 파일로 주기”를 따릅니다.

## Web(context-only)에서는 Web Runtime 사용

빌더를 실행할 수 없으면 `<main data-nhimc-role="content">…</main>`, 선택적 메뉴 JSON, 그리고 `<head>`에 넣은 `<script src="https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@v2.3.1/dist/nhimc-web.js"></script>` 한 줄로 HTML 하나를 완성합니다(본문 끝에 두면 스타일 없는 화면이 잠깐 보입니다). Runtime이 정본 Frame·Font·Icon·Logo를 씌우므로 `<nhimc-frame>`, 폰트, 아이콘, CSS를 직접 넣지 않습니다. 인터넷과 외부 스크립트가 막힌 호스트에서는 완성 파일을 만들 수 없다고 알리고 로컬 환경(Claude Code · Codex · Gemini CLI)에서 다시 요청하도록 안내합니다. Web Runtime은 미리보기만 하며 아무 파일도 자동으로 저장하지 않으므로, 브라우저 검증을 거친 외부 링크 없는 `index.html`이 필요하면 로컬 환경에서 빌더로 다시 만들도록 안내하세요.

## Self-check (완료 전 5개 계약)

- Protected Shell: Frame/Header/Left/Branding/favicon을 바꾸거나 다시 만들지 않았는가?
- Visual Foundation: Theme·Font·Icon·간격·radius·상태 규칙을 우회하지 않았는가?
- Component Reuse: 기존 Component나 Layout Primitive로 되는 UI를 새로 만들지 않았는가?
- Content Boundary: Content 때문에 Frame/전역 스타일/Registry를 수정하지 않았는가?
- Component Scope: 새 Component를 Shared 또는 Page-local로 올바르게 분류했는가?

## 전달 경계: single HTML

최종 결과는 인터넷과 저장소 없이 `file://`로 열리는 정확히 하나의 `index.html`입니다. `app.js`, CSS, 이미지, Font, manifest, receipt, README 또는 asset 폴더를 함께 전달하면 안 됩니다. **MUST NOT DELIVER** an approximate or handcrafted Frame as a finished NHIMC artifact. 저작용 원본을 완성 파일로 첨부하면 안 됩니다.

**원본 위치:** 저작 원본(`source.html`)은 결과물 옆에 두지 않습니다. 사용자 프로젝트 폴더에는 `index.html` 하나만 남기며, 원본은 임시 위치(Claude Code: 세션 scratchpad 또는 OS 임시 폴더)에서 `--input`으로만 씁니다. 빌드 뒤 출력 폴더에 `index.html` 외 파일이 있으면 삭제하거나 임시 위치로 옮기고(`build_verified_artifact.py`가 남아 있으면 경고합니다), 사용자가 “원본도 보관해줘”라고 명시한 경우에만 원본을 출력 폴더에 둡니다. 결과 보고에는 최종 산출물 경로(`index.html`)만 쓰고 원본 경로는 쓰지 않습니다.

호스트가 canonical builder와 정확한 브라우저 검증기를 실행할 수 없으면 capability를 `context-only`라고 보고합니다. 참고용 구조는 논의할 수 있지만 검증된 HTML을 만들었다고 주장하지 마세요.

ChatGPT Web은 검증된 Builder Bridge가 실제 연결되고 다운로드 시험까지 통과한 경우에만 `READY`입니다. 저장소 컨텍스트만 있으면 `WEB_BOOTSTRAP / context-only`입니다.

저장소 유지보수 검증은 목적별로 한 단계만 실행합니다. 개발 중 빠른 확인은 `python scripts/verify_all.py --quick`, 일반 변경의 최종 인계 전에는 `python scripts/verify_all.py`, 공개 릴리스 판단에는 전체 검증을 내부에 포함한 `python scripts/verify_release.py`를 실행합니다. `verify_release.py` 직전에 `verify_all.py`를 중복 실행하지 않습니다.
