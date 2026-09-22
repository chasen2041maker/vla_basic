# 2026-09-22｜HighwayEnv 项目入口调整

## 决策与证据边界

以 `vla_basic` 承载持续改进的驾驶实验；保留旧 Lab 和长期 VLA 路线，不复制上游仓库，不另建项目，不提前引入训练框架。当前只做 H001：观察、明确动作、真实环境一步/单回合、可视化、记录和结束原因。

基础提交：`6b8a260183db5c168645e5b3ba1f58d7cead3669`。

工程实现已加入中文入口、单回合脚本、参数检查、单位/坐标/时间契约、固定直接依赖、真实集成测试、Linux/Windows CI、日志/PNG/GIF 与版本摘要。

学习者尚未提交自己的运行结果、字段解释、动作预测或失败定位，不因此标记 PASSED。旧 Lab 000/001 的个人验收保持未完成。

## 已执行的验证

本地执行环境 Python 3.13.5：源码编译通过，3 个纯逻辑测试通过。Git 克隆与 pip 安装因 DNS 解析失败，没有在此本地环境运行 HighwayEnv，也没有声称在学习者电脑运行过。

通过 GitHub 接口在重构分支执行真实 CI：

| 代码版本 | 检查 | 结果与边界 |
|---|---|---|
| `af1752c` | [Highway CI](https://github.com/chasen2041maker/vla_basic/actions/runs/35694565190)、[旧 CI](https://github.com/chasen2041maker/vla_basic/actions/runs/35694565219) | Linux/Windows 安装、pip check、旧 Lab、10 个新测试与输出通过；后续发现重复依赖与画面检查缺口 |
| `feb3b6f` | [Highway CI](https://github.com/chasen2041maker/vla_basic/actions/runs/35695041543)、[旧 CI](https://github.com/chasen2041maker/vla_basic/actions/runs/35695041509) | 去掉重复 pygame，仅使用 pygame-ce 后，两平台全部通过；下载检查却发现图像是黑屏，因此不作为有效回放证据 |

新测试为 3 个纯逻辑测试 + 7 个真实环境集成测试。旧 Lab 000 有 4 个单元测试，Lab 001 有 7 个单元测试。教学输出保持 `SYSTEM MAP RESULT: 4 / 4 PASS` 与 `BASELINE RESULT: 4 / 6 PASS`，后者不是两个单元测试失败。

smoke 命令为 `--max-steps 5 --output-dir outputs/ci-smoke`，日志实际记录 `runner_step_limit`、5 个决策步、1.000 秒模拟时间、IDLE。这是短回合工程检查，不是安全驾驶结论。

## 两个真实排错记录

**重复依赖：** 首轮日志显示 pygame 与上游需要的 pygame-ce 同时安装、共享导入名。现已只固定 `pygame-ce==2.5.8`，摘要按真实分发包名称记录版本；同时记录 runner_sha256，区分相同 HEAD 下的本地代码改动。

**合法图片也可能是黑屏：** 下载 `feb3b6f` 的实际 CI 工件并打开 PNG 后，发现全黑。原测试只验证 PNG 格式和尺寸，未检查内容；因此测试全绿不代表回放有效。官方 EnvViewer 在 `SDL_VIDEODRIVER=dummy` 时设置 `enabled=False`，跳过全部绘制，即使 offscreen=True。

修正方式：`capture_frame()` 仅对离屏 viewer 恢复绘制，不创建桌面窗口，并拒绝全单色帧。强化现有集成测试：图片须含多种颜色、初末帧有变化、GIF 有多个不同帧。仍是 10 个新测试，但检查内容更严格。此兼容点依赖当前固定上游版本，升级时需重验。

依据：[官方 EnvViewer 源码](https://highway-env.farama.org/_modules/highway_env/envs/common/graphics/)。

渲染修正后的 CI 与实际画面复核，待下一次验证完成后记录，不能用上面两轮结果代替。

## 限制

默认使用模拟器状态与恒定高层动作，没有实现感知、跟车避碰、轨迹学习、强化学习或 VLA。当前种子场景不是专门构造的慢前车案例。GIF 仅采样决策时刻，不包含全部物理帧。当前只锁直接依赖，完整解析版本由 CI artifact 的 pip-freeze 留档。

原生桌面窗口、学习者本机和 macOS 没有本次运行证据。CI 的图片/日志工件保留 14 天，过期后应重跑工作流。
