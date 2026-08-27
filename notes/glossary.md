# Glossary

只记录本仓库实际用到、且容易混淆的术语。答案成熟后应回写到对应 lab；这里用于速查。

## Scene

一段连续驾驶过程或场景，不等于单帧图片。

## Sample

围绕某个 reference time 构造的一次模型输入与标签。

## History Window

reference time 之前提供给模型的观测序列。

## Future Trajectory

reference time 之后的自车目标/真值轨迹。必须明确：

- 坐标系；
- 时间间隔；
- horizon；
- 单位；
- 是否包含 yaw / speed。

## Ego State

自车在某个时间点的状态，例如位置、航向、速度。必须带时间戳。

## Waypoint

轨迹中的一个离散目标点。单个 waypoint 不等于完整 trajectory。

## Trajectory

按时间排序的一组未来状态或位置点。

## Control

直接作用于车辆执行层的命令，例如转向、制动或驱动。Trajectory 通常仍需控制器跟踪。

## Open-Loop Evaluation

模型输出不会改变后续输入的离线评价。

## Closed-Loop Evaluation

模型动作会改变环境和后续观测的评价。

## Pseudo-Simulation

介于纯开放环和完整交互闭环之间的数据驱动评价方法。具体定义以所用框架为准。

## ODD

Operational Design Domain，系统预期有效的道路、天气、速度、区域和交通条件边界。

## Silent Failure

程序正常返回、格式合法，但任务语义错误，例如未来轨迹从过去开始。
