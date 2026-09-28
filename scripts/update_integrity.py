import argparse
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import load_json, sha256_file


def _refresh_entries(root: Path, entries: list[dict]) -> None:
    for entry in entries:
        path = root / entry["path"]
        if not path.is_file():
            raise FileNotFoundError(entry["path"])
        entry["sha256"] = sha256_file(path)


def _write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def refresh_integrity(
    root: Path, frame_id: str, expected_frame_version: str
) -> None:
    root = root.resolve()
    frame_path = root / "registry/frames.json"
    asset_path = root / "registry/assets.json"
    frames = load_json(frame_path)
    assets = load_json(asset_path)
    frame = next(
        (item for item in frames["frames"] if item["id"] == frame_id), None
    )
    if frame is None:
        raise ValueError(f"unknown frame: {frame_id}")
    if frame["version"] != expected_frame_version:
        raise ValueError("frame version confirmation does not match registry")
    _refresh_entries(root, frame["protectedFiles"])
    _refresh_entries(root, assets["assets"])
    _write_json(frame_path, frames)
    _write_json(asset_path, assets)


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh protected file digests")
    parser.add_argument("--frame", required=True)
    parser.add_argument("--frame-version", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    refresh_integrity(args.root, args.frame, args.frame_version)
    print(f"integrity refreshed: {args.frame}@{args.frame_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
