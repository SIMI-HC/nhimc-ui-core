# Platform support

Use `bootstrap.md` for exact loading and readiness checks. `registry/project.json` is the machine-readable source of truth.

| Environment | Adapter | Declared path after verification |
| --- | --- | --- |
| ChatGPT Web | `plugin.json` | `READY` |
| Codex | `plugin.json` with `.codex-plugin/plugin.json` compatibility metadata | `READY` |
| Claude Web | uploaded `skills/nhimc-ui` package | `READY` |
| Claude Code | `.claude-plugin/plugin.json` | `READY` |
| Gemini Web | repository/session context | `WEB_BOOTSTRAP` |
| Gemini CLI | `gemini-extension.json` and `GEMINI.md` | `READY` |

Use `UNSUPPORTED` when the host cannot load the repository or Skill. Never say a host loaded, installed, or activated this project merely because an adapter file exists. Confirm the host can discover `nhimc-ui`, resolve registries, and identify `nhimc-default` before reporting readiness.
