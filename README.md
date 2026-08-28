# Autonomous Driving VLA Engineering Transition Lab

这是一个面向 **自动驾驶 VLA / 端到端驾驶 / Physical AI Engineering** 的长期学习与转型仓库。

仓库的北极星不是“跑过多少 Demo”，而是帮助学习者从已有的 Python、Agent 和深度学习经验，逐步形成接近智能驾驶研发岗位所需要的完整控制力：

```text
看懂驾驶系统全链路
→ 检查数据的时间、坐标与物理语义
→ 训练并修改轨迹模型
→ 建立可信的开放环与闭环评测
→ 定位 data / model / action / control / eval / system 故障
→ 做蒸馏、量化、部署和安全边界验证
→ 再进入 Driving VLM / VLA、强化学习和世界模型
```

这里的 VLA 指接近乘用车智能驾驶方向的：

```text
历史多相机视觉 + 自车状态 + 导航 / 语义条件
                         ↓
              时序表征 / 推理 / latent
                         ↓
             未来轨迹或动作表示
                         ↓
             安全检查 / 控制 / 闭环
```

它不是机械臂抓取教程。旧版机器人操作内容保留在：

```text
archive/robot-manipulation-vla-2026-07
```

---

## 学习者当前起点

当前教学默认：

- Python、RAG、Agent/workflow、tool calling 和 AI Coding 有实际经验；
- 能进行常规深度学习模型训练；
- 学过蒸馏和量化，但仍需用驾驶任务验证；
- 未学习强化学习；
- 计算机视觉、相机几何、多相机时序、车辆运动、轨迹规划、闭环评测和 Driving VLA 需要系统建立。

因此本仓库不会从 Python 或普通训练循环重新开始，也不会把“学过蒸馏/量化”直接当作驾驶工程证据。

完整能力缺口见 [`SKILL_GAP_MATRIX.md`](SKILL_GAP_MATRIX.md)。

---

## 先看系统，再进局部 Lab

新的学习入口不是直接打开 `validator.py`，而是先建立整车智能链路：

```text
真实道路
  ↓
传感器采集
  ↓
数据契约 / 时间同步 / 坐标变换
  ↓
视觉与时序表征
  ↓
预测 / 规划 / VLA 模型
  ↓
轨迹或动作
  ↓
安全检查
  ↓
控制器与执行器
  ↓
车辆改变环境
  ↓
下一帧观测 + 评测 + 数据闭环
```

详见 [`SYSTEM_MENTAL_MODEL.md`](SYSTEM_MENTAL_MODEL.md)。

---

## 日常接棒顺序

新会话按下面顺序读取：

1. [`LEARNER_PROFILE.md`](LEARNER_PROFILE.md)：长期背景与教学边界；
2. [`SKILL_GAP_MATRIX.md`](SKILL_GAP_MATRIX.md)：哪些跳过、验证、系统补齐或延后；
3. [`SYSTEM_MENTAL_MODEL.md`](SYSTEM_MENTAL_MODEL.md)：整车系统全景；
4. [`PROGRESS.md`](PROGRESS.md)：当前状态和证据；
5. 当前唯一的 `CURRENT_TASK.md`；
6. 当前任务指定的 reference code 和 tests。

完整路线见：

- [`ROLE_TARGET.md`](ROLE_TARGET.md)
- [`MASTER_GROWTH_PLAN.md`](MASTER_GROWTH_PLAN.md)
- [`ROADMAP.md`](ROADMAP.md)

---

## 当前任务

当前从 **Lab 000A — Driving System Map** 开始：

> 先说清从传感器到车辆运动的完整执行链，并能判断四类故障分别应在哪个边界被发现。

入口：

- [`labs/000-driving-system-map/CURRENT_TASK.md`](labs/000-driving-system-map/CURRENT_TASK.md)

运行：

```powershell
cd labs\000-driving-system-map\guided_reference\000a
python run_trace.py
python -m unittest discover -s tests -v
```

预期：

```text
SYSTEM MAP RESULT: 4 / 4 PASS
```

这不是模型训练，而是建立后续所有课程的导航图。

---

## 能力路线

```text
000  System Map & Failure Boundaries
001  Driving Data Contract & Time Semantics
002  Coordinate Frames / SE(2) / Trajectory / Vehicle Motion
003  Camera Geometry
004  Multi-Camera Temporal Modeling / BEV Mental Model
005  End-to-End Trajectory Learning Baseline
006  Open-Loop / Closed-Loop Evaluation
007  Public Driving Stack / NAVSIM
008  Driving VLM / VLA
009  Action Representation
010  Distillation / Quantization / Deployment
011  Safety / ODD / Observability
012  Reinforcement Learning / World Model / Long Tail
```

强化学习和世界模型被保留为后期能力，不会在 state、action、rollout 和 closed loop 尚未建立时提前教学。

---

## 学习方式

采用：

```text
Orient 系统定位
→ Trace 数据与执行链
→ Explain 职责和失败边界
→ Run 运行参考实现
→ Change 修改关键逻辑
→ Break 注入故障
→ Measure 用 tests / eval / visualization 证明
→ Review 审查并更新证据
```

不以“是不是从空白原创”判断掌握，而以：

```text
看得懂
讲得清
改得对
测得出
出错能定位
知道结论何时失效
```

判断。

---

## 仓库结构

```text
vla_basic/
├── README.md
├── SYSTEM_MENTAL_MODEL.md
├── SKILL_GAP_MATRIX.md
├── LEARNER_PROFILE.md
├── ROLE_TARGET.md
├── MASTER_GROWTH_PLAN.md
├── ROADMAP.md
├── PROGRESS.md
├── LEARNING_METHOD.md
├── MENTORING_SYSTEM.md
├── ENGINEERING_PRINCIPLES.md
├── FRONTIER_RADAR.md
├── AGENTS.md
├── labs/
│   ├── 000-driving-system-map/
│   └── 001-driving-data-contract/
├── notes/
├── paper-notes/
└── scripts/
```

未来 Lab 只在依赖和当前证据足够时创建，不批量生成空目录。

---

## 仓库毕业标准

达到仓库主线毕业，不等于获得特定公司的职位承诺。它表示学习者至少能够：

```text
打开公开驾驶数据并解释字段、时间、坐标和标签
→ 跑通训练、推理和评测链
→ 独立修改一个模型或动作表示
→ 构造并定位数据、模型、控制和 evaluator 故障
→ 对比开放环与闭环表现
→ 分析失败场景和分布偏移
→ 验证蒸馏/量化后的行为与延迟
→ 明确 ODD、安全检查和 fallback
→ 在没有 Coding Agent 时完成关键调试
```

最终目标是：

> **从“会搭 AI 系统、会训练模型”，成长为“能让模型基于正确的物理世界数据，产生可验证、可执行、可部署的驾驶行为”。**
