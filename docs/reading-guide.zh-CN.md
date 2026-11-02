# 如何阅读循环模型与潜在推理

[English](reading-guide.md) · **简体中文** · [返回目录](../README.zh-CN.md#catalog)

这个方向的论文用不同方式扩展计算。在比较结果之前，先确认：**什么被重复，什么状态被传给下一步。** 下表是依据一手文献整理的阅读辅助，不是性能排名。

## 每种方法改变了什么？

| 工作 | 重复什么 | 携带什么状态 | 阅读时该看什么 |
| --- | --- | --- | --- |
| [Universal Transformers](https://arxiv.org/abs/1807.03819) | 一个共享的自注意力变换，执行可变步数 | token 状态与步数索引 | 把权重共享的效果与自适应停止分开看：基线通常把两者绑在一起。 |
| [Programmable Looped Transformers](https://arxiv.org/abs/2301.13196) | 权重被构造好的固定块，执行输入中给出的程序 | 写入序列的草稿区 | 区分“构造性计算”与“训练学到的算法”。 |
| [Huginn](https://arxiv.org/abs/2502.05171) | prelude 与 coda 之间的核心块，在推理时重复 | 潜在状态 `h` | 独立参数与执行深度的区别，以及实测单步时间而非名义循环次数。 |
| [Ouro](https://arxiv.org/abs/2510.25741) | 带可学习深度分配的循环堆栈 | 潜在状态 | 把预训练配方、深度分布与基准表放在一起读。 |
| [Parallel Loop Transformer](https://arxiv.org/abs/2510.24824) / [LoopCoder-v2](https://arxiv.org/abs/2606.18023) | 跨 token 并行执行循环迭代，首轮共享 KV | token 状态与共享 KV 缓存 | 执行依赖、位置编码，以及在给定批大小与序列长度下的延迟。 |
| [Mixture-of-Recursions](https://arxiv.org/abs/2507.10524) | 路由器为每个 token 分配递归深度 | 逐 token 状态与退出标记 | 活跃 token、KV 处理与吞吐，而不只是平均循环次数。 |
| [Loop the Loopies!](https://arxiv.org/abs/2607.16051) / [SMELT](https://arxiv.org/abs/2609.01343) | MoE 模型内部的层级循环 | 潜在状态与专家路由 | FLOPs、非嵌入参数与 KV 是否同时匹配；专家选择是否坍缩。 |
| [Fixed-Point Reasoners](https://arxiv.org/abs/2606.18206) / [Attractor Models](https://arxiv.org/abs/2605.12466) | 被训练到收敛于平衡点的循环 | 不动点本身 | 收敛判据、停止规则，以及不存在不动点时会发生什么。 |
| [Coconut](https://arxiv.org/abs/2412.06769) | 架构上没有循环；最后一个隐状态作为下一步输入嵌入 | 连续思维 | 这**不是**循环 Transformer。应在任务与监督上比较，而不是比循环次数。 |
| [HRM](https://arxiv.org/abs/2506.21734) / [TRM](https://arxiv.org/abs/2510.04871) | 两个耦合的循环模块（HRM），或一个小网络交替更新潜在状态与答案（TRM） | 潜在 `z` 与候选答案 `y` | 任务范围、监督方式，以及模型依赖的不动点假设。 |
| [Looped Diffusion Transformer](https://arxiv.org/abs/2609.40305) / [Looped Uniform Diffusion LMs](https://arxiv.org/abs/2610.30066) | 在去噪过程内部做循环 | 带噪潜在状态 | 采样器与去噪预算；循环次数与去噪步数是两种不同的“货币”。 |

## 循环模型的结构解剖

核心路线的大多数架构都可以拆成五个选择：

1. **共享什么？** 单层（Universal Transformer）、块（Huginn）、先重复再前进的连续块（[Block Recursive Transformers](https://arxiv.org/abs/2610.24998)），还是中段的一段层（[Loop the Loopies!](https://arxiv.org/abs/2607.16051)）。
2. **循环放在哪？** prelude–循环–coda 结构不共享嵌入与读出层；中段结构只循环一部分深度，常见比例约为 0.5。
3. **更新规则是什么？** 普通残差复用、门控更新、收缩步、ODE 子步，还是只有注意力的循环。
4. **迭代多少次？** 训练时固定、随机采样、逐 token 学习，还是推理时决定。这几种不能互换。
5. **结果如何读出？** 最后一轮、各轮平均、学习式混合，还是求解不动点。

三条轴在互相交换：

- **深度**——共享权重的迭代次数；参数便宜，延迟昂贵。
- **宽度**——独立参数与专家；显存昂贵，串行步数便宜。
- **序列**——输出 token 与草稿区；上下文与 KV 缓存昂贵。

在固定宽度与序列的前提下增加循环，检验的是深度；同时增加循环与宽度，就不是。这是本领域最常见的夸大来源。

## 应该测量什么

主动索取这些数字；如果论文没有报告，就注明缺失，而不是自行推算。

- **存储参数**与**执行深度**。一次循环不等于一层。
- **训练算力**：token 数 × 参数量 × 每 token FLOPs，并计入循环次数。
- **推理算力**：实际执行的循环、活跃 token 与输出 token。
- **延迟与吞吐**：注明硬件、批大小、序列长度与精度。
- **KV 缓存大小**：是否随循环增长、随序列长度增长，还是都不增长。
- **基线对齐**：FLOPs、非嵌入参数与 KV 三项是否都匹配；只匹配一项时要说明是哪一项。
- **读出方式**：是否针对每个基准单独调过。
- **方差**：随机种子、误差棒，以及换任务后收益是否仍在。

## 常见的比较陷阱

1. **把循环次数当作算力代理。** 并行循环、自适应停止与 KV 共享会让每轮成本相差数倍。
2. **只赢过同参数量的非循环模型。** 更有意义的比较是在匹配训练 FLOPs 与匹配推理成本下进行，而那个基线通常更小、更强。
3. **训练算力匹配，推理成本不匹配。** 模型可能在训练算力上占优，却在服务时的延迟或显存上大幅落后。
4. **把合成任务当作通用推理。** 数独、迷宫与奇偶校验的结果说明算法外推能力，不说明语言模型质量。
5. **读出泄漏。** 学习式读出或逐基准选择深度，可能把收益算到循环头上。
6. **选择性报告循环次数。** “最高 32 轮”可能只在一个基准上成立；要找到完整的分布。

## 术语表

- **循环深度（recurrent depth）**——在一次前向中让同一组权重出现在多个深度。
- **权重绑定 / 共享（weight tying）**——多层或多轮迭代共用一套参数。
- **循环次数（T）**——共享模块被应用的次数。
- **Prelude / coda**——循环核心前后不共享的入口块与出口块。
- **潜在状态（latent state）**——在迭代之间传递的隐藏表示。
- **ACT（自适应计算时间）**——学习何时停止迭代的机制。
- **Ponder 成本**——期望步数，常作为训练正则项。
- **不动点（fixed point）**——满足 `F(h) = h` 的状态，即收敛循环的极限。
- **路径无关性（path independence）**——从不同初始化都收敛到同一解。
- **KV 缓存**——为已处理 token 存储的键与值；推理显存的主要开销之一。
- **并行循环（parallel loops）**——让不同 token 的迭代并发执行，而非串行。
- **潜在推理（latent reasoning）**——在隐藏状态中计算，不输出中间 token。
- **连续思维（continuous thought）**——把隐状态作为下一步输入，如 Coconut。
- **测试时计算（test-time compute）**——在推理阶段而非训练阶段投入的计算。

## 按目标选读

- **我要看架构。** Universal Transformers → Programmable Looped Transformers → MoEUT → Relaxed Recursive Transformers → Huginn → Ouro。
- **我要看扩展证据。** Huginn → Ouro → LoopCoder-v2 → Loop the Loopies! → SMELT → Iso-Depth 扩展律。
- **我要把推理做便宜。** Mixture-of-Recursions → Parallel Loop Transformer → Looped Latent Attention → LoopQ → LoopSpec → Do Halting Heads Really Save Compute?
- **我要一个小型推理模型。** HRM → TRM → HRM: Perspectives and Misconceptions → Are Your Reasoning Models Reasoning or Guessing? → Fixed-Point Reasoners。
- **我要用到某个模态。** LoopCoder → LoopViT → RD-VLA → LatentMT → LoopGR。

发现区分不准确？请带着论文小节或一手链接开 issue。
