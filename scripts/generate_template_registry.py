from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.canonical_templates import load_template_contracts


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path("registry/templates.json")


def render_template_registry(root: Path) -> str:
    root = root.resolve()
    contracts = load_template_contracts(root)
    upstream = json.loads(
        (root / "vendor/nhimc-design/upstream.json").read_text(encoding="utf-8")
    )
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    payload = {
        "schemaVersion": 1,
        "coreVersion": version,
        "upstreamCommit": upstream["commit"],
        "templates": [
            contracts[template_id].as_registry_entry()
            for template_id in sorted(contracts)
        ],
    }
    return json.dumps(
        payload, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"


def registry_is_current(root: Path) -> bool:
    path = root.resolve() / REGISTRY_PATH
    try:
        return path.read_text(encoding="utf-8") == render_template_registry(root)
    except OSError:
        return False


def update_template_registry(root: Path) -> bool:
    root = root.resolve()
    path = root / REGISTRY_PATH
    rendered = render_template_registry(root)
    try:
        if path.read_text(encoding="utf-8") == rendered:
            return False
    except OSError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(rendered)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the canonical Template registry")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if registry_is_current(args.root):
            print("canonical Template registry: PASS")
            return 0
        print("canonical Template registry: OUTDATED", file=sys.stderr)
        return 1
    changed = update_template_registry(args.root)
    print(f"canonical Template registry: {'updated' if changed else 'unchanged'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
