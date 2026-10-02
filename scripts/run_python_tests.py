from __future__ import annotations

import argparse
from pathlib import Path
import sys
import unittest

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.test_profiles import select_tests


ROOT = Path(__file__).resolve().parents[1]


def build_suite(root: Path, profile: str) -> tuple[unittest.TestSuite, int]:
    discovered = unittest.defaultTestLoader.discover(
        str(root / "tests/python"), pattern="test_*.py"
    )
    # quick: no browser tests; gated: browser tests except those a verify_all gate already runs; full: everything
    return select_tests(
        discovered, include_slow=profile != "quick", include_gate_covered=profile == "full"
    )


def run_python_tests(root: Path = ROOT, profile: str = "full") -> int:
    suite, excluded = build_suite(root.resolve(), profile)
    print(
        f"python tests ({profile}): {suite.countTestCases()} selected"
        f", {excluded} slow excluded",
        flush=True,
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("quick", "gated", "full"), default="full")
    arguments = parser.parse_args(argv)
    return run_python_tests(profile=arguments.profile)


if __name__ == "__main__":
    raise SystemExit(main())
