---
name: nhimc-ui
description: Use when building or changing an NHIMC-branded web interface that must preserve the registered application frame, branding, theme, components, assets, and public-release contracts.
---

# NHIMC UI

Work from the repository root, two directories above this file.

## Start with contracts

1. Read `registry/project.json` for the version, defaults, and bootstrap status vocabulary.
2. Read `registry/frames.json`, `registry/themes.json`, `registry/components.json`, and `registry/assets.json` before choosing structure or styling.
3. Use the default registered frame implementation. Put business UI in its default content slot and provide navigation through the registered `menu` property and `nhimc:navigate` event.

Do not recreate the header, branding, left navigation, responsive shell, or status bar inside business content. Treat every `protectedFiles` hash as immutable. An intentional frame change requires an explicit version bump, updated integrity data, and full verification.

## Default deliverable: one offline HTML

When the task generates a business screen and does not explicitly request another package format, the deliverable is exactly one file named `index.html` that opens from `file://` without internet access.

1. Author the business markup inside the default `<nhimc-frame>` slot and keep its behavior in one `<script type="module" data-nhimc-business>` block in that HTML.
2. Reference the repository Core only while authoring. Do not hand-copy or rewrite the Frame, Theme, Components, Logo, icons, or fonts.
3. Finalize the same file once with `python scripts/build_single_html.py --input <index.html> --output <index.html>`. The verified builder embeds the registered Core and removes module and relative-resource dependencies. It rejects an already-finalized file; rebuild from the authoring source after changes.
4. Hand off only the resulting `index.html`. A generated `app.js`, stylesheet, image, font, manifest, README, or asset directory means the default artifact contract was not met.
5. Run `python scripts/run_browser_tests.py --standalone-file <index.html>` before claiming the file works offline. This must open the exact deliverable from its arbitrary path with no HTTP server.

Read `references/contracts.md` for the authoring shape and standalone boundary.

## Compose before extending

Reuse registered layout primitives and components first. Keep application-specific markup inside examples or consuming applications. Use theme tokens for visual values; do not hard-code colors outside a registered theme.

If required behavior is genuinely absent, document the decision with `docs/decisions/new-component.md`, register the component, and add contract, accessibility, and browser coverage. Do not create a new frame or parallel sidebar to solve a content-layout problem.

Read `references/contracts.md` before implementation changes. Read `references/platform-support.md` when loading or reporting host support.

## Verify claims

Run `python scripts/verify_all.py` before declaring repository work complete. Run `python scripts/verify_release.py` before declaring a public artifact releasable. Report host readiness only after the relevant adapter is loaded and its checks pass; repository files alone do not prove host installation.
