# 驾驶术语速查

这里用于遇到术语时速查，不是进入实验前要背完的清单。当前模拟器实验实际使用观察、动作、控制、时间和坐标；相机、VLA、压缩等属于后续参考，出现定义不表示工程已交付。完整讲解与动手步骤维护在教材中，当前接续看 [PROGRESS](../PROGRESS.md)。

## 当前运行里最容易混淆的几个词

| 名称 | 先这样理解 | 去哪个现象核对 |
| --- | --- | --- |
| State / Target | 现在的状态 / 希望达到的状态 | 04 的实际速度曲线与目标线 |
| Step / Simulation Time | 环境推进一次 / 模拟世界经过的秒数 | 实验打印的动作前后时间；不同配置的一步不一定同长 |
| Observation | 当前接口提供的信息，可能经过相对变换、归一化或裁剪 | 00 的候选行与最近距离；它是模拟器状态表，不是相机识别 |
| Seed | 在匹配的软件与配置下控制随机初态 | 原版与修改版首次观察是否相同，不要求后续状态相同 |
| End Reason | 为什么这次停止 | 05 的环境时限与脚本步数预算；停止不等于任务成功 |

这些现象对应[已有实验](../experiments/highway_driving/demos/README.md)，不增加一套术语 Demo。

## Sensor Observation

传感器在某个采集时间得到的原始或处理后观测。读取时间不等于采集时间。

## Scene

一段连续驾驶过程或场景，不等于单帧图片。

## Sample

围绕一个 reference time 构造的一次模型输入与标签。

## Reference Time

样本定义“现在”的时间锚点。历史输入位于它之前或附近，future label 应位于它之后。

## History Window

reference time 之前提供给模型的观测序列。

## Ego State

自车在某个时间点的位置、航向、速度等状态，必须带时间和坐标语义。

## Coordinate Frame

描述位置和方向所采用的参考系。常见有 world、ego、camera、image 和 BEV。

## Camera Intrinsics

描述相机内部投影关系的参数，例如焦距和主点。

## Camera Extrinsics

描述相机相对于车辆或世界的位置和朝向。

## Representation

从原始像素和状态提取的模型内部表达，例如 feature map、visual token、BEV 或 occupancy。

## Perception

从传感器中理解道路、目标、空间和运动的过程。端到端模型可以不显式输出所有感知结果，但仍需形成可用于动作的表征。

## Waypoint

轨迹中的一个离散目标点。单个 waypoint 不等于完整 trajectory。

## Trajectory

按时间排序的一组未来状态或位置点，必须明确坐标、horizon、采样间隔和单位。

## Future Trajectory

reference time 之后的自车目标或真值轨迹。

## Action

策略、规则、人工指定或模型生成的动作输出，用于影响环境的后续状态。可能是高层目标、轨迹、离散 token、连续控制等，含义取决于接口。当前 IDLE/SLOWER 来自脚本或规则，不需要先有神经网络。

## Control

直接作用于车辆执行层的命令，例如转向、制动和驱动。Trajectory 通常仍需控制器跟踪。

## VLM

Vision-Language Model。结合视觉和语言/语义进行理解或生成，不自动意味着能输出可执行驾驶动作。

## VLA

Vision-Language-Action Model。把视觉、语言/语义或其他状态条件连接到动作输出。驾驶 VLA 的 action 必须明确其时间、坐标、horizon 和执行方式。

## Behavior Cloning / Imitation Learning

从专家记录的状态—动作对学习策略。离线拟合好不代表闭环稳定。

## Open-Loop Evaluation

在已记录的输入上比较策略或模型输出，输出不会改变这份记录的后续输入。例如预测轨迹与真实标签的误差；仅打印一次状态不自动构成开放环评测。

## Closed-Loop Evaluation

把被评估策略的动作交给交互环境，再用变化后的观测继续决策并评价整段行为。当前跟车规则具有这种策略反馈；恒定动作实验只展示交互执行与控制响应，不能因环境在推进就声称策略已经会利用反馈驾驶。

## Pseudo-Simulation

介于纯开放环和完整交互仿真之间的数据驱动评价。具体定义以框架为准。

## Stale Observation

观测在被模型使用时已经过期。格式仍合法，但它描述的不是当前世界。

## Silent Failure

程序正常返回、格式合法，但任务语义错误，例如未来轨迹从过去开始。

## ODD

Operational Design Domain，系统预期有效的道路、天气、速度、区域和交通条件边界。

## Fallback

主策略不可用、超时、越界或不安全时切换的替代行为。

## Distillation

用 teacher 的输出、特征或行为监督 student。驾驶中必须检查 student 是否继承 teacher 错误，以及闭环行为是否保留。

## Quantization

降低权重或激活数值精度以换取速度、内存或能耗收益。平均精度接近不代表长尾驾驶行为不变。

## Reinforcement Learning

通过环境交互或轨迹反馈优化 policy。进入前必须定义 state、action、transition、reward、rollout、evaluator 和 safety boundary。

## World Model

学习环境状态如何随动作和时间演化的模型。可用于预测、仿真、数据生成或训练，但会受到 model bias 和 rollout drift 影响。
