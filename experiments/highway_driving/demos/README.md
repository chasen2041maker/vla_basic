# Highway 阶段｜主项目中的学习实验

这些实验属于 vla_basic；HighwayEnv 提供模拟器。当前小节见 [CURRENT_TASK](../CURRENT_TASK.md)，唯一学习进度见 [PROGRESS](../../../PROGRESS.md)。原练习与模拟器源码保留在同级 HighwayEnv 作来源参考，今后学习修改以本目录为准。

| 实验 | 来源与当前用途 | 本人证据边界 |
| --- | --- | --- |
| [00_following.py](00_following.py) | 原 HighwayEnv/demo.py 的规则保留，补固定种子及动作前后时间打印；教材 2.1 先运行、2.6 亲手改阈值 | 已有用户运行与部分解释；新配置的助手检查不算本人新实验 |
| [01_lane_change.py](01_lane_change.py) | 原助手准备的单次右变道示例，观察目标与实际位置 | 本人运行和解释待反馈 |
| [02_action_space.py](02_action_space.py) | 查看动作空间以及编号 4、5 是否在范围内 | 用户自述已运行，未附具体输出 |
| [03_continuous_action.py](03_continuous_action.py) | 原用户连续动作练习，打印控制量和前后速度 | 代码已存在，本人单步输出待反馈 |
| [04_target_speed.py](04_target_speed.py) | 教材 1.5：道路画面与目标/实际速度曲线；本地目标已由本人改成 10，原版为 20 | 本人确认已修改、运行并看到变化；现象解释见 1.6，最新接续见主项目 PROGRESS |
| [05_compare_actions.py](05_compare_actions.py) | 教材 4.1：两组真实回放与速度曲线；4.4 把 MAX_STEPS 从 40 改为 5 比较结束原因 | 仅助手验证；未开始本人第 4 章学习 |

## 从 VS Code 运行

每次只选当前章节的一条命令。下面都使用本机已有解释器和完整路径，不需要先换目录或自行猜脚本名。

**第 1 章：调速画面与曲线**（本人已完成修改运行；现象解释见 1.6）

```powershell
& 'D:\miniconda\envs\py310\python.exe' 'C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\04_target_speed.py'
```

改动位置：顶部 `TARGET_SPEED`；本人当前值是 10，原版 20。空格暂停、R 重播、Esc/叉号退出；改源码后要保存并重新启动，R 不重读文件。

**第 2 章：跟车窗口**

```powershell
& 'D:\miniconda\envs\py310\python.exe' 'C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\00_following.py'
```

改动位置：当前生效的 `if nearest_distance < 40:`，不要改三引号中的旧方案。看动作前时间/距离和动作后时间/速度；在终端 Ctrl+C 可停止，脚本会说明当前局是否结束。

**第 3 章：一次变道**

```powershell
& 'D:\miniconda\envs\py310\python.exe' 'C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\01_lane_change.py'
```

改动位置：`if step == 2:`。窗口看车，终端看实际前后时间、目标车道与 y；仿真到 10 秒结束，也可 Ctrl+C。

**第 4 章：两组回放与速度对照**

```powershell
& 'D:\miniconda\envs\py310\python.exe' 'C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\05_compare_actions.py'
```

改动位置：顶部 `MAX_STEPS`。先生成报告再尝试用默认浏览器打开；若没有自动打开，使用终端打印的完整报告路径。05 没有原生车辆窗口，回放来自本次真实运行。

<details>
<summary>02/03 专项参考与维护者无窗口验证</summary>

动作空间查询和连续动作补充只在对应疑问出现时使用，不是额外入门关卡：

```powershell
& 'D:\miniconda\envs\py310\python.exe' 'C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\02_action_space.py'
```

```powershell
& 'D:\miniconda\envs\py310\python.exe' 'C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\03_continuous_action.py'
```

00 的 `main(render_mode=None, max_steps=3)`、01 的 `main(render_mode=None)`、04 的 `run_demo(headless=True)`、05 的 `run_comparison(open_browser=False)` 可无窗口验证。04 不传目标时使用文件顶部当前值；检查初始版 20 必须显式传 `target_speed=20`，避免把原版检查当成本人修改后的结果。完整项目检查使用 `scripts/check_repo.py --with-highway`，助手检查不记成本人练习。

</details>

本机无需重装环境；新机器按阶段说明安装兼容依赖。现有 requirements 是记录器固定包环境，与本机 editable 模拟器源码版本不同。

## 配置不能混用

- 00：默认归一化 Kinematics 状态、4 车道、1 Hz 决策、40 秒环境时限；七档目标速度，现在每局固定 SEED=0 以便比较第一局，重复同种子不是多场景验证。默认 300 步脚本预算可能在一局中途结束；程序会保留并说明结束时当前局号、实际仿真时间和完成状态。`x*200`、`y*16` 依赖这些默认观察范围；历史未固定种子的个人记录不改写。
- 01：4 车道、0 辆其他车、起始车道 1、seed=0、1 Hz、10 秒；第 3 次发右变道，其余保持目标。打印真实动作前后时间，以及推进后的目标车道和世界 y（米）。目标中心从 y=4 改到 y=8，实际位置需逐步靠近。
- 02：只创建环境并查询动作空间，不执行驾驶回合。
- 03：ContinuousAction、0 辆其他车、seed=0、1 Hz；输入 float32 的 `[0.5,-0.2]`，打印原始归一化输入、解码控制、真实前后时间和速度差。内部状态与控制量仅作诊断，不作为新感知输入。
- 04：3 车道、0 辆其他车、起始车道 1、seed=0；物理 15 Hz、外层 5 Hz、8 秒。第 2 秒直接设置内部目标（原版 20 m/s，本人当前 10 m/s），始终 IDLE；每 0.2 秒记录速度，目标更改时额外保留同时间样本。道路与曲线使用真实模拟器输出；直接设置目标只作控制诊断，不是交通决策。助手截图写入忽略的 outputs，不当作学习者证据。
- 05：复用记录器，零交通、seed=7、物理 15 Hz/外层 5 Hz、环境 8 秒、默认 40 步；IDLE 与 SLOWER 从同初态运行。报告保存真实 GIF、trace、summary 和速率曲线到 outputs 的独立时间目录；改变为 5 步后只观察 1 秒。目标速度档位是 [20,25,30]，不是 00 的七档，也不是 40/50 米跟车策略评测；GIF 各自循环不同步，按曲线和日志对齐时间。

01 和 04 按固定时机发指令，没有自主判断交通；控制器追踪目标不等于策略使用反馈。无碰撞的零交通短实验不代表安全驾驶。当前只运行 PROGRESS 指定的小节，不要求同时重跑所有实验。

## 文字与源码

阅读[连续教材](../../../learning/BOOK.zh-CN.md)，必要源码与完整实验已在对应章节就地展示。需要核对原始实现时，可选打开本机 [controller.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/vehicle/controller.py) 与 [action.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/envs/common/action.py)；这不是额外的阅读任务。

迁移来源与校验值见[清单](../../../archive/notes/2026-09-27-project-consolidation.json)，历史结果见主项目 [learning/evidence](../../../learning/evidence)。迁移与助手验证不算学习者的新运行或掌握。
