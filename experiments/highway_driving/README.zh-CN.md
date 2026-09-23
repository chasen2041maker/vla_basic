# HighwayEnv 单回合运行器｜历史工具参考

**本目录自 2026-09-23 起不再是当前实践主线。** 实际学习、修改与实验移至 [highwayenv-learning](https://github.com/chasen2041maker/highwayenv-learning)，当前状态只看其 [PROGRESS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md)。

原程序、测试和依赖均保留原路径与内容。本次只调整文档定位，不修改行为、不删除旧成果、不宣称重新验证了运行器。

## 保留了什么

[run_episode.py](run_episode.py) 是固定动作的单回合记录工具，不是自动跟车策略。它保留种子、环境配置、逐步日志、目标与实际速度诊断、回放和结束原因等已有实现。依赖见 [requirements.txt](requirements.txt)，测试见 [tests/](tests/)。

完整原安装、参数、输出契约和检查说明可查 [改造前 README](https://github.com/chasen2041maker/vla_basic/blob/4503a9cc9d0b67add5e85c28aa5d75e73f2725a7/experiments/highway_driving/README.zh-CN.md)。这些说明对应旧工具自己的环境，不是让学习者为当前实践重新安装。

原 H001 任务和讲义分别通过 [历史任务入口](CURRENT_TASK.md) 与 [历史讲义入口](walkthrough/H001-idle-step.md) 保留。新的原理解释见 [理论讲义目录](../../theory/README.md)。

## 按需借鉴，不维护两套

以后需要更完整的日志、回放或评测记录时，可以在理解契约后将必要部分用于实践项目，不把整套旧 runner 原样复制，也不要求两仓库配置始终相同。

特别注意旧工具使用 5 Hz 决策、非归一化观察和默认 8 秒时限；当前实践 demo 的基准配置不同。对照见 [理论—实践对应表](../../PRACTICE_MAP.md)。

历史 CI 和测试只证明当时版本的指定范围。本次文档重组不是一次新仿真、桌面运行或学习者验收。旧 Lab 教学基线与许可证保持不变。
