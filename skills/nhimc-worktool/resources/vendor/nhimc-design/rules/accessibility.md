# Accessibility

- 모든 기능은 키보드만으로 완료 가능해야 한다.
- 인터랙티브 요소는 명확한 focus-visible 표시를 가진다. `outline: none/0`만 적용하지 않는다.
- Input, Select, Checkbox, Radio, Switch에는 고유 label을 연결한다.
- Dialog, Sheet, Drawer, overlay navigation은 focus trap, Esc 닫기, 닫힌 뒤 trigger로 focus 복귀를 제공한다.
- 상태와 분류는 색만으로 전달하지 않고 아이콘·텍스트 라벨을 병기한다.
- 아이콘 전용 버튼과 반응형에서 텍스트 라벨이 숨는 버튼은 정확한 `aria-label`을 가지며 hover와 keyboard focus에서 같은 문구의 Tooltip을 제공한다. 자체 포함 HTML에서 별도 Tooltip 컴포넌트가 없으면 최소한 `title`과 `aria-label`을 함께 제공하고 상태 변경 시 두 문구를 같이 갱신한다.
- reduced motion 환경에서는 비필수 애니메이션과 반복 motion을 중지한다.
- 확대·고대비·스크린리더 조합은 구현 환경에서 별도 확인한다.
