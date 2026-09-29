"""Keep the release tag in sync with VERSION.

Every prior release (v1.0.0 .. v1.3.2) has a git tag pointing at the commit that bumped
VERSION to that value; bootstrap.md and the Design Guide hand out version-tagged
githack/jsdelivr URLs that 404 until that tag exists on the remote. v1.4.0 and v1.4.1
shipped without one. Run this after committing a version bump, before calling the release
done: `python scripts/release_tag.py`.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, text=True, check=False
    )
    if completed.returncode:
        raise ValueError(f"git {' '.join(arguments)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def expected_tag(root: Path) -> str:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    return f"v{version}"


def tag_exists(root: Path, tag: str) -> bool:
    return bool(_git(root, "tag", "-l", tag))


def create_and_push_tag(root: Path, tag: str, *, commit: str = "HEAD", remote: str = "origin") -> None:
    root = root.resolve()
    target = _git(root, "rev-parse", commit)
    if tag_exists(root, tag):
        current = _git(root, "rev-list", "-n", "1", tag)
        if current != target:
            raise ValueError(f"tag {tag} already points at a different commit: {current} != {target}")
    else:
        _git(root, "tag", tag, target)
    _git(root, "push", remote, tag)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and push the git tag matching VERSION")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--commit", default="HEAD")
    args = parser.parse_args()
    root = args.root.resolve()
    tag = expected_tag(root)
    create_and_push_tag(root, tag, commit=args.commit, remote=args.remote)
    print(f"release tag: {tag} -> {args.remote}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
