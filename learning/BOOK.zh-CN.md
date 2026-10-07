# 智驾入门｜从一条指令到车辆行为

这本书用一个驾驶模拟器（HighwayEnv），把自动驾驶里最基础的一条链讲清楚：

```text
看到周围情况 → 决定怎么开 → 控制器算出转向和加减速 → 车辆运动 → 看到新的情况
```

你已经会 Python、做过 AI 和后端项目，所以这里不讲语法和训练基础，只补驾驶领域的东西：**时间、坐标、目标与实际、动作与控制、怎样评测**。

---

## 开始之前

### 怎么读

每一节都按同一个顺序：**一个具体现象 → 用大白话解释 → 看真正起作用的几行代码 → 自己动手改一处**。读一小段就动手，不用等整章读完。

书里的代码块有三种，标题会写清楚：

| 标注 | 含义 |
| --- | --- |
| **源码摘录** | 从真实代码里挑出的相关几行：语句不改，只省略文档字符串，中文注释是为讲解加的。需要放回原文件才能跑 |
| **教学简化** | 删掉了无关分支、方便看主干的版本，不是原文 |
| **可以直接运行** | 复制出来就能跑 |

折叠的 `▶` 小块是细节，第一遍可以跳过。

### 运行准备（只需一次）

在 VS Code 里打开 PowerShell 终端：

```powershell
conda activate py310
cd C:\company\own\vla_basic
```

之后所有实验都在这个目录下用 `python 文件路径` 运行。实验文件都在 [experiments/highway_driving/demos/](../experiments/highway_driving/demos/README.md)。

### 全书地图：一次 `env.step()` 里发生了什么

你写的程序每调用一次 `env.step(action)`，模拟器内部大致做这些事。每一章负责其中一段：

```text
你的程序                       模拟器内部
─────────                      ─────────────────────────────────────────
                               ┌─ 第 3 章：把动作编号翻译成“改目标”
obs ──► 选动作 ──► env.step ──►│     （目标速度、目标车道）
  ▲     第 2 章                │  重复几个物理小步：
  │                            │     控制器：目标 vs 实际 → 转向角、加速度   第 1、3 章
  │                            │     运动模型：按加速度和转向推进 dt 秒      第 1、3 章
  │                            │     检查碰撞
  │                            └─ 生成新的观察表、奖励、是否结束             第 2、4 章
  └──────────────── 新的 obs ◄──┘
```

第 4 章讲的是另一件事：**改了策略之后，怎样公平地判断它变好了没有。**

想直接对照源码文件，看[附录 A：一次 env.step 的源码地图](#appendix-a)。

### 四个实验的设置不一样，先记住这张表

模拟器有两个频率：**物理频率**（每秒推进车辆运动几次）和**决策频率**（每秒调用几次 `env.step`）。本书所有实验物理频率都是 15 Hz，决策频率不同，所以“一步”有多长也不同：

| 实验 | 章 | 决策频率 | 一次 `env.step` 推进 | 其他车辆 | 种子 | 目标速度档位 (m/s) |
| --- | --- | --- | --- | --- | --- | --- |
| [04_target_speed.py](../experiments/highway_driving/demos/04_target_speed.py) | 1 | 5 Hz | 0.2 秒（3 个物理小步） | 0 | 0 | 不用档位，直接设目标 |
| [00_following.py](../experiments/highway_driving/demos/00_following.py) | 2 | 1 Hz | 1 秒（15 个物理小步） | 50 | 0 | 0, 5, 10, 15, 20, 25, 30 |
| [01_lane_change.py](../experiments/highway_driving/demos/01_lane_change.py) | 3 | 1 Hz | 1 秒（15 个物理小步） | 0 | 0 | 20, 25, 30（默认） |
| [05_compare_actions.py](../experiments/highway_driving/demos/05_compare_actions.py) | 4 | 5 Hz | 0.2 秒（3 个物理小步） | 0 | 7 | 20, 25, 30 |

> 看到“第几步”时，先想一下这一步是 0.2 秒还是 1 秒。很多困惑都来自把不同实验的“一步”混在一起。

### 贯穿全书的几组词

| 词 | 意思 | 例子 |
| --- | --- | --- |
| **实际** vs **目标** | 车现在的状态 vs 希望它达到的状态 | 实际速度 25 m/s，目标速度 20 m/s |
| **动作** vs **控制量** | 策略交给环境的高层请求 vs 控制器算出的转向角和加速度 | 动作 `SLOWER`；控制量 `{"acceleration": -8.33, "steering": 0}` |
| **一步** vs **物理小步** | 一次 `env.step()` vs 模拟器内部一次运动更新 | 一步 = 0.2 秒 = 3 个 1/15 秒的小步 |
| **仿真时间** vs 真实时间 | 模拟世界里过去的秒数 vs 你电脑上过去的秒数 | `env.unwrapped.time` 是仿真时间 |
| **观察** | 环境交给策略的信息表 | 5 行 × 5 列的车辆表（第 2 章） |

单位统一：距离米（m），速度米/秒（m/s，乘 3.6 是 km/h），加速度 m/s²，角度弧度。25 m/s = 90 km/h，20 m/s = 72 km/h。

---

<a id="chapter-01"></a>

## 第 1 章｜程序决定减速了，为什么车速是慢慢降下来的？

这一章只讲纵向（前后方向）：**目标速度怎样一步步变成实际速度。** 读完你会知道 `env.step()` 里面那几次“控制 → 运动”是怎么转的。

### 1.1 目标和实际是两个不同的变量

开车看到限速牌，你决定从 90 km/h 降到 72 km/h。做决定的那一瞬间，车速还是 90；松油门、踩刹车之后，车速才一点点降下来。

程序里也一样，车辆对象上有两个变量：

```python
speed = 25.0         # 实际速度：车现在多快（m/s）
target_speed = 20.0  # 目标速度：希望达到多快（m/s）
```

**把 `target_speed` 改成 20，`speed` 不会自己变。** 中间还隔着两段程序：

1. **控制器**：比较目标和实际，算出“现在该用多大的加速度”。
2. **运动模型**：拿这个加速度，推进一小段时间，更新速度和位置。

这和后端写数据库不一样：你保存一条“待执行”的记录，数据立刻就在那里了；而车要靠时间推进才能接近目标，并且已经开过的路不能回滚。

### 1.2 控制器：速度差 → 加速度

> **源码摘录** `highway_env/vehicle/controller.py` · `ControlledVehicle.speed_control`

```python
def speed_control(self, target_speed: float) -> float:
    return self.KP_A * (target_speed - self.speed)
```

就一行：**（目标 − 实际）× 系数 = 加速度**。

- 目标比实际低 → 结果是负数 → 减速。
- 差得越多，加速度越大；越接近目标，加速度越小，最后平稳贴上去。

这种“按差值大小成比例地调整”叫**比例控制**（P 控制）。系数 `KP_A = 1 / 0.6 ≈ 1.667`，单位是 1/秒。

代入数字：实际 25，目标 20，差 −5，加速度 = 1.667 × (−5) ≈ **−8.33 m/s²**。

注意：**这个方法只返回一个数**，它没有改速度，也没有让时间流逝。

### 1.3 时间推进以后，速度才真正改变

真正改速度的是运动模型里的这一行：

> **源码摘录** `highway_env/vehicle/kinematics.py` · `Vehicle.step`（其中一行）

```python
self.speed += self.action["acceleration"] * dt
```

`dt` 是这一个物理小步的时长。本章实验的物理频率是 15 Hz，所以 `dt = 1/15 秒`。

第一个小步：速度变化 = −8.33 × 1/15 ≈ −0.556，速度变成 **24.444**。

关键在下一个小步：控制器会**用新的实际速度重新算**。差变成 −4.444，加速度变成 −7.41，比上一次小。所以减速是“先快后慢”的曲线，不是直线。

你可以自己用 7 行 Python 把这个过程算出来：

> **可以直接运行**（纯 Python，不需要模拟器）

```python
KP_A = 1 / 0.6          # 控制器系数，单位 1/s
dt = 1 / 15             # 一个物理小步，单位秒
speed, target = 25.0, 20.0
for i in range(1, 4):
    acceleration = KP_A * (target - speed)   # 控制器：速度差 → 加速度
    speed += acceleration * dt               # 运动模型：加速度 × 时间 → 速度变化
    print(f"第 {i} 个小步后：加速度 {acceleration:6.2f} m/s²，速度 {speed:.3f} m/s")
```

输出：

```text
第 1 个小步后：加速度  -8.33 m/s²，速度 24.444 m/s
第 2 个小步后：加速度  -7.41 m/s²，速度 23.951 m/s
第 3 个小步后：加速度  -6.58 m/s²，速度 23.512 m/s
```

运行方法：终端输入 `python` 进入交互模式，粘贴后按回车；或存成 `outputs/try.py` 再 `python outputs/try.py`（`outputs/` 不进 Git）。

记住 **23.512** 这个数。1.5 的实验里，目标改成 20 之后 0.2 秒，模拟器显示的实际速度正好是 23.51。你这 7 行代码，就是模拟器在一次 `env.step()` 里做的事情。

<details>
<summary>▶ 完整的 Vehicle.step()：位置、朝向和速度一起更新</summary>

> **源码摘录** `highway_env/vehicle/kinematics.py` · `Vehicle.step`

```python
def step(self, dt: float) -> None:
    self.clip_actions()                       # 限制控制量；撞车后改为刹停
    delta_f = self.action["steering"]         # 前轮转向角（弧度）
    beta = np.arctan(1 / 2 * np.tan(delta_f)) # 车身侧偏角（自行车模型）
    v = self.speed * np.array(
        [np.cos(self.heading + beta), np.sin(self.heading + beta)]
    )                                         # 世界坐标下的速度向量
    self.position += v * dt                   # 先用旧速度推进位置
    if self.impact is not None:
        self.position += self.impact
        self.crashed = True
        self.impact = None
    self.heading += self.speed * np.sin(beta) / (self.LENGTH / 2) * dt
    self.speed += self.action["acceleration"] * dt   # 再更新速度
    self.on_state_update()                    # 重新判断自己在哪条车道
```

- `position`：世界坐标，米。`heading`：车头朝向，弧度。`speed`：沿车头方向的速度大小，m/s。
- 直路、不转向时 `delta_f = 0`，`beta = 0`，就只剩“位置 += 速度 × dt”和“速度 += 加速度 × dt”。
- 转向那部分（自行车模型）在第 3 章用到。

</details>

### 1.4 `env.step()` 把“控制”和“运动”接起来

平时你只写 `env.step(action)`，从来没手动调过控制器。是环境替你组织了这些调用。

> **教学简化** `highway_env/envs/common/abstract.py` · `AbstractEnv.step` 和 `_simulate`（删掉了渲染和手动驾驶分支）

```python
def step(self, action):
    self.time += 1 / self.config["policy_frequency"]   # 仿真时间前进一步
    self._simulate(action)                             # ① 推进若干物理小步
    obs = self.observation_type.observe()              # ② 生成新的观察表
    reward = self._reward(action)
    terminated = self._is_terminated()                 # 撞车等 → 回合结束
    truncated = self._is_truncated()                   # 到时间上限 → 回合截断
    info = self._info(obs, action)
    return obs, reward, terminated, truncated, info

def _simulate(self, action):
    frames = self.config["simulation_frequency"] // self.config["policy_frequency"]
    for frame in range(frames):                        # 本章：15 // 5 = 3 个小步
        if frame == 0:                                 # （原代码用 steps 取余判断）
            self.action_type.act(action)               # 把高层动作交给自车：改目标
        self.road.act()                                # 所有车：根据当前状态算控制量
        self.road.step(1 / self.config["simulation_frequency"])  # 所有车：运动 dt 秒，再查碰撞
        self.steps += 1
```

读这段代码要抓住三点：

1. **动作只在第一个小步交给车辆**，作用是改目标。
2. **每个小步都会 `road.act()`**：控制器每次都用最新的实际速度重新算加速度。
3. 所以即使你一直发 `IDLE`（“保持目标不变”），**控制器也没停**，它一直在把实际速度往目标拉。

这里有两层“反馈”，别混在一起：

- **控制层反馈**：控制器根据实际速度修正加速度（本章就是这个）。
- **决策层反馈**：策略根据新的路况重新选动作（第 2 章的跟车规则）。

<details>
<summary>▶ 为什么发 IDLE 不会把目标改回去？</summary>

> **源码摘录** `highway_env/vehicle/controller.py` · `MDPVehicle.act`

```python
def act(self, action: Union[dict, str] = None) -> None:
    if action == "FASTER":
        self.speed_index = self.speed_to_index(self.speed) + 1
    elif action == "SLOWER":
        self.speed_index = self.speed_to_index(self.speed) - 1
    else:                       # IDLE、变道、或 road.act() 传来的 None
        super().act(action)     # → ControlledVehicle.act：不改目标速度，只算控制量
        return
    self.speed_index = int(np.clip(self.speed_index, 0, self.target_speeds.size - 1))
    self.target_speed = self.index_to_speed(self.speed_index)
    super().act()
```

只有 `FASTER` / `SLOWER` 会重新选目标速度档位，而且是**以实际速度为基准**找最近的档位再加减一档。`IDLE` 直接走 `else`，目标保持原样。

</details>

### 1.5 动手：目标一下子变了，车速怎样跟上？

运行：

```powershell
python experiments\highway_driving\demos\04_target_speed.py
```

窗口上半部分是道路，下半部分是速度曲线：橙线是目标速度，绿线是实际速度。整段仿真 8 秒。

**按键**：空格 暂停/继续，R 重播，Esc 关闭。

先看这三件事：

1. **0–2 秒**：目标和实际都是 25，两条线重合（绿线会盖住橙线）。
2. **第 2 秒**：橙线**竖直**掉到新目标；绿线没有跳，而是开始往下弯。
3. **之后**：绿线越来越贴近橙线，下降越来越慢——这就是 1.3 里“先快后慢”。

脚本里真正和本章有关的只有这几行：

> **源码摘录** `04_target_speed.py`

```python
TARGET_SPEED = 20.0   # 文件顶部：你要改的就是这个（m/s，原版 20）

if steps == 10:       # 已经 step 了 10 次 = 第 2 秒
    env.unwrapped.vehicle.target_speed = float(target_speed)   # 只改目标
    record("target_changed")                                    # 此刻速度还没变
_, _, terminated, truncated, _ = env.step(idle)                 # 推进 0.2 秒
steps += 1
record("motion")                                                # 现在速度才变
```

其余代码都是画窗口和曲线，不用读。

> 这里直接改了车辆内部的 `target_speed`，是为了单独观察控制器。正常的策略应该通过动作（`SLOWER`）来改目标，第 2 章就是这样做的。

**▶ 自己改一处**

1. 先预测：把目标从 20 改成 10，橙线和绿线会怎样？绿线会更陡还是更缓？
2. 打开 [04_target_speed.py](../experiments/highway_driving/demos/04_target_speed.py)，把顶部改成 `TARGET_SPEED = 10.0`，保存。
3. 关掉旧窗口，重新运行同一条命令。（R 键只重播当前进程，不会读你刚保存的文件。）

<details>
<summary>▶ 对答案（实测，HighwayEnv 1.12.1）</summary>

| 仿真时间 | 目标 20 时的实际速度 | 目标 10 时的实际速度 |
| --- | --- | --- |
| 2.0 秒 | 25.000 | 25.000 |
| 2.2 秒 | 23.512 | 20.535 |
| 2.6 秒 | 21.732 | 15.197 |
| 3.0 秒 | 20.854 | 12.563 |
| 4.0 秒 | 20.146 | 10.438 |
| 8.0 秒 | 20.000 | 10.000 |

目标 10 时差值更大，所以一开始减速更猛（第一个小步加速度 −25 m/s²），曲线更陡；之后同样“先快后慢”地贴近目标。

−25 m/s² 远超真实汽车的刹车能力（一般最大 −8 到 −10 m/s² 左右）。这个简化控制器没有限制加速度，所以它只用来理解原理，不代表真实车辆能这样刹。

</details>

### 1.6 本章小结

- 改目标 ≠ 改实际。目标是一条要求，实际要靠时间推进才变化。
- 控制器（`speed_control`）：（目标 − 实际）× 系数 → 加速度，只算不动。
- 运动模型（`Vehicle.step`）：速度 += 加速度 × dt，这时才真正动。
- 一次 `env.step()` = 若干物理小步；每个小步都“先算控制，再运动”。所以一直发 `IDLE`，车也会继续向目标靠拢。

<details>
<summary>▶ 自测（想好再展开）</summary>

**1. 目标从 25 改成 20 的那一刻（还没调 `env.step`），实际速度是多少？**
还是 25。改目标只是给变量赋值；速度要等 `env.step()` 里的控制器和运动模型执行后才变。

**2. 控制器算出 −8.33 m/s²，经过一个 1/15 秒的小步，速度降多少？**
8.33 × 1/15 ≈ 0.556 m/s，从 25 变成约 24.444。

**3. 为什么一直发 IDLE，车速还能继续向目标靠近？**
IDLE 只表示“不改目标”。每个物理小步 `road.act()` 都会让控制器用当前速度和目标重新算加速度，所以控制一直在工作。

</details>

---

<a id="chapter-02"></a>

## 第 2 章｜前车慢了，程序怎样做出反应？

第 1 章的目标是我们手动设的。这一章让程序自己决定：**从观察表里找到前车，按距离选加速、保持或减速。** 这就是一个最简单的驾驶策略，也是第一次真正的“闭环”。

### 2.1 先运行，看十几秒

```powershell
python experiments\highway_driving\demos\00_following.py
```

窗口看车，终端看每一轮的打印：

```text
决策前仿真时间： 7.0 秒
本轮判断用的前车距离： 35.0 米
前车太近，减速
执行后仿真时间： 8.0 秒
执行后实际速度： 86.4 公里/小时
执行后目标速度： 72.0 公里/小时
```

（上面是格式示意，你的数字会不一样。）留意一件事：程序选了减速以后，**实际速度是不是马上等于目标速度？** 不是——这就是第 1 章讲的。

停止：回到终端按 Ctrl+C。程序会告诉你停在第几局、这一局有没有结束。

整个程序在做这件事：

```text
观察表 → 找出同车道最近的前车 → 按距离选动作 → env.step 推进 1 秒 → 新的观察表 → ……
```

这个程序没有摄像头。观察表直接来自模拟器内部的车辆状态，相当于“感知已经完美完成”。真实车辆要从图像里识别出这些车，那是以后的内容。

### 2.2 观察是一张表，每行一辆车

```python
obs, info = env.reset(seed=SEED)
```

默认配置下，`obs` 是 5 行 × 5 列的表，每行的 5 列是：

```text
[presence, x, y, vx, vy]
  有没有车  纵向位置 横向位置 纵向速度 横向速度
```

先用换算成米的数字来理解（下一节再讲表里实际存的小数）：

| 行 | presence | 表示什么 | 能当跟车对象吗 |
| --- | --- | --- | --- |
| 0 | 1 | **自己的车** | 跳过 |
| 1 | 1 | 前方 35 米，横向差 0 米 | 可以 |
| 2 | 1 | 前方 20 米，横向差 4 米 | 不行，在旁边车道 |
| 3 | 1 | 前方 70 米，横向差 0 米 | 可以，但比第 1 行远 |
| 4 | 0 | **空行**，没有车 | 跳过 |

两点要注意：

- `presence = 0` 的行是填充的空位。它的 x、y 都是 0，不代表“原点停着一辆车”。
- 表只有 5 行：自己 1 行 + 最多 4 辆其他车。默认场景有 50 辆车，表里只放离你最近的几辆（默认只看前方，以及紧贴在身后的车）。**行号也不是车的身份证**，这一轮第 1 行和下一轮第 1 行可能是两辆不同的车。

### 2.3 为什么代码里要乘 200 和 16

如果表里某辆车的 `x` 是 `0.175`，它不是在前方 0.175 米，而是 **35 米**。默认配置会把物理量缩放到 −1 到 1 之间，这叫**归一化**：

| 列 | 缩放前的范围 | 还原公式 |
| --- | --- | --- |
| `x` | −200 ～ 200 米 | `x * 200` |
| `y` | −16 ～ 16 米（4 车道 × 4 米宽） | `y * 16` |
| `vx`、`vy` | −80 ～ 80 m/s | `* 80` |

所以原脚本这样还原：

```python
distance = x * 200       # 纵向距离，米
side_distance = y * 16   # 横向距离，米
```

**归一化还会丢信息。** 默认 `clip=True`：超出范围的值会被截到 ±1。比如一辆车在 260 米外，260 / 200 = 1.3，被截成 1.0，还原回来只有 200。所以看到 `x = 1.0`，你只能说“至少 200 米”。

> **可以直接运行**

```python
for physical_x_m in (35.0, 200.0, 260.0):
    normalized_x = physical_x_m / 200.0
    clipped_x = max(-1.0, min(1.0, normalized_x))
    print(physical_x_m, "→", clipped_x, "→", clipped_x * 200.0)
```

输出 `35.0 → 0.175 → 35.0`、`200.0 → 1.0 → 200.0`、`260.0 → 1.0 → 200.0`。最后一行就是被截掉的信息。

**200 和 16 只对这个配置成立。** 换成 3 车道，y 的范围变成 ±12；关掉归一化（`normalize=False`），表里本来就是米，再乘 200 就错了。第 4 章的实验就是关掉归一化的。

### 2.4 “相对位置”只是做减法

默认 `absolute=False`：其他车的数值是**对方减自己**。

自车在世界坐标 (100, 4)，另一辆车在 (135, 4)，表里就记 (35, 0)。速度也一样：对方 20 m/s、自己 25 m/s，表里 `vx` 记 −5（归一化后 −5/80 = −0.0625）。**负数表示它比你慢，不是在倒车。**

两个容易踩的坑：

1. **第 0 行（自车）不是相对量**，而是自车自己的世界坐标和速度（再归一化）。所以第 0 行不会是全 0；自车开出 200 米后，它的 x 也会被截成 1。
2. **坐标轴没有跟着车头转**，只是平移了一下。现在道路正好沿世界 x 轴，所以“x 为正 = 在前面”成立。到了弯道，这个判断就不可靠了。

### 2.5 从几辆车里找出最近的前车

> **源码摘录** `00_following.py`

```python
nearest_distance = float('inf')            # 先当作“没看到前车”

for presense, x, y, vx, vy in obs[1:]:     # obs[1:] 跳过第 0 行（自己）
    distance = x * 200
    side_distance = y * 16
    if presense == 1 and distance > 0 and abs(side_distance) < 2:
        nearest_distance = min(nearest_distance, distance)
```

（`presense` 是原练习的拼写，和 `presence` 是一回事。）

筛选条件翻译成人话：**这一行有车、在我前面、横向差不到半个车道（2 米）**。

用 2.2 的表走一遍：35 米 → 记下；20 米那辆横向差 4 米 → 跳过；70 米 → `min(35, 70)` 还是 35；空行 → 跳过。结果是 **35 米**。

`float('inf')` 的意思是“还没找到前车”，不是“前车在无穷远”。

<details>
<summary>▶ 想看清每一行是怎么被筛掉的？加一行打印</summary>

在循环里 `side_distance = y * 16` 后面加（缩进对齐）：

```python
print("候选：", presense, "纵向", round(distance, 1), "米；横向", round(side_distance, 1), "米")
```

运行两轮后 Ctrl+C，对照着看哪些行被排除了。看清后可以删掉，不然终端太密。注意加在**当前生效**的循环里，不要加到三引号包起来的旧代码里。

</details>

### 2.6 距离怎样变成动作

> **源码摘录** `00_following.py`

```python
if nearest_distance < 40:
    action = 4                    # SLOWER
    decision = "前车太近，减速"
elif nearest_distance > 60:
    action = 3                    # FASTER
    decision = "前方距离充足，加速"
else:
    action = 1                    # IDLE
    decision = "保持当前目标速度"
```

35 米 → 减速；50 米 → 保持；70 米 → 加速。正好 40 或 60 米也是保持。

这几个整数的意思由动作配置决定（第 3 章细讲）：

| `action` | 名称 | 实际效果 |
| --- | --- | --- |
| 4 | `SLOWER` | 目标速度降一档 |
| 3 | `FASTER` | 目标速度升一档 |
| 1 | `IDLE` | 目标不变 |

本实验把档位设成 `[0, 5, 10, 15, 20, 25, 30]` m/s。以实际速度为基准找最近一档再升降，例如实际 25 时 `SLOWER` 把目标设成 20。**发出 4 的瞬间，速度不会变成 20**——之后由控制器慢慢降。

**▶ 自己改一处：把减速距离从 40 改成 50**

1. 先预测：前车 45 米时，原规则选什么？新规则选什么？
2. 在 [00_following.py](../experiments/highway_driving/demos/00_following.py) 里，把**当前生效的**这一行（不是三引号里的旧代码）：
   ```python
   if nearest_distance < 40:
   ```
   改成：
   ```python
   if nearest_distance < 50:
   ```
3. 其他不动，保存后重新运行。对比两次第一局：**第一次出现不同动作是在哪一轮**，之后速度怎样变化。

种子固定为 0，所以两次的起点完全一样。但只要某一轮动作不同，之后车的位置就不同，后面看到的距离也就不同了——不能拿后面的两行当作“同一个输入”对比。

<details>
<summary>▶ 不想受交通变化干扰？只对比规则本身</summary>

> **可以直接运行**（纯逻辑，不启动模拟器）

```python
def choose_action(distance_m, slow_below_m):
    if distance_m < slow_below_m:
        return "SLOWER"
    elif distance_m > 60:
        return "FASTER"
    return "IDLE"

for d in (35, 45, 50, 60, 70, float("inf")):
    print(d, choose_action(d, 40), "→", choose_action(d, 50))
```

45 米从 IDLE 变成 SLOWER；50 米仍是 IDLE（条件是 `<`）；`inf` 两边都是 FASTER——改阈值没有解决“看不到车就加速”的问题。

</details>

### 2.7 一轮打印里，距离和速度不是同一时刻

> **源码摘录** `00_following.py`

```python
print("决策前仿真时间：", round(env.unwrapped.time, 1), "秒")
print("本轮判断用的前车距离：", round(nearest_distance, 1), "米")
print(decision)

obs, reward, terminated, truncated, info = env.step(action)   # 推进 1 秒

print("执行后仿真时间：", round(env.unwrapped.time, 1), "秒")
print("执行后实际速度：", round(info["speed"] * 3.6, 1), "公里/小时")
```

时间线是这样的：

```text
第 7 秒的观察 → 找到前车 35 米 → 选 SLOWER
                    ↓
          env.step(action)：模拟器内部跑 15 个物理小步，共 1 秒
                    ↓
第 8 秒的新观察、实际速度、奖励、是否结束
                    ↓
下一轮用第 8 秒的观察重新找前车
```

所以同一组打印里，**距离是动作前的，速度是动作后的**。分析“为什么在这里减速”时，要看动作前的距离，不能拿动作后的位置去解释。

这就是**闭环**：这一轮的动作改变了车的位置，下一轮的观察因此不同，策略再根据新观察做决定。

### 2.8 这个规则有哪些问题

这个规则能跑，但很粗糙。看懂它的毛病，比记住它的代码更重要：

1. **只看距离，不看速度差。** 两辆前车都在 50 米：一辆和你同速，一辆比你慢 10 m/s。规则对两者都“保持”。可第二辆 1 秒后就只剩 40 米了。标题是“前车慢了”，但当前代码其实没有用 `vx`。
2. **“没看到车”被当成“安全”。** `nearest_distance` 是 `inf` 时，`inf > 60` 成立，规则会加速。但 `inf` 可能只是因为表里只有 4 辆车、或者筛选条件漏掉了车。
3. **横向差 < 2 米不等于同一车道。** 正在变道、压线的车可能被误判。
4. **距离是车中心之间的距离**，没有扣掉车长（约 5 米）。
5. **没考虑控制器减速需要时间。** 发了 `SLOWER` 后，速度要过一会儿才降下来。

如果车撞了，按时间往回查：撞之前几轮，规则看到的距离是多少？选了什么动作？目标降了没有？实际速度降得够不够快？这样一步步定位，才知道该改规则的哪一处。

**奖励（reward）** 是环境按自己的规则打的分：默认奖励鼓励开得快、靠右、不撞车。分数高不等于开得安全，第 4 章再讲。

默认环境一局最长 40 秒，撞车也会提前结束。脚本结束一局后打印成绩，再用同一个种子开下一局，所以**每一局的起点都一样**——跑 7 局不等于测了 7 种路况。

### 2.9 本章小结

- 观察表默认 5 行：第 0 行是自己（绝对量），其余是附近车辆（相对量），空行 presence = 0。
- 默认归一化：x 乘 200、y 乘 16 才是米；超出范围的值被截断，信息会丢。
- 规则：找同车道最近的前车 → 按 40 / 60 米选动作 → `env.step` → 用新观察再判断。这就是闭环。
- 同一轮打印里，距离是动作前的，速度是动作后的。
- 当前规则只看距离、把“没看到”当成安全，这是第 4 章和阶段 2 要改进的地方。

<details>
<summary>▶ 自测（想好再展开）</summary>

**1. 默认配置下，观察表某行是 `[1, 0.175, 0.0, -0.0625, 0]`，这辆车在哪、怎么动？**
在你前方约 35 米、同一车道（横向差 0），比你慢 5 m/s。

**2. 看到 `x = 1.0`，能说这辆车正好在 200 米处吗？**
不能。超出范围的值被截到 1，只能说“至少 200 米”。

**3. 规则打印“前方距离充足，加速”，前面一定没车吗？**
不一定。可能是 `inf`：表里只放了最近几辆车，筛选条件也可能漏掉车。规则把“没看到”当成了“安全”。

</details>

---

<a id="chapter-03"></a>

## 第 3 章｜一个变道指令怎样变成真正的运动？

第 1 章是纵向：目标速度 → 实际速度。这一章换成横向：**目标车道 → 实际横向位置。** 道理一样：目标可以立刻变，车要靠一段时间的运动才能过去。

### 3.1 先运行，看一次变道

```powershell
python experiments\highway_driving\demos\01_lane_change.py
```

场景：四车道直路，没有其他车。车道从左到右编号 0、1、2、3，自车从 1 号车道出发。前两次决策发 `IDLE`，**第 3 次发一次“向右变道”**，之后又全是 `IDLE`。仿真到 10 秒结束。

决定什么时候发指令的只有这几行：

> **教学简化** `01_lane_change.py`（省略了部分打印和结束判断）

```python
for step in range(10):          # step 从 0 开始数
    if step == 2:               # 第 3 次决策
        action = 2              # LANE_RIGHT
    else:
        action = 1              # IDLE
    obs, reward, terminated, truncated, info = env.step(action)
    print("行动后目标车道编号：", vehicle.target_lane_index[2])
    print("行动后横向位置 y：", round(float(vehicle.position[1]), 2), "米")
```

看终端：第 3 次之后目标车道变成 2；**第 4 次明明发的是 IDLE，车还在继续往右移**。为什么？下面三节解释。

先统一单位：车道宽 4 米，所以 **1 号车道中心 y = 4 米，2 号车道中心 y = 8 米**。车道编号不是米，“编号 2”不等于“y = 2”。这里的 y 是车辆内部的世界坐标（米，未归一化），和第 2 章观察表里归一化过的 y 不是一回事。

> 你在 HighwayEnv 仓库的 `learning/demos/01_lane_change.py` 还有一份自己改过的副本（有 5 辆背景车），那份用于源码阅读练习，和这里讲的无车版本不是同一个设置。

### 3.2 动作编号只在当前配置下有意义

`highway-v0` 默认动作类型是 `DiscreteMetaAction`（高层离散动作），动作表是：

> **源码摘录** `highway_env/envs/common/action.py` · `DiscreteMetaAction`

```python
ACTIONS_ALL = {0: "LANE_LEFT", 1: "IDLE", 2: "LANE_RIGHT", 3: "FASTER", 4: "SLOWER"}
```

所以本实验里 `2` 是右变道。但**整数本身没有固定含义**：

- 如果只开纵向动作，编号变成 `{0: SLOWER, 1: IDLE, 2: FASTER}`，2 就是加速。
- 如果换成 `DiscreteAction`，编号代表的是一组离散的“加速度 + 转向角”组合。

`env.action_space.contains(4)` 只回答“4 是不是合法编号”，不回答“现在减速合不合理”。

<details>
<summary>▶ HighwayEnv 的四种动作类型对比</summary>

| 动作类型 | 策略交出什么 | 车辆收到什么 | 例子 |
| --- | --- | --- | --- |
| `DiscreteMetaAction` | 一个整数 | 高层指令：改目标车道或目标速度，由控制器去追 | 本章的 2 = 右变道 |
| `ContinuousAction` | 两个 −1～1 的小数 | 直接映射成加速度和转向角 | `[0.5, -0.2]` → 2.5 m/s²、−0.157 弧度 |
| `DiscreteAction` | 一个整数 | 从“加速度 × 转向角”网格里选一个组合 | 默认每轴 3 档，共 9 种组合 |
| `MultiAgentAction` | 每辆受控车一个动作 | 分发给各自的车 | 打包本身不代表会协同 |

本章用的是第一种：**策略只说“我要去右边那条道”，具体怎么打方向盘由控制器负责。** 想对比“直接给控制量”的方式，见本章末尾的 3.6。

</details>

### 3.3 变道指令先改的是“目标车道”

动作接口这一层非常薄，只是把编号翻译成名字，交给车辆：

> **源码摘录** `highway_env/envs/common/action.py` · `DiscreteMetaAction.act`

```python
def act(self, action: int | np.ndarray) -> None:
    self.controlled_vehicle.act(self.actions[int(action)])   # 2 → "LANE_RIGHT"
```

车辆收到 `"LANE_RIGHT"` 后：

> **源码摘录** `highway_env/vehicle/controller.py` · `ControlledVehicle.act`（右变道分支 + 结尾）

```python
elif action == "LANE_RIGHT":
    _from, _to, _id = self.target_lane_index            # 当前的目标车道
    target_lane_index = (
        _from,
        _to,
        np.clip(_id + 1, 0, len(self.road.network.graph[_from][_to]) - 1),   # 编号 +1，不越出道路
    )
    if self.road.network.get_lane(target_lane_index).is_reachable_from(self.position):
        self.target_lane_index = target_lane_index      # ← 只改了目标

action = {
    "steering": self.steering_control(self.target_lane_index),   # 转向角（弧度）
    "acceleration": self.speed_control(self.target_speed),       # 加速度（m/s²）
}
super().act(action)                                     # 保存控制量，等运动模型使用
```

两个要点：

1. **被赋值的是 `target_lane_index`，不是 `position`。** 指令发出的那一刻，车还在原地。
2. 后半段的 `action` 字典才是真正的**控制量**：转向角和加速度。它和最开始的整数 `2` 已经不是一个层次了——`2` 说的是“我要去右边”，字典说的是“接下来这一小段时间方向盘打多少”。

为什么第 4 次发 `IDLE` 车还在动？`IDLE` 不进入任何改目标的分支，但**照样会执行结尾那段控制计算**。目标车道已经是 2，控制器就继续把车往 2 号车道拉。

两个延伸：

- **连续发 `LANE_RIGHT`** 会在“当前目标”基础上再 +1，目标可能变成 3 号车道。这不是“更快完成这次变道”，而是“换个更右的目标”。
- `is_reachable_from` 只检查道路几何（目标车道存在、够得着），**不检查旁边有没有车**。`get_available_actions()` 也一样。判断“现在变道安不安全”是策略的事。

**▶ 自己改一处：把变道推迟两次**

1. 先预测：如果右变道从第 3 次推迟到第 5 次，第 3～6 次打印的目标车道和 y 会怎样？
2. 在 [01_lane_change.py](../experiments/highway_driving/demos/01_lane_change.py) 里把 `if step == 2:` 改成 `if step == 4:`，顺手把旁边注释的“第 3 次”改成“第 5 次”。
3. 其他不动，保存后重新运行，对照你的预测。

<details>
<summary>▶ 对答案（实测，HighwayEnv 1.12.1，无其他车辆）</summary>

| 第几次决策 | 原版动作 | 原版：目标车道 / y（米） | 改后动作 | 改后：目标车道 / y（米） |
| --- | --- | --- | --- | --- |
| 1 | IDLE | 1 / 4.000 | IDLE | 1 / 4.000 |
| 2 | IDLE | 1 / 4.000 | IDLE | 1 / 4.000 |
| 3 | **RIGHT** | 2 / 7.408 | IDLE | 1 / 4.000 |
| 4 | IDLE | 2 / 7.954 | IDLE | 1 / 4.000 |
| 5 | IDLE | 2 / 7.997 | **RIGHT** | 2 / 7.408 |
| 6 | IDLE | 2 / 8.000 | IDLE | 2 / 7.954 |

推迟只改变了“什么时候开始”，变道过程本身一模一样，只是整体晚了 2 秒。

注意表里的 y 是**每次 `env.step()` 结束时**（已经过了 1 秒）的位置。所以第 3 次那一行 y 已经是 7.408，不是说“改目标的那行代码把车搬到了 7.408”。打印保留两位小数时 7.997 会显示成 8.0，也不代表已经精确到达。

</details>

### 3.4 控制器为什么同时看“位置”和“车头朝向”

车在 y = 4，目标中心 y = 8。如果控制器只想着“往右”，车头会一直斜着，冲过 8 米继续往外跑。所以它要同时管两件事：

1. **横向位置**：离目标车道中心还差多少？
2. **车头朝向**：车头是不是已经该摆正了？

`steering_control` 按这四步算转向角：

```text
① 离目标车道中心差多少米         → ② 希望的横向速度（差越多越大）
                                  → ③ 希望的车头朝向（道路方向 + 偏一点）
④ 希望朝向 − 实际朝向            → 转向角
```

前两步的源码：

> **源码摘录** `highway_env/vehicle/controller.py` · `ControlledVehicle.steering_control`（开头）

```python
target_lane = self.road.network.get_lane(target_lane_index)
lane_coords = target_lane.local_coordinates(self.position)   # [沿车道走了多远, 离中心线多远]
lane_next_coords = lane_coords[0] + self.speed * self.TAU_PURSUIT   # 往前看一点
lane_future_heading = target_lane.heading_at(lane_next_coords)      # 前方道路的方向

lateral_speed_command = -self.KP_LATERAL * lane_coords[1]   # 横向偏差 → 横向速度
```

`lane_coords[1]` 是相对**目标车道中心线**的横向偏差（米）。车在 y = 4、目标中心 y = 8 时，它是 −4；前面的负号把它变成“向右修正”。越靠近中心，偏差越小，修正越小。

车头朝向的比较：

```python
heading_rate_command = self.KP_HEADING * utils.wrap_to_pi(heading_ref - self.heading)
```

已经快到中心时，横向偏差很小，但车头可能还朝右斜着。这一项会让控制器反过来打方向，把车头摆正。所以变道的轨迹是一条平滑的 S 形，而不是冲过头再拉回来。

<details>
<summary>▶ 完整公式：横向速度 → 朝向 → 转向角</summary>

> **源码摘录** `highway_env/vehicle/controller.py` · `ControlledVehicle.steering_control`（后半段）

```python
# 横向速度 → 希望的车头偏角（限制在 ±45°）
heading_command = np.arcsin(
    np.clip(lateral_speed_command / utils.not_zero(self.speed), -1, 1)
)
heading_ref = lane_future_heading + np.clip(heading_command, -np.pi / 4, np.pi / 4)
# 朝向误差 → 希望的转动速度
heading_rate_command = self.KP_HEADING * utils.wrap_to_pi(heading_ref - self.heading)
# 转动速度 → 前轮转向角（自行车模型的反算）
slip_angle = np.arcsin(
    np.clip(
        self.LENGTH / 2 / utils.not_zero(self.speed) * heading_rate_command,
        -1,
        1,
    )
)
steering_angle = np.arctan(2 * np.tan(slip_angle))
steering_angle = np.clip(steering_angle, -self.MAX_STEERING_ANGLE, self.MAX_STEERING_ANGLE)
return float(steering_angle)
```

- `wrap_to_pi`：把角度差换算到 −π～π，避免把“转一点点”误算成“转一大圈”。
- `not_zero`：防止除以零。
- 系数（本机默认）：`KP_LATERAL ≈ 1.667`，`KP_HEADING = 5`，`TAU_PURSUIT = 0.1` 秒，`MAX_STEERING_ANGLE = π/3`。
- 这是简化控制器，在极低速、急弯等情况下不一定可靠。

</details>

### 3.5 运动模型推进之后，位置才改变

控制量算出来以后，由基础车辆保存：

> **源码摘录** `highway_env/vehicle/kinematics.py` · `Vehicle.act`

```python
def act(self, action: dict | str = None) -> None:
    if action:
        self.action = action     # 只是保存，还没动
```

真正改位置的是第 1 章见过的 `Vehicle.step(dt)`。转向时这三行都在起作用：

```python
self.position += v * dt          # v 由速度和（车头朝向 + 侧偏角）决定
self.heading += self.speed * np.sin(beta) / (self.LENGTH / 2) * dt
self.speed += self.action["acceleration"] * dt
```

本实验决策频率 1 Hz，一次 `env.step()` = 15 个 1/15 秒的物理小步。**车不是静止 1 秒后瞬间跳到新位置**，而是这 15 个小步里每一步都“重新算转向 → 移动一点”。

和第 1 章一样，这里也有两层：控制器每个小步都在用实际位置和朝向修正（控制层反馈）；但**脚本发变道的时机是写死的**，并没有看路况（没有决策层反馈）。所以这次变道顺利，只说明“执行”没问题，不说明程序会判断“什么时候能安全变道”。

### 3.6 对照：直接给控制量是什么样

<details>
<summary>▶ 连续动作实验 03_continuous_action.py（可选）</summary>

前面的 `LANE_RIGHT` 是“给目标，让控制器去追”。另一种方式是**直接给控制量**：

```powershell
python experiments\highway_driving\demos\03_continuous_action.py
```

> **源码摘录** `03_continuous_action.py`

```python
env = gym.make(
    "highway-v0",
    config={
        "action": {"type": "ContinuousAction"},   # 连续动作
        "vehicles_count": 0,
        "policy_frequency": 1
    },
)
...
    env.reset(seed = 0)

    action = np.array([0.5,-0.2],dtype=np.float32)   # [加速度输入, 转向输入]，都在 −1～1

    # 读取模拟器内部信息，仅用于验证源码
    control = env.unwrapped.action_type.get_action(action)   # 看看映射成了什么
    ...
    obs, reward, terminated, truncated, info = env.step(action)
```

默认映射：第一维 −1～1 → 加速度 −5～5 m/s²；第二维 −1～1 → 转向角 −π/4～π/4 弧度。所以 `[0.5, -0.2]` → 加速度 2.5 m/s²、转向角约 −0.157 弧度。

这里没有“目标车道”，这组控制量会在这 1 秒里一直保持，车不会自动回到车道中心。两种动作接口职责不同：一个说“去哪”，一个说“怎么打方向盘”。

</details>

### 3.7 本章小结

- 动作编号的含义由配置决定；本实验 `2 = LANE_RIGHT`。
- 变道指令只改 `target_lane_index`（目标车道），不直接改位置。
- `ControlledVehicle.act` 每次都会算控制量（转向角 + 加速度），`IDLE` 也不例外，所以变道会一直执行到位。
- 转向控制同时看横向偏差和车头朝向，才能平滑地进入新车道。
- 运动模型在每个物理小步里更新位置、朝向、速度。
- 车道“可达”只是几何检查，不检查邻车——安全判断是策略的事。

<details>
<summary>▶ 自测（想好再展开）</summary>

**1. 动作编号 2 永远代表右变道吗？**
不是。只有在 `DiscreteMetaAction` 且纵向、横向动作都启用时才是。只开纵向时 2 是 `FASTER`。

**2. 第 3 次发右变道、第 4 次发 IDLE，为什么第 4 次车还在往右移？**
第 3 次已经把目标车道改成 2。IDLE 不改目标，但控制器每个小步都继续算转向，把车往目标车道拉。

**3. 连续三次发 LANE_RIGHT 会怎样？**
每次都在当前目标车道的编号上 +1（受道路边界限制），目标可能变成更右的车道，而不是让这次变道更快完成。

</details>

---

<a id="chapter-04"></a>

## 第 4 章｜这次没撞，是改好了，还是路况刚好容易？

假设你把第 2 章的减速距离从 40 改成 50，跑了一局，没撞。是改好了吗？

不一定。可能这一局的交通本来就简单。这一章讲怎样**公平地比较**一次修改：固定起点、完整记录、先看结束原因、分开看不同指标。

### 4.1 公平比较要先固定什么

你训练模型时会固定随机种子。驾驶实验也要，但只固定种子不够。**“同条件”至少包括**：

- 同样的模拟器和代码版本
- 同样的配置（车道数、车辆数、时长、频率……）
- 同样的种子，因此同样的初始观察

两组实验**只有起点相同**。一旦动作不同，车的位置就不同，后面的观察也不同——这正是我们要比较的结果。

本章用项目里现成的记录器 [`run_episode.py`](../experiments/highway_driving/run_episode.py) 做一个最小对照：一组一直 `IDLE`，一组一直 `SLOWER`。这个记录器目前只支持“每步发同一个动作”，还不能接第 2 章的跟车规则；本章先学比较方法，到阶段 2 再接上真正的策略。

### 4.2 动手：生成一页对照报告

```powershell
python experiments\highway_driving\demos\05_compare_actions.py
```

它会真实跑两次仿真，保存回放、日志和一页 `report.html`，并尝试用浏览器打开。没自动打开的话，终端会打印报告路径。每次运行都保存到新的 `outputs/highway_driving/compare-actions/<时间>/` 目录，旧报告不会被覆盖。

设置：种子 7，**没有其他车辆**，每组最多 40 步（每步 0.2 秒，共 8 秒），目标速度档位 `[20, 25, 30]`。

页面左边是 `IDLE`，右边是 `SLOWER`，下面是两组的速度曲线。两张 GIF 各自循环，不保证同步；要对比同一时刻，看曲线。

先预测再运行：一直发 `SLOWER` 的那组，速度会降到多少？8 秒后比 `IDLE` 少走多少米？

<details>
<summary>▶ 对答案（实测，HighwayEnv 1.12.1）</summary>

| 组 | 最终速度 | 8 秒内 x 方向位移 | 结束原因 | 碰撞 |
| --- | --- | --- | --- | --- |
| IDLE | 25.0 m/s | 200.0 米 | `environment_time_limit` | 否 |
| SLOWER | 20.0 m/s | 163.0 米 | `environment_time_limit` | 否 |

`SLOWER` 最低只能降到 20，因为档位里最低就是 20。这和第 2 章（最低 0）不一样。所以这里的 `SLOWER` 不是紧急刹车。

</details>

### 4.3 日志为什么同时存“动作前”和“动作后”

记录器的核心是这两行：

> **源码摘录** `run_episode.py`

```python
observation_time_s = float(env.unwrapped.time)                    # 动作前的时间
next_obs, reward, terminated, truncated, info = env.step(action_id)  # 推进，得到动作后的观察
```

然后把动作前的观察和时间、动作、动作后的观察和时间，**写在同一条记录里**（`trace.jsonl` 的一行）。

这是为了避免第 2 章 2.7 的混淆：分析“为什么这一步选了减速”时，要看当时（动作前）的观察；分析“减速有没有效果”时，看动作后的。两者放在一行里，就不会对错时间。

### 4.4 先看结束原因，再看成绩

每一局停下来都有原因，`end_reason` 把它分清楚：

| `end_reason` | 发生了什么 | 怎么理解 |
| --- | --- | --- |
| `collision` | 撞车了 | 这局失败 |
| `off_road` | 开出了道路 | 回看动作和位置 |
| `terminated` | 环境的其他结束条件 | 查这个环境怎么定义的 |
| `environment_time_limit` | 跑满了环境规定的时长 | 跑完了，但还要结合其他指标看表现 |
| `runner_step_limit` | 脚本的步数预算用完了 | **是我们停止了观察**，环境本身没结束 |

最后两种最容易混：一个是“考试时间到了”，一个是“你提前交卷了”。只观察了 1 秒没撞，和跑满 8 秒没撞，不能放在一起比“安全程度”。

**▶ 自己改一处：缩短观察时间**

1. 先预测：每步 0.2 秒，只给 5 步，能看多久？结束原因会变成什么？
2. 打开 [05_compare_actions.py](../experiments/highway_driving/demos/05_compare_actions.py)，把顶部 `MAX_STEPS = 40` 改成 `MAX_STEPS = 5`，保存。
3. 重新运行，对比新旧两份报告：曲线在哪里停了？结束原因变了吗？

<details>
<summary>▶ 对答案（实测，HighwayEnv 1.12.1）</summary>

5 步 × 0.2 秒 = 1 秒。两组都在 1.0 秒停下，结束原因从 `environment_time_limit` 变成 `runner_step_limit`。曲线后面的空白表示“没有继续观察”，不是速度变成了 0。

| 组 | 最终速度 | 1 秒内 x 方向位移 |
| --- | --- | --- |
| IDLE | 25.000 m/s | 25.000 米 |
| SLOWER | 20.854 m/s | 22.487 米 |

改的是观察时长，不是驾驶行为，所以“没撞”在这里什么也说明不了。

</details>

### 4.5 奖励高，不等于开得好

`reward` 是环境按一张评分表打的分。`highway-v0` 默认奖励主要看三项：**开得快**（20～30 m/s 之间线性加分）、**靠右**、**没撞**。

这张评分表很重视速度。所以一个开得更快、更冒险的策略，分数可能更高。比较驾驶行为时，至少要把这几件事**分开**看：

- 有没有撞（安全）
- 走了多远、多快（效率）
- 有没有急加急减（舒适）

它们之间常常要取舍，不能用一个总分概括。

### 4.6 一个种子不够：调参场景和测试场景要分开

本章的零交通实验只够看“动作怎样影响速度”。想判断“50 米阈值比 40 米好”，需要：

1. **一批种子**（比如 50 个），每个种子跑一局，统计碰撞率、平均速度等。
2. **调参用的种子和最终测试用的种子分开**——和训练集 / 测试集一个道理。在测试种子上调参，结果会偏乐观。

这正是阶段 2 要做的批量评测。

<details>
<summary>▶ 可选：两个种子 + 12 辆车的终端对照</summary>

把下面的代码存成 `outputs/compare_two_seeds.py`，在项目根目录运行 `python outputs/compare_two_seeds.py`：

> **可以直接运行**

```python
import runpy

run_episode = runpy.run_path("experiments/highway_driving/run_episode.py")["run_episode"]

results = {"IDLE": [], "SLOWER": []}
for seed in (7, 11):
    for action in results:
        r = run_episode(seed=seed, max_steps=40, action_name=action, render_mode=None,
                        output_dir=None, duration_s=8.0, vehicles_count=12)
        results[action].append(r)
        print("种子", seed, action, r["end_reason"], "碰撞", r["crashed"],
              "仿真秒数", round(r["sim_time_s"], 2))

for action, runs in results.items():
    print(action, "碰撞局数：", sum(r["crashed"] for r in runs), "/", len(runs))
```

一共 2 个种子 × 2 个动作 = 4 局。碰撞率的分母是局数，不是步数。2 个种子只是演示方法，远不够下结论。

</details>

### 4.7 开环评测和闭环评测

这两个词以后会经常遇到：

- **开环评测（open-loop）**：拿一份已经录好的数据，让模型预测（比如“接下来 3 秒车会走到哪”），和录下来的真实答案比较。**模型的预测不会改变数据里接下来发生的事。**
- **闭环评测（closed-loop）**：把策略的输出真的交给环境执行，车的运动改变了之后的路况，策略再根据新路况决策，最后评价整段行为。

你做 NLP 时算的离线准确率，就是开环：模型答错一题，下一题不会因此变化。开车不一样：这一步刹晚了，下一步面对的就是更近的前车。**开环指标好，闭环不一定好**，因为小误差会一步步累积。

对照本书的实验：

| 实验 | 环境真的在推进吗 | 策略用了新观察吗 |
| --- | --- | --- |
| 第 4 章 05 对照（一直 IDLE / SLOWER） | 是 | 否，动作是固定的 |
| 第 2 章 00 跟车规则 | 是 | 是——这才是闭环策略 |

### 4.8 本章小结

- 公平比较 = 同版本 + 同配置 + 同种子。只有起点相同，动作之后本来就会分叉。
- 日志把动作前、动作后存在同一行，避免对错时间。
- 先看 `end_reason`：脚本停止观察（`runner_step_limit`）≠ 跑完全程（`environment_time_limit`）。
- 奖励是一张评分表，不等于安全或舒适；指标要分开看。
- 一个种子说明不了问题；调参场景和测试场景要分开。
- 开环：预测不影响后续数据；闭环：动作改变后续输入。

<details>
<summary>▶ 自测（想好再展开）</summary>

**1. `end_reason` 是 `runner_step_limit`，说明什么？**
脚本的步数预算用完，是我们停止了观察；环境本身并没有结束，不能算“跑完全程”。

**2. 开环和闭环评测最关键的区别是什么？**
闭环里，策略的输出会改变之后看到的输入；开环里不会。

**3. 改成 50 米后跑了一局没撞，能说明 50 比 40 好吗？**
不能。要在同一批种子上比较碰撞率等指标，而且调参用的种子和最后测试用的种子要分开。

</details>

---

<a id="appendix-a"></a>

## 附录 A｜一次 `env.step()` 的源码地图

这张表把前四章串成一条调用链，并对应到 [阶段 1 清单](../experiments/highway_driving/CURRENT_TASK.md) 的编号。读源码时可以拿它当导航。文件路径相对于 HighwayEnv 仓库的 `highway_env/` 目录。

```text
env.step(action)                                       envs/common/abstract.py · AbstractEnv.step
 ├─ time += 1 / policy_frequency
 ├─ _simulate(action)                                  envs/common/abstract.py · AbstractEnv._simulate
 │   └─ 重复 simulation_frequency // policy_frequency 次：
 │       ├─（仅第一个小步）action_type.act(action)       envs/common/action.py · DiscreteMetaAction.act
 │       │     └─ 自车 .act("LANE_RIGHT" 等)：改目标     vehicle/controller.py · MDPVehicle.act → ControlledVehicle.act
 │       ├─ road.act()：每辆车算自己的控制量             road/road.py · Road.act
 │       │     ├─ 自车：转向 + 加速度追目标               vehicle/controller.py · steering_control / speed_control
 │       │     └─ 背景车：MOBIL 决定变道 + IDM 算加速度    vehicle/behavior.py · IDMVehicle.act / acceleration / mobil
 │       └─ road.step(dt)：                              road/road.py · Road.step
 │             ├─ 每辆车按控制量运动 dt 秒               vehicle/kinematics.py · Vehicle.step
 │             └─ 两两检查碰撞                          vehicle/objects.py · handle_collisions
 ├─ observation_type.observe()：生成观察表              envs/common/observation.py · KinematicObservation.observe
 ├─ _reward / _is_terminated / _is_truncated / _info    envs/highway_env.py · HighwayEnv
 └─ return obs, reward, terminated, truncated, info
```

| 环节 | 一句话职责 | 本书哪里讲 | 阶段 1 清单 |
| --- | --- | --- | --- |
| `AbstractEnv.step` / `_simulate` | 推进时间；把一步拆成若干物理小步 | 1.4 | 第 1 项 |
| `HighwayEnv` 的奖励和结束条件 | 速度、靠右、碰撞打分；撞车结束，到时截断 | 4.5 | 第 2 项 |
| `ControlledVehicle.act` / `speed_control` / `steering_control` | 高层动作 → 改目标；目标 vs 实际 → 控制量 | 1.2、3.3、3.4 | 第 3 项 |
| `Vehicle.act` / `Vehicle.step` | 保存控制量；自行车模型更新位置、朝向、速度 | 1.3、3.5 | 第 4 项 |
| `IDMVehicle.acceleration` / `mobil` | 背景车怎样跟车、怎样决定变道 | 待讲（阶段 2 的规则策略要用） | 第 5 项 |
| `Road.act` / `Road.step` / `neighbour_vehicles` | 让所有车算控制、运动；找某车的前车和后车 | 1.4（简） | 第 6 项 |
| `KinematicObservation.observe` | 挑附近车辆、算相对量、归一化、补空行 | 第 2 章 | 第 7 项 |
| `handle_collisions` | 两车外形相交 → 标记碰撞 | — | 第 8 项 |

自车和背景车走的是同一个 `road.act()` / `road.step()`。区别只在 `act()`：自车听你的动作追目标，背景车用 IDM（跟车）和 MOBIL（变道）自己决定。

---

<a id="project-continuity"></a>

## 接下来：从这里走向真实的智驾工作

当前路线分三个阶段，具体清单只维护在 [CURRENT_TASK.md](../experiments/highway_driving/CURRENT_TASK.md)：

| 阶段 | 做什么 | 产出 |
| --- | --- | --- |
| 1. 收尾 HighwayEnv 主线 | 按附录 A 读一次闭环的关键源码，重点是 IDM / MOBIL | 能不看代码画出 `env.step` 调用链，讲清 IDM 公式每一项 |
| 2. 规则规划 + 批量评测 | 自己写跟车 + 变道规则（只用观察表）；多种子批量评测；训练 DQN 对比 | 一个可以放上 GitHub 的小项目：代码、评测表、失败案例、README |
| 3. 换到真实数据 | 用 nuPlan / Waymo Open Motion 等公开轨迹数据做预测或规划，比较开环与闭环 | 对应预测规划、数据闭环岗位的作品 |

这本书的四章正好是阶段 2 的地基：第 2 章的规则就是阶段 2 规则策略的起点，第 2.8 节列的问题就是要改进的地方，第 4 章的比较方法就是批量评测的雏形。

更远的方向（相机与视觉、多帧时序、端到端模型、VLA、压缩部署）也继续在这个项目里做。到时候本书反复问的几个问题仍然适用：

- 这个值是**什么时间**的？
- 在**哪个坐标系**，有没有归一化？
- 这个动作是**轨迹、高层指令还是直接控制量**？由谁去执行？
- 这个指标是**开环还是闭环**？
