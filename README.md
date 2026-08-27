# Autonomous Driving VLA Learning Lab

这是一个面向 **自动驾驶 VLA / 端到端规划 / Physical AI Engineering** 的长期实战学习仓库。

这里的 VLA 指的是接近小鹏汽车智能驾驶方向的：

```text
历史多相机视觉
+ 自车状态
+ 导航 / 语义条件
        ↓
时序视觉表征 / 显式推理 / 隐式 token
        ↓
未来自车轨迹或动作表示
        ↓
安全检查、控制与闭环评测
```

它**不是**桌面机械臂的抓取、夹爪、FK/IK、SO-101 或 pick-and-place 教程。

旧版机器人操作 VLA 内容已完整保留在分支：

```text
archive/robot-manipulation-vla-2026-07
```

---

## 当前定位

学习者已经具备 Python、RAG、Agent/workflow、tool calling 和 AI Coding 的实际经验，但自动驾驶数据、车辆运动、轨迹规划、闭环评测和驾驶 VLA 仍需要从工程基础建立。

因此本仓库不会：

- 从 Python 语法重新开始；
- 按论文年份堆模型名字；
- 一上来训练大模型；
- 把 LLM Agent 编排误当作车辆控制；
- 要求从空白目录反复手写样板代码；
- 声称复现没有公开代码和权重的量产闭源系统。

主线直接围绕可迁移的工程能力展开：

```text
Driving Data Contract
        ↓
Time Alignment & Coordinate Frames
        ↓
Trajectory Representation & Vehicle Motion
        ↓
Imitation-Learning Baseline
        ↓
Open-Loop / Closed-Loop Evaluation
        ↓
Driving VLM / VLA
        ↓
Action Tokens / Continuous Trajectory Heads
        ↓
World Models / Reasoning / Long-Tail Data
        ↓
Safety Boundary / ODD / Fallback
        ↓
Deployment / Latency / Observability
```

---

## 日常学习入口

新会话按下面顺序读取：

1. [`LEARNER_PROFILE.md`](LEARNER_PROFILE.md)：长期学习者画像与教学边界；
2. [`PROGRESS.md`](PROGRESS.md)：当前能力状态和已有证据；
3. [`labs/001-driving-data-contract/CURRENT_TASK.md`](labs/001-driving-data-contract/CURRENT_TASK.md)：唯一当前任务；
4. 当前任务指定的 reference code。

完整长期路线见：

- [`MASTER_GROWTH_PLAN.md`](MASTER_GROWTH_PLAN.md)
- [`ROADMAP.md`](ROADMAP.md)

前沿技术筛选见：

- [`FRONTIER_RADAR.md`](FRONTIER_RADAR.md)

---

## 学习方式

采用和 `backend-learning-lab`、`agent-learning-lab` 一致的高密度学习方式：

```text
和 ChatGPT 讲清问题、数据流和失败边界
        ↓
阅读可运行的 guided reference implementation
        ↓
自己运行并观察 trace / 指标
        ↓
只修改真正关键的逻辑
        ↓
故意制造时间、坐标、归一化或闭环故障
        ↓
增加 tests / eval
        ↓
用自己的话解释设计取舍
        ↓
ChatGPT 直接审查 GitHub
        ↓
更新 PROGRESS 并解锁下一任务
```

不以“是不是完全从零原创”判断掌握，而以：

```text
看得懂
讲得清
改得对
测得出
出错能定位
知道结论在哪些条件下失效
```

判断。

---

## 当前任务：Lab 001A

当前只做一件事：

> **读懂一条驾驶样本的数据契约，并通过验证 trace 找出两个“结构合法但语义错误”的样本。**

进入：

```powershell
cd labs\001-driving-data-contract\guided_reference\001a
python run_eval.py
python -m unittest discover -s tests -v
```

预期 baseline：

```text
4 / 6 PASS
2 / 6 FAIL
```

这两个失败不是程序崩溃，而是 baseline validator 没发现：

- 多相机时间偏差过大；
- 所谓“未来轨迹”实际从过去开始。

不要先修。先根据 trace 说明错误为什么发生。

完整任务见：

- [`labs/001-driving-data-contract/CURRENT_TASK.md`](labs/001-driving-data-contract/CURRENT_TASK.md)

---

## 两条学习线

### 主线：Driving VLA Engineering

- 多相机与时序输入；
- 自车状态和导航条件；
- BEV / token / latent representation；
- 轨迹回归、动作 token、扩散或 flow head；
- Driving VLM / VLA；
- reasoning 与 implicit token；
- world model 与长尾数据；
- 模型推理、微调、评测和部署。

### 支撑线：最低必要自动驾驶工程

- 时间戳与传感器同步；
- world / map / ego / sensor / image / BEV 坐标系；
- SE(2) 与运动学自行车模型；
- trajectory、waypoint 与 control 的区别；
- 横纵向控制直觉；
- 开放环、闭环与分布偏移；
- ODD、安全检查、fallback；
- latency、吞吐、日志、指标与实验复现。

支撑线按真实 VLA 问题补，不把仓库扩张成完整车辆工程、SLAM、底盘控制或嵌入式课程。

---

## 仓库结构

```text
vla_basic/
├── README.md
├── AGENTS.md
├── LEARNER_PROFILE.md
├── LEARNING_METHOD.md
├── MENTORING_SYSTEM.md
├── ROLE_TARGET.md
├── ENGINEERING_PRINCIPLES.md
├── MASTER_GROWTH_PLAN.md
├── ROADMAP.md
├── PROGRESS.md
├── FRONTIER_RADAR.md
├── MIGRATION.md
├── labs/
│   └── 001-driving-data-contract/
│       ├── README.md
│       ├── CURRENT_TASK.md
│       └── guided_reference/001a/
├── notes/
│   ├── glossary.md
│   └── learning-journal/
├── paper-notes/
├── scripts/
└── .github/workflows/ci.yml
```

---

## 掌握状态

```text
ASSUMED  根据已有工作经验暂时认为接触过，但未在本仓库验证
LEARNING 当前正在学习
REVIEW   基本正确，但仍有关键缺口
PASSED   已有代码、测试、实验或解释证据
REVISIT  曾经通过，但技术变化或理解退化，需要重验
```

只有 evidence 才能进入 `PASSED`。Evidence 可以是：

- commit；
- tests；
- eval result；
- fault diagnosis；
- 可复现 benchmark；
- 数据可视化；
- architecture decision；
- 对失败边界的解释。

---

## 公开仓库安全边界

永远不要提交：

- 公司源代码、内部模型、内部 Prompt 或架构；
- 真实车辆日志、客户数据或未脱敏视频；
- 内部域名、IP、账号、Token、Secret；
- 受限数据集的原始文件；
- 不能公开的论文附件或商业材料。

大型数据、模型权重和实验输出默认不进入 Git：

```text
data/
datasets/
checkpoints/
outputs/
*.pt
*.pth
*.ckpt
*.safetensors
```

仓库只保存公开可复现代码、配置、少量合成样本和高价值结论。

---

最终目标不是“背过多少 VLA 模型”，而是：

> **面对一个驾驶 VLA 系统，能够说明输入和动作契约、判断时间与坐标是否正确、建立可信评测、定位开放环与闭环失败、约束模型输出，并用实验而不是宣传语证明系统能力。**
