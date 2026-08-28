"""Run lightweight repository checks without third-party dependencies."""

from __future__ import annotations

import compileall
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB_000 = ROOT / "labs" / "000-driving-system-map" / "guided_reference" / "000a"
LAB_001 = ROOT / "labs" / "001-driving-data-contract" / "guided_reference" / "001a"


def run_tests(lab: Path) -> int:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=lab,
        check=False,
    )
    return completed.returncode


def run_and_expect(lab: Path, script: str, expected_text: str) -> int:
    completed = subprocess.run(
        [sys.executable, script],
        cwd=lab,
        check=False,
        capture_output=True,
        text=True,
    )
    print(completed.stdout)
    if completed.returncode != 0:
        print(completed.stderr, file=sys.stderr)
        return completed.returncode
    if expected_text not in completed.stdout:
        print(f"unexpected output from {lab / script}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    if not compileall.compile_dir(ROOT / "labs", quiet=1):
        print("compileall failed", file=sys.stderr)
        return 1

    for lab in (LAB_000, LAB_001):
        returncode = run_tests(lab)
        if returncode != 0:
            return returncode

    returncode = run_and_expect(
        LAB_000,
        "run_trace.py",
        "SYSTEM MAP RESULT: 4 / 4 PASS",
    )
    if returncode != 0:
        return returncode

    returncode = run_and_expect(
        LAB_001,
        "run_eval.py",
        "BASELINE RESULT: 4 / 6 PASS",
    )
    if returncode != 0:
        return returncode

    print("repository checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
