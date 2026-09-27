# Queued Task — 001A: Driving Contract Baseline

> Status: QUEUED  
> Prerequisite: 完成 Lab 000A Read 后再开始。  
> Mode: guided reference implementation。

## Role Relevance

核心 VLA、数据价值、评测和仿真岗位都需要判断：模型输入和训练标签是否表达同一个时间、坐标和物理事实。

## System Position

```text
Sensor Capture
        ↓
Data Contract & Alignment  ← 当前任务
        ↓
Representation / Model
```

## Why

自动驾驶模型的第一责任不是“模型够不够大”，而是：

> **输入和训练标签是否处于同一个时间、同一个坐标和同一个物理语义下。**

时间或坐标错了，代码可能完全不报错。

本轮建立：

```text
program success
≠ structural validity
≠ semantic validity
≠ model success
≠ driving success
```

## Mental Model

一条样本：

```text
reference_timestamp_ms
        ├── camera frames around this time
        ├── ego state at this time
        └── future trajectory strictly after this time
```

baseline validation path：

```text
JSON Case
  ↓
DrivingSample.from_dict
  ↓
BaselineValidator
  ↓
Validation Trace
  ↓
valid / invalid
  ↓
Evaluator compares expected semantic validity
```

## Reference

```text
guided_reference/001a/
├── data/cases.json
├── driving_contract/
│   ├── contracts.py
│   ├── transforms.py
│   └── validator.py
├── run_eval.py
└── tests/
```

## Run

在仓库根目录：

```powershell
cd labs\001-driving-data-contract\guided_reference\001a
python run_eval.py
python -m unittest discover -s tests -v
```

预期：

```text
4 / 6 PASS
2 / 6 FAIL
```

如果不是 4/6，先记录真实输出，不要修改代码。

## Observe

1. 哪两个 case 没通过？
2. baseline validator 为什么把它们当成 valid？
3. trace 中已经检查了什么？
4. 哪个语义事实完全没有被检查？
5. 为什么 dataclass 构造成功不代表驾驶样本正确？
6. 这些错误为什么必须在模型前被拦截？

## Learn

- `DrivingSample`；
- `reference_timestamp_ms`；
- `CameraFrame`；
- `EgoState`；
- `TrajectoryPoint`；
- `ValidationIssue`；
- `ValidationReport`；
- structural check 与 semantic check；
- data boundary 与 model boundary。

## Do

本小步只需要：

1. 运行；
2. 读代码；
3. 找到两个 failing case；
4. 用自己的话解释 failure 起点；
5. 把它们放回 Lab 000 的系统图。

暂时不要实现新 validator。

## Break It

在 `cases.json` 中临时把一个合法轨迹点的时间戳改成和前一个相同，运行后观察 baseline 是否能发现。

实验后恢复文件。

## Tests / Eval

当前测试故意锁定：

```text
baseline = 4 / 6
```

这不表示 validator 正确，只表示教学 baseline 没有意外变化。

## Explain

1. runtime success 为什么不等于 sample semantic success？
2. future_trajectory 为什么必须相对 reference time 定义？
3. 相机时间偏差为什么不能只靠 JSON schema 发现？
4. 如果模型用错位样本训练，为什么可能不会崩溃？
5. 这类错误在完整系统链中应在哪一层停止？
6. 这和 Agent 工具调用成功但用户任务失败有什么相似？
7. 类比在哪里失效？

## Pass Criteria — 001A Read

```text
[ ] 实际运行得到 4/6
[ ] 说出两个 failing case 名称
[ ] 指出 baseline 缺少的两类 semantic check
[ ] 按代码顺序解释 validation path
[ ] 解释 structural valid != semantic valid
[ ] 把 failure 定位到 data contract boundary
```

完成后进入：

```text
001B — Temporal Semantics + Before/After Eval
```

## Do Not Do Yet

- 不接真实数据集；
- 不下载 NAVSIM；
- 不训练模型；
- 不写 BEV；
- 不接 LLM；
- 不实现 world model；
- 不优化所有校验。

先建立时间契约。
