# Layout

업무용 Mode 명칭은 `사이드탭형 앱 셸`, `사이드탭형 앱 셸(블랭크 콘텐츠)`, `헤더 내비형 앱 셸`, `상단 헤더+좌측 탐색 앱 셸`이고, 콘텐츠·소식 전용 Mode는 `사이드바 없는 투명 헤더형 앱 셸`, 인증 전용 Mode는 `중앙 카드형 인증 화면`, 발표·브리핑 전용 Mode는 `슬라이드형 프레젠테이션 셸`과 `세로형 프레젠테이션 셸`이다. LEFT/LEFT BLANK/TOP/DEFAULT/BLOG/PRESENTATION/PRESENTATION VERTICAL은 사용자 표현을 이 명칭에 연결하는 별칭이다. 상세 수치와 Shell 컴포넌트 디자인의 정본은 `../docs/design-docs/design.md §4.2~§4.4, §6.2, §6.7`이다.

## LEFT Canonical Frame

`left-sidebar:v2`가 현재 LEFT 정본이다. 사용자가 최신 기준으로 지정한 `references/baseline/left.html`에서 Frame 구조와 동작을, `references/baseline/간호인력 근무표 자동생성 v2.html`에서 다크 면·접힘 중심축·업무 컴포넌트 조합을 승격했다. 메뉴명·URL·업무 데이터·Base64 폰트·축약 토큰은 포함하지 않았다. 생성 시 Reference를 다시 해석하지 않고 `templates/catalog.yaml.layouts[id=left]`의 `canonical_spec`과 `assets/layouts/left.html`만 사용한다.

정본은 48px SiteHeader, 256px expanded/76px collapsed/288px mobile Sidebar, 36px Logo와 44px collapsed mark, 42px Navigation row, 36px Toggle, 28px statusbar, Main 단독 Scroll, 200ms Frame transition을 기존 Token 경로로 참조한다. Desktop은 expanded, Tablet은 자동 collapsed, Mobile은 Header Hamburger와 왼쪽 Drawer/Overlay를 사용한다. 접기 아이콘 오른쪽의 SiteHeader 제목은 현재 메뉴명이 아니라 프로젝트명·서비스명이며 화면 전환 중 고정한다. 현재 화면명은 활성 메뉴와 Content Slot의 PageHeader가 담당한다. 접힌 레일은 흰색 라운드 배경의 44px `brandmark-solo-logo-1.svg`를 쓰며 펼친 가로 로고와 같은 위치에서 `{motion.fast}` opacity 교차 페이드한다. 메뉴 행은 좌우 padding 8px을 유지한 채 라벨의 폭·불투명도·gap만 전환해 36px 칩의 중심축이 움직이지 않게 하고 16px 아이콘 크기를 유지한다. Submenu는 Menu Data의 계층만 바꾸고 행 높이·padding·icon·motion은 동일 규격을 재사용한다.

Dark Mode에서는 본문만 어둡게 바꾸고 브랜드 Sidebar를 네이비로 남기지 않는다. `colors-dark.sidebar-brand`의 중립 다크 면과 밝은 전경을 적용하고, 파스텔 메뉴 칩과 활성 오버레이가 브랜드 식별을 담당한다. Theme 전환은 가능한 경우 `localStorage`에 보존하되 저장소 접근 실패가 화면 동작을 막지 않아야 한다. LEFT·TOP Frame의 내부 테마 버튼은 독립 실행과 Design Guide 상세 Preview 모두 해당 Frame 안에서만 모드를 전환한다. Guide 전체 테마는 Guide 상단 버튼만 소유하며, 이 전역 버튼을 누를 때는 모든 Preview와 Frame 내부 버튼의 아이콘·레이블·접근성 이름을 함께 갱신한다.

Template은 `content_contract`만 소유한다. Template 미리보기의 Shell markup은 정본이 아니며 Header, Sidebar, Logo, Toggle, statusbar, 전역 Scroll 또는 Mobile Drawer를 생성 결과로 복사할 수 없다. Frame Preview의 메뉴명도 업무 데이터가 아닌 구조 예시이므로 결과물에서는 screen manifest의 메뉴로 반드시 교체한다. 두 Frame의 `data-nhimc-navigation-source="manifest"`와 desktop/mobile navigation view가 이 결합 지점을 표시한다. Navigation과 각 panel은 안내 박스 없이 실제 메뉴·화면처럼 보이며, Frame Preview 자체에서도 각 `data-screen-target`은 Content Slot 안의 `data-screen-panel`과 1:1로 연결되어야 하고 메뉴 선택 시 연결된 panel 하나만 표시하며 데스크톱·모바일 활성 상태를 동기화한다.

Navigation과 Content Slot 중 무엇이 Frame 소유이고 무엇이 Template/Screen Manifest 삽입 영역인지는 Design Guide 상세보기의 "구조 보기" 탭에서 색상 구역과 범례로 확인하며, Canonical Frame 자체에는 점선 경계·빗금·안내 라벨을 넣지 않는다.

## LEFT BLANK Canonical Frame

`left-sidebar-blank:v1`(`assets/layouts/left-blank.html`)은 LEFT(`left-sidebar:v2`)와 Sidebar·Navigation·Content Slot·statusbar 계약을 그대로 공유하는 변형이다. 두 가지만 다르다: (1) 콘텐츠 쪽 SiteHeader는 배경·아래 경계선을 투명하게 비워 콘텐츠 영역이 시각적으로 이어져 보이게 하되 mobile-menu·site-title·도움말·테마 버튼은 같은 위치에 그대로 둔다. (2) 사이드바 접기 토글(`#sidebarToggle`)은 SiteHeader가 아니라 사이드바 브랜드 로고와 같은 행 오른쪽 끝에 있다. 접힌 76px 레일에서는 로고와 토글이 함께 들어갈 폭이 없으므로 로고를 숨기고 토글만 중앙에 남겨 재펼침 진입점을 유지한다. 이 외의 모든 계약(Sidebar 폭, statusbar 위치, 다크모드, 반응형)은 LEFT와 동일하며 자동 선택 대상이 아니다 — 사용자가 콘텐츠 헤더를 비운 형태를 명시적으로 요청했을 때만 선택한다.

| 기존 Layout Mode | 사용자 표현 | region/slot | 선택 기준 |
|---|---|---|---|
| 사이드탭형 앱 셸 | LEFT MENU | `Sidebar + SidebarInset(SiteHeader + Main) + statusbar` | 프로젝트 기본값. 메뉴가 많거나 그룹·접기·지속 탐색이 필요할 때 |
| 사이드탭형 앱 셸(블랭크 콘텐츠) `[EXT]` | LEFT BLANK | `Sidebar(브랜드 행에 접기 토글 포함) + SidebarInset(투명 SiteHeader + Main) + statusbar` | 자동 선택 대상이 아님. 콘텐츠 영역을 시각적으로 비워 보이게 해야 할 때만 명시적으로 사용 |
| 헤더 내비형 앱 셸 `[EXT]` | TOP MENU | 한 줄 `SiteHeader(Brand + topnav-inline + Utility) + Main + statusbar` | 기존 화면이 사용하거나 사용자가 명시한 경우, 최상위 메뉴 6~8개 이하 |
| 상단 헤더+좌측 탐색 앱 셸 `[EXT]` | DEFAULT | 전체 폭 `SiteHeader(Brand + Project Title + Utility)` 아래 `Sidebar + Main + statusbar` | 가이드·관리 콘솔처럼 전역 브랜드/프로젝트 영역과 지속 좌측 탐색을 분리할 때 |
| 사이드바 없는 투명 헤더형 앱 셸 `[EXT]` | BLOG | 투명 `SiteHeader(Brand + topnav-inline + Utility) + Main + site-footer(브랜드+링크+저작권)` | 자동 선택 대상이 아님. 사이드바 없이 소식·콘텐츠형 화면을 명시적으로 요청했을 때만 |
| 중앙 카드형 인증 화면 | 로그인/재인증 | 중앙 `Card` | 인증 진입만. 업무 화면에 사용하지 않음 |
| 슬라이드형 프레젠테이션 셸 `[EXT]` | PRESENTATION | 헤더·Sidebar·statusbar 없는 전체 화면 슬라이드 + 좌우 화살표/하단 점 내비게이션 | 자동 선택 대상이 아님. 사용자가 발표·브리핑·슬라이드 형태를 명시적으로 요청했을 때만 사용 |
| 세로형 프레젠테이션 셸 `[EXT]` | PRESENTATION VERTICAL | 헤더·Sidebar·statusbar 없는 전체 화면 슬라이드 + 상하 화살표/우측 세로 점 내비게이션(모바일 세로 브리핑·데모용) | 자동 선택 대상이 아님. 사용자가 모바일 세로·스토리형 브리핑을 명시적으로 요청했을 때만 사용 |

## 선택 흐름

Layout(위 표의 Mode)은 `templates/catalog.yaml`의 `layouts` 배열에 `id`(`left`/`top`/`top-left`)·`label`·`purpose`·`selectable`로 등록된, 사용자가 직접 고르는 독립 선택 단위다. Page Template(`templates` 배열)과 별개 개념이며 서로 곱해서 복제하지 않는다.

1. **신규 화면 + 기본값**: 사용자가 Layout을 지정하지 않았고 선택지를 보여달라고 요청하지도 않았으면, 되묻지 않고 아래 자동 선택 순서로 가장 알맞은 Layout을 AI가 바로 판단해 적용한다. 완료 보고에 고른 Layout과 한 줄 이유만 남기며 선택 승인을 기다리지 않는다.
2. **사용자가 선택지를 요청**: "레이아웃 골라줘", "선택지 보여줘"처럼 사용자가 직접 고르고 싶다는 의사를 밝히면 그때만 `layouts`에서 `selectable=true` 항목을 동적으로 나열해 고르게 한다. 각 선택지는 catalog의 `label`과 `purpose`, 아래 표의 선택 기준을 사용해 `이름 — 한 줄 구조 설명 · 추천 상황`으로 표시한다. 이름이나 내부 ID만 나열하지 않으며, 이름을 SKILL.md나 코드에 다시 하드코딩하지 않고 catalog를 읽어 목록을 만든다.
3. **사용자가 이미 명시**: "LEFT로", "TOP 레이아웃으로"처럼 이미 지정했거나 Design Guide "프롬프트 만들기"로 추출한 프롬프트에 `frame:`/`layout:` 값이 있으면 다시 묻지 않고 그 값을 그대로 따른다.
4. **같은 HTML 결과물 안의 다중 화면**: 지금 만들고 있는 같은 HTML 결과물(하나의 다중 화면 manifest) 안에서 이전 화면에 이미 Layout을 골랐으면(자동 판단이든 사용자 지정이든) 그 결과물의 후속 화면에는 그 선택을 기본값으로 유지한다. 화면마다 다시 판단하지 않으며, 사용자가 특정 화면만 다른 Layout으로 명시하면 그 화면만 변경한다. 같은 대화 중이라도 사용자가 그 결과물과 **별개인 새 HTML**을 요청하면 이는 새로운 신규 화면이므로 1번으로 돌아간다 — 같은 대화라는 이유로 이전 결과물의 선택을 이어받지 않는다. 별도의 영구 Memory는 만들지 않고 현재 작업 범위 안에서만 유지한다.
5. **기존 화면 수정**: 신규 생성이 아니라 기존 화면을 고치는 작업이면 Layout을 다시 판단하지 않고 아래 자동 선택 순서로 감지한 현재 Mode를 유지한다. 사용자가 Layout 변경을 명시한 경우에만 바꾼다.

## 자동 선택

위 1, 4, 5번 상황에서 사용하는 순서다.

1. 사용자가 지정한 기존 Mode
2. 수정하는 화면의 Mode
3. 같은 업무 영역 기존 화면의 Mode
4. 프로젝트의 공통 Shell
5. 위 표의 선택 기준
6. `사이드탭형 앱 셸`

`사이드탭형 앱 셸(블랭크 콘텐츠)`, `사이드바 없는 투명 헤더형 앱 셸`, `슬라이드형 프레젠테이션 셸`, `세로형 프레젠테이션 셸`은 이 자동 선택 순서에 포함하지 않는다. `left-blank`는 사용자가 콘텐츠 헤더를 비운 형태를 명시적으로 요청했거나 `frame:`/`layout:` 값으로 지정한 경우에만 선택한다. `blog`는 list/detail/form 같은 업무 Page Type 계약과 무관한 소식·콘텐츠형 화면을 사용자가 명시적으로 요청했거나 `frame:`/`layout:` 값으로 `blog`를 지정한 경우에만 선택한다. 발표·브리핑·슬라이드 형태를 명시적으로 요청했거나 `frame:`/`layout:` 값으로 `presentation` 또는 `presentation-vertical`을 지정한 경우에만 그 둘을 선택하며, 모바일 세로·스토리형 브리핑을 명시했을 때만 `presentation-vertical`을 고른다.

모드가 바뀌면 Shell의 Header/Sidebar/Navigation region만 교체한다. Main의 Template, Pattern/Composition, Component, Theme, 업무 순서와 API 계약은 유지한다. Shell 자체의 구조 기준(Golden Layout)은 `../assets/layouts/left.html`, `../assets/layouts/left-blank.html`, `../assets/layouts/top.html`, `../assets/layouts/top-left.html`, `../assets/layouts/blog.html`이며, 업무 화면의 Main 내부 구조는 이 문서가 아니라 `catalog.yaml`의 Page Template이 담당한다.

## BLOG Canonical Frame

`blog:v1`(`assets/layouts/blog.html`)은 TOP(`top:v1`)의 Header/Nav/Content-slot 구조를 그대로 재사용하되 두 가지가 다르다: (1) SiteHeader 배경·경계선을 투명하게 비워 콘텐츠와 시각적으로 이어지게 한다(라이트·다크 모두). (2) statusbar 대신 실제 브랜드 라벨 + 링크 그룹 + 저작권 줄을 가진 `site-footer`를 쓴다 — LEFT/TOP/DEFAULT의 얇은 운영용 statusbar 계약과는 다른 콘텐츠형 footer다. 사이드바가 없고 list/detail/form 같은 업무 Page Type Golden Template과 호환 계약을 맺지 않으므로 자동 선택 대상이 아니며, 사용자가 소식·콘텐츠형 화면을 명시적으로 요청했을 때만 선택한다.

## 기존 디자인 유지

- 사이드탭형은 public `dashboard-01` 골격을 쓰고 브랜드 변형 Sidebar의 네이비 솔리드 면, 메뉴별 파스텔 아이콘 칩, 활성 배경 채움, 기존 접기 트리거를 유지한다. 일산병원용 사이드바 헤더는 SiteHeader와 같은 높이의 투명 영역으로 만들고 가로형 병원 로고를 좌측 정렬한다. 흰 배경은 실제 로고 크기만 감싸는 작은 라운드 플레이트로 제한하며, 사이드바 폭을 채우는 흰 카드나 서비스명 텍스트를 만들지 않는다. 로고 영역은 클릭 시 현재 화면을 새로고침하고 정확한 `aria-label`·Tooltip을 제공한다. 모바일 오프캔버스에는 병원 로고 영역을 반복하지 않고 `전체 메뉴 + 닫기` 헤더 다음에 곧바로 내비게이션을 둔다.
- 신규 LEFT 화면은 `assets/layouts/left.html`의 Shell DOM·클래스·동작을 먼저 복사한 뒤 Main slot만 Pattern/Component 조합(필요하면 참고한 Golden Template)으로 채운다. 별도 햄버거·도움말 wrapper·임시 아이콘을 재구성하지 않는다. 데스크톱 접기에는 canonical `panel-left`, 모바일 열기에는 `menu`, 도움말에는 `help-circle`, 닫기에는 `x` 아이콘을 사용하며 Header의 아이콘 전용 버튼은 같은 36px hit area와 같은 간격을 유지한다. 접기 아이콘 오른쪽 `{component.site-header-title}`에는 고정 프로젝트명을 넣고 메뉴 클릭 코드에서 이 텍스트를 덮어쓰지 않는다.
- Main 삽입점은 `main[data-nhimc-role="content-slot"]` 하나다. Layout preview의 compact 안내는 경계를 설명할 뿐 업무 콘텐츠가 아니므로 결과물에서는 제거하고, 선택한 Page Template의 `main[data-nhimc-role="content"]` 자식만 삽입한다. PageHeader·Card·Table 샘플을 Layout 자산에서 복사하거나 Slot 안내와 함께 남기지 않는다.
- 사이드탭형 업무 화면은 viewport 높이의 `Sidebar + SidebarInset` 그리드를 사용하고 Main을 유일한 세로 스크롤 컨테이너로 둔다. 문서 길이가 길어져도 Sidebar·SiteHeader·statusbar가 본문과 함께 페이지 밖으로 밀려나지 않아야 하며, `position: fixed`를 화면 요소마다 따로 붙이지 않는다.
- LEFT·TOP·DEFAULT의 Main·Navigation·Dialog body·Table wrapper와 Guide는 Registry의 `Scrollbar` atom을 공유한다. 폭은 10px, track은 투명, thumb는 예전 TOP native scrollbar에 가까운 중립 회색인 라이트 `#9E9E9E`/hover `#7D7D7D`, 다크 `#6F6F6F`/hover `#8A8A8A`이며 `data-theme`와 `color-scheme`를 일치시킨다. 세로 scroll owner만 `scrollbar-gutter: stable`을 사용하고 가로 전용 Table wrapper에는 쓰지 않는다.
- LEFT·TOP Frame의 기본 utility는 도움말과 테마 전환이다. 인쇄 버튼·인쇄 전용 CSS·`window.print()` 연결은 Frame에 선탑재하지 않고 사용자가 요구한 개별 화면에서만 추가한다.
- Sidebar 내부는 기존 `SidebarHeader → SidebarContent → SidebarFooter` 구조를 유지한다. 사용자 영역의 표시 여부와 메뉴 그룹은 가장 가까운 기존 화면을 따르며 화면마다 임의로 추가하지 않는다. `SidebarContent`는 `overflow-x: hidden`과 `min-width: 0`을 유지하고, 메뉴 행과 라벨도 폭을 줄일 수 있게 한다. 접기·펼치기 중 라벨의 폭·불투명도·아이콘과의 gap을 같은 motion token으로 전환하고, 접힌 메뉴 행은 남은 gap 없이 아이콘 칩을 정확히 중앙 정렬한다. 라벨은 한 줄 말줄임 상태에서 가용 폭만큼 복원되며 가로 스크롤바를 만들지 않는다.
- 모바일에서 Sidebar는 제거하지 않고 기존 Sheet 전환을 재사용한다. 태블릿 자동 접기와 데스크톱 상태 복원도 정본 규칙을 따른다.
- 헤더 내비형은 64px 높이의 한 줄 SiteHeader, 제품명과 첫 항목 사이 구분선 하나, 기존 active/hover 언어, 도움말·테마·사용자 utility를 유지한다. 활성 메뉴는 `{colors.category-sky}` 배경 + `{colors.category-foreground}` 글자를 쓰며(`topnav-link-active`) 라이트·다크 모두 같은 토큰이 테마별 값으로 전환되어 선택 면의 대비를 확보한다. 일산병원 업무 앱은 스킬에서 결과물로 복사한 `assets/logo/brandmark-row-logo.svg` 가로형 병원 로고를 브랜드 영역에 쓰되, 파비콘은 모든 셸의 기본 자산인 `assets/logo/brandmark-solo-logo-1.svg`를 유지한다. 로고는 LEFT 펼침 상태와 같은 36px 높이·`3px 5px` 내부 여백·7px 모서리의 흰색 소형 plate를 라이트·다크 공통으로 사용한다. 이 네 값은 LEFT/TOP 동기화 계약이며 한쪽을 변경할 때 다른 쪽과 브라우저 비교 검사를 함께 갱신한다. 로고 버튼은 고정 폭 대신 콘텐츠 너비를 사용하고 로고 이미지에는 `width:auto`, `max-width:none`, `object-fit:contain`을 적용해 버튼 내부에 불필요한 좌우 영역을 만들지 않는다. 로고와 제품명은 하나의 브랜드 그룹에서 `{spacing.md}`(12px)를 띄우고, 이 그룹과 내비게이션 사이에는 정본 구분선 간격을 적용한다. LEFT 셸의 `.sidebar-nav { width:100%; flex:1 }` 같은 세로 탐색 배치값은 TOP 셸에서 반드시 `width:auto; flex:none`으로 재설정해 브랜드 그룹과 구분선을 압축하거나 덮지 않게 한다. 좁아질 때는 `아이콘+라벨 → 아이콘 → 기존 오프캔버스` 순으로 축약하며, `{breakpoint.lg}` 미만에서는 내비·유틸리티 라벨을 숨기고 `{breakpoint.md}` 미만에서는 햄버거 오프캔버스로 전환한다. 라벨 버튼은 `white-space: nowrap`과 비수축 조건으로 전환 직전까지 두 줄로 감기지 않게 하며, 제품명은 축소 가능한 단일 행에 `text-overflow: ellipsis`를 적용해 다음 내비 영역과 겹치지 않게 한다. `{breakpoint.md}`(767px) 미만 모바일에서는 좁은 헤더에 로고·햄버거·제품명이 함께 끼이지 않도록 병원 로고를 숨기고 햄버거와 제품명만 남긴다.
- `{component.help-drawer}`는 Layout Mode에 종속되지 않는 공용 컴포넌트다. 두 앱 셸 모두 데스크톱 `min(50vw, 620px)`, 모바일 `min(288px, calc(100vw - 48px))`를 사용하며 셸 전환 때 폭·패딩·모션을 바꾸지 않는다. 자체 포함 HTML에서는 오른쪽 높이 전체를 차지하는 `dialog` 자체에 slide-in/slide-out을 적용한다. 전체 viewport의 투명 dialog 안에 움직이는 내부 panel을 다시 중첩하면 기준점·폭·backdrop motion이 어긋나므로 사용하지 않는다.
- 헤더 내비형 Content Slot은 Grid를 쓰더라도 `align-content: start`로 화면 패널을 위에서부터 자연 높이로 배치한다. 짧은 대시보드·설정 화면이 남은 viewport 높이까지 늘어나 카드 사이 또는 카드 아래에 큰 공백을 만들지 않게 한다.
- 상단 헤더+좌측 탐색형은 64px TOP 헤더가 viewport 전체 폭을 먼저 차지하고, 병원 가로 로고·고정 프로젝트명·도움말·테마만 둔다. 실제 업무 메뉴는 헤더에 중복하지 않고 헤더 아래 LEFT Sidebar 한 곳에서만 제공한다. 데스크톱은 256px Sidebar, 태블릿은 64px 아이콘 rail, 모바일은 왼쪽 Drawer를 사용하며 모두 하나의 screen manifest와 동일한 활성 상태를 공유한다. TOP 헤더의 로고 plate는 기존 LEFT/TOP과 같은 36px·`3px 5px`·7px 규격을 쓴다. 모바일에서는 TOP과 동일하게 병원 로고를 숨기고 햄버거·제품명만 남긴다.
- statusbar는 LEFT·TOP·DEFAULT 업무 앱 셸에만 사용하고 인증 화면에는 붙이지 않는다. 세 셸 모두 28px 높이와 상단 1px 경계선을 쓰며, 왼쪽에는 `상태 점 + 상태 문구 · 현재 화면`, 오른쪽에는 화면 정보를 한 줄로 표시한다. 상태 점은 `ready/success={colors.success}`, `warning={colors.warning}`, `error={colors.destructive}`, `processing={colors.primary}`를 사용하고 색만으로 상태를 전달하지 않도록 문구를 항상 병기한다. 별도 제품 페이지 footer를 새로 만들지 않는다.
- 주요 action은 PageHeader 오른쪽, 폼 action은 마지막에 둔다.
- 틴트된 canvas 위에 card 면을 사용하고 Card를 불필요하게 중첩하지 않는다.
- 컴포넌트 사이 간격은 부모 gap 또는 한쪽 margin 중 하나만 소유한다. 필터 툴바와 결과 카드는 `spacing.base`만 띄운다.
- 섹션 정체성 띠는 `card-banded` 안에 가두며 음수 margin으로 카드 밖에 확장하지 않는다.
- 본문·카드 배치는 container query, 셸 전환과 독립 페이지는 viewport media query가 담당한다.
