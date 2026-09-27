# 智驾学习教材｜从一条指令到车辆行为

你已经做过 Python、AI 和后端项目，也开始跑过驾驶模拟器。我们接下来要补的是：程序得到的道路信息是什么意思，决定怎样开以后怎样真的执行，以及怎样判断一次修改有没有用。

这本书把当前阶段的讲解与相关代码放在同一页。先看具体问题，再看解释和代码；完整程序可以在需要实践时直接使用。源码文件路径留作可选出处，不需要开几个文件拼出一段意思。普通 Python 语法不重新讲一遍，驾驶里的新概念则从例子开始。

**当前从第 01 章开始。** 你已经说对了“目标速度是 20，实际 25 应该往下降”。本章接着解释谁计算减速、时间推进后哪个值改变，不再反复考同一道数字题。

## 本卷怎样读

| 章 | 围绕的问题 | 你会看到的代码与实验 |
| --- | --- | --- |
| [01 系统怎样让车动起来](#chapter-01) | 保存目标、计算控制、车辆运动分别发生在什么时候？ | 控制器和速度更新源码；完整无窗口调速实验 |
| [02 前车慢了，怎样作出反应](#chapter-02) | 表格中的哪辆车是前车，怎样根据它的距离选动作？ | 归一化、相对量、筛选与规则；现有跟车程序全文 |
| [03 一个变道指令怎样变成运动](#chapter-03) | 发一次变道之后，为什么保持动作还能继续转过去？ | 动作接口、控制与运动摘录；完整变道程序与连续动作补充 |
| [04 怎样知道修改有没有用](#chapter-04) | 一次没撞是策略变好，还是路况更容易？ | 时间日志、同条件对照、结束原因；完整小对照程序 |

先沿当前一章读，不需要今天把四章全运行。代码前会说明它是源码摘录、教学简化还是完整可运行程序；折叠内容是按需查阅的细节。

已有实验沿用本机 py310 环境。给出的数值会注明是手算、源码预期还是有记录的助手实验，你实际运行的结果另记。不同小实验有自己的时间频率和观察配置，切换时会在正文说明。

本卷完整覆盖当前已有实验的入门讲解与对照方法。后面的视觉、数据、轨迹模型、VLA 和部署仍属于同一个大项目，书末说明如何衔接；它们的实际训练工程尚未交付，不能把路线当作现成成果。

<details>
<summary>资料维护说明（不影响阅读）</summary>

本文件是唯一教材，直接在这里更新正文，不再维护分章副本。学习状态以 [PROGRESS.md](../PROGRESS.md) 为准，书写好不等于学习者已掌握。

</details>

---

<a id="chapter-01"></a>

## 第01章｜系统怎样让车动起来

你已经有 Python、AI 和后端经验。这一章从一个驾驶问题开始：**程序已经决定慢一点，为什么车速还需要逐渐变化？** 我们把“决定想要什么”和“让车实际变成那样”接起来，再看熟悉的 `env.reset()`、`env.step()` 包住了哪些工作。

本章的解释、相关代码和小实验都在这一页。HighwayEnv 提供道路、车辆和控制器，我们借它看清因果关系。没有相机或训练模型参与这次实验。

### 1.1 先有目标，再有实现目标的过程

想象你开车接近一个限速更低的路段。你决定降低车速，脚开始调整踏板，车辆随后逐渐慢下来。做出决定的那一刻，车速不会立刻跳到新的数值。

程序里也是如此。**实际速度**描述车此刻怎样运动，**目标速度**描述我们希望它达到什么状态。目标是一条要求，不是已经完成的结果。

在驾驶系统中，可以先认清这条短链：

```text
了解当前情况 → 决定目标 → 控制器计算调整量 → 车辆运动 → 得到新的当前情况
```

“控制器”是中间那段程序：它接收目标和当前状态，计算如何调整。在本章里，“决定目标”只是我们手动指定一个速度；“当前情况”直接来自模拟器；后两段则由模拟器里的控制器和运动模型完成。以后用模型输出目标，后面的执行过程仍然存在。

可以把保存目标类比为后端保存了一条待执行要求。但真实车辆的运动不能回滚：即使程序稍后发现目标不合适，车辆已经走过的距离也不会消失。这就是为什么我们始终要区分**刚设置目标、刚计算指令、已经运动之后**。

### 1.2 控制器把速度差变成加速度

车知道“需要慢下来”，还不够；运动模型需要知道接下来按多大的加速度改变速度。这里的加速度单位是 m/s²：持续 1 秒时，速度改变多少 m/s。负加速度表示速度朝减小的方向变化。

下面是本机 HighwayEnv 的 `ControlledVehicle.speed_control()` 完整方法。它是类里的源码摘录，需要车辆对象，不是独立运行的脚本。

```python
def speed_control(self, target_speed: float) -> float:
    """
    通过简单的比例控制器控制车速。

    :param target_speed: 期望速度
    :return: 加速度指令，单位为 m/s²
    """
    return self.KP_A * (target_speed - self.speed)
```

这个方法只做一件事：把“目标速度减实际速度”乘以系数，返回加速度。目标比实际低，返回负值；实际越接近目标，差越小，调整也越轻。这种按差值大小调整的方式叫**比例控制**，先理解这个意思即可。

本机实现中 `TAU_ACC = 0.6` 秒，`KP_A = 1 / TAU_ACC`，即约 1.667 每秒。举一个手算例子：实际速度为 18 m/s，目标为 15 m/s，差值为 −3 m/s，算出的加速度就是 −5 m/s²。

**算出 −5，不等于速度已经减少了 5。** 方法返回了一个数；它没有更新位置、速度，也没有让仿真时间流逝。真实汽车还需要把控制要求交给执行器；本模拟器将加速度交给简化的车辆运动模型，不模拟一整套动力与制动硬件。

### 1.3 时间推进以后，实际状态才改变

接下来需要让车辆运动一小段时间。对于速度，本机 `Vehicle.step()` 中真正更新它的语句是：

```python
self.speed += self.action["acceleration"] * dt
```

这是实际源码的一行，`dt` 是这次运动更新经历的秒数。完整方法在本节末尾展开，所有相关代码都留在本页。

沿用刚才的手算例子，如果这一小步长为 1/15 秒，速度变化就是 −5 × 1/15 ≈ −0.333 m/s。更新后的速度约为 17.667 m/s。控制器下次读取这个新速度，会重新计算调整量，而不是永远使用第一次的 −5。

车辆同时也在移动。本实现先使用更新前的速度推进这一小步的位置，再更新速度。对于不转弯的直路，第一小步前进约 18 × 1/15 = 1.2 米。上述数字是根据源码手算的例子，不是下面实验的实测输出；也没有假定加速度整段时间都不变。

因此，减速中的车继续前进完全正常。目标改变、速度变化、位置变化是不同的量；它们由同一条执行链联系起来，而不是一起被赋成目标值。

<details>
<summary>完整源码参考：Vehicle.step() 怎样更新位置、朝向和速度</summary>

下面是本机方法的完整摘录。转向几何留给后面的转弯内容；当前直路实验转向为零，只需把速度更新与时间对应起来。

```python
def step(self, dt: float) -> None:
    """
    根据动作推进车辆状态。

    使用修正的自行车模型积分，更新位置、朝向和速度。
    碰撞后，clip_actions 将转向设为 0，并制动至停车。
    同时更新车辆当前所在车道。

    :param dt: 模型积分的时间步长，单位为秒
    """
    self.clip_actions()
    delta_f = self.action["steering"]
    beta = np.arctan(1 / 2 * np.tan(delta_f))
    v = self.speed * np.array(
        [np.cos(self.heading + beta), np.sin(self.heading + beta)]
    )
    self.position += v * dt
    if self.impact is not None:
        self.position += self.impact
        self.crashed = True
        self.impact = None
    self.heading += self.speed * np.sin(beta) / (self.LENGTH / 2) * dt
    self.speed += self.action["acceleration"] * dt
    self.on_state_update()
```

`position` 是世界坐标中的位置，单位米；`heading` 是相对世界坐标轴的朝向，单位弧度；`speed` 是车辆沿自身行驶方向的标量速度，单位 m/s。这些内部状态没有归一化。只有当前保持沿世界 x 方向直行时，才可以直接把这个速度用于计算 x 方向位移。

</details>

### 1.4 `env.step()` 把控制和运动接起来

你以前运行的实验，通常只写一行 `env.step(action)`，没有手动反复调用控制器。原因是环境替你组织了这些调用。

`env.reset(seed=0)` 建立本回合道路和车辆，返回初始观察。`env.step(action)` 接收本次动作，让控制器计算、车辆运动，然后返回下一观察。最外层循环看到的一步，内部可以包含多次更短的运动更新。

本章明确设置物理更新频率为 15 Hz、外层决策频率为 5 Hz。因此，正常一次 `env.step()` 包含 3 个 1/15 秒的小步，总共推进 0.2 秒模拟时间。这里是本章的配置，不能套到使用 1 Hz 决策的旧 demos 上。

下面两行是本机 `AbstractEnv._simulate()` 在每个物理小步内实际执行的相邻源码：

```python
self.road.act()
self.road.step(1 / self.config["simulation_frequency"])
```

第一行让道路上的车辆计算控制，第二行让它们按这些控制推进运动。控制器在小步之间能读到更新后的实际速度。因此，**即使外层一直发 `IDLE`，控制器也不是停止工作**：它仍在根据实际速度追踪已有目标。

这里要分清两种“使用反馈”。控制器用实际速度修正加速度，是控制层反馈；驾驶策略根据前车、车道等情况重新选择目标，是决策层反馈。本章只演示前一种，没有前车，也没有会自主跟车的策略。

### 1.5 完整小实验：分别看三个时间点

这个实验只改变目标速度，然后继续发 `IDLE`。道路上没有其他车辆，固定 seed，不打开窗口；打印内部状态是为了诊断执行链，不是假装获得了相机感知结果。

先读代码里的三个标签：`target_saved` 是只保存了目标，`control_computed` 是只计算了加速度，`after_step` 才是环境推进之后。运行前，可以先想一下前两个标签的时间和实际速度是否应该变化；不需要另答一轮速度大小题。

下面是**完整可运行块**：在本项目的 PowerShell 终端整体粘贴即可，Python 通过标准输入执行，不创建 `.py` 文件，不需要激活环境。使用本机已有的 `D:\miniconda\envs\py310\python.exe`。

```powershell
@'
import gymnasium as gym
import highway_env

env = gym.make(
    "highway-v0",
    render_mode=None,
    config={
        "lanes_count": 3,
        "vehicles_count": 0,
        "initial_lane_id": 1,
        "duration": 2,
        "simulation_frequency": 15,
        "policy_frequency": 5,
        "action": {"type": "DiscreteMetaAction"},
        "observation": {
            "type": "Kinematics",
            "vehicles_count": 1,
            "features": ["presence", "x", "y", "vx", "vy"],
            "absolute": True,
            "normalize": False,
            "clip": False,
        },
    },
)

try:
    obs, info = env.reset(seed=0)
    vehicle = env.unwrapped.vehicle
    idle = env.unwrapped.action_type.actions_indexes["IDLE"]
    print("HighwayEnv source:", highway_env.__file__)
    print("stage                t_s  speed_mps target_mps x_world_m y_world_m")

    def show(stage):
        print(
            f"{stage:20s} {env.unwrapped.time:4.2f} "
            f"{vehicle.speed:9.4f} {vehicle.target_speed:10.4f} "
            f"{vehicle.position[0]:9.4f} {vehicle.position[1]:9.4f}"
        )

    show("reset")
    # 只为诊断直接设置目标；没有改写实际速度。
    vehicle.target_speed = float(vehicle.speed) - 3.0  # 单位 m/s
    show("target_saved")

    # 此函数只返回加速度，不保存控制、不推进运动。
    acceleration_mps2 = vehicle.speed_control(vehicle.target_speed)
    print(f"computed acceleration: {acceleration_mps2:.4f} m/s^2")
    show("control_computed")

    for index in range(1, 6):
        obs, reward, terminated, truncated, info = env.step(idle)
        show(f"after_step_{index}")
        if terminated or truncated:
            print("environment ended:", terminated, truncated)
            break
finally:
    env.close()
'@ | & 'D:\miniconda\envs\py310\python.exe' -
```

打印的 `t_s` 是模拟时间，不是代码运行的墙钟耗时；`speed_mps` 是当时的实际速度，`target_mps` 是当时保存的目标；`x_world_m`、`y_world_m` 是世界绝对位置，单位米，均未归一化。这里没有其他车辆，不涉及相对坐标；观察配置也明确使用了绝对量。

这段代码故意通过内部属性直接设目标，以便单独看到“赋值”和“运动”的区别。它不是一般驾驶策略的动作接口。实际送给 `env.step()` 的 `IDLE` 仍是高层动作，不是加速度、油门百分比或轨迹。

<details>
<summary>为何 IDLE 不会把刚设置的目标改回去？</summary>

本机 `MDPVehicle.act()` 的完整方法如下。只有 `FASTER`、`SLOWER` 分支会重新选择速度档位。`IDLE` 和道路自动调用时的 `None` 都进入 `else`，交给父类控制器后返回；父类在这两种情况下保留已有目标。

```python
def act(self, action: Union[dict, str] = None) -> None:
    """
    执行高层动作。

    - 若动作为速度调整，则从允许的离散速度档位中选择目标速度；
    - 否则将动作交给 ControlledVehicle 处理。

    :param action: 高层动作
    """
    if action == "FASTER":
        self.speed_index = self.speed_to_index(self.speed) + 1
    elif action == "SLOWER":
        self.speed_index = self.speed_to_index(self.speed) - 1
    else:
        super().act(action)
        return
    self.speed_index = int(
        np.clip(self.speed_index, 0, self.target_speeds.size - 1)
    )
    self.target_speed = self.index_to_speed(self.speed_index)
    super().act()
```

正常高层调速经过离散档位选择；本实验的直接赋值绕过了它，只用于诊断，不应推广成策略写内部状态的做法。

</details>

### 1.6 怎样阅读你实际得到的输出

先把 `reset` 与 `target_saved` 两行并排看：目标列发生改变，时间、实际速度和位置应保持原值。再看 `control_computed`：屏幕已经出现加速度计算结果，但运动状态仍未推进。这两处把“保存要求”和“算出调整”从实际执行中拆开了。

接着沿着 `after_step_1` 往下读：时间每次增加 0.2 秒，速度逐渐接近目标，x 位置继续增加。目标列应该保持不变；控制器在这个固定目标下，根据不断更新的实际速度计算调整。如果输出与这条关系不符，先比较实际打印的时间、目标与 `HighwayEnv source`，不要用预期数字盖过真实结果。

这些是依据当前源码和配置的预期读法，不是已经收到的个人实验结果。没有必要把五行都背下来；更有用的是能指着相邻两行解释：这一段时间里，哪个量只是要求，哪个量是已经发生的变化。

这次看到的是有反馈的控制与模拟运动，不是离线预测轨迹对标注的误差，也没有计算完整驾驶成绩。循环虽然接收 `obs`，却没有用它决定下一次目标；奖励也没有用于学习。无其他车辆的一秒调速实验只能说明这条执行链怎样工作，不能说明会跟车、会避碰或具备真实道路安全性。

此时再读 `env.step(action)`，它就不只是“执行一步”的接口了：动作交给控制器，控制器与车辆运动交替执行一段时间，然后你拿到已变化世界的下一次观察。

<details>
<summary>可选出处：本章对应的本机源码与既有实验</summary>

正文已包含当前解释所需代码。下面路径仅供追溯版本和继续研究，不影响本章独立阅读。

- `C:\Users\Administrator\Desktop\职业生涯项目\HighwayEnv\highway_env\vehicle\controller.py`：`ControlledVehicle.speed_control()`、`ControlledVehicle.act()`、`MDPVehicle.act()`。
- `C:\Users\Administrator\Desktop\职业生涯项目\HighwayEnv\highway_env\vehicle\kinematics.py`：`Vehicle.step()`。
- `C:\Users\Administrator\Desktop\职业生涯项目\HighwayEnv\highway_env\envs\common\abstract.py`：`AbstractEnv.step()`、`AbstractEnv._simulate()`。
- `C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\01_lane_change.py`：`main()`；同样可以观察目标车道与实际位置先后变化，当前不要求补跑。
- `C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\03_continuous_action.py`：已有连续动作练习；它使用不同动作接口与时间配置，不与本章输出混读。

</details>


---

<a id="chapter-02"></a>

## 第02章 前车慢了，我们怎样作出反应

你已经运行过跟车实验，也已经解释过“前车距离为 50 米时保持目标速度”。这一章把你做过的事情连成一段完整的讲解，方便连续阅读和回头复习，不要求重新提交已经答过的题。

正文会当场列出理解所需的代码，章末收录主项目已有跟车脚本的完整内容；你可以先连续阅读，需要动手时再按章内命令运行。

### 2.1 先想一件开车时会遇到的事

我们以 25 m/s 行驶，前面同一条车道有一辆车，距离我们 35 米。程序准备发出减速请求。这个决定至少需要回答两件事：那辆车是不是在我们前面？它是不是占着我们要走的这条道？隔壁车道的一辆车即使只有 20 米远，也不能直接当作当前跟车对象。

本章的程序做了下面这件事：

```text
模拟器给出附近车辆的表格
→ 从表格里找出同车道最近的前车
→ 根据距离选择减速、保持或加速
→ 模拟器让车辆运动一段时间
→ 用新的表格再次判断
```

我们负责中间的“找车和选动作”。HighwayEnv 提供道路、车辆状态、底层控制器和运动更新。这里没有相机识别：表格直接来自模拟器内部的车辆状态。以后从图像中识别周围车辆，才会补上当前被模拟器代办的那部分工作。

### 2.2 观察是一张表：先分清哪一行是什么

程序通过这一行拿到初始表格。这是原脚本摘录，需要前面已经创建好 `env`：

```python
obs, info = env.reset()
```

`obs` 默认有 5 行、5 列。每行的列顺序固定为：

```text
[presence, x, y, vx, vy]
```

先暂时用已经还原成米、米/秒的教学数值理解它，下一节再解释原始表格里的小数。

| 行 | `presence` | 这一行表示什么 | 能否作为本次跟车对象 |
| --- | --- | --- | --- |
| 第 0 行 | 1 | 自己的车 | 跳过，我们是在找其他车 |
| 第 1 行 | 1 | 比自车靠前 35 米，横向差 0 米 | 可以，是一个前车候选 |
| 第 2 行 | 1 | 比自车靠前 20 米，横向差 4 米 | 在旁边的车道，当前规则不选它 |
| 第 3 行 | 1 | 比自车靠前 70 米，横向差 0 米 | 可以，但比第 1 行更远 |
| 第 4 行 | 0 | 空槽，没有对应车辆 | 跳过 |

`presence=1` 表示这一行有对象；`presence=0` 表示填充行。空槽中的零，不是在说“原点停着一辆速度为零的车”。这份高速公路实验没有添加其他障碍物，所以这里按车辆来读。

原脚本检查的是 `obs[1:]`，正是为了跳过自己。变量 `presense` 是原练习中的拼写；它接住第一列，与列名 `presence` 指的是同一件事，本章保留原拼写。

把“是同车道前车”写成当前实验的条件，是下面这段摘录：

```python
if presense == 1 and distance > 0 and abs(side_distance) < 2:
    nearest_distance = min(nearest_distance,distance)
```

这里的 `distance` 是车辆中心沿道路前进方向的位置差，`side_distance` 是车辆中心的横向位置差。默认直路沿世界 x 轴延伸，车道宽 4 米，所以先用“横向差小于 2 米”筛选与自车大致对齐的车辆。

这只是本实验的简化判断，不是真正查询双方的车道编号。车辆正在跨车道、接近车道边缘或道路转弯时，这个条件可能误判。这里的距离也不是两车保险杠之间的净空，尚未扣掉车长。

### 2.3 为什么代码要乘 200 和 16

假设表格中一辆其他车的 `x` 是 `0.175`，它表示前方 35 米，而不是前方 0.175 米。当前默认观察把原来的物理量缩放后再交给程序：35 除以 200，得到 0.175。这一步叫**归一化**。

原脚本在这里把数值换回物理单位：

```python
distance = x * 200
side_distance = y * 16
```

为什么正好是这两个数？当前本地 HighwayEnv 的默认实现规定：x 的范围是 `[-5 * MAX_SPEED, 5 * MAX_SPEED]`，`MAX_SPEED` 为 40；y 的范围是正负“默认车道宽 × 同一路段的车道数”，当前是 `4 × 4`。因此得到：

| 字段 | 归一化使用的物理范围 | 未被裁剪时的还原 |
| --- | --- | --- |
| `x` | -200 到 200 米 | `x * 200` |
| `y` | -16 到 16 米 | `y * 16` |
| `vx`、`vy` | -80 到 80 米/秒 | 对应数值 `* 80` |

实现会把这些范围线性映射到 `[-1, 1]`。这些是**缩放范围**，不是“自车一定能看见前后 200 米”的承诺，也不是把速度允许范围设成了 ±80 m/s。

还需要知道一次信息损失。默认 `clip=True`：超过范围的数会停在端点。例如一个待归一化的 x 数值为 260 米，先得到 1.3，随后被裁剪成 1。再乘 200 只能得到 200，不能找回原来的 260。因而看到 `x=1`，只能知道原始量达到或超过这一范围的上端；不能断言原始量恰好为 200 米。

这也解释了这些乘法的限制：**配置匹配且没有被裁剪，才能还原原数值。** 改成三车道后 y 的默认范围会变成 ±12 米；若关闭归一化，观察本来已经是米，再乘 200 就会把距离放大 200 倍。其他实验也可能显式指定不同的范围，不能把这两个常数当作所有 HighwayEnv 代码的通用公式。

下面是一个完整、可单独执行的纯数学小例子，不创建环境，不产生驾驶结果：

```python
for physical_x_m in (35.0, 200.0, 260.0):
    normalized_x = physical_x_m / 200.0
    clipped_x = max(-1.0, min(1.0, normalized_x))
    restored_x_m = clipped_x * 200.0
    print(physical_x_m, "→", clipped_x, "→", restored_x_m)
```

按算式得到的三行是 `35 → 0.175 → 35`、`200 → 1 → 200`、`260 → 1 → 200`。最后一行展示的是裁剪造成的信息丢失，不是模拟器实测输出。

### 2.4 “相对”只做减法，坐标轴没有跟着车转

再用一组具体数值：自车世界位置是 `(100, 4)` 米，另一辆车世界位置是 `(135, 4)` 米。后者减去自车，得到 `(35, 0)` 米：沿世界 x 方向相差 35 米，沿世界 y 方向没有差。

默认 `absolute=False` 时，其他车辆的四个量按下面的关系生成。这是说明关系的教学简化，不是可直接运行的独立片段：

```python
relative_x = other_world_x - ego_world_x
relative_y = other_world_y - ego_world_y
relative_vx = other_world_vx - ego_world_vx
relative_vy = other_world_vy - ego_world_vy
```

随后才对这些结果归一化、裁剪。因此另一辆车若沿世界 x 方向以 20 m/s 行驶，而自车为 25 m/s，速度差就是 `-5 m/s`，表格中的 `vx` 会是 `-5 / 80 = -0.0625`。负号说明对方在这个方向比我们慢，不能直接理解成它在倒车。

第 0 行有一个必须单独记住的区别：它来自自车的**世界绝对位置和速度**，然后同样经过归一化、裁剪。其他有效行才来自“对方减自车”。所以第 0 行不会因为 `absolute=False` 就全变成零；它的世界 x 位置超过 200 米后，也可能被裁剪为 1。

“相对”在这里是相减，没有把坐标轴旋转到自车朝向。现在道路恰好沿世界 x 方向，才方便把正 x 读成前方。换到弯路或车头明显偏转时，世界 x 方向不再总是车辆正前方，原来的 `distance > 0` 也就不能直接沿用。

### 2.5 从几辆候选车里找最近的一辆

现在可以完整读懂找车这段代码了。下面是原脚本当前生效的摘录，运行时需要 `obs` 已由 `reset()` 或上一轮 `step()` 得到：

```python
# 先当作没有观察到同车道前车
nearest_distance = float('inf')

# 找到观察范围内，同车道最近的前车
for presense, x, y, vx, vy in obs[1:]:
    distance = x * 200
    side_distance = y * 16

    if presense == 1 and distance > 0 and abs(side_distance) < 2:
        nearest_distance = min(nearest_distance,distance)
```

代入前面的例子：35 米符合条件，先记下 35；20 米那辆横向差为 4 米，忽略；70 米符合条件，但 `min(35, 70)` 仍然是 35；空槽也忽略。最后留下的是 35 米。

`float('inf')` 的意思是“还没选中任何前车”，不是测到了一辆无限远的车。没有行满足条件时，这个值会一直保留到后面的动作选择。

还要限定“最近”指的是哪一批车。当前观察只有 5 行，其中一行是自车，最多另外 4 行有其他对象；默认场景却有 50 辆其他车。程序找到的是**已经进入这张有限表格、又符合筛选条件的最近前车**，不保证是整个道路上真正最近的同车道前车。默认排序也不让行号成为稳定车辆 ID，下一轮第 1 行未必还是同一辆车。

### 2.6 40 米和 60 米怎样变成一个动作

原脚本的规则如下。这是接在找车代码后的原文摘录：

```python
if nearest_distance < 40:
    action = 4
    decision = "前车太近，减速"

elif nearest_distance > 60:
    action = 3
    decision = "前方距离充足，加速"

else:
    action = 1
    decision = "保持当前目标速度"
```

于是 35 米对应减速，50 米对应保持，70 米对应加速。正好 40 米或 60 米也落在保持区间。这两个阈值是当前练习采用的规则，没有从车辆制动能力推导出“40 米一定安全”。

数字动作来自当前 `DiscreteMetaAction` 同时启用纵向和横向动作时的映射：

| `action` | 名称 | 本章怎样理解 |
| --- | --- | --- |
| `4` | `SLOWER` | 请求较低的目标速度档位 |
| `3` | `FASTER` | 请求较高的目标速度档位 |
| `1` | `IDLE` | 保持现有目标 |

这几个整数不是速度，也不是制动力。原脚本把目标速度档位配置成了下面的列表，单位为 m/s：

```python
"target_speeds": [0, 5, 10, 15, 20, 25, 30]
```

这一行是配置字典的摘录，完整创建环境的代码在章末。在当前实现中，调速动作先根据**实际速度**找最近档位，再请求相邻较慢或较快的档位，并限制在列表内。例如实际为 25 m/s 时，`SLOWER` 会请求 20 m/s。随后由控制器产生减速作用，实际速度随时间变化；收到 `4` 的瞬间不会直接把车速改成 20。

保持的是目标，也不意味着实际速度冻结。如果上一轮目标已降到 20，而实际还在 22，下一轮选择 `IDLE`，控制器仍会继续让车靠近目标。你已经说出的“目标 20，实际 25 应该往下降”就是这一方向关系。

现在回看 `inf`：它大于 60，所以没有选中前车时，这段程序也会打印“前方距离充足，加速”。**这是规则做出的选择，不是观察已经证明了前方安全。** 看懂这处差别，才能在出错时找到真正需要改的地方。

标题说“前车慢了”，但当前生效代码并没有比较 `vx`。它只能发现距离已变近，不能直接判断距离将以多快的速度缩短。章末脚本还保留着一段带 `vx < 0` 的旧方案，但它被三引号包住，不参与运行；不能把那段当成当前规则。

### 2.7 一次打印中的距离和速度，不是同一时刻

原脚本把距离打印在 `step()` 之前，把速度打印在它之后。相关代码在这里一次列全：

```python
print("本轮判断用的前车距离：", round(nearest_distance, 1), "米")
print(decision)

obs, reward, terminated, truncated, info = env.step(action)
print("当前速度：", round(info["speed"] * 3.6, 1), "公里/小时")
print("目标速度：", env.unwrapped.vehicle.target_speed * 3.6, "公里/小时")
total_reward += reward
```

假设这一轮开始时是第 7 秒，判断用的距离为 35 米。程序选择减速，调用 `step()`，道路上的车继续运动，随后打印第 8 秒的实际速度和此时保存的目标速度。顺序是：

```text
第 7 秒的 obs → 找到 35 米 → 选择 SLOWER
                    ↓
           env.step(action) 推进环境
                    ↓
第 8 秒的新 obs、实际速度、奖励和结束信号
                    ↓
下一轮使用这个新的 obs 重新找前车
```

这是用于解释时序的假设例子，不是新运行记录。本脚本采用本地默认的 `policy_frequency=1` 和 `simulation_frequency=15`：一次正常 `step()` 推进 1 秒模拟时间，其中有 15 次物理更新。这与旧 `run_episode.py` 的 5 Hz、每步 0.2 秒不同，不能混用。

打印时乘 `3.6` 只是把米/秒换成公里/小时。距离仍以米显示。若看到连续几行“35 米、减速、80 公里/小时”，不能把它们都当作动作前的同一帧，也不能据此认定“35 米时原本就是 80 公里/小时”。

这次程序确实使用了反馈：新 `obs` 会影响下一轮找车和动作选择。一次动作改变车辆位置后，后面的输入也会改变。这就是本章所说的交互闭环；它与在固定日志上只做预测比较不同，也还没有涉及强化学习。

### 2.8 只改一个阈值，先看规则变了哪里

如果想继续做一个小实验，可以只把原脚本的减速阈值从 40 改成 50，其他条件先不动：

```python
# 教学修改片段：替换原来 if nearest_distance < 40 这一行。
if nearest_distance < 50:
```

先不用猜整个回合的奖励。拿同一份“前车距离 45 米”的输入比较，就能说清一个确定变化：原规则选择保持，新规则选择减速。保持区间从 `[40, 60]` 变成 `[50, 60]`；正好 50 米仍保持，因为条件使用 `<`。这只能预测规则在相同输入下的输出，不能直接预测整局一定更安全。

下面是一个完整、可单独执行的纯逻辑对照，复述原规则但不启动模拟器：

```python
def choose_action(distance_m, slow_below_m):
    if distance_m < slow_below_m:
        return "SLOWER"
    elif distance_m > 60:
        return "FASTER"
    else:
        return "IDLE"

for distance_m in (35, 45, 50, 60, 70, float("inf")):
    old_action = choose_action(distance_m, 40)
    new_action = choose_action(distance_m, 50)
    print(distance_m, old_action, "→", new_action)

assert choose_action(45, 40) == "IDLE"
assert choose_action(45, 50) == "SLOWER"
assert choose_action(float("inf"), 50) == "FASTER"
```

注意最后一条：调阈值没有解决“未观察到前车就加速”的问题，也没有让规则开始考虑速度差。

需要看车辆实际反应时，在主项目根目录的 PowerShell 中使用现有环境运行：

```powershell
& 'D:\miniconda\envs\py310\python.exe' .\experiments\highway_driving\demos\00_following.py
```

脚本会打开窗口，按 `Ctrl+C` 可以结束。这份代码没有固定随机种子，两次运行会遇到不同场景。因此先用上面的相同输入对照确认规则变化，再把窗口中的运行当作寻找现象和失败的机会；不能把两个随机回合的总奖励直接当作阈值改进证据。本章没有要求重装已有环境，也没有替你宣称已运行这个改动。

### 2.9 出现失败时，回到它作决定的那一刻

为什么只看距离还不够？设两辆前车都在 50 米处：一辆与我们同速，另一辆比我们慢 10 m/s。当前规则对两种情况都会保持目标。可是在速度暂时不变的简化条件下，第二种情况经过 1 秒就会少 10 米距离，第一种不会。规则丢掉了这个差别，也没有考虑控制器减速需要时间。

所以，若看到车接近前车甚至碰撞，先对着输出追踪一小段因果：动作前选择了多大距离？规则因此选择了什么？动作后的目标是否已经降低？实际速度是否还在逐渐下降？若输出曾是 `inf`，还要回到有限观察和同车道筛选，不能直接断言“前面根本没有车”。原脚本只打印部分数据，有些细节仍无法仅凭这些输出确认；不要替日志补造答案。

运行期间，`reward` 是模拟器给这一段交互的评分，`total_reward` 把它累计起来。默认奖励同时考虑行驶速度、靠右和碰撞等因素，分数不是简单的“安全程度”。这些值来自执行动作后的模拟交互，不是固定数据上的开放环预测误差。

当前默认环境一局最长 40 秒，碰撞也会结束。脚本结束一局后会打印成绩、清零累计奖励，并调用 `reset()` 开新一局。不过外层只有总共 300 次 `step()` 的预算，预算用完时可能正好处于某一局中途；那一段不会自动补成完整的 40 秒成绩。也不能因为窗口正常关闭，就把未结束的一局算作完成。

这一章把已有规则接成了完整链条：观察中的相对位置，经筛选得到距离；距离决定高层目标请求；环境推进后才得到新的速度与观察。第一章讲过目标速度怎样逐渐实现，下一章把这条执行链扩展到横向运动：一个变道请求怎样让车实际转过去？

### 2.10 完整实验代码与可选来源

以下代码完整收录当前 `00_following.py`，可以在现有 HighwayEnv 环境中运行。保留原有变量拼写、注释和未启用片段，不把它偷偷替换成改良版；三引号内的旧判断和旧重启方案不参与执行。正文中的摘录用于讲解，这一块才是完整驾驶程序。

可选核对来源：本项目的 [00_following.py](../experiments/highway_driving/demos/00_following.py)，以及同级模拟器的 [observation.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/envs/common/observation.py)、[kinematics.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/vehicle/kinematics.py)、[action.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/envs/common/action.py)、[controller.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/vehicle/controller.py)、[abstract.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/envs/common/abstract.py) 和 [highway_env.py](https://github.com/chasen2041maker/highwayenv-learning/blob/main/highway_env/envs/highway_env.py)。正文已包含本章所需解释，这些链接用于进一步核对实现；同级来源链接依赖当前目录布局。

```python
import gymnasium as gym
import highway_env

# 创建高速公路场景，并显示窗口
#env = gym.make("highway-v0", render_mode="human")

env = gym.make(
    "highway-v0",
    render_mode="human",
    config={
        "action": {
            "type": "DiscreteMetaAction",
            "target_speeds": [0, 5, 10, 15, 20, 25, 30],
        }
    },
)

try:
    # 初始化车辆和道路
    obs, info = env.reset()
    episode = 1  # 当前是第几局
    total_reward = 0   # 这一局的累计得分

    for _ in range(300):
        """
        # 随机选择驾驶动作
        action = 1

        # 逐辆检查附近的车，跳过第一行自己的车
        for presense, x, y, vx, vy in obs[1:]:
            distance = x * 200
            side_distance = y * 16

            if (presense == 1 
                and 0 < distance < 40
                and abs(side_distance) < 2
                and vx < 0):
                action = 4
                print("发现同车道出现慢车，发出减速指令！")
                break
        """

        # 先当作没有观察到同车道前车
        nearest_distance = float('inf')

        # 找到观察范围内，同车道最近的前车
        for presense, x, y, vx, vy in obs[1:]:
            distance = x * 200
            side_distance = y * 16

            if presense == 1 and distance > 0 and abs(side_distance) < 2:
                nearest_distance = min(nearest_distance,distance)

        # 根据最近前车的距离，选择动作
        if nearest_distance < 40:
            action = 4
            decision = "前车太近，减速"

        elif nearest_distance > 60:
            action = 3
            decision = "前方距离充足，加速"

        else:
            action = 1
            decision = "保持当前目标速度"

        print("本轮判断用的前车距离：", round(nearest_distance, 1), "米")
        print(decision)



        # 让车辆执行动作
        obs, reward, terminated, truncated, info = env.step(action)
        print("当前速度：", round(info["speed"] * 3.6, 1), "公里/小时")
        print("目标速度：", env.unwrapped.vehicle.target_speed * 3.6, "公里/小时")
        total_reward += reward

        """"
        # 碰撞或时间到了，就重新开始
        if terminated or truncated:
            obs, info = env.reset()
            print("车辆观察数据：\n", obs)
        """

        if terminated or truncated:
            print("\n========== 本局成绩 ==========")
            print("第", episode, "局")

            if info["crashed"]:
                print("结果：发生碰撞")
            else:
                print("结果：到达本局时间上限")

            print("本局仿真时间：", round(env.unwrapped.time, 1), "秒")
            print("累计奖励：", round(total_reward, 2))
            print("==============================\n")

            # 准备下一局
            episode += 1
            total_reward = 0
            obs, info = env.reset()

except KeyboardInterrupt:
    pass
finally:
    env.close()
```


---

<a id="chapter-03"></a>

## 第03章｜一个变道指令怎样变成真正运动

本章可以从头连续阅读，理解所需的代码已经放在正文里，不需要读一句就切换一个文件。先看一次变道发生的过程，再读完整实验，最后亲手改一个条件。

本章只做一件事：**解释为什么目标车道可以立即改变，而车的位置需要经过一段运动才能靠近目标。** 你已经能说明“目标速度比实际速度低，就应该减速”；这里把同一个“目标与实际”的区别放到变道中。

### 3.1 先看我们要解释的现象

想象一条没有其他车辆的四车道直路。车道从左到右编号为 0、1、2、3，自车一开始在编号 1 的车道中心。我们先让它直行两次，第三次发出“向右变道”，之后恢复 `IDLE`。

你会看到两个不同的变化：目标先变成编号 2；车身随后逐渐向右移动，接近编号 2 的车道中心。发出一次右变道后，后面的 `IDLE` 并不会取消这个目标。控制器仍然在帮助车辆靠近已经设置的目标。

本实验的道路沿世界 x 方向延伸，世界 y 表示横向位置，单位是米。编号 1 的车道中心为 `y=4`，编号 2 为 `y=8`。因此问题可以直接写成：

```text
原来：目标是 y=4 米，实际也在 y=4 米
收到右变道：目标改为 y=8 米，刚修改目标时实际仍在原处
运动一段时间：实际 y 逐渐接近 8 米
到达附近：车头逐渐摆正，继续沿目标车道前进
```

这里的 y 来自模拟器车辆的 `position[1]`，是未归一化的世界坐标，不能与观察表中经过归一化的 y 混用。车道编号也不是米：编号 2 不等于位置 `y=2`。

把这个过程放回驾驶系统中：

```text
决策：这次发出右变道请求
        ↓
动作接口：把编号翻译成“向右变道”
        ↓
目标：记住接下来要跟踪哪条车道
        ↓
控制器：比较车辆当前位置、朝向与目标，计算转向角
        ↓
运动模型：按转向角、速度与时间推进位置和朝向
        ↓
下一时刻：控制器用新的位置、朝向继续修正
```

当前脚本按预定时刻发请求，没有观察邻车后再作交通判断。它适合研究“变道怎样执行”。道路上没有其他车，所以一次执行顺利，也不能说明策略已经会判断何时可以安全变道。

### 3.2 策略交出去的 action 到底是什么

`action` 只是接口名，它的意义由配置决定。下面四种类型不是四种驾驶水平，而是四种表达和分发动作的方式。

| 动作类型 | 策略交出的输入 | 接口交给车辆什么 | 一个直观例子 |
| --- | --- | --- | --- |
| `ContinuousAction` | 归一化的数值数组 | 映射后的加速度和转向角 | 默认双轴配置下 `[0.5, -0.2]` 指定两个连续控制量 |
| `DiscreteAction` | 一个整数编号 | 从有限组合中选出的加速度和转向角 | 默认双轴、每轴 3 档时，编号 4 对应归一化组合 `[0, 0]` |
| `DiscreteMetaAction` | 一个整数编号 | 调整车道或速度目标的高层指令 | 本章编号 2 表示向右变道，控制器负责跟踪 |
| `MultiAgentAction` | 按车辆顺序排列的动作元组 | 分给各辆受控车的动作 | 两辆车分别收到元组中的第一个、第二个动作；每辆车再按自己的动作类型解释 |

连续动作默认把第一维映射成加速度，单位 `m/s²`，把第二维映射成转向角，单位弧度。虽然有些接口文字使用 throttle，这里也不能把数值直接解释成真实车辆的油门踏板百分比。多车类型只负责组合与分发，不会因为打包了多辆车就自动完成协同决策。

本章完整脚本使用 `highway-v0` 的默认 `DiscreteMetaAction`，纵向与横向动作都启用。实际源码中的动作表为：

```python
# 源码摘录：DiscreteMetaAction 的默认双方向动作表，不是独立程序。
ACTIONS_ALL = {0: "LANE_LEFT", 1: "IDLE", 2: "LANE_RIGHT", 3: "FASTER", 4: "SLOWER"}
```

所以本实验的 `2` 才是右变道。如果只启用纵向动作，编号 2 表示 `FASTER`；换成 `DiscreteAction`，编号又是在选控制量组合。**整数没有跨配置通用的驾驶含义。** 只改速度档位列表也不会把这五种高层指令变成七种动作。

你此前的动作空间练习中，`env.action_space.contains(4)` 只回答“编号 4 是否属于这个输入空间”，不回答“此时减速是否合理”，也不回答“道路是否安全”。

### 3.3 右变道先改目标，没有直接搬动车辆

动作接口的关键方法非常短。下面是 `DiscreteMetaAction.act()` 的实际源码：

```python
# 源码摘录：此方法位于类内部，不能作为独立实验运行。
def act(self, action: int | np.ndarray) -> None:
    self.controlled_vehicle.act(self.actions[int(action)])
```

在本章配置下，这行完成的是 `2 → "LANE_RIGHT" → 交给受控车辆`。它没有把车辆坐标写成 `(x, 8)`。处理高层动作的车辆继续把请求交到 `ControlledVehicle.act()`，在那里才检查目标车道并更新目标。

更新目标最核心的一行是：

```python
# 源码摘录：通过目标车道的范围与可达性检查后，执行这一赋值。
self.target_lane_index = target_lane_index
```

左边是“车辆记住的目标”，不是 `self.position`。因此在这次赋值刚发生、运动尚未推进的瞬间，目标可以已经变了，实际坐标仍没有因为这次赋值而改变。

随后，同一个 `act()` 会执行以下源码：

```python
# 源码摘录：ControlledVehicle.act() 的控制输出部分。
action = {
    "steering": self.steering_control(self.target_lane_index),
    "acceleration": self.speed_control(self.target_speed),
}
action["steering"] = np.clip(
    action["steering"], -self.MAX_STEERING_ANGLE, self.MAX_STEERING_ANGLE
)
super().act(action)
```

这里新的 `action` 是一个控制量字典。`steering` 是转向角，`acceleration` 是加速度。它与最前面交给环境的整数 `2` 已经不在同一层：整数说的是“我要右变道”，字典说的是“这一小段时间具体怎样转向和加减速”。

`IDLE` 不进入新的调速或变道分支，但仍会走到这段控制输出。因此，第三次已经改好目标后，第四次恢复 `IDLE`，控制器会继续跟踪编号 2。若反复发送 `LANE_RIGHT`，程序可能继续把目标推到更右边的车道；这与“继续完成上一次变道”不同。

还有一个容易混淆的接口叫 `get_available_actions()`。它依据动作开关、车道可达性和速度档位边界列出候选动作，**不检查邻道有没有车，也不决定应该选哪个动作**。上面的 `DiscreteMetaAction.act()` 没有先调用它过滤输入。车辆处理右变道时确实还有道路编号范围和可达性检查，但这些几何条件不等于邻车安全检查。

<details>
<summary>源码细节：目标车道内部怎样表示，右变道分支检查了什么</summary>

模拟器用一个三元组标记车道：前两项标识道路连接，第三项才是当前这段道路上的车道编号。本章只在同一段直路上变道，前两项保持不变，第三项尝试加 1。下面是 `ControlledVehicle.act()` 中的原始右变道分支；`elif` 前后的其他分支已省略，不能单独运行。

```python
elif action == "LANE_RIGHT":
    _from, _to, _id = self.target_lane_index
    target_lane_index = (
        _from,
        _to,
        np.clip(_id + 1, 0, len(self.road.network.graph[_from][_to]) - 1),
    )
    if self.road.network.get_lane(target_lane_index).is_reachable_from(
        self.position
    ):
        self.target_lane_index = target_lane_index
```

`np.clip` 限制编号不要越出道路范围；`is_reachable_from` 检查目标车道的几何可达性等条件。这里没有查询邻车距离。还有一个细节：加 1 的基础是已经保存的**目标车道**，因此重复发指令可能再次改变目标，即使上一次还没到位。

</details>

### 3.4 控制器为什么同时看位置和车头朝向

设现在实际 `y=4`，目标车道中心 `y=8`。控制器需要让车向右靠近，但不能一直保持向右倾斜的车头，否则车会经过目标中心后继续向外移动。它要同时解决两件事：让横向位置接近中心，让车头逐渐转回车道方向。

本地 `steering_control()` 按以下顺序做事：

1. 将实际位置换算到目标车道上，得到“沿车道走了多远”和“离中心线横向差多少”。
2. 根据横向偏差，算出希望向目标中心靠近的横向速度。
3. 结合当前车速与前方车道方向，求出希望车头朝向哪里。
4. 比较希望朝向和实际朝向，把需要的转动速度换算成转向角。

前两步对应的实际源码是：

```python
# 源码摘录：steering_control() 中先定位目标、再计算横向修正。
target_lane = self.road.network.get_lane(target_lane_index)
lane_coords = target_lane.local_coordinates(self.position)
lane_next_coords = lane_coords[0] + self.speed * self.TAU_PURSUIT
lane_future_heading = target_lane.heading_at(lane_next_coords)

# 横向位置控制
lateral_speed_command = -self.KP_LATERAL * lane_coords[1]
```

`lane_coords[1]` 是相对于**目标车道中心线**的有符号横向偏差，单位米，未归一化。本章直路上，实际 y 为 4、目标中心 y 为 8 时，这个偏差为 -4 米。前面的负号会给出朝目标中心的横向修正方向。靠近中心后，偏差减小，这部分修正也随之减小。

`lane_future_heading` 是沿目标车道略向前看时的道路方向。直路上它不变；保留这个量是为了让控制器不仅能对着当前一点，还能参考前方道路方向。`TAU_PURSUIT` 的单位是秒，速度乘它得到向前看的距离。

实际朝向的比较在下一段源码中：

```python
# 源码摘录：heading_ref 已由道路方向和横向修正得到，单位弧度。
heading_rate_command = self.KP_HEADING * utils.wrap_to_pi(
    heading_ref - self.heading
)
```

`self.heading` 是车头当前朝向。位置误差很小时，车头仍可能朝右；这时航向误差会让控制器调整转向，帮助车辆回到沿车道前进的方向。因此不能只用一句“离目标越近，方向盘越小”概括完整行为；转向同时受横向位置、车头朝向和当前速度影响。

<details>
<summary>需要核对公式时再展开：横向速度、期望朝向与转向角</summary>

下面完整保留位置控制之后的计算。它是方法体摘录，输入依赖前文计算出的变量，不是独立脚本。

```python
# 将横向速度转换为航向
heading_command = np.arcsin(
    np.clip(lateral_speed_command / utils.not_zero(self.speed), -1, 1)
)
heading_ref = lane_future_heading + np.clip(
    heading_command, -np.pi / 4, np.pi / 4
)
# 航向控制
heading_rate_command = self.KP_HEADING * utils.wrap_to_pi(
    heading_ref - self.heading
)
# 将航向角速度转换为转向角
slip_angle = np.arcsin(
    np.clip(
        self.LENGTH / 2 / utils.not_zero(self.speed) * heading_rate_command,
        -1,
        1,
    )
)
steering_angle = np.arctan(2 * np.tan(slip_angle))
steering_angle = np.clip(
    steering_angle, -self.MAX_STEERING_ANGLE, self.MAX_STEERING_ANGLE
)
return float(steering_angle)
```

`wrap_to_pi` 避免把跨越角度边界的一小段转动误当成接近一整圈的差值。`clip` 限制数值或转向范围；`not_zero` 避免除以零。这些处理使计算有定义，但不能据此认定该简化控制器在停车、极低速或任意道路上都能可靠完成变道。

若只看纵向，当前比例控制器更直接：

```python
# 源码摘录：speed_control() 的返回表达式。
return self.KP_A * (target_speed - self.speed)
```

速度差单位为 `m/s`，`KP_A` 单位为 `1/s`，结果就是 `m/s²`。目标速度低于实际速度时结果为负；真正降低多少速度，还取决于这份加速度持续多久。

</details>

### 3.5 运动模型推进之后，实际状态才变

控制器计算出的字典最终由基础车辆的 `act()` 保存：

```python
# 源码摘录：Vehicle.act() 的动作保存逻辑。
if action:
    self.action = action
```

这仍然不是位置更新。环境接着调用运动模型的 `step(dt)`，才按一小段时间改变车辆状态。下面摘出三个关键更新，省略了速度方向计算和碰撞处理，不能独立运行：

```python
# 源码摘录：Vehicle.step(dt) 的状态更新。
self.position += v * dt
self.heading += self.speed * np.sin(beta) / (self.LENGTH / 2) * dt
self.speed += self.action["acceleration"] * dt
```

这里的 `v` 是运动模型根据当前速度、车头朝向与转向算出的二维运动速度；`dt` 单位秒。位置更新是“米/秒 × 秒”，得到米；加速度乘时间，得到速度变化。`beta` 是此简化车辆模型使用的角度中间量，具体公式放在下面，不影响先理解调用顺序。

本章脚本的决策频率是 **1 Hz**，沿用的物理仿真频率是 **15 Hz**。一次 `env.step(action)` 正常推进 1 秒模拟时间，其中包含 15 次、每次约 `1/15` 秒的物理更新。**不是车先静止等待 1 秒，随后瞬间跳到新位置。**

环境内部每个物理小步都做的核心两行是：

```python
# 源码摘录：AbstractEnv._simulate() 的物理小步循环内部。
self.road.act()
self.road.step(1 / self.config["simulation_frequency"])
```

第一行让车辆根据当前状态重新计算控制，第二行按时间推进运动。对本章受控车辆来说，即使策略这 1 秒没有再发一条新变道命令，控制器仍会随着新的位置和朝向更新转向量。

因此这里有两层不同的反馈：**控制器利用实际位置和朝向修正运动；脚本策略仍然按预定次数发动作，不利用交通观察选择何时变道。** 环境确实交互推进，不等于高层策略已经学会交通决策。

<details>
<summary>需要核对运动公式时再展开：Vehicle.step() 怎样取得 v 和 beta</summary>

这是 `Vehicle.step()` 开头的实际源码摘录。转向量是弧度，位置是世界坐标米，速度为米/秒。模型仍是教学仿真中的简化运动模型，不是完整轮胎与底盘模型。

```python
self.clip_actions()
delta_f = self.action["steering"]
beta = np.arctan(1 / 2 * np.tan(delta_f))
v = self.speed * np.array(
    [np.cos(self.heading + beta), np.sin(self.heading + beta)]
)
self.position += v * dt
```

接下来还会处理碰撞影响、更新朝向与速度，并重新计算车辆当前所在车道。已经保存的目标车道与根据实际位置识别的当前车道是两个量；即使当前车道编号已改变，也不能据此断言车身已经精确位于中心线。

</details>

### 3.6 把目标和实际位置画在同一条时间线上

对比之前先统一单位：目标编号 1、2 对应的目标中心分别为 4 米、8 米，然后再与实际 y 比较。不要直接把“编号 2”和“实际位置 7.41 米”放在同一条纵轴上。

下面的数值来自 **2026-09-24 助手的历史独立验证**，不是本章新运行，也不是你的个人实验结果。条件为 seed=0、四车道、无其他车辆、初始车道 1、1 Hz 决策、10 秒时限，调用 `main(render_mode=None)`，没有验证可见窗口。已有原始记录在本项目 `learning/evidence/2026-09-24-assistant-lane-change-check.json`。

| 动作后的模拟时间 | 本次动作 | 动作后目标车道 | 对应目标中心 y（米） | 动作后实际 y（米，保留 3 位） |
| --- | --- | --- | --- | --- |
| 1 秒 | `IDLE` | 1 | 4 | 4.000 |
| 2 秒 | `IDLE` | 1 | 4 | 4.000 |
| 3 秒 | `LANE_RIGHT` | 2 | 8 | 7.408 |
| 4 秒 | `IDLE` | 2 | 8 | 7.954 |
| 5 秒 | `IDLE` | 2 | 8 | 7.997 |

下面把变化形状画出来，**只示意目标先变、实际随后靠近，不按比例，也不插造中间时刻的实测值**：

```text
横向 y（米）
8  目标中心           ┌────────────────────────
   实际位置           │       ╭────────────────
                      │     ╭─╯
                      │   ╭─╯
4  目标与实际 ────────┘───╯
                      ↑
                第三次决策发出右变道
                （约 t=2 秒，随后推进至 t=3 秒）
                                    模拟时间 →
```

表里第三行已经是第三次 `env.step()` 返回之后，距离发送请求又过了 1 秒。因此它显示的是实际已经移动到约 7.408 米，不能据此说“改目标的那行代码直接把位置变成了 7.408”。刚赋值的瞬间和这一行打印的时刻不同。

第四、第五次发送的都是 `IDLE`，实际位置仍然继续靠近 8 米，这就是控制器继续跟踪目标的证据。打印保留两位小数时，7.9968 会显示为 8.00；显示相等不能证明内部数值完全相等。

### 3.7 本章完整实验：先运行现有版本

本章只运行下列变道实验。脚本已经归入主项目，不需要复制模拟器，也不需要重新安装环境。你可以在 VS Code 中打开它，对着下方全文阅读；已存在的文件不必重写。

```text
C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\01_lane_change.py
```

下面是该文件的**完整现有代码**，与上面的源码摘录不同，它可以作为完整脚本运行：

```python
"""实验 01：发送一次向右变道指令，观察目标车道和实际位置。"""

import gymnasium as gym
import highway_env  # 导入后，Gymnasium 才认识 highway-v0


def main(render_mode="human"):
    # 四车道、无其他车辆，先单独观察变道怎样执行。
    env = gym.make(
        "highway-v0",
        render_mode=render_mode,
        config={
            "lanes_count": 4,
            "vehicles_count": 0,
            "initial_lane_id": 1,
            "duration": 10,
            "policy_frequency": 1,
        },
    )

    try:
        obs, info = env.reset(seed=0)

        # 下列内部数据只用于观察模拟器，不参与驾驶决策。
        vehicle = env.unwrapped.vehicle
        print("车道从左到右编号为 0、1、2、3；本次从编号 1 出发。")
        print("编号 1 的车道中心 y=4 米，编号 2 的中心 y=8 米。")
        print("初始横向位置 y：", round(float(vehicle.position[1]), 2), "米")

        for step in range(10):
            # step 从 0 开始：第 3 次决策只发一次向右变道指令。
            if step == 2:
                action = 2
                decision = "向右变道一次"
            else:
                action = 1
                decision = "保持目标车道和目标速度"

            print("\n第", step + 1, "次决策：", decision, "，动作编号：", action)
            obs, reward, terminated, truncated, info = env.step(action)

            # 目标会先改变，实际位置需要随车辆运动逐渐靠近目标。
            print("行动后目标车道编号：", vehicle.target_lane_index[2])
            print("行动后横向位置 y：", round(float(vehicle.position[1]), 2), "米")

            if terminated or truncated:
                if info["crashed"]:
                    print("结束：发生碰撞。")
                elif truncated:
                    print("结束：达到 10 秒仿真时间上限。")
                else:
                    print("结束：环境终止。")
                break

    except KeyboardInterrupt:
        print("\n已手动停止实验。")
    finally:
        env.close()


if __name__ == "__main__":
    main()
```

这段脚本可以按三部分读。配置把其他车辆清空，固定起始车道与种子，便于单独观察执行过程；循环只在 `step == 2` 时发一次动作 2；`env.step()` 之后才打印目标和实际位置。`env.unwrapped.vehicle` 读的是模拟器内部诊断信息，不是从摄像头感知出来的数据，也没有被用来作交通决策。

在 PowerShell 中运行。本机继续使用已有的 `py310` 解释器，下面两个完整路径使命令不依赖终端当前目录：

```powershell
& 'D:\miniconda\envs\py310\python.exe' 'C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\01_lane_change.py'
```

保留第 2～5 次决策的输出及结束原因。先看第 3 次目标是否变了，再看第 4 次恢复 `IDLE` 后实际 y 是否继续靠近目标。达到时间上限表示这次实验按时结束；中途关闭或 Ctrl+C 应记为手动停止，不能当作完整回合。

### 3.8 只改一个条件：把请求推迟两次

先保留原版输出，在自己的笔记中写下一句预测：**如果右变道从第三次推迟到第五次，第 3～6 次打印出的目标车道和实际 y 将怎样变化？** 不需要预测到小数点，先判断哪个时刻目标改变、哪个阶段实际位置开始移动。

然后在同一个实验文件中亲手把这一行：

```python
if step == 2:
```

改为：

```python
if step == 4:
```

同时把相邻注释里的“第 3 次”改为“第 5 次”；这只是让注释符合新行为。种子、车辆数、起始车道、动作编号、频率与总时限都保持原样，再用同一条命令运行。

比较两次第 3～6 次决策的目标和 y，说明“请求推迟”影响的是时间，还是目标车道本身。如果结果不符合预测，先核对保存的文件、运行路径、实际动作编号与结束原因。不要同时改速度、道路或其他车辆，把一个问题变成多个变量。

本节留下四项简短记录即可：事前预测、两次输出对应的时间和动作、你对差异的解释、这次实验不能证明什么。能解释目标、控制和实际运动的先后，再讨论有交通时为什么要选择变道；读完本章或完成一次运行本身不自动代表掌握。

### 3.9 本章结论能够覆盖到哪里

这里的动作是**高层车道请求**；转向角和加速度由模拟器控制器计算；世界坐标中的位置经物理小步推进后才改变。控制器在利用实际状态反馈，脚本的变道时机仍然是预先写好的。

运行记录属于交互仿真的执行证据，不是离线轨迹误差，也不是一套完整的闭环驾驶成绩。本章没有比较交通策略的碰撞率或舒适性，没有视觉输入、模型训练或邻车安全判断。之后要学习“前车很慢时是否该变道”，还需要看本车道和邻道车辆、提出决策条件，并在同条件场景中评测。

<details>
<summary>独立补充：连续动作直接指定什么（本次不再派第二项实验）</summary>

如果以后要对照“高层目标”和“直接控制量”，可以使用已有的连续动作练习。它是另一个实验，不是变道脚本的后半段，也不要把它的数组传给本章 Meta 环境。

默认双轴 `ContinuousAction` 把 `[-1,1]` 映射到加速度 `[-5,5] m/s²` 与转向角 `[-π/4,π/4]` 弧度。因此 `[0.5,-0.2]` 映射到加速度 2.5 m/s² 和转向角 `-π/20`，约 -0.1571 弧度。这是源码映射的计算结果，不是本章新做的实测。最终单步速度仍应从真实输出确认。

现有文件的完整路径：

```text
C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\03_continuous_action.py
```

下方为该文件的完整现有代码，可独立运行。它不显示窗口；`get_action()` 只做映射并用于诊断，真正推进环境的是后面的 `env.step(action)`。

```python
import gymnasium as gym
import highway_env
import numpy as np

env = gym.make(
    "highway-v0",
    config={
        "action": {"type": "ContinuousAction"},
        "vehicles_count": 0,
        "policy_frequency": 1
    },
)

try:
    env.reset(seed = 0)

    action = np.array([0.5,-0.2],dtype=np.float32)

    # 读取模拟器内部信息，仅用于验证源码
    control = env.unwrapped.action_type.get_action(action)
    speed_before = env.unwrapped.vehicle.speed

    obs, reward, terminated, truncated, info = env.step(action)

    print("动作空间：", env.action_space)
    print("加速度：", round(control["acceleration"], 4), "m/s²")
    print("转向角：", round(control["steering"], 4), "弧度")
    print("执行前速度：", round(speed_before, 2), "m/s")
    print("执行后速度：", round(info["speed"], 2), "m/s")
    print("速度变化：", round(info["speed"] - speed_before, 2), "m/s")
finally:
    env.close()
```

本章的最小修改实验完成后，如选择研究这个独立问题，再运行：

```powershell
& 'D:\miniconda\envs\py310\python.exe' 'C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\03_continuous_action.py'
```

这里没有“目标车道 2”的请求，也不保证沿某条车道中心行驶。它提供的是持续一小段时间的控制量。两种动作接口承担的职责不同，不能只比较编号或数组大小就认为它们是同一驾驶意图。

</details>

<details>
<summary>可选源码出处与历史证据</summary>

正文摘录已足够完成本章阅读。需要在 VS Code 核对时再打开这些文件，不要求逐个完整读完：

- 动作定义：`C:\Users\Administrator\Desktop\职业生涯项目\HighwayEnv\highway_env\envs\common\action.py`，关注 `DiscreteMetaAction.act()` 与 `get_available_actions()`。
- 目标与控制：`C:\Users\Administrator\Desktop\职业生涯项目\HighwayEnv\highway_env\vehicle\controller.py`，关注 `ControlledVehicle.act()`、`steering_control()`、`speed_control()`。
- 运动更新：`C:\Users\Administrator\Desktop\职业生涯项目\HighwayEnv\highway_env\vehicle\kinematics.py`，关注 `Vehicle.act()` 与 `step()`。
- 环境内的小步循环：`C:\Users\Administrator\Desktop\职业生涯项目\HighwayEnv\highway_env\envs\common\abstract.py`，关注 `_simulate()`。
- 动作空间旧练习：`C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\experiments\highway_driving\demos\02_action_space.py`。
- 历史助手验证：`C:\Users\Administrator\Desktop\职业生涯项目\vla_basic\learning\evidence\2026-09-24-assistant-lane-change-check.json`。

源码依据是当前本机 HighwayEnv 开发版。更换版本或配置后，应重新核对动作表、频率、坐标和实际结果。正文中的历史数值与本轮助手运行检查分开记录；都不代替学习者自己的运行与解释。

</details>


---

<a id="chapter-04"></a>

## 第04章｜这次没撞，是改好了，还是这条路比较容易？

前面我们让车看前车距离，按规则决定加速或减速，也看过变道是怎样执行的。现在假设你把减速距离从 40 米改成了 50 米。新跑的一局没有撞车，你会自然地想：是不是这个修改有效？

问题是，原来的程序每次重开一局都可能生成不同交通。也许规则改好了，也许这次前车更远、更快。要判断修改的作用，我们先让两个版本面对尽量相同的起点。

### 4.1 先固定起点，再比较动作带来的变化

你做过模型训练，应该熟悉固定随机种子的作用。驾驶实验也需要种子，但只记种子还不够：道路配置、车辆数量、时间上限、代码与依赖版本也会影响结果。

在下面的实验中，“同条件”具体指同样的模拟器与运行器版本、配置、种子和初始观察。两个动作执行后，车辆位置和后续观察开始不同，这是我们要观察的结果，不应强行把它们改回一致。

我们先借项目已有记录器做一个小对照：一组始终保持目标，一组每一步都请求减速。这个记录器还不能传入跟车策略，所以本节先学比较方法，后续再将相同方法接到跟车规则。不能把下面的结果当作 40 米和 50 米阈值实验。

### 4.2 一条日志为什么同时保存两次观察

下面直接列出记录器的相关实际代码。它是程序的一段摘录，用来阅读，不是要求单独运行的完整文件：

```python
observation_time_s = float(env.unwrapped.time)
next_obs, reward, terminated, truncated, info = env.step(action_id)
```

第一行读的是动作之前的时间。第二行发出动作，让环境推进，然后取得动作之后的新观察。完整程序随后把前后两份信息写在同一条记录里。

只看打印顺序很容易混淆。假设我们用“前车距离 35 米”选择减速，随后打印速度，这个距离属于动作之前，速度属于动作之后。判断规则为什么做了这个决定时，要回到决策当时看见的距离，不能拿后来的位置替它补理由。

本节使用的旧记录器配置为：物理更新 15 Hz、决策 5 Hz。因此正常情况下，一次 `env.step` 推进 0.2 秒。前面跟车与变道示例用的是 1 Hz 决策，一次通常是 1 秒；它们是不同实验配置。`Hz` 表示每秒发生几次，循环一次并不天然等于一秒。

### 4.3 完整的小对照程序

下面是完整程序。它调用项目已有记录器，但比较条件、如何调用、读取哪些结果都在这里列出，不需要打开记录器源码才能做本节。

还要注意一处配置变化：本节记录器的目标速度档位为 **`[20, 25, 30]` m/s，最低仍是 20 m/s**。第 02 章跟车程序用的则是 `[0, 5, 10, 15, 20, 25, 30]`。因此这里连续请求 `SLOWER` 不会把目标降到零，更不能把它理解为紧急制动；速度如何接近目标仍由控制器决定。

下面是一个完整 PowerShell 块：在 VS Code 的 PowerShell 终端整体粘贴即可。它先进入本项目，再使用已有 py310 从标准输入执行 Python，不创建新脚本。当前只是提供后续章节的教材，不要求你现在同时开始这一章。

<!-- runnable: chapter04-paired-comparison -->
```powershell
Set-Location -LiteralPath 'C:\Users\Administrator\Desktop\职业生涯项目\vla_basic'
@'
from pathlib import Path
import runpy

# 工作目录应是 vla_basic；加载现有记录器，不执行它的命令行入口。
runner_path = Path("experiments/highway_driving/run_episode.py")
if not runner_path.is_file():
    raise RuntimeError("请先把终端工作目录切换到 vla_basic")
run_episode = runpy.run_path(str(runner_path))["run_episode"]

seeds = [7, 11]
results = {"IDLE": [], "SLOWER": []}

for seed in seeds:
    pair = {}
    for action in results:
        result = run_episode(
            seed=seed,
            max_steps=40,
            action_name=action,
            render_mode=None,
            output_dir=None,
            duration_s=8.0,
            vehicles_count=12,
        )
        pair[action] = result
        results[action].append(result)
        print(
            "种子", seed, "动作", action,
            "结束原因", result["end_reason"],
            "碰撞", result["crashed"],
            "仿真秒数", round(result["sim_time_s"], 2),
            "动作次数", result["steps"],
        )

    # 只比较初始条件；动作之后的状态本来就可能不同。
    assert pair["IDLE"]["initial_observation"] == pair["SLOWER"]["initial_observation"]
    assert pair["IDLE"]["config"] == pair["SLOWER"]["config"]

for action, runs in results.items():
    crashes = sum(int(item["crashed"]) for item in runs)
    print(action, "发生碰撞的回合数：", crashes, "/", len(runs))
'@ | & 'D:\miniconda\envs\py310\python.exe' -
```

这里运行的是 2 个种子 × 2 个动作，共 4 次独立回合，均不开图形窗口，也不写输出目录。每组的碰撞分母是 2 个回合，不是总步数。`assert` 只检查我们有没有真的从相同观察和配置开始，没有宣称两组的整个世界演化会相同。

本章没有预先填一组“应该谁赢”的碰撞数字。请以你实际输出为准；种子固定也不能替代代码和依赖版本记录。

### 4.4 先读结束原因，再看成绩

把 `end_reason` 翻译成日常语言，就能避免几个常见误判：

| 输出值 | 本次发生了什么 | 你可以怎样描述 |
| --- | --- | --- |
| `collision` | 模拟器记录到碰撞 | 这次回合发生了碰撞 |
| `environment_time_limit` | 到了预设环境时间 | 跑到了本实验时限，还要结合碰撞等字段说明表现 |
| `runner_step_limit` | 脚本用完了动作次数预算 | 我们停止了观察，不能称为完成了整个驾驶任务 |
| `off_road` | 模拟器判定离开道路 | 需要回看动作和道路位置 |
| `terminated` | 环境以其他终止条件结束 | 需要查看该环境的终止定义 |

比如只给 5 次动作、每次 0.2 秒，一共仅观察了约 1 秒；这不能和另一个跑满 8 秒的回合直接当成同等暴露时间比较“安全程度”。我们的对照先固定了时间和步数预算，但碰撞仍可能让某组提前结束，所以同时打印仿真时间。

记录器还能保存每一步的观察、动作及新状态。需要回放失败时再使用它的保存功能；先选一局能说明问题的记录，不必一次堆几百张图。

### 4.5 奖励高，不一定开得更合适

`reward` 是环境按自己设定的规则打的分。你可以把它理解成训练或实验用的一张评分表；如果评分表很鼓励速度，快一点可能提高分数，却不代表所有风险都得到了照顾。

比较驾驶行为时，至少要把“有没有撞”“是否向前行驶”“有没有突然加减速”分开看。它们是不同问题，可能存在取舍。当前记录器保存了速度与位置，尚未给出整套舒适性指标；不能因为目录里有日志就称为评测系统已经完成。

两个种子足够演示如何成对比较，还不足以证明普遍改进。后续应准备一批调试时用的场景，再留出另一批场景检查泛化。做过训练集/验证集切分的你可以沿用这个习惯，但驾驶场景往往包含同一段路、同一交通过程，不能简单把相邻时间步随机拆开就认为彼此独立。

### 4.6 开放环和闭环，先记它们实际做了什么

**开放环评测**：拿已经记录好的输入，让模型预测未来，再和对应标签比较。模型这一次的预测不会改变已经记录下来的下一张图或下一条状态。

**闭环评测**：把策略输出实际交给交互环境，车辆运动会改变之后看见的情况，后续决策再使用变化后的输入。

本节的模拟器确实执行了动作并推进环境，但我们选择的是恒定动作，不依据新观察换决定。它是交互环境中的执行与对照，不是一个已经利用反馈避碰的驾驶策略。前面的距离跟车规则会读取新观察并重新选动作，才具备那一层策略反馈。

你在 NLP 中常用的一次离线准确率，与一辆车连续执行动作的行为，区别就在这里：先前动作会改变之后遇到的数据。以后训练视觉或轨迹模型时，我们仍会回到这个区别。

### 4.7 做一个能解释的修改

等这一章成为当前任务时，可以只把 `max_steps=40` 改成 `max_steps=5`，其他条件保持相同。先预测它最多观察多少秒，以及为什么更短的一段无碰撞记录不能证明策略改进，再比较实际结束原因。

一次只改这一项；看懂结果后再考虑更多场景，而不是同时改车辆数、阈值、奖励和时间。你要练的是解释“是哪一个变化造成了哪些结果”，不是凑一个更好看的总分。

<details>
<summary>可选出处与已有实现</summary>

记录器：`experiments/highway_driving/run_episode.py`，关键函数 `run_episode` 与 `end_reason`。本地版本的旧基线采用未归一化、世界轴对齐的观察，和默认跟车 demo 的归一化表不同。本章不混用它们的观测数值。

可选源文件：[run_episode.py](../experiments/highway_driving/run_episode.py)。相关测试是已有的运行器检查，测试通过不能替代学习者解释或证明一般驾驶安全。

</details>


---

## 接下来，同一个项目怎样走向驾驶模型

当前四章先让你能解释一次动作的执行，也开始建立比较实验的习惯。模拟器直接给出车辆状态，省去了真实图像里“车在哪里、动得怎样”的困难。走向车企智驾工作时，还需要把这部分补回来，并选一个方向形成更深入的作品。

后续内容会继续写在 vla_basic，不把你送去另一个互不相干的教程。下面是还要交付的阶段及其具体问题，当前没有将它们记成已完成的章节或工程。

### 从当前状态走到驾驶数据和未来轨迹

假设一条训练样本包含最近几次观察，标签是接下来几秒车会走过的位置。输入只能使用作决定时已经知道的内容，标签可以包含未来，但不能偷偷跑回输入里。

接下来要处理三个问题：历史与未来怎样按时间切开；位置是相对于地图还是相对于当前车；同一段行车记录怎样划分，避免几乎相同的相邻片段同时进训练和测试。你已有的数据处理经验能用在这里，新增的是时间、几何和行车过程的含义。

未来轨迹可以先理解成一组“未来时刻希望到达的位置”。它比一句“向右变道”更具体，但仍需要车辆控制去实现。这个阶段将配坐标变换、轨迹标签与运动验证，尚未新增完整实验。

### 从规则走到第一个驾驶模型

现在规则根据距离选动作，之后可以先用模拟器状态训练一个小模型，学习状态到动作或轨迹的映射。这样能把训练问题和视觉输入问题分开定位。

普通的优化器、训练循环与验证集你已经接触过，不必从头重复；需要新检查的是驾驶输入的时间和坐标、标签含义，以及模型执行后会遇到什么状态。先让小样本跑通、定位错误，再比较规则和模型；一次 loss 下降不能代替车辆行为对照。

本阶段的状态模仿学习工程待交付，不能把当前手写规则称为训练好的 AI。

### 从模拟器表格走到相机图像

真实相机没有直接写着“前车 35 米”。我们要学习图像中的位置怎样通过相机参数关联到空间、不同相机和历史图像怎样对齐，以及输入中哪些信息能支持距离和运动判断。

例如图片尺寸改变后，相机内参也可能需要相应处理；把未来轨迹投到图上检查，有时能比单看 loss 更早发现坐标问题。这些概念会配可运行的小几何例子，然后再进入适合本机资源的公开视觉数据。真实数据适配器和视觉基线尚未实现。

### 从一张图走到历史信息、导航与轨迹预测

只看一张图，很难判断旁边的车正在加速还是减速。使用连续时刻的信息可以帮助估计变化，但必须知道每一帧发生在什么时候，不能把顺序打乱后还当作连续运动。

导航告诉系统希望到哪条路、哪个出口；模型需要在周围情况与行驶意图之间作出选择。这个阶段再引入历史信息、导航条件和未来轨迹，做输入去除对照，检查模型是否确实在使用所声称的信息。时序模型和训练结果待交付。

### VLM、VLA 与部署为什么放在后面

VLM 在这里先指处理视觉与语言的模型；VLA 还需要把信息接到可执行的动作表示。名字不能说明输出具体是什么：可能是轨迹点，也可能是需要解码的动作编号。它们仍要回答本卷的问题——输出之后，谁负责执行、时间怎样推进、执行结果怎样检查。

等已有可信模型和评测，再结合你学过的蒸馏与量化检查模型压缩。除了数值变化，还要测延迟、内存与驾驶行为。车端 C++、运行时和硬件集成会按目标岗位需要增加；你有课程基础，可以从具体读改和调试恢复，不必重上整套语法课。

强化学习和世界模型放在交互、数据与评测基础之后，按具体问题引入。现阶段不需要背算法名称才能继续学习。

这些后续方向共有基础，也有各自的深度要求。等你能拿当前实验解释执行链、复现失败并比较修改，我们再结合车企目标岗位，把其中一个方向做深，而不是要求一次精通整条产业链。
