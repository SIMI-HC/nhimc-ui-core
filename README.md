# NHIMC UI Core

NHIMC UI Core is a source-first application frame and design system for NHIMC-branded web tools. It packages one protected responsive shell, versioned registries, a token theme, reusable components, approved assets, examples, validation gates, and a shared AI implementation Skill.

## Architecture

- `registry/` is the machine-readable contract for the project, frame, theme, components, and assets.
- `src/frame/` owns branding, header, navigation, status, responsive breakpoints, and the business-content slot.
- `src/themes/nhimc-light.css` declares every visual token; components and layouts consume those tokens.
- `src/components/` and `src/layouts/primitives.css` provide reusable UI building blocks.
- `skills/nhimc-ui/` teaches supported agents to inspect and preserve these contracts.

Business applications configure `<nhimc-frame>` and place their own markup in its default slot. They must not copy the header or sidebar.

## Five-minute local use

No package install or build step is required. Python 3, Node.js, and Chrome or Edge are used only for verification.

```powershell
python -m http.server 8765 --bind localhost
```

Open `http://localhost:8765/examples/operations/` or `http://localhost:8765/examples/administration/`. The examples intentionally use different menu trees and business content while sharing the exact frame and components.

```html
<nhimc-frame id="app-frame">
  <main class="nhimc-page">Business content</main>
</nhimc-frame>
<script type="module">
  import './src/frame/nhimc-frame.js';
  const frame = document.querySelector('#app-frame');
  frame.menu = [{ id: 'home', label: 'Home', href: '#home' }];
  frame.addEventListener('nhimc:navigate', ({ detail }) => {
    location.hash = detail.href;
  });
</script>
```

Review [registered components and their canonical markup](registry/components.json), [layout primitives](src/layouts/primitives.css), and the two complete examples at [examples/operations](examples/operations/) and [examples/administration](examples/administration/). Load `src/themes/nhimc-fonts.css`, `src/themes/nhimc-light.css`, and `src/layouts/application.css` before application content.

## Themes and integrity

Replace appearance by supplying the registered custom properties from `registry/themes.json`; do not edit or override frame internals. New tokens belong in a versioned theme contract. Files listed in `protectedFiles` are immutable at a given frame version. An intentional change requires a version bump and:

```powershell
python scripts/update_integrity.py --frame nhimc-default --frame-version 1.0.0
```

Run the full implementation gate and the stricter public-release gate:

```powershell
python scripts/verify_all.py
python scripts/verify_release.py
```

The public asset decision, including the supplied NHIMC logo and bundled Noto Sans KR fonts, is recorded in [PUBLIC_ASSET_REVIEW.md](PUBLIC_ASSET_REVIEW.md).

## Agent platform support

`READY` means the host has a supported persistent loading path and passes its readiness checks. `WEB_BOOTSTRAP` is session-scoped context that must be repeated. `UNSUPPORTED` means the host cannot load the repository or shared Skill. A manifest in this repository is not proof that a user has loaded it.

| Environment | Verified persistent path | Fallback |
| --- | --- | --- |
| ChatGPT Web | plugin loaded → `READY` | repository context → `WEB_BOOTSTRAP`; otherwise `UNSUPPORTED` |
| Codex | root/compatibility plugin loaded → `READY` | readable checkout → `WEB_BOOTSTRAP`; otherwise `UNSUPPORTED` |
| Claude Web | Skill uploaded → `READY` | repository context → `WEB_BOOTSTRAP`; otherwise `UNSUPPORTED` |
| Claude Code | plugin loaded → `READY` | readable checkout → `WEB_BOOTSTRAP`; otherwise `UNSUPPORTED` |
| Gemini Web | no persistent path declared | repository context → `WEB_BOOTSTRAP`; otherwise `UNSUPPORTED` |
| Gemini CLI | extension installed and restarted → `READY` | readable checkout → `WEB_BOOTSTRAP`; otherwise `UNSUPPORTED` |

See [bootstrap.md](bootstrap.md) and `docs/platforms/` for exact host checks.

## Contributing and releases

Start with the registries, reuse the default frame and registered components, add tests before implementation, and document any genuinely new component with `docs/decisions/new-component.md`. Keep protected hashes and all manifests aligned with `VERSION`.

Create a reproducible archive only after the release gate passes:

```powershell
python scripts/build_release.py release/nhimc-ui-core-1.0.0.zip
```

Publishing is a separate action. A passing archive is release-ready locally, but it is not published until a maintainer selects a GitHub destination and performs that external action.
