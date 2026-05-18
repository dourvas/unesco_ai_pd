# DTP Redefinition — Design Proposal v1

**Date:** 2026-05-18
**Status:** Draft for review. No code written. This document proposes a redefinition
of the Developmental Trajectory Predictor (DTP); it is to be reviewed and signed off
before any implementation begins. The §7.4 calibration question and the
§7.1 / §7.2 / §9 items were resolved in the 2026-05-18 design session (see §12).
**Origin:** chat-side design session, 2026-05-18 (John Dourvas, PI).
**Roadmap relationship:** This is new work, not part of the original Phase D scope.
Proposed slot: **D.3a — DTP Redefinition**, a prerequisite to the existing
**D.3 — DTP XAI narrative** (proposed renamed to **D.3b**). Rationale in §9.

---

## 1. Summary

The Developmental Trajectory Predictor (DTP) currently produces a single
"developmental signal" by comparing a teacher's current reflection against their
most recent reflection from any other module. Because the 15 modules are
distributed across 5 UNESCO competency aspects, that comparison routinely places
reflections from *different* aspects side by side. The resulting cosine similarity
is dominated by topic difference rather than by developmental change, while the
instrument labels it a "developmental trajectory". This is a construct-validity
mismatch: the measure does not measure the construct it names.

This proposal redefines the DTP to compute **two separate, individually
interpretable signals**:

- a **Vertical Continuity Signal (VCS)** — comparison within a single UNESCO
  aspect, against the immediately lower proficiency level;
- a **Temporal Shift Signal (TSS)** — comparison against the immediately preceding
  module.

The redefinition reuses the existing cosine-similarity mechanism without
modification. Only the *selection* of which reflections to compare changes, plus
the shape of the composite output. The instrument becomes deliberately
**non-uniform**: modules at the base of an aspect column carry only the TSS, and
the very first module carries no signal at all. This non-uniformity is argued to
be a methodological strength, not a defect (§5).

A further decision (§7.4) shapes what the pilot version produces. The
three-category continuity label ("High" / "Moderate" / "Significant") is treated
as a post-pilot research-analysis artefact, not a pilot deliverable. During the
pilot the DTP shows only threshold-free, descriptive output — the thematic shifts
and a descriptive narrative — and stores each signal's raw similarity value. The
redefined DTP therefore ships with **no continuity thresholds at all**;
calibration is a documented post-pilot step.

---

## 2. Motivation — a construct-validity problem

### 2.1 What the DTP does today

For a teacher submitting a reflection at module *N*, the caller selects the
comparison reflection with a single query (`apps/modules/views.py:2315-2323`):

```sql
SELECT rq.reflection_text, m.code
FROM rag_queries rq
JOIN modules_module m ON rq.module_id = m.id
WHERE rq.user_id = %s
  AND rq.module_id != %s        -- any module other than the current one
ORDER BY rq.created_at DESC      -- most recent first
LIMIT 1;                         -- exactly one
```

`DTPAgent._do_generate` (`apps/agents/dtp.py:122-179`) then embeds both
reflections, computes a cosine similarity, buckets it against two thresholds
(`0.85` / `0.70`, `apps/agents/dtp.py:88-89`), extracts thematic shifts, and
generates a 60-word narrative.

Sequential module progression is enforced in platform code. The "most recent
reflection from a different module" is therefore always the reflection from
module *N-1*.

### 2.2 The flaw

The 15 modules form a 5x3 matrix of UNESCO competency aspects and proficiency
levels. The `Module` model carries this structure explicitly through the
`unesco_aspect` (1-5) and `proficiency_level` (`Acquire` / `Deepen` / `Create`)
fields. The five aspect columns are:

| Aspect | Acquire | Deepen | Create |
|---|---|---|---|
| 1 — Human-Centred Mindset | M1 | M6 | M11 |
| 2 — Ethics | M2 | M7 | M12 |
| 3 — AI Foundations | M3 | M8 | M13 |
| 4 — AI Pedagogy | M4 | M9 | M14 |
| 5 — Professional Development | M5 | M10 | M15 |

Modules are taken in numeric order. Consequently the chronologically preceding
module almost always belongs to a *different aspect*. When a teacher is at M8
(Aspect 3, Deepen), the DTP compares M8 against M7 (Aspect 2, Deepen): an
AI-Foundations reflection against an Ethics reflection.

A cosine similarity between two reflections on *different competency aspects* is
driven primarily by the difference in subject matter, not by any change in the
depth or maturity of the teacher's thinking. The instrument nonetheless presents
this number as a "developmental trajectory" and a continuity label. The name
claims a construct (developmental change within the teacher's professional
thinking) that the measure does not isolate.

### 2.3 Why this matters

The DTP is a research instrument, not only a user-facing feature. Its output is
displayed to teachers, is the object that the planned XAI narrative (D.3) will
explain, and is a candidate input to later research variables. A construct that
mislabels topic difference as development would propagate that error into every
downstream use and would not survive scrutiny by the dissertation examination
committee. Correcting it before the pilot is the motivation for this proposal.

---

## 3. The structure the redefinition builds on

The redefinition relies entirely on structure that already exists in the data:

- the `Module.unesco_aspect` and `Module.proficiency_level` fields;
- the five aspect columns shown in §2.2, which `UNESCO_VALIDATION_STARTING_POINT.md`
  documents as the platform's "5 vertical progressions";
- the enforced sequential progression rule, which makes "the preceding module"
  unambiguous.

No new schema is required to know, for any module, its same-aspect lower-level
counterpart and its immediate predecessor.

---

## 4. The redefined DTP — two signals

### 4.1 Vertical Continuity Signal (VCS)

The VCS compares the current reflection against the teacher's reflection at the
**immediately lower proficiency level of the same UNESCO aspect**:

- a **Deepen** module is compared against its **Acquire** counterpart
  (e.g. M8 vs M3);
- a **Create** module is compared against its **Deepen** counterpart
  (e.g. M13 vs M8).

Because both reflections concern the same competency aspect, the cosine
similarity removes the cross-aspect confound that undermines the current DTP
(§2.2). What it captures is conceptual continuity or shift *within a
held-constant competency* as the teacher moves up the Acquire -> Deepen -> Create
progression — a far better-isolated signal than the current cross-aspect
comparison. It is not, however, a measure of the *quality* or *magnitude* of the
teacher's growth; see the interpretation boundary in §4.4.

### 4.2 Temporal Shift Signal (TSS)

The TSS compares the current reflection against the reflection at the
**immediately preceding module (N-1)**. Given the enforced sequential rule, this
is unambiguous.

The TSS is computed exactly as the current DTP signal is computed. The change is
not in the computation but in the **label**: the TSS is presented honestly as a
measure of *how the teacher's focus shifted between consecutive modules*, not as
a developmental measure. The current DTP's defect was never the M(N) vs M(N-1)
computation itself; it was naming that computation "developmental trajectory".
Placed beside the VCS and named for what it is, the same number becomes a
legitimate, distinct variable: focus continuity across the module sequence.

### 4.3 The two signals together

The teacher is shown two clearly distinguished signals rather than one ambiguous
number. During the pilot each signal is presented *descriptively*: the thematic
shifts it surfaced and a short narrative of those shifts. Each signal's raw
similarity value is computed and stored but not displayed, and no three-category
continuity label is shown at all during the pilot (see §7.4). The VCS answers
"how has my thinking about *this competency* matured?"; the TSS answers "how much
did my focus move since the *previous* module?". They are different research
variables and are not to be read as two grades of the same thing.

### 4.4 Interpretation boundary — continuity is not quality

Both signals are cosine similarities, and a cosine similarity measures *semantic
continuity*, not the quality or magnitude of professional growth. A high
similarity is not "good" and a low similarity is not "bad".

The point is sharpest for the VCS. Consider a teacher whose Acquire reflection
reads "AI generates quizzes" and whose Deepen reflection reads "orchestrating AI
within inquiry-based pedagogy to support student agency". The conceptual growth
is large — yet the vocabulary has changed so much that the cosine similarity
*falls*. Genuine development can produce low similarity. The VCS therefore
measures how much a teacher's thinking about a competency has *shifted or stayed
continuous*; it does not measure how far it has *improved*.

This is consistent with the platform's existing stance: the DTP explainability
panel already states that the signal "describes what changed ... it does not
evaluate whether the change is positive or negative". This subsection makes that
boundary explicit for the redefined instrument. The dissertation write-up must
hold the same line — the DTP reports conceptual continuity and shift, not teacher
quality — and the boundary also constrains the calibration: the human raters in
§7.4 score continuity and shift, never quality.

---

## 5. Non-uniformity — by design

The two signals are not available at every module. The instrument's behaviour by
module type:

| Module type | Modules | VCS | TSS | Rationale |
|---|---|---|---|---|
| First module | M1 | — | — | No same-aspect lower level; no preceding module. |
| Acquire (not first) | M2–M5 | — | available | Base of an aspect column: no lower level exists. A preceding module exists. |
| Deepen / Create | M6–M15 | available | available | A same-aspect lower level and a preceding module both exist. |

This non-uniformity is deliberate and is argued to be a strength:

A teacher genuinely *has* less developmental history at an Acquire module than at
a Deepen or Create module. An instrument that reports a signal only where the
underlying data supports it is reporting the truth about its own evidence base.
An instrument that instead manufactured a uniform-looking signal everywhere would
be presenting a more impressive but less honest surface.

**Rejected alternative — onboarding variables as a vertical baseline.** One way to
give Acquire modules a VCS would be to compare the reflection against a baseline
drawn from onboarding (e.g. the AILST instrument administered at T0, or
`TeacherProfile` fields). This is rejected on **commensurability** grounds. The
VCS is a cosine similarity between two *reflective-text embeddings* — two artefacts
of the same kind and modality. Onboarding data is structured: AILST is a Likert
self-report scale, `TeacherProfile` holds categorical fields. A cosine similarity
between a reflective-text embedding and a Likert score is not a valid comparison;
forcing it would yield a number at Acquire modules that is not the same quantity
as the VCS computed at Deepen/Create modules. That is worse than an honest
absence of signal: it is a fabricated uniformity that masquerades as a single
variable while measuring two incommensurable things. An honest "no signal here"
is defensible; a fabricated incommensurable signal is not.

**Missing comparison reflection.** A signal is also omitted when its comparison
reflection is simply absent — for example a teacher who reached a Deepen module
without a stored reflection at the corresponding Acquire module (an admin bypass,
a data fault, or a module completed before the TAB5 reflection step existed).
This is handled identically to a structurally-absent signal: the lookup returns
nothing, that signal is omitted, and the remaining signal — and the DTP card
itself — renders normally. A missing reflection must never raise an error in the
agent.

---

## 6. Mechanism — what changes and what does not

**Unchanged:**

- the cosine-similarity-of-two-embeddings computation;
- `DTPAgent`'s position in the agent hierarchy — it remains a
  `ResearchInstrumentAgent`;
- the `generate()` entry point and the single-provenance-row contract
  (the composite remains one user-visible artefact, `artefact_kind='dtp_narrative'`);
- the TSS computation — given the sequential rule, the current DTP already
  computes what is here renamed the TSS. For the temporal signal the redefinition
  is, in effect, a relabelling.

**Changed:**

- **Reflection selection.** The single "most recent other module" query is
  replaced by two targeted lookups: (a) the same-aspect lower-level reflection for
  the VCS, (b) the M(N-1) reflection for the TSS. Either lookup may return nothing
  (§5), in which case that signal is omitted.
- **Orchestration.** `DTPAgent._do_generate` runs the embed-and-compare step up to
  twice, once per available signal.
- **Composite output shape.** The `reflection_dtp` JSON gains a second signal
  block. The old single-signal shape is discarded (§7.3).
- **Template.** The TAB5 reflection template renders up to two signal panels
  instead of one.
- **DTP prompt fixtures.** Phase E froze the DTP prompts as Layer-1 fixtures. This
  redefinition intentionally supersedes them. The `dtp.py` docstring already
  anticipated this: it states the methodology constants "must not drift without a
  separate methodology commit". This proposal *is* that separate methodology
  commit.

**Continuity thresholds — out of scope for v1.** The thresholds `0.85` / `0.70`
in the current DTP are undocumented values calibrated for a cross-aspect
comparison. The redefinition does not carry them forward. Per §7.4, the pilot
version of the DTP displays no three-category label, so the redefined DTP ships
with no thresholds to apply at generation time. The agent computes and stores the
raw similarity for each signal; bucketing into a label is a separate post-pilot
analysis step. The distributional difference between the two signals — the VCS is
within-aspect and will run systematically higher than the cross-aspect TSS —
still matters, but only for the post-pilot calibration, where each signal
receives its own thresholds (§7.4).

---

## 7. Open design points and recommendations

### 7.1 Create-level vertical pairing — recommendation: against the Deepen counterpart

A Create module (e.g. M13) has two lower levels in its column (M8 Deepen, M3
Acquire). **Recommendation:** the VCS always compares against the *immediately*
lower level, so M13 is compared against M8. This keeps the VCS a single
consistent rule ("one level down, same aspect") across both Deepen and Create
modules. Comparing M13 against M3 as well (the full Acquire->Create span) would
introduce a third signal; that is rejected to keep the design at two signals.
**Needs sign-off.**

### 7.2 One narrative or two — recommendation: one

**Recommendation:** a single narrative that explicitly references both signals,
with each signal's thematic shifts presented in its own panel above it.
Rationale: a single coherent prose paragraph reads better than two competing
ones; cost stays at one narrative LLM call, as today. The two signals remain
distinct to the teacher because each signal's theme panel is shown separately —
the narrative is synthesis, not the carrier of the distinction.
**Fallback:** if review of generated samples shows that one narrative blurs the
two signals, split into two. Confirmed as the plan; the sample-review check is
carried out during implementation.

**Implementation note — structured prompt.** To stop the single narrative from
blurring the two signals, the `DTPAgent` narrative prompt should require the
model to reason about each signal separately before synthesising. A structured,
tagged response — a `<vertical_analysis>` block, a `<temporal_analysis>` block,
and a final `<synthesis>` block carrying the 60-word narrative — forces that
separation. Only the synthesis block is surfaced to the teacher; the analysis
blocks are a chain-of-thought scaffold. New prompt fixtures are frozen for this
structure (§6, §8).

### 7.3 Old stored DTP data — delete, no migration

Per John: all existing `reflection_dtp` values are test data. The new composite
JSON shape will not be backward compatible, and no migration or compatibility
shim is required. Existing rows may be cleared.

### 7.4 Continuity thresholds and the pilot — resolved

The three-category continuity label requires thresholds on the cosine
similarity. Cosine-similarity thresholds have no theoretically universal value:
they depend on the embedding model, text length, and domain. There is therefore
no theory that supplies the numbers; the only defensible thresholds are ones
*derived from data*.

Two calibration approaches were considered:

- a purely **relative** split — the observed similarity distribution divided into
  equal tertiles. Simple and automatic, but it guarantees that a fixed proportion
  of teachers is always labelled "significant change" regardless of how much they
  actually changed; it reports rank among peers, not absolute development.
- a **criterion-anchored** approach — a sample of reflection pairs is
  independently rated by experienced judges (the researcher, and ideally one or
  two expert teachers) on the degree of conceptual continuity or shift —
  explicitly not on teaching quality (§4.4); the thresholds are then set to best
  reproduce the human ratings. An agreement statistic
  (e.g. Cohen's kappa) between the automated signal and the human raters becomes
  a reportable validity result.

The **criterion-anchored approach is chosen**, because the DTP makes an absolute
claim about an individual teacher's development, which a purely relative split
does not support.

Sequencing. The calibration needs both a body of reflection data and the rating
exercise; the pilot is when that data is produced. The pilot version of the DTP
therefore **shows no continuity label**. It presents only threshold-free
descriptive output (thematic shifts and a descriptive narrative) and stores each
signal's raw similarity. After the pilot, the rating exercise is run, per-signal
thresholds are derived (the VCS and TSS need separate thresholds because their
distributions differ — §6), and the labels are computed retroactively on the
stored similarities for the dissertation analysis.

The dissertation's answer to "why these thresholds" is therefore a *procedural*
one: the thresholds are justified by the documented calibration procedure, not by
any pre-chosen number.

Whether the calibrated label is ever surfaced in the platform UI is left open.
The pilot cohort's role explicitly includes helping shape the system, and the
platform is intended to evolve toward use by a large teacher population. A future
calibrated version may display the label; that is out of scope here and is not a
commitment.

---

## 8. Architectural placement

The change is concentrated in five places:

1. **`apps/modules/views.py` (`extract_dtp_view`)** — reflection selection: two
   targeted lookups in place of one. Each lookup must tolerate a `None` result
   (no matching reflection) and omit only that signal, never raise — see the
   missing-reflection edge case in §5.
2. **`apps/agents/dtp.py` (`DTPAgent`)** — `_do_generate` orchestrates up to two
   comparisons; the composite dict shape changes.
3. **The composite `reflection_dtp` JSON** — gains a second signal block.
4. **The TAB5 reflection template** — renders up to two signal panels and handles
   the non-uniform cases (one signal, no signal).
5. **The DTP prompt fixtures** — superseded; new fixtures frozen for the new
   prompts.

`DTPAgent` remains a `ResearchInstrumentAgent`; no new class is introduced by this
proposal. Provenance remains one row per `generate()` call regardless of whether
one or two narratives are produced, because the composite is a single artefact.

---

## 9. Relationship to D.3 (DTP XAI narrative)

D.3 adds an XAI narrative that explains the DTP. A faithful explanation must be
grounded in exactly the inputs the explained model used (explanation
faithfulness). If the DTP is redefined, an XAI narrative written against the
current DTP would explain an instrument that no longer exists.

Therefore this redefinition is a **prerequisite** to D.3. Proposed sequencing and
naming: **D.3a — DTP Redefinition** (this document) precedes **D.3b — DTP XAI
narrative**. The XAIAgent introduced in D.3b will explain the two-signal DTP and
must see exactly the two reflections each signal compared.

---

## 10. Dissertation coupling

Per John's instruction, the dissertation describes the DTP as deployed at pilot
time, not its development history. Consequences:

- The current DTP design need not be written up as history.
- The existing chapter drafts that describe the current DTP —
  `PROODOS_Architecture_Chapter_DRAFT_v1.md` and
  `PROODOS_Tab5_XAI_HITL_Architecture.md` — must be updated to describe the
  redefined two-signal DTP once it lands. This is part of "done" for D.3a.
- This proposal is itself a new, separate file and serves as a dissertation
  source for the construct-validity argument in §2, the interpretation boundary
  in §4.4, and the non-uniformity argument in §5.

---

## 11. Worked examples

**Teacher at M8 (Aspect 3 — AI Foundations, Deepen).** Both signals available.
VCS compares M8 against M3 (the teacher's Aspect-3 Acquire reflection) — "how has
your thinking about AI Foundations matured from the Acquire to the Deepen level".
TSS compares M8 against M7 — "how much your focus shifted since the previous
module". The teacher sees two descriptive theme panels and one narrative weaving
both; each signal's raw similarity is stored, not shown.

**Teacher at M3 (Aspect 3 — AI Foundations, Acquire).** One signal. M3 is at the
base of its aspect column, so there is no VCS. TSS compares M3 against M2. The
teacher sees one descriptive theme panel (the TSS) and a narrative for it; its
similarity is stored, not shown.

**Teacher at M1 (Aspect 1 — Human-Centred Mindset, Acquire; first module).** No
signal. M1 has no same-aspect lower level and no preceding module. The DTP card is
not rendered; in its place a short message explains that developmental signals
begin once a second reflection exists.

---

## 12. Decisions log

**Confirmed (chat session 2026-05-18):**

- The DTP is redefined into two signals: VCS (within-aspect, one level down) and
  TSS (against M(N-1)).
- The instrument is deliberately non-uniform (§5).
- Onboarding variables are not used as a vertical baseline (commensurability).
- The cosine-similarity mechanism is reused unchanged; only reflection selection
  and output shape change.
- Old stored DTP data is deleted; no migration.
- The dissertation describes the redefined DTP as-is, not its evolution.
- §7.1 — Create modules pair vertically against their Deepen counterpart.
- §9 — track naming: D.3a (this) precedes D.3b (XAI narrative).
- §7.4 — the continuity label is a post-pilot research-analysis artefact. The
  pilot version of the DTP shows no label and ships with no thresholds; it
  presents only descriptive output and stores raw similarities. Thresholds are
  calibrated post-pilot by a criterion-anchored procedure (human ratings of a
  reflection-pair sample). Whether the calibrated label ever appears in the
  platform UI is deliberately left open.
- §7.2 — one narrative is the plan, weaving both signals; the narrative prompt
  uses a structured, tagged format to keep the two signals separate (§7.2).
- §4.4 — interpretation boundary added: the signals measure conceptual
  continuity/shift, not teaching quality.
- §5, §8 — a missing comparison reflection is handled like a structurally-absent
  signal (omit that signal, never raise).
- The vertical signal is renamed Vertical Continuity Signal (VCS); "Development"
  was dropped to avoid implying a quality judgement. TSS is unchanged.

**Remaining to confirm during implementation:**

- §7.2 — verify, on real generated samples, that a single narrative does not blur
  the two signals; split into two only if it does.
