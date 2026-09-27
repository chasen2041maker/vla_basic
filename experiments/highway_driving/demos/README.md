# Highway 阶段｜主项目中的学习实验

这四个实验属于 vla_basic；HighwayEnv 提供模拟器。当前小节见 [CURRENT_TASK](../CURRENT_TASK.md)，唯一学习进度见 [PROGRESS](../../../PROGRESS.md)。原练习与模拟器源码保留在同级 HighwayEnv 作来源参考，今后学习修改以本目录为准。

| 实验 | 来源与当前用途 | 本人证据边界 |
| --- | --- | --- |
| [00_following.py](00_following.py) | 原 HighwayEnv/demo.py，按前车距离选择加速、保持和减速 | 已有用户运行与部分解释，不等于独立策略设计验收 |
| [01_lane_change.py](01_lane_change.py) | 原助手准备的单次右变道示例，观察目标与实际位置 | 本人运行和解释待反馈 |
| [02_action_space.py](02_action_space.py) | 查看动作空间以及编号 4、5 是否在范围内 | 用户自述已运行，未附具体输出 |
| [03_continuous_action.py](03_continuous_action.py) | 原用户连续动作练习，打印控制量和前后速度 | 代码已存在，本人单步输出待反馈 |

## 从 VS Code 运行

在 vla_basic 根目录使用现有解释器，按当前任务选一个脚本：

```powershell
& 'D:\miniconda\envs\py310\python.exe' .\experiments\highway_driving\demos\02_action_space.py
```

把末尾文件名换成 00、01 或 03 即可运行对应练习；00 和 01 默认打开模拟窗口。01 的 `main(render_mode=None)` 可用于助手无窗口检查。不要为了搬目录重装整个环境；新机器需按阶段说明安装兼容依赖。现有 `requirements.txt` 是旧记录器的固定包环境，与本机 editable 源码版本不同。

## 配置不能混用

- 00：默认归一化 Kinematics 状态、4 车道、1 Hz 决策、40 秒环境时限；七档目标速度，未固定种子，300 步脚本预算可能在一局中途结束。`x*200`、`y*16` 依赖这些默认观察范围。
- 01：4 车道、0 辆其他车、起始车道 1、seed=0、1 Hz、10 秒；第 3 次发右变道，其余保持目标。输出是每次动作推进后的目标车道和世界 y（米）。目标中心从 y=4 改到 y=8，实际位置需逐步靠近。
- 02：只创建环境并查询动作空间，不执行驾驶回合。
- 03：ContinuousAction、0 辆其他车、seed=0、1 Hz；输入 float32 的 `[0.5,-0.2]`，执行一步后打印速度差。内部状态与控制量仅作诊断，不作为新感知输入。

01 按固定时机发指令，没有自主判断交通；控制器追踪目标不等于策略使用反馈。无碰撞的零交通短实验不代表安全驾驶。当前只是已有实验入口，未要求同时重跑四个实验。

## 文字与源码

阅读[连续教材](../../../learning/BOOK.zh-CN.md)，必要源码与完整实验已在对应章节就地展示。需要核对原始实现时，可选打开本机 [controller.py](../../../../HighwayEnv/highway_env/vehicle/controller.py) 与 [action.py](../../../../HighwayEnv/highway_env/envs/common/action.py)；这不是额外的阅读任务。

迁移来源与校验值见[清单](../../../archive/notes/2026-09-27-project-consolidation.json)，历史结果见主项目 [learning/evidence](../../../learning/evidence)。迁移与助手验证不算学习者的新运行或掌握。
