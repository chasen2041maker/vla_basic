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

## 验证记录（只记实际已知状态）

当前状态：REVIEW，等待本次提交的 GitHub Actions 验证后补充实际 run、平台与结果。

本维护环境未成功克隆仓库且未安装 HighwayEnv/Gymnasium，因此**未声称本地完整检查通过**。工程验证使用仓库已有 GitHub Actions；配置存在或触发成功不等于测试通过。以实际 workflow/job/log 为依据补充后续记录。

需执行的现有完整检查：

```bash
python -m pip install -r experiments/highway_driving/requirements.txt
python -m pip check
python scripts/check_repo.py --with-highway
python experiments/highway_driving/run_episode.py --max-steps 5 --output-dir outputs/ci-smoke
```

Linux/Windows 无窗口集成不覆盖原生桌面 human 窗口，也不覆盖学习者本机实践。资料和课程审阅属于维护证据，不是学习掌握证据。

## 当前学习接棒

learning_status 保持 LEARNING，片段 A。上一轮已给教学方式示范，但尚未收到学习者对 H001 的独立回答、预测或实验。下一次 GPT 核对：给仍在行驶的车发送 IDLE，为什么不改变目标速度不等于把速度变零？

当前状态只在 PROGRESS.md 维护；本文是历史记录，不是第二套进度表。
