# Design Compliance

구현 완료 후 아래를 모두 확인한다.

- [ ] 프로젝트 구조와 가장 가까운 기존 화면을 먼저 확인하고 실제 재사용 경로를 기록했는가?
- [ ] App Structure를 단일/다중 화면으로 판정했으며, 다중 화면이면 주요 메뉴와 고유 화면이 1:1로 대응하는가?
- [ ] 디자인 전용 요청에서도 모든 주요 메뉴 화면을 정적 목업으로 만들었고, 중복 임시 target·빈 화면·dead navigation이 없는가?
- [ ] 데스크톱과 모바일 메뉴의 화면 목록·순서·활성 상태가 일치하며 화면 전환 시 SiteHeader 제목도 함께 바뀌는가?
- [ ] 기존 `사이드탭형 앱 셸` 또는 `헤더 내비형 앱 셸`을 선택했고 동일 역할 Layout을 만들지 않았는가?
- [ ] Layout Mode 변경 시 Shell만 바꾸고 Theme·Template·Pattern·Component·업무 로직을 유지했는가?
- [ ] 기존 Theme을 선택했고 모든 Theme이 같은 semantic key와 Component 구조를 공유하는가?
- [ ] Page Type(`list`/`detail`/`form`/`dashboard`/`settings`/`admin`/`login`)에 맞는 [page-type 원칙](../templates/list-page.md)의 section 순서를 따랐는가?
- [ ] 필요한 Pattern/Component를 [Pattern Registry](../patterns/registry.md)·[Component Registry](../components/registry.md)에서 우선 검색해 조합했는가?
- [ ] Golden Template을 참고했다면(선택 사항) 그 `content_contract`와 Content Slot 내부 section 순서가 일치하는가? 참고하지 않았다면 이 항목은 해당 없음으로 넘긴다.
- [ ] Golden Template을 참고했다면 그 `required_components`를 모두 사용했는가? 참고하지 않았다면 Pattern/Component 조합에서 도출한 필수 구성 요소를 모두 포함했는가?
- [ ] 정확한 이름 → alias → 비슷한 역할 → 기존 사용 사례 순서로 검색하고 실제 canonical Component를 우선 재사용했는가?
- [ ] Golden HTML의 raw element를 대상 프레임워크의 기존 Component 대신 production source로 복사하지 않았는가?
- [ ] Component visual style override는 하지 않고 화면 배치에 필요한 width·flex·grid placement만 지정했는가? Component가 레이아웃에 맞지 않았다면 [Component/Icon Decision Rule](../SKILL.md#componenticon-decision-rule)의 부모 Layout → Pattern → wrapper → size variant → Component 최소 변경 순서를 따랐는가?
- [ ] 기존 Pattern을 우선 조합했는가?
- [ ] Pattern이 담당하는 반복 조합을 별도 Composition/Block 이름으로 복제하지 않았는가?
- [ ] 신규 Component/Pattern/Template은 승인된 EXTENSION뿐인가?
- [ ] hardcoded color, spacing, radius, shadow, motion이 0건인가?
- [ ] `design.md` frontmatter의 typography 값을 따르고 임의 typography를 만들지 않았는가?
- [ ] loading/empty/error/success/partial loading이 모두 있는가?
- [ ] 라이트·다크가 모두 성립하는가?
- [ ] 375/768/1440px에서 깨짐·겹침·페이지 가로 스크롤이 없는가?
- [ ] keyboard, focus, label/aria, modal focus, reduced motion을 확인했는가?
- [ ] 아이콘 전용 또는 반응형에서 라벨이 숨는 action에 정확한 aria-label과 hover·focus Tooltip이 있고, 상태가 바뀌면 힌트 문구도 함께 바뀌는가?
- [ ] canonical 아이콘이 있는데 Unicode 기호(↻ ⟳ ☰ ✕ 등)·Emoji·직접 그린 새 SVG path로 대체하지 않았는가?
- [ ] primary action이 화면당 과도하지 않고 정해진 위치에 있는가?
- [ ] 상태가 색 외의 텍스트/아이콘으로도 전달되는가?
- [ ] 상태가 작은 색점만이 아니라 정해진 semantic surface·경계·아이콘·텍스트로 표현되는가?
- [ ] 필터/카드/표 사이 간격을 두 요소가 중복해서 만들지 않는가?
- [ ] 그룹 표의 `colgroup` 실제 열 수와 2단 헤더의 `colspan`/`scope`가 일치하는가?
- [ ] Select의 닫힌 배경은 라이트에서 `{colors.background}` 흰색이고 `{colors.border-accent}` 경계를 사용하며, 자체 포함 HTML의 chevron은 오른쪽 안쪽 11~12px에 정렬되는가?
- [ ] Table container는 `{colors.border-accent}` 외곽선을 사용하고 row hover는 중립 회색이 아닌 `{colors.band-sky}` 계열이며, 다크에서도 표 헤더와 hover가 카드에서 구분되는가?
- [ ] 섹션 띠가 카드 모서리 안에 포함되고 음수 margin을 쓰지 않는가?
- [ ] 헤더 내비형 셸에서 제품명과 첫 내비 항목 사이 구분선이 한 번만 있는가?
- [ ] LEFT 셸은 viewport 높이 안에서 Main만 스크롤하고 Sidebar·SiteHeader·statusbar가 함께 밀려나지 않는가?
- [ ] LEFT 셸의 가로 병원 로고가 투명·좌측 정렬·SiteHeader 동일 높이의 영역 안에 있고 실제 로고만 작은 흰색 라운드 배경으로 감싸며, 전체 폭 흰 카드와 모바일 오프캔버스 중복 로고가 없는가? 로고 클릭 새로고침과 힌트가 동작하는가?
- [ ] LEFT 메뉴 접기·펼치기 중 Sidebar 가로 스크롤이 없고 라벨이 아이콘 옆 한 줄 말줄임에서 자연스럽게 복원되는가?
- [ ] LEFT 접힌 레일에서 메뉴 행이 중앙 정렬되고 36px 칩·16px 아이콘·흰색 배경의 44px `brandmark-solo-logo-1.svg`가 축소되지 않으며 펼친 로고와 `{motion.fast}`로 교차 페이드하고, 다크모드 Sidebar가 `colors-dark.sidebar-brand`를 사용하는가?
- [ ] Layout preview의 `content-slot` 안내를 결과물에 남기지 않고 Template의 `main[data-nhimc-role="content"]` 자식만 삽입했는가?
- [ ] 도움말 드로어가 두 앱 셸에서 동일한 폭(데스크톱 `min(50vw, 620px)`, 모바일 `min(288px, calc(100vw - 48px))`)과 동작을 사용하며 오른쪽 dialog surface 자체에 열기·닫기 motion을 적용하는가?
- [ ] 실제 서비스명을 사용했는가? 기본 셸은 `brandmark-solo-logo-1.svg`, 일산병원 헤더 내비형 셸은 화면 브랜드 영역에 `assets/logo/brandmark-row-logo.svg` 가로형 병원 로고를 사용하고 비율을 보존했는가? 셸과 관계없이 파비콘은 `assets/logo/brandmark-solo-logo-1.svg`이며 불필요한 캐릭터를 추가하지 않았는가?
- [ ] Sidebar, 파스텔 메뉴 칩, 채움형 표 헤더와 상태 surface가 public 규칙과 일치하는가?
- [ ] LEFT 메뉴 칩과 대응 섹션 Card header band가 같은 `chip-*` 토큰을 공유하고 섹션별 색 배정이 고정되어 있는가?
- [ ] 인쇄 버튼이 있으면 `rules/print.md`를 적용해 앱 셸·Card 장식을 제거한 A4 문서 구조이며, 긴 컨테이너의 잘못된 `break-inside: avoid`로 첫 장이나 빈 페이지가 생기지 않는가?
- [ ] 존재하지 않는 구현 경로를 문서나 import에 만들지 않았는가?
- [ ] 기존 프로젝트 없는 HTML 요청에서 사용자가 파일 분리를 명시하지 않았다면 `.html` 한 파일만 만들고, 폰트·토큰·favicon·로고·CSS·최소 JavaScript를 자체 포함했는가?
- [ ] 한 파일 HTML 요청을 `Index`, `Fonts`, `Design tokens`, `Logo` 등의 별도 artifact로 나누지 않았는가?
- [ ] HTML 결과물과 Golden 자산에 CDN·외부 폰트·원격 이미지·외부 script/link·fetch/XHR/WebSocket/EventSource 의존성이 없는가?
- [ ] `rules/implementation-gate.md`와 실제 렌더링 후 `rules/taste-gate.md`를 각각 수행했는가?
- [ ] `.agents/skills/nhimc-worktool/` 외 중복 스킬, Claude/Codex 전용 디자인 문서, 불필요한 새 Markdown이 없는가?
- [ ] 완료 보고 전에 프로젝트 루트의 `python scripts/verify_all.py`가 PASS했으며 FAIL을 검사 완화나 Baseline 자동 변경으로 숨기지 않았는가?

자동 사전 검사는 `python scripts/check_compliance.py <project-root>`로 실행한다. hardcoded color/spacing, 외부 참조, `!important` canonical override, `reset`/`clear` 버튼 recolor, Unicode·Emoji 아이콘 대체, `<select>`의 브라우저 기본 화살표 노출을 검사한다. 이 검사는 "정본 Component/Icon이 있는데 새로 만들어 버리는 실수"를 잡는 목적이며 width·flex·grid·margin 같은 정상 layout CSS는 막지 않는다 — 디자인을 경직시키는 것이 목적이 아니다. canonical Component의 의미적 중복, 임의 SVG path 생성 여부, Golden Template 내부 Component의 화면별 변형 여부처럼 정적 분석으로 정확히 판정할 수 없는 항목은 [Implementation Gate](implementation-gate.md)의 수동 검토 대상으로 남긴다. catalog와 Golden HTML은 `python scripts/validate_templates.py`로, 스킬 배포 구조는 `python scripts/verify_ssot.py`로 확인한다. 전체 로컬 완료 Gate는 프로젝트 루트의 `python scripts/verify_all.py`다. 자동 검사는 수동 접근성·반응형·시각 검증을 대체하지 않는다.
