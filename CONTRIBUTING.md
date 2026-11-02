# Contributing

Corrections are as welcome as additions. The most useful contributions are: a paper that is missing, a venue or author list that is wrong, a claim in a summary that the paper does not support, or a code link that has moved.

## Add or fix a paper

1. Edit [`data/papers.json`](data/papers.json) — add an object to `papers` (or edit the existing one).
2. Regenerate both READMEs and the CSV:

   ```bash
   python scripts/build_readme.py
   python scripts/export_csv.py
   ```

3. Open a pull request. If you are only suggesting a paper, an issue with the arXiv link is enough; someone else can do the data entry.

## Entry schema

```json
{
  "id": "2502.05171",
  "date": "2025-02-07",
  "title": "Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach",
  "authors": "Jonas Geiping et al.",
  "venue": "NeurIPS 2025",
  "category": "Latent Reasoning",
  "tags": ["recurrent-depth", "latent-reasoning"],
  "summary": {
    "en": "One or two sentences on what the paper shows.",
    "zh": "一到两句话说明论文证明了什么。"
  },
  "paper": "https://arxiv.org/abs/2502.05171",
  "code": "https://github.com/seal-rg/recurrent-pretraining"
}
```

Rules:

- **`id`** is the arXiv identifier (without `arXiv:`) when one exists; otherwise a short slug such as `loopcoder-2026`.
- **`date`** is the first arXiv submission date, `YYYY-MM-DD`. It controls ordering and year grouping.
- **`authors`** is the first author plus `et al.` when there are more than three authors; otherwise the full list.
- **`venue`** is the published venue and year (`ICLR 2026`, `NeurIPS 2025`), or `arXiv <year>` if unpublished. Do not promote a preprint to a venue on the strength of a review score.
- **`category`** must be one of the twelve names in `data/papers.json`. Each paper appears once; use `tags` for cross-cutting themes.
- **`summary`** must exist in both languages and say what the paper demonstrates — ideally with the setting and the size of the effect — not what it is about. Keep the two languages equivalent.
- **`code`** and **`project`** should be official links. A third-party reimplementation can go in the PR description instead.
- Optional: `star: true` for essential reading (ask first; the list is curated), `deepDiveEn`/`deepDiveZh`/`zhPdf` for external deep dives, `foundation: true` for pre-2024 groundwork.

## Choosing a category

The first question is **what is repeated?** A paper that reuses a Transformer layer, block or stack through depth belongs to the core track. A method that computes in hidden states without block reuse belongs to *Broader Latent Reasoning*.

- New architecture, pretraining recipe or scaling law → **Architectures & Scaling**
- Theory, expressivity, length generalization, algorithm simulation → **Foundations & Theory**
- Inference-time depth in a language model (Huginn/Ouro style) → **Latent Reasoning**
- Routing, halting, early exit, elastic depth → **Adaptive Compute**
- Optimization, residual scaling, fixed points, training recipes → **Training, Stability & Analysis**
- Probing, causal or mechanistic analysis → **Interpretability**
- SFT, distillation, preference optimization, RL → **Post-Training & RL**
- HRM, TRM and descendants → **Tiny Recursive Reasoners**
- KV cache, quantization, serving, speculative decoding → **Efficiency & Systems**
- A modality or product domain → **Applications & Modalities**
- Jailbreaks, monitoring, steering, alignment → **Safety, Monitoring & Alignment**
- Continuous thoughts, implicit CoT, pause tokens → **Broader Latent Reasoning**

## Summary style

Write for a reader who has the abstract open in another tab. Prefer:

- the setting and scale (“on Sudoku-Extreme with a single shared block”),
- the mechanism in one clause (“a learned gate decides how much state to retain”),
- the result with its condition (“matches full-depth ViT-B with ~70% fewer stored parameters”).

Avoid “proposes a novel framework”, “achieves state-of-the-art” without the benchmark, and claims that only hold in the abstract's framing. If the paper reports a negative result, say so — those entries are among the most useful in the list.

## Review criteria

A pull request is merged when:

- the paper has a primary source (arXiv, OpenReview, PMLR, ACL Anthology, or the publisher);
- it is not already in the catalog (search by title and arXiv id);
- the category and tags are defensible under the rules above;
- both summaries are accurate and equivalent;
- the venue is correct and not inflated;
- links resolve, and code links are official.

## Corrections

Open an issue with the entry's title, the field that is wrong, and a source. For a disputed claim, quote the section, table or figure in the paper. If a paper has been superseded, say so and link the successor rather than deleting the entry.
