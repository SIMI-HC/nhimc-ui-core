# NHIMC UI Core Design Specification

**Date:** 2026-09-28  
**Status:** Approved for implementation planning  
**Project version:** 1.0.0  
**Frame version:** 1.0.0

## 1. Purpose

NHIMC UI Core is a public, reusable UI foundation extracted from the actual source of the existing NHIMC Worktool / Design System project. It provides one stable NHIMC application frame, a replaceable theme, reusable UI components, layout primitives, and platform adapters for ChatGPT Web, Claude Web, Gemini Web, Codex, Claude Code, and Gemini CLI.

The new project lives at `C:\Projects\nhimc-ui-core`. The source projects at `C:\Projects\NhimcDesign` and `C:\Projects\NhimcCore` remain unchanged.

## 2. Source Findings

The source of truth analyzed for extraction is:

`C:\Projects\NhimcDesign\.agents\skills\nhimc-worktool`

Relevant findings:

- The current default frame is `left-sidebar:v2`, implemented in `assets/layouts/left.html` as self-contained HTML, CSS, and JavaScript.
- The frame owns the application shell, header, branding, navigation position, sidebar dimensions and behavior, footer/status area, content boundary, responsive behavior, mobile drawer, and motion.
- The source component catalog documents many reusable components, while the actual local specimens are primarily static HTML/CSS/JavaScript in `assets/components/showcase.html`. External React/shadcn paths referenced by the catalog are not present and must not be represented as existing implementations.
- The canonical icon source is `assets/icons/nhimc-icons.svg`.
- Existing distribution scripts duplicate the source into platform-specific trees. The new project must instead retain one source and use thin adapters.
- The source contains internal network configuration and private IP references. None may be copied into the public project.
- Official logo assets are present, but the source does not contain sufficient public redistribution or CI/BI usage evidence. Public release must remain blocked until this is reviewed.
- Noto Sans KR is identified as SIL Open Font License material, but the license text must be included explicitly in the new project.

## 3. Design Principles

1. **Frame is implementation, not guidance.** Consumers use the supplied frame implementation instead of recreating it.
2. **A frame version is immutable.** Any intentional frame change creates a new frame version.
3. **Branding is immutable within a frame version.** Logo assets, favicon, icon registry, placement, and protected dimensions are integrity checked.
4. **Themes are replaceable.** A theme may change design tokens but cannot change frame structure, branding, or frame-owned dimensions.
5. **Reuse precedes creation.** Existing registered components must be used before adding a new component.
6. **Business content remains flexible.** Applications own menu data, routing, and slotted business content.
7. **No template system.** The project provides primitives and examples, not page templates or business-screen generators.
8. **One source, thin adapters.** Platform integration never forks the UI implementation.
9. **No unverified installation claims.** Bootstrap status reflects what was actually detected and verified.
10. **Public by construction.** Internal infrastructure, secrets, and personal data are rejected by validation.

## 4. Runtime Architecture

The runtime is a zero-dependency Web Standards implementation:

- Custom Element for the application frame
- Shadow DOM for frame isolation
- Semantic HTML and CSS for components
- CSS custom properties for themes
- Small JavaScript controllers only where interaction requires them
- No React, Vue, build-time framework, package runtime, CDN, or external icon dependency

This makes the same implementation usable in generated static pages, existing web applications, CLI-assisted projects, and web-agent workflows.

### 4.1 Frame

The default frame is registered as `nhimc-default` and implemented as `<nhimc-frame>`.

It is extracted from the behavior and visual contract of `left-sidebar:v2`. The frame owns:

- Header and NHIMC branding
- Left navigation shell
- Sidebar collapse and expansion
- Mobile drawer behavior
- Status bar
- Responsive breakpoints
- Content boundary and scroll ownership
- Frame spacing and protected dimensions
- Theme-link location
- Canonical logo, favicon, and icon use

The Shadow DOM deliberately exposes no `::part` hooks. Consumers receive a default slot for business content but cannot reach into the frame DOM through supported styling APIs.

Menu data is assigned as a JavaScript property containing a validated array. User selection dispatches `nhimc:navigate`; routing remains the host application's responsibility. Frame code does not contain business routes.

The frame registry records the frame ID, frame version, implementation files, protected asset hashes, owned behaviors, supported menu schema, content slot, and compatibility information.

### 4.2 Theme

The initial theme is `nhimc-light`:

- White base surface
- NHIMC blue primary family
- Green, amber, red, cyan, and violet secondary/status families
- Typography, spacing, radius, shadow, control height, focus, and state tokens

Themes are CSS custom-property sets registered in the theme registry. Theme files may supply token values only. They cannot redefine frame markup, frame-owned dimensions, logo geometry, navigation behavior, or breakpoint logic.

Hard-coded design colors outside approved token and asset files are validation failures, except for explicitly allow-listed browser/system values.

### 4.3 Components

The initial common component set is:

- Button
- Input and Textarea
- Select
- Checkbox
- Radio
- Switch
- Date Input
- Field and validation message
- Search UI
- Card
- Badge and status indicator
- Table
- Tabs
- Modal/Dialog
- Pagination
- Icon

Each registry entry defines its public markup or controller API, states, accessibility requirements, token dependencies, implementation location, and examples.

Adding a component requires evidence that the need cannot be met by an existing component or composition. Applications must not create local look-alike copies of registered components.

### 4.4 Layout Primitives

The project provides CSS-only layout primitives:

- Page
- PageHeader
- Section
- Stack
- Grid
- FormGrid
- Toolbar
- FieldGroup
- ContentCard

These primitives constrain spacing and responsive composition without dictating business content. There is no `templates` directory and no prescribed dashboard, form, list, or detail page template.

## 5. Branding and Assets

Approved runtime assets are referenced through an asset registry containing stable IDs, paths, media types, roles, and SHA-256 digests.

Logo and favicon files are exact extracted assets, not redrawn approximations. Canonical icons come from the NHIMC SVG sprite, with no runtime third-party icon library.

Before a public GitHub release:

- NHIMC logo redistribution and public CI/BI usage must be documented.
- `PUBLIC_ASSET_REVIEW.md` must contain no unresolved blocking item.
- The complete Noto Sans KR OFL text and attribution must be included.
- Any asset without a documented public license must be removed or replaced through an approved decision.

Local development may retain blocked assets solely for review, clearly marked as not yet approved for public release.

## 6. Repository Structure

```text
nhimc-ui-core/
├── VERSION
├── CHANGELOG.md
├── LICENSE
├── README.md
├── bootstrap.md
├── plugin.json
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── gemini-extension.json
├── skills/nhimc-ui/SKILL.md
├── src/
│   ├── frame/
│   ├── components/
│   ├── layouts/
│   ├── themes/
│   └── assets/
├── registry/
├── examples/
├── scripts/
├── tests/
└── docs/
```

Platform-specific metadata points to the same `skills/nhimc-ui` and source directories. Generated release archives may be created for convenience, but no platform directory contains a copied implementation.

## 7. Platform Integration

### 7.1 ChatGPT and Codex

The repository root contains the portable `plugin.json`. `.codex-plugin/plugin.json` exists only as a compatibility adapter. The shared skill resides under `skills/nhimc-ui`.

### 7.2 Claude Code and Claude Web

`.claude-plugin/plugin.json` treats the repository root as the plugin root and references the shared skills directory. Claude Web documentation describes the official custom-skill ZIP upload flow where available. It does not claim that a GitHub URL was installed automatically.

### 7.3 Gemini CLI and Gemini Web

`gemini-extension.json` is located at repository root and references shared project content. Gemini CLI documentation uses the official GitHub extension installation flow and notes restart requirements.

Gemini Web is treated as capability-dependent. If a compatible official skill or extension installation path cannot be verified, bootstrap selects web-context mode rather than inventing an installation step.

## 8. Bootstrap Contract

`bootstrap.md` is the public entry point. It performs or instructs the following sequence:

1. Detect the active environment and supported capabilities.
2. Select the official install/activation path for that environment.
3. Request user action only for UI or security boundaries that cannot be crossed programmatically.
4. Load and verify project, frame, component, theme, and asset registries.
5. Confirm version agreement and required file integrity.
6. Report exactly one outcome:
   - `READY`: installed or loaded and verified
   - `WEB_BOOTSTRAP`: usable from repository context without persistent installation
   - `UNSUPPORTED`: the required capability is not available

Bootstrap must not modify an existing application until the user asks it to adopt NHIMC UI Core. It must not claim `READY` solely because files were downloaded.

## 9. Validation and Testing

The project uses dependency-free validation, implemented with Python's standard library and browser-native JavaScript where needed.

### 9.1 Structural Validation

- Validate JSON and registry schemas.
- Confirm all manifests and registries agree on project and frame versions.
- Confirm every referenced source and asset exists.
- Reject copied platform implementations.
- Reject a template system or template directory.

### 9.2 Frame Integrity

- Hash immutable frame implementation files and protected branding assets.
- Detect supported override paths into frame DOM, protected dimensions, or branding.
- Verify menu data is dynamic and business routing is not embedded in the frame.
- Render two materially different fictional business examples against the same frame and confirm the same frame identity/hash.

### 9.3 Design-System Validation

- Detect hard-coded colors outside allowed files.
- Detect unregistered fonts and icons.
- Detect local reimplementations of registered components in examples.
- Verify theme replacement changes token values without changing frame integrity.
- Enforce the new-component decision record.

### 9.4 Public-Safety Validation

- Detect likely secrets and credentials.
- Detect private IP addresses and internal hostnames/URLs.
- Detect email, phone, resident/identity-number, and similar personal-data patterns in publishable files.
- Use fixtures to prove both positive and negative detection behavior.
- Produce a human-readable report without automatically deleting or rewriting findings.
- Treat approved public documentation URLs and clearly fictional test fixtures through explicit allow lists.

### 9.5 Accessibility and Interaction

- Use semantic controls and native dialog behavior where supported.
- Verify keyboard operation, focus visibility, labels, accessible names, and status announcements.
- Verify sidebar, drawer, tabs, modal, and menu interactions at desktop and mobile widths.
- Avoid animation when `prefers-reduced-motion` requests it.

## 10. Error Handling

Runtime and bootstrap failures are explicit and recoverable:

- Invalid menu entries are rejected with actionable validation messages; the frame remains rendered with safe empty navigation.
- Missing optional assets fall back only when a registered, approved fallback exists.
- Missing protected assets or integrity mismatches prevent `READY` status.
- Unsupported platform capability results in `WEB_BOOTSTRAP` or `UNSUPPORTED`, never a simulated success.
- Validation tools return non-zero exit codes and identify the file, rule, and remediation category.
- Public-release validation distinguishes blocking findings from warnings.

## 11. Example Content

Examples use fictional, non-medical business content and synthetic names/data. At least two examples exercise distinct menu shapes and content compositions while sharing the exact frame implementation. Examples demonstrate primitives and registered components, not reusable page templates.

## 12. Versioning and Change Control

- Semantic versioning applies to the project.
- Frame versions are independently recorded and immutable after release.
- A frame behavior, structure, protected dimension, or branding change requires a new frame version.
- Theme token additions that preserve existing contracts may be backward compatible.
- Component API changes follow semantic versioning and include migration notes.
- Release notes identify project, frame, component-registry, and theme-registry changes.

## 13. Release Gate

A public release is permitted only when:

1. All automated validation and tests pass.
2. Frame and branding hashes match the registry.
3. Platform manifests pass their format and path checks.
4. No private infrastructure, secret, or personal-data finding remains.
5. All public asset licensing blockers are resolved.
6. Examples contain only fictional data.
7. The generated release is reproducible from the single repository source.

Publishing or pushing to GitHub is a separate external action. It requires a selected repository destination and confirmed public-asset clearance; this specification does not authorize publishing by itself.

## 14. Non-Goals

- Rebuilding the original NHIMC Design project
- Modifying the existing source repositories
- Providing a React/Vue-specific component library in version 1.0
- Shipping business routing, application state, or backend integration
- Creating page templates or a screen generator
- Claiming official platform installation features that cannot be verified
- Publishing NHIMC branding before rights are confirmed

## 15. Acceptance Criteria

The design is successfully implemented when a consumer can load one canonical frame, replace its registered theme, supply arbitrary validated menu data, compose two different business screens from common components and primitives, and verify that the frame and branding remain unchanged. The same repository source must be consumable through documented adapters on all six target environments, with honest fallback status where persistent installation is unavailable.
