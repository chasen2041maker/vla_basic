# 阶段 06：VLA 模型

预估投入 15-25 小时 · 需要 GPU · 产出：跑通 OpenVLA 推理与微调，理解 VLA 的能力边界

## 这个阶段要解决什么

阶段 05 的 ACT 是「一个任务一个模型」。换个任务要重新采数据、重新训练。而且它不理解语言——你没法告诉它「这次抓蓝色的」。

VLA（Vision-Language-Action）想解决这个：**一个模型，用自然语言指定任务，输出动作。**

这是当前具身领域最活跃的方向，也是最容易被夸大的方向。这个阶段的目标之一就是让你亲眼看到它的真实能力边界。

## 6.1 VLA 是什么

一句话：**拿一个视觉语言模型（VLM）当骨干，把输出头从「预测文本 token」改成「预测动作」。**

```
输入：图像（一路或多路相机）+ 文本指令（"pick up the red block"）
        │
        ▼
   VLM 骨干（如 PaliGemma、Prismatic、LLaVA）
        │
        ▼
输出：动作（关节角度 / 末端位姿增量 / 夹爪开合）
```

关键点在于**为什么要用 VLM 当骨干**：VLM 在互联网规模的图文数据上预训练过，已经知道「红色」「杯子」「左边」这些概念。ACT 从零学，需要你的演示数据里覆盖所有情况；VLA 可以借用预训练的语义知识。

这个思路和你熟悉的 LLM 微调是同一个套路：拿预训练模型，换个任务头，用少量领域数据微调。

## 6.2 主要模型谱系

按时间和影响力排：

| 模型 | 出处 | 关键特点 | 权重 |
|---|---|---|---|
| **RT-1** | Google, 2022 | 早期工作，EfficientNet + Transformer，离散化动作 | 未公开 |
| **RT-2** | Google, 2023 | 首次把 VLM 直接当骨干，动作当成文本 token 输出 | 未公开 |
| **OpenVLA** | Stanford 等, 2024 | 开源，7B，基于 Prismatic VLM，在 OXE 数据上训练 | 公开 |
| **π0 (pi-zero)** | Physical Intelligence, 2024 | flow matching 输出连续动作，跨本体 | 部分公开 |
| **π0.5** | Physical Intelligence, 2025 | π0 的迭代，强调开放世界泛化 | 部分公开 |
| **GR00T N1** | NVIDIA, 2025 | 人形机器人基座模型 | 公开 |

> ⚠️ 需核实：这个领域每几个月就有新模型，上表在 2026 年可能已经不是最新。查 Hugging Face 和 Papers with Code 的当前榜单。

**对你的建议：从 OpenVLA 入手。** 理由是权重完全公开、代码可读、社区文档足够、而且 7B 规模在单张 24G 卡上能微调（用 LoRA）。

π0 值得读论文理解思路（flow matching 输出连续动作比离散化更优雅），但它的工程复杂度更高，不适合作为第一个上手的模型。

## 6.3 动作怎么表示：这是 VLA 的核心设计问题

VLM 的输出头本来是预测词表上的概率分布。要输出动作，有两条路。

**路线一：离散化成 token（RT-2、OpenVLA 走这条）**

把每个动作维度的连续值分成 256 个 bin，每个 bin 映射到词表里一个 token。这样动作就变成了「文本」，可以直接复用 VLM 的自回归生成。

```python
"""动作的离散化与反离散化。

OpenVLA 用的就是这个方案。理解它的量化误差很重要——
256 个 bin 听起来很多，但如果动作范围是 ±0.1 米，
每个 bin 就是 0.78 毫米，而抓取精度要求可能就在这个量级。
"""

import numpy as np


class ActionTokenizer:
    """把连续动作离散化成 token id，以及反向解码。

    分位数归一化是关键细节：不用简单的 min-max，而是用
    训练数据的 1% 和 99% 分位数作为范围边界。这样极端的
    离群动作不会把整个范围拉宽，导致常规动作全挤在中间几个 bin 里。
    """

    def __init__(
        self,
        action_low: np.ndarray,
        action_high: np.ndarray,
        num_bins: int = 256,
        vocab_offset: int = 31744,
    ):
        self.action_low = action_low
        self.action_high = action_high
        self.num_bins = num_bins
        # 动作 token 占用词表末尾一段，避免和真实文本 token 冲突
        self.vocab_offset = vocab_offset

    def encode(self, action: np.ndarray) -> np.ndarray:
        """连续动作 -> token id 数组。"""
        # 归一化到 [0, 1]
        normalized = (action - self.action_low) / (self.action_high - self.action_low)
        normalized = np.clip(normalized, 0.0, 1.0)
        # 量化到 bin 索引
        bins = (normalized * (self.num_bins - 1)).round().astype(int)
        return bins + self.vocab_offset

    def decode(self, token_ids: np.ndarray) -> np.ndarray:
        """token id -> 连续动作。

        注意这里的量化误差是不可恢复的：encode 再 decode
        不等于原值。误差上界是 (high - low) / (num_bins - 1) / 2。
        """
        bins = np.clip(token_ids - self.vocab_offset, 0, self.num_bins - 1)
        normalized = bins / (self.num_bins - 1)
        return normalized * (self.action_high - self.action_low) + self.action_low

    def quantization_error_bound(self) -> np.ndarray:
        """返回每个动作维度的最大量化误差，单位和动作相同。

        动手算一下这个值，和你的任务精度要求对比。
        如果量化误差已经超过精度要求，离散化方案就不适用。
        """
        return (self.action_high - self.action_low) / (self.num_bins - 1) / 2.0
```

**必做：** 用你阶段 05 的数据算一下 `quantization_error_bound()`，和抓取需要的精度对比。这会让你直观理解离散化方案的局限。

**路线二：连续输出（π0 走这条）**

不离散化，用 flow matching 或扩散模型直接生成连续动作向量。优点是没有量化误差、天然支持动作分块、多模态表达能力强。缺点是需要额外的动作专家网络，架构更复杂。

这是当前的趋势方向。理解这个区别，你就理解了 VLA 从 RT-2 到 π0 的主要演进逻辑。

## 6.4 跨本体问题

一个 VLA 在 Franka 上训练，能不能用在 SO-101 上？

**基本上不能，除非专门处理。** 原因：

- 关节数量不同（7 自由度 vs 6 自由度）
- 关节限位和几何尺寸不同
- 相机位置和视角不同
- 夹爪形态不同

这就是**跨本体（cross-embodiment）**问题。当前的处理方案：

**方案一：统一动作空间。** 不用关节角度，用末端位姿增量（相对当前的 Δx, Δy, Δz, Δrotation, 夹爪开合）。这个表示对不同机械臂是通用的，具体怎么实现由各自的 IK 负责。OpenVLA 用的就是这个。

**方案二：大规模混合数据训练。** Open X-Embodiment（OXE）数据集聚合了 22 种机器人、100 多万条轨迹。在这上面训练，模型见过多种本体，泛化更好。OpenVLA 就是在 OXE 上训的。

**方案三：本体适配层。** 主干模型输出抽象动作，每个本体有自己的小适配网络。

对你的实际意义：**下载的 OpenVLA 权重不能直接在 SO-101 上用。** 需要在你自己采的 SO-101 数据上微调。这一点很多人忽略，然后困惑为什么零样本效果极差。

## 6.5 跑通 OpenVLA 推理

先做纯推理，不训练。目标是建立「图像 + 文本进，动作出」的直观。

```bash
pip install transformers accelerate
# OpenVLA 需要 flash-attn，Windows 上装可能有麻烦，
# 装不上就用 attn_implementation="eager" 退化到普通注意力
```

```python
"""OpenVLA 推理最小示例。

7B 模型用 bfloat16 大概占 15GB 显存。24G 卡够用，
12G 卡需要 8bit 量化加载。
"""

import numpy as np
import torch
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor

MODEL_ID = "openvla/openvla-7b"

processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForVision2Seq.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True,
).to("cuda")


def predict_action(
    image: Image.Image,
    instruction: str,
    unnorm_key: str = "bridge_orig",
) -> np.ndarray:
    """预测一个 7 维动作：(dx, dy, dz, droll, dpitch, dyaw, gripper)。

    unnorm_key 指定用哪个数据集的动作统计量做反归一化。
    这个参数选错会导致动作幅度完全不对——比如用 bridge 的
    统计量去解码在另一个数据集上微调的模型，动作可能大 10 倍。
    这是新手最常见的错误之一。
    """
    prompt = f"In: What action should the robot take to {instruction}?\nOut:"
    inputs = processor(prompt, image).to("cuda", dtype=torch.bfloat16)
    action = model.predict_action(**inputs, unnorm_key=unnorm_key, do_sample=False)
    return action


if __name__ == "__main__":
    image = Image.open("test_scene.png")
    for instruction in [
        "pick up the red block",
        "pick up the blue block",
        "move to the left",
        "do nothing",
    ]:
        action = predict_action(image, instruction)
        print(f"{instruction!r:35} -> {np.round(action, 4)}")
```

> ⚠️ 需核实：OpenVLA 的 `predict_action` 接口和 `unnorm_key` 可选值在版本间有变化，以仓库 README 为准。

**必做实验（这些是这个阶段最有价值的部分）：**

**实验 1：语言敏感性。** 同一张图，换不同指令，看动作变化。「pick up the red block」和「pick up the blue block」应该给出不同方向的动作。如果几乎没差别，说明模型没真正理解语言，只是在做视觉反射。

**实验 2：语言鲁棒性。** 用同义表述：「pick up the red block」/「grab the red cube」/「拿起红色方块」（中文）。观察动作是否一致。你会发现它对措辞很敏感，中文基本不работает（训练数据几乎全是英文）。

**实验 3：无意义指令。** 输入「do nothing」「fly to the moon」「asdfghjkl」。观察它会不会输出零动作或者拒绝——**它不会**。VLA 没有「拒绝执行」的概念，任何输入都会得到一个动作。这个观察对阶段 08 极其重要。

**实验 4：视觉分布外。** 换一个和训练数据风格差很多的场景（不同背景、不同光照、没见过的物体）。观察动作是否变得毫无意义。

做完这四个实验，你会对 VLA 的真实能力有一个校准的认识：**它是一个有用但脆弱的组件，不是一个可信的决策者。**

## 6.6 LoRA 微调

全量微调 7B 需要多卡。用 LoRA 在单卡上就能做。

```python
"""OpenVLA 的 LoRA 微调配置要点。

如果你做过 LLM 的 LoRA/QLoRA 微调，这部分不新鲜。
重点看下面几个 VLA 特有的注意事项。
"""

from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=32,
    lora_alpha=64,
    lora_dropout=0.05,
    # 只对语言模型部分加 LoRA，视觉骨干通常冻结
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

**VLA 微调的三个特有注意点：**

**1. 动作归一化统计量必须重算。** 你自己的数据的动作分布和预训练数据不同。用错统计量会让动作幅度差一个数量级。这是最常见的失败原因。

**2. 视觉骨干冻不冻。** 冻结省显存且不容易过拟合，但如果你的场景和预训练数据视觉差异很大（比如工业场景 vs 厨房），解冻视觉骨干的最后几层通常有帮助。

**3. 数据量需求比 ACT 大。** ACT 50 条能看到效果，VLA 微调通常需要几百条。因为你要教它的不只是动作，还有「这句话对应这个动作」的映射。

## 6.7 VLA 推理部署：和 vLLM 的关系

这一节专门讲清一个容易混淆的问题，因为它和你的主业相关。

**VLA 推理不能用 vLLM。** 原因：

| | LLM 服务（vLLM） | VLA 推理 |
|---|---|---|
| 请求模式 | 多用户高并发 | 单机器人，串行 |
| 优化目标 | 吞吐（tokens/s 总量） | 单次延迟 |
| batching | continuous batching 是核心优化 | 无可 batch 的并发请求 |
| 输出长度 | 几百到几千 token | 7 个 token（一个动作） |
| 延迟预算 | 几百毫秒可接受 | 20-50ms 硬约束 |
| 部署位置 | 数据中心 GPU | 机器人本体或边缘设备 |

vLLM 的核心优化（PagedAttention 管理大量并发请求的 KV cache）在只有一个机器人的场景里完全用不上。

**VLA 部署实际用什么：**

- **TensorRT / TensorRT-LLM** — NVIDIA 平台上的编译优化，延迟最低
- **ONNX Runtime** — 跨平台，方便部署到边缘设备
- **torch.compile** — 最省事，PyTorch 原生，能拿到可观的加速
- **量化** — INT8/INT4，在边缘设备上是必需的

延迟优化的思路也不同：LLM 服务想办法把更多请求塞进一个 batch，VLA 想办法把单次前向压到 20 毫秒以内。

💡 对你主业的意义：如果你想在这两个方向之间找一个共通的技能，是**边缘推理部署**（Jetson 上跑量化模型）。这个既是 AI Infra 的一部分，也是具身的实际需求。而 vLLM 那条线是纯 LLM 服务，和具身不通。

## 6.8 VLA 与 LLM 规划层的分工

现在你有两个「智能」组件：阶段 04 的 LLM 规划器和这里的 VLA。它们怎么配合？

标准分工：

```
用户：「把桌上的东西收拾干净」
        │
        ▼
LLM 规划器（阶段 04）
  - 理解模糊指令，问清「收拾到哪里」
  - 拆解成技能序列
  - 跟踪世界状态，处理失败重规划
  - 决定什么时候需要人介入
        │  下发原子技能："pick up the red block"
        ▼
VLA（本阶段）
  - 把这一句话 + 当前图像变成动作
  - 只管这一个动作，不管全局
        │
        ▼
     机器人
```

**为什么不让 VLA 直接做长任务？** 因为它不行：

- 没有长期记忆和状态跟踪
- 不会问问题，指令模糊时只能瞎猜
- 不会判断「这件事做不到」，任何输入都输出动作
- 没有失败识别能力，抓空了也会继续往下走

**为什么不让 LLM 直接输出动作？** 因为它慢（秒级）且不精确（没有视觉伺服能力）。

这个分工是当前的主流架构，也是你的切入点所在——**你的能力在上面那一层，而那一层现在做得普遍很粗糙。**

## 6.9 本阶段大作业

**任务一：能力边界报告。**

跑完 6.5 节的四个实验，写一份 VLA 能力边界报告，包含：

- 语言敏感性：换指令动作变化有多大（给出量化数据，比如动作向量的余弦相似度）
- 语言鲁棒性：同义表述的一致性，中文的表现
- 无意义输入的行为：它实际输出了什么
- 视觉分布外的退化程度

这份报告的价值在于它是你自己测出来的，而不是从论文里读到的。以后有人跟你说「VLA 已经能理解自然语言了」，你有数据可以回应。

**任务二：LoRA 微调。**

用阶段 05 采的数据微调 OpenVLA，但这次给每条轨迹加上语言标注（"pick up the red block" / "pick up the blue block"）。

要求：

1. 至少两种物体、两种指令
2. 重算动作归一化统计量
3. 评估时测「指令跟随准确率」——给出指令 A，它是不是真的去抓 A 而不是 B
4. 和阶段 05 的 ACT 对比：同样数据量下谁的成功率高

**预期结果：** 数据量少的时候 ACT 会赢，因为它专精单任务。VLA 的优势要在多任务和语言泛化上才体现出来。如果你的 VLA 微调效果比 ACT 差不少，那是正常的，不是你做错了。

**任务三（可选）：把 VLA 接进阶段 04 的 agent。**

把 `pick` 技能的实现从「IK + 插值」换成「调用 VLA」，保留阶段 04 的世界信念跟踪、失败分类、熔断机制。

这一步做完，你就有了一个完整的两层系统，而且是你自己搭的。

## 验收标准

1. VLA 和 ACT 的根本区别是什么？为什么要用 VLM 当骨干？
2. 动作离散化和连续输出两条路线各有什么优劣？RT-2 到 π0 的演进逻辑是什么？
3. 256 个 bin 的量化误差怎么算？你的任务精度要求和它比如何？
4. 跨本体问题是什么？三种处理方案各是什么思路？
5. 为什么下载的 OpenVLA 权重不能直接用在 SO-101 上？
6. `unnorm_key` 选错会导致什么现象？
7. VLA 微调时为什么必须重算动作归一化统计量？
8. 给 VLA 一个无意义指令，它会怎么做？这对系统设计意味着什么？
9. 为什么 VLA 推理用不上 vLLM？两者的优化目标差别在哪？
10. LLM 规划层和 VLA 的分工边界在哪？为什么不能只用其中一个？

## 交付物检查

- [ ] OpenVLA 推理跑通，能输出 7 维动作
- [ ] 四个能力边界实验全部完成，有量化数据
- [ ] 能力边界报告写完
- [ ] 算过量化误差上界，并和任务精度做了对比
- [ ] LoRA 微调跑通，动作统计量重算过
- [ ] 指令跟随准确率测出来了
- [ ] 和 ACT 的对比结果有数据
- [ ] （可选）VLA 接进了阶段 04 的 agent

## 下一步

到这里所有东西都在仿真里。阶段 07 上真机，你会遇到 sim2real 落差——这是整条路线上挫败感最强、但收获最大的一段。

