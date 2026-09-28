# NHIMC UI Core 시작

이 파일은 모든 AI 환경의 단일 진입점입니다. 저장소 루트의 `VERSION`, `registry/project.json`, `skills/nhimc-ui/SKILL.md`를 읽고 그 계약을 따르세요.

사용자는 처음 한 번 다음처럼 요청합니다.

```text
https://github.com/SIMI-HC/nhimc-ui-core.git

bootstrap.md만 읽고 NHIMC UI Core를 준비해줘.
```

그다음에는 자연어 요구만 받습니다.

```text
이송업무 관리 화면 만들어줘.
```

별도의 설치 명령을 사용자에게 묻지 마세요.

## 상태 판정

- `READY`: 이 호스트에서 `scripts/build_verified_artifact.py`를 호출하고 검증된 `index.html` 다운로드까지 시험했습니다.
- `WEB_BOOTSTRAP`: 저장소와 Skill만 읽을 수 있는 `context-only` 상태입니다.
- `UNSUPPORTED`: 저장소 또는 Skill을 읽을 수 없습니다.

특히 ChatGPT Web은 callable Builder Bridge의 `verified-builder-bridge-connected-and-download-tested` capability가 확인될 때만 `READY`입니다. 저장소 URL, 매니페스트 또는 Library 항목만 존재하면 `WEB_BOOTSTRAP`입니다.

## 기본 산출물 계약

1. 업무 유형에 맞는 등록 Template을 먼저 선택합니다.
2. `<nhimc-frame data-frame="left" data-template="list-default">`처럼 Template ID를 명시합니다.
3. 정본 `main[data-nhimc-role="content"][data-nhimc-template-root]` 역할·컴포넌트 구조 안에서 업무 값과 안전한 업무 동작만 작성합니다.
4. capable host에서는 `scripts/build_verified_artifact.py`로 최종화합니다.
5. 브라우저 영수증과 정확히 일치하는 오프라인 `index.html` 하나만 다운로드로 전달합니다.

별도 `app.js`, CSS, 이미지, Font, receipt, README, asset 폴더는 최종 전달물이 아닙니다. 저작용 원본을 완성 파일로 첨부하면 안 됩니다.

빌더나 정확한 브라우저 검증을 실행할 수 없으면 `context-only`라고 명확히 알립니다. 수작업 HTML을 정본 완성품이라고 주장하거나 사용자에게 Python 실행을 떠넘기지 마세요.

유지보수 진단 시에만 다음 명령을 사용합니다.

```powershell
python scripts/build_verified_artifact.py --input path/to/source.html --output path/to/index.html
```
