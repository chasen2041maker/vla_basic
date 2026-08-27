# Frontier Radar — Autonomous Driving VLA

最后核对：2026-08-27

这份文件记录会快速变化的模型、工具和产业方向。稳定知识放在课程和 labs，不在这里重复。

状态：

```text
IGNORE  当前不投入
WATCH   跟踪，不进入主线
TRIAL   安排小实验
ADOPT   作为主线工具或基准
```

## 当前雷达

| 方向 / 项目 | 状态 | 为什么 | 当前行动 |
|---|---|---|---|
| XPENG VLA 2.0 | WATCH | 量产驾驶方向的重要架构参考，但完整代码、权重和训练栈未公开 | 学习公开架构思想，不声称复现 |
| XPENG X-World | WATCH | 多视角驾驶世界模型，面向数据生成、闭环验证和系统演进 | Lab 009 再研究 |
| XPENG X-Mind | WATCH | 强调预测与可解释视觉推理 | 关注 reasoning-action consistency |
| AutoVLA | TRIAL | 公开 Driving VLA 实现，包含轨迹 action token 与自适应推理路线 | Lab 007/008 候选复现对象 |
| NVIDIA Alpamayo 系列 | WATCH | 开放 reasoning VLA，模型规模和硬件门槛较高，生态仍快速变化 | 先读接口和评测，再决定试跑 |
| NAVSIM | ADOPT | 公开、可复现的驾驶规划评测主线，适合建立 open/pseudo-closed-loop 证据 | Lab 006 |
| CARLA | WATCH | 交互式闭环仿真价值高，但环境重，不适合第一阶段 | Lab 005 后再引入 |
| nuPlan devkit | WATCH | 规划数据与仿真基础，常与 NAVSIM 生态连接 | 按 NAVSIM 需要使用 |
| Robot Manipulation VLA | IGNORE | OpenVLA、π0、LeRobot 的机械臂知识不是当前主线 | 仅在动作表示类比时引用 |
| 自建真实车辆实验 | IGNORE | 安全、合规和成本不适合作为个人学习验收 | 使用公开数据和仿真 |

## 官方来源

### XPENG

- VLA 2.0：<https://www.xpeng.com/pressroom/news/019cae5e67b99c0960ee8a028129016a>
- VLA 2.0 架构发布：<https://www.xpeng.com/pressroom/news/019a56f54fe99a2a0a8d8a0282e402b7>
- X-World：<https://www.xpeng.com/news/019dd72da86c9dd703de8a0282290002>
- X-Mind：<https://www.xpeng.com/news/019f12539bff9f1220b48a028223000e>

### Public Reproduction Targets

- AutoVLA：<https://github.com/ucla-mobility/AutoVLA>
- NAVSIM：<https://github.com/autonomousvision/navsim>
- NVIDIA Alpamayo：<https://github.com/NVlabs/alpamayo>

## 进入主线前的检查

任何新模型或框架进入课程前，记录：

```text
检查日期
官方来源
代码 commit / release
权重是否公开
数据许可
最低硬件
能否只跑推理
能否在 mini 数据上评测
动作输出语义
评测协议
我是否亲自验证
```

“读过论文”或“看过 demo”不能把状态改为 `ADOPT`。

## 更新日志

| 日期 | 变化 | 依据 |
|---|---|---|
| 2026-08-27 | 仓库从机器人操作 VLA 重构为自动驾驶 VLA；建立 XPENG 方向参考、AutoVLA 复现、NAVSIM 评测三层关系 | 官方项目与公开仓库 |
