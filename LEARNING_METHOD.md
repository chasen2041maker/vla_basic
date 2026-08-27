# Learning Method

本仓库采用：

> **guided reference implementation + targeted modification + fault experiment + evidence-based progression**

目标是在有限业余时间内，高密度建立自动驾驶 VLA 的数据、模型、评测和工程 mental model。

## 为什么不用纯 blank-page 学习

学习者已有实际 AI 工程经验。每个主题从空目录搭工程，会把大量时间消耗在样板代码，而不是：

- 时间对齐；
- 坐标语义；
- 动作契约；
- 闭环分布偏移；
- evaluator 正确性；
- safety boundary；
- 模型延迟和部署一致性。

默认采用：

```text
看一个真实工程问题
→ 阅读可运行参考实现
→ 讲 execution / data path
→ 自己运行
→ 观察 trace / visualization / metric
→ 修改关键逻辑
→ 注入 failure
→ 增加 test / eval
→ 解释 trade-off
```

## 建议时间分配

大致：

- 45%：读懂数据流、模型接口、评测和设计取舍；
- 25%：修改 / 扩展 / debug；
- 20%：测试、可视化、fault injection 和结果分析；
- 10%：从空白重写最重要的核心逻辑。

原则是减少低价值样板，增加高价值判断。

## 每个任务的固定动作

```text
Run
→ Observe
→ Explain
→ Change
→ Break
→ Test
→ Review
```

一个主题不能只停留在“读过论文”或“代码跑通”。

## Reference Implementation 要求

1. 不依赖私有数据；
2. 第一次尽量用合成或 mini 数据；
3. 输入输出契约显式；
4. 时间戳、单位、坐标系写进类型和变量名；
5. 可重复运行；
6. 有预期输出；
7. 有至少一个故意保留的 failure gap；
8. 教学简化必须明说；
9. 框架出现时解释它隐藏的底层机制；
10. 不把宣传指标当成可复现实验。

## 驾驶 VLA 的四类证据

### 1. Contract Evidence

能证明：

- 字段齐全；
- 单位明确；
- 时间对齐；
- 坐标一致；
- train / inference contract 一致。

### 2. Model Evidence

能证明：

- baseline 可以过拟合小样本；
- loss 与行为指标的关系被检查；
- 输入消融真的改变输出；
- action decode 正确；
- 不是数据泄漏。

### 3. Evaluation Evidence

能证明：

- evaluator 本身正确；
- 开放环和闭环分开；
- 指标没有被“不动”或过度保守策略投机；
- failure category 可解释。

### 4. System Evidence

能证明：

- 延迟预算可测；
- 过期观测可检测；
- 输出经过可行性和安全检查；
- 日志足以复现实验；
- fallback 条件明确。

## 最终验收问题

- 能不能打开任意样本解释每个字段？
- 能不能画出历史输入到未来轨迹的时间关系？
- 能不能在 world / ego 坐标间转换并测试？
- 能不能解释 trajectory 和 control 的区别？
- 能不能判断一个 metric 是开放环还是闭环？
- 能不能定位模型、数据、解码、控制或 evaluator 的问题？
- 换一个 VLA 框架后 mental model 是否仍然成立？
