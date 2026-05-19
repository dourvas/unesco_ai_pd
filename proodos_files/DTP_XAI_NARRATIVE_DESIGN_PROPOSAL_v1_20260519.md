# DTP XAI Narrative (D.3b) — Design Proposal v1

**Date:** 2026-05-19
**Status:** Draft for review. No code written. This document proposes the
XAIAgent — the explainability layer over the redefined DTP. To be reviewed and
signed off before implementation begins.
**Origin:** chat-side design session, 2026-05-19 (John Dourvas, PI).
**Roadmap relationship:** D.3b — DTP XAI narrative. Builds directly on D.3a
(DTP redefinition — `DTP_REDEFINITION_DESIGN_PROPOSAL_v1_20260518.md`, complete
and committed). Fills the §4.5 placeholder of
`PROODOS_Architecture_Chapter_DRAFT_v1.md`.
**Bibliographic base:** §11 of `proodos_files/Literature_Review_Synthesis_Note(1).md`.

---

## 1. Summary

D.3b adds an **XAIAgent**: a new agent that produces a personalised,
natural-language explanation of *why* a teacher's DTP signal looks the way it
does. It is the first member of a new **`ServiceAgent`** branch of the agent
hierarchy — agents that operate on the output of *other agents* rather than on
a teacher's reflection.

The DTP's current explainability surface is a static template panel ("How this
signal was generated") that describes the *method* in general terms, identically
for every teacher. It does not explain any individual teacher's specific signal.
The XAIAgent closes that gap: it reads the teacher's stored DTP composite and
generates an explanation grounded in exactly what the DTP computed.

The design is governed by two principles:

- **Explanation faithfulness** — the explanation must be tethered to the DTP's
  actual computation, never a plausible invention.
- **Domain-driven explanation** — the explanation speaks in pedagogical and
  UNESCO-competency terms, not in cosine-similarity numbers. This is the
  empirically supported choice (Feldman-Maggor et al., 2025).

---

## 2. Motivation — why we build it

### 2.1 The what / why gap

After D.3a the DTP produces a dual-signal output and the teacher sees the card —
narrative plus two theme panels. Beneath it sits the static panel "How this
signal was generated". That panel is **template content**: it states how the
feature works in general (model, the two-comparison logic, intent), identically
for every teacher and every signal. It answers "how does the DTP work"; it does
not answer "why did *my* signal come out this way".

A teacher therefore sees *what* the instrument concluded without seeing *why*
their particular result took that shape. The interpretive work is left entirely
to the teacher, unsupported.

### 2.2 The misreading risk

Unsupported interpretation is not neutral — it can go wrong in a specific,
predictable direction. The theme panels mark themes that appear *less* in the
current reflection with a downward arrow. A teacher reads a downward arrow on
"technical understanding" as a regression: "I have become worse." For a teacher
at M6 (Human-Centred Mindset, Deepen), a reflection that dwells less on
technical framing and more on pedagogical fit is in fact moving in exactly the
direction the UNESCO progression intends — yet the bare signal tells the
opposite story. Without an explanation, the teacher is left to misread a shift
of attention as a decline.

(The arrow encoding itself is also being addressed as a small D.3a presentation
follow-up — §9. The XAIAgent is the deeper layer: it explains; it is not a
substitute for framing the primary card correctly.)

### 2.3 Regulatory and literature grounding

- **EU AI Act, Article 13 (transparency).** A user affected by an AI system
  should be able to understand its output. A static method description is a
  partial discharge of that duty; a per-result explanation is a fuller one.
- **Feldman-Maggor et al. (2025).** With 41 in-service teachers, explainability
  raised trust and acceptance, and **domain-driven explanations outperformed
  data-driven ones** for understandability. This is the empirical basis for the
  domain-driven principle (§5.2).
- **Li et al. (2025).** Generative-AI natural-language explanations helped
  educators revise and calibrate their judgements — but are best used as
  *auxiliary* information, not as an authority. This grounds the stance that the
  XAIAgent explanation supports the teacher's interpretation rather than
  replacing it.
- **Altukhi & Pradhan (2025).** The field has no single agreed definition of
  XAI; this document therefore defines, in §4, exactly what "explanation" means
  in PROODOS.
- **Türkmen (2025).** Situates the work in the active-but-young XAI-in-education
  research stream.

---

## 3. The agent hierarchy — the `ServiceAgent` branch

The Phase E agent layer is a tiered hierarchy:

```
BaseAIAgent (abstract, ABCMeta)
├── ResearchInstrumentAgent (marker) ── RAG, RTM, DTP, Peer
└── ServiceAgent (marker)             ── XAIAgent          ← D.3b
```

A `ResearchInstrumentAgent` operates on a **teacher's reflection** — it reads
what the teacher wrote and produces a new artefact about their learning. A
`ServiceAgent` operates on **another agent's output** — it does not generate
primary research data; it serves, summarises, or explains the work of other
agents.

`ServiceAgent` is introduced in D.3b as a thin marker class, exactly as
`ResearchInstrumentAgent` is: no method body, earning its place through (a) a
docstring contract, (b) an `isinstance` type tag for cross-cutting code, and
(c) reserving the branch for future service agents (e.g. a cost-aggregator, or
a validator/refiner agent of the kind described by Guo et al., 2024). The
`XAIAgent` is its first concrete member.

(`research.py`'s docstring currently states that service agents "inherit
directly from `BaseAIAgent`". That line predates this decision and is corrected
when `ServiceAgent` lands.)

---

## 4. Explanation faithfulness — the core constraint

An explanation is **faithful** when it is grounded in what the system actually
computed. It is **unfaithful** when it is a fluent, plausible account that is
*not* tethered to the real computation.

The risk is specific to a generative XAIAgent. A language model asked to
"explain why this teacher's DTP signal looks like this" will willingly produce a
persuasive explanation whether or not it corresponds to what the DTP did. A
fluent-but-unfaithful explanation is **worse than no explanation**: the teacher
trusts it and acquires a confident but wrong understanding. Structurally, an
unfaithful explanation is an **over-inference** — a conclusion the underlying
data does not support (the failure mode Guo et al., 2024, name and measure).

The governing rule of D.3b:

> The XAIAgent explains the DTP's output using the DTP's data — exactly that
> data, nothing more and nothing less. It does not independently re-read or
> re-interpret the teacher's reflections, and it does not draw conclusions
> beyond the stored DTP composite.

Faithfulness is not only an ethical commitment; it is the constraint that
dictates the design decisions in §6 (the XAIAgent's input is the stored DTP
composite precisely so that it sees what the DTP saw).

---

## 5. What the XAIAgent produces

### 5.1 Input

The XAIAgent's input is the teacher's **stored DTP composite** — the
`dtp_dual_v1` JSON written by the DTPAgent to `UserModuleProgress.reflection_dtp`:
the available signals (vertical / temporal), the comparison modules, the cosine
similarity values, and the per-signal theme lists. This composite *is* the
faithful record of what the DTP computed; explaining from it, and only from it,
is what makes the explanation faithful.

### 5.2 Output — a domain-driven explanation

A natural-language explanation, addressed to the teacher, that:

- is **domain-driven** — it speaks in terms of UNESCO competency aspects and
  pedagogical movement, not in cosine-similarity numbers or embedding mechanics
  (Feldman-Maggor et al., 2025);
- **reframes shift as attention-movement, not regression** — it makes explicit
  that a theme appearing less is a movement of reflective focus, consistent with
  the continuity-is-not-quality boundary established in §4.4 of the D.3a design
  proposal;
- is **bounded** — it is an explanation, not an essay. Description is the DTP's
  job; the XAIAgent adds the "why", concisely. A working budget is set during
  implementation against real samples (cf. the D.3a §7.2 narrative-length
  discussion: length is not the lever for clarity — framing is).

### 5.3 What the explanation must not do

- It must not invent a cause the composite does not support.
- It must not contradict or "correct" the DTP signal.
- It must not evaluate the quality of the teacher's development (continuity is
  not quality).
- It must not introduce data beyond the composite.

---

## 6. Design decisions (signed off, 2026-05-19)

### 6.1 When it runs — automatically, after the DTP
The XAIAgent runs automatically as a step *after* the DTPAgent returns — not
gated on a teacher request. Rationale: a complete research dataset (every DTP
signal has a stored explanation, analysable in the dissertation) and an
explanation that is ready the moment the teacher looks. Cost is not a factor
(~€0.0001 per call, ~14 calls per teacher ≈ €0.0014, negligible against the
€1/user budget). It runs as a distinct step so the DTP card itself can render
without waiting on the explanation (§7).

### 6.2 Entry point — `generate()`
The explanation is a persisted AI artefact shown to the teacher, not an
ephemeral proposal awaiting ratification (the `extract()` stance, used by RTM).
The XAIAgent therefore uses `generate()` — the "AI commits, human disputes"
contract of `BaseAIAgent`.

### 6.3 Provenance — its own row
The explanation is AI-generated content; under EU AI Act Article 13 and the
platform's provenance discipline, every AI artefact carries an
`AIArtefactProvenance` row. The XAIAgent writes its own, with a new
`artefact_kind='xai_narrative'`, sharing `artefact_pk` with the
`dtp_narrative` row it explains. `generate()` writes provenance by contract, so
this follows from §6.2.

### 6.4 Storage — a new field on `UserModuleProgress`
The explanation is stored in a new `TextField` on `UserModuleProgress`
(working name `reflection_dtp_xai`), parallel to the existing `reflection_dtp`,
`reflection_rag_feedback`, and `reflection_peer_synthesis` fields. Rejected
alternatives: folding it into the `reflection_dtp` JSON (conflates two agents'
artefacts); a dedicated `xai_narratives` table (over-built while the XAIAgent
explains only the DTP — revisit if it becomes cross-agent).

### 6.5 Prompt strategy — register control by worked example
*(settled during live verification, 2026-05-19)*

The XAIAgent's non-evaluation is enforced not by a list of forbidden words but
by a single embedded **worked example** (few-shot). Two findings during live
verification drove this:

- **Negative rules prime the banned phrase.** Iterative tightening first added
  explicit prohibitions ("do not say *valuable*, *natural evolution*, …").
  Live output still surfaced the explicitly banned phrase *natural evolution* —
  naming a phrase inside a prohibition can itself make the model more likely to
  produce it. Accumulating bans is therefore an unreliable lever for register.
- **A model answer fixes the register by demonstration.** The prompt embeds one
  `<reasoning>`/`<explanation>` pair on a *different* competency area and
  modules (Ethics of AI, M4/M8/M9), so the model learns the tone — descriptive
  shift-of-attention language, the symmetric non-evaluation sentence, no
  invented cause — without copying the content. The rule set is reduced to
  three essentials (domain terms; the non-evaluation principle; no concept or
  cause beyond the named themes); the worked example carries the rest.

Gemini 2.5 thinking is **disabled** for this call (`thinking_budget=0`). The
prompt already carries its own `<reasoning>` chain-of-thought scaffold; the
model's hidden thinking would duplicate it and, because thinking tokens count
against the output budget, truncate the visible answer before the
`<explanation>` block was reached. As a defence in depth, the parser degrades
to the canned fallback when a `<reasoning>` tag is present without an
`<explanation>`, so a truncated scaffold is never surfaced to the teacher.

---

## 7. Mechanism and architectural placement

The change is concentrated in:

1. **`apps/agents/service.py` (new)** — the `ServiceAgent` marker class.
2. **`apps/agents/xai.py` (new)** — `XAIAgent(ServiceAgent)`,
   `artefact_kind='xai_narrative'`, with `_do_generate` building a structured,
   domain-driven prompt from the DTP composite and one Gemini call, plus a
   frozen Layer-1 prompt fixture under `apps/agents/tests/prompt_fixtures/`.
3. **`apps/modules/views.py`** — a new async endpoint (working name
   `extract-dtp-xai/`) that the frontend calls immediately after it receives
   the DTP response. The endpoint loads the just-stored composite and invokes
   `XAIAgent().generate(save_target=progress, save_field='reflection_dtp_xai',
   …)`.
4. **`UserModuleProgress`** — a new `reflection_dtp_xai` `TextField`; one
   migration (applied with the backup + dry-run discipline).
5. **`AIArtefactProvenance.ARTEFACT_KIND_CHOICES`** — gains `xai_narrative`.
6. **`tab5_reflection.html`** — renders the explanation within the DTP card
   (presentation — collapsed vs visible — is an open point, §9).
7. **`apps/agents/tests/`** — agent tests for the XAIAgent and a prompt fixture.

`XAIAgent` uses `generate()`: it persists the explanation to
`reflection_dtp_xai` and writes the `xai_narrative` provenance row in one
atomic block, exactly as the other `generate()` agents do (CP-9).

---

## 8. Relationship to D.3a

D.3b builds on the redefined dual-signal DTP. The faithfulness rule (§4) ties
the XAIAgent's input directly to D.3a's `dtp_dual_v1` composite.

The D.3a **themes-panel presentation follow-up** — replacing the evaluative
↑/↓/warning encoding with neutral attention-shift language — should land before
or alongside D.3b. The XAIAgent must explain an *already correctly framed*
card; an explanation is not a band-aid over a primary surface that itself
implies regression.

---

## 9. Open points

**Resolved during implementation / live verification (2026-05-19):**

- **Presentation — collapsed or visible.** Settled: the explanation renders
  *expanded* by default, as a "💡 Why this signal looks this way" block within
  the DTP card (both the in-progress and completed states). The static
  "🔍 How this signal was generated" method-disclosure panel sits below it —
  the explanation complements the method disclosure, it does not replace it.
- **D.3a themes-panel reframe** — done. The evaluative ↑/↓/warning encoding on
  the DTP theme groups was replaced with neutral attention-shift language
  ("Came into focus / Moved to the background / Held steady").
- **Prompt sample-review.** Done. The prompt was reviewed against real
  generated samples on M6; this drove the §6.5 prompt strategy (worked example,
  thinking disabled). The fixture is frozen at the reviewed prompt.
- **Explanation length budget.** Settled empirically — generated explanations
  run to roughly one short paragraph (~150 words); no hard cap is imposed,
  `max_output_tokens` is 3000 with thinking disabled.

**Still open / deferred:**

- **Dispute / HITL surface for the explanation.** The `generate()` stance is
  "AI commits, human disputes". Whether the explanation gets its own dispute
  surface (as RAG / RTM / DTP do) is deferred — decide after pilot feedback.

---

## 10. Dissertation coupling

- D.3b fills the **§4.5 placeholder** of `PROODOS_Architecture_Chapter_DRAFT_v1.md`
  (the XAI Service Agent). The §3 `ServiceAgent` distinction and the §4
  faithfulness argument are the substance of that section, including the
  explanation-of-explanation provenance question (§6.3 answers it: yes).
- §11 of `Literature_Review_Synthesis_Note(1).md` is the bibliographic base.
- The `PROODOS_Tab5_XAI_HITL_Architecture.md` DTP panel section is updated when
  the explanation is added to the card.

---

## 11. Worked example — M6

The live D.3a verification produced this DTP composite for a teacher at M6
(Aspect 1, Human-Centred Mindset, Deepen):

- **Vertical signal** — vs M1 (Acquire): similarity 0.8832; increased themes
  *pedagogical fit, auditing rigor, contextual evaluation*; decreased themes
  *LLM mechanics, technical focus, general reliability*; stable themes
  *human judgment, critical thinking*.
- **Temporal signal** — vs M5: similarity 0.8717; increased themes
  *pedagogical fit, tool auditing, impact awareness*; decreased themes
  *general reliability, mind reading, sole accuracy*; stable themes
  *AI context*.

The XAIAgent, reading only this composite, produced — on live verification at
M6, with the §6.5 prompt — this explanation:

> "Your reflective writing has changed where it places its attention. Comparing
> your earlier work in the same competency area with your current module, your
> reflection now gives more emphasis to pedagogical fit, the impact on
> learning, and rigorous auditing. Themes such as LLM mechanics and the
> fundamental nature of AI appear less often. Teacher oversight and tool
> evaluation remain a steady presence. Comparing your current module with the
> one immediately before it, pedagogical fit, tool auditing, and deliberate
> evaluation are again in focus. Themes like the assumption of mind-reading,
> implicit trust in tools, and general reliability have moved to the
> background. A theme appearing less is a change in where your reflection is
> pointing — not a sign that you understand it less well, and equally not a
> sign of progress. It simply records which ideas your writing engaged with
> most directly in each module."

The explanation names the competency movement, frames every decreased theme as
attention-movement, closes with the symmetric non-evaluation sentence, and
draws nothing the composite does not contain. (The theme labels above differ
slightly from the composite stated earlier in §11 because theme extraction is
itself an LLM step and non-deterministic across runs; the live XAI
verification ran on a fresh DTP composite.)

---

## 12. Decisions log

**Confirmed (chat session 2026-05-19):**

- D.3b adds an `XAIAgent` — the first `ServiceAgent` — explaining the DTP.
- Governing principles: explanation faithfulness; domain-driven explanation.
- §6.1 — the XAIAgent runs automatically, as a step after the DTP.
- §6.2 — entry point `generate()`.
- §6.3 — its own provenance row, `artefact_kind='xai_narrative'`.
- §6.4 — stored in a new `UserModuleProgress.reflection_dtp_xai` field.
- §6.5 — register controlled by an embedded worked example, not a ban list;
  Gemini thinking disabled for the call.

**Settled during live verification (§9):**

- Presentation — explanation expanded by default; method-disclosure panel kept.
- D.3a themes-panel reframe — done (neutral attention-shift language).
- Prompt sample-review — done; drove the §6.5 strategy; fixture frozen.
- Explanation length — empirically ~one short paragraph; no hard cap.

**Open / deferred:**

- §9 — dispute / HITL surface for the explanation (decide after pilot feedback).
