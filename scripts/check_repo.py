"""保留零依赖旧 Lab 检查；--with-highway 显式加入真实模拟器测试。"""
from __future__ import annotations
import argparse
import compileall
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_000 = ROOT / "archive" / "labs" / "000-driving-system-map" / "guided_reference" / "000a"
LAB_001 = ROOT / "archive" / "labs" / "001-driving-data-contract" / "guided_reference" / "001a"
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
    for directory in (ROOT / "archive" / "labs", ROOT / "experiments"):
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
        # 归入主项目的教学脚本也检查真实导入与执行；不启动交互窗口。
        # 00 的短跑/回合边界及 04/05 的真实记录检查已由上面的测试发现运行。
        # 这些检查不作为学员个人验收。
        for name in ("02_action_space.py", "03_continuous_action.py"):
            if subprocess.run(
                [sys.executable, str(HIGHWAY / "demos" / name)],
                cwd=ROOT, check=False,
            ).returncode != 0:
                return 1
        if subprocess.run(
            [sys.executable, "-c",
             "import runpy; runpy.run_path("
             "'experiments/highway_driving/demos/01_lane_change.py')"
             "['main'](render_mode=None)"],
            cwd=ROOT, check=False,
        ).returncode != 0:
            return 1
        print("repository + HighwayEnv checks passed")
    else:
        print("legacy checks passed; HighwayEnv integration NOT RUN (use --with-highway)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
