# NHIMC UI Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-runtime-dependency NHIMC UI core with one immutable frame, replaceable themes, reusable components and primitives, honest six-platform bootstrap guidance, and enforceable public-release gates.

**Architecture:** A native Custom Element owns the protected frame inside an encapsulated Shadow DOM styling boundary, while business content enters through a single slot and design variation enters only through registered CSS tokens. JSON registries are the machine-readable contracts, Python and Node standard-library tests enforce them, and a localhost headless-browser runner verifies actual DOM behavior. Every platform adapter points at the one shared skill and source tree.

**Tech Stack:** HTML5, CSS custom properties, browser-native JavaScript modules and Custom Elements, SVG, JSON, Python 3.12 standard library, Node.js 24 built-in test runner, Chrome/Edge headless mode, Git.

**Spec:** `docs/superpowers/specs/2026-09-28-nhimc-ui-core-design.md`

## Global Constraints

- Project root is `C:\Projects\nhimc-ui-core`; do not modify `C:\Projects\NhimcDesign` or `C:\Projects\NhimcCore`.
- Project version is `1.0.0`; frame ID is `nhimc-default`; frame version is `1.0.0`; default theme is `nhimc-light`.
- Runtime code has no framework, package-runtime, CDN, remote font, or remote icon dependency.
- Frame DOM, branding, frame-owned dimensions, breakpoints, and navigation behavior are immutable within a frame version.
- Theme files contain registered token values only and cannot change frame structure or protected dimensions.
- Registered components must be reused before a new component is added.
- Provide layout primitives and examples; do not create a page-template system or `templates` directory.
- Platform metadata must reference the shared `skills/nhimc-ui` and shared source; do not duplicate implementations.
- Examples contain only fictional, non-medical data.
- Never report installation success without verification; valid bootstrap outcomes are `READY`, `WEB_BOOTSTRAP`, and `UNSUPPORTED`.
- Do not publish or push to GitHub without an explicit repository destination and publishing instruction. The user confirmed on 2026-09-28 that the supplied logo and font assets may be public; package the Noto Sans KR OFL text and record that confirmation.
- Implement features and fixes test-first with `superpowers:test-driven-development`; verify completion with `superpowers:verification-before-completion`.
- Use `frontend-design:frontend-design` when translating the approved visual direction, `skill-creator` plus `superpowers:writing-skills` for the shared skill, and `plugin-creator` for compatibility metadata while preserving the approved portable root manifest.

## File Map

### Project and contracts

- `VERSION` — canonical project version.
- `CHANGELOG.md` — 1.0.0 release notes and current public-release status.
- `LICENSE` — Apache-2.0 text for newly authored code.
- `NOTICE` — code/font attribution and the recorded public-use status of supplied NHIMC assets.
- `README.md` — usage, support matrix, examples, and release blockers.
- `registry/project.json` — version, defaults, registry locations, and bootstrap statuses.
- `registry/frames.json` — immutable frame contract and protected-file digests.
- `registry/themes.json` — allowed theme token names and theme file.
- `registry/components.json` — reusable component API inventory.
- `registry/assets.json` — asset IDs, roles, paths, media types, and digests.

### Runtime

- `src/frame/menu-model.js` — menu validation and immutable normalization.
- `src/frame/nhimc-frame.js` — `<nhimc-frame>` rendering and interaction.
- `src/frame/nhimc-frame.css` — frame-owned styles and breakpoints.
- `src/themes/nhimc-light.css` — default token values only.
- `src/layouts/primitives.css` — Page, PageHeader, Section, Stack, Grid, FormGrid, Toolbar, FieldGroup, and ContentCard.
- `src/components/components.css` — visual/state styles for registered components.
- `src/components/controllers.js` — tabs, dialog, and dismissible interaction controllers.
- `src/assets/icons/nhimc-icons.svg` — canonical local icon sprite.
- `src/assets/branding/*` — exact public branding assets with protected hashes.
- `src/assets/fonts/*` — local Noto Sans KR files approved by the asset registry.
- `src/assets/fonts/OFL.txt` — full SIL Open Font License.

### Examples and tests

- `examples/operations/index.html` and `app.js` — fictional operations workspace.
- `examples/administration/index.html` and `app.js` — fictional administration workspace with a different menu/content shape.
- `tests/python/test_contracts.py` — registry and version tests.
- `tests/python/test_design_rules.py` — design-system and no-template tests.
- `tests/python/test_public_safety.py` — public-data scanner tests.
- `tests/node/menu-model.test.js` — menu normalization tests.
- `tests/browser/runner.html` and `runner.js` — real DOM, keyboard, responsive, theme, and frame-integrity tests.
- `tests/fixtures/public-safety/*` — deterministic safe and unsafe scanner inputs.

### Tooling, platform adapters, and docs

- `scripts/common.py` — root discovery, JSON loading, hashing, and report types.
- `scripts/update_integrity.py` — explicit protected-file digest refresh for a new frame version.
- `scripts/validate_contracts.py` — registry/version/path validation.
- `scripts/validate_design.py` — token, icon/font, component-reuse, override, and template checks.
- `scripts/validate_public.py` — secret, private-network, internal-URL, and personal-data scan.
- `scripts/run_browser_tests.py` — temporary localhost server plus headless browser runner.
- `scripts/verify_all.py` — one non-release verification entry point.
- `scripts/verify_release.py` — all checks plus public-asset/license completeness gate.
- `bootstrap.md` — environment detection and verified outcomes.
- `plugin.json` — portable ChatGPT/Codex manifest.
- `.codex-plugin/plugin.json` — Codex compatibility manifest.
- `.claude-plugin/plugin.json` — Claude Code manifest.
- `gemini-extension.json` and `GEMINI.md` — Gemini CLI adapter.
- `skills/nhimc-ui/SKILL.md` and `skills/nhimc-ui/references/*` — shared skill and concise contract references.
- `PUBLIC_ASSET_REVIEW.md` — completed public-use and license evidence record.
- `docs/platforms/*.md` — official per-platform install/use instructions.
- `docs/decisions/new-component.md` — required component-admission record format.

## Review Focus

1. Cyclic, duplicate, empty, or malformed menu input must be rejected without breaking the rendered empty frame; Task 3 pins this in Node and browser tests.
2. A missing or altered protected logo/frame file must prevent verified readiness and release; Tasks 2 and 8 pin digest mismatch behavior.
3. Theme CSS that includes a selector other than `:root`/`[data-nhimc-theme="nhimc-light"]` or an unregistered custom property must fail; Task 4 pins both cases.
4. Content that attempts global frame selectors, `::part`, private/internal URLs, or hard-coded design colors must fail with file and rule identifiers; Tasks 6 and 8 pin these scans.
5. Unsupported web-host capability must produce `WEB_BOOTSTRAP` or `UNSUPPORTED`, never `READY`; Task 7 pins the decision table and exact output vocabulary.

---

### Task 1: Establish Versioned Project Contracts

**Files:**
- Create: `VERSION`
- Create: `CHANGELOG.md`
- Create: `LICENSE`
- Create: `NOTICE`
- Create: `registry/project.json`
- Create: `registry/frames.json`
- Create: `registry/themes.json`
- Create: `registry/components.json`
- Create: `registry/assets.json`
- Create: `scripts/common.py`
- Create: `scripts/validate_contracts.py`
- Create: `tests/python/test_contracts.py`

**Interfaces:**
- Consumes: Approved constants from the design spec.
- Produces: `load_json(path: Path) -> dict`, `sha256_file(path: Path) -> str`, `Finding(rule: str, path: str, message: str, blocking: bool)`, `validate_contracts(root: Path) -> list[Finding]`, and stable registry schemas consumed by every later task.

- [ ] **Step 1: Write failing contract tests**

```python
# tests/python/test_contracts.py
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_contracts import validate_contracts

ROOT = Path(__file__).resolve().parents[2]

class ContractTests(unittest.TestCase):
    def test_repository_contract_is_consistent(self):
        self.assertEqual([], validate_contracts(ROOT))

    def test_version_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "registry").mkdir()
            (root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            project = {"projectVersion": "9.9.9", "defaultFrame": "nhimc-default", "defaultTheme": "nhimc-light"}
            (root / "registry/project.json").write_text(json.dumps(project), encoding="utf-8")
            findings = validate_contracts(root)
            self.assertIn("contract.version-mismatch", {item.rule for item in findings})

    def test_missing_registry_reference_is_reported(self):
        findings = validate_contracts(ROOT, required_override=["registry/missing.json"])
        self.assertIn("contract.missing-file", {item.rule for item in findings})
```

- [ ] **Step 2: Run the tests and confirm the expected import failure**

Run: `python -m unittest tests.python.test_contracts -v`  
Expected: FAIL because `scripts.validate_contracts` does not exist.

- [ ] **Step 3: Implement the canonical contract loader and validator**

```python
# scripts/common.py
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

@dataclass(frozen=True, order=True)
class Finding:
    rule: str
    path: str
    message: str
    blocking: bool = True

def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()
```

Create registries with these stable shapes:

```json
{
  "schemaVersion": 1,
  "projectVersion": "1.0.0",
  "defaultFrame": "nhimc-default",
  "defaultTheme": "nhimc-light",
  "bootstrapStatuses": ["READY", "WEB_BOOTSTRAP", "UNSUPPORTED"],
  "registries": ["registry/frames.json", "registry/themes.json", "registry/components.json", "registry/assets.json"]
}
```

`validate_contracts()` must report malformed JSON, missing files, version disagreement, unknown defaults, duplicate IDs, paths escaping the repository, and references to nonexistent files. Empty protected-file digests are allowed only until Task 2 refreshes them and must be reported as warnings rather than omitted.

- [ ] **Step 4: Run contract tests**

Run: `python -m unittest tests.python.test_contracts -v`  
Expected: PASS, including mismatch and missing-file fixtures.

- [ ] **Step 5: Commit the contract foundation**

```powershell
git add VERSION CHANGELOG.md LICENSE NOTICE registry scripts/common.py scripts/validate_contracts.py tests/python/test_contracts.py
git commit -m "feat: establish versioned ui core contracts"
```

### Task 2: Register and Protect Local Assets

**Files:**
- Create: `src/assets/icons/nhimc-icons.svg`
- Create: `src/assets/branding/*`
- Create: `src/assets/fonts/*`
- Create: `src/assets/fonts/OFL.txt`
- Create: `PUBLIC_ASSET_REVIEW.md`
- Create: `scripts/update_integrity.py`
- Modify: `registry/assets.json`
- Modify: `registry/frames.json`
- Modify: `tests/python/test_contracts.py`

**Interfaces:**
- Consumes: `sha256_file()` and frame/asset registry schemas from Task 1; exact source assets from the read-only NhimcDesign tree.
- Produces: `check_integrity(root: Path, entries: list[dict]) -> list[Finding]`, `refresh_integrity(root: Path, frame_id: str, expected_frame_version: str) -> None`, and nonempty SHA-256 values for every protected asset.

- [ ] **Step 1: Add failing asset-integrity tests**

```python
from scripts.common import sha256_file
from scripts.validate_contracts import check_integrity

def test_registered_asset_hashes_match_files(self):
    findings = validate_contracts(ROOT)
    self.assertNotIn("contract.integrity-mismatch", {item.rule for item in findings})
    assets = json.loads((ROOT / "registry/assets.json").read_text(encoding="utf-8"))
    self.assertTrue(all(len(asset["sha256"]) == 64 for asset in assets["assets"]))

def test_changed_asset_is_detected(self):
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        asset = root / "logo.svg"
        asset.write_bytes(b"original")
        entries = [{"path": "logo.svg", "sha256": sha256_file(asset)}]
        asset.write_bytes(b"changed")
        findings = check_integrity(root, entries)
        self.assertEqual(["contract.integrity-mismatch"], [item.rule for item in findings])
        self.assertEqual("logo.svg", findings[0].path)
```

- [ ] **Step 2: Run the focused test and confirm it fails on empty/missing assets**

Run: `python -m unittest tests.python.test_contracts.ContractTests.test_registered_asset_hashes_match_files -v`  
Expected: FAIL because protected assets and hashes are absent.

- [ ] **Step 3: Copy only the approved source candidates and implement explicit digest refresh**

Use `Copy-Item -LiteralPath` from the exact analyzed source paths; do not copy scripts, internal manifests, examples, or generated releases. Preserve SVG/font bytes. `update_integrity.py` must refuse to run unless its `--frame-version` argument exactly matches the registry frame version:

```python
def refresh_integrity(root: Path, frame_id: str, expected_frame_version: str) -> None:
    registry_path = root / "registry/frames.json"
    registry = load_json(registry_path)
    frame = next(item for item in registry["frames"] if item["id"] == frame_id)
    if frame["version"] != expected_frame_version:
        raise ValueError("frame version confirmation does not match registry")
    for protected in frame["protectedFiles"]:
        protected["sha256"] = sha256_file(root / protected["path"])
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
```

`PUBLIC_ASSET_REVIEW.md` must record the user's 2026-09-28 confirmation that the supplied logo and font assets may be public, list every included asset path, document Noto Sans KR/OFL packaging, and contain no unresolved blocking item.

- [ ] **Step 4: Refresh hashes and run integrity tests**

Run: `python scripts/update_integrity.py --frame nhimc-default --frame-version 1.0.0`  
Run: `python -m unittest tests.python.test_contracts -v`  
Expected: PASS; every protected asset has a 64-character digest and byte mutation is detected.

- [ ] **Step 5: Commit protected assets and review record**

```powershell
git add src/assets registry PUBLIC_ASSET_REVIEW.md scripts/update_integrity.py tests/python/test_contracts.py
git commit -m "feat: register protected nhimc assets"
```

### Task 3: Implement the Immutable Frame and Menu Model

**Files:**
- Create: `src/frame/menu-model.js`
- Create: `src/frame/nhimc-frame.js`
- Create: `src/frame/nhimc-frame.css`
- Create: `tests/node/menu-model.test.js`
- Create: `tests/browser/runner.html`
- Create: `tests/browser/runner.js`
- Create: `scripts/run_browser_tests.py`
- Modify: `registry/frames.json`

**Interfaces:**
- Consumes: asset IDs and protected ownership from Task 2.
- Produces: `normalizeMenu(value) -> ReadonlyArray<MenuItem>`, `class NhimcFrame extends HTMLElement`, the `menu` property, `activeId` property, default business-content slot, and bubbling `nhimc:navigate` event with `{id, href}` detail.

- [ ] **Step 1: Write failing Node tests for valid and hostile menu input**

```javascript
// tests/node/menu-model.test.js
import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeMenu } from '../../src/frame/menu-model.js';

test('normalizes and freezes nested menu items', () => {
  const result = normalizeMenu([{ id: 'home', label: 'Home', href: '#home', children: [] }]);
  assert.equal(result[0].id, 'home');
  assert.ok(Object.isFrozen(result));
  assert.ok(Object.isFrozen(result[0]));
});

for (const value of [null, {}, [{ id: '', label: 'X' }], [{ id: 'a', label: 'A' }, { id: 'a', label: 'B' }]]) {
  test(`rejects malformed menu ${JSON.stringify(value)}`, () => {
    assert.throws(() => normalizeMenu(value), { name: 'TypeError' });
  });
}

test('rejects cyclic children', () => {
  const item = { id: 'a', label: 'A', children: [] };
  item.children.push(item);
  assert.throws(() => normalizeMenu([item]), /cyclic/i);
});
```

- [ ] **Step 2: Run Node tests and confirm the module is missing**

Run: `node --test tests/node/menu-model.test.js`  
Expected: FAIL with module-not-found for `menu-model.js`.

- [ ] **Step 3: Implement menu normalization, then the frame shell**

`normalizeMenu()` must accept only arrays; require unique nonempty string `id` and `label`; allow optional `href`, `icon`, and recursive `children`; reject cycles, duplicate IDs, unknown keys, unsafe `javascript:` URLs, and nesting deeper than three levels; clone and deeply freeze the result.

`nhimc-frame.js` must:

```javascript
export class NhimcFrame extends HTMLElement {
  #menu = Object.freeze([]);
  #activeId = '';
  #root = this.attachShadow({ mode: 'open' });

  set menu(value) {
    try {
      this.#menu = normalizeMenu(value);
      this.removeAttribute('data-menu-error');
    } catch (error) {
      this.#menu = Object.freeze([]);
      this.setAttribute('data-menu-error', error.message);
    }
    this.#renderNavigation();
  }

  get menu() { return this.#menu; }
  set activeId(value) { this.#activeId = String(value ?? ''); this.#syncActiveState(); }
  get activeId() { return this.#activeId; }
}

customElements.define('nhimc-frame', NhimcFrame);
```

Render the approved header, left navigation, desktop collapse control, mobile drawer control, status bar, and `<main><slot></slot></main>`. Load frame CSS as a local module string or constructable stylesheet without remote requests. Do not expose `part` attributes or `::part`. Use buttons for controls, update `aria-expanded`, close the mobile drawer on Escape, restore focus, and dispatch `nhimc:navigate` only after a valid menu selection.

- [ ] **Step 4: Add real-browser assertions and the localhost runner**

`runner.html` imports `runner.js`. The script creates a frame, assigns valid menu data, and writes `<meta name="nhimc-test-result" content="PASS">` only after checking:

- custom element registration and slotted content visibility
- no `part` attributes anywhere in the open test-visible shadow tree
- valid menu selection emits one `nhimc:navigate`
- invalid menu results in empty frozen `menu` and `data-menu-error`
- collapse toggles `aria-expanded`
- Escape closes the mobile drawer and restores focus

`run_browser_tests.py` binds `ThreadingHTTPServer` to `127.0.0.1` on an ephemeral port, locates Chrome then Edge in their standard Windows paths, runs `--headless --disable-gpu --dump-dom`, and exits zero only when dumped DOM contains the PASS meta tag. It always shuts down the server in `finally`.

- [ ] **Step 5: Run unit and browser tests**

Run: `node --test tests/node/menu-model.test.js`  
Run: `python scripts/run_browser_tests.py`  
Expected: both PASS; the runner prints the selected browser and `browser: PASS`.

- [ ] **Step 6: Refresh frame hashes and commit**

Run: `python scripts/update_integrity.py --frame nhimc-default --frame-version 1.0.0`  

```powershell
git add src/frame registry/frames.json tests/node tests/browser scripts/run_browser_tests.py
git commit -m "feat: implement immutable nhimc frame"
```

### Task 4: Implement the Registered Theme and Layout Primitives

**Files:**
- Create: `src/themes/nhimc-light.css`
- Create: `src/layouts/primitives.css`
- Create: `scripts/validate_design.py`
- Create: `tests/python/test_design_rules.py`
- Modify: `registry/themes.json`
- Modify: `tests/browser/runner.js`

**Interfaces:**
- Consumes: theme registry schema and the frame's documented token reads.
- Produces: `validate_design(root: Path) -> list[Finding]`, the registered `--nhimc-*` token set, and the nine approved layout classes.

- [ ] **Step 1: Write failing theme and layout rule tests**

```python
# tests/python/test_design_rules.py
import tempfile
import unittest
from pathlib import Path
from scripts.validate_design import validate_design

ROOT = Path(__file__).resolve().parents[2]

def make_minimal_design_root(root: Path) -> Path:
    (root / "src/themes").mkdir(parents=True)
    (root / "registry").mkdir()
    (root / "registry/themes.json").write_text(
        '{"schemaVersion":1,"themes":[{"id":"nhimc-light","file":"src/themes/nhimc-light.css",'
        '"tokens":["--nhimc-color-surface"]}]}\n', encoding="utf-8")
    (root / "src/themes/nhimc-light.css").write_text(
        ':root { --nhimc-color-surface: #ffffff; }\n', encoding="utf-8")
    return root

class DesignRuleTests(unittest.TestCase):
    def test_repository_obeys_design_rules(self):
        self.assertEqual([], validate_design(ROOT))

    def test_theme_rejects_unknown_token_and_selector(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "src/themes/nhimc-light.css").write_text(
                ".business-card { --unknown-color: #fff; }", encoding="utf-8")
            rules = {item.rule for item in validate_design(root)}
            self.assertIn("design.theme-selector", rules)
            self.assertIn("design.unregistered-token", rules)

    def test_templates_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_minimal_design_root(Path(folder))
            (root / "templates").mkdir()
            self.assertIn("design.template-system", {item.rule for item in validate_design(root)})
```

- [ ] **Step 2: Run the test and confirm the validator import fails**

Run: `python -m unittest tests.python.test_design_rules -v`  
Expected: FAIL because `scripts.validate_design` is absent.

- [ ] **Step 3: Implement the token theme, primitives, and CSS validator**

`nhimc-light.css` may contain only `:root` and `[data-nhimc-theme="nhimc-light"]`, declaring the registry's tokens for white surfaces, NHIMC blue, green, amber, red, cyan, violet, text, borders, focus, font, spacing, radii, shadows, and control heights.

`primitives.css` defines only these public classes: `.nhimc-page`, `.nhimc-page-header`, `.nhimc-section`, `.nhimc-stack`, `.nhimc-grid`, `.nhimc-form-grid`, `.nhimc-toolbar`, `.nhimc-field-group`, `.nhimc-content-card`. Responsive behavior uses registered breakpoints/tokens and no business-specific selectors.

`validate_design()` strips CSS comments safely, checks theme selectors and declarations, rejects hex/rgb/hsl values outside registered token/asset files, rejects a directory named `templates`, and reports `Finding` instances with exact relative paths. Tests must cover uppercase hex, whitespace variants, and colors inside comments.

- [ ] **Step 4: Add browser token-replacement assertions**

Extend `runner.js` to load a temporary alternate token value through a test stylesheet, assert the computed component color changes, and assert the protected frame hash/registry text fetched before and after remains identical.

- [ ] **Step 5: Run design and browser tests**

Run: `python -m unittest tests.python.test_design_rules -v`  
Run: `python scripts/run_browser_tests.py`  
Expected: PASS, including hostile selector/token fixtures and theme replacement.

- [ ] **Step 6: Commit theme and primitive contracts**

```powershell
git add src/themes src/layouts registry/themes.json scripts/validate_design.py tests/python/test_design_rules.py tests/browser/runner.js
git commit -m "feat: add token theme and layout primitives"
```

### Task 5: Implement the Reusable Component Set

**Files:**
- Create: `src/components/components.css`
- Create: `src/components/controllers.js`
- Create: `docs/decisions/new-component.md`
- Create: `tests/node/controllers.test.js`
- Modify: `registry/components.json`
- Modify: `tests/browser/runner.html`
- Modify: `tests/browser/runner.js`
- Modify: `tests/python/test_design_rules.py`

**Interfaces:**
- Consumes: theme tokens from Task 4.
- Produces: documented `.nhimc-*` component classes plus `initNhimcComponents(root: ParentNode = document) -> () => void`, returning a cleanup function for event listeners.

- [ ] **Step 1: Add failing component registry and controller tests**

```javascript
// tests/node/controllers.test.js
import test from 'node:test';
import assert from 'node:assert/strict';
import { nextTabIndex } from '../../src/components/controllers.js';

test('tab keyboard navigation wraps', () => {
  assert.equal(nextTabIndex(2, 3, 'ArrowRight'), 0);
  assert.equal(nextTabIndex(0, 3, 'ArrowLeft'), 2);
  assert.equal(nextTabIndex(1, 3, 'Home'), 0);
  assert.equal(nextTabIndex(1, 3, 'End'), 2);
});

test('unhandled key preserves index', () => {
  assert.equal(nextTabIndex(1, 3, 'Enter'), 1);
});
```

Add Python assertions that every component registry entry has a unique ID, selector, states array, accessibility array, token list, implementation path, and example marker; every selector must appear in `components.css`.

- [ ] **Step 2: Run focused tests and confirm missing exports/entries**

Run: `node --test tests/node/controllers.test.js`  
Run: `python -m unittest tests.python.test_design_rules -v`  
Expected: FAIL because controller code and complete registry entries do not exist.

- [ ] **Step 3: Implement registered component CSS and minimal controllers**

Implement Button, Input, Textarea, Select, Checkbox, Radio, Switch, Date Input, Field/message, Search UI, Card, Badge/status, Table, Tabs, Dialog, Pagination, and Icon. Styles cover default, hover, focus-visible, active, disabled, invalid, selected, and busy states where applicable. Use native inputs/buttons/dialog/table elements and visible labels.

`controllers.js` exports pure `nextTabIndex()` plus `initNhimcComponents()`. The initializer installs delegated tab keyboard/click handling, dialog opener/closer handling, Escape behavior, initial focus, and focus restoration. It must not mutate the frame shadow DOM.

`docs/decisions/new-component.md` requires: unmet use case, rejected registered composition, proposed API, accessibility behavior, token use, tests, and registry change. It is a decision-record form, not a page template.

- [ ] **Step 4: Add browser accessibility assertions**

Extend the browser runner with real specimens and assert labels/accessibility names, tab arrow-key wrap, dialog open/close/focus restoration, disabled buttons, invalid field linkage via `aria-describedby`, and reduced-motion CSS behavior through computed styles.

- [ ] **Step 5: Run component, design, and browser tests**

Run: `node --test tests/node/*.test.js`  
Run: `python -m unittest tests.python.test_design_rules -v`  
Run: `python scripts/run_browser_tests.py`  
Expected: PASS.

- [ ] **Step 6: Commit the reusable component library**

```powershell
git add src/components registry/components.json docs/decisions tests/node tests/browser tests/python/test_design_rules.py
git commit -m "feat: add accessible reusable components"
```

### Task 6: Prove Content Flexibility with Two Fictional Applications

**Files:**
- Create: `examples/operations/index.html`
- Create: `examples/operations/app.js`
- Create: `examples/administration/index.html`
- Create: `examples/administration/app.js`
- Modify: `tests/browser/runner.js`
- Modify: `tests/python/test_design_rules.py`

**Interfaces:**
- Consumes: `<nhimc-frame>`, `menu`, `nhimc:navigate`, component classes/controllers, and layout primitives.
- Produces: two independently runnable examples with different menus and content but identical frame source identity.

- [ ] **Step 1: Add failing example-composition tests**

Add this Python test, backed by small helpers that extract stylesheet/module paths and class names with `html.parser.HTMLParser` rather than fragile whole-document regular expressions:

```python
def test_examples_share_frame_without_copying_it(self):
    expected_imports = {
        "../../src/frame/nhimc-frame.js",
        "../../src/themes/nhimc-light.css",
        "../../src/layouts/primitives.css",
        "../../src/components/components.css",
    }
    menus = []
    for name in ("operations", "administration"):
        html_path = ROOT / f"examples/{name}/index.html"
        js_path = ROOT / f"examples/{name}/app.js"
        html = html_path.read_text(encoding="utf-8")
        script = js_path.read_text(encoding="utf-8")
        parsed = parse_example(html)
        self.assertEqual(1, parsed.tags.count("nhimc-frame"), name)
        self.assertTrue(expected_imports.issubset(parsed.references | extract_imports(script)), name)
        self.assertNotIn("<style", html.lower(), name)
        self.assertNotIn("::part", html + script, name)
        self.assertGreaterEqual(count_registered_classes(parsed.classes, ROOT), 7, name)
        menus.append(extract_literal_menu_shape(script))
    self.assertNotEqual(menus[0], menus[1])
```

The helper assertions require both examples to:

- import the same `src/frame/nhimc-frame.js`
- import the same theme, primitive, and component CSS
- contain `<nhimc-frame>` exactly once
- contain no copied `<header>`, navigation shell, inline `<style>`, hard-coded design color, medical record, resident number, real email, or `::part`
- use at least four registered components and three registered primitives
- have different menu JSON shapes

- [ ] **Step 2: Run the example tests and confirm missing files fail**

Run: `python -m unittest tests.python.test_design_rules.DesignRuleTests.test_examples_share_frame_without_copying_it -v`  
Expected: FAIL because the example applications are absent.

- [ ] **Step 3: Build both examples from shared contracts**

The operations example uses fictional queue, task, and service-status data. The administration example uses fictional role, policy, and audit-event data. Each `app.js` assigns its own menu array, listens for `nhimc:navigate`, swaps only slotted business sections, and updates `activeId`. Neither application reaches into the frame implementation.

- [ ] **Step 4: Extend real-browser navigation checks**

Load both example URLs through the existing localhost runner. For each, assert one frame host, expected title, menu navigation event, visible route-specific content, and the same fetched SHA-256 value for `nhimc-frame.js` and protected frame CSS.

- [ ] **Step 5: Run design and browser suites**

Run: `python -m unittest tests.python.test_design_rules -v`  
Run: `python scripts/run_browser_tests.py`  
Expected: PASS for both example applications.

- [ ] **Step 6: Commit the examples**

```powershell
git add examples tests/browser/runner.js tests/python/test_design_rules.py
git commit -m "feat: demonstrate flexible business content"
```

### Task 7: Create the Shared Skill and Six-Environment Adapters

**Files:**
- Create: `skills/nhimc-ui/SKILL.md`
- Create: `skills/nhimc-ui/references/contracts.md`
- Create: `skills/nhimc-ui/references/platform-support.md`
- Create: `bootstrap.md`
- Create: `plugin.json`
- Create: `.codex-plugin/plugin.json`
- Create: `.claude-plugin/plugin.json`
- Create: `gemini-extension.json`
- Create: `GEMINI.md`
- Create: `docs/platforms/chatgpt-codex.md`
- Create: `docs/platforms/claude.md`
- Create: `docs/platforms/gemini.md`
- Create: `tests/python/test_platform_adapters.py`
- Modify: `registry/project.json`

**Interfaces:**
- Consumes: project/registry paths and the verified runtime API.
- Produces: one `nhimc-ui` skill and metadata adapters whose paths remain inside the repository; a deterministic capability table mapping environment/capability to `READY`, `WEB_BOOTSTRAP`, or `UNSUPPORTED`.

- [ ] **Step 1: Read the required creation skills before editing**

Read completely: `skill-creator`, `superpowers:writing-skills`, and `plugin-creator`. Preserve the design's root portable `plugin.json`; use `.codex-plugin/plugin.json` only as compatibility metadata even if the plugin scaffold defaults differ.

- [ ] **Step 2: Write failing platform and bootstrap contract tests**

```python
# tests/python/test_platform_adapters.py
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class PlatformAdapterTests(unittest.TestCase):
    def test_all_manifests_use_version_and_shared_skill(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for path in ["plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json", "gemini-extension.json"]:
            data = json.loads((ROOT / path).read_text(encoding="utf-8"))
            self.assertEqual(version, data["version"], path)
            self.assertNotIn("distribution/", json.dumps(data), path)
        self.assertTrue((ROOT / "skills/nhimc-ui/SKILL.md").is_file())

    def test_bootstrap_uses_only_exact_status_vocabulary(self):
        text = (ROOT / "bootstrap.md").read_text(encoding="utf-8")
        for status in ("READY", "WEB_BOOTSTRAP", "UNSUPPORTED"):
            self.assertIn(status, text)
        self.assertNotIn("INSTALLED", text)

    def test_gemini_web_without_install_capability_is_not_ready(self):
        table = json.loads((ROOT / "registry/project.json").read_text(encoding="utf-8"))["bootstrapMatrix"]
        row = next(item for item in table if item["environment"] == "gemini-web" and not item["persistentInstall"])
        self.assertIn(row["status"], {"WEB_BOOTSTRAP", "UNSUPPORTED"})
```

- [ ] **Step 3: Run tests and confirm manifests/skill are missing**

Run: `python -m unittest tests.python.test_platform_adapters -v`  
Expected: FAIL on missing `plugin.json`.

- [ ] **Step 4: Implement the single shared skill and adapters**

The skill frontmatter name is `nhimc-ui`. Its imperative workflow must: inspect registries; reuse the frame/component sources; never recreate frame/branding; prefer registered components; require a decision record for a new component; validate changes; and report public-release blockers. Keep `SKILL.md` concise and route detail to the two reference files.

`bootstrap.md` contains an explicit decision table:

| Environment | Verified persistent mechanism | Without that mechanism |
|---|---|---|
| ChatGPT Web | portable plugin available and registry checks pass → `READY` | repository context usable → `WEB_BOOTSTRAP` |
| Codex | portable/root or compatibility plugin loaded and checks pass → `READY` | repository context usable → `WEB_BOOTSTRAP` |
| Claude Web | official custom-skill ZIP loaded and checks pass → `READY` | repository context usable → `WEB_BOOTSTRAP` |
| Claude Code | root plugin loaded and checks pass → `READY` | readable checkout → `WEB_BOOTSTRAP` |
| Gemini Web | only an officially exposed compatible loader may yield `READY` | repository context usable → `WEB_BOOTSTRAP`; otherwise `UNSUPPORTED` |
| Gemini CLI | root extension installed, restarted, and checks pass → `READY` | readable checkout → `WEB_BOOTSTRAP` |

No manifest may point outside the repository or contain copied source. Platform docs link only to official installation documentation already identified during design research and state restart/upload/manual steps accurately.

- [ ] **Step 5: Validate the skill and adapters**

Run the validation scripts prescribed by `skill-creator`/`writing-skills`, then run:  
Run: `python -m unittest tests.python.test_platform_adapters -v`  
Expected: all manifest, path, version, skill, and status tests PASS.

- [ ] **Step 6: Commit platform integration**

```powershell
git add skills bootstrap.md plugin.json .codex-plugin .claude-plugin gemini-extension.json GEMINI.md docs/platforms registry/project.json tests/python/test_platform_adapters.py
git commit -m "feat: add shared skill and platform adapters"
```

### Task 8: Enforce Public Safety and Release Blocking

**Files:**
- Create: `scripts/validate_public.py`
- Create: `tests/python/test_public_safety.py`
- Create: `tests/fixtures/public-safety/safe.txt`
- Create: `tests/fixtures/public-safety/private-ip.txt`
- Create: `tests/fixtures/public-safety/secret.txt`
- Create: `tests/fixtures/public-safety/personal-data.txt`
- Create: `tests/fixtures/public-safety/internal-url.txt`
- Create: `scripts/verify_all.py`
- Create: `scripts/verify_release.py`
- Modify: `scripts/validate_contracts.py`
- Modify: `scripts/validate_design.py`

**Interfaces:**
- Consumes: `Finding`, all prior validators, browser runner, and unresolved checklist syntax `- [ ] BLOCKING:`.
- Produces: `scan_public_tree(root: Path) -> list[Finding]`, non-release `verify_all() -> int`, and strict `verify_release() -> int`.

- [ ] **Step 1: Write failing scanner and release-gate tests**

```python
# tests/python/test_public_safety.py
import unittest
from pathlib import Path
from scripts.validate_public import scan_public_tree
from scripts.verify_release import unresolved_release_blockers

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/public-safety"

class PublicSafetyTests(unittest.TestCase):
    def test_safe_fixture_has_no_findings(self):
        self.assertEqual([], scan_public_tree(FIXTURES, include={"safe.txt"}))

    def test_each_unsafe_fixture_reports_its_rule(self):
        expected = {
            "private-ip.txt": "public.private-network",
            "secret.txt": "public.possible-secret",
            "personal-data.txt": "public.personal-data",
            "internal-url.txt": "public.internal-url",
        }
        for filename, rule in expected.items():
            self.assertIn(rule, {f.rule for f in scan_public_tree(FIXTURES, include={filename})})

    def test_asset_review_has_no_unresolved_blocker(self):
        blockers = unresolved_release_blockers(ROOT / "PUBLIC_ASSET_REVIEW.md")
        self.assertEqual([], blockers)
```

- [ ] **Step 2: Run tests and confirm scanner modules are absent**

Run: `python -m unittest tests.python.test_public_safety -v`  
Expected: FAIL because `validate_public.py` and `verify_release.py` do not exist.

- [ ] **Step 3: Implement deterministic public scanning**

Scan publishable text extensions, skip `.git`, generated caches, font binaries, and the unsafe fixture directory during whole-tree scans. Detect RFC1918/loopback/link-local IPs, internal TLD/host markers, high-confidence credential assignments/tokens, email/phone/resident-number patterns, and URL credentials. Allow-list official documentation domains and synthetic `example.com` data. Findings include line number in `path`, rule, redacted evidence category, and blocking severity; never print detected secret text.

Fixtures contain unmistakably synthetic values. `validate_public.py --format text` prints sorted findings; `--format json` emits stable JSON; either returns nonzero for blocking findings.

- [ ] **Step 4: Compose non-release and strict verification entry points**

`verify_all.py` runs Python tests, Node tests, contract/design/public validators, and browser tests, then prints one summary and returns the first nonzero result. It excludes known unsafe fixtures.

`verify_release.py` first requires `verify_all.py` success, then fails if `PUBLIC_ASSET_REVIEW.md` contains any unchecked `BLOCKING` line, required license/notice files are absent, or protected hashes differ. Its failure text must say `RELEASE BLOCKED` and name blocker categories without claiming the implementation tests failed.

- [ ] **Step 5: Run scanner, suite, and expected release block**

Run: `python -m unittest tests.python.test_public_safety -v`  
Expected: PASS.  
Run: `python scripts/verify_all.py`  
Expected: PASS.  
Run: `python scripts/verify_release.py`  
Expected: PASS because the public asset record, Apache-2.0 code license, OFL text, notices, and protected hashes are complete.

- [ ] **Step 6: Commit the enforcement layer**

```powershell
git add scripts tests/fixtures tests/python/test_public_safety.py
git commit -m "feat: enforce public safety and release gates"
```

### Task 9: Finish Documentation, Responsive QA, and Reproducibility

**Files:**
- Create: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `NOTICE`
- Modify: `PUBLIC_ASSET_REVIEW.md`
- Modify: `docs/platforms/*.md`
- Modify: `tests/browser/runner.js`
- Create: `scripts/build_release.py`
- Create: `tests/python/test_release_build.py`

**Interfaces:**
- Consumes: complete validated source tree and strict release blockers.
- Produces: `build_release(root: Path, output: Path) -> Path`, a deterministic public archive that is refused if any release gate fails.

- [ ] **Step 1: Write failing deterministic-build and documentation tests**

```python
# tests/python/test_release_build.py
import tempfile
import unittest
from pathlib import Path
from scripts.build_release import build_release

ROOT = Path(__file__).resolve().parents[2]

class ReleaseBuildTests(unittest.TestCase):
    def test_public_archives_are_byte_reproducible(self):
        with tempfile.TemporaryDirectory() as folder:
            one = build_release(ROOT, Path(folder) / "one.zip")
            two = build_release(ROOT, Path(folder) / "two.zip")
            self.assertEqual(one.read_bytes(), two.read_bytes())
```

Add assertions that README names all six environments, documents the three statuses, links the examples and asset record, includes no unsupported install claim, and distinguishes release readiness from the separate act of publishing to a selected GitHub destination.

- [ ] **Step 2: Run tests and confirm release builder is missing**

Run: `python -m unittest tests.python.test_release_build -v`  
Expected: FAIL because `scripts.build_release` does not exist.

- [ ] **Step 3: Implement deterministic archive generation**

Use Python `zipfile`; sort paths; exclude `.git`, caches, test unsafe fixtures, and previous archives; assign each entry the fixed ZIP timestamp `(2026, 9, 28, 0, 0, 0)` and normalized permission bits. The builder calls the release gate before writing and fails without leaving a partial archive.

- [ ] **Step 4: Complete user-facing documentation**

README covers architecture, five-minute local use, menu example, component/primitives links, theme replacement, integrity rules, validation commands, six-environment support matrix, bootstrap statuses, contribution flow, and publication steps. Changelog records the complete 1.0.0 implementation as unreleased. NOTICE separates Apache-licensed new code, SIL OFL fonts, and the publicly usable supplied NHIMC assets confirmed by the user.

- [ ] **Step 5: Expand browser QA across responsive widths**

Run the same browser assertions at 1440×900, 1024×768, and 390×844 by launching headless Chrome/Edge with `--window-size`. At mobile width assert desktop sidebar is not visually active, drawer trigger is visible, focus remains trapped while dialog is modal, no horizontal document overflow exists, and both examples remain usable.

- [ ] **Step 6: Run complete verification and inspect the examples**

Run: `python scripts/verify_all.py`  
Expected: PASS.  
Run: `python scripts/verify_release.py`  
Expected: PASS.  
Run: `python -m unittest tests.python.test_release_build -v`  
Expected: PASS, including byte-identical public archives.

Serve the repository with `python -m http.server 8765 --bind 127.0.0.1`, inspect both example URLs in Chrome at desktop and mobile sizes, and record no clipping, unreadable contrast, broken focus order, or console error. Stop the server after inspection.

- [ ] **Step 7: Commit documentation and reproducible build tooling**

```powershell
git add README.md CHANGELOG.md NOTICE PUBLIC_ASSET_REVIEW.md docs/platforms tests/browser scripts/build_release.py tests/python/test_release_build.py
git commit -m "docs: finish ui core usage and release guidance"
```

### Task 10: Final Verification and Review

**Files:**
- Modify only files required to fix independently verified findings.

**Interfaces:**
- Consumes: all previous deliverables.
- Produces: a clean, locally verified implementation commit series and an evidence-based release-readiness statement.

- [ ] **Step 1: Invoke completion and review skills**

Read and use `superpowers:verification-before-completion`, then `superpowers:requesting-code-review`. The final reviewer compares the implementation to both the design spec and this plan and checks that the original repositories remain unchanged.

- [ ] **Step 2: Run the full evidence set from a clean worktree**

Run: `git status --short`  
Expected: empty.  
Run: `python scripts/verify_all.py`  
Expected: PASS.  
Run: `git -C C:\Projects\NhimcDesign status --short`  
Expected: identical to its pre-implementation state.  
Run: `git -C C:\Projects\NhimcCore status --short 2>$null`  
Expected: no change if it is a Git worktree; otherwise report that it remains non-Git and untouched.

- [ ] **Step 3: Confirm the release gate truthfully**

Run: `python scripts/verify_release.py`  
Expected: PASS. Do not call the repository public-release-ready if this command fails.

- [ ] **Step 4: Fix any review finding test-first and rerun verification**

For each accepted finding, add a focused failing test to the owning suite, run it to observe failure, make the smallest correction, rerun the focused test, then rerun `python scripts/verify_all.py`.

- [ ] **Step 5: Commit verified review corrections when present**

```powershell
git add --all
git commit -m "fix: address final ui core review"
```

If no correction is needed, do not create an empty commit.

## Completion Evidence

Implementation is complete only when:

- all Python and Node tests pass;
- the real browser suite passes at all three widths;
- frame and protected-asset hashes match registries;
- both fictional applications share one frame and use registered components/primitives;
- all four manifests reference one shared skill/source tree;
- the public scanner reports no publishable-tree findings;
- verification archives are byte-reproducible;
- the original two project paths remain unchanged;
- `verify_release.py` truthfully reports either documented blockers or a clean release gate.

Public GitHub publication is not part of this plan and must not occur without an explicit destination and publishing instruction.
