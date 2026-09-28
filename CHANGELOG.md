# 변경 이력

## [2.0.0] - 2026-09-28

- NHIMC Worktool upstream 정본을 커밋 `08c45402eece8a7c55afc60385e8671c9f13081a`로 고정했습니다.
- 7개 Frame, 49개 Component, 9개 Logo, SVG Icon sprite, Noto Sans KR 6개 Font를 불변 vendor 스냅샷으로 등록했습니다.
- 업무 콘텐츠를 정본 Frame에 삽입하는 어댑터와 오프라인 단일 HTML 빌더를 추가했습니다.
- 7개 Frame × 3개 viewport × 2개 Theme의 픽셀·상태·동작 parity를 릴리스 차단 게이트로 추가했습니다.
- 축약된 v1 Frame, Theme, Component, layout 구현과 해당 우회 경로를 제거했습니다.
- `bootstrap.md` 하나로 환경을 준비하고 이후 업무 화면만 요청하는 한글 사용 흐름을 문서화했습니다.
- 최종 산출물은 별도 CSS·JavaScript·Font·이미지 없이 `index.html` 하나이며 정확한 파일의 `file://` 검증을 필수화했습니다.

이 기록은 로컬 구현과 릴리스 준비 상태를 설명하며 GitHub 게시를 의미하지 않습니다.
