# Master Growth Plan

## 目标

建立一套可迁移的自动驾驶 VLA 工程能力，而不是完成固定教程。

主线始终回答：

```text
系统现在看到了什么？
输入是什么时间、什么坐标？
模型输出的 action 到底是什么？
action 怎样经过安全和控制影响车辆？
如何证明行为正确？
失败位于 data、representation、model、decode、control、eval 还是 system？
```

---

# 路线总览

```text
Layer 0  System Orientation
Layer 1  Driving Foundations
Layer 2  Vision & Temporal Representation
Layer 3  End-to-End Model & Evaluation
Layer 4  Driving VLA & Action
Layer 5  Deployment, Safety & Closed-Loop Learning
```

课程按依赖和证据解锁，不按固定日期。

---

## Lab 000 — Driving System Map & Failure Boundaries

### 核心问题

一个驾驶模型如何从相机观测走到真实车辆运动？

### 内容

- sensor → data → representation → model → action → safety → control → environment → eval；
- 训练链与推理链；
- open loop 与 closed loop；
- failure localization；
- Agent 类比和物理世界失效点。

### 最小证据

- 能画完整系统图；
- 能说明每层输入、输出、职责和非职责；
- 能把 stale observation、unsafe trajectory、controller timeout 和 evaluator bug 放到正确边界；
- 运行 000A reference trace。

---

## Lab 001 — Driving Data Contract & Temporal Semantics

### 核心问题

一条训练或推理样本到底表达什么驾驶事实？

### 内容

- scene / frame / sample / history / future；
- reference time；
- camera / ego / trajectory timestamps；
- structural vs semantic validity；
- units、coordinate frame 和 validation trace。

### 最小证据

- 运行 4/6 intentional baseline；
- 找出 camera skew 与 future label in past；
- 增加时间语义检查；
- tests 证明 before/after；
- 解释程序成功为什么不等于样本正确。

---

## Lab 002 — Coordinate Frames, Trajectory & Vehicle Motion

### 核心问题

未来轨迹如何表示，怎样经过车辆运动模型改变状态？

### 内容

- world / ego；
- SE(2)、yaw 和单位；
- trajectory / waypoint / control；
- kinematic bicycle；
- rollout、horizon 和 feasibility。

### 最小证据

- 手写并测试坐标变换；
- rollout 一条轨迹；
- 注入 degree/radian 故障；
- 解释模型轨迹与执行器命令边界。

---

## Lab 003 — Camera Geometry

### 核心问题

二维像素与车辆周围空间如何关联？

### 内容

- image / camera / ego / world；
- intrinsics / extrinsics；
- projection、depth 和 field of view；
- calibration error；
- 教学级 2D/3D 可视化。

### 最小证据

- 投影和逆向射线实验；
- 坐标 round-trip test；
- 注入外参或单位错误；
- 解释数值合理但空间错误的症状。

---

## Lab 004 — Multi-Camera Temporal Modeling & BEV Mental Model

### 核心问题

异步多相机和历史帧如何形成同一个决策时刻的表征？

### 内容

- camera skew；
- history window；
- ego-motion compensation；
- feature/token fusion；
- BEV / occupancy 的输入输出和假设；
- stale observation。

### 最小证据

- 可视化多相机时间轴；
- 做一次运动补偿；
- 注入一帧延迟；
- 解释简单拼接为什么不等于空间融合。

---

## Lab 005 — End-to-End Trajectory Learning Baseline

### 核心问题

如何把已有深度学习能力迁移为一个可信的驾驶轨迹模型？

### 内容

- dataset split；
- image/feature + ego + route input；
- normalized target；
- temporal encoder + trajectory head；
- loss、leakage、overfit 和 inference contract。

### 最小证据

- 过拟合 32 个样本；
- 可视化预测与真值；
- 输入消融确实改变输出；
- 注入 normalization 或 future leakage 故障；
- 独立修改 head 或 loss。

---

## Lab 006 — Open-Loop vs Closed-Loop Evaluation

### 核心问题

为什么离线轨迹误差不错，车辆闭环仍可能失败？

### 内容

- ADE / FDE；
- safety / progress / comfort；
- evaluator tests；
- compounding error；
- distribution shift；
- lightweight closed loop。

### 最小证据

- 同一策略跑两类评测；
- 构造 open-loop 好、closed-loop 差案例；
- 证明 evaluator 本身正确；
- 输出 failure taxonomy。

---

## Lab 007 — Public Driving Stack / NAVSIM

### 核心问题

如何在公开自动驾驶栈中建立可复现 benchmark？

### 内容

- official split；
- agent interface；
- trajectory output contract；
- evaluation pipeline；
- environment / commit / config / license；
- mini-data reproducibility。

### 最小证据

- 跑通公开 mini split；
- 记录环境和 commit；
- 可视化一条预测；
- 复现合理 baseline 范围；
- 定位一次数据或评测问题。

---

## Lab 008 — Driving VLM / VLA

### 核心问题

视觉、状态、导航、语言和动作怎样进入统一模型？

### 内容

- visual token；
- temporal token；
- ego / route conditioning；
- VLM / VLA；
- direct trajectory vs reasoning；
- fast/slow path；
- public checkpoint or proxy experiment。

### 最小证据

- 跑通公开实现或最小代理；
- conditioning ablation；
- 无意义指令或冲突条件实验；
- 记录 action decode 与 latency；
- 解释 reasoning 正确但 action 错误的风险。

---

## Lab 009 — Action Representation

### 核心问题

离散 token、连续回归、diffusion/flow 轨迹头分别买来了什么？

### 内容

- trajectory codebook；
- quantization error；
- action horizon；
- multi-modality；
- continuous / token / diffusion / flow；
- decode consistency 与 feasibility。

### 最小证据

- encode/decode tests；
- 量化误差上界；
- 错 codebook 故障；
- 至少两类 action 表示对比。

---

## Lab 010 — Distillation, Quantization & Deployment

### 核心问题

怎样把大模型能力压到可运行系统，并证明行为没有被破坏？

### 内容

- teacher/student target；
- feature / logit / trajectory distillation；
- PTQ / QAT；
- token pruning；
- preprocessing / inference / decode latency；
- memory、throughput 和 stale deadline。

### 最小证据

- 一次驾驶任务蒸馏；
- 一次量化或剪枝；
- accuracy + behavior + latency + memory 对比；
- 弯道、长尾或小概率场景回归；
- 明确 rollback 条件。

---

## Lab 011 — Safety, ODD & Observability

### 核心问题

端到端模型外面哪些边界不可省略？

### 内容

- ODD；
- trajectory safety checker；
- timeout / stale / sensor missing；
- fallback / minimum-risk behavior；
- logs / metrics / trace；
- model/data/config version；
- regression gate。

### 最小证据

- 定义 allow / reject / fallback；
- 注入过期观测和不可行轨迹；
- 测误报、漏报和超时；
- 可复现一次线上式 failure trace。

---

## Lab 012 — Reinforcement Learning, World Model & Long Tail

### 核心问题

闭环强化学习和世界模型到底解决什么，何时值得增加复杂度？

### 前置条件

必须先理解并验证：

```text
state
+ action
+ transition / rollout
+ reward / metric
+ closed-loop evaluator
+ safety boundary
```

### 内容

- behavior cloning ceiling；
- offline / online RL mental model；
- reward design and reward hacking；
- PPO / DPO / GRPO 只按任务需要引入；
- controllable world model；
- synthetic long-tail data；
- sim-to-real / model bias；
- reasoning-action consistency。

### 最小证据

- 一个最小闭环 policy improvement 实验；
- reward hacking failure；
- world-model bias 或 rollout drift 实验；
- 明确何种证据会推翻当前方案。

---

# 横向能力线

以下内容不单独变成名词课，而是嵌入各 Lab：

- 数学：线性代数、概率、优化、几何；
- C++：数据结构、推理接口、性能和并发；
- 论文：问题、假设、方法、证据和复现边界；
- 工程：Linux、Git、CI、profiling、版本和可观测性；
- 沟通：系统图、实验报告、failure analysis 和 design decision。

---

# 晋级标准

一个 Lab 进入 `PASSED` 至少需要：

```text
系统位置解释
+ reference 运行成功
+ 完整数据 / 执行链
+ 一个独立修改
+ 一个 failure experiment
+ tests / eval 证据
+ trade-off 和失效边界
```

Lab 000A 是读取与系统定位任务，可在尚未修改代码时先通过 `READ` 小步；完整 Lab 000 仍需要后续故障定位证据。

---

# 当前阶段

```text
Lab 000A — Driving System Map Trace
状态：LEARNING
```

精确任务：

- [`labs/000-driving-system-map/CURRENT_TASK.md`](labs/000-driving-system-map/CURRENT_TASK.md)
