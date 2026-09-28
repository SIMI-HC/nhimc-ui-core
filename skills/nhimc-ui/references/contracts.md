# Contract map

All paths are relative to the repository root.

- `registry/project.json`: project version, default frame/theme, bootstrap vocabulary and matrix.
- `registry/frames.json`: the `nhimc-default` custom element, content slot, menu property/event, owned shell regions, and protected hashes.
- `registry/themes.json`: the `nhimc-light` token stylesheet, local font-face stylesheet, and registered custom-property tokens.
- `registry/components.json`: reusable selectors, states, accessibility requirements, token dependencies, and implementations.
- `registry/assets.json`: publishable asset paths, licenses, and integrity hashes.
- `src/layouts/primitives.css`: reusable content-layout primitives.
- `scripts/build_single_html.py`: validates Core contracts and bundles an authored business page into one offline `index.html`.

Invariants:

1. Business content may configure the frame but may not copy or own frame regions.
2. Menu data must satisfy the frame schema: unique identifiers, safe URLs, acyclic nesting, and no more than the registered maximum depth.
3. Component behavior must preserve native semantics, keyboard operation, visible focus, and reduced-motion handling.
4. New visual values belong in a registered theme token; component and frame CSS consume tokens.
5. Changing a protected file without a versioned contract and refreshed hash is a failure.
6. A generated business screen defaults to one offline `index.html`. The builder, not the agent, embeds registered Core CSS, scripts, SVG assets, and WOFF2 fonts. The final artifact has no sidecar files, module imports, relative runtime URLs, or network dependency.

Authoring HTML may temporarily reference repository styles and modules so it remains reviewable. Keep page behavior in a `data-nhimc-business` module block, then run the single-HTML builder in place. Verify that exact output with `python scripts/run_browser_tests.py --standalone-file <index.html>`. Do not manually edit the embedded Core block after building.
