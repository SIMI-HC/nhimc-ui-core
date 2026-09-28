# ChatGPT and Codex

The canonical adapter is the root `plugin.json`, using the portable Agent Plugins format. Skills live at the root `skills/` directory. `.codex-plugin/plugin.json` is retained as a compatibility adapter and points to the same shared directory; it does not fork the instructions.

ChatGPT Web is `READY` only after the portable plugin has been added and `nhimc-ui` is visible. Codex is `READY` only after the checkout/plugin has been loaded and the Skill can resolve the repository registries.

These are supported loading paths, not a claim that this repository is already installed or published in either host.

References: [OpenAI plugin format](https://developers.openai.com/plugins/build/plugins) and [OpenAI Skills guide](https://learn.chatgpt.com/docs/build-skills).
