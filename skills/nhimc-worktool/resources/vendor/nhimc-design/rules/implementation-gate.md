# NHIMC Implementation Gate

Taste Gate가 렌더 결과의 시각 품질을 판단한다면, Implementation Gate는 production 구현이 NHIMC의 Layout·Component·Pattern·Token 정본을 재사용했는지 판단한다. 완료 전에 둘을 별도로 수행한다.

## Layout

- [ ] 선택한 Layout Catalog ID와 Page Type을 기록했는가? Golden Template을 참고했다면 그 ID도 함께 기록했는가?
- [ ] Page Type의 section 순서를 [page-type 원칙](../templates/list-page.md)(참고한 Golden Template이 있다면 그 `content_contract`)으로 실제로 확인했는가(기억이나 추측으로 대신하지 않았는가)?
- [ ] Canonical Frame의 Shell/Header와 content-slot의 PageHeader·검색·탭·표·Pagination·ActionArea 책임을 분리하고 각 순서를 유지했는가?
- [ ] 사용자 요구 또는 기존 프로젝트 제약 없이 LEFT/TOP 셸이나 Main Skeleton을 임의 변경하지 않았는가?
- [ ] 계약 변경이 필요했다면 먼저 기존 Pattern/Component 조합이나 Golden Template variant로 해결 가능한지 확인하고 이유를 기록했는가?

## Components

- [ ] Golden Template을 참고했다면 그 `required_components`를 모두 구현했는가? 참고하지 않았다면 Pattern/Component 조합에서 도출한 필수 구성 요소를 모두 구현했는가?
- [ ] 대상 프로젝트의 정확한 이름, alias, 비슷한 역할, 기존 사용 사례를 검색했는가?
- [ ] 실제로 존재하는 canonical Component 경로와 재사용 결과를 기록했는가?
- [ ] 기존 Component가 있는데 raw `button`, `input`, `select`, `table`, custom modal/tab/pagination으로 다시 구현하지 않았는가?
- [ ] 기존 variant/size로 가능한 visual style을 화면 단 CSS·Tailwind arbitrary class로 덮지 않았는가?

## Tokens

- [ ] Golden Asset이 `data-theme="light"`로 시작하고 `[data-theme="dark"]`를 명시하며, Guide 테마 전환이 Frame·Template·Component Preview 전체에 전달되는가?

- [ ] 임의 color 값이 없는가?
- [ ] 임의 spacing, control height, row height, radius, shadow, breakpoint가 없는가?
- [ ] Component가 캡슐화한 token을 화면에서 중복 지정하지 않았는가?

## Patterns

- [ ] SearchFilter, DataTable, FormSection, DetailSection, PaginationArea, ActionArea 등 기존 Pattern을 우선 조합했는가?
- [ ] 이름만 다른 화면 전용 검색·표·폼·action 조합을 만들지 않았는가?

## Button

- [ ] SearchFilter 초기화가 Button `ghost-subtle`을 사용했는가(일반 `ghost`로 대체하지 않았는가)?
- [ ] 화면 CSS에서 Button의 text color·background·border를 재정의하지 않았는가?

## Select

- [ ] native Select가 OS 기본 화살표를 그대로 노출하지 않는가(`appearance:none`/`-webkit-appearance:none`)?
- [ ] Select border가 `--color-border-accent`인가?
- [ ] Input과 Select의 border token을 같은 것으로 잘못 묶지 않았는가(Input=`--color-input`, Select=`--color-border-accent`)?
- [ ] 오른쪽 padding이 36px 이상이라 chevron과 text가 겹치지 않는가?
- [ ] chevron이 `--color-ring`을 사용하는가?

## Icon

- [ ] 아이콘이 필요할 때 [nhimc-icons.svg](../assets/icons/nhimc-icons.svg)/[icons.md](../components/icons.md)에서 먼저 검색했는가?
- [ ] 있는 아이콘을 Unicode 기호(↻ ⟳ ☰ ✕ 등)나 Emoji, 또는 직접 그린 새 SVG path로 대체하지 않았는가?
- [ ] 재사용한 아이콘의 `path`를 원본 그대로 복사하고 크기(14/16/18/24px)만 역할에 맞게 조정했는가?
- [ ] 정본에 없는 아이콘을 새로 만들었다면 화면 안에서 한 번만 쓰고 버리지 않고 `icons.md`의 sprite에 등록했는가?

## Canonical drift

- [ ] design.md / `assets/components/showcase.html` / Golden Template이 같은 Component에 서로 다른 token을 쓰고 있지 않은가? 충돌을 발견했다면 화면을 계속 만들기 전에 [Canonical Component Resolution](../SKILL.md#canonical-component-resolution)에 따라 먼저 동기화했는가?

## Visual

- [ ] (권고) 밀도·위계가 애매하면 같은 Page Type의 Golden Template 하나를 열어 hierarchy, density, section spacing을 대조했는가? 참고하지 않았다면 이 항목은 해당 없음으로 넘긴다.
- [ ] 1440/768/375px 및 라이트·다크에서 Canonical Frame Contract와 Content Contract가 각각 유지되는가?
- [ ] LEFT 다크모드에서 Sidebar가 중립 다크 면으로 전환되고, 76px 접힌 레일의 메뉴 칩이 정확히 중앙 정렬되며 36px 칩·16px 아이콘·흰색 배경의 44px `brandmark-solo-logo-1.svg` 크기가 유지되는가? 가로 로고와 접힌 단독형 로고가 `{motion.fast}`로 교차 페이드하는가?
- [ ] Layout preview의 Slot 안내를 결과물에 남기지 않고 Template의 `main[data-nhimc-role="content"]` 자식만 `main[data-nhimc-role="content-slot"]`에 삽입했는가?

## 수동 검토 대상

정적 분석으로 Component의 의미적 중복이나 모든 CSS override를 정확히 판정하려 하지 않는다. raw element가 canonical Component를 우회했는지, 기존 Pattern을 재구현했는지, override가 배치 목적을 넘었는지, 아이콘 `<svg>`의 `path`가 정본과 실제로 같은 도형인지(임의로 새로 그린 것은 아닌지)는 코드 리뷰와 렌더 검토로 확인한다. `scripts/check_compliance.py`는 Unicode/Emoji 아이콘 대체·native select 화살표 노출·`!important` override 같이 규칙 기반으로 확실히 잡히는 패턴만 자동 검사하고, 그 밖의 의미적 판단은 이 체크리스트가 담당한다.
