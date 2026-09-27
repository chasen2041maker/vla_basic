# 理论—实践对应表

**vla_basic 讲原因，highwayenv-learning 做实验；当前状态只写一处。** 本表是稳定材料对应，不是当前任务列表，不记录个人完成状态。2026-09-27 增加评测、视觉衔接和工程补充，保留原有分工。

## 固定入口

| 内容 | 唯一位置 |
| --- | --- |
| 当前问题、实践状态、理解证据、下一步 | [实践 PROGRESS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md) |
| 理论正文 | [本仓库 theory/](theory/README.md) |
| 实际练习程序 | [实践 demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py) |
| 实验历史与依据 | [实践 LEARNING_LOG.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/learning/LEARNING_LOG.md) |
| 实践侧反向导航 | [实践 THEORY_LINKS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/learning/THEORY_LINKS.md) |

## 现有理论怎样接到代码

| 真实问题 | 理论解释 | 实際代码/源码入口 | 对照什么 |
| --- | --- | --- | --- |
| 目标速度与实际不同 | [01 目标速度与控制](theory/01-target-speed-and-control.md) | [demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py)、[controller.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/vehicle/controller.py) | 档位配置、两种速度与动作执行 |
| 每步重新观察、一步多久 | [02 step 与反馈](theory/02-step-and-feedback.md) | [demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py)、[abstract.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/envs/common/abstract.py) | 动作前后、仿真时间、结束标记 |
| 距离换算、同车道判断、速度差 | [03 观察与相对运动](theory/03-observation-and-relative-motion.md) | [demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py)、[observation.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/envs/common/observation.py) | presence、相对量、归一化、可见对象限制 |
| 策略修改是否真的有效 | [04 评测与证据](theory/04-evaluation-and-evidence.md) | 当前 demo 的回合输出；本仓库旧 [test_episode.py](experiments/highway_driving/tests/test_episode.py) 仅作测试思路参考 | 配对场景、指标与结束分类；成套批量评测工程未由本次实现 |
| 状态表怎样走向视觉模型 | [05 状态到相机](theory/05-state-to-camera-bridge.md) | 当前 observation.py 帮助明确起点；真实数据适配器尚未建立 | 输入/标签隔离、坐标/时间、真实图像；正文合成数学例子不能替代真实数据验证 |
| 数学与 C++ 怎样形成实证 | [06 工程检查](theory/06-engineering-and-math-checkpoints.md) | 正文局部代码复制到临时文件验证，不是仓库新增驾驶入口 | 跨语言手算正例、坏输入、编译与退出码；大型工程/部署尚未覆盖 |

VS Code 使用 Ctrl+P 输入表中的仓库相对路径或函数所在文件。两个仓库分别打开各自根目录；不能把理论库的路径拼到实践库。临时数学代码只在需要时验证，不成为第二个实验工程或进度源。

这些映射不授权同时开展多个新实验。下一步由实践进度决定；新增理论不自动算已授课。

## 复用旧工具之前先核对配置

以下是改造前代码对照，不是要求同步配置。源码依据：[实践基准 caeee82](https://github.com/chasen2041maker/highwayenv-learning/tree/caeee8225d88f8092fbcf39a5ff02c59d35904ca) 和 [旧运行器基准 4503a9c](https://github.com/chasen2041maker/vla_basic/blob/4503a9cc9d0b67add5e85c28aa5d75e73f2725a7/experiments/highway_driving/run_episode.py)。

| 项目 | highwayenv-learning 当时的 demo | vla_basic 保留的旧运行器 |
| --- | --- | --- |
| 动作选择 | 依据观察到的最近同车道前车距离 | 重复指定的恒定动作 |
| 观察归一化 | 默认开启，当时示例 x×200、y×16 | 显式关闭，位置已经是米 |
| 决策频率 | 默认 1 Hz | 5 Hz |
| 目标速度档位（m/s） | 0、5、10、15、20、25、30 | 20、25、30 |
| 回合时限 | 40 秒 | 8 秒 |
| 依赖背景 | 当时记录 Python 3.10 与源码开发版 | 旧 requirements 按 Python 3.12 配置 highway-env 1.12.1 |

不能把 x×200 搬到非归一化观察，不把不同频率/时限的累计 reward 直接比较，不因读理论重建已经可用的环境。旧日志思路可借鉴，不维护两份同步实现。

## 保存与版本

导航可用 main；论证源码与历史实验应绑定 commit。输入、动作或频率改变后复核讲义，不让旧例子冒充当前事实。正式选用新数据/模型/模拟器时，先明确实践工程、版本与资源，再增补本表；不预建虚假的路径。

个人实验和理解只更新实践进度及日志。这里可以引用证据，不复制成绩单或另一份当前任务。旧 H001 不因本次审查重做，也不自动标成通过。
