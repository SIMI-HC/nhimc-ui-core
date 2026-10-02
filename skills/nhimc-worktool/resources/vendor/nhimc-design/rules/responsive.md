# Responsive

- 정본 breakpoint만 사용한다. 새 breakpoint를 만들지 않는다.
- 375px, 768px, 1440px에서 페이지 가로 스크롤·겹침·잘림을 검사한다.
- 기본 Sidebar는 768px 미만에서 화면 이동을 없애지 않고 Sheet overlay로 제공한다.
- LEFT 셸은 768px 이상에서 viewport 높이를 유지하고 Main만 스크롤한다. 768px 미만에서도 모바일 Header/Main/statusbar 그리드를 유지하며 데스크톱 접힘 상태를 거쳐 열리는 전환을 만들지 않는다.
- LEFT 셸을 접거나 펼치는 동안 Sidebar와 메뉴 목록에는 가로 스크롤바가 생기지 않아야 한다. 메뉴 라벨은 `min-width: 0`, `white-space: nowrap`, `overflow: hidden`, `text-overflow: ellipsis`를 사용하고 너비·불투명도만 전환해 아이콘 옆 한 줄로 복원한다.
- 모바일 오프캔버스는 병원 로고 버튼이나 로고 카드를 중복하지 않고, 메뉴 헤더 바로 아래에 파스텔 아이콘 칩 내비게이션을 배치한다.
- 본문·카드 열 수는 public의 container breakpoint를 따른다.
- 표는 의미 있는 열 순서를 유지하고 wrapper의 `overflow-x: auto`로 흡수한다.
- Dialog/Sheet/Drawer, filter, action button, form grid의 좁은 화면 동작을 별도로 확인한다.

`left-sidebar:v2`의 고정 모드는 Desktop `min-width:1024px` expanded, Tablet `768px..1023px` collapsed, Mobile `max-width:767px` Drawer다. Mobile Main padding은 `20px {spacing.md}`, Drawer 폭은 `{layout.sidebar-width-mobile}`(viewport 여백 48px 상한), Drawer header는 56px이며 왼쪽에서 열리고 `{colors.overlay}`를 사용한다. Template은 이 breakpoint·Drawer·Overlay를 덮어쓰지 않는다.

Desktop 수동 접힘과 Tablet 자동 접힘은 동일한 76px 아이콘 레일 정렬을 사용한다. 메뉴 행은 gap 0, 좌우 padding 8px을 사용해 접기 전후 칩 중심축을 고정하며 칩 36px·내부 아이콘 16px·상단 흰색 라운드 배경의 44px `brandmark-solo-logo-1.svg`를 유지한다. 펼친 가로 로고와 접힌 단독형 로고는 같은 위치에서 `{motion.fast}` opacity 교차 페이드한다. Mobile Drawer는 펼친 메뉴 규격을 사용하고 접힘 레일 규칙을 상속하지 않는다.
