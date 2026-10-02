# Component Registry

Design Guide의 시각 표본은 `../assets/components/showcase.html`에서 관리한다. Registry의 모든 `id`는 동일한 `data-component-case`를 하나씩 가져야 하며, Guide는 해당 case 하나만 Preview 중앙에 표시한다. 카드 썸네일은 상세 열기용 읽기 전용이고 상세 Preview의 상태형 컨트롤은 클릭·선택·열기·닫기·진행 상태 변경이 실제로 동작해야 한다. Page Template 전체 화면을 Component Preview로 대체하지 않는다.

이 Registry는 NHIMC 업무 화면에서 직접 선택·조합하도록 승격한 49개 Component의 정본이다. `design.md`의 원천 UI 파일 커버리지 61개 전체와 같은 목록이 아니다. 원천 61개 중 일반 목적 55개는 규격 문서화 범위이고, AI 채팅 전용 6개는 일반 업무 화면에서 제외한다. 현재 승격 범위는 Registry 49개 = Showcase case 49개 = Guide Component 49개가 1:1로 일치해야 한다. 아직 승격되지 않은 원천 UI를 사용할 필요가 생기면 `component-selection.md`의 EXTENSION 게이트를 거쳐 Registry·Showcase·Guide를 같은 작업에서 함께 추가한다. 원천 61개 목록에 없는 순수 업무 참고 자산(예: `references/baseline/`의 내부 업무 화면)에서도 반복 재사용 가치가 확인되면 같은 EXTENSION 게이트를 거쳐 추가할 수 있으며, 이 경우 `spec_source`는 `design.md §6`이 아니라 해당 Component의 실제 정본인 `assets/components/showcase.html`과 유래 참고 파일을 함께 기록한다.

`layer=atom`은 다른 업무 Component를 포함하지 않고 단독 교체 가능한 제어·표현 원자다. `layer=composition`은 둘 이상의 atom 또는 접근성 배선을 결합해 별도 이름·상태·사용 계약을 갖는 응용 단위다. 단순 wrapper나 화면 전용 배치는 Component로 승격하지 않고 Pattern 또는 Template이 소유한다. Guide는 이 layer를 카드 분류와 검색에 표시한다.

각 항목은 기존 구현을 선택하기 위한 canonical Component 검색 Registry다. 상세 variants, sizes, states, accessibility, responsive behavior는 `../docs/design-docs/design.md §6`이 정본이다. `source`는 이 스킬 안의 canonical **규격**이며 대상 프로젝트의 실제 구현 경로가 아니다. 실제 `canonical_source`는 아래 검색 절차로 존재가 확인된 파일만 기록한다.

`added_date`는 Registry에 처음 등록된 날로 이후 바꾸지 않고, `updated_date`는 해당 Component의 규격·표본·상태 동작을 마지막으로 수정한 날짜로 갱신한다. `updated_at`은 같은 변경의 시간대가 포함된 ISO 8601 일시이며 날짜 부분은 `updated_date`와 일치해야 한다. Design Guide에는 `updated_at`을 `업데이트 YYYY.MM.DD HH:mm` 한 항목으로만 표시하고 검색·최신순 정렬에 사용한다.

아이콘이 필요하면 [icons.md](icons.md)의 canonical SVG를 쓴다. 이모지·유니코드 기호(☰ ✕ ▤ ▦ ♙ 등)를 아이콘 대신 쓰지 않는다 — `scripts/validate_templates.py`가 Golden Asset에서 이를 자동으로 탐지한다.

| id | purpose | when_to_use | when_not_to_use | variants/sizes/states | accessibility | responsive | related_items | spec_source | example | added_date | updated_date | updated_at | layer |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Button | 텍스트 중심 행동 실행 | 저장, 등록, 조회, 취소처럼 문구가 핵심인 행동 | 아이콘만 쓰는 compact 행동 또는 아이콘+문구 조합 | primary/secondary/outline/ghost/ghost-subtle/destructive; sm/default/lg; loading/disabled | 이름, focus-visible, disabled | 좁은 화면에서도 핵심 라벨 유지 | IconTextButton, IconButton, ButtonGroup, ConfirmAction | `design.md §6` | 주요 행동은 화면당 1개, SearchFilter 초기화는 ghost-subtle(destructive와 같은 red 채움 + 흰 텍스트) | 2026-09-11 | 2026-09-18 | 2026-09-18T15:40:00+09:00 | atom |
| IconButton | 아이콘 전용 행동 | 사이드바 접기, 모바일 메뉴, 도움말, 테마 | 텍스트가 필요한 주요 업무 행동 | ghost; 36px hit area; 18px icon; toggled/disabled | 정확한 aria-label·title, 상태 변화 시 이름 갱신 | 모바일/접힘에서도 hit area 유지 | Icon, Button, Tooltip, AppShell | `design.md §6.1, §6.2` | LEFT 헤더 유틸리티 | 2026-09-11 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| Input | 한 줄 입력 원자 | Field 또는 InputGroup 안의 검색어, 이름, 코드 입력 | label·help·error가 포함된 완성 필드 | default/error/disabled | 단독 표본은 aria-label, 업무 폼은 Field로 이름 연결 | 너비는 Field/InputGroup이 결정 | Label, Field, InputGroup, SearchFilter | `design.md §6` | label + input + help/error | 2026-09-11 | 2026-09-18 | 2026-09-18T13:00:00+09:00 | atom |
| Select | 단일 선택 트리거 원자 | Field 또는 SelectField 안의 상태·분류·정렬 선택 | label·help·error가 포함된 완성 필드 | default/error/disabled; closed/open | 단독 표본은 aria-label, 업무 폼은 SelectField로 이름 연결 | 모바일에서도 native/overlay 규칙 유지 | Label, SelectField, SearchFilter | `design.md §6` | 상태 필터 | 2026-09-11 | 2026-09-18 | 2026-09-18T13:00:00+09:00 | atom |
| Checkbox | 복수 선택 제어 원자 | 행 선택, 옵션 선택의 control | 사용자에게 문구가 필요한 완성 옵션 | checked/unchecked/indeterminate/disabled | 단독 표본은 aria-label, 업무 폼은 CheckboxField 사용 | 16px control과 터치 hit area 분리 | CheckboxField, CheckboxGroup, DataTable | `design.md §6` | 전체 선택 + 행 선택 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | atom |
| Radio | 상호배타 선택 제어 원자 | RadioField/RadioGroup 안의 단일 option control | 독립 boolean 또는 문구 없는 업무 옵션 | checked/unchecked/disabled | 단독 표본은 aria-label, 실제 선택은 RadioGroup의 이름·legend 연결 | 16px control, 좁은 화면은 Field가 hit area 보완 | RadioField, RadioGroup, FormSection | `design.md §6` | 처리 방식 선택 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | atom |
| Switch | 즉시 반영 on/off 제어 원자 | SwitchField 안의 기능 활성화 control | 저장이 필요한 일반 입력 또는 설명 없는 업무 옵션 | on/off/disabled | 단독 표본은 aria-label, 실제 설정은 SwitchField 문구 연결 | control 크기 유지 | SwitchField, SettingsPage | `design.md §6` | 알림 사용 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | atom |
| Badge | 상태·분류 라벨 | 행 상태, 카테고리 | 주요 행동 | default/secondary/destructive/success/warning/outline | 색 외 텍스트 병기 | 줄바꿈보다 축약 규칙 적용 | StatusDisplay, DataTable | `design.md §6.4` | `승인 대기` | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | atom |
| Avatar | 사람·조직을 빠르게 식별하는 보조 시각 정보 | 직원 목록, 담당자, 사용자 영역 | 이름이나 상태를 대신하는 유일한 정보 | image/fallback; sm/default/lg; loading | 이미지 대체 텍스트 또는 fallback 전체 이름을 접근 가능한 이름으로 제공 | 밀도에 따라 24/32/40px을 선택하고 축소 시 이름 텍스트를 우선 유지 | DataTable, StaffSummary, Badge | `design.md component.avatar` | 직원 이니셜 fallback + 이름·역할 | 2026-09-12 | 2026-09-13 | 2026-09-13T01:24:33+09:00 | atom |
| Card | 관련 정보 묶음 | 요약, 메트릭, 절차, 준비 상태, 섹션 | 모든 내용을 중첩 카드화 | default/interactive/card-banded/metric; loading/error | heading 구조 | 4→2→1열 또는 본문 단일 열 | DashboardPage, MetricOverview, WorkflowSteps, ReadinessChecklist, DetailSection | `design.md §6.3` | 정체성 띠는 card-banded 안에 포함, 음수 margin 금지 | 2026-09-11 | 2026-09-18 | 2026-09-18T13:00:00+09:00 | composition |
| Table | 구조화된 비교 데이터 | 목록, 이력, 메타 정보 | 단일 필드 상세 | 채움형 header, 선택적 2단 column-group band; loading/empty/error | caption 또는 region label, colgroup + header scope/colgroup | wrapper 가로 스크롤; 열 숨김 기준 문서화 | DataTable, Pagination | `design.md §6.8` | 환자 / 간기능(AST·ALT) / 신장(판정) | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Tabs | 2~5개 동급 영역 전환 | 같은 맥락의 상위 섹션 | 페이지 내비게이션 대체 | default; active/disabled | tab/tabpanel 관계, arrow keys | 넘치면 허용된 대안 사용 | DetailPage | `design.md §6` | 기본정보/이력 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Dialog | 짧은 확인·수정 | 집중 입력, 세부 확인 | 복잡한 보조 정보·모바일 장문 | default; open/closed/submitting/error | 제목 행 x IconButton, focus trap, Esc, return focus | 좁은 화면은 Sheet/Drawer 판정 | ConfirmAction, FormSection | `design.md §6.7` | 사용자 수정 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Sheet | 복잡한 보조 정보 | 데스크톱 측면 패널, 모바일 내비 | 단순 확인 | left/right; open/closed/loading | modal focus 규칙 | Sidebar 모바일 전환에 사용 | AppShell, DetailSection | `design.md §6.7` | 필터 상세 | 2026-09-11 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| Drawer | 모바일 중심 보조 작업 | 모바일 장문·단계 입력 | 데스크톱 기본 확인 | bottom; open/closed | focus/Esc/return | 모바일 우선 | FormSection | `design.md §6.9` | 모바일 추가 옵션 | 2026-09-11 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| Tooltip | 짧은 보조 설명 | 아이콘 의미 보충 | 핵심 정보·오류 메시지 | top/right/bottom/left | focus에서도 노출 | 터치만으로 의존 금지 | IconButton | `design.md §6` | 아이콘 설명 | 2026-09-11 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| Pagination | 긴 목록 페이지 이동 | 서버/클라이언트 페이지 목록 | 항목이 적거나 무한 스크롤 | page/prev/next/disabled | 현재 페이지 aria-current | 모바일 축약 | DataTable, PaginationArea | `design.md §6` | 1 2 3 다음 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Breadcrumb | 계층 위치·상위 이동 | 2단 이상 정보 계층 | 단일 레벨 앱 탭 | current/ancestor | nav label, current page | 중간 항목 축약 | PageHeader, DetailPage | `design.md §6` | 사용자 > 홍길동 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Alert | 중요한 인라인 상태 | 오류, 경고, 성공·안내 | 장식용 색면 | default/destructive/warning/success soft surface | role은 긴급도에 맞춤, 아이콘+텍스트 | 컨테이너 폭에 맞춤 | ErrorState, FormSection | `design.md §6, §7` | 조회 실패 + 재시도 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Skeleton | 최초 로딩 자리 보존 | 카드·표 초기 조회 | 기존 데이터가 있는 부분 로딩 | text/card/table | busy 영역 이름 | 실제 레이아웃과 동일 | LoadingState | `design.md §7` | 표 행 skeleton | 2026-09-11 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | atom |
| Spinner | 짧은 진행 표시 | 버튼 제출, 작은 영역 | 전체 화면 자리 보존 | sm/default | 상태 텍스트 병기 | inline 유지 | Button, PartialLoading | `design.md §7` | 저장 중 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | atom |
| Empty | 결과 없음과 다음 행동 | 검색 결과 없음, 최초 데이터 없음 | 네트워크 오류 | default/search | 제목·설명·CTA | 좁은 화면 CTA stack | EmptyState | `design.md §7` | 조건 초기화 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Progress | 진행률·부분 로딩 | 업로드, 증분 처리 | 알 수 없는 짧은 대기 | determinate/indeterminate | 값/설명 제공 | full width | PartialLoading | `design.md §7` | 60% 처리 | 2026-09-11 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | atom |
| BarChart | 항목 간 수치 비교 시각화 | 대시보드 카드 안에서 부서·분류별 지표를 막대로 비교 | 시간 흐름에 따른 추이(LineChart) 또는 단일 진행률(Progress) | default; loading/empty/error | `role="img"` + 요약 `aria-label`, 세부 값은 인접 Table로 병행 제공 | 컨테이너 폭에 맞춰 `viewBox` 스케일, 최소 높이 유지 | Card, Table, LineChart, MetricOverview | `design.md §6.16` | 부서별 민원 건수 막대 | 2026-09-16 | 2026-09-16 | 2026-09-16T16:00:00+09:00 | atom |
| LineChart | 시간 흐름에 따른 추이 시각화 | 대시보드 카드 안에서 기간별 지표 변화를 선으로 표현 | 항목 간 단순 비교(BarChart) 또는 단일 진행률(Progress) | default; loading/empty/error | `role="img"` + 요약 `aria-label`, 세부 값은 인접 Table로 병행 제공 | 컨테이너 폭에 맞춰 `viewBox` 스케일, 최소 높이 유지 | Card, Table, BarChart, MetricOverview | `design.md §6.16` | 월별 만족도 추이 선 | 2026-09-16 | 2026-09-16 | 2026-09-16T16:00:00+09:00 | atom |
| Toast | 비차단 완료 피드백 | 저장·복사 성공 | 복구가 필요한 오류 설명 | success/error/info | live region | scrollbar 폭을 더한 화면 가장자리 안전영역 | SuccessState | `design.md §7` | 저장 완료 | 2026-09-11 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| Icon | 100종 이상 canonical SVG 시각 원자 | Guide Icon Library에서 검색해 버튼·상태·메뉴에 재사용 | 단독으로 의미나 행동을 전달 | sprite catalog; 14/16/18px | 장식은 aria-hidden, 정보성은 접근 가능한 이름 | 부모 크기 규칙을 따름 | IconButton, IconTextButton, Badge | icons.md + nhimc-icons.svg | search, plus, x, help-circle, hospital | 2026-09-12 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | atom |
| IconTextButton | 아이콘과 문구가 함께 있는 행동 | 등록·추가·내보내기처럼 행동 인지와 스캔을 함께 높일 때 | 아이콘만 충분한 utility 또는 텍스트만으로 명확한 행동 | leading/trailing icon; Button variants/sizes/states 상속 | 문구가 accessible name을 제공하고 장식 아이콘은 aria-hidden | 좁은 화면에서도 핵심 문구 유지, 숨기면 IconButton으로 전환 | Icon, Button | design.md §6.1 | plus 아이콘 + 직원 등록 | 2026-09-12 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Label | 컨트롤 이름 원자 | Input·Select·Textarea에 보이는 이름 | 설명·오류·그룹 제목 | default/disabled/error | for/htmlFor 또는 primitive 연결 | 줄바꿈 허용, control과 8px 이내 | Field, Input, Select, Textarea | design.md §6.13 | 직원명 | 2026-09-12 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | atom |
| Field | 라벨·제어·설명·오류 조합 | 폼의 완성된 단일 입력 단위 | 필터 toolbar의 label-free control 또는 control 원자 확인 | horizontal/vertical; default/error/disabled | label과 control 연결, help/error aria-describedby, aria-invalid | 모바일 vertical, desktop grid 배치 | Label, Input, Select, Textarea | design.md §6.13 | 직원명 + Input + 도움말 | 2026-09-12 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Textarea | 여러 줄 입력 원자 | 메모, 사유, 상세 설명 | 한 줄 값 또는 선택지 | default/error/disabled; resize-y | 단독 표본은 aria-label, 업무 폼은 Field 사용 | 최소 높이 유지, 부모 폭 사용 | Label, Field | design.md §6.13 | 변경 사유 | 2026-09-12 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | atom |
| SelectField | Label·Select·설명·오류 조합 | 상태·분류 선택의 완성 필드 | Select 원자 또는 많은 값 검색 | default/error/disabled | label 연결, help/error aria-describedby | 모바일 full width 허용 | Label, Select, Field | design.md §6.13 | 고용 상태 + Select | 2026-09-12 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| CheckboxField | Checkbox와 문구의 한 옵션 | 약관·행 옵션처럼 문구를 눌러도 선택되어야 할 때 | 문구 없는 표 원자 또는 여러 옵션 그룹 | checked/unchecked/indeterminate/disabled | label 클릭 영역과 control 이름 연결 | control과 문구를 한 hit area로 유지 | Checkbox, CheckboxGroup | design.md §6.5 | 야간 근무 가능 | 2026-09-12 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| CheckboxGroup | 복수 CheckboxField 그룹 | 한 질문에서 여러 옵션을 선택 | 단일 boolean 또는 표 행 선택 | horizontal/vertical; disabled | fieldset/legend 또는 group accessible name | 모바일 vertical stack | CheckboxField, FormSection | design.md §6.5 | 가능 근무 유형 복수 선택 | 2026-09-12 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| RadioField | Radio와 문구의 한 옵션 | 문구를 눌러도 선택되는 상호배타 option | 독립 Radio 원자 또는 전체 선택 질문 | checked/unchecked/disabled | label과 radio 연결 | control과 문구를 한 hit area로 유지 | Radio, RadioGroup | design.md §6.5 | 자동 생성 | 2026-09-12 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| RadioGroup | RadioField 상호배타 그룹 | 2~5개 가시적 선택지 중 하나 | 많은 옵션 또는 화면 영역 전환 | horizontal/vertical; required/disabled | fieldset/legend, arrow-key selection | 좁은 화면 vertical stack | RadioField, FormSection | design.md §6.5 | 생성 방식: 자동/수동 | 2026-09-12 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| SwitchField | Switch와 상태 문구 조합 | 즉시 반영 설정을 이름·현재 상태와 함께 표시 | 저장 후 반영 입력 또는 Switch 원자 | on/off/disabled | 보이는 label과 aria-checked, 상태 문구 동기화 | 한 행 유지, 설명은 아래 배치 | Switch, SettingsPage | design.md §6.5 | 알림 사용 중 | 2026-09-12 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| ButtonGroup | 연관 행동·제어 묶음 | 보기 전환, 이전/다음, 붙어 있는 action set | 서로 무관한 주요 행동 | horizontal/vertical; attached/separated | 그룹 이름, 각 Button 이름 유지 | 좁은 화면 wrap 또는 vertical | Button, IconButton, IconTextButton | design.md §6.16 | 목록/카드 보기 전환 | 2026-09-12 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| InputGroup | 입력과 prefix/suffix action 조합 | 검색 아이콘, 단위, 지우기 버튼이 입력과 한 덩어리일 때 | 일반 label·help·error만 필요한 Field | prefix/suffix; input/button/addon | 내부 Input 이름과 IconButton 이름 유지 | 부모 폭 사용, addon 축소 금지 | Input, Icon, IconButton, Field | design.md §6.13 | 검색 Input + 지우기 IconButton | 2026-09-12 | 2026-09-15 | 2026-09-15T08:40:52+09:00 | composition |
| StatusIndicator | 상태 점과 상태 문구 조합 | 시스템 준비·처리·경고·오류 상태 | 상세 원인과 복구 행동이 필요한 Alert | ready/success/warning/error/processing | 색과 문구를 병기하고 live 필요 여부를 상태 긴급도로 결정 | 한 줄 말줄임, 점 크기 유지 | Badge, Alert, StatusDisplay | design.md §2, §7 | 초록 점 + 준비됨 | 2026-09-12 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | composition |
| Separator | 콘텐츠 구획선 원자 | 같은 surface 안의 관련 영역 구분 | Card를 대신하는 구조 분리 | horizontal/vertical | 장식이면 aria-hidden, 의미 구분이면 separator role | 부모 축과 길이를 따름 | Card, ButtonGroup, InputGroup | design.md §6.8 | 필터와 결과 요약 구분 | 2026-09-12 | 2026-09-12 | 2026-09-12T22:53:39+09:00 | atom |
| Scrollbar | 앱 내부 scroll owner의 공통 스크롤 표현 원자 | Main·Navigation·Dialog body·Table wrapper처럼 내용이 넘치는 영역 | 장식용 막대 또는 페이지마다 다른 색·폭 지정 | vertical/horizontal; light/dark; default/hover | 브라우저 스크롤 동작·키보드 접근은 유지하고 시각만 토큰화 | 10px, 투명 track, 세로 owner만 stable gutter | AppShell, Table, Dialog, Drawer | `design.md §6.15` | 예전 TOP처럼 중립 회색 thumb가 적용된 세로 scroll owner | 2026-09-13 | 2026-09-13 | 2026-09-13T00:45:33+09:00 | atom |
| HeatmapTable | 도메인×기간 격자의 값 강도를 색 농도로 비교 | 병동·부서×월별 지표를 한눈에 훑어보는 대시보드 | 정확한 값 비교가 우선인 목록(Table) 또는 단일 계열 추이(LineChart) | default; loading/empty/error | `scope="row"/"col"` 표 시맨틱 + 셀 값 텍스트 병기, 색만으로 강도를 전달하지 않음 | 컨테이너 폭에 맞춰 열 축소, 좁은 화면은 가로 스크롤 wrapper | Table, BarChart, LineChart, Card | `assets/components/showcase.html` · 참고: `references/baseline/환자경험_데이터허브_통합포털.html` | 병동별 월별 만족도 히트맵 | 2026-09-17 | 2026-09-17 | 2026-09-17T10:00:00+09:00 | atom |
| CommentList | 키워드 태그가 붙은 자유 의견(VOC) 카드 목록 | 정성적 피드백·의견 수집 화면의 목록 영역 | 정형 데이터 비교(Table) | default; loading/empty/error | 목록은 `<ul>`, 항목은 인용문+메타(날짜·출처) 구조 유지 | 카드 폭에 맞춰 줄바꿈, 태그는 줄바꿈 허용 | Card, Badge, EmptyState | `assets/components/showcase.html` · 참고: `references/baseline/환자경험_데이터허브_통합포털.html` | 키워드 태그 + 의견 인용 + 병동·일자 | 2026-09-17 | 2026-09-17 | 2026-09-17T10:00:00+09:00 | composition |
| UploadDropzone | 파일 드래그앤드롭 업로드 + 선택 파일 확인 | 대량 업로드가 필요한 화면의 파일 선택 영역 | 단일 값 입력(Input), 진행률만 필요한 경우(Progress) | idle/dragover/filled/uploading/error | 점선 드롭 영역 전체가 실제 `<button>` 파일 선택 트리거(별도 "찾아보기" 버튼 없음)이며 숨은 `<input type="file">`를 열어 실제 OS 파일 선택창을 사용, 드롭·선택된 실제 파일명을 상태 변화와 함께 병기 | 좁은 화면에서도 버튼 hit area 유지 | Icon, Button, Progress, Alert | `assets/components/showcase.html` · 참고: `references/baseline/환자경험_데이터허브_통합포털.html` | 엑셀 업로드 드롭존(전체 클릭 가능, 실제 파일 선택창 연동) + 선택 파일 목록 | 2026-09-17 | 2026-09-17 | 2026-09-17T17:00:00+09:00 | composition |
| FloatingPanel | 비모달·이동 가능한 보조 패널 | 그리드/캔버스 위에서 본문 조작을 막지 않고 열어두는 보조 정보(교환 제안, 계산 결과) | 화면 흐름을 막아야 하는 확인(Dialog), 항상 고정 위치인 보조 정보(Sheet) | open/closed/dragging | 제목·닫기 IconButton 제공, Esc로 닫기, 이동 손잡이는 장식 아이콘 + 키보드 대체 동작 | 모바일에서는 화면 폭을 넘지 않게 고정 위치로 대체 | Card, IconButton, Icon | `assets/components/showcase.html` · 참고: `references/baseline/nurse_scheduler_ai_v2.9_신규간호사_UI정리(한소라).html` | 근무 교환 제안 목록 플로팅 패널 | 2026-09-17 | 2026-09-17 | 2026-09-17T10:00:00+09:00 | composition |
| ChatPanel | 업무 보조 어시스턴트 메시지 패널 | 생성·분석 화면에서 맥락 질문·제안을 주고받는 보조 패널 | 일반 알림(Toast), 짧은 확인(Dialog) | ready/sending/disabled | 메시지 목록은 `aria-live="polite"`, 입력은 accessible name 필수 | 좁은 화면에서는 전체 폭 패널로 전환 | InputGroup, StatusIndicator | `assets/components/showcase.html` · 참고: `references/baseline/nurse_scheduler_ai_v2.9_신규간호사_UI정리(한소라).html` | 근무표 생성 어시스턴트 채팅(입력·전송은 InputGroup 재사용) | 2026-09-17 | 2026-09-17 | 2026-09-17T14:00:00+09:00 | composition |
| ScheduleGrid | 규칙 위반·희망휴무·잠금·교환 상태를 표시하는 편집형 근무표 격자 | 근무표 생성·검토 화면의 핵심 편집 영역 | 단순 값 비교만 필요한 목록(Table) | default; selected/locked/rule-violation/wish-violation/swap | 표 시맨틱(`scope`) 유지, 상태는 색+아이콘/문양+범례 텍스트로 병행 전달, 셀은 키보드 포커스 가능 | 좁은 화면은 가로 스크롤 wrapper, 열 수는 그대로 유지 | Table, chart-legend/chart-legend-swatch(`design.md §6.16`) | `assets/components/showcase.html` · 참고: `references/baseline/nurse_scheduler_ai_v2.9_신규간호사_UI정리(한소라).html` | 주간 근무표 격자 + `chart-legend-swatch`(8px) 상태 범례 | 2026-09-17 | 2026-09-17 | 2026-09-17T14:00:00+09:00 | composition |
| QuadrantMatrix | 두 평가축(예: 영향도×실현 가능성)의 2x2 사분면에 항목을 배치해 우선순위를 시각화 | 여러 과제·항목을 두 기준으로 동시에 비교해 우선순위 구간을 정할 때 | 단일 계열 비교(BarChart) 또는 시간 추이(LineChart), 3개 미만 항목 비교 | default; loading/empty/error | 사분면 순위·기준을 텍스트 배지로 병기하고 X·Y축 이름을 시각 위치와 함께 텍스트로 제공, 색만으로 순위를 전달하지 않음 | 컨테이너 폭에 맞춰 격자 축소, 좁은 화면은 축 라벨을 위/아래로 재배치 | Card, Badge, BarChart, LineChart | `assets/components/showcase.html` · 참고: `references/baseline/[AX 추진부] AI Agent 인터뷰 OT 자료.html` | 업무 영향도×실현 가능성 2x2 우선순위 매트릭스 | 2026-09-17 | 2026-09-17 | 2026-09-17T18:00:00+09:00 | atom |

## 선택 원칙

- 독립 제어·표현은 atom을, 라벨·문구·도움말·오류·그룹·아이콘 결합으로 별도 접근성 계약이 생기면 composition을 선택한다.
- 아이콘만 있는 행동은 `IconButton`, 아이콘과 문구가 함께 있는 업무 행동은 `IconTextButton`을 사용한다.
- 사용자에게 보이는 선택 문구가 있으면 `RadioField`/`CheckboxField`/`SwitchField`, 한 질문의 여러 선택지는 `RadioGroup`/`CheckboxGroup`을 사용한다. `Radio`/`Checkbox`/`Switch` atom을 화면에서 label과 반복 조합하지 않는다.
- 보이는 label·help·error가 있는 입력은 `Field`/`SelectField`, prefix·suffix action이 한 control surface를 이루면 `InputGroup`을 사용한다.
- `Select`: 여러 상태 값 중 하나. `Tabs`: 2~5개의 동급 화면 영역 전환.
- `Dialog`: 짧은 확인/수정. `Sheet/Drawer`: 복잡한 보조 정보 또는 모바일 장문.
- 삭제·철회는 destructive Button만으로 즉시 실행하지 않고 `ConfirmAction`을 사용한다.
- 기존 데이터가 보이는 추가 조회는 화면 전체 Skeleton 대신 partial loading을 사용한다.

## Component Implementation Contract

### canonical_source 결정

1. 대상 프로젝트 import 사용처에서 정확한 Component 이름을 찾는다.
2. 찾지 못하면 아래 Alias Index의 별칭과 같은 목적의 UI를 검색한다.
3. 공용 UI 디렉터리와 동일 화면의 기존 import를 확인한다.
4. 실제 파일이 존재할 때만 그 경로를 작업 보고의 `canonical_source`로 기록한다.
5. 실제 구현이 없으면 현재 프로젝트의 shadcn/new-york-v4 primitive를 확인하고, 그래도 없을 때만 기존 Pattern 조합 또는 신규 후보를 검토한다.

Golden HTML의 `<button>`, `<input>`, `<select>`, `<table>`은 시각·배치 참고다. React/Vue/Svelte 프로젝트에 Button/Input/Select/Table이 있으면 raw element를 복사하지 않고 해당 canonical Component를 사용한다.

### Variant·Size·State·Token 계약

| id | allowed_variants | allowed_sizes | states | token_dependencies | composition_rules |
|---|---|---|---|---|---|
| Button | primary, secondary, outline, ghost, ghost-subtle, destructive | sm, default, lg, icon | default, hover, focus, loading, disabled | primary, secondary, destructive, border-accent, foreground, accent, ring, radius-md | 주 행동은 화면당 과도하게 늘리지 않고 PageHeader/ActionArea 위치를 따른다. `ghost`는 `--color-border-accent` 외곽선 + foreground 텍스트를 쓰는 헤더·툴바 유틸리티 전용이고, `ghost-subtle`은 `--color-destructive` 채움 배경 + 흰 텍스트(destructive Button과 같은 red 채움)를 쓰는 SearchFilter 초기화 전용이다 — Primary/조회 Action과 뚜렷이 구분되어야 하는 행동에만 쓰고 서로 대체하지 않는다. |
| Input | default, error | default | default, focus, error, disabled | background, foreground, input, ring, radius-md | Field label·help/error와 조합하며 너비만 부모 Layout이 정한다. |
| Select | default, error | default | closed, open, focus, error, disabled | background, foreground, border-accent, ring, radius-md | 닫힌 트리거는 흰 surface이며 SearchFilter/FormSection 안에서 사용한다. border는 `--color-border-accent`이며 Input의 `--color-input`과 섞어 쓰지 않는다. 자체 포함 HTML은 `appearance:none`/`-webkit-appearance:none`으로 OS 기본 arrow를 숨기고, `--color-ring` 색상 chevron을 오른쪽 안쪽 11~12px 중심에 그리며, 오른쪽 padding을 최소 36px 확보해 chevron과 텍스트가 겹치지 않게 한다. |
| Checkbox | default | default | checked, unchecked, indeterminate, focus, disabled | primary, ring, foreground | 자체 포함 HTML은 16px native control과 primary `accent-color`를 유지하고 일반 Input의 width·height·padding을 상속하지 않는다. |
| Radio | default | default | checked, unchecked, focus, disabled | primary, ring, foreground | 자체 포함 HTML은 16px native control과 primary `accent-color`를 유지하고 일반 Input의 width·height·padding을 상속하지 않는다. |
| Table | default, column-group | comfortable, dense | loading, empty, error, partial-loading | card, foreground, border-accent, secondary, band-* | DataTable Pattern이 wrapper·header·row·상태·PaginationArea를 소유하며 row hover는 band-sky 계열을 사용한다. |
| Card | default, interactive, card-banded | default | default, hover, loading, error | card, card-foreground, border-accent, radius-xl | 중첩을 피하고 섹션 간격은 부모가 소유한다. |
| Tabs | default | default | active, hover, focus, disabled | primary, foreground, border-accent, ring | 같은 맥락의 2~5개 동급 영역에만 사용한다. |
| Badge | default, secondary, outline, success, warning, destructive | default | default | semantic surface/border/foreground | 상태 텍스트를 생략하지 않고 StatusDisplay/DataTable 안에서 사용한다. |
| Avatar | image, fallback | sm, default, lg | loaded, fallback, loading | muted, muted-foreground, border-accent, rounded-full | 사진은 대체 텍스트를 제공하고 fallback은 이니셜만 보이더라도 전체 이름을 접근 가능한 이름으로 제공한다. Avatar는 이름·역할 텍스트를 대체하지 않는다. |
| Pagination | page, previous, next | default, icon | current, hover, focus, disabled | primary, card, foreground, border-accent, secondary, ring | DataTable 아래 PaginationArea에서만 화면 간 동일 구조로 사용한다. 라이트 비활성은 card/foreground/border-accent, hover는 secondary, 현재 페이지는 primary/primary-foreground를 사용한다. |
| Dialog | default | sm, default | open, closed, submitting, error | background, foreground, border, overlay, radius-lg | 짧은 집중 편집은 제목 행 오른쪽 canonical x IconButton과 주 action을 사용한다. 명시적 닫기가 있으면 동일 의미의 footer 취소 버튼을 중복하지 않는다. 파괴적 확인은 Alert Dialog의 취소·확인 두 action을 유지한다. |
| IconButton | ghost | icon | default, hover, focus, toggled | foreground, secondary, ring, radius-md | 36px hit area 안에 18px canonical SVG를 중앙 정렬하고 라벨은 aria-label·title로 제공한다. |
| Icon | canonical | 14px, 16px, 18px | default | foreground, semantic status color | 장식 아이콘은 aria-hidden, 정보성 아이콘은 접근 가능한 이름을 제공하고 부모가 의미를 소유한다. |
| IconTextButton | Button variants | sm, default, lg | default, hover, focus, loading, disabled | Button + Icon | 문구가 accessible name을 제공하고 장식 Icon은 aria-hidden으로 둔다. |
| Label | default | default | default, disabled, error | foreground, destructive | for/htmlFor로 제어와 연결하며 설명·오류 역할을 대신하지 않는다. |
| Field | vertical, horizontal | default | default, focus-within, error, disabled | Label + Input/Select/Textarea + muted/destructive | label, control, help/error ID와 aria-describedby·aria-invalid 배선을 소유한다. |
| Textarea | default, error | default | default, focus, error, disabled | background, foreground, input, ring, radius-md | 여러 줄 원자이며 업무 폼에서는 Field 안에 둔다. |
| SelectField | default | default | default, focus-within, error, disabled | Label + Select | Select의 label·help/error 연결을 소유한다. |
| CheckboxField | default | default | checked, unchecked, indeterminate, disabled | Checkbox + Label | 문구 전체를 클릭 영역으로 만들고 control 이름을 연결한다. |
| CheckboxGroup | horizontal, vertical | default | default, disabled | CheckboxField | fieldset/legend 또는 동등한 group 이름으로 질문과 옵션을 묶는다. |
| RadioField | default | default | checked, unchecked, disabled | Radio + Label | 문구 전체를 클릭 영역으로 만들며 RadioGroup 안에서 사용한다. |
| RadioGroup | horizontal, vertical | default | default, required, disabled | RadioField | 하나의 이름과 상호배타 선택·키보드 이동을 소유한다. |
| SwitchField | default | default | on, off, disabled | Switch + Label | 보이는 이름과 현재 상태 문구를 aria-checked와 동기화한다. |
| ButtonGroup | attached, separated | default | default, disabled | Button, IconButton, IconTextButton | 관련 action만 group 이름 아래 묶고 무관한 주요 행동은 합치지 않는다. |
| InputGroup | prefix, suffix | default | default, focus-within, error, disabled | Input + Icon/IconButton/addon | 하나의 control surface로 보이는 prefix/suffix와 내부 이름·focus를 유지한다. |
| StatusIndicator | ready, success, warning, error, processing | default | static, live | success, warning, destructive, primary | 상태 점과 문구를 항상 병기하고 긴급도에 맞는 live semantics를 선택한다. |
| Separator | horizontal, vertical | default | default | border | 장식이면 aria-hidden, 의미 구획이면 separator role을 쓴다. |
| Scrollbar | vertical, horizontal | 10px | default, hover | scrollbar-thumb, scrollbar-thumb-hover, scrollbar-track | native/Radix 스크롤 동작은 유지하고 시각만 토큰화한다. 세로 Main·Navigation·Dialog body는 stable gutter를 예약하며 가로 전용 Table wrapper에는 예약하지 않는다. |
| QuadrantMatrix | default | default | default, loading, empty, error | card, border-accent, chart-1..5, foreground, muted-foreground | 4개 사분면 순위 배지는 Badge 계열(success/warning/secondary/outline)만 재사용하고 새 색을 만들지 않는다. 인접 기준 설명 Card와 조합해 축·판단 기준을 텍스트로 함께 제공한다. |

Component 내부에 캡슐화된 높이·색·radius를 화면 코드에서 다시 지정하지 않는다. `className`은 width, flex, grid placement 같은 배치 목적으로 제한한다.

### Alias / Search Keyword Index

| canonical id | aliases / search_keywords |
|---|---|
| Button | ActionButton, PrimaryButton, SubmitButton, TextButton |
| Icon | SvgIcon, LucideIcon, StatusIcon |
| IconButton | ActionIcon, UtilityButton, IconOnlyButton |
| IconTextButton | ButtonWithIcon, LeadingIconButton, TrailingIconButton |
| Input | TextField, SearchInput, TextInput |
| Label | FieldLabel, FormLabel |
| Field | FormField, InputField, FieldWrapper |
| Textarea | TextArea, MultilineInput |
| Select | Dropdown, SelectTrigger, Combobox |
| SelectField | LabeledSelect, DropdownField |
| CheckboxField | LabeledCheckbox, CheckboxItem |
| CheckboxGroup | MultiChoiceGroup, CheckboxList |
| RadioField | LabeledRadio, RadioItem |
| RadioGroup | SingleChoiceGroup, RadioList |
| SwitchField | LabeledSwitch, SettingSwitch |
| ButtonGroup | ActionGroup, SegmentedButtons |
| InputGroup | InputAddon, SearchField, InputWithButton |
| StatusIndicator | StatusDot, SystemStatus, ReadinessStatus |
| Separator | Divider, Rule |
| Scrollbar | ScrollArea, ScrollThumb, OverflowArea |
| Table | DataGrid, ResultTable, ListTable |
| Pagination | Pager, PageNav, PaginationControl |
| Tabs | TabList, SegmentedTabs, SectionTabs |
| Dialog | Modal, ConfirmDialog, AlertDialog |
| Card | Panel, SectionCard, Surface |
| Badge | StatusBadge, Tag, Chip |
| Avatar | UserAvatar, StaffAvatar, ProfileImage, Initials |
| QuadrantMatrix | PriorityMatrix, ImpactMatrix, TwoByTwoMatrix, EffortImpactGrid |

Pattern 별칭은 `../patterns/registry.md`에서 목적을 대조한다. 예를 들어 SearchFilter를 찾지 못하면 SearchForm, SearchBar, FilterBar, QueryFilter, ListFilter를 검색하고, DataTable을 찾지 못하면 DataGrid, ResultTable, TableSection을 검색한다.

## 실제 구현 Mapping

수정 대상 프로젝트에서 아래 순서로 실제 파일을 찾는다: import 사용처 → 공용 UI 디렉터리 → route 로컬 컴포넌트. 목적이 같은 구현이 있으면 Registry 이름으로 새 파일을 만들지 않고 그 구현을 재사용한다. 아래 `확인된 public 구현`이 실제 `canonical_source` 후보이며, 분석에 사용한 `ui-main` 루트에서 존재가 확인된 경로다. 표에 없는 Component는 canonical_source 미지정 상태이며 다른 프로젝트에 같은 경로가 있다고 가정하지 않는다.

| design item | 확인된 public 구현 |
|---|---|
| Button / Input / Select / Textarea / Label / Field / Table / Badge / Avatar / Card / Separator | `apps/v4/registry/new-york-v4/ui/button.tsx`<br>`apps/v4/registry/new-york-v4/ui/input.tsx`<br>`apps/v4/registry/new-york-v4/ui/select.tsx`<br>`apps/v4/registry/new-york-v4/ui/textarea.tsx`<br>`apps/v4/registry/new-york-v4/ui/label.tsx`<br>`apps/v4/registry/new-york-v4/ui/field.tsx`<br>`apps/v4/registry/new-york-v4/ui/table.tsx`<br>`apps/v4/registry/new-york-v4/ui/badge.tsx`<br>`apps/v4/registry/new-york-v4/ui/avatar.tsx`<br>`apps/v4/registry/new-york-v4/ui/card.tsx`<br>`apps/v4/registry/new-york-v4/ui/separator.tsx` |
| Radio / Checkbox / Switch / ButtonGroup / InputGroup | `apps/v4/registry/new-york-v4/ui/radio-group.tsx`<br>`apps/v4/registry/new-york-v4/ui/checkbox.tsx`<br>`apps/v4/registry/new-york-v4/ui/switch.tsx`<br>`apps/v4/registry/new-york-v4/ui/button-group.tsx`<br>`apps/v4/registry/new-york-v4/ui/input-group.tsx` |
| Dialog / Sheet / Drawer / Tooltip | `apps/v4/registry/new-york-v4/ui/dialog.tsx`<br>`apps/v4/registry/new-york-v4/ui/sheet.tsx`<br>`apps/v4/registry/new-york-v4/ui/drawer.tsx`<br>`apps/v4/registry/new-york-v4/ui/tooltip.tsx` |
| Sidebar | `apps/v4/registry/new-york-v4/ui/sidebar.tsx` |
| App Sidebar / SiteHeader | `apps/v4/registry/new-york-v4/blocks/dashboard-01/components/app-sidebar.tsx`<br>`apps/v4/registry/new-york-v4/blocks/dashboard-01/components/site-header.tsx` |
| dashboard composition | `apps/v4/registry/new-york-v4/blocks/dashboard-01/components/section-cards.tsx`<br>`apps/v4/registry/new-york-v4/blocks/dashboard-01/components/data-table.tsx`<br>`apps/v4/registry/new-york-v4/blocks/dashboard-01/components/chart-area-interactive.tsx` |
| login composition | `apps/v4/registry/new-york-v4/blocks/login-01/components/login-form.tsx` |

헤더 내비형 앱 셸, statusbar, help drawer는 `design.md`에 명시된 `[EXT]`이므로 위 ui-main 원형 경로를 꾸며내지 않는다. 소비 프로젝트에 이미 구현되어 있으면 그 실제 경로를 기록해 재사용하고, 없으면 기존 토큰과 Shell 규칙을 조합한다.
