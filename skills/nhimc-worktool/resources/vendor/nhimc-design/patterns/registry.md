# Pattern Registry

Pattern은 Main 내부의 반복 조합이며 이 스킬의 Composition 역할도 담당한다. `SearchFilter`, `DataTable`, `PageHeader`와 같은 기존 조합이 있으면 `SearchToolbar`, `TableSection`, `AppHeader`처럼 이름만 다른 Composition/Block을 추가하지 않는다.

Template은 이 Registry의 Pattern을 참조하고, Pattern은 아래 `related_items`의 Component를 조합하며, Component가 Token을 소유한다. Template HTML의 raw element는 배치와 위계를 보여주는 시각 참고일 뿐 production 구현 정본이 아니다.

## PageHeader

- purpose: 화면 맥락과 주요 행동을 한 위치에 고정한다.
- when_to_use: 모든 업무 화면의 본문 시작.
- when_not_to_use: Dialog 내부, 독립 Card 내부.
- related_items: Breadcrumb, Button, ListPage, DetailPage.
- source: `docs/design-docs/design.md §4`.
- example: 왼쪽 제목·설명, 오른쪽 주요 등록 버튼 하나.
- composition: 제목과 설명은 하나의 wrapper에서 `{spacing.xs}` 간격을 유지한다. action/status는 오른쪽 보조 영역에 두고, 좁은 화면에서는 제목 아래로 자연스럽게 내려오게 한다. 제목과 설명을 별도 형제로 두고 음수 margin으로 결합하지 않는다.

## SearchFilter

- purpose: 검색·필터·초기화를 같은 규칙으로 조합한다.
- when_to_use: 목록을 사용자가 좁혀야 할 때.
- when_not_to_use: 항목 수가 적고 탐색이 불필요할 때.
- related_items: Input, Select, Button, DataTable.
- source: `docs/design-docs/design.md §6`.
- example: 검색 Input + 상태 Select + 조회 Button + 초기화 Button(ghost-subtle).
- composition: 결과 DataTable 앞에서 검색→범위/상태→실행/초기화 순서를 유지한다. 제어가 1~2개면 compact toolbar, 설명·초기화 또는 3개 이상 제어가 있으면 Card 하나에 묶는다. 검색 영역과 결과 Card의 간격은 부모의 `spacing.base` 한 곳만 소유한다. 실행/조회는 primary 또는 해당 Golden Template이 지정한 canonical action variant를, 초기화는 반드시 Button `ghost-subtle`을 사용한다. 초기화 버튼을 화면 CSS에서 별도로 recolor하지 않는다 — SearchFilter Pattern은 Component 순서와 배치만 소유하고 color·height·radius·font-weight 같은 Component visual은 Button/Select/Input 정본을 그대로 따른다. 화면마다 `.reset-btn`, `.clear-button` 같은 별도 스타일을 만들지 않는다.
- density: 데스크톱은 가능한 한 한 행, 모바일은 검색 입력을 첫 행 전체 폭으로 두고 나머지 제어를 다음 행에 배치한다. 라벨·도움말 때문에 대형 빈 공간을 만들지 않는다.

## FilterToolbar

- purpose: 검색 외 정렬·기간·보기 옵션을 한 행에 배치한다.
- when_to_use: 3개 이상의 목록 제어가 있을 때.
- when_not_to_use: 단일 검색 입력뿐일 때.
- related_items: SearchFilter, Sheet.
- source: `docs/design-docs/design.md §6`.
- example: 모바일에서 주요 검색만 남기고 나머지는 Sheet로 이동.

## DataTable

- purpose: 데이터 목록·상태·행 행동·페이지네이션을 일관되게 제공한다.
- when_to_use: 비교 가능한 여러 레코드.
- when_not_to_use: 단일 객체 또는 카드형 탐색이 더 적합한 데이터.
- related_items: Table, Badge, EmptyState, LoadingState, PaginationArea.
- source: `docs/design-docs/design.md §6.8`.
- example: 기본 목록은 가로선 + hover. 그룹 비교표는 `colgroup` 너비 + 그룹명/개별 열명 2단 헤더 + 그룹 시작 경계만 사용하며 세로선·zebra stripe는 없음.
- composition: Card header에는 결과 제목과 건수 또는 대표 action만 둔다. 표는 header 바로 아래에서 시작하며 별도 Card를 중첩하지 않는다. comfortable 행은 읽기, dense 행은 비교 속도를 우선하되 동일 화면에서 두 밀도를 섞지 않는다.

## FormSection

- purpose: 관련 입력과 오류를 의미 단위로 묶는다.
- when_to_use: 등록·수정 폼.
- when_not_to_use: 검색 필터.
- related_items: Field, SelectField, RadioGroup, CheckboxGroup, SwitchField, FormPage.
- source: `docs/design-docs/design.md §6`.
- example: section heading + 설명 + field grid.

## DetailSection

- purpose: 상세 정보를 제목 있는 읽기 단위로 나눈다.
- when_to_use: 사용자·환자·승인·API Key 상세.
- when_not_to_use: 편집이 주목적인 폼.
- related_items: Card, Table, Tabs, DetailPage.
- source: `docs/design-docs/design.md §4, §6`.
- example: 기본정보, 권한, 변경 이력.

## StatusDisplay

- purpose: 상태를 색·아이콘·텍스트로 함께 전달한다.
- when_to_use: 레코드 상태, 시스템 상태, 검증 결과.
- when_not_to_use: 단순 카테고리.
- related_items: StatusIndicator, Badge, Alert, semantic tokens.
- source: `docs/design-docs/design.md §2, §6.4`.
- example: warning soft surface + warning icon + `승인 대기` 텍스트.

## RankBadge

- purpose: 여러 대상(부서·병동·발신자 등) 간 상대 순위를 "N위 / M" 형식과 등급 색으로 함께 전달한다.
- when_to_use: 순위·랭킹 비교가 있는 목록·대시보드(예: 부서별 만족도 순위, 발신 건수 순위).
- when_not_to_use: 절대 상태 판정(성공/실패/경고). 그 경우는 StatusDisplay/Badge의 success/warning/destructive를 그대로 쓴다.
- related_items: Badge, Table, Card.
- source: `docs/design-docs/design.md §6.4`(Badge 변형 재사용). 참고: `references/baseline/환자경험_데이터허브_통합포털.html`.
- example: `1위 / 12` success 계열, `6위 / 12` warning 계열, `11위 / 12` secondary 계열, 표본 부족 시 outline/muted.
- composition: 새 Component를 만들지 않고 기존 Badge의 `success`/`warning`/`secondary`/`outline` variant만 재사용한다. 상위 구간은 success, 중위는 warning, 하위는 secondary를 쓰고 destructive는 쓰지 않는다 — 순위가 낮다고 곧 오류·실패 상태는 아니기 때문이다. 표본 수가 적어 순위 신뢰도가 낮으면 outline + 흐린 텍스트로 별도 표시하고 숫자만으로 판단하지 않도록 "표본 부족" 문구를 병기한다.

## NumberedList

- purpose: 순서 의존성이 없는 병렬 항목(이유·질문 주제·체크 항목)을 순번과 함께 동일한 카드 구조로 나열한다.
- when_to_use: "왜 필요한가", "무엇을 물어보는가"처럼 개수는 정해져 있으나 항목 간 선후 관계나 완료 상태가 없는 설명형 목록.
- when_not_to_use: 현재/완료 상태가 있는 순차 진행(WorkflowSteps), 충족 여부를 판정하는 선행 조건(ReadinessChecklist), 수치 비교가 목적인 지표(MetricOverview).
- related_items: Card, Badge, Icon.
- source: `docs/design-docs/design.md §6.3`(Card 재사용). 참고: `references/baseline/[AX 추진부] AI Agent 인터뷰 OT 자료.html`.
- example: "01/02/03" 큰 순번 + 제목 + 설명의 3카드 그리드, 또는 원형 순번 칩 + 제목 + 설명의 4~7카드 그리드(마지막 항목만 강조 배경으로 요약 결론 표시).
- composition: 새 Component를 만들지 않고 기존 Card와 순번 표시(큰 숫자 텍스트 또는 `IconButton` 크기의 원형 칩)만 조합한다. 항목 수만큼 균등한 열로 배치하고, 항목 하나를 강조해야 하면 그 Card만 `card-banded`/primary 계열 배경으로 구분한다. 순번은 장식이 아니라 항목 수를 함께 전달하므로 텍스트로도 노출한다.

## EmptyState

- purpose: 데이터 없음의 이유와 다음 행동을 제시한다.
- when_to_use: 최초 데이터 없음 또는 검색 결과 없음.
- when_not_to_use: 조회 실패.
- related_items: Empty, Button.
- source: `docs/design-docs/design.md §7`.
- example: `검색 결과가 없습니다` + 필터 초기화.

## ErrorState

- purpose: 실패 원인과 복구 행동을 제공한다.
- when_to_use: 데이터·저장·권한 오류.
- when_not_to_use: 유효한 빈 결과.
- related_items: Alert, Button, Empty.
- source: `docs/design-docs/design.md §7`.
- example: destructive Alert + 재시도.

## LoadingState

- purpose: 최초 조회 중 레이아웃을 보존한다.
- when_to_use: 기존 콘텐츠가 없는 초기 로딩.
- when_not_to_use: 기존 데이터를 유지하는 증분 조회.
- related_items: Skeleton, Spinner.
- source: `docs/design-docs/design.md §7`.
- example: 실제 표 열과 같은 skeleton rows.

## PartialLoading

- purpose: 기존 콘텐츠를 유지하며 추가 진행만 알린다.
- when_to_use: 페이지 추가 조회, 백그라운드 처리.
- when_not_to_use: 최초 전체 조회.
- related_items: Progress, Spinner.
- source: `docs/design-docs/design.md §7`.
- example: 표 상단 progress + 기존 행 유지.

## ConfirmAction

- purpose: 파괴적·되돌리기 어려운 행동을 재확인한다.
- when_to_use: 삭제, 철회, 권한 회수.
- when_not_to_use: 취소 가능한 일반 저장.
- related_items: Dialog, destructive Button.
- source: `docs/design-docs/design.md §6.9`.
- example: 영향 설명 + 취소 + 삭제.

## PaginationArea

- purpose: 결과 수와 페이지 이동을 표 하단에 배치한다.
- when_to_use: 페이지 기반 목록.
- when_not_to_use: 항목이 적거나 명시적 무한 스크롤.
- related_items: Pagination, DataTable.
- source: `docs/design-docs/design.md §6`.
- example: 왼쪽 `총 120건`, 오른쪽 페이지 이동.

## ActionArea

- purpose: 저장·취소·삭제처럼 화면의 완료 행동을 일관된 순서와 위치에 배치한다.
- when_to_use: 폼 제출, 상세 편집 완료, 관리 정책 저장.
- when_not_to_use: 검색 실행이나 표의 행 단위 빠른 행동.
- related_items: Button, FormSection, ConfirmAction.
- source: `docs/design-docs/design.md §4, §6`.
- example: 오른쪽 정렬된 취소 secondary + 저장 primary. 파괴 행동은 본문 위험 구역의 ConfirmAction으로 분리.

## MasterDetail

- purpose: 왼쪽 선택 목록과 오른쪽 선택 대상 상세·편집을 하나의 업무 맥락으로 묶는다.
- when_to_use: 권한·정책·분류처럼 목록을 이동하며 상세를 반복 검토할 때.
- when_not_to_use: 각 상세가 독립 URL과 긴 이력을 가지거나 모바일에서 두 패널을 동시에 유지할 수 없을 때.
- related_items: Card, Input, CheckboxField, CheckboxGroup, Badge, DetailSection, ActionArea.
- source: `docs/design-docs/design.md §4, §6`.
- example: 검색 가능한 정책 목록 + 선택 정책 권한 + 저장 ActionArea. 모바일에서는 목록→상세 순서로 쌓는다.

## MetricOverview

- purpose: 핵심 수치와 예외 신호를 동일한 카드 구조와 밀도로 요약한다.
- when_to_use: 운영 대시보드의 최상단 지표 묶음.
- when_not_to_use: 단일 수치 또는 비교 의미가 없는 장식 카드.
- related_items: Card, Badge, StatusDisplay.
- source: `docs/design-docs/design.md §6.3`.
- example: 2~4개의 지표 카드. 수치, 단위, 기준 시점 또는 변화 설명을 함께 표시.
- composition: 각 카드에는 파스텔 아이콘 칩, 짧은 라벨, 핵심 수치, 기준 설명을 이 순서로 둔다. 데스크톱 4열, 태블릿 2열, 모바일 1열을 기본으로 하고 수치만 크게 남긴 빈 장식 카드를 만들지 않는다.

## WorkflowSteps

- purpose: 생성·승인·점검처럼 순서가 있는 업무의 현재 단계를 한눈에 보여준다.
- when_to_use: 3~5개의 순차 단계와 현재/완료 상태가 있는 대시보드·폼.
- when_not_to_use: 자유 순서 작업이나 단순 내비게이션.
- related_items: Card, Badge, StatusDisplay, Button.
- source: `docs/design-docs/design.md §6.3, §7`.
- example: 4단계 카드에서 완료는 success, 현재 단계는 primary border+ring, 이후 단계는 중립 surface.
- composition: 단계 번호·제목·한 줄 설명을 유지하고 색 외에 번호와 상태 텍스트로 현재 위치를 전달한다. 모바일은 한 열로 쌓는다.

## ReadinessChecklist

- purpose: 주요 실행 전 필수 조건의 충족·주의 상태와 다음 행동을 함께 제시한다.
- when_to_use: 자동 생성, 제출, 배포처럼 선행 조건 검증이 필요한 화면.
- when_not_to_use: 단순 정보 목록.
- related_items: Card, StatusDisplay, Button, Alert.
- source: `docs/design-docs/design.md §6.3, §7`.
- example: 조건별 check/warning 아이콘 + 상태 텍스트 + 하단 primary action.
- composition: 성공·주의 항목을 같은 행 구조로 보여주고 마지막에 다음 단계 행동 하나를 둔다. 경고가 있으면 행동 라벨은 해결 작업을 명시한다.
