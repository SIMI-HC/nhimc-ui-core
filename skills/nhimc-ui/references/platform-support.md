# Platform support

Use `bootstrap.md` for exact loading and readiness checks. `registry/project.json` is the machine-readable source of truth.

| Environment | Verified adapter outcome | Fallback outcome |
| --- | --- | --- |
| ChatGPT Web | `plugin.json` → `READY` | repository context → `WEB_BOOTSTRAP` |
| Codex | root/compatibility plugin → `READY` | readable checkout → `WEB_BOOTSTRAP` |
| Claude Web | uploaded `skills/nhimc-ui` → `READY` | repository context → `WEB_BOOTSTRAP` |
| Claude Code | `.claude-plugin/plugin.json` → `READY` | readable checkout → `WEB_BOOTSTRAP` |
| Gemini Web | no persistent adapter | repository/session context → `WEB_BOOTSTRAP` |
| Gemini CLI | extension and `GEMINI.md` → `READY` | readable checkout → `WEB_BOOTSTRAP` |

Use `UNSUPPORTED` when the host cannot load the repository or Skill. Never say a host loaded, installed, or activated this project merely because an adapter file exists. Confirm the host can discover `nhimc-ui`, resolve registries, and identify `nhimc-default` before reporting readiness.
