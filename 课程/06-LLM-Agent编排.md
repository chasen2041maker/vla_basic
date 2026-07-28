# 阶段 04：Agent 驱动仿真

预估投入 10-15 小时 · 无硬件要求（需要一个 LLM API key）· 产出：LLM 编排完成多步操作任务

## 这个阶段要解决什么

前三个阶段你手写了执行顺序。现在把编排交给 LLM。

这是整份教程里对你最有价值的一段，因为它会暴露**物理世界的 agent 和文本 agent 的根本差异**。你已有的 agent 经验在这里既能复用，也会第一次撞墙。

## 4.1 分层架构：大脑与小脑

具身系统的标准分层：

```
自然语言指令：「把桌上的红方块放进盒子」
        │
        ▼
┌─────────────────────────┐
│  任务规划层（大脑）        │  LLM，1 次/任务
│  拆解任务、选技能、重规划   │  延迟容忍：秒级
└─────────────────────────┘
        │  技能调用：pick("red_block")
        ▼
┌─────────────────────────┐
│  技能层                  │  代码或 VLA 策略
│  单个动作的完整执行        │  延迟容忍：百毫秒级
└─────────────────────────┘
        │  轨迹点：move_to(pos)
        ▼
┌─────────────────────────┐
│  控制层（小脑）           │  PD / 力控
│  跟踪轨迹                │  延迟要求：1kHz，硬实时
└─────────────────────────┘
        │  ctrl 力矩
        ▼
      硬件
```

关键点是**不同层的时间尺度差几个数量级**。LLM 推理几百毫秒到几秒，控制环 1 毫秒。所以 LLM 绝对不能在控制回路里。

💡 联系你的经验：这和你熟悉的分层很像——LLM 层是业务编排（可以慢、可以重试），控制层是数据面（必须快、不能阻塞）。把 AI 推理服务和实时数据计算拆成独立服务，是同一个道理。

## 4.2 把技能封装成工具

你的技能库已经在阶段 02 写好了。现在给它加上 LLM 能理解的 schema。

```python
"""把机器人技能暴露成 LLM 可调用的工具。

设计要点：每个工具的返回值必须包含足够的信息让 LLM 判断
下一步该做什么。只返回 True/False 是不够的——LLM 需要知道
失败的原因，才能决定是重试、换方法还是求助。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FailureKind(str, Enum):
    """失败类型。

    这个分类决定上层的应对策略，是整个设计里最关键的部分。
    """

    NONE = "none"
    # 目标不可达：IK 无解，重试无意义，必须换目标或换姿态
    UNREACHABLE = "unreachable"
    # 感知失败：看不见目标，重试可能有用（换视角、多等几帧）
    NOT_PERCEIVED = "not_perceived"
    # 抓取失败：夹爪闭合了但没夹住东西，重试可能有用但世界已变
    GRASP_FAILED = "grasp_failed"
    # 碰撞：撞到东西了，世界状态已改变，必须重新观测
    COLLISION = "collision"
    # 前置条件不满足：比如手里已经有东西还想再抓
    PRECONDITION = "precondition"


@dataclass
class ToolResult:
    """技能执行结果。

    刻意做得比后端的返回值更啰嗦，因为 LLM 需要上下文。
    world_changed 字段尤其重要：它告诉上层「即使失败了，
    世界也可能不是原来的样子」，这是物理世界特有的语义。
    """

    success: bool
    message: str
    failure_kind: FailureKind = FailureKind.NONE
    world_changed: bool = False
    observations: dict[str, Any] = field(default_factory=dict)

    def to_llm_text(self) -> str:
        """转成给 LLM 看的文本。"""
        status = "成功" if self.success else "失败"
        lines = [f"[{status}] {self.message}"]
        if not self.success:
            lines.append(f"失败类型: {self.failure_kind.value}")
            if self.world_changed:
                lines.append("警告: 世界状态已改变，重试前必须重新观测")
        if self.observations:
            lines.append(f"观测: {self.observations}")
        return "\n".join(lines)
```

`world_changed` 这个字段是整个设计的核心。文本 agent 的工具调用失败了，世界没变，可以原样重试。机器人抓取失败可能已经把物体推歪了——**重试的前提条件和第一次不一样**。

工具 schema 定义：

```python
ROBOT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "observe_scene",
            "description": (
                "观测当前场景，返回可见物体及其位置。"
                "在任务开始时、以及任何可能改变世界状态的操作之后，"
                "都必须先调用这个工具。"
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pick",
            "description": (
                "抓取指定物体。前置条件：夹爪为空、物体可见且可达。"
                "失败时物体位置可能已改变。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "要抓取的物体名称，必须来自 observe_scene 的返回",
                    }
                },
                "required": ["object_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "place",
            "description": (
                "把手中物体放到指定位置。前置条件：夹爪中有物体。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "目标位置名称，或 'x,y,z' 格式的坐标",
                    }
                },
                "required": ["target"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_gripper_state",
            "description": "查询夹爪当前是否持有物体。不确定状态时调用它，不要猜。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
```

注意 `pick` 的 description 里明确写了「失败时物体位置可能已改变」。这类信息必须写进 schema，否则 LLM 会像处理文本工具那样盲目重试。

## 4.3 世界状态：物理 agent 独有的问题

文本 agent 的上下文里，历史消息就是完整状态。物理 agent 不是——**真实状态在世界里，不在你的上下文里**。

这带来一个具体问题：LLM 会基于「它以为的世界」做决策，而这个认知可能已经过期。

```python
"""显式的世界状态跟踪。

核心思想：区分「我记录的状态」和「实际状态」，并在关键时刻
强制重新观测而不是相信记忆。
"""

import time
from dataclasses import dataclass, field

import numpy as np


@dataclass
class ObjectBelief:
    """对单个物体的信念，带时间戳和置信度。

    叫 belief 而不是 state，因为这只是我们「相信」的位置，
    不是真值。这个命名差异会一直提醒你不要信任它。
    """

    name: str
    position: np.ndarray
    observed_at: float
    confidence: float = 1.0

    def age(self, now: float) -> float:
        """这条信念有多旧（秒）。"""
        return now - self.observed_at

    def is_stale(self, now: float, max_age: float = 5.0) -> bool:
        """是否已过期需要重新观测。"""
        return self.age(now) > max_age


@dataclass
class WorldBelief:
    """整个场景的信念状态。

    invalidate_all 是这个类存在的理由：任何可能改变世界的
    动作之后，必须调用它，把所有信念标记为不可信。
    这比在每个地方手动判断要可靠得多。
    """

    objects: dict[str, ObjectBelief] = field(default_factory=dict)
    gripper_holding: str | None = None
    last_action_changed_world: bool = False

    def update_from_observation(self, observations: dict[str, np.ndarray]) -> None:
        """用一次新观测刷新信念。"""
        now = time.monotonic()
        for name, position in observations.items():
            self.objects[name] = ObjectBelief(name, position, now)
        self.last_action_changed_world = False

    def invalidate_all(self) -> None:
        """标记所有信念为不可信。

        在任何 world_changed=True 的动作之后调用。
        """
        self.last_action_changed_world = True
        for belief in self.objects.values():
            belief.confidence = 0.0

    def needs_reobservation(self) -> bool:
        """是否必须重新观测才能继续。"""
        if self.last_action_changed_world:
            return True
        now = time.monotonic()
        return any(b.is_stale(now) for b in self.objects.values())

    def to_llm_text(self) -> str:
        """转成给 LLM 看的场景描述。"""
        if self.needs_reobservation():
            return "场景信息已过期，必须先调用 observe_scene。"

        lines = ["当前场景:"]
        for belief in self.objects.values():
            pos = belief.position
            lines.append(
                f"  - {belief.name}: 位置 ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})"
            )
        holding = self.gripper_holding or "空"
        lines.append(f"夹爪状态: {holding}")
        return "\n".join(lines)
```

💡 联系你的经验：这就是缓存失效问题，而且是最难的那一类——你无法从外部得知缓存何时失效，只能保守地在每次可能变更后主动失效。如果你做过「上游数据源不提供变更通知」的缓存，是同一个模式。

## 4.4 Agent 主循环

```python
"""LLM 驱动的机器人任务执行。

结构上就是标准的 tool-calling 循环，但多了三个物理世界特有的机制：
  1. 每轮把世界信念注入上下文
  2. world_changed 之后强制重新观测
  3. 前置条件检查在执行前拦截明显错误的调用
"""

import json
from typing import Any

from openai import OpenAI

SYSTEM_PROMPT = """你在控制一个机械臂完成桌面操作任务。

重要规则：

1. 任务开始时必须先调用 observe_scene，不要凭猜测行动。
2. 任何操作失败后，如果提示「世界状态已改变」，必须重新
   调用 observe_scene，不要直接重试。
3. 抓取前确认夹爪为空，放置前确认夹爪有物体。不确定时
   调用 get_gripper_state 查询，不要假设。
4. 同一个动作连续失败两次后，不要继续重试。说明你的判断
   并停止，等待人的指示。
5. 物理动作不可撤销。放置位置要留出余量，避免碰倒其他物体。

你的每一步都会真实地改变物理世界。谨慎行动。
"""


class EmbodiedAgent:
    """用 LLM 编排机器人技能。"""

    def __init__(
        self,
        client: OpenAI,
        skills: Any,
        belief: WorldBelief,
        model: str = "deepseek-chat",
        max_turns: int = 20,
    ):
        self.client = client
        self.skills = skills
        self.belief = belief
        self.model = model
        self.max_turns = max_turns
        # 记录每个动作的连续失败次数，用于实现规则 4
        self.consecutive_failures: dict[str, int] = {}

    def run(self, instruction: str) -> str:
        """执行一个自然语言指令，返回最终结果说明。"""
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": instruction},
        ]

        for turn in range(self.max_turns):
            # 每轮都把最新的世界信念注入，而不是依赖 LLM 的记忆
            messages.append({
                "role": "system",
                "content": f"[世界状态]\n{self.belief.to_llm_text()}",
            })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=ROBOT_TOOLS,
            )
            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))

            if not message.tool_calls:
                return message.content or "任务结束，无进一步说明"

            for tool_call in message.tool_calls:
                result = self._execute_tool(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.to_llm_text(),
                })

        return f"达到最大轮数 {self.max_turns}，任务未完成"

    def _execute_tool(self, tool_call: Any) -> ToolResult:
        """执行一次工具调用，带前置条件检查和失败计数。"""
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments or "{}")

        # 前置检查：世界状态过期时拒绝执行动作类工具
        if name in {"pick", "place"} and self.belief.needs_reobservation():
            return ToolResult(
                False,
                "世界状态已过期，请先调用 observe_scene",
                FailureKind.PRECONDITION,
            )

        # 熔断：同一动作连续失败两次后拒绝继续
        failure_key = f"{name}:{json.dumps(args, sort_keys=True)}"
        if self.consecutive_failures.get(failure_key, 0) >= 2:
            return ToolResult(
                False,
                f"动作 {name} 已连续失败 2 次，拒绝继续重试。请改变策略或求助于人。",
                FailureKind.PRECONDITION,
            )

        result = self._dispatch(name, args)

        if result.success:
            self.consecutive_failures.pop(failure_key, None)
        else:
            self.consecutive_failures[failure_key] = (
                self.consecutive_failures.get(failure_key, 0) + 1
            )

        # 关键：world_changed 之后立即失效所有信念
        if result.world_changed:
            self.belief.invalidate_all()

        return result

    def _dispatch(self, name: str, args: dict[str, Any]) -> ToolResult:
        """把工具名分发到实际技能实现。

        TODO: 接上阶段 02/03 的 RobotSkills 和感知层。
        """
        raise NotImplementedError
```

`_dispatch` 留给你自己接。这个循环本身你应该很熟悉——它和标准的 tool loop 结构一样。差异全在那三个物理世界特有的机制上。

## 4.5 必做实验：撞墙

这一节是整个阶段的核心。下面每个实验都会让你撞到一个物理世界特有的问题。不做这些实验，前面的代码只是抄写。

**实验 1：不注入世界状态。** 把主循环里注入 `[世界状态]` 的那几行注释掉，只靠 LLM 的对话记忆。让它执行「把红方块放进盒子，然后把蓝方块也放进去」。

观察：LLM 会用第一次观测的位置去抓第二个物体，而那个位置在第一次操作后可能已经变了。它不会意识到这一点，因为对话历史里那条观测结果看起来还很新鲜。

**实验 2：去掉 world_changed 失效。** 保留状态注入，但把 `invalidate_all()` 调用去掉。故意让抓取失败（把噪声调大或者把接近高度设成 1cm 让它撞倒方块）。

观察：LLM 拿着过期的位置反复重试，每次都失败在同一个地方。它没有「我该重新看一眼」的概念，除非你逼它。

**实验 3：去掉熔断。** 把连续失败计数那段去掉，让一个不可达目标（放在 2 米外）成为任务目标。

观察：LLM 会一直重试到 `max_turns` 耗尽。它不会自己判断「这件事做不到」。文本 agent 里重试是廉价的，物理世界里每次重试都在消耗时间、磨损硬件、而且可能让场景更糟。

**实验 4：不区分失败类型。** 把 `FailureKind` 全部改成返回 `"操作失败"`。

观察：LLM 无法区分「看不见」（该换视角）和「够不到」（该放弃）。它会用同一种策略应对所有失败，通常是盲目重试。

**实验 5：并发/中断。** 在任务执行到一半时，手动在仿真里把方块移到别的地方（改 `data.qpos`）。

观察：这模拟真实场景里「有人动了东西」或者「物体自己滑落了」。你的 agent 完全没有察觉机制。这引出阶段 08 要解决的问题。

做完这五个实验，你会得到一个很具体的认识：**后端那套可靠性工具（幂等、重试、状态机、熔断）在这里全都需要，但语义都变了。** 幂等不再成立，重试需要先重新观测，状态机的状态在世界里而不在数据库里。

## 4.6 幂等性在物理世界的重新定义

你在后端里的幂等定义：同一个请求执行多次，效果和执行一次相同。

物理世界里这个定义直接失效。但有一个可用的替代概念：**幂等是关于目标状态的，不是关于动作的。**

```python
"""物理动作的幂等包装。

思路：不保证「动作执行一次和多次效果相同」，而是保证
「反复调用直到目标状态达成，且已达成时不再动作」。
这是声明式的幂等，类似 Kubernetes 的 reconcile 循环。
"""

from dataclasses import dataclass


@dataclass
class GoalState:
    """期望的目标状态，可被检验。

    关键设计：目标必须是可观测、可验证的，否则无法判断
    是否已经达成，也就无法实现幂等。
    """

    object_name: str
    target_position: np.ndarray
    tolerance: float = 0.03

    def is_satisfied(self, belief: WorldBelief) -> bool:
        """检查目标是否已达成。

        注意这里依赖 belief，也就是依赖观测。如果观测本身
        有误差，这个判断也会有误差——「以为放好了其实没放好」
        是真实存在的失败模式。
        """
        obj = belief.objects.get(self.object_name)
        if obj is None:
            return False
        distance = float(np.linalg.norm(obj.position - self.target_position))
        return distance <= self.tolerance


def reconcile_to_goal(
    skills: Any,
    belief: WorldBelief,
    goal: GoalState,
    max_attempts: int = 3,
) -> ToolResult:
    """反复尝试直到目标状态达成或耗尽尝试次数。

    这是把后端的 reconcile 模式搬到物理世界。每次循环开始
    都重新观测，因为上一次尝试可能已经改变了世界。

    这个函数是「幂等」的：如果目标已经达成，它什么都不做就返回成功。
    """
    for attempt in range(max_attempts):
        # 每次循环都重新观测，不信任上一轮的信念
        observations = skills.observe_scene()
        belief.update_from_observation(observations)

        if goal.is_satisfied(belief):
            return ToolResult(
                True,
                f"目标已达成（第 {attempt} 次检查）",
                observations={"attempts": attempt},
            )

        # 未达成，执行一次尝试
        pick_result = skills.pick(goal.object_name)
        if not pick_result.success:
            if pick_result.failure_kind == FailureKind.UNREACHABLE:
                # 不可达是永久性失败，重试无意义
                return pick_result
            continue

        skills.place(goal.target_position)

    return ToolResult(
        False,
        f"尝试 {max_attempts} 次后目标仍未达成",
        FailureKind.GRASP_FAILED,
        world_changed=True,
    )
```

💡 这个模式你应该很熟——它就是 Kubernetes 的 controller 循环，也是后端做 reconcile 的标准思路。物理世界让它变得更必要，因为你**永远无法确信一个动作成功了**，只能观测结果状态。

## 4.7 本阶段大作业

实现一个能完成多步任务的 agent，要求：

1. 任务：「把桌上所有方块按颜色分类放进对应的盒子」（场景里放 4 个方块 2 个盒子）
2. 世界信念跟踪完整实现，包括过期检测和主动失效
3. 失败类型区分至少 4 种，且每种有不同的应对策略
4. 实现熔断，连续失败后停止而不是无限重试
5. 实现 `reconcile_to_goal` 风格的目标态幂等
6. 全程结构化日志：每个决策、每个动作、每个观测都记录

第 6 条的日志要求不是走过场。建议格式：

```python
@dataclass
class ExecutionEvent:
    """一条执行记录。

    这份日志是阶段 08 的原材料——审计和证据链需要它。
    现在就按能被审计的标准记录，后面省很多事。
    """

    timestamp: float
    turn: int
    event_type: str  # llm_decision | tool_call | observation | failure
    tool_name: str | None
    arguments: dict[str, Any] | None
    result: dict[str, Any] | None
    world_belief_snapshot: dict[str, Any]
    reasoning: str | None  # LLM 给出的理由
```

**验收：** 4 个方块全部正确分类，且在中途注入噪声和一次人工干扰（手动移动方块）的情况下仍能完成。

## 4.8 这个阶段和你主业的关系

值得单独说一下：这个阶段做的事情会反向提升你的后端工作。

跑完实验 1 到 5 之后，回头看你自己的 agent 系统，问几个问题：

- 你的工具里有哪些其实是**不可逆**的？（发通知、下单、写外部系统、删数据）
- 这些工具失败后，你的重试逻辑假设了「世界没变」吗？
- 你的 agent 有「重新观测」的概念，还是一直信任第一次查询的结果？
- 你的失败类型区分够不够细，能让 LLM 做出不同应对吗？
- 你有熔断吗？还是靠 max_turns 兜底？

大部分文本 agent 系统在这几点上都是薄弱的，因为文本世界的失败大多确实可以原样重试，所以没人认真想过。做完具身这一段，你会开始在自己的系统里看到这些问题。

这也是为什么我说这条路对你不是纯消费——它给你一副新的眼镜。

## 验收标准

1. 为什么 LLM 不能放在控制回路里？三层的时间尺度各是多少？
2. `world_changed` 字段解决什么问题？没有它会发生什么？
3. 文本 agent 和物理 agent 在「重试」这件事上的根本差异是什么？
4. 为什么每轮都要重新注入世界信念，而不是依赖对话历史？
5. `ObjectBelief` 为什么叫 belief 而不是 state？
6. 物理世界里怎么重新定义幂等？为什么必须是声明式的？
7. 为什么失败类型必须细分？举例说明 UNREACHABLE 和 NOT_PERCEIVED 该有什么不同应对？
8. 「以为放好了其实没放好」这种失败模式怎么产生的？
9. 熔断为什么在物理世界比在后端更重要？

## 交付物检查

- [ ] 工具 schema 定义完整，description 里写清了前置条件和失败后果
- [ ] `WorldBelief` 实现了过期检测和主动失效
- [ ] Agent 主循环跑通，能完成至少 3 步的任务
- [ ] 五个撞墙实验全部做过，每个都能描述观察到的现象
- [ ] 实现了 `reconcile_to_goal` 目标态幂等
- [ ] 大作业完成：4 方块分类，含噪声和人工干扰
- [ ] 结构化执行日志完整，可以事后重建整个执行过程
- [ ] 回答了 4.8 节里关于自己主业系统的五个问题

## 下一步

到这里你的技能层还是手写代码（IK + 插值）。阶段 05 换成从数据里学出来的策略——这是通往 VLA 的第一步。

