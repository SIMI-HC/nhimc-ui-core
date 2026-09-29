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
