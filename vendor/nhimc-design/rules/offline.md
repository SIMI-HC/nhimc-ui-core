# 내부망·오프라인 규칙

NHIMC 업무도구와 Golden Template은 인터넷 연결 없이 열리고 읽혀야 한다.

- 런타임 CDN, Google Fonts, 외부 CSS·JavaScript·이미지·아이콘을 금지한다.
- `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, 동적 `import()`처럼 네트워크를 요구하는 동작을 정적 결과물에 넣지 않는다.
- 패키지 설치를 전제로 디자인하지 않는다. 기존 프로젝트에 이미 설치된 의존성만 재사용한다.
- 기존 프로젝트 없는 기본 HTML 요청은 CSS·최소 JavaScript·디자인 토큰·아이콘·로고를 한 HTML에 포함하되, 아이콘과 로고는 canonical inline SVG로 작성한다.
- Self-contained는 바이너리 내장을 뜻하지 않는다. 폰트·이미지·아이콘의 Base64를 금지하고, HTML 안의 `@font-face`와 `data:font/...`도 금지한다.
- 폰트는 `"Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", system-ui, sans-serif` 스택을 사용한다. 설치된 Noto Sans KR이 없으면 시스템 한글 글꼴로 자연스럽게 폴백하며 외부 다운로드를 시도하지 않는다.
- Golden Template도 같은 자산 원칙을 따른다. favicon이 필요하면 public app mark의 URL-encoded SVG data URL만 허용하고 `;base64,`는 허용하지 않는다.
- 단일 HTML의 `:root`에는 SSOT에 존재하는 Semantic Token 이름만 필요한 만큼 컴파일한다. `--p`, `--c`, `--b`, `--i` 같은 축약 토큰을 금지한다.
- 문서 안의 출처·배포 안내 링크는 사람이 클릭하는 참고 링크일 수 있으나 화면 렌더링의 필수 의존성이어서는 안 된다.
- `<svg xmlns="http://www.w3.org/2000/svg">`의 namespace와 manifest의 `$schema`는 런타임 리소스 요청이 아니다.

Golden Asset 자동 검사는 `python scripts/validate_templates.py`, 사용자 산출물 검사는 `python scripts/validate_deliverable.py <결과.html>`로 수행한다. 자동 검사가 통과해도 브라우저 개발자 도구의 Network 탭을 오프라인 상태에서 한 번 확인한다.
