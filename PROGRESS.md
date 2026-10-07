# 学习进度

更新：2026-10-07（America/Denver）

## 现在在哪

- **阶段 1 第 1 项**：读 `C:\company\own\highwayenv-learning\highway_env\envs\common\abstract.py`，已讲到第 318 行（奖励/结束占位、`_info`、`reset`、`step`、`_simulate`）。
- 教材 [learning/BOOK.zh-CN.md](learning/BOOK.zh-CN.md) 已改写成更好读的版本；1.4 节和[附录 A 源码地图](learning/BOOK.zh-CN.md#appendix-a)正好对应现在读的 `step` / `_simulate`，可以拿来复习。

## 下一步

1. 在 HighwayEnv 仓库的 01 练习里，`env.step(action)` 后面加一行 `print("reward：", round(reward, 3))`，运行，看前两步的 reward 是否和讲解手算的 0.822 一致：
   ```powershell
   conda activate py310
   cd C:\company\own\highwayenv-learning\learning\demos
   python .\01_lane_change.py
   ```
2. `abstract.py` 第 320 行以后快速过一遍（显示、环境副本、多车包装，知道是干什么的即可）。
3. 进入清单第 2 项：`highway_env.py` 回顾。

## 已经做过

- 跟车规则跑通，亲手改过减速距离；01 变道、04 调速跑过并改过参数（04 的目标速度现在是 10）。
- 读完 `action.py`、`highway_env.py`；`abstract.py` 讲到第 318 行。
- 能解释“目标 20、实际 25 时车会减速”；能说出 Fast 版更快是因为每局计算次数少。
- 本机建好 Conda `py310`，HighwayEnv 源码可编辑安装；记住要用 `python`，不要用 `py`。

## 卡点

- HighwayEnv 里的 01 练习现在有 5 辆背景车，第 3 步会撞；想看完整变道，把 `vehicles_count` 改成 0。

---

学习流水记录在 [learning/LEARNING_LOG.md](learning/LEARNING_LOG.md)（每次一到三行）。2026-10-07 之前的详细进度在 [archive/notes/2026-10-07-progress-before-replan.md](archive/notes/2026-10-07-progress-before-replan.md)。
