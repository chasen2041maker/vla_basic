# vla_basic｜自动驾驶与 VLA 理论讲义

**这里讲清楚为什么；[highwayenv-learning](https://github.com/chasen2041maker/highwayenv-learning) 负责真正修改、运行和验证。两个仓库，一条学习主线。**

2026-09-23 起，本仓库从“理论与实验混合课堂”调整为理论讲义、知识地图和理解沉淀。理论跟着真实驾驶问题讲，不要求先读完整本教材才能实践；不在这里再维护第二套驾驶程序、训练入口或实验进度。

## 从哪里开始

| 你现在要做什么 | 去哪里 |
| --- | --- |
| 继续上次的课，确认实际学到哪里 | [唯一当前进度：highwayenv-learning/PROGRESS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md) |
| 查找直白的理论解释 | [理论讲义目录](theory/README.md) |
| 从实验找到理论、从理论返回代码 | [理论—实践对应表](PRACTICE_MAP.md) |
| 查看长期需要补哪些能力 | [知识路线图](ROADMAP.md) |
| 换一个对话或 AI 接棒 | [教学与跨仓库约定](AGENTS.md)、[学习者背景](LEARNER_PROFILE.md) |

第一次接续不是重新做旧 H001：先读取实践仓库的最新进度和代码，再打开对应讲义。网页 GPT 和本地助手采用相同接续点；代码、讲义准备、已经讲解和个人理解分别记录。

## 已有讲义

- [01｜目标速度、实际速度与控制器](theory/01-target-speed-and-control.md)：为什么一直减速却曾经停在 72 km/h；为什么改了目标，实际速度不会瞬间到位。
- [02｜一次 step、时间与反馈](theory/02-step-and-feedback.md)：谁决定动作，环境何时推进，为什么每次都要重新观察。
- [03｜观察表、相对运动与规则边界](theory/03-observation-and-relative-motion.md)：这些数来自哪里，何时要换算，为什么只看距离不够。

**讲义已建立不等于已经授课，更不等于学习者掌握。** 当前状态只在实践仓库记录；上面是材料目录，不是三项新作业或通关清单。

## 两个仓库的边界

`vla_basic` 保存概念、数值例子、必要公式、局部代码带读、常见误解和来源。允许解释性代码片段，不建设新的可运行仿真/训练工程。

`highwayenv-learning` 保存实际程序、源码实验、配置、策略、训练、日志、失败复现和评测。实践中的重要原理沉淀回这里，实验结果不重复复制到理论库。

具体规则见 [PRACTICE_MAP.md](PRACTICE_MAP.md)。长期目标仍是驾驶 VLA / 端到端驾驶研发；当前模拟器状态表和规则驾驶不是视觉感知或 VLA。未来需要其他数据或模拟器时，按明确任务选择实践项目，本仓库继续承担理论主线。

## 原有内容怎样保留

[系统地图](SYSTEM_MENTAL_MODEL.md)、[工程原则](ENGINEERING_PRINCIPLES.md)、[能力参考](SKILL_GAP_MATRIX.md) 按需回查，不作为开始实验的门槛。[岗位方向](ROLE_TARGET.md)、[长期成长参考](MASTER_GROWTH_PLAN.md)、[前沿材料筛选](FRONTIER_RADAR.md) 保留为参考，不是另一套当前待办；涉及旧任务和排课方式时，以本次分工为准。

`labs/`、`experiments/highway_driving/` 的代码、测试和依赖保留原路径，作为历史工具；不删除，不继续扩建为第二套实践项目。旧实验入口见 [历史实验说明](experiments/highway_driving/README.zh-CN.md)。原 Lab 001 的 `BASELINE RESULT: 4 / 6 PASS` 是原有教学基线，不为全绿修改。

旧 H001 进度、讲义和验收标准保留于 [改造前版本 4503a9c](https://github.com/chasen2041maker/vla_basic/tree/4503a9cc9d0b67add5e85c28aa5d75e73f2725a7)，不再是当前课程。改造范围见 [维护记录](notes/2026-09-23-theory-practice-split.md)。

## 继续学习时

从实践仓库的当前问题开始：先看到现象，再讲原理、读相关代码、做一个小实验，最后分别保存理论与实际证据。不要重新安装环境，不要求从空白重写工程，也不因为调整仓库就把个人学习状态标成完成。
