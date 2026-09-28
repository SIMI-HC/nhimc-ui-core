# NHIMC Canonical Template Composition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade NHIMC UI Core to 3.0.0 so every accepted authoring document is composed from a pinned canonical Page Template and the exact Chrome-verified result is delivered as one offline `index.html`.

**Architecture:** Keep canonical bytes immutable under `vendor/nhimc-design`, parse their catalog into typed Core contracts, and adapt only the Template content root into an already verified canonical Frame. A separate delivery pipeline builds into a temporary workspace, obtains a detached Chrome receipt for the exact bytes, revalidates the completion manifest and digest, and atomically copies only `index.html` to the requested destination.

**Tech Stack:** Python 3.11+ standard library, Node.js 22+ built-in test runner and Chrome DevTools Protocol scripts, Chromium/Google Chrome/Microsoft Edge headless browser, HTML/CSS/JavaScript, Git.

**Spec:** `docs/superpowers/specs/2026-09-28-nhimc-canonical-template-delivery-design.md`

## Global Constraints

- Canonical source is `C:\Projects\NhimcDesign\.agents\skills\nhimc-worktool` pinned to commit `08c45402eece8a7c55afc60385e8671c9f13081a`.
- Vendored canonical files are copied byte-for-byte and recorded with byte length, SHA-256, media type, source, destination, and extraction role.
- Core version becomes exactly `3.0.0`; legacy unmarked business layouts are rejected rather than silently upgraded.
- One authoring boundary remains `<nhimc-frame>`, and every screen panel selects one registered canonical Template.
- Authored `<style>`, external resources, Frame-owned markup, already-built artifacts, remote URLs, and runtime sidecars are rejected.
- Template CSS is deterministically scoped below `[data-nhimc-template-root="<template-id>"]` and may not affect protected Frame roles, classes, IDs, elements, dialogs, or navigation.
- The delivered artifact is exactly one UTF-8 `index.html`, works through `file://`, makes zero network or sidecar requests, and contains six embedded Noto Sans KR font faces plus canonical logo and icon assets.
- A file is deliverable only when its bytes match a detached exact-browser receipt; the receipt is never copied beside the delivered HTML.
- No documentation may call source HTML, a Library entry, an inaccessible local path, or later build instructions a completed download.

## Review Focus

- An authoring document may declare a real Template ID but shuffle or duplicate its required roles; validation must reject it with the Template ID and first structural mismatch.
- A canonical Template stylesheet may contain grouped selectors, nested media queries, keyframes, pseudo-elements, or global selectors; scoping must preserve content behavior while rejecting every protected-Frame target.
- Two screen panels may use different registered Templates; validation and emitted manifest must preserve the per-screen mapping and never apply one panel's contract to the other.
- An artifact or receipt may be modified after Chrome verification; delivery must recompute both byte length and SHA-256 and refuse the transfer.
- Browser discovery may run on Windows or Linux; it must select an explicit executable deterministically and fail with an actionable message when no supported browser exists.

---

## File Structure

- `scripts/nhimc_upstream.py`: owns the canonical snapshot allowlist, destination mapping, extraction roles, and expected counts.
- `scripts/canonical_templates.py`: parses the pinned catalog and exposes immutable Frame/Template contracts.
- `scripts/canonical_template_adapter.py`: extracts canonical content markup/CSS, checks the protected boundary, and returns a scoped Template bundle.
- `scripts/build_single_html.py`: validates authoring input, composes Template content into a canonical Frame, embeds resources, and emits the completion manifest.
- `scripts/artifact_delivery.py`: validates completion manifests and detached receipts, then atomically transfers exact verified bytes.
- `scripts/build_verified_artifact.py`: local orchestration API/CLI used by humans and the later MCP bridge.
- `scripts/run_browser_tests.py`: exact-browser execution and detached receipt generation on Windows and Linux.
- `scripts/verify_template_parity.mjs`: canonical-versus-adapted Template and protected-Frame parity matrix.
- `registry/templates.json`: generated, reviewable Core registry derived from the pinned canonical catalog.
- `tests/fixtures/authoring/`: valid v3 authoring fixtures containing canonical Template structure.
- `tests/fixtures/unsafe-authoring/`: intentionally invalid legacy, leakage, and tampering inputs excluded from publishable examples.
- `tests/python/` and `tests/node/`: contract, adaptation, delivery, and browser-runner tests.

### Task 1: Expand the pinned snapshot to complete canonical Template material

**Files:**
- Modify: `scripts/nhimc_upstream.py`
- Modify: `scripts/sync_nhimc_design.py`
- Modify: `scripts/verify_nhimc_design_sync.py`
- Modify: `tests/python/test_nhimc_design_sync.py`
- Modify: `vendor/nhimc-design/upstream.json`
- Create: `vendor/nhimc-design/assets/templates/admin/master-detail.html`
- Create: `vendor/nhimc-design/assets/templates/dashboard/analytics.html`
- Create: `vendor/nhimc-design/assets/templates/dashboard/monitoring.html`
- Create: `vendor/nhimc-design/assets/templates/dashboard/workflow.html`
- Create: `vendor/nhimc-design/assets/templates/detail/default.html`
- Create: `vendor/nhimc-design/assets/templates/form/sections.html`
- Create: `vendor/nhimc-design/assets/templates/list/default.html`
- Create: `vendor/nhimc-design/assets/templates/list/dense.html`
- Create: `vendor/nhimc-design/assets/templates/list/with-tabs.html`
- Create: `vendor/nhimc-design/scripts/validate_templates.py`
- Create: `vendor/nhimc-design/scripts/validate_deliverable.py`

**Interfaces:**
- Consumes: `enumerate_allowlisted_files(source: Path) -> list[tuple[Path, Path]]` and the existing byte-preserving sync pipeline.
- Produces: `snapshot_counts(source: Path) -> dict[str, int]` with `templates == 9`, manifest roles `template-asset`, `template-contract`, and `canonical-validator`, and a byte-identical complete snapshot for Tasks 2–8.

- [ ] **Step 1: Write failing snapshot coverage tests**

```python
def test_snapshot_includes_every_catalogued_template_asset(self):
    source, _ = self._canonical_git_fixture()
    destinations = {destination.as_posix() for _, destination in enumerate_allowlisted_files(source)}
    self.assertIn("assets/templates/list/default.html", destinations)

def test_snapshot_counts_nine_templates(self):
    source = Path(r"C:\Projects\NhimcDesign\.agents\skills\nhimc-worktool")
    self.assertEqual(snapshot_counts(source)["templates"], 9)

def test_manifest_assigns_template_asset_role(self):
    source, _ = self._canonical_git_fixture()
    relative = Path("assets/templates/list/default.html")
    entry = manifest_entry(source, relative, _destination_for(relative))
    self.assertEqual(entry["role"], "template-asset")
```

Extend `_canonical_git_fixture()` before its initial commit with all nine catalog entries/assets and the two validator scripts, and extend the test imports with `enumerate_allowlisted_files`, `manifest_entry`, `_destination_for`, and `snapshot_counts`.

- [ ] **Step 2: Run the focused tests and observe the missing allowlist/count failures**

Run: `python -m unittest tests.python.test_nhimc_design_sync -v`

Expected: FAIL because `assets/templates` and canonical validator scripts are absent and `snapshot_counts()` has no `templates` key.

- [ ] **Step 3: Extend the allowlist, destination mapping, roles, and counts**

```python
ALLOWLIST_DIRECTORIES = (
    Path("assets/layouts"),
    Path("assets/templates"),
    Path("assets/icons"),
    Path("components"),
    Path("patterns"),
    Path("rules"),
    Path("tokens"),
    Path("templates"),
    Path("docs/design-docs/assets/logo"),
    Path("docs/design-docs/assets/font"),
)
ALLOWLIST_FILES = (
    Path("assets/components/showcase.html"),
    Path("docs/design-docs/assets/fonts.css"),
    Path("scripts/validate_templates.py"),
    Path("scripts/validate_deliverable.py"),
)
EXPECTED_COUNTS = {"layouts": 7, "templates": 9, "components": 49, "logos": 9, "fonts": 6}
```

Map `assets/templates` to `assets/templates`, `scripts/validate_templates.py` and `scripts/validate_deliverable.py` to `scripts/`, classify the two scripts as `canonical-validator`, and classify `templates/**` separately from `assets/templates/**` as `template-contract` and `template-asset`.

- [ ] **Step 4: Run snapshot tests until the expanded contract passes**

Run: `python -m unittest tests.python.test_nhimc_design_sync -v`

Expected: PASS, including destination collision, dirty-source, symlink, and byte-preservation tests.

- [ ] **Step 5: Regenerate the pinned snapshot from the clean canonical source**

Run: `python scripts/sync_nhimc_design.py --source C:\Projects\NhimcDesign\.agents\skills\nhimc-worktool --expected-commit 08c45402eece8a7c55afc60385e8671c9f13081a`

Expected: the nine Template assets and two validators appear in `vendor/nhimc-design`, and `upstream.json` contains their exact digests.

- [ ] **Step 6: Verify every vendored byte against the source commit**

Run: `python scripts/verify_nhimc_design_sync.py --source C:\Projects\NhimcDesign\.agents\skills\nhimc-worktool`

Expected: PASS with `templates=9` and no missing, extra, or digest-mismatched file.

- [ ] **Step 7: Commit the expanded snapshot**

```bash
git add scripts/nhimc_upstream.py scripts/sync_nhimc_design.py scripts/verify_nhimc_design_sync.py tests/python/test_nhimc_design_sync.py vendor/nhimc-design
git commit -m "feat: vendor canonical page templates"
```

### Task 2: Parse canonical Template contracts into a typed Core registry

**Files:**
- Create: `scripts/canonical_templates.py`
- Create: `scripts/generate_template_registry.py`
- Create: `tests/python/test_canonical_templates.py`
- Create: `registry/templates.json`
- Modify: `scripts/verify_nhimc_design_sync.py`

**Interfaces:**
- Consumes: verified `vendor/nhimc-design/templates/catalog.yaml`, which contains JSON despite its extension, and the component IDs in `vendor/nhimc-design/components/registry.md`.
- Produces: `TemplateContract`, `load_template_contracts(root: Path) -> dict[str, TemplateContract]`, `get_template_contract(root: Path, template_id: str) -> TemplateContract`, `validate_template_catalog(root: Path) -> list[str]`, and deterministic `registry/templates.json`.

- [ ] **Step 1: Write contract parsing and rejection tests**

```python
class CanonicalTemplateTests(unittest.TestCase):
    def test_loads_all_nine_selectable_templates(self):
        contracts = load_template_contracts(ROOT)
        self.assertEqual(len(contracts), 9)
        self.assertEqual(contracts["list-default"].asset, "assets/templates/list/default.html")
        self.assertEqual(contracts["list-default"].shells, ("left", "left-blank", "top", "blog", "top-left"))

    def test_rejects_unknown_template_id(self):
        with self.assertRaisesRegex(ValueError, "unknown canonical Template: invented-grid"):
            get_template_contract(ROOT, "invented-grid")

    def test_rejects_missing_required_component_registration(self):
        root = self.copy_repo_fixture()
        catalog = json.loads((root / "vendor/nhimc-design/templates/catalog.yaml").read_text("utf-8"))
        catalog["templates"][0]["required_components"].append("InventedWidget")
        (root / "vendor/nhimc-design/templates/catalog.yaml").write_text(json.dumps(catalog), "utf-8")
        self.assertIn("InventedWidget", "\n".join(validate_template_catalog(root)))
```

- [ ] **Step 2: Run the new tests and verify imports fail**

Run: `python -m unittest tests.python.test_canonical_templates -v`

Expected: FAIL with `ModuleNotFoundError: scripts.canonical_templates`.

- [ ] **Step 3: Implement immutable contract types and catalog validation**

```python
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

def get_template_contract(root: Path, template_id: str) -> TemplateContract:
    contracts = load_template_contracts(root)
    try:
        contract = contracts[template_id]
    except KeyError as error:
        raise ValueError(f"unknown canonical Template: {template_id}") from error
    if not contract.selectable:
        raise ValueError(f"canonical Template is not selectable: {template_id}")
    return contract
```

Validate unique IDs, safe relative assets below `vendor/nhimc-design/assets/templates`, registered shell IDs, registered components, nonempty content contracts, asset existence, and exact catalog-to-asset coverage.

- [ ] **Step 4: Generate a stable public registry**

Write `generate_template_registry.py` so `python scripts/generate_template_registry.py --check` compares canonical JSON serialization (`ensure_ascii=False`, `indent=2`, `sort_keys=True`, final newline) and normal execution rewrites only when bytes differ.

Run: `python scripts/generate_template_registry.py`

Expected: `registry/templates.json` contains nine sorted entries and the full pinned commit.

- [ ] **Step 5: Add dynamic catalog validation to snapshot verification**

Call `validate_template_catalog(root)` after digest verification and report each violation as a failed canonical snapshot condition. Do not import or execute the vendored validator; keep it as a behavioral reference while Core validates its own mapped paths.

- [ ] **Step 6: Run registry and snapshot checks**

Run: `python -m unittest tests.python.test_canonical_templates tests.python.test_nhimc_design_sync -v`

Run: `python scripts/generate_template_registry.py --check`

Run: `python scripts/verify_nhimc_design_sync.py`

Expected: all three commands PASS.

- [ ] **Step 7: Commit the typed registry**

```bash
git add scripts/canonical_templates.py scripts/generate_template_registry.py scripts/verify_nhimc_design_sync.py tests/python/test_canonical_templates.py registry/templates.json
git commit -m "feat: register canonical page template contracts"
```

### Task 3: Build a deterministic content-only Template adapter

**Files:**
- Create: `scripts/canonical_template_adapter.py`
- Create: `tests/python/test_canonical_template_adapter.py`
- Create: `tests/fixtures/unsafe-authoring/template-frame-leak.html`

**Interfaces:**
- Consumes: `TemplateContract` and verified bytes from `vendor/nhimc-design/assets/templates/**`.
- Produces: `TemplateBundle`, `adapt_canonical_template(root: Path, contract: TemplateContract) -> TemplateBundle`, and `validate_authored_template_content(root: Path, contract: TemplateContract, authored_html: str) -> None`.

- [ ] **Step 1: Write extraction, graph, determinism, and leakage tests**

```python
class CanonicalTemplateAdapterTests(unittest.TestCase):
    def test_extracts_list_default_content_and_scopes_css(self):
        contract = get_template_contract(ROOT, "list-default")
        bundle = adapt_canonical_template(ROOT, contract)
        self.assertEqual(bundle.template_id, "list-default")
        self.assertIn('data-nhimc-role="content"', bundle.skeleton_html)
        self.assertIn('[data-nhimc-template-root="list-default"] .toolbar', bundle.scoped_css)
        self.assertNotIn("<html", bundle.skeleton_html.lower())

    def test_adapter_is_byte_deterministic(self):
        contract = get_template_contract(ROOT, "dashboard-monitoring")
        first = adapt_canonical_template(ROOT, contract)
        second = adapt_canonical_template(ROOT, contract)
        self.assertEqual(first, second)

    def test_rejects_grouped_selector_that_reaches_sidebar(self):
        css = ".toolbar, .sidebar { display:grid }"
        with self.assertRaisesRegex(ValueError, "protected Frame selector.*sidebar"):
            scope_template_css("list-default", css)
```

Add tests for nested `@media`, preserved `@keyframes`, pseudo-elements, `:root`, `html`, `body`, IDs matching Frame controls, `[data-nhimc-role=app-shell]`, `.main`, `.site-header`, `.statusbar`, dialogs, and malformed CSS.

- [ ] **Step 2: Run the adapter tests and observe the missing module failure**

Run: `python -m unittest tests.python.test_canonical_template_adapter -v`

Expected: FAIL because the adapter module does not exist.

- [ ] **Step 3: Implement the adapter's explicit return type**

```python
@dataclass(frozen=True)
class TemplateBundle:
    template_id: str
    skeleton_html: str
    scoped_css: str
    roles: tuple[str, ...]
    components: tuple[str, ...]
    source_sha256: str

PROTECTED_ROLES = frozenset({"app-shell", "sidebar", "site-header", "content-slot", "statusbar", "mobile-drawer"})
PROTECTED_CLASSES = frozenset({"app-shell", "sidebar", "site-header", "main", "statusbar", "mobile-drawer"})
PROTECTED_IDS = frozenset({"sidebarToggle", "mobileMenuOpen", "mobileMenuClose", "helpDialog"})
```

Use `html.parser.HTMLParser` subclasses to extract exactly one `main[data-nhimc-role="content"]`, all inline `<style>` blocks, ordered roles, and component markers. Reject scripts, Frame-owned roles, external dependencies, duplicate content roots, and parser imbalance.

- [ ] **Step 4: Implement token-aware CSS scoping**

Implement `scope_template_css(template_id: str, css: str) -> str` as a brace/string/comment-aware scanner. Prefix every ordinary selector with the escaped Template root; recurse into `@media`, `@supports`, `@container`, and `@layer`; preserve `@keyframes`, `@font-face` rejection, and keyframe step selectors; reject `html`, `body`, `:root`, universal-only selectors, protected classes/IDs/roles, external `url()`, and unbalanced blocks before emitting CSS.

- [ ] **Step 5: Validate authored markup against the canonical graph**

```python
def validate_authored_template_content(root: Path, contract: TemplateContract, authored_html: str) -> None:
    authored = inspect_content_root(authored_html)
    canonical = inspect_content_root(adapt_canonical_template(root, contract).skeleton_html)
    require_single_root(authored, contract.id)
    require_role_order_and_nesting(authored, canonical, contract.id)
    require_components(authored.components, contract.required_components, contract.id)
    reject_unknown_components(authored.components, registered_component_ids(root), contract.id)
```

Error messages must include `Template <id>`, the missing/duplicated role or component, and its expected parent or order position.

- [ ] **Step 6: Run all adapter tests**

Run: `python -m unittest tests.python.test_canonical_template_adapter -v`

Expected: PASS for all nine assets, deterministic output, complex CSS constructs, and every protected selector rejection.

- [ ] **Step 7: Commit the adapter**

```bash
git add scripts/canonical_template_adapter.py tests/python/test_canonical_template_adapter.py tests/fixtures/unsafe-authoring/template-frame-leak.html
git commit -m "feat: adapt canonical content templates"
```

### Task 4: Enforce the v3 authoring contract in the single-HTML builder

**Files:**
- Modify: `scripts/build_single_html.py`
- Modify: `tests/python/test_single_html.py`
- Modify: `tests/fixtures/authoring/operations/index.html`
- Modify: `tests/fixtures/authoring/administration/index.html`
- Create: `tests/fixtures/unsafe-authoring/bare-business-layout.html`
- Create: `tests/fixtures/unsafe-authoring/already-built-artifact.html`
- Create: `tests/fixtures/unsafe-authoring/mixed-screen-templates.html`

**Interfaces:**
- Consumes: `get_template_contract()`, `adapt_canonical_template()`, and `validate_authored_template_content()`.
- Produces: `AuthoringScreen`, `parse_authoring_screens(source_html: str) -> tuple[AuthoringScreen, ...]`, and a Template-aware `build_single_html(root: Path, source: Path, output: Path) -> Path`.

- [ ] **Step 1: Convert the reported 5 KB failure pattern into a rejecting regression test**

```python
def test_rejects_bare_legacy_business_layout(self):
    with tempfile.TemporaryDirectory() as folder:
        output = Path(folder) / "index.html"
        with self.assertRaisesRegex(ValueError, "data-template.*registered canonical Template"):
            build_single_html(ROOT, ROOT / "tests/fixtures/unsafe-authoring/bare-business-layout.html", output)
        self.assertFalse(output.exists())

def test_rejects_authoring_source_at_delivery_boundary(self):
    source = ROOT / "tests/fixtures/authoring/operations/index.html"
    with self.assertRaisesRegex(ValueError, "not a completed artifact"):
        inspect_completion_manifest(source.read_text("utf-8"))
```

- [ ] **Step 2: Add failing tests for Template selection and panel mapping**

Test unknown IDs, unsupported Frame/Template pairs, absent Template roots, authored styles, missing required components, duplicate roles, already-built metadata, multiple panels with different Templates, and navigation-to-panel 1:1 binding.

Run: `python -m unittest tests.python.test_single_html -v`

Expected: FAIL because v2 accepts unmarked content and emits no Template bundle or manifest.

- [ ] **Step 3: Define the per-screen authoring representation**

```python
@dataclass(frozen=True)
class AuthoringScreen:
    screen_id: str
    template_id: str
    content_html: str

def parse_authoring_screens(source_html: str) -> tuple[AuthoringScreen, ...]:
    """Return navigation-bound screens in manifest order after strict v3 validation."""
```

For a single-screen document, require `data-template` on `<nhimc-frame>` and a matching `main[data-nhimc-role="content"][data-nhimc-template-root]`. For multiple panels, require `data-template` on each `section[data-screen-panel]` and exactly one matching content root inside each panel.

- [ ] **Step 4: Integrate canonical Template adaptation before Frame rendering**

For every `AuthoringScreen`, load its contract, assert the selected Frame occurs in `contract.shells`, validate its role/component graph, and collect one deduplicated `TemplateBundle` per Template ID. Pass only validated content roots to `FramePayload`; never copy a canonical Template's `<html>`, `<head>`, Frame shell, or script.

- [ ] **Step 5: Embed isolated Template CSS and completion metadata**

Insert sorted Template bundles after the canonical component bundle:

```html
<style data-nhimc-template-bundle="list-default">
/* deterministic scoped canonical CSS */
</style>
<script id="nhimc-completion-manifest" type="application/json">{"artifactType":"nhimc-single-html"}</script>
```

The manifest object uses these exact keys: `artifactType`, `schemaVersion`, `coreVersion`, `upstreamCommit`, `frameId`, `screens`, `themeId`, `bundleSha256`, `runtimeSha256`, `sidecarCount`, and `verificationRequired`. `screens` is an ordered array of `{screenId, templateId}`; `sidecarCount` is `0`; `verificationRequired` is `true`.

- [ ] **Step 6: Write output atomically**

Write UTF-8/LF bytes to `tempfile.NamedTemporaryFile(delete=False, dir=output.parent)`, flush and close, call `_validate_standalone()` and `inspect_completion_manifest()` on those exact bytes, then `os.replace(temp_name, output)`. On any exception, unlink only the explicitly created temporary file.

- [ ] **Step 7: Migrate valid fixtures from `.specimen`/`.grid` to canonical structures**

Base operations on `list-default` and administration on `admin-master-detail`. Preserve the canonical `data-nhimc-role`, `data-nhimc-component`, wrapper, field, table, action, and pagination hierarchy; change only business labels, rows, IDs, menu data, and safe business scripts.

- [ ] **Step 8: Run builder tests and inspect a real artifact**

Run: `python -m unittest tests.python.test_single_html -v`

Run: `python scripts/build_single_html.py --input tests/fixtures/authoring/operations/index.html --output .tmp/operations/index.html`

Expected: tests PASS; output contains no `<nhimc-frame>`, contains canonical Frame and `data-nhimc-template-root="list-default"`, and is larger than the authoring source because fonts, icons, logo, component CSS, Template CSS, and runtime are embedded.

- [ ] **Step 9: Commit the v3 builder boundary**

```bash
git add scripts/build_single_html.py tests/python/test_single_html.py tests/fixtures/authoring tests/fixtures/unsafe-authoring
git commit -m "feat: require canonical templates in authoring"
```

### Task 5: Add exact-browser receipts and fail-closed artifact delivery

**Files:**
- Create: `scripts/artifact_delivery.py`
- Create: `scripts/build_verified_artifact.py`
- Modify: `scripts/run_browser_tests.py`
- Modify: `scripts/verify_standalone_browser.mjs`
- Create: `tests/python/test_artifact_delivery.py`
- Modify: `tests/python/test_single_html.py`

**Interfaces:**
- Consumes: Template-aware `build_single_html()` and exact `file://` browser verification.
- Produces: `ArtifactReceipt`, `VerifiedArtifact`, `build_and_verify(root: Path, source: Path, work_dir: Path) -> VerifiedArtifact`, `load_matching_receipt(artifact: Path, receipt: Path) -> ArtifactReceipt`, and `deliver_verified_artifact(verified: VerifiedArtifact, destination: Path) -> Path`.

- [ ] **Step 1: Write failing receipt and tamper tests**

```python
def test_delivery_requires_matching_external_receipt(self):
    verified = self.build_fixture()
    verified.html_path.write_text(verified.html_path.read_text("utf-8") + "\n<!-- changed -->", "utf-8")
    with self.assertRaisesRegex(ValueError, "artifact digest does not match browser receipt"):
        deliver_verified_artifact(verified, self.folder / "index.html")

def test_delivery_returns_only_index_html(self):
    verified = self.build_fixture()
    destination = self.folder / "download" / "index.html"
    result = deliver_verified_artifact(verified, destination)
    self.assertEqual(result, destination)
    self.assertEqual([path.name for path in destination.parent.iterdir()], ["index.html"])
```

Also test changed receipt digest, changed receipt byte count, authoring source passed as artifact, missing manifest, absent receipt, non-`index.html` default normalization, and failure leaving no destination file.

- [ ] **Step 2: Run the delivery tests and verify the module is missing**

Run: `python -m unittest tests.python.test_artifact_delivery -v`

Expected: FAIL with `ModuleNotFoundError: scripts.artifact_delivery`.

- [ ] **Step 3: Define receipt and verified-artifact types**

```python
@dataclass(frozen=True)
class ArtifactReceipt:
    schema_version: int
    artifact_sha256: str
    artifact_bytes: int
    runtime_token: str
    browser_product: str
    browser_version: str
    verified_at: str

@dataclass(frozen=True)
class VerifiedArtifact:
    html_path: Path
    receipt_path: Path
    sha256: str
    bytes: int
    manifest: dict[str, object]
```

`verified_at` is UTC ISO-8601 and exists only in the detached receipt, so artifact reproducibility is unchanged.

- [ ] **Step 4: Make the browser runner write a receipt only after a full PASS**

Add `--receipt PATH` and require it only with `--standalone-file`. Extend the Node verifier's final JSON with browser product/version and the already checked runtime token. Python computes the exact file bytes and SHA-256 after Node exits `0`, writes the receipt atomically, and removes a pre-existing requested receipt before starting so a failed run cannot reuse stale proof.

- [ ] **Step 5: Implement receipt matching and delivery checks**

`load_matching_receipt()` must recompute artifact byte length and SHA-256, parse and validate the completion manifest, confirm the runtime token in HTML equals the receipt, require `verificationRequired is True`, require `sidecarCount == 0`, and reject `<nhimc-frame>`. `deliver_verified_artifact()` repeats these checks immediately before an atomic byte copy and names the destination `index.html` when a directory is supplied.

- [ ] **Step 6: Implement the local orchestration API and CLI**

```python
def build_and_verify(root: Path, source: Path, work_dir: Path) -> VerifiedArtifact:
    artifact = work_dir / "index.html"
    receipt = work_dir / "index.receipt.json"
    build_single_html(root, source, artifact)
    run_exact_browser_verification(root, artifact, receipt)
    proof = load_matching_receipt(artifact, receipt)
    return VerifiedArtifact(artifact, receipt, proof.artifact_sha256, proof.artifact_bytes, inspect_completion_manifest(artifact.read_text("utf-8")))
```

The CLI accepts `--input` and `--output`, creates a private temporary workspace, invokes `build_and_verify()`, invokes `deliver_verified_artifact()`, prints one JSON summary with `status`, `filename`, `mimeType`, `sha256`, and `bytes`, then deletes the workspace. It must never print authoring HTML.

- [ ] **Step 7: Run delivery and exact-browser tests**

Run: `python -m unittest tests.python.test_artifact_delivery tests.python.test_single_html -v`

Run: `python scripts/build_verified_artifact.py --input tests/fixtures/authoring/operations/index.html --output .tmp/delivery/index.html`

Run: `python scripts/run_browser_tests.py --standalone-file .tmp/delivery/index.html`

Expected: every command PASS; `.tmp/delivery` contains only `index.html`; CLI summary digest matches `Get-FileHash .tmp/delivery/index.html -Algorithm SHA256`.

- [ ] **Step 8: Commit exact delivery**

```bash
git add scripts/artifact_delivery.py scripts/build_verified_artifact.py scripts/run_browser_tests.py scripts/verify_standalone_browser.mjs tests/python/test_artifact_delivery.py tests/python/test_single_html.py
git commit -m "feat: deliver exact browser-verified html"
```

### Task 6: Verify Template parity, responsive behavior, and protected Frame isolation

**Files:**
- Create: `scripts/verify_template_parity.mjs`
- Create: `tests/browser/template-parity-probe.js`
- Create: `tests/node/template-parity.test.js`
- Modify: `scripts/run_browser_tests.py`
- Modify: `scripts/verify_all.py`
- Modify: `scripts/verify_release.py`
- Modify: `tests/python/test_single_html.py`

**Interfaces:**
- Consumes: nine canonical Template assets, their adapted bundles, seven Frame adapters, and browser executable discovery.
- Produces: `find_browser() -> Path` supporting explicit environment override and Windows/Linux candidates, `run_template_parity(root: Path, viewports=DEFAULT_VIEWPORTS) -> dict`, and a release-blocking Template matrix.

- [ ] **Step 1: Write browser discovery and parity-result tests**

```python
def test_find_browser_prefers_explicit_environment_path(self):
    with mock.patch.dict(os.environ, {"NHIMC_BROWSER_PATH": str(self.fake_browser)}):
        self.assertEqual(find_browser(), self.fake_browser)

def test_template_parity_requires_all_cells(self):
    result = run_template_parity(self.root, viewports=((390, 844),))
    self.assertEqual(len(result["results"]), 9 * 2)
    self.assertTrue(result["all_passed"])
```

Add a missing-browser test that names `NHIMC_BROWSER_PATH` and searched candidates in the exception.

- [ ] **Step 2: Run focused tests before implementation**

Run: `python -m unittest tests.python.test_single_html -v`

Run: `npm run test:node`

Expected: new discovery and Template parity tests FAIL.

- [ ] **Step 3: Implement portable browser discovery**

Check `NHIMC_BROWSER_PATH` first, then Windows standard paths, then `shutil.which()` for `google-chrome`, `google-chrome-stable`, `chromium`, `chromium-browser`, and `microsoft-edge`. Resolve and verify a regular file before returning it.

- [ ] **Step 4: Implement the parity probe and matrix runner**

For each selectable Template and light/dark theme at 1440×900, 1024×768, and 390×844, open the canonical asset and a standalone artifact containing the adapted Template. Collect role order/nesting, required component presence, focusability, horizontal overflow ownership, filter/action geometry, declared-state visibility, and screenshots. Separately snapshot protected Frame geometry/computed styles before and after Template injection.

`all_passed` is true only when every expected cell reports `structure`, `responsive`, `focus`, `pixels`, and `frameIsolation` true. The Node process prints a single final JSON object and exits nonzero on protocol or browser failure.

- [ ] **Step 5: Add matrix commands to all verification gates**

Insert `canonical template parity` after canonical Frame parity in `verify_all.py` and `verify_release.py`. Add CLI mode `--canonical-template-parity-only` to `run_browser_tests.py`; keep it mutually exclusive with standalone and component modes.

- [ ] **Step 6: Run the complete visual matrix**

Run: `python scripts/run_browser_tests.py --canonical-template-parity-only`

Expected: `9 templates x 3 viewports x 2 themes` and PASS, with no protected Frame change.

- [ ] **Step 7: Run Node and release-facing tests**

Run: `npm run test:node`

Run: `python -m unittest tests.python.test_single_html -v`

Expected: PASS.

- [ ] **Step 8: Commit the Template browser gate**

```bash
git add scripts/verify_template_parity.mjs tests/browser/template-parity-probe.js tests/node/template-parity.test.js scripts/run_browser_tests.py scripts/verify_all.py scripts/verify_release.py tests/python/test_single_html.py
git commit -m "test: enforce canonical template parity"
```

### Task 7: Publish the 3.0 lifecycle and migrate every platform contract

**Files:**
- Modify: `VERSION`
- Modify: `package.json`
- Modify: `plugin.json`
- Modify: `registry/project.json`
- Modify: `README.md`
- Modify: `bootstrap.md`
- Modify: `skills/nhimc-ui/SKILL.md`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.gemini-extension.json`
- Modify: `CHANGELOG.md`
- Modify: `tests/python/test_platform_adapters.py`
- Modify: `tests/python/test_release_build.py`
- Modify: `tests/python/test_contracts.py`

**Interfaces:**
- Consumes: v3 Template-aware builder and exact delivery command.
- Produces: one consistent platform lifecycle: prompt → Template selection → validation → build → exact-browser receipt → downloadable `index.html`; ChatGPT Web remains `WEB_BOOTSTRAP` until the separate Bridge plan is deployed and verified.

- [ ] **Step 1: Write failing version and wording tests**

```python
def test_all_manifests_report_version_3(self):
    self.assertEqual((ROOT / "VERSION").read_text("utf-8").strip(), "3.0.0")
    self.assertEqual(json.loads((ROOT / "package.json").read_text("utf-8"))["version"], "3.0.0")
    self.assertEqual(json.loads((ROOT / "plugin.json").read_text("utf-8"))["version"], "3.0.0")

def test_chatgpt_web_ready_requires_callable_verified_bridge(self):
    project = json.loads((ROOT / "registry/project.json").read_text("utf-8"))
    chatgpt = next(item for item in project["platformSupport"] if item["environment"] == "chatgpt-web")
    ready = [item for item in chatgpt["outcomes"] if item["status"] == "READY"]
    self.assertEqual(ready[0]["capability"], "verified-builder-bridge-connected-and-download-tested")
```

Also assert every user-facing guide contains `data-template`, `build_verified_artifact.py`, exact `index.html`, `context-only`, and a prohibition on attaching authoring source as the completed file.

- [ ] **Step 2: Run platform and release contract tests**

Run: `python -m unittest tests.python.test_platform_adapters tests.python.test_release_build tests.python.test_contracts -v`

Expected: FAIL on v2 versions and the old `portable-plugin-loaded-and-verified` readiness condition.

- [ ] **Step 3: Update all versions to exactly 3.0.0**

Change `VERSION`, package/plugin manifests, compatibility manifests, and `CHANGELOG.md` together. Describe the authoring contract break and the migration from `.specimen`/`.grid` to registered canonical Templates.

- [ ] **Step 4: Rewrite bootstrap and user guidance in Korean**

Document the default user experience as: invoke `bootstrap.md` once in a capable local host, ask for a screen in natural Korean, and receive one verified `index.html`. Put Python commands in a maintainer troubleshooting section, not the primary usage path. State that ChatGPT Web repository context alone cannot execute the builder and must never attach the source file as the final download.

- [ ] **Step 5: Update the Skill and platform registry**

Require Template selection before markup, require `build_verified_artifact.py` on local capable hosts, reserve “다운로드할 수 있게 만들었다” for an actual transferred verified file, and define ChatGPT Web `READY` capability exactly as `verified-builder-bridge-connected-and-download-tested`.

- [ ] **Step 6: Run platform tests and public scan**

Run: `python -m unittest tests.python.test_platform_adapters tests.python.test_release_build tests.python.test_contracts -v`

Run: `python scripts/validate_public.py`

Expected: PASS with no private path, credential, internal host, or unsafe binary finding in publishable content.

- [ ] **Step 7: Commit the v3 contract and documentation**

```bash
git add VERSION package.json plugin.json registry/project.json README.md bootstrap.md skills/nhimc-ui/SKILL.md .claude-plugin/plugin.json .gemini-extension.json CHANGELOG.md tests/python/test_platform_adapters.py tests/python/test_release_build.py tests/python/test_contracts.py
git commit -m "docs: publish canonical template delivery lifecycle"
```

### Task 8: Regenerate the reported transport-management artifact and close all Core gates

**Files:**
- Create: `tests/fixtures/authoring/transport-management/index.html`
- Create: `tests/python/test_transport_management_artifact.py`
- Modify: `scripts/verify_all.py`
- Modify: `PUBLIC_ASSET_REVIEW.md`

**Interfaces:**
- Consumes: all v3 Core APIs and gates from Tasks 1–7.
- Produces: a canonical `list-default` transport-management fixture, reproducible verified output, and a green Core 3.0 release gate ready for the separate Builder Bridge plan.

- [ ] **Step 1: Write the transport-screen acceptance test**

```python
def test_transport_management_build_is_canonical_and_offline(self):
    with tempfile.TemporaryDirectory() as folder:
        verified = build_and_verify(ROOT, FIXTURE, Path(folder))
        html = verified.html_path.read_text("utf-8")
        self.assertIn('data-nhimc-template-root="list-default"', html)
        self.assertIn('data-nhimc-component="PageHeader"', html)
        self.assertIn('data-nhimc-component="SearchFilter"', html)
        self.assertIn('data-nhimc-component="DataTable"', html)
        self.assertIn('data-nhimc-component="PaginationArea"', html)
        self.assertNotIn("<nhimc-frame", html)
        self.assertGreater(verified.bytes, 1_000_000)
```

- [ ] **Step 2: Run the acceptance test before the fixture exists**

Run: `python -m unittest tests.python.test_transport_management_artifact -v`

Expected: FAIL because the v3 fixture is absent.

- [ ] **Step 3: Author the screen from the canonical `list-default` skeleton**

Use the canonical role/component hierarchy for PageHeader, SearchFilter, DataTable, and PaginationArea. Populate hospital transfer status filters, request rows, assignment state badges, accessible labels, row-detail dialog behavior, navigation manifest, loading/empty/error states, and responsive table wrapper without adding authored CSS or Frame markup.

- [ ] **Step 4: Prove reproducibility and exact delivery**

Run the local delivery command twice into separate empty directories:

```powershell
python scripts/build_verified_artifact.py --input tests/fixtures/authoring/transport-management/index.html --output .tmp/run-a/index.html
python scripts/build_verified_artifact.py --input tests/fixtures/authoring/transport-management/index.html --output .tmp/run-b/index.html
if ((Get-FileHash .tmp/run-a/index.html -Algorithm SHA256).Hash -ne (Get-FileHash .tmp/run-b/index.html -Algorithm SHA256).Hash) { throw 'artifact digest mismatch' }
```

Expected: both exact-browser builds PASS and SHA-256 values are identical.

- [ ] **Step 5: Run the full Core test suite**

Run: `python -m unittest discover -s tests/python -v`

Run: `npm run test:node`

Expected: all tests PASS.

- [ ] **Step 6: Run every canonical, browser, public, and release gate**

Run: `python scripts/verify_all.py`

Run: `python scripts/verify_release.py`

Expected: both commands PASS, including snapshot, seven-Frame parity, nine-Template parity, 49-component coverage, standalone `file://`, public safety, legal assets, and protected integrity.

- [ ] **Step 7: Record the asset review and commit the corrected reference artifact source**

Update `PUBLIC_ASSET_REVIEW.md` with the pinned canonical commit, the nine Template count, public logo/font approval, and no unresolved `BLOCKING:` item.

```bash
git add tests/fixtures/authoring/transport-management/index.html tests/python/test_transport_management_artifact.py scripts/verify_all.py PUBLIC_ASSET_REVIEW.md
git commit -m "test: certify canonical transport management artifact"
```

- [ ] **Step 8: Inspect branch state without publishing or claiming web readiness**

Run: `git status --short`

Run: `git log --oneline --decorate -12`

Expected: clean worktree and the Task 1–8 commits present. Do not push, open a Pull Request, deploy a Bridge, or claim ChatGPT Web `READY` as part of this Core-only plan.
