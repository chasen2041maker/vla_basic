# 01｜目标速度、实际速度与控制器

关联实践：[demo.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/demo.py) 的 target_speeds 配置、动作选择和两种速度打印。实际进度只看 [实践 PROGRESS.md](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md)。

本篇是备课与回查材料，不代表本轮已经给学习者讲完或完成理解核对。源码核对版本：highwayenv-learning `caeee8225d88f8092fbcf39a5ff02c59d35904ca`。

## 先看现象：说了“减速”，为什么车没有马上变慢到目标？

把三个东西分开：你的规则决定“发什么动作”；高层动作改变“希望车辆达到的目标”；底层控制器根据目标与实际的差距，计算怎样推动速度变化。它们不是同一个变量，也不是同一个职责。

当前程序的链路是：观察附近车 → 距离规则选动作 → env.step(action) → 动作对象和车辆控制器处理目标 → 仿真推进运动 → 返回新的观察与实际速度。

因此，发出 SLOWER 不等于把实际速度直接赋成一个更小的数，也不等于直接踩某个强度的刹车。IDLE 不改目标，也不表示停车；若实际速度仍未到达目标，控制器仍会继续追踪它。

## 为什么以前最低停在 72 km/h 附近？

该版本 MDPVehicle 的默认目标档位由 np.linspace(20, 30, 3) 得到，即 20、25、30 m/s。20 m/s×3.6＝72 km/h。选择更低的目标会受到最低档位限制，不是打印“减速”的次数不够。

当前 demo 已通过 DiscreteMetaAction 的 target_speeds 配置使用 0、5、10、15、20、25、30 m/s，对应 0、18、36、54、72、90、108 km/h。是否继续减速仍由当时的距离规则决定；扩大档位不保证在随机交通中一定停到零，更不保证避免碰撞。

依据：[当前练习的固定版本](https://github.com/chasen2041maker/highwayenv-learning/blob/caeee8225d88f8092fbcf39a5ff02c59d35904ca/demo.py)、[MDPVehicle](https://github.com/chasen2041maker/highwayenv-learning/blob/caeee8225d88f8092fbcf39a5ff02c59d35904ca/highway_env/vehicle/controller.py)。

## 一个容易被说错的源码细节

这个版本的速度动作逻辑可以摘成：

```python
# MDPVehicle.act 的相关局部，不是完整实现。
if action == "SLOWER":
    self.speed_index = self.speed_to_index(self.speed) - 1
# 后续会裁剪合法档位范围，再更新 target_speed。
```

这里用的是 self.speed，也就是实际速度，而不是简单地对上一次目标档位一直减一。因此不能保证每发一次 SLOWER，目标必定再下降 5 m/s；决策很快而车辆还没追上目标时，可能重复得到同一档位。要结合当次实际速度和档位映射解释。

speed_to_index 的实现假设档位均匀分布。当前等间隔列表符合该假设；不要随意换成不均匀档位后还以为映射规则不变。依据同上 controller.py 中 MDPVehicle.act 和 speed_to_index。

## 实际速度怎样向目标靠近？

ControlledVehicle.speed_control 的核心是：

```python
return self.KP_A * (target_speed - self.speed)
```

返回的是加速度指令，单位 m/s²。目标高于实际，误差为正；目标低于实际，误差为负。随后车辆模型经过时间推进才得到新的速度，不是瞬间赋值。

教学假设：某时刻目标为 54 km/h，即 15 m/s；实际为 57.6 km/h，即 16 m/s。误差是 -1 m/s，控制器会继续给出减速方向的指令。实际暂时高于目标并不矛盾。这里的数字是用于解释的假设，不是学习者本轮新提交的运行结果。

该代码是简化的比例速度控制示例，不是完整量产车辆的制动模型、舒适性限制或安全保证。依据：[ControlledVehicle.speed_control](https://github.com/chasen2041maker/highwayenv-learning/blob/caeee8225d88f8092fbcf39a5ff02c59d35904ca/highway_env/vehicle/controller.py)。

## 读日志时要分清什么

demo 中 info["speed"] 是 step 后的实际速率；env.unwrapped.vehicle.target_speed 是读取模拟器内部目标作为诊断。乘 3.6 只做单位换算，round 只影响显示精度。目标速度不在当前策略的输入表中，不得悄悄当作新的感知信息使用。

看到两种速度时，先确认它们属于哪个时刻、动作是什么、是否处于最低档位，再讨论控制器是否在追踪。不要把四舍五入到 0.0 当作严格数学等于零，也不要把低速或无碰撞的短片段当作安全证明。

## 与后续 VLA 学习的连接

这里先建立一个判断习惯：模型或规则输出的动作表示什么，谁将它变成运动，过多久才能看到效果。后续实践采用离散动作、轨迹点或连续控制量时，都要重新核对这个接口；现在的规则车没有因此变成 VLA。

回到 [实践进度](https://github.com/chasen2041maker/highwayenv-learning/blob/main/PROGRESS.md) 继续现有实验，不新建第二份低速练习。相关材料：[02 step 与反馈](02-step-and-feedback.md)、[对应表](../PRACTICE_MAP.md)。
