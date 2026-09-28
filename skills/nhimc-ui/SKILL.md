---
name: nhimc-ui
description: NHIMC 업무 화면을 정본 Frame, Theme, Component, Logo, Icon, Font로 만들고 오프라인 단일 HTML로 검증할 때 사용합니다.
---

# NHIMC UI

저장소 루트에서 작업합니다. 이 Skill의 정본 기준은 `vendor/nhimc-design/upstream.json`에 고정된 canonical commit과 v2 registry입니다.

## 먼저 읽을 계약

1. `registry/project.json`에서 버전, 기본 Frame·Theme, 산출물 계약을 확인합니다.
2. `registry/frames.json`, `registry/themes.json`, `registry/components.json`, `registry/assets.json`을 읽습니다.
3. `references/contracts.md`에서 저작용 HTML 구조와 실패 시 처리 원칙을 확인합니다.
4. 업무 요구에 맞는 등록 컴포넌트의 `markup`을 재사용합니다.

AI가 작성하는 것은 업무 콘텐츠와 업무 동작뿐입니다. 헤더, 병원 로고, 내비게이션, 반응형 Frame, 상태 표시줄, 공통 Theme, Component CSS, Icon sprite, Noto Sans KR Font를 수작업으로 복제하거나 비슷하게 다시 만들지 마세요. 이 항목은 Core의 canonical 스냅샷과 어댑터가 소유합니다.

## 기본 결과: single HTML

별도 형식이 명시되지 않은 업무 화면의 최종 결과는 정확히 하나의 `index.html`입니다. 인터넷, HTTP 서버, 저장소 또는 옆 파일 없이 `file://`에서 열려야 합니다.

1. 저작용 HTML에 `<nhimc-frame data-frame="left" ...>` 하나를 두고 그 안에는 업무 콘텐츠만 작성합니다.
2. 내비게이션은 `script[type="application/json"][data-nhimc-menu]` 하나로 선언합니다. 각 항목은 안전한 `id`, 같은 값의 `#href`, 정본 sprite의 명시적 `icon`을 가져야 합니다.
3. 필요한 업무 JavaScript만 인라인 `script[type="module"][data-nhimc-business]`에 작성합니다. import, fetch, 외부 파일 참조는 금지합니다.
4. 다음 빌더를 실행해 정본 Frame, Theme, Component, Logo, Icon, Font와 provenance를 HTML 안에 포함합니다.

```powershell
python scripts/build_single_html.py --input path/to/index.html --output path/to/index.html
```

5. 사용자가 받을 바로 그 파일을 검증합니다.

```powershell
python scripts/run_browser_tests.py --standalone-file path/to/index.html
```

`standalone file: PASS` 전에는 완성됐다고 말하지 마세요. 빌더는 이미 최종화된 파일을 거부하므로 수정할 때는 저작용 원본에서 다시 빌드합니다.

최종 전달물에 `app.js`, CSS, 이미지, 폰트, manifest, README 또는 asset 폴더가 생기면 계약 위반입니다. **MUST NOT DELIVER** an approximate or handcrafted Frame as a finished NHIMC artifact.

## 도구를 실행할 수 없는 호스트

호스트가 canonical builder 또는 정확한 브라우저 검증기를 실행할 수 없으면 capability를 `context-only`라고 보고합니다. 참고용 업무 콘텐츠를 제안할 수는 있지만 검증된 NHIMC 결과라고 주장하거나 HTML을 최종 전달하면 안 됩니다. 사용자에게 Python 명령을 대신 실행하라고 떠넘기지 말고, 해당 호스트의 한계를 분명히 알립니다.

## 확장과 검증

등록된 49개 컴포넌트와 7개 Frame을 먼저 조합합니다. 정말 없는 기능은 `docs/decisions/new-component.md`에 결정 근거를 남기고 registry와 테스트를 함께 갱신합니다. 병렬 Frame이나 자체 Sidebar를 만들지 마세요.

저장소 변경 완료 전 `python scripts/verify_all.py`, 공개 릴리스 판단 전 `python scripts/verify_release.py`를 실행합니다. `READY`는 해당 플랫폼 로더가 실제로 설치되고 검증됐을 때만 보고합니다.
