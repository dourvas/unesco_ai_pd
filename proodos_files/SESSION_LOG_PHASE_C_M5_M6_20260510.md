# Phase C Session Log — M5 + M6 — 10 May 2026

**Date:** 2026-05-10
**Session scope:** Phase C migrations M5 (AilstResponse + scoring) and M6 (ConsentRecord + Step 3 refactor)
**Author:** Claude Code session (continuity-of-care log)
**Companion logs:**
- `proodos_files/SESSION_LOG_PHASE_C_M1_M3_20260509.md` (M1, M2, Γ.1, M3 from previous day)
- `proodos_files/SESSION_LOG_PHASE_C_M4_20260510.md` (M4, earlier today)

---

## Phase C status — end of day 2026-05-10

**ALL Phase C migrations applied. DB foundation complete.** Next phase: C.2 implementation (views, templates, middleware).

| # | Description | Status |
|---|---|---|
| Scaffolding | apps.compliance + apps.ailst, INSTALLED_APPS, plan markdown | DONE commit `09d0e08` |
| M1 | compliance/0001 — extend `consent_records.valid_consent_type` | **OBSOLETE** placeholder (consent_records dropped in Γ.1) |
| M2 | users/0007 — `teacher_profiles` +4 personalization columns | **APPLIED** commit `c5818ef` |
| Γ.1 | compliance/0002 — drop pre-Phase-C dead schema | **APPLIED** commit `02db101` |
| M3 | users/0008 — `TeacherProfileHistory` + signal | **APPLIED** commit `bbe478d` |
| M4 | ailst/0001 + ailst/0002 — `AilstItem` + EN seed | **APPLIED** commit `223ebf3` |
| M5 | ailst/0003 — `AilstResponse` + scoring + recompute | **APPLIED today** commit `dbb35b7` |
| M6 | compliance/0003 + compliance/0004 — `ConsentRecord` + Step 3 backfill | **APPLIED today** commit `a3aa285` |

## Commits this session

| Commit | Title |
|---|---|
| `dbb35b7` | Phase C M5: AilstResponse model + scoring helper + recompute command |
| `a3aa285` | Phase C M6: ConsentRecord Django model + Step 3 boolean refactor |

(Earlier Phase C commits documented in companion logs.)

## Notable decisions taken in this session

### M5

- **Schema:** added `last_saved_at` (auto_now) for abandonment analytics; composite index `(timepoint, completed_at)` for analytics queries; removed redundant `Index(fields=['user'])` (covered by `unique_together(user, timepoint)`).
- **DB CHECK on timepoint** (CP override of incremental proposal): research-design constant warrants strict enforcement, unlike `language` which stays choices-only.
- **Scoring timing:** eager + raw responses preserved + `recompute_ailst_scores` management command for formula-change recovery.
- **Defensive overall=None** if any factor lacks data (CP 6 reinforcement).
- **Recompute command** with `--commit / --dry-run / --instrument-version / --user-id` flags; the last for IRB-driven per-user audits.
- **CP 5 regression test** (`test_anchor_mapping_high_value_means_high_tail`) is load-bearing for the entire dissertation analysis chain.
- **Test naming correction:** `test_all_5s_perfect_score` was conceptually wrong (raw=5 on K1 means agreeing with the negation, NOT a perfect TAIL score). Renamed to `test_all_fully_applicable_yields_mixed_scores` with corrected expected values 5.00/4.60/4.50/4.50, overall=4.65.

### M6

- **REFACTOR-NOW decision** (CP override of incremental proposal): instead of leaving Step 3 booleans on TeacherProfile parallel to ConsentRecord (a permanent dual-system risk), backfilled them immediately. 6 rows backfilled in live DB, all matching canonical state.
- **Sync signal** (`sync_teacher_profile_booleans`) keeps the booleans as a backwards-compat read cache. Queries canonical state (any active row) on every ConsentRecord post_save, not just `instance.is_active`.
- **Bug caught + fixed during dev:** `revoke_consent` originally used `QuerySet.update()` which silently bypasses `post_save` signals; the boolean cache wouldn't update on revoke. Fixed to per-row `save()`. Caught by `test_revoke_consent_flips_boolean_false`.
- **DB CHECK on consent_type** (5-value vocab) follows the M5 timepoint precedent.
- **`is_active` property** added to ConsentRecord to avoid call-site repetition of the `granted AND not revoked_at` two-condition.
- **`record_consent` is idempotent** for (user, type, version, not-revoked) — makes the AI Disclosure middleware safe to re-trigger.
- **Backfill consent_text** notes the boolean field name + migration date + the pre-Phase-C limitation (original Step 3 wording was not preserved).
- **Table name `compliance_consentrecord`** (Django default), NOT `consent_records` (avoids cognitive collision with the dropped raw-SQL table).
- **`contact_for_research` is NOT migrated** to ConsentRecord (it is a contact preference, not a consent event). Stays as boolean on TeacherProfile indefinitely.

## New artefacts created this session

| Artefact | Path | Purpose |
|---|---|---|
| AilstResponse model | `apps/ailst/models.py` (extended) | Per-user-per-timepoint AILST administration |
| Scoring helper | `apps/ailst/scoring.py` | Pure-function `compute_factor_scores` |
| Recompute command | `apps/ailst/management/commands/recompute_ailst_scores.py` | Formula-change recovery + per-user audit |
| ConsentRecord model | `apps/compliance/models.py` | GDPR-compliant consent tracking |
| Service helpers | `apps/compliance/services.py` | `record_consent`, `revoke_consent`, `migrate_legacy_teacher_consents` |
| Signal | `apps/compliance/signals.py` | `sync_teacher_profile_booleans` (boolean cache) |
| IP redaction command | `apps/compliance/management/commands/redact_old_consent_ips.py` | GDPR data minimization |
| Tech debt log | `proodos_files/TECH_DEBT_LOG.md` | NEW — 7 deferred items with concrete forward paths |

## Open design questions for next session (C.2 implementation)

C.2 implementation will use the M2-M6 DB foundation. The migration sequence is complete; what remains is the actual user-facing onboarding flow and the AI Disclosure middleware.

| C.2 step | Open considerations |
|---|---|
| **Step 0 — AI Disclosure Modal** | (a) CP 7 — copy text legal review by John before commit; (b) middleware injection point (likely `apps/compliance/middleware.py::AIDisclosureMiddleware` registered in `MIDDLEWARE` after auth); (c) redirect to `/onboarding/ai-disclosure/` for any GET except logout / disclosure URL / static; (d) acknowledgment writes via `record_consent('ai_disclosure', ...)` AND sets `teacher_profile.ai_disclosure_acknowledged_at = now()`. |
| **Step 4 — AILST T0 (4 pages)** | (a) CP 8 — mobile Likert rendering; (b) state machine for partial fill (resume on (`responses` key count); (c) `select_for_update()` on POST to prevent double-click race; (d) `compute_and_save_scores()` + set `completed_at` only when 36 keys reached; (e) explicit page validation in view (don't trust UI to send pages in order). |
| **Step 3 amendment** | (a) CP 10 — IRB consent text drafted by Claude Code, John takes to IHU IRB office; (b) view rewrites to call `record_consent()` per checkbox instead of writing booleans; (c) booleans still update via signal, no extra wiring. |
| **Profile Edit extension** | (a) Add 3 form fields for `current_curriculum_pressure`, `student_population_special_needs`, `institutional_ai_policy`; (b) M3 signal will track changes automatically; (c) UI consideration for the `student_population_special_needs` multi-select with `'none'` exclusive logic. |
| **Module gating injection** | (a) `apps/modules/views.py:796` after `progress.mark_tab_complete(...)`; (b) condition: `progress.completed_at` just-set AND `code in ('M5','M15')`; (c) idempotency via `AilstResponse.objects.filter(user, timepoint, completed_at__isnull=False).exists()`; (d) redirect to `/ailst/t1/` or `/ailst/t2/`. |

## Reference paths

| Artefact | Path |
|---|---|
| Migration plan (living) | `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` |
| Tech debt log | `proodos_files/TECH_DEBT_LOG.md` |
| Dead schema audit | `audits/DEAD_SCHEMA_AUDIT_20260509.md` |
| AILST source paper | `~/Desktop/ΔΙΔΑΚΤΟΡΙΚΗ ΔΙΑΤΡΙΒΗ/ΕΡΓΑΣΙΕΣ/ΤΕΛΙΚΟ ΣΥΣΤΗΜΑ ΕΠΙΜΟΡΦΩΣΗΣ/ΒΙΒΛΙΟΓΡΑΦΙΑ/Development_and_validation_of_the_Artificial_Intel-1-1.pdf` |
| AILST EN seed | `apps/ailst/seeds/ning_2025_v1_en.json` |
| AILST scoring | `apps/ailst/scoring.py::compute_factor_scores` |
| Compliance services | `apps/compliance/services.py::record_consent / revoke_consent / migrate_legacy_teacher_consents` |
| Compliance signal | `apps/compliance/signals.py::sync_teacher_profile_booleans` |
| Tests (ailst) | `apps/ailst/tests.py` (16 tests, all pass) |
| Tests (compliance) | `apps/compliance/tests.py` (16 tests, all pass) |
| Settings pin | `config/settings.py::AILST_CURRENT_VERSION = 'ning_2025_v1'` |

## Backup files (RETAIN UNTIL post-2027)

Per audit Section 10 retention rule, **all 7** pre-migration backup SQL files at repo root MUST be retained unchanged until the pilot study completes. M5 + M6 added two new backups today.

| File | Created before |
|---|---|
| `pre_migration_backup_phaseC_M1_20260509.sql` | M1 apply |
| `pre_migration_backup_phaseC_M2_20260509.sql` | M2 apply |
| `pre_migration_backup_phaseC_GAMMA1_20260509.sql` | Γ.1 apply |
| `pre_migration_backup_phaseC_M3_20260509.sql` | M3 apply |
| `pre_migration_backup_phaseC_M4_20260510.sql` | M4 apply |
| `pre_migration_backup_phaseC_M5_20260510.sql` | M5 apply |
| `pre_migration_backup_phaseC_M6_20260510.sql` | M6 apply |

All committed to git. **DO NOT delete. DO NOT consolidate.** Phase H may move them to a `backups/phase_c/` subdirectory.

## Challenge Points status (cumulative through Phase C)

### Resolved across Phase C

| CP | Resolution |
|---|---|
| **CP 1** | M1 dry-run: 0 rows in dead consent_records; subsequently moot after Γ.1 dropped the table. |
| **CP 2** | 7-value `student_population_special_needs` vocabulary; encoded in TeacherProfile.student_population_special_needs JSONField (M2). |
| **CP 3** | 11 fields tracked in TeacherProfileHistory (M3). |
| **CP 4** | K1, A3, E3 reverse-scored; verified verbatim against paper Appendix; 5 invariants enforce in seed loader (M4). |
| **CP 5** | Anchor mapping `Fully applicable=5`; reverse K1/A3/E3 only at compute time; load-bearing regression test in M5. |
| **CP 6** | `overall_score` = mean of factor means; defensive None if any factor lacks data (M5). |
| **CP 9** | Module-completion gating injection point identified at `apps/modules/views.py:796` (will be wired in C.2). |
| **CP 11** | Decision: Option B — wipe non-staff. **NOT YET EXECUTED.** Original reset script crashed on dead-schema FK and was deleted in Γ.1. **Fresh script must be written before pilot starts** — now trivial since dead schema is gone (just `User.objects.filter(is_staff=False, is_superuser=False).delete()` + `record_consent('ai_disclosure', ...)` for staff). |

### Pending — to address during C.2 implementation

| CP | Resolved at | Notes |
|---|---|---|
| **CP 7** (AI disclosure copy text) | C.2 Step 0 | EU AI Act Article 50(1) wording; legal review by John before commit. |
| **CP 8** (mobile Likert rendering) | C.2 Step 4 | Must preserve measurement (5 radio + verbal anchors); only visual layout may change. |
| **CP 10** (IRB consent text) | C.2 Step 3 amendment | Option B chosen — Claude Code drafts custom; John takes to IHU IRB office. John has not yet applied. |

## Tech debt observations recorded this session

See `proodos_files/TECH_DEBT_LOG.md` for full entries. Summary:

- **TD-001** Consent audit retention if IRB requires (Phase H upgrade path documented)
- **TD-002** TeacherProfile boolean cache deprecation (Phase H, after all reads migrate to ConsentRecord)
- **TD-003** Timezone-naive timestamps on legacy teacher_profiles columns (workaround: Migration 0004 coerces to aware via `make_aware()`)
- **TD-004** Tier 3 backup tables cleanup (15 tables, Phase H)
- **TD-005** `rag_query_system.py` cp1253 print issue (workaround: `PYTHONIOENCODING=utf-8`)
- **TD-006** Ephemeral artefacts (`m13_canvas_export_smoke.pdf`, `proodos_matrix_files.zip`) → `.gitignore`
- **TD-007** M1 placeholder + future migration squash consideration

## Continuity guidance for next session

- **Resume with:** "C.2 design" (start of view/template implementation) OR "CP 11 wipe script" (write fresh non-staff wipe + staff backfill).
- **C.2 implementation order recommendation:**
  1. AI Disclosure Modal (Step 0) + middleware — minimal change, proves the `record_consent('ai_disclosure', ...)` write path end-to-end
  2. Profile Edit extension — adds 3 fields, exercises the M3 history signal
  3. Step 3 amendment — rewrites view to call `record_consent` instead of boolean writes
  4. AILST T0 (Step 4) — biggest piece, 4 pages + state machine + scoring
  5. Module gating injection — small, but depends on T1/T2 routes existing
- **Operational notes (carried forward):**
  - `PYTHONIOENCODING=utf-8` for any Bash `manage.py shell` invocation (TD-005).
  - Path discipline: absolute paths under `C:/Users/dourv/unesco_ai_pd/`. Worktree shell `cwd` flips mid-session.
  - Backup before any DB-affecting work: even though C.2 is mostly views, any test data setup that writes to the DB warrants a snapshot. Standing rule.
  - Memory files at `C:/Users/dourv/.claude/projects/C--Users-dourv-unesco-ai-pd/memory/` are loaded automatically.
- **C.2 Pre-flight checklist for John:**
  - CP 7 copy text: be ready to review legal wording when Claude Code drafts the modal
  - CP 10 IRB: contact IHU IRB office to know whether they have a boilerplate or accept a custom draft
  - CP 8 mobile: have a phone available for visual sanity-check of the Likert layout
  - CP 11: decide whether to wipe test users now (cleaner C.2 testing) or after C.2 ships (no impact on view/template work)

---

*End of session log. Resume in next session with John's "C.2 design" or "CP 11 wipe script" cue.*
