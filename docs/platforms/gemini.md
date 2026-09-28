# Gemini

Gemini CLI reads `gemini-extension.json`, loads `GEMINI.md` as context, and discovers the repository's root `skills/` directory. Restart Gemini CLI after install or update, then verify that the shared Skill and registries are readable.

Gemini Web has no persistent repository extension in this project. Use the session-scoped instructions in `bootstrap.md`; its truthful status is `WEB_BOOTSTRAP`, not `READY`.

The extension manifest documents a supported path; installation and restart remain explicit user actions.

References: [Gemini CLI extension reference](https://geminicli.com/docs/extensions/reference/) and [extension release guidance](https://geminicli.com/docs/extensions/releasing/).
