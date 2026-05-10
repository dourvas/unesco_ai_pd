# Phase C Session Log — M4 — 10 May 2026

**Date:** 2026-05-10
**Session scope:** Phase C migration M4 (AILST instrument items + EN seed)
**Author:** Claude Code session (continuity-of-care log)
**Companion log:** `proodos_files/SESSION_LOG_PHASE_C_M1_M3_20260509.md` (covers M1, M2, Γ.1, M3 from the previous day)

---

## Phase C status — end of day 2026-05-10

| # | Description | Status |
|---|---|---|
| Scaffolding | apps.compliance + apps.ailst, INSTALLED_APPS, plan markdown | DONE commit `09d0e08` |
| M1 | compliance/0001 — extend `consent_records.valid_consent_type` | **OBSOLETE** placeholder (consent_records dropped in Γ.1; original SQL preserved in commit `06357f2`) |
| M2 | users/0007 — `teacher_profiles` +4 personalization columns | **APPLIED** — commit `c5818ef` |
| Γ.1 | compliance/0002 — drop pre-Phase-C dead schema (22 tables + 2 SQL functions) | **APPLIED** — commit `02db101` |
| M3 | users/0008 — `TeacherProfileHistory` + Django signal-based change tracker | **APPLIED** — commit `bbe478d` |
| M4 | ailst/0001 (schema) + ailst/0002 (EN seed, Ning et al. 2025 v1) | **APPLIED today** — commit `223ebf3` |
| M5 | ailst/0003 — `ailst_responses` (per-user, per-timepoint) | **Pending** |
| M6 | compliance/0003 (NEW) — Django `ConsentRecord` model with FK to `auth_user` | **Pending** — slot AFTER M5, BEFORE C.2 implementation |

## Open design questions for M5 (next session)

| Question | Notes |
|---|---|
| Scoring computation timing | Eager (compute on submit, store factor + overall scores in row) vs lazy (compute on first read from JSONB). Trade-off: storage vs reproducibility under formula change. Default proposal: eager + recompute helper. |
| Partial-state handling | Resume mid-instrument: 4 pages (perception/knowledge_skills/applications_innovation/ethics), each with ~9 items. Save partial after each page. Schema implication: `responses` JSONB allowed to have <36 keys; `completed_at` NULL until all 36 answered. |
| Derived FK to ailst_items | YES (each response key joined to ailst_items via paper_code for data integrity check at scoring time) vs NO (looser coupling, allow scoring even if items table is in flux). Default proposal: NO formal FK; validate via app-layer guard at scoring time. JSONB keys are paper_codes — checked at compute. |
| JSONB responses key format | Already decided in M4: paper_codes (`{"P1": 4, "K10": 2, ...}`). M5 needs no further decision here. |

## Open design questions for M6 (post-M5)

Will be discussed when M5 is done. M6 (Django `ConsentRecord` model) must align with the C.2 AI Disclosure middleware flow (Step 0 of the redesigned onboarding) so that one acknowledgment writes one row. Current open items:

- FK to `auth_user(id)` (replaces dead schema's separate `users(id)` FK).
- Reuse of the constraint vocabulary `('platform_use', 'research_participation', 'data_sharing', 'video_recording', 'ai_disclosure')`.
- `consent_text` field stores the version-locked verbatim text the user agreed to (not just a version reference).
- `ip_address` field redacted after 30 days (matches the dropped `cleanup_old_analytics()` policy, but reimplemented in Python).

## Commits this session

| Commit | Title |
|---|---|
| `223ebf3` | Phase C M4: AILST instrument items model + EN seed (Ning et al. 2025 v1) |

(Earlier commits in Phase C are documented in the companion log.)

## Reference paths

| Artefact | Path |
|---|---|
| Migration plan (living) | `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` |
| Dead schema audit | `audits/DEAD_SCHEMA_AUDIT_20260509.md` |
| AILST source paper | `~/Desktop/ΔΙΔΑΚΤΟΡΙΚΗ ΔΙΑΤΡΙΒΗ/ΕΡΓΑΣΙΕΣ/ΤΕΛΙΚΟ ΣΥΣΤΗΜΑ ΕΠΙΜΟΡΦΩΣΗΣ/ΒΙΒΛΙΟΓΡΑΦΙΑ/Development_and_validation_of_the_Artificial_Intel-1-1.pdf` |
| AILST EN seed (live) | `apps/ailst/seeds/ning_2025_v1_en.json` |
| AILST seed-invariant tests | `apps/ailst/tests.py` (7 tests, all passing as of `223ebf3`) |
| Settings pin | `config/settings.py` line near end: `AILST_CURRENT_VERSION = 'ning_2025_v1'` |
| Companion session log | `proodos_files/SESSION_LOG_PHASE_C_M1_M3_20260509.md` |

## Backup files (RETAIN UNTIL post-2027)

Per audit Section 10 retention rule, **all 5** pre-migration backup SQL files at repo root MUST be retained unchanged until pilot study completes. Originally noted as 4 in the M1-M3 session log; M4 adds the 5th today.

| File | Size | Created before |
|---|---|---|
| `pre_migration_backup_phaseC_M1_20260509.sql` | 50.6 MB | M1 apply |
| `pre_migration_backup_phaseC_M2_20260509.sql` | 50.6 MB | M2 apply |
| `pre_migration_backup_phaseC_GAMMA1_20260509.sql` | 50.6 MB | Γ.1 apply |
| `pre_migration_backup_phaseC_M3_20260509.sql` | ~45 MB | M3 apply (smaller — dead schema gone) |
| `pre_migration_backup_phaseC_M4_20260510.sql` | ~21K lines, ~33 MB | M4 apply (smaller — dead schema gone, AILST tables not yet created) |

All committed to git. **DO NOT delete. DO NOT consolidate.** Phase H may move them to `backups/phase_c/` subdirectory but cannot remove them from history.

## Settings pin

```
AILST_CURRENT_VERSION = 'ning_2025_v1'
```

In `config/settings.py`, near the end of file. The AI Disclosure / AILST UI (C.2) reads this to determine which `instrument_version` to serve for new T0 administrations. In-progress `AilstResponse` rows preserve their own `instrument_version` (implicit pin), so version transitions never break in-flight users.

## Continuity guidance for next session

- **Resume with:** "M5 design".
- **First decision in M5 design:** scoring computation timing (eager vs lazy). Recommend eager: compute factor + overall scores at submit time, store alongside JSONB responses. Reproducibility preserved because raw `responses` JSONB is also stored — if formula ever changes, recompute from raw.
- **Operational notes (carried forward from M1-M3 log):**
  - `PYTHONIOENCODING=utf-8` for any `manage.py shell` invocation in Bash (cp1253 shell encoding issue).
  - Path discipline: absolute paths under `C:/Users/dourv/unesco_ai_pd/`. Worktree shell `cwd` flips mid-session.
  - Backup before apply: `pg_dump > pre_migration_backup_phaseC_M5_<date>.sql`. Standing rule, no exceptions.
  - Memory files at `C:/Users/dourv/.claude/projects/C--Users-dourv-unesco-ai-pd/memory/` are loaded automatically.

---

*End of session log. Resume in next session with John's "M5 design" cue.*
