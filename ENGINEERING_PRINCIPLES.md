# Engineering Principles

这些原则比具体模型和框架更稳定。

## 1. System Map Before Local Abstraction

先知道一段代码位于 sensor、data、representation、model、action、safety、control、eval 还是 system，再讨论类和函数。

## 2. Data Contract Before Model

先说清输入、标签、单位、时间和坐标，再讨论模型结构。

## 3. Time Is Part of the Type

`image` 不够。应当知道：

```text
image_captured_at_1020ms
ego_state_at_1000ms
trajectory_from_1100ms_to_3000ms
```

错位通常不会报错，只会让行为变差。

## 4. Coordinate Frame Is Part of the Variable Name

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

## 5. Trajectory Is Not Control

VLA 输出未来轨迹或动作表示，不等于直接向转向、制动和驱动执行器下发命令。规划层和控制层有不同职责、频率和失败模式。

## 6. Training Success Is Not Driving Success

loss 下降、checkpoint 保存和 validation metric 提升，都不自动证明车辆行为正确。必须检查标签、action decode、行为指标和闭环反馈。

## 7. Baseline Before Foundation Model

先用小模型和 mini 数据证明：

- 数据能读；
- 标签对齐；
- loss 能降；
- 小样本能过拟合；
- 输入消融有效；
- evaluator 正确。

否则大模型只会放大归因困难。

## 8. Open-Loop Is Not Closed-Loop

记录数据上的轨迹误差，不等于车辆在交互环境中的安全和完成度。两类指标必须分开记录。

## 9. Evaluator Is Production Code

错误 evaluator 会让所有实验结论失效。评测代码必须有测试、版本、故障样本和指标投机检查。

## 10. Reasoning Text Is Not a Safety Proof

CoT、视觉草图或隐式 token 可以帮助决策，但不能替代轨迹可行性、安全检查、ODD 和 fallback。

## 11. A Valid Output Can Still Be a Failed Task

模型总能生成格式合法轨迹，但轨迹可能：

- 碰撞；
- 驶出可行驶区域；
- 违反运动约束；
- 与导航目标无关；
- 来自过期观测；
- 无法被控制器稳定跟踪。

## 12. Physical Retry Changes the World

后端重试常假设前置状态大致不变。车辆继续前进后，观测、距离和其他交通参与者已经变化，不能原样重放旧动作。

## 13. Compression Must Preserve Behavior, Not Only Accuracy

蒸馏、量化和 token pruning 不能只报告平均精度。还要检查弯道、长尾、安全、latency、memory 和 deadline。

## 14. Tool Assistance Is Not Epistemic Delegation

Coding Agent 可以生成实现，但不能替代对时间、坐标、动作、评测和系统边界的判断。关键 debug 必须能够脱离 Agent 完成。

## 15. Closed Systems Are References, Not Reproduction Targets

量产闭源系统可以用于理解方向，但只有公开代码、数据、权重和评测才可作为复现实验。

## 16. Complexity Must Buy Evidence

加入 world model、RL、BEV、multi-agent、分布式平台或大模型前，必须说明：

```text
它解决哪个已测量瓶颈？
替代方案是什么？
新增风险是什么？
如何验证收益？
什么结果会推翻方案？
```
