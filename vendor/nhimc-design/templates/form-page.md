# FormPage

이 문서는 Golden Template을 여는지와 무관하게 `page_type=form` section 순서·원칙의 1차 근거다.

- 사용: 객체 등록·수정처럼 저장이 필요한 입력 화면.
- 금지: placeholder로 label을 대신하거나 서로 무관한 필드를 한 섹션에 넣는 것.
- 구조: `Sidebar + SidebarInset + SiteHeader > PageHeader > FormSection* > Bottom/Sticky Actions`.
- action: 취소는 secondary/ghost, 저장은 primary. 제출 중 중복 실행을 막는다.
- states: field error와 page error를 구분하고 성공은 Toast 또는 완료 화면으로 피드백한다.
- responsive: multi-column field grid는 좁은 화면에서 1열이다.
