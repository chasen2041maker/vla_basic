"""教学摘要契约：固定夹具只测格式；集成部分必须真的推进 HighwayEnv。"""
from __future__ import annotations

import json
import io
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from contextlib import redirect_stdout

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


class VisibleSpeedDemoTests(unittest.TestCase):
    def test_setting_target_does_not_move_vehicle_until_step(self):
        demo = runpy.run_path(str(PROJECT / "demos" / "04_target_speed.py"))
        with tempfile.TemporaryDirectory() as temp:
            from PIL import Image
            snapshot = Path(temp) / "speed.png"
            before_sdl = {k: os.environ.get(k) for k in ("SDL_VIDEODRIVER", "SDL_AUDIODRIVER")}
            records = demo["run_demo"](target_speed=20, headless=True, snapshot_path=snapshot)
            self.assertEqual(before_sdl, {k: os.environ.get(k) for k in before_sdl})
            change = next(i for i, row in enumerate(records) if row["event"] == "target_changed")
            before, changed, after = records[change - 1:change + 2]
            self.assertEqual(changed["time_s"], 2.0)
            for field in ("time_s", "speed_mps", "x_world_m", "y_world_m"):
                self.assertEqual(before[field], changed[field])
            self.assertEqual(changed["target_speed_mps"], 20.0)
            self.assertGreater(after["time_s"], changed["time_s"])
            self.assertGreater(after["x_world_m"], changed["x_world_m"])
            self.assertTrue(20 < after["speed_mps"] < changed["speed_mps"])
            motion = [r for r in records if r["event"] != "target_changed"]
            for left, right in zip(motion, motion[1:]):
                self.assertAlmostEqual(right["time_s"] - left["time_s"], 0.2)
            self.assertEqual(records[-1]["time_s"], 8.0)
            self.assertAlmostEqual(records[-1]["speed_mps"], 20, places=3)
            with Image.open(snapshot) as frame:
                # 查看实际道路区域的颜色，不能只检查 PNG 文件存在。
                colors = {color for count, color in
                          frame.crop((0, 108, 960, 318)).convert("RGB").getcolors(960 * 210)}
                self.assertGreater(len(colors), 3)
                self.assertTrue(any(g > r * 1.5 and g > b * 1.5 for r, g, b in colors))

    def test_lower_target_changes_response_from_same_initial_state(self):
        demo = runpy.run_path(str(PROJECT / "demos" / "04_target_speed.py"))
        regular = demo["run_demo"](target_speed=20, headless=True)
        lower = demo["run_demo"](target_speed=10, headless=True)
        self.assertEqual([r for r in regular if r["time_s"] < 2],
                         [r for r in lower if r["time_s"] < 2])
        a = next(r for r in regular if r["time_s"] == 2.2)
        b = next(r for r in lower if r["time_s"] == 2.2)
        self.assertLess(b["speed_mps"], a["speed_mps"])
        self.assertGreater(b["speed_mps"], b["target_speed_mps"])
        self.assertAlmostEqual(lower[-1]["speed_mps"], 10, places=3)

    def test_headless_default_uses_current_file_parameter(self):
        run = runpy.run_path(str(PROJECT / "demos" / "04_target_speed.py"))["run_demo"]
        # 模拟学习者修改顶部配置；不改写其实际文件，也不把参考值20当当前值。
        with patch.dict(run.__globals__, {"TARGET_SPEED": 15.0}):
            records = run(headless=True)
        changed = next(row for row in records if row["event"] == "target_changed")
        self.assertEqual(changed["target_speed_mps"], 15.0)
        self.assertAlmostEqual(records[-1]["speed_mps"], 15, places=3)


class FollowingEntryTests(unittest.TestCase):
    def test_short_observation_is_not_reported_as_a_complete_episode(self):
        run = runpy.run_path(str(PROJECT / "demos" / "00_following.py"))["main"]
        output = io.StringIO()
        with redirect_stdout(output):
            result = run(render_mode=None, max_steps=3)
        self.assertEqual(result["steps"], 3)
        self.assertEqual(result["episode"], 1)
        self.assertAlmostEqual(result["episode_time_s"], 3)
        self.assertFalse(result["episode_finished"])
        self.assertIn("本局未完成", output.getvalue())

    def test_budget_at_episode_end_keeps_final_state_instead_of_resetting(self):
        run = runpy.run_path(str(PROJECT / "demos" / "00_following.py"))["main"]
        with redirect_stdout(io.StringIO()):
            result = run(render_mode=None, max_steps=40)
        self.assertEqual(result["steps"], 40)
        self.assertEqual(result["episode"], 1)
        self.assertAlmostEqual(result["episode_time_s"], 40)
        self.assertTrue(result["episode_finished"])
        self.assertEqual(result["stop_reason"], "runner_step_limit")


class ComparisonReportTests(unittest.TestCase):
    def test_short_report_preserves_actual_motion_and_observation_limit(self):
        from PIL import Image
        compare = runpy.run_path(str(PROJECT / "demos" / "05_compare_actions.py"))["run_comparison"]
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(compare.__globals__, {"OUTPUT_ROOT": Path(temp)}):
                result = compare(max_steps=5, open_browser=False)
            self.assertTrue(result["initial_conditions_match"])
            report = Path(result["report_path"])
            page = report.read_text(encoding="utf-8")
            self.assertIn("runner_step_limit", page)
            self.assertIn("不是 40/50 米阈值策略评价", page)
            a, b = result["runs"]["IDLE"], result["runs"]["SLOWER"]
            self.assertEqual(a["summary"]["initial_observation"], b["summary"]["initial_observation"])
            self.assertLess(b["final_speed_mps"], a["final_speed_mps"])
            self.assertLess(b["displacement_x_m"], a["displacement_x_m"])
            for action, run in result["runs"].items():
                summary = run["summary"]
                self.assertEqual(summary["steps"], 5)
                self.assertAlmostEqual(summary["sim_time_s"], 1.0)
                self.assertEqual(summary["end_reason"], "runner_step_limit")
                self.assertFalse(summary["terminated"] or summary["truncated"])
                saved = [json.loads(line) for line in Path(run["trace_path"]).read_text(
                    encoding="utf-8").splitlines()]
                self.assertEqual(saved, run["trace"])
                self.assertEqual(run["final_speed_mps"], saved[-1]["speed_mps"])
                self.assertIn(f'{action}/episode.gif', page)
                self.assertTrue((report.parent / action / "summary.json").exists())
                with Image.open(run["gif_path"]) as gif:
                    self.assertEqual(gif.n_frames, 6)  # 初始帧 + 五个真实后续时刻。
                    self.assertEqual(gif.info["duration"], 200)


if __name__ == "__main__":
    unittest.main()
