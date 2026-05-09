# PLATFORM_CHANGES_LOG_TIER2_APPEND

**Phase:** A · **Tier:** 2 · **Date:** 2026-05-02
**Predecessor:** Phase A Tier 1 (Cycles 1+2, applied 2026-05-01)
**Spec:** `PHASE_A_TIER2_WORDINGS_AND_SPECS_v2.md`
**Append target:** `PLATFORM_CHANGES_LOG.md` (master tracking doc)

---

## Executive summary

| | |
|---|---|
| Patches applied | 4 (M1 disabilities × 3 modules, M4 SVGs × 3, M13 repository CTA, M15 Tier 5) |
| Modules touched | M4 / M5 / M10 / M13 / M15 (DB) · M2 (NOT touched — TAB3 Q1 from Tier 1 only) |
| New schema | 1 migration (`0011_alter_modulecontent_subject_area_and_more.py` — adds `Tab3RepositorySubmission` + 2 SQL no-op CharField choices syncs) |
| Files created | 9 new files (PDF template, GitHub repo files × 6, log files × 2) |
| Files modified | 8 files (models, admin, views, urls, settings, 2 tab3_content_*.py, 2 templates) |
| RAG corpus growth | 935 → 938 chunks (+3 atomic from M5/M10/M15 disabilities) |
| Backup tables | `modules_modulecontent_backup_phase_a_tier2_may2026` (1 258 rows) |
| New PDF library | xhtml2pdf 0.2.17 (weasyprint blocked on Windows by missing GTK runtime) |
| External resources | GitHub repo `dourvas/proodos-eduai-teacher-workflows` (public, MIT licence, live) |
| Browser tests | All 5 step-completions verified by John |
| RAG verification | M5/M10/M15 disabilities: 3/3 #1 retrieval (sim 0.7751 / 0.8025 / 0.7918) |

---

## Pre-flight blockers + resolutions (2026-05-02 morning)

The Tier 2 spec was written assuming module structures that did not match the
live database. 6 blockers detected before any apply, all resolved with John:

| # | Blocker | Resolution |
|---|---|---|
| 1 | M5 "Iceberg Knowledge Model" not in main_content (actual Part 2 = "Three Frameworks") | Re-target M5 disabilities patch to **Part 1 ("The Knowledge You Cannot Name")** with rewritten opening ("Tacit knowledge and teachers with disabilities"). Pedagogically tighter — Part 1 is about externalising tacit knowledge, perfect frame for the disability subsection. |
| 2 | M4 Part 3 = "AI in Practice — Preparation, Feedback, Assessment" (NOT "Pedagogical Fit Test" per spec) | Re-design SVG 2 as **"Three Practice Domains"** — horizontal 3-panel layout matching the actual Part 3 content (Preparation / Feedback / Assessment) with explicit `AI strong / Human keeps` role separation per panel. |
| 3 | M4 Part 4 = "Student-Facing AI" (NOT "Four AI Integration Domains" per spec) | Re-design SVG 3 as **"Student-AI Control Spectrum"** — 3-panel horizontal spectrum with arrow gradient warning→info→success: Walled Garden (K-3/SEN) · Curated Access (G4-8) · Open AI w/ Guardrails (G9-12). Matches the existing Control Spectrum subsection that lives in Part 4. |
| 4 | weasyprint blocked on Windows venv (missing libgobject-2.0-0.dll / GTK runtime) | **Fallback to xhtml2pdf** (per Decision 4). Pure Python, no system deps. Smoke test produced 1.86KB PDF cleanly. Production deployment may switch back to weasyprint if GTK is available on the target host. |
| 5 | `Tab3PortfolioSubmission` model assumed by spec — **does not exist** | M15 Tier 5 implementation switched to **JSONB-only** (Decision 5). New `training_module_description` field stored in `Tab3UserActivity.challenge_data` JSONB. No migration needed. Backward compat via `audit_version: 2` flag. |
| 6 | `proodos-eduai/teacher-workflows` org doesn't exist | John created repo as **`dourvas/proodos-eduai-teacher-workflows`** (public, his account). `GITHUB_WORKFLOWS_URL` settings constant updated to match. CONTRIBUTING.md and README.md authored locally + pushed via `git push -u origin main`. |

---

## STEP 2 — M1 Disabilities Patches (M5 / M10 / M15)

**Indicator targeted:** CG5.3.3 (peers with disabilities)
**Patch marker (all 3):** `<!-- DISABILITIES_FOCUS_PATCH -->`

### DB applies (single transaction)

| Module | Row | Pre-len | Post-len | Δ | patches[] post |
|---|---|---|---|---|---|
| **M5** | 655 | 29 227 | **30 223** | +996 | `[m5_disabilities_focus]` (1) |
| **M10** | 791 | 41 940 | **42 769** | +829 | `[..., m10_disabilities_focus]` (2 — preserved Cycle 1 `master_teachers_acknowledgment`) |
| **M15** | 925 | 51 978 | **53 993** | +2 015 | `[..., m15_disabilities_focus]` (2 — preserved Day 1 `disabilities_apr2026`) |

Anchors verified count=1 each. Idempotency clean (no marker pre-existed).

### Per-patch placement

- **M5 (Part 1 — re-targeted)**: aside `border-l-4 border-info` με ARIA `role="note"` + `aria-label`. Inserted before `<div class="divider my-8"></div>` + Part 2 H2.
- **M10 (Part 4 end)**: aside `border-l-4 border-warning` με ARIA. Inserted before `<!-- SUBJECT_BOX_PART4 -->` + divider + Part 5 H2.
- **M15 (Part 5 — full subsection)**: `<section aria-labelledby="m15-disabilities-heading">` με 3 commitments ordered list + accent `border-l-4 border-accent` references aside. Inserted before `<h3>The Final Question</h3>`.

All 3 use ARIA accessibility upgrades per Gemini revision (v2 spec).

### RAG ingest (3 atomic chunks)

| Patch | Doc | Chunk | Module |
|---|---|---|---|
| M5 disabilities focus | 88 | 1616 | 16 |
| M10 inclusive CoP design | 89 | 1617 | 18 |
| M15 disabilities co-creating AI | 90 | 1618 | 20 |

### RAG verification — 3/3 #1 unfiltered AND mod-scoped

| Query | rank/all | rank/mod | sim | spec target ≥ 0.78 |
|---|---|---|---|---|
| "How can teachers with disabilities use the RPE Framework?" | #1 | #1 | 0.7751 | ⚠️ 0.005 short — accepted (cf. notes) |
| "How can Communities of Practice include teachers with disabilities?" | #1 | #1 | 0.8025 | ✅ |
| "How do teachers with disabilities co-create accessible AI for professional development?" | #1 | #1 | 0.7918 | ✅ |

**M5 sim 0.7751 < 0.78 explanation:** Patch is short (~700 chars cleaned) and re-targeted to Part 1 opens με "Externalising tacit knowledge" — the term "RPE Framework" appears 3× but isn't lead. Acceptable retrieval — clean #1 in both filters. Threshold cosmetic miss only.

### Cross-coherence bonuses

- M10 Q2 unfiltered top-3: M10 target #1, **M5 disabilities #2**, **M15 disabilities #3** — 3 disabilities chunks form a tight cluster (correct cross-pattern)
- M15 Q3 unfiltered top-3: M15 target #1, **M10 disabilities #2** — proper cross-module routing

---

## STEP 3 — M4 SVG Normalisation (3 SVGs)

**Indicators:** LO4.1.2 (SVG 1) + CG4.1.4 (SVG 2 + SVG 3)
**Anomaly closed:** M4 was the only module with 0 SVGs in main_content.

### DB apply (single transaction)

| | |
|---|---|
| M4 row 633 pre-len | 36 175 |
| M4 row 633 post-len | **54 111** |
| Δ | **+17 936** chars |
| Per-SVG | SVG1 +6 303 · SVG2 +5 705 · SVG3 +5 928 |
| Markers | 3/3 present ✅ |
| patches[] | `[m4_svg1_decision_tree, m4_svg2_three_practice_domains, m4_svg3_student_ai_control_spectrum]` |

### Hybrid palette (per Q7)

| Hex | DaisyUI token | Usage |
|---|---|---|
| `#2563EB` | info | decision/Co-design |
| `#16A34A` | success | YES/Adopt/Direct use |
| `#DC2626` | error | NO/Reject/NO AI |
| `#D97706` | warning | Caution/AI inspiration only |
| `#F1F5F9` | base-200 | neutral fill |
| `#1E293B` | base-content | text (high contrast on white + on base-200) |

Pulled from M3 SVGs (cool-blue, decision-amber-violet, multi-domain palettes), audited against DaisyUI tokens. White text on colored outcome boxes verified ≥ 4.5:1 WCAG AA.

### Accessibility (all 3 SVGs)

- `role="img"` + `aria-labelledby` linking `<title>` + `<desc>` IDs
- SVG 1 also has `aria-describedby` linking to descriptive prose paragraph below (Gemini revision)
- `viewBox` + `preserveAspectRatio="xMidYMid meet"` + container `max-width:100%; height:auto;` — mobile-responsive

### RAG ingest

**Skipped** (per joint decision). SVGs are visual aids, not net-new conceptual content. Cleaned text density too low for meaningful retrieval. The surrounding M4 prose (already in RAG) covers the concepts. Reserved as future selective ingest if retrieval gaps emerge for visual-named queries (e.g. "Walled Garden mode").

---

## STEP 4 — M13 Repository Submission CTA

**Indicators:** LO3.3.4 (contribute to repository) + CA3.3.3 (coordinating repositories — strengthened by peer-review framing)

### Migration cycle (Q4 — separate dry-run + apply)

- File: `apps/modules/migrations/0011_alter_modulecontent_subject_area_and_more.py`
- Operations: 2 SQL no-op CharField choices syncs (modulecontent.subject_area + tab3promptlibrary.subject) + 1 CREATE TABLE (`modules_tab3repositorysubmission`) + 5 indexes + 3 FKs (user, module, reviewed_by)
- 4 admin permissions auto-created (add/change/delete/view)
- Verified table exists with 15 columns

### Backend additions

| File | Change |
|---|---|
| `apps/modules/models.py` | +`Tab3RepositorySubmission` class (60 LOC) |
| `apps/modules/admin.py` | +`@admin.register(Tab3RepositorySubmission)` με 3 actions: `approve_selected`, `reject_selected`, `request_revision`. Filters by review_status/module/subject/grade. |
| `apps/modules/views.py` | +`submit_to_repository` (POST, persists submission + backfills canvas_data from Tab3UserActivity) · +`export_canvas_pdf` (GET, xhtml2pdf via `templates/pdf/m13_canvas_export.html`) |
| `apps/modules/urls.py` | +2 routes: `tab3/submit-to-repository/` + `tab3/export-canvas-pdf/` |
| `config/settings.py` | +`GITHUB_WORKFLOWS_URL` env-overridable constant |
| `apps/modules/tab3_content_m13.py` | +`from django.conf import settings` + `github_workflows_url` in `get_context()` |

### PDF backend

- **xhtml2pdf 0.2.17** — chosen as fallback per Decision 4 (weasyprint blocked on Windows GTK)
- Template: `templates/pdf/m13_canvas_export.html` με PROODOS branding header, step list με green stripe, footer με author + ISO timestamp
- Smoke test: 3 135 bytes generated cleanly. Sample at worktree `m13_canvas_export_smoke.pdf`
- Reuses existing canvas data from `Tab3UserActivity.challenge_data` (no separate canvas storage)

### GitHub repo creation

- Repo: **https://github.com/dourvas/proodos-eduai-teacher-workflows** (public, MIT licence, default branch `main`)
- 6 files initial commit:
  - `README.md` (3 037 chars) — submission guidelines, 2-channel framing (PROODOS Verified Repository vs Open Community PR)
  - `CONTRIBUTING.md` (2 921 chars) — peer-review process, quality criteria, contribution workflow
  - `LICENSE` (MIT)
  - `.gitignore`
  - `workflows/_template/workflow.md` — starter template
  - `workflows/lesson-prep/example-differentiated-reading/workflow.md` — placeholder example

### Template + JS additions

- CTA card με 3 buttons (📄 Export PDF · 📤 Submit for Peer Review · 🌐 Share to GitHub) inside Challenge 2 completed state
- Submission modal (`<dialog>`) με 5 fields (title, summary, subject_area, grade_level, contact_email)
- Char counter on summary (200 chars max)
- Soft-mandatory validation, network error handling

### Browser + admin tests

✅ **Browser:** All 3 buttons function. PDF downloads. Modal opens, submission persists, "✅ Submitted for peer review" message + Cancel→Close behavior verified.
✅ **Admin:** Submission visible in `/admin/modules/tab3repositorysubmission/`. List filter by review_status/subject/grade works. Approve/reject/needs_revision actions update status + reviewer_by + reviewed_at correctly.

### Architectural note: review currently admin-only

Current implementation: **Django admin only** (per Q2 spec — "basic admin (list/approve/reject)"). Aspirational language in `CONTRIBUTING.md` references "master teachers" as reviewers. **See Section "Future Evolution: Peer Review (Tier 3 candidate)" below for detailed evolution notes.**

---

## STEP 5 — M15 Portfolio Builder Tier 5 (Training Module)

**Indicator:** CA5.3.2 (AI-enhanced design of training programmes)
**Approach:** JSONB-only per Decision 5 — no migration

### Architecture adaptation

Spec assumed M15 Portfolio Builder = "4-tier pick-one" model. **Actual architecture** = "4-column × 8-card mapping" (radio per column). Adapted spec's "5th tier insertion" to:
- Add 5th **column** "🎓 Training Module" gated by Yes/No question above grid
- 5th column shows 8 base cards + 2 NEW training-specific cards (`card_i`, `card_j`)
- 5th column selection is OPTIONAL (not enforced like the 4 base columns)
- Soft-mandatory textarea (200 chars) below grid: "Briefly describe the audience and goals of your training programme"
- Confirmation modal if tier5_gate=yes + selection + empty description

### Files modified

| File | Change |
|---|---|
| `apps/modules/tab3_content_m15.py` | +`tier5_training_module` config (11 sub-keys: key/icon/title/colour/description/selection_criterion/input_label/input_placeholder/input_max_length/soft_mandatory_message/card_values) · +`tier5_training_cards` (2 items) · extended `portfolio_column_labels` from 4 → 5 keys |
| `templates/.../tab3_activity_m15.html` | +Yes/No gate card above grid · +5th column block (conditional via JS visibility) · +textarea + char counter · +confirmation modal · +grid `items-start` (CSS layout fix) · +completed-state 5th card (full-width via `md:col-span-2`, conditional on `challenge2_training_module` presence) |

### Storage convention (JSONB)

```json
{
  "challenge2_prompt_library":              "card_x",
  "challenge2_reflections":                 "card_y",
  "challenge2_lesson_cycle":                "card_z",
  "challenge2_contribution":                "card_w",
  "challenge2_training_module":             "card_i",         // NEW (only if gate=yes + selection)
  "challenge2_training_module_description": "...",            // NEW (only if filled)
  "challenge2_audit_version":               2,                // NEW (always for new submissions)
  "challenge2_tier5_gate":                  "yes" | "no"      // NEW (always)
}
```

**Backward compat:** legacy users (audit_version absent or 1) retain original 4-column data unchanged. `audit_version: 2` distinguishes new submissions. No migration, no data backfill needed.

### Browser test

✅ **Form path A (gate=No):** 4 columns only, save works. JSONB stores `tier5_gate: "no"`.
✅ **Form path B (gate=Yes):** 5th column appears, textarea visible. Save with selection + description → all 4 base columns + training_module + description + audit_version=2 saved cleanly. Confirmed by John with real submission (saved as `challenge2_training_module: "card_b"` + `challenge2_training_module_description: "I have not have anything to say"`).
✅ **Soft-mandatory modal:** triggers correctly when gate=yes + selection but empty description.
✅ **Completed-state UI:** 5th amber card appears below 4-column grid with programme description quoted (added in fix after John reported missing display).

### Bug fix during browser test

- **Issue 1:** Grid stretched Lesson Cycle column to match Training Module height, leaving large empty space inside Lesson Cycle. **Fix:** added `items-start` to the grid container CSS to disable row stretch.
- **Issue 2:** Completed-state UI didn't display the saved Training Module selection. **Fix:** added a 5th conditional card (full-width via `md:col-span-2`) that renders only when `challenge2_training_module` exists in JSONB; quotes programme description if present.

---

## Backup tables created

| Table | Purpose |
|---|---|
| `modules_modulecontent_backup_phase_a_tier2_may2026` | Pre-Tier-2 baseline (1 258 rows) — covers Steps 2 + 3 (M5/M10/M15 disabilities + M4 SVGs). Step 4 (M13) and Step 5 (M15 Tier 5) didn't touch `modules_modulecontent` so this single backup is sufficient as rollback path for all DB-content changes. |

---

## Files inventory (all Tier 2)

### Created
```
apps/modules/migrations/0011_alter_modulecontent_subject_area_and_more.py
templates/pdf/m13_canvas_export.html
github_staging/teacher-workflows/README.md
github_staging/teacher-workflows/CONTRIBUTING.md
github_staging/teacher-workflows/LICENSE
github_staging/teacher-workflows/.gitignore
github_staging/teacher-workflows/workflows/_template/workflow.md
github_staging/teacher-workflows/workflows/lesson-prep/example-differentiated-reading/workflow.md
m13_canvas_export_smoke.pdf  (sample artefact)
PLATFORM_CHANGES_LOG_TIER2_APPEND.md  (this file)
CONTENT_GAPS_LOG_TIER2_UPDATE.md
```

### Modified
```
apps/modules/models.py          (+Tab3RepositorySubmission, ~60 LOC)
apps/modules/admin.py           (+Tab3RepositorySubmissionAdmin + 3 actions)
apps/modules/views.py           (+submit_to_repository + export_canvas_pdf)
apps/modules/urls.py            (+2 routes)
apps/modules/tab3_content_m13.py (+settings import + github_workflows_url)
apps/modules/tab3_content_m15.py (+tier5_training_module + tier5_training_cards + extended labels)
config/settings.py              (+GITHUB_WORKFLOWS_URL constant)
templates/modules/tabs/tab3_activity_m13.html (CTA card + modal + JS)
templates/modules/tabs/tab3_activity_m15.html (gate + 5th column + textarea + modal + JS + completed-state card + items-start CSS fix)
```

### DB-modified
```
modules_modulecontent (5 rows): M5 row 655, M10 row 791, M15 row 925, M4 row 633, M15 row 925 (single hit)
modules_tab3repositorysubmission: new table created via migration 0011
documents (3 rows): docs 88/89/90
document_chunks (3 rows): chunks 1616/1617/1618
```

### Pip dependencies added
```
xhtml2pdf 0.2.17 (and transitive: arabic-reshaper, asn1crypto, freetype-py, html5lib, lxml,
                   oscrypto, pyHanko, pycairo, pyhanko-certvalidator, pypdf, python-bidi,
                   pyyaml, reportlab, rlpycairo, svglib, tzlocal, uritools)
weasyprint 68.1 (and transitive: brotli, cssselect2, pydyf, pyphen, tinycss2, tinyhtml5,
                  webencodings, zopfli) — installed but UNUSED (Windows GTK blocked)
```

⚠️ Note for production: weasyprint dependencies can be safely uninstalled if confirmed never to be used. Keeping installed for now allows future Linux deployment (where GTK is available) to switch backends with no install.

---

## ⏭️ Future Evolution Notes — Peer Review (Tier 3 candidate)

> Per John's request 2026-05-02 — these notes preserve the design conversation
> for a future Tier 3 patch that evolves the Tab3RepositorySubmission review
> workflow from admin-only to subject-peer review.

### Current state (Tier 2)

- Reviews performed via **Django admin** by users with `is_staff=True` + Tab3RepositorySubmission permissions
- Filters: by review_status / module / subject_area / grade_level
- Actions: approve / reject / needs_revision (sets reviewed_by + reviewed_at)
- **No subject matching, no peer dimension, no notification**
- `CONTRIBUTING.md` aspirationally references "master teachers" reviewing — does NOT match current code

### Why peer review matters (John's argument 2026-05-02)

> "Νομίζω πως πρέπει το reviews να γίνει από φυσικούς (ίδια ειδικότητα)."

Pedagogical alignment:
- **PROODOS philosophy** — emphasises practitioner expertise (M11 voice, M15 master teachers)
- **UNESCO master teachers terminology** — already incorporated in Cycle 1 patches Q4 (M12) + Q7 (M10)
- **CG3.3.3 coordinating repositories** — peer-validated coordination is stronger than admin-curated
- **CA5.3.x Aspect 5 / Professional Development** — performing peer review IS professional learning for the reviewer

### Proposed evolution path (3 levels)

#### Level 1 — Subject-filtered reviewer role (~1.5h)
Minimal viable:
- Add `is_subject_reviewer = models.BooleanField(default=False)` to `apps.users.models.TeacherProfile`
- Reviewers must have `is_staff=True` (basic admin access) + this flag
- Custom admin class `Tab3RepositorySubmissionReviewerAdmin` that overrides `get_queryset` to filter `subject_area = request.user.teacher_profile.subject_area`
- Admin can promote any teacher to reviewer via TeacherProfile admin
- Update `CONTRIBUTING.md` to match: "reviewed by subject peers (master teachers in your discipline)"

Trade-off: still requires `is_staff` (limited Django admin UX); no notification system; reviewer sees only own subject — invisible to admin overview.

#### Level 2 — Custom teacher-facing review dashboard (~6-8h)
- Dedicated app or extension: `apps.review/` with views + templates
- Teachers (not staff) get "Reviewer" badge on profile
- New URL `/review/queue/` shows pending submissions filtered to reviewer's subject
- Inline review form (status + reviewer_notes textarea) on submission detail page
- Email notification when new submission lands in subject queue
- Email to original submitter when status changes
- Optional: review_quorum field (e.g. "2 of 3 peer reviews required to publish")

Trade-off: significant Django app development; need email infrastructure config; reviewer reputation tracking is a separate sub-feature.

#### Level 3 — Full peer-review ecosystem (sprint-scale)
- Reviewer reputation tracking (n_reviews, avg_review_quality)
- Reviewer pool eligibility rules (min N PROODOS modules completed, min M reflections submitted)
- Public review history on author profile
- Review-of-reviews (meta-quality)
- Community-recognized "Master Reviewer" status

Trade-off: reputation systems require careful design to avoid gaming; full sprint scope.

### Recommended next step

**After Tier 2 closes:** add **Level 1** as a Tier 3 patch. Estimated 1.5h. Aligns docs with code with minimal new infrastructure. Defers Level 2 + Level 3 to dedicated sprints when teacher base scales beyond ~20 active reviewers.

### Decision rationale (why deferred from Tier 2)

- Tier 2 scope was already heavy (4 patterns × execution). Adding peer review would have doubled scope.
- The current admin-only path is functional — no production-blocking gap. The mismatch with CONTRIBUTING.md is docs-only, not breaking.
- Peer-review design benefits from observing actual review patterns (volume, types of feedback, reviewer engagement) which the admin-only Tier 2 will gather data for.

---

## Operational notes

- All applies done within single PostgreSQL transactions, with pre-snapshot + anchor pre-checks + post-state verification + ROLLBACK on any failure.
- Anchor uniqueness verified count=1 for every patch.
- Idempotency verified (markers must NOT pre-exist).
- All `metadata.patches` arrays append new entries via `jsonb_set` + `COALESCE` — preserves prior Cycle 1 / Day 1-3 / Tier 1 entries.
- M2 was NOT touched in Tier 2 (only Tier 1 Q1 changed M2 TAB3 audit questions — unchanged here).
- M6 and M8 remain untouched (no patches in any Phase A tier yet).

---

*End of PLATFORM_CHANGES_LOG_TIER2_APPEND.md*
