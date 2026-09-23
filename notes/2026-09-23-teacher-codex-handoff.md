# 2026-09-23｜GPT 授课 / 学习者与 Codex 实现 / 双轨进度

## 来源与执行者

来源：用户在本次对话明确要求，区分 GPT 当老师该讲的内容与学习者、Codex 共同实现的内容，将进度规范写入 AGENTS.md，并按上一轮审核改造仓库。

基准 commit：06f7a2559aa3c561b2f70923f3c3539209240fe7。

执行者：GPT 的仓库维护角色。没有把此次维护、教材生成或工程测试归为学习者实践，没有为学习者代写 H001 答案。

## 变更边界

- AGENTS.md 成为角色、课堂分区、交接卡、双轨状态与字段写权限的唯一规范；Codex 不得自行提升学习状态。
- MENTORING_SYSTEM、LEARNING_METHOD、LEARNER_PROFILE 与入口统一；PROGRESS 保留能力基线，精确记录未收到的个人证据与下一问。
- H001 增加实际带读和分片教学；仍只有一个活跃任务，不生成 H002、policy.py 或训练内容。
- run_episode 只增加 step 前后的真实速率/目标速度诊断与首步摘要，保留恒定动作、环境配置、观察列、旧输出字段与旧 Lab 教学缺口。
- summary.schema_version 从 1 升至 2；first_transition 与第一条 trace 一致；不把目标速度加入策略输入。
- 新增 5 项教学摘要测试：2 项格式/缺字段测试、3 项真实模拟器或 CLI 集成测试；原有测试不删除。

## 已核验的工程证据

被测代码 commit：[4c78cfb326c6ab95810b97426e758d4c71fd6a27](https://github.com/chasen2041maker/vla_basic/commit/4c78cfb326c6ab95810b97426e758d4c71fd6a27)。在验证分支运行后才推进 main；最后文档收尾只补验证事实与修正接棒链接，不改变被测 Python 代码。

| 检查 | 实际结果 / 来源 |
|---|---|
| 原有 ci 工作流 | [run 35813857582](https://github.com/chasen2041maker/vla_basic/actions/runs/35813857582)，success |
| highway-driving | [run 35813857590](https://github.com/chasen2041maker/vla_basic/actions/runs/35813857590)，Linux 与 Windows jobs 均 completed/success |
| Ubuntu 完整检查 | [job 107031069258](https://github.com/chasen2041maker/vla_basic/actions/runs/35813857590/job/107031069258)，依赖安装、pip check、完整检查、实际回合与上传均通过 |
| Windows 完整检查 | [job 107031069415](https://github.com/chasen2041maker/vla_basic/actions/runs/35813857590/job/107031069415)，相同步骤均通过 |
| 测试数量 | 已读 Ubuntu 日志：Lab 000 为 4 项、Lab 001 为 7 项、HighwayEnv 为 15 项，共 26 项，全部 OK；其中含新增 5 项 |
| 原教学基线 | SYSTEM MAP RESULT 为 4/4；Lab 001 BASELINE RESULT 保持 4/6，两个故意保留的 failure gap 未被修掉 |

运行平台采用 Python 3.12；Ubuntu 日志确认为 CPython 3.12.14。直接依赖：HighwayEnv 1.12.1、Gymnasium 1.3.0、NumPy 2.2.6、pygame-ce 2.5.8、Pillow 11.3.0。完整解析依赖保存在上传的 pip-freeze.txt。

实际执行并通过的检查：

```bash
python -m pip install -r experiments/highway_driving/requirements.txt
python -m pip check
python scripts/check_repo.py --with-highway
python experiments/highway_driving/run_episode.py --max-steps 5 --output-dir outputs/ci-smoke
```

证据归属是 CI/维护者，不是学习者。无窗口 CI 使用 SDL dummy；不能说已验证原生桌面 human 窗口。

## 一条可用于老师示范的真实首步

来源：上述 Ubuntu job 的实际回合步骤，日志时间 2026-09-23T03:19:46Z（UTC）。参数为默认 seed=7、IDLE、12 辆其他车，运行器上限 5 步；以下只摘取首步显示值：

```text
仿真时间 (s)：0.000 → 0.200
自车世界位置 (m)：(204.710, 4.000) → (209.710, 4.000)
实际速率 (m/s)：25.000 → 25.000
目标速度 (m/s，模拟器诊断)：25.000 → 25.000
本步环境标志：terminated=False；truncated=False
整回合结束原因：runner_step_limit；共 5 步；总仿真时间=1.000s
```

这些是三位小数的终端显示值，精确数值见产物。它说明该回合首步目标保持且位置变化，不证明一般驾驶安全。这是 **12 车维护者示例**，不能混成第一课 0 车条件的学习者预测对照。

## 产物与可复现边界

两份产物均已由 Actions 返回为未过期：

- [Ubuntu artifact 10730583584](https://github.com/chasen2041maker/vla_basic/actions/runs/35813857590/artifacts/10730583584)，包含回放、首末图、trace、summary 与 pip-freeze。
- [Windows artifact 10730198597](https://github.com/chasen2041maker/vla_basic/actions/runs/35813857590/artifacts/10730198597)，同类产物。

保留期 14 天，当前到期日为 2026-10-07 UTC；链接不是永久证据存储。源码、命令与关键事实已留在仓库，过期后需要重新运行。

本维护环境未成功克隆仓库且未安装 HighwayEnv/Gymnasium，因此没有声称本地完整检查通过；实际验证来自已核对的 GitHub Actions。学习者本机运行、原生窗口和个人掌握都未验证。

## 当前学习接棒

learning_status 保持 LEARNING，片段 A。上一轮已给教学方式示范，但尚未收到学习者对 H001 的独立回答、预测或实验。下一次 GPT 核对：给仍在行驶的车发送 IDLE，为什么不改变目标速度不等于把速度变零？

当前状态只在 PROGRESS.md 维护；本文是带来源的历史记录，不是第二套进度表。
