# Bootstrap No-Clone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove `git clone`/`git pull` from the normal NHIMC UI Core readiness procedure, reorder it so official plugin/skill registration is always checked before any clone fallback, and make Codex's skill-only install self-contained by mirroring required resources into `skills/nhimc-worktool/resources/`.

**Architecture:** A new `scripts/skill_resources.py` module enumerates the six required resources (`registry/`, `scripts/`, `guide/`, `vendor/`, `VERSION`, and the always-present `skills/`) and compares repo-root copies byte-for-byte against a mirror under `skills/nhimc-worktool/resources/`. `scripts/sync_skill_resources.py` writes that mirror; `scripts/verify_skill_resources_sync.py` checks it (wired into `verify_all.py`/`verify_release.py`). `bootstrap.md` and `SKILL.md` are rewritten to a 9-step procedure: read `bootstrap.md` and `VERSION` via raw GitHub URLs (never clone), search for an existing install, verify its resources, ask about official registration before ever considering a clone, and only allow `git clone` — into a scratch/temp path, never the working folder — as a documented last resort when no official path exists and a real build is still needed.

**Tech Stack:** Python 3.12 (repo scripts/tests), `unittest`, Markdown procedure docs consumed by AI agents (not executable, verified via text assertions).

**Spec:** `docs/superpowers/specs/2026-09-29-bootstrap-no-clone-design.md`

## Global Constraints

- Normal readiness procedure (fresh prep, re-prep with existing install, update) must never run `git clone` or `git pull` against the user's working/project folder.
- `bootstrap.md` itself is read via `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md`, never by cloning.
- Remote version check reads only `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/VERSION`.
- Required resources for any install root: `registry/`, `scripts/`, `guide/`, `skills/`, `vendor/`, `VERSION`.
- An install missing any required resource must be reported as incomplete — never silently patched over with a clone.
- The one allowed exception (no official registration possible/declined, local shell, real verified artifact needed) clones into a scratch/temp location only, matching the existing `source.html` temp-location convention — never the user's project folder.
- `skills/nhimc-worktool/resources/` must stay a byte-identical mirror of the root `registry/`, `scripts/`, `guide/`, `vendor/`, `VERSION` (excluding `__pycache__`/`.pyc`), enforced by `verify_all.py` and `verify_release.py`.
- `python scripts/verify_all.py` and `python scripts/verify_release.py` must both pass before this work is considered done.

## Review Focus

- **Sync script picks up `__pycache__`/`.pyc` noise from `scripts/`** — a person re-running sync locally after running tests would get a mirror that differs machine-to-machine; the sync/verify must exclude these by name/suffix, not just "the files that happen to exist."
- **Mirror goes stale after someone edits `registry/*.json` or `scripts/*.py` without re-running sync** — `verify_skill_resources_sync.py` must fail loudly (not silently pass) when root and mirror diverge, and `verify_release.py` must gate on it.
- **Orphaned files left in `skills/nhimc-worktool/resources/`** after a source file is deleted at the root — verify must detect mirror-only files, not just missing ones, or a stale file could mislead a Codex skill-only install.
- **Doc-text tests silently pass on stale wording** — the existing `test_bootstrap_contract.py` assertions target the old 5-step structure; if not updated alongside the rewrite, they'd keep passing on leftover old phrases (e.g. old numbered-list text) while missing the new 9-step structure entirely, giving false confidence.
- **The scratch-only clone exception gets read as "clone is back to being fine"** — the rewritten docs must make the working-folder-vs-scratch distinction impossible to miss at the exact lines that still mention `git clone`, since a careless reader skimming for "git clone" and finding it unqualified would reintroduce the original bug.

---

## File Structure

- `scripts/skill_resources.py` — **create**. Defines `MIRROR_ROOT`, `SOURCE_DIRS`, `SOURCE_FILES`, exclusion rules, `iter_source_relative_paths(root)`, `compare(root)` returning findings (missing/mismatched/orphan).
- `scripts/sync_skill_resources.py` — **create**. CLI + `sync_resources(root)` that stages and atomically replaces `skills/nhimc-worktool/resources/`.
- `scripts/verify_skill_resources_sync.py` — **create**. CLI + `verify_sync(root)` wrapping `skill_resources.compare`.
- `scripts/verify_all.py` — **modify**: add the sync check to both the canonical and non-canonical check lists.
- `scripts/verify_release.py` — **modify**: gate on the same check.
- `skills/nhimc-worktool/resources/` — **create** (generated tree; committed as data, not hand-written).
- `bootstrap.md` — **modify**: rewrite entry point + "준비 절차" + "준비 완료 후: Design Guide 열기" + the builder-location paragraph in "웹에서 URL 없는 완성 HTML".
- `skills/nhimc-worktool/SKILL.md` — **modify**: rewrite "준비 절차 요약" to match the 9-step procedure and reference the resource mirror.
- `docs/platforms/chatgpt-codex.md` — **modify**: note the skill-only install path and the resource mirror.
- `tests/python/test_bootstrap_contract.py` — **modify**: replace stale 5-step assertions with 9-step assertions; add incomplete-install and raw-read assertions.
- `tests/python/test_skill_resources_sync.py` — **create**: unit tests for `skill_resources.compare` and `sync_skill_resources.sync_resources` against synthetic temp roots.

---

### Task 1: `skill_resources` module — enumerate and compare

**Files:**
- Create: `scripts/skill_resources.py`
- Test: `tests/python/test_skill_resources_sync.py`

**Interfaces:**
- Produces: `MIRROR_ROOT: Path` (`Path("skills/nhimc-worktool/resources")`), `SOURCE_DIRS: tuple[Path, ...]` (`Path("registry")`, `Path("scripts")`, `Path("guide")`, `Path("vendor")`), `SOURCE_FILES: tuple[Path, ...]` (`Path("VERSION")`), `iter_source_relative_paths(root: Path) -> list[Path]`, `compare(root: Path) -> list[Finding]` (uses `scripts.common.Finding`, `sha256_file`).

- [ ] **Step 1: Write the failing tests**

```python
# tests/python/test_skill_resources_sync.py
from pathlib import Path
import tempfile
import unittest

from scripts.skill_resources import MIRROR_ROOT, compare, iter_source_relative_paths


class IterSourceRelativePathsTests(unittest.TestCase):
    def setUp(self):
        self._temporaries: list[tempfile.TemporaryDirectory] = []

    def tearDown(self):
        for temporary in self._temporaries:
            temporary.cleanup()

    def _root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self._temporaries.append(temporary)
        return Path(temporary.name)

    def _write(self, root: Path, relative: str, data: bytes = b"x") -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def test_lists_files_under_each_source_dir_and_version(self):
        root = self._root()
        self._write(root, "registry/frames.json")
        self._write(root, "scripts/build_release.py")
        self._write(root, "guide/nhimc-design-guide.html")
        self._write(root, "vendor/nhimc-design/upstream.json")
        self._write(root, "VERSION")
        result = {path.as_posix() for path in iter_source_relative_paths(root)}
        self.assertEqual(
            result,
            {
                "registry/frames.json",
                "scripts/build_release.py",
                "guide/nhimc-design-guide.html",
                "vendor/nhimc-design/upstream.json",
                "VERSION",
            },
        )

    def test_excludes_pycache_and_pyc(self):
        root = self._root()
        self._write(root, "scripts/build_release.py")
        self._write(root, "scripts/__pycache__/build_release.cpython-312.pyc")
        self._write(root, "scripts/stale.pyc")
        result = {path.as_posix() for path in iter_source_relative_paths(root)}
        self.assertEqual(result, {"scripts/build_release.py"})


class CompareTests(unittest.TestCase):
    def setUp(self):
        self._temporaries: list[tempfile.TemporaryDirectory] = []

    def tearDown(self):
        for temporary in self._temporaries:
            temporary.cleanup()

    def _root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self._temporaries.append(temporary)
        return Path(temporary.name)

    def _write(self, root: Path, relative: str, data: bytes = b"x") -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def test_reports_missing_mirror_file(self):
        root = self._root()
        self._write(root, "VERSION", b"1.3.2\n")
        findings = compare(root)
        self.assertTrue(any(item.rule == "skill-resources.missing" for item in findings))

    def test_reports_mismatched_mirror_file(self):
        root = self._root()
        self._write(root, "VERSION", b"1.3.2\n")
        self._write(root, (MIRROR_ROOT / "VERSION").as_posix(), b"1.3.1\n")
        findings = compare(root)
        self.assertTrue(any(item.rule == "skill-resources.mismatch" for item in findings))

    def test_reports_orphan_mirror_file(self):
        root = self._root()
        self._write(root, "VERSION", b"1.3.2\n")
        self._write(root, (MIRROR_ROOT / "VERSION").as_posix(), b"1.3.2\n")
        self._write(root, (MIRROR_ROOT / "registry/deleted.json").as_posix(), b"{}")
        findings = compare(root)
        self.assertTrue(any(item.rule == "skill-resources.orphan" for item in findings))

    def test_clean_mirror_reports_nothing(self):
        root = self._root()
        self._write(root, "VERSION", b"1.3.2\n")
        self._write(root, (MIRROR_ROOT / "VERSION").as_posix(), b"1.3.2\n")
        self.assertEqual(compare(root), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m unittest tests.python.test_skill_resources_sync -v`
Expected: FAIL/ERROR — `scripts.skill_resources` does not exist yet.

- [ ] **Step 3: Implement `scripts/skill_resources.py`**

```python
from __future__ import annotations

from pathlib import Path

from scripts.common import Finding, sha256_file

MIRROR_ROOT = Path("skills/nhimc-worktool/resources")
SOURCE_DIRS = (Path("registry"), Path("scripts"), Path("guide"), Path("vendor"))
SOURCE_FILES = (Path("VERSION"),)
EXCLUDED_DIR_NAMES = {"__pycache__"}
EXCLUDED_SUFFIXES = {".pyc"}


def _is_excluded(relative: Path) -> bool:
    if relative.suffix in EXCLUDED_SUFFIXES:
        return True
    return any(part in EXCLUDED_DIR_NAMES for part in relative.parts)


def iter_source_relative_paths(root: Path) -> list[Path]:
    root = root.resolve()
    results: list[Path] = []
    for source_dir in SOURCE_DIRS:
        directory = root / source_dir
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if _is_excluded(relative):
                continue
            results.append(relative)
    for source_file in SOURCE_FILES:
        path = root / source_file
        if path.is_file():
            results.append(source_file)
    return sorted(results, key=lambda item: item.as_posix())


def compare(root: Path) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    expected_mirror_paths: set[Path] = set()
    for relative in iter_source_relative_paths(root):
        mirror_relative = MIRROR_ROOT / relative
        expected_mirror_paths.add(mirror_relative)
        mirror_path = root / mirror_relative
        if not mirror_path.is_file():
            findings.append(
                Finding("skill-resources.missing", mirror_relative.as_posix(), "Mirrored resource file is missing")
            )
            continue
        source_path = root / relative
        if sha256_file(source_path) != sha256_file(mirror_path):
            findings.append(
                Finding("skill-resources.mismatch", mirror_relative.as_posix(), "Mirrored resource file does not match source")
            )

    mirror_root = root / MIRROR_ROOT
    if mirror_root.is_dir():
        for path in mirror_root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if _is_excluded(relative):
                continue
            if relative not in expected_mirror_paths:
                findings.append(
                    Finding("skill-resources.orphan", relative.as_posix(), "Mirrored resource file has no matching source file")
                )
    return sorted(findings, key=lambda item: (item.rule, item.path))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m unittest tests.python.test_skill_resources_sync -v`
Expected: PASS (all `IterSourceRelativePathsTests` and `CompareTests` cases green).

- [ ] **Step 5: Commit**

```bash
git add scripts/skill_resources.py tests/python/test_skill_resources_sync.py
git commit -m "feat: add skill_resources module to compare root resources against the skill mirror"
```

---

### Task 2: sync and verify CLIs

**Files:**
- Create: `scripts/sync_skill_resources.py`
- Create: `scripts/verify_skill_resources_sync.py`
- Modify: `tests/python/test_skill_resources_sync.py`

**Interfaces:**
- Consumes: `scripts.skill_resources.{MIRROR_ROOT, SOURCE_DIRS, SOURCE_FILES, iter_source_relative_paths, compare}`, `scripts.common.Finding`.
- Produces: `sync_skill_resources.sync_resources(root: Path) -> None` (writes the mirror), `verify_skill_resources_sync.verify_sync(root: Path) -> list[Finding]` (thin wrapper over `compare`), both with `main() -> int` CLI entry points printing `PASS`/`ERROR ...` lines matching the style of `verify_nhimc_design_sync.py`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/python/test_skill_resources_sync.py`:

```python
from scripts.sync_skill_resources import sync_resources
from scripts.verify_skill_resources_sync import verify_sync


class SyncResourcesTests(unittest.TestCase):
    def setUp(self):
        self._temporaries: list[tempfile.TemporaryDirectory] = []

    def tearDown(self):
        for temporary in self._temporaries:
            temporary.cleanup()

    def _root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self._temporaries.append(temporary)
        return Path(temporary.name)

    def _write(self, root: Path, relative: str, data: bytes = b"x") -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def test_sync_then_verify_reports_nothing(self):
        root = self._root()
        self._write(root, "registry/frames.json", b"{}")
        self._write(root, "scripts/build_release.py", b"# script")
        self._write(root, "guide/nhimc-design-guide.html", b"<html></html>")
        self._write(root, "vendor/nhimc-design/upstream.json", b"{}")
        self._write(root, "VERSION", b"1.3.2\n")
        sync_resources(root)
        self.assertEqual(verify_sync(root), [])

    def test_sync_removes_stale_mirror_files(self):
        root = self._root()
        self._write(root, "VERSION", b"1.3.2\n")
        sync_resources(root)
        self._write(root, (Path("skills/nhimc-worktool/resources/registry/deleted.json")).as_posix(), b"{}")
        sync_resources(root)
        self.assertEqual(verify_sync(root), [])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m unittest tests.python.test_skill_resources_sync -v`
Expected: FAIL/ERROR — `scripts.sync_skill_resources` / `scripts.verify_skill_resources_sync` do not exist yet.

- [ ] **Step 3: Implement `scripts/sync_skill_resources.py`**

```python
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.skill_resources import MIRROR_ROOT, iter_source_relative_paths


def sync_resources(root: Path) -> None:
    root = root.resolve()
    destination = root / MIRROR_ROOT
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage_parent = Path(tempfile.mkdtemp(prefix="nhimc-skill-resources-", dir=root))
    stage = stage_parent / "resources"
    try:
        stage.mkdir()
        for relative in iter_source_relative_paths(root):
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((root / relative).read_bytes())
        backup = destination.parent / f".{destination.name}.backup"
        if backup.exists():
            shutil.rmtree(backup)
        moved_old = False
        try:
            if destination.exists():
                os.replace(destination, backup)
                moved_old = True
            os.replace(stage, destination)
        except BaseException:
            if moved_old and backup.exists() and not destination.exists():
                os.replace(backup, destination)
            raise
        else:
            if backup.exists():
                shutil.rmtree(backup)
    finally:
        shutil.rmtree(stage_parent, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror NHIMC UI Core resources into the skill package")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    sync_resources(args.root)
    print(f"skill resources: synced to {MIRROR_ROOT.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Implement `scripts/verify_skill_resources_sync.py`**

```python
from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import Finding
from scripts.skill_resources import compare


def verify_sync(root: Path) -> list[Finding]:
    return compare(root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the NHIMC UI Core skill resource mirror")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings = verify_sync(args.root)
    for item in findings:
        print(f"ERROR {item.rule} {item.path}: {item.message}")
    if not findings:
        print("skill resources sync: PASS")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m unittest tests.python.test_skill_resources_sync -v`
Expected: PASS (all tests including the two new `SyncResourcesTests` cases).

- [ ] **Step 6: Commit**

```bash
git add scripts/sync_skill_resources.py scripts/verify_skill_resources_sync.py tests/python/test_skill_resources_sync.py
git commit -m "feat: add sync/verify CLIs for the skill resource mirror"
```

---

### Task 3: Wire the sync check into `verify_all.py` and `verify_release.py`

**Files:**
- Modify: `scripts/verify_all.py`
- Modify: `scripts/verify_release.py`

**Interfaces:**
- Consumes: `scripts.verify_skill_resources_sync` (invoked as a subprocess, matching the existing `("canonical snapshot", [...])` pattern in `verify_all.py`), `scripts.skill_resources.compare` (imported directly in `verify_release.py`, matching how it already imports `validate_contracts`/`validate_design`/`scan_public_tree`).

- [ ] **Step 1: Add the check to `verify_all.py`**

In `scripts/verify_all.py`, add a new entry to the always-run `checks` list (not gated by `include_canonical`, since the mirror must stay in sync regardless of canonical-vendor checks). Append it **after** `"browser"`, not before — the existing `if include_canonical: checks[5:5] = [...]` below inserts canonical checks at positional index 5 (immediately before whatever is currently last, `"browser"`). Inserting the new check before `"browser"` would silently shift that slice index and reorder the canonical checks relative to `"browser"`. Appending after `"browser"` leaves index 5 untouched:

```python
    checks = [
        ("python tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests/python", "-v"]),
        ("node tests", [npm, "run", "test:node"]),
        ("contracts", [sys.executable, "scripts/validate_contracts.py"]),
        ("design rules", [sys.executable, "scripts/validate_design.py"]),
        ("public tree", [sys.executable, "scripts/validate_public.py"]),
        ("browser", [sys.executable, "scripts/run_browser_tests.py"]),
        ("skill resources sync", [sys.executable, "scripts/verify_skill_resources_sync.py"]),
    ]
```

The `if include_canonical: checks[5:5] = [...]` block below is unchanged — it still inserts before index 5 (`"browser"`), now followed by the new `"skill resources sync"` entry at the end regardless of `include_canonical`.

- [ ] **Step 2: Add the gate to `verify_release.py`**

In `scripts/verify_release.py`, import `compare` and add a blocking category alongside the existing contract/design/public checks:

```python
from scripts.skill_resources import compare as compare_skill_resources
```

and inside `verify_release`, after the `scan_public_tree` check:

```python
    if compare_skill_resources(root):
        categories.append("skill resources sync")
```

- [ ] **Step 3: Verify by running the full suites**

Run: `python scripts/verify_all.py`
Expected: at this point the new "skill resources sync" check FAILS (mirror doesn't exist yet) — this is expected; Task 4 fixes it. Confirm the failure is specifically the new check, not an unrelated regression, then proceed.

- [ ] **Step 4: Commit**

```bash
git add scripts/verify_all.py scripts/verify_release.py
git commit -m "feat: gate verify_all/verify_release on the skill resource mirror"
```

---

### Task 4: Generate and commit the real resource mirror

**Files:**
- Create: `skills/nhimc-worktool/resources/` (generated tree — registry/, scripts/, guide/, vendor/, VERSION)

- [ ] **Step 1: Run the sync script against the real repo**

Run: `python scripts/sync_skill_resources.py`
Expected output: `skill resources: synced to skills/nhimc-worktool/resources`

- [ ] **Step 2: Verify the mirror**

Run: `python scripts/verify_skill_resources_sync.py`
Expected: `skill resources sync: PASS`

- [ ] **Step 3: Sanity-check the generated tree**

Run: `find skills/nhimc-worktool/resources -maxdepth 1` (or the PowerShell equivalent `Get-ChildItem skills/nhimc-worktool/resources`)
Expected: `registry`, `scripts`, `guide`, `vendor`, `VERSION` all present; no `__pycache__` directories under `resources/scripts`.

- [ ] **Step 4: Commit**

```bash
git add skills/nhimc-worktool/resources
git commit -m "chore: generate the skill resource mirror for Codex skill-only installs"
```

---

### Task 5: Rewrite `bootstrap.md` — raw entry, 9-step procedure, scratch-only clone

**Files:**
- Modify: `bootstrap.md`

- [ ] **Step 1: Replace the intro (current lines 1–20) to require raw reads from the first action**

Replace:

```markdown
# NHIMC UI Core 시작

이 파일은 모든 AI 환경의 단일 진입점입니다. 저장소 루트의 `VERSION`, `registry/project.json`, `skills/nhimc-worktool/SKILL.md`를 읽고 그 계약을 따르세요.

이 저장소는 NhimcDesign(NHIMC Worktool)을 GitHub로 옮긴 프로젝트입니다. 플러그인·스킬 이름은 기존과 같은 `nhimc-worktool`이므로 이미 설치된 스킬이 있으면 이 저장소 버전으로 갱신하고, 없으면 새로 준비합니다.
```

with:

```markdown
# NHIMC UI Core 시작

이 파일은 모든 AI 환경의 단일 진입점입니다. 이 문서를 읽는 것 자체는 **항상 raw 파일 읽기**(`https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md`)로 합니다. `bootstrap.md`를 읽기 위한 목적만으로 `git clone`을 하지 않습니다. 이후 절차는 아래 "준비 절차"를 그대로 따릅니다.

이 저장소는 NhimcDesign(NHIMC Worktool)을 GitHub로 옮긴 프로젝트입니다. 플러그인·스킬 이름은 기존과 같은 `nhimc-worktool`이므로 이미 설치된 스킬이 있으면 이 저장소 버전으로 갱신하고, 없으면 새로 준비합니다.
```

- [ ] **Step 2: Replace the "준비 절차" section (current lines 22–40) with the 9-step procedure**

Replace the entire block from `## 준비 절차 (항상 이 순서로, 사본이 남아 있어도 생략하지 않습니다)` through the end of the old numbered list (ending at `... Design Guide(열었음 / 링크 전달 / 생략: 이미 최신)를 함께 씁니다.`) with:

```markdown
## 준비 절차 (항상 이 순서로, 사본이 남아 있어도 생략하지 않습니다)

이전 대화나 샌드박스에 저장소 사본·스킬·**플러그인 설치본**이 남아 있어도 **아래 1~9를 건너뛰지 않습니다.** 여기서 “사본”은 저장소 클론뿐 아니라 마켓플레이스로 설치한 플러그인 설치본, 스킬 업로드본도 포함합니다. 사본이 있다는 이유만으로 준비를 생략하지 않습니다.

**필수 리소스**: 어떤 설치 경로든 `<루트>`로 쓰려면 `registry/`, `scripts/`, `guide/`, `skills/`, `vendor/`, `VERSION` 6가지가 모두 있어야 합니다. 전체 저장소를 설치하는 플러그인 경로는 이 6가지가 저장소 루트에 그대로 있습니다. Codex의 “스킬만 업로드” 같은 경량 경로는 `skills/nhimc-worktool/`만 설치될 수 있으므로, 그 경우 나머지 5가지는 `skills/nhimc-worktool/resources/`(레포에 미리 미러링되어 있음) 아래에서 찾습니다.

1. **raw `bootstrap.md` 읽기.** `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md`를 읽습니다(클론 아님). 지금 읽고 있는 이 문서가 그 결과입니다.
2. **raw `VERSION` 확인.** `https://raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/VERSION`**만** 읽어(클론하지 않습니다) 앞으로 비교할 원격 최신 버전을 기억합니다. 읽을 수 없으면 `확인 못함`이며 이후 어떤 설치본도 “최신”이라고 말하지 않습니다.
3. **설치된 `nhimc-worktool` 검색.** 이 환경의 플러그인 목록·스킬 목록·확장 목록에서 `nhimc-worktool`을 찾습니다. Claude Code는 `~/.claude/plugins/cache/<마켓플레이스>/nhimc-worktool/<버전>/`이며, 다른 환경은 그 환경의 플러그인/스킬 목록에서 설치 경로를 확인합니다.
4. **설치본이 있으면 버전과 필수 리소스를 검증.** 찾은 설치 경로를 `<루트>` 후보로 놓고 위 “필수 리소스” 6가지가 모두 있는지 확인합니다(직접 있거나, `skills/nhimc-worktool/resources/` 아래에 미러로 있으면 됨).
   - 모두 있고 로컬 버전이 2단계의 원격과 같거나 더 새로우면: 이 설치본을 `<루트>`로 확정하고 8단계로 갑니다.
   - 모두 있고 원격이 더 새로우면: 5단계로 가되 “업데이트할지” 질문합니다.
   - **하나라도 빠지면**: 이 설치본은 `<루트>` 후보에서 제외합니다. **클론으로 대체하지 않습니다.** 이 환경에 다른 등록 경로(예: 스킬 업로드 말고 정식 플러그인)가 더 있으면 3단계로 돌아가 확인하고, 없으면 5단계에서 “완전한 경로로 다시 등록할지”를 묻습니다.
5. **미등록이거나 불완전하면 공식 등록 가능 여부를 확인하고 사용자에게 묻습니다.** 이 환경이 지원하는 공식 등록 경로(플러그인 마켓플레이스를 우선하고, 그다음 스킬 업로드, 확장 순)가 있으면 **등록(또는 완전한 경로로 재등록)할지 사용자에게 먼저 묻습니다.** 자동 설치나 비공식 우회(클론 포함)를 하지 않습니다. 등록 경로가 없거나 사용자가 거절하면 `WEB_BOOTSTRAP`으로 확정하고 8단계로 건너뜁니다(이 경우도 작업 폴더에 클론하지 않습니다. 로컬 셸이 있고 사용자가 실제 검증된 산출물을 원하면 “웹에서 URL 없는 완성 HTML을 다운로드 파일로 주기”의 임시 경로 clone 예외를 씁니다).
6. **승인 시 공식 경로로 설치·업데이트합니다.** Claude Code는 `claude plugin marketplace add SIMI-HC/nhimc-ui-core` 다음 `claude plugin install nhimc-worktool@nhimc-worktool-marketplace`(업데이트는 `claude plugin marketplace update nhimc-worktool-marketplace` 다음 `claude plugin update nhimc-worktool@nhimc-worktool-marketplace`)입니다. 다른 환경은 그 환경의 공식 명령을 씁니다. 어떤 경우에도 `git clone`/`git pull`로 대신하지 않습니다.
7. **새 설치 경로를 `<루트>`로 설정하고 필수 리소스를 재검증합니다.** 6단계에서 설치·업데이트된 경로에 6가지 리소스가 모두 있는지 다시 확인합니다. 빠졌으면 “설치 패키지가 불완전하다”고 정확히 보고하고 `WEB_BOOTSTRAP`으로 폴백합니다(작업 폴더에 클론하지 않습니다).
8. **Design Guide를 표출합니다.** 처음 준비했거나 2단계에서 “원격이 더 새로움”으로 판정했을 때만 아래 “준비 완료 후: Design Guide 열기”대로 엽니다. 파일은 `<루트>/guide/nhimc-design-guide.html`(또는 스킬 전용 설치는 `<루트>/resources/guide/nhimc-design-guide.html`)입니다. 이미 최신이면 다시 열지 않고 링크만 한 줄로 알려 줍니다.
9. **결과를 보고합니다.** `platform`, `projectVersion`, `defaultFrame`, `defaultTheme`, `installationMode`에 더해 `최신 확인 결과`(갱신함/이미 최신/확인 못함), `스킬·플러그인 상태`(등록됨/업데이트함/업데이트 안 함/미등록·미지원/불완전), `Design Guide`(열었음/링크 전달/생략: 이미 최신)를 함께 씁니다.
```

- [ ] **Step 3: Update "준비 완료 후: Design Guide 열기" to reference step 8 instead of "준비 절차 4단계"**

Replace the first sentence of that section:

```markdown
준비 절차 4단계에서 `<루트>/guide/nhimc-design-guide.html`을 사용자에게 엽니다(플러그인이 설치돼 있으면 클론하지 않고 그 설치 경로의 파일을 엽니다. 처음 준비하거나 버전이 갱신됐을 때는 생략하지 않습니다). 설치 가이드, 사용법, 프롬프트 만들기, Frame·Component·Icon 미리보기가 들어 있는 단일 오프라인 HTML입니다.
```

with:

```markdown
준비 절차 8단계에서 `<루트>/guide/nhimc-design-guide.html`을 사용자에게 엽니다(설치본이 있으면 클론하지 않고 그 설치 경로 — 필요하면 `resources/guide/` 아래 — 의 파일을 엽니다. 처음 준비하거나 버전이 갱신됐을 때는 생략하지 않습니다). 설치 가이드, 사용법, 프롬프트 만들기, Frame·Component·Icon 미리보기가 들어 있는 단일 오프라인 HTML입니다.
```

- [ ] **Step 4: Make the scratch-only clone exception explicit in "웹에서 URL 없는 완성 HTML을 다운로드 파일로 주기"**

Replace:

```markdown
1. 빌더 위치 `<루트>`를 정합니다. 스킬·플러그인이 설치돼 있으면 **클론하지 않고** 플러그인 설치 경로의 `scripts/`를 그대로 실행합니다(결과물만 작업 폴더에 씁니다). **설치돼 있지 않을 때만** `git clone https://github.com/SIMI-HC/nhimc-ui-core.git`(이미 있으면 위 “항상 먼저 확인”에 따라 갱신)로 받습니다.
```

with:

```markdown
1. 빌더 위치 `<루트>`를 정합니다. 설치본이 있고 필수 리소스가 모두 있으면 **클론하지 않고** 그 설치 경로의 `scripts/`(또는 `resources/scripts/`)를 그대로 실행합니다(결과물만 작업 폴더에 씁니다). 설치본이 없거나 불완전하고, 공식 등록도 불가능하거나 사용자가 거절했는데 로컬 셸에서 실제 검증된 산출물이 필요할 때만 **임시/scratch 경로에** `git clone https://github.com/SIMI-HC/nhimc-ui-core.git`로 받습니다. `source.html`과 같은 임시 위치(세션 scratchpad 또는 OS 임시 폴더)를 쓰고, **사용자 작업 폴더에는 절대 clone하지 않습니다.**
```

- [ ] **Step 5: Diff-review the whole file**

Run: `git diff bootstrap.md`
Expected: only the four blocks above changed; PRESENTATION Frame, BLOG Frame, 프롬프트 힌트, 상태 판정, 기본 산출물 계약, 메뉴/Page, Web Runtime sections are untouched.

- [ ] **Step 6: Commit**

```bash
git add bootstrap.md
git commit -m "docs: rewrite bootstrap.md readiness procedure to remove working-folder clone"
```

---

### Task 6: Rewrite `SKILL.md` — matching procedure summary

**Files:**
- Modify: `skills/nhimc-worktool/SKILL.md`

- [ ] **Step 1: Replace "준비 절차 요약" section**

Replace:

```markdown
## 준비 절차 요약 (사본이 남아 있어도 생략 금지 — 플러그인 설치본도 “사본”)

`bootstrap.md`의 “준비 절차”를 순서대로 따릅니다. 먼저 `<루트>`를 정합니다: **플러그인이 설치돼 있으면 플러그인 설치 경로**(Claude Code: `~/.claude/plugins/cache/<마켓플레이스>/nhimc-worktool/<버전>/`)이고, 이때 저장소를 작업 폴더에 **클론하지 않습니다**(registry·scripts·guide·SKILL은 설치 경로에서 읽고 결과물만 작업 폴더에 씁니다). 설치돼 있지 **않을 때만** 클론합니다. ① 원격 `VERSION`만 읽어 설치본(또는 클론 사본)과 비교 ② 클론 사본이 필요할 때만(미설치) `git clone`/`git pull` ③ 스킬·플러그인이 미등록이면 **등록할지 먼저 묻고**, 등록돼 있고 새 버전이 있으면 **업데이트할지 반드시 묻고** 승인 시 공식 경로로 갱신(Claude Code: `claude plugin marketplace update` + `claude plugin update`; 클론으로 대신하지 않음) ④ 처음 준비했거나 버전이 갱신됐으면 `<루트>/guide/nhimc-design-guide.html`로 Design Guide를 반드시 표출(열거나 클릭 링크) ⑤ 최신 확인 결과·스킬/플러그인 상태·Design Guide 상태를 보고합니다.
```

with:

```markdown
## 준비 절차 요약 (사본이 남아 있어도 생략 금지 — 플러그인 설치본·스킬 업로드본도 “사본”)

`bootstrap.md`의 “준비 절차”(9단계)를 순서대로 따릅니다: ① raw `bootstrap.md` 읽기 ② raw `VERSION` 확인(클론 아님) ③ 설치된 `nhimc-worktool` 검색 ④ 설치본이 있으면 버전과 필수 리소스(`registry/`, `scripts/`, `guide/`, `skills/`, `vendor/`, `VERSION`) 검증 — 리소스가 빠지면 클론으로 대체하지 않고 그 설치본을 후보에서 제외 ⑤ 미등록이거나 불완전하면 공식 등록 가능 여부를 확인하고 **클론을 고려하기 전에 먼저** 사용자에게 등록 여부를 묻기 ⑥ 승인 시 공식 경로로 설치·업데이트(Claude Code: `claude plugin marketplace add/update` + `claude plugin install/update`; 클론으로 대신하지 않음) ⑦ 새 설치 경로를 `<루트>`로 재확정하고 리소스 재검증 — 여전히 불완전하면 “설치 패키지가 불완전하다”고 보고하고 `WEB_BOOTSTRAP`으로 폴백(작업 폴더 클론 없음) ⑧ 처음 준비했거나 버전이 갱신됐으면 `<루트>/guide/nhimc-design-guide.html`(스킬 전용 설치는 `<루트>/resources/guide/`)로 Design Guide를 반드시 표출 ⑨ 최신 확인 결과·스킬/플러그인 상태·Design Guide 상태를 보고합니다.

**정상 절차에서는 `git clone`/`git pull`을 실행하지 않습니다.** 유일한 예외는 공식 등록이 불가능하거나 거절됐고 로컬 셸에서 실제 검증된 `index.html`이 필요한 경우이며, 이때도 사용자 작업 폴더가 아니라 `source.html`과 같은 **임시/scratch 경로**에만 clone합니다(`bootstrap.md`의 “웹에서 URL 없는 완성 HTML을 다운로드 파일로 주기” 참고).
```

- [ ] **Step 2: Diff-review**

Run: `git diff skills/nhimc-worktool/SKILL.md`
Expected: only the "준비 절차 요약" section changed.

- [ ] **Step 3: Commit**

```bash
git add skills/nhimc-worktool/SKILL.md
git commit -m "docs: sync SKILL.md readiness summary with the 9-step bootstrap procedure"
```

---

### Task 7: Update `docs/platforms/chatgpt-codex.md`

**Files:**
- Modify: `docs/platforms/chatgpt-codex.md`

- [ ] **Step 1: Add a paragraph about the skill-only install and the resource mirror**

Replace:

```markdown
ChatGPT Web은 검증된 Builder Bridge가 연결되고 실제 `index.html` 다운로드까지 시험됐을 때만 `READY`입니다. Codex도 체크아웃 또는 플러그인을 로드하고 registry, Layout Primitive, `scripts/build_verified_artifact.py` 경로를 확인한 뒤에만 `READY`입니다. 저장소가 대화 컨텍스트에만 있으면 `WEB_BOOTSTRAP / context-only`입니다.
```

with:

```markdown
ChatGPT Web은 검증된 Builder Bridge가 연결되고 실제 `index.html` 다운로드까지 시험됐을 때만 `READY`입니다. Codex도 설치본을 로드하고 registry, Layout Primitive, `scripts/build_verified_artifact.py` 경로를 확인한 뒤에만 `READY`입니다. 저장소가 대화 컨텍스트에만 있으면 `WEB_BOOTSTRAP / context-only`입니다.

Codex가 “스킬 업로드”처럼 `skills/nhimc-worktool/`만 설치하는 경량 경로를 제공하는 경우, `registry/`·`scripts/`·`guide/`·`vendor/`·`VERSION`은 그 폴더 바로 아래가 아니라 `skills/nhimc-worktool/resources/`(저장소가 릴리스마다 미러링해 둔 사본)에서 찾습니다. 이 리소스가 없으면 `bootstrap.md`의 준비 절차에 따라 “설치 패키지가 불완전하다”고 보고하고, 저장소를 작업 폴더에 clone하지 않습니다.
```

- [ ] **Step 2: Diff-review**

Run: `git diff docs/platforms/chatgpt-codex.md`

- [ ] **Step 3: Commit**

```bash
git add docs/platforms/chatgpt-codex.md
git commit -m "docs: note the Codex skill-only install path and resource mirror"
```

---

### Task 8: Update `test_bootstrap_contract.py` for the 9-step procedure

**Files:**
- Modify: `tests/python/test_bootstrap_contract.py`

**Interfaces:**
- Consumes: `BOOTSTRAP` and `SKILL` module-level strings already defined in the file (full text of `bootstrap.md` / `SKILL.md`).

- [ ] **Step 1: Write the failing test additions**

Replace the `PluginInstallDoesNotCloneTests` class body with an expanded version that checks the new structure (old assertions that still hold are kept; assertions tied to the old 5-step numbering are replaced):

```python
class PluginInstallDoesNotCloneTests(unittest.TestCase):
    def test_clone_and_pull_are_scoped_to_scratch_or_the_no_install_case(self):
        lines = [line for line in BOOTSTRAP.splitlines() if "git clone" in line or "git pull" in line]
        self.assertGreaterEqual(len(lines), 1)
        for line in lines:
            self.assertRegex(
                line,
                r"임시|scratch|않(?:으면|을 때만)|하지 않(?:습니다|고)",
                line[:120],
            )

    def test_first_step_reads_bootstrap_via_raw_url_not_clone(self):
        self.assertIn("raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/main/bootstrap.md", BOOTSTRAP)
        intro = BOOTSTRAP.split("## 준비 절차", 1)[0]
        self.assertIn("git clone을 하지 않습니다", intro)

    def test_required_resources_are_listed(self):
        for text in (BOOTSTRAP, SKILL):
            for resource in ("registry/", "scripts/", "guide/", "skills/", "vendor/", "VERSION"):
                self.assertIn(resource, text)

    def test_nine_step_procedure_is_present_in_order(self):
        markers = [
            "raw `bootstrap.md` 읽기",
            "raw `VERSION` 확인",
            "설치된 `nhimc-worktool` 검색",
            "필수 리소스를 검증",
            "공식 등록 가능 여부를 확인",
            "공식 경로로 설치·업데이트",
            "필수 리소스를 재검증",
            "Design Guide를 표출",
            "결과를 보고",
        ]
        positions = [BOOTSTRAP.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_incomplete_install_is_reported_not_cloned_over(self):
        self.assertIn("설치 패키지가 불완전하다", BOOTSTRAP)
        around = BOOTSTRAP[BOOTSTRAP.index("설치 패키지가 불완전하다") : BOOTSTRAP.index("설치 패키지가 불완전하다") + 200]
        self.assertNotIn("git clone", around)

    def test_plugin_install_path_is_the_root_and_a_copy_includes_the_plugin_install(self):
        for text in (BOOTSTRAP, SKILL):
            self.assertIn("~/.claude/plugins/cache/<마켓플레이스>/nhimc-worktool/<버전>/", text)
        self.assertIn("플러그인 설치본", BOOTSTRAP)
        self.assertIn("아래 1~9를 건너뛰지 않습니다", BOOTSTRAP)
        self.assertIn("사본이 남아 있어도 생략 금지", SKILL)

    def test_update_goes_through_the_official_path_after_asking(self):
        for text in (BOOTSTRAP, SKILL):
            self.assertIn("claude plugin marketplace update", text)
            self.assertIn("claude plugin update", text)
        self.assertIn("<루트>/guide/nhimc-design-guide.html", BOOTSTRAP)
```

- [ ] **Step 2: Run the tests to verify they fail before Task 5/6 land**

Run: `python -m unittest tests.python.test_bootstrap_contract -v`
Expected: at this point (if run before Task 5/6) FAIL on the new marker/ordering assertions. This task is sequenced after Task 5 and Task 6 in execution, so in practice run this after those docs are rewritten — if executing tasks out of order, expect failures here until Task 5/6 land.

- [ ] **Step 3: Run the tests to verify they pass**

Run: `python -m unittest tests.python.test_bootstrap_contract -v`
Expected: PASS — all classes including `SingleDeliverableTests` (unchanged) green.

- [ ] **Step 4: Commit**

```bash
git add tests/python/test_bootstrap_contract.py
git commit -m "test: assert the 9-step bootstrap procedure and incomplete-install reporting"
```

---

### Task 9: Full verification run

**Files:** none (verification only)

- [ ] **Step 1: Run the full verification gate**

Run: `python scripts/verify_all.py`
Expected: `VERIFY PASS: <n> checks` — including the new "skill resources sync" check.

- [ ] **Step 2: Run the release gate**

Run: `python scripts/verify_release.py`
Expected: `RELEASE PASS: public artifact requirements satisfied`.

- [ ] **Step 3: If either fails, fix forward**

Do not skip or weaken a check to make it pass. If `verify_release.py` fails on `skill resources sync`, re-run `python scripts/sync_skill_resources.py` and re-verify — the mirror must have drifted because a doc edit in Task 5/6 touched a tracked resource path (unlikely, since `bootstrap.md`/`SKILL.md` are not in `SOURCE_DIRS`) or because `scripts/verify_all.py`/`scripts/verify_release.py` edits in Task 3 weren't re-synced. Investigate the actual `ERROR skill-resources.*` line rather than guessing.

- [ ] **Step 4: Report results to the user**

Summarize: both commands' pass/fail status, the exact output lines, and confirm no task left `git clone`/`git pull` reachable from the normal readiness procedure (grep check: `grep -n "git clone\|git pull" bootstrap.md skills/nhimc-worktool/SKILL.md` and confirm every remaining line is the scratch-only exception).
