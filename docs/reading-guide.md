# Reading looped models and latent reasoning

**English** · [简体中文](reading-guide.zh-CN.md) · [Back to the catalog](../README.md#catalog)

The papers in this list extend computation in different ways. Before comparing results, establish **what is repeated, and which state is passed to the next step**. The table below is an editorial reading aid based on the primary sources, not a performance ranking.

## What changes in each approach?

| Work | What repeats | State carried | What to examine |
| --- | --- | --- | --- |
| [Universal Transformers](https://arxiv.org/abs/1807.03819) | One shared self-attentive transition, applied for a variable number of steps | Token states plus a step index | Separate the effect of weight sharing from adaptive halting: they are often bundled in one baseline. |
| [Programmable Looped Transformers](https://arxiv.org/abs/2301.13196) | A fixed block whose constructed weights execute an input-supplied program | A scratchpad written into the sequence | Distinguish a computational construction from an algorithm learned by training. |
| [Huginn](https://arxiv.org/abs/2502.05171) | The core block between a prelude and a coda, repeated at inference | Latent state `h` | Unique parameters versus executed depth, and measured step time rather than nominal loop count. |
| [Ouro](https://arxiv.org/abs/2510.25741) | A looped stack trained with learned depth allocation | Latent state | Read the pretraining recipe and the depth distribution together with the benchmark table. |
| [Parallel Loop Transformer](https://arxiv.org/abs/2510.24824) / [LoopCoder-v2](https://arxiv.org/abs/2606.18023) | Loop iterations parallelized across tokens, with first-loop KV sharing | Token states plus a shared KV cache | Execution dependencies, positional encoding, and latency at a stated batch size and sequence length. |
| [Mixture-of-Recursions](https://arxiv.org/abs/2507.10524) | A router assigns a recursion depth to each token | Per-token state and exit flags | Active tokens, KV handling and throughput, not just average loops. |
| [Loop the Loopies!](https://arxiv.org/abs/2607.16051) / [SMELT](https://arxiv.org/abs/2609.01343) | Layer-level recurrence inside a mixture-of-experts model | Latent state plus expert routing | Whether FLOPs, non-embedding parameters and KV cache are all matched; expert-selection collapse. |
| [Fixed-Point Reasoners](https://arxiv.org/abs/2606.18206) / [Attractor Models](https://arxiv.org/abs/2605.12466) | A loop trained to converge to an equilibrium | The fixed point itself | The convergence criterion, the halting rule, and what happens when no fixed point exists. |
| [Coconut](https://arxiv.org/abs/2412.06769) | Nothing architectural; the last hidden state becomes the next input embedding | A continuous thought | This is *not* a looped Transformer. Compare it on task and supervision, not on loop count. |
| [HRM](https://arxiv.org/abs/2506.21734) / [TRM](https://arxiv.org/abs/2510.04871) | Two coupled recurrent modules (HRM), or one tiny network alternating latent and answer updates (TRM) | Latent `z` and candidate answer `y` | Task scope, supervision, and the fixed-point assumptions the model relies on. |
| [Looped Diffusion Transformer](https://arxiv.org/abs/2609.40305) / [Looped Uniform Diffusion LMs](https://arxiv.org/abs/2610.30066) | Looping inside a denoising process | Noisy latents | The sampler and denoising budget; loop count and denoising steps are different currencies. |

## The anatomy of a looped model

Most architectures in the core track can be read as five choices:

1. **What is shared?** A single layer (Universal Transformer), a block (Huginn), a contiguous block repeated before advancing ([Block Recursive Transformers](https://arxiv.org/abs/2610.24998)), or a mid-stack range ([Loop the Loopies!](https://arxiv.org/abs/2607.16051)).
2. **Where does the loop sit?** Prelude–loop–coda designs keep the embedding and readout layers untied; mid-stack designs loop a fraction of the depth, often around 0.5.
3. **What is the update rule?** Plain residual reuse, a gated update, a contractive step, an ODE sub-step, or an attention-only recurrence.
4. **How many iterations?** Fixed at training, sampled, learned per token, or chosen at inference. These are not interchangeable.
5. **How is the result read out?** Last loop, an average over loops, a learned mixture, or a fixed-point solve.

Three axes are being traded against one another:

- **Depth** — iterations of shared weights; cheap in parameters, expensive in latency.
- **Width** — unique parameters and experts; expensive in memory, cheap in sequential steps.
- **Sequence** — output tokens and scratchpad; expensive in context and KV cache.

A paper that adds loops while holding width and sequence fixed is testing depth. A paper that adds loops *and* width is not. This is the most common source of inflated claims in the area.

## What to measure

Ask for these numbers explicitly; if a paper does not report one, say so rather than inferring it.

- **Stored parameters** versus **executed depth**. One recurrence is not one layer.
- **Training compute**: tokens × parameters × FLOPs per token, with the loop count included.
- **Inference compute**: loops actually executed, active tokens, and output tokens.
- **Latency and throughput** at a stated hardware, batch size, sequence length and precision.
- **KV-cache size** and whether it grows with loops, with sequence length, or neither.
- **Baselines matched on** FLOPs, non-embedding parameters and KV — all three, or state which one.
- **Readout choice** and whether it was tuned per benchmark.
- **Variance**: seeds, error bars, and whether the gain survives a change of task.

## Common comparison traps

1. **Loop count as a proxy for compute.** Parallel loops, adaptive halting and KV sharing change the cost per loop by large factors.
2. **Beating an unlooped model of the same parameter count.** The interesting comparison is at matched training FLOPs and matched inference cost, which is a different and usually smaller baseline.
3. **Training-matched but inference-unmatched.** A model can win at matched training compute and lose badly on latency or memory at serving time.
4. **Synthetic tasks presented as general reasoning.** Sudoku, maze and parity results are informative about algorithmic extrapolation, not about language-model quality.
5. **Readout leakage.** A learned readout or per-benchmark depth choice can absorb gains that are attributed to the loop.
6. **Selective reporting of loop counts.** “Up to 32 loops” may mean 32 on one benchmark and 4 elsewhere; look for the distribution.

## Glossary

- **Recurrent depth** — using the same weights at several depths within one forward pass.
- **Weight tying / sharing** — using one parameter set for multiple layers or iterations.
- **Loop count (T)** — the number of times the shared module is applied.
- **Prelude / coda** — the untied entry and exit blocks around a recurrent core.
- **Latent state** — the hidden representation carried between iterations.
- **ACT (adaptive computation time)** — a learned halting mechanism that decides when to stop iterating.
- **Ponder cost** — the expected number of steps, used as a training regularizer.
- **Fixed point** — a state `h` such that `F(h) = h`; the limit of a convergent loop.
- **Path independence** — converging to the same solution from different initializations.
- **KV cache** — stored keys and values for previously processed tokens; a major inference memory cost.
- **Parallel loops** — executing iterations for different tokens concurrently rather than sequentially.
- **Latent reasoning** — computation in hidden states without emitting intermediate tokens.
- **Continuous thought** — a hidden state fed back as the next input, as in Coconut.
- **Test-time compute** — computation spent at inference rather than during training.

## Reading list by goal

- **I need the architecture.** Universal Transformers → Programmable Looped Transformers → MoEUT → Relaxed Recursive Transformers → Huginn → Ouro.
- **I need the scaling evidence.** Huginn → Ouro → LoopCoder-v2 → Loop the Loopies! → SMELT → Iso-Depth Scaling Laws.
- **I need to make inference cheap.** Mixture-of-Recursions → Parallel Loop Transformer → Looped Latent Attention → LoopQ → LoopSpec → Do Halting Heads Really Save Compute?
- **I need a small reasoning model.** HRM → TRM → HRM: Perspectives and Misconceptions → Are Your Reasoning Models Reasoning or Guessing? → Fixed-Point Reasoners.
- **I need to apply it to a modality.** LoopCoder → LoopViT → RD-VLA → LatentMT → LoopGR.

Found an inaccurate distinction? Open an issue with the paper section or a primary-source link.
