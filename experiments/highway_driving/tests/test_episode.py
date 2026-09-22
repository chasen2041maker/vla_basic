"""真实 HighwayEnv 集成检查：缺依赖就失败，不用 mock 或 skip 假装跑通。"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_episode import FEATURES, make_env, run_episode


class EpisodeTests(unittest.TestCase):
    def test_observation_contract_and_world_axes(self):
        env = make_env()
        try:
            obs, _ = env.reset(seed=7)
            ego = env.unwrapped.vehicle
            self.assertEqual(obs.shape, (5, len(FEATURES)))
            self.assertTrue(np.isfinite(obs).all())
            self.assertEqual(float(obs[0, 0]), 1.0)
            np.testing.assert_allclose(obs[0, 1:3], ego.position, atol=1e-4)
            np.testing.assert_allclose(obs[0, 3:5], ego.velocity, atol=1e-4)
            candidates = [np.r_[v.position - ego.position, v.velocity - ego.velocity]
                          for v in env.unwrapped.road.vehicles if v is not ego]
            others = obs[1:][obs[1:, 0] == 1]
            self.assertGreater(len(others), 0)
            for row in others:
                self.assertTrue(any(np.allclose(row[1:], value, atol=1e-4) for value in candidates))
        finally:
            env.close()

    def test_padding_and_one_real_step(self):
        env = make_env(vehicles_count=0)
        try:
            obs, _ = env.reset(seed=7)
            np.testing.assert_array_equal(obs[1:], 0)
            action = env.unwrapped.action_type.actions_indexes["IDLE"]
            next_obs, _, terminated, truncated, _ = env.step(action)
            self.assertGreater(next_obs[0, 1], obs[0, 1])
            self.assertAlmostEqual(env.unwrapped.time, 0.2)
            self.assertFalse(terminated or truncated)
        finally:
            env.close()

    def test_same_seed_same_rollout(self):
        a = run_episode(seed=7, max_steps=3, render_mode=None)
        b = run_episode(seed=7, max_steps=3, render_mode=None)
        np.testing.assert_allclose(a["initial_observation"], b["initial_observation"])
        np.testing.assert_allclose(a["final_observation"], b["final_observation"])
        self.assertEqual(a["end_reason"], b["end_reason"])
        self.assertAlmostEqual(a["total_reward"], b["total_reward"])

    def test_slower_changes_motion(self):
        idle = run_episode(max_steps=2, vehicles_count=0, render_mode=None)
        slower = run_episode(max_steps=2, vehicles_count=0, action_name="SLOWER", render_mode=None)
        self.assertLess(slower["final_observation"][0][3], idle["final_observation"][0][3])

    def test_step_limit_is_not_environment_truncation(self):
        result = run_episode(max_steps=1, vehicles_count=0, render_mode=None)
        self.assertEqual(result["steps"], 1)
        self.assertEqual(result["end_reason"], "runner_step_limit")
        self.assertFalse(result["terminated"] or result["truncated"])

    def test_environment_time_limit_stops_loop(self):
        result = run_episode(max_steps=10, duration_s=0.4, vehicles_count=0, render_mode=None)
        self.assertEqual(result["steps"], 2)
        self.assertEqual(result["end_reason"], "environment_time_limit")
        self.assertTrue(result["truncated"])
        self.assertFalse(result["terminated"])

    def test_saved_artifacts_and_trace_continuity(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "episode"
            result = run_episode(max_steps=2, vehicles_count=0, output_dir=folder)
            saved = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(result, saved)
            rows = [json.loads(line) for line in (folder / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["next_observation"], rows[1]["observation"])
            self.assertEqual(rows[0]["next_observation_time_s"], rows[1]["observation_time_s"])
            for row in rows:
                self.assertAlmostEqual(row["next_observation_time_s"] - row["observation_time_s"], 0.2)
            for name in ("initial.png", "final.png", "episode.gif"):
                with Image.open(folder / name) as image:
                    self.assertEqual(image.size, (720, 160))
                    image.verify()
            with self.assertRaises(FileExistsError):
                run_episode(max_steps=1, output_dir=folder)


if __name__ == "__main__":
    unittest.main()
