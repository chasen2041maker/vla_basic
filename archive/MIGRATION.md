# Migration History

## Migration 1 — Robot Manipulation VLA → Autonomous Driving VLA

旧版仓库的 VLA 指向：

```text
MuJoCo
机械臂
FK / IK
夹爪
pick-and-place
ACT / OpenVLA
SO-101
```

用户目标是类似小鹏智能驾驶的自动驾驶 VLA：

```text
多相机时序视觉
自车状态
导航 / 语义条件
未来车辆轨迹或动作
驾驶评测
安全与部署
```

两个方向共享视觉、语言/语义和动作抽象，但数据、动作、仿真、评测和安全边界不同，因此不能混成一条课程。

旧内容保留在：

```text
archive/robot-manipulation-vla-2026-07
```

旧提交：

```text
2bff8713e215c919b027ee3f8ae434cfb58457d7
```

---

## Migration 2 — Lab-first → Role-driven System-first

日期：2026-08-28

### 为什么再次重构

旧路线虽然方向正确，但日常入口直接进入 Lab 001 数据契约，容易把局部 validator 当成课程实质。

学习者进一步明确：

- 会常规深度学习模型训练；
- 学过蒸馏和量化；
- 未学习强化学习；
- 视觉、几何、车辆运动、轨迹控制和闭环评测基本不会；
- 目标是从当前背景成长到类似小鹏智能驾驶研发所需能力。

因此课程必须先回答：

```text
我要成为什么研发人员？
完整驾驶系统怎样工作？
我会什么、缺什么？
当前局部任务位于哪一层？
```

### 新增

- `SYSTEM_MENTAL_MODEL.md`：整车智能链路；
- `SKILL_GAP_MATRIX.md`：USE / VERIFY / LEARN / LATER；
- `Lab 000`：系统图和 failure boundary；
- 角色目标、桥梁岗位和作品证据；
- 蒸馏、量化、部署的驾驶化验证；
- 强化学习的依赖门槛；
- CI 对 Lab 000 和 Lab 001 的共同验证。

### 重排

```text
System Map
→ Data / Time
→ Coordinate / Motion
→ Camera Geometry
→ Multi-Camera Temporal
→ Trajectory Model
→ Open / Closed Loop
→ Public Stack
→ Driving VLA
→ Action Representation
→ Distill / Quantize / Deploy
→ Safety
→ RL / World Model
```

### 保留

- Lab 001A 的可运行 4/6 intentional baseline；
- 读懂 → 运行 → 修改 → 故障 → 测试 → 解释；
- evidence-based progression；
- 公开复现与闭源量产的边界；
- 不从空白重复写低价值样板。

这次重构不删除有效代码，而是给现有 Lab 增加正确的系统上下文和依赖顺序。
