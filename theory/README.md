# 理论讲义｜带着实践问题来查

本目录解释原理，不存放运行工程。先看 [唯一实践进度](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md)，再选当前需要的一小段；不要求按编号全部学完才运行程序。

| 讲义 | 要回答的问题 | 关联实践 |
| --- | --- | --- |
| [01 目标速度与控制](01-target-speed-and-control.md) | 目标与实际为什么不同，SLOWER 到底改了什么 | 现有 demo 的低速档位与速度打印 |
| [02 step 与反馈](02-step-and-feedback.md) | 一步发生什么，为什么每一步要重新观察 | demo 主循环与环境 step |
| [03 观察与相对运动](03-observation-and-relative-motion.md) | 观察表如何换算，距离规则有哪些盲区 | demo 车辆筛选与距离判断 |

这三份是已准备的材料，不代表三节课已经讲完，更不代表学习者独立掌握。当前题目和理解证据不写在本目录。

每篇讲义提供真实代码入口、必要的数值例子、适用边界与源码版本；具体修改和运行指令由实践仓库当前进度承接，不在这里再发一份动手任务。

更多方向见 [知识路线](../ROADMAP.md)，完整双向映射见 [PRACTICE_MAP.md](../PRACTICE_MAP.md)。返回 [项目首页](../README.md)。
