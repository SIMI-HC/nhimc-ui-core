# NHIMC UI Core 시작

이 파일은 모든 AI 환경의 단일 진입점입니다. 저장소 루트의 `VERSION`, `registry/project.json`, `skills/nhimc-worktool/SKILL.md`를 읽고 그 계약을 따르세요.

이 저장소는 NhimcDesign(NHIMC Worktool)을 GitHub로 옮긴 프로젝트입니다. 플러그인·스킬 이름은 기존과 같은 `nhimc-worktool`이므로 이미 설치된 스킬이 있으면 이 저장소 버전으로 갱신하고, 없으면 새로 준비합니다.

사용자는 처음 한 번 다음처럼 요청합니다.

```text
https://github.com/SIMI-HC/nhimc-ui-core.git
bootstrap.md만 읽고 NHIMC UI Core를 준비해줘.
```

그다음에는 자연어 요구만 받습니다.

```text
이송업무 관리 화면 만들어줘.
```

별도의 설치 명령을 사용자에게 묻지 마세요.

## 스킬·플러그인 등록 확인

준비 단계에서 이 환경에 `nhimc-worktool` 스킬(또는 플러그인·확장)이 등록되어 있는지 확인합니다.

- 등록되어 있지 않고 이 환경이 공식 등록 경로(플러그인, Skill 업로드, 확장)를 지원하면, **등록할지 사용자에게 먼저 묻습니다**. 자동 설치나 지원되지 않는 방법으로의 우회는 하지 않습니다. 승인하면 그 경로로 등록하고, 거절하거나 지원하지 않으면 Web Bootstrap으로 계속합니다.
- 이미 등록되어 있고 저장소 `VERSION`이 더 새로우면 저장소 사본과 함께 **스킬·플러그인도 같은 버전으로 업데이트**합니다(승인이 필요하면 요청). 같거나 더 새로우면 건너뜁니다.
- 등록이나 업데이트를 실제로 확인하지 못했으면 됐다고 말하지 않습니다.

## 이미 준비되어 있는 경우 (항상 먼저 확인)

이전 대화나 샌드박스에 저장소 사본·스킬이 남아 있어도 **재준비를 생략하기 전에 반드시 버전을 비교**합니다. 사본이 있다는 이유만으로 건너뛰지 않습니다.

1. 원격 최신 버전을 읽습니다: `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/VERSION`
2. 로컬 사본(또는 설치된 `nhimc-worktool`)의 `VERSION`과 비교합니다.
3. 원격이 더 새로우면 갱신합니다: 저장소 사본은 `git pull`(또는 다시 클론), 플러그인·스킬은 공식 업데이트 경로를 씁니다(승인이 필요하면 요청). 갱신 뒤 `bootstrap.md`, `skills/nhimc-worktool/SKILL.md`, registry를 다시 읽습니다.
4. 같거나 설치본이 더 새로우면 그대로 사용하고 갱신은 건너뜁니다.
5. 원격 버전을 읽을 수 없으면 최신인지 확인하지 못했다고 보고하고, 갱신했다고 말하지 않습니다.

준비 상태 보고에는 실제로 사용한 `projectVersion`과 “최신 확인 결과(갱신함 / 이미 최신 / 확인 못함)”를 포함합니다.

## 준비 완료 후: Design Guide 열기

준비 상태(`platform`, `projectVersion`, `defaultFrame`, `defaultTheme`, `installationMode`)를 보고한 직후 `guide/nhimc-design-guide.html`을 사용자에게 엽니다. 설치 가이드, 사용법, 프롬프트 만들기, Frame·Component·Icon 미리보기가 들어 있는 단일 오프라인 HTML입니다.

1. 로컬 셸이 있으면 기본 브라우저로 엽니다: Windows `start "" guide\nhimc-design-guide.html`(또는 `open-guide.cmd`), macOS `open guide/nhimc-design-guide.html`, Linux `xdg-open guide/nhimc-design-guide.html`.
2. 열 수 없으면(명령 실패, GUI 없음, 웹 환경) 사용자가 바로 열 수 있는 **클릭 링크**로 전달합니다. 이 링크는 브라우저에서 화면으로 열립니다(HTML로 제공되는 정적 호스팅):

   `https://rawcdn.githack.com/SIMI-HC/nhimc-ui-core/v1.1.1/guide/nhimc-design-guide.html`

   버전 태그(`v1.1.1`)는 저장소 `VERSION`에 맞춰 바꿉니다. 링크를 열 수 없는 환경이면 `https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@v1.1.1/guide/nhimc-design-guide.html` 는 텍스트로 제공되므로 소스가 보이는 것이 정상이며, 이 경우 그 내용을 `nhimc-design-guide.html`로 저장해서 열도록 안내합니다. 파일을 첨부·저장할 수 있는 환경이면 `guide/nhimc-design-guide.html`을 그대로 첨부합니다.
3. 실제로 열었을 때만 “열었다”고 말하고, 못 열었으면 “다운로드 파일로 전달했다”고 정확히 말합니다.

## PRESENTATION Frame (`presentation`, `presentation-vertical`)

Frame이 Header(도움말·테마 버튼)와 Controller(슬라이드 점·화살표) 밖에 **Content Safe Area**를 제공합니다. AI는 `main[data-nhimc-role="content"]`만 작성하며, 헤더나 컨트롤러를 피하려는 `margin`·`padding`·`position`을 쓰지 않습니다. 사용자에게 “헤더와 컨트롤러를 피해서 작성하라”는 별도 프롬프트를 요구하지 않습니다. 한 화면(16:9)에 들어가지 않는 Content는 검증이 Safe Area 초과로 알려 주므로 내용을 줄이거나 페이지를 나눕니다.

## 프롬프트 힌트 해석

사용자 요청에 다음 줄이 있으면(Design Guide의 “프롬프트 만들기” 결과) 그대로 따릅니다. 값 뒤의 ` — 이름`은 설명이므로 무시하고 첫 토큰만 id로 씁니다.

- `frame: <id>` → 저작 원본 `<html data-frame="<id>">` (`left`, `left-blank`, `top`, `top-left`, `presentation`, `presentation-vertical`, `blog`). 없으면 `left`(`nhimc-default`).
- `theme: <id>` → `<html data-theme-color="<id>">` (`nhimc-default`, `mint`, `pear`, `apricot`, `neutral`, `color-mix`). 라이트/다크는 `data-theme="light|dark"`.
- `requirements: …` → 화면 요구사항. 메뉴와 Page 구성은 이 내용에서 AI가 판단합니다.
- 값이 `(미선택 - AI 추천)`이면 업무에 맞춰 AI가 고릅니다.

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

별도 `app.js`, CSS, 이미지, Font, receipt, README, asset 폴더는 최종 전달물이 아닙니다. 저작용 원본을 완성 파일로 첨부하면 안 됩니다.

빌더나 정확한 브라우저 검증을 실행할 수 없으면 `context-only`라고 명확히 알립니다. 수작업 HTML을 정본 완성품이라고 주장하거나 사용자에게 Python 실행을 떠넘기지 마세요.

유지보수 진단 시에만 다음 명령을 사용합니다.

```powershell
python scripts/build_verified_artifact.py --input path/to/source.html --output path/to/index.html
```

## 메뉴와 Page는 AI가 정합니다

Frame은 그대로 복사되고, AI는 **메뉴 JSON**과 **Page(Content)** 두 영역만 채웁니다.

1. 업무 요구를 보고 필요한 메뉴와 Page 수를 판단합니다. 메뉴는 `<script type="application/json" data-nhimc-menu>[{"id":"items","label":"품목 관리","icon":"hospital","href":"#items"}]</script>` 형식이며 그룹은 `children`(최대 3단)으로 표현합니다. `icon`은 `vendor/nhimc-design/icons/nhimc-icons.svg`에 있는 이름만 씁니다(`dashboard`, `list`, `users`, `settings`, `calendar`, `bar-chart`, `hospital`, `ambulance` 등).
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
- 상태 표시는 `badge ok|warn|bad`, 버튼은 `btn primary|ghost|ghost-subtle`, 검색 필드는 `label.field`입니다.

## Web(빌더를 실행할 수 없는 환경): 프롬프트 안에서 끝내기

`WEB_BOOTSTRAP / context-only`에서는 Frame을 직접 만들지 않고 **Web Runtime**을 씁니다. HTML 파일 하나만 작성합니다.

```html
<!doctype html>
<html lang="ko" data-theme="light">
<head><meta charset="utf-8"><title>화면 제목</title>
<script src="https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@v1.1.1/dist/nhimc-web.js"></script>
</head>
<body>
<main data-nhimc-role="content">…등록 Component와 Layout Primitive만…</main>
<script type="application/json" data-nhimc-menu>[{"id":"main","label":"메뉴","icon":"hospital","href":"#main"}]</script>
</body></html>
```

1. `<script src>`는 반드시 `<head>`에 둡니다(본문 끝에 두면 Frame이 늦게 씌워져 스타일 없는 화면이 잠깐 보입니다). `<nhimc-frame>`, `<style>`, 폰트, 아이콘, 로고, 자체 Frame은 넣지 않습니다. Runtime이 로드될 때 정본 Frame·Font·Icon·Logo·Theme을 씌웁니다.
2. 메뉴 `icon`은 `vendor/nhimc-design/icons/nhimc-icons.svg`에 있는 이름만 씁니다. 메뉴 JSON은 생략하면 제목 한 개짜리 메뉴가 됩니다.
3. 인터넷과 외부 `<script src>`를 허용하는 호스트에서만 동작합니다. 막힌 호스트에서는 완성 파일을 만들 수 없다고 알리고, 오프라인 `index.html`이 필요하면 Claude Code · Codex · Gemini CLI 같은 로컬 환경에서 다시 요청하도록 안내합니다.
4. Web Runtime 화면에는 오른쪽 아래 “오프라인 HTML 저장” 버튼이 자동으로 생깁니다. 사용자가 이 버튼으로 CSS·스크립트·폰트가 모두 들어간 HTML을 내려받을 수 있다고 안내합니다(직접 파일을 만들어 붙여 넣지 않습니다). 이 결과는 Web Runtime 결과이며 브라우저 검증을 거친 `index.html`이 아닙니다. 저작용 원본을 완성 파일로 첨부하지 말고, 사용자가 실제 브라우저에서 열어 확인하도록 안내합니다.
