# Highway Driving｜驾驶决策与失败分析实验

## 这是什么，不是什么

这是 `vla_basic` 当前主项目。先借 HighwayEnv 的道路、车辆、控制器和模拟状态，自己维护实验入口、策略、日志、评测与失败分析。

长期追问：**前车更慢时，怎样调整行为，又怎样证明修改有用？** 当前 H001 只打通观察和动作的真实交互，还没有固定慢前车场景、跟车规则、视觉网络、强化学习或驾驶 VLA。默认种子复现的是随机生成场景，不保证每次都有特定的慢前车事件。

## 安装与第一跑

推荐 Python 3.12。先按 [根 README](../../README.md#直接运行) 创建独立环境。下列 `python` 均指该环境解释器，命令从仓库根目录执行：

```bash
python -m pip install -r experiments/highway_driving/requirements.txt
python experiments/highway_driving/run_episode.py --seed 7 --action IDLE
```

不要为本轮安装 PyTorch、训练框架或 GPU 工具链。`requirements.txt` 固定直接依赖，不是全量依赖锁文件；CI 用 `pip-freeze.txt` 留下实际解析版本，摘要也记录核心包、Python 和代码版本。不要把同种子误当成跨版本、跨平台逐位一致的承诺。

三种显示方式：默认 `--render rgb_array` 保存画面；`--render human` 打开窗口并保存日志；`--render none` 仅保存日志。无桌面时默认方式更合适，原生 Windows 窗口需要在学习者电脑另验。

```bash
# 首先只取得初始观察，执行一个明确动作
python experiments/highway_driving/run_episode.py --max-steps 1

# 运行一个回合并看窗口
python experiments/highway_driving/run_episode.py --render human

# 在同种子下改变动作；每次自动建立独立输出目录
python experiments/highway_driving/run_episode.py --seed 7 --action SLOWER
```

其余选项：`--duration-seconds` 默认 8，允许 (0,60]；`--vehicles` 默认 12；`--max-steps` 默认 50；`--output-dir` 指定一个**尚不存在**的目录。拒绝覆盖旧输出。参数不合法、依赖缺失或写入失败时非零退出；没有完整 `summary.json` 的目录不作为完成证据。

## 环境交互：不是旧 Lab 的合成 trace

```text
reset(seed) → 初始 obs
                   ↓
选择本轮明确的高层动作（目前恒定，不依据 obs）
                   ↓
step(action) → 新 obs、reward、terminated、truncated、info
                   ↓
记录 → 未结束则继续；结束后 close，不自动重开一轮
```

HighwayEnv 真正推动车辆并返回下一观察。但“真实模拟器交互”不等于“策略已经利用反馈”；本轮恒定动作只提供可对比的基线。

## 观察契约：先把值读对

配置固定为 `Kinematics`，列顺序是 `[presence, x, y, vx, vy]`，形状为 `(5, 5)`。场景中 12 辆其他车与观察中的 5 行不是同一概念：后者包括自车，只保留有限附近车辆。

`normalize=False`、`clip=False`：位置单位为米，速度为米/秒，不把归一化值当真实物理量。

`absolute=False` 的特殊处：**第 0 行自车仍是世界绝对位置/速度；其余有效行才是“其他车减自车”的位置差/速度差。轴仍与世界坐标对齐，不会随自车航向旋转。** 因而不能把自车位置期待为零，也不能直接把其他行的 `vx` 当对方绝对速度。

`presence=0` 表示空槽，不代表有辆静止汽车在原点。`order=sorted` 表示附近车辆排序，行号不是稳定车辆 ID；不要直接逐行相减当成同一辆车的历史。

观察来自模拟器的车辆状态。俯视 PNG/GIF 是可视化，不是已实现的相机感知系统。

## 动作契约：IDLE 不等于停车

使用 `DiscreteMetaAction`。代码按环境的动作名称映射查找编号，不写死整数。

| 名称 | 语义 |
|---|---|
| IDLE | 不改变目标车道/目标速度，底层控制器仍工作 |
| SLOWER / FASTER | 在 `[20,25,30]` m/s 目标速度档位中降低/提高目标 |
| LANE_LEFT / LANE_RIGHT | 请求相邻目标车道，由底层控制器跟踪 |

**SLOWER 不是紧急制动，最低目标 20 m/s，不保证能停车或避免碰撞。** 连续发送可能到达档位边界。日志保留 `action_available`，不可用请求不能当作车辆确实完成该动作的证据。

## 时间与结束原因

`simulation_frequency=15` Hz，`policy_frequency=5` Hz：当前配置一轮策略动作对应 3 次物理更新，正常情况下是 0.2 秒。日志读取环境的实际 `time`，不把循环次数直接当秒数。修改频率时需重新检查整除关系、测试和 GIF 帧间隔。

`trace.jsonl` 每行成对保存当前观察及其时间、动作、下一观察及其时间。GIF 只采样策略时刻，约 5 帧/秒，不含全部物理帧。

`end_reason` 区分 `collision`、`off_road`、其他 `terminated`、`environment_time_limit`、`runner_step_limit`。同时保留原始 `terminated` 和 `truncated`，二者可能同时为真。脚本步数上限是运行器停止，不伪造环境 `truncated=True`。

跑到时间上限、累计奖励高、进程返回 0，都不等于安全驾驶验证通过。

## 一次运行保存什么

```text
outputs/highway_driving/<本次 UTC 时间>/
├── initial.png         # 初始画面（默认模式）
├── final.png           # 最后画面
├── episode.gif         # 策略时刻的回放
├── trace.jsonl         # 每一步的状态、动作、时间和结果
└── summary.json        # 配置、版本、种子、初末状态和结束原因
```

输出目录已被仓库现有 `.gitignore` 排除。不要提交大量二进制、数据集或真实车辆日志。需要共享结论时，在 `notes/` 写最小复现条件与证据引用。

## 验证与边界

```bash
python scripts/check_repo.py --with-highway
```

纯逻辑测试检查参数和结束分类；真实环境测试检查观察物理单位/相对关系、空槽、一步运动与时间、同种子复现、SLOWER 改变运动、两类停止条件、日志连续性及图片文件。缺依赖直接失败，不跳过真实测试来制造绿色状态。

这些检查只能证明当前实验入口和记录满足已测契约，不能证明一般驾驶安全。工程执行证据与学习者掌握证据分别见 [工程记录](../../notes/2026-09-22-highway-entry.md) 和 [PROGRESS](../../PROGRESS.md)。

## 当前只读哪段代码

先看 `run_episode.py` 的 `make_env()` → `run_episode()` 中 `reset` 与 `step` → 日志里的对应字段。暂时不逐行讲命令行和保存细节。按 [CURRENT_TASK](CURRENT_TASK.md) 预测一个变化，再做一次小修改。

## 官方依据

- [上游仓库](https://github.com/Farama-Foundation/HighwayEnv)
- [入门与配置](https://highway-env.farama.org/quickstart/)
- [观察：自车绝对量、其他车相对量和空槽](https://highway-env.farama.org/observations/)
- [动作：高层动作与底层控制器](https://highway-env.farama.org/actions/)
- [时间频率与录制说明](https://highway-env.farama.org/faq/)
- [采用的 HighwayEnv 1.12.1 发布页](https://pypi.org/project/highway-env/1.12.1/)
