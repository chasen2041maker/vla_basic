# Lab 000 — Driving System Map & Failure Boundaries

## 主题

在进入数据、视觉、模型和轨迹细节前，先建立一条完整的智能驾驶执行链：

```text
sensor
→ data contract
→ representation
→ model / planning
→ action decode
→ safety
→ control
→ vehicle / environment
→ evaluation / data loop
```

## 为什么先做这一课

学习局部代码时，最危险的问题不是语法不懂，而是不知道：

- 这个模块在整车链路哪里；
- 它的输入是否可信；
- 它输出的是表征、轨迹还是控制；
- 哪类错误应该由它拦截；
- 下游为什么不能自动修复所有上游错误。

Lab 000 提供后续所有 Lab 的导航图。

## 分步任务

### 000A — Read System Trace（当前）

```text
运行 4 个场景
→ 观察每个 stage 的 trace
→ 定位 stale observation、past trajectory 和 controller timeout
→ 解释 model success != driving success
```

任务：

- [`CURRENT_TASK.md`](CURRENT_TASK.md)

### 000B — Draw & Classify（后续证据）

计划：

- 用自己的话画系统图；
- 给 8–12 个故障分类；
- 说明每层负责和不负责什么；
- 增加一个独立场景与测试。

## 完成 Lab 000 的证据

```text
[ ] 000A reference 运行得到 4/4
[ ] 能画完整系统链
[ ] 能解释四个 stage boundary
[ ] 能指出 Agent retry 类比失效点
[ ] 独立增加一个 failure scenario
[ ] 增加对应 test
[ ] Teacher review
```

000A-Read 完成后可以并行进入 Lab 001A；完整 Lab 000 `PASSED` 仍需独立修改和测试。
