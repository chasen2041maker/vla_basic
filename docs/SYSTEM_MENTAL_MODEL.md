# 智能驾驶是怎样让车动起来的

这是按需查询的系统参考。第一次阅读请打开 [连续教材 BOOK.zh-CN.md](../learning/BOOK.zh-CN.md)，相关代码与解释已放在同一章；本文件不再作为必读第一课。

查系统位置时，把概念接回已经能运行的东西：04 调速展示“目标→控制→运动”，00 跟车展示“观察→规则→新观察”，01 变道展示“车道请求→转向→位置”，05 展示“真实执行→记录→对照”。对应运行命令统一在[实验入口](../experiments/highway_driving/demos/README.md)，本人当前任务只查 [PROGRESS](../PROGRESS.md)。相机、模型和部署的系统框图用于解释位置，当前还没有相应完整实验，不能把框图当实现。

## 1. 先看一辆车怎样完成一次调整

比如前车变慢了，我们希望自己的车也慢下来。整个过程可以先理解成：

```text
获取周围情况 → 决定怎样开 → 计算怎样调速、转向 → 车辆运动 → 再看新的情况
```

其中“控制器”是一段程序：知道车现在怎样，也知道希望车怎样，然后计算应该怎样调整。它后面的车辆运动需要时间；一次决定之后，还要看车实际变成了什么样。

真实车辆用传感器获取信息。当前练习里，HighwayEnv 模拟器直接提供车辆状态，我们先借它学习“决定怎样开”和“怎样执行”。它省去了相机感知这部分工作，后面课程还会补齐。

下面只用减速这一个例子理解，不同时展开其他模块。

### 1.1 实际速度是 25，目标是 20，车会怎样变化？

**实际速度**是车现在开多快；**目标速度**是希望它达到多快。

假设某一时刻，车正在以 25 m/s 行驶，我们把目标设为 20 m/s。这里的 m/s 就是米/秒，两种速度使用相同单位；它们分别相当于 90 和 72 公里/小时。

你的判断应该是：**车要从 25 往下降，逐渐接近 20。** 在正常减速过程中，这就是我们希望看到的现象。

#### 把这个过程按先后顺序拆开

| 看的是哪个时候 | 程序或车辆正在做什么 | 实际速度与目标 |
| --- | --- | --- |
| 刚保存目标，还没执行运动 | 把“希望达到的速度”记为 20 | 实际仍是 25，目标是 20 |
| 接下来计算怎样减速 | 控制器发现实际速度高于目标，计算减速指令 | 算出指令本身还没有推进运动 |
| 车辆运动了一小段时间以后 | 模拟器根据指令更新速度，再把新速度交给控制器继续调整 | 实际速度开始下降，逐渐接近 20 |

所以，“刚设置目标的那一瞬间，实际还是 25”和“接下来实际速度会往 20 降”说的是两个不同时间，都是这个过程的一部分。先前的问题没有把截取的时间点说清楚，不应据此认定你没理解减速。

**如果已经调用了 `env.step(action)`，情况就不同了：它通常已经推进了一段仿真时间，返回的实际速度可能已经下降。** 不能把“刚保存目标、尚未推进运动”的答案照搬到一步运行之后；届时要看动作、时间和真实输出。

#### 谁负责让它往下降？

在当前模拟器里，控制器先根据“实际太快了”计算减速所需的加速度指令，然后运动模型用这个指令推进速度和位置。控制器再读取更新后的实际速度，继续调整。

```text
目标是 20，实际是 25
        ↓
控制器：实际比目标快，需要减速
        ↓
运动模型：经过一小段时间，更新实际速度
        ↓
控制器：再看看实际速度离目标还有多少
```

这里的数字是解释用的假设，没有新跑一次实验，也没有宣称具体多久会达到 20。只保存一个目标、不让后面的控制和运动执行，车就不会因为这个目标变量而自动减速。

#### 再把两个名字认出来

```python
speed = 25         # 实际速度：现在开多快，单位 m/s
target_speed = 20  # 目标速度：希望达到多快，单位 m/s
```

上面只是变量含义示意，不是需要新建文件运行的完整程序。你已经说出了“目标是 20，实际从 25 往下降”，这一点可以记录为本人的理解；接下来结合控制器与运动的先后顺序继续学，不必反复回答同一道数字题。

<details>
<summary>稍后看源码时再展开：这两个值保存在什么地方</summary>

对应 [controller.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/vehicle/controller.py) 的 `ControlledVehicle.__init__()`，第 35–48 行：

```python
super().__init__(road, position, heading, speed)
self.target_lane_index = target_lane_index or self.lane_index
self.target_speed = target_speed or self.speed
self.route = route
```

第一行初始化当前状态；随后保存目标。这段没有调用运动更新。这里的 `or` 是真值选择，传入目标速度 0 时也会回退到当前速度；这个边界留到源码带读解释，不需要为了第一遍理解减速先掌握它。它也不意味着其他路径不能设置零目标。

车道、位置和朝向是后续变道时要看的信息：车道索引是路段和车道编号；位置是世界坐标中的米，朝向用弧度。现在先分清速度与目标，暂不把这些都塞进同一小节。

后续通过 [主项目的变道示例](../experiments/highway_driving/demos/01_lane_change.py) 看同样的“目标先改变、实际逐渐变化”。当前进度只记在 [PROGRESS.md](../PROGRESS.md)。

</details>

<details>
<summary>系统参考：后面各个模块对应的完整链路</summary>

原系统链路，供后续按模块查阅：

```text
真实道路与交通参与者
        ↓
[1] Sensor Capture
相机等传感器在不同时间采集观测
        ↓
[2] Data Contract & Alignment
校验字段、单位、时间戳、坐标系和新鲜度
        ↓
[3] Representation / Perception
把像素转为视觉 token、BEV、occupancy 或其他场景表征
        ↓
[4] Prediction / Planning / VLA
结合历史、自车状态和导航，输出未来轨迹或动作表示
        ↓
[5] Decode & Safety Boundary
解码 action，检查时间、可行性、碰撞风险、ODD 和超时
        ↓
[6] Controller
把目标轨迹转换为转向、驱动和制动命令
        ↓
[7] Vehicle & Environment
车辆运动，环境和其他交通参与者继续变化
        ↓
[8] Next Observation
传感器再次看到已经改变的世界
        ↓
[9] Evaluation & Data Loop
记录安全、进度、舒适度、延迟和失败样本，反馈训练
```

这条链同时解释了为什么：

```text
模型输出格式正确
≠ 轨迹安全
≠ 控制器跟得上
≠ 闭环驾驶成功
```

---


</details>

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

## 4. 四个强制问题

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

## 6. Failure localization

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

## 8. 怎样回到项目里的实际问题

本文件不维护另一套未来 Lab 编号或通关顺序。当前实验对应上述观察、动作、控制、运动和记录；后续怎样复用日志、补数据与几何、训练模型、接视觉和部署，统一看[教材书末的项目衔接](../learning/BOOK.zh-CN.md#project-continuity)。

遇到问题时只取相关边界：曲线不符合预期，先查目标、控制和时间；轨迹方向不对，再查坐标；报告结论不对，再查记录与评测。旧专项实现留在 archive 按需提取，不要求先学完整个系统图再继续当前实验。

---

## 附录：工程检查原则

按具体任务查阅，不作为初学者逐项背诵或通关要求。

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
