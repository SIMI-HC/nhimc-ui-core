# ChatGPT Web과 Codex

루트 `plugin.json`은 portable Agent Plugins 형식의 공통 어댑터이고 `.codex-plugin/plugin.json`은 같은 `skills/`를 가리키는 호환 어댑터입니다. 지침을 복제하지 않습니다.

ChatGPT Web은 검증된 Builder Bridge가 연결되고 실제 `index.html` 다운로드까지 시험됐을 때만 `READY`입니다. Codex도 체크아웃 또는 플러그인을 로드하고 v3 registry, `data-template`, `scripts/build_verified_artifact.py` 경로를 확인한 뒤에만 `READY`입니다. 저장소가 대화 컨텍스트에만 있으면 `WEB_BOOTSTRAP / context-only`입니다.

업무 화면은 반드시 canonical builder와 정확한 `file://` 브라우저 검증을 거쳐 단일 HTML로 전달합니다. 해당 명령을 실행할 수 없는 ChatGPT Web 세션은 `context-only`이며 수작업한 유사 Frame이나 저작용 원본을 완성 파일로 첨부할 수 없습니다.

이 문서는 지원 경로를 설명할 뿐 현재 저장소가 호스트에 설치됐거나 GitHub에 게시됐다고 주장하지 않습니다.
