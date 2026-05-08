# LO3.1.1 + CG3.2.2 Independent Audit

**Reviewer:** Claude Code (Opus 4.7, 1M context)
**Date:** 4 May 2026
**Scope:** Independent audit of LO3.1.1 (M3 Acquire) + CG3.2.2 (M8 Deepen) — vertical pair on AI training pipeline. **No DB writes.** No Gemini calls.
**Sources:** UNESCO PDF Chapter 4 verbatim · M3 row 362 raw HTML · M8 row 447 raw HTML · platform_changes_log.md (Day 3 + Tier 3 entries) · M3 / M8 matrix entries.

**Transparency note:** Appendix A's chat-side hypothesis was visible in the same incoming brief. Verdict built bottom-up from UNESCO wording + actual content audits. Reconciliation section at the end documents agreement / divergence.

---

## Up-front finding (read this first)

**The two indicators have DIFFERENT closure status under strict UNESCO reading:**

- **LO3.1.1 (Acquire-level lifecycle):** ✅ STRONG via M3 AI_LIFECYCLE_PATCH apr2026 (Sprint 1-style sync). Defensible at Acquire level even though M3 covers 5 of UNESCO's 7 named lifecycle steps.
- **CG3.2.2 (Deepen-level research-based learning on LLM training/testing):** ⚠️ **PARTIAL** under strict reading. Neither M3 (Acquire-level conceptual stages, no peer-reviewed citations on LLM training) nor M8 (Studio SVGs visualise the Studio, not the LLM; m8_cross_ref_m3 routes to AI techniques NOT to training methodology) genuinely meets CG3.2.2's "research-based learning... including on how a selected AI system (such as a large language model) is trained and tested" wording.

This is the **A2 pattern repeated** for CG3.2.2 (Tier 1 lenient closure; substantive AI-empirical layer missing for the Deepen-level ask). LO3.1.1 is the A3 pattern (genuine distributed STRONG, sync issue).

**Recommended treatment: split, not single sync.**

---

## Dimension 1 — UNESCO definitions (verbatim)

### LO3.1.1 (lines 1124-1138 of unesco_framework.txt)

> "Demonstrate conceptual knowledge appropriate to their competencies and responsibilities on how AI systems are developed using data, algorithms and computing architecture; acquire relevant understanding and skills on data, algorithms and programming; and **exemplify key steps including problem-scoping, design, training, testing, deployment, feedback and iteration**."

**Sub-clauses:**
1. Conceptual knowledge on how AI systems are developed (data, algorithms, computing architecture)
2. Understanding/skills on data, algorithms, programming
3. **7 named lifecycle steps**: problem-scoping · design · training · testing · deployment · feedback · iteration

**Level:** Acquire (basic conceptual knowledge for teachers' competencies/responsibilities — NOT engineering depth)

### CG3.2.2 (lines 1442-1450)

> "**Scaffold deepened construction of conceptual knowledge** by facilitating teachers' **research-based learning**, including on how a **selected AI system (such as a large language model) is trained and tested** and what typical models, algorithms and datasets are used for the training."

**Sub-clauses:**
1. Scaffold deepened construction of conceptual knowledge
2. **Research-based learning** (not visualization, not experiential — RESEARCH-based)
3. How a selected AI system (e.g., LLM) is **trained AND tested**
4. Typical models, algorithms, datasets used in training

**Level:** Deepen (deepened construction beyond Acquire basics)

### LO3.2.2 (lines 1438-1442) — for vertical context

> "Visually represent how selected AI systems work, including how they are trained and tested, as well as the typical models, algorithms, and datasets used."

**Note:** LO3.2.2 specifies "visually represent" — concept maps + visualizations satisfy. CG3.2.2 specifies "research-based learning" — citation/discussion of peer-reviewed research is the natural fit.

**Tier 3 status (per CONTENT_VALIDATION_MATRIX.md):** LO3.2.2 was audit-corrected to STRONG (DISTRIBUTED M3+M8) on May 3, 2026. **CG3.2.2 was NOT audit-corrected** — it remains in M8's "Indicators with partial/no coverage" line.

---

## Dimension 2 — M3 native content audit (LO3.1.1 closure source)

M3 row 362 length: 39,280 chars. Parts 1–6.

### M3 AI_LIFECYCLE_PATCH apr2026 (lines 196–211, Day 3 patch)

**Title:** "How AI Models Are Built — A Teacher's Conceptual Map" (within Part 1)
**Word count:** ~530 words
**Structure:** 4 conceptual stages with teacher-question framing for each

**M3's 4 stages → UNESCO LO3.1.1's 7 named steps mapping:**

| UNESCO step | M3 coverage | Strength |
|---|---|---|
| problem-scoping | not named explicitly | ❌ |
| design | not named explicitly | ❌ |
| training | M3 Stage 1 (Data collection) + Stage 2 (Training) | ✅ |
| testing | not named as a distinct stage; implicit in M3 Stage 3 (Fine-tuning + human feedback) | 🟡 |
| deployment | M3 Stage 4 (Deployment and feedback) | ✅ |
| feedback | M3 Stage 4 explicitly | ✅ |
| iteration | M3 Stage 4 implicitly ("signal for the next iteration") | 🟡 |

**Net:** M3 covers 4/7 UNESCO steps explicitly + 2/7 implicitly + 2/7 not named.

**Defensibility note:** UNESCO LO3.1.1 says "**exemplify** key steps" — "exemplify" doesn't require all 7 named verbatim. M3's framing is teacher-appropriate Acquire-level ("you don't need to be an AI engineer"). The 4 stages capture the heart of the lifecycle. Defensible at Acquire level.

### Inline pipeline mentions in M3

| Term | Present? | Where |
|---|---|---|
| training data | ✅ | Stage 1, Stage 2 lifecycle patch |
| fine-tuning | ✅ | Stage 3 lifecycle patch |
| billions of parameters | ✅ | Stage 2 ("billions of internal parameters") |
| pre-training | ❌ (concept covered without name) | n/a |
| RLHF | ❌ | n/a |
| instruction tuning | ⚠️ (concept covered: "follow instructions, refuse harmful requests" — Stage 3) | Stage 3 |
| transformers | ❌ | n/a |
| neural networks | ❌ | n/a |

**Teacher-appropriate framing:** ✅ The patch explicitly frames itself for teachers ("You don't need to be an AI engineer to teach with AI"). UNESCO LO3.1.1 says "appropriate to their competencies and responsibilities" — teacher-appropriate framing is exactly what's asked.

### Part 1A vs Part 1B distinction (the brief's framing)

**The brief assumed M3 has separate Part 1A (4-step LLM diagram) and Part 1B (4-stage lifecycle SVG).** Verified in row 362: M3 has **Part 1 only** with 4 sub-sections (Token / Context Window / Temperature / LLMs vs Google) + the AI_LIFECYCLE_PATCH inserted between Temperature SVG and the "LLMs vs Google" subsection. There is NO separate Part 1B in M3. The brief's "Part 1A 4-step diagram + Part 1B 4-stage lifecycle SVG" is a conflation.

What actually exists:
- M3 Part 1 Context Window SVG (lines 81–101, 4-element visual but it's about context window, NOT lifecycle)
- M3 AI_LIFECYCLE_PATCH (lines 196–211) — 4 narrative stages with bold-labelled headers, NO SVG diagram

So M3 has a TEXT-based 4-stage lifecycle, NOT an SVG diagram of the lifecycle. The lifecycle is narrative + teacher-question framing, not visual.

For LO3.1.1 ("Demonstrate conceptual knowledge... exemplify key steps") this is OK — exemplification can be narrative.
For LO3.2.2 ("Visually represent how AI systems work") this is **less OK** — the lifecycle isn't visualized. The Tier 3 audit-correction relied on M8's Studio SVG cumulatively, not on M3 having a lifecycle SVG.

---

## Dimension 3 — M8 native content audit (CG3.2.2 closure source)

M8 row 447 length: 44,351 chars. Parts 1–6.

### M8 patches (lines 54–60 + 425–450)

| Patch | Lines | Content | Indicator targeted |
|---|---|---|---|
| `M8_CROSS_REF_M3_PATCH` (Tier 3) | 54–60 | "A note on AI techniques" — routes M8 readers to M3 Part 2 for symbolic/predictive/generative AI breakdown | CG3.2.1 (operation/comparison) |
| `M8_ETHICS_BY_DESIGN_PATCH` (Tier 3) | 425–450 | "Hands-on Ethics in Your Prompts" 3-check pattern | CG3.2.4 (ethics by design) |

**Neither patch addresses CG3.2.2 (LLM training pipeline).** The cross-reference to M3 routes to AI techniques comparison, NOT to training pipeline depth.

### M8 SVGs

| SVG | Lines | What it visualises |
|---|---|---|
| RPE Strategies 1–5 | 86–145 | The 5 instructional design strategies (Goals/Context/Format/Cognitive Level/Examples) |
| EduPrompt Studio Interface | 195–248 | The Studio's interface fields |
| Enhancement Flow | 255–315 | How a prompt is enhanced through the Studio |

**All 3 M8 SVGs visualise Studio + RPE — NOT the LLM training pipeline.** This is exactly what CONTENT_GAPS_LOG.md flagged: "M8 Studio SVGs visualise the Studio, not the LLM — defendable design choice for Deepen prompt-engineering module."

For LO3.2.2 ("visually represent how AI systems work") this defendability holds because Studio + Enhancement Flow are user-facing AI system visualizations, satisfying the visualization-of-AI-systems sub-clause cumulatively with M3's lifecycle text + Three Categories SVG.

For CG3.2.2 ("**research-based learning** on LLM training+testing") this defendability does NOT hold because:
- No SVG visualises LLM training methodology
- No inline content discusses peer-reviewed research on LLM training
- m8_cross_ref_m3 routes to AI techniques (not training research)

### M8 inline LLM training mentions

```
grep -niE 'pre.train|fine.tun|RLHF|instruction tun|training data|model parameter|weight|transformer|neural network|how.*trained|tested|train.*test|research.based|empirical|peer.review|systematic review|meta.analy'
```

Result: **0 mentions of any LLM training pipeline term in M8 main_content.** No "pre-training", "fine-tuning", "RLHF", "instruction tuning", "transformers", "training data", "model parameters", "weights", "neural networks", "research-based", "peer-reviewed", "systematic review", or "meta-analysis".

The grep DID surface "tested" — but only as part of "are tested" inside the M8 cross-ref patch describing what M3 Part 2 covers. **M8 has zero native content on LLM training/testing.**

### Research-based learning framing in M8

CG3.2.2 specifically asks for "research-based learning". M8's empirical references (per matrix bibliography) are:
- Dourvas, Kokkonis & Kontogiannis (2025) — RPE Framework (not LLM training)
- Mishra & Koehler (2006), Mishra et al. (2023) — TPACK (not LLM training)
- Celik (2023), Wiggins & McTighe (2005), Anderson & Krathwohl (2001), Lo (2023), Schön (1983), Zhou et al. (2026), Wenger (1998), Black & Wiliam (1998), Meyer/Rose/Gordon (2014), Polanyi (1966), Crosthwaite et al. (2025), Walter (2024), Sweller et al. (2019), Vygotsky (1978)

**None of these are about LLM training methodology.** They're about prompt engineering, instructional design, scaffolding, communities of practice. Excellent for M8's prompt-engineering scope but **not addressing CG3.2.2's specific "research-based learning on LLM training/testing" ask.**

---

## Dimension 4 — UNESCO mapping (per-sub-clause matrix)

### LO3.1.1 sub-clauses

| Sub-clause | M3 native | M8 native | Cumulative |
|---|---|---|---|
| 1. Conceptual knowledge on how AI systems are developed | ✅ STRONG (AI_LIFECYCLE_PATCH 4 stages + teacher-question framing) | partial (m8_cross_ref_m3 routes here) | ✅ **STRONG** |
| 2. Data, algorithms, programming | 🟡 MODERATE (training data + algorithms named; programming not addressed) | n/a | 🟡 **MODERATE** (programming intentionally omitted at Acquire level for K-12 teacher audience — defendable) |
| 3a. problem-scoping | ❌ not named | n/a | ❌ |
| 3b. design | ❌ not named | n/a | ❌ |
| 3c. training | ✅ Stage 1+2 explicit | n/a | ✅ |
| 3d. testing | 🟡 implicit in Stage 3 | n/a | 🟡 |
| 3e. deployment | ✅ Stage 4 explicit | n/a | ✅ |
| 3f. feedback | ✅ Stage 4 explicit | n/a | ✅ |
| 3g. iteration | 🟡 implicit in Stage 4 | n/a | 🟡 |

**Net:** 5/9 STRONG + 3/9 MODERATE + 1/9 ABSENT (3a problem-scoping, 3b design — both arguably engineering-level not Acquire-level).

### CG3.2.2 sub-clauses

| Sub-clause | M3 native | M8 native | Cumulative |
|---|---|---|---|
| 1. Scaffold deepened construction of conceptual knowledge | M3 is Acquire-level (not Deepen) | ✅ STRONG (RPE Strategies + Studio + Audit Template — Deepen-level scaffolding for prompt engineering) | ✅ STRONG **for prompt engineering**; MODERATE for LLM training specifically |
| 2. **Research-based learning** | ❌ no peer-reviewed citations on LLM training | ❌ no peer-reviewed citations on LLM training | ❌ **WEAK / not closed** |
| 3. How a selected AI system (LLM) is trained AND tested | 🟡 M3 covers training at Acquire level; testing not named | ❌ M8 not native; cross-ref routes to M3 Part 2 (AI techniques, not training methodology) | 🟡 Acquire-level only; Deepen-level training+testing not covered |
| 4. Typical models, algorithms, datasets in training | M3 mentions "billions of words from books, websites...", "billions of parameters", "carefully curated datasets", "human feedback" but no model architectures named | ❌ not in M8 | 🟡 partial via M3 conceptual stages |

**Net for CG3.2.2:** 1/4 STRONG + 2/4 MODERATE + 1/4 WEAK/not closed (sub-clause 2 — research-based learning is the genuinely missing piece).

---

## Dimension 5 — Sufficiency verdict (per indicator)

### LO3.1.1 — ✅ Verdict A (STRONG, audit-only sync sufficient)

M3 AI_LIFECYCLE_PATCH covers the heart of LO3.1.1's lifecycle ask at Acquire level appropriate to teacher audience. UNESCO wording "exemplify key steps" doesn't require all 7 verbatim — exemplification at conceptual level satisfies. The PHASE_A flag is stale residue (predates Day 3 patch being credited).

**Action:** Audit-only sync. Update CONTENT_VALIDATION_MATRIX.md M3 entry, PHASE_A_REMAINING_GAPS_POST_TIER3.md row 3.1, CONTENT_GAPS_LOG.md M3 Κενό #1.

### CG3.2.2 — ⚠️ Verdict C (STRONG-WITH-RESERVATION, small reinforcement worth doing)

The cumulative coverage closes 3/4 sub-clauses adequately at Deepen level (scaffolding deepened conceptual knowledge via M8 Studio + RPE; LLM training at Acquire level via M3; typical datasets/parameters via M3). **Sub-clause 2 (research-based learning) is genuinely thin** — neither M3 nor M8 cites peer-reviewed research on LLM training methodology.

This is the **same A2 pattern** as CG4.2.2 (Tier 1 lenient closure; substantive AI-empirical layer missing for the Deepen-level ask).

**Action:** Step 1 audit-only sync (matrix says LO3.2.2 STRONG; extend to CG3.2.2 with sub-clause-aware framing). Step 2 reinforcement patch in M8 — small (~50-100 word) inline citation block at end of Part 1 (after the m8_cross_ref_m3 patch) referencing 1-2 peer-reviewed papers on LLM training methodology. Candidate references for John to consider:

- **Mishra, Warr & Islam (2023)** "TPACK in the age of ChatGPT and Generative AI" (Journal of Digital Learning in Teacher Education) — already in M3+M8 bibliography, has empirical framing of GenAI properties (protean/opaque/unstable/generative/social) which is teacher-relevant context for "how LLMs work"
- **Ouyang et al. (2022)** "Training language models to follow instructions with human feedback" (NeurIPS, the InstructGPT paper) — primary peer-reviewed paper on RLHF, names the methodology UNESCO is asking about
- **Bender et al. (2021)** "On the Dangers of Stochastic Parrots" (FAccT 2021) — peer-reviewed critique of LLM training paradigm, complements M2's sustainability framing
- Other AI-empirical papers from M8's bibliography that touch on LLM training (Crosthwaite 2025, Walter 2024)

The reinforcement should be SMALL (M8 is dense already; 50-100 words is enough). Format: in-Part-1 citation footer similar to T1.4/T1.5/A2.

**This is NOT a closure-blocker for the broader Aspect 3 — it's the kind of reinforcement that hardens defendability at viva. If John prefers to defer (A3-style audit-only sync), that's also defensible — Tier 3 already accepted M3+M8 distributed coverage for LO3.2.2, and CG3.2.2 closure can ride on that with the caveat that "research-based learning" is interpreted broadly (RPE Framework + Studio + ethics-by-design ARE forms of research-based learning, even if not specifically about LLM training).**

---

## Dimension 6 — Pattern comparison with A2 / A3

| Indicator | Pattern | Outcome |
|---|---|---|
| CG2.1.3 / CG4.3.4 / CG5.3.4 (Sprint 1) | distributed STRONG, sync issue | Audit-only |
| CG4.2.2 (A2) | Tier 1 LENIENT, AI-empirical layer missing for Deepen-level | Reinforcement patch |
| CG1.3.2 (A3) | distributed STRONG, sync issue (PHASE_A predated Day 3+Tier 3) | Audit-only |
| **LO3.1.1 (this audit)** | **distributed STRONG (Sprint 1 / A3 pattern)** | **Audit-only sync** |
| **CG3.2.2 (this audit)** | **A2 pattern repeated** — Tier 1+Tier 3 closure satisfied LO3.2.2 (visualization) but NOT CG3.2.2 (research-based learning); the brief conflated them | **Audit-only sync + small reinforcement (Verdict C)** |

The brief itself partially flags this risk: "CG3.2.2 wording is more specific than LO3.1.1. It asks for 'research-based learning'... The 'research-based learning' phrasing might require AI-empirical citations (not just SVG diagrams), similar to A2's CG4.2.2 strict reading." My audit confirms exactly that.

The brief's alternative skepticism prompt also confirms: "M3 Part 1B is at Acquire level by definition. CG3.2.2 is at Deepen level. Distributing the closure across M3 (Acquire) + M8 (Studio visualisations only) might be lenient under strict reading — same risk as A2." My audit confirms this is the actual situation.

---

## Final recommendation

**Split treatment:**

1. **LO3.1.1: Audit-only sync (Sprint 1 / A3 pattern)** — ~30 min docs work. M3 AI_LIFECYCLE_PATCH covers it at Acquire level. PHASE_A flag is stale residue.

2. **CG3.2.2: Audit-only sync + small Step 2B reinforcement patch (A2 pattern)** — Step 1 ~30 min docs (interim PARTIAL→STRONG with "pending Step 2" marker, same as A2 process), Step 2 ~1-2h reinforcement (~50-100 word in-M8 citation block + atomic-chunk RAG ingest).

**Combined treatment if John prefers single sync (A3-style):**

- Treat CG3.2.2 closure as STRONG cumulative under broad reading: M3 lifecycle + M8 Studio + Tier 3 LO3.2.2 audit-correction = sufficient. Skip the reinforcement.
- Defensible — Tier 3 accepted distributed M3+M8 for LO3.2.2; the same logic extends to CG3.2.2 if "research-based learning" is read as "scaffolded conceptual learning grounded in research", which RPE Framework satisfies.
- Risk: a strict viva reviewer asks for the AI-empirical citation on LLM training specifically. Same risk A2 surfaced.

**My preference: split treatment** (audit-only for LO3.1.1, audit + reinforcement for CG3.2.2). This matches the A2 lesson: paper-grounded reinforcement makes the strict-reading closure more defensible than distributed-cumulative alone.

But this is a judgment call. John may reasonably choose the unified A3-style sync if dissertation-pacing favours speed over reinforcement-thickness.

Coverage trajectory impact:
- Split treatment: 149/170 → 151/170 (~88.8%) [LO3.1.1 +1 + CG3.2.2 +1 with reinforcement]
- Unified A3-style: 149/170 → 151/170 (~88.8%) [LO3.1.1 +1 + CG3.2.2 +1 audit-only]

Same +2 numerical impact either way; quality differs (strict-reading defendability).

---

## Reconciliation with Appendix A (chat-side hypothesis)

| Dimension | Chat-side prediction | My audit | Match? |
|---|---|---|---|
| LO3.1.1 verdict | A — STRONG distributed | A — STRONG distributed | ✅ same |
| CG3.2.2 verdict | A — STRONG distributed | **C — STRONG-WITH-RESERVATION** | ⚠️ **different** |
| LO3.1.1 action | Audit-only sync | Audit-only sync | ✅ same |
| CG3.2.2 action | Audit-only sync | **Audit-only sync + small reinforcement** | ⚠️ **different** |
| LO3.1.1 pattern | Same as A3 (sync) | Same as A3 (sync) | ✅ same |
| CG3.2.2 pattern | Same as A3 (sync) | **Same as A2 (substantive interpretation gap)** | ⚠️ **different** |

### Where my audit diverges from Appendix A

1. **LO3.2.2 vs CG3.2.2 conflation:** Appendix A treats them as the same. They're not. LO3.2.2 (visualization sub-component) was Tier 3 audit-corrected to STRONG and that's correct. **CG3.2.2 (broader research-based learning ask) was NOT audit-corrected** and remains in M8's "partial" line in the master matrix. The brief's table treats CG3.2.2 status by reading the LO3.2.2 line, which is a category error.

2. **"Research-based learning" sub-clause:** Appendix A's recommendation (audit-only) doesn't address sub-clause 2 of CG3.2.2 — research-based learning. Neither M3 nor M8 cites peer-reviewed research on LLM training methodology. This is the same gap A2 surfaced (CG4.2.2 needed Aravantinos+Viberg AI-empirical citations beyond Tier 1's foundational pedagogical theory).

3. **A2 lesson applies here:** If A2 pattern was correct for CG4.2.2, it's correct for CG3.2.2. CG3.2.2's "research-based learning" wording is even MORE explicit than CG4.2.2's "research reports" wording — a strict reviewer would expect at least one peer-reviewed citation on LLM training methodology in M8 (or expanded in M3).

### Action

**Same verdict on LO3.1.1; different verdict on CG3.2.2.** Per the audit brief's instruction: "Disagreement on any indicator? → STOP. Report the disagreement back to John in chat. Do NOT apply changes until John reconciles."

Reporting back to John for reconciliation. Two paths forward:

- **Path 1 (my recommendation):** Split treatment — LO3.1.1 audit-only Step 1, CG3.2.2 audit + small Step 2B reinforcement (A2 pattern). Effort: ~45 min docs + ~1-2h reinforcement.
- **Path 2 (chat-side):** Unified audit-only sync for both. Effort: ~45 min docs total. Risk: strict viva reviewer flags CG3.2.2 sub-clause 2 (research-based learning).

John picks. If Path 2, the audit-table sync is fine; defendability under strict reading depends on broad interpretation of "research-based learning" to include the RPE Framework + Studio scaffolding (which IS research-grounded if viewed as instructional design research, even if not LLM-training research).

---

## Hard guardrails respected

- ❌ No DB writes
- ❌ No RAG document changes
- ❌ No Gemini call
- ❌ No SQL outside read-only inspection
- ❌ No patch wording proposed (verdict + reinforcement direction only)
- ✅ Read M3 row 362 + M8 row 447 in full
- ✅ Per-sub-clause matrix grounded in actual content (line numbers cited)
- ✅ Appendix A read AFTER saving Dimensions 1–6
- ✅ Disagreement on CG3.2.2 flagged for John reconciliation
- ✅ Saved to file; reported back

---

*End of independent audit. Awaiting John on the LO3.1.1 (single sync OK) + CG3.2.2 (split treatment vs unified) decision.*
