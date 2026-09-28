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
URL = re.compile(r"url\(\s*['\"]?([^'\")]+)", re.IGNORECASE)
FONT_FAMILY = re.compile(r"(?<![-\w])font-family\s*:\s*([^;}{]+)", re.IGNORECASE)
FRAME_OVERRIDE = re.compile(r"(?i)(?:\bnhimc-frame\b|::part\s*\(|\.(?:brand|sidebar|statusbar|mobile-brand)\b)")
ASSET_REFERENCE = re.compile(r"['\"]([^'\"]+\.(?:svg|woff2?|ttf|otf)(?:#[^'\"]*)?)['\"]", re.IGNORECASE)
PROTECTED_FRAME_TOKENS = {
    "--nhimc-frame-sidebar-width",
    "--nhimc-frame-sidebar-collapsed-width",
    "--nhimc-frame-header-height",
}
ALLOWED_FONT_FAMILIES = {
    "noto sans kr", "malgun gothic", "apple sd gothic neo", "system-ui",
    "sans-serif", "serif", "monospace",
}
BASELINE_COMPONENT_IDS = {
    "button", "input", "textarea", "select", "checkbox", "radio", "switch",
    "date-input", "field", "search", "card", "badge", "status", "table",
    "tabs", "dialog", "pagination", "icon",
}
REQUIRED_DECISION_HEADINGS = {
    "## Unmet use case",
    "## Rejected registered composition",
    "## Proposed API",
    "## Accessibility behavior",
    "## Token use",
    "## Tests",
}
ALLOWED_THEME_SELECTORS = {":root", '[data-nhimc-theme="nhimc-light"]'}
IGNORED_PARTS = {".git", ".superpowers", "__pycache__", "vendor"}


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
    registered_assets = set()
    asset_registry = root / "registry/assets.json"
    if asset_registry.is_file():
        registered_assets = {
            item.get("path", "")
            for item in load_json(asset_registry).get("assets", [])
        }
    component_registry = root / "registry/components.json"
    if component_registry.is_file():
        component_data = load_json(component_registry)
        for component in component_data.get("components", []):
            component_id = component.get("id", "")
            decision = component.get("decision")
            if component_id not in BASELINE_COMPONENT_IDS and not decision:
                findings.append(
                    Finding(
                        "design.missing-component-decision",
                        "registry/components.json",
                        f"New component requires a decision record: {component_id}",
                    )
                )
            elif decision:
                decision_path = root / decision
                expected_prefix = f"docs/decisions/components/{component_id}"
                if not decision.startswith(expected_prefix) or not decision_path.is_file():
                    findings.append(
                        Finding(
                            "design.missing-component-decision",
                            decision,
                            f"Component-specific decision record is missing: {component_id}",
                        )
                    )
                else:
                    decision_text = decision_path.read_text(encoding="utf-8")
                    if not REQUIRED_DECISION_HEADINGS.issubset(set(decision_text.splitlines())) or "[ ]" in decision_text or "TODO" in decision_text:
                        findings.append(
                            Finding(
                                "design.incomplete-component-decision",
                                decision,
                                f"Component decision record is incomplete: {component_id}",
                            )
                        )
    for theme in registry.get("themes", []):
        relative = theme.get("file", "")
        path = root / relative
        if not path.is_file():
            findings.append(Finding("design.missing-theme", relative, "Registered theme is missing"))
            continue
        text = _without_comments(path.read_text(encoding="utf-8"))
        font_file = theme.get("fontFile")
        if font_file and not (root / font_file).is_file():
            findings.append(
                Finding("design.missing-font-styles", font_file, "Registered font stylesheet is missing")
            )
        allowed_tokens = set(theme.get("tokens", []))
        for token in sorted(allowed_tokens & PROTECTED_FRAME_TOKENS):
            findings.append(
                Finding(
                    "design.protected-frame-token",
                    relative,
                    f"Theme cannot own protected frame dimension: {token}",
                )
            )
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
        if _is_ignored(relative_path):
            continue
        text = _without_comments(path.read_text(encoding="utf-8"))
        relative = relative_path.as_posix()
        if relative_path.parts[:2] != ("src", "frame") and FRAME_OVERRIDE.search(text):
            findings.append(
                Finding("design.frame-override", relative, "CSS attempts to style the protected frame")
            )
        for family_match in FONT_FAMILY.finditer(text):
            value = family_match.group(1).strip()
            if value.startswith("var("):
                continue
            families = {
                item.strip().strip("'\"").lower() for item in value.split(",")
            }
            unknown = families - ALLOWED_FONT_FAMILIES
            if unknown:
                line = text.count("\n", 0, family_match.start()) + 1
                findings.append(
                    Finding("design.unregistered-font", f"{relative}:{line}", "CSS references an unregistered font family")
                )
        for url_match in URL.finditer(text):
            value = url_match.group(1)
            if value.startswith(("data:", "http:", "https:")):
                continue
            resolved = (path.parent / value.split("#", 1)[0]).resolve()
            try:
                asset_relative = resolved.relative_to(root).as_posix()
            except ValueError:
                asset_relative = value
            suffix = Path(value.split("#", 1)[0]).suffix.lower()
            if suffix in {".woff", ".woff2", ".ttf", ".otf"} and asset_relative not in registered_assets:
                findings.append(
                    Finding("design.unregistered-font", relative, "CSS references an unregistered font asset")
                )
            if suffix == ".svg" and asset_relative not in registered_assets:
                findings.append(
                    Finding("design.unregistered-icon", relative, "CSS references an unregistered SVG asset")
                )
        if relative_path.parts[:2] == ("src", "themes"):
            continue
        for match in COLOR.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(Finding("design.hard-coded-color", f"{relative_path.as_posix()}:{line}", "Use a registered --nhimc-* color token"))

    examples = root / "examples"
    for path in examples.rglob("*.css") if examples.is_dir() else []:
        text = _without_comments(path.read_text(encoding="utf-8"))
        if re.search(r"\.nhimc-[a-z0-9-]+", text, re.IGNORECASE):
            findings.append(
                Finding(
                    "design.local-component-style",
                    path.relative_to(root).as_posix(),
                    "Examples cannot reimplement registered components",
                )
            )
    for path in examples.rglob("*.html") if examples.is_dir() else []:
        text = _without_comments(path.read_text(encoding="utf-8"))
        relative = path.relative_to(root).as_posix()
        if re.search(r"(?i)<style\b|\sstyle\s*=", text):
            findings.append(
                Finding("design.example-inline-style", relative, "Examples cannot contain inline styles")
            )
        if re.search(r"(?i)<(?:link|script|img)\b[^>]+(?:href|src)\s*=\s*['\"]https?://", text):
            findings.append(
                Finding("design.external-asset", relative, "Examples cannot load external runtime assets")
            )
        if re.search(r"(?i)(?:\.style\.|style\.setProperty|insertRule|adoptedStyleSheets)", text):
            findings.append(
                Finding(
                    "design.example-style-injection",
                    relative,
                    "Examples cannot inject local styles",
                )
            )
    for path in examples.rglob("*.js") if examples.is_dir() else []:
        text = _without_comments(path.read_text(encoding="utf-8"))
        if re.search(r"(?i)(?:\.style\.|style\.setProperty|insertRule|adoptedStyleSheets|<style\b)", text):
            findings.append(
                Finding(
                    "design.example-style-injection",
                    path.relative_to(root).as_posix(),
                    "Examples cannot inject local styles",
                )
            )
    for extension in ("*.html", "*.js"):
        for path in root.rglob(extension):
            relative_path = path.relative_to(root)
            if _is_ignored(relative_path):
                continue
            text = path.read_text(encoding="utf-8")
            for match in ASSET_REFERENCE.finditer(text):
                value = match.group(1)
                if value.startswith(("data:", "http:", "https:")):
                    continue
                resolved = (path.parent / value.split("#", 1)[0]).resolve()
                try:
                    asset_relative = resolved.relative_to(root).as_posix()
                except ValueError:
                    asset_relative = value
                if asset_relative not in registered_assets:
                    kind = "font" if Path(value.split("#", 1)[0]).suffix.lower() != ".svg" else "icon"
                    findings.append(
                        Finding(
                            f"design.unregistered-{kind}",
                            relative_path.as_posix(),
                            f"Source references an unregistered {kind} asset",
                        )
                    )
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
