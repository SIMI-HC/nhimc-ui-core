# DetailPage

이 문서는 Golden Template을 여는지와 무관하게 `page_type=detail` section 순서·원칙의 1차 근거다.

- 사용: 단일 사용자·환자·승인·키의 요약, 세부 속성, 이력을 조회하는 화면.
- 금지: 읽기 화면 전체를 편집 폼으로 노출하거나 모든 DetailSection을 Card로 중첩하는 것.
- 구조: `Sidebar + SidebarInset + SiteHeader > PageHeader/Breadcrumb > Summary > DetailSection* > History/Actions`.
- action: 수정은 PageHeader, 삭제·회수는 ConfirmAction 안에서 수행한다.
- responsive: 정의 목록과 2열 상세 grid는 좁은 화면에서 1열로 전환한다.
