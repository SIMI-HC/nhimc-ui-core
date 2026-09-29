# Bootstrap: 작업 폴더 clone 제거 설계

## 배경

`bootstrap.md`/`SKILL.md`는 이미 "플러그인이 설치돼 있으면 클론하지 않는다"는 원칙을 담고 있지만(v1.3.2), 실제로는 다음 결함이 남아 있다.

1. 사용자가 `https://github.com/SIMI-HC/nhimc-ui-core.git` + "bootstrap.md만 읽고 준비해줘"라고 요청할 때, `bootstrap.md` 자체를 읽기 위해 AI가 저장소 전체를 clone할 수 있다(최초 진입점 자체가 절차 밖에 있음).
2. 미설치 환경에서 현재 절차 순서는 "1. 원격 VERSION 확인 → 2. 사본 결정(미설치면 즉시 clone) → 3. 공식 등록 여부를 사용자에게 질문"이다. 즉 공식 등록 가능 여부를 묻기도 전에 이미 작업 폴더에 clone이 끝나 있다.
3. 절차는 "설치돼 있으면 설치 경로에 저장소 전체(`registry/`, `scripts/`, `guide/`, `skills/`, `vendor/`, `VERSION`)가 있다"고 가정하지만, 이는 마켓플레이스를 통한 전체 플러그인 설치에서만 보장된다. Codex가 "스킬만 업로드"하는 경량 등록 경로를 제공한다면 `skills/nhimc-worktool/`만 설치되고 나머지 디렉터리는 없을 수 있다. 이 경우 현재 절차는 리소스 부재를 감지하지 못하고 clone으로 조용히 우회하게 된다.

## 목표

- 정상적인 준비 과정(초기 진입, 이미 설치된 환경 재확인, 버전 업데이트)에서 **작업 폴더에 절대 `git clone`/`git pull`을 실행하지 않는다.**
- `bootstrap.md` 자체를 포함해 모든 참조 파일은 최초에 GitHub raw URL로 읽는다.
- 공식 등록 가능 여부 확인 및 사용자에게 등록 여부를 묻는 절차가 clone 여부 판단보다 **항상 먼저** 온다.
- 설치본(플러그인이든 스킬 업로드든)은 사용 전에 필수 리소스 존재를 검증하고, 불완전하면 clone으로 우회하지 않고 사실대로 보고한다.
- Codex의 경량 설치 경로도 필수 리소스를 포함하도록 패키징을 수정한다.

## 범위 밖으로 남기는 것

- **로컬 셸이 있지만 공식 등록이 불가능하거나 사용자가 거절했고, 실제 브라우저 검증까지 마친 `index.html`을 만들어야 하는 경우**는 예외로 허용한다. 이때만 `git clone`을 쓰되, **작업 폴더(사용자 프로젝트 폴더)가 아니라 임시/scratch 경로**(source.html과 같은 위치: Claude Code 세션 scratchpad 또는 OS 임시 폴더)에만 사본을 만든다. 결과물(`index.html`)만 사용자 폴더에 남는다는 기존 "전달 경계: single HTML" 원칙은 그대로 유지된다.
- ChatGPT Web처럼 플러그인/스킬 개념이 아예 없는 완전한 웹 세션의 "코드 실행이 되는 경우" 빌더 경로(§152 `bootstrap.md`)는 위 예외와 동일하게 scratch-only clone으로 재정의한다(현재도 이미 임시 위치를 쓰고 있어 실질적 변경은 "작업 폴더 아님"을 명문화하는 수준).

## 설계

### 1. 최초 진입: raw 파일 읽기, clone 아님

사용자가 저장소 URL과 "bootstrap.md만 읽고 준비해줘"를 보내면, AI는 `git clone` 대신 `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md`를 직접 읽는다(WebFetch 또는 해당 환경의 URL 읽기 수단). 로컬 셸이 있어도 이 단계에서는 clone하지 않는다 — bootstrap.md를 읽는 목적만으로 저장소를 통째로 받을 이유가 없다.

### 2. 준비 절차 재정렬 (9단계)

기존 5단계 절차를 아래 순서로 교체한다. 핵심 변경은 **"등록 가능 여부 확인 및 질문"이 "클론 여부 판단"보다 먼저 온다**는 것과, 클론 자체가 "정상 경로"에서 완전히 빠진다는 것이다.

1. **raw `bootstrap.md` 읽기** (1절)
2. **raw `VERSION` 확인** — `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/VERSION`만 읽어 `갱신함/이미 최신/확인 못함`을 기억한다. 이 시점까지 clone 없음.
3. **설치된 `nhimc-worktool` 검색** — 이 환경(플러그인 목록, 스킬 목록, 확장 목록)에 이미 등록된 설치본이 있는지 본다.
4. **설치본이 있으면 버전 및 필수 리소스 검증** — 설치 경로를 `<루트>` 후보로 잡고, `registry/`, `scripts/`, `guide/`, `skills/`, `vendor/`, `VERSION`이 모두 존재하는지 확인한다.
   - 모두 있고 버전이 최신이거나 로컬이 최신 → 이 설치본을 `<루트>`로 확정, 8단계로.
   - 모두 있고 원격이 더 새로움 → 5단계로 진행하되 "업데이트"로 질문한다.
   - **리소스가 하나라도 빠짐** → 이 설치본은 `<루트>` 후보에서 제외한다. **clone으로 대체하지 않는다.** 다른 등록 경로(예: 스킬 업로드만 있고 플러그인은 없음)가 있으면 3단계로 돌아가 다른 경로를 마저 찾고, 없으면 5단계에서 "완전한 경로(플러그인)로 등록"을 제안한다.
5. **미등록이거나 불완전하면 공식 등록 가능 여부 확인 후 사용자에게 질문** — 이 환경이 지원하는 공식 등록 경로(플러그인 마켓플레이스 우선, 그다음 스킬 업로드, 확장)가 있으면 **등록할지(또는 완전한 경로로 재등록할지) 먼저 묻는다.** 자동 설치나 비공식 우회(clone 포함)를 하지 않는다.
6. **승인 시 공식 경로로 설치/업데이트** — Claude Code: `claude plugin marketplace add` → `claude plugin install`(또는 update 경로). 다른 환경은 해당 공식 명령을 쓴다.
7. **새 설치 경로를 `<루트>`로 설정하고 필수 리소스 재검증** — 방금 설치/업데이트된 경로에 6종 리소스가 모두 있는지 다시 확인한다. 빠졌으면 "설치 패키지가 불완전하다"고 정확히 보고하고 `WEB_BOOTSTRAP`으로 폴백한다(이 경우도 작업 폴더에 clone하지 않는다. 로컬 셸이 있고 사용자가 실제 산출물을 원하면 "범위 밖" 절의 scratch-only clone 예외를 쓴다).
8. **Design Guide 열기** — `<루트>/guide/nhimc-design-guide.html`. 처음 준비했거나 버전이 갱신됐을 때만.
9. **준비 결과 보고** — `platform`, `projectVersion`, `defaultFrame`, `defaultTheme`, `installationMode`, 최신 확인 결과, 등록 상태(등록됨/업데이트함/업데이트 안 함/미등록·미지원/불완전), Design Guide 상태.

미등록 + 등록 경로 미지원(또는 사용자 거절) 환경은 5단계에서 바로 `WEB_BOOTSTRAP`으로 확정하고 8~9단계로 건너뛴다(작업 폴더 clone 없음).

### 3. Codex 패키징: 스킬 경로도 리소스를 포함

`.codex-plugin/plugin.json`이 선언하는 `skills/nhimc-worktool/`이 단독으로 설치될 가능성에 대비해, 릴리스 빌드 시 `registry/`, `scripts/`, `guide/`, `vendor/`, `VERSION`을 `skills/nhimc-worktool/resources/`(신규 디렉터리) 아래로 **미러링**한다.

- 신규 스크립트 `scripts/sync_skill_resources.py`: 원본(저장소 루트의 6종 리소스)을 `skills/nhimc-worktool/resources/`로 바이트 동일하게 복사한다. 기존 `verify_nhimc_design_sync.py`(vendor 미러 검증)와 같은 패턴으로 "원본 vs 미러 해시 비교" 검증 함수를 제공한다.
- `verify_all.py`/`verify_release.py`에 동기화 게이트 추가: 미러가 원본과 다르면(추가/누락/내용 불일치) 릴리스를 막는다.
- `bootstrap.md`/`SKILL.md`의 "루트 결정" 절차에서 리소스 존재를 확인할 때, 설치 경로 바로 아래(`<루트>/registry` 등) 또는 `skills/nhimc-worktool/resources/` 아래 둘 중 있는 위치를 `<루트>`의 리소스 출처로 인정한다(플러그인 전체 설치는 전자, 스킬 단독 설치는 후자).
- `build_release.py`의 공개 zip은 영향 없음(이미 전체 트리 포함). `dist/manifest.json` 계열은 이 저장소에는 없으므로 신규 작업 없음.

### 4. 회귀 테스트

기존 `tests/python/test_bootstrap_contract.py`는 문서 텍스트를 assert하는 방식이며(AI 절차서라 실행 코드 경로가 없음), 새 테스트도 같은 스타일과 다음 실행 가능 검증을 조합한다.

문서 텍스트 검증(신규/수정, `test_bootstrap_contract.py`에 추가):
- 준비 절차 9단계 헤더가 순서대로 등장한다(raw bootstrap → raw VERSION → 설치 검색 → 리소스 검증 → 등록 질문 → 승인 시 설치 → 재검증 → Design Guide → 결과 보고).
- "raw.githubusercontent.com"이 `bootstrap.md` 1단계 설명에 등장하고, 그 문장에 "clone"이 없다.
- "필수 리소스" 목록(`registry/`, `scripts/`, `guide/`, `skills/`, `vendor/`, `VERSION`)이 문서에 명시된다.
- "불완전" 보고 문구가 존재하고, 해당 문장 주변에 "clone"으로 대체한다는 표현이 없다(정규식으로 "불완전...clone" 같은 우회 문구 부재 확인).
- 정상 절차 관련 모든 "git clone"/"git pull" 언급 줄에 "임시" 또는 "scratch" 관련 한정어가 포함된다(작업 폴더 clone 완전 제거를 문서 차원에서 보증).

실행 가능 검증(신규, `tests/python/test_skill_resources_sync.py`):
- `scripts/sync_skill_resources.py`의 검증 함수가 원본과 미러 간 해시 불일치를 감지한다(미러 파일을 임시로 변형해 실패를 확인).
- 미러가 원본에 없는 파일을 포함하면 실패한다(고아 파일 감지).
- `skills/nhimc-worktool/resources/`에 6종 리소스가 모두 존재하는지 확인하는 스모크 테스트.

이 스펙 범위에서 "실제 Codex/Claude Code 클라이언트가 설치 시 어떤 파일을 가져오는지"는 코드로 시뮬레이션할 수 없다(외부 호스트 동작). 따라서 회귀 테스트는 "문서가 올바른 절차를 지시하는가"와 "패키징 산출물이 완전한가"까지만 보증하고, 실제 호스트 설치 동작 검증은 범위 밖으로 남긴다.

## 완료 조건

- `python scripts/verify_all.py`, `python scripts/verify_release.py` 통과.
- `bootstrap.md`, `SKILL.md`, `docs/platforms/chatgpt-codex.md`(필요 시)가 9단계 절차와 일치.
- `skills/nhimc-worktool/resources/`가 저장소 루트 6종 리소스의 바이트 동일 미러.
- 신규/수정 테스트 전부 통과.
