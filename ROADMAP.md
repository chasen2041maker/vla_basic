# Roadmap

这是日常可读的能力地图。完整要求见 `MASTER_GROWTH_PLAN.md`。

| Lab | 主题 | 状态 | 主要产出 | 最小独立证据 |
|---|---|---|---|---|
| 000 | System Map / Failure Boundaries | **LEARNING** | 整车执行链与故障定位 | 4 场景 trace + 系统图 |
| 001 | Data Contract / Time Semantics | QUEUED | 可验证驾驶样本 | 两类 silent failure + 修复 |
| 002 | Coordinates / Trajectory / Motion | LOCKED | SE(2) 与 rollout | round-trip + yaw fault |
| 003 | Camera Geometry | LOCKED | 投影与标定 mental model | projection + extrinsic fault |
| 004 | Multi-Camera Temporal / BEV | LOCKED | 对齐后的时序表征 | skew + motion compensation |
| 005 | Trajectory Learning Baseline | LOCKED | 小型端到端模型 | overfit + leakage/ablation |
| 006 | Open / Closed Loop Eval | LOCKED | 双评测和 failure taxonomy | 指标背离案例 |
| 007 | Public Stack / NAVSIM | LOCKED | 可复现公开 benchmark | mini split + config evidence |
| 008 | Driving VLM / VLA | LOCKED | 多模态动作实验 | conditioning ablation |
| 009 | Action Representation | LOCKED | token/continuous 对比 | encode/decode + error bound |
| 010 | Distill / Quantize / Deploy | LOCKED | 压缩和延迟报告 | behavior + latency + memory |
| 011 | Safety / ODD / Observability | LOCKED | 系统安全边界 | stale/unsafe/fallback tests |
| 012 | RL / World Model / Long Tail | LOCKED | 闭环学习假设实验 | reward/model-bias fault |

## 主依赖

```text
000 READ
→ 001

001 + 002
→ 003 / 004

002 + 004
→ 005

005
→ 006

006
→ 007 / 008

008
→ 009

006 + 009
→ 010 / 011

006 + 011
→ 012
```

## 并行验证线

不需要等待所有 Lab 才验证已有能力：

```text
深度学习训练    在 Lab 005 形成证据
蒸馏与量化      在 Lab 010 形成证据
Linux / Git      每次任务持续验证
无 Agent 调试    每个关键故障至少一次
C++              从 Lab 002 后逐步加入
论文阅读         从 Lab 004 后按当前问题进入
```

## 当前入口

[`labs/000-driving-system-map/CURRENT_TASK.md`](labs/000-driving-system-map/CURRENT_TASK.md)

## 中断后恢复

```text
1. LEARNER_PROFILE.md
2. SKILL_GAP_MATRIX.md
3. PROGRESS.md
4. 当前 CURRENT_TASK.md
5. 运行当前 tests / eval
6. 从未完成的最小证据继续
```

不要机械从头复习，也不要跳过未满足的系统依赖。
