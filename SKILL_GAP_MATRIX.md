# Skill Gap Matrix

最后校准：2026-08-28

本文件把“已经会”“需要验证”“必须系统学习”和“现在延后”分开，避免重复学习，也避免把自述经验直接当作驾驶研发证据。

## 1. 状态含义

```text
USE      可以直接作为教学起点使用
VERIFY   不从基础重讲，但要在真实任务中用代码和实验验证
LEARN    当前主要缺口，需要系统建立
LATER    有价值，但依赖尚未满足，暂不进入主线
PASSED   已在仓库中形成可复现证据
```

`USE / VERIFY` 是课程安排，不等于招聘层面的精通。

---

## 2. 当前能力矩阵

| 能力 | 当前状态 | 教学决策 | 需要的仓库证据 |
|---|---|---|---|
| Python 工程阅读与开发 | USE | 不从语法开始 | 能独立跟踪完整 execution path |
| Agent / workflow / tool calling | USE | 只作为系统类比 | 能指出类比在物理世界哪里失效 |
| 常规深度学习训练 | VERIFY | 跳过基础训练循环 | 过拟合小数据、定位 loss/shape/gradient 问题 |
| Transformer / Attention | VERIFY | 按视觉与时序任务复用 | 能解释 token、mask、时序条件如何影响输出 |
| 蒸馏 | VERIFY | 不重讲定义，后期做驾驶实验 | teacher/student 目标、消融、行为与延迟对比 |
| 量化 | VERIFY | 不重讲定义，后期做部署实验 | 精度、行为、延迟、内存和失败场景对比 |
| 强化学习 | LATER | 先不学 PPO 名词表 | 先完成 state/action/rollout/closed-loop 基础 |
| 计算机视觉基础 | LEARN | 系统补齐 | 图像特征、ViT/CNN、检测/分割基本实验 |
| 相机几何与坐标 | LEARN | 系统补齐 | 内外参、投影、ego/world/camera round-trip tests |
| 多相机与时序 | LEARN | 系统补齐 | 时间轴、skew、ego-motion compensation 实验 |
| BEV / occupancy mental model | LEARN | 在几何后进入 | 能说明输入、输出、假设和失败症状 |
| 驾驶数据契约 | LEARN | 当前早期主线 | silent failure、validator 和 tests |
| trajectory / waypoint / control | LEARN | 系统补齐 | 轨迹表示、rollout、控制边界解释 |
| 车辆运动学 | LEARN | 系统补齐 | SE(2)、bicycle model、yaw/unit fault |
| 模仿学习驾驶 baseline | LEARN | 复用已有训练能力 | trajectory model、overfit、leakage check |
| 开放环 / 闭环评测 | LEARN | 核心缺口 | 构造指标背离与 compounding error |
| Driving VLM / VLA | LEARN | 基础依赖满足后进入 | 公开实现、conditioning ablation、action decode |
| ODD / safety / fallback | LEARN | 与闭环并行建立 | allow/reject/fallback tests |
| C++ 智驾代码阅读 | VERIFY | 当前水平待仓库验证 | 能读改基础 C++ 数据与推理链 |
| Linux / Git / 调试 | VERIFY | 不单独开基础课 | 无 Coding Agent 完成一次关键排错 |
| 分布式训练 | LATER | 单机 baseline 稳定后进入 | 可复现实验和性能瓶颈证明 |
| 车端推理与可观测性 | LEARN | 利用量化经验迁移 | latency breakdown、stale detection、version log |

---

## 3. 最短转型路径

### 路径 A：先形成可投递的桥梁能力

更贴近当前工程背景：

```text
驾驶数据契约
→ 数据价值 / 场景挖掘
→ 评测与仿真
→ 模型训练和推理链
→ 部署与可观测性
```

可连接的岗位方向包括：

- 智驾数据价值与数据闭环；
- 自动化评测与仿真；
- AI Infra / 训练平台 / 推理平台；
- 端到端算法工程支持。

### 路径 B：长期进入核心 VLA 算法

```text
视觉与几何
→ 多相机时序
→ 轨迹与车辆运动
→ 端到端模型
→ 闭环评测
→ Driving VLM / VLA
→ RL / world model / long-tail
```

两条路径不是二选一。路径 A 提供更快的行业入口，路径 B 是长期北极星。

---

## 4. 不重复教学规则

以下内容不机械重讲：

- Python 基础语法；
- 普通 `Dataset/DataLoader` API 大全；
- 基础反向传播和 optimizer 定义；
- 蒸馏、量化的纯名词课；
- 从空白搭大量训练 boilerplate。

但遇到驾驶任务时仍会验证：

```text
能否跟踪 tensor 和时间语义
能否修改 loss / head / decode
能否定位 leakage / normalization / metric 问题
能否用实验说明蒸馏或量化的真实收益
```

---

## 5. 当前优先级

```text
P0  系统全景和 failure boundary
P0  时间、坐标、trajectory/control
P0  视觉与相机几何
P0  open-loop / closed-loop
P1  端到端 trajectory baseline
P1  Driving VLM / VLA
P1  C++ / deployment / observability
P2  distillation / quantization 驾驶化验证
P2  reinforcement learning / world model
```

优先级由依赖决定，不代表后面的内容不重要。
