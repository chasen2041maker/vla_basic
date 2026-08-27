"""Run lightweight repository checks without third-party dependencies."""

from __future__ import annotations

import compileall
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "001-driving-data-contract" / "guided_reference" / "001a"


def main() -> int:
    if not compileall.compile_dir(ROOT / "labs", quiet=1):
        print("compileall failed", file=sys.stderr)
        return 1

    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=LAB,
        check=False,
    )
    if tests.returncode != 0:
        return tests.returncode

    baseline = subprocess.run(
        [sys.executable, "run_eval.py"],
        cwd=LAB,
        check=False,
        capture_output=True,
        text=True,
    )
    print(baseline.stdout)
    if baseline.returncode != 0:
        print(baseline.stderr, file=sys.stderr)
        return baseline.returncode
    if "BASELINE RESULT: 4 / 6 PASS" not in baseline.stdout:
        print("unexpected Lab 001A baseline", file=sys.stderr)
        return 1

    print("repository checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
