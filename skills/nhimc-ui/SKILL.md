---
name: nhimc-ui
description: NHIMC 업무 화면을 정본 Template과 Frame으로 조합하고 검증된 오프라인 index.html 하나로 전달할 때 사용합니다.
---

# NHIMC UI Core 3.0

저장소 루트에서 작업합니다. 정본 기준은 `vendor/nhimc-design/upstream.json`의 고정 commit과 v3 registry입니다.

## 필수 순서

1. `registry/project.json`, `registry/templates.json`, `registry/frames.json`, `registry/themes.json`, `registry/components.json`, `registry/assets.json`을 읽습니다.
2. 업무 유형과 필요한 상태에 맞는 등록 Template을 먼저 선택합니다.
3. 호환 Frame을 확인하고 저작 원본의 `<nhimc-frame>` 또는 각 화면 패널에 `data-template`을 선언합니다.
4. 정본 Template의 역할 순서·중첩과 필수 `data-nhimc-component`를 보존한 채 업무 라벨, 데이터, 안전한 인라인 동작만 바꿉니다.
5. capable local host에서는 다음 명령으로 빌드·브라우저 검증·전달을 한 번에 수행합니다.

```powershell
python scripts/build_verified_artifact.py --input path/to/source.html --output path/to/index.html
```

6. 실제로 전달된 파일이 하나의 `index.html`인지 확인한 뒤에만 “다운로드할 수 있게 만들었다”고 말합니다.

Frame, Theme, Logo, Navigation, Sidebar, 상태 표시줄, Component CSS, Icon sprite, Noto Sans KR Font를 수작업으로 복제하지 마세요. 임의 `<style>`, 외부 URL, fetch/import, sidecar 파일, 자체 Frame은 금지합니다.

## 전달 경계: single HTML

최종 결과는 인터넷과 저장소 없이 `file://`로 열리는 정확히 하나의 `index.html`입니다. `app.js`, CSS, 이미지, Font, manifest, receipt, README 또는 asset 폴더를 함께 전달하면 안 됩니다. **MUST NOT DELIVER** an approximate or handcrafted Frame as a finished NHIMC artifact. 저작용 원본을 완성 파일로 첨부하면 안 됩니다.

호스트가 canonical builder와 정확한 브라우저 검증기를 실행할 수 없으면 capability를 `context-only`라고 보고합니다. 참고용 구조는 논의할 수 있지만 검증된 HTML을 만들었다고 주장하지 마세요.

ChatGPT Web은 검증된 Builder Bridge가 실제 연결되고 다운로드 시험까지 통과한 경우에만 `READY`입니다. 저장소 컨텍스트만 있으면 `WEB_BOOTSTRAP / context-only`입니다.

저장소 변경 완료 전 `python scripts/verify_all.py`, 공개 릴리스 판단 전 `python scripts/verify_release.py`를 실행합니다.
