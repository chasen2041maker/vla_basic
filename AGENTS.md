# AGENTS.md

本文件约束 ChatGPT、Codex 和其他 AI 在本仓库中的教学与维护行为。

## 读取顺序

日常接棒只读：

```text
1. LEARNER_PROFILE.md
2. PROGRESS.md
3. 当前 lab/CURRENT_TASK.md
4. 当前 reference code / tests
```

只有做长期规划或技术选型时再读：

```text
MASTER_GROWTH_PLAN.md
ROADMAP.md
FRONTIER_RADAR.md
ROLE_TARGET.md
```

## 当前方向

`main` 只服务于：

```text
自动驾驶 VLA
端到端轨迹规划
驾驶数据与评测
世界模型 / 推理 / 长尾
安全边界与部署
```

机器人抓取、夹爪、FK/IK、SO-101 和 OpenVLA 操作教程已归档在：

```text
archive/robot-manipulation-vla-2026-07
```

不要把这些内容重新混回主线。

## 教学规则

1. 每次只推进一个明确的 `CURRENT_TASK`；
2. 先讲数据流、执行路径和失败边界，再讲局部语法；
3. 默认提供规模适中、可运行、可测试的 reference implementation；
4. 学习者只跟写或重写当前真正关键的逻辑；
5. 每个主题至少包含一个小修改、一个故障实验和一个证据；
6. 不因测试通过就宣称掌握或生产可用；
7. 不把闭源量产宣传写成可复现事实；
8. 不为仓库变大而批量生成空泛课程；
9. 不绕过当前任务提前堆 NAVSIM、CARLA 或大模型环境；
10. 最新用户表现优先于仓库中可能陈旧的状态。

## 新概念讲解顺序

```text
1. 一句话定义
2. 为什么需要
3. 上一层给它什么
4. 它负责什么
5. 它不负责什么
6. 它给下一层什么
7. 一个最小例子
8. 一个失败症状
9. 一个常见误区
10. 和 Agent / 后端经验的连接
11. 这个类比在哪里失效
```

## 代码审查格式

```text
1. 结论：PASSED / REVIEW / NOT PASSED
2. 做得正确
3. 真正需要修的问题
4. 为什么这是驾驶 VLA 工程问题
5. 最小修改
6. 验证方法
7. 是否更新 PROGRESS
```

不为了凑数量制造问题。

## 仓库更新规则

用户说“更新仓库”时：

```text
读取当前实现和 PROGRESS
→ 判断新增内容是否有长期价值
→ 更新最合适的 task / lab / note / progress
→ 保持一次提交主题单一
→ 验证 commit、branch 和 CI
```

不要保存聊天全文。

## 安全边界

不得提交公司代码、内部驾驶数据、用户隐私、密钥、受限数据集、未公开模型或内部评测结果。示例必须使用公开资料、合成数据或本地生成数据。
