import gymnasium as gym
import highway_env
import numpy as np

env = gym.make(
    "highway-v0",
    config={
        "action": {"type": "ContinuousAction"},
        "vehicles_count": 0,
        "policy_frequency": 1
    },
)

try:
    env.reset(seed = 0)

    action = np.array([0.5,-0.2],dtype=np.float32)

    # 读取模拟器内部信息，仅用于验证源码
    control = env.unwrapped.action_type.get_action(action)
    speed_before = env.unwrapped.vehicle.speed
    time_before_s = float(env.unwrapped.time)

    obs, reward, terminated, truncated, info = env.step(action)

    print("动作空间：", env.action_space)
    print("原始归一化动作 [加速度输入, 转向输入]：", action, "（无量纲）")
    print("仿真时间：", round(time_before_s, 3), "→",
          round(float(env.unwrapped.time), 3), "秒")
    print("加速度：", round(control["acceleration"], 4), "m/s²")
    print("转向角：", round(control["steering"], 4), "弧度")
    print("执行前速度：", round(speed_before, 2), "m/s")
    print("执行后速度：", round(info["speed"], 2), "m/s")
    print("速度变化：", round(info["speed"] - speed_before, 2), "m/s")
finally:
    env.close()
