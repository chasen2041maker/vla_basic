# Role Target — XPENG-like Autonomous Driving R&D

公开方向资料原核对：2026-08-28；个人求职目标更新：2026-09-27（Asia/Shanghai）。下方历史岗位与技术链接不因本次个人目标更新而视作重新核验。

这不是职位或录用承诺，而是仓库用来筛选学习内容和证据强度的目标画像。

## 当前求职约束与待核对项

用户目标是进入**车企的智能驾驶团队**并胜任工作，薪资 20k 以上，**杭州优先、上海其次**。岗位必须实际服务智能驾驶研发；车企的一般 IT、座舱或营销 AI 岗位不能仅凭公司名称算作匹配。暂按人民币税前月薪 20k+ 理解，薪资口径待确认；城市必须核实实际办公地点，不能仅凭公司总部或职位标题推断。

岗位采样优先使用车企自身智驾团队和直接发布的 JD，同时记录劳动合同主体及子公司/合资关系。供应商、Robotaxi 服务商和外包驻场岗位可以作为其他行业资料，但不能替代目标车企团队的岗位样本，也不能默认用户接受它们。

现阶段要审查“全链路入门 + 一个方向做到可独立交付”能否服务求职，具体优先岗位仍待结合真实 JD 和个人条件选择。保留下文的 VLA 长期目标与数据闭环、评测仿真、模型工程等候选桥梁方向，不把它们当成已确定适合用户的岗位。

用户已说明 UNSW 硕士、AI 专业/方向，并在学校学过 C++；当前简历教育时间截至 2025.10，AI 应用后端工作自 2026.04 起。2027 届校招样本不能默认适用，须按实际学位授予时间和企业批次核对；同时关注符合经验条件的社招或允许往届的机会。转行期限、数学/C++实际水平、每周学习时间和硬件尚未确认或验证。正式岗位对照应逐项记录招聘类型、城市、硬性条件、必备能力、薪资口径、作品与个人证据。已结束岗位只能作历史样本；薪资区间不代表个人 offer。

早期课程审查材料及抽样依据保留在 [历史审查说明](../archive/COURSE_REVIEW_BRIEF.md)，其中课程状态已过时，不作当前入口。当前教材覆盖四章驾驶入门，视觉和模型等后续工程尚未交付，不能因为课程目录出现某能力就认为已达到岗位要求。

## 学历与 Python / C++ 的定位（2026-09-27）

AI 硕士与部分智驾算法、仿真和模型工程岗位的学历/专业范围相符，具体要看 JD。不能从学校和专业名称推断已经具备视觉、车辆运动、系统集成或独立排错能力。学校学过 C++ 是恢复学习的基础，下一证据应是读懂一个模块、完成小改、编译运行并定位错误。

语言要求按模块区分：训练实验、数据处理和分析常用 Python；仿真引擎、车端运行、规划控制与性能敏感模块常要求 C++；同一团队可能同时使用两者。当前使用 Python 串通驾驶实验，之后在实际职责需要时安排 C++ 的读改与调试，不把更换语言当成驾驶能力进步。具体学习接续以 PROGRESS 为准。

本轮使用企业招聘人员直接发布的两份小鹏 JD 作具体例证：

- [上海，27 届仿真算法工程师](https://www.nowcoder.com/jobs/detail/462573?urlSource=sitemap)：接受人工智能等相关专业，硕士优先；Python/C++/Go/Java 中至少精通一种，同时考察 Linux、算法和工程能力。这支持“学历专业有匹配岗位”的判断，但毕业年份资格仍待核实。
- [北京，27 届仿真软件工程师](https://www.nowcoder.com/jobs/detail/462576)：明确要求 C++ 面向对象基础、Python 与 Linux，并将 Agent/RAG/tool calling 等落地经验列为加分项。仅用于说明技能迁移和语言分工，北京不满足当前城市优先范围。

两份页面均为薪资面议，不构成 20k+ 的薪资证据；个别岗位也不能代表所有车企团队的要求。

## 根据当前简历校准的候选方向（2026-09-27）

当前简历主要呈现 AI 应用后端交付及 NLP 个人实验，尚未呈现驾驶、视觉几何、轨迹控制或 C++ 工程项目。基于这些已描述经历，优先对照车企智驾团队中的仿真评测工具/平台、数据闭环与场景检索工程、模型工具链与研发效率岗位；这只是候选排序，仍需具体 JD 和个人代码验证。

算法与模型研发保留为持续深入方向，需补齐对应的驾驶数据、视觉/时序、模型与评测作品。仿真平台工程不等于仿真建模算法；容器应用交付不等于分布式训练基础设施；NLP 蒸馏量化也不等于车端部署。不要通过更换简历术语掩盖这些边界。

课程让同一驾驶项目逐步形成场景复现、规则对照、自动评测与失败分析证据，再按选定方向深入；当前小节只由 PROGRESS 维护。简历更新只是校准起点，不改变当前学习验收状态。

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

岗位和技术信息按当前任务重新核实。[旧前沿雷达](../archive/FRONTIER_RADAR.md) 只保留历史来源与当时判断，不作为现行工具选型或动态进度。

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

## 5. 长期综合作品目标与近期投递证据

长期争取拥有一个公开、可复现的综合项目，能够展示：

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

以上是长期综合能力目标，**不是所有入门岗位共同的投递前置条件**。近期应依据选定的车企智驾岗位，确定与职责直接相关的作品和验收：例如数据闭环方向重点展示数据质量、场景检索与迭代证据，评测方向重点展示场景复现、指标和回归定位，模型工程方向重点展示训练/推理调试和行为/性能对照。具体岗位尚未选定，不能声称已有适合本人且满足薪资要求的投递路线。

---

## 6. 范围边界

本仓库不以以下角色为主：

- 纯控制理论研究员；
- SLAM / 高精地图深水区专家；
- 底盘嵌入式和车辆硬件工程师；
- 真实道路测试安全驾驶员；
- 只做 Prompt 或聊天 Agent 的应用工程师。

这些方向会按主线需要学习最低必要知识，但不会无限扩张。

---

## 附录：能力与证据参考

以下为 2026-09-27 的起点盘点与验收参考；个人最新掌握状态只维护在 PROGRESS.md，不在这里重复记进度。

最后局部校准：2026-09-27（新增 C++ 学校课程背景；其他能力状态未升级）

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
| C++ 智驾代码阅读 | VERIFY | 自述学校学过，先恢复与验证，不按零接触重讲 | 能读改、编译和调试基础 C++ 数据与推理链 |
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
