# PROODOS Epilogue (Phase G) — Design Proposal v2

**Date:** 2026-05-21
**Status:** PI-approved 2026-05-21; implementation in progress. Supersedes
`PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v1_20260521.md`. Incorporates the full
review of v1 (John Dourvas, PI, 2026-05-21): items B.1-B.5, C.1-C.5, D.1-D.4,
and the five supplementary points.

**Implementation correction (2026-05-21, during G.0):** the `epilogue_portrait`
artefact kind already exists in `AIArtefactProvenance.ARTEFACT_KIND_CHOICES`
(added forward-compat in C.3), so the planned `compliance` migration is
unnecessary. G.0 is a single migration on `epilogue_completions`. §8.5 / §9 /
§16 / §17 / §19 corrected accordingly.

**Implementation correction (2026-05-23, during G.3):** three clarifications
landed during G.3 design — the storage of transient portrait proposals and the
regeneration counter (no new schema field; reuse `dialogue_turns`), the
skip-dialogue bypass of the Portrait (so the test sweep cannot regress it),
and the exact `xhtml2pdf` shape of the Article 50(2) machine-readable marker
(JSON-LD block inside the rendered HTML **plus** a PDF document-metadata
callback). Captured in full in §22; §8 / §8.4 / §8.5 / §9 / §10 are read in
light of §22. No proposal direction changes.

**Implementation correction (2026-05-23, before G.6a):** the chatbot has been
given a teacher-facing persona ("Aletheia") in the G.6 design proposal. To
keep the persona consistent at the actual *model* level (rather than only at
the template level), four lines are added to `EpilogueDialogueAgent.
_SYSTEM_PROMPT` — no first-person voice, no self-naming, no in-dialogue
references to being an AI. Captured in §23. The agent-contract surface of v2
§7 is otherwise unchanged; no schema change, no provenance change, no view
change. Lands as a stand-alone commit *before* G.6a so the G.6 design changes
inherit a prompt that already enforces the persona.
**Origin:** Phase G kickoff design session + v1 review, 2026-05-21.
**Roadmap relationship:** Implements `PROODOS_UNIFIED_ROADMAP.md` §3 Phase G
(G.1 / G.2 / G.3) and resolves TD-011. Builds on the C.2.5 Epilogue placeholder.
**Supersedes:** v1 of this proposal, and the open questions Q1-Q6 in
`EPILOGUE_C25_IMPLEMENTATION_NOTES_20260511.md` §13.

---

## 0. Changelog v1 -> v2

| Review item | Change in v2 |
|---|---|
| B.1 | Stage 2 reframed from "contradiction/tension surfacing" to **juxtaposition surfacing** — the agent presents the teacher's own data points neutrally, the teacher names them. Removes the back-door evaluative stance that would have violated D.3a §4.4. |
| B.2 | `OneToOneField` kept (DB-level one-shot invariant); replay logged as **TD-022** with an explicit mechanical migration path. |
| B.3 | Stage 0 visual designed in **HTML/CSS, no SVG** — one render path for screen and PDF. The v1 §8.3 "technical risk" is eliminated. |
| B.4 | Consent for the dialogue corpus resolved — **option (α)**: covered by `research_participation` via an explicit text amendment folded into C.5. §11. |
| B.5 | M15 RAG re-ingest is a **pre-pilot** operation; sequencing made explicit + TD-023. §12. |
| C.1 | New §6.3 — dialogue prompt structure and per-turn token budget. |
| C.2 | §14 — real cost calculation with verified Gemini 2.5 Flash pricing. |
| C.3 | `stage0_snapshot` stores a **JSON semantic payload only**, never rendered HTML. |
| C.4 | 3-stage structure grounded in **Korthagen ALACT** (primary), **Mezirow**, **Schön** (via the project's own RPE paper). Brookfield considered and set aside. §15. |
| C.5 | Stage 2 skip given a **strict quantitative threshold**. §6.4. |
| D.1 | Learning Portrait HITL contract added (§8.4); `EpiloguePortraitAgent` moved from `generate()` to `extract()`. |
| D.2 | Article 50(2) machine-readable AI markers for the Portrait made explicit. §8.5. |
| D.3 | New §10.1 — failure modes and resume semantics. |
| D.4 | New §13 — research variables, with an explicit crosswalk to roadmap §H.5. |

---

## 1. Summary

The PROODOS Epilogue is a post-completion synthesis feature between Module 15
and the AILST T2 assessment. It is methodologically distinct from the 15
UNESCO-aligned modules — it adds synthesis and dialogue, not content — and is
not assessed.

C.2.5 delivered a one-page placeholder that captured the lifecycle and the
`M15 -> Epilogue -> T2` routing chain. Phase G builds the full four-stage
feature on top of it:

- **Stage 0 — Personal Evolution Dashboard.** A silent, input-free view of the
  teacher's own data: a descriptive DTP view (theme-evolution map + narrative
  timeline) and the RTM tension trajectories.
- **Stages 1-3 — a three-phase reflective dialogue** (Look Back / Look In /
  Look Forward) with Gemini, grounded in Korthagen's ALACT model.
- **Output — a Learning Portrait**, a 300-400 word narrative synthesis the
  teacher reviews, may regenerate, accepts, and downloads as a PDF.

The routing chain, the M15-completion gate, and the absence of a consent gate
on the Epilogue itself (C.2.5 decision D4) are retained unchanged.

---

## 2. Background — placeholder vs Phase G

### 2.1 Kept from the C.2.5 placeholder

- `apps/epilogue/` as a separate app, URL namespace `/epilogue/`, 12 tests.
- `EpilogueCompletion` — OneToOne with `auth.User`, `started_at` /
  `completed_at`.
- The `M15 -> /epilogue/ -> T2` routing chain and `_post_epilogue_destination`.
- The M15-completion gate (TD-013), on GET and POST.
- No consent gate on the Epilogue itself (D4) — it is pedagogical.

### 2.2 Added by Phase G

Schema extension (§9); Stage 0 (§5); Stages 1-3 and two new agents (§6, §7);
the Learning Portrait and its PDF (§8); the dialogue-corpus consent amendment
(§11); M15 content alignment (§12). The placeholder view becomes the Stage 0
entry point; `_post_epilogue_destination` is unchanged.

---

## 3. The four-stage architecture

| Stage | Purpose | Teacher input | LLM |
|---|---|---|---|
| Stage 0 — Personal Evolution Dashboard | The teacher sees their own data | None — view only | None (aggregation of stored data) |
| Stage 1 — Look Back | Dialogue on the journey | Dialogue | Gemini |
| Stage 2 — Look In | Dialogue on a neutral juxtaposition of the teacher's own data | Dialogue | Gemini |
| Stage 3 — Look Forward | Dialogue toward a concrete commitment | Dialogue | Gemini |
| Output — Learning Portrait | 300-400 word narrative, reviewed and accepted, exported as PDF | Review / accept | Gemini |

Stage 0 is part of the mandatory flow (zero burden — viewing, not a task).
Stages 1-3 are an optional, actively-invited dialogue (decision Q5).

---

## 4. Decisions log

### 4.1 Scope and architecture (Phase G kickoff)

| # | Decision | Choice |
|---|---|---|
| G-D1 | Build basis | Extend the C.2.5 placeholder app. |
| G-D2 | Stage 0 data sources | DTP + RTM only. No AILST chart — T2 has not run at Epilogue time. |
| G-D3 | Stage 0 DTP view | Theme-evolution map (no numbers) + narrative timeline M2->M15. Descriptive, D.3a-consistent. |
| G-D4 | DTP model | The D.3a dual-signal descriptive DTP (VCS + TSS). Raw similarity stored, never displayed. |
| G-D5 | Dialogue length | Ceiling 5 turns/phase; typical design target 2-3. The ceiling is a pedagogical / teacher-time lever, **not** a cost lever (§14). |
| G-D6 | Image retrospective reflection | Parked — Phase H / v2.0 candidate. |
| G-D7 | Epilogue agents | Two agents, both extending `BaseAIAgent` via `extract()` (revised from v1 — see D.1 / §7). |

### 4.2 The six open questions

| Q | Decision | Grounding |
|---|---|---|
| Q1 | One-shot for the pilot; `OneToOneField` retained (B.2). | Research-design integrity; DB-level invariant. No new construct. |
| Q2 | Stage 0 dashboard visible as a collapsible side panel through Stages 1-3. | Cognitive Load Theory / split-attention (§15). |
| Q3 | Stage 0 frozen at first entry; a JSON snapshot is stored (C.3). | Research-record stability. No new construct. |
| Q4 | Learning Portrait PDF: narrative text + an embedded HTML/CSS-rendered Stage 0 visual (B.3). | Roadmap §3 G.3; M15 portfolio framing. |
| Q5 | Stage 0 mandatory (zero burden); Stages 1-3 dialogue optional, actively invited. | Self-Determination Theory (§15). |
| Q6 | Thin data: show what exists + an honest adaptive message; the dialogue adapts; Stage 2 has a strict skip threshold (§6.4). | Extends D.3a §5 "honest absence of signal". No new external construct. |

### 4.3 Review-driven decisions (v1 -> v2)

All of B.1-B.5, C.1-C.5, D.1-D.4 are accepted and incorporated; see §0 and the
referenced sections. The single decision that required PI sign-off — B.4,
consent for the dialogue corpus — is resolved as option (α) with two conditions
(§11).

---

## 5. G.1 — Stage 0: the Personal Evolution Dashboard

### 5.1 Data sources (all already collected; no new LLM calls)

- **DTP:** `UserModuleProgress.reflection_dtp` — the D.3a `dtp_dual_v1` JSON
  composite (M2-M15). Per available signal: comparison module, raw similarity
  (stored, not displayed), themes (`increased`/`decreased`/`stable`), and a
  ~60-word descriptive narrative.
- **RTM:** `ReflectionTension` rows — per user / module / `tension_label`, with
  `selected_position` (1-5), `position_confirmed`, `optional_comment`.
- **Counts:** `UserModuleProgress`, `ReflectionTension`,
  `reflection_input_modality`.

### 5.2 What Stage 0 renders

**(A) Theme-evolution map.** The `increased` / `decreased` / `stable` theme
phrases from every DTP composite are aggregated into a descriptive map: which
themes recurred, which grew, which faded. No numbers. Delivers M15's promised
"themes that defined your reflective writing".

**(B) Narrative timeline.** An M2->M15 strip; each module shows its DTP
descriptive narrative — the trajectory as a story spine, not a numeric curve.

**(C) RTM tension trajectories.** For each tension met in more than one module,
the teacher's `selected_position` (1-5) is plotted across those modules. The
positions are the teacher's own self-positioning, not an AI score — so plotting
them carries none of the D.3a display concern that applies to cosine
similarity.

**(D) Quantitative summary.** Descriptive, non-evaluative counts only: modules
completed, reflections written, distinct tensions surfaced, tensions actively
engaged (`position_confirmed`), and the input-modality mix.

All four are rendered in **HTML/CSS, no SVG** (B.3) — see §8.3.

### 5.3 Why no DTP similarity curve

After D.3a there is no single DTP score; the raw cosine similarity is kept
stored-but-not-displayed (D.3a §7.4) because it has no theoretically meaningful
threshold and "continuity is not quality" (D.3a §4.4). A numeric self-curve in
Stage 0 would silently reverse that grounded decision. G-D3 keeps Stage 0
descriptive.

### 5.4 Freezing — first entry only

Stage 0 is computed **once, on the teacher's first entry to the Epilogue**, and
the semantic payload is stored in `EpilogueCompletion.stage0_snapshot`
(JSON only — never rendered HTML, C.3; rendering is always live from a template
against this JSON, so a later CSS change cannot break an old teacher's view).

**Explicit consequence (supplementary point 3).** The snapshot is a photograph
of the moment the teacher first reached the Epilogue — effectively the moment
they finished M15. If the teacher views Stage 0, leaves, and returns two weeks
later to do the dialogue, the dialogue and the Learning Portrait run against the
**two-week-old frozen snapshot**, not a recomputation. This is intentional — it
keeps the Learning Portrait reproducible and the research record stable — and is
stated here so it is not a surprise. In practice the underlying DTP/RTM data
does not change after M15, so the snapshot equals a live recompute anyway;
freezing makes that explicit.

---

## 6. G.2 — Stages 1-3: the reflective dialogue

### 6.1 Structure

Three phases, each a short Gemini-driven dialogue. Each Gemini response is
<=150 words. Each phase has a hard ceiling of 5 turns and is designed to
resolve typically in 2-3 (G-D5). The three phases map onto Korthagen's ALACT
model (§15) and onto the three "questions to bring to the Epilogue" already
printed in M15 TAB2.

- **Stage 1 — Look Back.** Gemini opens with a synthesis of the journey drawn
  from the frozen Stage 0 snapshot; the teacher responds.
- **Stage 2 — Look In.** See §6.2.
- **Stage 3 — Look Forward.** Gemini moves the teacher toward one concrete,
  near-term classroom commitment.

### 6.2 Stage 2 — juxtaposition surfacing (B.1)

Stage 2 was described in v1 as surfacing a "contradiction". This is corrected.
Calling, for example, a theme the DTP marked `decreased` a "contradiction"
mislabels **development** as inconsistency, and re-introduces the evaluative
stance that D.3a §4.4 deliberately removed ("continuity is not quality"). Stage
2 must not do this.

In v2, Stage 2 performs **juxtaposition surfacing**:

- The view pre-computes, from the frozen Stage 0 snapshot, candidate
  juxtapositions of the teacher's **own** data — for example a theme prominent
  in early modules and absent later, or an RTM tension met in several modules
  with the teacher's positions on it.
- The agent presents **one** such juxtaposition **neutrally and without
  interpretation** ("In your early modules you returned often to X; in your
  later reflections X did not appear") and asks an **open** question.
- The **teacher** names what it is — development, a context-specific theme, or a
  tension they still hold. The agent never asserts the label.

This is the Schön / Mezirow distinction: the reflective practitioner surfaces
and names the dilemma; an external party that pre-names it is not supporting
reflection but replacing it. The user-facing stage name remains "Look In".

### 6.3 Dialogue prompt structure and token budget (C.1)

Each dialogue turn is one `extract()` call on `EpilogueDialogueAgent`. The
prompt is assembled as:

1. **System prompt** (~300 tokens) — role: a reflective dialogue partner, not
   an evaluator; descriptive-not-evaluative stance (consistent with D.3a);
   <=150-word responses; the current stage's ALACT-grounded purpose.
2. **Frozen Stage 0 summary** (~500 tokens) — a compact summary of the
   `stage0_snapshot`: the top recurring / grown / faded themes, the recurring
   RTM tensions, the quantitative counts. **Not** the full reflection corpus.
3. **Prior-stage carry-forward** (~150 tokens) — a 1-2 sentence summary of what
   the earlier phases concluded. Earlier phases' full transcripts are not
   re-sent.
4. **Current-phase history** (up to ~1,700 tokens) — the turns of the current
   phase only (bounded by the 5-turn ceiling).

Worst-case input per turn ~2,700 tokens; output ~200 tokens. This bounds the
cost calculation in §14. The commitment to a **summary** context (not the full
corpus) is firm; it is what keeps the cost envelope an order of magnitude below
budget.

### 6.4 Stage 2 skip — strict quantitative threshold (C.5, supplementary point 2)

If the teacher's data is too sparse to support any juxtaposition, Stage 2 is
skipped — the dialogue goes directly from Stage 1 to Stage 3, with a message to
the teacher. The threshold is **quantitative and auditable**, not subjective.

Stage 2 is skipped if and only if **both**:

- `distinct_tensions` < 3 — fewer than three distinct `tension_label` values
  across all of the teacher's `ReflectionTension` rows; **and**
- `shifting_dtp_composites` < 3 — fewer than three `reflection_dtp` composites
  (M2-M15) in which at least one signal has a non-empty `increased` or
  `decreased` theme list (i.e. the composite shows actual thematic movement,
  not only stable themes).

On skip, a record is written to `dialogue_turns`:
`{stage: 2, role: 'system', event: 'stage2_skipped',
reason: 'insufficient_juxtaposition_material',
metrics: {distinct_tensions: N, shifting_dtp_composites: M}}` — so the skip is
fully reconstructable for the research record.

### 6.5 Persistence and transparency

- Dialogue turns are stored in `EpilogueCompletion.dialogue_turns` (JSON):
  `[{stage, role, content, model, generated_at}]`.
- The dialogue screen carries an EU AI Act Article 50(1) transparency notice,
  consistent with the TAB5 notices.
- Per-turn inline metadata (`model`, `generated_at`) is the audit trail for the
  conversational content; the formal `AIArtefactProvenance` row is reserved for
  the Learning Portrait (§8.5).

---

## 7. The Epilogue agents

Two concrete agents, both `ResearchInstrumentAgent`s (they operate on the
teacher's reflective artefacts and produce primary research data), both used
via **`extract()`**:

- **`EpilogueDialogueAgent`** — one `extract()` call produces one dialogue turn,
  given the stage, the current-phase history, and the frozen Stage 0 summary.
  `extract()` is correct: the AI proposes a turn, the teacher ratifies it by
  responding; there is no atomic artefact commit per turn.
- **`EpiloguePortraitAgent`** — one `extract()` call proposes the Learning
  Portrait text. **Revised from v1**, which used `generate()`. Per D.1 the
  Portrait has a review/regenerate/accept loop, so persistence is a separate,
  user-driven action — the defining case for `extract()`. A companion
  "accept portrait" endpoint performs the persist + provenance write inside one
  `transaction.atomic` block (the CP-9 atomicity praised in the v1 review is
  preserved — it is relocated from the agent to the accept-endpoint, exactly as
  `RTMAgent` + `save_tensions` already do it).

Both use `gemini-2.5-flash`. No change to the agent hierarchy
(`BaseAIAgent -> ResearchInstrumentAgent`).

---

## 8. G.3 — the Learning Portrait

### 8.1 Content

A 300-400 word narrative synthesis of the teacher's journey, produced by
`EpiloguePortraitAgent` from the dialogue responses and the frozen Stage 0
snapshot.

### 8.2 PDF generation

The codebase already has a PDF path: `xhtml2pdf` (`pisa`), used for the M13
canvas export. The Learning Portrait reuses it — a dedicated
`templates/pdf/learning_portrait.html` rendered to PDF. **No new dependency.**

### 8.3 The Stage 0 visual — HTML/CSS, one render path (B.3)

The v1 §8.3 "technical risk" (xhtml2pdf has limited SVG support) is removed by
**designing the Stage 0 visual in HTML/CSS from the start, with no SVG**: the
theme-evolution map as styled HTML blocks / badges, the narrative timeline as
text blocks, the RTM trajectories as an HTML table or CSS bars. The same
template renders the Stage 0 view **both** in-page (Stage 0, and the collapsible
side panel during the dialogue) **and** inside the Learning Portrait PDF. One
render path, zero new dependency, no SVG-to-raster conversion.

### 8.4 HITL contract — "AI proposes, human ratifies" (D.1)

The Learning Portrait is not an AI output the teacher passively receives. Its
human-in-the-loop contract:

1. `EpiloguePortraitAgent.extract()` **proposes** the portrait text.
2. The teacher **reviews** it in-page.
3. The teacher may **regenerate** it — bounded to **2 regenerations** (a
   cost-and-closure bound; each regeneration is a fresh `extract()` call).
4. On **accept**, the companion endpoint persists `learning_portrait_text`,
   generates the PDF, and writes the `AIArtefactProvenance` row — atomically.

This gives the Portrait the same ratification pathway every other AI output in
the platform has, and matches the `extract()` semantics in `BaseAIAgent`.

### 8.5 EU AI Act Article 50(2) — machine-readable markers (D.2)

The Learning Portrait is AI-generated content. Both renderings carry markers via
the existing C.3 infrastructure:

- The in-page Portrait uses the `{% ai_provenance %}` and
  `{% ai_provenance_jsonld %}` template tags (human-readable marker + page-level
  JSON-LD).
- The PDF carries a human-readable AI-provenance footer and an embedded
  machine-readable marker (JSON-LD block / document metadata).

The Portrait's provenance uses the existing `epilogue_portrait` value in
`AIArtefactProvenance.ARTEFACT_KIND_CHOICES` (added forward-compat in C.3);
no `compliance` change is required.

---

## 9. Schema extension

One additive migration on `epilogue_completions`. No existing column altered.

| Field | Type | Purpose |
|---|---|---|
| `stage0_snapshot` | `JSONField(default=dict, blank=True)` | Frozen Stage 0 semantic payload (JSON only — C.3). |
| `stage0_seen_at` | `DateTimeField(null=True, blank=True)` | First Stage 0 view. |
| `dialogue_entered` | `BooleanField(default=False)` | Did the teacher enter the dialogue (Q5 measured variable). |
| `stage1_completed_at` | `DateTimeField(null=True, blank=True)` | Look Back finished. |
| `stage2_completed_at` | `DateTimeField(null=True, blank=True)` | Look In finished (or skipped — §6.4). |
| `stage3_completed_at` | `DateTimeField(null=True, blank=True)` | Look Forward finished. |
| `dialogue_turns` | `JSONField(default=list, blank=True)` | Conversation log + skip records. |
| `learning_portrait_text` | `TextField(blank=True, default='')` | Accepted narrative. |
| `learning_portrait_pdf` | `FileField(upload_to='epilogue_portraits/', null=True, blank=True)` | Generated PDF. |
| `learning_portrait_generated_at` | `DateTimeField(null=True, blank=True)` | Accept timestamp. |

`completed_at` keeps its meaning — set when the Epilogue is finished (after
Stage 3 + portrait accept, or when the teacher skips the dialogue). The
`OneToOneField` is **retained** (B.2): it enforces the one-shot invariant at the
database level. Replay is out of pilot scope and is logged as TD-022 (§18).

No `compliance` migration is required: the `epilogue_portrait` artefact kind
already exists in `AIArtefactProvenance.ARTEFACT_KIND_CHOICES` (added
forward-compat in C.3). G.0 is therefore a single migration.

---

## 10. Routing and lifecycle

Unchanged from C.2.5: `M15 -> /epilogue/ -> T2` (or dashboard).

```
no row                          -> never visited /epilogue/
row, stage0_seen_at set          -> Stage 0 viewed (mandatory flow)
row, dialogue_entered = false    -> teacher chose to skip the dialogue
row, stageN_completed_at set     -> dialogue progressing
row, learning_portrait_text set  -> portrait accepted
row, completed_at set            -> Epilogue finished; routed forward
```

### 10.1 Failure modes and resume semantics (D.3)

- **Gemini fails mid-turn.** The agents return `None` on AI-side failure (the
  established convention). The dialogue view surfaces a graceful "the assistant
  could not respond — try again" state; no turn is written; the teacher retries.
  No partial turn is persisted.
- **The teacher closes the browser mid-dialogue.** Every completed turn is
  already in `dialogue_turns`. On return, the Epilogue resumes at the last
  stored stage / turn — the frozen `stage0_snapshot` makes the resumed context
  identical to the original.
- **PDF generation fails.** The portrait **text** is persisted at the accept
  step independently of the PDF. A PDF failure leaves `learning_portrait_text`
  intact and `learning_portrait_pdf` null; the download view regenerates the
  PDF on demand from the stored text. The teacher never loses the portrait.
- **`extract()` returns `None` for the portrait.** Treated as a failed
  proposal; the teacher sees a retry control; nothing is persisted until a
  successful proposal is accepted.

---

## 11. Consent treatment for the dialogue corpus (B.4)

The Stage 1-3 dialogue produces a new body of text — the teacher's responses
and the AI turns. The C.2.2 consent set (`research_participation` +
`data_sharing`) names reflections, RTM, AILST, DTP, but not a dialogue corpus.
This gap is closed as follows.

**Decision: option (α) — covered by `research_participation` via an explicit
text amendment.** Rationale (PI, IRB-considered): the `dialogue_turns` are
**reflective text in dialogue form** — the same category of personal data as
the existing reflections, not a new or special category. A fourth consent type
would worsen onboarding consent fatigue (which the C.2.5b interstitial exists to
mitigate) and would invite the IRB question "why is this separate?". The
`ConsentRecord` supersede pattern (C.2.2) was designed for exactly this case.

**Two binding conditions (PI):**

1. **Explicit naming.** The amended text must name the dialogue corpus
   explicitly — not a vague "all reflective content". IRB at the IHU Ethics
   Committee requires specificity. Proposed language names "dialogue-form
   reflection produced in the PROODOS Epilogue, including the teacher's written
   responses and the AI-generated dialogue turns".
2. **Version logging.** The consent text version each participant agreed to
   must be auditable per-participant in the `ConsentRecord` log, so the IRB can
   see who consented to which version.

**Mechanism and the C.5 dependency.** C.5 (§3.C.5 of the roadmap — confirmed to
exist) already mints `RESEARCH_PARTICIPATION_TEXT_V2_IRB_REVISED` in
`apps/compliance/copy.py` and bumps `RESEARCH_CONSENT_CURRENT_VERSION`. The
dialogue-corpus language is added as a **required line item to the C.5
checklist** — it must be in the V2 text regardless of what the IRB feedback
otherwise contains. Phase G must therefore add one row to the roadmap §3.C.5
table.

**Architecture (pedagogical vs research separation).** The dialogue runs for
**all** teachers (pedagogical feature, no consent gate — D4); `dialogue_turns`
are stored for all. The dialogue corpus enters the **research dataset** only for
teachers with active `research_participation` consent — the same separation the
platform already applies to reflections. Phase G's **research use** of the
dialogue corpus is gated on C.5 being applied; since C.6 already requires
"C.5 applied" before pilot recruitment, the sequencing
`Phase G code -> C.5 -> C.6 -> pilot` holds with no extra gate.

This section is a research/legal artefact; the final consent wording is
confirmed with the PI and the IRB before deployment.

---

## 12. M15 content alignment

M15 TAB2 references the Epilogue and currently describes the pre-D.3a DTP. The
M15 `main_content` row (single Universal variant) is updated:

- **Part 2 ("Reading Your Own Development")** — rewritten for the D.3a
  dual-signal DTP (VCS + TSS, descriptive, non-uniform, no scores/labels). The
  example "DTP Similarity Curve" SVG and the "similarity score /
  High-Moderate-Significant" table are removed; the description is aligned to
  what Stage 0 shows.
- **Stale internal copy** — "Your actual dashboard in TAB3 will show your own
  data" corrected to point to the Epilogue.
- **The three "questions to bring to the Epilogue"** are kept — they map onto
  Stages 1-3.
- **Part 5 Epilogue notice** — the "optional / invitation" framing is kept (it
  is accurate for the dialogue under Q5); one sentence is added clarifying that
  Stage 0 is shown to every teacher.

### 12.1 RAG re-ingest — pre-pilot, no contamination (B.5)

M15 TAB2 content feeds the RAG corpus, so the content edit is followed by an
M15 RAG re-ingest. **Contamination is avoided by timing, not by versioning.**
Phase G is pre-pilot work: per the roadmap, all code-bearing phases complete and
C.5/C.6 run before participant recruitment. The M15 content edit + re-ingest
therefore happens while there is no pilot participant; current M15 completions
are test data. The proposal makes this explicit and adds a checklist item to the
C.6 pre-pilot operational sequence: "confirm M15 content edit + RAG re-ingest
done". RAG-corpus versioning is unnecessary given the pilot feature-freeze and
is logged only as a defensive note — TD-023 (§18).

---

## 13. Research variables produced by Phase G (D.4)

Phase G is not only a feature; it produces research data. The variables, and
their place in the dissertation analysis, with an explicit crosswalk to roadmap
**§H.5** (which already lists "Learning Portraits" in the qualitative corpus):

| Variable | Source | Dissertation use | §H.5 mapping |
|---|---|---|---|
| `dialogue_entered` | `EpilogueCompletion` | Binary covariate in the T0->T1->T2 analysis: did the teacher engage the dialogue. | Quantitative — moderator variable |
| Per-stage completion timestamps | `stage1/2/3_completed_at` | Engagement duration and depth-reached. | Quantitative |
| Dialogue turn counts per stage | `dialogue_turns` | Engagement intensity / verbosity. | Quantitative |
| `stage2_skipped` + metrics | `dialogue_turns` skip record | Data-sufficiency covariate; lets sparse-data teachers be analysed separately. | Quantitative |
| Dialogue corpus | `dialogue_turns` (teacher + AI text) | Thematic / discourse analysis in the discussion chapter. | **Qualitative corpus — extends §H.5** |
| Stage 2 interpretive responses | `dialogue_turns` | How the teacher names a juxtaposition (development / context / tension). | Qualitative |
| Learning Portrait text | `learning_portrait_text` | Narrative synthesis corpus. | Qualitative — already named in §H.5 |

This table is the Phase G entry in the dissertation's measurement crosswalk;
§H.5 of the roadmap should reference it once Phase G lands.

---

## 14. Cost envelope (C.2)

Verified pricing — Gemini 2.5 Flash, standard interactive: **$0.30 / 1M input
tokens, $2.50 / 1M output tokens** (Google AI for Developers, May 2026).

- **Stage 0:** zero new Gemini calls — aggregation of stored data.
- **Dialogue:** worst case 15 turns (5/phase x 3); input ~2,700 tokens/turn
  (§6.3), output ~200 tokens/turn.
- **Learning Portrait:** 1 proposal + up to 2 regenerations = 3 calls; input
  ~3,000 tokens, output ~500 tokens each.

Worst-case totals: input ~46,500 tokens -> ~$0.014; output ~4,500 tokens ->
~$0.011. **~$0.025 ≈ EUR 0.023 per teacher.** Even at 4x the assumed context
size, ~EUR 0.09.

This is negligible against the EUR 1 / teacher budget (which covers the whole
15-module pipeline). **Consequence:** the 5-turns-per-phase ceiling is a
pedagogical / teacher-time lever, **not** a cost control. The figure above is
re-verified against live `cost_tracker` data once the dialogue runs (§20).

---

## 15. Bibliographic grounding

**The three-stage structure — primary grounding: Korthagen's ALACT model.**
Korthagen et al. (2001) describe reflection as a five-phase cycle — Action,
Looking back, Awareness of essential aspects, Creating alternative methods,
Trial. The Epilogue's three phases map onto it:

| Epilogue stage | ALACT phase(s) |
|---|---|
| Look Back | Action + Looking back |
| Look In | Awareness of essential aspects |
| Look Forward | Creating alternative methods + Trial |

The ALACT "Awareness of essential aspects" phase is, in Korthagen, the
reflector's **own** realisation — which also grounds the B.1 correction: Stage 2
is awareness the teacher reaches, not a label the AI imposes.

**Dialogic critical reflection — Mezirow.** Transformative learning (Mezirow,
1991): critical reflection often proceeds through dialogue, and the
"disorienting dilemma" is **experienced by the learner**. This grounds both the
dialogic format of Stages 1-3 and, again, B.1 — a juxtaposition the teacher
works through, not a verdict delivered to them.

**The reflective practitioner — Schön, via the project's own RPE paper.** Schön
(1983), *The Reflective Practitioner*, is already the theoretical backbone of
the project's publication Dourvas, Kokkonis & Kontogiannis,
*Reconceptualizing Prompt Engineering as Reflective Professional Practice*
(reference [10] in that paper). The Epilogue is the retrospective culmination of
the reflective-practice framing that paper established for TAB5 / RTM / DTP.
Grounding the Epilogue in Schön through the project's own prior work is
deliberate — it keeps the dissertation's theoretical framework continuous rather
than importing a fresh external reference.

**Considered and set aside — Brookfield.** Brookfield's Four Lenses (1995) —
autobiographical, students' eyes, colleagues, theoretical literature — are
**vantage points / sources** of reflection, not temporal phases. They do not map
onto a Look Back / Look In / Look Forward sequence and are therefore not used as
the grounding for the three-stage structure.

**Q2 — Cognitive Load Theory / split-attention.** Sweller (1988); Chandler &
Sweller (1992). The dialogue refers continuously to the Stage 0 data; a
persistent, collocated (collapsible) dashboard avoids the split-attention
extraneous load that removing it would impose.

**Q5 — Self-Determination Theory.** Ryan & Deci (2000); Deci & Ryan (2000).
Autonomy is the hallmark of intrinsic motivation; coerced reflection becomes
performative. Stage 0 (information, not a task) can sit in the mandatory flow;
the dialogue is kept a genuine, clearly-labelled choice.

**Q6 / Stage 0 descriptive stance — internal.** Extends the D.3a §4.4 / §5
principles ("describe, do not evaluate"; "an honest 'no signal here' is
defensible"). No new external construct.

All external references are folded into
`Literature_Review_Synthesis_Note(1).md` §15.

---

## 16. Architectural placement — files

**New:**
- `apps/epilogue/migrations/0002_*.py` — schema extension (§9).
- `apps/epilogue/services_stage0.py` — Stage 0 aggregation (DTP + RTM -> JSON
  snapshot) + Stage 2 juxtaposition pre-computation + the §6.4 skip evaluation.
- `apps/agents/epilogue_dialogue.py` — `EpilogueDialogueAgent`.
- `apps/agents/epilogue_portrait.py` — `EpiloguePortraitAgent`.
- `templates/epilogue/stage0.html`, `dialogue.html`, `portrait.html` +
  a shared Stage 0 partial used in-page and in the PDF.
- `templates/pdf/learning_portrait.html`.

**Modified:**
- `apps/epilogue/models.py`, `views.py`, `urls.py`, `tests.py`.
- `apps/compliance/copy.py` — dialogue-corpus consent language (the V2 mint;
  coordinated with C.5 — §11).
- M15 `main_content` row + M15 RAG re-ingest (§12).
- `PROODOS_UNIFIED_ROADMAP.md` (§3 Phase G, §3.C.5 checklist row, §H.5
  crosswalk reference), `TECH_DEBT_LOG.md` (TD-011 close, TD-022, TD-023),
  `Literature_Review_Synthesis_Note(1).md` §15, the architecture chapter.

---

## 17. Migration plan

One additive migration on `epilogue_completions` (the ten new fields), preceded
by a `pg_dump` backup and a `sqlmigrate` / `migrate --plan` dry-run reported for
explicit PI approval. No `compliance` migration is required — the
`epilogue_portrait` artefact kind already exists (C.3 forward-compat). The
migration is additive; no existing data is touched.

---

## 18. Tech-debt entries

**TD-022 — Epilogue replay.** Current `OneToOneField` enforces one-shot at DB
level. Post-pilot, if replay is desired, drop the unique constraint and add
`is_active` semantics. Migration is mechanical.

**TD-023 — M15 RAG corpus versioning (defensive).** The M15 content edit + RAG
re-ingest is pre-pilot, so no participant sees two corpus versions (§12.1). If
M15 content is ever edited mid-pilot, RAG-corpus versioning per `RAGQuery`
becomes necessary. Not needed under the pilot feature-freeze; logged so the
assumption is explicit.

---

## 19. Commit plan

| Commit | Content |
|---|---|
| G.0 | Schema extension — the `epilogue_completions` migration (§17). |
| G.1 | Stage 0 dashboard — aggregation service, HTML/CSS view + shared partial, template. No LLM. |
| G.2a | `EpilogueDialogueAgent` + dialogue endpoint + Stage 1 (Look Back). |
| G.2b | Stage 2 (Look In) — juxtaposition pre-computation, neutral presentation, the §6.4 skip threshold. |
| G.2c | Stage 3 (Look Forward) + dialogue completion + skip path. |
| G.3 | `EpiloguePortraitAgent` + the review/regenerate/accept loop + PDF export + Article 50(2) markers. |
| G.4 | M15 content alignment + M15 RAG re-ingest (§12). |
| G.5 | Test sweep + roadmap (§3 Phase G, §3.C.5 row, §H.5), TD-011/022/023, Literature-note, architecture-chapter updates. |
| G.6 | Magazine design upgrade — visual treatment of Stage 0, the dialogue (Stages 1-3), and the Learning Portrait in-page + PDF, in the TAB1/TAB2/TAB5 editorial register. Separate design proposal first (planned 2026-05-23 during G.2a sample-review). |

The dialogue-corpus consent language (§11) is delivered into `copy.py` here but
**activated** in C.5; G.5 adds the §3.C.5 checklist row.

---

## 20. Implementation-time verification

- Sample-review of generated dialogue turns and Learning Portraits, to confirm
  the descriptive-not-evaluative stance holds in practice (mirrors the D.3a
  §7.2 narrative-sample check).
- Re-verify the §14 cost figure against live `cost_tracker` data once the
  dialogue runs end-to-end.
- The G.6 magazine design upgrade may force §8.3's single-HTML-render
  decision to relax: a rich in-page magazine treatment may not survive
  `xhtml2pdf`. Plan: re-evaluate at G.6 design time; if necessary, the
  Learning Portrait PDF carries a simpler variant of the magazine markup
  (rich in-page + simple PDF), accepted as a trade-off.

---

## 21. Decisions log

**Confirmed (kickoff + v1 review, 2026-05-21):** G-D1..G-D7; Q1..Q6;
B.1-B.5; C.1-C.5; D.1-D.4; B.4 = option (α) with the two §11 conditions.

**To confirm:** this proposal as a whole, then the G.0 migrations under the
backup / dry-run / approval protocol.

---

## 22. G.3 implementation clarifications (2026-05-23, during G.3)

Three points came out of the G.3 design session that were either implicit in
the v2 text or where an implementation choice had to be pinned down. None
changes the v2 direction; each is recorded here so the implementation matches
what was reviewed.

### 22.1 Transient portrait proposals + the regeneration counter — `dialogue_turns`, not a new column

§8.4 specifies an "AI proposes -> teacher reviews -> may regenerate (bounded
to 2) -> accept" loop. §9 lists `learning_portrait_text` (the **accepted**
text) but does not name a place to hold the **proposed-but-not-yet-accepted**
text or the regeneration counter. Two options were considered:

- Add a new `JSONField` (or pair of fields) to `epilogue_completions`. This
  would require a second migration after G.0 and break the "G.0 is a single
  migration" commitment recorded in the header correction.
- Reuse the existing `dialogue_turns` JSONField with a `portrait`-stage
  family of system events.

**Decision: reuse `dialogue_turns`.** The pattern is already established —
Stage 2 skip records are written there (§6.4). The schema extension is
internal to a `JSONField(default=list)`, so it is a no-migration change.
Each new proposal appends one row:

```
{stage: 'portrait', role: 'assistant', event: 'proposal',
 content: '<full proposed text>',
 model: 'gemini-2.5-flash',
 generated_at: '<iso>'}
```

The **current proposal** = the most recent `proposal` event. The
**regeneration count** = `(count of 'proposal' events) - 1`. The hard ceiling
is therefore three `proposal` events (1 initial + 2 regenerations); the
regenerate endpoint refuses a fourth.

On accept, two additional events land — atomically with the
`learning_portrait_text` / `learning_portrait_pdf` writes and the
`AIArtefactProvenance` row:

```
{stage: 'portrait', role: 'system', event: 'accepted',
 accepted_proposal_index: <0-based index into the proposal events>,
 generated_at: '<iso>'}
```

This keeps the research record reconstructable: the analyst can see how many
proposals the teacher saw, when each was generated, and which one they
accepted — without a separate audit table.

**Consequence for §9:** the field list is unchanged. The `dialogue_turns`
help_text grows to mention the `portrait`-stage events alongside the existing
stage-2 skip records; no migration is required.

### 22.2 Skip-dialogue teachers do not see the Portrait

§8.1 specifies that the Portrait is produced "from the dialogue responses and
the frozen Stage 0 snapshot". A teacher who skipped the dialogue at Stage 0
(`dialogue_entered = false`) has no dialogue responses to draw on; the
Portrait is therefore not generated for them. §10's lifecycle table already
reflects this — the `dialogue_entered = false` row goes directly to
`completed_at` — but the implication for the Portrait was implicit.

**Made explicit:** the skip-dialogue path bypasses `/epilogue/portrait/` and
routes the existing `/epilogue/complete/` endpoint unchanged (Stage 0 ->
skip -> complete -> T2/dashboard). The dialogue-entered path inserts the
Portrait between Stage 3 and `/complete/`. The `_post_epilogue_destination`
helper from C.2.5 is unchanged; the rewiring is upstream of it.

A regression test in G.3b covers this: a teacher with `dialogue_entered=False`
who POSTs to `/epilogue/complete/` is routed to T2/dashboard with no Portrait
row touched.

### 22.3 Article 50(2) in the PDF — strict variant (JSON-LD + PDF document metadata)

§8.5 commits to a "machine-readable marker (JSON-LD block / document
metadata)" but leaves the choice of mechanism open. `xhtml2pdf` (pisa) does
not interpret `<script type="application/ld+json">` as embedded structured
data — it ignores it visually, and the JSON-LD becomes plain text inside the
PDF stream (greppable via `pdftotext`, but not a true metadata layer). The
two options were considered:

- **Regular:** ship only the in-HTML JSON-LD block + a human-readable footer.
  Greppable, faithful to the in-page rendering, simple.
- **Strict:** add the in-HTML JSON-LD block **and** a `pisa` link-callback /
  context that sets PDF document metadata (Title / Author / Subject /
  Producer / Creator) on the document itself.

**Decision: strict.** The Learning Portrait is the most prominent AI artefact
the platform produces — a downloadable PDF that may circulate outside the
platform's surfaces — and Article 50(2) reads more naturally as
"machine-readable on the artefact itself" than "readable if you extract the
PDF's text stream and grep it". The extra cost is a small `pisa`
`xhtml2pdf_default_callbacks`-style hook in the PDF view + one test that the
generated PDF carries the expected metadata.

Concretely:

- The PDF document metadata layer carries:
  - **Title:** "PROODOS Learning Portrait — <teacher display name>"
  - **Author:** "PROODOS Platform (AI-generated, human-accepted)"
  - **Subject:** "AI-generated reflective synthesis (EU AI Act Article 50)"
  - **Creator / Producer:** "gemini-2.5-flash via xhtml2pdf"
- The rendered HTML still carries:
  - The `{% ai_provenance_jsonld %}` block at the head (greppable structured
    data).
  - A footer paragraph: "This Learning Portrait was generated by
    gemini-2.5-flash on YYYY-MM-DD and accepted by the teacher in the
    PROODOS Epilogue. EU AI Act Article 50."

The in-page Portrait (§8.5 first bullet) is unchanged — it already uses the
existing `{% ai_provenance %}` and `{% ai_provenance_jsonld %}` template
tags. The strict variant adds the metadata layer only on the PDF side.

---

## 23. Aletheia persona — agent-prompt enforcement (2026-05-23, before G.6a)

### 23.1 What this section adds

The G.6 design proposal (`PHASE_G_G6_DESIGN_PROPOSAL_v1_20260523.md`) gives
the dialogue chatbot a teacher-facing persona named **Aletheia** and codifies
linguistic rules in its §3.3 / §3.5 — friendly framing uses the name
"Aletheia"; the agent itself **does not** name itself, does not use first-
person emotional voice, and does not reference being an AI within the
dialogue. G.6 §3.5 phrased this as a design rule; §0 of G.6 ruled "no agent
change" within G.6's scope. The two are in tension: a rule that depends on
the agent's actual output cannot be enforced from outside the agent.

This §23 resolves that tension within v2's own scope — the agent contracts
live here (v2 §7), so the prompt enforcement of the persona also lives here.
External review by a second LLM on 2026-05-23 surfaced the gap explicitly
(see G.6 §B.3 in the briefing thread); §23 closes it.

### 23.2 The prompt addition

The following block is **appended** (not replacing) to
`_SYSTEM_PROMPT` in `apps/agents/epilogue_dialogue.py`, immediately
after the existing "never open a reply by appraising what the
teacher said" instruction block and **before** the closing
word-cap paragraph. The existing descriptive-non-evaluative stance
(v2 §6.2) stays in force — the new block adds *persona* constraints
on top of the existing *stance* constraints. The 23.6 layer-2
regression check guards against the new block eroding the stance
(see §23.6).

```
You are the reflective partner the platform names "Aletheia" to the
teacher; you yourself do NOT introduce, name, or refer to yourself
by that name in the conversation. Do not begin replies with "I" and
avoid first-person language anywhere in your reply — emotional
("I feel", "I am glad"), cognitive ("I notice", "I think",
"I understand"), and perceptual ("I see", "I hear"). Do not refer
to being an AI, a model, a system, an assistant, or a chatbot
within the dialogue — the teacher already knows; restating it
in-turn is a distraction. Address the teacher in the second person
("you"); when an action would naturally take a subject, prefer
impersonal phrasing ("a thread runs through what you said") over
self-reference ("I notice a thread").
```

**Wording history (audit trail).** Drafted as 4 lines (v1, 2026-05-23
afternoon). Third-pass external review flagged two potential holes —
(a) the v1 phrasing covered only *emotional* first-person ("I feel"),
missing the equally anthropomorphising *cognitive* ("I notice",
"I think") and *perceptual* ("I see") variants that LLMs reach for
naturally; (b) the v1 "do not begin replies with 'I'" rule was
invisible in Greek (which expresses first-person through verb
endings). Hole (a) is closed in the current wording — it is a
language-neutral fix and tightens the anti-anthropomorphisation
guard meaningfully. Hole (b) is **deferred** by PI decision
(2026-05-23): the platform's EL branch is scheduled for the
following week and will introduce **Greek-language prompts written
in Greek register from the start**, with their own
anti-anthropomorphisation guidance using Greek-natural examples
(verb-ending patterns, no `νιώθω / παρατηρώ / βλέπω / σκέφτομαι`
etc.). Mixing one Greek-targeting bullet into an otherwise English
prompt — for a prompt that the current EN locale never runs against
Greek output — would be premature scope-creep that confuses both
languages' guidance. The EL branch owns the Greek rules cleanly.

### 23.3 Why these four rules, and only these four

The rules are minimal and specific — they do not redefine the agent's
voice or stance (those are owned by the existing prompt, v2 §6.2 / §6.5).
They close exactly the gap the reviewer surfaced:

- **No self-naming.** Without this, the agent could write "as Aletheia, I
  notice…", which would surface the persona inside the dialogue and break
  the §3.5 "named not voiced" boundary. The persona belongs to the
  template surface; the dialogue belongs to the reflective partner role.
- **No first-person language — emotional, cognitive, or perceptual.**
  Without this, "I am moved by what you said" (emotional), "I notice
  a thread in your reflections" (cognitive), and "I see what you
  mean" (perceptual) all break the descriptive-non-evaluative stance
  v2 §6.2 / D.3a §4.4 already commit to. The original draft of this
  rule (2026-05-23 afternoon) covered only the emotional variant —
  third-pass review caught that LLMs reach for cognitive and
  perceptual first-person at least as often, and the rule was
  expanded to cover all three. The "do not begin with 'I'" sub-rule
  is the directly-testable anchor; the "avoid anywhere in your
  reply" extension catches mid-sentence variants like "That returns
  to what, I think, you said earlier".
- **No in-dialogue AI self-reference.** Without this, "as an AI system I
  cannot judge…" surfaces in the conversation. The Article 50(1)
  transparency notice already discloses the AI status *outside* the
  dialogue (v2 §6.5); in-turn restating is bureaucratic and weakens the
  reflective register.
- **Second-person impersonal phrasing.** Provides a concrete positive
  replacement for the three forbidden patterns above — so the model
  reaches for "a thread runs through…" rather than "I notice…". Without
  this positive instruction, the negative rules would leave the model
  without a fallback voice.

### 23.4 What §23 does NOT change

- No schema change.
- No `AIArtefactProvenance` change. The provenance row still names
  `gemini-2.5-flash`; the teacher's PDF still carries
  `<meta name="creator">` with the model identifier (v2 §22.3).
- No view contract change. The dialogue endpoint still calls
  `EpilogueDialogueAgent().extract(...)` with the same signature.
- No `dialogue_turns` JSON record change. The agent still produces one
  turn per call; the turn's `model` field still records
  `gemini-2.5-flash`. The conversation as stored is byte-compatible
  with G.2 turns.
- No change to `EpiloguePortraitAgent`. The Portrait is third-person
  narrative ("Across your fifteen modules…") and does not need the
  no-self-reference rule. Its prompt is unchanged.
- No change to the Article 50(1) transparency notice (the "Google Gemini"
  language outside the dialogue is unchanged).

### 23.5 Commit plan

A single one-line-change commit landed *before* the G.6a CSS commit:

| Commit | Content |
|---|---|
| **v2-§23** | Prompt addition in `apps/agents/epilogue_dialogue.py`. One new test (`EpilogueDialoguePromptTest::test_persona_guards_present`) asserts the four guards appear in the assembled prompt. The 50-test dialogue suite (v2 §7) re-runs unchanged otherwise — the existing prompt-shape assertions are append-only and do not break. |

### 23.6 Verification — two-layer

The four prompt rules introduced in §23.2 are **restrictive**, not
generative — they remove patterns the model would otherwise produce.
Restrictive rules carry a known risk: they can over-constrain and
shift the agent's tone away from what the existing prompt (v2 §6.2
descriptive-non-evaluative stance, §6.5 reflective-partner role)
established. Verification therefore runs at two layers — the rules
must **hold**, AND the prior stance must **not regress**.

**Layer 1 — pattern check (forbidden-substring scan).** The next live
sample-review (G.6c, the dialogue chapter rewrite) reads ~10 dialogue
turns generated post-prompt-change and asserts none of them contain,
case-insensitive:

- `^I\b` at the start of a reply (first-person opening)
- `\bI feel\b`, `\bI am (excited|moved|glad|happy|sad|impressed)\b`
  (first-person *emotional* voice)
- `\bI (notice|think|understand|believe|see|hear|sense)\b` anywhere
  in the reply (first-person *cognitive / perceptual* voice — added
  in the third-pass-revised wording, §23.2)
- `\bas (an? )?AI\b`, `\bas (an? )?(model|system|assistant|chatbot)\b`
  (in-dialogue AI self-reference)
- `\bAletheia\b` (self-naming)

The patterns are English-only because the prompt the agent receives
and produces from is English; when the EL branch lands the following
week, layer 1 grows a Greek pattern set (verb-ending matches:
`\b(νιώθω|παρατηρώ|βλέπω|σκέφτομαι|καταλαβαίνω|πιστεύω)\b`) scoped
to the EL prompt's own §23-equivalent.

A slip on layer 1 is treated as **prompt-tuning feedback** (refine
the four lines), not a v3 trigger.

**Layer 2 — behavioural-regression check (added v2-revised per
second-pass reviewer point 5).** The same ~10 turns are also
inspected for *what the existing prompt was already supposed to
produce*. The four new rules must not erode any of these:

- (a) **Descriptive-not-evaluative stance** (v2 §6.2 / D.3a §4.4).
  No appraisals of the teacher's reflection ("interesting",
  "insightful", "valuable", "powerful", "meaningful"). No grading,
  praising, or ranking of the journey.
- (b) **Refusal of evaluation when asked** (v2 §6.5). When the
  teacher asks "was that right?" or "what do you think?", the agent
  still names the boundary ("that is yours to decide") rather than
  judging.
- (c) **One open question per turn** (v2 §6.1, the dialogue-shape
  invariant). Each reply still ends with exactly one open question.
- (d) **Warm and plain register** (v2 §6.2). Replies still feel
  like a partner, not a form field — the restrictive rules must
  not make the agent stiff or bureaucratic.

If (a)-(d) regress, the §23.2 prompt addition is **over-
constraining** and must be revised — either softened, or replaced
with a positive-form rule that achieves the same end without
collateral damage to the stance. Layer 2 protects the existing
character of the agent from the restrictive rules of layer 1.

The verification artefact lives at
`proodos_files/V23_PROMPT_VERIFICATION_20260524.md` (created during
the §23 commit's sample-review pass), with the 10 sample turns
quoted and each rule pass/fail tagged.

---

*End of Phase G Epilogue design proposal v2.*
