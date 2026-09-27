# 05｜从状态表到相机：不能省略的中间几步

材料补充：2026-09-27。当前实践仍读其 [PROGRESS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md)。本篇交付几何小例子与迁移设计，不声称已经有真实相机数据管线、视觉网络或 VLA。

## 不是把 obs 换成图片就学会了视觉驾驶

当前 Kinematics 观察由模拟器提供运动学信息。实际相机给的是像素：对象可能被遮挡，距离和速度不是直接给出的表格字段。HighwayEnv 也有渲染图像观察，但模拟器的俯视渲染不是车载相机数据。观察类型依据 [Farama 官方文档](https://highway-env.farama.org/observations/)，读取于 2026-09-27；具体实践仍以自己的配置为准。

在整车链路中，这次迁移改变的是“传感器数据 → 空间/时序信息 → 规划输入或直接模型输出”的上游。下游轨迹、控制、反馈和评测依然需要明确。不能把模拟器真值偷偷喂给视觉策略，再称为模型从图像识别出了车辆状态。

| 数据角色 | 可以包含什么 | 不能发生什么 |
| --- | --- | --- |
| 模型输入 | 决策时实际可用的历史/当前图像、自车历史状态、允许的路线条件 | 未来图像、未来位姿、只有仿真器知道的对象真值悄悄进入 |
| 训练标签 | 明确来源的未来动作/轨迹、可合法使用的标注 | 未声明的参考坐标、不同动作层级混合，或把标签同时作为输入 |
| 诊断与评测 | 真值、控制器内部目标、碰撞状态等，明确标为诊断 | 因为日志里有这个字段，就默认策略也可以看到 |

## 相对位置不一定是自车坐标

当前状态表中的其他车辆位置相对自车平移，但坐标轴仍可能沿世界方向。把自车位置减掉，只移动了原点，没有把坐标轴随车转动。

本节自定义一个数学约定：平面世界坐标 x/y；自车局部 x 向前、y 向左；yaw 是从世界 x 轴逆时针转向自车 x 轴的弧度。世界点 p 转为自车坐标：

```text
q = R(-yaw) (p - ego_position)
qx = cos(yaw)*dx + sin(yaw)*dy
qy = -sin(yaw)*dx + cos(yaw)*dy
```

假设自车在 `(10,0)`，朝向正世界 y，即 yaw=π/2；物体在 `(10,5)`。世界相对量是 `(0,5)`，而自车坐标是 `(5,0)`，即正前方 5 米。这是合成数值例子，不是直接套用 HighwayEnv 的屏幕方向或任何数据集轴定义。

## 相机投影又多了哪一步

采用一个独立的理想针孔相机例子：相机 x 向右、y 向下、z 向前，点已经在相机坐标中，忽略畸变。投影为 `u=fx*X/Z+cx`、`v=fy*Y/Z+cy`。`(2,1,10)` 米，焦距均为 800 像素、主点 `(640,360)`，得到 `(800,440)` 像素。

此例没有给出 ego→camera 外参，所以不能把上一节的二维结果直接接入。真实数据必须先核对外参方向，再进行三维变换。正深度是这里的必要条件，投影落在图像内也不保证该点没被遮挡。

### 一个可以自己跑的小检查

将代码保存到临时目录中的 `geometry_check.py`，不是往理论库添加驾驶程序。VS Code 打开该临时目录后，用 Ctrl+P 找这个文件。Linux 可用 `/tmp/vla-curriculum-check`；Windows 可用 `$env:TEMP\vla-curriculum-check`，均先自行创建目录和文件。

```python
import math


def world_to_ego(point: tuple[float, float], origin: tuple[float, float],
                 yaw_rad: float) -> tuple[float, float]:
    if not all(math.isfinite(v) for v in (*point, *origin, yaw_rad)):
        raise ValueError("坐标和角度必须是有限数")
    dx, dy = point[0] - origin[0], point[1] - origin[1]
    c, s = math.cos(yaw_rad), math.sin(yaw_rad)
    return c * dx + s * dy, -s * dx + c * dy


def ego_to_world(point: tuple[float, float], origin: tuple[float, float],
                 yaw_rad: float) -> tuple[float, float]:
    if not all(math.isfinite(v) for v in (*point, *origin, yaw_rad)):
        raise ValueError("坐标和角度必须是有限数")
    c, s = math.cos(yaw_rad), math.sin(yaw_rad)
    return (c * point[0] - s * point[1] + origin[0],
            s * point[0] + c * point[1] + origin[1])


def project(point: tuple[float, float, float], fx: float, fy: float,
            cx: float, cy: float) -> tuple[float, float]:
    x, y, z = point
    if not all(math.isfinite(v) for v in (*point, fx, fy, cx, cy)):
        raise ValueError("投影参数必须是有限数")
    if z <= 0 or fx <= 0 or fy <= 0:
        raise ValueError("要求正深度与正焦距")
    return fx * x / z + cx, fy * y / z + cy


def close_pair(actual: tuple[float, float], expected: tuple[float, float]) -> None:
    if not all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(actual, expected)):
        raise AssertionError((actual, expected))


if __name__ == "__main__":
    p, origin, yaw = (10.0, 5.0), (10.0, 0.0), math.pi / 2
    local = world_to_ego(p, origin, yaw)
    close_pair(local, (5.0, 0.0))
    close_pair(ego_to_world(local, origin, yaw), p)
    close_pair(project((2.0, 1.0, 10.0), 800, 800, 640, 360), (800, 440))
    for z in (0.0, -1.0, math.nan):
        try:
            project((2.0, 1.0, z), 800, 800, 640, 360)
        except ValueError:
            pass
        else:
            raise AssertionError("未拒绝无效深度")
    print("geometry checks passed")
```

从保存目录运行 `python geometry_check.py`，预期输出 `geometry checks passed`。先把 yaw 改成 0 并预测结果，再改成 90 看检查为何失败；不能为了通过而跟着错误结果修改期望。也可改变点的深度，解释同一空间横向距离为何映射到不同像素偏移。

这个例子只覆盖有限范围的二维刚体变换、理想投影和几种坏输入，不处理畸变、图像边界、三维姿态、溢出或遮挡。正反变换都写错时也可能互相抵消，所以同时保留手算正例，不能只做 round-trip。

## 真实数据迁移：选定候选，不假装已经接通

首个真实相机数据候选为 nuScenes mini，用途限定为元数据、图像/标定/位姿对齐及小样本调试，不用于宣称泛化或量产能力。官方 [schema](https://github.com/nutonomy/nuscenes-devkit/blob/master/docs/schema_nuscenes.md)说明了 sample、sample_data、calibrated_sensor、ego_pose 等关联，读取于 2026-09-27。正式动手时必须固定数据版本、devkit commit、许可、下载方式和时间戳单位；不能只把浮动 master 当成已锁定环境。

建议按以下三个小阶段实现，**以下均为待建设的实践交付，不是本仓库已有脚本**：

| 小阶段 | 具体输入与输出 | 验证方式 |
| --- | --- | --- |
| 数据读通 | 合法数据中的一段 scene、单相机图像、该帧标定和位姿 → 一条带来源的样本记录 | 图像/元数据 token 对得上；核对坐标、单位、采集时间；可视化投影，不能只看 tensor shape |
| 标签与单帧基线 | 截止 t0 可用的图像/自车信息 → 固定时间间隔的未来 ego 轨迹标签 | 未来世界轨迹统一变到 t0 的自车参考系；留出整段 scene/log，不随机打散相邻帧 |
| 时序与评测 | 单帧基线上加入历史帧、路线条件 → 同一输出格式 | 比较单帧/历史/去条件；检查缺帧、错时和 ego-motion；重新说明评测环境的边界 |

未来轨迹标签可以由未来位姿生成，但未来位姿只能用于标签，不进入模型输入。历史帧对应不同采集时刻的位姿，不能直接把所有帧当成同一时刻。时间戳也要分采集、到达/可用和决策；训练数据有一帧不等于运行时那一刻已经能用。

### 拟定的数据接口

不是要求先造大框架，而是约定生产者与消费者说同一种话：

```text
sample identity: dataset_version, scene_id, sample_id, split, t0
inputs: images/history + capture_times + availability rule
        calibration/poses + ego_history + permitted route condition
labels: future_xy_in_ego_at_t0 + future_dt + valid_mask
outputs: predicted_xy_in_ego_at_t0 + future_dt + confidence/validity
metadata: units, axis conventions, image order, model/data/config revisions
```

这些字段是课程设计，不是声称某个上游数据集天然采用这个 schema。消费者必须拒绝缺单位、时序倒置、错误 shape 或混用坐标系；标签 mask 必须进入损失和指标，不能把缺失未来当成零轨迹。

## 资源和评测选择不能继续留成一句话

先在已有 CPU 环境处理一段元数据与少量图像，测磁盘、读入和峰值内存；再根据实际硬件选择图像分辨率、历史长度、batch 和小模型。GPU/显存未知，因此本轮不指定大模型大小、租用费用或保证训练时长，不让用户先下载全部数据再发现跑不动。

评测可以先做离线标签误差，再选择具体协议。NAVSIM 是一个候选参考，但本轮读取的 [官方 README](https://github.com/autonomousvision/navsim)明确 main 对应 v2，v1 在 v1.1 分支，v2 伪仿真不是顺序且交互的驾驶闭环。正式选用必须固定版本并如实描述其协议，不能写成“已完成实车式闭环”。另选交互模拟器时再核验传感器、动作、控制和资源，本轮没有实现这种集成。

只有当数据适配、标签、训练、推理与评测都实际连通，才把视觉阶段标为成套交付。当前交付的是跨越这道缺口的解释、接口设计和局部数学检查。返回 [路线](../ROADMAP.md)与 [讲义目录](README.md)。
