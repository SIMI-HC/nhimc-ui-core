# NHIMC UI Core

NHIMC UI Core는 국민건강보험 일산병원 업무 화면을 하나의 정본 디자인 시스템으로 생성하기 위한 공개 프로젝트입니다. 고정 커밋의 Frame, Theme, Component, Logo, Icon, Font를 재사용하고, AI는 업무 콘텐츠만 작성합니다.

정본 스냅샷 커밋: `08c45402eece8a7c55afc60385e8671c9f13081a`

## 사용법

처음 한 번 AI에게 저장소 주소와 다음 문장을 전달합니다.

```text
https://github.com/SIMI-HC/nhimc-ui-core.git

bootstrap.md만 읽고 NHIMC UI Core를 준비해줘.
```

준비가 끝나면 업무 요구만 말하면 됩니다.

```text
이송업무 관리 화면 만들어줘.
```

AI는 정본 Core를 적용하고 검증한 뒤 오프라인에서 실행되는 단일 HTML `index.html` 하나만 전달해야 합니다. 사용자는 파일을 내려받아 더블클릭하면 됩니다. 인터넷, 서버, 저장소, 별도 `app.js`, CSS, 이미지, 폰트 폴더가 필요하지 않습니다.

## 왜 하나의 HTML인가

저작 중에는 저장소의 정본을 참조하지만, 최종 빌더가 필요한 Frame·Theme·Component·Logo·Icon·Font를 HTML 안에 포함합니다. 따라서 다음 오류를 방지합니다.

- `ERR_FILE_NOT_FOUND`
- `file://` ES Module CORS 오류
- 상대경로가 끊겨 발생하는 Logo·Icon·Font 누락
- 화면마다 Frame이나 Component가 달라지는 수작업 복제

정본 전체를 AI가 임의로 다시 그리는 방식이 아닙니다. 고정된 vendor 스냅샷의 digest를 확인한 뒤 Core 어댑터가 업무 콘텐츠를 정본 Frame의 콘텐츠 영역에 삽입합니다.

## AI·개발자용 빌드와 검증

다음 명령은 일반 사용자가 입력하는 설치 절차가 아니라 AI 또는 Core 개발자가 내부적으로 수행하는 최종화 절차입니다.

```powershell
python scripts/build_single_html.py --input path/to/index.html --output path/to/index.html
python scripts/run_browser_tests.py --standalone-file path/to/index.html
```

두 번째 명령은 사용자가 받을 정확한 파일을 Chrome 또는 Edge에서 `file://`로 열어 검사합니다. 정본 Frame 역할, 49개 Component 번들, SVG 제어 아이콘, Noto Sans KR 6개 Font face, provenance, 외부 리소스 0개, 네트워크 0개, 시작 오류 0개를 모두 확인합니다. 결과가 `standalone file: PASS`가 아니면 전달하면 안 됩니다.

저작용 구조와 메뉴 JSON 예시는 [정본 계약](skills/nhimc-ui/references/contracts.md)에 있습니다. 테스트 fixture는 검증 입력일 뿐 실제 화면 디자인 예제가 아닙니다.

## 저장소 구조

- `vendor/nhimc-design/`: 고정 커밋에서 동기화한 불변 정본 스냅샷
- `src/generated/frame/`: 정본 Frame 공통 동작 어댑터
- `src/generated/components/`: 정본 49개 Component CSS와 controller
- `registry/`: v2 프로젝트·Frame·Theme·Component·Asset 계약
- `scripts/canonical_frame.py`: 7개 정본 Frame에 업무 콘텐츠를 안전하게 삽입
- `scripts/build_single_html.py`: 오프라인 단일 HTML 빌더
- `scripts/verify_canonical_parity.mjs`: 7개 Frame의 픽셀·상태 일치 검증
- `skills/nhimc-ui/`: 모든 지원 AI가 공유하는 작업 규칙
- `bootstrap.md`: 사용자가 호출하는 단일 진입점

## 지원 환경

| 환경 | 검증된 로딩 경로 | 로더가 없을 때 |
| --- | --- | --- |
| ChatGPT Web | 플러그인 로드·검증 후 `READY` | 저장소 컨텍스트 `WEB_BOOTSTRAP`, 접근 불가 `UNSUPPORTED` |
| Codex | 플러그인 로드·검증 후 `READY` | 읽을 수 있는 체크아웃 `WEB_BOOTSTRAP`, 접근 불가 `UNSUPPORTED` |
| Claude Web | Skill 업로드·검증 후 `READY` | 저장소 컨텍스트 `WEB_BOOTSTRAP`, 접근 불가 `UNSUPPORTED` |
| Claude Code | 플러그인 로드·검증 후 `READY` | 읽을 수 있는 체크아웃 `WEB_BOOTSTRAP`, 접근 불가 `UNSUPPORTED` |
| Gemini Web | 선언된 영구 로더 없음 | 저장소 컨텍스트 `WEB_BOOTSTRAP`, 접근 불가 `UNSUPPORTED` |
| Gemini CLI | 확장 기능 로드·재시작·검증 후 `READY` | 읽을 수 있는 체크아웃 `WEB_BOOTSTRAP`, 접근 불가 `UNSUPPORTED` |

매니페스트 파일이 있다는 이유만으로 설치가 끝난 것은 아닙니다. 실제 로딩과 검증이 완료돼야 `READY`입니다. 빌더나 정확한 브라우저 검증기를 실행할 수 없는 환경은 `context-only`이며, 비슷하게 수작업한 HTML을 완성품으로 전달할 수 없습니다.

## 검증과 공개

```powershell
python scripts/verify_all.py
python scripts/verify_release.py
python scripts/build_release.py release/nhimc-ui-core-2.0.0.zip
```

Logo와 Font의 공개 사용 승인, Noto Sans KR 라이선스 및 자산 무결성 범위는 [PUBLIC_ASSET_REVIEW.md](PUBLIC_ASSET_REVIEW.md)에 기록되어 있습니다.

릴리스 검증과 압축 파일 생성은 공개 준비가 끝났다는 뜻이며 GitHub에 이미 게시됐다는 뜻이 아닙니다. 게시 작업은 별도 절차입니다. 이 저장소 작업에서는 외부 push나 release 게시를 수행하지 않습니다.
