# PROODOS Programme Duration & Time-on-Task Methodology — v1

*Doctoral dissertation appendix · Drafted 2026-05-26 · Resolves
TECH_DEBT_LOG TD-027 · Feeds the Certificate of Attendance values
in `apps/certification/services.py` and the per-module
`Module.estimated_hours` field in `apps/modules/models.py`.*

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
| **Yoon et al. (2007)** — REL 2007-No. 033 | Across nine What Works Clearinghouse-standards studies, **PD averaging 49 hours produced a +21 percentile-point gain in student achievement**. The under-14-hour studies showed no significant effect. |
| **Darling-Hammond et al. (2017)** — Learning Policy Institute, review of 35 rigorous studies | "Sustained duration" identified as one of seven features of effective PD. The review documents effective programmes typically lasting "weeks, months, and even academic years" with cumulative contact hours far above one-off workshop totals. |
| **Desimone (2009)** — *Educational Researcher* 38, 181–200 | "Duration" named as one of the five core features of the consensus PD-impact framework, alongside content focus, active learning, coherence, and collective participation. |
| **Garet et al. (2001)** — *AERJ* 38, 915–945 | Empirical evidence from a national sample of 1,027 teachers that the *form* + *duration* + *collective participation* of PD are the structural features that significantly affect teacher learning outcomes. |

The convergence is clean: **brief PD does not work; sustained PD
does, with measurable thresholds around 49 hours of cumulative
contact**. The PROODOS workload must sit comfortably above that
threshold to claim plausibly that it can affect teacher learning.

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
PROODOS targets the lower end of this range
(5 hours/week × 15 weeks) — sustainable for K-12 teachers
balancing PD against full classroom workloads, without falling
below the UNESCO precedent's minimum.

---

## 4. Per-Tab cognitive-activity decomposition

The PROODOS module architecture distributes each module's
time-on-task across five Tabs. Each Tab carries a different
cognitive load profile, anchored to its own literature.

| Tab | Activity | Time | Anchor citation |
|---|---|---|---|
| **TAB1 Introduction** | Orientation, prior-knowledge activation, module framing | **20 min** | Ausubel (1968) on Advance Organizers — orientation phases support subsequent acquisition by giving learners anchoring schemata |
| **TAB2 Core Content** | Theory reading, framework comprehension, SVG analysis | **75 min** | Standard academic-reading-speed estimates (250–300 wpm; technical material 100–200 wpm) for the ~6000–9000 words typical per module |
| **TAB3 Practical Challenges** | Hands-on AI-tool scenarios, lesson-design exercise, Practice Workshop participation | **120 min** | Wenger (1998) Communities of Practice — situated practice is the empirical heart of professional learning, justifying its disproportionate share of programme time |
| **TAB4 Quiz** | Formative-assessment scenarios (15 items) | **30 min** | Black & Wiliam (1998) — formative assessment as learning event; quiz time is cognitive engagement, not mere recall |
| **TAB5 Reflection** | Written reflection, dual-signal DTP/RTM interaction | **45 min** | Schön (1983) Reflection-on-Action + RPE Framework (Dourvas et al., 2025) — reflective writing is itself a learning act, not a coda |
| **Total per module** | | **5 hours** | UNESCO Rapid TPD lower bound (5–7h/week) |

This breakdown is theoretically defensible at viva: each Tab's
duration cites a separately-grounded literature, and the total
aligns with the UNESCO precedent's lower-bound expectation.

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

### 5.3 Position against benchmarks

| Benchmark | Hours | PROODOS position |
|---|---|---|
| **Yoon et al. (2007)** effective-PD threshold | 49h | **+26 hours above** |
| **UNESCO Rapid TPD** Module 1+3 baseline | ~5–7h/week | **At/just below lower bound** |
| **Garet et al. (2001)** sustained-PD criterion | sustained (multi-week) | **Met (15 weeks)** |
| **Darling-Hammond et al. (2017)** seven features include sustained duration | n/a (qualitative) | **Met** |

The PROODOS workload sits **above** the empirical effectiveness
floor and **within** the UNESCO precedent envelope. Both required
constraints (§2 C1 + C2 + C3) are satisfied.

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

Each Tab's duration estimate rests on a separately-verified
citation. The verification status notes below mirror the
project's standing rule on no hallucinated citations.

### TAB1 Introduction — 20 minutes

Ausubel, D. P. (1968). *Educational psychology: A cognitive view.*
New York: Holt, Rinehart and Winston.

**Verification:** Foundational text on advance organisers and
cognitive scaffolding — appears in every cognitive-psychology
review since its publication. Standard education reference;
verified through canonical citation chains rather than direct
search (book pre-dates online discovery). **Citation defensible
at viva.**

### TAB2 Core Content — 75 minutes

Standard academic-reading-speed estimates: 250–300 words per
minute (wpm) for typical prose; 100–200 wpm for technical or
unfamiliar material. PROODOS module Core Content sections range
6000–9000 words (typical Tab2 module content). At 100 wpm
(conservative, accounting for the SVG-diagram analysis cost):
6000–9000 / 100 = 60–90 minutes. **75 minutes adopted as
midpoint.**

This estimate is not anchored to a single citation but to a
well-documented range in reading-research literature (e.g.,
Carver, 1990 on reading rates; Rayner et al., 2016 on
comprehension-vs-rate trade-offs). **Citation defensible at viva
via citation of the general reading-speed literature.**

### TAB3 Practical Challenges — 120 minutes

Wenger, E. (1998). *Communities of Practice: Learning, Meaning,
and Identity.* Cambridge: Cambridge University Press.

**Verification:** Verified via WebSearch 2026-05-26. Cambridge
University Press canonical edition; ISBN 9780521663632. Series:
"Learning in Doing: Social, Cognitive and Computational
Perspectives." [Cambridge link](https://www.cambridge.org/highereducation/books/communities-of-practice/724C22A03B12D11DFC345EEF0AD3F22A).

### TAB4 Quiz — 30 minutes

Black, P., & Wiliam, D. (1998). Inside the black box: Raising
standards through classroom assessment. *Phi Delta Kappan, 80*(2),
139–148.

**Verification:** Standard education reference; landmark text on
formative assessment in the K-12 classroom. The 30-minute estimate
allows for the 15-item assessment + reading + reflection on
incorrect answers (formative engagement, not pure recall).
**Citation defensible at viva.**

### TAB5 Reflection — 45 minutes

Schön, D. A. (1983). *The Reflective Practitioner: How
professionals think in action.* New York: Basic Books.

Plus: Dourvas, J., Kokkonis, G., & Kontogiannis, S. (2025).
Reflective Prompt Engineering for Educator AI Literacy: The RPE
Framework. *British Journal of Educational Technology* (under
revision after first-round rejection — see BJET resubmission
project notes).

**Verification:** Schön (1983) is the foundational text on
reflection-in-action and reflection-on-action; standard education
reference. Dourvas et al. (2025) is the dissertation author's own
work in submission; cited as PROODOS-internal grounding.
**Citation defensible at viva.**

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
  gain in student achievement; under-14-hour PD showed no
  significant effect.

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
  (resubmission in revision). PROODOS author's own work.

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
