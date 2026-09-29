# Component Selection

신규 UI를 만들기 전에 Catalog 계약을 확인하고 대상 프로젝트와 Registry를 차례로 검색한다.

## 검색 순서

1. 대상 프로젝트에서 정확한 Component 이름과 import 사용처를 찾는다.
2. `components/registry.md`의 alias/search keyword로 찾는다.
3. 목적과 역할이 비슷한 Component/Pattern을 찾는다.
4. 기존 화면에서 동일한 UI가 사용된 사례를 찾는다.

실제 파일이 존재하는 경로만 `canonical_source`로 기록한다. 기존 Component가 있으면 Golden HTML의 raw element를 production 구현으로 복사하지 않는다.

## 판단 규칙

- 독립 제어·표현만 필요하면 `layer=atom`, 라벨·문구·도움말·그룹·아이콘 결합처럼 별도 접근성 계약이 생기면 `layer=composition`을 선택한다.
- 문구 없는 Radio/Checkbox/Switch 원자가 아니라 사용자가 읽고 누르는 옵션이면 RadioField/CheckboxField/SwitchField를 사용하고, 질문 단위의 여러 옵션이면 RadioGroup/CheckboxGroup을 사용한다.
- 아이콘만 있는 행동은 IconButton, 아이콘과 문구를 함께 유지해야 하는 업무 행동은 IconTextButton을 사용한다.
- Label·help·error가 있는 입력은 Input/Select/Textarea 원자를 화면에서 즉석 조합하지 않고 Field/SelectField를 우선한다.
- 여러 상태 값 중 하나 선택: Select.
- 2~5개 동급 화면 영역 전환: Tabs.
- 짧은 확인·수정: Dialog.
- 복잡한 보조 정보: Sheet, 모바일 중심이면 Drawer.
- 검색 목록: SearchFilter + DataTable.
- 삭제·철회·권한 회수: ConfirmAction + destructive Button.
- 데이터 없음: EmptyState. 실패는 ErrorState로 분리.
- 최초 조회: LoadingState. 기존 데이터가 있는 추가 조회: PartialLoading.

## 레이아웃 불일치 해결 순서

canonical Component가 이미 있는데 화면 배치에 맞지 않을 때는 Component 자체를 고치지 않는다. 아래 순서를 위에서부터 시도하고, 위 단계로 해결되면 아래 단계로 내려가지 않는다.

1. **부모 Layout 조정** — Frame/Golden Template의 grid·flex·container 구조를 먼저 본다.
2. **Pattern 조정** — SearchFilter/DataTable 같은 Pattern 내부 배치를 조정한다.
3. **wrapper 조정** — Component를 감싸는 wrapper의 width·flex·grid 배치·간격을 조정한다.
4. **size variant 조정** — Component가 이미 제공하는 sm/default/lg 등 기존 size variant로 바꾼다.
5. **Component 최소 변경(최후 수단)** — 위 네 단계로 해결되지 않을 때만 Component 자체를 최소 변경한다.

5번에서 허용되는 수정은 배치·크기 관련 값뿐이다: `width`, `min-width`/`max-width`, `flex`, `grid` 배치, `column`/`span`, `order`, `margin`, wrapper 간격, 필요하면 기존 size variant 선택. `border`, `radius`, `padding`, `font`, 색상, `hover`/`focus`, native arrow, icon 구조 등 Component의 시각적 정체성을 바꾸는 수정은 이 단계에서도 하지 않는다. 가능하면 Component 자체가 아니라 그 부모 wrapper/layout을 수정한다.

레이아웃 문제가 아니라 정본 Component 자체에 결함이 있다고 판단되면(예: 어떤 배치에서도 겹침이 발생하는 구조적 문제), 화면에서 임시 override로 봉합하지 않고 [Canonical Component Resolution](../SKILL.md#canonical-component-resolution)에 따라 **Canonical Component 개선 대상**으로 분리해 보고한다 — 이 경우도 아래 EXTENSION 게이트와 마찬가지로 화면 하나만 고치고 정본은 그대로 두지 않는다.

## EXTENSION 게이트

다음 질문에 모두 `아니오`일 때만 신규 항목을 후보로 제안한다.

1. 기존 항목으로 구현 가능한가?
2. 기존 Component의 Variant 추가로 가능한가?
3. 기존 Pattern 조합으로 가능한가?
4. 기존 Template Variant로 가능한가?
5. 재사용 가치가 있는 독립 UI 단위인가?

5번까지 해당할 때 후보 이름 앞에 `EXTENSION:`을 붙이고 필요성, 기존 항목으로 불가능한 이유, 토큰 영향, 접근성·반응형·상태 설계를 사용자에게 제시한다. 실제 canonical Component가 생성되면 purpose, 실제 source, variant, states, token dependency, 사용 위치를 Registry에 등록한다. 한 화면의 단순 wrapper는 승격하지 않는다.

신규 등록 시 `layer`를 반드시 `atom` 또는 `composition`으로 기록하고 같은 ID의 Showcase 단독 specimen을 추가한다. composition은 포함하는 atom을 `related_items`에 명시하며, atom과 composition 중 하나만 등록해 다른 층을 화면별 raw markup으로 반복 생성하지 않는다.
