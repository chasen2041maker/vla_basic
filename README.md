# vla_basic｜驾驶项目、GPT 授课与你和 Codex 的实现练习

**围绕同一个驾驶项目持续改进：GPT 先讲并带读，你与 Codex 完成有限实践，再分别记录工程结果和个人理解。**

长期目标是自动驾驶 VLA / 端到端驾驶研发。当前项目是 **基于 HighwayEnv 的驾驶决策与失败分析实验**，还不是视觉感知、跟车策略或 VLA。不另开仓库，不删除旧 Lab，不全量推倒。

## 现在从哪里开始

唯一活跃任务是 **H001：运行并解释一个驾驶回合**。当前真正讲到哪里、下一问是什么，只看 [PROGRESS.md](PROGRESS.md)。

| 入口 | 用途 |
|---|---|
| [AGENTS.md](AGENTS.md) | GPT、你、Codex 的分工；双轨进度、写权限与交接格式的唯一规范 |
| [当前任务](experiments/highway_driving/CURRENT_TASK.md) | 老师教什么，你与 Codex 做什么，如何验收和在哪里停止 |
| [H001 带读讲义](experiments/highway_driving/walkthrough/H001-idle-step.md) | 具体代码与日志的分析过程；备课材料不等于课程已经完成 |
| [项目中文说明](experiments/highway_driving/README.zh-CN.md) | 安装、参数、观察/动作/时间契约和边界 |

说“继续上课”时，GPT 从精确接棒点讲一个片段，核对一个理解问题，不把整份任务清单一次发出。你与 Codex 只执行已经激活的动手范围；Codex 完成报告不能自行升级个人学习状态。

## 直接运行

在仓库根目录使用 Python 3.12 和独立虚拟环境，不需要 GPU 或模型权重。

Windows PowerShell（无需激活环境）：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r experiments/highway_driving/requirements.txt
.\.venv\Scripts\python.exe experiments/highway_driving/run_episode.py --seed 7 --vehicles 0 --max-steps 1 --action IDLE
```

Linux / macOS：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r experiments/highway_driving/requirements.txt
.venv/bin/python experiments/highway_driving/run_episode.py --seed 7 --vehicles 0 --max-steps 1 --action IDLE
```

这里显式用 **0 辆其他车、1 步**隔离动作和自车运动，服务于第一课。脚本默认仍为 12 辆其他车，三车道，5 行车辆观察，15 Hz 仿真与 5 Hz 决策；本次没有改变环境或恒定动作基线。

终端新增首步教学摘要：动作前后时间、位置、实际速率与目标速度分开显示；目标速度明确标为模拟器诊断，不是策略输入。完整回合的停止原因单独标出，不能和首步状态混用。

默认不弹窗，在 `outputs/highway_driving/<本次时间>/` 保存 GIF、首末 PNG、`trace.jsonl` 与 `summary.json`。`--render human` 打开窗口并只保存日志；`--render none` 只保存日志。原生桌面窗口仍需在本机验证。

IDLE 保持目标，不表示停车。SLOWER 降低目标速度档位，不等于紧急制动。当前脚本不根据观察选择动作，不会自动跟车或避碰。

## 检查

以下 `python` 指虚拟环境解释器：

```bash
# 旧 Lab 基线和源码编译；不代表 HighwayEnv 集成已通过
python scripts/check_repo.py

# 旧 Lab + 真实 HighwayEnv + 教学摘要/命令行验证
python scripts/check_repo.py --with-highway
```

原有 CI 保留；`highway-driving` 在 Linux / Windows、Python 3.12 下安装依赖、运行完整检查并上传回合证据。配置 CI 不等于通过，工程验证范围和未验证项见 [本次维护记录](notes/2026-09-23-teacher-codex-handoff.md)。原始入口的历史记录见 [2026-09-22 工程记录](notes/2026-09-22-highway-entry.md)。

Lab 001 的 `BASELINE RESULT: 4 / 6 PASS` 是故意保留的教学基线，不是两个单元测试意外失败，不为全绿修改它。

## 项目结构

```text
experiments/highway_driving/
├── README.zh-CN.md
├── CURRENT_TASK.md          # 唯一活跃任务的内容与动手边界；状态不在这里复制
├── walkthrough/
│   └── H001-idle-step.md     # GPT 备课与学习者回查
├── requirements.txt
├── run_episode.py           # 环境交互、诊断记录、回放与教学摘要
└── tests/                   # 原有契约 + 教学摘要的真实验证
PROGRESS.md                  # 唯一当前状态与精确接棒
AGENTS.md                    # 角色和进度写入规范
labs/                        # 旧 Lab 000/001 按需回查
notes/                       # 高价值知识与带来源的历史证据
```

现在不创建策略工厂、插件系统、模型注册中心，也不提前生成 `policy.py`。H001 内部课堂片段不等于新增四个活跃任务。

## 长期路线与边界

[ROADMAP.md](ROADMAP.md) 保留通向视觉、几何、轨迹、开放环/闭环、VLA、蒸馏量化和 RL 的目标。系统地图、能力矩阵和旧长期规划继续作为参考，不再构成运行项目的先修门槛。机器人操作材料留在 `archive/robot-manipulation-vla-2026-07` 分支。

代码完成、CI 通过、GPT 已讲、学习者理解、学习者独立实践是不同事实。任何角色都不能相互代填。

## 官方入口

- [HighwayEnv 源码](https://github.com/Farama-Foundation/HighwayEnv)
- [官方文档](https://highway-env.farama.org/)
- [官方入门](https://highway-env.farama.org/quickstart/)

上游作为固定版本的外部依赖，不复制整个上游仓库。只使用公开合法资料、合成或合法本地数据，不提交公司信息、敏感日志、凭证或受限文件。
