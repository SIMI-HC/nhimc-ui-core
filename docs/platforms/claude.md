# Claude

Claude Code uses `.claude-plugin/plugin.json`; its `skills` path resolves to the repository's shared `skills/` directory. Reload Claude Code after adding or updating the plugin.

Claude Web uses the same `skills/nhimc-ui` directory as an uploaded custom Skill package. An upload is a separate host action, so repository presence alone is not a successful readiness check.

Distribution of this source or its release archive does not perform either host action.

References: [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference), [create custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills), and [use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).
