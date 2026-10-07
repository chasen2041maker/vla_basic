# 实验目录

六个小实验，每个对应教材里的一节。讲解都在 [教材](../../../learning/BOOK.zh-CN.md) 里，这里只放运行方法和“改哪里”。

先进入环境和项目目录（每次开新终端做一次）：

```powershell
conda activate py310
cd C:\company\own\vla_basic
```

## 一览

| 实验 | 看什么 | 运行 | 动手改哪里 | 教材 |
| --- | --- | --- | --- | --- |
| [04_target_speed.py](04_target_speed.py) | 目标速度一变，实际速度怎样慢慢跟上（道路 + 速度曲线） | `python experiments\highway_driving\demos\04_target_speed.py` | 顶部 `TARGET_SPEED`（原版 20，你现在是 10） | 1.5 |
| [00_following.py](00_following.py) | 按前车距离选加速 / 保持 / 减速 | `python experiments\highway_driving\demos\00_following.py` | `if nearest_distance < 40:`（不要改三引号里的旧代码） | 2.1、2.6 |
| [01_lane_change.py](01_lane_change.py) | 一次右变道：目标车道先变，位置慢慢过去 | `python experiments\highway_driving\demos\01_lane_change.py` | `if step == 2:` | 3.1、3.3 |
| [05_compare_actions.py](05_compare_actions.py) | 同一起点，一直 IDLE vs 一直 SLOWER，生成网页报告 | `python experiments\highway_driving\demos\05_compare_actions.py` | 顶部 `MAX_STEPS` | 4.2、4.4 |
| [03_continuous_action.py](03_continuous_action.py) | 连续动作：直接给加速度和转向角 | `python experiments\highway_driving\demos\03_continuous_action.py` | `action = np.array([0.5, -0.2])` | 3.6 |
| [02_action_space.py](02_action_space.py) | 动作空间有多大，哪些编号合法 | `python experiments\highway_driving\demos\02_action_space.py` | — | 3.2 |

操作提示：

- **04**：空格暂停，R 重播，Esc 关闭。改了文件要关掉窗口重新运行，R 不会重新读文件。
- **00、01**：在终端按 Ctrl+C 停止。
- **05**：没有车辆窗口，跑完会用浏览器打开报告；报告保存在 `outputs/highway_driving/compare-actions/<时间>/`。

## 各实验的设置

物理频率都是 15 Hz。决策频率不同，所以“一步”的长度不同：

| 实验 | 决策频率 | 一步 | 其他车辆 | 种子 | 时长 | 速度档位 (m/s) | 观察 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 04 | 5 Hz | 0.2 秒 | 0 | 0 | 8 秒 | 直接设内部目标 | — |
| 00 | 1 Hz | 1 秒 | 50 | 0 | 每局 40 秒 | 0, 5, …, 30 七档 | 默认：归一化，相对量 |
| 01 | 1 Hz | 1 秒 | 0 | 0 | 10 秒 | 20, 25, 30 | 只打印内部的目标车道和 y |
| 05 | 5 Hz | 0.2 秒 | 0 | 7 | 8 秒 | 20, 25, 30 | 不归一化，单位米、m/s |
| 03 | 1 Hz | 1 秒 | 0 | 0 | — | 连续动作 | — |

几个容易混的地方：

- 00 的 `x * 200`、`y * 16` 只对它的默认观察成立（4 车道、归一化）。05 用的记录器关掉了归一化，不能再乘。
- 00 每局都用同一个种子重开，跑很多局也是同一种路况。
- 04 是直接改车辆内部的目标速度，只为观察控制器；正常策略应该发 `SLOWER` 这类动作。
- HighwayEnv 仓库的 `learning/demos/01_lane_change.py` 是你自己改过的另一份（`highway-fast-v0`、5 辆背景车），用于源码阅读练习，和这里的 01 设置不同。

<details>
<summary>维护：无窗口运行和来源</summary>

无窗口调用（测试和 CI 用）：00 的 `main(render_mode=None, max_steps=3)`，01 的 `main(render_mode=None)`，04 的 `run_demo(headless=True)`，05 的 `run_comparison(open_browser=False)`。04 不传 `target_speed` 时用文件顶部的值。

完整检查：`python scripts\check_repo.py --with-highway`。

来源：00、02、03 是你最初在 HighwayEnv 仓库写的练习，2026-09-27 迁入本项目（清单见 [archive/notes/2026-09-27-project-consolidation.json](../../../archive/notes/2026-09-27-project-consolidation.json)）；之后 00 加了固定种子和动作前后的时间打印，规则没变。01、04、05 是助手为教材写的。早期运行记录在 [learning/evidence/](../../../learning/evidence)。

</details>
