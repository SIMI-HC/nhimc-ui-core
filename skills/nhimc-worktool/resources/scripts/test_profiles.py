from __future__ import annotations

import unittest
from collections.abc import Iterable
from typing import TypeVar


SLOW_TEST_ATTRIBUTE = "__nhimc_slow_test__"
T = TypeVar("T")


def slow_test(target: T) -> T:
    """Mark a unittest class or method as browser-backed/slow."""
    setattr(target, SLOW_TEST_ATTRIBUTE, True)
    return target


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
    suite: unittest.TestSuite, *, include_slow: bool
) -> tuple[unittest.TestSuite, int]:
    selected = unittest.TestSuite()
    excluded = 0
    for case in iter_cases(suite):
        if not include_slow and is_slow_test(case):
            excluded += 1
            continue
        selected.addTest(case)
    return selected, excluded
