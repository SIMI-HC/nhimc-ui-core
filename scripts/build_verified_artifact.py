from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.artifact_delivery import build_and_verify, deliver_verified_artifact


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build, browser-verify, and deliver one offline NHIMC index.html"
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix="nhimc-verified-") as folder:
            verified = build_and_verify(ROOT, args.input, Path(folder))
            delivered = deliver_verified_artifact(verified, args.output)
            summary = {
                "status": "PASS",
                "filename": delivered.name,
                "mimeType": "text/html",
                "sha256": verified.sha256,
                "bytes": verified.bytes,
            }
    except (OSError, UnicodeDecodeError, ValueError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
