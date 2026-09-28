from pathlib import Path
import tempfile
import unittest

from scripts.artifact_delivery import build_and_verify


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/authoring/transport-management/index.html"


class TransportManagementArtifactTests(unittest.TestCase):
    def test_transport_management_build_is_canonical_and_offline(self):
        with tempfile.TemporaryDirectory() as folder:
            verified = build_and_verify(ROOT, FIXTURE, Path(folder))
            html = verified.html_path.read_text(encoding="utf-8")
            self.assertNotIn("data-nhimc-template", html)
            self.assertIn('data-nhimc-layout-bundle="primitives"', html)
            for component in (
                "PageHeader", "SearchFilter", "DataTable", "PaginationArea"
            ):
                self.assertIn(f'data-nhimc-component="{component}', html)
            self.assertIn("로딩 중", html)
            self.assertIn("조회 결과가 없습니다", html)
            self.assertIn("조회 중 오류", html)
            self.assertNotIn("<nhimc-frame", html)
            self.assertGreater(verified.bytes, 1_000_000)


if __name__ == "__main__":
    unittest.main()
