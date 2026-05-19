# D.1 — AI Output Relevance Profile — Design Proposal v1

*Phase D, sub-track D.1. Drafted 2026-05-19. Companion to the D.3a
(`DTP_REDEFINITION_DESIGN_PROPOSAL_v1_20260518.md`) and D.3b
(`DTP_XAI_NARRATIVE_DESIGN_PROPOSAL_v1_20260519.md`) proposals.*

---

## 1. Summary

D.1 turns the human-in-the-loop ratings teachers already give on AI
outputs into a **researcher-facing analytic profile**. Across the
programme, each teacher rates the relevance of the RAG, RTM and DTP
outputs on their own reflection (`AIOutputDispute`, ratings
*relevant / partially / not relevant*, with optional reason codes).
D.1 aggregates those ratings into a per-teacher and cohort-level
**profile of perceived AI-output relevance** — a new descriptive
research variable for the dissertation.

D.1 is **read-only**: it adds no data collection, changes no teacher
surface. It only aggregates and displays data that already exists.

The roadmap's original name for this sub-track — *Trust Calibration
Score* — is **not** adopted. Section 3 explains why; section 4 explains
why the profile is shown only to the researcher, never to the teacher.

---

## 2. Motivation — and what D.1 is NOT

### 2.1 Why build it
Every teacher, on every module, can rate each AI output. That rating
stream is one of the platform's richest research assets: it is direct,
per-feature, per-module evidence of how teachers received the AI
support. Left un-aggregated it is invisible. D.1 makes it analysable.

### 2.2 What D.1 is NOT
- It is **not a measure of the teacher's competence or development.**
  It measures how relevant the teacher found the *AI's* output.
- It is **not a grade.** No teacher is ranked, scored, or compared.
- It is **not a trust-calibration instrument** in the technical sense
  (§3).
- It is **not shown to teachers** (§4).

---

## 3. The construct — perceived relevance, not trust calibration

The roadmap called D.1 a *Trust Calibration Score*. A construct-validity
review (the same scrutiny that drove the D.3a DTP redefinition) found
the name over-claims.

**Trust calibration** (Lee & See, 2004) is defined as the match between
a user's trust and the **actual capability** of the automation:
overtrust leads to misuse, distrust to disuse. Calibration is therefore
a *two-axis* construct — it needs both the trust the user shows **and**
a ground-truth measure of how reliable each AI output actually was.

The platform has the first axis (the relevance rating is a proxy for
the teacher's reliance) but **not the second**: there is no expert or
ground-truth quality label on each RAG/RTM/DTP output. Without the
reliability axis, calibration cannot be computed — only the *level* of
perceived relevance can. Calling that "calibration" would be the same
category of over-claim D.3a removed from the DTP.

What D.1 honestly measures is therefore named the **AI Output Relevance
Profile** — the distribution of a teacher's *perceived relevance* of the
AI outputs. "Perceived" is load-bearing: it is the teacher's judgement,
not an objective accuracy.

A genuine calibration study would require adding expert ratings of the
AI outputs as the reliability axis — a substantial manual instrument,
out of scope for the pilot and noted as future work (§12).

---

## 4. Researcher-facing only — the reactivity argument

D.1's profile is shown **only to the researcher**, in a staff-gated
analytics view. It never appears in TAB5, the teacher dashboard, or any
teacher-facing surface.

The reason is **measurement reactivity**. The `AIOutputDispute` ratings
are a research instrument; their validity depends on teachers rating
honestly, without optimising a visible target. Showing a teacher a
profile derived from their own ratings turns the rating buttons into a
score they can manage — they may rate strategically (everything
"relevant" to look well-disposed, or the reverse). Either way the
instrument is contaminated.

This is a documented effect: measurement reactivity is a special case
of the Hawthorne effect in which awareness of measurement, and feedback
about it, change the participant's behaviour (Paradis & Sutkin, 2017).
The mitigation is precisely to withhold feedback that reveals the
nature of the measurement. D.1 follows that: the profile is an analytic
output for the dissertation, not a teacher-facing feature.

(A teacher-facing *metacognitive* benefit — noticing one's own pattern
of reliance on AI — is real and literature-supported, but it is served
by scaffolded reflective prompts, not by a score; it is explicitly out
of D.1's scope.)

---

## 5. Input — what D.1 reads

D.1 aggregates the `AIOutputDispute` model (`apps/modules/models.py`):

- **feature_type** — only `rag`, `rtm`, `dtp` feed the profile. `peer`
  is **excluded by design**: peer synthesis makes no claim about the
  teacher's own reflection, so its rating is a *usefulness* signal of a
  different construct (TD-019, resolved 2026-05-19). The aggregation
  query whitelists `rag/rtm/dtp` explicitly.
- **rating** — `yes` (relevant) / `partial` / `no` (not relevant).
- **reason** — optional code on `partial`/`no`: `mismatch`,
  `misinterpretation`, `generic`, `pedagogical`, `other`.
- **module**, **user**, **created_at**.

Existing indexes — `(feature_type, rating)`, `(module, feature_type)`,
`(user, module)` — already support every aggregation D.1 needs; no
schema change.

The rating is **optional** for teachers. D.1 must therefore treat the
data as sparse and self-selected (§9).

---

## 6. Output — a profile, not a single score

D.1 deliberately produces a **profile** (a set of distributions), not
one composite number. A single "score" would flatten two things the
research needs kept apart — *how much* the AI was found relevant, and
*why* it was not — and would invite exactly the grade-like reading §4
guards against.

The profile has three levels:

**6.1 Per teacher.** For each of rag/rtm/dtp: the count/proportion of
`yes`/`partial`/`no`, the dominant `reason` codes, and **coverage** —
how many of the AI outputs that were actually generated for that
teacher were rated (the non-response indicator).

**6.2 Cohort.** The same distributions across all teachers, sliceable
by **module** and by **subject area** (`TeacherProfile.subject_area`).
This is the "AI alignment per feature, module, subject" the model
docstring always promised.

**6.3 Reason analysis.** Across the cohort, the breakdown of *why*
outputs were rated `partial`/`no` — which is the actionable, diagnostic
layer (e.g. "DTP is most often marked `generic`").

A single descriptive "relevance rate" (e.g. proportion rated `yes`) may
be shown **as a convenience field inside the profile**, clearly labelled
as a descriptive proportion about the AI output — never as an
evaluative score of the teacher.

---

## 7. Design decisions

*Decisions 7.1–7.3 follow from the discussion of 2026-05-19. Decisions
7.4–7.5 are proposed here and listed for sign-off in §12.*

### 7.1 Name — "AI Output Relevance Profile"
Adopted over "Trust Calibration Score" (§3). The dissertation variable
is "perceived AI-output relevance".

### 7.2 Researcher-facing, staff-gated
The profile lives in a view reachable only by staff users
(`is_staff` / `staff_member_required`), never linked from any
teacher-facing page (§4).

### 7.3 A profile, not a single score
D.1 outputs distributions and a reason breakdown (§6).

### 7.4 Where the code lives — *proposed*
D.1 is read-only aggregation + a staff view. Two options:

- **(A) A new `apps/analytics/` app.** D.2 (Position Confirmation
  Analytics / Engagement Depth Score) is also a read-only,
  staff-facing analytic over existing data. A shared `analytics` app
  gives both a common home and a `/analytics/` URL namespace.
- **(B) Keep it in `apps/modules/`.** D.1's only input model
  (`AIOutputDispute`) already lives there; no new app.

**Recommendation: (A).** Two roadmap sub-tracks (D.1, D.2) share the
same shape and audience; an `analytics` app is a category home, not an
over-build. D.1 would be its first view, D.2 joins later.

### 7.5 Read-only — no change to data collection — *confirmed by design*
D.1 adds no model, no migration, no teacher-facing change. It is a pure
read-side feature. This keeps it low-risk and keeps the
`AIOutputDispute` instrument untouched.

---

## 8. Mechanism and architectural placement

Assuming decision 7.4(A):

1. **`apps/analytics/` (new app)** — `apps.py`, `urls.py`, registered
   in settings + root URLconf.
2. **`apps/analytics/services.py`** — the aggregation functions:
   per-teacher profile, cohort distributions, reason analysis. Pure
   ORM queries over `AIOutputDispute`, whitelisting `rag/rtm/dtp`. No
   AI calls, no cost.
3. **`apps/analytics/views.py`** — a `staff_member_required` view
   rendering the relevance profile (cohort overview + per-teacher
   drill-down).
4. **`templates/analytics/ai_relevance_profile.html`** — server-rendered
   tables / simple bars. No teacher-facing styling concerns.
5. **`apps/analytics/tests.py`** — aggregation correctness (including
   the `peer`-exclusion guard) and the staff-gating of the view.

No change to `AIOutputDispute`, no migration.

---

## 9. Methodological caveats (for the dissertation)

- **Optional rating → self-selection.** Teachers are not required to
  rate. The profile must report N and coverage; the dissertation must
  treat the rated subset as potentially non-representative.
- **Perceived, not objective.** The profile measures teacher judgement
  of relevance, not AI accuracy (§3). No reliability ground truth.
- **Sparse per-cell data in the pilot.** With a small pilot cohort,
  per-module × per-subject cells may be thin; report counts honestly,
  avoid over-reading small cells.
- **Peer excluded.** The profile is the rag/rtm/dtp alignment construct
  only; peer usefulness is reported separately if at all.

---

## 10. Dissertation coupling

- D.1 yields a new descriptive research variable — *perceived
  AI-output relevance* — cross-tabbable with subject area, module, and
  (post-hoc) other instruments (AILST, career stage — cf. TD-020).
- The construct argument (§3) and the reactivity argument (§4) are
  themselves dissertation content: they show construct-validity and
  research-ethics reasoning applied to the platform's own instruments.
- The architecture chapter gains a short analytics-layer subsection
  when D.1 (and later D.2) land.

---

## 11. Bibliography

Verified 2026-05-19; to be folded into
`Literature_Review_Synthesis_Note(1).md`.

- **Lee, J.D. & See, K.A. (2004).** Trust in automation: Designing for
  appropriate reliance. *Human Factors*, 46(1), 50–80. — defines trust
  calibration as the match between trust and automation capability;
  grounds §3.
- **Buçinca, Z., Malaya, M.B. & Gajos, K.Z. (2021).** To trust or to
  think: Cognitive forcing functions can reduce overreliance on AI in
  AI-assisted decision-making. *Proceedings of the ACM on
  Human-Computer Interaction*, 5(CSCW1), Article 188. — over-reliance
  as accepting AI even when wrong; the trust/performance distinction.
- **Paradis, E. & Sutkin, G. (2017).** Beyond a good story: from
  Hawthorne Effect to reactivity in health professions education
  research. *Medical Education*, 51, 31–39. — measurement reactivity;
  grounds the researcher-facing-only decision (§4).

---

## 12. Open points (for sign-off)

- **§7.4 — code location.** New `apps/analytics/` app (recommended) vs
  keep in `apps/modules/`.
- **Admin view detail.** What the staff view shows first — cohort
  overview, per-teacher drill-down, or both — and whether simple
  bar charts or plain tables suffice for the pilot.
- **Peer usefulness reporting.** Whether the peer usefulness signal
  (TD-019) gets its own small panel in the same analytics view, clearly
  separated from the relevance profile, or is left for ad-hoc query.
- **Naming sign-off.** "AI Output Relevance Profile" — confirm.

---

## 13. Decisions log

**Confirmed (chat session 2026-05-19):**

- D.1 is the AI Output Relevance Profile — a researcher-facing analytic
  over the existing `AIOutputDispute` ratings.
- The "Trust Calibration Score" framing is rejected; the construct is
  *perceived AI-output relevance* (§3).
- Researcher-facing only — no teacher-facing surface — on reactivity
  grounds (§4).
- A profile of distributions, not a single score (§6).
- Built on the 3 alignment features (rag/rtm/dtp); peer excluded
  (TD-019).
- Read-only: no model, no migration, no change to data collection.

**Proposed — pending sign-off (§12):**

- New `apps/analytics/` app as the code home (shared with D.2).
- Admin view scope and presentation detail.
- Peer-usefulness reporting placement.
