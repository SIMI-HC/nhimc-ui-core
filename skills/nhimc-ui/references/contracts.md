# 정본 계약

모든 경로는 저장소 루트 기준입니다.

- `vendor/nhimc-design/upstream.json`: 고정된 정본 커밋, 파일 목록과 SHA-256
- `registry/project.json`: v2 아키텍처, 기본 Frame·Theme, 단일 HTML 산출물과 환경 상태
- `registry/frames.json`: 7개 정본 Frame, 어댑터, 보호 파일과 소유 영역
- `registry/themes.json`: 정본 라이트·다크 Theme와 Font 원본
- `registry/components.json`: 49개 정본 Component의 사용 계약과 표준 markup
- `registry/assets.json`: 공개 가능한 정본 Logo, Icon, Font와 무결성 값
- `scripts/build_single_html.py`: 저작용 업무 화면을 오프라인 단일 HTML로 최종화하는 유일한 빌더
- `scripts/run_browser_tests.py`: 정확한 최종 파일의 `file://` 동작을 검증하는 브라우저 게이트

## 저작용 HTML

```html
<!doctype html>
<html lang="ko" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>업무 화면</title>
</head>
<body>
  <nhimc-frame data-frame="left" data-project-title="업무 화면" data-active-id="home">
    <main id="business-content">업무 콘텐츠</main>
  </nhimc-frame>
  <script type="application/json" data-nhimc-menu>
    [{"id":"home","label":"홈","icon":"home","href":"#home"}]
  </script>
  <script type="module" data-nhimc-business>
    document.addEventListener('nhimc:navigate', event => {
      console.log(event.detail.id);
    });
  </script>
</body>
</html>
```

저작용 파일도 외부 stylesheet, script, font, image, 네트워크 요청을 참조하지 않습니다. 업무 콘텐츠는 Frame이 소유하는 header, sidebar, navigation, statusbar 클래스를 복제할 수 없고 색상이나 보호 스타일을 덮어쓸 수 없습니다.

## 최종 산출물

빌더가 정본 레이아웃, 49개 Component CSS·controller, SVG Icon sprite, 병원 Logo, 라이트·다크 Theme, Noto Sans KR 6개 WOFF2를 하나의 HTML에 포함합니다. 최종 파일에는 정본 커밋과 번들 무결성 메타데이터가 기록됩니다.

다음 조건은 즉시 실패입니다.

1. 정본 digest 불일치 또는 누락
2. 안전하지 않은 메뉴 id·href, 중복 id, 존재하지 않는 Icon
3. 외부 URL, import, fetch, sidecar 또는 다른 HTML로 이동
4. Frame 보호 영역 복제나 스타일 주입
5. 빌드 후 정확한 파일의 브라우저 검증 실패

브라우저 게이트를 실행할 수 없는 `context-only` 호스트는 최종 산출물을 전달할 수 없습니다.
