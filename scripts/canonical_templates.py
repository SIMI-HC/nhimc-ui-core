from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
import re


VENDOR = Path("vendor/nhimc-design")
CATALOG = VENDOR / "templates/catalog.yaml"
COMPONENT_REGISTRY = VENDOR / "components/registry.md"
PATTERN_REGISTRY = VENDOR / "patterns/registry.md"
TEMPLATE_ASSETS = VENDOR / "assets/templates"
COMPONENT_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|")


@dataclass(frozen=True)
class TemplateContract:
    id: str
    asset: str
    page_type: str
    variant: str
    shells: tuple[str, ...]
    selectable: bool
    content_contract: tuple[str, ...]
    required_components: tuple[str, ...]
    optional_components: tuple[str, ...]
    supported_states: tuple[str, ...]

    def as_registry_entry(self) -> dict[str, object]:
        value = asdict(self)
        value["shells"] = list(self.shells)
        value["content_contract"] = list(self.content_contract)
        value["required_components"] = list(self.required_components)
        value["optional_components"] = list(self.optional_components)
        value["supported_states"] = list(self.supported_states)
        return value


def _load_catalog(root: Path) -> dict:
    path = root.resolve() / CATALOG
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"canonical Template catalog is unreadable: {path}") from error
    if not isinstance(value, dict):
        raise ValueError("canonical Template catalog must be a JSON object")
    return value


def _registered_components(root: Path) -> set[str]:
    path = root.resolve() / COMPONENT_REGISTRY
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"canonical component registry is unreadable: {path}") from error
    values: set[str] = set()
    in_table = False
    for line in lines:
        if line.startswith("| id | purpose |"):
            in_table = True
            continue
        if not in_table or line.startswith("|---"):
            continue
        match = COMPONENT_ROW.match(line)
        if not match:
            if values:
                break
            continue
        values.add(match.group(1).strip())
    return values


def _registered_patterns(root: Path) -> set[str]:
    path = root.resolve() / PATTERN_REGISTRY
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"canonical pattern registry is unreadable: {path}") from error
    return {
        line.removeprefix("## ").strip()
        for line in lines
        if line.startswith("## ") and line.removeprefix("## ").strip()
    }


def registered_design_items(root: Path) -> frozenset[str]:
    return frozenset(_registered_components(root) | _registered_patterns(root))


def _string_tuple(entry: dict, field: str, template_id: str, errors: list[str]) -> tuple[str, ...]:
    value = entry.get(field, [])
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(f"Template {template_id}: {field} must be a string array")
        return ()
    return tuple(value)


def _safe_asset(root: Path, asset: object, template_id: str, errors: list[str]) -> str:
    if not isinstance(asset, str) or not asset:
        errors.append(f"Template {template_id}: template asset is missing")
        return ""
    relative = PurePosixPath(asset)
    if relative.is_absolute() or ".." in relative.parts or relative.suffix.lower() != ".html":
        errors.append(f"Template {template_id}: asset is outside canonical Template assets: {asset}")
        return asset
    expected_prefix = PurePosixPath("assets/templates")
    if relative.parts[: len(expected_prefix.parts)] != expected_prefix.parts:
        errors.append(f"Template {template_id}: asset is outside canonical Template assets: {asset}")
        return asset
    base = (root.resolve() / TEMPLATE_ASSETS).resolve()
    path = (root.resolve() / VENDOR / Path(*relative.parts)).resolve()
    try:
        path.relative_to(base)
    except ValueError:
        errors.append(f"Template {template_id}: asset is outside canonical Template assets: {asset}")
        return asset
    if not path.is_file():
        errors.append(f"Template {template_id}: canonical Template asset is missing: {asset}")
    return asset


def _contracts_and_errors(root: Path) -> tuple[list[TemplateContract], list[str]]:
    try:
        catalog = _load_catalog(root)
    except ValueError as error:
        return [], [str(error)]
    entries = catalog.get("templates")
    layouts = catalog.get("layouts")
    if not isinstance(entries, list) or not entries:
        return [], ["canonical Template catalog templates must be a nonempty array"]
    if not isinstance(layouts, list):
        return [], ["canonical Template catalog layouts must be an array"]
    known_shells = {
        item.get("id") for item in layouts if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    try:
        known_components = registered_design_items(root)
    except ValueError as error:
        return [], [str(error)]
    contracts: list[TemplateContract] = []
    errors: list[str] = []
    ids: list[str] = []
    assets: list[str] = []
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            errors.append(f"Template at index {index} must be an object")
            continue
        template_id = raw.get("id")
        if not isinstance(template_id, str) or not template_id:
            template_id = f"index-{index}"
            errors.append(f"Template at index {index}: id is missing")
        ids.append(template_id)
        asset = _safe_asset(root, raw.get("template"), template_id, errors)
        if asset:
            assets.append(asset)
        shells = _string_tuple(raw, "shell", template_id, errors)
        for shell in shells:
            if shell not in known_shells:
                errors.append(f"Template {template_id}: unknown shell {shell}")
        required = _string_tuple(raw, "required_components", template_id, errors)
        optional = _string_tuple(raw, "optional_components", template_id, errors)
        for component in (*required, *optional):
            if component not in known_components:
                errors.append(f"Template {template_id}: unregistered component {component}")
        content_contract = _string_tuple(raw, "content_contract", template_id, errors)
        if not content_contract:
            errors.append(f"Template {template_id}: content_contract must not be empty")
        page_type = raw.get("page_type")
        variant = raw.get("variant")
        if not isinstance(page_type, str) or not page_type:
            errors.append(f"Template {template_id}: page_type is missing")
            page_type = ""
        if not isinstance(variant, str) or not variant:
            errors.append(f"Template {template_id}: variant is missing")
            variant = ""
        selectable = raw.get("selectable", True)
        if not isinstance(selectable, bool):
            errors.append(f"Template {template_id}: selectable must be boolean")
            selectable = False
        contracts.append(
            TemplateContract(
                id=template_id,
                asset=asset,
                page_type=page_type,
                variant=variant,
                shells=shells,
                selectable=selectable,
                content_contract=content_contract,
                required_components=required,
                optional_components=optional,
                supported_states=_string_tuple(raw, "supported_states", template_id, errors),
            )
        )
    for duplicate in sorted({value for value in ids if ids.count(value) > 1}):
        errors.append(f"duplicate Template id: {duplicate}")
    for duplicate in sorted({value for value in assets if assets.count(value) > 1}):
        errors.append(f"duplicate Template asset: {duplicate}")
    asset_root = root.resolve() / TEMPLATE_ASSETS
    discovered = {
        "assets/templates/" + path.relative_to(asset_root).as_posix()
        for path in asset_root.rglob("*.html")
    } if asset_root.is_dir() else set()
    for extra in sorted(discovered - set(assets)):
        errors.append(f"uncatalogued Template asset: {extra}")
    return contracts, errors


def validate_template_catalog(root: Path) -> list[str]:
    return _contracts_and_errors(root)[1]


def load_template_contracts(root: Path) -> dict[str, TemplateContract]:
    contracts, errors = _contracts_and_errors(root)
    if errors:
        raise ValueError("\n".join(errors))
    return {contract.id: contract for contract in contracts if contract.selectable}


def get_template_contract(root: Path, template_id: str) -> TemplateContract:
    contracts = load_template_contracts(root)
    try:
        contract = contracts[template_id]
    except KeyError as error:
        raise ValueError(f"unknown canonical Template: {template_id}") from error
    if not contract.selectable:
        raise ValueError(f"canonical Template is not selectable: {template_id}")
    return contract
