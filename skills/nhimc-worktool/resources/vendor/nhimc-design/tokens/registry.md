# Token Registry

값의 정본은 `../docs/design-docs/design.md` frontmatter이며 `../docs/design-docs/design-tokens.css`는 CSS 미러다. 아래는 선택용 registry다.

| name | purpose | when_to_use | when_not_to_use | related_items | source | example |
|---|---|---|---|---|---|---|
| color-primary | 유일한 브랜드 전압·주요 행동 | primary action, 활성 내비, 링크 | 장식 배경, 분류색 | Button/default, active navigation | `design-tokens.css --color-primary` | `color: var(--color-primary)` |
| color-surface | 업무 화면 바닥과 보조 면 | 앱 배경, muted section | 주요 행동 | Card, AppShell | `--color-surface` | `background: var(--color-surface)` |
| color-card | 콘텐츠 정보 단위 | Card, Dialog, Table container | 페이지 전체 바닥 | Card, DataTable | `--color-card` | `background: var(--color-card)` |
| color-border-accent `[EXT]` | 주요 업무 요소의 옅은 푸른 경계 | Card, Button, Input, Select, Table container | 일반 내부 구분선 | Card, Button, Form, DataTable | `--color-border-accent` | `border: 1px solid var(--color-border-accent)` |
| color-scrollbar `[EXT]` | 예전 TOP native scrollbar에 가까운 중립 회색 스크롤 표시 | Frame/Guide main·nav·dialog·table scroll owner | 푸른 계열 또는 OS 다크 설정에 맡긴 검은 native thumb | Scrollbar atom, Frame, Toast 안전영역 | `--color-scrollbar-thumb/hover/track`, `--scrollbar-inline-size` | 10px neutral thumb + transparent track |
| semantic-state | 성공·경고·오류 의미와 저채도 상태 면 | Badge, Alert, StatusDisplay | 브랜드 장식 | StatusDisplay, Alert | `--color-success/warning/destructive`, `--color-alert-*-bg/border` | 상태 면 + 경계 + 아이콘 + 텍스트 |
| category | 데이터 분류 | 태그·차트 계열 | 버튼·본문·아이콘 | Badge/category, Chart | `--color-category-*` | 분류명 텍스트 병기 |
| sidebar-brand | 브랜드 Sidebar와 메뉴 칩 | 업무 앱 셸 | 본문 카드 전체 | AppShell, Navigation | `--color-sidebar-brand`, `--color-chip-*` | 네이비 면 + 파스텔 칩 |
| table-band | 표 헤더와 의미 있는 열 그룹 | 2단 비교 표·그룹 열 | 줄무늬 행, 모든 셀 세로 격자 | DataTable | `--color-canvas`, `--color-band-*` | colgroup 너비 + 그룹 시작 경계 + 열 그룹 틴트 |
| typography | public의 텍스트 위계 | 모든 텍스트 | 임의 크기·굵기 | 모든 컴포넌트 | `--font-*`, `--type-*` | 본문 400, 제목 토큰 적용 |
| spacing | 일관된 밀도와 리듬 | padding, gap, margin | 임의 px | Template, Pattern | `--space-*` | `gap: var(--space-md)` |
| radius | 컨트롤·표면 모서리 | Button, Input, Card, overlay | 임의 radius | Component registry | `--radius-*` | `border-radius: var(--radius-md)` |
| shadow | 겹치는 표면의 최소 깊이 | Dialog, Dropdown, Toast | 셸 구획·카드 남용 | Overlay patterns | `--shadow-*` | 카드 경계는 border 우선 |
| motion | 상태 전환과 피드백 | overlay, toast, loading | 장식 애니메이션 | reduced-motion rule | `--motion-*` | 정본 max 이하 |
| breakpoint | 셸·콘텐츠 반응형 기준 | media/container query | 임의 breakpoint | responsive rule | `--breakpoint-*`, `--cq-*` | 리터럴은 토큰과 동일해야 함 |

`left-sidebar:v2`는 별도 수치 묶음을 만들지 않고 기존 `{layout.sidebar-width}`, `{layout.sidebar-width-icon}`, `{layout.sidebar-width-mobile}`, `{layout.header-height}`, `{motion.base}`, `{motion.easing}`, `{spacing.lg}`, `{spacing.md}`, `{colors.overlay}`를 참조한다. 최신 LEFT Reference 승격으로 `{layout.sidebar-width-icon}`은 64px이 정본이며 `dashboard-sidebar-width-icon`은 이 값을 가리키는 호환 alias다. Frame 조합과 소유권은 `templates/catalog.yaml.layouts[].canonical_spec`이 담당한다.

## 적용 규칙

- 새 값이 필요해도 코드에서 먼저 만들지 않는다. `design.md` frontmatter에 `EXTENSION` 후보로 제안하고 충돌을 검토한다.
- CSS에는 `design-tokens.css` 변수만 사용한다. 조건식에서 변수 사용이 불가능할 때만 정본과 동일한 breakpoint 리터럴을 허용한다.
- 라이트와 다크 토큰을 함께 검증한다.
- 모든 Frame은 `data-theme`에 맞는 `color-scheme`를 명시한다. 세로 scroll owner는 10px scrollbar와 안정적인 gutter를 쓰며 Toast 같은 fixed overlay는 scrollbar 폭을 더한 inline-end 안전영역을 확보한다.

## Dark Mode와 Theme(Color)은 독립 축이다

Dark Mode는 `design.md` frontmatter `colors:`/`colors-dark:`와 `design-tokens.css`의 기본 라이트/`[data-theme="dark"]` 두 mapping이 정본이며, 위 semantic key 전부를 다크용으로 재정의한다(무채색 중립·상태·분류 포함). Preset/Profile을 새로 만들지 않는다.

Theme(Color)은 이와 다른 축이다. "Pear Light"·"Pear Dark"처럼 Theme × Mode를 독립 조합할 수 있어야 하며, Dark Mode처럼 모든 semantic key를 다시 정의하지 않는다. 모든 Theme은 "색이 있는 자리"인 brand/action 5개 key를 바꾼다. `Color Mix`는 여기에 탐색·분류용 `chip-*` 6개와 각 칩 위 아이콘용 `accent-*-foreground` 6개를 완전한 한 묶음으로 추가 교체한다. background/surface, text, border, status(success/warning/destructive), navigation overlay(`sidebar-brand-10/18` 등), `category-*`/`chart-*`/`band-*`는 계속 공유한다 — 의료 상태 배지의 성공/경고/위험 의미가 Theme에 따라 달라지면 안 되기 때문이다.

## Theme(Color) Registry와 선택 흐름

Theme의 SSOT는 [tokens/themes/catalog.yaml](themes/catalog.yaml)이며, 실제 CSS 값은 `docs/design-docs/design-tokens.css`의 `[data-theme-color="<id>"]` 블록이 미러한다. 대표 렌더 자산은 [assets/themes/preview.html](../assets/themes/preview.html)이다. Layout·Page Template Catalog와 책임을 분리하며 같은 값을 중복 정의하지 않는다.

| Semantic Token Contract(모든 Theme 필수) | 의미 | 공유 여부 |
|---|---|---|
| `primary` | 주요 행동·활성 표식 | Theme마다 다름 |
| `primary-foreground` | primary 면 위 텍스트 | Theme마다 다름 |
| `ring` | 포커스 링 | Theme마다 다름 |
| `primary-90` | 버튼 hover 알파(90%) | Theme마다 다름(primary 파생) |
| `primary-20` | Progress track 알파(20%) | Theme마다 다름(primary 파생) |
| `chip-sky/pear/apricot/yellow/purple/pink/amber` | 메뉴·섹션 탐색용 분류색 | 선택 계약. 사용할 때 전체 key를 Light/Dark 모두 완전하게 정의 |
| `accent-sky/pear/apricot/yellow/purple/pink/amber-foreground` | Color Mix 칩 위 아이콘·짧은 식별 텍스트 | `chip-*`와 1:1 짝으로 Light/Dark 모두 정의 |
| background/surface, text, border | 무채색 중립 | 모든 Theme 공유(기본값) |
| status(success/warning/destructive) | 상태 의미 | 모든 Theme 공유(기본값) |
| navigation(`sidebar-*`), classification(`category-*`/`chart-*`/`band-*`) | 셸·상태와 결합되지 않은 분류색 | 모든 Theme 공유(기본값) |

선택 순서는 다음과 같다.

1. **신규 화면 + 기본값**: 사용자가 Theme을 지정하지 않았고 선택지를 보여달라고 요청하지도 않았으면, 되묻지 않고 업무 목적과 화면 특성(예: 대량 테이블 조회 → Neutral, 의료/상태 모니터링 → Pear)을 분석해 가장 알맞은 Theme을 AI가 바로 적용한다. 완료 보고에 고른 Theme과 한 줄 이유만 남기며 선택 승인을 기다리지 않는다.
2. **사용자가 선택지를 요청**: "테마 골라줘", "선택지 보여줘"처럼 사용자가 직접 고르고 싶다는 의사를 밝히면 그때만 `tokens/themes/catalog.yaml`에서 `selectable=true` 항목을 동적으로 나열해 `label` + 한 줄 특징(`summary`) + 추천 상황(`recommended_for`)과 함께 고르게 한다. 이름을 SKILL.md나 코드에 하드코딩하지 않는다. 사용 중인 선택 UI가 한 질문에 표시 가능한 선택지 개수를 제한하면(예: 4개), 그 한도 때문에 `selectable=true` 항목 일부를 임의로 목록에서 빼지 않는다 — 한도를 넘는 나머지는 같은 질문의 텍스트 설명에 함께 나열하거나 두 번째 질문으로 이어서 제시해 모든 `selectable=true` 항목이 실제로 선택 가능해야 한다. UI가 이미 자동으로 제공하는 "기타/직접 입력" 선택지를 직접 다시 만들어 남은 선택지 슬롯을 낭비하지 않는다.
3. **사용자가 이미 명시**: "Pear 테마로", "Apricot으로"처럼 이미 지정했거나 Design Guide "프롬프트 만들기"로 추출한 프롬프트에 `theme:` 값이 있으면 다시 묻지 않고 그 값을 그대로 따른다.
4. **같은 HTML 결과물 안의 다중 화면**: 지금 만들고 있는 같은 HTML 결과물 안에서 이전 화면에 이미 Theme을 골랐으면(자동 판단이든 사용자 지정이든) 그 결과물의 후속 화면에만 기본값으로 유지한다. 사용자가 특정 화면만 다른 Theme으로 명시하면 그 화면만 바꾼다. 같은 대화 중이라도 그 결과물과 별개인 새 HTML을 요청하면 신규 화면으로 취급해 1번으로 돌아간다 — 같은 대화라는 이유로 이전 결과물의 선택을 이어받지 않는다. 별도의 영구 Memory는 만들지 않는다.
5. **기존 화면 수정**: 감지 가능한 기존 Theme을 유지하고, 사용자가 변경을 명시한 경우에만 바꾼다.

Layout·Page Template과 Theme을 곱한 조합(`left-list-blue` 등)을 만들지 않는다. Theme은 구현 단계에서 선택된 Theme의 기본 5개 token을 교체하고, Catalog에 선택 accent가 있으면 전체 `chip-*`와 대응하는 `accent-*-foreground` token도 함께 교체한다. Color Mix에서는 메뉴·분류 카드·보조 IconButton처럼 서로 다른 대상을 구별하는 위치에 `data-nhimc-accent="sky|pear|apricot|yellow|purple|pink|amber"`를 안정적으로 배정하고, 면에는 `nhimc-accent-surface`, 선형 아이콘에는 `nhimc-accent-icon`을 사용한다. 같은 업무 항목은 화면이 바뀌어도 같은 accent를 유지한다.

새 Theme 추가는 무분별하게 늘리지 않는다. 명확히 구분되는 소수만 유지하고, 모든 항목이 기본 Semantic Token Contract(5개 key, light/dark 모두)와 WCAG AA 대비(`primary`/`primary-foreground` ≥ 4.5:1)를 만족해야 한다. 혼합형 accent는 일부만 정의하지 않고 전체 `chip-*`와 대응하는 `accent-*-foreground` key를 Light/Dark 양쪽에 모두 제공해야 하며 `scripts/validate_templates.py`가 자동 검사한다. 반복되는 프로젝트 요구나 명시적 브랜드 근거가 없으면 새 Theme을 추가하지 않는다.
