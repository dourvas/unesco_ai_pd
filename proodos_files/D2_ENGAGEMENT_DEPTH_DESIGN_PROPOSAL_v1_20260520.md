# D.2 — Engagement Depth (Position Confirmation Analytics) — Design Proposal v1

*Phase D, sub-track D.2. Drafted 2026-05-20. Companion to the D.1
proposal (`D1_AI_RELEVANCE_PROFILE_DESIGN_PROPOSAL_v1_20260519.md`);
shares the `apps/analytics/` app D.1 created.*

---

## 1. Summary

D.2 turns the Reflective Tension Mapper's positioning telemetry into a
**researcher-facing engagement analytic**. When a teacher works through
the RTM, the platform already records, per tension, whether the teacher
*actively engaged* with that tension or left it at its default. D.2
aggregates that signal into an **Engagement Depth Score (EDS)** — the
proportion of RTM tensions a teacher genuinely positioned — plus a
profile of supporting engagement signals.

The EDS distinguishes **surface engagement** (the teacher completed the
RTM step — clicked the button — without working through the tensions)
from **deep engagement** (the teacher actively positioned themselves).
It is the empirical basis for the dissertation's *"beyond completion
rates"* argument: a teacher can complete a module without engaging with
it, and EDS makes that difference visible.

D.2 is **read-only**: it adds no data collection and changes no teacher
surface. It renders as a new section on the analytics page D.1 created.

---

## 2. Motivation — beyond completion rates

A module's completion status records that the teacher reached the end of
each tab. It says nothing about the *quality* of their participation. A
teacher who opens the RTM card, clicks "Confirm My Positions" without
moving a single slider, and a teacher who works carefully through every
tension both register as having completed the reflection tab.

The platform already holds the signal that separates them — it is simply
never aggregated or surfaced. D.2 surfaces it. This is, in the language
of the engagement literature, a measure of **behavioural engagement** —
effortful participation in a learning task, as distinct from mere
attendance or completion (Fredricks, Blumenfeld & Paris, 2004).

---

## 3. The construct — engagement depth

### 3.1 What `position_confirmed` records
The RTM stores each extracted tension as a `ReflectionTension` row. The
recording mechanism (verified in the TAB5 template + `save_tensions`
view) is:

1. On extraction, the frontend **auto-saves every tension** at
   `selected_position = 3` (the neutral mid-point) with
   `position_confirmed = false`.
2. When the teacher clicks "✓ Confirm My Positions", each tension is
   re-saved with `position_confirmed = true` **only if the teacher
   actually touched that tension's slider**.

So `position_confirmed` is a faithful **per-tension engagement signal**:
it records whether the teacher actively worked a given tension, and it
is independent of *where* they landed (a teacher may touch a slider and
deliberately rest it at the neutral mid-point — that still counts as
engaged).

### 3.2 The Engagement Depth Score
For a teacher, **EDS = confirmed tensions / total tensions presented**.
The denominator is clean: because every extracted tension is auto-saved
as a row, the total is simply the teacher's `ReflectionTension` count.

Unlike D.1's rejected "Trust Calibration Score", EDS as a headline
number does **not** over-claim. "Confirmation rate" is a literal,
transparent proportion — the share of tensions the teacher engaged. It
names exactly what it measures. A headline EDS is therefore acceptable,
reported alongside a profile of supporting signals (§6).

### 3.3 What EDS is NOT
EDS is a **behavioural** engagement indicator, not a cognitive one
(Fredricks et al., 2004, separate the two). Touching a slider is
effortful participation; it is not, on its own, evidence of deep
*thinking*. D.2 measures the behavioural layer honestly and claims
nothing beyond it. EDS is also not a measure of teacher quality or
competence — a low EDS is a fact about engagement with one platform
feature, nothing more.

---

## 4. Researcher-facing only

EDS is shown only to the researcher, in the staff-gated analytics view
D.1 established — never in TAB5 or any teacher-facing surface.

`position_confirmed` is behavioural telemetry rather than a teacher's
explicit rating, but the **measurement-reactivity** argument still
holds. If a teacher could see their EDS, the engagement signal would
become a visible target: a teacher would touch every slider to lift the
number, and the signal would stop measuring genuine engagement
(Paradis & Sutkin, 2017). The score is kept on the researcher side so
the telemetry stays valid.

---

## 5. Input — what D.2 reads

D.2 aggregates the `ReflectionTension` model (`apps/modules/models.py`):

- **`position_confirmed`** (bool) — the primary signal: did the teacher
  engage this tension.
- **`selected_position`** (1–5) — the teacher's positioning; `3` is the
  neutral default.
- **`comment_used`** (bool) / **`optional_comment`** — whether the
  teacher added an optional explanation (a further engagement signal).
- **`time_spent_ms`** (int, nullable) — interaction time on the RTM card.
- **`user`**, **`module`**, **`tension_label`**, **`created_at`**.

Existing indexes on `user`, `module`, `selected_position`, `created_at`
cover the aggregations. No schema change, no migration.

---

## 6. Output — EDS headline + supporting profile

D.2 reports, per teacher and across the cohort:

**6.1 The headline EDS** — confirmed / total tensions, as a proportion.

**6.2 A supporting engagement profile:**
- **comment-use rate** — share of tensions with an optional comment;
- **interaction time** — median `time_spent_ms` where recorded;
- **non-neutral rate** — among *confirmed* tensions, the share placed
  off the neutral mid-point (`selected_position != 3`) — a teacher who
  engages and takes a definite stance, vs one who engages but stays
  neutral.

**6.3 Slices** — EDS by module and by subject area, so the researcher
can see whether engagement depth varies across the programme or across
teaching contexts.

The headline number and the profile are reported together so that EDS
is always read in context — a low EDS with high comment use, or with
long interaction times, tells a different story than a low EDS across
the board.

---

## 7. Design decisions

*Decisions confirmed in the chat session of 2026-05-20.*

### 7.1 EDS form — a headline rate plus a profile
EDS is reported as a headline confirmation rate (§3.2) with a supporting
profile (§6.2). The headline is admissible here, unlike in D.1, because
"confirmation rate" is a literal proportion with no construct over-claim.

### 7.2 Researcher-facing, staff-gated
EDS appears only behind the existing staff gate (§4).

### 7.3 A section on the unified analytics page
D.2 is rendered as a new section on the analytics page D.1 created, not
as a separate page. The page becomes the platform's single
researcher-facing analytics surface, with two sections: the AI Output
Relevance Profile (D.1) and Engagement Depth (D.2). The page title and
route are generalised accordingly (§12 — minor open point).

### 7.4 Read-only — no change to data collection
D.2 adds no model, no migration, no teacher-facing change. Like D.1, it
is a pure read-side aggregation over data the platform already records.

---

## 8. Mechanism and architectural placement

D.2 extends the existing `apps/analytics/` app — no new app.

1. **`apps/analytics/services.py`** — new aggregation functions:
   `cohort_engagement_depth()` and `per_teacher_engagement_depth()`,
   pure ORM aggregation over `ReflectionTension`.
2. **`apps/analytics/views.py`** — the existing analytics view is
   extended to add the engagement-depth context (one unified page).
3. **`templates/analytics/`** — the analytics template gains an
   "Engagement Depth" section below the relevance-profile sections.
4. **`apps/analytics/tests.py`** — aggregation-correctness tests for
   the EDS functions.

No `ReflectionTension` change, no migration.

---

## 9. Methodological caveats (for the dissertation)

- **Behavioural, not cognitive.** EDS measures slider engagement, a
  behavioural proxy. It does not measure the depth of the teacher's
  thinking (§3.3).
- **Small denominators.** A teacher whose reflection yielded few
  tensions has an EDS over a small base; report N alongside the rate.
- **Telemetry edge cases.** `time_spent_ms` is frontend-reported and
  nullable; treat it as indicative, not exact. A confirmed tension may
  still rest on the neutral mid-point — that is engagement, not
  indecision, and §6.2's non-neutral rate is reported separately rather
  than folded into EDS.
- **No RTM, no row.** If a teacher's reflection produced no tensions,
  they contribute no engagement data; this is reported as missing, not
  as zero engagement.

---

## 10. Dissertation coupling

- D.2 fills the **§5.6 placeholder** of
  `PROODOS_Architecture_Chapter_DRAFT_v1.md` (Position Confirmation
  Analytics).
- It is the empirical basis for the dissertation's *"beyond completion
  rates"* section: completion and engagement are distinct, and EDS
  quantifies the gap.
- The behavioural-engagement construct (Fredricks et al., 2004) is the
  theoretical anchor; the architecture chapter's §2 theory section can
  reference it.

---

## 11. Bibliography

Verified 2026-05-20; to be folded into
`Literature_Review_Synthesis_Note(1).md`.

- **Fredricks, J.A., Blumenfeld, P.C. & Paris, A.H. (2004).** School
  engagement: Potential of the concept, state of the evidence.
  *Review of Educational Research*, 74(1), 59–109. — the canonical
  engagement framework; behavioural / emotional / cognitive engagement.
  Behavioural engagement (effortful participation, distinct from mere
  completion) is the EDS construct.
- **Paradis, E. & Sutkin, G. (2017).** Beyond a good story: from
  Hawthorne Effect to reactivity in health professions education
  research. *Medical Education*, 51, 31–39. — measurement reactivity;
  grounds the researcher-facing-only decision (§4). Carried over from
  the D.1 proposal.

---

## 12. Open points (for sign-off)

- **Analytics page route / title.** With D.2 added, the page is no
  longer only "AI Output Relevance Profile". Proposed: retitle it
  "PROODOS Research Analytics" and (optionally) move the route from
  `/analytics/ai-relevance/` to `/analytics/`, updating the navbar
  link. Low-stakes; can also be left as-is.
- **Non-neutral rate.** Confirm §6.2's "non-neutral rate" is wanted, or
  drop it for a leaner first version.
- **Presentation detail.** Tables vs light bars for the EDS section
  (consistent with the D.1 section).

---

## 13. Decisions log

**Confirmed (chat session 2026-05-20):**

- D.2 is Engagement Depth — a researcher-facing analytic over the RTM
  `position_confirmed` telemetry.
- EDS = confirmation rate (headline) + a supporting engagement profile
  (§6).
- Researcher-facing only — staff-gated, on measurement-reactivity
  grounds (§4).
- Rendered as a section on the unified analytics page (not a separate
  page).
- Read-only: no model, no migration, no change to data collection.
- Built on `ReflectionTension`; lives in the existing `apps/analytics/`
  app.

**Proposed — pending sign-off (§12):**

- Analytics page retitle / route generalisation.
- Whether to include the non-neutral rate.
- Presentation detail.
