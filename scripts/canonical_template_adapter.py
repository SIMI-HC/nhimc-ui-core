from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from scripts.canonical_templates import TemplateContract, registered_design_items


PROTECTED_ROLES = frozenset(
    {"app-shell", "app-main", "sidebar", "site-header", "content-slot", "statusbar", "mobile-drawer"}
)
PROTECTED_CLASSES = frozenset(
    {
        "app-shell", "sidebar", "sidebar-inset", "site-header", "main",
        "statusbar", "mobile-drawer", "mobile-dialog", "help-dialog", "dialog",
        "header", "side", "shell", "frame", "nav", "brand",
    }
)
PROTECTED_IDS = frozenset(
    {
        "appShell", "sidebarToggle", "mobileMenuOpen", "mobileMenuClose",
        "mobileDialog", "helpDialog", "helpOpen", "themeToggle",
    }
)
PROTECTED_ELEMENTS = frozenset({"html", "body", "header", "aside", "footer", "dialog", "nav"})
VOID_ELEMENTS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
)
STYLE_OPEN = re.compile(r"<style\b(?P<attrs>[^>]*)>", re.I)
EXTERNAL_URL = re.compile(r"url\(\s*(['\"]?)(?!data:|#)(.*?)\1\s*\)", re.I)
ROLE_SELECTOR = re.compile(r"\[\s*data-nhimc-role\s*=\s*(['\"]?)([^\]'\"\s]+)\1\s*\]", re.I)
CLASS_TOKEN = re.compile(r"\.([A-Za-z_][\w-]*)")
ID_TOKEN = re.compile(r"#([A-Za-z_][\w-]*)")
THEME_PREFIX = re.compile(r"^(\[data-theme\s*=\s*(['\"]?)[^\]]+\2\])\s+(.*)$", re.I | re.S)


@dataclass(frozen=True)
class TemplateBundle:
    template_id: str
    skeleton_html: str
    scoped_css: str
    roles: tuple[str, ...]
    components: tuple[str, ...]
    source_sha256: str


@dataclass(frozen=True)
class ContentInspection:
    html: str
    roles: tuple[str, ...]
    role_graph: tuple[tuple[str, str | None], ...]
    components: tuple[str, ...]
    classes: frozenset[str]
    ids: frozenset[str]
    tags: frozenset[str]
    template_id: str | None


def _attrs_map(attrs) -> dict[str, str]:
    return {name.lower(): value or "" for name, value in attrs}


class _DocumentExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.roots: list[str] = []
        self.styles: list[str] = []
        self._capture: list[str] | None = None
        self._capture_tags: list[str] = []
        self._style: list[str] | None = None
        self._style_tags = 0
        self.error: str | None = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        values = _attrs_map(attrs)
        if tag == "script":
            self.error = "canonical Template cannot contain scripts"
        if tag == "style":
            if self._style is not None:
                self.error = "nested style element is not allowed"
            self._style = []
            self._style_tags += 1
        raw = self.get_starttag_text()
        if self._capture is not None:
            self._capture.append(raw)
            if tag not in VOID_ELEMENTS:
                self._capture_tags.append(tag)
        elif tag == "main" and values.get("data-nhimc-role") == "content":
            self._capture = [raw]
            self._capture_tags = [tag]

    def handle_startendtag(self, tag, attrs):
        if self._capture is not None:
            self._capture.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "style":
            if self._style is None:
                self.error = "unbalanced style element"
            else:
                self.styles.append("".join(self._style))
                self._style = None
            return
        if self._capture is None:
            return
        if not self._capture_tags or self._capture_tags[-1] != tag:
            self.error = f"unbalanced content markup near </{tag}>"
            return
        self._capture.append(f"</{tag}>")
        self._capture_tags.pop()
        if not self._capture_tags:
            self.roots.append("".join(self._capture))
            self._capture = None

    def handle_data(self, data):
        if self._style is not None:
            self._style.append(data)
        elif self._capture is not None:
            self._capture.append(data)

    def handle_entityref(self, name):
        if self._capture is not None:
            self._capture.append(f"&{name};")

    def handle_charref(self, name):
        if self._capture is not None:
            self._capture.append(f"&#{name};")

    def handle_comment(self, data):
        if self._capture is not None:
            self._capture.append(f"<!--{data}-->")

    def close(self):
        super().close()
        if self._capture is not None or self._capture_tags:
            self.error = self.error or "unbalanced content root"
        if self._style is not None:
            self.error = self.error or "unbalanced style element"


class _ContentInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.root_count = 0
        self.roles: list[str] = []
        self.role_graph: list[tuple[str, str | None]] = []
        self.components: list[str] = []
        self.classes: set[str] = set()
        self.ids: set[str] = set()
        self.tags: set[str] = set()
        self.template_id: str | None = None
        self._stack: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        values = _attrs_map(attrs)
        self.tags.add(tag)
        role = values.get("data-nhimc-role")
        parent_role = next((item[1] for item in reversed(self._stack) if item[1]), None)
        if role:
            if role in PROTECTED_ROLES:
                raise ValueError(f"protected Frame role {role} is not allowed in Template content")
            self.roles.append(role)
            self.role_graph.append((role, parent_role))
            if role == "content":
                self.root_count += 1
                self.template_id = values.get("data-nhimc-template-root") or None
        for component in values.get("data-nhimc-component", "").split():
            if component:
                self.components.append(component)
        self.classes.update(values.get("class", "").split())
        if values.get("id"):
            self.ids.add(values["id"])
        if tag in {"style", "script", "link", "base", "iframe", "object", "embed"}:
            raise ValueError(f"forbidden {tag} element in Template content")
        if any(name in values for name in ("src", "srcset", "poster")):
            raise ValueError("Template content contains an external resource attribute")
        inline_style = values.get("style")
        if inline_style and re.search(
            r"url\s*\(|@import|expression\s*\(|javascript\s*:|[{}]",
            inline_style,
            re.I,
        ):
            raise ValueError("Template content contains an unsafe inline style")
        if tag not in VOID_ELEMENTS:
            self._stack.append((tag, role))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_ELEMENTS:
            self._stack.pop()

    def handle_endtag(self, tag):
        tag = tag.lower()
        if not self._stack or self._stack[-1][0] != tag:
            raise ValueError(f"unbalanced Template content near </{tag}>")
        self._stack.pop()

    def close(self):
        super().close()
        if self._stack:
            raise ValueError(f"unbalanced Template content: <{self._stack[-1][0]}>")


def inspect_content_root(html: str) -> ContentInspection:
    parser = _ContentInspector()
    parser.feed(html)
    parser.close()
    if parser.root_count != 1:
        raise ValueError(f"Template content must contain exactly one content root; found {parser.root_count}")
    return ContentInspection(
        html=html,
        roles=tuple(parser.roles),
        role_graph=tuple(parser.role_graph),
        components=tuple(parser.components),
        classes=frozenset(parser.classes),
        ids=frozenset(parser.ids),
        tags=frozenset(parser.tags),
        template_id=parser.template_id,
    )


def _split_top_level(value: str, delimiter: str = ",") -> list[str]:
    parts: list[str] = []
    start = 0
    quote: str | None = None
    square = round_depth = 0
    escaped = False
    for index, char in enumerate(value):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"":
            quote = char
        elif char == "[":
            square += 1
        elif char == "]":
            square -= 1
        elif char == "(":
            round_depth += 1
        elif char == ")":
            round_depth -= 1
        elif char == delimiter and square == 0 and round_depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    if quote or square or round_depth:
        raise ValueError("malformed CSS selector")
    return [part for part in parts if part]


def _parse_rules(css: str) -> list[tuple[str, str]]:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules: list[tuple[str, str]] = []
    index = 0
    length = len(css)
    while index < length:
        while index < length and css[index].isspace():
            index += 1
        if index >= length:
            break
        prelude_start = index
        quote: str | None = None
        escaped = False
        round_depth = square_depth = 0
        while index < length:
            char = css[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in "'\"":
                quote = char
            elif char == "(":
                round_depth += 1
            elif char == ")":
                round_depth -= 1
            elif char == "[":
                square_depth += 1
            elif char == "]":
                square_depth -= 1
            elif char == "{" and round_depth == 0 and square_depth == 0:
                break
            elif char == "}" and round_depth == 0 and square_depth == 0:
                raise ValueError("malformed CSS: unexpected closing brace")
            index += 1
        if index >= length or quote or round_depth or square_depth:
            raise ValueError("malformed CSS: missing rule block")
        prelude = css[prelude_start:index].strip()
        if not prelude:
            raise ValueError("malformed CSS: empty rule selector")
        index += 1
        body_start = index
        depth = 1
        quote = None
        escaped = False
        while index < length and depth:
            char = css[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in "'\"":
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            index += 1
        if depth or quote:
            raise ValueError("malformed CSS: unbalanced rule block")
        rules.append((prelude, css[body_start : index - 1].strip()))
    return rules


def _protected_selector_reason(selector: str) -> str | None:
    lower = selector.lower()
    if re.search(r"(^|[\s>+~,(]):root(?=$|[\s>+~.:[#])", lower):
        return ":root"
    for role_match in ROLE_SELECTOR.finditer(selector):
        if role_match.group(2).lower() in PROTECTED_ROLES:
            return role_match.group(2)
    for value in CLASS_TOKEN.findall(selector):
        if value in PROTECTED_CLASSES:
            return value
    for value in ID_TOKEN.findall(selector):
        if value in PROTECTED_IDS:
            return value
    tokens = re.findall(r"(?<![-\w.#])([A-Za-z][\w-]*)(?=$|[\s>+~.:[#])", selector)
    for token in tokens:
        if token.lower() in PROTECTED_ELEMENTS:
            return token
    stripped = re.sub(r"::?[\w-]+(?:\([^)]*\))?", "", selector).strip()
    if stripped in {"*", ""} and "*" in selector:
        return "universal selector"
    return None


def _selector_relevant(selector: str, inspection: ContentInspection) -> bool:
    theme = THEME_PREFIX.match(selector)
    if theme:
        selector = theme.group(3).strip()
    if selector == "main" or selector.startswith("main[") or selector.startswith("main ") or selector.startswith("main>"):
        return True
    if set(CLASS_TOKEN.findall(selector)) & inspection.classes:
        return True
    if set(ID_TOKEN.findall(selector)) & inspection.ids:
        return True
    element_tokens = {
        token.lower()
        for token in re.findall(r"(?<![-\w.#])([A-Za-z][\w-]*)(?=$|[\s>+~.:[#])", selector)
    }
    return bool(element_tokens & inspection.tags)


def _scope_selector(template_id: str, selector: str) -> str:
    reason = _protected_selector_reason(selector)
    if reason:
        raise ValueError(f"protected Frame selector is not allowed: {reason}")
    root = f'[data-nhimc-template-root="{template_id}"]'
    theme = THEME_PREFIX.match(selector)
    theme_prefix = ""
    if theme:
        theme_prefix = theme.group(1) + " "
        selector = theme.group(3).strip()
        reason = _protected_selector_reason(selector)
        if reason:
            raise ValueError(f"protected Frame selector is not allowed: {reason}")
    main = re.match(r"^main(?:\[data-nhimc-role\s*=\s*(['\"]?)content\1\])?(.*)$", selector, re.I | re.S)
    if main:
        suffix = main.group(2).strip()
        if suffix and suffix[0] not in ">+~:[.#":
            suffix = " " + suffix
        return f"{theme_prefix}{root}{suffix}"
    return f"{theme_prefix}{root} {selector}"


def _transform_css(
    template_id: str,
    css: str,
    inspection: ContentInspection | None,
    filter_irrelevant: bool,
) -> str:
    if re.search(r"@import\b", css, re.I) or EXTERNAL_URL.search(css):
        raise ValueError("Template CSS contains an external dependency")
    output: list[str] = []
    for prelude, body in _parse_rules(css):
        lower = prelude.lower()
        if lower.startswith("@font-face"):
            raise ValueError("Template CSS cannot contain @font-face")
        if re.match(r"@(?:-[a-z]+-)?keyframes\b", lower):
            _parse_rules(body)
            output.append(f"{prelude}{{{body}}}")
            continue
        if lower.startswith(("@media", "@supports", "@container", "@layer")):
            nested = _transform_css(template_id, body, inspection, filter_irrelevant)
            if nested:
                output.append(f"{prelude}{{{nested}}}")
            continue
        if prelude.startswith("@"):
            raise ValueError(f"unsupported Template CSS at-rule: {prelude}")
        scoped: list[str] = []
        for selector in _split_top_level(prelude):
            reason = _protected_selector_reason(selector)
            if reason:
                if filter_irrelevant:
                    continue
                raise ValueError(f"protected Frame selector is not allowed: {reason}")
            if filter_irrelevant and inspection is not None and not _selector_relevant(selector, inspection):
                continue
            scoped.append(_scope_selector(template_id, selector))
        if scoped:
            output.append(f"{','.join(scoped)}{{{body}}}")
    return "".join(output)


def scope_template_css(template_id: str, css: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", template_id):
        raise ValueError(f"invalid Template id for CSS scope: {template_id}")
    return _transform_css(template_id, css, None, False)


def _verified_asset(root: Path, contract: TemplateContract) -> bytes:
    root = root.resolve()
    manifest = json.loads(
        (root / "vendor/nhimc-design/upstream.json").read_text(encoding="utf-8")
    )
    destination = f"vendor/nhimc-design/{contract.asset}"
    entry = next(
        (item for item in manifest.get("files", []) if item.get("destination") == destination),
        None,
    )
    if entry is None or entry.get("role") != "template-asset":
        raise ValueError(f"Template {contract.id}: asset is not in the verified snapshot")
    path = root / destination
    data = path.read_bytes()
    if len(data) != entry.get("bytes") or sha256(data).hexdigest() != entry.get("sha256"):
        raise ValueError(f"Template {contract.id}: asset digest does not match pinned snapshot")
    return data


def _add_template_root(markup: str, template_id: str) -> str:
    opening = re.match(r"(<main\b)([^>]*>)", markup, re.I | re.S)
    if not opening:
        raise ValueError(f"Template {template_id}: content root is not a main element")
    attrs = opening.group(2)
    attrs = re.sub(r"\sdata-nhimc-template-root\s*=\s*(['\"]).*?\1", "", attrs, flags=re.I | re.S)
    replacement = f'{opening.group(1)} data-nhimc-template-root="{template_id}"{attrs}'
    return replacement + markup[opening.end() :]


def adapt_canonical_template(root: Path, contract: TemplateContract) -> TemplateBundle:
    data = _verified_asset(root, contract)
    try:
        document = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"Template {contract.id}: asset is not UTF-8") from error
    extractor = _DocumentExtractor()
    extractor.feed(document)
    extractor.close()
    if extractor.error:
        raise ValueError(f"Template {contract.id}: {extractor.error}")
    if len(extractor.roots) != 1:
        raise ValueError(
            f"Template {contract.id}: expected exactly one content root; found {len(extractor.roots)}"
        )
    skeleton = _add_template_root(extractor.roots[0], contract.id)
    inspection = inspect_content_root(skeleton)
    css = "".join(
        _transform_css(contract.id, style, inspection, True)
        for style in extractor.styles
    )
    return TemplateBundle(
        template_id=contract.id,
        skeleton_html=skeleton,
        scoped_css=css,
        roles=inspection.roles,
        components=inspection.components,
        source_sha256=sha256(data).hexdigest(),
    )


def validate_authored_template_content(
    root: Path,
    contract: TemplateContract,
    authored_html: str,
) -> None:
    authored = inspect_content_root(authored_html)
    canonical = inspect_content_root(adapt_canonical_template(root, contract).skeleton_html)
    if authored.template_id != contract.id:
        raise ValueError(
            f"Template {contract.id}: content root data-nhimc-template-root must equal {contract.id}"
        )
    if authored.role_graph != canonical.role_graph:
        authored_roles = set(authored.roles)
        for role, parent in canonical.role_graph:
            if role not in authored_roles:
                raise ValueError(
                    f"Template {contract.id}: missing role {role}; expected parent {parent or 'document'}"
                )
        raise ValueError(f"Template {contract.id}: role order or nesting differs from canonical structure")
    authored_components = set(authored.components)
    for component in contract.required_components:
        if component not in authored_components:
            raise ValueError(f"Template {contract.id}: missing required component {component}")
    known = registered_design_items(root)
    for component in authored.components:
        if component not in known:
            raise ValueError(f"Template {contract.id}: unknown component {component}")
