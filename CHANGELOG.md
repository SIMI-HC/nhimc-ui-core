# 변경 이력

## [Unreleased]

- `START.md`: ChatGPT가 프롬프트의 "이 파일만 읽고"를 글자 그대로 지켜 `START.md`만 읽고 `bootstrap.md`는 읽지 않은 채 멈추던 문제를 고쳤습니다. 맨 위에 "여기서 멈추지 말고 `bootstrap.md`까지 읽는 것이 요청에 포함된다"를 넣고, 셸이 없는 환경은 곧바로 `main/bootstrap.md`를 읽게 했습니다. 프롬프트 문구는 그대로입니다.

## [2.4.0] - 2026-10-07

- **AI가 만든 업무 화면이 어색하게 나오던 원인 세 가지를 고쳤습니다.**
  - 검색 조건을 `nhimc-form-grid`로 감싸 `nhimc-toolbar` 안에 넣으면 폭을 못 받아 필드가 한 줄에 하나씩 쌓이던 것 → 툴바 안에서는 한 줄에 나란히 놓입니다(열 최소 180px).
  - 카드 안에 클래스 없는 `<div><strong>37</strong><span>건</span></div>`를 넣으면 여백이 0이라 글자가 카드 가장자리에 붙고 잘려 보이던 것 → 클래스 없는 `div`·`p`·`form`은 카드 본문 여백(18px)을 받고, 강조 카드의 수치·단위는 큰 숫자와 작은 단위로 보입니다.
  - 좁은 화면에서 표 글자가 `환자`/`명`, `TR-`/`20261007-`/`0037`처럼 쪼개지던 것 → 표 칸은 줄바꿈하지 않고 표가 `nhimc-scroll` 안에서 가로로 스크롤됩니다(설명처럼 긴 글 칸만 `class="nhimc-wrap"`).
- **Layout Primitive `Stat`·`StatGrid`(MetricOverview) 추가**: 핵심 수치 하나를 보여 주는 카드(`nhimc-stat-value`·`nhimc-stat-unit`·`nhimc-stat-note`)와 2~4개를 한 줄에 놓는 격자(`nhimc-stat-grid`). 패턴 목록(`MetricOverview`·`SearchFilter` 등)은 설명 문장뿐이고 마크업·CSS가 없어서 AI가 `.metric`·`.metrics`·`.fields`·`.card-head` 같은 클래스를 지어냈고, 그 클래스는 스타일이 없어 글자가 붙어 나왔습니다.
- **등록되지 않은 CSS 클래스 검사**: 오프라인 빌더(`content_rules.py`)가 스타일이 없는 클래스를 거부하고 올바른 대체(예: `metric` → `Stat`, `table-wrap` → `nhimc-scroll`)를 알려 줍니다. 웹 미리보기는 화면은 그대로 보여 주되 맨 위에 "스타일이 없는 클래스를 썼습니다" 안내를 띄웁니다. 기존 테스트 화면 전부에서 오탐은 없었습니다.
- **복사용 조각 추가**(`bootstrap.md`·`SKILL.md`의 "자주 쓰는 Page 조각"): 제목 줄+행동 버튼, 검색 조건(`nhimc-toolbar`), 핵심 수치 카드(`nhimc-stat`), 표 줄바꿈 규칙, 자주 틀리는 클래스 대응표. 조각이 빌더 검사를 통과하는지 테스트가 지킵니다.
- **내용 레이아웃 게이트 강화**: 카드 본문이 가장자리에 붙음, 검색 조건이 불필요하게 쌓임, 표 글자가 여러 줄로 쪼개짐을 검사하고, 테스트 화면 두 개(`kpi-filter`: 공식 마크업, `ai-misuse`: AI가 실제로 만든 잘못된 마크업)를 추가했습니다. 예전 CSS에서는 `ai-misuse`가 위 세 문제로 실패하는 것을 확인했습니다.

## [2.3.8] - 2026-10-07

- 기능 변경 없는 확인용 릴리스입니다. `START.md`가 이미 읽힌 뒤에 새 릴리스가 나와도 `git ls-remote`로 최신 태그(`v2.3.8`)를 찾아 그 태그의 `bootstrap.md`를 읽는지 확인하기 위해 버전만 올렸습니다.

## [2.3.7] - 2026-10-07

- **첫 프롬프트가 `https://raw.githack.com/SIMI-HC/nhimc-ui-core/main/START.md`을 가리킵니다.** `START.md`는 버전이 하나도 없는 짧은 파일이라 웹 AI 서비스가 읽은 복사본을 오래 들고 있어도 틀리지 않습니다. 셸이 있는 환경에서는 `git ls-remote --tags --sort=-v:refname`(클론 아님)으로 최신 릴리스 태그를 찾아 `…/<태그>/bootstrap.md`를 읽게 합니다. 태그 주소는 내용이 바뀌지 않아 옛 복사본 문제가 구조적으로 없습니다. 셸이 없으면 `main/bootstrap.md`를 읽는 대체 경로가 있습니다.
- `bootstrap.md`: `문서 버전` 줄을 다시 두고(최신 태그와 비교용), 2단계 원격 버전 확인을 `git ls-remote` 최신 태그로 바꿨으며, 보고(9단계)에 확인 방법과 읽은 태그 주소를 함께 쓰게 했습니다. `VERSION`·`main` 주소는 웹에서 옛 값(2.0.2)이 와서 읽지 않습니다.
- 테스트: `START.md`에 버전 숫자가 없고 `git ls-remote`와 태그 주소 형식이 있는지, `bootstrap.md`의 `문서 버전`이 `VERSION`과 같은지 검사합니다.

## [2.3.6] - 2026-10-07

- **첫 프롬프트의 주소를 `https://raw.githack.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md`로 바꿨습니다.** Claude 웹은 주소별로 처음 읽은 내용을 오래 들고 있어서 `raw.githubusercontent.com/…/main/bootstrap.md`는 v2.0.2(9월 30일 상태)로, 그 뒤에 읽은 `refs/heads/main`·`HEAD` 형태도 각각 2.3.2·2.3.4로 굳어 있었습니다(시크릿 채팅·"캐시 없이" 문구도 소용없음). 한 번도 읽지 않은 `raw.githack.com` 주소는 최신 내용이 읽히는 것을 확인했습니다. README, bootstrap, Design Guide(프롬프트 만들기 포함), 쉬운 가이드를 이 주소로 맞췄습니다.
- `bootstrap.md` 2단계의 원격 버전 확인을 `VERSION` 파일에서 `https://raw.githack.com/SIMI-HC/nhimc-ui-core/main/registry/project.json`의 `projectVersion`으로 바꿨습니다. githack이 확장자 없는 `VERSION`을 raw로 리다이렉트하고, raw의 `main/VERSION`은 Claude 웹에서 옛 값(2.0.2)으로 굳어 있었기 때문입니다.
- **첫 프롬프트를 처음 형태로 되돌렸습니다**: `main/bootstrap.md` 주소 한 줄과 "이 파일만 읽고 NHIMC UI Core를 준비해줘. (git clone 금지)". `bootstrap.md` 맨 위의 `문서 버전` 줄과 `HEAD` 주소 안내를 뺐고, 2단계는 다시 `VERSION`을 읽습니다(못 열면 문서 안 링크의 버전을 `문서 기준`으로 씁니다). "웹 채팅은 설치를 묻지 않음", 여러 화면 예시, Web Runtime `@2`는 그대로입니다.
- `bootstrap.md`: ① `VERSION` 파일을 읽지 않고 문서의 `문서 버전`을 씁니다(웹에서는 못 열거나 옛 복사본 2.0.2가 와서 오히려 틀렸습니다). ② 웹 채팅(claude.ai·ChatGPT·Gemini)에서는 샌드박스 셸이 있어도 "플러그인을 설치할까요?"를 묻지 않고 바로 `WEB_BOOTSTRAP`으로 진행합니다. 설치를 묻는 것은 사용자 컴퓨터의 Claude Code·Codex·Gemini CLI뿐입니다. SKILL.md의 준비 절차 요약도 같이 고쳤습니다.

## [2.3.5] - 2026-10-07

- **첫 프롬프트의 주소를 `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/HEAD/bootstrap.md`로 바꿨습니다.** 같은 파일의 다른 표기(`HEAD` = 기본 브랜치)입니다. Claude 웹은 한 번 읽은 주소의 내용을 오래 들고 있어서 `main/bootstrap.md`는 v2.0.2로, `refs/heads/main/bootstrap.md`는 2.3.2로 굳어 있었습니다. 읽은 적 없는 `HEAD` 주소는 새 대화에서 `projectVersion 2.3.4`(문서 버전 기준)로 정확히 읽히는 것을 확인했습니다. README, bootstrap, Design Guide(프롬프트 만들기 포함), 쉬운 가이드를 모두 이 주소로 바꿨습니다.
- 한 번 읽은 복사본이 굳어도 괜찮도록 문서가 버전을 고정하지 않습니다(Web Runtime `@2`, 문서 버전 줄, `VERSION`은 선택). README에 예전 `main/bootstrap.md`를 쓰지 말라는 안내를 넣었습니다.
- `bootstrap.md` 맨 위에 `문서 버전`을 적고, 2단계를 "`VERSION`은 열 수 있을 때만"으로 바꿨습니다. 웹 채팅 AI(ChatGPT·Claude 웹)는 사용자가 입력한 주소만 열 수 있어서 문서 안의 `VERSION` 주소를 열지 못해 "읽을 수 없음"을 오류처럼 보고하던 문제입니다. 이제 문서 버전을 `projectVersion`으로 쓰고 `확인 못함(문서 기준 v…)`만 보고합니다. 릴리스마다 이 줄이 `VERSION`과 같은지 `test_version_references.py`가 검사합니다.
- `release_tag.py`의 jsDelivr 확인을 고쳤습니다: 사내망처럼 TLS를 가로채는 환경에서 Python이 인증서 검증에 실패하면 요청 자체를 못 했는데도 "옛 파일"이라고 경고하던 것을, 공개 파일을 바이트 비교로 검증하는 읽기 요청에서는 인증서 검증에 막히지 않게 하고 "옛 파일"과 "확인 못 함"을 구분해 알립니다. 새 태그를 색인할 시간을 위해 최대 대기도 늘렸습니다.

## [2.3.4] - 2026-10-07

- **웹 AI가 쓰는 Web Runtime 주소를 `@v2.3.4` 같은 고정 태그에서 `@2`(메이저 범위)로 바꿨습니다**: bootstrap.md, README, SKILL.md. 웹 AI 서비스가 옛 `bootstrap.md` 복사본을 읽어도(전에는 v2.0.2를 읽었습니다) 그 문서가 가리키는 주소가 항상 최신 2.x 런타임이 되어, 릴리스마다 문서를 고칠 필요가 없고 옛 복사본이 최신 디자인을 막지 않습니다. 호환이 깨지는 MAJOR(3.x)는 `@2`가 자동으로 막습니다. 디자인 가이드 링크는 참고용이라 버전 고정(`rawcdn.githack.com/…/v버전/`)을 그대로 둡니다.
- **`release_tag.py`가 릴리스 직후 jsDelivr 캐시를 갱신합니다**: 새 태그를 올리면 jsDelivr가 한동안 404를 주고(그 실패를 기억합니다), `@2` 같은 범위 주소는 몇 시간 동안 옛 파일을 주던 문제를 막습니다. 태그를 푸시한 뒤 purge하고 `dist/nhimc-web.js`와 바이트가 같아질 때까지 확인하며, 안 맞으면 경고만 출력합니다(릴리스를 막지는 않습니다).
- 테스트: 문서의 Web Runtime 주소가 `VERSION`의 메이저 범위(`@2`)인지, CDN 주소 목록이 올바른지 검사합니다.

## [2.3.3] - 2026-10-07

- **첫 프롬프트를 다시 주소 한 줄로**: 2.3.2의 `?v=버전`·`VERSION` 줄은 릴리스마다 바꿔야 해서 되돌렸습니다. 사용자는 버전 없는 고정 주소 하나만 줍니다.
- **그 주소를 `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/refs/heads/main/bootstrap.md`로 바꿨습니다.** `main/bootstrap.md`와 같은 파일의 다른 표기입니다. Claude 웹이 `main/bootstrap.md`는 9월 30일의 옛 복사본(v2.0.2)을 계속 읽고 있었고, 이 표기로는 최신(문서 기준 v2.3.2)을 읽는 것을 확인했습니다. README, bootstrap, Design Guide(프롬프트 만들기 포함), 쉬운 가이드가 같이 바뀌었습니다.
- `bootstrap.md`: 사용자가 "이 파일만 읽고"라고 해서 `VERSION`을 열지 않으면 문서 안의 버전을 `문서 기준`으로 보고하도록 했습니다.
- 테스트: 첫 프롬프트가 버전 없는 한 줄 주소(`?v=` 없음)인지 검사합니다.

## [2.3.2] - 2026-10-07

- **웹 AI(ChatGPT·Claude 웹)에서 화면이 여러 개일 때 빈 화면이 되던 문제 수정**: AI가 `<main>` 하나에 모든 `data-screen-panel` 화면을 넣어도 Web Runtime이 화면마다 `<main>`을 만들어 줍니다. 전에는 `screen … must contain one content root` 오류 한 줄만 남고 화면이 비었습니다.
- **Web Runtime 오류를 알아보기 쉽게**: 오류가 나면 작은 글씨 대신 "화면을 만들지 못했습니다" 안내 상자와 원인 메시지를 보여 주고, 그 메시지를 AI에게 붙여 넣어 다시 만들게 하도록 안내합니다.
- **첫 프롬프트가 두 주소를 `?v=버전`과 함께 줍니다**: `bootstrap.md?v=…`와 `VERSION?v=…`. 웹 AI가 예전에 캐시한 `bootstrap.md`(예: v2.0.2)를 읽거나, 사용자가 주지 않은 `VERSION` 주소를 열지 못해 버전을 `확인 못함`으로 보고하던 문제를 줄입니다. README, bootstrap, Design Guide(프롬프트 만들기 포함), 쉬운 가이드가 같이 바뀌었고, Design Guide는 릴리스마다 버전이 자동으로 들어갑니다.
- `bootstrap.md`의 Web Runtime 절에 여러 화면 예시를 추가하고, `VERSION`을 열 수 없으면 문서 안의 버전을 `문서 기준`으로 쓰도록 했습니다.
- 테스트: 한 `<main>`에 모은 화면과 오류 안내를 브라우저로 확인하는 테스트 2개, 첫 프롬프트의 `?v=`가 `VERSION`과 같은지 검사하는 테스트를 추가했습니다.

## [2.3.1] - 2026-10-02

- **스킬 본문의 Web Runtime 주소가 `@v2.2.0`으로 남아 있던 것을 수정**: 2.3.0의 `SKILL.md`가 코드 실행이 안 되는 웹 환경에서 2.2.0 런타임을 불러왔습니다(이번 릴리스의 LEFT DUAL·TOP·BLOG 수정이 빠짐). `@v2.3.1`로 고쳤습니다.
- 모든 고정 릴리스 주소(`nhimc-ui-core@v…`, githack `…/v…/`)가 `VERSION`과 같은지 검사하는 `test_version_references.py`를 추가했습니다. 전에는 `skills/` 안의 주소가 검사 대상이 아니었습니다.

## [2.3.0] - 2026-10-02

- **다크 모드에서 TOP·BLOG의 메뉴가 안 보이던 문제 수정** (TOP 1.4.1, BLOG 1.7.1): 햄버거 버튼, 드로어의 닫기 버튼, 드로어 메뉴 항목이 색을 지정하지 않고 브라우저 기본 버튼색을 써서, 페이지는 다크인데 `color-scheme`이 light로 남아 있으면 검정이 되어 사라졌습니다. 다른 헤더 버튼처럼 `color:var(--fg)`를 지정했습니다.
- **BLOG 헤더의 좌우 여백이 좁은 화면에서 달랐던 문제 수정** (BLOG 1.7.1): 헤더 오른쪽에 스크롤바 칸(10px)을 항상 더해 좁은 화면에서 24px/34px로 어긋났습니다. 이제 본문 칼럼이 가운데에 있을 때만 더하고, 좁은 화면에서는 양쪽 24px로 대칭입니다.
- **LEFT DUAL 레일을 아이콘만 보이게**: 1단계 메뉴 레일에서 이름 글자를 빼고(스크린리더용 이름은 `aria-label`로 유지) 폭을 88px에서 64px로 줄였습니다. 항목은 44px 정사각 아이콘 버튼이고 항목 사이는 14px(키가 작은 화면에서는 6px)이며, 하위 메뉴 패널(224px)은 그대로입니다. 접으면 64px 레일만 남습니다. 1024px 미만의 햄버거 드로어도 같은 구조입니다. 왼쪽 아이콘 레일(64px)을 누르면 드로어 안에서 옆 패널에 그 메뉴의 세부 메뉴가 나오고(이동·닫힘 없음), 세부 메뉴를 누르면 이동하며 닫힙니다. 전에는 평평한 목록이었고 768~1023px에서는 LEFT의 태블릿 규칙 때문에 이름까지 사라졌습니다.
- **전체 검증이 훨씬 빨라졌습니다**: `verify_all.py`의 `python tests`가 새 `gated` 프로파일을 씁니다. 별도 게이트가 이미 같은 브라우저 행렬(frame render·modal stability·blog scroll owner·canonical parity·presentation safe area 48셀)을 돌리는데 `python tests`가 그것을 한 번 더 돌려 전체의 대부분(약 16분 중 약 15분)을 차지했습니다. 이 5개를 `@gate_covered`로 표시해 `gated`에서만 뺍니다. `run_python_tests.py --profile full`은 그대로 전부 돌립니다.
- **검증 안정화**: `verify_all.py`가 독립 검사를 4개씩 병렬로 실행합니다(`--jobs 1`로 순차 실행). 브라우저 검증 스크립트 4개는 페이지 target이 목록에 올라올 때까지 재시도해 간헐적인 "browser page target was not found"를 없앴고, 브라우저 탐색 경로에 `Program Files (x86)`의 Chrome을 추가해 `:has()`를 지원하지 않는 구형 Edge로 넘어가지 않게 했습니다.
- **다이얼로그를 열 때 화면이 흔들리는지 점검하는 게이트 추가** (`scripts/modal_stability.py`, `verify_modal_stability.mjs`, `verify_all.py`의 "modal stability"): 세로 스크롤바가 있는 긴 화면에서 도움말 시트·모바일 메뉴를 열기 전/열린 중/닫은 뒤에 헤더와 첫 카드의 x·y·width와 스크롤 위치가 같은지, 맨 위·중간 두 경우, 설치된 Chrome·Edge 모두에서 잽니다. 페이지 스크롤 잠금(`overflow:hidden`을 html/body에 거는 경우) 시나리오도 포함합니다.
  - LEFT·LEFT BLANK·LEFT DUAL·TOP·DEFAULT·BLOG(`main`)는 이미 흔들림이 없었습니다(잠금을 걸어도 그대로). Frame 쪽 스크롤 잠금 코드는 없고, 스크롤 컨테이너의 `scrollbar-gutter:stable`도 이중으로 잡히지 않습니다.
  - **BLOG 1.7.1** `document` 스크롤에서 두 가지를 고쳤습니다. ① 앵커용 `scroll-margin-top`이 모든 `[id]`에 걸려 있어서 도움말 시트를 닫고 포커스가 헤더의 도움말 버튼으로 돌아갈 때 페이지가 63px 위로 튀었습니다 → `.content [id]`로 한정. ② html/body에 `overflow:hidden` 잠금이 걸리면 스크롤바(17px)가 사라지고 sticky 헤더가 풀렸습니다 → `document` 스크롤은 그 잠금을 무시합니다(`overflow-y:auto!important`, body `overflow:visible!important`). 대신 이 모드에서는 모달이 열려도 뒤 화면이 스크롤될 수 있습니다.

## [2.2.0] - 2026-10-02

- **LEFT DUAL의 하위 메뉴 패널을 접을 수 있게**: 패널 제목 줄 오른쪽 끝의 접기 버튼으로 224px 패널을 접어 88px 레일만 남깁니다. 접힌 상태에서는 별도 펼침 버튼 없이 레일 메뉴를 누르면 패널이 다시 펼쳐집니다. 접고 펼 때 패널 폭이 부드럽게 줄고 늘며, 메뉴가 많아도 레일·패널에 스크롤바가 보이지 않습니다(키가 작은 화면에서는 레일 항목이 촘촘해짐). 브랜드 줄 아래 구분선은 뺐습니다.
- **LEFT DUAL Frame 추가** (1.0.0): vendor 파일은 그대로 두고 LEFT 레이아웃에서 파생합니다(`scripts/derived_frames.py`, `canonical_frame.layout_source`).
  - `left-dual`: 1단계 메뉴는 아이콘+이름 레일(88px, 이름 글자 10px, 맨 위 36px 일산병원 마크, 마크 위아래 여백 10px로 TOP Frame 로고와 같음), 선택한 메뉴의 하위(children) 화면은 옆 패널(224px, 제목 줄 높이가 헤더와 같고 아래 선은 없음)에 나옵니다. 하위 메뉴가 없는 항목은 패널에 자기 자신만 나옵니다. 레일·패널은 `src/frames/dual-runtime.js`가 평평한 LEFT 메뉴에서 만들고, 그러려고 side 메뉴 링크에 `data-parent-id`를 달았습니다. 1024px 미만은 햄버거 드로어입니다.
  - AI 추천 후보에는 들어가지만 가장 후순위입니다(`top-left`·`top`으로 담기 어려운 2단계·다수 하위 화면 메뉴일 때만). `frame: left-dual`로 명시해도 됩니다.
- **BLOG Frame 레이아웃 개선** (BLOG 1.7.0): 내용이 가운데 한 줄(최대 1080px)로 모이고, 헤더는 로고 왼쪽·메뉴 오른쪽(도움말·테마 버튼 앞)이고 안쪽 폭이 내용 칸(Page의 좌우 여백은 BLOG에서 0)의 좌우 끝과 같습니다(좁은 화면 포함).
- **Design Guide의 Frame·Component 목록을 업데이트 시각 최신순으로 정렬**하고, 바뀐 Frame(BLOG·PRESENTATION 둘·LEFT DUAL)의 업데이트 시각을 2026.10.02로 갱신했습니다.
- **AI 추천 규칙 위치 정정**: 앞서 `vendor/.../rules/layout.md`를 고쳤더니 vendor 해시 검증(`upstream.digest`)이 깨져 되돌렸습니다. AI 추천 제한은 `bootstrap.md`·`SKILL.md`에만 두고 layout.md보다 우선한다고 적었습니다.
- **BLOG Frame의 `site-header`를 반투명으로 변경** (BLOG 1.6.0): `--site-header-surface`를 페이지 배경(캔버스)색 40%(`rgba`)로 두고 `backdrop-filter: blur(12px)`를 추가했습니다. `main`·`document` 스크롤 모두 같고, `document`의 sticky 헤더는 테두리·그림자를 그대로 유지합니다. 눈에 보이도록 `main` 스크롤도 Main이 헤더 밑까지 올라와 내용이 헤더 뒤로 비치게 했습니다(음수 margin + header 높이만큼 padding-top, 앵커는 `scroll-margin-top`). 완전 투명 + sticky 조합만 계속 금지합니다. 보호 파일 `frame_patches.py` 해시를 모든 Frame에서 갱신하고 `dist/nhimc-web.js`를 다시 빌드했습니다.
- **PRESENTATION·PRESENTATION VERTICAL Frame 왼쪽 위에 일산병원 로고 추가** (두 Frame 1.2.0): TOP Frame의 로고 SVG를 도움말 버튼과 같은 줄(top 20px)에 32px 높이(모바일 26px)로 넣었습니다.
## [2.1.0] - 2026-10-01

- **BLOG·TOP·DEFAULT Frame의 `site-header` 높이를 64px에서 56px로 줄임** (BLOG 1.5.0, TOP·DEFAULT(top-left) 1.4.0). 모바일 드로어 머리(56px)와 같은 높이입니다.
  - BLOG: `--site-header-height` 값을 56px로 바꿨습니다. 문서 스크롤(`document`)일 때 헤더에 가려지지 않게 앵커가 띄우는 간격도 이 값을 따라 56px + 16px로 줄어듭니다.
  - TOP: `.site-header`의 `height`를 56px로 바꿨습니다.
  - DEFAULT(top-left): 첫 번째 행 높이(`grid-template-rows`)를 데스크톱·모바일 모두 56px로 바꿨습니다. 사이드바 접힘 너비 64px는 헤더가 아니라 그대로입니다.
  - LEFT·LEFT BLANK·PRESENTATION Frame은 바뀌지 않았습니다. 보호 파일 `frame_patches.py` 해시를 모든 Frame에서 새로 갱신했습니다. `blog_scroll_owner.py` 브라우저 검증은 헤더 높이 기대값을 56으로 바꿨습니다.
  - `guide/nhimc-design-guide-easy.html`은 예전 TOP Frame(64px)이 박힌 완성 파일이라 이번 변경에 따라오지 않습니다(원본이 저장소에 없어 다시 빌드하지 못함).
- **카드 머리·팝업 머리·필수/선택 배지에 구분 색 추가 (`data-nhimc-accent`)**: 참고한 CancerFormAuto 화면처럼 구역마다 파스텔 색을 입힐 수 있게 Core 레이아웃(`src/layouts/primitives.css`)에 속성 하나로 쓰는 색 규칙을 추가했습니다. 값은 `sky`·`pear`·`apricot`·`yellow`·`purple`·`pink`·`amber`. 예전에는 `style="background:var(--color-chip-sky)…"`를 카드마다 직접 적어야 했습니다.
  - `ContentCard`: `<section class="card nhimc-card" data-nhimc-accent="sky">`로 머리 배경·글자색·테두리가 한 번에 바뀝니다. 머리의 건수 글자도 같은 색으로 읽힙니다.
  - `Dialog`: `<dialog class="dialog-box" data-nhimc-accent="sky">`로 팝업 머리에 같은 색이 들어가고 위쪽 모서리가 둥글게 맞습니다.
  - `Badge`: `<span class="badge" data-nhimc-accent="pink">필수</span>`. 입력 라벨(`label.field`) 안의 배지는 줄 높이를 밀지 않게 작게 맞춥니다.
  - 모든 색 테마에서 동작합니다. 칩 색은 라이트·다크 모두 같은 파스텔이고, 글자색은 테마의 `--color-accent-*-foreground`가 있으면 그 값을, 없으면 `--color-chip-foreground`를 씁니다. `purple`·`pink`·`amber` 칩은 Color Mix 테마에만 정의돼 있어 다른 테마에서는 각각 `sky`·`apricot`·`yellow` 색으로 대신 보입니다(일곱 색을 모두 쓰려면 `theme: color-mix`).
  - Frame은 바뀌지 않았습니다(Frame 버전·보호 파일 해시 그대로).
- **Design Guide 업데이트 시각 갱신**: 위 변경이 닿는 Card·Dialog·Badge Component의 업데이트 시각을 2026.10.01 15:55으로 바꾸고, 세 미리보기에 새 색 변형을 보여줍니다. 가이드 빌더의 시각 보정표 이름을 `FRAME_UPDATED_AT`에서 `UPDATED_AT`으로 바꿨습니다(Frame 외 항목도 보정하므로).
## [2.0.2] - 2026-09-30

- **Design Guide Frame 업데이트 시각 갱신**: 그라데이션·헤더 간격을 고친 LEFT, LEFT BLANK, DEFAULT(top-left) Frame이 업스트림의 옛 업데이트 시각(2026.09.18·09.21)을 그대로 보여주던 것을 이번 수정 시각으로 바꿨습니다.
- **`frame:` 줄이 없을 때의 기본 동작 변경**: 예전에는 `left`로 고정했지만, 이제 `(미선택 - AI 추천)`과 똑같이 업무에 맞춰 AI가 Frame을 고릅니다(`bootstrap.md`, `SKILL.md`). `theme:` 줄이 없으면 `nhimc-default`를 씁니다. "디폴트로 해줘"라고 명시하면 계속 `left`입니다. 빌더의 `data-frame` 누락 시 `left` 폴백은 그대로입니다.
- **쉬운 버전 가이드 추가**: 비개발자용 한 페이지 가이드 `guide/nhimc-design-guide-easy.html`(TOP Frame)을 추가하고 `skills/nhimc-worktool/resources/guide/`에 미러링했습니다. 복사 한 번으로 설치와 화면 만들기, 프롬프트로 고치기, 실제 Frame 미리보기와 Theme 갤러리가 들어 있습니다.

## [2.0.1] - 2026-09-30

- **LEFT·LEFT BLANK 로고 테두리 제거, 사이드바 그라데이션** (Frame 1.3.0). 일산병원 로고 둘레에 깔았던 반투명 패널(테두리)을 없앴습니다. 대신 파란 사이드바·셸 배경이 위에서 아래로 연한 색에서 진한 색으로 이어지는 그라데이션(사이드바 토큰 위에 흰색 16% → 검정 26% 반투명 겹침, 다크는 7% → 30%)이 되어 로고의 파란 부분이 위쪽 연한 배경 위에서 또렷이 보입니다. 색상 테마를 바꿔도 같은 방식으로 적용되며 모바일(767px 이하)은 기존 배경을 유지합니다. LEFT BLANK의 접힌 레일은 정본 그대로입니다.
- **DEFAULT Frame 헤더 간격**: 로고 옆 구분선이 프로젝트명·로고와 2px만 떨어져 붙어 보이던 것을 양쪽 10px로 넓혔습니다(Frame 1.3.0).

## [2.0.0] - 2026-09-30

- 메이저 버전을 2.0.0으로 올렸습니다. 1.4.3 이후 `main`에 들어간 변경(콘텐츠 레이아웃·검증 워크플로 개선)을 포함하며, 이 릴리스 자체에서 코드·Frame·정본을 바꾸지는 않았습니다(Frame 버전은 그대로). 플러그인·Web Runtime 주소의 태그는 `v2.0.0`입니다.

## [1.4.3] - 2026-09-29

- **"프롬프트 힌트 해석"의 `frame: <id>` 설명이 기본 Frame 이름을 헷갈리게 썼던 문제 수정.** `bootstrap.md`가 "없으면 `left`(`nhimc-default`)."라고 레지스트리 내부 id(`nhimc-default`)를 `left`와 나란히 노출해서, "디폴트로 해줘"라는 요청을 처리할 때 어떤 이름을 써야 하는지(`left`인지 `nhimc-default`인지) 혼동을 일으켰습니다. `nhimc-default`는 `registry/frames.json`의 내부 id일 뿐 `frame:` 값으로 쓰지 않는다는 점을 명시하고, "디폴트로 해줘"는 항상 `left`를 뜻한다고 못박았습니다.

## [1.4.2] - 2026-09-29

- **버전-태그 동기화 안전장치 추가.** v1.4.0·v1.4.1이 커밋만 되고 git 태그가 만들어지지 않아 bootstrap.md·Design Guide가 안내하는 `v1.4.1` githack·jsdelivr 링크가 실제로는 404였던 문제를 발견하고 수정했습니다(누락된 `v1.4.0`, `v1.4.1` 태그를 해당 릴리스 커밋에 만들어 푸시).
  - `scripts/release_tag.py` 신설: `VERSION`에 맞는 `v<VERSION>` 태그를 만들고 `origin`에 푸시합니다. 이미 있고 같은 커밋을 가리키면 그대로 두고, 다른 커밋을 가리키면 오류로 막습니다.
  - `scripts/verify_release.py`가 이제 현재 `VERSION`에 대응하는 git 태그가 없으면 `RELEASE BLOCKED: release tag`로 막습니다. `README.md`의 릴리스 절차에 `python scripts/release_tag.py` 단계를 추가했습니다(`verify_all.py` 다음, `verify_release.py` 전).
- **"NhimcDesign을 GitHub로 옮긴 프로젝트" 같은 옛 마이그레이션 문구를 전부 정리.** `README.md`(정본 출처 행, 플러그인·스킬 이름 행의 괄호 설명, 첫 인용문), `bootstrap.md`, `SKILL.md`(제목·설명·본문), `src/guide/sections.html`(설치 안내 문단과 노트), 4개 플러그인 매니페스트(`plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `gemini-extension.json`)의 `description`에서 "NhimcDesign(NHIMC Worktool)을 GitHub로 옮긴 프로젝트" 서술과 "(기존 NhimcDesign와 동일)" 표기를 제거했습니다. 벤더 스냅샷 커밋 고정 사실(`08c45402eece`)은 "NhimcDesign" 이름 없이 별도 행으로 유지했습니다.
- **Design Guide 헤더에 버전과 릴리스 날짜 표시.** `scripts/build_design_guide.py`가 `CHANGELOG.md`에서 현재 `VERSION`에 해당하는 날짜를 읽어 헤더 부제(옛 "NhimcDesign · nhimc-worktool" 문구 자리)에 "v{version} · 최종 업데이트 {날짜}"를 넣습니다. 릴리스마다 재빌드하면 자동으로 최신 날짜로 갱신됩니다.
- 회귀 테스트: `tests/python/test_release_tag.py`(신규), `verify_release.py`의 태그 게이트, Design Guide 헤더 문구·"NhimcDesign" 완전 제거를 확인하는 테스트를 추가했습니다.

## [1.4.1] - 2026-09-29

- **최초 진입 프롬프트가 `.git` 주소를 쓰던 문제 수정.** 사용자가 처음 붙여넣는 문장에 `https://github.com/SIMI-HC/nhimc-ui-core.git`이 들어 있으면 AI가 `bootstrap.md`를 읽기도 전에 clone부터 하는 경우가 있었고("클론하지 않습니다"라는 문서 안 지침은 이미 늦게 읽힘), 로컬 사본을 읽고도 "raw로 읽었다"고 착각하는 경우도 있었습니다.
  - `bootstrap.md`, `README.md`, Design Guide의 설치 프롬프트(`src/guide/sections.html`, `scripts/build_design_guide.py`의 "프롬프트 만들기")가 이제 `.git` 주소 대신 `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md`와 "이 파일만 읽고 NHIMC UI Core를 준비해줘. (git clone 금지)"를 씁니다.
  - `bootstrap.md` 제목 바로 아래에 5줄 이내 "먼저 지킬 규칙" 블록을 추가했습니다(clone/pull 금지, 작업 폴더 클론 금지, 공식 등록 경로만 사용, 원격 `VERSION`은 raw로 확인). 기존 첫 문단에 있던 같은 내용은 이 블록으로 옮기고 중복을 지웠습니다.
  - 클론이 허용되는 유일한 예외(공식 등록 불가·거절 + 로컬 셸에서 실제 검증된 산출물 필요 시, 임시/scratch 경로 한정)는 "웹에서 URL 없는 완성 HTML을 다운로드 파일로 주기" 절 한 곳에만 두었고, 준비 절차 5단계 본문에서는 그 절을 가리키는 한 줄만 남겼습니다(9단계 구조 자체는 그대로).
  - `tests/python/test_design_guide.py`, `tests/python/test_bootstrap_contract.py`의 관련 문구 검사를 새 프롬프트·규칙 블록에 맞춰 갱신했습니다.

## [1.4.0] - 2026-09-29

- **메뉴 id가 아이콘 이름과 같으면 아이콘이 안 보이던 결함 수정** (Frame: left 1.2.2). 원인: 여러 Page가 있는 화면에서 빌더가 각 Page를 감싸는 `<section>`에 메뉴 `id`를 그대로 HTML `id` 속성으로 썼는데(`scripts/build_single_html.py`), 아이콘 스프라이트에도 같은 이름의 `<symbol id="...">`가 있어 문서에 같은 `id`가 두 번 생겼습니다. 메뉴 아이콘의 `<use href="#id">`는 브라우저 규칙상 문서 순서상 먼저 나오는 요소(스프라이트보다 앞서 삽입되는 `<section>`)로 해석되어, `<symbol>`이 아니라 화면 Page 컨테이너를 가리키며 아이콘이 렌더되지 않았습니다. 빌더와 기존 브라우저 검증은 이 충돌을 확인하지 않아 PASS로 통과했습니다.
  - `scripts/build_single_html.py`, `scripts/canonical_frame.py`(Page 컨테이너 id, PRESENTATION 단일 슬라이드 id), `src/web/nhimc-web.template.js`(Web Runtime의 동일 로직)가 이제 실제 HTML `id`에 `screen-<메뉴id>` 네임스페이스를 씁니다. 메뉴 `href="#id"` 저작 규약과 런타임의 `[data-screen-panel]`/`[data-menu-id]` 기반 화면 전환은 그대로입니다(런타임은 `id`나 `href`로 화면을 찾지 않고 항상 이 속성들로 찾습니다).
  - `canonical_frame.render_layout()`과 Web Runtime 둘 다 최종 문서에 중복 `id`가 남아 있으면 어떤 경우든 명확한 오류로 빌드를 막습니다(이 종류의 결함 전체에 대한 이중 안전장치).
  - 회귀 테스트: `tests/python/test_single_html.py`가 기존 `tests/fixtures/authoring/multi-page/index.html`(메뉴 id·아이콘이 모두 "dashboard")로 실제 재현 조건을 검증하고, 실제 Chrome으로도 확인했습니다.
- **브라우저 검증 강화**: `scripts/verify_standalone_browser.mjs`(최종 산출물 검증)가 문서 전체의 중복 `id`와, 메뉴 아이콘의 `<use href="#...">`가 실제 `<symbol>`로 해석되고 화면에 보이는 아이콘이 0 크기가 아닌지 확인합니다(숨겨진 모바일 메뉴 사본처럼 원래 화면에 없는 아이콘은 크기 검사에서 제외). `scripts/verify_frame_render.mjs`/`scripts/frame_render.py`(left·top·top-left·blog × 테마 × 뷰포트 504칸 행렬)도 각 메뉴 아이콘이 `<symbol>`로 해석되는지 함께 측정·게이트합니다.
- **Core 아이콘 추가 절차 신설**: `vendor/nhimc-design/icons/nhimc-icons.svg`는 상위 저장소 고정 commit과 바이트 동일한 미러라 직접 편집할 수 없어, 등록되지 않은 아이콘이 필요할 때 정식 경로가 없었습니다. `scripts/icon_overlay.py`가 Core 소유 오버레이(`src/generated/icons/core-icons.svg`, 기본은 비어 있음)를 빌드 시점에 정본 스프라이트와 합칩니다(`scripts/frame_patches.py`가 Frame 동작 괴리를 다루는 것과 같은 패턴). 모든 symbol은 스타일 규격(`viewBox="0 0 24 24"`, 내부 요소에 `fill`/`stroke`를 직접 넣지 않아 공용 아이콘 래퍼의 `currentColor`를 그대로 상속, `data-label`·`data-category`·`data-updated-at` 필수)을 추가 시점과 `validate_design.py` 실행 시점 모두에서 검증하며, 벤더 아이콘과 겹치는 id는 거부합니다. `scripts/add_canonical_icon.py`가 정식 추가 절차이며, symbol 추가와 함께 `src/guide/upstream/gallery-data.json`(Design Guide 아이콘 미리보기)에도 같은 항목을 추가합니다. `registry/assets.json`에 오버레이 파일의 protected 항목을 등록했습니다.
- `bootstrap.md`·`SKILL.md`: 메뉴 id를 아이콘 이름과 겹치지 않게 짓도록 안내하고(구조적으로는 이제 겹쳐도 깨지지 않지만 명확성을 위해 권장), 맞는 아이콘이 없으면 임의로 비슷한 아이콘을 쓰지 말고 사용자에게 알린 뒤 승인받아 Core 아이콘 추가 절차로 추가하도록 명시했습니다.

## [1.3.2] - 2026-09-29

- **도움말 패널·모바일 메뉴가 바깥 클릭으로 닫히지 않던 결함 수정** (Frame: left·left-blank·top-left 1.2.0, top 1.3.0, blog 1.4.0). 원인: 실제 빌드에 들어가는 `src/generated/frame/frame-runtime.js`에 바깥 클릭 처리가 없었습니다(정본 Frame 인라인 스크립트에는 있지만 빌드는 그 스크립트를 이 런타임으로 교체합니다). 그래서 X 버튼과 Esc만 닫혔습니다. 이제 도움말·모바일 dialog는 패널 밖(backdrop) 클릭 시 닫히고, TOP·BLOG의 `.nav-backdrop` 클릭은 `nav-open`을 해제하고 메뉴 버튼의 `aria-expanded`를 `false`로 되돌립니다. Web Runtime(`dist/nhimc-web.js`)에도 같이 들어갑니다.
  - 회귀 테스트: `scripts/outside_click.py`(`run_browser_tests.py --outside-click-only`, `verify_all`, `verify_release`)가 left·left-blank·top·top-left·blog에서 실제 마우스 클릭으로 도움말 열기 → 안쪽 클릭(유지) → 바깥 클릭(닫힘), 390px에서 메뉴 열기 → 바깥/backdrop 클릭 → 닫힘·`aria-expanded` 복귀를 확인합니다. 수정 전 런타임에서는 5개 Frame 모두 실패합니다.
- **최종 산출물은 `index.html` 하나만 남기기**: 저작 원본(`source.html`)을 사용자 프로젝트 폴더의 결과물 옆에 저장하던 문제. `SKILL.md`(필수 순서 6번, “전달 경계”)와 `bootstrap.md`(“기본 산출물 계약”, “웹에서 URL 없는 완성 HTML”)에 원본은 임시 위치(Claude Code: 세션 scratchpad 또는 OS 임시 폴더)에 두고 `--input`만 임시 경로, `--output`만 사용자 폴더의 `index.html`로 주며, 빌드 뒤 출력 폴더에 다른 파일이 있으면 삭제하거나 임시 위치로 옮기고, 사용자가 “원본도 보관해줘”라고 명시할 때만 원본을 출력 폴더에 두며, 결과 보고에는 `index.html` 경로만 쓴다고 명시했습니다. `build_verified_artifact.py`는 출력 폴더에 `index.html` 외 항목이 있으면 stderr로 경고합니다(자동 삭제 없음).
- **플러그인을 이미 설치했는데도 AI가 저장소를 작업 폴더에 클론하던 문제 수정** (`bootstrap.md` “준비 절차”, `SKILL.md` “준비 절차 요약”). 플러그인 캐시에 저장소 전체(registry·scripts·guide·SKILL·vendor)가 들어 있어 클론은 불필요하고 작업 폴더만 어지러워졌습니다.
  - `git clone`/`git pull`은 **스킬·플러그인이 설치돼 있지 않을 때만** 합니다(2단계, “웹에서 URL 없는 완성 HTML” 1단계).
  - 플러그인이 설치돼 있으면 클론하지 않고 원격 raw `VERSION`만 읽어 비교하며, registry·scripts·guide·SKILL은 플러그인 설치 경로 `<루트>`(Claude Code: `~/.claude/plugins/cache/<마켓플레이스>/nhimc-worktool/<버전>/`)에서 읽습니다. 빌더도 설치 경로의 `scripts/`를 실행하고 결과물만 작업 폴더에 둡니다.
  - 새 버전이면 업데이트 여부를 먼저 묻고, 승인하면 공식 경로(Claude Code: `claude plugin marketplace update` + `claude plugin update`)로 갱신합니다. 클론으로 대신하지 않습니다.
  - Design Guide도 클론이 아니라 `<루트>/guide/nhimc-design-guide.html`을 엽니다.
  - “사본이 남아 있어도 1~5를 생략하지 않는다”는 문구는 유지하되, 사본에 플러그인 설치본(플러그인 캐시)을 포함한다고 명시했습니다.

## [1.3.1] - 2026-09-29

- **일산병원 로고의 흰색 테두리(타일) 제거** (Frame: left·left-blank·top-left 1.1.0, top 1.2.0, blog 1.3.0). 로고 뒤 흰색 둥근 배경, 안쪽 여백(3px 5px), 그림자, 모서리 반경을 모두 없애 로고 그림 그대로 보입니다. 펼친 가로 로고와 접힌 레일의 단독형 마크 모두 적용됩니다. 벤더 미러는 그대로 두고 `scripts/frame_patches.py`가 오프라인 빌더·Web Runtime·Design Guide에 공통 적용합니다. 로고 크기는 타일 안쪽 여백만큼(높이 36px 안에서 30px → 36px) 커집니다.
- 타일을 없애자 라이트 테마의 남색 사이드바에서 로고의 남색 블록이 배경에 묻혀 경계가 안 보였습니다. 흰 선 대신 LEFT·LEFT BLANK 사이드바 로고 뒤에 사이드바 토큰 `--color-sidebar-brand-18`의 반투명 패널(활성 메뉴 행과 같은 옅은 면)을 사방 패딩 3px, 모서리 3px로 깔았습니다. 흰색이 아니고 라이트·다크 모두 같은 토큰으로 자동 전환됩니다. LEFT BLANK를 접은 레일은 정본 그대로(접기 버튼만, 로고 마크 없음)입니다.

## [1.3.0] - 2026-09-29

- **로컬 빌더·Web Runtime Frame 렌더링 결함 수정** (Frame: blog 1.2.0, top 1.1.0).
  - 테마 색이 적용되지 않던 문제: `[data-theme-color="pear"]` 등 Theme 덮어쓰기 CSS가 `<head>` 맨 앞에 들어가 Frame 자체의 `[data-theme="light"]{--color-primary:#003d94…}`(같은 우선순위, 나중 것이 이김)에 덮였습니다. 라이트 모드에서 mint·pear·apricot·neutral이 모두 남색으로 나왔고 **로컬 빌더와 Web Runtime 두 경로 모두, 모든 Frame**에서 같았습니다(다크는 선택자가 더 구체적이라 정상). Theme 덮어쓰기를 `</head>` 직전의 별도 `<style data-nhimc-theme-color-bundle>`로 옮겼습니다(`build_single_html.py`, `build_web_runtime.py`, `nhimc-web.template.js`).
  - 메뉴 아이콘이 크게 렌더되던 문제: BLOG 헤더 메뉴에는 svg 크기 규칙이 없어(TOP은 17px) 1440px에서 56px로 라벨을 덮었고, BLOG·TOP의 모바일 Drawer 메뉴 아이콘도 크기 규칙이 없어 열면 184px였습니다. `scripts/frame_patches.py`가 BLOG 헤더 아이콘(17px, 라벨 옆)과 BLOG·TOP Drawer 아이콘(18px)을 정합니다. `.topnav button span.label{display:none}`(1024px 미만 아이콘 모드)은 TOP과 같은 의도이며, 아이콘만 남는 메뉴 버튼이 이름을 잃지 않도록 메뉴 버튼에 `aria-label`·`title`을 넣었습니다.
  - 검증: `scripts/frame_render.py`가 모든 Frame × Theme 6종 × 라이트/다크 × 1440/768/375px × 로컬 빌더/Web Runtime = 504칸에서 계산된 `--color-primary`·주요 Button 색, 메뉴 아이콘 크기·라벨 겹침·접근 가능한 이름, 가로 스크롤을 측정합니다(`--frame-render-only`, `verify_all`, `verify_release`). 완료 검증(`verify_standalone_browser.mjs`)도 선택한 테마의 `--color-primary`와 메뉴 아이콘 상한(24px)을 확인하므로, 예전처럼 PASS인데 화면이 깨진 산출물이 나오지 않습니다.
- Marketplace 등록 파일 추가: `.claude-plugin/marketplace.json`(Claude Code)과 `.agents/plugins/marketplace.json`(Codex). 저장소에 마켓플레이스 파일이 없어 `marketplace add`가 404 / "Marketplace file not found"로 실패하던 문제입니다.

- **BLOG Frame 스크롤 소유자** (`blog`, Frame 1.1.0). 원인: BLOG 헤더의 투명은 테마 블록의 `background-color: transparent !important`로만 유지되어, 문서 스크롤 화면에서 헤더를 sticky로 바꾸면 투명한 채 콘텐츠와 겹쳤습니다. `scripts/frame_patches.py` 1.2.0이 스크롤 소유자를 BLOG Frame 안의 상태(`<html data-scroll-owner="main|document">`)로 추가했습니다. 새 Layout variant는 만들지 않았습니다.
  - `main`(기본): app-shell `100svh`, SiteHeader `flex:none`, Main(`.content`)만 스크롤하고 헤더는 투명을 유지합니다.
  - `document`: 문서가 스크롤하고 SiteHeader는 sticky + 불투명(`--color-background`) + `--color-border-accent` 하단 경계 + 정본 `--shadow-lg`입니다. 앵커는 `scroll-margin-top`으로 헤더를 피합니다. 모바일 Drawer(z-index 10)는 헤더(8) 위에 그대로 열립니다.
  - `!important` 투명 강제 규칙(`.site-header`, `.statusbar`)을 제거하고 헤더 배경은 토큰 `--site-header-surface`로 제어합니다. `<header>`에 카드 surface를 강제하던 규칙은 `header:not(.site-header)`로 한정해 도움말 Dialog 헤더는 그대로입니다.
  - 선택은 `<html data-scroll-owner>` 또는 `<nhimc-frame data-scroll-owner>`이며 BLOG 외 Frame은 `document`를 거부합니다. `:has()`를 쓰지 않아 구형 Edge에서도 동작합니다.
  - 검증: `scripts/blog_scroll_owner.py`가 main/document × light/dark × 375/768/1440px × 오프라인/Web Runtime 24칸에서 긴 콘텐츠를 실제로 스크롤해 헤더 고정·불투명·겹침·앵커·모바일 메뉴·도움말·가로 스크롤을 측정합니다. `verify_all`, `verify_release`에 게이트를 추가했고 회귀 테스트는 `tests/python/test_blog_scroll_owner.py`입니다.
  - vendor(`vendor/nhimc-design`)는 바이트 동일 미러라 고치지 않았습니다. 상위 catalog·layout 규칙 문서에는 이 상태가 없으므로 NhimcDesign 정본에 반영될 때까지 Core 문서(`bootstrap.md`, `SKILL.md`, Design Guide)가 기준입니다.

## [1.2.2] - 2026-09-29

- Web Runtime: 1.2.1에서 넣은 "Frame이 갖춰지면 오프라인 HTML을 자동 저장" 동작을 되돌렸습니다. 페이지를 열거나 새로고침할 때마다 파일이 반복해서 다운로드되는 문제가 있었습니다. 이제 Web Runtime은 순수 미리보기이며 아무 것도 자동으로 저장하지 않습니다. `window.nhimcExportHtml()`은 도구용으로 남아 있습니다. 외부 링크 없는 진짜 오프라인 파일은 로컬 환경(Claude Code · Codex · Gemini CLI)에서 `build_verified_artifact.py` / `build_single_html.py`로 만듭니다.

## [1.2.1] - 2026-09-29

- Web Runtime: “오프라인 HTML 저장” 버튼을 없애고, Frame이 갖춰지면 오프라인 HTML을 자동으로 저장합니다. `window.nhimcExportHtml()`은 그대로 남아 있습니다.

## [1.2.0] - 2026-09-29

- **Presentation Base Contract** (`presentation`, `presentation-vertical`, Frame 1.1.0). 두 Frame은 방향(슬라이드 이동 축, 방향키, Flow 방향)만 다르고 나머지는 같은 계약과 같은 코드를 씁니다.
  - 공통 Runtime `src/presentation/presentation-runtime.js`: 상위 정본 Presentation 스크립트(슬라이드 생명주기, transition, prev/next, 점, 키보드, 테마, 도움말)에서 방향만 매개변수로 뺀 것입니다. 이전에는 범용 Runtime이 슬라이드 animation 없이 `hidden`만 바꿔서 전환 애니메이션이 사라져 있었습니다.
  - Frame이 슬라이드 요소(`section.slide[data-screen-panel]`)를 소유합니다. 오프라인 빌더와 Web Runtime이 Content를 그 안에 넣습니다.
  - Content는 Safe Area의 시각적 중앙에 놓입니다. 정본 `.slide`(중앙 정렬 flex, transition)의 padding을 Header·Controller가 차지하는 공간으로 잡고 스크롤바 gutter를 양쪽에 예약합니다. 페이지가 위치를 보정할 필요가 없습니다.
  - Layout Primitive 추가: `PresentationContent`(자동 배치), `PresentationHero`, `PresentationFlow`. 발표용 Content 규칙(한 슬라이드 = 핵심 메시지 하나, 60~75%)을 `bootstrap.md`와 `SKILL.md`에 명시했습니다.
  - `registry/frames.json`: 공통 계약(`baseContracts.presentation`)과 두 Frame의 `extends`, `owns`(header, controller, safe area, center, transition, navigation, runtime)를 명시했습니다.
- 검증 게이트 확장: 두 Frame × light/dark × 데스크톱·900×600·좁은 세로 × 오프라인/Web Runtime 결과를 측정합니다(48칸). Safe Area 침범, 중앙 정렬, 초과 감지, 전환 클래스, prev/next·점·방향키, 두 Frame의 Header·Theme·Branding·Controller·timing 동일성, 라이트·다크 대비.
- Design Guide: 두 Presentation Frame을 가로 발표/세로 발표로 구분해 설명하고 공통 기능을 함께 보여 줍니다.

## [1.1.1] - 2026-09-29

- **PRESENTATION Frame(`presentation`, `presentation-vertical`) Content Safe Area** (Frame 1.0.1). 원인: Header(도움말·테마 버튼)와 Controller(슬라이드 점·화살표)가 전체 화면을 덮는 Content 슬롯 위에 떠 있어 AI Content가 그 아래로 들어갔습니다. `scripts/frame_patches.py`가 콘텐츠 슬롯을 컨트롤이 차지하는 공간만큼 안쪽으로 들이고(Frame 소유 CSS 변수 `--presentation-safe-*`) Content는 그 안에서만 스크롤합니다. 개별 화면에 margin/padding을 넣을 필요가 없습니다. 다른 Frame은 바뀌지 않습니다.
- Web Runtime(`dist/nhimc-web.js`)도 같은 패치를 씁니다.
- 검증: 오프라인 빌더와 Web Runtime 결과를 두 PRESENTATION Frame × light/dark × 데스크톱·좁은 세로 화면에서 측정(`scripts/presentation_safe_area.py`)하고, 지나치게 긴 Content가 Safe Area 초과로 감지되며 Header·Controller 위치는 그대로인지 확인합니다. `verify_all`과 `verify_release`에 게이트를 추가했습니다.
- 정확한 완료 검증(`build_verified_artifact`)이 Frame별 기대값을 쓰도록 고쳤습니다. 이전에는 LEFT 계열만 통과하고 top·top-left·blog·presentation은 실패했습니다. PRESENTATION 산출물은 16:9 캔버스에서 모든 페이지가 Safe Area에 들어가는지도 확인합니다.
- Design Guide: “정본 보기” 버튼(GitHub의 해당 릴리스 정본 파일)을 되살렸고, 프롬프트에서 버전 확인 문구를 뺐습니다(`bootstrap.md`가 담당).
- `bootstrap.md`: 스킬·플러그인이 등록돼 있지 않으면 사용자에게 먼저 묻고, 등록돼 있고 더 새 버전이 있으면 스킬·플러그인도 함께 업데이트합니다.

## [1.1.0] - 2026-09-29

- Web Runtime 화면 오른쪽 아래에 “오프라인 HTML 저장” 버튼을 추가했습니다. 누르면 CSS·스크립트·폰트를 모두 안에 넣은 단일 HTML 파일을 내려받으며(외부 URL·`<script src>` 없음), 인터넷 없이 열립니다. 저장 버튼은 저장된 파일에 포함되지 않습니다.
- 저장한 파일을 네트워크를 막은 브라우저에서 열어 Frame이 정상 표시되고 콘솔 오류가 없는지 테스트에 추가했습니다.

## [1.0.1] - 2026-09-28

- Web Runtime의 “CSS가 늦게 로드되는 것처럼 보이는” 현상을 고쳤습니다. 원인은 3MB짜리 스크립트가 다 내려받아질 때까지 스타일 없는 Content가 먼저 보였기 때문입니다.
  - 폰트를 base64로 넣지 않고 같은 검증된 파일을 CDN URL로 불러오도록 해 스크립트를 3.1MB에서 0.9MB(압축 전송 약 0.3MB)로 줄였고, 폰트는 스크립트와 병렬로 미리 받기 시작합니다.
  - Frame이 씌워지기 전에는 페이지를 숨기고(`visibility:hidden`) 씌운 뒤 보여 주며, 오류가 나도 반드시 다시 보이게 합니다.
  - `<script src>`는 `<head>`에 두도록 안내를 바꿨습니다.
- 오프라인 `index.html`은 그대로 폰트를 안에 포함합니다(인터넷 없이 열림).

## [1.0.0] - 2026-09-28

첫 공개 릴리스입니다. NhimcDesign(NHIMC Worktool)을 GitHub로 옮긴 프로젝트이며 플러그인·스킬 이름은 기존과 같은 `nhimc-worktool`입니다.

- 정본 Frame 7종(left, left-blank, top, top-left, presentation, presentation-vertical, blog), Theme(light/dark + color 5종), Component 49종, 일산병원 로고·아이콘·Noto Sans KR을 정본 스냅샷(NhimcDesign `v1.3.29`, 커밋 `08c45402eece`)에서 가져와 고정했습니다.
- Template 없이 등록 Component와 Layout Primitive(Page, PageHeader, Section, Stack, Grid, FormGrid, Toolbar, FieldGroup, ContentCard)로 Content를 조합합니다. 메뉴와 Page는 AI가 정합니다.
- 일산병원 로고 타일(흰색 테두리) 모서리 반경은 8px입니다. 벤더 미러는 그대로 두고 `scripts/frame_patches.py` 한 곳에서 오프라인 빌더, Web Runtime, Design Guide 미리보기에 같은 패치를 적용합니다.
- 오프라인 빌더(`scripts/build_verified_artifact.py`)가 브라우저 검증을 거친 단일 `index.html`을 전달합니다.
- Web Runtime(`dist/nhimc-web.js`)으로 빌더를 실행할 수 없는 웹 AI도 Content와 `<script src>` 한 줄로 프롬프트 안에서 화면을 완성합니다(인터넷 필요).
- Design Guide(`guide/nhimc-design-guide.html`): 설치 가이드, 사용법, 프롬프트 만들기(`frame:` / `theme:` / `requirements:`), Frame·Component·Icon 미리보기. 복사가 막힌 환경에서는 프롬프트를 선택해 Ctrl+C로 복사하게 합니다.
- `bootstrap.md` 하나가 6개 환경(ChatGPT Web · Claude Web · Gemini Web · Codex · Claude Code · Gemini CLI)의 진입점입니다. 남아 있는 사본이 있어도 원격 `VERSION`과 비교해 최신일 때만 재준비를 생략합니다.
- 라이선스: 재배포·수정 금지(사용 허가만). 자세한 내용은 `LICENSE`를 참고하세요.
