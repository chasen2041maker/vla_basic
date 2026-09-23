# 理论—实践对应表

**vla_basic 讲原因，highwayenv-learning 做实验；当前状态只写一处。** 本表是稳定的材料对应，不是当前任务列表，也不记录个人完成状态。

## 固定入口

| 内容 | 唯一位置 |
| --- | --- |
| 当前问题、实践状态、理解证据、下一步 | [实践 PROGRESS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md) |
| 理论正文 | [本仓库 theory/](theory/README.md) |
| 实际练习程序 | [实践 demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py) |
| 实验历史与依据 | [实践 LEARNING_LOG.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/learning/LEARNING_LOG.md) |
| 实践侧反向导航 | [实践 THEORY_LINKS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/learning/THEORY_LINKS.md) |

## 现有理论怎样接到代码

| 真实问题 | 理论解释 | 实际代码/源码入口 | 对照什么 |
| --- | --- | --- | --- |
| 最低速度档位、目标与实际不同 | [01 目标速度与控制](theory/01-target-speed-and-control.md) | [demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py)、[controller.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/vehicle/controller.py) | 已有档位配置和两种速度打印；不是另写一个实验 |
| 每步重新观察、一步多久 | [02 step 与反馈](theory/02-step-and-feedback.md) | [demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py)、[abstract.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/envs/common/abstract.py) | 动作前后的观察、仿真时间和结束标记 |
| 距离换算、同车道判断、速度差 | [03 观察与相对运动](theory/03-observation-and-relative-motion.md) | [demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py)、[observation.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/envs/common/observation.py) | presence、相对量、归一化、车辆数量限制 |

这些映射不授权同时开展三个新实验。下一步由实践进度决定；新实践暴露新问题后再增补对应理论。

## 复用旧工具之前先核对配置

以下是改造前两份代码的对照，不是要求同步配置。源码依据：[实践基准 caeee82](https://github.com/chasen2041maker/highwayenv-learning/tree/caeee8225d88f8092fbcf39a5ff02c59d35904ca) 和 [旧运行器基准 4503a9c](https://github.com/chasen2041maker/vla_basic/blob/4503a9cc9d0b67add5e85c28aa5d75e73f2725a7/experiments/highway_driving/run_episode.py)。

| 项目 | highwayenv-learning 当时的 demo | vla_basic 保留的旧运行器 |
| --- | --- | --- |
| 动作选择 | 按观察到的最近同车道前车距离选动作 | 重复指定的恒定动作 |
| 观察归一化 | 默认开启，示例用 x×200、y×16 换算 | 显式关闭，位置值已是米 |
| 决策频率 | 默认 1 Hz | 5 Hz |
| 目标速度档位（m/s） | 0、5、10、15、20、25、30 | 20、25、30 |
| 默认回合时限 | 40 秒 | 8 秒 |
| 本机/依赖记录 | 实践进度记录 Python 3.10 与源码开发版 | 旧 requirements 按 Python 3.12 配置 highway-env 1.12.1 |

因此不要把 x×200 原样搬到非归一化观察，不把两个环境的累计奖励直接比较，不因读理论重建用户已经能用的环境。旧运行器的日志思路可以借鉴，但不维护两份始终同步的实现。

## 保存与互链规则

讲义引用实际实验文件，实践文档指回讲义；导航可用 main，源码论证与历史数据用固定 commit。代码改动改变了语义时更新对应讲义的版本说明，不让旧例子悄悄冒充当前实现。

实验结果与个人理解只更新实践进度及日志。这里最多引用证据，不复制一份成绩单、当前任务和完成勾选。旧 H001 不重做，也不自动全标通过。
