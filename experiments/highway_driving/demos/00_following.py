import gymnasium as gym
import highway_env

SEED = 0  # 固定每局初态，便于比较亲手修改前后的规则；不代表覆盖多种路况。

def main(render_mode="human", max_steps=300):
    """默认显示原跟车练习；render_mode=None 可做无窗口短跑。"""
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 1:
        raise ValueError("max_steps 必须是正整数")
    # 创建高速公路场景，并显示窗口
    #env = gym.make("highway-v0", render_mode="human")
    env = gym.make(
        "highway-v0",
        render_mode=render_mode,
        config={
            "action": {
                "type": "DiscreteMetaAction",
                "target_speeds": [0, 5, 10, 15, 20, 25, 30],
            }
        },
    )
    episode = 1  # 当前是第几局
    total_reward = 0   # 这一局的累计得分
    steps_completed = 0
    episode_finished = False
    interrupted = False

    try:
        # 初始化车辆和道路；每局使用相同种子，方便同场景对照。
        obs, info = env.reset(seed=SEED)
        print("本次种子：", SEED, "；每局重置为相同初态。")

        for _ in range(max_steps):
            """
            # 随机选择驾驶动作
            action = 1

            # 逐辆检查附近的车，跳过第一行自己的车
            for presense, x, y, vx, vy in obs[1:]:
                distance = x * 200
                side_distance = y * 16

                if (presense == 1
                    and 0 < distance < 40
                    and abs(side_distance) < 2
                    and vx < 0):
                    action = 4
                    print("发现同车道出现慢车，发出减速指令！")
                    break
            """

            # 先当作没有观察到同车道前车
            nearest_distance = float('inf')

            # 找到观察范围内，同车道最近的前车
            for presense, x, y, vx, vy in obs[1:]:
                distance = x * 200
                side_distance = y * 16

                if presense == 1 and distance > 0 and abs(side_distance) < 2:
                    nearest_distance = min(nearest_distance,distance)

            # 根据最近前车的距离，选择动作
            if nearest_distance < 40:
                action = 4
                decision = "前车太近，减速"

            elif nearest_distance > 60:
                action = 3
                decision = "前方距离充足，加速"

            else:
                action = 1
                decision = "保持当前目标速度"

            print("决策前仿真时间：", round(env.unwrapped.time, 1), "秒")
            print("本轮判断用的前车距离：", round(nearest_distance, 1), "米")
            print(decision)

            # 让车辆执行动作
            obs, reward, terminated, truncated, info = env.step(action)
            steps_completed += 1
            episode_finished = bool(terminated or truncated)
            print("执行后仿真时间：", round(env.unwrapped.time, 1), "秒")
            print("执行后实际速度：", round(info["speed"] * 3.6, 1), "公里/小时")
            print("执行后目标速度：", env.unwrapped.vehicle.target_speed * 3.6, "公里/小时")
            total_reward += reward

            """"
            # 碰撞或时间到了，就重新开始
            if terminated or truncated:
                obs, info = env.reset()
                print("车辆观察数据：\n", obs)
            """

            if terminated or truncated:
                print("\n========== 本局成绩 ==========")
                print("第", episode, "局")

                if info["crashed"]:
                    print("结果：发生碰撞")
                else:
                    print("结果：到达本局时间上限")

                print("本局仿真时间：", round(env.unwrapped.time, 1), "秒")
                print("累计奖励：", round(total_reward, 2))
                print("==============================\n")

                # 还有预算才准备下一局；最后一步不 reset 掉真正的结束时刻。
                if steps_completed < max_steps:
                    episode += 1
                    total_reward = 0
                    episode_finished = False
                    obs, info = env.reset(seed=SEED)

    except KeyboardInterrupt:
        interrupted = True
    finally:
        stopped_at_s = float(env.unwrapped.time)
        env.close()

    stop_reason = "user_interrupt" if interrupted else "runner_step_limit"
    print("\n本次运行停止：", "手动停止" if interrupted else "用完脚本步数预算")
    print("当前第", episode, "局；仿真时间：", round(stopped_at_s, 1), "秒")
    print("本局状态：", "环境已结束" if episode_finished else "本局未完成")
    print("本次已返回的 step 次数：", steps_completed, "；环境结束不代表安全通过。")
    return {"seed": SEED, "steps": steps_completed, "episode": episode,
            "episode_time_s": stopped_at_s, "episode_finished": episode_finished,
            "stop_reason": stop_reason}


if __name__ == "__main__":
    main()
