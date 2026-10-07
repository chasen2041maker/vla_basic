# Highway Driving｜实验与记录器说明

这个目录是项目的模拟器阶段：在 HighwayEnv 里做驾驶决策、控制和评测实验。

- 学习讲解看 [教材](../../learning/BOOK.zh-CN.md)。
- 各个小实验怎么跑看 [demos/README.md](demos/README.md)。
- 当前任务看 [CURRENT_TASK.md](CURRENT_TASK.md)。

本页是 [`run_episode.py`](run_episode.py)（单回合记录器）的技术说明。教材第 4 章用到它，阶段 2 的批量评测也会在它的基础上扩展。

## 它做什么

```text
reset(seed) → 初始观察
   ↓
每一步发同一个高层动作（IDLE / SLOWER / ……，目前不看观察做决定）
   ↓
step(action) → 新观察、奖励、是否结束
   ↓
把“动作前观察 + 动作 + 动作后观察”写成一行日志 → 没结束就继续
```

这是一个**固定动作的基线**，用来对比和检查记录格式，还不是会避让的策略。

## 运行

```powershell
conda activate py310
cd C:\company\own\vla_basic
python experiments\highway_driving\run_episode.py --seed 7 --action SLOWER
```

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--seed` | 7 | 随机种子（非负整数） |
| `--action` | IDLE | IDLE / SLOWER / FASTER / LANE_LEFT / LANE_RIGHT |
| `--max-steps` | 50 | 脚本最多走几步 |
| `--duration-seconds` | 8 | 环境时长上限，(0, 60] |
| `--vehicles` | 12 | 其他车辆数，0–100 |
| `--render` | rgb_array | `rgb_array` 保存画面；`human` 开窗口；`none` 只存日志 |
| `--output-dir` | 自动按时间新建 | 必须是**不存在**的目录，不会覆盖旧结果 |

## 环境设置

3 车道，自车从 1 号车道出发；物理 15 Hz、决策 5 Hz，所以**一步 = 0.2 秒 = 3 个物理小步**。`offroad_terminal=True`（开出道路就结束）。

### 观察：不归一化，单位是米和 m/s

`Kinematics`，5 行 × 5 列，列为 `[presence, x, y, vx, vy]`，设置 `normalize=False, clip=False, absolute=False, order="sorted", see_behind=True`。

- **第 0 行是自车**：世界坐标里的绝对位置和速度。
- **其他行是“对方减自车”**：相对位置和相对速度。坐标轴和世界对齐，不随车头旋转。
- `presence=0` 是空行，不是停在原点的车。
- 行号不是车辆 ID，相邻两步的同一行可能是不同的车。

这和 00 跟车实验的默认观察（归一化）不同，不能套用 `x * 200`。

### 动作：IDLE 不等于停车

`DiscreteMetaAction`，代码按名字查编号，不写死整数。

| 名称 | 效果 |
| --- | --- |
| IDLE | 不改目标车道和目标速度，控制器继续工作 |
| SLOWER / FASTER | 在 `[20, 25, 30]` m/s 三档里降 / 升一档 |
| LANE_LEFT / LANE_RIGHT | 目标车道左 / 右移一条，由控制器去追 |

最低档是 20 m/s，所以 SLOWER **不是紧急刹车**，刹不停车。日志里的 `action_available` 只说明这个动作当时在可选列表里，不说明它安全。

### 结束原因 `end_reason`

| 值 | 含义 |
| --- | --- |
| `collision` | 撞车 |
| `off_road` | 开出道路 |
| `terminated` | 环境的其他结束条件 |
| `environment_time_limit` | 跑满环境时长 |
| `runner_step_limit` | 脚本步数用完，**环境本身没结束** |

原始的 `terminated`、`truncated` 也都保存。

## 输出文件

```text
outputs/highway_driving/<UTC 时间>/
├── initial.png    初始画面
├── final.png      最后画面
├── episode.gif    每一步一帧的回放（约 5 帧/秒，不含物理小步）
├── trace.jsonl    每行一步：动作前观察与时间、动作、动作后观察与时间、奖励、速度、目标速度……
└── summary.json   配置、种子、版本、初末观察、结束原因
```

`summary.json` 最后才写；没有它的目录说明那次运行没正常完成。`outputs/` 不进 Git。

## 安装（新机器）

本机已经有 `py310` 环境，不用重装。新机器用 Python 3.12：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r experiments/highway_driving/requirements.txt
```

`requirements.txt` 固定了 highway-env 1.12.1 等直接依赖，CI 用的就是它。本机 `py310` 装的是 HighwayEnv 源码开发版，两者个别数值可能略有不同。

## 测试

```powershell
python scripts\check_repo.py --with-highway
```

覆盖：参数校验、结束原因分类、观察单位和相对关系、空行、一步的时长、同种子可复现、SLOWER 确实改变运动、日志前后连续、回放图片不是空白；以及 00 / 04 / 05 三个实验的无窗口运行。缺依赖会直接失败，不会跳过。

## 参考

- [HighwayEnv 仓库](https://github.com/Farama-Foundation/HighwayEnv) · [文档](https://highway-env.farama.org/)
- [观察](https://highway-env.farama.org/observations/) · [动作](https://highway-env.farama.org/actions/) · [时间频率 FAQ](https://highway-env.farama.org/faq/)
