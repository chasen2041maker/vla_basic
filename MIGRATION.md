# Migration: Robot Manipulation VLA → Autonomous Driving VLA

## 为什么重构

旧版仓库的 VLA 指向：

```text
MuJoCo
机械臂
FK / IK
夹爪
pick-and-place
ACT / OpenVLA
SO-101
```

用户明确的目标则是类似小鹏汽车的自动驾驶 VLA：

```text
多相机时序视觉
自车状态
导航 / 语义条件
未来车辆轨迹
驾驶评测
安全与部署
```

两个方向共享“视觉、语言/语义、动作”的抽象，但数据、动作、仿真、评测和安全边界不同，因此不能在同一主线中混学。

## 旧内容在哪里

完整旧版保留在：

```text
archive/robot-manipulation-vla-2026-07
```

旧提交：

```text
2bff8713e215c919b027ee3f8ae434cfb58457d7
```

没有删除 Git 历史。

## 保留了什么

保留旧版最有价值的学习思想：

- 读懂 → 跑通 → 修改 → 制造失败 → 独立解释；
- 稳定知识与动态生态分离；
- 故障实验；
- 不把运行成功当成掌握；
- 明确类比失效点；
- 用证据更新进度。

## 替换了什么

- 机械臂本体 → 汽车；
- qpos / gripper → ego state / trajectory；
- FK / IK → SE(2) / bicycle model；
- MuJoCo → lightweight synthetic loop / NAVSIM / CARLA；
- OXE / LeRobot → nuPlan / NAVSIM 等驾驶生态；
- 抓取成功率 → safety / progress / comfort / trajectory metrics；
- SO-101 真机 → 公开数据、仿真、部署与安全边界；
- LLM tool orchestration 主线 → Driving VLM / VLA 与动作生成主线。
