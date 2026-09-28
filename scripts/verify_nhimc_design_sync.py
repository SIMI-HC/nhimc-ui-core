from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import Finding, sha256_file
from scripts.nhimc_upstream import EXPECTED_COUNTS, VENDOR_PREFIX, count_component_registry


def _load_manifest(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"canonical upstream manifest is unreadable: {path}") from error


def verify_vendor_directory(vendor: Path, manifest: dict) -> list[Finding]:
    findings: list[Finding] = []
    vendor = vendor.resolve()
    expected_files = {"upstream.json"}
    for item in manifest.get("files", []):
        destination = item.get("destination", "")
        prefix = VENDOR_PREFIX.as_posix() + "/"
        if not destination.startswith(prefix):
            findings.append(Finding("upstream.destination", destination, "Destination is outside canonical vendor root"))
            continue
        relative = destination[len(prefix) :]
        expected_files.add(relative)
        path = (vendor / relative).resolve()
        try:
            path.relative_to(vendor)
        except ValueError:
            findings.append(Finding("upstream.destination", destination, "Destination escapes canonical vendor root"))
            continue
        if not path.is_file():
            findings.append(Finding("upstream.missing-file", destination, "Canonical vendored file is missing"))
            continue
        if path.stat().st_size != item.get("bytes") or sha256_file(path) != item.get("sha256"):
            findings.append(Finding("upstream.digest", destination, "Canonical vendored file digest does not match manifest"))

    actual_files = {
        path.relative_to(vendor).as_posix()
        for path in vendor.rglob("*")
        if path.is_file()
    }
    for relative in sorted(actual_files - expected_files):
        findings.append(Finding("upstream.extra-file", relative, "Unlisted file exists in canonical vendor root"))

    counts = manifest.get("counts")
    if counts != EXPECTED_COUNTS:
        findings.append(Finding("upstream.counts", "upstream.json", "Canonical resource counts do not match contract"))
    registry = vendor / "components/registry.md"
    if registry.is_file() and count_component_registry(registry) != EXPECTED_COUNTS["components"]:
        findings.append(Finding("upstream.components", "components/registry.md", "Canonical component count does not match contract"))
    commit = manifest.get("commit", "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        findings.append(Finding("upstream.commit", "upstream.json", "Canonical source commit is invalid"))
    return sorted(set(findings))


def verify_snapshot(root: Path) -> list[Finding]:
    vendor = root.resolve() / VENDOR_PREFIX
    manifest_path = vendor / "upstream.json"
    if not manifest_path.is_file():
        return [Finding("upstream.missing-manifest", VENDOR_PREFIX.as_posix(), "Canonical upstream manifest is missing")]
    try:
        manifest = _load_manifest(manifest_path)
    except ValueError:
        return [Finding("upstream.invalid-manifest", manifest_path.as_posix(), "Canonical upstream manifest is unreadable")]
    return verify_vendor_directory(vendor, manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the vendored NHIMC Design snapshot")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()
    findings = verify_snapshot(args.root)
    if args.allow_missing and {item.rule for item in findings} == {"upstream.missing-manifest"}:
        print("canonical snapshot: pending")
        return 0
    for item in findings:
        print(f"ERROR {item.rule} {item.path}: {item.message}")
    if not findings:
        print("canonical snapshot: PASS")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
