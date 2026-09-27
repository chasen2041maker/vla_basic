# 理论讲义｜带着实践问题来查

本目录解释原理，不存放独立仿真/训练工程。先看 [唯一实践进度](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md)，再选择对应讲义；不要求按编号全部学完才能运行程序。

| 讲义 | 要回答的问题 | 材料范围 |
| --- | --- | --- |
| [01 目标速度与控制](01-target-speed-and-control.md) | 目标与实际为什么不同，SLOWER 到底改了什么？ | 已有实践 demo 与控制器源码带读 |
| [02 step 与反馈](02-step-and-feedback.md) | 一步发生什么，为什么每一步重新观察？ | 主循环、环境时间与结束标记 |
| [03 观察与相对运动](03-observation-and-relative-motion.md) | 观察表如何换算，距离规则有哪些盲区？ | 车辆筛选、坐标/归一化和规则边界 |
| [04 评测与证据](04-evaluation-and-evidence.md) | 如何知道一次修改真的更好？ | 配对比较、指标验证、零失败统计小例子；批量评测器未交付 |
| [05 从状态到相机](05-state-to-camera-bridge.md) | 从真值表格到图像究竟缺了哪几步？ | 坐标/投影可运行例子、数据契约与迁移方案；真实数据适配器未交付 |
| [06 数学与工程检查](06-engineering-and-math-checkpoints.md) | C++/Linux 和数学怎样在项目里落到实处？ | 可编译局部例子、故障注入、分方向深化；非车端项目 |

01–03 为此前材料；04–06 为 2026-09-27 新增补充讲义。局部数学与 C++ 例子的维护者检查见 [审查记录](../notes/2026-09-27-curriculum-review.md)，不等于用户实验、完整课程集成或个人掌握。

需要公式验证时，按正文把小代码复制到临时目录；这些临时文件不是仓库中已存在的训练或驾驶入口。当前实践任务、实验日志和理解状态仍只写在实践仓库，不把新增讲义自动变为当前作业。

更多方向见 [知识路线](../ROADMAP.md)，对应关系见 [PRACTICE_MAP.md](../PRACTICE_MAP.md)，材料交付规则见 [CURRICULUM_STANDARD.md](../CURRICULUM_STANDARD.md)。返回 [首页](../README.md)。
