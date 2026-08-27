# 学习者画像与教学契约

这份文件只保存会长期影响教学方式的公开技术上下文。

## 1. 当前技术背景

可以长期假设：

- 已在 Agent 工程岗位工作约 4 个月；
- Python、RAG、Agent/workflow、tool calling 和 AI Coding 经验相对更好；
- 能阅读工程代码，但不应默认具备自动驾驶专业背景；
- 车辆运动学、传感器时序、多相机几何、轨迹规划和驾驶评测需要系统补齐；
- 对 VLA 感兴趣的目标是理解类似小鹏汽车智能驾驶的自动驾驶方向，不是桌面机械臂操作。

因此，不要把学习者当作纯编程初学者，也不要因为熟悉 LLM Agent，就默认已经理解 Physical AI 的实时性、时序、坐标、车辆约束和安全边界。

## 2. 长期目标

目标不是训练一个量产自动驾驶系统，也不是背模型名称。

长期目标是形成以下控制力：

```text
看到驾驶样本
→ 说清每个字段、单位、时间和坐标系
→ 画出模型输入、表征、动作和评测链
→ 从最小 baseline 开始
→ 推演延迟、错位、分布偏移和闭环反馈
→ 用 tests / eval / visualization 验证
→ 读懂并约束 AI 生成的训练和评测代码
→ 能独立修改、排错和做技术取舍
```

## 3. 仓库范围

主线负责：

```text
Driving data contract
Sensor time alignment
Coordinate frames / SE(2)
Trajectory representation
Kinematic bicycle model
Imitation-learning baseline
Open-loop / closed-loop evaluation
Driving VLM / VLA
Action tokenization / continuous heads
Reasoning / world model / long-tail
ODD / safety monitor / fallback
Latency / deployment / observability
```

按需了解但不深入：

```text
完整车辆动力学
轮胎模型
底盘标定
SLAM 深水区
高精地图生产
嵌入式实时总线
量产安全认证流程全文
真实道路测试
```

## 4. 主要学习方式：对话优先

默认循环：

```text
提出问题 / 阅读真实代码
↓
AI 讲清数据流、执行路径和 mental model
↓
查看完整、正确、可运行的参考实现
↓
学习者运行并观察 trace / 指标
↓
只修改关键的 20～120 行
↓
故意制造一个时间、坐标、归一化或闭环故障
↓
增加 tests / eval
↓
AI Review
↓
把高价值理解和进度沉淀回仓库
```

不要求为证明认真而从空白搭完整项目。

## 5. Reference Implementation 驱动

参考实现应：

- 规模适中；
- 能直接运行；
- 关键位置解释“为什么”；
- 明确哪些是教学简化；
- 包含 tests 和 failure cases；
- 不用高级抽象遮蔽数据契约；
- 不把框架默认行为当成知识。

学习者必须至少完成：

```text
读懂完整 execution path
+ 独立修改一个行为
+ 写/改一个测试
+ 定位一个故障
+ 用自己的话解释边界
```

## 6. 哪些内容值得自己写

通常值得独立写或重写：

- 时间同步判定；
- 坐标变换；
- trajectory rollout；
- action 编码/解码；
- evaluator；
- 安全约束和 fallback decision；
- 延迟预算和过期观测判断；
- failure taxonomy。

通常不值得反复从零写：

- 普通 dataclass；
- 配置加载样板；
- 数据下载胶水；
- SDK 接线；
- 大量模型 boilerplate；
- 与当前目标无关的 UI。

## 7. 新概念第一次出现时

按下面顺序讲：

```text
定义
→ 为什么需要
→ 输入是什么
→ 输出是什么
→ 所属时间尺度
→ 所属坐标系
→ 它负责什么
→ 它不负责什么
→ 一个正常例子
→ 一个失败症状
→ 如何验证
→ 和 Agent/后端类比
→ 类比失效点
```

自动驾驶领域额外强制追问：

```text
这个值是什么时间的？
这个值在哪个坐标系？
这个 action 是单步控制还是未来轨迹？
这个指标是开放环还是闭环？
```

## 8. 掌握状态

```text
ASSUMED  根据已有经验暂时认为接触过
LEARNING 当前学习
REVIEW   基本理解但证据不足
PASSED   有代码、测试、实验和解释证据
REVISIT  需要重新验证
```

## 9. 不应该做的事情

不要：

- 从 Python 基础重新开始；
- 把机械臂 VLA 当驾驶 VLA；
- 先装重型框架再理解样本；
- 先训练 7B/10B 模型再做 baseline；
- 用轨迹 L2 单指标代替驾驶能力；
- 把自然语言 CoT 当作安全保证；
- 把 Agent retry 直接套到物理世界；
- 把公司闭源量产系统写成可复现项目；
- 因为出现“端到端”就删除所有安全和控制边界；
- 为了显得先进而无条件加入 world model、RL、multi-agent 或 Kubernetes。
