# D.4 — Dashboard: UNESCO Matrix + RTM Heatmap — Design Proposal v1

*Phase D, sub-track D.4 — the last. Drafted 2026-05-20. Builds on the
`apps/analytics/` app and the consent / date / subject scoping the D.1
and D.2 work established.*

---

## 1. Summary

D.4 adds two **cohort-level visualisations** to the existing
`/analytics/` research dashboard:

1. a **UNESCO Matrix 5×3** — the 5 competency aspects × 3 proficiency
   levels grid, each of the 15 cells showing the cohort's completion of
   that module;
2. an **RTM Heatmap** — 16 subject areas × 15 modules, each cell showing
   how many teachers of that subject have RTM data on that module.

Both are read-only, researcher-facing, restricted to research-consenting
teachers, and rendered as two further sections on the `/analytics/`
page. D.4 is the final Phase D sub-track.

---

## 2. Motivation

The platform's structure — the UNESCO 5×3 competency framework — and its
RTM positioning data have no at-a-glance cohort view. Module completion
is visible only one teacher at a time; RTM data is buried per row. D.4
gives the researcher a single visual reading of where the cohort stands
in the framework and where the RTM instrument has coverage. The roadmap
also earmarks both visuals as dissertation figures.

---

## 3. The two visualisations

### 3.1 UNESCO Matrix 5×3
A 5×3 grid: rows = the 5 UNESCO aspects (Human-Centred Mindset, Ethics,
AI Foundations, AI Pedagogy, Professional Development), columns = the 3
proficiency levels (Acquire, Deepen, Create). Each of the 15 cells maps
to exactly one module and shows its **cohort completion rate** —
consenting teachers who completed that module, over all consenting
teachers — with the cell shaded by that rate. The matrix reads as the
cohort's progress shape through the framework (a descending staircase
from M1 toward M15 is the expected, healthy pattern, not a deficiency).

### 3.2 RTM Heatmap
A 16×15 grid: rows = the 16 `TeacherProfile.subject_area` values,
columns = the 15 modules. Each cell shows a **coverage count** — the
number of distinct consenting teachers of that subject who have at
least one `ReflectionTension` row for that module — with the cell shaded
by that count. It answers "which subjects engaged the RTM, on which
modules", as a density map.

---

## 4. Scope — inherits the `/analytics/` page rules

D.4 inherits the dashboard contract: **staff-only**, **research-consent
restricted**, and **filter-aware** (the date-range and subject filters).
Two scoping notes:

- The **RTM heatmap** is fully scoped — consent, subject and date all
  apply (it aggregates `ReflectionTension.created_at`, an event).
- The **UNESCO matrix** shows *cumulative* completion — a standing
  state, not an event in a window. Consent and subject apply to it; the
  **date filter does not narrow it** (date-windowing a cumulative state
  is incoherent). The matrix carries a one-line note to this effect when
  a date filter is active.

---

## 5. Design decisions

*Settled in the chat sessions of 2026-05-19/20.*

### 5.1 Matrix cell = cohort completion rate
Completed-count over all consenting teachers — the natural cohort
progress metric.

### 5.2 Heatmap cell = coverage count
The cell counts distinct consenting teachers of the subject with RTM
data on the module. Rejected alternatives: **mean position** (averages
`selected_position` across tension-specific scales — methodologically
incoherent); **EDS per cell** (engagement depth is noise at the N≈0–1
of a pilot subject×module cell). At pilot scale the heatmap is honestly
a coverage map, and a count is the honest thing to show (§7).

### 5.3 Placement — two sections on the `/analytics/` page
D.4 renders as sections 3 (UNESCO Matrix) and 4 (RTM Heatmap) below the
D.1 and D.2 sections. No separate page; the audience is the same
(researcher) and §5.7 of the architecture chapter fixes the scope.

### 5.4 Read-only — no model, no migration
D.4 visualises `Module`, `UserModuleProgress` and `ReflectionTension`
data that already exists. Pure read-side aggregation.

---

## 6. Mechanism and architectural placement

1. **`apps/analytics/services.py`** — two new functions:
   `cohort_unesco_matrix(filters)` (the 5×3 grid of module completion)
   and `cohort_rtm_heatmap(filters)` (the 16×15 coverage grid). Pure ORM
   aggregation, consent-scoped; the heatmap also date-scoped.
2. **`apps/analytics/views.py`** — the view passes the filter dict to
   the two new functions and adds their output to the context.
3. **`templates/analytics/research_analytics.html`** — two new sections
   render the grids (CSS-grid tables, cells shaded by value).
4. **`apps/analytics/tests.py`** — aggregation-correctness tests for the
   matrix and the heatmap, including the consent restriction.

No change to any model, no migration.

---

## 7. Methodological caveats (for the dissertation)

- **Small N — the heatmap is a coverage map.** A 16×15 grid over a pilot
  cohort is mostly empty; most cells are 0–2 teachers. It must be read
  as *where RTM data exists*, not as a comparative measure. The cell
  shows a count, deliberately — a count cannot be over-interpreted the
  way a rate or a colour gradient invites.
- **The matrix staircase is expected.** Later modules show lower
  completion because teachers progress sequentially; the descending
  shape is the progress signal, not under-performance.
- **Completion ≠ engagement.** The matrix records completion only; the
  engagement question is D.2's (§5.6 of the architecture chapter). The
  two are read together.

---

## 8. Dissertation coupling

- D.4 fills the **§5.7 placeholder** of
  `PROODOS_Architecture_Chapter_DRAFT_v1.md` (the UNESCO Dashboard and
  RTM Heatmap).
- The matrix rests on the UNESCO AI Competency Framework already
  anchored in the architecture chapter's §2.1. **D.4 introduces no new
  construct** — it visualises existing measures (module completion, RTM
  presence) — so it needs no new external references. The
  researcher-facing, consent-restricted scoping reuses the
  measurement-reactivity grounding of §5.5/§5.6 (Paradis & Sutkin,
  2017). This is noted explicitly to satisfy the standing
  bibliographic-support rule: the absence of new citations here is a
  considered position, not an omission.

---

## 9. Decisions log

**Confirmed (chat sessions 2026-05-19/20):**

- D.4 is two cohort visualisations — a UNESCO 5×3 completion matrix and
  an RTM 16×15 coverage heatmap — on the existing `/analytics/` page.
- Matrix cell = cohort completion rate; heatmap cell = coverage count.
- Researcher-facing, staff-gated, consent-restricted, filter-aware.
- The matrix is cumulative (not date-narrowed); the heatmap is fully
  filtered.
- Read-only: no model, no migration.
- No new external references — D.4 introduces no new construct.
