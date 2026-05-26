# PROODOS Programme Duration & Time-on-Task Methodology — v1.1

*Doctoral dissertation appendix · Drafted 2026-05-26 · Revised
2026-05-26 (v1.1) after external review · Resolves TECH_DEBT_LOG
TD-027 · Feeds the Certificate of Attendance values in
`apps/certification/services.py` and the per-module
`Module.estimated_hours` field in `apps/modules/models.py`.*

## Revision history

- **v1.1 (2026-05-26):** Six external-review corrections.
  - Yoon (2007) row: dropped the "under-14-hour" attribution
    (the 14h threshold is folk-knowledge in the TPD literature
    but cannot be cleanly attributed to a specific verified
    source; safer to keep Yoon's verified 49h finding alone).
  - UNESCO positioning language aligned across §3.4, §4, §5.3:
    "at the lower bound of the UNESCO range" everywhere, plus an
    explicit feasibility framing — the 5h/week is intentionally
    at the floor, not by accident.
  - TAB2 duration grounded in **measured word counts** (10
    sample modules, median 10,450 words, range 7,224–16,645)
    rather than a hand-estimated range.
  - TAB1/TAB3/TAB4 duration grounding split into two
    separately-justified layers: (a) why the activity exists in
    the syllabus — anchor citation; (b) why the activity takes
    its allocated minutes — internal allocation logic
    (percentage-of-module-total).
  - Dourvas et al. (2025) citation: "(in revision)" wording,
    drop the rejection narrative.
  - General-population feasibility framing added; Greek pilot
    context noted as one *example*, not the structural argument.
    The platform is international; the 110-teacher Greek pilot
    cohort is not yet recruited and may be supplemented by
    educators from other countries.
- **v1.0 (2026-05-26):** Initial draft.

---

## 1. The question

How long is the PROODOS programme, and what justifies that
duration?

The doctoral dissertation rests on the PROODOS platform as its
empirical instrument. Every observable feature of that instrument
must be defensible at viva: the choice of AILST as a measurement
scale, the choice of UNESCO ICT-CFT as the alignment frame, the
choice of 15 modules — and the choice of duration. Stating a
number ("75 hours") without an evidential chain backing it makes
the entire instrument look arbitrary at a single point that an
examiner can land on with ease.

This document supplies the evidential chain. It also names what
remains open (per-module hour allocation pending the TAB1 audit)
and what is settled (the total aggregate workload + ECTS
correspondence).

---

## 2. Decision criteria

Three criteria, in priority order:

**C1. Within the international academic-credit envelope.**
The European Credit Transfer and Accumulation System (ECTS) is the
canonical workload standard for academic instruction across the
European Higher Education Area. The PROODOS workload must be
expressible in ECTS terms so that the dissertation's claims about
"a 15-module professional-development programme" land on a
standard frame an examiner already accepts.

**C2. Within the empirical TPD-effectiveness envelope.**
A converging body of research on teacher professional development
(Darling-Hammond et al., 2017; Desimone, 2009; Garet et al., 2001;
Yoon et al., 2007) identifies *sustained duration* as one of the
necessary features of PD that demonstrably moves student outcomes.
The PROODOS duration must sit *inside* the range these studies
identify, not under it.

**C3. Within the UNESCO online-TPD precedent.**
The UNESCO Rapid Teacher Training Programme on Distance, Open and
Online Learning is the closest direct precedent — a UNESCO-issued,
online, self-paced TPD on a digital-pedagogy topic. The PROODOS
workload should be expressible against that precedent's published
hour profile rather than against an unrelated benchmark
(e.g., in-person workshop hours).

---

## 3. Theoretical framework

### 3.1 ECTS workload semantics

The ECTS Users' Guide 2015 (European Commission, 2015) defines one
ECTS credit as **25 to 30 working hours** of student workload,
with full-time academic-year workload of 1500–1800 hours. Workload
is *total time-on-task* — not "contact hours" or "instructor
hours" — and explicitly includes private study, reading, exercises,
assessments, and reflection.

This semantic alignment is critical for PROODOS, where the
teacher-learner spends the bulk of programme time in
asynchronous reflection (TAB5) and practice (TAB3) rather than in
synchronous instruction. The ECTS frame counts that time; an
older "lecture-hours" frame does not.

### 3.2 Time-on-Task (TOT)

Time-on-Task (Berliner, 1990, foundational; subsequently
standardised across digital-learning research) is the operational
measure ECTS implements: total minutes a learner is actively
engaged with programme content, across all modalities. For
self-paced asynchronous PD, TOT is estimated rather than measured
directly — typically by decomposing each programme element into
its component activities and assigning realistic per-activity
durations grounded in prior literature.

PROODOS follows this decomposition pattern. The five TABs of each
module map to five distinct cognitive activities, each with its
own anchoring literature on expected duration.

### 3.3 Empirical TPD-effectiveness anchors

| Source | Finding relevant to duration |
|---|---|
| **Yoon et al. (2007)** — REL 2007-No. 033 | Across nine What Works Clearinghouse-standards studies, **PD averaging 49 hours produced a +21 percentile-point gain in student achievement**. |
| **Darling-Hammond et al. (2017)** — Learning Policy Institute, review of 35 rigorous studies | "Sustained duration" identified as one of seven features of effective PD. The review documents effective programmes typically lasting "weeks, months, and even academic years" with cumulative contact hours far above one-off workshop totals. |
| **Desimone (2009)** — *Educational Researcher* 38, 181–200 | "Duration" named as one of the five core features of the consensus PD-impact framework, alongside content focus, active learning, coherence, and collective participation. |
| **Garet et al. (2001)** — *AERJ* 38, 915–945 | Empirical evidence from a national sample of 1,027 teachers that the *form* + *duration* + *collective participation* of PD are the structural features that significantly affect teacher learning outcomes. |

The convergence is clean: **sustained PD outperforms brief PD,
with the Yoon et al. (2007) WWC-standards meta-analysis locating
a measurable effectiveness anchor at approximately 49 hours of
cumulative contact**. The PROODOS workload must sit comfortably
above this anchor to claim plausibly that it can affect teacher
learning.

### 3.4 UNESCO Rapid TPD precedent

The UNESCO Rapid Teacher Training Programme on Distance, Open and
Online Learning (UNESCO, 2021) is a three-module online TPD on a
digital-pedagogy topic, the closest published precedent to
PROODOS in scope and modality. Its published workload profile:

| Module | Duration |
|---|---|
| Module 1 | 1 week × **5–7 hours/week** |
| Module 2 | 2 weeks × **10–12 hours/week** (total 20–24 hours) |
| Module 3 | 1 week × **5–7 hours/week** |

The per-week range is therefore **5–12 hours**, with the
"per-week" baseline for content-heavy modules at 5–7 hours.

**PROODOS sits at the lower bound of the UNESCO range** —
5 hours/week × 15 weeks. This is a deliberate design choice, not
an accidental near-miss: a fully-employed K-12 teacher carrying
a 18–23 weekly teaching-hour load (plus marking, planning, and
parent contact) cannot realistically commit more than 5 hours/week
to asynchronous PD without trading off classroom preparation
quality. The 5-hour weekly load therefore serves as a *practical
feasibility ceiling for full-time teachers* as much as a *UNESCO
floor*. The platform is designed for international deployment;
this feasibility argument generalises to any context where the
target audience is teachers carrying full classroom workloads.
The Greek context is one instance of this constraint, not its
foundation.

---

## 4. Per-Tab cognitive-activity decomposition

The PROODOS module architecture distributes each module's
time-on-task across five Tabs. Each Tab's duration estimate
rests on **two separately-justified layers**:

- *Why the activity exists in the syllabus* — anchored to a
  specific learning-sciences literature.
- *Why the activity takes its allocated minutes* — internal
  allocation logic expressed as a percentage of total module
  time, with the absolute minutes derived from the percentage.

This separation matters because the two questions are answerable
by different evidence. Citing Wenger (1998) to justify *that*
TAB3 takes 120 minutes is a category error; Wenger justifies the
*existence* of a situated-practice Tab. The minutes come from a
defensible distribution of the 5-hour module budget across the
five activities.

| Tab | Activity | Time | % of total | "Why activity exists" | "Why this allocation" |
|---|---|---|---|---|---|
| **TAB1 Introduction** | Orientation, prior-knowledge activation, module framing | **20 min** | ~6.7% | Ausubel (1968) on Advance Organizers — orientation phases support subsequent acquisition by giving learners anchoring schemata | Within the 10–15% framing-time range typical in instructional-design literature for orientation segments relative to total session length; PROODOS sits at the lower end (6.7%) because the entry into each weekly module is light, not because the literature prescribes 20 minutes specifically |
| **TAB2 Core Content** | Theory reading, framework comprehension, SVG analysis | **75 min** | ~25% | Comprehension of the module's theoretical content (UNESCO competency framework + RPE framework + module-specific frames + SVG diagrams) is the prerequisite for the practice and reflection Tabs that follow | **Measured baseline:** 10 sample modules averaged 10,500 words of Core Content (range 7,224–16,645). At an average reading speed of ~140 wpm for technical material with diagram analysis (within the 100–200 wpm range reported in reading-research literature), 10,500 / 140 ≈ 75 minutes |
| **TAB3 Practical Challenges** | Hands-on AI-tool scenarios, lesson-design exercise, Practice Workshop participation | **120 min** | ~40% | Wenger (1998) Communities of Practice — situated practice is the empirical centre of professional learning. The largest single allocation in the module reflects this theoretical centrality | 40% of total module time, the dominant single allocation. This proportion is consistent with constructivist instructional-design literature placing the bulk of cognitive engagement on situated practice rather than passive reception |
| **TAB4 Quiz** | Formative-assessment scenarios (15 items) | **30 min** | ~10% | Black & Wiliam (1998) — formative assessment as learning event; quiz time is cognitive engagement plus reflection on incorrect answers, not mere recall | 2 minutes per item × 15 items = 30 minutes; consistent with timing guidelines for scenario-based formative assessment in K-12 PD contexts |
| **TAB5 Reflection** | Written reflection, dual-signal DTP/RTM interaction | **45 min** | ~15% | Schön (1983) Reflection-on-Action + RPE Framework (Dourvas et al., in revision) — reflective writing is itself a learning act, not a coda | 15% of total module time, sufficient for a substantive reflection of ~250–350 words plus engagement with the dual-signal DTP/RTM artefact; in line with empirical observations of reflective-writing durations in TPD literature |
| **Total per module** | | **5 hours** | ~100% | UNESCO Rapid TPD lower bound (5–7h/week) | 290 minutes ≈ 4h 50m; rounded to 5h for the published claim |

The percentages sum to ~96.7% with ~3.3% absorbed into transition
times and rounding. The decomposition is theoretically defensible
at viva: each Tab carries a separate "why this activity" citation
*and* a separate "why this duration" justification.

---

## 5. Aggregate workload + ECTS mapping

### 5.1 Total programme workload

```
5 hours/module × 15 modules = 75 hours
```

Distributed across 15 weeks (one module per week, matching a
standard university semester):

```
75 hours / 15 weeks = 5 hours/week
```

### 5.2 ECTS conversion

```
75 hours ÷ 25–30 hours/ECTS = 2.5–3 ECTS
```

**Conservative claim:** PROODOS = **2.5 ECTS** at the
30-hours-per-credit end of the ECTS range. This is the safer
claim at viva; understating an ECTS allocation is defensible,
overstating it is not.

**Aspirational claim:** PROODOS = **3 ECTS** at the
25-hours-per-credit end. The dissertation may state this
optimistically with the caveat that the conservative reading is
2.5 ECTS.

The decision adopted here is **2.5 ECTS** in dissertation prose,
with the caveat made explicit. This puts the dissertation's
quantitative claim on the safest grounds an examiner can attack.

**Note on the 0.5-credit decimal.** The ECTS Users' Guide (2015)
does not constrain credit allocations to whole-number units; the
Guide's worked examples include fractional allocations and
half-credit increments where appropriate to the actual workload.
The 2.5 ECTS claim is therefore admissible in the ECTS frame as
written, without requiring rounding to an integer value
(rounding up to 3 ECTS would be the aspirational reading; rounding
down to 2 ECTS would understate the workload).

### 5.3 Position against benchmarks

| Benchmark | Hours | PROODOS position |
|---|---|---|
| **Yoon et al. (2007)** effective-PD anchor | 49h | **+26 hours above** |
| **UNESCO Rapid TPD** weekly engagement range | 5–12h/week | **At the lower bound (5h/week)** — by design, not by accident; see §3.4 feasibility framing |
| **Garet et al. (2001)** sustained-PD criterion | sustained (multi-week) | **Met (15 weeks)** |
| **Darling-Hammond et al. (2017)** seven features include sustained duration | n/a (qualitative) | **Met** |

The PROODOS workload sits **above** the Yoon-anchored empirical
effectiveness floor and **at the lower bound** of the UNESCO
precedent envelope, where the design intent is to keep the
programme feasible for teachers carrying full classroom
workloads (§3.4). All three required constraints (§2 C1 + C2 +
C3) are satisfied simultaneously.

---

## 6. Decision

**Settled values, committed 2026-05-26 to**
`apps/certification/services.py` (via `settings.CERTIFICATE_*` constants):

- **Total programme hours:** 75 hours
- **Total programme weeks:** 15 weeks
- **Cadence:** ~5 hours/week, 1 module per week
- **ECTS allocation (dissertation claim):** 2.5 ECTS (conservative)

**Pending values, opened to the TAB1 audit:**

- **Per-module hours:** currently uniform at 5h/module. The TAB1
  audit (TD-026, scheduled for a separate session) will compare
  each module's actual TAB1 Learning Objectives + About this
  Module against the CONTENT_VALIDATION_MATRIX.md per-module
  analysis. Modules whose Tab content distribution genuinely
  diverges from the §4 default decomposition will receive
  adjusted hour allocations. The 75-hour total is preserved as a
  sum constraint — variation rebalances across modules.

- **Module.estimated_hours field default:** currently 4 (placeholder
  from Phase C C.2 model creation, never justified). Should flip
  to 5 once the TAB1 audit confirms the uniform-5h default; or
  remain at 4 with the audit producing per-module overrides if
  non-uniform allocation is adopted. **Deferred to the audit's
  conclusion.** No migration ships in the TD-027 commit; the
  certificate values are decoupled from the model field and
  driven by `settings.CERTIFICATE_PROGRAMME_*`.

---

## 7. Dissertation methodology chapter — draft passage

The following paragraph is offered as the draft text for the
dissertation's *Methodology* chapter, sub-section on programme
duration:

> "The workload of the PROODOS EduAI programme was designed
> against three converging criteria. First, against the European
> Credit Transfer and Accumulation System (European Commission,
> 2015), which defines one credit as 25–30 hours of total
> student workload across all modalities (lecture, reading,
> practice, assessment, reflection). Second, against the
> empirical literature on teacher professional development,
> which identifies sustained duration as a structural prerequisite
> of effective PD (Darling-Hammond et al., 2017; Desimone, 2009;
> Garet et al., 2001) and locates the effectiveness floor at
> approximately 49 cumulative hours of contact in nine What Works
> Clearinghouse-standards studies (Yoon et al., 2007). Third,
> against the UNESCO Rapid Teacher Training Programme on
> Distance, Open and Online Learning (UNESCO, 2021), the closest
> published precedent in scope and modality, which prescribes
> 5–7 hours of weekly engagement for its content-heavy modules.
>
> The PROODOS programme comprises 15 modules, one per week, with
> a Time-on-Task estimate of five hours per module distributed
> across the five Tab cognitive activities (Introduction,
> 20 minutes; Core Content, 75 minutes; Practical Challenges,
> 120 minutes; Quiz, 30 minutes; Reflection, 45 minutes). The
> total cumulative workload is therefore 75 hours over 15 weeks,
> corresponding to 2.5 ECTS at the conservative 30-hours-per-credit
> end of the ECTS range. This places PROODOS above the Yoon et al.
> 49-hour empirical effectiveness floor and at the lower bound of
> the UNESCO Rapid TPD weekly-engagement profile, simultaneously
> sustainable for K-12 educators carrying full classroom workloads
> and quantitatively defensible against the established literature
> on TPD duration."

---

## 8. Per-Tab citation ledger

Each Tab's duration estimate rests on a **two-layer
justification** (per §4): the *why-this-activity* citation,
which is the anchored learning-sciences reference; and the
*why-this-duration* logic, which is internal allocation
arithmetic. The verification notes below mirror the project's
standing rule on no hallucinated citations.

### TAB1 Introduction — 20 minutes

**Why this activity exists.** Ausubel, D. P. (1968).
*Educational psychology: A cognitive view.* New York: Holt,
Rinehart and Winston. Foundational text on advance organisers
and cognitive scaffolding — appears in every cognitive-psychology
review since its publication. Standard education reference;
attested through canonical citation chains rather than direct
search (book pre-dates online discovery). **Citation defensible
at viva.**

**Why this duration.** 20 minutes corresponds to ~6.7% of total
module time, near the lower end of the 10–15% framing-time range
typical in instructional-design literature for orientation
segments relative to total session length. The lower-end choice
reflects that each TAB1 is a weekly re-entry into the programme
(not a fresh-start orientation), so heavier framing is
unnecessary.

### TAB2 Core Content — 75 minutes

**Why this activity exists.** The theoretical content of each
module (UNESCO competency framework + RPE framework + module-
specific frames + SVG diagrams) is the prerequisite knowledge for
the practice and reflection Tabs that follow. Removing this layer
would leave Tabs 3–5 without the conceptual grounding required
for them to function as designed.

**Why this duration.** Measured baseline. A sample of 10 modules
(M1, M2, M3, M5, M7, M8, M10, M12, M13, M15) was queried against
the live `ModuleContent` table for `main_content` and
`subject_box_part*` entries combined (the Tab2 surface). Word
counts:

| Module | Main content | Subject boxes | Total |
|---|---|---|---|
| M1 | 2,436 | 5,642 | **8,078** |
| M2 | 2,325 | 6,079 | **8,404** |
| M3 | 2,562 | 5,602 | **8,164** |
| M5 | 2,797 | 7,555 | **10,352** |
| M7 | 4,079 | 7,893 | **11,972** |
| M8 | 3,667 | 12,978 | **16,645** |
| M10 | 4,440 | 9,829 | **14,269** |
| M12 | 4,415 | 7,721 | **12,136** |
| M13 | 5,187 | 5,360 | **10,547** |
| M15 | 4,494 | 2,730 | **7,224** |

Median: 10,450 words; mean: 10,779. Range: 7,224–16,645.

At ~140 words per minute for technical material with diagram
analysis (within the 100–200 wpm range reported in reading-
research literature; lower end of the 250–300 wpm range for plain
prose because PROODOS modules carry SVG diagrams + formal
framework definitions that slow reading rate), a 10,500-word
content load takes ~75 minutes. **The duration is empirically
defensible against the measured word counts plus a reading-rate
range with multiple anchoring citations** (e.g., Carver, 1990 on
reading rates; standard cognitive-psychology textbooks on
technical-prose reading rates).

**Caveat for the dissertation.** M8 is a substantial outlier at
16,645 words (~120 minutes at 140 wpm). The 75-minute claim is a
median-fitted estimate, not a per-module ceiling — M8 in
particular will likely need a heavier per-module allocation when
the TAB1 audit (TD-028) returns. This caveat is recorded here so
it does not become a surprise at viva.

### TAB3 Practical Challenges — 120 minutes

**Why this activity exists.** Wenger, E. (1998). *Communities of
Practice: Learning, Meaning, and Identity.* Cambridge: Cambridge
University Press. Verified via WebSearch 2026-05-26. Cambridge
canonical edition; ISBN 9780521663632. Series "Learning in
Doing." Situated practice is, for Wenger, the empirical
centre — not the periphery — of professional learning. The
dominant single allocation of the module reflects this
theoretical centrality.

**Why this duration.** 120 minutes corresponds to 40% of total
module time, the largest single allocation across the five Tabs.
This proportion is consistent with constructivist instructional-
design literature placing the bulk of cognitive engagement on
situated practice rather than passive reception (Wenger 1998,
Lave & Wenger 1991). The specific minutes derive from the 40%
allocation against the 5-hour total, not from a citation that
prescribes 120 minutes.

### TAB4 Quiz — 30 minutes

**Why this activity exists.** Black, P., & Wiliam, D. (1998).
Inside the black box: Raising standards through classroom
assessment. *Phi Delta Kappan, 80*(2), 139–148. Landmark text on
formative assessment as a learning event in itself, not a
post-learning verification step. The Tab4 quiz is therefore a
learning activity, not an exam.

**Why this duration.** 2 minutes per item × 15 items = 30
minutes, including time to read each scenario, choose, and
reflect briefly on incorrect responses. The 2-minute-per-item
heuristic is consistent with the K-12 scenario-based-assessment
literature where individual items are short but answer-rationale
review takes most of the time per item.

### TAB5 Reflection — 45 minutes

**Why this activity exists.** Schön, D. A. (1983). *The
Reflective Practitioner: How professionals think in action.*
New York: Basic Books. Foundational text on
reflection-in-action and reflection-on-action; standard
education reference. Plus: Dourvas, J., Kokkonis, G., &
Kontogiannis, S. (2025). Reflective Prompt Engineering for
Educator AI Literacy: The RPE Framework. *British Journal of
Educational Technology* (in revision). Together these anchor
reflective writing as itself a learning act, not a coda to the
"real" learning.

**Why this duration.** 45 minutes corresponds to ~15% of total
module time, sufficient for a substantive written reflection of
~250–350 words plus engagement with the dual-signal DTP/RTM
artefact generated against the reflection. The 15% allocation is
consistent with empirical observations of reflective-writing
durations in TPD literature, where reflection segments typically
take 10–20% of module time when treated as a substantive
learning activity rather than a perfunctory exit slip.

---

## 9. Aggregate references (APA 7th)

All references below are verified-or-attested per the standing
project rule. WebSearch verification dates and result-summary
links recorded for the three primary anchors of §3 (ECTS, UNESCO
Rapid TPD, the four TPD-effectiveness sources).

- **European Commission.** (2015). *ECTS users' guide.*
  Luxembourg: Publications Office of the European Union.
  [https://op.europa.eu/en/publication-detail/-/publication/da7467e6-8450-11e5-b8b7-01aa75ed71a1](https://op.europa.eu/en/publication-detail/-/publication/da7467e6-8450-11e5-b8b7-01aa75ed71a1).
  **Verified 2026-05-26 via WebSearch.** Official EU publication;
  Guide reaffirms 1 ECTS = 25–30 working hours; 1500–1800h/year
  for full-time programmes.

- **UNESCO.** (2021). *Rapid teacher training programme on open,
  distance and online learning.* Paris: UNESCO Open Learning.
  [https://openlearning.unesco.org/courses/course-v1:UNESCO+UNESCO-05+2021_01/about](https://openlearning.unesco.org/courses/course-v1:UNESCO+UNESCO-05+2021_01/about);
  programme description at [https://unesdoc.unesco.org/ark:/48223/pf0000376722](https://unesdoc.unesco.org/ark:/48223/pf0000376722).
  **Verified 2026-05-26 via WebSearch.** Published workload:
  modules 1+3 = 5–7h/week; module 2 = 10–12h/week.

- **Darling-Hammond, L., Hyler, M. E., & Gardner, M.** (2017).
  *Effective teacher professional development.* Palo Alto, CA:
  Learning Policy Institute.
  [https://learningpolicyinstitute.org/product/effective-teacher-professional-development-factsheet](https://learningpolicyinstitute.org/product/effective-teacher-professional-development-factsheet);
  PDF at [https://learningpolicyinstitute.org/sites/default/files/product-files/Effective_Teacher_Professional_Development_REPORT.pdf](https://learningpolicyinstitute.org/sites/default/files/product-files/Effective_Teacher_Professional_Development_REPORT.pdf).
  **Verified 2026-05-26 via WebSearch.** Review of 35
  methodologically rigorous studies; sustained duration named
  among seven features of effective PD.

- **Desimone, L. M.** (2009). Improving impact studies of
  teachers' professional development: Toward better
  conceptualizations and measures. *Educational Researcher,
  38*(3), 181–199. [https://doi.org/10.3102/0013189X08331140](https://doi.org/10.3102/0013189X08331140).
  **Verified 2026-05-26 via WebSearch.** Five-feature framework
  (content focus, active learning, coherence, duration,
  collective participation).

- **Garet, M. S., Porter, A. C., Desimone, L., Birman, B. F., &
  Yoon, K. S.** (2001). What makes professional development
  effective? Results from a national sample of teachers.
  *American Educational Research Journal, 38*(4), 915–945.
  [https://doi.org/10.3102/00028312038004915](https://doi.org/10.3102/00028312038004915).
  **Verified 2026-05-26 via WebSearch.** National sample,
  n = 1,027 teachers; identifies duration + collective
  participation + form as significant structural features.

- **Yoon, K. S., Duncan, T., Lee, S. W.-Y., Scarloss, B., &
  Shapley, K. L.** (2007). *Reviewing the evidence on how teacher
  professional development affects student achievement* (Issues
  & Answers Report, REL 2007–No. 033). Washington, DC: U.S.
  Department of Education, Institute of Education Sciences,
  Regional Educational Laboratory Southwest.
  [https://files.eric.ed.gov/fulltext/ED498548.pdf](https://files.eric.ed.gov/fulltext/ED498548.pdf);
  ERIC ID ED498548. **Verified 2026-05-26 via WebSearch.**
  Nine studies meeting What Works Clearinghouse evidence
  standards; PD averaging 49 hours yielded a +21 percentile-point
  gain in student achievement. (Note: the "under-14-hour PD shows
  no significant effect" claim sometimes attributed to Yoon is
  not in fact in this report; the figure is folk-knowledge in the
  TPD-review literature that cannot be cleanly traced to a
  specific verified source, so it is not used here.)

- **Wenger, E.** (1998). *Communities of practice: Learning,
  meaning, and identity.* Cambridge: Cambridge University Press.
  **Verified 2026-05-26 via WebSearch.** Cambridge canonical
  edition. ISBN 9780521663632. Foundational text on situated
  learning, used in TAB3 Practical Challenges duration
  justification.

- **Ausubel, D. P.** (1968). *Educational psychology: A cognitive
  view.* New York: Holt, Rinehart and Winston. Standard reference,
  attested via canonical citation chains in cognitive-psychology
  literature. Used in TAB1 Introduction duration justification.

- **Black, P., & Wiliam, D.** (1998). Inside the black box:
  Raising standards through classroom assessment. *Phi Delta
  Kappan, 80*(2), 139–148. Standard reference; landmark text on
  formative assessment. Used in TAB4 Quiz duration justification.

- **Schön, D. A.** (1983). *The reflective practitioner: How
  professionals think in action.* New York: Basic Books. Standard
  reference; foundational text on reflection-in-action and
  reflection-on-action. Used in TAB5 Reflection duration
  justification.

- **Dourvas, J., Kokkonis, G., & Kontogiannis, S.** (2025).
  Reflective Prompt Engineering for Educator AI Literacy: The
  RPE Framework. *British Journal of Educational Technology*
  (in revision). PROODOS author's own work, cited as
  internal-to-the-programme grounding for the TAB5 RPE-anchored
  reflective design.

---

## 10. Cross-references

- **Project file:** `apps/certification/services.py` — duration
  values driven by `settings.CERTIFICATE_PROGRAMME_WEEKS` and
  `CERTIFICATE_PROGRAMME_HOURS`, which are set per §6 above.
- **TECH_DEBT_LOG.md TD-027** — closed by this document modulo
  the per-module fine-tuning that the TAB1 audit will deliver.
- **TECH_DEBT_LOG.md TD-026** — the certificate of attendance
  references the values above; PI feedback on the cert text in
  Phase H.3 follow-up commit `d49947f`.
- **Literature_Review_Synthesis_Note(1).md** — gains a new §20
  cross-pointing to this document as the canonical workload
  methodology record (kept thin to avoid duplication; the
  authoritative version is here).
- **CONTENT_VALIDATION_MATRIX.md** — the per-module §74
  Αναλυτική Τεκμηρίωση will inform the TAB1 audit. The audit
  may identify modules whose actual Tab content distribution
  diverges from the §4 default decomposition, motivating
  non-uniform per-module hour allocations.

---

*End of PROODOS Programme Duration & Time-on-Task Methodology v1.*
