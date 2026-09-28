# NHIMC UI Core

NHIMC UI Core 3.0은 국민건강보험 일산병원 업무 화면을 정본 Frame, Theme, Component, Logo, Icon, Font로 조합하고, 검증된 오프라인 단일 HTML `index.html`로 전달하는 공개 프로젝트입니다. 정본 스냅샷은 커밋 `08c45402eece8a7c55afc60385e8671c9f13081a`에 고정됩니다.

## 사용법

처음 한 번 AI에게 저장소 주소와 아래 문장만 전달합니다.

```text
https://github.com/SIMI-HC/nhimc-ui-core.git

bootstrap.md만 읽고 NHIMC UI Core를 준비해줘.
```

준비가 끝나면 자연어로 화면을 요청합니다.

```text
병원 이송업무 관리 화면 만들어줘.
```

빌더를 실행할 수 있는 로컬 호스트에서는 AI가 업무에 맞는 등록 Template을 선택하고 `data-template` 저작 원본을 만든 뒤, 브라우저 검증과 다운로드 전달까지 수행합니다. 정상 결과는 정확히 하나의 `index.html`입니다. 사용자는 이 파일을 내려받아 더블클릭하면 되며 인터넷, 서버, 저장소, `app.js`, CSS, 이미지, 폰트 폴더가 필요하지 않습니다.

## 일관성이 유지되는 이유

AI가 Frame을 복제하거나 CSS를 새로 그리지 않습니다. Core가 고정 digest를 확인하고 다음 순서로 합성합니다.

1. 업무 유형에 맞는 9개 정본 Template 중 하나를 선택합니다.
2. 정본 역할·컴포넌트 구조만 허용하고 임의 Frame/CSS를 거부합니다.
3. 7개 정본 Frame 중 호환되는 Frame에 업무 콘텐츠를 삽입합니다.
4. Theme, 49개 Component, 병원 Logo, Icon sprite, Noto Sans KR 6개 Font face를 HTML 안에 포함합니다.
5. Chrome 또는 Edge에서 실제 `file://` 파일을 열어 외부 요청 0건과 런타임 오류 0건을 확인합니다.
6. 파일 digest와 일치하는 브라우저 영수증이 있을 때만 `index.html`을 전달합니다.

이 구조는 `ERR_FILE_NOT_FOUND`, ES Module CORS, 상대경로 단절, Logo·Icon·Font 누락을 방지합니다.

## 환경 상태

- `READY`: 빌더를 실제 호출하고 검증된 파일 다운로드까지 시험한 상태입니다.
- `WEB_BOOTSTRAP`: 저장소 내용을 현재 대화에서만 읽는 `context-only` 상태입니다.
- `UNSUPPORTED`: 저장소 또는 공통 Skill을 읽을 수 없는 상태입니다.

ChatGPT Web은 저장소 URL을 읽었다는 이유만으로 `READY`가 아닙니다. callable Builder Bridge가 연결되고 실제 다운로드 시험까지 통과해야 `READY`입니다. 그렇지 않으면 `WEB_BOOTSTRAP / context-only`라고 알리고, 저작용 원본을 완성 파일로 첨부하면 안 됩니다.

| 환경 | `READY` 조건 | 대체 상태 |
| --- | --- | --- |
| ChatGPT Web | 검증된 Builder Bridge 연결 및 다운로드 시험 | 저장소 컨텍스트만 있으면 `WEB_BOOTSTRAP` |
| Codex | 로컬 플러그인·빌더·브라우저 검증 가능 | 읽기 전용 체크아웃이면 `WEB_BOOTSTRAP` |
| Claude Web | 업로드 Skill과 검증된 빌드 실행 경로 | 저장소 컨텍스트만 있으면 `WEB_BOOTSTRAP` |
| Claude Code | 플러그인·빌더·브라우저 검증 가능 | 읽기 전용 체크아웃이면 `WEB_BOOTSTRAP` |
| Gemini Web | 현재 영구 실행 로더 없음 | 저장소 컨텍스트만 있으면 `WEB_BOOTSTRAP` |
| Gemini CLI | 확장 기능·빌더·브라우저 검증 가능 | 읽기 전용 체크아웃이면 `WEB_BOOTSTRAP` |

## 유지보수와 문제 해결

아래 명령은 일반 사용자가 실행하는 설치 과정이 아니라 Core 유지보수 및 장애 진단용입니다.

```powershell
python scripts/build_verified_artifact.py --input path/to/source.html --output path/to/index.html
python scripts/run_browser_tests.py --standalone-file path/to/index.html
python scripts/verify_all.py
python scripts/verify_release.py
python scripts/build_release.py release/nhimc-ui-core-3.0.0.zip
```

첫 명령은 빌드, 정확한 브라우저 검증, 영수증 대조, `index.html` 전달을 한 번에 수행합니다. `scripts/build_single_html.py`는 내부 합성기이며 사용자의 기본 흐름이 아닙니다.

주요 계약은 `registry/templates.json`, `registry/frames.json`, `registry/components.json`, `skills/nhimc-ui/references/contracts.md`에 있습니다. Logo와 Font 공개 승인 및 라이선스 범위는 [PUBLIC_ASSET_REVIEW.md](PUBLIC_ASSET_REVIEW.md)에 기록되어 있습니다.

릴리스 검증은 공개 준비 상태를 뜻하며 GitHub Release 게시 여부와는 별개입니다. 게시 작업은 별도 절차입니다.
