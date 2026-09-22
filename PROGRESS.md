# Progress

最后更新：2026-09-22

## 当前一句话接棒

> **当前只推进 H001：运行并解释 HighwayEnv 的一个驾驶回合。先看车运行，读懂一条观察/动作/下一观察的时间与物理语义，再预测并比较 IDLE 与 SLOWER。旧 Lab 按需回查，不要求先通关。**

唯一活跃任务：[experiments/highway_driving/CURRENT_TASK.md](experiments/highway_driving/CURRENT_TASK.md)

项目说明：[README.zh-CN.md](experiments/highway_driving/README.zh-CN.md)

## 本次改变了什么

学习入口从按 Lab 顺序解锁改为同一个驾驶项目持续改进。保留旧 Lab 000/001、系统地图、能力矩阵和长期 VLA 目标；没有把旧任务标为已完成。

新增真实环境交互、固定配置/种子、明确高层动作、逐步日志、回放、结束分类和最小测试。当前没有慢前车专用场景、跟车规则、训练模型、视觉感知或 VLA。工程验证详情见 [本次记录](notes/2026-09-22-highway-entry.md)。

**代码与 CI 完成，是维护者的工程证据，不是学习者已掌握的证据。**

## 学习者基线：未擅自升级

会常规深度学习训练，学过蒸馏和量化，未学习强化学习；Python、Agent/workflow、RAG 和 AI Coding 经验可作为起点。视觉、几何、车辆运动、轨迹控制、闭环评测与 Driving VLA 仍需学习与验证。

| 能力 | 状态 | 现有依据 / 下一证据 |
|---|---|---|
| Python 工程阅读 | ASSUMED | 工作背景；下一步解释当前实验执行链 |
| Agent / workflow mental model | ASSUMED | 说明物理世界 retry 的类比失效点 |
| 常规深度学习训练 | REVIEW | 自述；后续驾驶模型 overfit/debug/ablation |
| Transformer / Attention | REVIEW | 驾驶时序模型专项证据未形成 |
| 蒸馏 / 量化 | REVIEW | 自述学过；驾驶行为、延迟与内存证据未形成 |
| 强化学习 | ASSUMED-NO | 明确未学；延后到闭环基础之后 |
| 驾驶系统全景 | LEARNING | Lab 000 保留；个人系统解释仍待验证 |
| 驾驶数据契约 | QUEUED / 按需参考 | Lab 001 保留，未将其学习任务标为完成 |
| 观察/动作/仿真时间 | LEARNING | 当前 H001，个人运行和解释待补 |
| 视觉与相机几何 | ASSUMED-NO | 缺口不变，项目需要时补齐 |
| 多相机时序 / BEV | ASSUMED-NO | 尚无个人实现证据 |
| trajectory / control / vehicle motion | ASSUMED-NO | H001 只接触高层动作，不等于掌握轨迹控制 |
| open-loop / closed-loop eval | ASSUMED-NO | 仿真入口存在不等于个人会设计评测 |
| Driving VLM / VLA | ASSUMED-NO | 尚未实现或训练 |
| deployment / observability | ASSUMED | 工程经验可迁移，驾驶专项证据不足 |

`ASSUMED-NO` 仅表示明确缺口，不属于晋级状态。个人掌握仍须通过解释、修改、实验与故障定位确认。

## 学习者尚未提供的证据

- 未记录学习者在自己电脑运行 H001、解释字段和动作的结果。
- 未有学习者对 IDLE/SLOWER 的事前预测与事后日志对照。
- 原 Lab 000 的系统图、独立故障定位与 Lab 001 的个人诊断仍未完成验收。
- 未有个人驾驶视觉/几何、轨迹模型训练、开放环对比、蒸馏量化驾驶化验证、RL 或真实车辆证据。

不能把维护者运行 CI 的日志填进这些个人验收项。

## 下一次接棒只做这一件事

先围绕“IDLE 后车为什么还动”讲清环境、动作和控制器的分工，再读 H001 对应代码。不要输出一整套新课程，也不要要求先重写 Python 或从零造模拟器。

记录模板：

```text
代码版本 / Python / 依赖版本：
seed / action / max_steps：
输出目录 / 结束原因：
obs[0] 和其他有效行分别是什么意思：
一次动作前后时间：
预测 SLOWER 的结果：
实际日志对照：
还不能证明什么：
```

H001 的个人证据完成后，再决定是否激活 H002（慢前车与第一条跟车规则）；本次不提前创建第二个活跃任务。
