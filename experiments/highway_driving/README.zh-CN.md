# Highway Driving｜驾驶决策与失败分析实验

## 这是什么，不是什么

这是 vla_basic 当前主项目。借 HighwayEnv 的道路、车辆、控制器和模拟状态，逐步维护实验入口、策略、日志、评测与失败分析。长期问题是：前车更慢时怎样调整行为，又怎样证明修改有用？

当前 H001 只打通观察和动作的真实交互；没有固定慢前车场景、跟车规则、视觉网络、RL 或驾驶 VLA。默认种子复现随机生成场景，不保证出现特定慢前车事件。

## GPT 怎么教，你与 Codex 怎么做

[AGENTS.md](../../AGENTS.md) 是角色和进度规范；[CURRENT_TASK.md](CURRENT_TASK.md) 把老师讲解和有限动手分开；[H001 带读](walkthrough/H001-idle-step.md) 提供具体课堂材料。当前实际进度只看 [PROGRESS.md](../../PROGRESS.md)。

GPT 先示范如何跟代码、读日志，核对学习者理解；你与 Codex 再执行已激活的动手卡。Codex 更新客观工程证据，不自行升级个人掌握。第一课可以只运行与解释，不为形式造新功能。

## 安装与第一跑

使用 Python 3.12，按 [根 README](../../README.md#直接运行) 建独立环境。下面的 python 均指虚拟环境解释器，命令从仓库根目录执行：

```bash
python -m pip install -r experiments/highway_driving/requirements.txt
python experiments/highway_driving/run_episode.py --seed 7 --vehicles 0 --max-steps 1 --action IDLE
```

这里 0 辆其他车、1 步是第一课的控制条件，不是默认配置被改成空场景。需要附近车辆观察时使用 `--vehicles 12`；需要完整回合时去掉 `--max-steps 1`。

本轮不需要 PyTorch、训练框架或 GPU。requirements.txt 固定直接依赖，不是全量锁文件；CI 留下 pip-freeze.txt，摘要记录核心包、Python、平台、代码版本与脚本哈希。同种子不意味着跨版本跨平台逐位一致。

显示模式：默认 `--render rgb_array` 保存画面；`--render human` 打开窗口并保存日志；`--render none` 只保存日志。无桌面时用默认模式，原生 Windows 窗口仍需本机另验。

其余参数：`--duration-seconds` 默认 8，允许 (0,60]；`--vehicles` 默认 12；`--max-steps` 默认 50；`--output-dir` 必须是尚不存在的目录。拒绝覆盖旧输出；参数、依赖或写入错误时非零退出。没有完整 summary.json 的目录不能作为完成证据。

## 环境交互

```text
reset(seed) → 初始 obs
→ 当前恒定高层动作（目前不依据 obs 选择）
→ step(action) → 新 obs、reward、terminated、truncated、info
→ 记录；未结束则继续，结束后 close，不自动重开回合
```

环境确实推动车辆并返回新观察；这不意味着脚本已经依据反馈决策。旧 Lab 的合成 trace 不冒充本项目的实际模拟器交互。

## 观察契约

Kinematics 的列为 `[presence,x,y,vx,vy]`，形状 (5,5)。5 行含自车，只观察有限附近车辆；与场景默认 12 辆其他车不是同一数量。

normalize=False、clip=False，位置单位 m，速度分量 m/s。absolute=False 的特殊点：第 0 行自车仍为世界绝对位置/速度，其他有效行是“其他车减自车”的位置差与速度差。坐标轴仍与世界对齐，不随自车航向旋转。

presence=0 是空槽，不是原点的一辆静止车。order=sorted 的行号不是稳定车辆 ID，不可直接按前后同一行推导同车历史。负相对 vx 不等于对方一定倒车。

观察来自模拟器状态，PNG/GIF 是俯视可视化，不是相机感知系统。

## 动作契约

DiscreteMetaAction 使用名称查编号，不写死整数：

| 动作 | 含义 |
|---|---|
| IDLE | 不改变目标车道/目标速度，底层控制继续工作 |
| SLOWER / FASTER | 降低/提高目标速度档位，当前档位 [20,25,30] m/s |
| LANE_LEFT / LANE_RIGHT | 请求相邻目标车道，由底层控制跟踪 |

SLOWER 不是紧急制动，最低目标 20 m/s，不保证停车或避碰。连续请求可能到档位边界。action_available 只说明请求可用性，不证明安全或动作已经完成。

## 时间与结束

simulation_frequency=15 Hz、policy_frequency=5 Hz：当前正常一个决策步是 3 次物理更新、0.2 秒。日志读环境实际 time，不把循环次数或程序耗时当仿真秒数。改频率时须复核整除关系、测试与 GIF 间隔。

GIF 仅采样策略时刻，约 5 帧/秒，不含所有物理帧。日志成对记录动作前后的观察和时间。

end_reason 区分 collision、off_road、其他 terminated、environment_time_limit、runner_step_limit。原始 terminated/truncated 保留，二者可同时为真；运行器步数上限不伪造 truncated=True。

时间用尽、累计奖励高、进程退出 0 都不等于通过驾驶安全验证。

## 首步教学摘要与日志 schema v2

本次不改变环境、动作选择或观察列，只增加教学诊断：

| 字段 | 语义 |
|---|---|
| speed_before_mps | step 前的自车实际速率 |
| speed_mps | step 后实际速率，保留原字段含义 |
| target_speed_before_mps | step 前控制器目标速度；模拟器内部诊断 |
| target_speed_after_mps | step 后控制器目标速度；模拟器内部诊断 |
| summary.first_transition | 与 trace.jsonl 第一行相同的整条首步记录 |

实际速率不能总用世界 x 轴分量 vx 替代，尤其有侧向运动时。目标速度不是策略观察，不加入 observation、不参与新的决策。diagnostic_contract 记录来源和时间语义。

summary.schema_version 升为 2；原有字段保留。新格式器需要 v2 的 first_transition，不用旧日志缺失字段拼出假值；旧 v1 运行证据保留，不能据此声称已有目标速度记录。

终端显示首步动作、前后时间/位置/实际速率/目标速度和本步环境标志，另列整回合结束原因、步数与总仿真时间。显示保留三位小数，精确数值在 JSON 中。多步回合不能把首步动作与末步位置混作一条 transition。

## 输出

```text
outputs/highway_driving/<UTC 时间>/
├── initial.png
├── final.png
├── episode.gif
├── trace.jsonl
└── summary.json
```

目录由已有 gitignore 排除，不提交大量二进制、数据集或敏感车辆日志；有价值的复现条件和结论写到 notes，标注执行者。老师/维护者/Codex 运行不冒充学习者亲自运行。

## 验证

```bash
python scripts/check_repo.py --with-highway
```

原有纯逻辑与真实集成测试保留；新增教学摘要格式、首步/末步区分、目标/实际速率分离、直接模拟器逐步核对和 CLI 存盘一致性测试。缺依赖时集成失败，不 skip 来制造全绿。

这些检查只证明所测实验契约，不证明一般驾驶安全或学习者掌握。本次工程证据见 [维护记录](../../notes/2026-09-23-teacher-codex-handoff.md)。

## 官方依据

- [上游仓库](https://github.com/Farama-Foundation/HighwayEnv)
- [入门与配置](https://highway-env.farama.org/quickstart/)
- [观察](https://highway-env.farama.org/observations/)
- [动作](https://highway-env.farama.org/actions/)
- [控制器源码](https://highway-env.farama.org/_modules/highway_env/vehicle/controller/)
- [时间频率与录制](https://highway-env.farama.org/faq/)
- [采用的 1.12.1 发布页](https://pypi.org/project/highway-env/1.12.1/)
