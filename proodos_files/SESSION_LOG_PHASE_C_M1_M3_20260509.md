# Phase C Session Log — M1 through M3

**Date:** 2026-05-09
**Session scope:** Phase C migrations M1, M2, Γ.1, M3
**Author:** Claude Code session (continuity-of-care log)

---

## Status counter

| # | Description | Status |
|---|---|---|
| Scaffolding | apps.compliance + apps.ailst created, registered in INSTALLED_APPS, plan markdown drafted | **DONE** commit `09d0e08` |
| M1 | compliance/0001 — extend `consent_records.valid_consent_type` constraint | **OBSOLETE** — placeholder no-op (consent_records was dropped in Γ.1). Original SQL preserved in commit `06357f2`. |
| M2 | users/0007 — add 4 personalization columns to `teacher_profiles` | **APPLIED** 2026-05-09 |
| Γ.1 | compliance/0002 — drop pre-Phase-C dead schema (22 tables + 2 functions) | **APPLIED** 2026-05-09 |
| M3 | users/0008 — `TeacherProfileHistory` + signal-based change tracker | **APPLIED** 2026-05-09 |
| M4 | ailst/0001 — `ailst_items` table + EN seed from paper Appendix | Pending |
| M5 | ailst/0002 — `ailst_responses` table | Pending |
| M6 | compliance/0003 (NEW) — Django `ConsentRecord` model with FK to `auth_user`. Replaces the dropped raw-SQL `consent_records`. Slot AFTER M5, BEFORE C.2 implementation, so the AI Disclosure middleware (Step 0) writes to it on first deployment. | Pending |

## Commits (this session)

| Commit | Title |
|---|---|
| `c5818ef` | Phase C M2: add personalization fields to teacher_profiles |
| `02db101` | Phase C Γ.1: drop pre-Phase-C dead schema |
| `bbe478d` | Phase C M3: TeacherProfile change tracking via signal-driven history table |

Earlier (prior session, baseline):
- `09d0e08` Phase C: scaffold compliance + ailst apps and migration plan
- `06357f2` Phase C M1: extend consent_records.valid_consent_type for ai_disclosure (now obsoleted by Γ.1; SQL preserved here for forensic reference)

## Key reference paths

| Artefact | Path |
|---|---|
| Migration plan (living) | `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` |
| Dead schema audit | `audits/DEAD_SCHEMA_AUDIT_20260509.md` |
| Audit scratch (DB inventory) | `audits/_db_inventory_raw.txt`, `audits/_db_functions_views.txt` |
| Phase C hand-off (original chat session) | `~/Downloads/PHASE_C_HANDOFF_FOR_CLAUDE_CODE.md` |
| AILST source paper | `~/Desktop/ΔΙΔΑΚΤΟΡΙΚΗ ΔΙΑΤΡΙΒΗ/ΕΡΓΑΣΙΕΣ/ΤΕΛΙΚΟ ΣΥΣΤΗΜΑ ΕΠΙΜΟΡΦΩΣΗΣ/ΒΙΒΛΙΟΓΡΑΦΙΑ/Development_and_validation_of_the_Artificial_Intel-1-1.pdf` |

## Backup files (RETAIN UNTIL post-2027)

Per audit Section 10 retention rule (dissertation IRB defensibility), all 4 pre-migration backup SQL files at repo root MUST be retained unchanged until pilot study completes:

| File | Size | Created before |
|---|---|---|
| `pre_migration_backup_phaseC_M1_20260509.sql` | 50.6 MB | M1 apply |
| `pre_migration_backup_phaseC_M2_20260509.sql` | 50.6 MB | M2 apply |
| `pre_migration_backup_phaseC_GAMMA1_20260509.sql` | 50.6 MB | Γ.1 apply |
| `pre_migration_backup_phaseC_M3_20260509.sql` | ~45 MB | M3 apply (smaller — dead schema gone) |

All committed to repo. **DO NOT delete. DO NOT consolidate.**

## Challenge Points — status

### Resolved this session

| CP | Resolution |
|---|---|
| **CP 1** (constraint dry-run) | Resolved at M1 dry-run: `consent_records` had 0 rows; no constraint conflict possible. Subsequently moot after Γ.1 dropped the table. |
| **CP 2** (special needs vocabulary) | 7 values: `learning_disability, behavioural_support, physical_disability, language_minority, gifted, socioeconomic_disadvantage, none`. Multi-select; `'none'` exclusive. Encoded in `TeacherProfile.student_population_special_needs` JSONField (M2). |
| **CP 3** (history fields tracked) | 11 fields: subject_area, grade_level, teaching_years, school_location, average_class_size, ai_experience, ai_tools_used, primary_goals, current_curriculum_pressure, student_population_special_needs, institutional_ai_policy. (10 originally proposed + `ai_tools_used` added at M3 design.) |
| **CP 4** (reverse-scored items) | Confirmed K1, A3, E3. Verified verbatim against paper Appendix. |
| **CP 5** (scoring direction) | Likert: Fully applicable=5, Completely not applicable=1. Reverse K1/A3/E3 only at compute time (`scored = 6 - raw`). UI: 5 radio buttons with verbal anchors, no numeric labels. Storage: raw 1-5 in JSONB. |
| **CP 6** (overall_score formula) | Mean of factor means. Reasoning: 4-factor structure is the paper's theoretical claim; mean of items would impose 28/28/22/22 weighting from item count alone. |
| **CP 9** (gating injection point) | `apps/modules/views.py:796`, immediately after `progress.mark_tab_complete(...)`. Conditions: `progress.completed_at` just-set AND `code in ('M5', 'M15')`. Idempotency via `AilstResponse.objects.filter(user, timepoint, completed_at__isnull=False).exists()`. |
| **CP 11** (test user retroactive policy) | Decision: **Option B** — wipe non-staff test users + backfill `ai_disclosure_acknowledged_at = NOW()` on staff. **NOT YET EXECUTED.** Original reset script (`phaseC_M2_reset_test_users.py`) crashed on dead-schema FK violation and was deleted in Γ.1 commit. **Fresh script must be written post-Γ.1, before pilot starts.** |

### Pending — to address in subsequent migrations / steps

| CP | Resolved at | Notes |
|---|---|---|
| **CP 7** (AI disclosure copy text) | C.2 Step 0 implementation | EU AI Act Article 50(1) wording; legal review by John before commit. |
| **CP 8** (mobile Likert rendering) | C.2 Step 4 implementation | Must preserve measurement (5 radio + verbal anchors); only visual layout may change. |
| **CP 10** (IRB consent text) | C.2 Step 3 amendment | Option B chosen — Claude Code drafts custom; John takes to IHU IRB office for approval. John has not yet applied. |

## Tech debt observations (NOT for Phase C)

1. **Timezone-naive timestamps** on legacy `teacher_profiles` columns (`profile_completion_date`, `created_at`, `consent_timestamp`). RuntimeWarnings during test runs but no functional issue. Recorded in memory `reference_codebase_quirks.md` as deferred Phase H tech debt.
2. **Tier 3 backup tables remain** (15 tables + 3 views + 2 trigger functions). Out of Phase C scope. Phase H cleanup. See `audits/DEAD_SCHEMA_AUDIT_20260509.md` §1.1 Tier 3.
3. **`rag_query_system.py:26`** prints checkmark `✓` which crashes under `cp1253`-encoded shells (Greek Windows default). Workaround: `PYTHONIOENCODING=utf-8`. Permanent fix: `sys.stdout.reconfigure(encoding='utf-8')` at top of file. Not Phase C scope.

## Continuity guidance for next session

- **Resume with:** "M4 design".
- **Open implementation questions for M4** (already drafted in plan §6.4):
  - Schema for `ailst_items` (i18n-ready, EN seed at C.2 launch, EL later).
  - Item ordering convention: `item_number` 1-36 monotonic vs paper codes (`P1..P10, K1..K10, A3..A10, E1+E3..E10`). Default: 1-36 monotonic with `paper_code` field for semantic identifier.
  - Seed format: hardcoded list inside `RunPython` operation in the migration, vs external `apps/ailst/seeds/ning_2025_v1_en.json` loaded at migration time. Default proposal: external JSON for cleanliness + version control of seed data.
- **Operational notes:**
  - Use `PYTHONIOENCODING=utf-8` for any `manage.py shell` invocation in Bash (cp1253 shell encoding issue).
  - Path discipline: absolute paths under `C:/Users/dourv/unesco_ai_pd/`. Worktree shell `cwd` flips mid-session.
  - Backup before apply: `pg_dump > pre_migration_backup_phaseC_M4_<date>.sql`. Standing rule, no exceptions.
  - Memory files at `C:/Users/dourv/.claude/projects/C--Users-dourv-unesco-ai-pd/memory/` are loaded automatically; consult `project_proodos.md`, `feedback_workflow.md`, `reference_codebase_quirks.md`, `reference_phaseC.md`, `user_john.md` for project context, John's collaboration style, and codebase quirks.

---

*End of session log. Resume in next session with John's "M4 design" cue.*
