# 02｜一次 step、时间与重新观察

关联实践：[demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py) 主循环。当前操作与理解状态只看 [实践进度](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md)。本篇是材料，不是新增活跃任务。

源码依据：[caeee82 的 AbstractEnv](https://github.com/chasen2041maker/highwayenv-learning/blob/caeee8225d88f8092fbcf39a5ff02c59d35904ca/highway_env/envs/common/abstract.py)、[该版本 demo](https://github.com/chasen2041maker/highwayenv-learning/blob/caeee8225d88f8092fbcf39a5ff02c59d35904ca/demo.py)。

## 你不是只发一次命令，车就永远自己处理交通

reset 生成一个新回合的道路、车辆和初始观察。你的程序用当前 obs 选动作，step 执行动作并推进环境，然后返回新 obs、reward、terminated、truncated 和 info。

一个回路可以读成：

```text
现在看到的车辆状态 → 这次选的动作 → 世界往前运动一段时间
→ 新的车辆状态 → 再作下一次选择
```

前车也在移动，所以不能一直拿启动时的距离判断。当前 demo 每轮先遍历现有 obs，再用 step 返回的新 obs 覆盖旧值，这就是反馈。规则也可以使用反馈；不是只有神经网络才有这个回路。

## 一次 Python 循环不天然等于一秒

AbstractEnv.step 以 1 / policy_frequency 增加仿真时间，再进行模拟更新并生成新观察。

该实践版本默认 policy_frequency=1，所以一次决策间隔为 1 秒；simulation_frequency=15 表示更细的物理更新频率。两者分别回答“多久重新选动作”和“运动模拟分多细更新”，不是同一个设置。当前 15 与 1 的组合能整除；其他配置不能只看频率名字就假定内部推进完全一致，应核对实现。

vla_basic 保留的旧运行器配置为 5 Hz 决策、15 Hz 仿真，因此其决策步为 0.2 秒。不要把旧 H001 的 0.2 秒当成实践 demo 当前的一步。依据：[旧运行器固定版本](https://github.com/chasen2041maker/vla_basic/blob/4503a9cc9d0b67add5e85c28aa5d75e73f2725a7/experiments/highway_driving/run_episode.py)。

屏幕刷新、电脑实际等待多久和仿真时间是不同概念。解释车辆运动或比较策略时，要记录环境配置和仿真时刻，而不是仅看窗口流畅程度。

## reward 和结束标记不是同一个东西

reward 是当前环境定义的数值反馈，累计 reward 是把各步数值相加；它不是通用驾驶质量证书。当前 highway-v0 在碰撞等条件下 terminated，到达配置时限时 truncated；具体行为须按所用场景实现核对。

demo 的 range(300) 是脚本总循环预算，途中可以 reset 进入多局。若循环预算在某局中途用完，不应把该局记成“完整无碰撞成功”。手动中断、环境时间上限、碰撞和脚本步数上限也要分别说明。

来源：[highway-v0 结束与奖励实现](https://github.com/chasen2041maker/highwayenv-learning/blob/caeee8225d88f8092fbcf39a5ff02c59d35904ca/highway_env/envs/highway_env.py)、上述 demo。不同频率和回合时限下的累计奖励不能直接当作同条件对比。

## 与模型实验的连接

以后将手写规则换成模型，外层的观察—动作—执行—新观察仍要解释清楚。模型是否看到了最新状态、动作对应哪个时刻、日志是否把前后状态混在一起，都可能造成与模型本身无关的错误。

先能沿当前程序解释一个真实回合，再按实践需要加入有限记录；不在理论仓库新写 runner。返回 [对应表](../PRACTICE_MAP.md)，或继续 [03 观察与相对运动](03-observation-and-relative-motion.md)。
