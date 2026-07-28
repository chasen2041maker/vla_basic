# 阶段 07：真机与 sim2real

预估投入 20-40 小时 · 需要 SO-101（几千块）· 产出：真机完成抓取任务

## 这个阶段要解决什么

前六个阶段都在仿真里。仿真是干净的：观测无噪声、执行精确、时间可以暂停、失败可以重置。

真机全部相反。这个阶段的目标是让你体验这个落差，并学会应对。

**心理准备：这是整条路线上挫败感最强的一段。** 预期你会花两个下午在标定上，采数据采到手腕酸，第一次训出来的策略成功率可能只有 30%。这些都是正常的，不是你做错了。

## 7.1 硬件选择

推荐 **SO-101**，理由：

- 便宜，整套几千块（含舵机、3D 打印件、控制板）
- 开源，LeRobot 官方支持，社区活跃
- leader-follower 双臂设计，遥操作采数据很方便
- 6 自由度加夹爪，足够做桌面操作任务

| 型号 | 价格档 | 说明 |
|---|---|---|
| **SO-101** | 几千 | SO-100 的改进版，推荐首选 |
| SO-100 | 几千 | 上一代，仍可用，社区资料更多 |
| Koch v1.1 | 几千 | 类似定位，LeRobot 也支持 |
| ALOHA / 双臂 | 几万 | 双臂协作任务，暂时不需要 |
| 人形 | 十几万起 | 不要买，调试地狱且对你的目标无额外收益 |

需要额外准备的：

- **相机**：一个普通 USB 摄像头就能起步。想要深度信息可以上 RealSense D405/D435，但先不必
- **工作台**：一块平整的桌面，最好铺深色不反光的垫子（利于视觉）
- **标定物**：打印一张 AprilTag 或棋盘格
- **训练机器**：带 GPU 的机器，可以和机器人不在一起（推理时通过网络下发动作，延迟可接受）

> ⚠️ 需核实：SO-101 的具体采购渠道、BOM 清单和装配说明以 LeRobot 官方仓库当前文档为准，硬件版本迭代较快。

## 7.2 组装与舵机标定

组装跟着官方文档走，不复述。说几个容易出问题的地方：

**舵机 ID 设置。** 每个舵机出厂 ID 都一样，必须逐个改成不同 ID。这一步顺序错了后面全乱。建议贴标签。

**零位标定。** 每个关节的「0 度」在哪，需要手动摆到中位然后写入。零位偏了会导致所有 IK 计算系统性偏差——这就是阶段 03 讲的系统偏差，你现在会真实遇到它。

**关节方向。** 舵机的正方向和你的运动学模型假设的正方向可能相反。检查方法：给一个小的正向指令，看关节朝哪边动。

**限位。** 软件限位必须设，否则舵机会撞到机械结构造成堵转，堵转会发热损坏舵机。

```python
"""舵机标定检查清单脚本。

组装完必须逐项验证。跳过这一步，后面所有问题都会归因困难——
你不知道是策略不好还是硬件没标好。
"""

from dataclasses import dataclass


@dataclass
class JointCheckResult:
    joint_id: int
    zero_position_ok: bool
    direction_ok: bool
    limits_ok: bool
    notes: str = ""


def verify_joint_calibration(robot, joint_id: int) -> JointCheckResult:
    """逐个验证关节标定。

    检查项：
      1. 零位：指令 0 时关节是否在物理中位
      2. 方向：正向指令是否让关节朝预期方向动
      3. 限位：软件限位是否在机械限位内侧（留 5 度余量）

    这三项任何一项不过，都不要进入下一步。
    """
    raise NotImplementedError("按你的硬件实现，这里是检查项清单")
```

## 7.3 安全第一

真机会伤人和自伤。SO-101 力量不大，但仍需要基本纪律。

**必须做到的五条：**

1. **物理急停可达。** 手边有电源开关或急停按钮，能一秒切断。软件的停止指令在程序卡死时无效。
2. **限制速度。** 开发阶段把速度上限设到很低（比如正常速度的 30%）。快速运动是大部分事故的原因。
3. **工作区清空。** 机器人周围不放水杯、不放手机、不放你的手。
4. **先空跑。** 任何新策略先在没有物体的场景里跑一遍，确认轨迹不会撞到自己或桌面。
5. **过流保护。** 舵机堵转会持续发热。监控电流，异常时立刻断电。

```python
"""真机安全包装层。

这一层的存在意义是：即使上层策略输出了危险指令，
这里也能拦住。永远不要信任策略的输出。
"""

import numpy as np


class SafetyLimiter:
    """动作安全限制器。

    这是一个纯函数式的过滤层，放在策略和硬件之间。
    它不关心策略为什么输出这个动作，只负责保证下发到
    硬件的指令在安全范围内。

    设计原则：宁可让任务失败，不可让硬件受损。
    """

    def __init__(
        self,
        joint_limits: np.ndarray,      # (n, 2) 每个关节的 [min, max]
        max_velocity: np.ndarray,       # (n,) 每步最大变化量
        workspace_bounds: np.ndarray,   # (3, 2) 末端可达空间的 xyz 范围
    ):
        self.joint_limits = joint_limits
        self.max_velocity = max_velocity
        self.workspace_bounds = workspace_bounds

    def limit(
        self,
        target_joints: np.ndarray,
        current_joints: np.ndarray,
    ) -> tuple[np.ndarray, list[str]]:
        """限制目标关节角度到安全范围。

        返回 (安全的目标角度, 触发的限制列表)。

        触发列表不能忽略——如果每一步都在触发限速，
        说明策略输出的动作幅度和你的限制不匹配，
        这时策略实际执行的是被削弱的版本，行为会和训练时不同。
        """
        triggered: list[str] = []
        safe = target_joints.copy()

        # 1. 关节限位
        clipped = np.clip(safe, self.joint_limits[:, 0], self.joint_limits[:, 1])
        if not np.allclose(clipped, safe):
            triggered.append("joint_limit")
            safe = clipped

        # 2. 速度限制：限制单步变化量
        delta = safe - current_joints
        excessive = np.abs(delta) > self.max_velocity
        if excessive.any():
            triggered.append("velocity_limit")
            delta = np.clip(delta, -self.max_velocity, self.max_velocity)
            safe = current_joints + delta

        return safe, triggered
```

💡 联系你的经验：这就是你在 AgentTrust Runtime 里做的事——在工具执行前做权限和边界检查，不信任上游的输出。区别是这里的后果是物理性的。阶段 08 会把这个类比推到底。

## 7.4 遥操作采数据

SO-101 的 leader-follower 设计：你手动操作 leader 臂，follower 臂跟随，同时记录两者的关节角度和相机图像。

```bash
# LeRobot 的采集命令（示意，以当前版本文档为准）
lerobot-record \
  --robot.type=so101_follower \
  --teleop.type=so101_leader \
  --dataset.repo_id=你的用户名/pick_block \
  --dataset.num_episodes=50 \
  --dataset.single_task="pick up the red block"
```

> ⚠️ 需核实：LeRobot 的 CLI 命令和参数名变化频繁，务必先看官方 README。

**采数据的实践要点，这些比代码重要：**

**保持动作风格一致。** 同一个任务，每次的接近路径、速度、抓取姿态尽量一致。风格混乱的数据会让模型学到平均行为——回想阶段 05 讲的多模态问题，这就是它在真机上的表现。

**故意包含恢复行为。** 只采完美轨迹会让模型没有纠错能力（阶段 05 的复合误差问题）。做法：偶尔故意偏一点，然后修正回来。这些数据教会模型「偏了怎么办」。

**随机化初始位置。** 每条轨迹开始前把物体放在不同位置。范围先小（±5cm），后面可以扩大。

**记录失败。** 采集时如果失败了，不要直接删。标记为失败保留下来，训练时再决定是否用。

**分批采集。** 一次采 50 条会很累，累了动作质量下降。分几次采，每次 15-20 条。

**中途检查数据。** 采完 10 条就回放看一遍，确认图像清晰、动作平滑、没有丢帧。不要采完 50 条才发现相机对焦不对。

**手腕会酸。** 这不是玩笑。50 条演示大概一小时，全程手臂悬空操作 leader。安排好休息。

## 7.5 sim2real 落差的来源

如果你想把仿真训的策略搬到真机（sim2real），需要知道差异来自哪里。按影响大小排序：

**1. 视觉外观差异（影响最大）。** 仿真渲染和真实相机图像差别巨大：光照模型、纹理、噪声、镜头畸变、白平衡。这是 sim2real 失败的首要原因。

**2. 动力学差异。** 摩擦系数、关节阻尼、舵机响应曲线、连杆柔性。仿真里的刚体假设在真机上不成立——3D 打印件会弯。

**3. 延迟。** 真机有通信延迟、图像采集延迟、舵机响应延迟，加起来可能几十毫秒。仿真里是零。策略在训练时看到的是「当前」图像，真机上看到的是「几十毫秒前」的图像。

**4. 标定误差。** 相机内外参、零位偏移。这是系统偏差，会让所有动作一致地偏。

**5. 物体差异。** 仿真里的方块是完美立方体，真实方块有倒角、有重心偏移、表面摩擦不均。

**主流应对手段：**

| 手段 | 针对 | 说明 |
|---|---|---|
| **域随机化** | 视觉、动力学 | 训练时随机化光照、纹理、摩擦、质量，让策略被迫鲁棒 |
| **真实图像增强** | 视觉 | 加噪声、模糊、色彩抖动，模拟真实相机 |
| **系统辨识** | 动力学 | 测量真机参数，调仿真参数去匹配 |
| **延迟建模** | 延迟 | 在仿真里人为加入和真机匹配的延迟 |
| **真机数据微调** | 全部 | 最有效，也最省事 |

**对你的建议：跳过 sim2real，直接在真机上采数据训练。**

理由很实际：sim2real 是一个独立的研究课题，投入产出比对你不划算。而 SO-101 采 50 条数据只要一小时，直接真机训练又快又有效。

sim2real 真正有价值的场景是「真机数据极其昂贵或危险」（比如自动驾驶、腿足机器人摔倒）。桌面机械臂不属于这一类。

## 7.6 真机部署与推理循环

训练完成后部署。真机推理循环和仿真的最大区别是**它必须实时**。

```python
"""真机推理循环。

关键差异：仿真里你控制时间（mj_step 推进），真机上时间自己走。
如果你的推理比控制周期慢，就会累积延迟，机器人动作变得迟滞。
"""

import time

import numpy as np


class RealtimeController:
    """固定频率的真机控制循环。

    维护一个固定的控制周期，并监控实际耗时。
    超时不是可以忽略的警告——它意味着策略实际运行在
    比训练时更低的频率上，行为会不一致。
    """

    def __init__(
        self,
        policy,
        robot,
        camera,
        safety: SafetyLimiter,
        control_hz: float = 30.0,
    ):
        self.policy = policy
        self.robot = robot
        self.camera = camera
        self.safety = safety
        self.period = 1.0 / control_hz
        self.overrun_count = 0

    def run(self, instruction: str, max_steps: int = 300) -> dict:
        """执行一个任务，返回统计信息。"""
        stats = {"steps": 0, "overruns": 0, "safety_triggers": []}

        for step in range(max_steps):
            loop_start = time.perf_counter()

            # 1. 观测
            image = self.camera.read()
            current_joints = self.robot.read_joint_positions()

            # 2. 策略推理
            target_joints = self.policy.predict(image, current_joints, instruction)

            # 3. 安全过滤（永远不要跳过这一步）
            safe_joints, triggered = self.safety.limit(target_joints, current_joints)
            if triggered:
                stats["safety_triggers"].extend(triggered)

            # 4. 下发
            self.robot.set_joint_positions(safe_joints)

            stats["steps"] = step + 1

            # 5. 维持固定频率
            elapsed = time.perf_counter() - loop_start
            remaining = self.period - elapsed
            if remaining > 0:
                time.sleep(remaining)
            else:
                # 超时了：这一步实际耗时超过控制周期
                self.overrun_count += 1
                stats["overruns"] = self.overrun_count

        return stats
```

**部署时必查的三件事：**

**1. 推理延迟是否满足控制周期。** 30Hz 意味着每步 33 毫秒预算，其中要包含图像采集、推理、通信。ACT 单次前向在 3090 上大概几毫秒，但图像采集和 USB 通信可能占几十毫秒。先测量再优化。

**2. 观测的预处理必须和训练时完全一致。** 图像尺寸、归一化参数、通道顺序（RGB vs BGR）、裁剪方式。这里错一点策略就完全不工作。这是真机部署最高频的 bug。

**3. 动作的语义必须一致。** 训练时用的是绝对关节角度还是增量？角度单位是弧度还是度？夹爪的 0 是张开还是闭合？

💡 联系你的经验：这三条本质是「训练服务一致性」问题，和你在模型部署里遇到的特征不一致是同一类问题。区别是这里的表现是机器人乱动，而不是准确率下降。

## 7.7 调试方法论

真机不给 stack trace。策略失败了，你面对的是「机械臂擦着方块过去了」这个现象，需要自己定位原因。

**建立分层排查顺序，从下往上：**

**第 0 层：硬件。** 舵机是否正常响应？给一个固定角度指令，实际到位精度多少？重复 10 次的一致性如何？如果这一层就有问题（比如某个舵机有 3 度回差），上层怎么调都没用。

**第 1 层：标定。** 用手动遥操作把夹爪对准一个已知位置的物体，读出关节角度，用 FK 算出末端位置，和实际测量对比。偏差多少？方向一致吗？如果是一致的偏差，就是标定问题。

**第 2 层：感知。** 相机看到的物体位置和实际位置差多少？把物体放在几个已知位置，逐个验证。

**第 3 层：策略。** 前三层都确认没问题，再怀疑策略。这时的排查手段是回放训练数据看模型在训练分布内的表现，以及可视化模型的注意力。

**这个顺序不能颠倒。** 大部分人的错误是直接怀疑策略、反复重训，而问题其实在标定。

```python
"""分层诊断工具。

每一层都有一个可量化的判据。写下来，因为真机调试时
很容易凭感觉判断，而感觉不可靠。
"""

from dataclasses import dataclass


@dataclass
class DiagnosticReport:
    """分层诊断结果。

    按 layer 从低到高排查，第一个不通过的层就是问题所在。
    不要跳层——上层的表现会被下层的问题污染。
    """

    layer: str
    passed: bool
    measured_value: float
    threshold: float
    unit: str
    note: str = ""

    def describe(self) -> str:
        status = "通过" if self.passed else "不通过"
        return (
            f"[{self.layer}] {status}: "
            f"实测 {self.measured_value:.4f}{self.unit} "
            f"(阈值 {self.threshold:.4f}{self.unit}) {self.note}"
        )


def diagnose_joint_repeatability(robot, joint_id: int, trials: int = 10) -> DiagnosticReport:
    """第 0 层：测量单关节的重复定位精度。

    做法：反复在两个角度之间往返，每次到位后读取实际角度，
    统计标准差。舵机的回差（backlash）会在这里暴露。

    阈值 0.5 度是经验值：超过这个数，末端位置误差会
    大到影响抓取（关节误差经过连杆放大）。
    """
    raise NotImplementedError("按你的硬件实现")
```

## 7.8 本阶段大作业

**任务：真机完成方块抓取放置。**

步骤：

1. 组装 SO-101，完成舵机标定，通过第 0 层诊断（重复精度 < 0.5 度）
2. 实现 `SafetyLimiter` 并接入所有下发路径
3. 遥操作采集 50 条演示（±5cm 随机化，包含恢复行为）
4. 中途检查数据质量（第 10 条时回放确认）
5. 训练 ACT
6. 部署，测量推理延迟，确认满足 30Hz
7. 评估 30 次，统计成功率和失败模式
8. 用分层诊断定位最主要的失败原因，做一轮改进，再评估一次

**预期结果：** 第一次训练成功率 30-50%。改进一轮后 60-80%。如果第一次就超过 80%，检查一下任务是不是设计得太简单（比如物体位置几乎不变）。

**必做记录：** 写一份 sim2real 落差报告，对比同一个任务在仿真和真机的成功率，并分析差异来源。这份报告是你这个阶段最有价值的产出。

**改进的常见方向，按性价比排序：**

1. 补数据。失败集中在某类初始位置？针对那个区域多采 20 条
2. 查标定。系统性偏一个方向就是标定问题
3. 加图像增强。光照变化导致失败就加色彩抖动重训
4. 调 chunk_size。动作不平滑或末端不准可以试着调
5. 换策略架构。这是最后手段，通常收益最小

## 验收标准

1. 真机相比仿真，差异来源有哪五类？按影响大小排序。
2. 为什么建议你跳过 sim2real 直接真机训练？什么场景下 sim2real 才值得做？
3. 舵机零位偏移会导致什么类型的误差？怎么和随机噪声区分？
4. 分层排查的四层顺序是什么？为什么不能颠倒？
5. 为什么采数据时要故意包含「偏了再修正」的恢复行为？
6. 控制循环超时（overrun）为什么不能忽略？
7. 部署时最容易出错的三件一致性是什么？
8. 为什么安全过滤层必须在策略和硬件之间，而不是信任策略输出？
9. 关节角度 0.5 度的误差为什么会影响抓取？

## 交付物检查

- [ ] SO-101 组装完成，舵机 ID、零位、方向、限位全部验证过
- [ ] 第 0 层诊断通过（重复精度达标）
- [ ] `SafetyLimiter` 实现并接入，测试过它能拦住越界指令
- [ ] 50 条真机演示数据采集完成，含恢复行为
- [ ] 数据质量中途检查过
- [ ] ACT 训练完成并部署到真机
- [ ] 推理延迟测量过，满足控制频率
- [ ] 30 次评估完成，成功率和失败模式都有记录
- [ ] 分层诊断做过，定位了主要失败原因
- [ ] 改进一轮后重新评估，有对比数据
- [ ] sim2real 落差报告写完

## 下一步

到这里你已经能让真实机械臂完成任务了。阶段 08 是唯一别人做不出、只有你能做的部分——把你的 Agent 运行时治理能力带进具身。

