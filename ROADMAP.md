# Roadmap

这是一张日常可读的能力地图。完整要求见 `MASTER_GROWTH_PLAN.md`。

| Lab | 主题 | 状态 | 主要产出 | 最小独立证据 |
|---|---|---|---|---|
| 000 | Scope / System Map | REVIEW | 驾驶 VLA 系统图 | 能区分模型、轨迹、控制和评测 |
| 001 | Driving Data Contract | **LEARNING** | 可验证驾驶样本 | 时间/坐标语义检查 + fault |
| 002 | SE(2) / Bicycle / Trajectory | LOCKED | 轨迹 rollout | 坐标变换与 yaw 故障 |
| 003 | Camera Time / BEV | LOCKED | 多传感器时间轴 | skew + stale observation |
| 004 | Imitation Baseline | LOCKED | 小型轨迹模型 | overfit 32 samples |
| 005 | Open / Closed Loop Eval | LOCKED | 双评测报告 | 构造指标背离案例 |
| 006 | NAVSIM | LOCKED | 公开 benchmark baseline | mini split 复现 |
| 007 | Driving VLM / VLA | LOCKED | 公开 checkpoint 实验 | conditioning ablation |
| 008 | Action Representation | LOCKED | token/continuous 对比 | encode/decode + error |
| 009 | Reasoning / World Model | LOCKED | 假设实验 | rationale-action consistency |
| 010 | Safety / ODD / Fallback | LOCKED | safety boundary | stale/unsafe injection |
| 011 | Deployment / Observability | LOCKED | latency/eval pipeline | regression evidence |

## 解锁规则

不是按日期解锁，而是按依赖和证据：

```text
001 PASS
→ 002

002 + 003 PASS
→ 004

004 PASS
→ 005

005 PASS
→ 006 / 007

007 PASS
→ 008 / 009

005 + 007 PASS
→ 010

006 + 010 PASS
→ 011
```

## 当前入口

[`labs/001-driving-data-contract/CURRENT_TASK.md`](labs/001-driving-data-contract/CURRENT_TASK.md)

## 中断后恢复

```text
1. PROGRESS.md
2. 当前 CURRENT_TASK.md
3. 当前 reference README
4. 运行 tests
5. 从未完成的最小步骤继续
```

不要机械从 Lab 000 重新复习。
