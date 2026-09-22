# vla_basic｜驾驶实验与 VLA 学习主线

**围绕同一个驾驶项目持续改进：先看到车运行，再解释状态、动作、时间和失败，遇到基础问题再回查 Lab。**

长期目标仍是自动驾驶 VLA / 端到端驾驶研发；当前项目是 **基于 HighwayEnv 的驾驶决策与失败分析实验**。不另开仓库，不删除旧实验，也不把模拟器提供的状态冒充自己实现的视觉感知。

## 现在从哪里开始

当前唯一任务：**H001：运行并解释一个驾驶回合**。

- [项目中文说明](experiments/highway_driving/README.zh-CN.md)
- [当前任务](experiments/highway_driving/CURRENT_TASK.md)
- [学习进度与接棒](PROGRESS.md)

本轮先回答：**我给出 IDLE 后，为什么车还在动？一次 step 究竟过去多少时间？**

## 直接运行

在仓库根目录使用 Python 3.12，独立虚拟环境，不需要 GPU 或模型权重。

Windows PowerShell（无需激活环境）：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r experiments/highway_driving/requirements.txt
.\.venv\Scripts\python.exe experiments/highway_driving/run_episode.py --seed 7 --action IDLE
```

Linux / macOS：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r experiments/highway_driving/requirements.txt
.venv/bin/python experiments/highway_driving/run_episode.py --seed 7 --action IDLE
```

默认不弹窗，在 `outputs/highway_driving/<本次时间>/` 保存 `episode.gif`、首末 PNG、`trace.jsonl` 和 `summary.json`。要看窗口，在相同命令后追加 `--render human`；窗口模式只保存日志。没有桌面的机器使用默认模式。需要只执行一次动作时追加 `--max-steps 1`。

默认固定种子、三车道、12 辆其他车、5 行车辆观察、15 Hz 仿真与 5 Hz 决策。IDLE 是保持目标车道/目标速度的高层动作，不是停车。第一版是恒定动作基线，不会自动跟车或避碰。

## 检查

以下 `python` 指所建虚拟环境的解释器：

```bash
# 旧 Lab 基线和源码编译；明确不代表 HighwayEnv 集成通过
python scripts/check_repo.py

# 旧 Lab + 真实 HighwayEnv 集成测试
python scripts/check_repo.py --with-highway
```

原有 CI 保留；新增 `highway-driving` 工作流在 Linux / Windows、Python 3.12 下安装依赖、执行完整检查并上传真实回合证据。**配置 CI 不等于 CI 已通过**，实际验证记录见 [本次工程记录](notes/2026-09-22-highway-entry.md) 与 [Actions](https://github.com/chasen2041maker/vla_basic/actions)。

Lab 001 的 `BASELINE RESULT: 4 / 6 PASS` 是故意保留的教学基线，不是两个单元测试意外失败。

## 项目结构

```text
experiments/highway_driving/
├── README.zh-CN.md       # 问题、运行、契约和边界
├── CURRENT_TASK.md       # 只保留一个活跃任务
├── requirements.txt     # 固定直接依赖
├── run_episode.py       # 环境交互、记录和画面
└── tests/               # 纯逻辑 + 真实环境测试
labs/                    # 原有 Lab 000/001 完整保留，按需回查
notes/                   # 可验证结论，不保存整段聊天
scripts/check_repo.py    # 显式选择轻量/完整检查
```

现在不创建策略工厂、插件系统或模型注册中心。需要跟车策略时再增加 `policy.py`；需要批量比较时再增加评测脚本。

## 学习方法与接棒

**驾驶问题 → 运行当前版本 → 看相关代码 → 预测一个改动 → 小步修改 → 实验核对 → 记录结论。**

新会话先读 `AGENTS.md`、`LEARNER_PROFILE.md`、`PROGRESS.md`，再读当前任务与代码。`SYSTEM_MENTAL_MODEL.md` 是系统地图，`SKILL_GAP_MATRIX.md` 是能力缺口，旧 Lab 是专项材料；它们不再构成运行 HighwayEnv 的先修通关门槛。

[近期路线](ROADMAP.md) 保留通向视觉、几何、轨迹模型、开放环/闭环、VLA、蒸馏量化与强化学习的长期目标。`ROLE_TARGET.md`、`MASTER_GROWTH_PLAN.md` 等旧长期规划继续作为能力参考，活跃任务以 `PROGRESS.md` 为准。

## 上游官方入口

- [HighwayEnv 源码](https://github.com/Farama-Foundation/HighwayEnv)
- [官方文档](https://highway-env.farama.org/)
- [官方入门](https://highway-env.farama.org/quickstart/)

上游作为固定版本的外部依赖，不复制整个上游仓库。旧机器人操作材料仍在 `archive/robot-manipulation-vla-2026-07` 分支，不混回驾驶主线。
