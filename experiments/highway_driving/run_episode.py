"""单回合驾驶实验：观察 → 明确动作 → 环境推进 → 新观察；不是视觉感知或 VLA。"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ACTIONS = ("IDLE", "SLOWER", "FASTER", "LANE_LEFT", "LANE_RIGHT")
FEATURES = ["presence", "x", "y", "vx", "vy"]


def validate_options(seed: int, max_steps: int, action_name: str,
                     render_mode: str | None, duration_s: float,
                     vehicles_count: int) -> None:
    """先拒绝无效输入，不静默换动作，也不开始一个零步实验。"""
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed 必须是非负整数")
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 1:
        raise ValueError("max_steps 必须是正整数")
    if action_name not in ACTIONS:
        raise ValueError(f"action_name 必须属于 {ACTIONS}")
    if render_mode not in (None, "rgb_array", "human"):
        raise ValueError("render_mode 必须是 none、rgb_array 或 human")
    if not math.isfinite(duration_s) or not 0 < duration_s <= 60:
        raise ValueError("duration_s 必须在 (0, 60] 秒内")
    if isinstance(vehicles_count, bool) or not isinstance(vehicles_count, int) or not 0 <= vehicles_count <= 100:
        raise ValueError("vehicles_count 必须是 0 到 100 的整数")


def make_env(*, render_mode: str | None = None, duration_s: float = 8.0,
             vehicles_count: int = 12) -> Any:
    """配置集中在这里；外部库延迟导入，让纯逻辑测试不依赖模拟器。"""
    if render_mode != "human":
        # 无窗口运行和 CI 不要求桌面或声卡；须在导入 pygame 前设置。
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import gymnasium as gym
    import highway_env

    gym.register_envs(highway_env)
    return gym.make("highway-v0", render_mode=render_mode, config={
        "lanes_count": 3,
        "initial_lane_id": 1,
        "vehicles_count": vehicles_count,
        "duration": duration_s,
        "simulation_frequency": 15,
        "policy_frequency": 5,
        "offroad_terminal": True,
        "observation": {
            "type": "Kinematics", "vehicles_count": 5,
            "features": list(FEATURES), "normalize": False, "clip": False,
            "absolute": False, "order": "sorted", "see_behind": True,
        },
        "action": {
            "type": "DiscreteMetaAction", "longitudinal": True, "lateral": True,
            "target_speeds": [20, 25, 30],
        },
        "screen_width": 720, "screen_height": 160,
        "offscreen_rendering": render_mode != "human",
        "real_time_rendering": render_mode == "human",
    })


def end_reason(*, crashed: bool, on_road: bool, terminated: bool,
               truncated: bool) -> str:
    """仅分类本次结束原因；时间用尽不等于驾驶成功。原始标志另存。"""
    if crashed:
        return "collision"
    if not on_road:
        return "off_road"
    if terminated:
        return "terminated"
    if truncated:
        return "environment_time_limit"
    return "runner_step_limit"


def code_revision() -> str:
    """证据绑定实际代码；不把未知版本伪装成 main。"""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT,
            text=True, stderr=subprocess.DEVNULL, timeout=5,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def run_episode(*, seed: int = 7, max_steps: int = 50,
                action_name: str = "IDLE", render_mode: str | None = "rgb_array",
                output_dir: Path | None = None, duration_s: float = 8.0,
                vehicles_count: int = 12) -> dict[str, Any]:
    validate_options(seed, max_steps, action_name, render_mode, duration_s, vehicles_count)
    if output_dir is not None:
        output_dir = Path(output_dir)
        # 绝不覆盖上一次实验，保证日志、截图属于同一回合。
        output_dir.mkdir(parents=True, exist_ok=False)
    env = make_env(render_mode=render_mode, duration_s=duration_s,
                   vehicles_count=vehicles_count)
    frames: list[Any] = []
    trace: list[dict[str, Any]] = []
    try:
        obs, _ = env.reset(seed=seed)
        initial_observation = obs.tolist()
        action_id = int(env.unwrapped.action_type.actions_indexes[action_name])
        if render_mode == "rgb_array" and output_dir is not None:
            from PIL import Image
            frames.append(Image.fromarray(env.render()))

        terminated = truncated = False
        for step in range(1, max_steps + 1):
            observation_time_s = float(env.unwrapped.time)
            available = action_id in env.unwrapped.action_type.get_available_actions()
            # 本轮是恒定动作基线，故意不依据 obs 决策；不是避碰策略。
            next_obs, reward, terminated, truncated, info = env.step(action_id)
            trace.append({
                "step": step, "observation_time_s": observation_time_s,
                "observation": obs.tolist(), "action_name": action_name,
                "action_id": action_id, "action_available": bool(available),
                "next_observation_time_s": float(env.unwrapped.time),
                "next_observation": next_obs.tolist(), "reward": float(reward),
                "speed_mps": float(info["speed"]),
                "crashed": bool(info["crashed"]),
                "on_road": bool(env.unwrapped.vehicle.on_road),
                "terminated": bool(terminated), "truncated": bool(truncated),
            })
            obs = next_obs
            if render_mode == "rgb_array" and output_dir is not None:
                frames.append(Image.fromarray(env.render()))
            if terminated or truncated:
                break  # 结束后不再 step，也不偷偷 reset 成第二个回合。

        last = trace[-1]
        summary = {
            "schema_version": 1, "environment": "highway-v0", "seed": seed,
            "policy": "constant_meta_action", "action_name": action_name,
            "action_id": action_id, "requested_max_steps": max_steps,
            "steps": len(trace), "sim_time_s": last["next_observation_time_s"],
            "terminated": bool(terminated), "truncated": bool(truncated),
            "crashed": last["crashed"], "on_road": last["on_road"],
            "end_reason": end_reason(crashed=last["crashed"], on_road=last["on_road"],
                                     terminated=terminated, truncated=truncated),
            "total_reward": sum(row["reward"] for row in trace),
            "initial_observation": initial_observation,
            "final_observation": obs.tolist(),
            "observation_contract": {
                "features": FEATURES, "position_unit": "m", "velocity_unit": "m/s",
                "ego_row": "absolute world position and velocity",
                "other_rows": "relative position and velocity; world-aligned axes",
                "padding": "presence=0 means absent, not a stationary vehicle",
                "normalize": False,
            },
            "config": env.unwrapped.config, "code_revision": code_revision(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python": platform.python_version(), "platform": platform.platform(),
            "packages": {name: version(name) for name in
                         ("highway-env", "gymnasium", "numpy", "pygame-ce", "Pillow")},
        }
        if output_dir is not None:
            (output_dir / "trace.jsonl").write_text(
                "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n"
                        for row in trace), encoding="utf-8")
            if frames:
                frames[0].save(output_dir / "initial.png")
                frames[-1].save(output_dir / "final.png")
                # GIF 仅记录策略时刻，不是模拟器内部每个物理帧。
                frames[0].save(output_dir / "episode.gif", save_all=True,
                               append_images=frames[1:], duration=200, loop=0)
            # 最后写 summary：有完整 summary 才代表这次保存流程结束。
            (output_dir / "summary.json").write_text(
                json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                encoding="utf-8")
        return summary
    finally:
        env.close()
        for frame in frames:
            frame.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--action", choices=ACTIONS, default="IDLE")
    parser.add_argument("--render", choices=("none", "rgb_array", "human"), default="rgb_array")
    parser.add_argument("--duration-seconds", type=float, default=8.0)
    parser.add_argument("--vehicles", type=int, default=12)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output = args.output_dir or ROOT / "outputs" / "highway_driving" / datetime.now(
        timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    try:
        result = run_episode(seed=args.seed, max_steps=args.max_steps,
                             action_name=args.action, render_mode=None if args.render == "none" else args.render,
                             output_dir=output, duration_s=args.duration_seconds,
                             vehicles_count=args.vehicles)
    except (ValueError, OSError, ImportError) as exc:
        print(f"实验未完成：{exc}\n依赖安装：python -m pip install -r "
              "experiments/highway_driving/requirements.txt", file=sys.stderr)
        return 1
    print("初始观察 [presence, x, y, vx, vy]：")
    print(json.dumps(result["initial_observation"], ensure_ascii=False))
    print(f"结束：{result['end_reason']}；决策步数={result['steps']}；"
          f"仿真时间={result['sim_time_s']:.3f}s；action={result['action_name']}")
    print(f"实验输出：{output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
