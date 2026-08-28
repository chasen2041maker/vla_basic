# Glossary

只记录本仓库实际使用且容易混淆的术语。成熟解释应回写对应 Lab；这里用于速查。

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

会影响系统未来状态的模型输出。可能是轨迹、离散 token、连续控制或其他表示，不能只写一个模糊的 `action`。

## Control

直接作用于车辆执行层的命令，例如转向、制动和驱动。Trajectory 通常仍需控制器跟踪。

## VLM

Vision-Language Model。结合视觉和语言/语义进行理解或生成，不自动意味着能输出可执行驾驶动作。

## VLA

Vision-Language-Action Model。把视觉、语言/语义或其他状态条件连接到动作输出。驾驶 VLA 的 action 必须明确其时间、坐标、horizon 和执行方式。

## Behavior Cloning / Imitation Learning

从专家记录的状态—动作对学习策略。离线拟合好不代表闭环稳定。

## Open-Loop Evaluation

模型输出不会改变后续输入的离线评价。

## Closed-Loop Evaluation

模型动作会改变环境和后续观测的评价。

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
