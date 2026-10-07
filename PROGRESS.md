# 唯一学习进度

更新时间：2026-10-07（America/Denver）

## 现在在哪

- 路线：三阶段（收尾 HighwayEnv 主线 → 规则规划+评测项目 → 真实数据），详见 [CURRENT_TASK](experiments/highway_driving/CURRENT_TASK.md)。
- 当前：**阶段 1 第 1 项**，`C:\company\own\highwayenv-learning\highway_env\envs\common\abstract.py` 已讲到第 318 行（奖励/结束占位、`_info`、`reset`、`step`、`_simulate` 已讲）。
- 下一步：看 01 练习打印的 reward 是否与讲解的 0.822 吻合；然后 `abstract.py` 第 320 行以后快速导航，进入第 2 项 `highway_env.py` 回顾。

## 已经做过

- 跟车规则 demo 跑通，亲手改过减速距离；01 变道、04 调速跑过并改过参数。
- 读完 `action.py`、`highway_env.py`；`abstract.py` 读到第 162 行。
- 能解释“目标速度 20、实际 25 时车会减速”；能说出 Fast 版更快是因为每局计算次数变少。

## 卡点 / 待办

- 本机依赖：方案为系统 Python 直接 `py -m pip install -e .`（在 highwayenv-learning 根目录），安装结果待确认；`noise` 若编译失败需装微软 C++ 生成工具。
- 01 练习当前是 5 辆背景车，第 3 步会撞；想看完整变道可把 `vehicles_count` 改为 0。

## 记录方式

本页只写当前位置、做过什么、卡点、下一步。每次学习在 [learning/LEARNING_LOG.md](learning/LEARNING_LOG.md) 追加一到三行。2026-10-07 之前的详细进度在 [archive/notes/2026-10-07-progress-before-replan.md](archive/notes/2026-10-07-progress-before-replan.md)。

学习者背景见 [docs/LEARNER_PROFILE.md](docs/LEARNER_PROFILE.md)，教材 [learning/BOOK.zh-CN.md](learning/BOOK.zh-CN.md) 第 1–4 章按需参考。
