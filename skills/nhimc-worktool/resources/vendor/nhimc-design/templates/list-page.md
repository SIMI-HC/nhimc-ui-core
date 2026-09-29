# ListPage

이 문서는 Golden Template을 여는지와 무관하게 `page_type=list` section 순서·원칙의 1차 근거다.

- 사용: 비교 가능한 레코드를 검색·필터·페이지 이동하는 화면.
- 금지: 카드 그리드로 표 데이터를 재해석하거나, 페이지마다 다른 필터 순서를 만드는 것.
- 구조: `Sidebar + SidebarInset + SiteHeader > PageHeader > SearchFilter/FilterToolbar > DataTable > PaginationArea`.
- visual: 네이비 Sidebar + 메뉴별 파스텔 아이콘 칩, 채움형 표 헤더를 쓴다.
- hierarchy: PageHeader가 제목·설명을 함께 소유하고, 검색과 결과는 `spacing.base`의 연속된 작업 흐름으로 배치한다. 설명을 음수 margin으로 제목에 끌어올리지 않는다.
- density: 1~2개 필터는 compact toolbar, 설명·초기화·3개 이상 필터는 하나의 surface를 사용한다. DataTable Card header와 첫 표 행 사이에 중복 여백을 만들지 않는다.
- action: 등록은 PageHeader 오른쪽의 primary action 하나. 행별 행동은 마지막 열 메뉴.
- states: Table 영역 안에서 loading/empty/error/partial을 교체하고 성공은 Toast로 알린다.
- responsive: 필수 식별 열을 유지하고 표 wrapper에서 가로 스크롤한다. 보조 필터는 Sheet로 이동할 수 있다.
