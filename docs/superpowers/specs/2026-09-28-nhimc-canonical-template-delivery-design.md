# NHIMC Canonical Template and Download Delivery Design

**Date:** 2026-09-28  
**Status:** Approved direction, pending written-spec review  
**Canonical source:** `C:\Projects\NhimcDesign\.agents\skills\nhimc-worktool`  
**Pinned source commit:** `08c45402eece8a7c55afc60385e8671c9f13081a`

## 1. Objective

NHIMC UI Core must generate a visually complete business screen from the canonical Page Template system and return the verified result as a downloadable `index.html`. A user must not receive the small authoring source that still contains `<nhimc-frame>` and lacks embedded Frame, Template, component, logo, icon, and font resources.

The generated file must remain a single offline artifact. It opens directly through `file://`, makes no network or sidecar request, and needs neither the Core repository nor Python after delivery.

## 2. Root Cause

Version 2.0 vendors canonical Frames, the component showcase, icons, logos, and fonts, but omits the canonical Page Template assets and the rules that select and validate them. The omitted source includes:

- `templates/catalog.yaml` and the page-type guidance;
- `assets/templates/list`, `detail`, `form`, `dashboard`, and `admin`;
- content patterns such as PageHeader, SearchFilter, DataTable, PaginationArea, MetricOverview, and FormSection;
- template and deliverable validators.

Consequently an AI can use a few atomic classes such as `btn` and `badge` while inventing the surrounding business layout from plain `div`, `section`, and `article` elements. The Frame may be canonical after building, but the business composition is not.

A second failure exists at the delivery boundary. A web host can correctly classify itself as `WEB_BOOTSTRAP / context-only`, then still attach the 5 KB authoring source when the user asks for a download. That file has no Core CSS or runtime and therefore renders as unstyled HTML. The repository currently documents fail-closed behavior, but it lacks a machine-verifiable final-artifact handoff contract.

## 3. Success Criteria

A release is complete only when all of the following hold:

1. Every selectable canonical Page Template and its catalog contract is in the pinned vendor snapshot.
2. The authoring input selects one registered Template and preserves its required role/component structure.
3. The builder combines canonical Frame and Template content without allowing Template CSS to alter protected Frame regions.
4. The builder rejects unregistered templates, missing required components, bare improvised business layouts, and already-built inputs.
5. The exact delivered file passes the Chrome `file://` offline gate.
6. The deliverable contains a signed-by-content completion manifest that identifies Core version, canonical commit, Frame, Template, theme, and runtime digest.
7. A delivery command or tool returns that exact file with filename `index.html` and MIME type `text/html`.
8. Documentation and platform prompts forbid presenting source HTML, a Library path, a local-only path, or build commands as the completed download.
9. ChatGPT Web reports `READY` only when a callable Builder Bridge can return the verified file. A GitHub URL or repository context alone remains `WEB_BOOTSTRAP / context-only`.

## 4. Canonical Snapshot Expansion

The byte-preserving allowlist is extended with the canonical material required for screen composition:

- `templates/catalog.yaml`;
- `templates/registry.md` and page-type guidance files;
- all selectable files under `assets/templates/`;
- `patterns/registry.md`;
- applicable rules: layout, component selection, states, responsive behavior, accessibility, offline behavior, implementation gate, compliance, and anti-patterns;
- canonical template and deliverable validators used as behavioral references.

`vendor/nhimc-design/upstream.json` records each new file, byte length, SHA-256 digest, media type, and extraction role. Vendored bytes remain opaque and immutable. Core-generated adapters are deterministic derivatives and are never edited as substitute designs.

Snapshot verification dynamically reads the catalog. It asserts that every selectable template asset exists, every asset is allowlisted, every declared required component or pattern is known, and no Frame-owned role enters a content-only Template.

## 5. Authoring Contract

The single authoring boundary remains one `<nhimc-frame>`, but it gains a required Template selection:

```html
<nhimc-frame
  data-frame="left"
  data-template="list-default"
  data-project-title="병원 이송업무 관리"
  data-active-id="transport">
  <main data-nhimc-role="content" data-nhimc-template-root="list-default">
    <!-- canonical Template structure with business text and rows -->
  </main>
</nhimc-frame>
```

The AI selects the Template from the catalog based on the requested page type. It starts from that Template's canonical content root, changes only business text, data, identifiers, menu data, and business behavior, and retains:

- required section order;
- `data-nhimc-role` markers;
- `data-nhimc-component` markers;
- required component set;
- state and responsive contracts;
- table wrappers, form field structure, action placement, and pagination structure.

An authoring input may contain multiple screen panels, but each panel declares its own registered Template and remains bound 1:1 to the navigation manifest. It may not copy Header, Sidebar, Logo, statusbar, mobile Drawer, or other Frame-owned regions.

Legacy unmarked arbitrary business content is rejected instead of being treated as a finished NHIMC screen. This is a deliberate breaking contract and advances Core to version `3.0.0`.

## 6. Template Adapter and CSS Isolation

Template adaptation is separate from Frame adaptation.

1. Read the pinned catalog and selected Template asset.
2. Verify the asset digest and its `content-only` scope.
3. Extract the single `main[data-nhimc-role="content"]` root and its required role/component graph.
4. Extract the Template CSS needed by that content.
5. Rewrite the Template content root to a scoped wrapper inside the canonical Frame content slot.
6. Deterministically scope Template selectors under `[data-nhimc-template-root="<id>"]`.
7. Reject selectors that target Frame-owned roles, classes, IDs, or unscoped global elements after transformation.
8. Merge business values into the verified Template skeleton without accepting authored CSS.

The adapter does not reinterpret the appearance or create new layout CSS. It carries the canonical Template grammar into the Frame while preventing rules from leaking into `.app-shell`, `.sidebar`, `.site-header`, `.main`, `.statusbar`, dialogs owned by the Frame, or responsive navigation.

Frame parity is run before and after Template injection. Any protected-region geometry, computed-style, behavior, or screenshot change fails the build.

## 7. Composition Validation

The builder validates the business content against the selected catalog entry:

- the Template ID exists and is selectable;
- the chosen Frame is in the Template's supported shell list;
- the content root and required roles occur exactly once where required;
- all required components occur and all component IDs are registered;
- structural roles occur in canonical order and nesting;
- atomic controls use canonical markup contracts;
- no authored `<style>`, stylesheet, remote resource, hard-coded color, Frame override, or runtime sidecar exists;
- declared screen states have canonical loading, empty, error, or partial representations where applicable;
- accessible names, labels, captions, focus behavior, and responsive table wrappers satisfy the canonical rules.

Validation reports the missing role/component and selected Template. It never repairs an arbitrary layout silently and never falls back to the component-showcase `.specimen` surface.

## 8. Build and Final Artifact

`scripts/build_single_html.py` performs the full composition in this order:

1. validate Core registries and pinned snapshot;
2. validate the authoring boundary, menu, and Template selection;
3. validate and adapt canonical Template content;
4. render the selected canonical Frame;
5. inject scoped canonical Template CSS and the registered component runtime;
6. embed the complete icon sprite, approved logos, theme, and all six Noto Sans KR faces;
7. embed business behavior as a closed classic script;
8. apply the offline CSP;
9. emit the final completion manifest and runtime digest;
10. validate the completed output before writing it atomically.

The completion manifest is machine-readable and cannot be supplied by authoring input. It contains at least:

- `artifactType: "nhimc-single-html"`;
- Core version;
- full canonical commit;
- Frame and Template IDs;
- theme ID;
- bundle and runtime SHA-256 values;
- `sidecarCount: 0`;
- `verificationRequired: true` so the delivery layer must require a matching external browser receipt.

The browser verifier writes the verified state into a detached receipt next to temporary build output. The delivery layer requires both the artifact digest and matching receipt, then returns only the HTML. The receipt is not delivered as a sidecar.

## 9. Download Delivery Contract

Completion means transferring the verified file, not merely generating it.

On a capable host, the final response must:

1. attach or expose the exact verified `index.html` as a clickable download;
2. identify it as one offline HTML file;
3. avoid attaching authoring source, scripts, CSS, assets, receipts, or README files;
4. avoid claiming completion from a Library entry, code block, filesystem path unavailable to the user, or instructions to run Python later.

Before handoff the delivery adapter reopens the file and confirms its digest, completion manifest, absence of `<nhimc-frame>`, presence of the canonical Frame shell and Template root, embedded fonts, embedded icon/logo assets, and matching browser receipt.

If attachment or file-resource transfer is unavailable, the host must not say that a downloadable final file was created. It reports `context-only` and may provide a non-HTML source snippet for discussion, clearly named as source rather than `index.html`.

## 10. Builder Bridge for Web Hosts

A static GitHub repository cannot execute Python or Chrome in ChatGPT Web. Repository visibility alone therefore cannot make that environment `READY`. Automatic web delivery requires a callable Builder Bridge.

The Bridge exposes one operation with a narrow contract:

```text
build_nhimc_artifact(authoring_html, requested_filename="index.html")
  -> verified text/html file resource + digest + public-safe summary
```

The Bridge runs the same repository builder and exact browser verifier in an isolated worker. It accepts no external URLs, performs no fetch on behalf of the source, limits input/output size and execution time, uses a fresh temporary directory, and removes temporary data after the response. It must not log business HTML or patient-identifying content.

Two transports share the same implementation:

- local CLI/tool transport for Codex, Claude Code, Gemini CLI, and disconnected workstations;
- a deployable Streamable HTTP MCP server for ChatGPT Web or other web hosts.

The MCP server exposes `build_nhimc_artifact` from `/mcp`. A successful tool result contains structured status and digest fields plus an MCP `resource_link` whose media type is `text/html`, filename is `index.html`, and target is an opaque, single-artifact download URL. The download response uses `Content-Disposition: attachment; filename="index.html"`, disables caching, expires promptly, and cannot enumerate other jobs. Failed build or browser verification returns no resource link.

The produced artifact is fully offline even when a web host calls the Bridge. Deployment credentials, hosting, and connection approval are separate operational steps; the repository must not claim ChatGPT Web `READY` until the deployed tool is actually callable and its returned file passes an end-to-end download test.

## 11. Verification Strategy

### 11.1 Snapshot and catalog

- byte-identical sync from the pinned clean source;
- deterministic manifest generation;
- full selectable Template coverage;
- rejection of missing, extra, dirty, or unregistered Template material.

### 11.2 Template adaptation

- one fixture per selectable Template;
- expected role/component graph and required component coverage;
- deterministic scoped CSS;
- rejection of Frame selector leakage;
- rejection of the attached bare-layout pattern that previously produced an unstyled 5 KB file.

### 11.3 Visual and responsive behavior

- canonical Template reference versus adapted content at 1440×900, 1024×768, and 390×844 in light and dark themes;
- protected Frame parity with each Template injected;
- table overflow, filter reflow, action placement, empty/loading/error states, and keyboard focus checks.

### 11.4 Offline and delivery

- exact Chrome `file://` execution with zero network/sidecar requests;
- all font, logo, icon, component, and Template resources present;
- authoring source rejected by the delivery adapter;
- tampered artifact or receipt rejected;
- final attachment filename, MIME type, digest, and bytes match the verified artifact;
- local Bridge and web Bridge contract tests return byte-identical output for identical input.

## 12. Migration and Documentation

The existing operations and administration authoring fixtures migrate from `.specimen` and unstyled `.grid` usage to registered canonical Templates. The downloaded problem case becomes a regression fixture that must fail authoring validation until converted to `list-default` or another appropriate Template.

`bootstrap.md`, `README.md`, `skills/nhimc-ui/SKILL.md`, platform support guidance, manifests, and default prompts state the full lifecycle:

```text
prompt -> canonical Template selection -> authoring validation
-> canonical Frame/Template build -> exact browser verification
-> downloadable index.html handoff
```

They also state that `WEB_BOOTSTRAP / context-only` can discuss or prepare source but cannot attach it as a completed HTML file. The phrase “다운로드할 수 있게 만들었다” is reserved for a response that contains an actual transferable, verified file.

## 13. Delivery Sequence

Implementation proceeds in dependency order:

1. expand and verify the pinned canonical snapshot;
2. add Template registry and generated adapter contracts;
3. add Template-aware authoring validation and migrate fixtures;
4. compose and isolate canonical Template CSS inside canonical Frames;
5. add completion manifest, browser receipt, and fail-closed delivery adapter;
6. add local Builder Bridge and deployable web transport package;
7. update platform bootstrap and download guidance;
8. regenerate the reported 업무관리 screen from the canonical ListPage Template;
9. run full parity, browser, release, reproducibility, public-safety, and end-to-end download gates;
10. publish the feature branch and Pull Request without claiming web `READY` until a deployed Bridge connection is verified.

No phase may solve the issue by adding arbitrary page CSS, copying a Frame into business content, returning the authoring source as `index.html`, or weakening canonical parity.
