# States

데이터 기반 화면은 아래 다섯 상태를 모두 설계한다.

1. loading: 기존 콘텐츠가 없는 최초 조회. 실제 골격과 같은 Skeleton 또는 설명이 있는 Spinner.
2. empty: 유효한 결과 없음. 이유, 설명, 다음 행동 CTA.
3. error: 실패. 원인 한 줄, 복구/재시도 action, destructive Alert.
4. success: 저장·등록·복사 완료. 비차단 Toast 또는 명확한 완료 상태.
5. partial loading: 기존 콘텐츠를 유지한 증분 조회. 작은 Spinner 또는 Progress.

Empty와 Error를 같은 UI로 처리하지 않는다. loading 중 레이아웃이 크게 이동하지 않아야 한다.

## 시각 매핑

| 상태 | 면/경계 | 보조 표시 |
|---|---|---|
| loading | category-sky + primary | Spinner 또는 Skeleton + `불러오는 중` |
| empty | category-purple | 빈 상자 아이콘 + 이유 + CTA |
| error | alert-destructive soft surface | 오류 아이콘 + 원인 + 재시도 |
| success | alert-success soft surface | 완료 아이콘 + 결과 문구 |
| partial loading | category-apricot 또는 alert-warning | 기존 콘텐츠 유지 + 작은 Spinner/Progress |

작은 색점만 바꾸는 구현은 금지한다. 상태 면·경계와 아이콘·텍스트를 함께 쓰고, 같은 상태에는 모든 화면에서 같은 매핑을 적용한다.
