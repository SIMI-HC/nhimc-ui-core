---
name: nhimc-worktool
description: NhimcDesign(NHIMC Worktool)을 GitHub로 옮긴 프로젝트의 스킬. NHIMC 업무 화면을 정본 Frame 안에 등록 Component와 Layout Primitive로 조합하고 검증된 오프라인 index.html 하나로 전달할 때 사용합니다.
---

# NhimcDesign (nhimc-worktool) 1.x

이 스킬은 NhimcDesign 프로젝트를 GitHub로 옮긴 것이며, 기존 `nhimc-worktool` 스킬과 같은 이름이라 설치하면 같은 스킬이 이 버전으로 갱신됩니다. 저장소 루트에서 작업합니다. 정본 기준은 `vendor/nhimc-design/upstream.json`의 고정 commit과 v4 registry입니다. Template 시스템은 없습니다.

## 필수 순서

1. `registry/project.json`, `registry/frames.json`, `registry/themes.json`, `registry/components.json`, `registry/layouts.json`, `registry/assets.json`을 읽습니다.
2. 필요한 UI마다 Component Registry를 먼저 검색합니다. 동일 Component → 기존 Variant → 책임이 같으면 확장 → 마지막에만 신규 Component 순서입니다.
3. 저작 원본은 `<nhimc-frame data-frame="left" data-project-title="..." data-active-id="...">` 안에 `<main data-nhimc-role="content">` 하나만 둡니다. 메뉴는 `<script type="application/json" data-nhimc-menu>`에 JSON으로 선언합니다. Template 속성은 사용하지 않습니다.
4. Content는 Layout Primitive(`nhimc-page-header`, `nhimc-toolbar`, `nhimc-grid`, `nhimc-form-grid`, `nhimc-card`, `nhimc-stack`, `nhimc-section`, `nhimc-field-group`, `nhimc-scroll`, `nhimc-pagination`)와 등록 Component 마크업으로만 구성합니다. 화면 구성·메뉴·Page 수·검색조건·Table 열은 요구사항에 따라 자유롭게 판단합니다.
5. Component는 `registry/components.json`의 `markup`을 그대로 사용합니다(예: `btn primary`, `nav.pages`, `badge ok`, `label.field`). 필요한 곳에 `data-nhimc-component="이름"`을 표기합니다.
6. capable local host에서는 다음 명령으로 빌드·브라우저 검증·전달을 한 번에 수행합니다.

```powershell
python scripts/build_verified_artifact.py --input path/to/source.html --output path/to/index.html
```

7. 실제로 전달된 파일이 하나의 `index.html`인지 확인한 뒤에만 “다운로드할 수 있게 만들었다”고 말합니다.

Frame, Theme, Logo, Navigation, Sidebar, 상태 표시줄, Component CSS, Icon sprite, Noto Sans KR Font를 수작업으로 복제하지 마세요. 임의 `<style>`, 외부 URL, fetch/import, sidecar 파일, 자체 Frame, `html`/`body`/`button`/`table` 전역 스타일 변경은 금지합니다.

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

## 이미 준비되어 있는 경우

남아 있는 사본·스킬이 있어도 재준비를 생략하기 전에 원격 `VERSION`(raw)과 비교해 더 새로울 때만 갱신하고, 결과(갱신함 / 이미 최신 / 확인 못함)를 보고합니다. 절차는 `bootstrap.md`의 “이미 준비되어 있는 경우 (항상 먼저 확인)”를 따릅니다.

## Design Guide와 프롬프트 힌트

- 준비가 끝나면 `guide/nhimc-design-guide.html`을 열어 줍니다(못 열면 다운로드 파일로 전달). 절차는 `bootstrap.md`의 “준비 완료 후: Design Guide 열기”를 따릅니다.
- 요청에 `frame:` / `theme:` / `requirements:` 줄이 있으면 각각 `<html data-frame>` / `<html data-theme-color>` / 화면 요구사항으로 반영합니다. `(미선택 - AI 추천)`이면 업무에 맞춰 고릅니다.

## Web(context-only)에서는 Web Runtime 사용

빌더를 실행할 수 없으면 `<main data-nhimc-role="content">…</main>`, 선택적 메뉴 JSON, 그리고 `<script src="https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@v1.0.0/dist/nhimc-web.js"></script>` 한 줄로 HTML 하나를 완성합니다. Runtime이 정본 Frame·Font·Icon·Logo를 씌우므로 `<nhimc-frame>`, 폰트, 아이콘, CSS를 직접 넣지 않습니다. 인터넷과 외부 스크립트가 막힌 호스트에서는 완성 파일을 만들 수 없다고 알리고 로컬 환경(Claude Code · Codex · Gemini CLI)에서 다시 요청하도록 안내합니다. Web Runtime 결과를 오프라인 검증된 `index.html`이라고 말하지 마세요.

## Self-check (완료 전 5개 계약)

- Protected Shell: Frame/Header/Left/Branding/favicon을 바꾸거나 다시 만들지 않았는가?
- Visual Foundation: Theme·Font·Icon·간격·radius·상태 규칙을 우회하지 않았는가?
- Component Reuse: 기존 Component나 Layout Primitive로 되는 UI를 새로 만들지 않았는가?
- Content Boundary: Content 때문에 Frame/전역 스타일/Registry를 수정하지 않았는가?
- Component Scope: 새 Component를 Shared 또는 Page-local로 올바르게 분류했는가?

## 전달 경계: single HTML

최종 결과는 인터넷과 저장소 없이 `file://`로 열리는 정확히 하나의 `index.html`입니다. `app.js`, CSS, 이미지, Font, manifest, receipt, README 또는 asset 폴더를 함께 전달하면 안 됩니다. **MUST NOT DELIVER** an approximate or handcrafted Frame as a finished NHIMC artifact. 저작용 원본을 완성 파일로 첨부하면 안 됩니다.

호스트가 canonical builder와 정확한 브라우저 검증기를 실행할 수 없으면 capability를 `context-only`라고 보고합니다. 참고용 구조는 논의할 수 있지만 검증된 HTML을 만들었다고 주장하지 마세요.

ChatGPT Web은 검증된 Builder Bridge가 실제 연결되고 다운로드 시험까지 통과한 경우에만 `READY`입니다. 저장소 컨텍스트만 있으면 `WEB_BOOTSTRAP / context-only`입니다.

저장소 변경 완료 전 `python scripts/verify_all.py`, 공개 릴리스 판단 전 `python scripts/verify_release.py`를 실행합니다.
