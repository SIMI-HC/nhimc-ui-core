"""Safety and registry rules for authored Content (no Template system)."""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import json
from pathlib import Path
import re

PROTECTED_ROLES = frozenset(
    {"app-shell", "app-main", "sidebar", "site-header", "content-slot", "statusbar", "mobile-drawer"}
)
FORBIDDEN_TAGS = frozenset({"style", "script", "link", "base", "iframe", "object", "embed"})
VOID_ELEMENTS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
)
PATTERN_REGISTRY = Path("vendor/nhimc-design/patterns/registry.md")


@dataclass(frozen=True)
class ContentInspection:
    components: tuple[str, ...]
    roles: tuple[str, ...]


class _Inspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.content_roots = 0
        self.roles: list[str] = []
        self.components: list[str] = []
        self._stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        values = {name.lower(): value or "" for name, value in attrs}
        role = values.get("data-nhimc-role")
        if role:
            if role in PROTECTED_ROLES:
                raise ValueError(f"protected Frame role {role} is not allowed in Content")
            self.roles.append(role)
            if role == "content":
                self.content_roots += 1
        self.components.extend(values.get("data-nhimc-component", "").split())
        if tag in FORBIDDEN_TAGS:
            raise ValueError(f"forbidden {tag} element in Content")
        if any(name in values for name in ("src", "srcset", "poster")):
            raise ValueError("Content contains an external resource attribute")
        if "data-nhimc-template-root" in values or "data-template" in values:
            raise ValueError("Templates are not supported; compose registered components and layout primitives")
        inline = values.get("style")
        if inline and re.search(r"url\s*\(|@import|expression\s*\(|javascript\s*:|[{}]", inline, re.I):
            raise ValueError("Content contains an unsafe inline style")
        if tag not in VOID_ELEMENTS:
            self._stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_ELEMENTS:
            self._stack.pop()

    def handle_endtag(self, tag):
        tag = tag.lower()
        if not self._stack or self._stack[-1] != tag:
            raise ValueError(f"unbalanced Content near </{tag}>")
        self._stack.pop()

    def close(self):
        super().close()
        if self._stack:
            raise ValueError(f"unbalanced Content: <{self._stack[-1]}>")


def registered_names(root: Path) -> frozenset[str]:
    components = json.loads((root / "registry/components.json").read_text(encoding="utf-8"))["components"]
    names = {item["id"] for item in components}
    patterns = root / PATTERN_REGISTRY
    if patterns.is_file():
        names.update(
            line.removeprefix("## ").strip()
            for line in patterns.read_text(encoding="utf-8").splitlines()
            if line.startswith("## ") and line[3:].strip()
        )
    layouts = json.loads((root / "registry/layouts.json").read_text(encoding="utf-8"))["primitives"]
    names.update(item["id"] for item in layouts)
    return frozenset(names)


def validate_content(root: Path, html: str) -> ContentInspection:
    parser = _Inspector()
    parser.feed(html)
    parser.close()
    if parser.content_roots != 1:
        raise ValueError(f"Content must contain exactly one content root; found {parser.content_roots}")
    known = registered_names(root)
    for component in parser.components:
        if component not in known:
            raise ValueError(f"unknown component {component}; use the Component Registry")
    return ContentInspection(tuple(parser.components), tuple(parser.roles))
