# NHIMC UI Core

NHIMC UI Core는 NHIMC 업무용 웹 화면을 일관된 형태로 만들기 위한 애플리케이션 프레임 및 디자인 시스템입니다. 반응형 공통 프레임, 테마, 컴포넌트, 로고, 아이콘, 글꼴, 검증 도구와 AI 공통 Skill을 제공합니다.

## 가장 쉬운 사용법

### 1. 최초 한 번: Core 설치 요청

AI에게 아래와 같이 요청합니다.

```text
https://github.com/SIMI-HC/nhimc-ui-core.git

bootstrap.md만 읽고 NHIMC UI Core를 설치해줘.
```

AI는 `bootstrap.md`에서 현재 실행 환경을 확인하고, 공통 `skills/nhimc-ui/SKILL.md`를 자동으로 불러와야 합니다. 설치가 가능한 환경에서는 필요한 플러그인·Skill·확장 기능을 설치하고 준비 상태를 확인합니다.

AI가 보고하는 상태의 의미는 다음과 같습니다.

- `READY`: 영구 로딩 경로가 설치되고 검증되었습니다. 이후부터는 Git URL이나 `bootstrap.md`를 다시 입력하지 않고 화면만 요청하면 됩니다.
- `WEB_BOOTSTRAP`: 현재 대화에서만 Core가 로딩되었습니다. 같은 대화에서는 화면만 요청할 수 있지만, 새 대화에서는 Git URL과 `bootstrap.md` 요청을 다시 입력해야 합니다.
- `UNSUPPORTED`: 현재 환경에서는 저장소나 공통 Skill을 불러올 수 없습니다.

### 2. 설치 후: 필요한 화면만 요청

`READY` 상태에서는 이후 다음처럼 업무 화면만 요청하면 됩니다.

```text
운송 관리 화면 만들어줘.
```

또는 필요한 기능을 조금 더 구체적으로 작성할 수 있습니다.

```text
배차 현황, 차량 검색, 운송 상태 변경, 신규 배차 등록 기능이 있는 운송 관리 화면 만들어줘.
```

AI가 알아서 NHIMC Core를 적용하고 검증한 다음, 최종 산출물로 오프라인 실행 가능한 `index.html` 하나만 제공해야 합니다.

### 3. 결과 사용

전달받은 `index.html`을 다운로드하여 더블클릭합니다.

- 인터넷 연결 불필요
- 웹서버 불필요
- NHIMC UI Core 저장소 불필요
- 별도 `app.js` 또는 CSS 파일 불필요
- 별도 로고·아이콘·글꼴 파일 불필요

Frame, Theme, Components, Logo, Icon, Font는 생성 시점에 검증된 Core 저장소에서 읽어 하나의 HTML 안에 포함됩니다. 따라서 최종 HTML에서는 `ERR_FILE_NOT_FOUND`, 로컬 ES Module CORS, 상대 경로 누락 문제가 발생하지 않아야 합니다.

> 아래의 Python 및 Node 명령은 일반 사용자가 입력하는 사용법이 아닙니다. AI 또는 Core 개발자가 생성·검증 과정에서 내부적으로 사용하는 명령입니다.

## 구성 구조

- `registry/`: 프로젝트, 프레임, 테마, 컴포넌트 및 자산의 기계 판독형 계약
- `src/frame/`: 로고, 헤더, 내비게이션, 상태 표시줄, 반응형 동작 및 업무 콘텐츠 슬롯
- `src/themes/nhimc-light.css`: 공통 디자인 토큰
- `src/components/`: 재사용 가능한 UI 컴포넌트
- `src/layouts/primitives.css`: 업무 콘텐츠용 레이아웃 도구
- `skills/nhimc-ui/`: 지원되는 AI가 Core 규칙을 읽고 지키도록 하는 공통 Skill
- `bootstrap.md`: 사용자가 호출하는 단일 진입점

업무 화면은 `<nhimc-frame>`의 기본 슬롯에 배치합니다. 업무 콘텐츠에서 헤더, 사이드바, 상태 표시줄 등 공통 프레임을 복제하면 안 됩니다.

## AI 및 개발자용 단일 HTML 생성 절차

작성 중인 업무 HTML에서는 업무 동작을 `data-nhimc-business` 모듈 블록에 둡니다. 최종 전달 전에 AI 또는 개발자가 다음 빌더를 실행합니다.

```powershell
python scripts/build_single_html.py --input path/to/index.html --output path/to/index.html
python scripts/run_browser_tests.py --standalone-file path/to/index.html
```

첫 번째 명령은 Core 계약을 검증하고 Frame, Theme, Components, Logo, 아이콘 스프라이트 및 Noto Sans KR 글꼴을 HTML 내부에 포함합니다. 두 번째 명령은 사용자가 받을 정확한 파일을 Chrome 또는 Edge에서 `file://`로 열어 다음 항목을 검사합니다.

- JavaScript 실행 오류 및 처리되지 않은 Promise 오류
- 네트워크 또는 별도 로컬 파일 요청
- 다른 HTML 파일로 이동하는 sidecar 의존성
- 누락된 프레임·스타일·글꼴
- 외부 스타일시트, 모듈 및 스크립트 참조

검사 결과가 `standalone file: PASS`일 때만 해당 `index.html`을 전달합니다. 빌더는 이미 최종화된 파일을 변경하지 않고 거부하므로, 업무 내용이 바뀌면 작성 원본에서 다시 생성해야 합니다.

## 로컬 예제 확인

Python 3, Node.js, Chrome 또는 Edge는 Core 개발 및 검증에만 사용됩니다.

```powershell
python -m http.server 8765 --bind localhost
```

브라우저에서 다음 예제를 확인할 수 있습니다.

- `http://localhost:8765/examples/operations/`
- `http://localhost:8765/examples/administration/`

두 예제는 서로 다른 메뉴와 업무 콘텐츠를 사용하지만 동일한 프레임과 컴포넌트를 공유합니다. 등록된 컴포넌트 표준 마크업은 [registry/components.json](registry/components.json), 레이아웃 도구는 [src/layouts/primitives.css](src/layouts/primitives.css)에서 확인할 수 있습니다.

```html
<nhimc-frame id="app-frame">
  <main class="nhimc-page">업무 콘텐츠</main>
</nhimc-frame>
<script type="module" data-nhimc-business>
  import './src/frame/nhimc-frame.js';
  const frame = document.querySelector('#app-frame');
  frame.menu = [{ id: 'home', label: '홈', href: '#home' }];
</script>
```

## 테마 및 무결성

화면의 시각 값은 `registry/themes.json`에 등록된 사용자 정의 속성을 사용합니다. 공통 프레임 내부를 직접 수정하거나 덮어쓰지 않습니다. 새로운 디자인 값은 버전이 관리되는 테마 계약에 추가해야 합니다.

`protectedFiles`에 등록된 파일은 같은 프레임 버전에서 변경할 수 없습니다. 의도적으로 변경하려면 버전을 올리고 다음 명령으로 무결성 정보를 갱신해야 합니다.

```powershell
python scripts/update_integrity.py --frame nhimc-default --frame-version 1.0.0
```

전체 구현 및 공개 릴리스 검증:

```powershell
python scripts/verify_all.py
python scripts/verify_release.py
```

NHIMC 로고 및 Noto Sans KR 글꼴을 포함한 공개 자산 검토 결과는 [PUBLIC_ASSET_REVIEW.md](PUBLIC_ASSET_REVIEW.md)에 기록되어 있습니다.

## AI 환경별 지원 상태

저장소 안에 매니페스트가 존재하는 것만으로 설치 완료를 의미하지는 않습니다. 해당 환경의 로딩 경로가 실제로 설치되고 검증되어야 `READY`입니다.

| 환경 | 영구 사용 경로 | 영구 설치가 없을 때 |
| --- | --- | --- |
| ChatGPT Web | 플러그인 로딩 및 검증 완료 → `READY` | 저장소 컨텍스트 → `WEB_BOOTSTRAP`, 불러올 수 없음 → `UNSUPPORTED` |
| Codex | 루트/호환 플러그인 로딩 및 검증 완료 → `READY` | 읽을 수 있는 저장소 → `WEB_BOOTSTRAP`, 불러올 수 없음 → `UNSUPPORTED` |
| Claude Web | Skill 업로드 완료 → `READY` | 저장소 컨텍스트 → `WEB_BOOTSTRAP`, 불러올 수 없음 → `UNSUPPORTED` |
| Claude Code | 플러그인 로딩 완료 → `READY` | 읽을 수 있는 저장소 → `WEB_BOOTSTRAP`, 불러올 수 없음 → `UNSUPPORTED` |
| Gemini Web | 선언된 영구 설치 경로 없음 | 저장소 컨텍스트 → `WEB_BOOTSTRAP`, 불러올 수 없음 → `UNSUPPORTED` |
| Gemini CLI | 확장 기능 설치 및 재시작 완료 → `READY` | 읽을 수 있는 저장소 → `WEB_BOOTSTRAP`, 불러올 수 없음 → `UNSUPPORTED` |

정확한 환경별 확인 절차는 [bootstrap.md](bootstrap.md)와 `docs/platforms/`를 참고합니다.

## 기여 및 릴리스

변경 작업은 먼저 registry 계약을 확인하고, 기본 프레임과 등록된 컴포넌트를 우선 재사용해야 합니다. 정말 새로운 컴포넌트가 필요한 경우 `docs/decisions/new-component.md`에 결정을 기록하고 테스트를 추가합니다. `VERSION`, 보호 파일 해시 및 모든 매니페스트 버전은 서로 일치해야 합니다.

검증을 통과한 재현 가능한 릴리스 압축 파일 생성:

```powershell
python scripts/build_release.py release/nhimc-ui-core-1.0.0.zip
```

게시 작업은 별도 절차입니다. 로컬 검증을 통과한 압축 파일은 릴리스 준비가 완료된 상태일 뿐이며, 관리자가 GitHub 게시 위치를 선택하고 실제 게시 작업을 수행하기 전에는 게시된 것이 아닙니다.
