"""实验 04：同一窗口观察道路与速度；直接设置内部目标，仅用于诊断控制过程。"""
import math
import os
from pathlib import Path

TARGET_SPEED = 10.0  # m/s：本人已从原版 20 改为 10；保留当前实验值。


def run_demo(target_speed=None, headless=False, snapshot_path=None):
    """未指定目标时使用文件顶部当前值；无窗口可保存画面并返回真实记录。"""
    if target_speed is None:
        target_speed = TARGET_SPEED
    if not math.isfinite(target_speed) or not 0 <= target_speed <= 30:
        raise ValueError("本示例目标速度需在 0–30 m/s 内，与图表范围一致")
    previous_sdl = {key: os.environ.get(key) for key in ("SDL_VIDEODRIVER", "SDL_AUDIODRIVER")}
    import gymnasium as gym
    import highway_env
    import pygame

    env = gym.make("highway-v0", render_mode="rgb_array", config={
        "lanes_count": 3, "initial_lane_id": 1, "vehicles_count": 0,
        "duration": 8, "simulation_frequency": 15, "policy_frequency": 5,
        "action": {"type": "DiscreteMetaAction"},
        "screen_width": 960, "screen_height": 210,
        "offscreen_rendering": True, "real_time_rendering": False,
    })
    records = []

    def record(event):
        vehicle = env.unwrapped.vehicle
        records.append({
            "time_s": round(float(env.unwrapped.time), 10), "event": event,
            "speed_mps": float(vehicle.speed),
            "target_speed_mps": float(vehicle.target_speed),
            "x_world_m": float(vehicle.position[0]), "y_world_m": float(vehicle.position[1]),
        })  # 内部实际速度与世界坐标位置，未归一化；不是视觉感知结果。

    def road_image():
        frame = env.render()
        viewer = env.unwrapped.viewer
        if viewer.offscreen and not viewer.enabled:
            viewer.enabled = True  # SDL dummy 下恢复离屏绘制，不创建窗口。
            frame = env.render()
        if frame is None or (frame == frame[0, 0]).all():
            raise ValueError("道路画面为空，不能作为有效回放")
        return pygame.surfarray.make_surface(frame.swapaxes(0, 1))

    try:
        if headless:
            os.environ.update(SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        env.reset(seed=0)  # 当前 highway-v0 自车初始速度为 25 m/s。
        record("initial")
        road = road_image()  # 先创建离屏 viewer，再创建我们自己的窗口。
        screen = pygame.Surface((960, 670)) if headless else pygame.display.set_mode((960, 670))
        pygame.display.set_caption("Target speed and actual motion")
        font = pygame.font.Font(None, 24)
        title_font = pygame.font.Font(None, 32)
        clock = pygame.time.Clock()
        idle = env.unwrapped.action_type.actions_indexes["IDLE"]
        steps, paused, finished, running = 0, False, False, True
        next_step_ms = pygame.time.get_ticks() + 200

        def text(label, x, y, color=(222, 230, 240), title=False):
            screen.blit((title_font if title else font).render(label, True, color), (x, y))

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    paused = not paused
                    next_step_ms = pygame.time.get_ticks() + 200
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    env.reset(seed=0)
                    records.clear()
                    record("initial")
                    steps, paused, finished = 0, False, False
                    next_step_ms = pygame.time.get_ticks() + 200
            if not running:
                break
            if not paused and not finished and (headless or pygame.time.get_ticks() >= next_step_ms):
                if steps == 10:  # 已推进 2 秒；目标先改变，实际状态与时间还没变。
                    env.unwrapped.vehicle.target_speed = float(target_speed)
                    record("target_changed")  # 同时间保留前后样本，让目标曲线出现竖直阶跃。
                _, _, terminated, truncated, _ = env.step(idle)
                steps += 1
                record("motion")  # 每次 step 推进 0.2 秒，内部有 3 次控制与物理更新。
                finished = terminated or truncated or steps >= 40
                next_step_ms = pygame.time.get_ticks() + 200
            road = road_image()
            screen.fill((16, 24, 39))
            text("Target speed and actual motion", 24, 14, title=True)
            text("Internal target diagnostic | IDLE throughout | No traffic", 24, 47, (160, 177, 199))
            current = records[-1]
            state = "Finished - R to replay" if finished else "Paused" if paused else "Running"
            text(f"t = {current['time_s']:.1f} s    actual = {current['speed_mps']:.2f} m/s    "
                 f"target = {current['target_speed_mps']:.1f} m/s    {state}", 24, 77)
            screen.blit(road, (0, 108))
            text("Speed (m/s)", 24, 341)
            text("Target", 704, 341, (255, 185, 78))
            text("Actual", 820, 341, (71, 217, 190))
            # 固定坐标轴：横轴仿真 0–8 秒，纵轴 0–30 m/s，保留完整历史。
            for speed in range(0, 31, 5):
                y = 586 - speed * 7
                pygame.draw.line(screen, (48, 61, 79), (70, y), (924, y))
                text(str(speed), 35, y - 9, (155, 172, 192))
            for second in range(9):
                x = 70 + second * 854 / 8
                pygame.draw.line(screen, (35, 47, 64), (x, 376), (x, 586))
                text(str(second), x - 4, 596, (155, 172, 192))
            text("Time (s)", 837, 619, (155, 172, 192))
            for key, color in (("target_speed_mps", (255, 185, 78)), ("speed_mps", (71, 217, 190))):
                points = [(70 + row["time_s"] * 854 / 8, 586 - row[key] * 7) for row in records]
                if len(points) > 1:
                    pygame.draw.lines(screen, color, False, points, 3)
                pygame.draw.circle(screen, color, points[-1], 4)
            text("Space: pause/resume    R: restart    Esc / X: close", 24, 641)
            if headless and finished:
                break
            if not headless:
                pygame.display.flip()
                clock.tick(60)  # 暂停或结束后仍处理按键，但不推进仿真。
        if snapshot_path is not None:
            path = Path(snapshot_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(screen, str(path))
        return records
    finally:
        env.close()
        pygame.quit()
        if headless:
            for key, old_value in previous_sdl.items():
                if old_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = old_value


if __name__ == "__main__":
    run_demo(target_speed=TARGET_SPEED)
