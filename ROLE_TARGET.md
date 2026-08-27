# Role Target — Autonomous Driving VLA / Physical AI Engineer

这不是职位承诺，而是仓库用来筛选学习内容的能力目标。

## 目标角色

偏向以下交叉岗位：

- Autonomous Driving VLA Engineer；
- End-to-End Planning / Applied AI Engineer；
- Driving Foundation Model Engineer；
- Physical AI Systems / Evaluation Engineer；
- VLM/VLA 推理、微调、评测与部署工程师。

## 不以这些角色为主目标

- 纯车辆控制理论研究员；
- 底盘嵌入式工程师；
- SLAM / 高精地图算法专家；
- 传感器硬件工程师；
- 真实道路测试安全驾驶员；
- 只做 Prompt 或聊天 Agent 的应用工程师。

## 核心能力模型

### A. Driving Data

- 理解 scene / frame / sample / history / future；
- 多相机与自车状态时间同步；
- 训练标签和数据切分；
- world / map / ego / sensor / image / BEV 坐标；
- 数据质量、泄漏和分布偏移。

### B. Action & Motion

- waypoint / trajectory / control；
- SE(2)；
- 运动学自行车模型；
- trajectory feasibility；
- action tokenization；
- continuous trajectory head；
- 轨迹到控制器的边界。

### C. Model

- 时序视觉编码；
- VLM / VLA conditioning；
- imitation learning；
- action chunk / horizon；
- reasoning / implicit token；
- world model；
- fine-tuning 与推理。

### D. Evaluation

- deterministic contract checks；
- open-loop metrics；
- closed-loop / pseudo-simulation；
- safety、progress、comfort；
- failure taxonomy；
- ablation；
- reproducible benchmark。

### E. Systems

- latency budget；
- stale observation；
- batching / quantization；
- model serving；
- logging / metrics / trace；
- ODD / safety monitor / fallback；
- dataset / model versioning。

## 能力成熟度

```text
L1 见过：知道名词
L2 能解释：能画数据链和指出失败点
L3 能控制：能修改、测试、排错
L4 能权衡：知道替代方案、成本和适用边界
```

目标不是在所有方向达到研究专家，而是在主链上形成 L3，并在核心评测与工程边界逐步进入 L4。
