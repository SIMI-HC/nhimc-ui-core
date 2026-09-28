# NHIMC UI Core 시작

이 파일은 모든 AI 환경에서 사용하는 단일 진입점입니다. 저장소 루트의 `VERSION`과 플랫폼 매니페스트를 확인한 뒤 `skills/nhimc-ui/SKILL.md`를 읽고 그대로 따르세요.

사용자는 처음에 다음과 같이 요청합니다.

```text
https://github.com/SIMI-HC/nhimc-ui-core.git

bootstrap.md만 읽고 NHIMC UI Core를 준비해줘.
```

준비가 끝나면 별도의 설치 명령을 묻지 않고 업무 화면을 요청할 수 있어야 합니다.

```text
이송업무 관리 화면 만들어줘.
```

## 환경 상태

| 환경 | 영구 로딩 경로 | 영구 로딩 경로가 없을 때 |
| --- | --- | --- |
| ChatGPT Web | 플러그인을 로드하고 검증했으면 `READY` | 저장소 컨텍스트만 있으면 `WEB_BOOTSTRAP`, 읽을 수 없으면 `UNSUPPORTED` |
| Codex | 플러그인을 로드하고 검증했으면 `READY` | 체크아웃을 읽을 수 있으면 `WEB_BOOTSTRAP`, 읽을 수 없으면 `UNSUPPORTED` |
| Claude Web | Skill을 업로드하고 검증했으면 `READY` | 저장소 컨텍스트만 있으면 `WEB_BOOTSTRAP`, 읽을 수 없으면 `UNSUPPORTED` |
| Claude Code | 플러그인을 로드하고 검증했으면 `READY` | 체크아웃을 읽을 수 있으면 `WEB_BOOTSTRAP`, 읽을 수 없으면 `UNSUPPORTED` |
| Gemini Web | 선언된 영구 설치 경로 없음 | 저장소 컨텍스트가 있으면 `WEB_BOOTSTRAP`, 없으면 `UNSUPPORTED` |
| Gemini CLI | 확장 기능을 로드하고 재시작·검증했으면 `READY` | 체크아웃을 읽을 수 있으면 `WEB_BOOTSTRAP`, 읽을 수 없으면 `UNSUPPORTED` |

- `READY`: 해당 환경의 로딩 경로가 실제로 설치되고 검증된 상태입니다.
- `WEB_BOOTSTRAP`: 현재 대화에서만 저장소와 Skill을 읽을 수 있는 상태입니다. 새 대화에서는 다시 준비해야 합니다.
- `UNSUPPORTED`: 저장소나 공통 Skill을 읽을 수 없어 정본 산출물을 만들 수 없는 상태입니다.

매니페스트가 존재한다는 이유만으로 `READY`라고 보고하지 마세요. 버전, 참조 경로, Skill 로딩과 검증이 모두 끝나야 합니다.

## 기본 산출물 계약

AI는 업무 콘텐츠만 작성합니다. Frame, Theme, Component, Logo, Icon, Font는 고정 커밋 `08c45402eece8a7c55afc60385e8671c9f13081a`의 정본 스냅샷과 Core 어댑터가 제공합니다.

업무 화면의 기본 결과는 인터넷과 저장소 없이 `file://`로 열리는 단일 `index.html`입니다. 별도 `app.js`, CSS, 이미지, 폰트 또는 자산 폴더를 함께 전달하면 안 됩니다. 반드시 저장소 빌더로 최종화하고 정확한 산출물 자체를 브라우저 검증해야 합니다.

호스트가 `scripts/build_single_html.py`와 `scripts/run_browser_tests.py --standalone-file`을 실행할 수 없다면 `context-only` capability라고 명확히 보고하세요. 이 경우 수작업으로 비슷한 Frame을 만들어 최종 HTML인 것처럼 전달하면 안 됩니다.
