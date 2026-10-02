from __future__ import annotations

import unittest
from collections.abc import Iterable
from typing import TypeVar


SLOW_TEST_ATTRIBUTE = "__nhimc_slow_test__"
GATE_COVERED_ATTRIBUTE = "__nhimc_gate_covered__"
T = TypeVar("T")


def slow_test(target: T) -> T:
    """Mark a unittest class or method as browser-backed/slow."""
    setattr(target, SLOW_TEST_ATTRIBUTE, True)
    return target


def gate_covered(target: T) -> T:
    """Slow test that runs the same browser matrix as a standalone verify_all gate; the 'gated' profile skips it."""
    setattr(target, GATE_COVERED_ATTRIBUTE, True)
    return slow_test(target)


def is_gate_covered(case: unittest.TestCase) -> bool:
    method = getattr(case, case._testMethodName)
    return bool(
        getattr(case.__class__, GATE_COVERED_ATTRIBUTE, False)
        or getattr(method, GATE_COVERED_ATTRIBUTE, False)
    )


def is_slow_test(case: unittest.TestCase) -> bool:
    method = getattr(case, case._testMethodName)
    return bool(
        getattr(case.__class__, SLOW_TEST_ATTRIBUTE, False)
        or getattr(method, SLOW_TEST_ATTRIBUTE, False)
    )


def iter_cases(suite: unittest.TestSuite) -> Iterable[unittest.TestCase]:
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from iter_cases(item)
        else:
            yield item


def select_tests(
    suite: unittest.TestSuite, *, include_slow: bool, include_gate_covered: bool = True
) -> tuple[unittest.TestSuite, int]:
    selected = unittest.TestSuite()
    excluded = 0
    for case in iter_cases(suite):
        if (not include_slow and is_slow_test(case)) or (
            not include_gate_covered and is_gate_covered(case)
        ):
            excluded += 1
            continue
        selected.addTest(case)
    return selected, excluded
