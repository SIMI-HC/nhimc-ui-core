import unittest

from scripts.run_browser_tests import DEFAULT_VIEWPORTS, run_parity_matrix
from scripts.test_profiles import gate_covered


@gate_covered
class CanonicalParityMatrixTests(unittest.TestCase):
    def test_release_gate_covers_every_canonical_frame(self):
        result = run_parity_matrix(viewports=DEFAULT_VIEWPORTS)

        self.assertEqual(
            {
                "left",
                "left-blank",
                "left-dual",
                "top",
                "top-left",
                "presentation",
                "presentation-vertical",
                "blog",
            },
            set(result["frames"]),
        )
        self.assertEqual(
            {"1440x900", "1024x768", "390x844"}, set(result["viewports"])
        )
        self.assertEqual(48, len(result["results"]))
        self.assertTrue(result["all_passed"], result)


if __name__ == "__main__":
    unittest.main()
