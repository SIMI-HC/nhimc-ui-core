# Gemini Web과 Gemini CLI

Gemini CLI는 `gemini-extension.json`과 `GEMINI.md`를 통해 공통 `skills/`를 읽습니다. 설치·갱신 뒤 CLI를 재시작하고 v2 registry, 정본 스냅샷, canonical builder, 브라우저 검증 경로를 확인해야 `READY`입니다.

Gemini Web에는 이 프로젝트가 선언한 영구 확장 경로가 없습니다. `bootstrap.md`를 현재 세션에서 읽은 상태는 `WEB_BOOTSTRAP`이며 `READY`가 아닙니다.

빌더와 정확한 `file://` 검증을 실행할 수 없는 환경은 `context-only`입니다. 이때 AI는 업무 콘텐츠 참고안을 설명할 수 있지만 수작업 Frame이나 검증하지 않은 단일 HTML을 최종 산출물로 전달하면 안 됩니다. 매니페스트는 지원 경로만 설명하며 설치나 GitHub 게시를 수행하지 않습니다.
