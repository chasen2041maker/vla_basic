# Driving System Mental Model

这份文件是仓库的第一张地图。第一次进入任何局部代码前，先确定它位于整车链路的哪里。

## 1. 一条完整的智能驾驶闭环

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

## 8. 后续 Lab 如何映射到系统

| Lab | 主要系统边界 |
|---|---|
| 000 | 全链路与 failure localization |
| 001 | Data Contract & Alignment |
| 002 | Action / Motion / Control boundary |
| 003–004 | Sensor、Geometry、Representation |
| 005 | Model training and trajectory head |
| 006–007 | Evaluation and public benchmark |
| 008–009 | Driving VLM/VLA and action representation |
| 010 | Compression and deployment system |
| 011 | Safety / ODD / fallback / observability |
| 012 | Closed-loop learning, RL and world model |

局部知识只有放回这张图，才算真正理解。
