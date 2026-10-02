# Icon Registry

Golden Layout/Template/Example와 자체 포함 HTML 산출물에서 아이콘이 필요할 때 쓰는 규칙 문서다. **기계 판독 가능한 SVG 정본은 [`assets/icons/nhimc-icons.svg`](../assets/icons/nhimc-icons.svg)**이며 100종 이상을 유지한다. Design Guide의 Icon Library는 이 sprite의 `symbol`을 자동으로 읽으므로 목록을 Guide에 다시 하드코딩하지 않는다. 아래 표는 자주 쓰는 시작 항목의 빠른 참조이며 전체 목록·검색·확대 Preview는 Guide에서 확인한다. 이모지·유니코드 기호(☰ ✕ ▤ ▦ ♙ ⌁ ⓘ ? 등)를 아이콘 대신 쓰지 않는다 — 폰트마다 굵기·기준선·크기가 달라 칩·버튼 안에서 어긋나 보이고, 의미도 실제 아이콘과 무관한 경우가 많다.

## 사용 규칙

- 모든 아이콘은 `viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"`인 inline SVG다. 색은 `currentColor`로 부모에서 상속하고, 크기는 SVG `width`/`height` 속성이 아니라 CSS로 지정해 토큰과 맞춘다.
- 크기는 역할별 고정값을 쓴다(SKILL.md NHIMC Visual DNA #21과 동일): 상태 배지 아이콘 14px, 메뉴 아이콘 칩 내부 16px, 일반 action 아이콘 18px. 임의 크기를 만들지 않는다.
- 칩·버튼 중앙에 아이콘이 오도록 부모에 `display:flex;align-items:center;justify-content:center`(또는 `place-items:center`)를 주고, 아이콘 자체에는 `display:block;flex:none`을 준다 — inline 기본값(`display:inline`)로 두면 기준선 때문에 몇 px 어긋나 보인다.
- 아이콘 전용 버튼(라벨이 숨는 경우 포함)에는 `aria-label`과 `title`을 함께 준다(접근성 규칙과 동일).
- 새 아이콘이 필요하면 SVG sprite에 고유 `id`, 한국어 `data-label`, `data-category`, `viewBox="0 0 24 24"`, 시간대가 포함된 ISO 8601 `data-updated-at`를 가진 `symbol`로 추가한 뒤 사용한다. 화면마다 즉석으로 다른 모양의 유사 아이콘을 새로 그리지 않는다 — 목적이 같으면 Guide에서 가장 가까운 것을 재사용한다. 기존 아이콘의 path를 고치는 경우에도 그 `symbol`의 `data-updated-at`을 갱신한다 — Guide Icon Library는 이 값 기준 최신순으로 정렬된다.
- 여기 없는 아이콘이 필요하면 목적이 비슷한 기존 항목으로 대체 가능한지 먼저 확인한다. 정말 새 아이콘이 필요할 때만 같은 시각 언어(24x24, stroke 2, round cap/join)로 추가한다.

## 공통 UI

| id | 용도 | path |
|---|---|---|
| `menu` | 모바일 사이드바/내비게이션 열기(햄버거) | `<path d="M4 7h16M4 12h16M4 17h16"/>` |
| `panel-left` | 데스크톱 LEFT 사이드바 접기·펼치기 | `<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/>` |
| `x` | 닫기(다이얼로그, 오프캔버스 패널) | `<path d="M18 6 6 18M6 6l12 12"/>` |
| `chevron-down` | Select 화살표, 펼치기 | `<path d="m6 9 6 6 6-6"/>` |
| `chevron-right` | 다음, 하위 항목 | `<path d="m9 18 6-6-6-6"/>` |
| `chevron-left` | 이전 | `<path d="m15 18-6-6 6-6"/>` |
| `search` | 검색 | `<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>` |
| `refresh` | 검색 조건 초기화, 새로고침 | `<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/>` |
| `printer` | 인쇄 | `<path d="M6 9V3h12v6"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>` |
| `help-circle` | 도움말 | `<circle cx="12" cy="12" r="9"/><path d="M9.8 9a2.3 2.3 0 1 1 3.3 2.1c-.8.4-1.1.9-1.1 1.9M12 17h.01"/>` |
| `moon` | 다크 모드 전환 | `<path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z"/>` |
| `sun` | 라이트 모드 전환 | `<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>` |
| `settings` | 환경 설정 | `<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1 1.55V21a2 2 0 1 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 1 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 1 1 4 0v.09a1.7 1.7 0 0 0 1 1.55 1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 1 1 0 4h-.09a1.7 1.7 0 0 0-1.55 1Z"/>` |
| `filter` | 필터 | `<path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3Z"/>` |
| `plus` | 추가, 신규 등록 | `<path d="M12 5v14M5 12h14"/>` |
| `pencil` | 수정 | `<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>` |
| `trash-2` | 삭제 | `<path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="m19 6-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/>` |
| `check` | 완료 표시 | `<path d="M20 6 9 17l-5-5"/>` |
| `check-circle` | 승인, 완료 상태 | `<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>` |
| `alert-triangle` | 경고, 주의(원내 기준 배지 등) | `<path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v5M12 17.3h.01"/>` |
| `info` | 안내 | `<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>` |
| `x-circle` | 오류, 거부 상태 | `<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/>` |
| `alert-circle` | 주의(원형, 배지 등에서 alert-triangle 대신) | `<circle cx="12" cy="12" r="10"/><path d="M12 7v6M12 17h.01"/>` |

## 메뉴 칩·업무 도메인

사이드바 메뉴 아이콘 칩(`{component.nav-icon-chip}`)과 카드 헤더 띠에 쓴다. 화면 목적에 맞는 것이 없으면 가장 가까운 것으로 대체하고, 정말 없을 때만 같은 시각 언어로 추가한다.

| id | 용도 | path |
|---|---|---|
| `layout-dashboard` | 대시보드, 운영 현황 | `<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>` |
| `list` | 목록, 조회 | `<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/>` |
| `building-2` | 진료과, 부서, 조직 | `<path d="M4 22V6a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v16"/><path d="M15 22V10a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v12"/><path d="M2 22h20"/><path d="M7 8h.01M7 12h.01M7 16h.01"/>` |
| `flask-conical` | 검사 수치, 검사실 | `<path d="M9 3h6"/><path d="M10 3v6.5L4.5 19a1.7 1.7 0 0 0 1.5 2.5h12a1.7 1.7 0 0 0 1.5-2.5L14 9.5V3"/><path d="M7 15h10"/>` |
| `ban` | 중단, 금지(중단 약물 등) | `<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>` |
| `megaphone` | 공지, 안내 사항 | `<path d="M3 11v2a2 2 0 0 0 2 2h1l4 5v-14l-4 5H5a2 2 0 0 0-2 2Z"/><path d="M16 8a4 4 0 0 1 0 8"/><path d="M19 5a8 8 0 0 1 0 14"/>` |
| `users` | 직원 관리, 사용자 | `<circle cx="9" cy="8" r="4"/><path d="M2 21v-2a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v2"/><path d="M17 11a4 4 0 0 0 0-7.75"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/>` |
| `shield-check` | 권한, 정책, 보안 | `<path d="M12 2 4 5v6c0 5 3.5 9 8 11 4.5-2 8-6 8-11V5Z"/><path d="m9 12 2 2 4-4"/>` |
| `bar-chart-3` | 운영 현황, 모니터링 | `<path d="M3 3v18h18"/><path d="M7 16v-4M12 16V8M17 16v-7"/>` |
| `folder` | 이력, 보관함 | `<path d="M3 5a2 2 0 0 1 2-2h4l2 3h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/>` |
| `clipboard-list` | 감사 이력, 정책 목록 | `<rect x="6" y="3" width="12" height="4" rx="1"/><path d="M6 5H5a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-1"/><path d="M9 12h6M9 16h6M9 8h1"/>` |
| `calendar` | 일정, 날짜 범위 | `<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>` |

## 예시

```html
<button class="mobile-menu" id="menuBtn" aria-label="메뉴 열기" title="메뉴 열기">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
</button>
```

```html
<span class="chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22V6a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v16"/><path d="M15 22V10a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v12"/><path d="M2 22h20"/><path d="M7 8h.01M7 12h.01M7 16h.01"/></svg></span>진료과 기준
```
