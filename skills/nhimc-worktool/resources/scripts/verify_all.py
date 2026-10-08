import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]


def verification_checks(
    root: Path = ROOT, *, include_canonical: bool = True, quick: bool = False
) -> list[tuple[str, list[str]]]:
    root = root.resolve()
    npm = shutil.which("npm") or shutil.which("npm.cmd") or "npm"
    checks = [
        (
            "python tests",
            [
                sys.executable,
                "scripts/run_python_tests.py",
                "--profile",
                "quick" if quick else "gated",
            ],
        ),
        ("node tests", [npm, "run", "test:node"]),
        ("contracts", [sys.executable, "scripts/validate_contracts.py"]),
        ("design rules", [sys.executable, "scripts/validate_design.py"]),
        ("public tree", [sys.executable, "scripts/validate_public.py"]),
        ("skill resources sync", [sys.executable, "scripts/verify_skill_resources_sync.py"]),
    ]
    if quick:
        if include_canonical:
            checks.insert(
                5,
                ("canonical snapshot", [sys.executable, "scripts/verify_nhimc_design_sync.py"]),
            )
        return checks

    checks.insert(5, ("browser", [sys.executable, "scripts/run_browser_tests.py"]))
    if include_canonical:
        checks[5:5] = [
            ("canonical snapshot", [sys.executable, "scripts/verify_nhimc_design_sync.py"]),
            (
                "canonical frame parity",
                [
                    sys.executable,
                    "scripts/run_browser_tests.py",
                    "--canonical-parity-only",
                    "--all-frames",
                ],
            ),
            (
                "content layout",
                [sys.executable, "scripts/run_browser_tests.py", "--content-layout-only"],
            ),
            (
                "presentation safe area",
                [
                    sys.executable,
                    "scripts/run_browser_tests.py",
                    "--presentation-safe-area-only",
                ],
            ),
            (
                "blog scroll owner",
                [sys.executable, "scripts/run_browser_tests.py", "--blog-scroll-owner-only"],
            ),
            (
                "frame enhancements",
                [sys.executable, "scripts/run_browser_tests.py", "--frame-enhancements-only"],
            ),
            (
                "frame render",
                [sys.executable, "scripts/run_browser_tests.py", "--frame-render-only"],
            ),
            (
                "outside click",
                [sys.executable, "scripts/run_browser_tests.py", "--outside-click-only"],
            ),
            (
                "modal stability",
                [sys.executable, "scripts/run_browser_tests.py", "--modal-stability-only"],
            ),
        ]
    return checks


def run_check(root: Path, label: str, command: list[str]) -> tuple[str, int, float, str]:
    started = time.perf_counter()
    completed = subprocess.run(
        command, cwd=root, check=False, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    return label, completed.returncode, time.perf_counter() - started, completed.stdout


def verify_all(
    root: Path = ROOT, include_canonical: bool = True, quick: bool = False, jobs: int = 4
) -> int:
    root = root.resolve()
    checks = verification_checks(root, include_canonical=include_canonical, quick=quick)
    started = time.perf_counter()

    def run_and_report(check: tuple[str, list[str]]) -> tuple[str, int, float]:
        label, code, elapsed, output = run_check(root, *check)
        # print each finished check as one block so parallel output never interleaves
        print(f"[verify] {label}: {elapsed:.1f}s\n{output if code else ''}", end="", flush=True)
        return label, code, elapsed

    # ponytail: checks assumed independent (own temp dirs, port 0); --jobs 1 restores serial order
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        results = list(pool.map(run_and_report, checks))
    failures = [label for label, code, _ in results if code]
    if failures:
        print(f"VERIFY FAILED: {', '.join(failures)}")
        return next(code for _, code, _ in results if code)
    profile = " QUICK" if quick else ""
    print(
        f"VERIFY{profile} PASS: {len(results)} checks"
        f" in {time.perf_counter() - started:.1f}s"
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quick",
        action="store_true",
        help="skip browser-backed Python tests and browser matrix gates",
    )
    parser.add_argument("--jobs", type=int, default=4, help="parallel checks (1 = serial)")
    arguments = parser.parse_args()
    raise SystemExit(verify_all(quick=arguments.quick, jobs=arguments.jobs))
