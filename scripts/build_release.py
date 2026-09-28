import argparse
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.verify_release import verify_release


FIXED_TIMESTAMP = (2026, 9, 28, 0, 0, 0)
IGNORED_PARTS = {
    ".git", ".superpowers", ".worktrees", "__pycache__", "node_modules",
    ".pytest_cache", ".mypy_cache", "dist", "release",
}
UNSAFE_FIXTURE = ("tests", "fixtures", "public-safety")


def _publishable_files(root: Path, output: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file() or path.resolve() == output.resolve():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if relative.parts[: len(UNSAFE_FIXTURE)] == UNSAFE_FIXTURE:
            continue
        if path.suffix.lower() == ".zip":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def build_release(root: Path, output: Path) -> Path:
    root = root.resolve()
    output = output.resolve()
    if verify_release(run_full_verification=False):
        raise RuntimeError("release gate failed; archive was not written")

    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    prefix = f"nhimc-ui-core-{version}"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    if temporary.exists():
        temporary.unlink()
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for path in _publishable_files(root, output):
                relative = path.relative_to(root).as_posix()
                info = ZipInfo(f"{prefix}/{relative}", FIXED_TIMESTAMP)
                info.compress_type = ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
        temporary.replace(output)
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise
    print(f"release archive: {output}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic NHIMC UI Core archive")
    parser.add_argument("output", type=Path, nargs="?", default=Path("release/nhimc-ui-core-1.0.0.zip"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    build_release(args.root, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
