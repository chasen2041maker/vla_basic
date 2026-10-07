# 驾驶术语速查

遇到不认识的词时来查，不用提前背。前面一张表是当前实验里最常用的；后面的相机、VLA、压缩等是以后会遇到的。

## 当前运行里最容易混淆的几个词

| 名称 | 先这样理解 | 去哪个现象核对 |
| --- | --- | --- |
| State / Target | 现在的状态 / 希望达到的状态 | 04 的实际速度曲线与目标线 |
| Step / Simulation Time | 环境推进一次 / 模拟世界经过的秒数 | 实验打印的动作前后时间；不同配置的一步不一定同长 |
| Observation | 环境交给策略的信息，可能做过相对变换、归一化或裁剪 | 00 的候选行与最近距离（来自模拟器状态表，不是相机识别） |
| Seed | 随机种子：同版本、同配置下决定初始路况 | 原版与修改版的第一份观察相同，之后会因动作不同而分叉 |
| End Reason | 为什么这次停止 | 05 的环境时限与脚本步数预算；停止不等于任务成功 |

表里的实验见 [demos/README.md](../experiments/highway_driving/demos/README.md)。

## Sensor Observation｜传感器观测

传感器在某个采集时间得到的原始或处理后观测。读取时间不等于采集时间。

## Scene｜场景

一段连续驾驶过程或场景，不等于单帧图片。

## Sample｜样本

围绕一个 reference time 构造的一次模型输入与标签。

## Reference Time｜参考时刻

样本定义“现在”的时间锚点。历史输入位于它之前或附近，future label 应位于它之后。

## History Window｜历史窗口

reference time 之前提供给模型的观测序列。

## Ego State｜自车状态

自车在某个时间点的位置、航向、速度等状态，必须带时间和坐标语义。

## Coordinate Frame｜坐标系

描述位置和方向所采用的参考系。常见有 world、ego、camera、image 和 BEV。

## Camera Intrinsics｜相机内参

描述相机内部投影关系的参数，例如焦距和主点。

## Camera Extrinsics｜相机外参

描述相机相对于车辆或世界的位置和朝向。

## Representation｜表征

从原始像素和状态提取的模型内部表达，例如 feature map、visual token、BEV 或 occupancy。

## Perception｜感知

从传感器中理解道路、目标、空间和运动的过程。端到端模型可以不显式输出所有感知结果，但仍需形成可用于动作的表征。

## Waypoint｜路点

轨迹中的一个离散目标点。单个 waypoint 不等于完整 trajectory。

## Trajectory｜轨迹

按时间排序的一组未来状态或位置点，必须明确坐标、horizon、采样间隔和单位。

## Future Trajectory｜未来轨迹

reference time 之后的自车目标或真值轨迹。

## Action｜动作

策略、规则、人工指定或模型生成的动作输出，用于影响环境的后续状态。可能是高层目标、轨迹、离散 token、连续控制等，含义取决于接口。本项目的 IDLE / SLOWER 来自脚本或规则，不一定要有神经网络。

## Control｜控制量

直接作用于车辆执行层的命令，例如转向、制动和驱动。Trajectory 通常仍需控制器跟踪。

## VLM｜视觉语言模型

Vision-Language Model。结合视觉和语言/语义进行理解或生成，不自动意味着能输出可执行驾驶动作。

## VLA｜视觉语言动作模型

Vision-Language-Action Model。把视觉、语言/语义或其他状态条件连接到动作输出。驾驶 VLA 的 action 必须明确其时间、坐标、horizon 和执行方式。

## Behavior Cloning / Imitation Learning｜行为克隆 / 模仿学习

从专家记录的状态—动作对学习策略。离线拟合好不代表闭环稳定。

## Open-Loop Evaluation｜开环评测

在已记录的输入上比较策略或模型输出，输出不会改变这份记录的后续输入。例如预测轨迹与真实标签的误差；仅打印一次状态不自动构成开放环评测。

## Closed-Loop Evaluation｜闭环评测

把被评估策略的动作交给交互环境，再用变化后的观测继续决策并评价整段行为。本项目里，00 跟车规则是闭环的；05 的固定动作对照虽然环境在推进，但策略不看新观察，所以只是在看控制响应。

## Pseudo-Simulation｜伪仿真

介于纯开放环和完整交互仿真之间的数据驱动评价。具体定义以框架为准。

## Stale Observation｜过期观测

观测在被模型使用时已经过期。格式仍合法，但它描述的不是当前世界。

## Silent Failure｜静默失败

程序正常返回、格式合法，但任务语义错误，例如未来轨迹从过去开始。

## ODD｜设计运行域

Operational Design Domain，系统预期有效的道路、天气、速度、区域和交通条件边界。

## Fallback｜降级 / 兜底

主策略不可用、超时、越界或不安全时切换的替代行为。

## Distillation｜蒸馏

用 teacher 的输出、特征或行为监督 student。驾驶中必须检查 student 是否继承 teacher 错误，以及闭环行为是否保留。

## Quantization｜量化

降低权重或激活数值精度以换取速度、内存或能耗收益。平均精度接近不代表长尾驾驶行为不变。

## Reinforcement Learning｜强化学习

通过环境交互或轨迹反馈优化 policy。进入前必须定义 state、action、transition、reward、rollout、evaluator 和 safety boundary。

## World Model｜世界模型

学习环境状态如何随动作和时间演化的模型。可用于预测、仿真、数据生成或训练，但会受到 model bias 和 rollout drift 影响。
