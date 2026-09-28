# Platform bootstrap

The repository exposes one shared Skill through host-specific adapters. A status describes a verified loading path, not the mere presence of a manifest.

| Environment | Status | Loading path | Readiness check |
| --- | --- | --- | --- |
| ChatGPT Web | `READY` | Install the root portable plugin. | Confirm version `1.0.0` and that `nhimc-ui` is discoverable. |
| Codex | `READY` | Load the root portable plugin; `.codex-plugin/plugin.json` is the compatibility adapter. | Ask Codex to identify the registered default frame before editing. |
| Claude Web | `READY` | Upload `skills/nhimc-ui` as a custom Skill package. | Confirm the Skill appears and cites `registry/frames.json`. |
| Claude Code | `READY` | Add the repository as a Claude plugin. | Restart/reload and confirm `nhimc-ui` guidance is discoverable. |
| Gemini Web | `WEB_BOOTSTRAP` | Attach the repository context and instruct the session to follow `skills/nhimc-ui/SKILL.md`. | Confirm the session identifies `nhimc-default`; repeat for a new session. |
| Gemini CLI | `READY` | Install the repository as an extension and restart Gemini CLI. | Confirm `GEMINI.md` is loaded and the shared Skill is discoverable. |

`UNSUPPORTED` is the required status when a host cannot read the repository or accept the shared Skill. Never relabel `WEB_BOOTSTRAP` as `READY`: web bootstrap is session-scoped and must be repeated.

Before reporting any environment as ready, compare its manifest version with `VERSION`, resolve every referenced path inside the repository, open `skills/nhimc-ui/SKILL.md`, and run the repository verification command documented in the Skill.
