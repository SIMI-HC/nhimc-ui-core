# SettingsPage

이 문서는 Golden Template을 여는지와 무관하게 `page_type=settings` section 순서·원칙의 1차 근거다. `catalog.yaml`에는 이 page_type의 Golden Template이 없으므로 다른 variant에 억지로 끼워 맞추지 말고 이 문서만으로 Pattern/Component 조합을 진행한다.

- 사용: 계정·알림·표시·연동 등 제품 설정을 관리하는 화면.
- 구조: `Sidebar + SidebarInset + SiteHeader > PageHeader > Settings Navigation/FormSection* > Actions`.
- 고정: 화면 이동 항목의 마지막에 위치한다.
- 금지: 서로 무관한 설정을 한 카드에 몰아넣거나 저장 범위를 불명확하게 만드는 것.
