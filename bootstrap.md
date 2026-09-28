# Platform bootstrap

The repository exposes one shared Skill through host-specific adapters. A status describes a verified loading path, not the mere presence of a manifest.

This file is the only prompt entry point. Determine the environment outcome below, then open `skills/nhimc-ui/SKILL.md` and follow it. For a generated business screen, its default artifact contract applies in every supported environment: produce one offline `index.html`, finalize it with the repository builder, and return no sidecar CSS, JavaScript, font, image, or documentation files.

| Environment | Verified persistent mechanism | Without that mechanism |
| --- | --- | --- |
| ChatGPT Web | Portable plugin loaded and checks pass → `READY` | Repository context → `WEB_BOOTSTRAP`; no compatible loader → `UNSUPPORTED` |
| Codex | Portable or compatibility plugin loaded and checks pass → `READY` | Readable checkout → `WEB_BOOTSTRAP`; no repository access → `UNSUPPORTED` |
| Claude Web | Custom Skill uploaded and checks pass → `READY` | Repository context → `WEB_BOOTSTRAP`; no compatible loader → `UNSUPPORTED` |
| Claude Code | Claude plugin loaded and checks pass → `READY` | Readable checkout → `WEB_BOOTSTRAP`; no repository access → `UNSUPPORTED` |
| Gemini Web | No persistent mechanism is declared | Repository context → `WEB_BOOTSTRAP`; otherwise `UNSUPPORTED` |
| Gemini CLI | Extension loaded, restarted, and checks pass → `READY` | Readable checkout → `WEB_BOOTSTRAP`; no repository access → `UNSUPPORTED` |

`UNSUPPORTED` is the required status when a host cannot read the repository or accept the shared Skill. Never relabel `WEB_BOOTSTRAP` as `READY`: web bootstrap is session-scoped and must be repeated.

Before reporting any environment as ready, compare its manifest version with `VERSION`, resolve every referenced path inside the repository, open `skills/nhimc-ui/SKILL.md`, and run the repository verification command documented in the Skill.
