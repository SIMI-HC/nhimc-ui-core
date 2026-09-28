from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess


PINNED_COMMIT = "08c45402eece8a7c55afc60385e8671c9f13081a"
VENDOR_PREFIX = Path("vendor/nhimc-design")
ALLOWLIST_DIRECTORIES = (
    Path("assets/layouts"),
    Path("assets/icons"),
    Path("components"),
    Path("patterns"),
    Path("rules"),
    Path("tokens"),
    Path("templates"),
    Path("docs/design-docs/assets/logo"),
    Path("docs/design-docs/assets/font"),
)
ALLOWLIST_FILES = (
    Path("assets/components/showcase.html"),
    Path("docs/design-docs/assets/fonts.css"),
)
EXPECTED_COUNTS = {"layouts": 7, "components": 49, "logos": 9, "fonts": 6}


def _git(source: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=source,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode:
        raise ValueError("source must be inside a Git worktree")
    return completed.stdout.strip()


def require_clean_git_source(source: Path, expected_commit: str | None) -> tuple[Path, str]:
    source = source.resolve()
    if not source.is_dir():
        raise ValueError("source must be inside a Git worktree")
    worktree = Path(_git(source, "rev-parse", "--show-toplevel")).resolve()
    try:
        source.relative_to(worktree)
    except ValueError as error:
        raise ValueError("source must be inside a Git worktree") from error
    commit = _git(source, "rev-parse", "HEAD")
    if expected_commit is not None and commit != expected_commit:
        raise ValueError(f"source commit does not match expected commit: {commit}")
    pathspecs = [item.as_posix() for item in (*ALLOWLIST_DIRECTORIES, *ALLOWLIST_FILES)]
    status = _git(
        source,
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        *pathspecs,
    )
    if status:
        raise ValueError("modified canonical source files are not allowed")
    return source, commit


def _destination_for(relative: Path) -> Path:
    mappings = (
        (Path("assets/layouts"), Path("layouts")),
        (Path("assets/icons"), Path("icons")),
        (Path("assets/components"), Path("components")),
        (Path("components"), Path("components")),
        (Path("patterns"), Path("patterns")),
        (Path("rules"), Path("rules")),
        (Path("tokens"), Path("tokens")),
        (Path("templates"), Path("templates")),
        (Path("docs/design-docs/assets/logo"), Path("branding")),
        (Path("docs/design-docs/assets/font"), Path("fonts")),
    )
    if relative == Path("docs/design-docs/assets/fonts.css"):
        return Path("fonts/fonts.css")
    for source_prefix, destination_prefix in mappings:
        try:
            suffix = relative.relative_to(source_prefix)
        except ValueError:
            continue
        return destination_prefix / suffix
    raise ValueError(f"source path is not allowlisted: {relative.as_posix()}")


def _role(relative: Path) -> str:
    value = relative.as_posix()
    if value.startswith("assets/layouts/"):
        return "layout"
    if value.startswith("assets/icons/"):
        return "icon"
    if value.startswith("docs/design-docs/assets/logo/"):
        return "logo"
    if value.endswith(".woff2"):
        return "font"
    if value.endswith("fonts.css"):
        return "font-styles"
    if value.startswith(("assets/components/", "components/")):
        return "component"
    return "contract"


def _media_type(path: Path) -> str:
    return {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "text/javascript",
        ".json": "application/json",
        ".md": "text/markdown",
        ".svg": "image/svg+xml",
        ".woff2": "font/woff2",
        ".yaml": "application/yaml",
        ".yml": "application/yaml",
    }.get(path.suffix.lower(), "text/plain")


def enumerate_allowlisted_files(source: Path) -> list[tuple[Path, Path]]:
    source = source.resolve()
    candidates: set[Path] = set()
    for relative in ALLOWLIST_DIRECTORIES:
        directory = (source / relative).resolve()
        if not directory.is_dir():
            raise ValueError(f"canonical directory is missing: {relative.as_posix()}")
        try:
            directory.relative_to(source)
        except ValueError as error:
            raise ValueError(f"canonical directory escapes source: {relative.as_posix()}") from error
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise ValueError(f"canonical symlink is not allowed: {path.relative_to(source).as_posix()}")
            if path.is_file():
                candidates.add(path.resolve())
    for relative in ALLOWLIST_FILES:
        path = (source / relative).resolve()
        if not path.is_file():
            raise ValueError(f"canonical file is missing: {relative.as_posix()}")
        candidates.add(path)

    results: list[tuple[Path, Path]] = []
    destinations: set[Path] = set()
    for path in sorted(candidates, key=lambda item: item.relative_to(source).as_posix()):
        relative = path.relative_to(source)
        destination = _destination_for(relative)
        if destination in destinations:
            raise ValueError(f"canonical destination collision: {destination.as_posix()}")
        destinations.add(destination)
        results.append((relative, destination))
    return results


def count_component_registry(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_table = False
    count = 0
    for line in lines:
        if line.startswith("| id | purpose |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|---"):
            continue
        if not line.startswith("|"):
            if count:
                break
            continue
        count += 1
    return count


def snapshot_counts(source: Path) -> dict[str, int]:
    return {
        "layouts": len(list((source / "assets/layouts").glob("*.html"))),
        "components": count_component_registry(source / "components/registry.md"),
        "logos": len(list((source / "docs/design-docs/assets/logo").glob("*.svg"))),
        "fonts": len(list((source / "docs/design-docs/assets/font").glob("*.woff2"))),
    }


def manifest_entry(source: Path, relative: Path, destination: Path) -> dict:
    data = (source / relative).read_bytes()
    return {
        "bytes": len(data),
        "destination": (VENDOR_PREFIX / destination).as_posix(),
        "mediaType": _media_type(relative),
        "role": _role(relative),
        "sha256": sha256(data).hexdigest(),
        "source": relative.as_posix(),
    }
