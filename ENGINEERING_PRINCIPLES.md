# Engineering Principles

这些原则比具体模型和框架更稳定。

## 1. Data Contract Before Model

先说清输入、标签、单位、时间和坐标，再讨论模型结构。

## 2. Time Is Part of the Type

`image` 不够。应当知道：

```text
image_at_1020ms
ego_state_at_1000ms
trajectory_from_1100ms_to_3000ms
```

错位一帧通常不会报错，只会让行为变差。

## 3. Coordinate Frame Is Part of the Variable Name

优先：

```text
target_xy_in_ego_m
trajectory_in_world
yaw_in_ego_rad
```

避免：

```text
position
target
angle
```

数值合理不代表坐标正确。

## 4. Trajectory Is Not Control

VLA 输出未来轨迹，不等于直接向转向、制动和驱动执行器下发命令。规划层与控制层有不同职责和时间尺度。

## 5. Baseline Before Foundation Model

先用小模型和少量合成/mini 数据证明：

- 数据能读；
- 标签对齐；
- loss 能降；
- 32 个样本能过拟合；
- evaluator 正确。

否则大模型只会放大归因困难。

## 6. Open-Loop Is Not Closed-Loop

记录数据上的轨迹误差，不等于车辆在交互环境中的安全和完成度。两类指标必须分开记录。

## 7. Evaluator Is Production Code

错误 evaluator 会让所有实验结论失效。评测代码必须有测试、版本和故障样本。

## 8. Reasoning Text Is Not a Safety Proof

CoT、视觉草图或隐式 token 可以帮助决策，但不能替代轨迹可行性、安全检查、ODD 和 fallback。

## 9. A Valid Output Can Still Be a Failed Task

模型总能生成格式合法轨迹，但轨迹可能：

- 碰撞；
- 驶出可行驶区域；
- 违反动力学约束；
- 与导航目标无关；
- 来自过期观测。

格式成功不等于驾驶成功。

## 10. Physical Retry Changes the World

后端重试常假设前置状态不变。车辆继续前进后，观测、距离和其他交通参与者都已变化。不能原样重放旧动作。

## 11. Closed Systems Are References, Not Reproduction Targets

量产闭源系统可以用于理解方向，但只有公开代码、数据、权重和评测才可作为复现实验。

## 12. Complexity Must Buy Evidence

加入 world model、RL、BEV、multi-agent、Kafka、Kubernetes 或 10B 模型前，必须说明它解决哪个已测量瓶颈，以及如何验证收益。
