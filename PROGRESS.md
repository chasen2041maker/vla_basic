# Progress

最后更新：2026-08-27

## 当前一句话接棒

> **从 Lab 001A 开始：运行 6 个驾驶数据契约案例，确认 baseline 为 4/6，借助 validation trace 找出 camera clock skew 和 future trajectory starts in past 两个 silent failure；暂时不要修代码。**

当前任务：

- [`labs/001-driving-data-contract/CURRENT_TASK.md`](labs/001-driving-data-contract/CURRENT_TASK.md)

## 当前能力状态

| 能力 | 状态 | 证据 | 下一步 |
|---|---|---|---|
| Python 工程阅读 | ASSUMED | 工作背景，仓库内未专项验证 | 在 Lab 001 通过代码解释验证 |
| Agent / workflow mental model | ASSUMED | 工作背景 | 仅作类比，不替代驾驶基础 |
| 自动驾驶 VLA 系统边界 | REVIEW | 已明确目标是小鹏式驾驶方向 | 完成 Lab 000 自述图 |
| 驾驶数据契约 | LEARNING | 当前任务 | 运行 baseline 并解释两类 silent failure |
| 时间对齐 | LEARNING | 无仓库证据 | Lab 001B 实现检查 |
| 坐标系 / SE(2) | ASSUMED | 仅见过通用概念 | Lab 002 验证 |
| trajectory vs control | ASSUMED | 无代码证据 | Lab 002 验证 |
| imitation learning | ASSUMED | AI 经验不等于驾驶证据 | Lab 004 |
| open-loop / closed-loop eval | LEARNING | 已建立概念方向，未实验 | Lab 005 |
| Driving VLM / VLA | LEARNING | 了解模型名称，未复现 | Lab 007 |
| world model / reasoning | ASSUMED | 仅方向认知 | Lab 009 |
| ODD / safety / fallback | ASSUMED | 无证据 | Lab 010 |
| deployment / latency | ASSUMED | Agent 工程经验可迁移但未验证 | Lab 011 |

## 已确认的学习方式

```text
Reference implementation
→ 对话讲 data/execution path
→ 运行
→ 小改
→ fault injection
→ tests/eval
→ review
→ evidence-based progress
```

不要求从空白搭全部样板，但关键的时间、坐标、轨迹、评测和安全逻辑必须自己控制。

## 当前尚未产生的证据

以下内容不要提前标记为通过：

- 没有实际运行 Lab 001；
- 没有提交独立修改；
- 没有新增测试；
- 没有故障诊断记录；
- 没有 NAVSIM / CARLA / AutoVLA 复现；
- 没有大模型训练或微调；
- 没有真实车辆实验。

## 完成 001A-Read 后应记录

```text
运行环境：
实际输出：
两个 failing case：
failure 起点：
为什么 runtime valid != semantic valid：
commit / screenshot / log：
```

只有这些证据出现后，Teacher 才更新下一状态。
