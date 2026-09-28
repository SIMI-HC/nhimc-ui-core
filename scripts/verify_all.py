from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def _command(label: str, command: list[str]) -> tuple[str, int]:
    print(f"[verify] {label}", flush=True)
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return label, completed.returncode


def verify_all() -> int:
    npm = shutil.which("npm") or shutil.which("npm.cmd") or "npm"
    checks = [
        ("python tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests/python", "-v"]),
        ("node tests", [npm, "run", "test:node"]),
        ("contracts", [sys.executable, "scripts/validate_contracts.py"]),
        ("design rules", [sys.executable, "scripts/validate_design.py"]),
        ("public tree", [sys.executable, "scripts/validate_public.py"]),
        ("browser", [sys.executable, "scripts/run_browser_tests.py"]),
    ]
    results = [_command(label, command) for label, command in checks]
    failures = [label for label, code in results if code]
    if failures:
        print(f"VERIFY FAILED: {', '.join(failures)}")
        return next(code for _, code in results if code)
    print(f"VERIFY PASS: {len(results)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(verify_all())
