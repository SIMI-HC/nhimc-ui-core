from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SHOWCASE_PATH = Path("vendor/nhimc-design/components/showcase.html")
REGISTRY_PATH = Path("vendor/nhimc-design/components/registry.md")
EXPECTED_COLUMNS = [
    "id", "purpose", "when_to_use", "when_not_to_use", "variants/sizes/states",
    "accessibility", "responsive", "related_items", "spec_source", "example",
    "added_date", "updated_date", "updated_at", "layer",
]


@dataclass(frozen=True)
class CanonicalComponent:
    id: str
    purpose: str
    when_to_use: str
    when_not_to_use: str
    variants_sizes_states: str
    accessibility: str
    responsive: str
    related_items: str
    spec_source: str
    example: str
    added_date: str
    updated_date: str
    updated_at: str
    layer: str


def _cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def parse_canonical_registry(path: Path) -> list[CanonicalComponent]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if _cells(line) == EXPECTED_COLUMNS),
        None,
    )
    if header_index is None:
        raise ValueError("canonical component registry table schema is missing")
    rows: list[CanonicalComponent] = []
    for line in lines[header_index + 2 :]:
        if not line.startswith("|"):
            break
        values = _cells(line)
        if len(values) != len(EXPECTED_COLUMNS):
            raise ValueError(f"canonical component row has {len(values)} columns")
        rows.append(CanonicalComponent(*values))
    ids = [row.id for row in rows]
    if len(rows) != 49:
        raise ValueError(f"expected 49 canonical components, found {len(rows)}")
    if len(ids) != len(set(ids)):
        raise ValueError("canonical component ids must be unique")
    return rows


def _extract_showcase(showcase: str) -> tuple[str, str, dict[str, str]]:
    styles = re.findall(r"<style>\s*(.*?)\s*</style>", showcase, re.DOTALL | re.IGNORECASE)
    scripts = re.findall(r"<script>\s*(.*?)\s*</script>", showcase, re.DOTALL | re.IGNORECASE)
    if len(styles) != 1 or len(scripts) != 1:
        raise ValueError("canonical showcase must contain exactly one style and script block")
    starts = list(re.finditer(r'<section class="specimen" data-component-case="([^"]+)">', showcase))
    if len(starts) != 49:
        raise ValueError(f"expected 49 canonical specimens, found {len(starts)}")
    specimens: dict[str, str] = {}
    script_start = showcase.index("<script>", starts[-1].start())
    for index, match in enumerate(starts):
        boundary = starts[index + 1].start() if index + 1 < len(starts) else script_start
        candidate = showcase[match.start() : boundary]
        section_end = candidate.rfind("</section>")
        if section_end < 0:
            raise ValueError(f"canonical specimen boundary is ambiguous: {match.group(1)}")
        block = candidate[: section_end + len("</section>")].strip()
        specimens[match.group(1)] = block
    return styles[0].strip() + "\n", scripts[0].strip() + "\n", specimens


def _split_contract(value: str) -> tuple[list[str], list[str]]:
    groups = [group.strip() for group in value.split(";") if group.strip()]
    variants = [item.strip() for item in groups[0].split("/") if item.strip()] if groups else []
    states_group = groups[-1] if len(groups) > 1 else (groups[0] if groups else "default")
    states = [item.strip() for item in states_group.split("/") if item.strip()]
    return variants or ["default"], states or ["default"]


def _write_if_changed(path: Path, data: bytes) -> None:
    if path.is_file() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def generate_components(root: Path = ROOT, *, output_root: Path | None = None) -> dict:
    root = root.resolve()
    output_root = (output_root or root).resolve()
    registry_rows = parse_canonical_registry(root / REGISTRY_PATH)
    showcase_path = root / SHOWCASE_PATH
    showcase_bytes = showcase_path.read_bytes()
    showcase = showcase_bytes.decode("utf-8")
    css, script, specimens = _extract_showcase(showcase)
    if [row.id for row in registry_rows] != list(specimens):
        raise ValueError("canonical registry and showcase specimen order differ")
    digest = hashlib.sha256(showcase_bytes).hexdigest()
    components = []
    for row in registry_rows:
        variants, states = _split_contract(row.variants_sizes_states)
        components.append(
            {
                "id": row.id,
                "layer": row.layer,
                "purpose": row.purpose,
                "whenToUse": row.when_to_use,
                "whenNotToUse": row.when_not_to_use,
                "variants": variants,
                "states": states,
                "accessibility": [row.accessibility],
                "responsive": row.responsive,
                "relatedItems": [item.strip() for item in row.related_items.split(",") if item.strip()],
                "canonicalSpec": row.spec_source,
                "canonicalSource": SHOWCASE_PATH.as_posix(),
                "canonicalDigest": digest,
                "implementation": "src/generated/components/components.css",
                "controller": "src/generated/components/components.js",
                "markup": specimens[row.id],
            }
        )
    document = {
        "schemaVersion": 2,
        "projectVersion": (root / "VERSION").read_text(encoding="utf-8").strip(),
        "components": components,
    }
    registry_data = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write_if_changed(output_root / "registry/components.json", registry_data)
    _write_if_changed(output_root / "src/generated/components/components.css", css.encode("utf-8"))
    _write_if_changed(output_root / "src/generated/components/components.js", script.encode("utf-8"))
    return {"count": len(components), "showcaseDigest": digest}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the canonical NHIMC component catalog")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = generate_components(args.root)
    print(f"{result['count']} canonical components generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
