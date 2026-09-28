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

## Compose before extending

Reuse registered layout primitives and components first. Keep application-specific markup inside examples or consuming applications. Use theme tokens for visual values; do not hard-code colors outside a registered theme.

If required behavior is genuinely absent, document the decision with `docs/decisions/new-component.md`, register the component, and add contract, accessibility, and browser coverage. Do not create a new frame or parallel sidebar to solve a content-layout problem.

Read `references/contracts.md` before implementation changes. Read `references/platform-support.md` when packaging, loading, or reporting host support.

## Verify claims

Run `python scripts/verify_all.py` before declaring repository work complete. Run `python scripts/verify_release.py` before declaring a public artifact releasable. Report host readiness only after the relevant adapter is loaded and its checks pass; repository files alone do not prove host installation.
