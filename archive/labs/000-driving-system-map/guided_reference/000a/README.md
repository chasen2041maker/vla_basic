# Guided Reference 000A

这是一个零第三方依赖的系统边界教学 baseline。

它没有真实图像、神经网络、控制器或车辆仿真，只用确定性场景展示：

```text
Sensor Capture
→ Data Contract
→ Model Inference
→ Safety Monitor
→ Control
→ Environment Feedback
```

## Run

```powershell
python run_trace.py
python -m unittest discover -s tests -v
```

预期：

```text
SYSTEM MAP RESULT: 4 / 4 PASS
```

## 四个场景

| 场景 | 结果 | 停止层 |
|---|---|---|
| nominal | 完成闭环前半程 | none |
| stale_camera | 观测过期 | data_contract |
| past_trajectory | 模型输出不是纯未来轨迹 | safety_monitor |
| controller_timeout | 控制执行不可用 | control |

## 教学简化

- `model_inference` 直接读取场景中的 synthetic trajectory；
- 没有真实视觉表征；
- safety 只检查时间语义；
- control 只检查是否可用；
- environment 只记录“动作已应用”；
- threshold 不代表量产标准。

这些简化用于隔离第一件事：**知道错误属于哪个系统边界。**
