# 阶段 01：环境与心智模型

预估投入 6-10 小时 · 无硬件要求 · 产出：仿真里的机械臂在你的代码控制下动起来

## 这个阶段要解决什么

两件事：把环境跑通，以及在脑子里建立「代码 → 物理世界」这个回路的正确模型。

第二件比第一件重要。很多人装完环境就急着跑 VLA，结果对底层发生了什么完全没概念，后面遇到问题无法定位。

## 1.1 为什么是 MuJoCo

主流的机器人仿真器有几个，选择逻辑：

| 仿真器 | 特点 | 适合场景 |
|---|---|---|
| **MuJoCo** | 轻量、物理精确、Python API 干净、免费开源 | 学习、机械臂操作、算法研究 |
| Isaac Sim / Isaac Lab | NVIDIA 出品、渲染逼真、大规模并行、需要 RTX 卡 | 大规模 RL 训练、sim2real |
| PyBullet | 老牌、简单、社区大 | 快速原型 |
| Gazebo | 和 ROS 深度集成 | ROS 生态的系统级仿真 |

从 MuJoCo 开始，理由：安装最省事（`pip install mujoco` 就完事），物理引擎质量最高，而且 LeRobot、ACT、Diffusion Policy 这些你后面要用的项目都用它。

Isaac Sim 留到阶段 07 再看，它安装重、吃显存，现在用不上。

## 1.2 环境安装

```bash
# 建议用独立虚拟环境
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install mujoco
pip install numpy
```

验证安装：

```bash
python -c "import mujoco; print(mujoco.__version__)"
```

可视化查看器（强烈建议装，你需要用眼睛看）：

```bash
python -m mujoco.viewer
```

这会打开一个空的查看器窗口。把 `.xml` 模型文件拖进去就能看。

> ⚠️ 需核实：MuJoCo 3.x 之后 API 有变动（旧代码里的 `mujoco_py` 是已废弃的独立项目，不要用）。本文按官方 `mujoco` 包（3.x）写。

## 1.3 MuJoCo 的核心概念

这是整个阶段最重要的部分。MuJoCo 的数据模型只有两个核心对象：

**`MjModel`（模型）** — 静态的、不变的描述。有几个关节、每个连杆多重、摩擦系数多少、电机力矩上限多少。从 XML 文件加载，加载后基本不改。

**`MjData`（数据）** — 动态的、每一步都在变的状态。当前每个关节的角度、速度、受力、每个物体的位置。

💡 联系你的经验：`MjModel` 相当于数据库 schema，`MjData` 相当于某一时刻的表内容。仿真的每一步就是一次状态转移。

关键字段：

```python
# MjData 里你最常碰的几个
data.qpos    # 广义位置（关节角度 / 自由物体的位姿），长度 = model.nq
data.qvel    # 广义速度，长度 = model.nv
data.ctrl    # 控制输入（你写这里来驱动机器人），长度 = model.nu
data.time    # 仿真时间
data.xpos    # 每个 body 在世界坐标系的位置，形状 (nbody, 3)
data.xquat   # 每个 body 的姿态四元数，形状 (nbody, 4)
```

注意 `qpos` 和 `xpos` 的区别，这是新手最容易混的地方：

- `qpos` 是**关节空间**：机械臂 6 个关节，`qpos` 就是这 6 个角度
- `xpos` 是**笛卡尔空间**：每个连杆在三维空间里的实际位置

从 `qpos` 算 `xpos` 叫**正运动学**，MuJoCo 会在每次 `mj_step` 或 `mj_forward` 时自动帮你算好。反过来从想要的 `xpos` 求 `qpos` 叫**逆运动学**，MuJoCo 不直接提供，阶段 02 会手写。

## 1.4 第一个脚本：让物体掉下来

先用最简单的场景理解仿真循环。

创建 `code/01_falling_box.xml`：

```xml
<mujoco model="falling_box">
  <option timestep="0.002" gravity="0 0 -9.81"/>

  <worldbody>
    <!-- 光源，纯粹为了看得清 -->
    <light pos="0 0 3" dir="0 0 -1"/>

    <!-- 地面：静态几何体，不属于任何可动 body -->
    <geom name="floor" type="plane" size="2 2 0.1" rgba="0.8 0.8 0.8 1"/>

    <!-- 一个会掉落的方块 -->
    <body name="box" pos="0 0 1">
      <!-- freejoint 表示这个 body 有完整的 6 自由度（可以自由移动和旋转） -->
      <freejoint/>
      <geom name="box_geom" type="box" size="0.05 0.05 0.05" rgba="1 0 0 1" mass="0.1"/>
    </body>
  </worldbody>
</mujoco>
```

创建 `code/01_falling_box.py`：

```python
"""最小仿真循环：观察一个方块自由落体。

这个脚本的目的不是做什么有用的事，而是让你看清 MuJoCo 的
三个基本动作：加载模型、推进一步、读取状态。
"""

import mujoco
import mujoco.viewer

# 1. 加载模型（静态描述）
model = mujoco.MjModel.from_xml_path("01_falling_box.xml")

# 2. 创建数据（动态状态），初始状态来自模型里的 pos 定义
data = mujoco.MjData(model)

print(f"自由度数量 nq={model.nq}, 速度维度 nv={model.nv}, 控制维度 nu={model.nu}")
# freejoint 提供 7 维 qpos（位置 3 + 四元数 4）和 6 维 qvel（线速度 3 + 角速度 3）
# 没有电机，所以 nu=0

# 3. 找到 box 这个 body 的索引，后面用来读它的位置
box_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "box")

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running() and data.time < 3.0:
        # 推进一个时间步（timestep=0.002 秒）
        mujoco.mj_step(model, data)

        # 每 100 步打印一次高度
        if int(data.time / model.opt.timestep) % 100 == 0:
            z = data.xpos[box_id][2]
            print(f"t={data.time:.3f}s  高度={z:.4f}m")

        viewer.sync()
```

运行：

```bash
cd code
python 01_falling_box.py
```

你应该看到方块落下、弹一下、停在地面上，终端打印高度从 1.0 逐渐降到约 0.05（方块半边长）。

**动手改一改，建立直觉：**

1. 把 `gravity` 改成 `0 0 -1.62`（月球重力），观察下落变慢
2. 把 `timestep` 改成 `0.02`，观察物理变得不稳定甚至穿透地面 — 这是你第一次遇到「时间是硬约束」
3. 给 geom 加 `friction="0.01 0.005 0.0001"`，把地面倾斜，看方块滑动

第 2 条特别重要。时间步太大，数值积分就会发散。这在后端里没有对应物——你的代码不会因为「跑得太快」而算错。

## 1.5 第二个脚本：驱动一个关节

现在加入执行器（actuator），这是你的代码影响物理世界的唯一通道。

创建 `code/01_single_joint.xml`：

```xml
<mujoco model="single_joint">
  <option timestep="0.002"/>

  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
    <geom name="floor" type="plane" size="2 2 0.1" rgba="0.8 0.8 0.8 1"/>

    <body name="base" pos="0 0 0.5">
      <!-- hinge 关节：绕单轴旋转，1 个自由度 -->
      <joint name="j1" type="hinge" axis="0 1 0" range="-90 90"/>
      <geom name="arm" type="capsule" fromto="0 0 0  0.3 0 0" size="0.02" rgba="0 0.5 1 1"/>
    </body>
  </worldbody>

  <actuator>
    <!-- position 类型执行器：你给目标角度，内部 PD 控制器负责到达 -->
    <position name="j1_motor" joint="j1" kp="10" ctrlrange="-1.57 1.57"/>
  </actuator>
</mujoco>
```

创建 `code/01_single_joint.py`：

```python
"""驱动单关节：理解 data.ctrl 是你影响物理世界的唯一入口。"""

import math

import mujoco
import mujoco.viewer

model = mujoco.MjModel.from_xml_path("01_single_joint.xml")
data = mujoco.MjData(model)

print(f"nq={model.nq}, nu={model.nu}")  # nq=1, nu=1

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running() and data.time < 10.0:
        # 让目标角度做正弦运动
        target = 1.2 * math.sin(data.time * 2.0)

        # ctrl 是控制输入向量。position 执行器把它解释为目标角度（弧度）
        data.ctrl[0] = target

        mujoco.mj_step(model, data)

        if int(data.time / model.opt.timestep) % 200 == 0:
            actual = data.qpos[0]
            error = target - actual
            print(f"t={data.time:5.2f}  目标={target:+.3f}  实际={actual:+.3f}  误差={error:+.3f}")

        viewer.sync()
```

运行后观察终端：**实际角度永远追不上目标角度，总有滞后和误差。**

这是本阶段最关键的一个观察。原因是 `position` 执行器内部是一个 PD 控制器，`kp=10` 是它的刚度。目标变化快时它跟不上。

**动手实验：**

1. `kp` 改成 `100`，误差变小但可能开始震荡
2. `kp` 改成 `2`，机械臂软绵绵地跟不动
3. 把执行器类型换成 `<motor>`，这时 `ctrl` 变成直接给力矩，你会发现机械臂完全不受控地转起来 — 因为没有反馈控制

💡 联系你的经验：这就是「观测不完整」和「动作不精确」的最小演示。你下发的指令和实际发生的事情之间永远有偏差。后端里 `UPDATE users SET name='x'` 执行完 name 就是 'x'，物理世界里没有这种保证。

## 1.6 三种执行器，你需要知道的区别

| 类型 | `ctrl` 的含义 | 行为 | 什么时候用 |
|---|---|---|---|
| `<position>` | 目标位置（角度） | 内部 PD 控制，自动到达并保持 | 大多数情况，最好用 |
| `<velocity>` | 目标速度 | 内部 P 控制速度 | 需要匀速运动时 |
| `<motor>` | 直接的力/力矩 | 无反馈，纯开环 | 需要自己写控制器、力控 |

真实机器人也是这三类接口。SO-101 的舵机是位置控制，所以你在阶段 07 用的是 `position` 那一套心智模型。

## 1.7 加载一个真实的机械臂模型

自己写 XML 只适合学习。真实项目用现成模型。

MuJoCo 官方维护了一个模型库 `mujoco_menagerie`，包含 Franka Panda、UR5e、Google Robot 等主流机械臂的高质量模型。

```bash
git clone https://github.com/google-deepmind/mujoco_menagerie.git
```

> ⚠️ 需核实：仓库地址和目录结构可能变动，clone 后看它的 README。

加载 Franka Panda：

```python
import mujoco
import mujoco.viewer

# 路径按你 clone 的位置调整
XML = "mujoco_menagerie/franka_emika_panda/scene.xml"

model = mujoco.MjModel.from_xml_path(XML)
data = mujoco.MjData(model)

print(f"关节数 nq={model.nq}")
print(f"执行器数 nu={model.nu}")

# 打印所有关节名，这个习惯很有用
for i in range(model.njnt):
    name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i)
    print(f"  joint[{i}] = {name}")

# 打印所有执行器名
for i in range(model.nu):
    name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
    print(f"  actuator[{i}] = {name}")

mujoco.viewer.launch(model, data)
```

Panda 是 7 自由度机械臂加一个夹爪。运行后在查看器里用鼠标拖动，观察它在重力下垂下来。

**动手：** 写一个脚本让 Panda 的每个关节依次转动到某个角度并保持。这需要你把 `data.ctrl` 的每一维和对应关节搞清楚。

## 1.8 心智模型总结

跑完这个阶段，你脑子里应该有这张图：

```
你的 Python 代码
      │
      │ 写入 data.ctrl
      ▼
  执行器（PD 控制器 / 直接力矩）
      │
      │ 产生力和力矩
      ▼
  物理引擎（mj_step 求解动力学）
      │
      │ 更新 qpos / qvel
      ▼
  正运动学（自动计算）
      │
      │ 更新 xpos / xquat
      ▼
你读取状态（可能带噪声，如果是真机）
```

这个回路每 `timestep` 秒执行一次。你的所有控制、策略、规划，最终都要落到 `data.ctrl` 上。

💡 联系你的经验：这个循环和你熟悉的请求-响应模型最大的区别是**它一直在跑**。你不下发指令，物理世界也在演化（东西会掉、会滑、会因为惯性继续动）。后端里没有请求就没有状态变化，这里没有。

## 验收标准

不看代码、不查文档，回答下面问题。答不上的回去补。

1. `MjModel` 和 `MjData` 的区别是什么？哪个在仿真过程中会变？
2. `data.qpos` 和 `data.xpos` 分别是什么空间的量？从前者算后者叫什么？
3. `data.ctrl` 的语义由什么决定？同样写入 `0.5`，`position` 执行器和 `motor` 执行器的行为差别是什么？
4. 为什么 `timestep` 设得太大会导致物理错误？这在后端工程里有对应的现象吗？
5. 为什么 `position` 执行器下发目标角度后，实际角度总有误差和滞后？`kp` 调大会怎样，调到很大会怎样？
6. 一个 `freejoint` 贡献几维 `qpos`？为什么和 `qvel` 的维度不一样？

## 交付物检查

- [ ] `01_falling_box.py` 能跑，看到方块落下
- [ ] 改过 `timestep` 并观察到物理发散
- [ ] `01_single_joint.py` 能跑，理解了目标与实际的误差
- [ ] 换过三种执行器类型并观察差异
- [ ] 成功加载 `mujoco_menagerie` 里的 Panda 并打印出所有关节名
- [ ] 写过一个脚本让 Panda 的关节按你的指令动到指定角度

## 下一步

阶段 02 会解决一个具体问题：你想让机械臂的手到空间中的某个点，但你只能控制关节角度。这就是逆运动学。
