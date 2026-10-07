# vla_basic｜智能驾驶学习项目

从零进入智能驾驶的个人学习项目：先在驾驶模拟器 HighwayEnv 里搞懂“决策 → 控制 → 运动 → 评测”这半条链（感知由模拟器代办），再做规则规划与评测项目，最后换到真实轨迹数据。

## 从哪里开始

| 我想…… | 打开 |
| --- | --- |
| 知道现在学到哪、下一步做什么 | [PROGRESS.md](PROGRESS.md) |
| 看整体路线、当前阶段清单、HighwayEnv 在路线里的位置 | [CURRENT_TASK.md](experiments/highway_driving/CURRENT_TASK.md) |
| 读教材（四章 + 源码地图） | [learning/BOOK.zh-CN.md](learning/BOOK.zh-CN.md) |
| 运行或修改实验 | [experiments/highway_driving/demos/](experiments/highway_driving/demos/README.md) |

## 运行实验

在 VS Code 的 PowerShell 终端：

```powershell
conda activate py310
cd C:\company\own\vla_basic
python experiments\highway_driving\demos\04_target_speed.py
```

`py310` 环境里装的是本机 HighwayEnv 源码（`C:\company\own\highwayenv-learning`，可编辑安装），改那边的源码会直接生效。注意用 `python`，不要用 `py`——`py` 会启动另一个没装依赖的 Python。

## 路线

| 阶段 | 内容 | 状态 |
| --- | --- | --- |
| 1 | 收尾 HighwayEnv：读一次 `env.step` 闭环的关键源码 | 进行中 |
| 2 | 自己写跟车 + 变道规则，多种子批量评测，和 DQN 对比 | 未开始 |
| 3 | 换到 nuPlan / Waymo 等真实轨迹数据，做预测或规划 | 未开始 |

更远的方向（视觉、端到端模型、VLA、部署）也在这个项目里继续，见[教材末尾](learning/BOOK.zh-CN.md#project-continuity)。

## 目录

```text
PROGRESS.md                 当前位置和下一步（唯一进度）
learning/
  BOOK.zh-CN.md             教材
  LEARNING_LOG.md           每次学习一到三行的流水记录
  evidence/                 早期实验的原始输出
experiments/highway_driving/
  CURRENT_TASK.md           当前阶段清单
  demos/                    00–05 六个小实验
  run_episode.py            单回合记录器（第 4 章用）
  tests/                    实验和记录器的测试
docs/                       参考资料：系统全景、术语、岗位方向、学习者背景
archive/                    旧课程、旧规划和历史记录，只供追溯
AGENTS.md                   给 AI 助手的教学和维护规则
```

`outputs/`（实验生成的图片、日志、报告）不进 Git。

<details>
<summary>维护：检查命令与 CI</summary>

```powershell
python scripts\check_repo.py                  # 旧 Lab 测试与编译检查，不需要模拟器
python scripts\check_repo.py --with-highway   # 再加上真实 HighwayEnv 测试和 01/02/03 示例
```

GitHub Actions 用 `experiments/highway_driving/requirements.txt` 里固定的 highway-env 1.12.1 在 Ubuntu 和 Windows 上跑同样的检查。本机用的是 HighwayEnv 源码的开发版，两边版本不同，个别数值可能有细微差异。

归档里的旧 Lab 仍参与检查，其中 001 的基线结果是 `4 / 6 PASS`，这是当时的教学设计，不需要改成全过。

</details>
