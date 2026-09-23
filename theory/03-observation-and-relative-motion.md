# 03｜观察表、相对运动与距离规则的边界

关联实践：[demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py) 的车辆筛选和 nearest_distance。实际进度以 [实践 PROGRESS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md) 为准，不因材料建立新增训练或变道任务。

源码依据：[caeee82 的 KinematicObservation](https://github.com/chasen2041maker/highwayenv-learning/blob/caeee8225d88f8092fbcf39a5ff02c59d35904ca/highway_env/envs/common/observation.py)、[固定版本 demo](https://github.com/chasen2041maker/highwayenv-learning/blob/caeee8225d88f8092fbcf39a5ff02c59d35904ca/demo.py)。

## 表格不是相机识别出来的结果

当前 observation 是模拟器提供的运动学表格。默认列是 presence、x、y、vx、vy，默认总共 5 行：自车加至多 4 个附近对象，数量不够时用零行补齐。窗口里有画面，不等于策略使用了图像。

presence=0 表示填充，不是一辆停在原点的真车。自车行来自自身世界状态；在当前 absolute=False 设置下，其他有效行的位置和速度相对于自车。相对量仍采用当前世界坐标轴含义，不能脱离道路方向理解正负号。

行号只是该次观察的排列，不是稳定车辆 ID。换一步后同一行可能已经换了一辆车；默认 see_behind=False，也不能拿这份有限表格证明后方或相邻车道安全。

## 为什么代码要乘 200 和 16？

当前默认观察会归一化：把配置的物理量范围映射到 -1 到 1，且默认会裁剪。当前实践记录中的 x×200、y×16 对应当时的默认范围和四车道配置，是对这份观察的换算，不是所有 HighwayEnv 数据的通用公式。

若归一化前的值已被裁剪，乘回范围也不能恢复丢失的真实幅度；若修改车道数、features_range 或关闭 normalize，也必须重新核对。源码的 normalize_obs 展示了范围生成和 clip 过程，实践的 [基准配置记录](https://github.com/chasen2041maker/highwayenv-learning/blob/caeee8225d88f8092fbcf39a5ff02c59d35904ca/PROGRESS.md) 说明了当前示例换算的前提。

旧 vla_basic runner 明确关闭归一化，位置已经以米表示，不能再次乘 200。遇到数值先问“原始量还是归一化量”，再进行距离判断。

## 相对速度解决什么问题？

教学假设：同样在前方 50 米，第一辆前车与你同速；第二辆前车比你慢 10 m/s。第一种当前距离没有因这两车的速度差而缩短；第二种在匀速直线假设下每秒缩短 10 米。

因此在忽略车长、加减速、换道和控制延迟的简化假设下，50 / 10 = 5 秒表示追近的时间尺度。它不是完整碰撞时间或保证安全的阈值，更不能直接当作刹车距离。

当前有效其他车辆行中的负相对 vx，在直线沿 x 方向的场景下表示前车的该方向速度低于自车。使用数值大小时先还原单位；不能把归一化值直接当 m/s。相对速度让你区分“距离相同但正在快速接近”和“距离相同且大致同速”。

## 当前距离规则知道什么，不知道什么？

demo 在可见行中用 presence、前方 x 和横向位置差筛选对象，然后找最小距离。当前实际执行的分支只根据小于 40、超过 60 或位于两者之间选择动作，没有使用速度差。

nearest_distance 初始为正无穷。如果观察里未找到同车道前车，它会保持为无穷并进入加速分支；这只表示“这次有限观察没有找到”，不表示整条路一定为空。横向差阈值也是当前直路上的简单筛选，不是通用车道关联或变道安全验证。

下一步是否加入相对速度或扩大观察由实践进度决定。本篇解释边界，不顺便代写新的策略，也不把已有几局无碰撞升级成可靠性结论。

## 向视觉与 VLA 延伸时保留这个习惯

先问输入究竟是什么、包含哪些对象、哪些信息被归一化或丢掉、动作依据的是当前还是旧状态。换成视觉模型后，这些契约仍需核对，但模型输入与验证方法需要重新设计；状态表练习不自动替代视觉学习。

返回 [讲义目录](README.md)、[理论—实践对应表](../PRACTICE_MAP.md)，实际操作继续 [实践仓库](https://github.com/chasen2041maker/highwayenv-learning)。
