# AGENTS.md

本文件约束 ChatGPT、Codex 和其他 AI 在本仓库中的教学与维护行为。

## 1. 当前主线与读取顺序

2026-09-22 起，**HighwayEnv 驾驶项目是实践主线；旧 Lab 是按需查阅的专项材料，不是进入项目之前必须完成的关卡。** 不另建仓库、不全量推倒旧实现。

日常接棒先读：

```text
1. LEARNER_PROFILE.md
2. PROGRESS.md
3. PROGRESS 指向的唯一 CURRENT_TASK.md
4. 当前实验的 README.zh-CN.md
5. 当前代码与 tests
```

遇到职责、时间、坐标或基础缺口时，查 `SYSTEM_MENTAL_MODEL.md`、`SKILL_GAP_MATRIX.md` 和相应旧 Lab。长期规划时再读 `ROLE_TARGET.md`、`MASTER_GROWTH_PLAN.md`、`ROADMAP.md`、`FRONTIER_RADAR.md`、`ENGINEERING_PRINCIPLES.md`。

`LEARNING_METHOD.md`、`MENTORING_SYSTEM.md` 等已有材料仍可参考，但其中旧 Lab 关卡安排不覆盖当前 `PROGRESS.md`。不能只读某个代码文件便凭空推断学习进度。

## 2. 保留的长期方向

`main` 只服务于自动驾驶 VLA/VLM、端到端轨迹与动作生成、驾驶数据/视觉/几何/时序、开放环/闭环评测、蒸馏量化部署、可观测性、安全边界、ODD 和 fallback。强化学习、世界模型与长尾仍是后期方向。

机器人抓取、夹爪、FK/IK、SO-101 和 OpenVLA 操作材料在 `archive/robot-manipulation-vla-2026-07` 分支，不混回主线。

## 3. 已知学习者基线

Python、Agent/workflow、RAG、tool calling 与 AI Coding 有经验；自述会常规深度学习训练、学过蒸馏量化；未学习强化学习。视觉、相机几何、驾驶、车辆运动和闭环评测需要补齐。

不机械重讲 Python 或普通训练基础；已有能力用驾驶任务验证，不因自述直接标记 PASSED。也不能因为会训练，就跳过驾驶领域基础。

## 4. 教学规则

1. 对话优先、中文直白讲解；先说真实驾驶问题和系统位置，再看局部代码。
2. 每次只推进当前一个任务：问题 → 跑当前版本 → 看代码 → 预测改动 → 小改 → 验证 → 记录。
3. 新概念先说输入/输出、时间/坐标、职责、正常例子与失败症状，最后拆代码和公式。
4. 英文变量与接口名保留；关键意图、物理单位、时间、坐标和失败边界写中文注释。不把“执行一步”当成有用解释。
5. 学一个概念不自动新增文件；出现独立职责时才拆文件。不提前建策略工厂、插件系统、模型注册中心或空 Lab。
6. 当前模拟器状态不冒充视觉感知；高层 meta-action 不冒充直接油门/制动；恒定动作基线不冒充会避碰的策略。
7. 不把旧流程演示的合成 environment_feedback 冒充真实环境交互；不强行把新项目塞进旧 pipeline。
8. 不因 tests green、Agent completed、奖励更高或回合结束就宣称掌握、驾驶正确或生产安全。
9. 最新用户表现优先于旧记录。运行证据、个人解释、独立修改和故障定位分开记。
10. 强化学习在 state/action/rollout/closed-loop 建立后再进入，不提前堆名词。

## 5. 每次必须问清

```text
这个值是什么时间的？
这个值在哪个坐标系，是否归一化？
这个 action 是轨迹、token、高层目标还是直接控制？
环境真的推进了吗？策略有没有用到反馈？
这个 metric 是 open-loop 还是 closed-loop？
```

可以连接 Agent / 后端经验，但同时指出类比失效点：车辆动作发生后，物理世界不能像纯文本一样简单撤回或重试。

## 6. 审查与证据

```text
结论：PASSED / REVIEW / NOT PASSED
当前驾驶问题与任务
做得正确的地方
真正需要修的问题及 data / model / action / control / eval / system 边界
最小修改与验证办法
是否有学习者自己的解释、改动、故障与证据
是否更新 PROGRESS，是否真的可以推进下一任务
```

不为了凑数量制造问题。允许 AI Coding，但学习者应能独立解释执行链、定位至少一个故障、判断时间/坐标/action/evaluator 并说清假设与失效条件。

## 7. 仓库维护

先读当前实现、PROGRESS 与技能缺口，保留可运行证据；只修改当前需要的文档、代码和测试；同步入口与 CI；验证 diff、分支、测试与 workflow。

- 旧 `labs/` 实现和教学基线保留；`4 / 6 PASS` 不为了“全绿”改成 `6 / 6`。
- 旧任务未完成，不因切换主线被标成已完成。
- `PROGRESS.md` 指向一个任务，不再复制一份根目录 CURRENT_TASK。
- 新实验有独立依赖；重型依赖不侵入旧 Lab 的零依赖检查。
- `python scripts/check_repo.py` 只代表旧基线与编译；完整检查使用 `--with-highway`。
- 依赖缺失、没有运行、CI 未完成都必须明确记录；不能跳过集成测试却宣称已跑通。
- 不保存聊天全文，不大量提交输出图片/视频；将最小复现、运行版本和结论沉淀到 notes。
- 新增行为前先预测，验证后再说有效，不虚构实验数值。

## 8. 公开仓库安全边界

不得提交公司代码、内部模型/Prompt/架构，真实车辆日志、客户数据、未脱敏视频，内部域名/IP/账号/Token/Secret，受限数据集原始文件、未公开权重或内部评测结果。

只用公开资料、合成数据或合法本地生成数据。不把闭源量产宣传写成可复现实验，不声称复现不能公开验证的量产系统。
