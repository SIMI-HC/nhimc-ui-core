# Contract map

All paths are relative to the repository root.

- `registry/project.json`: project version, default frame/theme, bootstrap vocabulary and matrix.
- `registry/frames.json`: the `nhimc-default` custom element, content slot, menu property/event, owned shell regions, and protected hashes.
- `registry/themes.json`: the `nhimc-light` stylesheet and registered custom-property tokens.
- `registry/components.json`: reusable selectors, states, accessibility requirements, token dependencies, and implementations.
- `registry/assets.json`: publishable asset paths, licenses, and integrity hashes.
- `src/layouts/primitives.css`: reusable content-layout primitives.

Invariants:

1. Business content may configure the frame but may not copy or own frame regions.
2. Menu data must satisfy the frame schema: unique identifiers, safe URLs, acyclic nesting, and no more than the registered maximum depth.
3. Component behavior must preserve native semantics, keyboard operation, visible focus, and reduced-motion handling.
4. New visual values belong in a registered theme token; component and frame CSS consume tokens.
5. Changing a protected file without a versioned contract and refreshed hash is a failure.
