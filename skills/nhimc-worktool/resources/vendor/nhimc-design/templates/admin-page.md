# AdminPage

이 문서는 Golden Template을 여는지와 무관하게 `page_type=admin` section 순서·원칙의 1차 근거다.

- 사용: 승인 대기, 계정, 권한, 정책 등 높은 영향의 관리 화면.
- 구조: `Sidebar + SidebarInset + SiteHeader > PageHeader > SearchFilter > DataTable > PaginationArea`, 행 선택 시 `DetailSection` 또는 Dialog.
- action: 승인과 반려를 시각적으로 구분하고 삭제·회수는 ConfirmAction을 사용한다.
- 고정: 높은 영향의 작업은 수행자·시각·변경 이력을 확인할 수 있어야 한다.
