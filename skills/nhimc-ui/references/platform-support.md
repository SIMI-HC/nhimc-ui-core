# 플랫폼 지원

정확한 로딩·준비 상태는 `bootstrap.md`, 기계 판독 기준은 `registry/project.json`을 따릅니다.

| 환경 | 검증된 결과 | 대체 결과 |
| --- | --- | --- |
| ChatGPT Web | portable plugin 검증 후 `READY` | 저장소 컨텍스트 `WEB_BOOTSTRAP` |
| Codex | plugin 또는 체크아웃 로더 검증 후 `READY` | 읽기 가능한 체크아웃 `WEB_BOOTSTRAP` |
| Claude Web | `skills/nhimc-ui` 업로드·검증 후 `READY` | 저장소 컨텍스트 `WEB_BOOTSTRAP` |
| Claude Code | Claude plugin 검증 후 `READY` | 읽기 가능한 체크아웃 `WEB_BOOTSTRAP` |
| Gemini Web | 영구 어댑터 없음 | 세션 컨텍스트 `WEB_BOOTSTRAP` |
| Gemini CLI | extension과 `GEMINI.md` 검증 후 `READY` | 읽기 가능한 체크아웃 `WEB_BOOTSTRAP` |

저장소나 Skill을 읽을 수 없으면 `UNSUPPORTED`입니다. 매니페스트가 있다는 이유만으로 설치·활성화를 주장하지 않습니다. canonical builder와 정확한 브라우저 검증을 실행할 수 없으면 `context-only`이며 완성 산출물을 전달하지 않습니다.
