import argparse
import ipaddress
import json
import re
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import Finding
from scripts.common import load_json
from scripts.public_inventory import KNOWN_BINARY_SUFFIXES, iter_publishable_files
from scripts.skill_resources import MIRROR_ROOT


MIRROR_PREFIX = MIRROR_ROOT.as_posix() + "/"


def _canonical_relative(relative: str) -> str:
    """The skill resource mirror is a byte-identical copy of an already-cleared root file.

    Scanning it under its own path would re-flag content (devtools loopback strings, registered
    fonts) that was already reviewed and allowlisted at its source path.
    """
    if relative.startswith(MIRROR_PREFIX):
        return relative[len(MIRROR_PREFIX):]
    return relative


IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
URL_CREDENTIALS = re.compile(r"https?://[^\s/:@]+:[^\s/@]+@", re.IGNORECASE)
INTERNAL_HOST = re.compile(
    r"https?://(?:[^\s/]+\.)?(?:localhost|intranet|[^\s/.]+\.(?:local|internal|corp))(?:[/:\s]|$)",
    re.IGNORECASE,
)
BARE_INTERNAL_HOST = re.compile(
    r"(?i)\b(?:localhost|intranet|(?:[a-z0-9-]+\.)+(?:internal|corp|local))(?=[\s/:\"'\\]|$)"
)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|access[_-]?token|auth[_-]?token|client[_-]?secret|password)\b"
    r"\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{16,}"
)
TOKEN = re.compile(r"\b(?:sk|ghp|glpat|xox[baprs])-[A-Za-z0-9_-]{20,}\b")
EMAIL = re.compile(
    r"(?<![A-Z0-9._%+-])[A-Z0-9._%+-]{1,64}"
    r"@([A-Z0-9.-]{1,253}\.[A-Z]{2,63})\b",
    re.IGNORECASE,
)
KOREAN_PHONE = re.compile(r"(?<!\d)01[016789][ -]?\d{3,4}[ -]?\d{4}(?!\d)")
RESIDENT_NUMBER = re.compile(r"(?<!\d)\d{6}[ -][1-4]\d{6}(?!\d)")
ALLOWED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net"}
PRIVATE_KEY = re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")
LOCAL_NETWORK_ALLOWLIST = {
    "README.md",
    "scripts/run_browser_tests.py",
    "scripts/verify_standalone_browser.mjs",
    "scripts/verify_canonical_parity.mjs",
    "scripts/verify_content_layout.mjs",
    "scripts/probe_console.mjs",
    "scripts/verify_presentation_safe_area.mjs",
    "scripts/verify_blog_scroll_owner.mjs",
    "scripts/verify_frame_render.mjs",
    "scripts/verify_outside_click.mjs",
    "scripts/verify_modal_stability.mjs",
    "docs/superpowers/plans/2026-09-28-nhimc-ui-core-implementation.md",
    "docs/superpowers/plans/2026-09-28-nhimc-web-builder-bridge.md",
}


def _line_findings(relative: str, number: int, line: str, *, canonical: str | None = None) -> list[Finding]:
    location = f"{relative}:{number}"
    allowlist_key = canonical if canonical is not None else relative
    findings: list[Finding] = []

    for match in IPV4.finditer(line):
        try:
            address = ipaddress.ip_address(match.group(0))
        except ValueError:
            continue
        if (
            address.is_private or address.is_loopback or address.is_link_local
        ) and allowlist_key not in LOCAL_NETWORK_ALLOWLIST:
            findings.append(
                Finding("public.private-network", location, "Private or local network address detected")
            )
            break

    if URL_CREDENTIALS.search(line):
        findings.append(
            Finding("public.url-credentials", location, "URL contains embedded credentials")
        )
    if INTERNAL_HOST.search(line) and allowlist_key not in LOCAL_NETWORK_ALLOWLIST:
        findings.append(
            Finding("public.internal-url", location, "Internal host marker detected")
        )
    if BARE_INTERNAL_HOST.search(line) and allowlist_key not in LOCAL_NETWORK_ALLOWLIST:
        findings.append(
            Finding("public.internal-host", location, "Internal host marker detected")
        )
    if SECRET_ASSIGNMENT.search(line) or TOKEN.search(line):
        findings.append(
            Finding("public.possible-secret", location, "High-confidence credential pattern detected")
        )
    if PRIVATE_KEY.search(line):
        findings.append(
            Finding("public.private-key", location, "Private key material detected")
        )
    if KOREAN_PHONE.search(line) or RESIDENT_NUMBER.search(line):
        findings.append(
            Finding("public.personal-data", location, "Personal identifier pattern detected")
        )
    for match in EMAIL.finditer(line):
        if match.group(1).lower() not in ALLOWED_EMAIL_DOMAINS:
            findings.append(
                Finding("public.personal-data", location, "Non-example email address detected")
            )
            break
    return findings


def scan_public_tree(root: Path, include: set[str] | None = None) -> list[Finding]:
    root = root.resolve()
    whole_tree = include is None
    findings: list[Finding] = []
    registered_binary_assets = set()
    asset_registry = root / "registry/assets.json"
    if asset_registry.is_file():
        registered_binary_assets = {
            item.get("path", "")
            for item in load_json(asset_registry).get("assets", [])
            if Path(item.get("path", "")).suffix.lower() in KNOWN_BINARY_SUFFIXES
        }
    paths = iter_publishable_files(root, skip_unsafe_fixtures=whole_tree)
    for path in paths:
        relative_path = path.relative_to(root)
        relative = relative_path.as_posix()
        if include is not None and path.name not in include and relative not in include:
            continue
        canonical = _canonical_relative(relative)
        if path.is_symlink():
            findings.append(
                Finding("public.symlink", relative, "Symbolic links are not publishable")
            )
            continue
        if path.suffix.lower() in KNOWN_BINARY_SUFFIXES:
            if relative in registered_binary_assets or canonical in registered_binary_assets:
                continue
            findings.append(
                Finding("public.unknown-binary", relative, "Unregistered binary asset detected")
            )
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in data:
            findings.append(
                Finding("public.unknown-binary", relative, "Unregistered binary file detected")
            )
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            findings.append(
                Finding("public.unknown-binary", relative, "Unreadable non-text file detected")
            )
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            findings.extend(_line_findings(relative, number, line, canonical=canonical))
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan the publishable tree for private data")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    findings = scan_public_tree(args.root)
    if args.format == "json":
        print(json.dumps([item.__dict__ for item in findings], indent=2, sort_keys=True))
    else:
        for item in findings:
            level = "ERROR" if item.blocking else "WARNING"
            print(f"{level} {item.rule} {item.path}: {item.message}")
    return 1 if any(item.blocking for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
