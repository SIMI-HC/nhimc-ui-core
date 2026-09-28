# Anti-patterns

- 임의 hex/rgb, spacing, radius, shadow, breakpoint, animation 생성.
- 기존 Button/Card/Input/Table과 비슷한 컴포넌트 재구현.
- 페이지마다 다른 검색·필터·action 배치.
- 같은 의미의 Badge variant 중복.
- Card 중첩, 장식 gradient, 목적 없는 animation과 shadow.
- 아이콘 크기 임의 지정 또는 이모지 아이콘 사용.
- 색만으로 상태·출처 표현.
- Table의 세로 격자선과 zebra stripe.
- 좁은 화면에서 navigation 또는 주요 action 제거.
- NHIMC 병원 로고·캐릭터·전용 셸을 public UI에 혼용.
- 무채색 기본 shadcn 화면처럼 만들고 public의 네이비 Sidebar·파스텔 아이콘 칩·채움형 표 헤더를 누락.
- 기존 프로젝트의 화면·공용 컴포넌트를 확인하기 전에 Golden Template을 그대로 덮어쓰기.
- Golden Template을 참고할 때 catalog에서 하나를 고르지 않고 모든 Golden Template을 한꺼번에 읽기.
- 메뉴가 여러 개인 참고 앱을 한 화면으로 축약하거나 빈 화면·dead navigation 만들기.
- 부모 `gap`과 자식 `margin`이 같은 컴포넌트 사이 간격을 동시에 소유해 이중 간격을 만들거나, 반대로 섹션 간격을 없애 카드끼리 붙이기.
- CDN, Google Fonts, 원격 이미지, 외부 script/link 또는 네트워크 API를 내부망 결과물의 런타임 의존성으로 만들기.
- 둥근 모서리 Card 안에 색배경 header band를 넣으면서 `overflow:hidden`을 빠뜨려 밴드 모서리가 카드 밖으로 삐져나오게 두기.
- 모바일 오프캔버스 사이드바/드로어에 열기 버튼만 만들고 패널 내부의 명시적 닫기(X) 버튼을 빠뜨리기.
- 전체 스크립트가 `(function(){...})()` IIFE로 감싸져 있는데, 그 안의 함수를 마크업의 인라인 `onclick="fn()"`으로 호출하기(전역 스코프에서 `ReferenceError` 발생). 같은 파일의 기존 버튼처럼 `id` + `addEventListener`로 연결한다.
- 파일 열기·명령 실행 같은 동작을 실제 결과를 확인하지 않고 "했다"/"열었다"고 보고하기. exit code나 tool 출력만으로 실제 창이 떴는지 확신할 수 없으면 그렇게 확신할 수 없다고 사용자에게 알리고, 열람이 필요한 정보(Guide 목록 등)는 AI가 파일을 직접 읽어 대체 확인한다.
- 신규 화면에서 사용자가 Layout·Theme 선택지를 보여달라고 명시적으로 요청했는데도 catalog 후보를 실제로 나열하지 않고 업무 배경·산출물 형태 같은 임의 질문으로 대체하기. 또는 AI가 판단해야 할 Page Type을 사용자에게 직접 고르게 하기. Layout·Theme은 사용자가 요청하지 않는 한 되묻지 않고 AI가 바로 판단해 적용한다(`SKILL.md`의 UI 생성 워크플로).
- 같은 대화라는 이유만으로, 지금 만들고 있는 HTML 결과물과 무관한 **별개의 새 HTML** 요청에도 이전 결과물에서 고른 Layout·Theme을 이어받아 다시 묻지 않기. Layout·Theme 재사용은 같은 HTML 결과물(하나의 다중 화면 manifest) 안에서만 유효하다.
- Layout/Template/Theme 선택지를 `catalog.yaml`·`tokens/themes/catalog.yaml`의 `selectable=true` 전체가 아니라 일부만(예: Theme 5개 중 3개만) 골라서 하드코딩해 보여주기. 개수를 외워서 나열하지 말고 그 자리에서 catalog 파일을 읽어 전체 목록을 만든다.
- 병원 브랜드 로고(`brandmark-row-logo.svg`) 같은 canonical inline SVG를 손으로 축약·재구성해 일부 `<path>`만 옮기고 나머지를 `<text>` 등으로 임의 대체하기. 원본 아트웍의 좌표계(`viewBox`)는 전체 도형을 기준으로 잡혀 있어 일부만 떼어내면 남은 도형과 새로 끼워 넣은 요소가 서로 맞지 않아 겹치거나 깨져 보인다. 로고는 항상 정본 파일 전체를 그대로(byte 단위로) 복사해 붙여넣고, 필요하면 스크립트로 추출해서 옮긴다.
- 도움말·확인 같은 UI를 구현할 시간이 부족하다는 이유로 브라우저 네이티브 `alert()`/`confirm()`/`prompt()`를 임시 placeholder로 남겨두기. Canonical LEFT·TOP Layout asset은 이미 X·Esc·외부 클릭으로 닫히는 슬라이드형 `<dialog class="help-dialog">`와 그 JS 배선을 완전한 형태로 포함하므로, 새로 설계하지 말고 그 마크업과 스크립트를 그대로 재사용한 뒤 안내 문구만 화면에 맞게 바꾼다.
- 화면 전용 CSS에서 `--color-muted-foreground` 같은 이미 있는 Semantic Token 대신 비슷해 보이는 회색 hex(`#555`, `#666` 등)를 직접 적어 넣기. 라이트에서는 우연히 구분되어 보여도 다크 모드 대비가 없어 텍스트가 배경에 묻힌다. 새 요소를 추가할 때도 같은 파일의 다른 보조 텍스트가 어떤 token을 쓰는지 먼저 확인하고 그대로 재사용한다.
- Golden Layout/Template/Component 정본 자산을 고치고 나서 `templates/catalog.yaml`·`components/registry.md`의 `updated_date`/`updated_at` 갱신을 빠뜨리기. 정본 파일을 하나라도 수정한 작업은 완료 보고 전에 반드시 그 정본을 가리키는 Registry 행의 날짜도 같은 커밋 단위로 갱신했는지 확인한다.
- "초기화 버튼이 너무 진해 보인다"는 이유로 특정 화면에서 `.reset-btn{color:var(--color-muted-foreground)}`처럼 화면 전용 CSS로 recolor하기, Select가 어색해 보여 특정 화면에서 border·arrow를 별도 재구현하기, canonical Component가 있는데 화면 안에서 hover/focus/color/font-weight를 다시 정의하기, 정본 충돌을 발견하고도 화면 한 개만 고치고 정본(design.md/showcase.html/Registry/Golden Template)은 그대로 두기. 필요한 시각 위계가 기존 Variant로 표현되지 않으면(예: SearchFilter 초기화처럼 muted 저강조가 필요한데 `ghost`뿐인 경우) [Canonical Component Resolution](../SKILL.md#canonical-component-resolution)에 따라 Component Variant를 정식으로 추가하고 design.md → registry → showcase → pattern/template → validator를 한 번에 동기화한 뒤, 화면은 그 Variant 이름만 선택한다.
- `--color-chip-*`(사이드바 메뉴 아이콘 칩 전용, 다크 모드에서도 값이 고정)를 안내 배너·카드 헤더 띠처럼 큰 면 배경에 재사용하기. 라이트에서는 괜찮아 보이지만 다크 모드에서 밝은 파스텔 박스가 그대로 튀어 보인다. 이런 용도는 이미 테마별로 값이 바뀌는 `--color-secondary`·`--color-band-sky`나 Component Registry의 Alert(`assets/components/showcase.html` `.alert{background:var(--color-secondary)}`)를 재사용한다.

## 구현 계약 위반 사례

- **BAD:** 기존 Button이 있는데 화면 전용 custom button 생성.
- **BAD:** 기존 SearchFilter가 있는데 화면마다 검색영역을 별도 구현.
- **BAD:** 기존 DataTable이 있는데 화면마다 table markup 반복.
- **BAD:** Golden Template이 Sidebar Layout인데 근거 없이 Top Navigation으로 변경.
- **BAD:** Button variant/size가 있는데 `className`으로 색·높이·radius를 모두 재정의.
- **BAD:** spacing token이 있는데 arbitrary value 사용.
- **BAD:** SearchFilter 초기화 버튼이 순검정 굵은 글씨로 Primary Action처럼 튀는데도 화면별 `.reset-btn` 색상 override로 봉합.
- **BAD:** `refresh` canonical 아이콘이 있는데 ↻/⟳ 같은 Unicode 문자나 이모지, 또는 직접 그린 새 SVG path로 대체.
- **BAD:** Golden Template HTML을 복사한 뒤 그 안의 canonical Component(Button/Select/Table 등)를 화면마다 조금씩 다르게 수정 — Template은 section 배치·정보 위계 참고이지 그 안 Component의 스타일을 바꿔도 된다는 뜻이 아니다.
- **BAD:** native `<select>`의 브라우저 기본 화살표가 그대로 보이거나, canonical chevron/native 기본 UI가 화면마다 다르게 노출.
- **BAD:** 같은 Component(예: Button)가 화면마다 border·radius·padding·hover가 조금씩 달라 하나의 디자인 시스템처럼 보이지 않음.
- **GOOD:** Canonical Frame을 그대로 재사용하고 Golden Template의 Content Contract를 기존 canonical Component + Pattern + Token으로 조립.
- **GOOD:** 필요한 시각 위계가 기존 Variant로 표현되지 않으면 Component Variant(예: `ghost-subtle`)를 정식으로 추가하고 design.md → registry → showcase → pattern/template → validator를 한 번에 동기화한 뒤, 화면은 Variant 이름만 선택.
