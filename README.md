# vla_basic｜自动驾驶与 VLA 理论讲义

**这里讲清楚为什么；[highwayenv-learning](https://github.com/chasen2041maker/highwayenv-learning) 负责真正修改、运行和验证。两个仓库，一条学习主线。**

2026-09-23 起，本仓库承担理论讲义、知识地图和理解沉淀，不再维护第二套驾驶程序或实验进度。2026-09-27 的课程审查继续保留这项分工。

## 这能不能当你的第一本智驾教材？

可以作为项目驱动的第一条学习主线，**目前还不是覆盖视觉、训练、VLA 和部署的完整教材**。已有内容能帮助理解动作、观察、控制和反馈；后续能力必须由对应的正文、真实工程与个人解释逐步兑现，不能用目录或 CI 代替。

本次增加了评测、状态到相机的衔接、数学与 C++ 工程小例子，并明确岗位分流和阶段交付标准。它们不表示后续训练工程已经完成，也不表示学习者已经掌握。具体范围、版本差异和检查结果见 [2026-09-27 审查记录](notes/2026-09-27-curriculum-review.md)。

## 从哪里开始

| 你现在要做什么 | 去哪里 |
| --- | --- |
| 继续上次的课，确认实际学到哪里 | [唯一当前进度：highwayenv-learning/PROGRESS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md) |
| 查直白的原理和数值例子 | [理论讲义目录](theory/README.md) |
| 从实验找到理论、从理论返回代码 | [理论—实践对应表](PRACTICE_MAP.md) |
| 看长期顺序与阶段成果 | [知识路线](ROADMAP.md)、[教材与作品交付标准](CURRICULUM_STANDARD.md) |
| 判断与目标岗位的关系 | [岗位目标](ROLE_TARGET.md)、[能力补齐决策](SKILL_GAP_MATRIX.md) |
| 换一个对话或 AI 接棒 | [协作约定](AGENTS.md)、[学习者背景](LEARNER_PROFILE.md) |

**不要用旧 H001 覆盖实践库的新进度。** 第一件事是实际读取实践进度和当前代码，而不是因为教材改版就重新做旧实验。公开仓库与本地说明不一致时，先标出版本，不猜测未上传的正文。

## 已有讲义

| 内容 | 材料范围 |
| --- | --- |
| [01 目标速度与控制](theory/01-target-speed-and-control.md) | 高层动作、档位、实际速度与比例控制 |
| [02 step 与反馈](theory/02-step-and-feedback.md) | 决策时间、仿真时间、重新观察与回合边界 |
| [03 观察与相对运动](theory/03-observation-and-relative-motion.md) | 归一化、相对量、对象覆盖和距离规则盲区 |
| [04 评测与证据](theory/04-evaluation-and-evidence.md) | 公平比较、失败复现、统计小例子；不是已实现的批量评测器 |
| [05 从状态到相机](theory/05-state-to-camera-bridge.md) | 坐标与投影例子、数据接口、后续视觉实验衔接；尚无真实数据适配器 |
| [06 数学与工程检查](theory/06-engineering-and-math-checkpoints.md) | 可编译 C++ 例子、故障注入和分方向工程要求；不是车端部署项目 |

讲义编号是知识索引，不是另开六项作业。已准备材料、已经讲解、学习者运行过和独立掌握分别记录；个人状态只在实践仓库保存。

## 两个仓库的边界

`vla_basic` 保存概念、必要公式、数值例子、局部代码带读、误解与来源。允许用临时文件验证公式，不新建独立驾驶 runner、训练入口、数据副本或第二份实验输出。

`highwayenv-learning` 保存当前实际程序、配置、策略、源码练习、日志、失败复现和评测。以后需要真实相机数据或其他模拟器时，再明确实践工程、版本和资源；不把 HighwayEnv 俯视图当作真实相机感知。

## 原有内容怎样保留

[系统地图](SYSTEM_MENTAL_MODEL.md)、[工程原则](ENGINEERING_PRINCIPLES.md) 按需回查。[长期成长参考](MASTER_GROWTH_PLAN.md) 与 [前沿材料](FRONTIER_RADAR.md) 保留为历史参考；涉及当前岗位范围和学习顺序时，以新的 ROLE_TARGET、ROADMAP 和实际实践进度为准。

`labs/`、`experiments/highway_driving/` 的代码、测试与依赖保留原路径，作为历史工具，不删除也不扩建成第二条实践主线。Lab 001 的 `BASELINE RESULT: 4 / 6 PASS` 是原有教学基线，不为全绿修改。

旧 H001 及其验收记录见 [改造前版本 4503a9c](https://github.com/chasen2041maker/vla_basic/tree/4503a9cc9d0b67add5e85c28aa5d75e73f2725a7)。双仓库改造依据见 [2026-09-23 记录](notes/2026-09-23-theory-practice-split.md)。

继续学习时仍从正在解决的驾驶问题出发：看现象、讲原理、读代码、做有限修改、核对证据。不因本次文档维护重新安装现有环境或把任何个人能力标成完成。
