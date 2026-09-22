"""保留零依赖旧 Lab 检查；--with-highway 显式加入真实模拟器测试。"""
from __future__ import annotations
import argparse
import compileall
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_000 = ROOT / "labs" / "000-driving-system-map" / "guided_reference" / "000a"
LAB_001 = ROOT / "labs" / "001-driving-data-contract" / "guided_reference" / "001a"
HIGHWAY = ROOT / "experiments" / "highway_driving"


def run_tests(directory: Path) -> int:
    return subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=directory, check=False,
    ).returncode


def run_and_expect(lab: Path, script: str, expected_text: str) -> int:
    completed = subprocess.run(
        [sys.executable, script], cwd=lab, check=False,
        capture_output=True, text=True, encoding="utf-8",
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-highway", action="store_true")
    args = parser.parse_args()
    for directory in (ROOT / "labs", ROOT / "experiments"):
        if not compileall.compile_dir(directory, quiet=1):
            return 1
    for lab in (LAB_000, LAB_001):
        if run_tests(lab) != 0:
            return 1
    for lab, script, expected in (
        (LAB_000, "run_trace.py", "SYSTEM MAP RESULT: 4 / 4 PASS"),
        (LAB_001, "run_eval.py", "BASELINE RESULT: 4 / 6 PASS"),
    ):
        if run_and_expect(lab, script, expected) != 0:
            return 1
    if args.with_highway:
        if run_tests(HIGHWAY) != 0:
            return 1
        print("repository + HighwayEnv checks passed")
    else:
        print("legacy checks passed; HighwayEnv integration NOT RUN (use --with-highway)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
