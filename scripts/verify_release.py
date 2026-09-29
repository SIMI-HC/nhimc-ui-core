import re
from pathlib import Path
import subprocess
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.release_tag import expected_tag, tag_exists
from scripts.skill_resources import compare as compare_skill_resources
from scripts.validate_contracts import validate_contracts
from scripts.validate_design import validate_design
from scripts.validate_public import scan_public_tree
from scripts.verify_all import verify_all


ROOT = Path(__file__).resolve().parents[1]
BLOCKER = re.compile(r"^\s*-\s*\[\s\]\s*BLOCKING:\s*(.+?)\s*$", re.IGNORECASE)
REQUIRED_LEGAL = ("LICENSE", "NOTICE", "src/assets/fonts/OFL.txt")


def unresolved_release_blockers(review: Path) -> list[str]:
    if not review.is_file():
        return ["public asset review is missing"]
    blockers = []
    for line in review.read_text(encoding="utf-8").splitlines():
        match = BLOCKER.match(line)
        if match:
            blockers.append(match.group(1))
    return blockers


def verify_release(root: Path = ROOT, run_full_verification: bool = True) -> int:
    root = root.resolve()
    categories: list[str] = []
    if run_full_verification:
        if verify_all(root, include_canonical=False):
            categories.append("verification gate")
        canonical_gates = (
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
        )
        for label, command in canonical_gates:
            if subprocess.run(command, cwd=root, check=False).returncode:
                categories.append(label)

    if any(item.blocking for item in validate_contracts(root)):
        categories.append("contract validation")
    if any(item.blocking for item in validate_design(root)):
        categories.append("design validation")
    if any(item.blocking for item in scan_public_tree(root)):
        categories.append("public safety")
    if compare_skill_resources(root):
        categories.append("skill resources sync")
    try:
        tagged = tag_exists(root, expected_tag(root))
    except (OSError, ValueError):
        tagged = False
    if not tagged:
        categories.append("release tag")

    if unresolved_release_blockers(root / "PUBLIC_ASSET_REVIEW.md"):
        categories.append("public asset review")
    if any(not (root / relative).is_file() for relative in REQUIRED_LEGAL):
        categories.append("license or notice")
    integrity_rules = {
        finding.rule
        for finding in validate_contracts(root)
        if finding.rule in {"contract.integrity-mismatch", "contract.empty-digest"}
    }
    if integrity_rules:
        categories.append("protected integrity")

    if categories:
        print(f"RELEASE BLOCKED: {', '.join(dict.fromkeys(categories))}")
        return 1
    print("RELEASE PASS: public artifact requirements satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(verify_release())
