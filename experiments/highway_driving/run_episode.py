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


def capture_frame(env: Any) -> Any:
    """保存真实画面，而不是只检查 PNG 文件能否创建。"""
    from PIL import Image

    frame = env.render()  # 首次调用同时创建 viewer。
    viewer = env.unwrapped.viewer
    if viewer.offscreen and not viewer.enabled:
        # HighwayEnv 1.12.1 在 SDL dummy 下会关闭全部绘制，造成合法但全黑的图片。
        # 仅恢复离屏画布绘制，offscreen=True 仍不创建桌面窗口。
        # 上游升级后须复核此兼容点，tests 会检查非空白画面和帧变化。
        viewer.enabled = True
        frame = env.render()
    if frame is None or (frame == frame[0, 0]).all():
        raise ValueError("渲染得到空白画面，不能作为有效回放保存")
    return Image.fromarray(frame)


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


def format_teaching_summary(summary: dict[str, Any]) -> str:
    """只展示第一条真实 transition；不能把首步动作与整回合末状态混在一起。"""
    row = summary["first_transition"]
    before = row["observation"][0]
    after = row["next_observation"][0]
    return "\n".join([
        "H001 教学摘要（仅第 1 步，不是整回合）：",
        f"动作：{row['action_name']}；请求可用={row['action_available']}",
        f"仿真时间 (s)：{row['observation_time_s']:.3f} → "
        f"{row['next_observation_time_s']:.3f}",
        f"自车世界位置 (m)：({before[1]:.3f}, {before[2]:.3f}) → "
        f"({after[1]:.3f}, {after[2]:.3f})",
        # speed 是速率，不用世界 x 轴速度分量 vx 冒充转弯时的实际速率。
        f"实际速率 (m/s)：{row['speed_before_mps']:.3f} → {row['speed_mps']:.3f}",
        f"目标速度 (m/s，模拟器诊断)：{row['target_speed_before_mps']:.3f} → "
        f"{row['target_speed_after_mps']:.3f}",
        f"本步环境标志：terminated={row['terminated']}；truncated={row['truncated']}",
        f"整回合结束原因：{summary['end_reason']}；共 {summary['steps']} 步；"
        f"总仿真时间={summary['sim_time_s']:.3f}s",
        "说明：目标速度不是策略观察；可用不等于安全；显示值已舍入，精确值见 trace.jsonl。",
    ])


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
            frames.append(capture_frame(env))

        terminated = truncated = False
        for step in range(1, max_steps + 1):
            observation_time_s = float(env.unwrapped.time)
            available = action_id in env.unwrapped.action_type.get_available_actions()
            speed_before_mps = float(env.unwrapped.vehicle.speed)
            # 仅供老师对照控制器目标与实际运动；不传入策略，不改变 observation。
            target_speed_before_mps = float(env.unwrapped.vehicle.target_speed)
            # 本轮是恒定动作基线，故意不依据 obs 决策；不是避碰策略。
            next_obs, reward, terminated, truncated, info = env.step(action_id)
            trace.append({
                "step": step, "observation_time_s": observation_time_s,
                "observation": obs.tolist(), "action_name": action_name,
                "action_id": action_id, "action_available": bool(available),
                "next_observation_time_s": float(env.unwrapped.time),
                "next_observation": next_obs.tolist(), "reward": float(reward),
                "speed_before_mps": speed_before_mps,
                "speed_mps": float(info["speed"]),
                "target_speed_before_mps": target_speed_before_mps,
                "target_speed_after_mps": float(env.unwrapped.vehicle.target_speed),
                "crashed": bool(info["crashed"]),
                "on_road": bool(env.unwrapped.vehicle.on_road),
                "terminated": bool(terminated), "truncated": bool(truncated),
            })
            obs = next_obs
            if render_mode == "rgb_array" and output_dir is not None:
                frames.append(capture_frame(env))
            if terminated or truncated:
                break  # 结束后不再 step，也不偷偷 reset 成第二个回合。

        last = trace[-1]
        summary = {
            "schema_version": 2, "environment": "highway-v0", "seed": seed,
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
            # 与 trace.jsonl 第一行完全相同，不拼接最后一步的速度或位置。
            "first_transition": trace[0],
            "diagnostic_contract": {
                "source": "simulator internals; diagnostics only, not policy inputs",
                "speed_before_mps": "ego speed magnitude before step",
                "speed_mps": "ego speed magnitude after step (existing field)",
                "target_speed_before_mps": "controller target before step",
                "target_speed_after_mps": "controller target after step",
            },
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
    print(format_teaching_summary(result))
    print(f"结束：{result['end_reason']}；决策步数={result['steps']}；"
          f"仿真时间={result['sim_time_s']:.3f}s；action={result['action_name']}")
    print(f"实验输出：{output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
