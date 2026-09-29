from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def verify_all(root: Path = ROOT, include_canonical: bool = True) -> int:
    root = root.resolve()
    npm = shutil.which("npm") or shutil.which("npm.cmd") or "npm"
    checks = [
        ("python tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests/python", "-v"]),
        ("node tests", [npm, "run", "test:node"]),
        ("contracts", [sys.executable, "scripts/validate_contracts.py"]),
        ("design rules", [sys.executable, "scripts/validate_design.py"]),
        ("public tree", [sys.executable, "scripts/validate_public.py"]),
        ("browser", [sys.executable, "scripts/run_browser_tests.py"]),
    ]
    if include_canonical:
        checks[5:5] = [
            ("canonical snapshot", [sys.executable, "scripts/verify_nhimc_design_sync.py"]),
            (
                "canonical frame parity",
                [
                    sys.executable, "scripts/run_browser_tests.py",
                    "--canonical-parity-only", "--all-frames",
                ],
            ),
            (
                "content layout",
                [sys.executable, "scripts/run_browser_tests.py", "--content-layout-only"],
            ),
            (
                "presentation safe area",
                [sys.executable, "scripts/run_browser_tests.py", "--presentation-safe-area-only"],
            ),
            (
                "blog scroll owner",
                [sys.executable, "scripts/run_browser_tests.py", "--blog-scroll-owner-only"],
            ),
            (
                "frame render",
                [sys.executable, "scripts/run_browser_tests.py", "--frame-render-only"],
            ),
            (
                "outside click",
                [sys.executable, "scripts/run_browser_tests.py", "--outside-click-only"],
            ),
        ]
    results = []
    for label, command in checks:
        print(f"[verify] {label}", flush=True)
        completed = subprocess.run(command, cwd=root, check=False)
        results.append((label, completed.returncode))
    failures = [label for label, code in results if code]
    if failures:
        print(f"VERIFY FAILED: {', '.join(failures)}")
        return next(code for _, code in results if code)
    print(f"VERIFY PASS: {len(results)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(verify_all())
