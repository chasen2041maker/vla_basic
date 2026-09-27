# Current Task — 000A: Driving System Trace

> Mode: system orientation + guided reference  
> 当前不是训练模型，也不是修改 validator，而是先看懂完整驾驶链路和故障边界。

## Role Relevance

智能驾驶研发人员不能只会训练模型。面对“车辆表现不好”，必须先判断问题位于：

```text
data
representation
model
action / safety
control
or evaluation / system
```

这是后续做 VLA、蒸馏、量化、强化学习和部署的共同基础。

## System Position

本任务覆盖整条链：

```text
Sensor Capture
→ Data Contract
→ Model Inference
→ Safety Monitor
→ Control
→ Environment Feedback
```

它暂时把视觉表征和真实模型简化掉，只保留职责边界。

## Why

如果不知道边界，会出现这些错误归因：

- 相机过期却责怪模型结构；
- 模型轨迹来自过去却让控制器修；
- 控制器超时却继续优化 trajectory loss；
- evaluator 写错却相信模型指标；
- 量化后只看 accuracy，不看行为和 deadline。

## Mental Model

```text
reference_timestamp_ms
        ↓
camera timestamps + ego-state timestamp
        ↓
Data Contract 判断观测是否新鲜且对齐
        ↓
Model 产生 synthetic future trajectory
        ↓
Safety 判断轨迹是否真在未来且时间递增
        ↓
Controller 把轨迹转为执行命令
        ↓
Environment 接受动作并产生下一状态
```

## Reference

```text
guided_reference/000a/
├── driving_system/
│   ├── __init__.py
│   └── pipeline.py
├── run_trace.py
└── tests/test_pipeline.py
```

## Run

在仓库根目录：

```powershell
cd labs\000-driving-system-map\guided_reference\000a
python run_trace.py
python -m unittest discover -s tests -v
```

预期：

```text
SYSTEM MAP RESULT: 4 / 4 PASS
```

## Observe

先找出：

1. `nominal` 为什么能走完整条链？
2. `stale_camera` 在哪一层停止？为什么模型不应该接收它？
3. `past_trajectory` 为什么经过 model stage 后仍被拒绝？
4. `controller_timeout` 为什么不是 trajectory model 的错误？
5. 一个 stage 停止后，哪些下游 stage 不应该再运行？

## Learn

本轮必须能解释：

- `SystemScenario`；
- `PipelineTraceEvent`；
- `PipelineReport`；
- observation freshness；
- model output 与 safe action 的区别；
- trajectory 与 control 的边界；
- fail-fast；
- system success 与 model success 的区别。

## Do

本小步只需要：

1. 阅读 `SYSTEM_MENTAL_MODEL.md`；
2. 运行 reference；
3. 按顺序解释 nominal execution path；
4. 为三个失败场景指出停止层和责任边界；
5. 用自己的话画出系统链。

暂时不要修改代码。

## Break It

只读实验：

在 `run_trace.py` 中临时把 `stale_camera` 的旧相机时间从 `4750` 改成 `4980`，观察它是否能继续进入 model stage。

实验后恢复文件。

## Tests / Eval

当前测试证明：

```text
nominal              → completed
stale_camera         → data_contract
past_trajectory      → safety_monitor
controller_timeout   → control
```

测试只证明当前简化系统按契约运行，不代表量产自动驾驶安全。

## Explain

完成后回来回答：

1. 为什么 `model_inference=pass` 不等于驾驶成功？
2. 为什么 stale observation 应该在 model 前被拒绝？
3. 为什么 future trajectory 的语义还需要 safety monitor 检查？
4. 为什么 controller timeout 不应该通过重新训练模型解决？
5. open-loop 评测看不到这条链中的哪些问题？
6. 这和 Agent workflow 的 stage / tool boundary 有什么相似？
7. 类比在哪里失效？

## Pass Criteria — 000A Read

```text
[ ] 实际运行得到 4/4
[ ] 能按顺序解释 nominal trace
[ ] 能说出三个失败场景的 stopped_at
[ ] 能解释 model output、safe action 和 control 的区别
[ ] 能画 sensor 到 environment feedback 的完整链
[ ] 能指出至少一个 Agent 类比失效点
```

完成后解锁：

```text
001A — Driving Data Contract Baseline
```

## Do Not Do Yet

- 不训练神经网络；
- 不下载真实驾驶数据；
- 不学相机内外参；
- 不写 BEV；
- 不学 PPO / DPO / GRPO；
- 不接 CARLA / NAVSIM；
- 不优化所有安全检查；
- 不讨论量产系统完整架构。

先建立正确导航图。
