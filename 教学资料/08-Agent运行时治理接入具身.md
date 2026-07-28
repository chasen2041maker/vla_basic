# 阶段 08：Agent 运行时治理接入具身

不设时间上限 · 硬件可选 · 产出：你自己的开源项目

## 为什么这个阶段最重要

阶段 01 到 07 是补课。你做的都是别人做过的事，而且很多人做得比你专业——做 VLA 的人有 CV 博士背景，做控制的人有十年经验。你在那些方向上很难做出差异。

这个阶段不一样。

具身领域现在的人大多是算法背景，关心的是「策略成功率能不能从 35% 提到 50%」。极少有人在系统层面认真问：

- 一个动作执行前，怎么判断它是否可逆、是否需要人确认？
- 失败之后世界状态已经变了，怎么安全地恢复？
- 长任务执行到一半需要人介入，怎么挂起、怎么续跑、怎么处理超时？
- 整个执行过程怎么留下可审计的证据？
- 多个技能并发时，怎么保证不会互相破坏对方的前置条件？

**这些正是生产级 Agent 运行时已经解决过的问题。** 任务生命周期管理（配额预留/提交/退款、ownership 租约、流式序号、取消、checkpoint 恢复、悬挂状态回收）、人在环挂起（语义 slot 抽取、运行中断点、超时过期），以及 AgentTrust Runtime 的 allow/ask/deny 加持久化审批加哈希链证据——这套东西搬到机器人上，就是具身领域缺的那一层。

所以这个阶段的定位是：**不是学新东西，是把你已有的能力翻译到新领域。**

## 8.1 能力映射表

先把你已有的东西和具身的需求对应起来。这张表是整个阶段的路线图。

| 文本 Agent 运行时里的机制 | 具身里对应的问题 | 难度变化 |
|---|---|---|
| ToolIntent/ToolResult 统一管线 | 技能调用的统一契约 | 相同 |
| allow / ask / deny 权限门禁 | 动作执行前的可逆性与授权判断 | 更重要（后果物理化） |
| 持久化审批 | 人在环确认，跨进程重启存活 | 相同 |
| 哈希链证据 | 执行过程的防篡改审计 | 相同 |
| HITL elicitation（挂起问人、24h 超时） | 「杯子里有水，要继续吗」 | 相同，但触发条件来自感知 |
| 任务生命周期 + checkpoint 恢复 | 长任务中断后从哪续 | 更难（世界状态无法回滚） |
| 配额预留/提交/退款 | 资源与时间预算管理 | 相同 |
| Outbox + 幂等 | 目标态 reconcile（阶段 04 讲过） | 语义变化，见 8.3 |
| reaper / recovery worker | 悬挂任务、超时、僵死状态回收 | 相同 |
| GroundGuard report_only 事实门禁 | 动作前的前置条件校验、动作后的结果核验 | 强类比，见 8.5 |
| 失败类型细分 | 决定重试/重规划/求助 | 更重要 |

看这张表你会发现:大部分是「相同」。这不是巧合——**Agent 运行时解决的一直是「不可靠工具 + 有状态长任务 + 需要审批和审计」这一类问题**,具身只是把工具从 shell 命令换成了机械臂。

真正变化的只有两处:世界状态不可回滚(8.3),以及前置条件来自带噪声的感知(8.5)。

## 8.2 动作可逆性分级

这是整个治理体系的基础。AgentTrust 里你按「文件读 / 文件写 / shell / git / MCP」分类工具风险。物理动作需要一套自己的分级。

```python
"""物理动作的可逆性分级与授权策略。

这是整个治理体系的基础设施。分级标准不是「危险程度」，
而是「出错后能否恢复，以及恢复成本」——这个区分很重要，
因为一个动作可能很安全但不可逆（把糖倒进咖啡），
也可能看着吓人但完全可逆（快速移动到某个位置）。
"""

from dataclasses import dataclass, field
from enum import IntEnum


class Reversibility(IntEnum):
    """可逆性等级，数值越大越不可逆。

    分级依据是「撤销这个动作需要什么」：

    FULLY_REVERSIBLE: 反向执行同一动作即可撤销。
      例：移动到某个位置（可以移回去）、张开夹爪（可以再合上）

    REVERSIBLE_WITH_EFFORT: 可以撤销，但需要额外的动作序列，
      且可能失败。例：把物体从 A 移到 B（可以移回来，但要重新抓取）

    PARTIALLY_IRREVERSIBLE: 主要状态可恢复，但有副作用残留。
      例：把积木塔推倒（可以重建，但顺序可能不同）

    IRREVERSIBLE: 无法通过机器人自身动作撤销。
      例：倒出液体、按下不可复位的按钮、切割、粘合

    DESTRUCTIVE: 不可逆且造成损害。
      例：打碎物体、撞坏设备、伤到人
    """

    FULLY_REVERSIBLE = 0
    REVERSIBLE_WITH_EFFORT = 1
    PARTIALLY_IRREVERSIBLE = 2
    IRREVERSIBLE = 3
    DESTRUCTIVE = 4


class AuthorizationMode(str, Enum):
    """授权模式，对应 AgentTrust 的 allow/ask/deny。"""

    ALLOW = "allow"          # 直接执行
    ASK = "ask"              # 需要人确认，阻塞等待
    ASK_ASYNC = "ask_async"  # 需要人确认，但挂起任务而非阻塞
    DENY = "deny"            # 拒绝执行


@dataclass
class ActionRisk:
    """一个动作的风险评估结果。

    注意 reversibility 和 confidence 是两个独立维度：
    一个「可逆」但「低置信度」的动作也可能需要人确认——
    因为低置信度意味着你不确定它到底会做什么。
    """

    reversibility: Reversibility
    confidence: float                    # 感知/策略的置信度 0-1
    affects_objects: list[str] = field(default_factory=list)
    estimated_force: float | None = None  # 牛顿，超过阈值需谨慎
    notes: str = ""

    def required_authorization(
        self,
        *,
        confidence_threshold: float = 0.7,
    ) -> AuthorizationMode:
        """根据风险决定授权模式。

        策略：
          - DESTRUCTIVE 一律拒绝，不给人确认的机会
            （因为人也可能误点，而后果不可承受）
          - IRREVERSIBLE 必须异步确认（挂起等人，不阻塞资源）
          - 低置信度升级一档
          - 其余放行
        """
        if self.reversibility >= Reversibility.DESTRUCTIVE:
            return AuthorizationMode.DENY

        if self.reversibility >= Reversibility.IRREVERSIBLE:
            return AuthorizationMode.ASK_ASYNC

        if self.confidence < confidence_threshold:
            # 置信度不足时升级：本来可以直接做的也要问
            if self.reversibility >= Reversibility.PARTIALLY_IRREVERSIBLE:
                return AuthorizationMode.ASK_ASYNC
            return AuthorizationMode.ASK

        return AuthorizationMode.ALLOW
```

💡 这个类的设计直接对应 AgentTrust 的 `ToolIntent`。差别是多了 `reversibility` 这个维度——在 shell 工具里 `rm -rf` 和 `ls` 的区别也是可逆性，但你当时可能是按「工具类型」而不是「可逆性」来分类的。物理世界让这个维度变成一等公民。

## 8.3 补偿而非回滚

这是从后端搬过来时**唯一需要根本重新设计**的地方。

后端的事务模型：要么全部成功，要么回滚到操作前的状态。物理世界没有回滚——你不能把倒出去的水收回来。

替代方案是 **Saga 模式**：为每个动作定义一个「补偿动作」，失败时执行补偿序列。这在分布式系统里你应该见过（跨服务事务用 Saga 而不是 2PC）。

```python
"""物理动作的 Saga 补偿。

核心认知：补偿不等于回滚。
- 回滚保证「状态回到操作前」
- 补偿只保证「达到一个可接受的状态」

比如「把杯子从桌上移到架子上」的补偿是「把杯子移回桌上」，
但杯子的朝向可能变了、位置差几厘米——这是可接受的，
不是完美还原。这个语义差异必须在设计时就承认。
"""

from dataclasses import dataclass, field
from typing import Callable, Protocol


class CompensableAction(Protocol):
    """可补偿的动作。"""

    def execute(self) -> ToolResult: ...
    def compensate(self) -> ToolResult: ...
    def can_compensate(self) -> bool: ...


@dataclass
class SagaStep:
    """Saga 中的一步。

    compensate 为 None 表示这一步不可补偿——一旦执行成功，
    整个 Saga 就跨过了一个不可返回的点。这类步骤必须在
    执行前经过 ASK 授权，因为它消除了后续的所有退路。
    """

    name: str
    execute: Callable[[], ToolResult]
    compensate: Callable[[], ToolResult] | None
    risk: ActionRisk

    @property
    def is_point_of_no_return(self) -> bool:
        return self.compensate is None


@dataclass
class SagaExecution:
    """Saga 执行器，带补偿。

    与后端 Saga 的三个关键差异：

    1. 补偿本身可能失败。物理动作没有「保证成功」的补偿。
       补偿失败后需要升级到人工介入，不能无限重试。

    2. 补偿前必须重新观测。世界可能已经变了，
       按记忆执行补偿可能造成新的破坏。

    3. 越过 point_of_no_return 后，前面的补偿可能变得无意义。
       比如你已经把水倒进杯子，再把杯子移回原位没有意义了。
    """

    steps: list[SagaStep]
    completed: list[SagaStep] = field(default_factory=list)
    crossed_no_return: bool = False

    def run(self, observe: Callable[[], None]) -> ToolResult:
        """顺序执行所有步骤，失败时反向补偿。"""
        for step in self.steps:
            # 越过不可返回点前，记录这个事实
            if step.is_point_of_no_return:
                self.crossed_no_return = True

            result = step.execute()

            if result.success:
                self.completed.append(step)
                continue

            # 失败：开始补偿
            if self.crossed_no_return:
                return ToolResult(
                    False,
                    f"步骤 {step.name} 失败，且已越过不可返回点 "
                    f"（已完成 {len(self.completed)} 步）。"
                    f"无法自动补偿，需要人工介入。",
                    FailureKind.PRECONDITION,
                    world_changed=True,
                )

            return self._compensate_all(observe, failed_step=step.name)

        return ToolResult(True, f"Saga 完成，共 {len(self.completed)} 步")

    def _compensate_all(
        self,
        observe: Callable[[], None],
        failed_step: str,
    ) -> ToolResult:
        """反向执行补偿动作。

        每次补偿前重新观测，因为上一次补偿也改变了世界。
        """
        failures: list[str] = []

        for step in reversed(self.completed):
            if step.compensate is None:
                failures.append(f"{step.name}: 无补偿动作")
                continue

            # 关键：每次补偿前重新观测
            observe()

            comp_result = step.compensate()
            if not comp_result.success:
                # 补偿失败不重试——可能会越补越糟
                failures.append(f"{step.name}: 补偿失败 ({comp_result.message})")

        if failures:
            return ToolResult(
                False,
                f"步骤 {failed_step} 失败，补偿过程也有问题: {'; '.join(failures)}。"
                f"需要人工检查现场。",
                FailureKind.PRECONDITION,
                world_changed=True,
            )

        return ToolResult(
            False,
            f"步骤 {failed_step} 失败，已成功补偿回可接受状态",
            world_changed=True,
        )
```

**必做设计练习：** 为下面这些动作写出补偿动作，或者论证它无法补偿：

1. 移动到某个位置
2. 抓起一个物体
3. 把物体从 A 放到 B
4. 打开抽屉
5. 把水从杯子倒进碗里
6. 把两块积木叠起来
7. 按下电源按钮

第 5 和第 7 是不可补偿的（point of no return）。第 4 和第 6 是「可补偿但不完美」。做完这个练习你会对可逆性分级有实感。

## 8.4 HITL：把 elicitation 搬过来

文本 Agent 里的 elicitation 机制——语义 slot 抽取、运行中断点、checkpoint 决策、最大轮次、超时过期——这套东西在具身里的价值比在文本里更大。

**文本场景的 elicitation：** 用户问「帮我分析这只股票」，agent 发现缺少「哪只股票」，挂起问人。

**具身场景的 elicitation：** 机器人执行「把杯子收起来」，走到跟前发现杯子里有水。这时该问人：「杯子里有液体，要先倒掉还是连着水一起放？」

区别在于**触发条件来自感知而不是来自指令解析**。这是新的部分，也是有意思的部分。

```python
"""具身场景的人在环挂起。

和文本 elicitation 的三个差异：

1. 触发源是感知发现的意外状态，不是指令里缺失的字段
2. 挂起期间机器人必须处于安全状态（不能举着重物等 24 小时）
3. 恢复时世界可能已经变了，必须重新观测再决定是否还能继续
"""

import time
from dataclasses import dataclass, field
from enum import Enum


class InterruptTrigger(str, Enum):
    """挂起的触发原因。"""

    MISSING_PARAMETER = "missing_parameter"      # 指令不完整（文本场景同款）
    UNEXPECTED_STATE = "unexpected_state"        # 感知发现意外（具身特有）
    IRREVERSIBLE_PENDING = "irreversible_pending"  # 即将执行不可逆动作
    LOW_CONFIDENCE = "low_confidence"            # 置信度不足
    REPEATED_FAILURE = "repeated_failure"        # 反复失败，需要人判断


@dataclass
class SafeParkingState:
    """挂起期间机器人的安全停放状态。

    这是具身特有的需求。文本 agent 挂起时什么都不用做，
    机器人挂起时必须先进入一个能长时间维持的状态：
      - 不能举着物体（舵机持续受力会发热）
      - 不能停在可能被撞到的位置
      - 不能挡住人的操作空间

    如果手里有东西，先放到一个安全的临时位置，
    并记录下来以便恢复时找回。
    """

    parked_at: np.ndarray
    released_object: str | None = None
    released_at: np.ndarray | None = None
    parked_time: float = field(default_factory=time.time)


@dataclass
class EmbodiedInterrupt:
    """一次挂起请求。

    timeout_seconds 的默认值可以沿用文本 Agent 的经验值（数小时到一天），
    但具身场景可能需要更短——机器人占用物理空间，
    长时间挂起会阻塞别人。
    """

    trigger: InterruptTrigger
    question: str
    options: list[str]
    observation_snapshot: dict
    parking: SafeParkingState
    created_at: float = field(default_factory=time.time)
    timeout_seconds: float = 3600.0
    answer: str | None = None

    def is_expired(self, now: float | None = None) -> bool:
        now = now or time.time()
        return (now - self.created_at) > self.timeout_seconds

    def can_resume(self, current_observation: dict) -> tuple[bool, str]:
        """判断是否还能从这个挂起点恢复。

        这是具身特有的检查。人回答完问题后，世界可能已经
        不是挂起时的样子了——目标物体被拿走了、有人重新
        摆过桌子、临时放下的物体不见了。

        返回 (能否恢复, 原因说明)。
        """
        # 检查临时放下的物体还在不在
        if self.parking.released_object:
            if self.parking.released_object not in current_observation:
                return False, (
                    f"临时放置的 {self.parking.released_object} 已不在原处，"
                    f"无法恢复原任务"
                )

        # 检查快照里的关键物体是否还在
        for name in self.observation_snapshot:
            if name not in current_observation:
                return False, f"物体 {name} 已消失，场景已变化"

        return True, "可以恢复"
```

**必做实验：** 在阶段 04 的 agent 里加一个 elicitation 触发点。做法：在场景里放一个「装了水的杯子」（用一个额外的属性标记），当 agent 要抓它时触发挂起，问人「要先倒掉吗」。

然后测试三种情况：

1. 人及时回答，正常恢复
2. 人不回答，超时后 agent 怎么处理
3. 人回答之前，你手动把杯子拿走，观察 `can_resume` 是否正确拒绝恢复

第 3 种情况是具身特有的,文本 agent 里不存在。

## 8.5 前置条件与结果核验：GroundGuard 的物理版

你的 GroundGuard 做的是：回答生成后，把关键声明和工具返回的事实做比对，不一致就标记。

物理版本是双向的：**动作前校验前置条件，动作后核验结果状态。**

```python
"""物理动作的前置条件与后置核验。

这是 GroundGuard 思路的直接移植：
  - GroundGuard: 声明 vs 工具事实
  - 这里: 期望状态 vs 观测状态

关键设计沿用 GroundGuard 的 report_only 优先原则：
先只观测和记录，不阻断。积累足够数据确认判据可靠后，
再开启 enforce 模式。这个上线姿势在物理系统上更重要，
因为误阻断会让机器人在半途卡死。
"""

from dataclasses import dataclass, field
from enum import Enum


class GateMode(str, Enum):
    """门禁模式。

    和 GroundGuard 的设计一致：先 report_only 观测，
    确认判据可靠后再 enforce。

    区别是物理系统多了一个 SAFE_STOP 模式——检测到问题时
    不是拒绝执行，而是让机器人进入安全状态后停下等人。
    """

    REPORT_ONLY = "report_only"
    ENFORCE = "enforce"
    SAFE_STOP = "safe_stop"


@dataclass
class Precondition:
    """一个可检验的前置条件。

    check 返回 (是否满足, 说明)。必须能从观测中判定，
    不能依赖内部状态记忆——因为记忆可能过期（阶段 04 讲过）。
    """

    name: str
    check: Callable[[dict], tuple[bool, str]]
    required: bool = True


@dataclass
class PostCondition:
    """动作执行后应当成立的状态。

    tolerance 很重要：物理世界里「杯子在架子上」不是精确判断，
    而是「在目标位置 ±3cm 内」。判据太严会误报失败，
    太松会漏过真实失败（比如杯子放歪了但还没倒）。
    """

    name: str
    check: Callable[[dict], tuple[bool, str]]
    tolerance: float = 0.03


@dataclass
class VerificationReport:
    """一次动作的前后校验报告。

    这份报告是审计链的原材料。即使在 REPORT_ONLY 模式下
    也要完整记录，因为它是你后续决定判据阈值的数据来源。
    """

    action_name: str
    mode: GateMode
    precondition_results: list[tuple[str, bool, str]] = field(default_factory=list)
    postcondition_results: list[tuple[str, bool, str]] = field(default_factory=list)
    blocked: bool = False

    @property
    def preconditions_passed(self) -> bool:
        return all(ok for _, ok, _ in self.precondition_results)

    @property
    def postconditions_passed(self) -> bool:
        return all(ok for _, ok, _ in self.postcondition_results)

    @property
    def silent_failure(self) -> bool:
        """静默失败：动作报告成功，但后置条件不满足。

        这是物理系统里最危险的一类失败——策略以为自己成功了，
        继续往下走，但实际状态和预期不符。后果会在几步之后
        以莫名其妙的方式爆发。

        检测这个是本节最重要的价值。
        """
        return not self.postconditions_passed
```

**`silent_failure` 是这一节的核心价值。**

回想阶段 06 的实验：VLA 对任何输入都会输出动作，不会说「我做不到」。而 ACT 策略抓空了也会继续执行后面的放置动作。**策略本身没有失败识别能力。**

所以「动作执行后核验结果状态」这一层必须由你的运行时提供。这是当前具身系统普遍缺失的一环，也是你最容易做出差异的地方。

**必做实验：** 在阶段 05 或 07 的策略外面包一层后置核验。统计一下:策略自己报告成功、但后置条件不满足的比例有多高。这个数字通常会让你意外。

## 8.6 执行证据链

你在 AgentTrust 里做的哈希链证据，在具身里的价值更直接：机器人做错了事，需要能回溯到底哪一步出了问题、当时看到了什么、谁批准的。

```python
"""物理执行的防篡改证据链。

和 AgentTrust 的哈希链设计相同，但记录内容多了物理世界特有的项：
  - 观测快照（图像哈希，不存原图以免爆炸）
  - 策略输出的原始动作 vs 安全层过滤后的动作
  - 关节实际到位值 vs 指令值
  - 授权决策及其依据
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field


@dataclass
class ExecutionRecord:
    """一条执行记录。

    prev_hash 构成链式结构，任何历史记录被改动都会导致
    后续所有哈希失配。

    注意 commanded_action 和 executed_action 分开记录：
    安全层可能修改了动作，事后排查时必须能区分
    「策略想做什么」和「实际做了什么」。
    """

    sequence: int
    timestamp: float
    action_name: str
    commanded_action: list[float]
    executed_action: list[float]
    safety_triggers: list[str]
    observation_hash: str
    authorization: str
    authorized_by: str | None
    risk_level: int
    verification: dict | None
    prev_hash: str

    def compute_hash(self) -> str:
        """计算这条记录的哈希。

        用 sort_keys 保证序列化确定性——否则字典顺序变化
        会导致同一条记录算出不同哈希。
        """
        payload = json.dumps(asdict(self), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class EvidenceChain:
    """执行证据链。

    append-only。verify 可以检出任何历史篡改。
    """

    records: list[ExecutionRecord] = field(default_factory=list)
    _last_hash: str = "0" * 64

    def append(self, **kwargs) -> ExecutionRecord:
        record = ExecutionRecord(
            sequence=len(self.records),
            timestamp=time.time(),
            prev_hash=self._last_hash,
            **kwargs,
        )
        self._last_hash = record.compute_hash()
        self.records.append(record)
        return record

    def verify(self) -> tuple[bool, str]:
        """验证整条链的完整性。"""
        expected_prev = "0" * 64
        for record in self.records:
            if record.prev_hash != expected_prev:
                return False, f"记录 {record.sequence} 的 prev_hash 失配"
            expected_prev = record.compute_hash()
        return True, f"链完整，共 {len(self.records)} 条记录"


def hash_observation(image: np.ndarray, joints: np.ndarray) -> str:
    """把观测压缩成一个哈希。

    不存原图的原因：一次任务几百帧，存图会让证据链体积爆炸。
    存哈希足够证明「当时的观测是这个」，配合单独的图像归档
    （按哈希命名）就能在需要时找回原图。
    """
    hasher = hashlib.sha256()
    hasher.update(np.ascontiguousarray(image).tobytes())
    hasher.update(np.ascontiguousarray(joints).tobytes())
    return hasher.hexdigest()
```

## 8.7 把它做成一个开源项目

前面几节是零件。这一节讲怎么把它们组装成一个别人能用的东西。

**项目定位建议：**

> 一个面向具身 Agent 的执行治理运行时：在机器人技能调用前实施可逆性分级与授权门禁，在执行后核验结果状态，支持人在环挂起与恢复，并产出可审计的执行证据链。

这个定位的好处是它**不和任何人竞争**。做 VLA 的人不做这个，做控制的人不做这个，而所有想把具身系统投入真实场景的人都需要这个。

**范围控制,第一版只做这些:**

1. 技能调用的统一契约（`SkillIntent` / `SkillResult`）
2. 可逆性分级与 allow/ask/deny 门禁
3. 前置条件校验 + 后置结果核验（report_only 优先）
4. 静默失败检测
5. 执行证据链
6. 一个 SO-101 或 MuJoCo 的参考适配器

**不要做的**（第一版）：

- 自己的策略实现（用 LeRobot 的）
- 自己的仿真器（用 MuJoCo）
- 通用的机器人抽象层（用 ROS 2 或者只支持一两种本体）
- Web UI（命令行 + 结构化日志就够）

**技术选型建议：**

- Python，因为具身生态是 Python
- 依赖尽量少。一个治理运行时如果自己拖进来十几个传递依赖，就没人愿意把它放进机器人控制链路
- 提供 MuJoCo 适配器作为零硬件的可运行示例——这决定了别人愿不愿意试用
- 测试覆盖要真实：目标是测试代码量和实现代码量相当，且集成测试跑在真实依赖上而不是全 mock

**README 要回答的三个问题：**

1. 没有这个东西会怎样（举一个具体的静默失败案例）
2. 五分钟能跑起来的例子（MuJoCo，无硬件）
3. 边界在哪（明确说不做什么，以及当前的验证状态）

第 3 条尤其重要。把「区分本地、共享环境、生产三级验证，证据不足时拒绝声称完成」这个习惯写进 README，会立刻和大部分项目区分开——具身领域的开源项目普遍在过度宣传，一个诚实标注「哪些验证过、哪些没有」的项目会显得可信得多。

## 8.8 阶段任务

**任务一：可逆性分级练习。** 完成 8.3 节的七个动作补偿设计，写成文档。这是纯思考任务，不用写代码，但它决定了后面所有设计的质量。

**任务二：静默失败测量。** 在阶段 05（仿真）或 07（真机）的策略外面包一层后置核验，跑 50 次，统计「策略报告成功但后置条件不满足」的比例。这个数字是你项目 README 里最有说服力的一句话。

**任务三：HITL 挂起。** 在阶段 04 的 agent 里实现 8.4 节的三个测试场景，特别是第三个（挂起期间世界被改变，`can_resume` 正确拒绝）。

**任务四：证据链。** 给你的执行流程接上 `EvidenceChain`，跑完一个任务后验证链完整性，并手动改一条历史记录，确认 `verify` 能检出。

**任务五：开源。** 把上面的东西整理成一个仓库，写好 README，附一个 MuJoCo 的可运行示例。

任务一到四每个几小时，任务五不设期限。

## 验收标准

1. 可逆性分级的依据是什么？为什么不按「危险程度」分？
2. 「可逆」和「高置信度」是同一个维度吗？为什么低置信度要升级授权？
3. 补偿（compensation）和回滚（rollback）的语义差异是什么？
4. 什么是 point of no return？越过它之后前面的补偿为什么可能失效？
5. 为什么补偿失败不能无限重试？
6. 具身 elicitation 的触发源和文本 elicitation 有什么不同？
7. 为什么机器人挂起前必须先进入安全停放状态？
8. `can_resume` 检查的是什么？文本 agent 为什么不需要这个？
9. 什么是静默失败？为什么策略本身检测不到它？
10. 为什么门禁要先上 report_only 而不是直接 enforce？
11. 证据链为什么要区分 commanded_action 和 executed_action？
12. 为什么观测只存哈希不存原图？

## 交付物检查

- [ ] 七个动作的补偿设计文档完成
- [ ] 静默失败比例测量完成，有具体数字
- [ ] HITL 挂起的三个场景全部实现并测试
- [ ] 证据链接入，篡改检测验证过
- [ ] 开源仓库建好，README 三个问题都回答了
- [ ] MuJoCo 可运行示例能在无硬件环境跑通
- [ ] 明确标注了当前的验证状态和边界

## 结语

到这里，你手里有两样东西：一份从零到真机的完整实践经历，以及一个别人做不出来的项目。

前者让你能和具身领域的人对话，后者是你的差异化。而两者都不需要你放弃已有的分布式后端和 Agent 运行时能力——恰恰相反，正是那些能力让第八阶段成为可能。

这条路的定位始终是：不是转行做具身，是**把 Agent 运行时的工程能力带进具身**。

