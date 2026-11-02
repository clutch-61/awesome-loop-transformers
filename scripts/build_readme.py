#!/usr/bin/env python3
"""Render README.md and README.zh-CN.md from data/papers.json.

Usage:
    python scripts/build_readme.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "papers.json").read_text(encoding="utf-8"))

ANCHORS = {
    "Foundations & Theory": "foundations--theory",
    "Architectures & Scaling": "architectures--scaling",
    "Latent Reasoning": "latent-reasoning",
    "Adaptive Compute": "adaptive-compute",
    "Training, Stability & Analysis": "training-stability--analysis",
    "Interpretability": "interpretability",
    "Post-Training & RL": "post-training--rl",
    "Tiny Recursive Reasoners": "tiny-recursive-reasoners",
    "Efficiency & Systems": "efficiency--systems",
    "Applications & Modalities": "applications--modalities",
    "Safety, Monitoring & Alignment": "safety-monitoring--alignment",
    "Broader Latent Reasoning": "broader-latent-reasoning",
}

CATS = DATA["categories"]
PAPERS = DATA["papers"]
TOTAL = len(PAPERS)
CODE_N = sum(1 for p in PAPERS if p.get("code"))

START = [
    ("1807.03819", "The canonical depth-recurrent Transformer. Read for the baseline every later paper measures against."),
    ("2301.13196", "What a looped Transformer can execute: programs, scratchpads and the limits of a construction proof."),
    ("2502.05171", "Recurrent depth at language-model scale. The modern reference point for latent test-time compute."),
    ("2510.25741", "Looped pretraining at 7.7T tokens with learned depth allocation — the recipe paper."),
    ("2507.10524", "Per-token recursion depth. The cleanest adaptive-compute design in the core track."),
    ("2510.24824", "Parallel loop execution, first-loop KV sharing and gated attention — the latency paper."),
    ("2412.06769", "The contrast case: latent reasoning by feeding hidden states back as inputs, without block reuse."),
    ("2506.21734", "The small recursive reasoner that restarted the tiny-model line."),
    ("2510.04871", "A minimal recursive model with strong puzzle results and an unusually honest ablation set."),
    ("2606.18023", "Compute-matched evidence that two loops can pay, plus the positional cost of parallel loops."),
    ("2607.16051", "MoE + layer-looping at 20B-A2B: the 2026 compute-matching result in full."),
    ("2609.01343", "Scaling laws with FLOPs, non-embedding parameters and KV cache jointly matched."),
]

START_ZH = {
    "1807.03819": "深度循环 Transformer 的经典形式；后续工作几乎都以它为基线。",
    "2301.13196": "循环 Transformer 能执行什么：程序、草稿纸，以及构造性证明的边界。",
    "2502.05171": "语言模型规模的循环深度；潜在测试时计算的现代参照点。",
    "2510.25741": "7.7T token 的循环预训练与可学习深度分配——配方论文。",
    "2507.10524": "逐 token 的递归深度；核心路线中最清晰的自适应计算设计。",
    "2510.24824": "并行循环执行、首轮 KV 共享与门控注意力——延迟论文。",
    "2412.06769": "对照案例：不循环复用块，而是把隐状态作为下一步输入来做潜在推理。",
    "2506.21734": "重新点燃小型递归推理器路线的 HRM。",
    "2510.04871": "极简递归模型，在谜题上表现强劲，消融也异常诚实。",
    "2606.18023": "算力匹配下“两轮循环就够”的证据，以及并行循环的位置代价。",
    "2607.16051": "20B-A2B 的 MoE + 层循环：2026 年算力匹配结果的全貌。",
    "2609.01343": "同时匹配 FLOPs、非嵌入参数与 KV 缓存的扩展律。",
}

FINDINGS_EN = """1. **Recurrence is a parameter-efficiency trade, not free depth.** Iso-depth scaling puts one recurrence at roughly r^0.46 unique parameters, and the compute-matched wins of 2026 need MoE + mid-stack looping + two loops — not loops replacing parameters. ([Iso-Depth Scaling Laws](https://arxiv.org/abs/2604.21106) · [SMELT](https://arxiv.org/abs/2609.01343) · [Loop the Loopies!](https://arxiv.org/abs/2607.16051))
2. **Loop count splits into two regimes.** At a fixed pretraining budget, two loops is the common operating point (Loopie, LoopCoder-v2, SMELT, Nanbeige4.2); when inference compute is the variable, models run to 32–64 loops (Huginn) or to convergence (fixed-point reasoners).
3. **Loop placement is converging on the middle of the stack.** Depth fraction ≈ 0.5 is the recurring choice, and MoE loops want layer-mode rather than stack-mode recurrence. ([How to Loop MoE](https://arxiv.org/abs/2609.35751) · [Block Recursive Transformers](https://arxiv.org/abs/2610.24998))
4. **Two design philosophies coexist.** Treat a pretrained mid-stack as an ODE flow (sub-step, keep the endpoint) or train the loop to be a fixed point ([Fixed-Point Reasoners](https://arxiv.org/abs/2606.18206) · [Attractor Models](https://arxiv.org/abs/2605.12466)). The choice changes both training stability and what "more loops" means at inference.
5. **Stability is turning from folklore into theory.** Residual scaling 1/N, the DeepLoop exponent, LayerNorm as implicit gain control, and learning-rate transfer across loop counts now have derivations behind them. ([Residual Scaling](https://arxiv.org/abs/2606.18524) · [DeepLoop](https://arxiv.org/abs/2607.13491))
6. **Matched training compute is not matched inference cost.** Latency, KV memory and quantization are three separate problems with separate fixes: parallel loops, cross-loop KV compression, 2–4 bit loop-aware quantization and speculative decoding. ([PLT](https://arxiv.org/abs/2510.24824) · [Looped Latent Attention](https://arxiv.org/abs/2607.15456) · [LoopQ](https://arxiv.org/abs/2605.16343))
7. **Latent loops and explicit chain-of-thought are complements.** LoopCoder-v2 reports super-additive gains when both are used; LOTUS closes the gap from the other direction. Standard GRPO mis-assigns credit across loops, which is why RLTT and LoopRPT change the credit assignment rather than the architecture.
8. **Loops manipulate knowledge; they do not store it.** Recurrent depth helps composition and retrieval from what is already in the weights. Pairing loops with retrieval, long context or a larger MoE expert bank is the pattern that keeps working.
9. **Adaptive depth is not automatically a saving.** Several 2026 papers find halting gates that do not reduce measured compute, and depth adaptation that pays only as a late training stage. ([Do Halting Heads Really Save Compute?](https://arxiv.org/abs/2610.32246) · [Adaptive-Depth Is a Finishing Stage](https://arxiv.org/abs/2610.14252))
10. **The evidence base is uneven.** Most 2026 entries are arXiv preprints; many results are at ≤1B parameters or on synthetic tasks. Compare at matched FLOPs, parameters and KV, and check whether latency is measured rather than inferred from loop count."""

FINDINGS_ZH = """1. **循环是参数效率的交换，不是免费的深度。** 等深扩展律给出的近似是：一次循环约等于 r^0.46 个独立参数；2026 年算力匹配下的收益来自 MoE + 中段循环 + 两轮循环，而不是用循环替代参数。（[Iso-Depth 扩展律](https://arxiv.org/abs/2604.21106) · [SMELT](https://arxiv.org/abs/2609.01343) · [Loop the Loopies!](https://arxiv.org/abs/2607.16051)）
2. **循环次数分成两种范式。** 固定预训练预算时，两轮是常见工作点（Loopie、LoopCoder-v2、SMELT、Nanbeige4.2）；推理算力可变时，模型会跑到 32–64 轮（Huginn），或一直迭代到收敛（不动点推理器）。
3. **循环位置正在向层堆栈中段收敛。** 深度比例约 0.5 是反复出现的选择；MoE 更适合层模式而非整栈循环。（[How to Loop MoE](https://arxiv.org/abs/2609.35751) · [Block Recursive Transformers](https://arxiv.org/abs/2610.24998)）
4. **两种设计哲学并存。** 把预训练中段当作 ODE 流（走子步、保留终点），或把循环训练成不动点（[Fixed-Point Reasoners](https://arxiv.org/abs/2606.18206) · [Attractor Models](https://arxiv.org/abs/2605.12466)）。这同时改变训练稳定性与“更多循环”在推理时的含义。
5. **稳定性正在从经验变成理论。** 1/N 残差缩放、DeepLoop 指数、LayerNorm 的隐式增益控制、跨循环数的学习率迁移，都有了推导支撑。（[Residual Scaling](https://arxiv.org/abs/2606.18524) · [DeepLoop](https://arxiv.org/abs/2607.13491)）
6. **训练算力匹配不等于推理成本匹配。** 延迟、KV 显存与量化是三个独立问题：并行循环、跨轮 KV 压缩、2–4 bit 循环感知量化与投机解码各有解法。（[PLT](https://arxiv.org/abs/2510.24824) · [Looped Latent Attention](https://arxiv.org/abs/2607.15456) · [LoopQ](https://arxiv.org/abs/2605.16343)）
7. **潜在循环与显式思维链是互补的。** LoopCoder-v2 报告两者叠加有超加性收益；LOTUS 则从另一侧缩小差距。标准 GRPO 会错配跨循环的信用，因此 RLTT 与 LoopRPT 改的是信用分配而不是架构。
8. **循环操作知识，不存储知识。** 循环深度帮助组合与检索权重中已有的内容；把循环与检索、长上下文或更大的 MoE 专家库配合，是持续有效的模式。
9. **自适应深度不自动等于省算力。** 2026 年多篇论文发现停止门控并未降低实测计算，或深度自适应只在训练后段作为“收尾阶段”才有收益。（[Do Halting Heads Really Save Compute?](https://arxiv.org/abs/2610.32246) · [Adaptive-Depth Is a Finishing Stage](https://arxiv.org/abs/2610.14252)）
10. **证据基础参差不齐。** 2026 年的条目大多是 arXiv 预印本，不少结果在 ≤1B 参数或合成任务上取得。比较时至少对齐 FLOPs、参数量与 KV，并确认延迟是实测而非由循环次数推算。"""


def esc(s):
    return s.replace("|", "\\|")


def render_catalog(lang):
    out = []
    for cat in CATS:
        name = cat["name"] if lang == "en" else cat["nameZh"]
        blurb = cat["blurb"] if lang == "en" else cat["blurbZh"]
        items = [p for p in PAPERS if p["category"] == cat["name"]]
        out.append(f'<a id="{ANCHORS[cat["name"]]}"></a>')
        out.append("")
        out.append(f"### {name}")
        out.append("")
        out.append(blurb)
        out.append("")
        years = sorted({p["date"][:4] for p in items}, reverse=True)
        for y in years:
            group = [p for p in items if p["date"][:4] == y]
            group.sort(key=lambda p: (p["date"], p["id"]), reverse=True)
            if lang == "en":
                summary_label = f"{len(group)} papers" if len(group) != 1 else "1 paper"
            else:
                summary_label = f"{len(group)} 篇"
            out.append("<details>")
            out.append(f"<summary><strong>{y}</strong> · {summary_label}</summary>")
            out.append("")
            for p in group:
                star = " ⭐" if p.get("star") else ""
                out.append(f'- **[{esc(p["title"])}]({p["paper"]})**{star}<br>')
                out.append(f'  {esc(p["authors"])} · *{esc(p["venue"])}*<br>')
                out.append(f'  {esc(p["summary"][lang])}<br>')
                links = [f'[Paper]({p["paper"]})']
                if p.get("code"):
                    links.append(f'[Code]({p["code"]})')
                if p.get("project"):
                    links.append(f'[Project]({p["project"]})')
                if p.get("deepDiveEn"):
                    links.append(f'[Deep dive]({p["deepDiveEn"]})')
                    links.append(f'[中文精读]({p["deepDiveZh"]})')
                if p.get("zhPdf"):
                    links.append(f'[中译 PDF]({p["zhPdf"]})')
                out.append("  " + " · ".join(links))
                out.append("")
            out.append("</details>")
            out.append("")
        out.append(f'[↑ Back to catalog](#catalog)' if lang == "en" else f'[↑ 返回目录](#catalog)')
        out.append("")
    return "\n".join(out)


def catalog_table(lang):
    rows = []
    head = (
        "| Topic | Works | What it covers |\n| --- | :---: | --- |"
        if lang == "en"
        else "| 主题 | 篇数 | 内容 |\n| --- | :---: | --- |"
    )
    rows.append(head)
    for c in CATS:
        name = c["name"] if lang == "en" else c["nameZh"]
        blurb = c["blurb"] if lang == "en" else c["blurbZh"]
        rows.append(f'| **[{name}](#{ANCHORS[c["name"]]})** | {c["count"]} | {blurb} |')
    return "\n".join(rows)


def start_table(lang):
    if lang == "en":
        rows = ["| Work | Year | Why read it |", "| --- | --- | --- |"]
    else:
        rows = ["| 工作 | 年份 | 为什么读 |", "| --- | --- | --- |"]
    for pid, why in START:
        p = next(x for x in PAPERS if x["id"] == pid)
        year = p["date"][:4]
        title = p["title"]
        if len(title) > 78:
            title = title.split(":")[0]
        reason = why if lang == "en" else START_ZH[pid]
        rows.append(f'| **[{esc(title)}]({p["paper"]})** | {year} | {reason} |')
    return "\n".join(rows)


def open_models(lang):
    if lang == "en":
        return """| Model | Params | Tokens | Loops | Links |
| --- | --- | --- | --- | --- |
| Huginn-0125 | 3.5B dense | 0.8T | random at train, free at test (mean 32) | [HF](https://huggingface.co/tomg-group-umd/huginn-0125) · [code](https://github.com/seal-rg/recurrent-pretraining) |
| Ouro 1.4B / 2.6B (+Thinking) | dense | 7.7T | 4 | [site](http://ouro-llm.github.io) |
| LoopCoder-V2 | 7B dense PLT | 18T | 2 | [HF](https://huggingface.co/Multilingual-Multimodal-NLP/LoopCoder-V2) |
| Loopie-20B-A2B / 6B-A0.6B | MoE | 3.5T | 2 (layer-loop) | [paper](https://arxiv.org/abs/2607.16051) |
| Nanbeige4.2-3B | 3B | 28T | 2 | [paper](https://arxiv.org/abs/2607.22083) |"""
    return """| 模型 | 参数 | Token 数 | 循环 | 链接 |
| --- | --- | --- | --- | --- |
| Huginn-0125 | 3.5B dense | 0.8T | 训练随机、推理自由（均值 32） | [HF](https://huggingface.co/tomg-group-umd/huginn-0125) · [代码](https://github.com/seal-rg/recurrent-pretraining) |
| Ouro 1.4B / 2.6B (+Thinking) | dense | 7.7T | 4 | [主页](http://ouro-llm.github.io) |
| LoopCoder-V2 | 7B dense PLT | 18T | 2 | [HF](https://huggingface.co/Multilingual-Multimodal-NLP/LoopCoder-V2) |
| Loopie-20B-A2B / 6B-A0.6B | MoE | 3.5T | 2（层循环） | [论文](https://arxiv.org/abs/2607.16051) |
| Nanbeige4.2-3B | 3B | 28T | 2 | [论文](https://arxiv.org/abs/2607.22083) |"""


def deep_table(lang):
    rows = []
    core = [
        ("1807.03819", "01_universal_transformers"),
        ("2502.05171", "02_recurrent_depth_huginn"),
        ("2605.23872", "03_training_free_looped"),
        ("2606.18023", "04_loopcoder_v2"),
        ("2607.16051", "05_loop_the_loopies"),
    ]
    base = "https://github.com/asimfish/awesome_loop_transformer/blob/main"
    if lang == "en":
        rows.append("| Work | Report (EN) | Report (ZH) | Layout-preserving 中译 PDF |")
        rows.append("| --- | --- | --- | --- |")
    else:
        rows.append("| 工作 | 英文报告 | 中文精读 | 保版式中译 PDF |")
        rows.append("| --- | --- | --- | --- |")
    for pid, slug in core:
        p = next(x for x in PAPERS if x["id"] == pid)
        rows.append(
            f'| **{esc(p["title"])}** | [EN]({base}/reports/en/{slug}.md) | [中文]({base}/reports/zh/{slug}.md) | [PDF]({base}/papers/zh/{pid}.zh.pdf) |'
        )
    return "\n".join(rows)


def counts_by_year():
    ys = {}
    for p in PAPERS:
        y = p["date"][:4]
        ys[y] = ys.get(y, 0) + 1
    return " · ".join(f"{y}: {n}" for y, n in sorted(ys.items(), reverse=True))


def head(lang):
    if lang == "en":
        return f"""<p align="center"><img src="assets/hero.svg" alt="A prelude, a shared recurrent block applied T times, and a coda." width="100%" /></p>

<h1 align="center">Awesome Loop Transformers &amp; Latent Reasoning</h1>

<p align="center"><strong>Looped Transformers, recurrent depth, latent reasoning, and test-time compute.<br>A bilingual, annotated reading guide — {TOTAL} papers, 12 topics, open models, and deep dives.</strong></p>

<p align="center"><a href="https://awesome.re"><img alt="Awesome" src="https://awesome.re/badge.svg"></a>&nbsp;<a href="#catalog"><img alt="Papers" src="https://img.shields.io/badge/papers-{TOTAL}-5df2ff?style=flat-square"></a>&nbsp;<a href="LICENSE"><img alt="License: CC BY 4.0" src="https://img.shields.io/badge/license-CC%20BY%204.0-a78bfa?style=flat-square"></a>&nbsp;<a href="CONTRIBUTING.md"><img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-c6ff4a?style=flat-square"></a></p>

<p align="center"><strong>English</strong> · <a href="README.zh-CN.md">简体中文</a> · <a href="docs/reading-guide.md">Reading guide</a> · <a href="https://github.com/clutch-61/awesome-loop-transformers/issues/new?template=paper-suggestion.yml">Suggest a paper</a></p>

<p align="center"><sub>{TOTAL} works · 2015–2026 · {CODE_N} with official code · bilingual summaries · updated {DATA["lastUpdated"]}</sub></p>

---

Looped Transformers reuse the same weights more than once: a shared layer, block, or stack is applied repeatedly to a latent state before a readout. The idea is old — Universal Transformers date to 2018 — but it became a serious scaling axis in 2025–2026, as Huginn, Ouro, Loopie and SMELT showed that extra depth can buy reasoning without extra output tokens.

This list collects that line of work together with the adaptive-compute machinery that decides how many loops to run, the systems work that makes looping affordable, and the adjacent latent-reasoning literature (Coconut, HRM, TRM, and others). It merges and extends two earlier lists: [Mrkkew/Awesome-Loop-Transformers](https://github.com/Mrkkew/Awesome-Loop-Transformers) and [asimfish/awesome_loop_transformer](https://github.com/asimfish/awesome_loop_transformer).

**Scope.** The core track is models that reuse a learned Transformer layer, block, or stack through depth within one forward pass, plus their theory, training, systems and applications. The broader track is latent-reasoning work that computes in hidden states without necessarily reusing blocks; it is kept in a separate category so the two are not conflated.

## Contents

| | |
| --- | --- |
| [Start here](#start-here) | Twelve papers that anchor the field |
| [Reading paths](#reading-paths) | Five routes through the catalog |
| [What the literature supports](#what-the-literature-supports) | Ten findings, with caveats |
| [How to read a paper](#how-to-read-a-paper) | A six-question checklist |
| [Catalog](#catalog) | {TOTAL} works in 12 topics |
| [Open models](#open-models) | Weights you can download |
| [Surveys and deep dives](#surveys-and-deep-dives) | Longer-form companions |
| [Industry signals](#industry-signals) | Reporting that is not peer-reviewed |
| [Code and tools](#code-and-tools) | Reference implementations |
| [Contributing](#contributing) · [Citation](#citation) · [Acknowledgements](#acknowledgements) | |

"""
    return f"""<p align="center"><img src="assets/hero.svg" alt="Prelude、共享循环块重复 T 次、Coda 的结构示意图" width="100%" /></p>

<h1 align="center">Awesome Loop Transformers &amp; Latent Reasoning</h1>

<p align="center"><strong>循环 Transformer、循环深度、潜在推理与测试时计算。<br>一份中英双语、逐条注释的阅读地图——{TOTAL} 篇论文，12 个主题，开放模型与深度解读。</strong></p>

<p align="center"><a href="https://awesome.re"><img alt="Awesome" src="https://awesome.re/badge.svg"></a>&nbsp;<a href="#catalog"><img alt="Papers" src="https://img.shields.io/badge/papers-{TOTAL}-5df2ff?style=flat-square"></a>&nbsp;<a href="LICENSE"><img alt="License: CC BY 4.0" src="https://img.shields.io/badge/license-CC%20BY%204.0-a78bfa?style=flat-square"></a>&nbsp;<a href="CONTRIBUTING.md"><img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-c6ff4a?style=flat-square"></a></p>

<p align="center"><a href="README.md">English</a> · <strong>简体中文</strong> · <a href="docs/reading-guide.zh-CN.md">阅读指南</a> · <a href="https://github.com/clutch-61/awesome-loop-transformers/issues/new?template=paper-suggestion.yml">推荐论文</a></p>

<p align="center"><sub>{TOTAL} 篇工作 · 2015–2026 · {CODE_N} 篇有官方代码 · 双语摘要 · 更新于 {DATA["lastUpdated"]}</sub></p>

---

循环 Transformer 会让同一组权重在一次前向中重复使用：共享的层、块或层堆栈被反复作用于一个潜在状态，最后再读出结果。这个想法并不新——Universal Transformer 早在 2018 年就提出了——但 2025–2026 年 Huginn、Ouro、Loopie、SMELT 等工作让它重新成为一条严肃的扩展轴：不增加输出 token，也能用额外深度换取推理能力。

本仓库收录这条路线上的论文与系统，以及决定“循环多少次”的自适应计算机制、让循环变得可负担的系统工作，和相邻的潜在推理文献（Coconut、HRM、TRM 等）。它合并并扩展了两份此前的清单：[Mrkkew/Awesome-Loop-Transformers](https://github.com/Mrkkew/Awesome-Loop-Transformers) 与 [asimfish/awesome_loop_transformer](https://github.com/asimfish/awesome_loop_transformer)。

**范围。** 核心路线指在一次前向中复用 Transformer 层、块或层堆栈的模型，以及它们的理论、训练、系统与应用；广义路线指在隐藏状态中完成计算、但不一定复用块的潜在推理工作。两者分列，避免混为一谈。

## 目录

| | |
| --- | --- |
| [从这里开始](#start-here) | 十二篇奠基性论文 |
| [阅读路线](#reading-paths) | 五条穿过目录的路线 |
| [文献支持了什么](#what-the-literature-supports) | 十条结论及其限定条件 |
| [如何读一篇论文](#how-to-read-a-paper) | 六问检查表 |
| [完整目录](#catalog) | {TOTAL} 篇工作，12 个主题 |
| [开放模型](#open-models) | 可直接下载的权重 |
| [综述与深度解读](#surveys-and-deep-dives) | 更长的伴读材料 |
| [产业信号](#industry-signals) | 未经同行评审的报道 |
| [代码与工具](#code-and-tools) | 参考实现 |
| [贡献](#contributing) · [引用](#citation) · [致谢](#acknowledgements) | |

"""


def body_en():
    return f"""<a id="start-here"></a>

## Start here

Twelve entry points, in reading order. ⭐ marks them in the catalog below.

{start_table("en")}

<a id="reading-paths"></a>

## Reading paths

**Architecture, in one afternoon.** [Universal Transformers](https://arxiv.org/abs/1807.03819) → [Programmable Looped Transformers](https://arxiv.org/abs/2301.13196) → [MoEUT](https://arxiv.org/abs/2405.16039) → [Relaxed Recursive Transformers](https://arxiv.org/abs/2410.20672) → [Huginn](https://arxiv.org/abs/2502.05171) → [Ouro](https://arxiv.org/abs/2510.25741) → [Towards Looped Models Done Right, Part I](https://arxiv.org/abs/2610.23036).

**Reasoning and scaling.** [Huginn](https://arxiv.org/abs/2502.05171) → [Ouro](https://arxiv.org/abs/2510.25741) → [LoopCoder-v2](https://arxiv.org/abs/2606.18023) → [Loop the Loopies!](https://arxiv.org/abs/2607.16051) → [SMELT](https://arxiv.org/abs/2609.01343) → [Iso-Depth Scaling Laws](https://arxiv.org/abs/2604.21106) → [Loop, Think, & Generalize](https://arxiv.org/abs/2604.07822).

**Adaptive and efficient inference.** [ACT](https://arxiv.org/abs/1603.08983) → [PonderNet](https://arxiv.org/abs/2107.05407) → [Mixture-of-Recursions](https://arxiv.org/abs/2507.10524) → [Think-at-Hard](https://arxiv.org/abs/2511.08577) → [PLT](https://arxiv.org/abs/2510.24824) → [Looped Latent Attention](https://arxiv.org/abs/2607.15456) → [LoopSpec](https://arxiv.org/abs/2609.17184) → [Do Halting Heads Really Save Compute?](https://arxiv.org/abs/2610.32246).

**Tiny recursive reasoners.** [HRM](https://arxiv.org/abs/2506.21734) → [TRM](https://arxiv.org/abs/2510.04871) → [HRM: Perspectives and Misconceptions](https://arxiv.org/abs/2510.00355) → [Are Your Reasoning Models Reasoning or Guessing?](https://arxiv.org/abs/2601.10679) → [Fixed-Point Reasoners](https://arxiv.org/abs/2606.18206).

**Applications.** [LoopCoder](https://arxiv.org/abs/2605.23872) → [Nanbeige4.2-3B](https://arxiv.org/abs/2607.22083) → [RD-VLA](https://arxiv.org/abs/2602.07845) → [LatentMT](https://arxiv.org/abs/2607.18618) → [LoopGR](https://arxiv.org/abs/2610.34157).

<a id="what-the-literature-supports"></a>

## What the literature supports

Ten claims that recur across the papers, stated with their limits. Points 1–8 condense the survey in [awesome_loop_transformer](https://github.com/asimfish/awesome_loop_transformer); points 9–10 are our reading of the 2026 preprint record.

{FINDINGS_EN}

<a id="how-to-read-a-paper"></a>

## How to read a paper in this area

The first question is always **what is repeated, and which state is passed to the next step?** Then ask:

- **Capacity.** How many unique parameters are stored, and which modules are shared? Executed depth is not stored depth.
- **Computation.** How many loops, active tokens, and output tokens are used? Are training and inference budgets reported separately?
- **Execution.** What are measured latency, throughput and peak memory, at which hardware, batch size and sequence length? A loop count is not a latency measurement.
- **Baselines.** Are FLOPs, non-embedding parameters and KV cache matched, or only one of them? A looped model that beats a smaller unlooped model proves little.
- **Readout.** Last loop, average of loops, or a learned readout? LoopCoder-v2 and the fixed-point line make different choices here.
- **Evidence class.** Proof, synthetic algorithm task, language-model benchmark, or product claim? These answer different questions.

See the [reading guide](docs/reading-guide.md) for a mechanism-by-mechanism comparison, common comparison traps, and a glossary.

<a id="catalog"></a>

## Catalog

{catalog_table("en")}

{render_catalog("en")}

<a id="open-models"></a>

## Open models

Checkpoints that make the looped-model claims reproducible. Loop counts are those reported by the authors.

{open_models("en")}

<a id="surveys-and-deep-dives"></a>

## Surveys and deep dives

| Resource | What it is |
| --- | --- |
| [A Survey on Latent Reasoning](https://arxiv.org/abs/2507.06203) | A taxonomy of latent-reasoning methods, including but not limited to looped models. |
| [Interactive catalog](https://awesome-loop-transformers.liyulin.workers.dev/#catalog) | Search the 247-entry source catalog by title, author or model. |
| [awesome_loop_transformer survey (EN)](https://github.com/asimfish/awesome_loop_transformer/blob/main/survey/en/survey_en.md) · [(ZH)](https://github.com/asimfish/awesome_loop_transformer/blob/main/survey/zh/survey_zh.md) | A ~60-paper map, timeline, ten trend insights and open problems. |
| [Loop Transformers reading guide](https://github.com/Mrkkew/Awesome-Loop-Transformers/blob/main/docs/reading-guide.md) | The companion guide from the other source list: what to examine in each mechanism. |
| [This repository's reading guide](docs/reading-guide.md) | A merged, extended version with a comparison table, traps and a glossary. |

Five core papers have full-length reports, layout-preserving Chinese translations, and object-level QA records:

{deep_table("en")}

Read together, the five reports trace one argument: Universal Transformers establish the architecture and its halting variants; Huginn turns recurrence into a pretraining and inference-budget recipe; Training-Free Looped asks whether a pretrained model can be looped without retraining; LoopCoder-v2 makes the compute-matched case for two loops; and Loop the Loopies! carries the argument to MoE layer-looping at 20B-A2B.

The full report PDFs are [here (EN)](https://github.com/asimfish/awesome_loop_transformer/blob/main/reports/pdf/awesome_loop_transformer_report_en.pdf) and [here (ZH)](https://github.com/asimfish/awesome_loop_transformer/blob/main/reports/pdf/awesome_loop_transformer_report_zh.pdf).

<a id="industry-signals"></a>

## Industry signals

These are secondary reports, not peer-reviewed evidence. Read them as claims about deployment, not about architecture.

- **GPT-6 Astra** — [release page](https://openai.com/index/gpt-6-astra/). No architectural details disclosed.
- **"Secret Technique Behind OpenAI's Astra Model Sparks Security Concerns"** — The Information, 2026-09-02, by Stephanie Palazzolo. Reports "recurrent depth" from anonymous sources; paywalled.
- **Thread: five papers behind recurrent depth** — [@nrehiew_](https://x.com/nrehiew_/status/2095115984873062675), [@kimmonismus](https://x.com/kimmonismus/status/2095045887131087357).
- **《刚刚，GPT-6 Astra 背后的 Loop 技术全被挖出来了》** — PaperAgent, WeChat, 2026-09. [article](https://mp.weixin.qq.com/s/7vEMyFVpf2O9WL4Lu4gSFQ).

<a id="code-and-tools"></a>

## Code and tools

- **[recurrent-pretraining](https://github.com/seal-rg/recurrent-pretraining)** — Huginn's training and sampling code.
- **[Ouro](http://ouro-llm.github.io)** — model family, checkpoints and technical report.
- **[LoopCoder-V2](https://huggingface.co/Multilingual-Multimodal-NLP/LoopCoder-V2)** — 7B parallel-loop code model.
- **[LOOM](https://github.com/hed-ucas/LOOM)** — looping beyond two passes for MoE.
- **[xllm-loop](https://github.com/ifm-ai/xllm-loop)** — looped-model design axes, including topology and input injection.
- **[InfiLoop](https://github.com/pixeli99/InfiLoop)** — loop-native attention residuals for very long test-time iteration.

<a id="contributing"></a>

## Contributing

Add or correct an entry in [`data/papers.json`](data/papers.json), then regenerate both READMEs:

```bash
python scripts/build_readme.py
```

Each paper needs `id`, `date`, `title`, `authors`, `venue`, `category`, `tags`, `summary` (`en` and `zh`), and `paper`; `code`, `project`, `star` and `deepDiveEn`/`deepDiveZh` are optional. Keep the venue to the published venue or `arXiv <year>`, add an official code link when one exists, and write the summary as a claim about what the paper shows rather than a restatement of its title. Please keep the two language summaries aligned in meaning.

Corrections to claims, numbers, or attributions are as welcome as new papers. Open an issue if you are unsure where an entry belongs.

<a id="citation"></a>

## Citation

```bibtex
@misc{{awesome_loop_transformers_2026,
  title  = {{Awesome Loop Transformers: Looped Transformers, Recurrent Depth and Latent Reasoning}},
  author = {{{{awesome-loop-transformers contributors}}}},
  year   = {{2026}},
  url    = {{https://github.com/clutch-61/awesome-loop-transformers}}
}}
```

<a id="acknowledgements"></a>

## Acknowledgements

This list merges two prior projects, both released under CC BY 4.0:

- **[Mrkkew/Awesome-Loop-Transformers](https://github.com/Mrkkew/Awesome-Loop-Transformers)** — 247-paper bilingual catalog, topic taxonomy and reading guide. Entries carried over from it keep their English and Chinese summaries.
- **[asimfish/awesome_loop_transformer](https://github.com/asimfish/awesome_loop_transformer)** — 122-paper curated list, five deep-dive reports, layout-preserving Chinese translations, survey, slides and the open-models table. Entries unique to it were summarized here from their arXiv abstracts; the reports and translations remain in the original repository and are linked, not copied.

Summaries added for this merged list are released under the same license. Original papers remain under their authors' licenses.

## License

Text and data are released under [CC BY 4.0](LICENSE). The scripts in `scripts/` are released under the MIT license ([LICENSE-CODE](LICENSE-CODE)).
"""


def body_zh():
    return f"""<a id="start-here"></a>

## 从这里开始

十二个入口，按阅读顺序排列。目录中以 ⭐ 标出。

{start_table("zh")}

<a id="reading-paths"></a>

## 阅读路线

**一个下午搭起架构脉络。** [Universal Transformers](https://arxiv.org/abs/1807.03819) → [Programmable Looped Transformers](https://arxiv.org/abs/2301.13196) → [MoEUT](https://arxiv.org/abs/2405.16039) → [Relaxed Recursive Transformers](https://arxiv.org/abs/2410.20672) → [Huginn](https://arxiv.org/abs/2502.05171) → [Ouro](https://arxiv.org/abs/2510.25741) → [Towards Looped Models Done Right, Part I](https://arxiv.org/abs/2610.23036)。

**推理与扩展。** [Huginn](https://arxiv.org/abs/2502.05171) → [Ouro](https://arxiv.org/abs/2510.25741) → [LoopCoder-v2](https://arxiv.org/abs/2606.18023) → [Loop the Loopies!](https://arxiv.org/abs/2607.16051) → [SMELT](https://arxiv.org/abs/2609.01343) → [Iso-Depth 扩展律](https://arxiv.org/abs/2604.21106) → [Loop, Think, & Generalize](https://arxiv.org/abs/2604.07822)。

**自适应与高效推理。** [ACT](https://arxiv.org/abs/1603.08983) → [PonderNet](https://arxiv.org/abs/2107.05407) → [Mixture-of-Recursions](https://arxiv.org/abs/2507.10524) → [Think-at-Hard](https://arxiv.org/abs/2511.08577) → [PLT](https://arxiv.org/abs/2510.24824) → [Looped Latent Attention](https://arxiv.org/abs/2607.15456) → [LoopSpec](https://arxiv.org/abs/2609.17184) → [Do Halting Heads Really Save Compute?](https://arxiv.org/abs/2610.32246)。

**微型递归推理器。** [HRM](https://arxiv.org/abs/2506.21734) → [TRM](https://arxiv.org/abs/2510.04871) → [HRM: Perspectives and Misconceptions](https://arxiv.org/abs/2510.00355) → [Are Your Reasoning Models Reasoning or Guessing?](https://arxiv.org/abs/2601.10679) → [Fixed-Point Reasoners](https://arxiv.org/abs/2606.18206)。

**应用。** [LoopCoder](https://arxiv.org/abs/2605.23872) → [Nanbeige4.2-3B](https://arxiv.org/abs/2607.22083) → [RD-VLA](https://arxiv.org/abs/2602.07845) → [LatentMT](https://arxiv.org/abs/2607.18618) → [LoopGR](https://arxiv.org/abs/2610.34157)。

<a id="what-the-literature-supports"></a>

## 文献支持了什么

十条在论文中反复出现的结论，同时写明它们的边界。第 1–8 条浓缩自 [awesome_loop_transformer](https://github.com/asimfish/awesome_loop_transformer) 的综述；第 9–10 条是我们对 2026 年预印本的解读。

{FINDINGS_ZH}

<a id="how-to-read-a-paper"></a>

## 如何读一篇论文

第一个问题永远是：**什么被重复，什么状态被传给下一步？** 然后依次问：

- **容量。** 存储了多少独立参数，哪些模块共享？执行深度不等于存储深度。
- **计算。** 用了多少轮循环、多少活跃 token、多少输出 token？训练与推理预算是否分开报告？
- **执行。** 在什么硬件、批大小与序列长度下，实测的延迟、吞吐与峰值显存是多少？循环次数不是延迟测量。
- **基线。** FLOPs、非嵌入参数与 KV 缓存是对齐了，还是只对齐了其中一项？循环模型打赢一个更小的非循环模型，说明不了太多。
- **读出方式。** 取最后一轮、各轮平均，还是学习式读出？LoopCoder-v2 与不动点路线在这里做了不同选择。
- **证据类型。** 证明、合成算法任务、语言模型基准，还是产品宣称？它们回答的是不同问题。

机制逐项对比、常见比较陷阱与术语表见[阅读指南](docs/reading-guide.zh-CN.md)。

<a id="catalog"></a>

## 完整目录

{catalog_table("zh")}

{render_catalog("zh")}

<a id="open-models"></a>

## 开放模型

可复现循环模型结论的公开权重。循环次数为作者报告值。

{open_models("zh")}

<a id="surveys-and-deep-dives"></a>

## 综述与深度解读

| 资源 | 内容 |
| --- | --- |
| [A Survey on Latent Reasoning](https://arxiv.org/abs/2507.06203) | 潜在推理方法的分类综述，不限于循环模型。 |
| [交互式目录](https://awesome-loop-transformers.liyulin.workers.dev/#catalog) | 按标题、作者或模型检索源清单的 247 条记录。 |
| [awesome_loop_transformer 综述（英文）](https://github.com/asimfish/awesome_loop_transformer/blob/main/survey/en/survey_en.md) · [（中文）](https://github.com/asimfish/awesome_loop_transformer/blob/main/survey/zh/survey_zh.md) | 约 60 篇论文的地图、时间线、十条趋势判断与开放问题。 |
| [Loop Transformers 阅读指南](https://github.com/Mrkkew/Awesome-Loop-Transformers/blob/main/docs/reading-guide.md) | 另一份源清单的伴读指南：每种机制该看什么。 |
| [本仓库阅读指南](docs/reading-guide.zh-CN.md) | 合并并扩展后的版本，含对比表、比较陷阱与术语表。 |

五篇核心论文配有完整精读报告、保版式中译与逐对象 QA 记录：

{deep_table("zh")}

五篇报告连起来是一条论证线：Universal Transformers 确立架构与停止机制；Huginn 把循环变成预训练与推理预算配方；Training-Free Looped 追问预训练模型能否不经重训直接循环；LoopCoder-v2 给出“两轮循环”的算力匹配证据；Loop the Loopies! 把论证推进到 20B-A2B 的 MoE 层循环。

完整报告 PDF：[英文](https://github.com/asimfish/awesome_loop_transformer/blob/main/reports/pdf/awesome_loop_transformer_report_en.pdf) · [中文](https://github.com/asimfish/awesome_loop_transformer/blob/main/reports/pdf/awesome_loop_transformer_report_zh.pdf)。

<a id="industry-signals"></a>

## 产业信号

以下为二手报道，不是同行评审证据。请把它们当作关于部署的说法，而不是关于架构的证据。

- **GPT-6 Astra** — [发布页](https://openai.com/index/gpt-6-astra/)，未披露架构细节。
- **《Secret Technique Behind OpenAI's Astra Model Sparks Security Concerns》** — The Information，2026-09-02，Stephanie Palazzolo。匿名信源称其使用“循环深度”；付费墙。
- **关于循环深度背后五篇论文的讨论串** — [@nrehiew_](https://x.com/nrehiew_/status/2095115984873062675)、[@kimmonismus](https://x.com/kimmonismus/status/2095045887131087357)。
- **《刚刚，GPT-6 Astra 背后的 Loop 技术全被挖出来了》** — PaperAgent，微信公众号，2026-09。[文章](https://mp.weixin.qq.com/s/7vEMyFVpf2O9WL4Lu4gSFQ)。

<a id="code-and-tools"></a>

## 代码与工具

- **[recurrent-pretraining](https://github.com/seal-rg/recurrent-pretraining)** — Huginn 的训练与采样代码。
- **[Ouro](http://ouro-llm.github.io)** — 模型系列、权重与技术报告。
- **[LoopCoder-V2](https://huggingface.co/Multilingual-Multimodal-NLP/LoopCoder-V2)** — 7B 并行循环代码模型。
- **[LOOM](https://github.com/hed-ucas/LOOM)** — 让 MoE 循环超过两轮。
- **[xllm-loop](https://github.com/ifm-ai/xllm-loop)** — 循环模型的设计轴，包括拓扑与输入注入。
- **[InfiLoop](https://github.com/pixeli99/InfiLoop)** — 面向极长测试时迭代的循环原生注意力残差。

<a id="contributing"></a>

## 贡献

在 [`data/papers.json`](data/papers.json) 中新增或修正条目，然后重新生成两份 README：

```bash
python scripts/build_readme.py
```

每条需要 `id`、`date`、`title`、`authors`、`venue`、`category`、`tags`、`summary`（`en` 与 `zh`）和 `paper`；`code`、`project`、`star`、`deepDiveEn`/`deepDiveZh` 可选。会议/期刊字段填正式发表出处或 `arXiv <年份>`；有官方代码就补上；摘要请写“这篇论文证明了什么”，而不是复述标题，并保持中英文含义一致。

对论断、数字与署名的更正，和对新论文的补充同样欢迎。不确定条目该放哪一类时，直接开 issue。

<a id="citation"></a>

## 引用

```bibtex
@misc{{awesome_loop_transformers_2026,
  title  = {{Awesome Loop Transformers: Looped Transformers, Recurrent Depth and Latent Reasoning}},
  author = {{{{awesome-loop-transformers contributors}}}},
  year   = {{2026}},
  url    = {{https://github.com/clutch-61/awesome-loop-transformers}}
}}
```

<a id="acknowledgements"></a>

## 致谢

本清单合并了两个此前的项目，二者均以 CC BY 4.0 发布：

- **[Mrkkew/Awesome-Loop-Transformers](https://github.com/Mrkkew/Awesome-Loop-Transformers)** — 247 篇论文的双语目录、主题分类与阅读指南。沿用的条目保留其英文与中文摘要。
- **[asimfish/awesome_loop_transformer](https://github.com/asimfish/awesome_loop_transformer)** — 122 篇论文的精选清单、五篇精读报告、保版式中译、综述、幻灯片与开放模型表。仅见于该清单的条目，其摘要由我们根据 arXiv 摘要重新撰写；精读报告与中译仍保留在原仓库，此处只做链接，不复制。

为合并清单新增的摘要以相同许可发布。原始论文仍归各自作者所有。

## 许可

文本与数据以 [CC BY 4.0](LICENSE) 发布；`scripts/` 下的代码以 MIT 许可发布（[LICENSE-CODE](LICENSE-CODE)）。
"""


def main():
    (ROOT / "README.md").write_text(head("en") + body_en(), encoding="utf-8")
    (ROOT / "README.zh-CN.md").write_text(head("zh") + body_zh(), encoding="utf-8")
    print("README.md:", (ROOT / "README.md").stat().st_size, "bytes")
    print("README.zh-CN.md:", (ROOT / "README.zh-CN.md").stat().st_size, "bytes")
    print("papers:", TOTAL, "categories:", len(CATS), "code links:", CODE_N)
    print("years:", counts_by_year())


if __name__ == "__main__":
    main()
