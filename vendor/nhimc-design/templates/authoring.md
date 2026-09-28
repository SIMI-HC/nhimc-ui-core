# Reference → 정식 Layout/Template/Theme 승격 Workflow

`references/inbox/`에 새 참고 HTML을 추가하고 "정식 Layout/Template/Theme으로 승격해줘" 같은 요청을 받았을 때 따르는 절차다. 이 문서는 새 Layout·Page Template·Theme을 추가하는 관리자 작업의 SSOT이며, `SKILL.md`는 이 문서로 라우팅만 한다.

## 절차

```text
references/inbox/의 신규 HTML
→ Classification
→ Duplicate Check
→ Visual Grammar Extraction
→ Golden Asset 작성
→ catalog.yaml 등록(selectable=false)
→ Render / Regression / Quality Gate
→ PASS
→ selectable=true
→ 다음 신규 화면 생성부터 사용자 선택지에 자동 노출
```

### 1. Classification

새 HTML 하나가 들어왔다고 항상 새 Template을 만들지 않는다. 다음 중 하나로 분류한다.

- **A. Layout 후보**: Navigation/Shell(Sidebar, SiteHeader, 앱 전체 구조)만 새롭다.
- **B. Page Template 후보**: Main Content Skeleton(섹션 구성·정보 배치 순서)이 새롭거나, 기존 Template보다 업무 완성도·데이터 표현이 뛰어나 그 Template 자체를 갱신할 가치가 있다.
- **C. Theme 후보**: Layout/구조는 기존과 동일하지만 Color System(브랜드 색·강조색)만 유의미하게 다르다.
- **D. 기존 개선 참고자료**: 간격·밀도·세부 아이디어만 유용하다. 정식 항목을 만들지 않고 해당 Token/Pattern/Component 개선의 참고로만 남긴다.

Layout/구조는 그대로인데 색만 다른 Reference를 새 Page Template으로 만들지 않는다 — 반드시 C(Theme 후보)로 분류한다.

### 2. Duplicate Check

- Layout 후보는 `catalog.yaml`의 `layouts` 배열과 비교해 기존 `left`/`top`/`top-left`로 충분히 표현되지 않는지 확인한다.
- Template 후보는 `catalog.yaml`의 `templates` 배열과 `page_type`·`features`·`density`가 겹치지 않는지 확인한다.
- Theme 후보는 `tokens/themes/catalog.yaml`의 `themes` 배열과 비교해 기존 Theme의 `primary` 계열색과 색상환 상 충분히 구분되는지 확인한다.
- 겹치면 새 항목을 만들지 않고 가장 가까운 기존 Golden Layout/Template/Theme의 개선 참고자료(D)로 남긴다.

### 3. Visual Grammar Extraction

새로운 가치가 있는 구조·간격·위계만 추출한다. Reference HTML의 raw element나 임의 색·간격을 그대로 옮기지 않고, 기존 Token(`tokens/registry.md`, `docs/design-docs/design.md`)·Component(`components/registry.md`)·Pattern(`patterns/registry.md`) 체계로 재구성한다.

### 4. Golden Asset 작성

- Layout 후보 → `assets/layouts/<id>.html`. Shell(Sidebar/SiteHeader/Main slot/statusbar)만 담당하고 업무 Pattern(SearchFilter, DataTable, Tabs, Form, Pagination, Dashboard Card 등)을 포함하지 않는다.
- Template 후보 → `assets/templates/<page-type>/<variant>.html`. `body[data-nhimc-template-scope="content-only"]` 아래 하나의 `main[data-nhimc-role="content"]`만 두고 `data-nhimc-role`/`data-nhimc-component` marker를 붙인다. Header·Sidebar·Footer·statusbar·모바일 Drawer 같은 Frame 요소는 넣지 않는다.
- Theme 후보 → 새 HTML/CSS 파일을 만들지 않는다. Reference에서 Semantic Color만 추출해 `tokens/themes/catalog.yaml`에 값으로 등록하고 `docs/design-docs/design-tokens.css`의 `[data-theme-color="<id>"]` 블록에 미러한다(아래 4절 참고).
- 모든 Golden Asset은 외부 CDN·원격 자산 없이 단독으로 열리고, Noto Sans KR은 이름으로만 참조하며 `data:font/...;base64`를 직접 삽입하지 않는다([offline.md](../rules/offline.md), [design-docs/assets/README.md](../docs/design-docs/assets/README.md)).

### 5. catalog.yaml 등록

- Layout: `id`, `label`, `purpose`, `asset`, `selectable`, `added_date`, `updated_date`, `updated_at`.
- Template: 기존 필수 필드(`id`, `added_date`, `updated_date`, `updated_at`, `variant`, `page_type`, `purpose`, `template`, `features`, `shell`, `density`, `content_contract`, `required_components`, `supported_states`, 선택적 `optional_components`)를 사용한다. `content_contract`에는 Content Slot 내부 역할만 등록한다. Validator는 콘텐츠 전용 scope와 단일 content root를 검사하고 Frame role이 하나라도 있으면 실패시킨다.
- `added_date`는 최초 Catalog 등록일로 고정하고 `updated_date`는 해당 Frame/Template 정본을 마지막으로 수정한 날짜로 갱신한다. 둘 다 `YYYY-MM-DD` 형식이며 수정일이 추가일보다 빠를 수 없다. `updated_at`은 같은 변경의 시간대가 포함된 ISO 8601 일시(`YYYY-MM-DDTHH:mm:ss+09:00`)로 기록하고 날짜 부분을 `updated_date`와 일치시킨다. Guide는 `updated_at`만 분 단위로 표시·검색·최신순 정렬한다.
- Theme: `tokens/themes/catalog.yaml`에 `id`, `label`, `summary`(한 줄 특징), `recommended_for`(추천 상황), `selectable`, `tokens.light`/`tokens.dark`(`primary`, `primary-foreground`, `ring`, `primary-90`, `primary-20` 5개 key)를 등록한다.
- 새 항목은 검증 전까지 반드시 `selectable: false`로 등록한다.

### 6. Render / Regression / Quality Gate

```powershell
python .agents/skills/nhimc-worktool/scripts/validate_templates.py
python scripts/verify_all.py
```

새 Template이면 `tests/regression/cases/`에 최소 1개 Case와 `tests/regression/prompts/`에 대응 prompt를 추가해 Template Coverage에 포함시킨다. Layout/Theme은 별도 Case 없이 `run_regression.py`가 selectable Layout/Theme마다 최소 1회 렌더 검증(Layout Coverage/Theme Coverage)을 수행한다. Theme은 `assets/themes/preview.html`을 공유 렌더 대상으로 쓰고 Light/Dark 모두 렌더하며, `validate_templates.py`가 `primary`/`primary-foreground` WCAG AA 대비(≥4.5:1)를 자동 검사한다.

### 7. selectable=true

Quality Gate가 PASS하면 `selectable`을 `true`로 바꾼다. 이 변경 이전에는 사용자 선택지에 노출하지 않는다. 이후 신규 화면 생성부터 해당 Layout/Template/Theme이 선택지에 자동으로 나타난다.

## 금지사항

- Reference HTML을 그대로 Golden Asset으로 복사하지 않는다.
- 검증 전에 `selectable: true`로 등록하지 않는다.
- Layout과 Page Template을 곱한 조합 HTML(`left-list-default` 등)을 만들지 않는다.
- Color만 다른 Reference를 새 Page Template(`list-default-blue` 등)으로 만들지 않는다 — Theme 후보로 분류한다.
- 새 Layout/Template/Theme ID를 Python 코드에 하드코딩하지 않는다. Validator는 catalog를 동적으로 읽는다.
