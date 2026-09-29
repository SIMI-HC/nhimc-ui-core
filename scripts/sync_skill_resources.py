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
