import argparse
import ipaddress
import json
import re
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import Finding


TEXT_EXTENSIONS = {
    ".css", ".html", ".js", ".json", ".md", ".mjs", ".py", ".sh",
    ".svg", ".toml", ".txt", ".xml", ".yaml", ".yml",
}
IGNORED_PARTS = {
    ".git", ".superpowers", "__pycache__", "node_modules", ".pytest_cache",
    ".mypy_cache", "dist", "release",
}
UNSAFE_FIXTURE = ("tests", "fixtures", "public-safety")
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
URL_CREDENTIALS = re.compile(r"https?://[^\s/:@]+:[^\s/@]+@", re.IGNORECASE)
INTERNAL_HOST = re.compile(
    r"https?://(?:[^\s/]+\.)?(?:localhost|intranet|[^\s/.]+\.(?:local|internal|corp))(?:[/:\s]|$)",
    re.IGNORECASE,
)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|access[_-]?token|client[_-]?secret|password)\b"
    r"\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{16,}"
)
TOKEN = re.compile(r"\b(?:sk|ghp|glpat|xox[baprs])-[A-Za-z0-9_-]{20,}\b")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.IGNORECASE)
KOREAN_PHONE = re.compile(r"(?<!\d)01[016789][ -]?\d{3,4}[ -]?\d{4}(?!\d)")
RESIDENT_NUMBER = re.compile(r"(?<!\d)\d{6}[ -][1-4]\d{6}(?!\d)")
ALLOWED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net"}
LOCAL_NETWORK_ALLOWLIST = {
    "README.md",
    "scripts/run_browser_tests.py",
    "docs/superpowers/plans/2026-09-28-nhimc-ui-core-implementation.md",
}


def _is_ignored(relative: Path, whole_tree: bool) -> bool:
    if any(part in IGNORED_PARTS for part in relative.parts):
        return True
    return whole_tree and relative.parts[: len(UNSAFE_FIXTURE)] == UNSAFE_FIXTURE


def _line_findings(relative: str, number: int, line: str) -> list[Finding]:
    location = f"{relative}:{number}"
    findings: list[Finding] = []

    for match in IPV4.finditer(line):
        try:
            address = ipaddress.ip_address(match.group(0))
        except ValueError:
            continue
        if (
            address.is_private or address.is_loopback or address.is_link_local
        ) and relative not in LOCAL_NETWORK_ALLOWLIST:
            findings.append(
                Finding("public.private-network", location, "Private or local network address detected")
            )
            break

    if URL_CREDENTIALS.search(line):
        findings.append(
            Finding("public.url-credentials", location, "URL contains embedded credentials")
        )
    if INTERNAL_HOST.search(line) and relative not in LOCAL_NETWORK_ALLOWLIST:
        findings.append(
            Finding("public.internal-url", location, "Internal host marker detected")
        )
    if SECRET_ASSIGNMENT.search(line) or TOKEN.search(line):
        findings.append(
            Finding("public.possible-secret", location, "High-confidence credential pattern detected")
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
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative_path = path.relative_to(root)
        relative = relative_path.as_posix()
        if _is_ignored(relative_path, whole_tree):
            continue
        if include is not None and path.name not in include and relative not in include:
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            findings.extend(_line_findings(relative, number, line))
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
