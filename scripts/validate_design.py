import argparse
import re
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import Finding, load_json


COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.DOTALL)
DECLARED_TOKEN = re.compile(r"(--[a-z0-9-]+)\s*:", re.IGNORECASE)
COLOR = re.compile(r"#[0-9a-f]{3,8}\b|(?:rgb|rgba|hsl|hsla)\(\s*[^)]*\)", re.IGNORECASE)
ALLOWED_THEME_SELECTORS = {":root", '[data-nhimc-theme="nhimc-light"]'}
IGNORED_PARTS = {".git", ".superpowers", "__pycache__"}


def _without_comments(text: str) -> str:
    return COMMENT.sub("", text)


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def validate_design(root: Path) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    registry_path = root / "registry/themes.json"
    if not registry_path.is_file():
        return [Finding("design.missing-theme-registry", "registry/themes.json", "Theme registry is required")]

    registry = load_json(registry_path)
    for theme in registry.get("themes", []):
        relative = theme.get("file", "")
        path = root / relative
        if not path.is_file():
            findings.append(Finding("design.missing-theme", relative, "Registered theme is missing"))
            continue
        text = _without_comments(path.read_text(encoding="utf-8"))
        allowed_tokens = set(theme.get("tokens", []))
        for selector_group, body in RULE.findall(text):
            selectors = {item.strip() for item in selector_group.split(",")}
            for selector in sorted(selectors - ALLOWED_THEME_SELECTORS):
                findings.append(Finding("design.theme-selector", relative, f"Theme selector is not allowed: {selector}"))
            for token in DECLARED_TOKEN.findall(body):
                if token not in allowed_tokens:
                    findings.append(Finding("design.unregistered-token", relative, f"Theme declares unregistered token: {token}"))

    for path in root.rglob("templates"):
        if path.is_dir() and not _is_ignored(path.relative_to(root)):
            findings.append(Finding("design.template-system", path.relative_to(root).as_posix(), "Page template directories are not allowed"))

    src = root / "src"
    for path in src.rglob("*.css") if src.is_dir() else []:
        relative_path = path.relative_to(root)
        if _is_ignored(relative_path) or relative_path.parts[:2] == ("src", "themes"):
            continue
        text = _without_comments(path.read_text(encoding="utf-8"))
        for match in COLOR.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(Finding("design.hard-coded-color", f"{relative_path.as_posix()}:{line}", "Use a registered --nhimc-* color token"))
    return sorted(findings)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate NHIMC design rules")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings = validate_design(args.root)
    for item in findings:
        print(f"ERROR {item.rule} {item.path}: {item.message}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
