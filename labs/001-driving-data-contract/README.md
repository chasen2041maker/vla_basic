# Lab 001 — Driving Data Contract

## 主题

在接触模型前，先建立一条驾驶样本的完整契约：

```text
reference time
+ camera frames
+ ego state
+ coordinate frame
+ future trajectory
```

## 为什么是第一课

驾驶模型最危险的错误经常不会报异常：

- 相机帧错位；
- ego state 来自另一个时间；
- future label 从过去开始；
- world / ego 坐标混用；
- 秒和毫秒混用；
- yaw 的度和弧度混用。

模型仍然可以训练，loss 仍然可以下降，但学到的是错误关系。

## 分步任务

### 001A — Read Baseline（当前）

```text
运行 6 个 case
→ 观察 4/6
→ 找到两个 semantic silent failure
→ 解释 validation trace
```

任务：

- [`CURRENT_TASK.md`](CURRENT_TASK.md)

### 001B — Add Temporal Semantics（未解锁）

计划：

- camera skew；
- ego/reference time；
- future trajectory starts after reference；
- tests；
- before/after eval。

### 001C — Coordinate Contract（未解锁）

计划：

- world ↔ ego；
- round-trip；
- frame name；
- wrong-yaw fault。

## 完成 Lab 001 的证据

```text
[ ] 001A baseline 运行
[ ] 能解释 6 个 case
[ ] 001B temporal checks
[ ] 001B tests
[ ] 001C coordinate round-trip
[ ] 一次 fault injection
[ ] 一篇 learning journal
[ ] Teacher review
```
