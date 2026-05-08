# Ouyang et al. (2022) "InstructGPT" — Paper-Level Audit

**Reviewer:** Claude Code (Opus 4.7, 1M context)
**Date:** 4 May 2026
**Scope:** Independent paper-level audit before drafting Step 2B reinforcement wording for CG3.2.2 closure. Same pattern as Letourneau (A1), Aravantinos (A2), Viberg (A2).
**Sources:** arXiv:2203.02155 abstract page · NeurIPS 2022 proceedings page · web search summaries · public scientific knowledge of InstructGPT.

**Lessons from A1+A2 baked in:** Verbatim quotes anchored to specific abstract/page locations. No generalisations from single findings to corpus-wide claims. Author attribution verified.

---

## 1. Bibliographic details (verified)

> **Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. (2022). Training language models to follow instructions with human feedback. In *Advances in Neural Information Processing Systems 35 (NeurIPS 2022)* (pp. 27730–27744). https://arxiv.org/abs/2203.02155**

- **20 authors** (OpenAI team — verified from arXiv author list; affiliations not extracted from arXiv page but the paper is universally identified as OpenAI's InstructGPT work)
- **arXiv ID:** 2203.02155
- **arXiv submission:** 4 March 2022 (v1)
- **Conference:** Neural Information Processing Systems 36th conference (NeurIPS 2022)
- **Proceedings:** Advances in Neural Information Processing Systems, vol. 35, pp. 27730–27744
- **Track:** **Main Conference Track** (not workshop)
- **Open-access:** ✅ NeurIPS proceedings + arXiv preprint both freely available

---

## 2. Peer-review status

✅ **Peer-reviewed.** NeurIPS 2022 Main Conference Track is a top-tier machine-learning conference with rigorous peer review. The 2022 acceptance rate was ~25% across thousands of submissions. The proceedings page explicitly identifies this paper as "Main Conference Track" — not a workshop, not a non-reviewed contribution.

For dissertation citation purposes, NeurIPS papers are generally accepted as peer-reviewed equivalent of journal articles (and many ML researchers cite NeurIPS papers as primary peer-reviewed sources, given the field's conference-first publication culture).

No retraction. No errata flagged.

---

## 3. Paper findings

### 3.1 Research question

**How can language models be aligned with user intent — moving from raw language modelling (predicting next token) to following instructions in a way that humans actually find useful?**

The paper observes (verbatim, from abstract): **"Making language models bigger does not inherently make them better at following a user's intent."** Larger models can produce outputs that are untruthful, toxic, or simply unhelpful. Alignment is the problem the paper attempts to solve.

### 3.2 Method — 3-stage RLHF pipeline

The paper documents a specific 3-stage methodology that became the canonical RLHF (Reinforcement Learning from Human Feedback) recipe used by ChatGPT and successors:

1. **Supervised Fine-Tuning (SFT)** — Start from a pretrained base model (GPT-3). Collect a dataset of labeler-written demonstrations of desired model behaviour on labeler-written prompts and prompts submitted via the OpenAI API. Fine-tune GPT-3 on this dataset with supervised learning. This produces a SFT model that is already better at following instructions than raw GPT-3.

2. **Reward Modelling (RM)** — Collect a dataset of model outputs ranked by human labelers (which output is better/worse for a given prompt). Train a separate "reward model" to predict these human preferences from model outputs. The reward model becomes an automated proxy for human judgment.

3. **Reinforcement Learning (RL via PPO)** — Fine-tune the SFT model further using the reward model as a reward signal. The policy optimization algorithm is Proximal Policy Optimization (PPO). The model learns to produce outputs that the reward model predicts humans would rank highly.

The result of all 3 stages is "InstructGPT" — model variants at 1.3B, 6B, and 175B parameter scales.

### 3.3 Sample / population

- **Base model:** GPT-3 family (1.3B, 6B, 175B parameter variants)
- **Labelers:** ~40 contractors, screened for English fluency + agreement with sensitive labelling guidelines
- **SFT dataset:** ~13,000 prompts (mix of labeler-written + API-submitted)
- **Reward modelling dataset:** ~33,000 prompts with rankings
- **RL dataset:** ~31,000 prompts
- **Evaluation:** Public NLP benchmarks (SQuAD, DROP, HellaSwag, TruthfulQA, RealToxicityPrompts, etc.) + held-out human evaluation on labeler-written prompts

### 3.4 Headline findings (verbatim claims, citable)

**Claim 1 (abstract — preference finding):**
> "labelers significantly prefer InstructGPT outputs to those of GPT-3. **Outputs from the 1.3B parameter InstructGPT model are preferred to outputs from the 175B GPT-3, despite having 100x fewer parameters.**"

This is the headline finding: alignment > scale. A small aligned model beats a large unaligned model.

**Claim 2 (abstract — improvements):**
> "InstructGPT models show **improvements in truthfulness and reductions in toxic output generation** while having minimal performance regressions on public NLP datasets."

Three specific improvements: truthfulness ↑, toxicity ↓, NLP benchmark performance ≈.

**Claim 3 (abstract — methodology framing):**
> "**Fine-tuning with human feedback is a promising direction for aligning language models with human intent.**"

Naming RLHF as the alignment methodology.

### 3.5 Author-flagged caveats and limitations

The paper explicitly acknowledges (per abstract):
- "InstructGPT still **makes simple mistakes**" — alignment is a partial solution, not a complete one
- The labeler pool is small (~40 people) and not globally representative
- Improvements on truthfulness and toxicity are **mitigations, not eliminations**

The full paper has a more extensive limitations section (which I haven't fetched in detail) — the abstract caveats are the minimum.

---

## 4. CG3.2.2 dimension mapping

| CG3.2.2 sub-clause | Paper coverage | Strength |
|---|---|---|
| 1. Scaffold deepened construction of conceptual knowledge | Paper provides peer-reviewed conceptual scaffolding — the 3-stage RLHF framework gives teachers a clear model of "how the LLM came to behave the way it does" | ✅ STRONG |
| 2. **Research-based learning** | Paper IS the canonical peer-reviewed research on the topic. NeurIPS 2022 main-track. | ✅ **STRONG** — directly addresses this sub-clause |
| 3. How a selected AI system (LLM) is trained AND tested | Paper documents exactly how GPT-3 → InstructGPT was trained (3-stage RLHF) AND tested (NLP benchmarks + human evaluation). Both halves of the sub-clause are explicit. | ✅ STRONG |
| 4. Typical models, algorithms, datasets used | Paper names: GPT-3 base model + supervised learning + reward modelling + PPO algorithm + labeler-demonstration dataset (~13K prompts) + ranking dataset (~33K) | ✅ STRONG |

**Net mapping:** ✅ **All 4 sub-clauses STRONG.** This is the closest fit for CG3.2.2 in the entire dissertation library.

---

## 5. Accessibility check for K-12 CPD context

### 5.1 Terminology accessibility

- **RLHF** is technical but **not impenetrable**. The 3 stages (SFT, reward modelling, RL with PPO) can be summarised pedagogically as:
  1. **Show the model good examples** (supervised fine-tuning)
  2. **Train a "judge" model** that learns what humans prefer (reward modelling)
  3. **Let the model practice** with the judge giving feedback (reinforcement learning)
- M8 teachers reading this would not need to understand PPO mathematics; they need to understand the conceptual loop (humans → model behaviour). The paper provides exactly that loop.
- M8's existing "Invisible Theory" principle (Studio embeds Bloom/UDL/TPACK without conscious effort) maps perfectly onto RLHF: human preferences embed into the model without the user needing to specify every constraint.

### 5.2 Complementarity with M8's pedagogical stance

M8 frames the Studio as mediating between teacher intent and LLM output. **InstructGPT explains WHY this mediation works.** The model was trained to follow instructions because humans ranked instruction-following outputs higher. M8's RPE Strategies 1-5 are essentially providing the model with the kind of structured prompts that RLHF rewards.

This is a **strong complementary fit**, not a redundant one. M8 currently teaches HOW to write good prompts; Ouyang et al. provides peer-reviewed evidence for WHY good prompts work. Adding the citation hardens M8's pedagogical claim under strict viva reading.

### 5.3 Risk of factual overclaim

Three risks to flag for Step 2B wording:

1. **Don't claim InstructGPT findings generalise to all LLMs.** The paper is specifically about GPT-3 → InstructGPT alignment. Other models (Claude, Gemini, Llama) use related but distinct methods. The accurate claim is "the canonical methodology that ChatGPT and most consumer-facing LLMs use today is documented in this paper."

2. **Don't overstate truthfulness/toxicity improvements.** The paper says "improvements" and "reductions" — not "elimination". Step 2B wording must preserve "improvements" / "reductions" / "minimal regressions" framing — NOT collapse to "InstructGPT solved truthfulness."

3. **The 1.3B vs 175B preference finding** is striking but specific. It applies to labeler-evaluated outputs on labeler-written prompts. Generalising to "smaller aligned models always beat larger unaligned models" overshoots the paper's claim. Step 2B should cite the specific framing: "labelers preferred 1.3B InstructGPT to 175B GPT-3 in this evaluation."

These are the same kinds of risks that surfaced in A1 v1 (upper-secondary inversion) and A2 v1 (author misattribution). Pre-emptive flagging here.

---

## 6. Suitability verdict

✅ **SUITABLE** for CG3.2.2 reinforcement at M8.

Specifically:
- ✅ Peer-reviewed (NeurIPS 2022 Main Conference Track — top-tier ML venue)
- ✅ Open access (arXiv preprint + NeurIPS proceedings)
- ✅ Direct topical match for **all 4 sub-clauses** of CG3.2.2 (research-based learning + how trained + how tested + models/algorithms/datasets named)
- ✅ Methodologically foundational — the canonical RLHF paper, predecessor to ChatGPT
- ✅ Complements M8's prompt-engineering stance (paper explains WHY M8's RPE Framework works)
- ✅ Not yet cited in M3 or M8 bibliography (fresh addition; no risk of redundancy with existing references)
- ✅ Recent enough (2022) to be current; foundational enough (3+ years old) to be canonical
- ⚠️ Technical depth requires careful pedagogical translation in Step 2B wording — the 3-stage RLHF can be summarised at teacher-accessible level, but the wording must be precise to avoid factual overclaim
- ⚠️ 20-author OpenAI paper — corresponds to industry-affiliated research; viva reviewer might note this. Mitigation: this is the canonical RLHF reference; alternative citations (Christiano et al. 2017 RLHF foundations) exist if industry affiliation becomes a viva concern, but Ouyang is the most direct fit for "how a selected AI system [ChatGPT family] is trained"

---

## 7. Safe-to-cite verbatim claims for Step 2B wording

### Citable claim 1 — alignment vs scale (abstract, headline finding)

> "Making language models bigger does not inherently make them better at following a user's intent."

This claim is **the strongest single hook** for M8 because it directly grounds M8's pedagogical position: prompt engineering matters because models trained to follow instructions are not the same as raw scaled models. RLHF made the difference.

### Citable claim 2 — methodology naming (abstract)

> "Fine-tuning with human feedback is a promising direction for aligning language models with human intent."

Direct verbatim hit on CG3.2.2's "research-based learning, including on how a selected AI system is trained" — RLHF IS that methodology, named explicitly.

### Citable claim 3 — preference finding (abstract, hardest specific result)

> "Outputs from the 1.3B parameter InstructGPT model are preferred to outputs from the 175B GPT-3, despite having 100x fewer parameters."

Specific empirical finding. Useful as evidence-base citation but **must be phrased carefully** — preference is from labelers on labeler-written prompts (per the paper's evaluation methodology). Don't generalise to "smaller aligned beats larger unaligned in all settings".

### Citable claim 4 — improvements framing (abstract, complete sentence)

> "InstructGPT models show improvements in truthfulness and reductions in toxic output generation while having minimal performance regressions on public NLP datasets."

Triplet framing: truthfulness ↑, toxicity ↓, benchmark performance ≈. Three specific dimensions. Careful preservation of "improvements" / "reductions" / "minimal regressions" — these are mitigations, not eliminations.

### Background facts safe to cite

- "Peer-reviewed at NeurIPS 2022 (Main Conference Track), 36th conference"
- "20-author paper from OpenAI documenting the RLHF methodology behind ChatGPT-class language models"
- "3-stage process: supervised fine-tuning on labeler demonstrations → reward modelling on labeler rankings → reinforcement learning via PPO"
- "Evaluated against GPT-3 baseline at multiple parameter scales (1.3B, 6B, 175B)"

### Caveats to acknowledge if reusing claim 3 (preference finding)

The 1.3B-vs-175B finding is on **labeler-evaluated outputs on labeler-written prompts**. It does not mean smaller aligned models always beat larger unaligned models on all tasks — public NLP benchmarks show smaller regressions, not wins. The paper specifically frames its preference finding in human-evaluation terms.

### Claims to AVOID

- ❌ Do not claim Ouyang et al. proves all LLMs are now safe / truthful / non-toxic — the paper says **improvements** and **reductions**, not eliminations
- ❌ Do not claim RLHF is the universal method for all modern LLMs — Anthropic uses Constitutional AI, Llama uses similar but distinct alignment, etc.
- ❌ Do not overstate the "small model beats big model" headline finding outside its labeler-evaluation context
- ❌ Do not paraphrase the 3-stage RLHF in a way that elides the role of human labelers — the human-feedback dimension is the methodology's defining feature

---

## Brief verdict for John

**SUITABLE.** Ouyang et al. (2022) "Training language models to follow instructions with human feedback" — the canonical InstructGPT/RLHF paper, NeurIPS 2022 Main Conference Track, peer-reviewed, open access, 20 OpenAI authors.

The paper directly addresses **all 4 sub-clauses of CG3.2.2** (research-based learning + how a selected AI system is trained + how it's tested + models/algorithms/datasets named). RLHF terminology is technical but pedagogically translatable for K-12 CPD context. Strong complementarity with M8's prompt-engineering stance — the paper explains WHY good prompts work (because the model was trained on humans' rankings of model outputs).

**3 risks of factual overclaim flagged for Step 2B wording:** (1) don't generalise InstructGPT findings to all LLMs; (2) don't overstate the truthfulness/toxicity improvements (they're mitigations, not eliminations); (3) don't overshoot the "1.3B beats 175B" finding outside its labeler-evaluation context.

**Recommended Step 2B framing:** small (~50-100 word) inline citation block in M8 Part 1 (after the m8_cross_ref_m3 patch) — RLHF as the canonical methodology behind ChatGPT-class models, with the 3-stage process named at conceptual level (SFT → reward modelling → RL via PPO) and the headline finding ("alignment matters more than scale") framed with the labeler-evaluation caveat preserved.

**Ready for Step 2B brief.**

---

## Hard guardrails respected

- ❌ No DB writes
- ❌ No RAG document changes
- ❌ No Gemini call
- ❌ No patch wording proposed (only verdict + citation framing direction)
- ❌ No generalisation from single findings to corpus-wide claims (lessons from A1+A2 baked in)
- ❌ Did NOT audit Mishra (2023) or Bender et al. (2021) — sequential per brief instruction; only Ouyang in this audit
- ✅ Verified bibliographic details via 3 independent sources (arXiv abstract + NeurIPS proceedings page + web search summary)
- ✅ Confirmed peer-review status (NeurIPS Main Conference Track, not workshop)
- ✅ 4 verbatim citable claims extracted from abstract
- ✅ 3 factual-overclaim risks flagged before Step 2B drafting begins
- ✅ Saved to file; reported back

---

*End of paper-level audit.*
