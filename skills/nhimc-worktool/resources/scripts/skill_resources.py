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
                Finding(
                    "skill-resources.mismatch",
                    mirror_relative.as_posix(),
                    "Mirrored resource file does not match source",
                )
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
                    Finding(
                        "skill-resources.orphan",
                        relative.as_posix(),
                        "Mirrored resource file has no matching source file",
                    )
                )
    return sorted(findings, key=lambda item: (item.rule, item.path))
