# 当前任务｜阶段 1：收尾 HighwayEnv 主线

**做法：做项目，用到哪里读到哪里。** 不再逐行读完 HighwayEnv 全部代码（2026-10-07 调整，旧计划见 [archive/notes/2026-10-07-current-task-before-replan.md](../../archive/notes/2026-10-07-current-task-before-replan.md)）。

## 三阶段路线

| 阶段 | 做什么 | 产出 | 预计 |
| --- | --- | --- | --- |
| **1. 收尾 HighwayEnv 主线** | 只读一次闭环的关键代码：step 循环、控制器、自行车模型、IDM/MOBIL、找前后车、观察表 | 能不看代码画出一次 `env.step` 的调用链，讲清每一步 | 2–3 天 |
| **2. 规则规划 + 批量评测** | 自己写跟车 + 变道规则；批量评测脚本；训练 DQN 对比 | 一个可放 GitHub 的项目：策略、评测报告、失败分析 | 1–2 周 |
| **3. 换到真实数据** | 用 nuPlan / Waymo Open Motion 等真实轨迹数据做预测或规划，比较开环与闭环 | 对应预测规划、数据闭环岗位的作品 | 之后再定 |

## 阶段 1 清单

源码根目录：`C:\company\own\highwayenv-learning\highway_env\`。每项读完做一个小动手（打印或改一个数），能讲清就打勾。整条链的总图见教材[附录 A](../../learning/BOOK.zh-CN.md#appendix-a)。

| # | 读什么 | 看懂什么 | 教材对应 |
| --- | --- | --- | --- |
| 1 | `envs/common/abstract.py`：`step`、`_simulate`（第 260–318 行是核心） | 一步怎样拆成多个物理小步；动作只在第一个小步下达 | 1.4 |
| 2 | `envs/highway_env.py` 第 71–155 行 | 怎样造车、奖励怎样算、什么时候结束 | 4.5 |
| 3 | `vehicle/controller.py` 第 89–230 行：`act`、`steering_control`、`speed_control` | 变道指令怎样变成转向角，目标速度怎样变成加速度 | 1.2、3.3、3.4 |
| 4 | `vehicle/kinematics.py` 第 123–170 行：`act`、`step` | 自行车模型怎样更新位置、朝向和速度 | 1.3、3.5 |
| 5 | `vehicle/behavior.py` 第 150–330 行：`acceleration`（IDM）、`mobil` | **最重要，阶段 2 要用**：背景车怎样跟车、怎样决定变道 | 待讲 |
| 6 | `road/road.py` 第 475–530 行：`act`、`step`、`neighbour_vehicles` | 所有车怎样一起推进；怎样找前车和后车 | 附录 A |
| 7 | `envs/common/observation.py` 第 243 行起：`KinematicObservation.observe` | 观察表的每一行、每一列怎么来的 | 第 2 章 |
| 8 | `vehicle/objects.py` 第 95–140 行 | 碰撞怎样检测（看大意即可） | 附录 A |

当前进度：

- [ ] 1. 已讲到第 318 行（`step`、`_simulate` 已讲），第 320 行以后快速导航即可
- [ ] 2.
- [ ] 3.
- [ ] 4.
- [ ] 5.
- [ ] 6.
- [ ] 7.
- [ ] 8.

其余文件（其他场景、道路生成、显示、不确定性预测等）不逐行读，阶段 1 结束时用一张表各写一句话职责。

**完成标准：** 不看代码画出 `env.step(action)` → 动作对象 → 控制器 → 运动模型 → 道路推进 → 碰撞 → 观察 / 奖励 的调用链；说出 IDM 公式里每一项的驾驶含义。

## 阶段 2 预告（阶段 1 完成后细化）

1. **规则策略**：只用观察表（不偷看模拟器内部），按 IDM 思路选加减速，按 MOBIL 思路判断是否变道。起点是教材第 2 章的跟车规则，2.8 节列的问题就是要改的地方。
2. **批量评测**：调参用的种子和最终测试用的种子分开；指标为碰撞率、平均速度、变道次数、最小碰撞时间（TTC）；输出表格和图。
3. **学习策略对比**：参考 HighwayEnv 仓库的 `scripts/sb3_highway_dqn.py` 训练 DQN，在同一组种子上与随机动作、规则策略比较。
4. **报告**：README 写清方法、结果表、失败案例回放、局限。

代码放在 `experiments/highway_driving/` 下，文件名到时再定。

## 阶段 3 预告

开始前再选数据集、核对硬件和依赖。候选：nuPlan、Waymo Open Motion、nuScenes 的轨迹预测 / 规划任务。
