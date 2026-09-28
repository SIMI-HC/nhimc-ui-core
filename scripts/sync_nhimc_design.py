from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.nhimc_upstream import (
    EXPECTED_COUNTS,
    PINNED_COMMIT,
    VENDOR_PREFIX,
    enumerate_allowlisted_files,
    manifest_entry,
    require_clean_git_source,
    snapshot_counts,
)
from scripts.validate_public import scan_public_tree
from scripts.verify_nhimc_design_sync import verify_vendor_directory


def _write_manifest(path: Path, manifest: dict) -> None:
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _copy_allowlisted_bytes(source: Path, stage: Path, commit: str) -> dict:
    entries = []
    for relative, destination in enumerate_allowlisted_files(source):
        target = stage / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((source / relative).read_bytes())
        entries.append(manifest_entry(source, relative, destination))
    return {
        "schemaVersion": 1,
        "commit": commit,
        "sourceRoot": ".agents/skills/nhimc-worktool",
        "counts": snapshot_counts(source),
        "files": entries,
    }


def _format_findings(findings) -> str:
    return "; ".join(f"{item.rule} {item.path}: {item.message}" for item in findings)


def _replace_directory_atomically(stage: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = destination.parent / f".{destination.name}.backup"
    if backup.exists():
        raise ValueError(f"canonical snapshot backup already exists: {backup}")
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


def sync_snapshot(
    source: Path,
    root: Path,
    expected_commit: str | None = PINNED_COMMIT,
) -> dict:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    source, commit = require_clean_git_source(source.resolve(), expected_commit)
    stage_parent = Path(tempfile.mkdtemp(prefix="nhimc-vendor-", dir=root))
    stage = stage_parent / "nhimc-design"
    try:
        stage.mkdir()
        manifest = _copy_allowlisted_bytes(source, stage, commit)
        if manifest["counts"] != EXPECTED_COUNTS:
            raise ValueError(f"canonical resource counts do not match contract: {manifest['counts']}")
        _write_manifest(stage / "upstream.json", manifest)
        text_files = {
            item["destination"].removeprefix(VENDOR_PREFIX.as_posix() + "/")
            for item in manifest["files"]
            if item["role"] != "font"
        }
        findings = scan_public_tree(stage, include=text_files)
        findings.extend(verify_vendor_directory(stage, manifest))
        if findings:
            raise ValueError(_format_findings(sorted(set(findings))))
        _replace_directory_atomically(stage, root / VENDOR_PREFIX)
        return manifest
    finally:
        shutil.rmtree(stage_parent, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Vendor the canonical NHIMC Design snapshot")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expected-commit", default=PINNED_COMMIT)
    args = parser.parse_args()
    expected = None if args.expected_commit.lower() == "none" else args.expected_commit
    manifest = sync_snapshot(args.source, args.root, expected)
    print(f"canonical snapshot: {manifest['commit']} ({len(manifest['files'])} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
