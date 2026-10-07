# 智能驾驶系统全景（参考）

遇到“这段代码 / 这个模型在整个系统的哪一层”时来查。不是必读课程；入门讲解在[教材](../learning/BOOK.zh-CN.md)，当前任务看 [PROGRESS](../PROGRESS.md)。

## 1. 完整链路

一辆自动驾驶汽车从“看到”到“动起来”再到“变得更好”，大致经过这九层：

```text
真实道路与交通参与者
        ↓
[1] Sensor Capture 传感器采集
    相机等传感器在各自的时间采集观测
        ↓
[2] Data Contract & Alignment 数据契约与对齐
    校验字段、单位、时间戳、坐标系和新鲜度
        ↓
[3] Representation / Perception 表征与感知
    把像素变成视觉 token、BEV、occupancy 等场景表示
        ↓
[4] Prediction / Planning / VLA 预测与规划
    结合历史、自车状态和导航，输出未来轨迹或动作
        ↓
[5] Decode & Safety Boundary 解码与安全边界
    解码动作，检查时间、可行性、碰撞风险、ODD 和超时
        ↓
[6] Controller 控制器
    把目标轨迹变成转向、驱动、制动命令
        ↓
[7] Vehicle & Environment 车辆与环境
    车辆运动，其他交通参与者也在变化
        ↓
[8] Next Observation 下一次观测
    传感器看到已经改变的世界
        ↓
[9] Evaluation & Data Loop 评测与数据闭环
    记录安全、进度、舒适、延迟和失败样本，反馈到训练
```

所以：**模型输出格式正确 ≠ 轨迹安全 ≠ 控制器跟得上 ≠ 闭环驾驶成功。**

### 和本项目的对应

| 层 | 现在的 HighwayEnv 实验里是谁 | 教材 |
| --- | --- | --- |
| 1–3 传感器、对齐、感知 | 模拟器直接给车辆状态表，相当于“感知已经完美完成” | 第 2 章 |
| 4 规划 | 你写的规则（00 跟车）或固定动作（04 / 05） | 第 2 章 |
| 5 解码 | `DiscreteMetaAction` 把动作编号翻译成高层指令 | 第 3 章 |
| 6 控制器 | `ControlledVehicle.speed_control` / `steering_control` | 第 1、3 章 |
| 7 车辆与环境 | `Vehicle.step` 自行车模型；背景车用 IDM / MOBIL | 第 1、3 章，附录 A |
| 8 下一次观测 | `env.step` 返回的新 `obs` | 第 2 章 |
| 9 评测 | `run_episode.py` 记录器、05 对照报告；阶段 2 的批量评测 | 第 4 章 |

排查问题时只看相关的那一层：曲线不对先查目标、控制和时间；方向不对查坐标；报告结论不对查记录和评测。

---

## 2. 每一层负责什么

| 层 | 输入 | 输出 | 负责 | 不负责 | 常见失败 |
|---|---|---|---|---|---|
| Sensor Capture | 真实光线与车辆状态 | 带时间戳的原始观测 | 采集 | 判断驾驶意图 | 丢帧、曝光、时钟漂移 |
| Data Contract | 原始观测和标签 | 可解释、对齐的样本 | 时间、单位、坐标、字段 | 学习驾驶策略 | 相机错位、未来标签来自过去 |
| Representation | 图像与状态 | token / feature / BEV | 提取可用于决策的表征 | 保证最终动作安全 | 目标丢失、深度或时序错误 |
| Planning / VLA | 表征、历史、导航 | 轨迹或 action | 生成未来行为候选 | 直接驱动执行器 | 错路线、不可行轨迹、幻觉动作 |
| Decode / Safety | 模型输出和系统状态 | allow / fallback / reject | 解码、约束、超时与边界 | 替模型学会所有场景 | action 解码错、漏检危险 |
| Controller | 目标轨迹与车辆状态 | steering / throttle / brake | 跟踪轨迹 | 决定高层路线 | 振荡、跟踪误差、控制超时 |
| Vehicle / Environment | 控制命令 | 新车辆状态和新世界 | 真实物理演化 | 为旧动作保持世界不变 | 打滑、延迟、其他车交互 |
| Evaluation | trace、轨迹和结果 | 指标与失败分类 | 判断系统行为 | 自动证明因果 | evaluator bug、指标投机 |

---

## 3. 训练时和车辆运行时不是同一条链

### 训练时

```text
记录数据
→ 构造 history / future 样本
→ 模型预测
→ 与标签计算 loss
→ 反向传播
```

训练链最容易隐藏：

- future leakage；
- 时间或坐标错位；
- normalization 不一致；
- train / inference contract 不一致；
- loss 下降但行为指标变差。

### 推理与闭环时

```text
当前观测
→ 模型输出
→ 安全检查
→ 控制执行
→ 世界改变
→ 下一次观测
```

闭环链最容易隐藏：

- 延迟导致观测过期；
- 小误差逐步累积；
- 控制器无法跟踪模型轨迹；
- 一个动作改变后续数据分布；
- fallback 触发条件错误。

---

## 4. 四个必问问题

看到任何驾驶变量、模型或指标，先问：

```text
1. 这个值是什么时间的？
2. 这个值在哪个坐标系？
3. 这个 action 是未来轨迹、离散 token，还是单步控制？
4. 这个结果来自开放环、伪闭环，还是真正交互闭环？
```

如果四个问题没有答案，暂时不能相信实验结论。

---

## 5. 一个最小例子

设决策参考时刻是 `t0 = 5000 ms`：

```text
front camera      5000 ms
front-left camera 4750 ms
front-right       5010 ms
ego state          5000 ms
future trajectory 5100, 5200, 5300 ms
```

程序能把这些值装进对象，但左前相机已经旧了 250 ms。假设车辆速度为 8 m/s，车辆在这段时间可移动约 2 m。

错误应该在：

```text
Data Contract & Alignment
```

被发现，而不是寄希望于模型、控制器或 evaluator 自动修复。

再设模型输出：

```text
trajectory timestamps = 4900, 5100, 5200 ms
```

它内部严格递增，但第一点位于参考时刻之前。这个错误至少应该在：

```text
Data Contract（训练标签）
或 Decode & Safety（推理输出）
```

被拒绝。

---

## 6. 故障定位：按层排查

面对“车开得不好”，不要直接归因于模型不够大。按边界排查：

```text
Data
字段、时间、坐标、单位、切分、泄漏是否正确？
        ↓
Model
输入是否被使用？loss 是否对应任务？是否过拟合或欠拟合？
        ↓
Action / Decode
模型输出含义和解码是否一致？horizon、单位、codebook 是否正确？
        ↓
Safety / Control
轨迹是否可行？控制器是否跟得上？fallback 是否及时？
        ↓
Evaluation
指标和实现是否正确？开放环与闭环是否被混淆？
        ↓
System
观测是否过期？延迟、吞吐、版本和日志是否可复现？
```

---

## 7. 与 Agent 工程的连接和失效点

有用的类比：

```text
工具调用返回 200
≠ 用户任务完成

模型返回合法 trajectory
≠ 驾驶任务成功
```

类比失效点：

- Agent retry 时外部状态有时基本不变；车辆 retry 前已经继续移动；
- 文本错误通常可以撤回；物理动作可能不可逆；
- Agent latency 影响体验；驾驶 latency 可能直接改变安全边界；
- 多个工具输出不一致可以重新查询；多相机错位可能已进入训练数据并长期污染模型。

---

---

## 附录：工程原则

这些原则比具体模型和框架更稳定。按需查阅，不用背。

### A1. System Map Before Local Abstraction

先知道一段代码位于 sensor、data、representation、model、action、safety、control、eval 还是 system，再讨论类和函数。

### A2. Data Contract Before Model

先说清输入、标签、单位、时间和坐标，再讨论模型结构。

### A3. Time Is Part of the Type

`image` 不够。应当知道：

```text
image_captured_at_1020ms
ego_state_at_1000ms
trajectory_from_1100ms_to_3000ms
```

错位通常不会报错，只会让行为变差。

### A4. Coordinate Frame Is Part of the Variable Name

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

### A5. Trajectory Is Not Control

VLA 输出未来轨迹或动作表示，不等于直接向转向、制动和驱动执行器下发命令。规划层和控制层有不同职责、频率和失败模式。

### A6. Training Success Is Not Driving Success

loss 下降、checkpoint 保存和 validation metric 提升，都不自动证明车辆行为正确。必须检查标签、action decode、行为指标和闭环反馈。

### A7. Baseline Before Foundation Model

先用小模型和 mini 数据证明：

- 数据能读；
- 标签对齐；
- loss 能降；
- 小样本能过拟合；
- 输入消融有效；
- evaluator 正确。

否则大模型只会放大归因困难。

### A8. Open-Loop Is Not Closed-Loop

记录数据上的轨迹误差，不等于车辆在交互环境中的安全和完成度。两类指标必须分开记录。

### A9. Evaluator Is Production Code

错误 evaluator 会让所有实验结论失效。评测代码必须有测试、版本、故障样本和指标投机检查。

### A10. Reasoning Text Is Not a Safety Proof

CoT、视觉草图或隐式 token 可以帮助决策，但不能替代轨迹可行性、安全检查、ODD 和 fallback。

### A11. A Valid Output Can Still Be a Failed Task

模型总能生成格式合法轨迹，但轨迹可能：

- 碰撞；
- 驶出可行驶区域；
- 违反运动约束；
- 与导航目标无关；
- 来自过期观测；
- 无法被控制器稳定跟踪。

### A12. Physical Retry Changes the World

后端重试常假设前置状态大致不变。车辆继续前进后，观测、距离和其他交通参与者已经变化，不能原样重放旧动作。

### A13. Compression Must Preserve Behavior, Not Only Accuracy

蒸馏、量化和 token pruning 不能只报告平均精度。还要检查弯道、长尾、安全、latency、memory 和 deadline。

### A14. Tool Assistance Is Not Epistemic Delegation

Coding Agent 可以生成实现，但不能替代对时间、坐标、动作、评测和系统边界的判断。关键 debug 必须能够脱离 Agent 完成。

### A15. Closed Systems Are References, Not Reproduction Targets

量产闭源系统可以用于理解方向，但只有公开代码、数据、权重和评测才可作为复现实验。

### A16. Complexity Must Buy Evidence

加入 world model、RL、BEV、multi-agent、分布式平台或大模型前，必须说明：

```text
它解决哪个已测量瓶颈？
替代方案是什么？
新增风险是什么？
如何验证收益？
什么结果会推翻方案？
```
