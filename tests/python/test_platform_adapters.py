import json
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]


class PlatformAdapterTests(unittest.TestCase):
    def test_no_approximate_v1_frame_or_component_fallback_remains(self):
        for relative in (
            "src/frame/nhimc-frame.js",
            "src/frame/nhimc-frame.css",
            "src/components/components.css",
            "src/themes/nhimc-light.css",
            "src/themes/nhimc-fonts.css",
            "src/layouts/application.css",
            "src/layouts/primitives.css",
        ):
            self.assertFalse((ROOT / relative).exists(), relative)
        for relative in (
            "registry/project.json",
            "registry/frames.json",
            "registry/themes.json",
            "registry/components.json",
            "bootstrap.md",
            "README.md",
            "skills/nhimc-ui/SKILL.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("UI Core 1.0", text, relative)
            self.assertNotIn("src/frame/nhimc-frame.js", text, relative)

    def test_skill_requires_canonical_builder_and_fail_closed_delivery(self):
        skill = (ROOT / "skills/nhimc-ui/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("canonical", skill.lower())
        self.assertIn("single HTML", skill)
        self.assertIn("MUST NOT DELIVER", skill)
        self.assertIn("context-only", skill)
        self.assertIn("data-template", skill)
        self.assertIn("scripts/build_verified_artifact.py", skill)
        self.assertIn("index.html", skill)
        self.assertIn("저작용 원본을 완성 파일로 첨부", skill)

    def test_chatgpt_web_ready_requires_callable_verified_bridge(self):
        project = json.loads((ROOT / "registry/project.json").read_text(encoding="utf-8"))
        chatgpt = next(
            item for item in project["platformSupport"]
            if item["environment"] == "chatgpt-web"
        )
        ready = [item for item in chatgpt["outcomes"] if item["status"] == "READY"]
        self.assertEqual(
            "verified-builder-bridge-connected-and-download-tested",
            ready[0]["capability"],
        )

    def test_user_guides_describe_the_exact_v3_delivery_lifecycle(self):
        for relative in ("README.md", "bootstrap.md", "skills/nhimc-ui/SKILL.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in (
                "data-template", "build_verified_artifact.py", "index.html",
                "context-only", "저작용 원본을 완성 파일로 첨부",
            ):
                self.assertIn(phrase, text, relative)

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
        self.assertIn("bootstrap.md만 읽고 NHIMC UI Core를 준비해줘.", text)
        self.assertIn("이송업무 관리 화면 만들어줘.", text)

    def test_gemini_web_without_install_capability_is_not_ready(self):
        table = json.loads(
            (ROOT / "registry/project.json").read_text(encoding="utf-8")
        )["platformSupport"]
        row = next(item for item in table if item["environment"] == "gemini-web")
        self.assertTrue(
            all(
                outcome["status"] in {"WEB_BOOTSTRAP", "UNSUPPORTED"}
                for outcome in row["outcomes"]
            )
        )

    def test_every_environment_has_a_deterministic_status(self):
        project = json.loads(
            (ROOT / "registry/project.json").read_text(encoding="utf-8")
        )
        rows = project["platformSupport"]
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
        for row in rows:
            self.assertNotIn("status", row)
            outcomes = row["outcomes"]
            self.assertGreaterEqual(len(outcomes), 2)
            self.assertTrue(all(item["status"] in project["bootstrapStatuses"] for item in outcomes))
            self.assertTrue(any(item["status"] != "READY" for item in outcomes))
            if row["environment"] == "gemini-web":
                self.assertNotIn("READY", {item["status"] for item in outcomes})
            else:
                self.assertIn("READY", {item["status"] for item in outcomes})


if __name__ == "__main__":
    unittest.main()
