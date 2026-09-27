# vla_basic｜智能驾驶学习项目

**从 [连续教材](learning/BOOK.zh-CN.md) 开始，当前读第 01 章。** 解释、相关代码和完整实验都在同一份文件里；已有 Python/AI 经验直接用，驾驶知识从具体问题补起。

| 你要做什么 | 打开哪里 |
| --- | --- |
| 看教材、跟着学习 | [learning/BOOK.zh-CN.md](learning/BOOK.zh-CN.md) |
| 看学到哪里、下次接哪里 | [PROGRESS.md](PROGRESS.md) |
| 运行或修改当前实验 | [experiments/highway_driving/demos](experiments/highway_driving/demos/README.md) |

HighwayEnv 是当前阶段的模拟器工具。后续数据、视觉、轨迹模型、VLA 与部署继续属于本项目；当前已交付四章入门教材，后续工程状态在书末说明。

<details>
<summary>项目维护与参考资料（需要时再看）</summary>

- `learning/LEARNING_LOG.md`、`learning/evidence/`：学习记录和实验依据。
- `docs/`：背景、岗位能力、系统原理和术语参考。
- `archive/`：旧课程、规划与历史记录，不是当前作业。
- `AGENTS.md`：助手教学与维护规则。
- [运行器技术说明](experiments/highway_driving/README.zh-CN.md)：安装、日志和旧基线配置。

本机沿用已有的 `D:\miniconda\envs\py310\python.exe`。完整检查命令为 `python scripts/check_repo.py --with-highway`；不带参数只检查旧 Lab 与编译。归档 Lab 仍参与检查，原有 `4 / 6 PASS` 教学基线保留。

</details>
