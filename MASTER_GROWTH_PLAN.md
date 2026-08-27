# Master Growth Plan

## 目标

建立一套可迁移的自动驾驶 VLA 工程能力，而不是完成固定教程。

主线必须始终回答：

```text
模型看到了什么？
这些输入是什么时间、什么坐标？
模型输出的 action 到底是什么？
action 怎样影响车辆状态？
如何证明行为正确？
失败发生在 data、model、decode、control 还是 eval？
```

---

# 能力轴

## 轴 A：Driving Foundations

- 时间戳与同步；
- 坐标系与 SE(2)；
- trajectory / waypoint / control；
- 运动学自行车模型；
- 轨迹可行性；
- 最低必要控制直觉。

## 轴 B：VLA & Model Engineering

- 多相机时序输入；
- ego-state / route conditioning；
- imitation learning；
- VLM / VLA；
- action token / continuous head；
- reasoning / implicit token；
- world model；
- fine-tuning / inference。

## 轴 C：Evaluation & Reliability

- contract validation；
- deterministic evaluator；
- open-loop；
- closed-loop / pseudo-simulation；
- failure taxonomy；
- ODD / safety monitor / fallback；
- latency / stale observation；
- reproducibility / observability。

三条轴不是三套独立课程。每个 lab 用一个真实问题同时推进。

---

# 阶段路线

## Stage 0 — Scope & Mental Model

### 必须理解

- 模块化自动驾驶、端到端驾驶、Driving VLM、Driving VLA、world model 的区别；
- 小鹏式量产方向只能作为架构参考；
- 公开复现主线应依赖公开代码、数据和评测。

### 证据

能画出：

```text
sensors + ego + route
→ representation / reasoning
→ trajectory
→ safety / control
→ environment
→ next observation
```

---

## Lab 001 — Driving Data Contract

### 核心问题

一条训练/推理样本到底表达什么事实？

### 内容

- sample / scene / history / future；
- camera timestamps；
- ego timestamp；
- future trajectory；
- units；
- coordinate frame；
- structural validity vs semantic validity；
- validation trace。

### 最小证据

- 运行 baseline；
- 找出两个 silent contract failures；
- 增加时间语义检查；
- tests 证明修复；
- 能解释为什么程序成功但样本无效。

---

## Lab 002 — SE(2), Bicycle Model & Trajectory

### 核心问题

未来轨迹如何表示，怎样改变车辆状态？

### 内容

- world ↔ ego；
- yaw；
- curvature；
- kinematic bicycle；
- rollout；
- waypoint spacing；
- horizon；
- trajectory vs control。

### 最小证据

- 手写并测试坐标变换；
- rollout 一条轨迹；
- 故意把 yaw 单位写错；
- 解释模型输出和执行器命令的边界。

---

## Lab 003 — Camera Time & BEV Mental Model

### 核心问题

多相机和历史帧如何形成同一个决策时刻的观测？

### 内容

- intrinsics / extrinsics；
- asynchronous cameras；
- ego-motion compensation；
- image / sensor / ego / BEV；
- stale observation；
- single-frame vs temporal。

### 最小证据

- 可视化时间轴；
- 检测 camera skew；
- 做一次 ego-motion compensation；
- 注入一帧延迟并解释影响。

---

## Lab 004 — Imitation-Learning Trajectory Baseline

### 核心问题

不用 VLA，最小模型能否从输入预测未来轨迹？

### 内容

- dataset split；
- normalized input / target；
- small encoder + trajectory head；
- overfit 32 samples；
- loss vs behavior；
- leakage checks。

### 最小证据

- 过拟合小样本；
- 可视化预测与真值；
- 故意用错 normalization；
- 新增一个 failure test。

---

## Lab 005 — Open-Loop vs Closed-Loop Evaluation

### 核心问题

为什么离线轨迹看起来不错，闭环仍会失败？

### 内容

- ADE / FDE；
- collision / progress / comfort；
- evaluator tests；
- compounding error；
- conservative policy；
- lightweight closed loop；
- pseudo-simulation mental model。

### 最小证据

- 同一策略跑两类评测；
- 构造开放环好、闭环差的案例；
- 解释指标投机；
- 给 evaluator 写单元测试。

---

## Lab 006 — NAVSIM Onboarding

### 核心问题

如何在公开自动驾驶评测栈中复现 baseline？

### 内容

- official data split；
- agent interface；
- trajectory output contract；
- PDMS / evaluation pipeline；
- environment version；
- data license；
- reproducible config。

### 最小证据

- 跑通 mini split；
- 记录 commit / environment / result；
- 可视化一条预测；
- 复现官方 baseline 的合理范围。

---

## Lab 007 — Driving VLM / VLA

### 核心问题

语言、视觉、状态和动作怎样进入统一模型？

### 内容

- visual tokens；
- route / instruction；
- ego-state token；
- action token；
- direct trajectory vs reasoning；
- fast / slow reasoning；
- conditioning ablation。

### 最小证据

- 跑通公开 checkpoint 或最小代理实验；
- 证明语言/route 是否影响输出；
- 无意义指令实验；
- 记录延迟和动作解码。

---

## Lab 008 — Action Representation

### 核心问题

离散 action token、连续回归、diffusion/flow 有何边界？

### 内容

- trajectory codebook；
- quantization error；
- multi-modality；
- action horizon；
- decode consistency；
- physical feasibility。

### 最小证据

- 编码/解码测试；
- 量化误差上界；
- 错 codebook 故障；
- 与任务精度对比。

---

## Lab 009 — Reasoning, World Models & Long Tail

### 核心问题

显式推理、隐式 token 和世界模型到底解决什么？

### 内容

- CoT / Chain-of-Causation；
- visual reasoning；
- implicit latent；
- future prediction；
- synthetic long-tail data；
- reasoning-action consistency；
- hallucinated rationale。

### 最小证据

- reasoning ablation；
- rationale 与 action 冲突案例；
- 合成长尾场景；
- 明确何种结果会推翻当前假设。

---

## Lab 010 — Safety Boundary & ODD

### 核心问题

端到端模型外面还需要哪些不可省略的边界？

### 内容

- ODD；
- trajectory safety checker；
- timeout；
- sensor missing；
- fallback；
- minimum-risk behavior；
- SOTIF mental model；
- evidence log。

### 最小证据

- 定义 allow / fallback / stop 条件；
- 注入过期观测；
- 注入不可行轨迹；
- 测误报和漏报。

---

## Lab 011 — Deployment & Observability

### 核心问题

模型怎样在延迟和资源约束下稳定运行？

### 内容

- preprocessing / inference / decode / control latency；
- batching；
- quantization；
- TensorRT / ONNX 的适用边界；
- model/data/config version；
- logs / metrics / traces；
- regression eval。

### 最小证据

- latency breakdown；
- overrun detection；
- before/after benchmark；
- 可复现实验清单；
- rollback 条件。

---

# 晋级标准

一个 Lab 进入 `PASSED` 至少需要：

```text
Reference 运行成功
+ 能画完整数据/执行链
+ 一个独立修改
+ 一个 failure experiment
+ tests / eval 证据
+ 能解释 trade-off
```

论文阅读、视频观看、README 运行成功都不能单独构成 `PASSED`。

---

# 当前阶段

```text
Lab 001A — Driving Data Contract Baseline
状态：LEARNING
```

精确任务：

- [`labs/001-driving-data-contract/CURRENT_TASK.md`](labs/001-driving-data-contract/CURRENT_TASK.md)
