import io
from contextlib import redirect_stderr
from pathlib import Path
import tempfile
import unittest

from scripts.build_verified_artifact import extra_files, warn_extra_files

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = (ROOT / "bootstrap.md").read_text(encoding="utf-8")
SKILL = (ROOT / "skills/nhimc-worktool/SKILL.md").read_text(encoding="utf-8")


class PluginInstallDoesNotCloneTests(unittest.TestCase):
    def test_clone_and_pull_are_scoped_to_scratch_or_the_no_install_case(self):
        lines = [line for line in BOOTSTRAP.splitlines() if "git clone" in line or "git pull" in line]
        self.assertGreaterEqual(len(lines), 1)
        for line in lines:
            self.assertRegex(
                line,
                r"임시|scratch|않(?:으면|을 때만)|하지 않(?:습니다|고)|금지",
                line[:120],
            )

    def test_first_step_reads_bootstrap_via_raw_url_not_clone(self):
        self.assertIn("raw.githubusercontent.com/SIMI-HC/nhimc-ui-core/HEAD/bootstrap.md", BOOTSTRAP)
        intro = BOOTSTRAP.split("## 준비 절차", 1)[0]
        self.assertIn("`git clone`/`git pull`을 하지 않습니다", intro)

    def test_required_resources_are_listed(self):
        for text in (BOOTSTRAP, SKILL):
            for resource in ("registry/", "scripts/", "guide/", "skills/", "vendor/", "VERSION"):
                self.assertIn(resource, text)

    def test_nine_step_procedure_is_present_in_order(self):
        markers = [
            "raw `bootstrap.md` 읽기",
            "raw `VERSION` 확인",
            "설치된 `nhimc-worktool` 검색",
            "필수 리소스를 검증",
            "공식 등록 가능 여부를 확인",
            "공식 경로로 설치·업데이트",
            "필수 리소스를 재검증",
            "Design Guide를 표출",
            "결과를 보고",
        ]
        positions = [BOOTSTRAP.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_incomplete_install_is_reported_not_cloned_over(self):
        self.assertIn("설치 패키지가 불완전하다", BOOTSTRAP)
        start = BOOTSTRAP.index("설치 패키지가 불완전하다")
        around = BOOTSTRAP[start : start + 200]
        self.assertNotIn("git clone", around)

    def test_plugin_install_path_is_the_root_and_a_copy_includes_the_plugin_install(self):
        self.assertIn("~/.claude/plugins/cache/<마켓플레이스>/nhimc-worktool/<버전>/", BOOTSTRAP)
        self.assertIn("플러그인 설치본", BOOTSTRAP)
        self.assertIn("아래 1~9를 건너뛰지 않습니다", BOOTSTRAP)
        self.assertIn("사본이 남아 있어도 생략 금지", SKILL)

    def test_update_goes_through_the_official_path_after_asking(self):
        self.assertIn("claude plugin marketplace update", BOOTSTRAP)
        self.assertIn("claude plugin update", BOOTSTRAP)
        self.assertIn("claude plugin marketplace add/update", SKILL)
        self.assertIn("claude plugin install/update", SKILL)
        self.assertIn("<루트>/guide/nhimc-design-guide.html", BOOTSTRAP)


class SingleDeliverableTests(unittest.TestCase):
    def test_authoring_source_lives_in_a_temporary_location(self):
        for text in (BOOTSTRAP, SKILL):
            self.assertIn("임시 위치", text)
            self.assertIn("원본도 보관해줘", text)
            self.assertIn("<임시 경로>/source.html", text)
        self.assertIn("임시 위치의 `source.html`로 저장합니다", BOOTSTRAP)
        self.assertIn("원본 경로는 쓰지 않습니다", BOOTSTRAP)
        self.assertIn("원본 경로는 쓰지 않습니다", SKILL)

    def test_builder_warns_about_other_files_in_the_output_folder_without_deleting(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "index.html"
            out.write_text("<!doctype html>", encoding="utf-8")
            self.assertEqual([], extra_files(out))
            (Path(folder) / "source.html").write_text("x", encoding="utf-8")
            captured = io.StringIO()
            with redirect_stderr(captured):
                warn_extra_files(out)
            self.assertIn("source.html", captured.getvalue())
            self.assertIn("Nothing was deleted", captured.getvalue())
            self.assertTrue((Path(folder) / "source.html").exists())


if __name__ == "__main__":
    unittest.main()
