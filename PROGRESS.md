# Progress｜工程与学习分开接棒

更新时间：2026-09-23。字段、状态与写权限遵循 [AGENTS.md](AGENTS.md)；本文件是唯一当前接棒真源。

## 1. 当前接棒卡

| 必填字段 | 当前值 |
|---|---|
| 当前任务 | H001：运行并解释一个驾驶回合 |
| 唯一任务路径 | [experiments/highway_driving/CURRENT_TASK.md](experiments/highway_driving/CURRENT_TASK.md) |
| 当前课堂片段 | A：高层目标与 IDLE；B/C/D 尚不据此标成已讲完 |
| engineering_status | REVIEW：本次教学摘要与协作规范待新版本 CI 核验 |
| 工程验证范围与执行者 | 原入口历史验证见 2026-09-22 记录；本次执行者为 GPT 维护角色，验证范围按本次记录更新 |
| 工程待验证项 | 本次完整 CI、Linux/Windows 集成与摘要；原生桌面窗口和学习者本机运行未验证 |
| learning_status | LEARNING；没有因为维护、讲义或 CI 提升为 PASSED |
| 课堂阶段 | EXPLAIN：先核对高层目标与实际运动的区别 |
| GPT 已实际讲解 | 上轮对话已示范 IDLE 保持目标、控制器和 step 的分工及时间概念；这是教学方式示范，不代表 H001 全部授课完成 |
| 学习者已证明的理解 | 未收到 H001 独立理解回答；本次确认的是角色分工与仓库改造要求，不是驾驶知识验收 |
| 仍不确定或误解 | 对目标速度、实际速率、时间和观察字段的理解尚待核对；没有证据，不推断具体误解 |
| 实践证据 | 仅有维护者工程材料；没有可归为学习者 H001 亲自运行或独立修改的证据 |
| 待老师审查证据 | 暂无新的学习者回答、预测、实验或故障记录 |
| 下一次 GPT 从哪里开始 | [H001 讲义 A](experiments/highway_driving/walkthrough/H001-idle-step.md#a-gpt-老师先讲为什么-idle-以后车还会动)；定位 make_env 的 action 配置和 run_episode 的 step 前后记录 |
| 下一次 GPT 的一个问题 | 给一辆仍在行驶的车发送 IDLE，为什么“不改变目标速度”不等于“把速度变成零”？ |
| 下一次你与 Codex 做什么 | 等 GPT 核对所需理解后，按 H001 动手区运行 0 车、seed=7、1 步 IDLE 并读首步摘要；暂不提前比较 SLOWER或改测试 |
| 本轮不做什么 | 不激活 H002，不生成跟车策略、慢前车场景、训练或新活跃任务 |

教材准备与实际授课必须区分：新增讲义不表示 B/C/D 已讲给学习者；老师示范的推理不能填成学习者答案。

## 2. 本次维护改了什么

按用户要求，将 GPT 授课、你与 Codex 有限实现、双轨验收写入 AGENTS.md；统一教学入口；加入 H001 实际带读；将目标速度和实际速率分别写进真实日志并显示首步摘要；新增格式、真实模拟器对照和 CLI 测试。

**工程变更不改变个人学习状态。** 维护范围和测试证据见 [2026-09-23 记录](notes/2026-09-23-teacher-codex-handoff.md)。旧入口与回放验证见 [2026-09-22 记录](notes/2026-09-22-highway-entry.md)。

## 3. 学习者能力基线：未擅自升级

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

ASSUMED-NO 是历史能力矩阵中的明确缺口，不是新的晋级状态。没有根据这次维护改写这些判断。

## 4. 尚未收到的个人证据

未记录学习者亲自运行 H001 并解释字段；未有自己的 IDLE/SLOWER 事前预测和事后对照；未有时间断言故障对照及解释。旧 Lab 000/001 的个人验收也未因切换主线而完成。

没有个人驾驶视觉/几何、轨迹模型训练、开放环/闭环对比、驾驶化蒸馏量化、RL 或真实车辆证据。维护者日志不能填入上述项目。

## 5. 后续证据如何写

先读本卡，只更新本次有新证据的字段。Codex 可以追加以下客观记录，个人学习状态与课堂切换交给 GPT 核对：

```text
日期 / 来源 / 执行者 / 协作方式：
任务 / 课堂片段 / 分支 / commit：
Python / 依赖 / 平台：
实际命令与退出码：
seed / vehicles / action / max_steps：
结果 / 输出位置 / 可访问证据：
未验证项：
仍需学习者解释的内容：
```

GPT 记录自己的实际讲解、学习者真实回答与核对结论；没有收到就保持未知。H001 个人验收满足后再决定是否激活 H002。
