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
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request

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


REPO = "SIMI-HC/nhimc-ui-core"


def cdn_runtime_urls(version: str) -> list[str]:
    """The pinned tag and the major range ("@2") that bootstrap.md and README hand to web AIs."""
    return [f"https://cdn.jsdelivr.net/gh/{REPO}@{ref}/dist/nhimc-web.js" for ref in (f"v{version}", version.split(".")[0])]


# The two requests below read public files and the body is compared byte for byte with dist/, and nothing secret
# is sent, so TLS interception on a corporate network (Python rejects its CA) must not stop the check.
_CONTEXT = ssl.create_default_context()
_CONTEXT.check_hostname = False
_CONTEXT.verify_mode = ssl.CERT_NONE


def _get(url: str, timeout: float) -> bytes:
    return urllib.request.urlopen(url, timeout=timeout, context=_CONTEXT).read()


def refresh_cdn(root: Path, version: str, *, attempts: int = 8, wait: float = 15.0) -> list[tuple[str, str]]:
    """jsDelivr answers 404 for a brand-new tag (and keeps the miss) and serves a range such as @2 from a cache that
    lasts hours: ask it to refetch, then wait until it serves dist/nhimc-web.js byte for byte.
    Returns (url, "stale" | "unreachable") for every URL that never matched."""
    expected = (root / "dist/nhimc-web.js").read_bytes()
    problems = []
    for url in cdn_runtime_urls(version):
        reason = "unreachable"
        for attempt in range(attempts):
            try:
                _get(url.replace("https://cdn.jsdelivr.net/", "https://purge.jsdelivr.net/"), 30)
            except OSError:
                pass
            try:
                body = _get(url, 60)
            except urllib.error.HTTPError:
                reason, body = "stale", b""
            except OSError:
                body = b""
            else:
                reason = "stale"
            if body == expected:
                break
            time.sleep(wait)
        else:
            problems.append((url, reason))
    return problems


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
    version = tag[1:]
    problems = refresh_cdn(root, version)
    for url, reason in problems:
        what = "is not serving the current runtime yet" if reason == "stale" else "could not be checked (network)"
        print(f"WARNING: jsDelivr {what}: {url} (check or purge it again later)")
    if not problems:
        print("jsDelivr serves the current runtime")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
