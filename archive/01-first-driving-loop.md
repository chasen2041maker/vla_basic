# 旧 H001 记录器带练｜保留作参考

[新版连续教材](../learning/BOOK.zh-CN.md) · 对应旧运行器 [H001](notes/2026-09-27-h001-task-history.md)

> 2026-09-27 核对：本篇基于旧运行器，其配置、频率和日志不同于当前实践库；不再是唯一活跃任务。实际接续以 [主项目 PROGRESS.md](../PROGRESS.md) 为准，不要求为本篇重做已有实验。

本章是人工智能驾驶项目的第一段实践：用已有代码理解“观察、动作、车辆运动、下一观察”的关系。HighwayEnv 在这里提供实验道路和车辆；我们要学的是驾驶系统如何工作，以及怎样用证据解释行为。

本章不需要训练模型。读一小节就做一个实验，把日志和自己的解释留下来；不要先把全部源码看完才运行。

## 1. 驾驶问题：我没有要求加速，车为什么还在走？

一辆车已经在行驶，你发出 `IDLE`，它继续前进。这不一定是程序故障：高层决策可以保持已有目标，而底层控制器继续维持车速和车道。要判断行为是否符合预期，得先问清动作到底送到了哪一层。

在完整驾驶系统中，本章的位置是：

```text
传感器 → 感知/状态估计 → 决策与规划 → 控制器 → 车辆运动
              ↑                                │
              └──────── 下一时刻反馈 ────────────┘

本章的简化：
模拟器给出状态 → 脚本给出固定高层动作 → 模拟器控制器 → 模拟车辆运动
      ↑                                                   │
      └─────────── 模拟器返回下一观察，脚本记录 ─────────────┘
```

脚本收到下一观察，但目前**没有根据观察改变动作**。这是有环境交互的恒定动作基线，还不是会跟车的反馈策略。以后加入模型，也必须说清模型接管哪一段，而不是只增加一个网络调用。

你熟悉的 tool calling 可以帮助理解“请求 → 执行 → 返回结果”。类比到车辆时要停一下：模拟器可以重置，真实车辆已经发生的运动不能像文本请求一样撤回重试。

## 2. 先知道本章输入、输出和分工

| 部分 | 本章输入与输出 | 负责什么 |
|---|---|---|
| HighwayEnv | 高层动作 → 车辆运动、新观察、奖励、结束信号 | 道路、其他车辆、控制器与物理更新 |
| `run_episode.py` | seed、动作、步数等参数 → 日志、摘要和回放 | 配置、调用 `reset/step`、记录证据、结束清理 |
| 当前“策略” | 运行前选定的动作 → 每步重复该动作 | 提供对照基线；不读取前车状态作决定 |
| 学习者 | 实际日志和源码 → 行为解释、预测、对照结论 | 判断时间、坐标、动作含义与结论边界 |

观察是模拟器提供的车辆状态，形状 `(5, 5)`，每行列顺序为 `[presence, x, y, vx, vy]`。PNG/GIF 是俯视回放，不是车载相机，也不是我们做出的视觉感知结果。

动作是 `DiscreteMetaAction` 高层目标请求，既不是轨迹序列、语言 token，也不是直接油门/制动量。`IDLE` 保持目标车道和目标速度；`SLOWER` 请求降低目标速度档位。档位为 `[20, 25, 30]` m/s，最低档仍在运动，不能把它当紧急制动。

正常现象是：初始车已在运动，发出 `IDLE` 后位置继续变化。需要检查的症状包括：误以为 IDLE 必须停车、把相对速度负值理解为对方倒车、把一次循环当一秒，或把无碰撞的一步当安全证明。

## 3. 第一次运行：只执行一个 IDLE

以下命令在 **Windows PowerShell、仓库根目录**执行。使用 Python 3.12 的独立环境，不需要激活虚拟环境；已建好环境时不必重复创建。

```powershell
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    py -3.12 -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install -r experiments/highway_driving/requirements.txt
.\.venv\Scripts\python.exe --version
```

如果 `py -3.12` 提示找不到对应版本，先安装 Python 3.12，再重试。不要因为本章叫“人工智能驾驶”就安装 PyTorch、GPU 工具链或下载模型；当前代码用不到它们。

下面为本次实验建立唯一目录名，并只执行一次动作。后续命令继续使用同一个 PowerShell 窗口里的变量。

```powershell
$h001RunTag = Get-Date -Format 'yyyyMMddTHHmmssfffffff'
$h001IdleDir = "outputs/highway_driving/h001-idle-$h001RunTag"
.\.venv\Scripts\python.exe experiments/highway_driving/run_episode.py --seed 7 --action IDLE --max-steps 1 --output-dir $h001IdleDir
$h001IdleExitCode = $LASTEXITCODE
Get-ChildItem -LiteralPath $h001IdleDir
```

默认不会弹出窗口，成功保存后目录含 `initial.png`、`final.png`、`episode.gif`、`trace.jsonl` 和 `summary.json`。打开首末图片或 GIF 看位置变化；画面帮助你理解场景，数值判断还要读日志。

`$h001IdleExitCode` 为 0 且有完整 `summary.json`，才说明这次运行和保存流程完成。遇到“实验未完成”，先保留错误信息；不要把只生成了一部分文件的目录当成运行成功。输出目录必须原先不存在，重跑时重新生成 `$h001RunTag`。

## 4. 读一条日志：把时间和物理量对上

读取第一条记录，再读本次摘要：

```powershell
$h001IdleStep = Get-Content -LiteralPath "$h001IdleDir/trace.jsonl" -TotalCount 1 | ConvertFrom-Json
$h001IdleSummary = Get-Content -LiteralPath "$h001IdleDir/summary.json" -Raw | ConvertFrom-Json
$h001IdleStep | Select-Object observation_time_s, action_name, action_available, next_observation_time_s, speed_mps, crashed, terminated, truncated | Format-List
$h001IdleStep.observation | ConvertTo-Json -Depth 5
$h001IdleStep.next_observation | ConvertTo-Json -Depth 5
$h001IdleSummary | Select-Object end_reason, steps, sim_time_s, python, packages, code_revision, runner_sha256 | Format-List
```

同一条记录的顺序是：

```text
observation_time_s 时刻的 observation
→ 提交 action_name
→ 环境推进
→ next_observation_time_s 时刻的 next_observation
```

`speed_mps`、`crashed` 和结束信号描述动作后的结果。`action_available` 是发出动作之前的可用性检查；它不保证目标已经完成，比如请求变道不等于下一瞬间已到相邻车道。

默认仿真频率 15 Hz，策略频率 5 Hz；一个策略动作期间正常发生 3 次物理更新，所以正常一步为 **0.2 秒**。这里是配置推导，不是本教程替你运行得到的日志。请用实际两个时间字段相减确认，而不是只抄 0.2。

```powershell
$h001IdleStep.next_observation_time_s - $h001IdleStep.observation_time_s
$h001IdleStep.next_observation[0][1] - $h001IdleStep.observation[0][1]
```

第一行计算时间差（秒）；第二行计算自车世界 x 方向位移（米）。两者能回答“环境真的推进了吗”。注意 0.2 秒是模拟时间，不能用终端运行耗时替代。

观察表的读法如下：

| 行/字段 | 物理意义 | 常见误读 |
|---|---|---|
| 第 0 行，即 `observation[0]` | 自车世界绝对位置和速度 | 以为 `absolute=False` 会令自车全零 |
| 其余 `presence=1` 的行 | 其他车辆减自车的位置差、速度差 | 把 `vx` 直接当对方绝对速度 |
| `presence=0` 的行 | 没有车辆的填充槽 | 当成原点有辆静止车 |
| `x, y` | 米；轴与世界坐标对齐 | 当成随自车朝向旋转的车体坐标 |
| `vx, vy` | 米/秒；`normalize=False`，未归一化 | 当成比例、km/h 或相机像素 |

`clip=False`，这里也没有把观察裁剪到归一化范围。`order=sorted` 表示附近车辆排序，**行号不是稳定车辆 ID**；多步后不能直接把第 2 行与上一时刻第 2 行当作同一辆车。

举一个**只用于理解、不是实测输出**的例子：自车世界 `vx=25` m/s，另一有效行 `vx=-3` m/s，表示对方世界 x 方向速度比自车小 3 m/s，对方对应分量为 22 m/s；负号本身不代表倒车。当前道路沿世界 x 方向延伸，但“世界轴”这个契约不会自动变成任意弯路上的前后左右。

默认场景有 12 辆其他车，而观察只有 5 行（含自车）。这个观察不能代表看到场景里全部车辆，也不能保证 seed 7 一定构成专门设计的慢前车事件。

## 5. 回到源码：只跟这四处走

打开 [run_episode.py](../experiments/highway_driving/run_episode.py)，按函数名定位，不必从文件第一行逐句翻译。

1. **`make_env()`**：找到 `observation`、`action`、`simulation_frequency` 和 `policy_frequency`。把刚读过的日志列名、单位及 0.2 秒对应回配置。环境负责把高层目标转成底层车辆运动，我们的脚本没有直接计算油门。
2. **`run_episode()` 的 `env.reset(seed=seed)`**：这时取得初始观察，并按动作名称查 `actions_indexes`。不要死记 IDLE 的整数编号；接口名和环境映射才说明你要发什么请求。
3. **循环里的 `env.step(action_id)`**：先读取动作前时间，再调用环境推进，随后记录动作后的时间和观察。注意 `action_id` 在循环前已确定，没有用 `obs` 重新计算动作。
4. **`obs = next_obs` 与退出条件**：这让下一步保存的当前观察接上前一步结果，但赋值本身不是“根据反馈作决策”。环境结束就 `break`；最后由 `end_reason()` 分类，`finally` 中关闭环境。

把其中最关键的几行并排看。下面是源码节选，中间省去了记录和渲染部分，供对照阅读；实际运行仍用原脚本：

```python
obs, _ = env.reset(seed=seed)
action_id = int(env.unwrapped.action_type.actions_indexes[action_name])

for step in range(1, max_steps + 1):
    observation_time_s = float(env.unwrapped.time)
    available = action_id in env.unwrapped.action_type.get_available_actions()
    next_obs, reward, terminated, truncated, info = env.step(action_id)
    # 原脚本在这里记录动作前后的观察、时间和结果。
    obs = next_obs
    # 原脚本还会按运行模式保存画面。
    if terminated or truncated:
        break
```

`reset` 给出起点，`step` 才产生新的车辆运动。`observation_time_s` 在 `step` 前取得，因此不能把它贴到动作后的状态上。当前 `action_id` 只在循环前选一次；即使 `obs` 已更新，下一轮仍然发送同一个动作。这几行把“收到反馈”和“利用反馈改变决策”的区别直接暴露出来。

现在合上这段文字，试着指着源码说出：“我的动作在哪里进入模拟器，车辆在哪里真正推进，日志中的两个时间在哪里取得？”如果只能说“for 循环执行一步”，还没解释清驾驶含义。

对应的 [真实环境测试](../experiments/highway_driving/tests/test_episode.py) 中，`test_padding_and_one_real_step` 检查空槽、运动和时间，`test_observation_contract_and_world_axes` 检查坐标关系，`test_saved_artifacts_and_trace_continuity` 检查记录连续性。测试给你契约依据；测试通过不代替你的解释。

## 6. 先写预测，再换成 SLOWER

先在自己的笔记里填下面三项，**填完再运行**：

```text
我的预测：SLOWER 单步之后，相对 IDLE 的自车速度会怎样？
依据：我认为它改变的是哪个目标，由谁使车辆速度发生变化？
验证字段：我要比较日志的哪些字段；哪些现象不能据此判断？
```

现在只改 `--action`，保持 seed 7、一步和其余配置一致。这里修改的是实验输入，不需要复制脚本或新增策略文件。

```powershell
$h001SlowerDir = "outputs/highway_driving/h001-slower-$h001RunTag"
.\.venv\Scripts\python.exe experiments/highway_driving/run_episode.py --seed 7 --action SLOWER --max-steps 1 --output-dir $h001SlowerDir
$h001SlowerExitCode = $LASTEXITCODE
$h001SlowerStep = Get-Content -LiteralPath "$h001SlowerDir/trace.jsonl" -TotalCount 1 | ConvertFrom-Json
$h001SlowerSummary = Get-Content -LiteralPath "$h001SlowerDir/summary.json" -Raw | ConvertFrom-Json

# 先核对初始条件，不只比较最终值。
$h001IdleSummary.initial_observation | ConvertTo-Json -Depth 5
$h001SlowerSummary.initial_observation | ConvertTo-Json -Depth 5

# 两次动作后的速度，以及动作后的自车世界 x 位置。
@($h001IdleStep, $h001SlowerStep) | Select-Object action_name, action_available, next_observation_time_s, speed_mps, @{Name='ego_world_x_m'; Expression={$_.next_observation[0][1]}} | Format-Table
```

核对两次 `summary.json` 中的版本、配置和初始观察，再说明结果是否符合预测。相同种子有助于同一环境下做对照，不保证跨依赖版本、跨平台逐位相同。需要继续试验时使用新输出目录，不覆盖这一组证据。

一次动作只观察了很短的响应，不能要求车速立即精确等于目标档位。日志没有直接保存每步目标速度，不能把 `speed_mps` 叫作“目标速度”。如果结果偏离预测，先查实际动作、可用性、时间和初始条件，再决定是否需要延长实验；不要直接改成“预测正确”。

本章没有写入任何实测速度或碰撞结论。表格里的结果来自你刚刚运行的文件；请保存你的事前预测与实际对照，而不是只写“运行成功”。

## 7. 可选排错：让错误停在参数边界

做一次不会改变驾驶实现的最小故障练习。先预测错误会发生在“创建环境前、环境推进时、保存结果时”的哪一步，再运行：

```powershell
.\.venv\Scripts\python.exe experiments/highway_driving/run_episode.py --max-steps 0
$h001InvalidExitCode = $LASTEXITCODE
$h001InvalidExitCode
```

根据现有代码，这个参数应被拒绝，提示 `max_steps 必须是正整数`，退出码非零。去 `validate_options()` 和 `main()` 定位拒绝与错误打印位置，用调用顺序说明为什么本次没有发生驾驶交互。这是 runner 参数/系统边界的问题，不能归咎于模型或车辆控制。

把参数改回 1，并使用新的输出目录即可恢复。不要为让它“通过”而删除校验。相关依据见 [test_logic.py](../experiments/highway_driving/tests/test_logic.py) 的 `test_invalid_options`。

## 8. 结束原因、评测边界和本章证据

读自己的 `summary.end_reason`：`collision` 是碰撞，`off_road` 是离路，`environment_time_limit` 是环境时限，`runner_step_limit` 是脚本先停止。单步实验如果没有环境终止，通常停在运行器步数上限；以实际日志为准。

运行器步数上限不会伪造 `truncated=True`。`terminated` 与 `truncated` 是原始信号，可能同时为真，因此脚本同时保留它们和结束分类。进程退出码 0 说明程序流程成功，不说明车辆安全。

本章的 `total_reward`、碰撞标志和结束原因来自**模拟环境交互回合**，属于闭环仿真运行的统计；它们不是离线数据上预测轨迹与标注轨迹的 open-loop 误差。这里又必须区分：环境交互已经发生，但当前策略不利用观察反馈。一次单步回合也不足以构成完整驾驶评测，更不是生产安全证明。

有依赖环境后，如需核对仓库工程契约，可运行完整检查：

```powershell
.\.venv\Scripts\python.exe scripts/check_repo.py --with-highway
```

不带 `--with-highway` 只检查旧 Lab 基线与编译，不代表真实 HighwayEnv 集成通过。缺依赖或没运行就记录“未验证”；不要把维护者或 CI 的结果填成自己的实验结果。

完成后提交给自己或讲解者的最小笔记是：

```text
代码版本 / runner_sha256 / Python / 依赖版本：
seed / 两次动作 / max_steps / 输出目录 / 退出码：
我的事前预测：
初始条件是否一致，依据是什么：
动作前后时间、IDLE 与 SLOWER 的实测字段对照：
用自己的话解释自车绝对量、其他车相对量、世界轴和单位：
IDLE 为什么还会动，SLOWER 为什么不是紧急制动：
环境有没有推进，当前策略有没有根据反馈改动作：
实际结束原因，这些统计属于什么评测：
若做排错：错误信息、定位函数、最小修正与恢复结果：
这次实验还不能证明什么：
```

H001 是否完成仍按 [旧任务快照](notes/2026-09-27-h001-task-history.md) 审核。运行证据、自己的解释、参数修改和故障定位分别记录；材料已经写好不表示你已经掌握。出现你的实际证据后才更新 [PROGRESS](../PROGRESS.md)，再决定是否进入下一项实践。
