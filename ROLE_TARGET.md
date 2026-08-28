# Role Target — XPENG-like Autonomous Driving R&D

最后核对：2026-08-28

这不是职位或录用承诺，而是仓库用来筛选学习内容和证据强度的目标画像。

## 1. 北极星角色

长期目标偏向：

- Driving VLM / VLA Algorithm Engineer；
- End-to-End Autonomous Driving Algorithm Engineer；
- Driving Foundation Model / World Model Engineer；
- Action Representation / Planning Model Engineer；
- Autonomous Driving Evaluation / Physical AI Systems Engineer。

现实桥梁岗位包括：

- 智驾数据价值、场景挖掘和数据闭环；
- 自动驾驶评测、仿真和 failure mining；
- AI Infra、训练平台、推理平台和模型优化；
- 端到端模型工程、部署和可观测性。

---

## 2. 2026 公开信号

公开岗位和技术资料表明，目标能力已经不只是普通深度学习训练，还包括：

- 不依赖 Coding Agent 完成关键 debug；
- 多模态理解、时序推理和端到端模型；
- VLA、VLM、世界模型和闭环强化学习；
- 数据价值、场景发现和数据流转；
- 闭环仿真、模型评估和长尾数据生成；
- 蒸馏、视觉 token 压缩、推理效率和车端部署。

这些是路线设计依据，不代表每个候选人必须一开始同时精通所有方向。

公开来源：

- VLA/VLM 算法工程师：<https://xiaopeng.jobs.feishu.cn/campus/position/7658239744397347110/detail>
- 数据价值算法工程师：<https://xiaopeng.jobs.feishu.cn/campus/position/7658239755088447770/detail>
- 大模型算法工程师（智驾/机器人）：<https://xiaopeng.jobs.feishu.cn/campus/m/position/7668513578471475462/detail>
- 世界模型及环境感知：<https://xiaopeng.jobs.feishu.cn/campus/m/position/7658239755087759642/detail>
- X-World：<https://www.xiaopeng.com/news/company_news/5548.html>
- FastDriveVLA：<https://www.xiaopeng.com/news/company_news/5526.html>

岗位和技术会变化，`FRONTIER_RADAR.md` 负责动态更新。

---

## 3. 能力成熟度

```text
L0 不知道：无法解释基本输入输出
L1 见过：知道名词和用途
L2 能解释：能画数据链并指出常见失败
L3 能控制：能实现、修改、测试、评测和排错
L4 能权衡：能设计对照实验、替代方案和生产边界
```

目标不是所有方向都成为研究专家，而是：

```text
主链 data → model → action → eval → system 达到 L3
+ 至少一个方向逐步达到 L4
```

---

## 4. 七条能力轴

### A. Coding & Debugging

目标：L3

- Python / PyTorch 工程链；
- Linux、Git、profiling 和最小复现；
- 能在没有 Coding Agent 时定位关键 bug；
- C++ 达到阅读、修改和调试基础智驾模块；
- tensor shape、device、dtype、mask、NaN、显存和吞吐排错。

### B. Deep Learning & Experimentation

目标：已有基础进入驾驶化验证

- 训练、优化、过拟合、泛化、泄漏和消融；
- Transformer、ViT 和时序建模；
- 蒸馏、量化和模型压缩；
- 分布式训练和大模型微调按需要补齐；
- 强化学习在闭环基础建立后进入。

### C. Vision, Geometry & Temporal Understanding

目标：L3

- 图像、视觉特征和 token；
- 相机内参、外参、投影和深度；
- ego / world / camera / image / BEV 坐标；
- 多相机异步、历史帧和 ego-motion compensation；
- BEV / occupancy / temporal representation 的边界。

### D. Driving Motion & Action

目标：L3

- scene / sample / history / future；
- waypoint / trajectory / speed profile / control；
- SE(2) 和运动学自行车模型；
- trajectory feasibility；
- action token、continuous head 和 decode consistency；
- 规划层与控制层职责边界。

### E. Driving Model / VLA

目标：L3

- imitation-learning trajectory baseline；
- 多相机历史、ego state 和 route conditioning；
- Driving VLM / VLA；
- direct trajectory、action token、diffusion/flow head；
- reasoning / implicit token；
- conditioning、action 和模型消融。

### F. Evaluation & Reliability

目标：L3–L4

- contract tests；
- open-loop / pseudo-closed-loop / closed-loop；
- safety、progress、comfort 和 rule compliance；
- evaluator unit tests；
- failure taxonomy、long-tail 和 domain shift；
- 结论边界和可复现实验。

### G. Systems, Safety & Deployment

目标：L3

- preprocessing / inference / decode / control latency；
- stale observation 和 deadline；
- quantization / token pruning / runtime；
- ODD、safety monitor、fallback 和 minimum-risk behavior；
- model/data/config versioning、logs、metrics、trace 和 rollback。

---

## 5. 可投递前的最低作品证据

至少拥有一个公开、可复现的完整项目，能够展示：

```text
数据契约与可视化
+ 端到端训练和推理
+ 独立模型或 action 修改
+ 开放环和闭环评测
+ 三类以上 failure analysis
+ 蒸馏/量化或部署实验
+ latency / memory / behavior 对比
+ 安全边界与 fallback
+ 清楚的技术报告和复现说明
```

只跑 README、只展示 loss 曲线、只让 Coding Agent 写完或只背模型名称，都不足以达到目标。

---

## 6. 范围边界

本仓库不以以下角色为主：

- 纯控制理论研究员；
- SLAM / 高精地图深水区专家；
- 底盘嵌入式和车辆硬件工程师；
- 真实道路测试安全驾驶员；
- 只做 Prompt 或聊天 Agent 的应用工程师。

这些方向会按主线需要学习最低必要知识，但不会无限扩张。
