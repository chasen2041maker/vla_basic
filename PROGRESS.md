# Progress

最后更新：2026-08-28

## 当前一句话接棒

> **先完成 Lab 000A：建立 sensor → data → representation → model → action → safety → control → environment → eval 的系统图，运行 4 个 trace，并能把故障定位到正确边界；暂时不要进入 Lab 001 代码细节。**

当前任务：

- [`labs/000-driving-system-map/CURRENT_TASK.md`](labs/000-driving-system-map/CURRENT_TASK.md)

---

## 最新学习者校准

学习者明确说明：

- 会进行常规深度学习模型训练；
- 学过蒸馏和量化；
- 未学习强化学习；
- 计算机视觉、相机几何、多相机时序、车辆运动、轨迹控制、闭环评测和 Driving VLA 基本需要从领域基础建立。

教学决策：

```text
深度学习 / 蒸馏 / 量化：不从定义重讲，后续真实任务验证
视觉 / 几何 / 驾驶 / 闭环：系统学习
强化学习：延后到 state-action-rollout-eval 成熟之后
```

---

## 当前能力状态

| 能力 | 状态 | 现有依据 | 下一证据 |
|---|---|---|---|
| Python 工程阅读 | ASSUMED | 工作背景 | 解释 Lab 000/001 execution path |
| Agent / workflow mental model | ASSUMED | 工作背景 | 说明物理 retry 类比失效点 |
| 常规深度学习训练 | REVIEW | 学习者自述 | Lab 005 overfit、debug、ablation |
| Transformer / Attention | REVIEW | 与模型训练背景相关，未专项验证 | Lab 004/005 时序模型解释 |
| 模型蒸馏 | REVIEW | 学习者自述学过 | Lab 010 驾驶行为蒸馏实验 |
| 模型量化 | REVIEW | 学习者自述学过 | Lab 010 行为/延迟/内存实验 |
| 强化学习 | ASSUMED-NO | 学习者明确未学 | Lab 012 前不提前标记 |
| 驾驶系统全景 | LEARNING | 当前任务 | 4/4 trace + 系统图解释 |
| 驾驶数据契约 | QUEUED | 已有 reference，尚未运行证据 | Lab 001A 4/6 diagnosis |
| 视觉与相机几何 | ASSUMED-NO | 学习者明确缺口 | Lab 003 |
| 多相机时序 / BEV | ASSUMED-NO | 学习者明确缺口 | Lab 004 |
| trajectory / control / vehicle motion | ASSUMED-NO | 学习者明确缺口 | Lab 002 |
| open-loop / closed-loop eval | ASSUMED-NO | 学习者明确缺口 | Lab 006 |
| Driving VLM / VLA | ASSUMED-NO | 学习者明确缺口 | Lab 008 |
| deployment / observability | ASSUMED | 工程经验可迁移，驾驶证据不足 | Lab 010/011 |

`ASSUMED-NO` 只用于本表表达“明确尚未学习”，不属于晋级状态；完成后仍按 `LEARNING → REVIEW → PASSED` 更新。

---

## 当前尚未产生的证据

- 没有 Lab 000 trace 运行记录；
- 没有完整驾驶系统图的个人解释；
- 没有 Lab 001 实际 4/6 输出；
- 没有驾驶视觉、几何或车辆运动代码；
- 没有 trajectory model 训练、消融或闭环实验；
- 没有蒸馏/量化在驾驶行为上的验证；
- 没有 RL、world model 或真实车辆实验。

不要提前标记为 `PASSED`。

---

## 完成 000A-Read 后应记录

```text
运行环境：
实际输出：
完整系统链：
stale_camera 停在哪一层：
past_trajectory 停在哪一层：
controller_timeout 停在哪一层：
为什么模型成功 != 驾驶成功：
Agent 类比的失效点：
commit / screenshot / log：
```

完成 000A-Read 后解锁 Lab 001A；Lab 000 的完整 `PASSED` 仍需要后续独立故障定位或系统图证据。
