# NHIMC Canonical Vendor Sync Design

**Date:** 2026-09-28  
**Status:** Approved design, pending implementation plan  
**Canonical source:** `C:\Projects\NhimcDesign\.agents\skills\nhimc-worktool`  
**Pinned source commit:** `08c45402eece8a7c55afc60385e8671c9f13081a`

## 1. Objective

NHIMC UI Core must stop approximating the NHIMC Worktool design system. It will vendor the approved canonical UI resources from `NhimcDesign`, preserve them as immutable source snapshots, and build offline single-file business screens from those snapshots.

Success means that Frame geometry and behavior, themes, components, logos, icons, and fonts originate from the canonical files rather than a manually rewritten substitute. AI-generated output owns only business content, menu data, project-specific labels, and business behavior.

## 2. Root Cause Being Corrected

The current Core copied the font files and the semantic contents of the logo and icon SVGs, but manually recreated the Frame, theme, and a reduced component set. Its integrity tests lock the recreated Core files without comparing them to `NhimcDesign`. Consequently, a self-consistent but noncanonical Frame passes every existing test.

Examples of current drift include different sidebar, collapsed sidebar, header, and mobile drawer dimensions; missing canonical medical decoration, help panel, and dark-mode controls; text glyphs in place of canonical SVG controls; ignored menu icon values; and only 18 registered Core components compared with the canonical component catalog.

## 3. Source and Ownership Boundaries

`NhimcDesign` remains the design-system source of truth. NHIMC UI Core owns distribution, deterministic adaptation, offline bundling, and verification.

The Core repository must not require `NhimcDesign` at runtime or when an end user opens a generated file. A pinned, reviewed snapshot is stored inside Core so that generation and final artifacts work without internet access and without the original repository.

Vendored files are immutable inputs. Generated adapters and bundles may transform them deterministically, but developers and AI agents must not hand-edit the vendored snapshot or recreate its visuals independently.

## 4. Vendored Canonical Scope

The sync process imports the complete public UI asset set needed to reproduce the Worktool design system, rather than selecting a small baseline subset.

### 4.1 Frames

All canonical layout documents are included:

- `assets/layouts/left.html`
- `assets/layouts/left-blank.html`
- `assets/layouts/top.html`
- `assets/layouts/top-left.html`
- `assets/layouts/presentation.html`
- `assets/layouts/presentation-vertical.html`
- `assets/layouts/blog.html`

`left.html` remains the default business Frame. The other canonical Frames are available through an explicit frame selection and are never reconstructed from the default Frame.

### 4.2 Components and composition contracts

The following canonical sources are included as complete directories or files, not a selected subset:

- `assets/components/showcase.html`
- `components/`
- `patterns/`
- `rules/`
- `tokens/`
- `templates/` contracts

All 49 component entries in the pinned canonical registry are represented in Core. Core must not silently reduce the catalog to its current 18 entries. Static specimens remain specimens; interactive behavior is imported or deterministically extracted from the canonical showcase instead of being redesigned.

### 4.3 Brand, icons, and fonts

The sync includes:

- every approved logo SVG in `docs/design-docs/assets/logo/`
- the logo catalog
- `assets/icons/nhimc-icons.svg` in full
- `docs/design-docs/assets/fonts.css`
- all six Noto Sans KR WOFF2 files
- the applicable font license and public-asset approval record

Text assets are copied byte-for-byte and protected from Git line-ending conversion. Font binaries are copied byte-for-byte. SVG optimization, redraw, path rewriting, and icon substitution are prohibited.

### 4.4 Explicit exclusions

The sync uses an allowlist. It excludes business examples, screen-specific records, personal information, credentials, internal hosts and IP addresses, build output, temporary files, private baseline documents, and unrelated distribution copies. Public-safety validation runs before any synced snapshot can be accepted.

## 5. Repository Structure

The target structure is:

```text
vendor/nhimc-design/
  upstream.json
  layouts/
  components/
  icons/
  branding/
  fonts/
  tokens/
  patterns/
  rules/
src/generated/
  frame/
  components/
  themes/
scripts/
  sync_nhimc_design.py
  verify_nhimc_design_sync.py
```

`upstream.json` records the source repository commit, logical source root, every imported source path, destination path, byte length, SHA-256 digest, media type, and extraction role. Local absolute paths are never published in runtime code or generated artifacts.

`.gitattributes` marks vendored canonical text as `-text` so clones do not rewrite CRLF/LF bytes and invalidate provenance.

## 6. Synchronization Workflow

`scripts/sync_nhimc_design.py` accepts an explicit `--source` path and performs the following operations:

1. Confirm that the source is a Git worktree and record its exact commit.
2. Require a clean source worktree for all allowlisted files.
3. Resolve only allowlisted canonical paths inside the declared source root.
4. Run public-safety validation before copying.
5. Copy approved files as bytes into a temporary staging directory.
6. Generate `upstream.json` and deterministic adapters in staging.
7. Validate completeness, provenance, component coverage, and runtime contracts.
8. Replace the prior snapshot atomically only after all checks pass.

Normal Core builds do not invoke this sync and do not need `NhimcDesign`. Updating the canonical snapshot is an explicit maintainer action followed by review and a Core version change.

## 7. Runtime Adaptation

The canonical documents contain sample menu and content data, while Core must accept business-specific data. Adaptation is therefore restricted to named ownership boundaries:

- project title
- menu manifest and active route
- main content slot
- status text and state
- optional frame selection and theme selection

Everything outside those boundaries remains canonical, including Shell DOM, CSS, dimensions, responsive breakpoints, medical decoration, brand placement, icon paths, help UI, theme UI, Drawer behavior, focus behavior, and motion behavior.

Adapters operate on stable `data-nhimc-role` markers and verified anchors. An expected anchor occurring zero or multiple times is a build error. The adapter may not use a separately authored replacement stylesheet or alternate Frame markup.

The existing authoring input may continue to use a single `<nhimc-frame>` boundary for AI simplicity. During finalization, the builder extracts only the business-owned values and replaces that authoring boundary with the selected canonical Frame. The delivered file is canonical Frame markup, not the current hand-written Custom Element implementation.

## 8. Components and Icons in Generated Screens

The generated component bundle comes from the canonical registry and showcase. It includes the complete canonical component styles and shared controllers so any registered component can be used without sidecar files.

AI screen generation selects markup from the canonical registry instead of inventing lookalike classes. Unsupported custom components fail validation unless added to `NhimcDesign` first and resynced.

Menu items preserve their canonical icon identifiers. The Frame renders the requested symbol from the complete canonical SVG sprite. Control icons such as menu, panel-left, help-circle, sun, moon, and x use their canonical SVG paths; Unicode substitutes are forbidden.

## 9. Single-HTML Build

`build_single_html.py` continues to produce exactly one offline HTML artifact. The revised builder:

1. validates the business-owned authoring input;
2. selects an immutable canonical Frame snapshot;
3. injects only approved project, menu, content, status, and theme values;
4. embeds the canonical component bundle;
5. embeds the complete icon sprite;
6. embeds the selected canonical logos and favicon;
7. converts all six canonical fonts to data URLs;
8. applies the offline CSP and removes all remaining runtime file and network references;
9. records the Core version, Frame ID, upstream commit, and snapshot digest in metadata.

The final artifact must open through `file://`, require no repository or server, and make no network or sidecar request.

## 10. Verification

### 10.1 Provenance and completeness

- Every allowlisted canonical source has a matching vendored file and digest.
- No unlisted file enters the snapshot.
- Logo, icon, font, layout, component, token, pattern, and rule counts are asserted.
- Vendored bytes and `upstream.json` must be reproducible from the pinned clean source commit.

### 10.2 Canonical parity

Browser tests compare the vendored canonical layout with the generated Core result at 1440×900, 1024×768, and 390×844 in both light and dark modes. They compare:

- Shell region presence and order
- computed dimensions and geometry
- computed colors, type, borders, radii, and spacing
- logo and SVG path identity
- menu, collapse, help, theme, mobile Drawer, statusbar, scrolling, and focus behavior
- canonical responsive transitions

Frame-region screenshots are captured under the same browser, viewport, content, font state, and motion settings. A visual difference outside explicitly masked business-content and dynamic-text regions fails the parity test.

### 10.3 Component coverage

- Every canonical registry component has a Core catalog entry.
- Every entry resolves to canonical markup, style, and declared behavior.
- Canonical specimens render without missing assets or runtime errors.
- Generated business fixtures use registered components and canonical icon identifiers.

### 10.4 Offline artifact

The exact delivered file is opened through `file://` and must pass startup-error, missing-font, missing-logo, missing-icon, external-resource, sidecar-navigation, and network-request checks in all three viewport classes.

## 11. Failure Handling

All synchronization and build paths fail closed.

- Missing or dirty source files prevent sync.
- A source commit or digest change requires an explicit snapshot update.
- Missing anchors or ambiguous extraction boundaries prevent adapter generation.
- Public-safety findings prevent copy and identify only the affected rule and path.
- Missing canonical registry coverage prevents release.
- Canonical parity differences prevent release.
- A host that cannot execute the builder and exact-artifact verifier may load documentation but may not claim a deliverable is complete.

No failure mode falls back to the current approximate Frame or to invented UI.

## 12. Versioning and Migration

Replacing the protected Frame and expanding the component contract is a breaking Core change. The project version and protected Frame version advance together from `1.0.0` to `2.0.0`. The upstream commit and snapshot digest become part of the release identity.

The current hand-authored Frame, reduced component registry, and approximate theme are removed after the canonical adapter passes parity tests. Compatibility is retained only at the AI authoring boundary where it does not alter the delivered canonical Frame.

Existing internal fixtures are rewritten as minimal business inputs and are never used as visual references. README, bootstrap, Skill, platform adapters, release notes, and registry contracts describe the canonical vendored architecture and the single-HTML workflow.

## 13. Delivery Sequence

Implementation proceeds in dependency order:

1. provenance manifest, allowlist, byte-preserving sync, and public-safety gate;
2. brand, icon, font, token, and Frame snapshot import;
3. canonical Frame adapter and parity verification;
4. full component registry and component runtime import;
5. single-HTML builder integration;
6. authoring fixtures, platform guidance, release validation, and migration cleanup.

No approximate Frame is published during migration. The existing release remains the last usable version until all canonical parity and offline checks pass together.
