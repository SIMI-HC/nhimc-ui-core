# Claude Web과 Claude Code

Claude Code는 `.claude-plugin/plugin.json`을 사용하며 저장소의 공통 `skills/`를 읽습니다. 설치나 갱신 뒤에는 Claude Code를 다시 로드하고 v3 registry, `data-template`, `scripts/build_verified_artifact.py`와 정확한 브라우저 검증기를 확인해야 `READY`입니다.

Claude Web은 같은 `skills/nhimc-ui`를 custom Skill로 업로드하고 검증했을 때만 `READY`입니다. 저장소 내용을 현재 대화에서만 읽는 경우 `WEB_BOOTSTRAP`입니다.

canonical builder 또는 정확한 최종 파일 검증을 실행할 수 없으면 `context-only`라고 보고하고, 비슷하게 다시 만든 HTML을 검증된 NHIMC 결과로 전달하지 않습니다. 저장소 배포와 외부 게시 작업은 별도 절차입니다.
