# NHIMC UI Core

NHIMC UI Core는 국민건강보험 일산병원 업무 화면을 정본 Frame, Theme, Component, Logo, Icon, Font로 조합하고, 검증된 오프라인 단일 HTML `index.html`로 전달하는 공개 프로젝트입니다. 정본 스냅샷은 커밋 `08c45402eece8a7c55afc60385e8671c9f13081a`에 고정됩니다.

## 버전

| 항목 | 값 | 확인 위치 |
| --- | --- | --- |
| 프로젝트(NHIMC UI Core) | `2.0.1` | `VERSION`, `registry/project.json` |
| Frame | `1.3.0` (left, left-blank, top, top-left), `1.1.0` (presentation, presentation-vertical), `1.4.0` (blog) | `registry/frames.json` |
| 플러그인 · 스킬 이름 | `nhimc-worktool` | `plugin.json`, `skills/nhimc-worktool/SKILL.md` |
| 벤더 스냅샷 | 커밋 `08c45402eece` | `vendor/nhimc-design/upstream.json` |
| Web Runtime | `@v2.0.1` | `dist/nhimc-web.js` |
| 완료 파일 매니페스트 | `schemaVersion 4` | `index.html`의 `nhimc-completion-manifest` |

- 버전은 Semantic Versioning을 따릅니다. PATCH는 계약을 깨지 않는 수정, MINOR는 하위호환 기능(Frame·Theme·Component·플랫폼 추가), MAJOR는 Frame·Component·Token·Branding·Bootstrap 계약의 Breaking Change입니다.
- Frame 버전은 프로젝트 버전과 따로 올라갑니다. 같은 Frame 버전은 같은 Frame 소스와 자산을 뜻합니다.
- 같은 이름의 스킬이 이미 설치되어 있으면 저장소 `VERSION`이 더 새로울 때만 갱신됩니다.
- 변경 내용은 [CHANGELOG.md](CHANGELOG.md)에 있습니다. Web Runtime 주소의 태그(`@v2.0.1`)는 릴리스마다 함께 올립니다.

## 사용법

처음 한 번 AI에게 아래 두 줄만 전달합니다(clone이 아니라 raw 파일을 읽으라는 뜻입니다).

```text
https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md
이 파일만 읽고 NHIMC UI Core를 준비해줘. (git clone 금지)
```

준비가 끝나면 자연어로 화면을 요청합니다.

```text
병원 이송업무 관리 화면 만들어줘.
```

빌더를 실행할 수 있는 로컬 호스트에서는 AI가 등록 Component와 Layout Primitive로 Content만 조합한 저작 원본을 만든 뒤, 브라우저 검증과 다운로드 전달까지 수행합니다. 정상 결과는 정확히 하나의 `index.html`입니다. 사용자는 이 파일을 내려받아 더블클릭하면 되며 인터넷, 서버, 저장소, `app.js`, CSS, 이미지, 폰트 폴더가 필요하지 않습니다.

### Design Guide (설치 가이드 · 사용법 · 프롬프트 만들기)

`guide/nhimc-design-guide.html` 하나에 설치 가이드, 사용법, 프롬프트 만들기(Layout·Theme 선택 → 붙여넣을 프롬프트), Frame·Component·Icon 미리보기가 들어 있습니다. 인터넷 없이 열립니다. 설치(bootstrap)가 끝나면 AI가 이 파일을 열어 주고, 열 수 없으면 다운로드 파일로 전달합니다. 다시 열려면 `open-guide.cmd`를 실행하세요. 웹에서는 `https://rawcdn.githack.com/SIMI-HC/nhimc-ui-core/v2.0.1/guide/nhimc-design-guide.html` 링크로 바로 열립니다(파일로 저장해도 됩니다). 파일은 `python scripts/build_design_guide.py`로만 생성합니다.

### 메뉴와 Page

Frame은 고정이고 메뉴와 Page는 AI가 업무 요구에 맞춰 정합니다. 메뉴 JSON(`data-nhimc-menu`)에 항목을 넣고, 항목마다 `<section data-screen-panel="메뉴id"><main data-nhimc-role="content">…</main></section>` Page를 등록 Component로 채웁니다. 메뉴를 바꿔도 Frame 소스는 수정하지 않습니다.

### 웹 AI(ChatGPT Web 등)에서 쓰는 방법

웹 AI는 빌더를 실행할 수 없으므로 **Web Runtime**으로 프롬프트 안에서 끝냅니다. AI가 만드는 HTML은 Content(`main[data-nhimc-role="content"]`)와 `<head>`에 넣는 다음 한 줄뿐입니다.

```html
<script src="https://cdn.jsdelivr.net/gh/SIMI-HC/nhimc-ui-core@v2.0.1/dist/nhimc-web.js"></script>
```

Runtime이 로드될 때 정본 Frame·Font·Icon·Logo·Theme을 씌웁니다. 인터넷과 외부 스크립트를 허용하는 곳에서 열어야 하며, 미리보기일 뿐 오프라인 검증된 `index.html`은 아니고 아무 파일도 자동으로 저장하지 않습니다. 브라우저 검증까지 거친, 외부 링크 없는 오프라인 파일이 필요하면 Claude Code · Codex · Gemini CLI 같은 로컬 환경에서 요청하세요(코드 실행으로 `build_verified_artifact.py`를 돌립니다). `dist/nhimc-web.js`는 `python scripts/build_web_runtime.py`로만 생성합니다.

## 일관성이 유지되는 이유

AI가 Frame을 복제하거나 CSS를 새로 그리지 않습니다. Core가 고정 digest를 확인하고 다음 순서로 합성합니다.

1. Frame은 그대로 복사됩니다. AI는 `main[data-nhimc-role="content"]` 안만 작성합니다.
2. Content는 Component Registry의 49개 Component를 먼저 재사용하고 Layout Primitive로 여백·격자를 맞춥니다. 임의 Frame/CSS/스타일은 거부합니다.
3. 7개 정본 Frame 중 하나에 업무 콘텐츠를 삽입합니다.
4. Theme, 49개 Component, Layout Primitive, 병원 Logo, Icon sprite, Noto Sans KR 6개 Font face를 HTML 안에 포함합니다.
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

## 플러그인으로 설치 (Marketplace)

저장소 루트가 Claude Code·Codex 마켓플레이스이자 플러그인입니다(`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`). GitHub에 push된 상태에서 등록합니다.

```
claude plugin marketplace add SIMI-HC/nhimc-ui-core
claude plugin install nhimc-worktool@nhimc-worktool-marketplace

codex plugin marketplace add SIMI-HC/nhimc-ui-core
codex plugin add nhimc-worktool@nhimc-worktool-marketplace
```

Claude Code 대화창에서는 `/plugin marketplace add SIMI-HC/nhimc-ui-core`도 같습니다. 릴리스마다 `VERSION`, 두 `plugin.json`, `.claude-plugin/marketplace.json`의 버전을 함께 올립니다(테스트가 검사합니다).

## 유지보수와 문제 해결

아래 명령은 일반 사용자가 실행하는 설치 과정이 아니라 Core 유지보수 및 장애 진단용입니다.

```powershell
python scripts/build_verified_artifact.py --input path/to/source.html --output path/to/index.html
python scripts/run_browser_tests.py --standalone-file path/to/index.html
python scripts/verify_all.py --quick
python scripts/verify_all.py
python scripts/release_tag.py
python scripts/verify_release.py
python scripts/build_release.py release/nhimc-ui-core-2.0.1.zip
```

첫 명령은 빌드, 정확한 브라우저 검증, 영수증 대조, `index.html` 전달을 한 번에 수행합니다. `scripts/build_single_html.py`는 내부 합성기이며 사용자의 기본 흐름이 아닙니다.

검증은 목적별로 한 단계만 실행합니다. 개발 중에는 브라우저 의존 테스트와 대규모 화면 행렬을 제외한 `python scripts/verify_all.py --quick`, 일반 변경의 최종 인계 전에는 전체 `python scripts/verify_all.py`, 공개 릴리스 판단에는 전체 검증을 내부에 포함한 `python scripts/verify_release.py`를 사용합니다. `verify_release.py` 직전에 `verify_all.py`를 따로 실행하지 않습니다. 각 게이트는 단계별 및 전체 소요 시간을 출력합니다.

`VERSION`을 올린 커밋을 푸시한 뒤에는 반드시 `python scripts/release_tag.py`로 `v<VERSION>` 태그를 만들어 `origin`에 푸시하세요. bootstrap.md와 Design Guide가 안내하는 githack·jsdelivr 링크는 이 태그가 있어야 동작하며, `scripts/verify_release.py`는 이제 태그가 없으면 `RELEASE BLOCKED: release tag`로 막습니다.

주요 계약은 `registry/frames.json`, `registry/components.json`, `registry/layouts.json`, `skills/nhimc-worktool/references/contracts.md`에 있습니다. Logo와 Font 공개 승인 및 라이선스 범위는 [PUBLIC_ASSET_REVIEW.md](PUBLIC_ASSET_REVIEW.md)에 기록되어 있습니다.

릴리스 검증은 공개 준비 상태를 뜻하며 GitHub Release 게시 여부와는 별개입니다. 게시 작업은 별도 절차입니다.

## 라이선스

재배포·수정 금지(사용 허가만)입니다. 자세한 내용은 [LICENSE](LICENSE)를 참고하세요(초안, 법무 검토 전). Noto Sans KR은 SIL OFL 1.1이며 일산병원 로고와 정본 디자인의 권리는 각 권리자에게 있습니다.
