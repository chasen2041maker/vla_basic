# Learning Method

本仓库采用：

> **system-first orientation + guided reference + targeted modification + fault experiment + evidence-based progression**

目标是在已有 AI 和深度学习经验上，高密度建立自动驾驶 VLA 的视觉、空间、动作、评测和系统 mental model。

## 1. 为什么先看系统全景

直接进入一个 validator、模型 head 或 loss，容易知道“代码做了什么”，却不知道：

- 它位于整车链路哪里；
- 上游给它的数据是否可信；
- 下游如何消费结果；
- 错误应该在哪个边界被发现；
- 模型输出与真实车辆行为之间还隔着什么。

所以每个新领域先完成：

```text
系统位置
→ 输入 / 输出
→ 时间 / 坐标
→ 职责 / 非职责
→ 正常链路
→ 失败链路
```

之后再进入 reference code。

---

## 2. 默认学习循环

```text
Orient   在整车系统中定位
Trace    跟踪数据和执行路径
Explain  讲清职责与失败边界
Run      运行 reference 和 baseline
Change   修改真正关键的逻辑
Break    故意制造时间、坐标、动作或闭环故障
Measure  用 tests / eval / visualization / profile 证明
Review   审查、记录证据、解锁下一步
```

一个主题不能只停留在“听过”“读过论文”或“代码跑通”。

---

## 3. Verify 与 Learn 双通道

### Verify

适用于学习者已有经验：

- Python；
- 常规深度学习训练；
- Transformer 基础；
- 蒸馏和量化；
- Linux / Git / AI Coding。

方式：

```text
不重讲定义
→ 放进真实驾驶任务
→ 独立改动或排错
→ 用行为和系统指标验证
```

### Learn

适用于当前主要缺口：

- 计算机视觉；
- 相机几何和坐标；
- 多相机时序和 BEV；
- 车辆运动、轨迹和控制；
- 开放环和闭环评测；
- Driving VLM / VLA；
- safety / ODD / fallback。

方式：

```text
直白 mental model
→ 最小公式
→ 可运行 reference
→ fault injection
→ tests / eval
→ 独立解释
```

---

## 4. 为什么不用纯 blank-page 学习

每个主题从空目录搭项目，会把时间消耗在：

- dataclass 和配置样板；
- 数据下载胶水；
- SDK 接线；
- 大量模型 boilerplate；
- 当前目标无关的工程包装。

真正值得学习者控制的是：

- 时间同步判定；
- 坐标变换；
- trajectory rollout；
- action 编码与解码；
- loss 和 evaluator；
- safety / fallback decision；
- latency budget 和 stale detection；
- failure taxonomy。

---

## 5. 建议时间分配

大致：

- 30%：系统定位、数据流和设计边界；
- 25%：视觉、几何、车辆运动等新领域基础；
- 20%：修改、扩展和 debug；
- 15%：测试、可视化、闭环和故障实验；
- 10%：从空白重写最重要的核心逻辑。

遇到已有能力时，基础讲解时间转移到真实实验和失败分析。

---

## 6. Reference Implementation 要求

1. 不依赖私有数据；
2. 第一次尽量使用合成或 mini 数据；
3. 输入输出契约显式；
4. 时间戳、单位和坐标写进类型与变量名；
5. 可重复运行；
6. 有预期输出；
7. 有至少一个故意保留的 failure gap；
8. 教学简化必须明说；
9. 框架出现时解释它隐藏的底层机制；
10. 不把宣传指标当成可复现实验；
11. 复杂度必须购买新的证据。

---

## 7. 四类核心证据

### Contract Evidence

字段、单位、时间、坐标、切分和 train/inference contract 正确。

### Model Evidence

模型能过拟合小样本，输入消融有效，loss 与行为指标被检查，action decode 正确且无泄漏。

### Evaluation Evidence

evaluator 有测试，开放环和闭环分开，指标不能被静止或过度保守策略投机，failure 可分类。

### System Evidence

延迟可测，过期观测可检测，输出经过安全检查，版本和日志足以复现实验，fallback 条件明确。

---

## 8. 强化学习进入条件

强化学习不按流行度解锁。必须先能回答：

```text
state 是什么？
action 是什么？
transition 如何发生？
rollout 如何生成？
reward 和 driving metric 有什么差别？
evaluator 是否可信？
安全边界在哪里？
```

否则只会背算法名，无法判断 reward hacking、model bias 和闭环风险。

---

## 9. 最终验收问题

- 能否画出传感器到车辆运动的全链路？
- 能否解释任意样本的时间、坐标和标签？
- 能否在 world / ego / camera 之间转换并测试？
- 能否解释 trajectory、action token 和 control 的区别？
- 能否独立训练、修改和排错一个轨迹模型？
- 能否判断 metric 是开放环还是闭环？
- 能否定位 data、model、decode、control 或 evaluator 问题？
- 能否证明蒸馏/量化后系统在行为和延迟上仍然成立？
- 换一个 VLA 框架后 mental model 是否仍然成立？
