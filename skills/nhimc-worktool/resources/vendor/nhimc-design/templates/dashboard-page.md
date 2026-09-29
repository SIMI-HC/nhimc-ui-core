# DashboardPage

이 문서는 Golden Template을 여는지와 무관하게 `page_type=dashboard` section 순서·원칙의 1차 근거다.

- 사용: 핵심 지표, 추세, 예외 레코드를 한눈에 판단하는 운영 화면.
- 금지: 의미 없는 장식 차트, 같은 수치를 카드와 차트에 중복, 과도한 Card 중첩.
- 구조: `Sidebar + SidebarInset + SiteHeader > PageHeader > Metric Cards > Charts/Data Sections > Exception DataTable`.
- 간격: Main의 최상위 콘텐츠 스택이 `spacing.base`의 세로 `gap`을 단독 소유한다. Metric·Chart·DataTable Card가 서로 맞닿지 않게 하며, 각 Card에 별도 하단 margin을 중복 지정하지 않는다.
- action: 조회 범위는 toolbar, 주요 후속 행동은 PageHeader에 둔다.
- responsive: 카드와 차트 열 수는 기존 container breakpoint에서 감소한다.
