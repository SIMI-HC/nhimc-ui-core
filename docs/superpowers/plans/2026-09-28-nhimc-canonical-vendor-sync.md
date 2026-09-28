# NHIMC Canonical Vendor Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the approximate NHIMC UI Core implementation with a byte-traceable, offline-capable distribution of the complete approved canonical Frame, component, icon, logo, font, theme, token, pattern, rule, and template resources from `NhimcDesign`.

**Architecture:** A byte-preserving sync tool vendors an allowlisted canonical snapshot and records source provenance. Build-time adapters modify only explicit business-owned anchors in canonical layouts, while the single-HTML builder embeds the canonical assets and a browser parity suite compares generated Frame regions with the vendored originals.

**Tech Stack:** Python 3.12 standard library, JavaScript ES modules, Web Components only at the authoring compatibility boundary, Chrome/Edge DevTools Protocol, Node.js built-in test runner, HTML/CSS/SVG, JSON registries.

**Spec:** `docs/superpowers/specs/2026-09-28-nhimc-canonical-vendor-sync-design.md`

## Global Constraints

- Canonical source root is `C:\Projects\NhimcDesign\.agents\skills\nhimc-worktool` at commit `08c45402eece8a7c55afc60385e8671c9f13081a`.
- Project and protected Frame versions advance together from `1.0.0` to `2.0.0`.
- Vendor all 7 canonical layout documents, all 49 component registry entries, all 9 approved logo SVGs, the complete icon sprite, and all 6 WOFF2 files.
- Vendored canonical bytes are immutable, protected with `-text`, and never hand-edited.
- Exclude business examples, private baseline documents, internal hosts/IPs, credentials, personal data, temporary output, and unrelated platform distribution copies.
- Runtime artifacts have no framework, CDN, package-runtime, network, local sidecar, or original-repository dependency.
- The default deliverable is exactly one offline `index.html`; no CSS, JavaScript, font, image, or documentation sidecars are returned.
- Only project title, menu manifest, active route, main content, status, frame choice, and theme choice are business-owned.
- No fallback may use the approximate v1 Frame, Unicode control glyphs, or invented component styling.
- Use TDD for every behavior change and run the exact artifact through `file://` before completion.

## Review Focus

- A malicious or mistaken `--source` outside a Git worktree must fail before reading or copying files; covered by Task 1 source-boundary tests.
- A canonical source with a modified allowlisted file must fail without replacing the last good snapshot; covered by Task 1 dirty-source and atomicity tests.
- CRLF/LF conversion must not silently change provenance; covered by Task 1 byte-digest and `.gitattributes` tests.
- Missing or duplicated `data-nhimc-role` anchors must fail instead of producing partially adapted Frame markup; covered by Task 3 anchor-cardinality tests.
- A final file containing a hidden URL, sidecar navigation, unhandled startup error, missing font, or noncanonical icon must fail exact-artifact verification; covered by Tasks 5 and 6.

---

### Task 0: Preserve the completed fixture cleanup

**Files:**
- Commit only the already completed `examples/` removal, `tests/fixtures/authoring/` migration, README clarification, Skill clarification, and related test-path changes currently present in the worktree.

**Interfaces:**
- Consumes: the verified worktree state from the preceding cleanup request.
- Produces: a clean baseline commit before canonical migration starts.

- [ ] **Step 1: Re-run the completed cleanup verification**

Run:

```powershell
python scripts/verify_all.py
git diff --check
```

Expected: `VERIFY PASS: 6 checks`, Python 57/57, Node 12/12, all browser widths pass, and `standalone file: PASS`.

- [ ] **Step 2: Confirm the cleanup diff contains no canonical migration code**

Run:

```powershell
git status --short
git diff --stat
```

Expected: only the previously reported example-to-fixture cleanup files are present; the new spec and this plan are already committed separately or explicitly excluded.

- [ ] **Step 3: Commit the completed cleanup**

```powershell
git add README.md docs/superpowers/specs/2026-09-28-nhimc-ui-core-design.md examples scripts/run_browser_tests.py skills/nhimc-ui/SKILL.md tests/browser/runner.js tests/fixtures/authoring tests/python/test_design_rules.py tests/python/test_release_build.py tests/python/test_single_html.py
git commit -m "refactor: keep authoring samples internal"
```

### Task 1: Add byte-preserving canonical snapshot synchronization

**Files:**
- Create: `scripts/nhimc_upstream.py`
- Create: `scripts/sync_nhimc_design.py`
- Create: `scripts/verify_nhimc_design_sync.py`
- Create: `tests/python/test_nhimc_design_sync.py`
- Modify: `.gitattributes`
- Modify: `scripts/verify_all.py`

**Interfaces:**
- Consumes: `Path` to the canonical `nhimc-worktool` directory and a destination Core root.
- Produces: `sync_snapshot(source: Path, root: Path, expected_commit: str | None = None) -> dict`, `verify_snapshot(root: Path) -> list[Finding]`, and `vendor/nhimc-design/upstream.json`.

- [ ] **Step 1: Write failing source-boundary, allowlist, and atomicity tests**

Add tests with temporary Git repositories and a minimal canonical-shaped tree:

```python
class NhimcDesignSyncTests(unittest.TestCase):
    def test_sync_rejects_non_git_source(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError, "Git worktree"):
                sync_snapshot(Path(source), Path(root))

    def test_sync_rejects_dirty_allowlisted_source_without_replacing_snapshot(self):
        source, root = self._canonical_git_fixture()
        sync_snapshot(source, root)
        before = (root / "vendor/nhimc-design/upstream.json").read_bytes()
        (source / "assets/layouts/left.html").write_text("dirty", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "modified canonical source"):
            sync_snapshot(source, root)
        self.assertEqual(before, (root / "vendor/nhimc-design/upstream.json").read_bytes())

    def test_sync_copies_only_allowlisted_paths_and_records_byte_digests(self):
        source, root = self._canonical_git_fixture()
        (source / "references/private.txt").parent.mkdir(parents=True)
        (source / "references/private.txt").write_text("must-not-copy", encoding="utf-8")
        manifest = sync_snapshot(source, root)
        destinations = {item["destination"] for item in manifest["files"]}
        self.assertNotIn("references/private.txt", destinations)
        for item in manifest["files"]:
            data = (root / item["destination"]).read_bytes()
            self.assertEqual(item["bytes"], len(data))
            self.assertEqual(item["sha256"], hashlib.sha256(data).hexdigest())
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```powershell
python -m unittest tests.python.test_nhimc_design_sync -v
```

Expected: import failure for `scripts.nhimc_upstream` or missing `sync_snapshot`.

- [ ] **Step 3: Implement the immutable allowlist and manifest model**

In `scripts/nhimc_upstream.py`, define exact allowlisted roots and fixed files:

```python
PINNED_COMMIT = "08c45402eece8a7c55afc60385e8671c9f13081a"
VENDOR_PREFIX = Path("vendor/nhimc-design")
ALLOWLIST_DIRECTORIES = (
    Path("assets/layouts"),
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
)
EXPECTED_COUNTS = {"layouts": 7, "components": 49, "logos": 9, "fonts": 6}
```

Add helpers that reject resolved paths outside `source`, enumerate sorted files, invoke `git status --porcelain -- <allowlisted paths>`, and return manifest entries with `source`, `destination`, `bytes`, `sha256`, `mediaType`, and `role`.

- [ ] **Step 4: Implement staged byte copying and verification**

In `sync_nhimc_design.py`, write to a sibling temporary directory, call the existing public-safety scanner on every staged file, serialize JSON deterministically, verify the stage, then replace only `vendor/nhimc-design`:

```python
def sync_snapshot(source: Path, root: Path, expected_commit: str | None = PINNED_COMMIT) -> dict:
    source = require_clean_git_source(source.resolve(), expected_commit)
    stage_parent = Path(tempfile.mkdtemp(prefix="nhimc-vendor-", dir=root))
    stage = stage_parent / "nhimc-design"
    try:
        manifest = copy_allowlisted_bytes(source, stage)
        write_manifest(stage / "upstream.json", manifest)
        findings = verify_staged_snapshot(stage, manifest)
        if findings:
            raise ValueError(format_findings(findings))
        replace_directory_atomically(stage, root / VENDOR_PREFIX)
        return manifest
    finally:
        shutil.rmtree(stage_parent, ignore_errors=True)
```

`verify_nhimc_design_sync.py` must recalculate every digest, reject extra files, assert counts, and expose `verify_snapshot(root)` for `verify_all.py`.

- [ ] **Step 5: Protect canonical bytes from line-ending conversion**

Append to `.gitattributes`:

```gitattributes
vendor/nhimc-design/** -text
```

Add a test that writes `b"line1\r\nline2\r\n"`, syncs it, and asserts the vendored bytes are identical.

- [ ] **Step 6: Run Task 1 tests and full existing tests**

Run:

```powershell
python -m unittest tests.python.test_nhimc_design_sync -v
python -m unittest discover -s tests/python -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit Task 1**

```powershell
git add .gitattributes scripts/nhimc_upstream.py scripts/sync_nhimc_design.py scripts/verify_nhimc_design_sync.py scripts/verify_all.py tests/python/test_nhimc_design_sync.py
git commit -m "feat: add canonical design snapshot sync"
```

### Task 2: Import the pinned complete canonical snapshot and bump contracts

**Files:**
- Create mechanically: `vendor/nhimc-design/**`
- Modify: `VERSION`
- Modify: `package.json`
- Modify: `registry/project.json`
- Modify: `registry/frames.json`
- Modify: `registry/themes.json`
- Modify: `registry/assets.json`
- Modify: `tests/python/test_contracts.py`
- Modify: `tests/python/test_nhimc_design_sync.py`

**Interfaces:**
- Consumes: `sync_snapshot` and the clean pinned source worktree.
- Produces: a complete immutable snapshot and v2 registry references used by every later task.

- [ ] **Step 1: Add failing completeness and version tests**

```python
def test_repository_contains_complete_pinned_snapshot(self):
    manifest = json.loads((ROOT / "vendor/nhimc-design/upstream.json").read_text(encoding="utf-8"))
    self.assertEqual(PINNED_COMMIT, manifest["commit"])
    self.assertEqual(7, count_role(manifest, "layout"))
    self.assertEqual(9, count_role(manifest, "logo"))
    self.assertEqual(6, count_role(manifest, "font"))
    self.assertEqual(49, parse_component_count(ROOT / "vendor/nhimc-design/components/registry.md"))

def test_project_and_frame_are_version_2(self):
    self.assertEqual("2.0.0", (ROOT / "VERSION").read_text().strip())
    frames = load_json(ROOT / "registry/frames.json")["frames"]
    self.assertEqual("2.0.0", frames[0]["version"])
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
python -m unittest tests.python.test_nhimc_design_sync tests.python.test_contracts -v
```

Expected: snapshot missing and version still `1.0.0`.

- [ ] **Step 3: Run the sync against the pinned source**

```powershell
python scripts/sync_nhimc_design.py --source C:\Projects\NhimcDesign\.agents\skills\nhimc-worktool --root . --expected-commit 08c45402eece8a7c55afc60385e8671c9f13081a
```

Expected: a deterministic `vendor/nhimc-design/upstream.json` and no copied disallowed paths.

- [ ] **Step 4: Advance project and registry contracts to 2.0.0**

Update version fields to `2.0.0`. Register all seven canonical Frame IDs and paths, all nine logos, the icon sprite, all six font files, `fonts.css`, and the upstream manifest. Protected entries use vendored byte hashes; generated adapter files are added only after Task 3 creates them.

- [ ] **Step 5: Verify the imported snapshot and public tree**

Run:

```powershell
python scripts/verify_nhimc_design_sync.py
python scripts/validate_contracts.py
python scripts/validate_public.py
```

Expected: all three exit zero; no private path or internal value appears in output.

- [ ] **Step 6: Commit Task 2**

```powershell
git add VERSION package.json registry vendor/nhimc-design tests/python/test_contracts.py tests/python/test_nhimc_design_sync.py
git commit -m "feat: vendor canonical NHIMC design assets"
```

### Task 3: Build the canonical Frame adapter without visual recreation

**Files:**
- Create: `scripts/canonical_frame.py`
- Create: `src/generated/frame/frame-runtime.js`
- Create: `tests/python/test_canonical_frame.py`
- Create: `tests/browser/canonical-parity.html`
- Create: `tests/browser/canonical-parity.js`
- Modify: `registry/frames.json`
- Modify: `scripts/run_browser_tests.py`
- Modify: `scripts/verify_all.py`

**Interfaces:**
- Consumes: canonical layout HTML and `FramePayload`.
- Produces: `render_canonical_frame(root: Path, frame_id: str, payload: FramePayload) -> str` and browser runtime `window.NhimcCanonicalFrame`.

- [ ] **Step 1: Write failing anchor and preservation tests**

```python
class CanonicalFrameTests(unittest.TestCase):
    def test_only_business_owned_regions_change(self):
        source = canonical_layout("left")
        result = render_canonical_frame(ROOT, "left", sample_payload())
        self.assertEqual(protected_regions(source), protected_regions(result))
        self.assertIn("이송업무 관리", owned_region(result, "content-slot"))

    def test_missing_or_duplicate_anchor_fails_closed(self):
        for count in (0, 2):
            broken = layout_with_anchor_count("content-slot", count)
            with self.assertRaisesRegex(ValueError, "content-slot.*exactly once"):
                render_layout(broken, sample_payload())

    def test_menu_icons_render_canonical_svg_use_elements(self):
        result = render_canonical_frame(ROOT, "left", sample_payload(icon="ambulance"))
        self.assertIn('href="#ambulance"', result)
        self.assertNotIn("☰", result)
        self.assertNotIn("‹", result)
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m unittest tests.python.test_canonical_frame -v
```

Expected: missing `scripts.canonical_frame`.

- [ ] **Step 3: Implement strict anchor replacement**

Define immutable payload types and explicit adapter metadata:

```python
@dataclass(frozen=True)
class MenuItem:
    id: str
    label: str
    icon: str
    href: str
    children: tuple["MenuItem", ...] = ()

@dataclass(frozen=True)
class FramePayload:
    project_title: str
    menu: tuple[MenuItem, ...]
    active_id: str
    content_html: str
    status_text: str = "준비됨 · 오프라인 문서"
    status_state: str = "ready"
    theme: str = "light"
    business_script: str = ""
```

Implement anchor lookup using the exact `data-nhimc-role` attributes and per-layout metadata. Preserve source substrings outside owned element contents. Escape text and attributes, validate IDs and canonical icon IDs, and reject scripts or URLs inside menu data.

- [ ] **Step 4: Implement canonical runtime behavior**

Extract the canonical layout script into `src/generated/frame/frame-runtime.js` without changing its visual behavior. Replace only sample-specific routing with generic `data-menu-id` activation and `nhimc:navigate` dispatch. Retain canonical collapse, help, theme, Drawer, focus restoration, reduced-motion, and status behavior.

The runtime API is:

```javascript
window.NhimcCanonicalFrame = Object.freeze({
  setActive(id) { /* update canonical nav and visible business panel */ },
  setStatus(state, text) { /* update canonical status dot and text */ },
  setTheme(theme, persist = false) { /* canonical light/dark behavior */ },
});
```

- [ ] **Step 5: Add browser geometry and behavior parity tests**

`canonical-parity.js` loads the untouched vendored layout and the adapted layout in sibling iframes, normalizes business-owned text, waits for fonts, and records:

```javascript
function frameSnapshot(doc) {
  const pick = (selector) => {
    const node = doc.querySelector(selector);
    const rect = node.getBoundingClientRect();
    const css = getComputedStyle(node);
    return {
      rect: [rect.x, rect.y, rect.width, rect.height],
      color: css.color,
      background: css.backgroundColor,
      border: css.borderColor,
      radius: css.borderRadius,
      font: css.font,
    };
  };
  return {
    shell: pick('[data-nhimc-role="app-shell"]'),
    sidebar: pick('[data-nhimc-role="sidebar"]'),
    header: pick('[data-nhimc-role="site-header"]'),
    statusbar: pick('[data-nhimc-role="statusbar"]'),
  };
}
```

Assert identical snapshots and identical SVG path data at 1440×900, 1024×768, and 390×844 for light and dark modes. Exercise collapse, help, theme, and mobile Drawer focus.

- [ ] **Step 6: Run Frame tests**

```powershell
python -m unittest tests.python.test_canonical_frame -v
python scripts/run_browser_tests.py --canonical-parity-only
```

Expected: all layouts pass structural tests; default LEFT passes all geometry and behavior checks at six viewport/theme combinations.

- [ ] **Step 7: Register generated adapter hashes and commit**

```powershell
python scripts/update_integrity.py --frame nhimc-default --frame-version 2.0.0
git add scripts/canonical_frame.py src/generated/frame registry/frames.json scripts/run_browser_tests.py scripts/verify_all.py tests/browser/canonical-parity.* tests/python/test_canonical_frame.py
git commit -m "feat: adapt canonical NHIMC frames"
```

### Task 4: Import the complete canonical component catalog and runtime

**Files:**
- Create: `scripts/generate_canonical_components.py`
- Create: `src/generated/components/components.css`
- Create: `src/generated/components/components.js`
- Replace generated content: `registry/components.json`
- Create: `tests/python/test_canonical_components.py`
- Create: `tests/browser/canonical-components.html`
- Create: `tests/browser/canonical-components.js`
- Modify: `scripts/validate_design.py`
- Modify: `scripts/run_browser_tests.py`

**Interfaces:**
- Consumes: vendored `components/registry.md`, `components/icons.md`, and `assets/components/showcase.html`.
- Produces: `generate_components(root: Path) -> dict`, a 49-entry JSON registry, canonical component CSS, and shared controllers.

- [ ] **Step 1: Write failing catalog completeness and provenance tests**

```python
def test_generated_registry_contains_every_canonical_component(self):
    canonical = parse_canonical_registry(ROOT / "vendor/nhimc-design/components/registry.md")
    generated = load_json(ROOT / "registry/components.json")["components"]
    self.assertEqual(49, len(canonical))
    self.assertEqual([item.id for item in canonical], [item["id"] for item in generated])

def test_each_generated_component_points_to_canonical_specimen(self):
    for component in generated_components():
        self.assertTrue(component["canonicalSource"].startswith("vendor/nhimc-design/"))
        self.assertTrue(component["canonicalDigest"])
        self.assertCanonicalSnippet(component["markup"], component["canonicalSource"])
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m unittest tests.python.test_canonical_components -v
```

Expected: generator missing or registry count equals 18 instead of 49.

- [ ] **Step 3: Implement deterministic registry parsing and bundle generation**

Parse the first canonical Markdown registry table through `## 선택 원칙`. Require the exact schema columns and unique IDs. Extract canonical stylesheet and script blocks from the showcase by verified markers, preserving rule text and order. Write deterministic outputs only when generated bytes differ.

Each JSON entry must contain:

```json
{
  "id": "IconButton",
  "variants": ["ghost"],
  "states": ["default", "hover", "focus", "toggled"],
  "canonicalSource": "vendor/nhimc-design/assets/components/showcase.html",
  "canonicalDigest": "<sha256>",
  "markup": "<button class=\"icon-button\" ...>...</button>"
}
```

The full canonical stylesheet is loaded before the selected Frame stylesheet so the Frame remains authoritative for Shell selectors. Tests must fail if the component stylesheet changes a protected Frame snapshot.

- [ ] **Step 4: Generate and validate all 49 components**

```powershell
python scripts/generate_canonical_components.py
python scripts/validate_design.py
```

Expected: `49 canonical components generated`; design validation exits zero.

- [ ] **Step 5: Add interactive component browser coverage**

Render every canonical specimen and verify no missing selector, missing SVG symbol, console error, unhandled rejection, overflow, or inaccessible control name. Exercise Switch, Tabs, Dialog, Sheet, Drawer, Pagination, Progress, Toast, UploadDropzone, FloatingPanel, ChatPanel, and ScheduleGrid behaviors declared in the registry.

- [ ] **Step 6: Run component and regression tests**

```powershell
python -m unittest tests.python.test_canonical_components tests.python.test_design_rules -v
python scripts/run_browser_tests.py --canonical-components-only
npm run test:node
```

Expected: all tests pass and all 49 entries are reported.

- [ ] **Step 7: Commit Task 4**

```powershell
git add scripts/generate_canonical_components.py src/generated/components registry/components.json scripts/validate_design.py scripts/run_browser_tests.py tests/browser/canonical-components.* tests/python/test_canonical_components.py
git commit -m "feat: import complete canonical component catalog"
```

### Task 5: Rebuild the single-HTML pipeline around canonical snapshots

**Files:**
- Modify: `scripts/build_single_html.py`
- Modify: `scripts/verify_standalone_browser.mjs`
- Modify: `scripts/run_browser_tests.py`
- Modify: `tests/python/test_single_html.py`
- Modify: `tests/fixtures/authoring/operations/index.html`
- Modify: `tests/fixtures/authoring/administration/index.html`

**Interfaces:**
- Consumes: existing single-HTML authoring input, `render_canonical_frame`, generated component bundle, and vendor manifest.
- Produces: one self-contained canonical offline HTML file with provenance metadata.

- [ ] **Step 1: Replace fixture expectations with canonical artifact assertions**

Add failing tests:

```python
def test_builder_emits_canonical_frame_and_provenance(self):
    output = build_fixture("operations")
    html = output.read_text(encoding="utf-8")
    self.assertIn('data-nhimc-role="app-shell"', html)
    self.assertNotIn("<nhimc-frame", html)
    self.assertNotIn("☰", html)
    self.assertNotIn("‹", html)
    self.assertIn('name="nhimc-upstream-commit" content="08c4540', html)
    self.assertIn('href="#ambulance"', html)

def test_builder_uses_all_six_canonical_fonts_and_no_sidecars(self):
    html = build_fixture("operations").read_text(encoding="utf-8")
    self.assertEqual(6, html.count("@font-face"))
    self.assertNotRegex(html, r"(?:src|href)=[\"'](?!data:|#)")
```

- [ ] **Step 2: Run single-HTML tests and verify RED**

```powershell
python -m unittest tests.python.test_single_html -v
```

Expected: current Custom Element Frame and missing upstream metadata cause failures.

- [ ] **Step 3: Replace v1 Frame embedding with canonical assembly**

Keep current security validation and business-script extraction, but replace `_bundle_frame_runtime` with:

```python
def _assemble_canonical_document(root: Path, source: Path, html: str) -> str:
    authoring = parse_authoring_document(source, html)
    payload = FramePayload(
        project_title=authoring.project_title,
        menu=authoring.menu,
        active_id=authoring.active_id,
        content_html=authoring.content_html,
        status_text=authoring.status_text,
        status_state=authoring.status_state,
        theme=authoring.theme,
        business_script=authoring.business_script,
    )
    document = render_canonical_frame(root, authoring.frame_id, payload)
    document = embed_component_bundle(root, document)
    document = embed_icon_sprite(root, document)
    document = embed_brand_assets(root, document)
    document = embed_fonts(root, document)
    return add_offline_policy_and_provenance(root, document)
```

Every embed helper verifies the input digest against `upstream.json` before reading it.

- [ ] **Step 4: Update authoring fixtures to canonical component and icon contracts**

Use Korean fictional business content, include explicit `icon` identifiers for every top-level menu item, and use only markup present in the generated 49-entry registry. Do not add fixture-local CSS or copied Frame markup.

- [ ] **Step 5: Strengthen exact-artifact verification**

In `verify_standalone_browser.mjs`, assert canonical roles, upstream metadata, six loaded fonts, SVG control icons, complete absence of Unicode control substitutes, zero external resources, zero navigation, no startup errors, and no marker spoofing.

- [ ] **Step 6: Run builder and exact artifact tests**

```powershell
python -m unittest tests.python.test_single_html -v
python scripts/run_browser_tests.py --standalone-only
```

Expected: every test passes and `standalone file: PASS`.

- [ ] **Step 7: Commit Task 5**

```powershell
git add scripts/build_single_html.py scripts/verify_standalone_browser.mjs scripts/run_browser_tests.py tests/python/test_single_html.py tests/fixtures/authoring
git commit -m "feat: build canonical offline HTML artifacts"
```

### Task 6: Complete all-Frame visual and behavior parity gates

**Files:**
- Create: `scripts/verify_canonical_parity.mjs`
- Create: `tests/python/test_canonical_parity.py`
- Modify: `scripts/run_browser_tests.py`
- Modify: `scripts/verify_release.py`
- Modify: `scripts/verify_all.py`

**Interfaces:**
- Consumes: all seven vendored Frame documents and corresponding adapted documents.
- Produces: a release-blocking parity result per Frame, viewport, and supported theme.

- [ ] **Step 1: Add failing all-Frame parity matrix tests**

```python
def test_release_gate_covers_every_canonical_frame(self):
    result = run_parity_matrix(ROOT)
    self.assertEqual(
        {"left", "left-blank", "top", "top-left", "presentation", "presentation-vertical", "blog"},
        set(result.frames),
    )
    self.assertEqual({"1440x900", "1024x768", "390x844"}, set(result.viewports))
    self.assertTrue(result.all_passed)
```

- [ ] **Step 2: Run test and verify RED**

```powershell
python -m unittest tests.python.test_canonical_parity -v
```

Expected: parity matrix runner missing.

- [ ] **Step 3: Implement deterministic screenshot and state comparison**

Use the existing Chrome/Edge discovery and CDP connection. For each matrix cell, disable animation, await `document.fonts.ready`, normalize approved business-owned text, capture Frame-region PNGs, and compare byte-identical output produced in the same browser session. Also compare the structured state snapshot from Task 3 so a screenshot masking error cannot hide geometry or behavior drift.

Return JSON with this schema:

```json
{
  "frames": ["left"],
  "viewports": ["1440x900"],
  "results": [{"frame":"left","viewport":"1440x900","theme":"light","state":true,"pixels":true}],
  "all_passed": true
}
```

- [ ] **Step 4: Make parity release-blocking**

Add canonical sync verification and parity verification to both `verify_all.py` and `verify_release.py`. A skipped browser, missing source snapshot, masked protected region, state mismatch, or pixel mismatch is a non-zero failure.

- [ ] **Step 5: Run the full parity matrix**

```powershell
python scripts/run_browser_tests.py --canonical-parity-only --all-frames
python -m unittest tests.python.test_canonical_parity -v
```

Expected: seven Frames pass their supported viewport/theme matrix.

- [ ] **Step 6: Commit Task 6**

```powershell
git add scripts/verify_canonical_parity.mjs scripts/run_browser_tests.py scripts/verify_release.py scripts/verify_all.py tests/python/test_canonical_parity.py
git commit -m "test: enforce canonical frame parity"
```

### Task 7: Remove approximate v1 implementation and update AI guidance

**Files:**
- Delete after replacement: `src/frame/nhimc-frame.js`
- Delete after replacement: `src/frame/nhimc-frame.css`
- Delete after replacement: `src/components/components.css`
- Delete after replacement: obsolete v1 theme/layout sources superseded by generated canonical bundles
- Modify: `registry/project.json`
- Modify: `registry/frames.json`
- Modify: `registry/themes.json`
- Modify: `registry/components.json`
- Modify: `registry/assets.json`
- Modify: `bootstrap.md`
- Modify: `skills/nhimc-ui/SKILL.md`
- Modify: `skills/nhimc-ui/references/contracts.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `NOTICE`
- Modify: `PUBLIC_ASSET_REVIEW.md`
- Modify: `docs/platforms/*.md`
- Modify: `tests/python/test_platform_adapters.py`
- Modify: `tests/python/test_release_build.py`

**Interfaces:**
- Consumes: the canonical v2 runtime, registries, and builder.
- Produces: one unambiguous supported path with no reachable approximate Frame fallback.

- [ ] **Step 1: Add failing no-fallback and guidance tests**

```python
def test_no_approximate_v1_frame_remains(self):
    self.assertFalse((ROOT / "src/frame/nhimc-frame.js").exists())
    self.assertFalse((ROOT / "src/frame/nhimc-frame.css").exists())
    for path in public_text_files(ROOT):
        text = path.read_text(encoding="utf-8", errors="replace")
        self.assertNotIn("UI Core 1.0", text)

def test_skill_requires_canonical_builder_and_fail_closed_delivery(self):
    skill = (ROOT / "skills/nhimc-ui/SKILL.md").read_text(encoding="utf-8")
    self.assertIn("canonical", skill.lower())
    self.assertIn("single HTML", skill)
    self.assertIn("must not deliver", skill)
```

- [ ] **Step 2: Run documentation and adapter tests and verify RED**

```powershell
python -m unittest tests.python.test_platform_adapters tests.python.test_release_build -v
```

Expected: v1 paths and old guidance are still present.

- [ ] **Step 3: Delete only superseded v1 implementation files**

Before deletion, confirm every former public contract resolves to a v2 generated or vendored replacement. Remove the hand-authored Frame and reduced component/theme files with `apply_patch`; do not delete the new vendor snapshot, generated runtime, builder, registries, or licenses.

- [ ] **Step 4: Update bootstrap, Skill, README, and platform documentation**

Document this user flow in Korean:

```text
bootstrap.md만 읽고 NHIMC UI Core를 준비해줘.
이송업무 관리 화면 만들어줘.
```

State that AI creates business content only; Core supplies the complete canonical Frame, components, logos, icons, themes, and fonts; the builder returns one offline HTML. If the host cannot call the canonical builder and exact browser verifier, it must report context-only capability and must not handcraft or deliver an approximate HTML.

- [ ] **Step 5: Update release metadata and legal records**

Record v2.0.0, pinned upstream commit, snapshot digest, complete public asset set, Noto Sans KR license, and the user's public-use approval. Do not claim GitHub publication unless a push/release actually occurs.

- [ ] **Step 6: Run adapter, contract, design, and public-safety tests**

```powershell
python -m unittest tests.python.test_platform_adapters tests.python.test_release_build -v
python scripts/validate_contracts.py
python scripts/validate_design.py
python scripts/validate_public.py
```

Expected: all commands exit zero.

- [ ] **Step 7: Commit Task 7**

```powershell
git add -A src registry bootstrap.md skills README.md CHANGELOG.md NOTICE PUBLIC_ASSET_REVIEW.md docs/platforms tests/python/test_platform_adapters.py tests/python/test_release_build.py
git commit -m "refactor: retire approximate UI core v1"
```

### Task 8: Final release verification and reproducibility

**Files:**
- Modify only if a test exposes a defect in an owning task; do not add unrelated cleanup.
- Generate temporarily: exact single-HTML artifacts and two release ZIPs outside tracked source.

**Interfaces:**
- Consumes: all prior task outputs.
- Produces: evidence that v2 is canonical, complete, reproducible, safe, and offline.

- [ ] **Step 1: Run the complete test suite**

```powershell
python scripts/verify_all.py
```

Expected: Python, Node, contracts, canonical sync, design rules, public tree, all-Frame parity, browser behavior, and standalone artifact checks pass.

- [ ] **Step 2: Build and test a real Korean business artifact**

```powershell
python scripts/build_single_html.py --input tests/fixtures/authoring/operations/index.html --output $env:TEMP\nhimc-canonical-index.html
python scripts/run_browser_tests.py --standalone-file $env:TEMP\nhimc-canonical-index.html
```

Expected: one file exists, `standalone file: PASS`, and no sidecar file is created.

- [ ] **Step 3: Verify deterministic release archives**

```powershell
python scripts/build_release.py $env:TEMP\nhimc-ui-core-2.0.0-a.zip
python scripts/build_release.py $env:TEMP\nhimc-ui-core-2.0.0-b.zip
Get-FileHash -Algorithm SHA256 $env:TEMP\nhimc-ui-core-2.0.0-a.zip,$env:TEMP\nhimc-ui-core-2.0.0-b.zip
```

Expected: both SHA-256 values are identical.

- [ ] **Step 4: Inspect final repository state**

```powershell
git status --short
git log --oneline --decorate -12
git diff HEAD~7..HEAD --check
```

Expected: no unintended generated files or uncommitted changes; each task has a focused commit.

- [ ] **Step 5: Commit any verification-only correction and rerun its owning test**

If a verification step exposed a defect, return to the task that owns the behavior, add a failing regression test, implement the smallest correction, rerun that task's tests and `verify_all.py`, then commit with a scoped `fix:` message. If no defect exists, create no empty commit.
