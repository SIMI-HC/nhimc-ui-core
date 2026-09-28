import json
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]


class PlatformAdapterTests(unittest.TestCase):
    def test_all_manifests_use_version_and_shared_skill(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for relative in [
            "plugin.json",
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            "gemini-extension.json",
        ]:
            data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual(version, data["version"], relative)
            self.assertNotIn("distribution/", json.dumps(data), relative)
        self.assertTrue((ROOT / "skills/nhimc-ui/SKILL.md").is_file())

    def test_manifest_paths_stay_in_repository(self):
        manifests = [
            ROOT / ".codex-plugin/plugin.json",
            ROOT / ".claude-plugin/plugin.json",
            ROOT / "gemini-extension.json",
        ]
        for manifest in manifests:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            for key in ("skills", "contextFileName"):
                value = data.get(key)
                if not isinstance(value, str):
                    continue
                normalized = PurePosixPath(value.replace("\\", "/"))
                self.assertFalse(normalized.is_absolute(), manifest)
                self.assertNotIn("..", normalized.parts, manifest)

    def test_bootstrap_uses_only_exact_status_vocabulary(self):
        text = (ROOT / "bootstrap.md").read_text(encoding="utf-8")
        for status in ("READY", "WEB_BOOTSTRAP", "UNSUPPORTED"):
            self.assertIn(status, text)
        self.assertNotIn("INSTALLED", text)

    def test_gemini_web_without_install_capability_is_not_ready(self):
        table = json.loads(
            (ROOT / "registry/project.json").read_text(encoding="utf-8")
        )["bootstrapMatrix"]
        row = next(
            item
            for item in table
            if item["environment"] == "gemini-web"
            and not item["persistentInstall"]
        )
        self.assertIn(row["status"], {"WEB_BOOTSTRAP", "UNSUPPORTED"})

    def test_every_environment_has_a_deterministic_status(self):
        project = json.loads(
            (ROOT / "registry/project.json").read_text(encoding="utf-8")
        )
        rows = project["bootstrapMatrix"]
        self.assertEqual(
            {
                "chatgpt-web",
                "codex",
                "claude-web",
                "claude-code",
                "gemini-web",
                "gemini-cli",
            },
            {row["environment"] for row in rows},
        )
        self.assertTrue(
            all(row["status"] in project["bootstrapStatuses"] for row in rows)
        )


if __name__ == "__main__":
    unittest.main()
