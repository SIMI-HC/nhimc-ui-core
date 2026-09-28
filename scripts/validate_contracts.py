import argparse
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Iterable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import Finding, load_json, sha256_file


DEFAULT_REQUIRED = [
    "registry/project.json",
    "registry/frames.json",
    "registry/themes.json",
    "registry/components.json",
    "registry/assets.json",
]


def _safe_relative_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def _iter_paths(value, key: str = "") -> Iterable[str]:
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            if child_key in {"path", "file", "implementation"} and isinstance(
                child_value, str
            ):
                yield child_value
            else:
                yield from _iter_paths(child_value, child_key)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_paths(child, key)


def _duplicate_ids(document: dict) -> list[str]:
    duplicates = []
    for value in document.values():
        if not isinstance(value, list):
            continue
        ids = [item.get("id") for item in value if isinstance(item, dict)]
        seen = set()
        for item_id in ids:
            if item_id and item_id in seen and item_id not in duplicates:
                duplicates.append(item_id)
            seen.add(item_id)
    return duplicates


def check_integrity(root: Path, entries: list[dict]) -> list[Finding]:
    findings = []
    for entry in entries:
        relative = entry.get("path", "")
        expected = entry.get("sha256", "")
        if not _safe_relative_path(relative):
            findings.append(
                Finding("contract.unsafe-path", relative, "Path must remain in repository")
            )
            continue
        target = root / relative
        if not target.is_file():
            findings.append(
                Finding("contract.missing-file", relative, "Protected file is missing")
            )
        elif expected and sha256_file(target) != expected:
            findings.append(
                Finding(
                    "contract.integrity-mismatch",
                    relative,
                    "Protected file digest does not match registry",
                )
            )
        elif not expected:
            findings.append(
                Finding(
                    "contract.empty-digest",
                    relative,
                    "Protected file digest has not been recorded",
                    blocking=False,
                )
            )
    return findings


def validate_contracts(
    root: Path, required_override: list[str] | None = None
) -> list[Finding]:
    root = root.resolve()
    required = required_override or DEFAULT_REQUIRED
    findings: list[Finding] = []
    documents: dict[str, dict] = {}

    version_path = root / "VERSION"
    canonical_version = ""
    if version_path.is_file():
        canonical_version = version_path.read_text(encoding="utf-8").strip()
    else:
        findings.append(
            Finding("contract.missing-file", "VERSION", "Canonical version is missing")
        )

    for relative in required:
        if not _safe_relative_path(relative):
            findings.append(
                Finding("contract.unsafe-path", relative, "Registry path escapes repository")
            )
            continue
        path = root / relative
        if not path.is_file():
            findings.append(
                Finding("contract.missing-file", relative, "Required registry is missing")
            )
            continue
        try:
            documents[relative] = load_json(path)
        except (json.JSONDecodeError, OSError) as error:
            findings.append(
                Finding("contract.invalid-json", relative, f"Cannot load JSON: {error}")
            )

    for relative, document in documents.items():
        document_version = document.get("projectVersion")
        if canonical_version and document_version != canonical_version:
            findings.append(
                Finding(
                    "contract.version-mismatch",
                    relative,
                    f"Expected {canonical_version}, found {document_version!r}",
                )
            )
        for duplicate in _duplicate_ids(document):
            findings.append(
                Finding(
                    "contract.duplicate-id",
                    relative,
                    f"Duplicate registry id: {duplicate}",
                )
            )
        for referenced in _iter_paths(document):
            if not _safe_relative_path(referenced):
                findings.append(
                    Finding(
                        "contract.unsafe-path",
                        f"{relative}:{referenced}",
                        "Referenced path escapes repository",
                    )
                )
            elif not (root / referenced).is_file():
                findings.append(
                    Finding(
                        "contract.missing-file",
                        referenced,
                        f"Referenced by {relative}",
                    )
                )

    project = documents.get("registry/project.json")
    frames = documents.get("registry/frames.json", {}).get("frames", [])
    themes = documents.get("registry/themes.json", {}).get("themes", [])
    if project:
        frame_ids = {item.get("id") for item in frames}
        theme_ids = {item.get("id") for item in themes}
        if project.get("defaultFrame") not in frame_ids:
            findings.append(
                Finding(
                    "contract.unknown-default",
                    "registry/project.json",
                    "defaultFrame is not registered",
                )
            )
        if project.get("defaultTheme") not in theme_ids:
            findings.append(
                Finding(
                    "contract.unknown-default",
                    "registry/project.json",
                    "defaultTheme is not registered",
                )
            )

    integrity_entries = []
    for frame in frames:
        integrity_entries.extend(frame.get("protectedFiles", []))
    integrity_entries.extend(
        entry
        for entry in documents.get("registry/assets.json", {}).get("assets", [])
        if "sha256" in entry
    )
    findings.extend(check_integrity(root, integrity_entries))
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate NHIMC UI Core contracts")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings = validate_contracts(args.root)
    for item in findings:
        level = "ERROR" if item.blocking else "WARNING"
        print(f"{level} {item.rule} {item.path}: {item.message}")
    return 1 if any(item.blocking for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
