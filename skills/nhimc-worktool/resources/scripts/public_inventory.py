from pathlib import Path


IGNORED_PARTS = {
    ".git", ".superpowers", ".worktrees", "__pycache__", "node_modules",
    ".pytest_cache", ".mypy_cache", "dist", "release",
}
UNSAFE_FIXTURE = ("tests", "fixtures", "public-safety")
KNOWN_BINARY_SUFFIXES = {".woff2"}


def iter_publishable_files(
    root: Path,
    *,
    excluded: set[Path] | None = None,
    skip_unsafe_fixtures: bool = True,
) -> list[Path]:
    root = root.resolve()
    excluded_resolved = {item.resolve() for item in excluded or set()}
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.resolve() in excluded_resolved:
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if skip_unsafe_fixtures and relative.parts[: len(UNSAFE_FIXTURE)] == UNSAFE_FIXTURE:
            continue
        if path.suffix.lower() == ".zip":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())
