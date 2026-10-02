# Page-type Principle Registry

이 문서는 page type별 원칙을 찾는 인덱스다. 실제 Golden Template의 선택은 먼저 [`catalog.yaml`](catalog.yaml)에서 수행한다. catalog 항목 하나를 고른 뒤 해당 HTML 하나만 읽고, 세부 원칙이 필요할 때 아래 문서를 읽는다. 앱 전체 Shell은 Template과 독립적으로 `../rules/layout.md`에서 선택하며 Layout Mode를 바꿔도 Main의 Template은 유지한다. Template의 `content_contract`는 Content Slot 내부만 정의하며 Header·Sidebar·Logo·statusbar·전역 Scroll·Responsive Navigation을 포함할 수 없다. Golden Template HTML은 `body[data-nhimc-template-scope="content-only"]` 아래 하나의 `main[data-nhimc-role="content"]`만 두는 콘텐츠 전용 정본이다.

| name | purpose | when_to_use | when_not_to_use | related_items | source | example |
|---|---|---|---|---|---|---|
| ListPage | 검색·목록·페이지 이동 | 사용자, 환자, 승인, 로그 목록 | 단일 객체 상세 | PageHeader, SearchFilter, DataTable, PaginationArea | `list-page.md` | 사용자 관리 목록 |
| DetailPage | 단일 객체 조회·행동·이력 | 사용자·환자·승인 상세 | 대량 편집 | PageHeader, DetailSection, Tabs, ConfirmAction | `detail-page.md` | 사용자 상세 |
| FormPage | 등록·수정 입력과 제출 | API Key, 사용자, 설정 등록 | 필터만 있는 목록 | PageHeader, FormSection | `form-page.md` | API Key 등록 |
| DashboardPage | 핵심 지표와 예외 탐색 | 운영 현황, 처리량, 장애 | 단순 목록 | PageHeader, Metric Cards, Chart, DataTable | `dashboard-page.md` | 승인 현황 대시보드 |
| SettingsPage | 도구 설정·입출력 자기서술 | 환경, 알림, 입출력 명세 | 일반 상세정보 | PageHeader, FormSection, metadata table | `settings-page.md` | 도구 설정 |
| AdminPage | 관리 객체와 정책 제어 | 권한, 승인 대기, 계정 관리 | 개인 설정 | PageHeader, SearchFilter, DataTable, ConfirmAction | `admin-page.md` | 승인 대기 관리 |
| LoginPage | 인증 진입 | 로그인·재인증 | 인증 후 업무 화면 | Card, Input, Button | `docs/design-docs/design.md §4` | 중앙 인증 카드 |
