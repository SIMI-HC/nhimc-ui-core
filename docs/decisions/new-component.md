# New Component Decision Record

Use this record only when registered components and their compositions cannot meet a verified need.

## Unmet use case

Describe the user task and the observable behavior that is missing.

## Registered compositions considered

List the registered components and compositions considered, and explain why each fails the use case.

## Proposed public API

Specify semantic markup, `.nhimc-*` selector, attributes, events, states, and controller behavior.

## Accessibility behavior

Specify accessible name, keyboard interaction, focus behavior, roles, states, and announcements.

## Token use

List every registered theme token used. New tokens require a separate theme-contract change.

## Tests

List the unit, real-browser, accessibility, and design-rule tests that will fail before implementation.

## Registry change

Provide the complete `registry/components.json` entry and the versioning effect.
