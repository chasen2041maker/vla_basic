# 当前任务｜阶段 1：收尾 HighwayEnv 主线

2026-10-07（America/Denver）本人同意调整学习方式：**不再逐行读完 HighwayEnv 全部代码，改为“做项目，用到哪里读到哪里”。** 原 5 天 40 小时计划停止，旧版本见 [archive/notes/2026-10-07-current-task-before-replan.md](../../archive/notes/2026-10-07-current-task-before-replan.md)。

## 三阶段路线

| 阶段 | 做什么 | 产出 | 预计 |
| --- | --- | --- | --- |
| **1. 收尾 HighwayEnv 主线** | 只读一次闭环的关键代码：step 循环、控制器、自行车模型、IDM/MOBIL、找前后车、观察表 | 能不看代码画出一次 `env.step` 的调用链，讲清每一步 | 2–3 天 |
| **2. 规则规划 + 批量评测小项目** | 自己写跟车+变道规则策略；批量评测脚本；训练 DQN 对比 | 一个可放 GitHub 的项目：策略、评测报告、失败分析 | 1–2 周 |
| **3. 换到真实数据** | 用 nuPlan / Waymo Open Motion 等真实轨迹数据做预测或规划模型，比较开环与闭环评测 | 对应预测规划、数据闭环岗位的作品 | 之后再定 |

## 阶段 1 清单

源码根目录：`C:\company\own\highwayenv-learning\highway_env\`。每项读完做一个小动手（打印或改一个数），能讲清就打勾。

- [ ] **1. 环境骨架** `envs/common/abstract.py`
  - 已讲：第 1–162 行（导入、`__init__`、配置叠加、`define_spaces`）
  - 待讲：第 164–258 行（奖励/结束占位、`_info`、`reset`），第 260–318 行（`step`、`_simulate`，**核心**）
  - 第 320 行以后（显示、环境副本、多车包装）只看一眼知道是干什么的
- [ ] **2. 场景回顾** `envs/highway_env.py` 第 71–155 行：造车、奖励、结束条件（已读过，快速回顾）
- [ ] **3. 控制器** `vehicle/controller.py` 第 89–230 行：`act`、`steering_control`、`speed_control` —— 变道指令怎么变成转向角，目标速度怎么变成加速度
- [ ] **4. 车辆运动** `vehicle/kinematics.py` 第 123–170 行：`act`、`step` —— 自行车运动学模型，位置和速度怎么更新
- [ ] **5. 背景车的驾驶规则（最重要，阶段 2 要用）** `vehicle/behavior.py` 第 150–330 行：IDM 跟车加速度 `acceleration`、MOBIL 变道判断 `mobil`
- [ ] **6. 道路推进与找前后车** `road/road.py` 第 475–530 行：`act`、`step`、`neighbour_vehicles`
- [ ] **7. 观察表怎么来** `envs/common/observation.py` 第 243 行起 `KinematicObservation.observe`
- [ ] **8. 碰撞检测** `vehicle/objects.py` 第 95–140 行，看大意即可

其余文件（其他场景、道路生成、显示、不确定性预测等）不逐行读，阶段 1 结束时用一张表各写一句话职责。

**阶段 1 完成标准：** 能画出 `env.step(action)` → 动作对象 → 控制器 → 运动模型 → 道路推进 → 碰撞 → 观察/奖励 的调用链；能说出 IDM 公式里每一项的驾驶含义。

## 阶段 2 预告（阶段 1 完成后细化）

1. **规则策略**：自车只用观察表（不偷看模拟器内部），按 IDM 思路选加减速，按 MOBIL 思路判断是否变道。
2. **批量评测**：固定两组种子（调参用、最终测试用分开）；指标为碰撞率、平均速度、变道次数、最小碰撞时间；输出表格和图。
3. **学习策略对比**：参考 `scripts/sb3_highway_dqn.py` 训练 DQN，与随机动作、规则策略在同一组种子上比较。
4. **报告**：README 写清方法、结果表、失败案例回放、局限。

代码放在 `vla_basic/experiments/highway_driving/` 下，具体文件到时再定。

## 阶段 3 预告

开始前再选数据集、核对硬件和依赖；候选：nuPlan、Waymo Open Motion、nuScenes 的轨迹预测/规划任务。
