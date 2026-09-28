# 변경 이력

## [3.0.0] - 2026-09-28

- 저작 경계를 임의 `.specimen`/`.grid` 조합에서 등록된 9개 canonical Template과 필수 `data-template` 계약으로 변경했습니다.
- Template CSS를 Frame 보호 영역 밖으로 누출하지 않는 결정적 content-only 어댑터를 추가했습니다.
- 빌드 완료 매니페스트, 정확한 `file://` 브라우저 영수증, digest 일치 후 `index.html`만 전달하는 fail-closed 경계를 추가했습니다.
- 9개 Template × 3개 viewport × 2개 Theme의 구조·반응형·포커스·스크린샷·Frame 격리 검증을 릴리스 게이트에 추가했습니다.
- ChatGPT Web은 검증된 Builder Bridge 연결과 실제 다운로드 시험 전까지 `WEB_BOOTSTRAP / context-only`로 유지합니다.

## [2.0.0] - 2026-09-28

- NHIMC Worktool upstream 정본을 커밋 `08c45402eece8a7c55afc60385e8671c9f13081a`로 고정했습니다.
- 7개 Frame, 49개 Component, 9개 Logo, SVG Icon sprite, Noto Sans KR 6개 Font를 불변 vendor 스냅샷으로 등록했습니다.
- 업무 콘텐츠를 정본 Frame에 삽입하는 어댑터와 오프라인 단일 HTML 빌더를 추가했습니다.
- 7개 Frame × 3개 viewport × 2개 Theme의 픽셀·상태·동작 parity를 릴리스 차단 게이트로 추가했습니다.
- 축약된 v1 Frame, Theme, Component, layout 구현과 해당 우회 경로를 제거했습니다.
- `bootstrap.md` 하나로 환경을 준비하고 이후 업무 화면만 요청하는 한글 사용 흐름을 문서화했습니다.
- 최종 산출물은 별도 CSS·JavaScript·Font·이미지 없이 `index.html` 하나이며 정확한 파일의 `file://` 검증을 필수화했습니다.

이 기록은 로컬 구현과 릴리스 준비 상태를 설명하며 GitHub 게시를 의미하지 않습니다.
