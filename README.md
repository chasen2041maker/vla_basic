# vla_basic｜智能驾驶学习项目

**从 [连续教材](learning/BOOK.zh-CN.md) 开始，当前接续位置见 [PROGRESS](PROGRESS.md)。** 解释、相关代码和完整实验都在同一份文件里；已有 Python/AI 经验直接用，驾驶知识从具体问题补起。

| 你要做什么 | 打开哪里 |
| --- | --- |
| 看教材、跟着学习 | [learning/BOOK.zh-CN.md](learning/BOOK.zh-CN.md) |
| 看学到哪里、下次接哪里 | [PROGRESS.md](PROGRESS.md) |
| 运行或修改当前实验 | [experiments/highway_driving/demos](experiments/highway_driving/demos/README.md) |

HighwayEnv 是当前阶段的模拟器工具。后续数据、视觉、轨迹模型、VLA 与部署继续属于本项目；当前已交付四章入门教材，后续工程状态在书末说明。

**整个项目统一按“短段学习、及时实践”交付。** 一次具体问题要配齐短讲解、就地代码、运行入口、可观察结果、本人小改和对照证据；这适用于现有工程以及后续数据、几何、模型、视觉/时序、VLA 和部署。项目长期规则见 [AGENTS.md](AGENTS.md)，不是只约束一本 Markdown。

| 项目部分 | 在学习中负责什么 |
| --- | --- |
| learning/BOOK | 连续讲解与就地代码；读一小段即动手 |
| experiments/ | 真正运行、修改和验证；模拟器作为依赖 |
| outputs/ | 本机生成的回放、曲线、原始日志和报告，不纳入 Git |
| PROGRESS + learning/LEARNING_LOG | 一个当前任务；区分本人实践与助手检查 |
| docs/ | 按当前疑问查系统、术语、背景和岗位证据，不另排课程关卡 |
| archive/ | 保留旧实现与历史，按需取用，不改写当时结论 |

现有四章已配调速、跟车、变道和实验对照。后续从这些日志、数据契约与评测方式继续展开，具体衔接和待交付状态见[书末项目路线](learning/BOOK.zh-CN.md#project-continuity)。你的当前任务仍以 PROGRESS 为准。

<details>
<summary>项目维护与参考资料（需要时再看）</summary>

- `learning/LEARNING_LOG.md`、`learning/evidence/`：学习记录和实验依据。
- `docs/`：背景、岗位能力、系统原理和术语参考。
- `archive/`：旧课程、规划与历史记录，不是当前作业。
- `AGENTS.md`：助手教学与维护规则。
- [运行器技术说明](experiments/highway_driving/README.zh-CN.md)：安装、日志和旧基线配置。

本机沿用已有的 `D:\miniconda\envs\py310\python.exe`。完整检查命令为 `python scripts/check_repo.py --with-highway`；不带参数只检查旧 Lab 与编译。归档 Lab 仍参与检查，原有 `4 / 6 PASS` 教学基线保留。

</details>
