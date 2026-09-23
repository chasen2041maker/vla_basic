"""教学摘要契约：固定夹具只测格式；集成部分必须真的推进 HighwayEnv。"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from run_episode import format_teaching_summary, make_env, run_episode


class TeachingFormatTests(unittest.TestCase):
    def test_first_step_is_not_mixed_with_episode_end_or_vx(self):
        # 人工单元测试夹具，不是驾驶实验结果；vx=3、vy=4，速率=5。
        summary = {
            "first_transition": {
                "action_name": "SLOWER", "action_available": True,
                "observation_time_s": 1.0, "next_observation_time_s": 1.2,
                "observation": [[1, 10, 8, 3, 4]],
                "next_observation": [[1, 10.6, 8.8, 2.7, 3.6]],
                "speed_before_mps": 5.0, "speed_mps": 4.5,
                "target_speed_before_mps": 25.0, "target_speed_after_mps": 20.0,
                "terminated": False, "truncated": False,
            },
            "final_observation": [[1, 999, 999, 0, 0]],
            "end_reason": "environment_time_limit", "steps": 40, "sim_time_s": 8.0,
        }
        text = format_teaching_summary(summary)
        self.assertIn("仅第 1 步，不是整回合", text)
        self.assertIn("仿真时间 (s)：1.000 → 1.200", text)
        self.assertIn("(10.000, 8.000) → (10.600, 8.800)", text)
        self.assertIn("实际速率 (m/s)：5.000 → 4.500", text)
        self.assertIn("目标速度 (m/s，模拟器诊断)：25.000 → 20.000", text)
        self.assertIn("本步环境标志：terminated=False；truncated=False", text)
        self.assertIn("整回合结束原因：environment_time_limit；共 40 步", text)
        self.assertIn("目标速度不是策略观察", text)
        self.assertNotIn("999.000", text)

    def test_missing_transition_is_not_replaced_with_an_invented_example(self):
        with self.assertRaises(KeyError):
            format_teaching_summary({"end_reason": "runner_step_limit"})


class TeachingIntegrationTests(unittest.TestCase):
    def test_logged_diagnostics_match_direct_simulator_before_and_after(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "diagnostics"
            saved = run_episode(seed=7, max_steps=3, action_name="SLOWER",
                                vehicles_count=0, render_mode=None, output_dir=folder)
            rows = [json.loads(line) for line in
                    (folder / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(saved["schema_version"], 2)
            self.assertEqual(saved["first_transition"], rows[0])
            self.assertEqual(saved["policy"], "constant_meta_action")
            self.assertEqual(saved["observation_contract"]["features"],
                             ["presence", "x", "y", "vx", "vy"])
            env = make_env(vehicles_count=0)
            try:
                obs, _ = env.reset(seed=7)
                action = env.unwrapped.action_type.actions_indexes["SLOWER"]
                for row in rows:
                    self.assertEqual(row["observation"], obs.tolist())
                    self.assertAlmostEqual(row["observation_time_s"], env.unwrapped.time)
                    self.assertAlmostEqual(row["speed_before_mps"], env.unwrapped.vehicle.speed)
                    self.assertAlmostEqual(row["target_speed_before_mps"],
                                           env.unwrapped.vehicle.target_speed)
                    obs, _, _, _, info = env.step(action)
                    self.assertEqual(row["next_observation"], obs.tolist())
                    self.assertAlmostEqual(row["next_observation_time_s"], env.unwrapped.time)
                    self.assertAlmostEqual(row["speed_mps"], info["speed"])
                    self.assertAlmostEqual(row["target_speed_after_mps"],
                                           env.unwrapped.vehicle.target_speed)
                for left, right in zip(rows, rows[1:]):
                    self.assertAlmostEqual(left["speed_mps"], right["speed_before_mps"])
                    self.assertAlmostEqual(left["target_speed_after_mps"],
                                           right["target_speed_before_mps"])
            finally:
                env.close()

    def test_idle_and_slower_expose_target_and_actual_motion_separately(self):
        idle = run_episode(seed=7, max_steps=1, vehicles_count=0, render_mode=None)
        slower = run_episode(seed=7, max_steps=1, vehicles_count=0,
                             action_name="SLOWER", render_mode=None)
        a, b = idle["first_transition"], slower["first_transition"]
        self.assertEqual(a["observation"], b["observation"])
        self.assertEqual(a["target_speed_before_mps"], a["target_speed_after_mps"])
        self.assertLess(b["target_speed_after_mps"], b["target_speed_before_mps"])
        self.assertLess(b["speed_mps"], a["speed_mps"])
        self.assertGreater(b["speed_mps"], b["target_speed_after_mps"])
        self.assertGreater(a["next_observation"][0][1], a["observation"][0][1])
        self.assertAlmostEqual(a["next_observation_time_s"] - a["observation_time_s"], 0.2)
        self.assertEqual(idle["end_reason"], "runner_step_limit")
        self.assertFalse(idle["terminated"] or idle["truncated"])

    def test_cli_summary_is_based_on_saved_first_transition(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "cli"
            completed = subprocess.run(
                [sys.executable, str(PROJECT / "run_episode.py"), "--seed", "7",
                 "--action", "SLOWER", "--vehicles", "0", "--max-steps", "2",
                 "--render", "none", "--output-dir", str(folder)],
                cwd=PROJECT.parents[1], capture_output=True, text=True,
                encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"}, timeout=60,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            saved = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
            row = json.loads((folder / "trace.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(saved["first_transition"], row)
            self.assertIn(format_teaching_summary(saved), completed.stdout)
            self.assertIn("仿真时间 (s)：0.000 → 0.200", completed.stdout)
            self.assertIn("共 2 步；总仿真时间=0.400s", completed.stdout)
            self.assertFalse((folder / "episode.gif").exists())


if __name__ == "__main__":
    unittest.main()
