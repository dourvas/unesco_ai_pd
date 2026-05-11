# Phase C — Migration Plan v1

**Date:** 2026-05-09
**Author:** Claude Code (read-only sprint output)
**Supersedes:** §4.2 of `PHASE_C_HANDOFF_FOR_CLAUDE_CODE.md` (only the migration sub-section; the rest of the hand-off remains authoritative)
**Approved by:** John Dourvas (pending review of this document)
**Critical deadline:** 2 August 2026 (EU AI Act Article 50)

---

## 0. Why this document exists

The hand-off doc §4.2 listed five migrations against an assumed schema baseline (`database_schema_current.sql`) which does not exist as a file. The read-only sprint also surfaced that two artefacts (`consent_records` table and `anonymize_user` function) live in the live DB as **raw SQL** outside Django's migration system, and that `teacher_profiles` has 31 columns (not 30 — `blog_subject_filter_preference` was added in `users/0006`).

Decisions taken in chat session reset two items: CP 11 flipped from Option A (mark + skip) to **Option B (wipe non-staff test users)**, removing the `pre_phase_c_user` flag from Migration 2.

This document captures the corrected sequence with all currently-resolved Challenge Points incorporated. Pending CPs are listed with the migration / step where each will be resolved.

---

## 1. Standing rules (apply to every migration)

1. **Backup before first apply.** `pg_dump unesco_ai_teacher_pd > pre_migration_backup_phaseC_<MNN>_<YYYYMMDD>.sql` saved at repo root.
2. **Dry-run first.** `python manage.py migrate <app> <migration_number> --plan` and `manage.py sqlmigrate <app> <migration_number>` reviewed before apply.
3. **One migration at a time.** After apply, stop. Browser test + verification by John before next migration.
4. **No `--no-verify`, no hooks bypass.** Standard project convention.
5. **All artefacts in English.** Code, schema names, comments. Greek only in chat / design discussion.
6. **Path discipline.** All file edits at absolute paths under `C:/Users/dourv/unesco_ai_pd/`. Never trust shell `cwd`.
7. **Tone in commit messages and code comments:** factual, no `successfully implemented` / emojis / superlatives.

---

## 2. Decision register

### 2.1 Resolved

| CP | Decision |
|----|----------|
| CP 2 | `student_population_special_needs` vocabulary: `["learning_disability", "behavioural_support", "physical_disability", "language_minority", "gifted", "socioeconomic_disadvantage", "none"]`. Multi-select checkbox UI. `none` exclusive (disables others client-side). |
| CP 4 | Reverse-scored items: **K1, A3, E3** (verified verbatim against paper Appendix). |
| CP 5 | Likert anchor mapping: `Fully applicable=5, Applicable=4, Uncertain=3, Not applicable=2, Completely not applicable=1`. Storage: raw 1-5 in `responses` JSONB. Reversal for K1/A3/E3 only at compute time (`scored = 6 - raw`). UI: 5 radio buttons with verbal anchors, no numeric labels. |
| CP 6 | `overall_score` = mean of factor means (not mean of items). Rationale: 4-factor structure is the paper's theoretical claim; mean of items would impose 28/28/22/22 weighting from item count alone. |
| CP 9 | Module-completion gating injection point: `apps/modules/views.py:796` (immediately after `progress.mark_tab_complete(...)` returns). Conditions: `progress.completed_at` was just set in this call AND `code in ('M5', 'M15')`. Idempotency: skip redirect if `AilstResponse.objects.filter(user=request.user, timepoint=tp, completed_at__isnull=False).exists()`. |
| CP 11 | **Option B — wipe.** All non-staff test users deleted. Staff/admin accounts preserved with `ai_disclosure_acknowledged_at = now()` set manually so middleware does not block them. Migration 2 does **not** add `pre_phase_c_user` flag. |
| App layout | Two new apps: `apps/ailst/` (instrument + scoring + analytics) and `apps/compliance/` (middleware + AI markers + privacy dashboard + Article 50 PDF/HTML page). |
| Backup discipline | `pg_dump pre_migration_backup_phaseC_<...>.sql` is mandatory, not optional. |

### 2.2 Pending — resolved during the noted step

| CP | Resolved at | What is still open |
|----|-------------|---------------------|
| CP 1 | Migration 1 dry-run | Confirm no existing `consent_records` row violates the new constraint. |
| CP 3 | Migration 3 design | Final list of fields tracked in `teacher_profile_history`. Suggested set in §6.3, awaiting confirm. |
| CP 7 | C.2 Step 0 implementation | Final wording of AI Disclosure copy text. Legal review by John. |
| CP 8 | C.2 Step 4 implementation | Mobile Likert layout — must preserve measurement (5 radio + verbal anchors), only visual variant changes. |
| CP 10 | C.2 Step 3 consent text | IRB boilerplate from IHU. John to consult IHU IRB office. Phase C Option B = custom draft from Claude Code, John takes to committee. |

---

## 3. Codebase audit — corrections to hand-off §4.1

| Hand-off claim | Actual |
|----------------|--------|
| `database_schema_current.sql` exists in repo | Does not exist. Source of truth = Django migrations + `proodos_backup_m15_complete_20260417_1152.sql` for raw-SQL artefacts. |
| `teacher_profiles` has 30 columns | **31** columns. Missing from hand-off list: `blog_subject_filter_preference` (added in `apps/users/migrations/0006_*`, Phase A Tier 3). |
| `consent_records` is an existing table | **Confirmed exists in live DB** (backup line 740). Created via raw SQL outside Django migrations. No Django model. Migration 1 must use `migrations.RunSQL`, not `AlterField`. |
| `anonymize_user(p_user_id)` is an existing function | **Confirmed exists in live DB** (backup line 80). Comment: `'GDPR compliance: Anonymize user while preserving research data'`. C.4 will call this via raw SQL `cursor.execute("SELECT anonymize_user(%s)", [user_id])`. |
| Onboarding flow is in a dedicated `onboarding` app | Onboarding views live in `apps/users/views.py`. URLs in `apps/users/urls.py`. Templates in `templates/onboarding/` (top-level templates dir, NOT per-app). |
| `consent_records` is wired into onboarding flow | **It is not.** `onboarding_summary` view writes `consent_timestamp` on `teacher_profiles` only. The `consent_records` table is orphaned (only `cleanup_old_analytics()` SQL function references it). Phase C will activate it. |

---

## 4. Pre-migration scaffolding (one-shot, before Migration 1)

These steps create the new apps and register them. Not migrations, but prerequisites.

### 4.1 Create `apps/compliance/`

```
python manage.py startapp compliance apps/compliance
```

Edit `apps/compliance/apps.py` to set `name = 'apps.compliance'`. Add to `INSTALLED_APPS` in `config/settings.py` after `apps.peer_blog`.

### 4.2 Create `apps/ailst/`

```
python manage.py startapp ailst apps/ailst
```

Same convention. Add to `INSTALLED_APPS` after `apps.compliance`.

### 4.3 Verify

```
python manage.py check
python manage.py showmigrations
```

Both new apps should appear with no migrations yet.

🛑 **Pause point:** John verifies new apps registered cleanly before Migration 1 begins.

---

## 5. Migration sequence — overview

Updated 2026-05-09 post-Γ.1: M1 obsoleted; new M6 added for `ConsentRecord` Django model after pre-Phase-C dead schema was dropped.

| # | App | Type | Purpose | Status |
|---|-----|------|---------|--------|
| M1 | compliance | RunSQL | Extend `consent_records.valid_consent_type` to include `'ai_disclosure'`. | **OBSOLETE** — no-op placeholder. Dead schema dropped in Γ.1 |
| M2 | users | AddField | Add 4 new columns to `teacher_profiles`. | **APPLIED** 2026-05-09 |
| Γ.1 | compliance | RunSQL | Drop pre-Phase-C dead schema (22 tables + 2 functions). | **APPLIED** 2026-05-09 |
| M3 | users | CreateModel + signal | Create `teacher_profile_history` + Django signal in `apps/users/signals.py`. | **APPLIED** 2026-05-09 |
| M4 | ailst | CreateModel + RunPython | Create `ailst_items` + seed EN-only data from paper Appendix. | Pending |
| M5 | ailst | CreateModel + helper + tests | Create `ailst_responses` + `apps/ailst/scoring.py` + recompute command + 9 added tests. | **APPLIED** 2026-05-10 |
| M6 (NEW) | compliance | CreateModel + data migration + signal | `ConsentRecord` Django model with FK to `auth_user`, `valid_consent_type` DB CHECK, `is_active` property. Plus data migration that backfills 6 rows from existing TeacherProfile booleans (version `v0_pre_phase_c`). Plus `sync_teacher_profile_booleans` signal that keeps the legacy boolean cache in sync. Plus `record_consent`/`revoke_consent` service helpers and `redact_old_consent_ips` management command. | **APPLIED** 2026-05-10 |

Detailed design per migration in §6.

---

## 6. Migration designs

### 6.1 Migration 1 — `apps/compliance/migrations/0001_initial.py`

**Status:** APPLIED 2026-05-09 12:47:45 UTC, commit `06357f2`. **OBSOLETED** by Γ.1 on 2026-05-09 14:17:48 UTC: extended a CHECK constraint on `consent_records`, which was dropped along with the entire dead schema. The 0001_initial.py file is preserved on disk as an empty no-op placeholder (Django migration graph requires importable nodes for any migration in `dependencies`); the original RunSQL forward + reverse blocks remain in commit `06357f2` for forensic reference. Its `django_migrations.id=43` row is left in place. Backup at repo root: `pre_migration_backup_phaseC_M1_20260509.sql` (50.6 MB, 24067 lines).

**Type:** `migrations.RunSQL` (because `consent_records` is raw-SQL only).

**Forward SQL:**
```sql
ALTER TABLE consent_records DROP CONSTRAINT valid_consent_type;
ALTER TABLE consent_records
    ADD CONSTRAINT valid_consent_type CHECK (
        consent_type IN (
            'platform_use',
            'research_participation',
            'data_sharing',
            'video_recording',
            'ai_disclosure'
        )
    );
```

**Reverse SQL:**
```sql
ALTER TABLE consent_records DROP CONSTRAINT valid_consent_type;
ALTER TABLE consent_records
    ADD CONSTRAINT valid_consent_type CHECK (
        consent_type IN (
            'platform_use',
            'research_participation',
            'data_sharing',
            'video_recording'
        )
    );
```

**Pre-apply check (CP 1):**
```sql
SELECT consent_type, COUNT(*)
FROM consent_records
GROUP BY consent_type;
```
Expected: only the 4 existing values. If any row has a different value, halt and report.

**Post-apply check:**
```sql
\d+ consent_records
-- Verify constraint includes 'ai_disclosure'
```

### 6.2 Migration 2 — `apps/users/migrations/0007_*.py`

**Status:** APPLIED 2026-05-09 13:34 UTC. Filename `0007_teacherprofile_ai_disclosure_acknowledged_at_and_more.py`. 4 AddField operations completed in single transaction. All 6 existing `teacher_profiles` rows extended with NULL for the 3 nullable columns and `[]` for `student_population_special_needs`. `pre_phase_c_user` flag NOT added (CP 11 Option B). Pre-apply backup at repo root: `pre_migration_backup_phaseC_M2_20260509.sql` (50.6 MB).

**Type:** `AlterField`-style (Django model changes).

**Model changes** (in `apps/users/models.py` under `TeacherProfile`):

```python
# AI Disclosure (compliance)
ai_disclosure_acknowledged_at = models.DateTimeField(
    null=True, blank=True,
    verbose_name="AI Disclosure Acknowledged At",
    help_text="Timestamp of acknowledgment of EU AI Act Article 50 disclosure modal."
)

# Phase C personalization fields
CURRICULUM_PRESSURE_CHOICES = [
    ('low', 'Low — flexible curriculum'),
    ('medium', 'Medium — standard pacing'),
    ('high', 'High — strict curriculum coverage demands'),
    ('variable', 'Variable — depends on term / class'),
]
current_curriculum_pressure = models.CharField(
    max_length=20, choices=CURRICULUM_PRESSURE_CHOICES,
    null=True, blank=True,
    verbose_name="Current Curriculum Pressure"
)

student_population_special_needs = models.JSONField(
    default=list, blank=True,
    verbose_name="Student Population Special Needs",
    help_text="Multi-select. Allowed values: learning_disability, behavioural_support, physical_disability, language_minority, gifted, socioeconomic_disadvantage, none."
)

INSTITUTIONAL_AI_POLICY_CHOICES = [
    ('none', 'No policy'),
    ('restrictive', 'Restrictive — AI use discouraged'),
    ('permissive', 'Permissive — AI use allowed'),
    ('explicit_supportive', 'Explicit & supportive — AI use encouraged'),
    ('unknown', 'I do not know'),
]
institutional_ai_policy = models.CharField(
    max_length=30, choices=INSTITUTIONAL_AI_POLICY_CHOICES,
    null=True, blank=True,
    verbose_name="Institutional AI Policy"
)
```

**No `pre_phase_c_user` field** (CP 11 Option B chosen).

**Post-apply data step (one-shot script `scripts/phaseC_reset_test_users.py`):**

```
1. List all auth_user where is_staff = false and is_superuser = false → wipe (delete + cascade)
   - Use anonymize_user(id) instead of hard delete to preserve referential integrity in ailst_items, etc. (none yet, but future-proof)
   - OR simply DELETE FROM auth_user WHERE is_staff=false AND is_superuser=false (faster, all FKs cascade)
2. For all remaining auth_user (staff/superuser):
   UPDATE teacher_profiles SET ai_disclosure_acknowledged_at = NOW() WHERE user_id = ...
3. Insert one consent_records row per staff user with consent_type='ai_disclosure', granted=true, version='v1', consent_text='Backfilled by Phase C reset (CP 11 Option B)'
```

This script runs **after** Migration 2 (so the column exists) and **before** any user-facing Phase C UI is enabled.

🛑 **Decision needed before this step:** hard DELETE or `anonymize_user()`? Hard delete is cleaner since these are throwaway test accounts. Default proposal: hard DELETE.

### 6.3 Migration 3 — `apps/users/migrations/0008_*.py` + `apps/users/signals.py`

**Status:** APPLIED 2026-05-09. Filename `0008_teacherprofilehistory.py`. CreateModel for `TeacherProfileHistory` + 4 indexes (PK, user FK, change_event_id, idx_profile_history_user_time, idx_profile_history_field) executed in single transaction. Pre-apply backup: `pre_migration_backup_phaseC_M3_20260509.sql` (50.6 MB).

**TRACKED_FIELDS finalized as 11 fields** (CP 3 resolved 2026-05-09): subject_area, grade_level, teaching_years, school_location, average_class_size, ai_experience, ai_tools_used, primary_goals, current_curriculum_pressure, student_population_special_needs, institutional_ai_policy. Excluded: timestamps, admin bools, free-text, demographics, name, UI preferences, ai_disclosure_acknowledged_at (set once).

**Schema decisions (locked):**
- old_value/new_value: TEXT NOT NULL with JSON-serialized values; literal `'null'` string for Python None (no SQL NULL).
- change_event_id: UUID, indexed, generated fresh per save event in pre_save.
- change_source: optional CharField default `''`, set by call sites that want to label the change (e.g. `instance._change_source = 'profile_edit'`).
- 2 indexes beyond auto-generated FK/PK: `idx_profile_history_user_time` (user, -changed_at) and `idx_profile_history_field` (field_name).

**Signal mechanism (locked):** pre_save captures diffs to `instance._pending_history` + fresh `_change_event_id`; post_save bulk_creates rows on success then clears all transients (`_pending_history`, `_change_event_id`, `_change_source`). created=True path skips. Comparison is plain `==`.

**Verification (all 4 tests passed):**
1. Single field change → 1 history row, valid UUID, change_source propagated ✓
2. Multi-field save (3 fields) → 3 rows sharing one change_event_id, change_source uniform ✓
3. No-change save → 0 rows ✓
4. New profile (created=True) → 0 rows; temp user not committed (rollback clean) ✓

**Model:**
```python
class TeacherProfileHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='profile_history')
    field_name = models.CharField(max_length=50)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teacher_profile_history'
        indexes = [
            models.Index(fields=['user', '-changed_at'], name='idx_profile_history_user_time'),
            models.Index(fields=['field_name'], name='idx_profile_history_field'),
        ]
```

**Signal (`apps/users/signals.py`):** `pre_save` on `TeacherProfile`. For each tracked field, compare old vs new; if differs, queue an insert into `TeacherProfileHistory`. Connect in `apps/users/apps.py::ready()`.

**CP 3 — fields tracked (proposal, awaiting confirm):**

```
TRACKED_FIELDS = {
    'subject_area', 'grade_level', 'teaching_years',
    'school_location', 'average_class_size',
    'ai_experience', 'primary_goals',
    'current_curriculum_pressure',
    'student_population_special_needs',
    'institutional_ai_policy',
}
```

Skipped: timestamps (`created_at`, `updated_at`, `last_profile_update`, `consent_timestamp`, `profile_completion_date`), administrative bools (`profile_completed`, `profile_skipped`), free-text (`notes`, `ai_teaching_integration`), demographics (`age_range`, `gender`, `language_primary`), name fields (`first_name`, `last_name`, `display_name`).

🛑 **Decision at M3:** confirm the 10 tracked fields above.

### 6.4 Migration 4 — `apps/ailst/migrations/0001_initial.py` + `0002_seed_ailst_en.py`

**Status:** APPLIED 2026-05-10. Schema (0001_initial) + EN data seed (0002_seed_ailst_en) split into two migrations for separation of concerns and easier future i18n. Schema introduces `paper_code` field (additional to `item_number`) so `AilstResponse.responses` JSONB keys can be joined back to items. Five invariants enforced in seed loader: file present, exactly 36 items, exactly K1/A3/E3 reverse-scored, paper_codes match the 36-code identity set, `_meta.removed_items` matches `{A1,A2,E2,E6}`. All 7 unit tests pass on fresh test DB. `AILST_CURRENT_VERSION = 'ning_2025_v1'` added to `config/settings.py` as explicit version pin. Pre-apply backup: `pre_migration_backup_phaseC_M4_20260510.sql` (~21K lines, smaller than earlier backups since dead schema is gone).

**Models:**
```python
class AilstItem(models.Model):
    item_number = models.IntegerField()
    factor = models.CharField(max_length=30, choices=[
        ('perception', 'AI Perception'),
        ('knowledge_skills', 'AI Knowledge and Skills'),
        ('applications_innovation', 'AI Applications and Innovation'),
        ('ethics', 'AI Ethics'),
    ])
    language = models.CharField(max_length=5, choices=[('en', 'English'), ('el', 'Greek')])
    item_text = models.TextField()
    is_reverse_scored = models.BooleanField(default=False)
    instrument_version = models.CharField(max_length=20, default='ning_2025_v1')

    class Meta:
        db_table = 'ailst_items'
        unique_together = [('item_number', 'language', 'instrument_version')]
        indexes = [
            models.Index(fields=['language', 'instrument_version', 'factor', 'item_number'],
                         name='idx_ailst_items_lookup'),
        ]
```

**Plus a `RunPython` data migration** that seeds 36 EN items from paper Appendix verbatim. Item codes preserved (`P1..P10, K1..K10, A3..A10, E1, E3..E5, E7..E10`). `is_reverse_scored=True` for `K1, A3, E3` only.

**Item ordering note:** `item_number` will be 1-36 monotonic for storage simplicity, with `factor` + paper code (e.g., `K1`) as the semantic identifier. Mapping table inside seed script. Confirm convention at M4 implementation time.

### 6.5 Migration 5 — `apps/ailst/migrations/0003_ailstresponse.py`

**Status:** APPLIED 2026-05-10 08:23:10 UTC. Numbering note: in plan §5 this was labelled "ailst/0002" but in practice ailst already has `0001_initial` (schema) + `0002_seed_ailst_en` (data) from M4, so M5 became `0003_ailstresponse`. Schema introduces `last_saved_at` (auto_now, for abandonment analytics) and a DB-level CHECK constraint `valid_timepoint` on the timepoint column (CP override: research-design constant warrants strict enforcement, unlike `language` which stays choices-only). Five derived score columns are nullable; raw `responses` JSONB is the source of truth and is recomputable via `manage.py recompute_ailst_scores --commit` (with optional `--user-id` and `--instrument-version` flags). Pure-function scoring helper at `apps/ailst/scoring.py::compute_factor_scores` enforces CP 5 (anchor: 5='Fully applicable', reverse K1/A3/E3) and CP 6 (overall = mean of factor means, defensive None if any factor lacks data). 16 unit tests (7 seed invariants + 5 scoring + 4 lifecycle) all pass on fresh test DB. Pre-apply backup: `pre_migration_backup_phaseC_M5_20260510.sql`.

**Model:**
```python
class AilstResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ailst_responses')
    timepoint = models.CharField(max_length=3, choices=[('T0','T0'),('T1','T1'),('T2','T2')])
    language = models.CharField(max_length=5, default='en')
    instrument_version = models.CharField(max_length=20, default='ning_2025_v1')

    perception_score = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    knowledge_skills_score = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    applications_innovation_score = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    ethics_score = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    overall_score = models.DecimalField(max_digits=4, decimal_places=2, null=True)

    responses = models.JSONField()  # {"P1": 4, "P2": 5, ..., "E10": 3}, raw 1-5
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ailst_responses'
        unique_together = [('user', 'timepoint')]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['timepoint']),
        ]
```

Scoring runs server-side on completion (not on partial save). Stored both raw responses and per-factor + overall computed scores so reproducibility holds even if the scoring formula is later revised — recompute from `responses` JSONB.

---

## 7. Per-migration verification template

Each migration ends with:

1. **Pre-apply state captured:** `pg_dump --schema-only --table=<table> ... > pre_<MNN>_state.sql`
2. **Apply:** `manage.py migrate <app>` (no `--fake`, no `--run-syncdb` shortcuts).
3. **Post-apply schema check:** `\d+ <table>` in `psql`. Compare to expected.
4. **Constraint test:** insert one valid row + one invalid row; expect second to fail.
5. **Rollback test:** `manage.py migrate <app> <prev>` succeeds; data unaffected for unrelated rows.
6. **Re-apply test:** `manage.py migrate <app>` is idempotent (no-op on already-applied).
7. **Browser test (when UI is connected):** Phase C migrations alone do not affect UI; first browser test happens after C.2 view + template work.
8. **Report back to chat:** status, schema diff, any anomaly.

---

## 8. New observations from codebase audit

These are not blocking, but worth surfacing.

1. `consent_records` orphaned. Currently nothing writes to it. C.2 + C.3 + C.4 each have new write paths into it (AI disclosure acknowledgment, AILST consent, possibly profile-edit consent updates). Worth a single helper `apps/compliance/services.py::record_consent(user, consent_type, granted, text, version)` to centralize the pattern.
2. `cleanup_old_analytics()` SQL function (backup line 174) updates `consent_records` to redact IPs after 30 days. Phase C must not break this — verify after Migration 1 that the function still parses correctly.
3. `anonymize_user(p_user_id)` is the canonical GDPR-compliant deletion. C.4 uses it as-is; do **not** create a parallel Django delete path.
4. `templates/onboarding/` is top-level (not under `apps/users/templates/`). Step 0 + Step 4 templates go there: `templates/onboarding/ai_disclosure.html`, `templates/onboarding/ailst_t0.html` (or 4 sub-templates per factor).
5. Onboarding session state uses `request.session['onboarding_step']` integer. Phase C extends to `>=4` once Step 4 is added; backward-compatible.
6. `mark_tab_complete` view is shared across all tabs/modules. Gating logic for M5/M15 must be conditional on `code` and `tab_name` to avoid firing on intermediate tab completions.
7. No existing `apps/users/signals.py`. Migration 3 will be the first signal in this app — set the precedent cleanly: register in `apps.UsersConfig.ready()`.

---

## 9. Open implementation questions for John

Resolved before starting Migration 1:

- **Q9.1** Hard delete vs `anonymize_user()` for non-staff test users in §6.2 post-apply step? (Default proposal: hard delete via `auth_user.delete()` cascading FKs.)
- **Q9.2** Confirm staff list to preserve. List of `is_staff=true OR is_superuser=true` accounts will be printed during the reset script for explicit John approval before deletion.

Resolved during their respective migrations (already deferred per §2.2):

- **Q9.3 (CP 1)** Pre-apply check on `consent_records` shows no surprises — at M1 dry-run.
- **Q9.4 (CP 3)** Final tracked fields list — at M3 design.
- **Q9.5 (CP 7)** AI disclosure copy text — at C.2 Step 0.
- **Q9.6 (CP 8)** Mobile Likert — at C.2 Step 4.
- **Q9.7 (CP 10)** IRB consent text — at C.2 Step 3 amendment, after John consults IHU IRB.

---

## 10. What happens after this plan is approved

1. Claude Code creates `apps/compliance/` and `apps/ailst/` (§4) and registers them in `INSTALLED_APPS`. Reports.
2. John verifies + approves.
3. Claude Code writes Migration 1 (compliance/0001) and runs **dry-run only**. Reports.
4. John reviews dry-run output (CP 1 check + sqlmigrate output) and approves apply.
5. Claude Code runs `pg_dump pre_migration_backup_phaseC_M1_<date>.sql` then applies Migration 1. Verifies. Reports.
6. John browser-tests (no UI change at this step, but `\d+ consent_records` confirms).
7. Same loop for M2 → M3 → M4 → M5.
8. After M5 verified: read-only Phase C foundation is in place. C.2 implementation (views, templates, middleware) begins next.

---

## 11. Document maintenance

This plan is a living document for the duration of Phase C migrations. Updates:

- After each migration applied, add a `**Status:** APPLIED <date>, commit <hash>` line under §6.X.
- If a CP changes during execution, update §2 and add a dated changelog entry below.
- Final `PHASE_C_IMPLEMENTATION_REPORT_<date>.md` (per hand-off §9) will reference this document by name and commit hash.

### Changelog

- **2026-05-09 — v1**: Initial plan, written from chat-session decisions and read-only sprint findings.
- **2026-05-09 — M1 applied**: Migration 1 (compliance/0001_initial) applied. CP 1 resolved: `consent_records` had 0 rows pre-apply, no constraint conflict possible. Constraint now accepts `ai_disclosure` plus the original 4 values. Negative test (`garbage_type`) confirmed rejected. No residual test data.
- **2026-05-09 — M2 applied**: Migration 2 (users/0007) added 4 Phase C personalization fields to `teacher_profiles`. `pre_phase_c_user` flag NOT added (CP 11 Option B). 6 existing rows extended with NULL/`[]` defaults. Pre-apply backup: `pre_migration_backup_phaseC_M2_20260509.sql`.
- **2026-05-09 — Γ.0 audit + pivot**: Attempted post-M2 reset script crashed on FK violation: `consent_records.user_id` references a separate raw-SQL `users` table, not Django `auth_user`. Investigation revealed an entire abandoned pre-Django architectural layer (22 tables + 2 SQL functions). Decision: drop the dead schema (Option Γ) but only after a documented read-only audit. See `audits/DEAD_SCHEMA_AUDIT_20260509.md` for verdict A CONFIRMED.
- **2026-05-09 — Γ.1 applied**: Migration `compliance/0002_drop_dead_schema` applied at 14:17:48 UTC. 22 dead tables and 2 SQL functions dropped. M1 placeholder rewritten as no-op. Reset script `phaseC_M2_reset_test_users.py` deleted. All 21 verified Django live-table row counts unchanged. `update_updated_at_column()` preserved. RAG triggers on `documents` and `rag_queries` preserved. Pre-Γ.1 backup: `pre_migration_backup_phaseC_GAMMA1_20260509.sql` (50.6 MB).
- **2026-05-10 — M4 applied**: Migration 4 split into `ailst/0001_initial` (schema) + `ailst/0002_seed_ailst_en` (data load). EN seed loaded from `apps/ailst/seeds/ning_2025_v1_en.json` with 5 enforced invariants (file present, exactly 36 items, K1/A3/E3 reverse, paper_codes identity, `_meta.removed_items` identity). 7 unit tests in `apps/ailst/tests.py` all pass. `AILST_CURRENT_VERSION='ning_2025_v1'` added to settings as explicit version pin. Schema introduces `paper_code` column for JSONB join in M5. Pre-apply backup: `pre_migration_backup_phaseC_M4_20260510.sql`.
- **2026-05-10 — M5 applied**: Migration `ailst/0003_ailstresponse` (renumbered from plan's "ailst/0002" because ailst already had 0001+0002 from M4). Schema deviations from plan §6.5: added `last_saved_at` (auto_now, abandonment analytics), composite index `(timepoint, completed_at)`, removed redundant `Index(fields=['user'])` (covered by unique_together), and DB-level CHECK constraint `valid_timepoint` (CP override: research-design constant). Score columns are derived/cached; raw `responses` JSONB is source of truth. Pure-function scoring helper `apps/ailst/scoring.py::compute_factor_scores` (CP 5 anchors + CP 6 mean-of-factor-means + defensive overall=None if any factor None). Management command `recompute_ailst_scores` with `--dry-run` / `--commit` / `--instrument-version` / `--user-id` flags. Tests extended to 16 (7 seed invariants + 5 scoring + 4 lifecycle), all pass on fresh test DB. Includes load-bearing regression test `test_anchor_mapping_high_value_means_high_tail` that guards CP 5 against silent flips. Pre-apply backup: `pre_migration_backup_phaseC_M5_20260510.sql`.
- **2026-05-10 — M6 applied**: Migrations `compliance/0003_consentrecord` (schema, table `compliance_consentrecord` with `valid_consent_type` DB CHECK + `is_active` property + 5-value vocabulary including `ai_disclosure`) and `compliance/0004_migrate_teacherprofile_consents` (data migration backfilling 6 rows from existing TeacherProfile booleans with `version='v0_pre_phase_c'`). REFACTOR-NOW decision (CP override of incremental proposal): Step 3 booleans on TeacherProfile become a sync-cache via `sync_teacher_profile_booleans` post_save signal in `apps/compliance/signals.py`; `revoke_consent` service uses per-row save() (not bulk update) so signals fire correctly. New `apps/compliance/services.py` with `record_consent` / `revoke_consent` / `migrate_legacy_teacher_consents` helpers. New management command `redact_old_consent_ips` with `--dry-run` / `--commit` / `--days` flags and `logger.info` event logging. Tests added to 16 in `apps/compliance/tests.py` (4 model + 4 service + 3 legacy-migration + 3 signal-sync + 2 IP-redaction). All pass. Post-apply verification: 6 backfilled rows, all `is_active=True`, all 6 users have TeacherProfile booleans matching canonical ConsentRecord state. Tech debt items recorded in new `proodos_files/TECH_DEBT_LOG.md` (TD-001 through TD-007). Pre-apply backup: `pre_migration_backup_phaseC_M6_20260510.sql`.
- **2026-05-10 — C.2.0 implemented (end of migration sequence; first view-layer piece)**: AI Disclosure Modal + middleware. New files: `apps/compliance/middleware.py` (`AIDisclosureMiddleware`, slot between Authentication and Messages middleware), `apps/compliance/views.py` (`ai_disclosure_view`, `ai_act_compliance_stub_view`), `apps/compliance/copy.py` (versioned consent text + bullets, `AI_DISCLOSURE_TEXT_V1_PRE_IRB`), `apps/compliance/urls.py`, `templates/onboarding/_locked_base.html` (no-nav modal layout), `templates/onboarding/ai_disclosure.html`, `templates/about/ai_act_compliance_stub.html`, `scripts/pre_deploy_c20_acknowledge_staff.py` (auto-ack script for staff/superuser accounts so deployment doesn't lock them out). Settings additions: `AI_DISCLOSURE_CURRENT_VERSION = 'v1_pre_irb'` + middleware registration. config/urls.py extended with compliance namespace. Bypass set per spec: disclosure URL itself, logout, login/register/landing, /admin/login + logout, /about/ai-act-compliance/, /privacy-policy/, /terms/, health endpoints, /static/, /media/. AJAX requests (X-Requested-With or Accept: application/json) get 403+JSON instead of 302 redirect. Tests extended to 29 in `apps/compliance/tests.py` (added `AIDisclosureMiddlewareTest` + `AIDisclosureViewTest`, including the load-bearing regression `test_stored_consent_text_matches_copy_module_exactly`). All 29 pass. Tech debt added: `TD-008` for C.4 revocation logic. Consent text v1_pre_irb is DRAFT pending IHU IRB review (CP 7); IRB submission is a parallel track to development. CP 8 (mobile Likert) and CP 10 (IRB Step 3 consent) still open, addressed at C.2.3 and C.2.2 respectively.
- **2026-05-10 — C.2.1 implemented**: Profile Edit extension. `apps/users/forms.py::ProfileEditForm` extended with the 3 Phase C personalization fields (M2 columns): `current_curriculum_pressure` (RadioSelect with prepended 'Prefer not to say' empty option, CharField nullable), `student_population_special_needs` (CheckboxSelectMultiple with 7-value SEN vocabulary including 'none' exclusive validation, JSONField list), `institutional_ai_policy` (RadioSelect with 'Prefer not to say' + 'I do not know'). Form choice labels read from M2 model definitions (canonical, descriptive). `clean_*` methods coerce '' to None for nullable storage. View one-line addition: `form.instance._change_source = 'profile_edit'` before save() so M3 history rows carry attribution. Template (`templates/users/profile_edit.html`) extended with new "Additional context" section using DaisyUI/Tailwind classes (matches existing pattern; no inline `<style>` introduced). Inline JS for SEN 'none' exclusive UX (mirrors goals_checkboxes pattern in same template). i18n stubs (`{% load i18n %}` + `{% trans %}` + `gettext_lazy` in form) added to new sections only. Tests in `apps/users/tests.py` (new file): 6 tests in `ProfileEditPhaseCFieldsTest` — storage, M3 signal integration, change_source attribution, 'none' exclusive validation, valid combinations, independence of the 3 fields. All 6 pass. Tech debt added: `TD-009` for self-service `/profile/history/` view (defer to Phase D). Last-modified timestamps per field deliberately NOT shown on edit form (UX clutter; future audit view is the right separation).
- **2026-05-10 — C.2.0 templates refactored to DaisyUI**: `templates/onboarding/_locked_base.html` (~70 lines of inline `<style>` removed; now uses DaisyUI `card bg-base-100 shadow-xl` + Tailwind `flex` centering with same CDN load as `base.html`), `templates/onboarding/ai_disclosure.html` (inline `style="..."` attributes removed; DaisyUI `card-title`, `btn btn-primary`, `btn btn-outline btn-primary`, `link link-hover`, `badge badge-ghost badge-sm`), `templates/about/ai_act_compliance_stub.html` (DaisyUI `alert alert-info` with standard info icon). Compliance test suite all 29 pass after refactor (transparent — tests assert response codes + body content, not CSS classes). Visual smoke test deferred to John's local browser.
- **2026-05-10 — C.2.2 implemented**: Step 3 consent amendment. New canonical write path via `record_consent` (no more direct boolean writes from the form). `apps/compliance/copy.py` extended with `RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB` and `DATA_SHARING_TEXT_V1_PRE_IRB` (DRAFT, IHU IRB review pending — both texts include PI + supervisor identification, GDPR + Greek Law 4624/2019 reference, AILST 3x commitment language with M5/M15 gating, withdrawal mechanism, and a TBD contact email placeholder). New setting `RESEARCH_CONSENT_CURRENT_VERSION = 'v1_pre_irb'` (single setting for both texts — IRB reviews them together). `apps/users/forms.py::GoalsPreferencesForm` refactored: `research_consent` and `consent_data_sharing` REMOVED from `Meta.fields`, declared as standalone `BooleanField` form fields (`consent_research_participation`, `consent_data_sharing`); form `__init__` initialises them from canonical ConsentRecord state for round-trip editability. `apps/users/views.py::onboarding_step3` reworked: helper `_apply_step3_consents` translates checkbox state into `record_consent`/`revoke_consent` calls per consent_type. Template `templates/onboarding/step3.html` shows the two consent texts verbatim (linebreaksbr-rendered) inside DaisyUI `bg-base-200` cards with the checkbox below each, plus version-stamp badge. M6 service `record_consent` upgraded with **supersede pattern**: granting a NEW version of an active consent_type silently revokes prior active versions (audit trail preserved, current state clean — exactly one active row per consent identity). M6 test suite refactored accordingly: `test_revoke_consent_specific_version` and `test_revoke_consent_all_versions` rewritten to use direct ORM creates (bypassing supersede) for the multi-version-active scenarios; new `test_record_consent_supersedes_prior_version` and `test_record_consent_same_version_is_idempotent_no_supersede` validate supersede semantics. Compliance tests now 31 (was 29 before C.2.2). New `OnboardingStep3ConsentTest` (7 tests) in `apps/users/tests.py`: storage, unchecked/independent, revoke-on-uncheck, verbatim-text regression, signal sync, double-submission idempotency. All 60 Phase C tests pass (compliance 31 + users 13 + ailst 16).
- **2026-05-09 — M3 applied**: Migration `users/0008_teacherprofilehistory` applied. New `teacher_profile_history` table + signal-based change tracker in `apps/users/signals.py`. CP 3 resolved: 11 fields tracked (10 originally proposed + `ai_tools_used`). 4 standalone tests passed (single change, multi-field save with shared UUID, no-change save, created=True path). Pre-M3 backup: `pre_migration_backup_phaseC_M3_20260509.sql`.
- **2026-05-11 — C.2.5 implemented**: PROODOS Epilogue placeholder + post-M15 reroute. New app `apps/epilogue/` registered in INSTALLED_APPS and mounted at `/epilogue/`. New table `epilogue_completions` (Django migration `epilogue/0001_initial`, additive only — pre-apply backup: `pre_migration_backup_phaseC_C25_20260511.sql`, 49MB) with `OneToOneField(User)`, `started_at` (auto_now_add) and `completed_at` (nullable). Two views: `epilogue_placeholder_view` (GET, creates row on first visit, renders `templates/epilogue/placeholder.html` with a "feature under construction" copy quoting the April 2026 patch notes verbatim) and `epilogue_complete_view` (POST, idempotent flip of `completed_at`, redirect to `/ailst/t2/` for consenting users with T2 not yet done, else `/dashboard/`). Per D4, no consent gate on the Epilogue itself — pedagogical feature, not research instrument; the T2 gate remains at the AILST entry view. Cross-app integration via `apps/epilogue/services.py::get_post_module_epilogue_redirect_url`. `apps/modules/views.py::mark_tab_complete` now calls both the AILST helper (M5 -> T1, C.2.4) and the Epilogue helper (M15 -> /epilogue/, C.2.5) and packs whichever URL fires into the existing `ailst_redirect_url` JSON key plus a new `ailst_redirect_label` key ("Continue to AI Literacy assessment" for M5, "Continue to PROODOS Epilogue" for M15). Frontend in `templates/modules/tabs/tab5_reflection.html` updated to read the label from the server. `apps/ailst/services.py` mapping drops M15 (T2 no longer triggers from M15 directly) and a comment block documents the rationale. The C.2.4 changelog entry stays correct; this entry supersedes the M15 mapping. Architectural note: the Epilogue is a **methodologically distinct post-completion feature**, not module 16 — DB code `EPILOGUE`, separate app, separate model. Stages 0-3 + Gemini dialogue + Learning Portrait PDF deferred to TD-011 (post-pilot). New tests in `apps/epilogue/tests.py` (12 tests across placeholder view, complete view, and routing helper). One M15 integration test in `apps/modules/tests.py` updated from "/ailst/t2/" expectation to "/epilogue/" expectation. Whole Phase C suite: 110 tests pass (ailst 47 + users 30 + compliance 14 + modules 7 + epilogue 12). Single commit `C.2.5`.

- **2026-05-11 — C.2.4 implemented**: Module-completion -> AILST gating wired into the existing `apps/modules/views.py::mark_tab_complete` AJAX endpoint. New file `apps/ailst/services.py` exposes `get_post_module_redirect_url(user, module_code)` as the integration surface: returns `/ailst/t1/` for a just-completed M5 or `/ailst/t2/` for M15 when (a) the user's `TeacherProfile.research_consent` is True (M6 cache; sync-signal kept canonical), and (b) the matching `AilstResponse` row for the timepoint has `completed_at IS NULL` (idempotency guard against admin progress resets, double-submits, parallel tabs). Modules layer calls the helper immediately after `progress.mark_tab_complete(...)` and only when `progress.completed_at is not None` — i.e., the just-marked tab also finalised the module. Returned URL is added to the JSON response as `ailst_redirect_url`. Module mapping pinned in `POST_MODULE_AILST_TIMEPOINT = {'M5': 'T1', 'M15': 'T2'}`. CP 9 resolved (insertion point exactly at line 796 as specified). Per design decision D4 (10 May 2026 chat), research_consent gating is enforced at the modules layer rather than at the AILST layer: a non-consenting user who completes M5 stays in the normal module-completion flow (no AILST redirect, no double-redirect via consent_required page). Per D7, the helper lives in `apps/ailst/services.py` (public function, AILST-app-owned, discoverable) rather than as a private helper in the modules view. Frontend changes in 3 sites: two generic JS handlers in `templates/modules/module_detail.html` (introduction/main_content/assessment tab handler + activity form handler) check `result.ailst_redirect_url` before the normal `next_tab` flow; the reflection submission handler in `templates/modules/tabs/tab5_reflection.html` rewires the "Reflection Completed" button(s) (marked with `data-reflection-continue`) so the user reads the RAG feedback first and then clicks through to the AILST baseline. Tests: 7 integration tests in new `apps/modules/tests.py::AilstModuleGatingTest` covering all 7 cases (M5+consent+T1-not-done -> T1 redirect, M5+T1-done -> no redirect [idempotency], M15+consent+T2-not-done -> T2 redirect, M5+consent=False -> no redirect [consent gating], M3+consent=True -> no redirect [not in gating set], mid-tab partial completion -> no redirect, backwards-compatible JSON shape when no redirect). Whole-suite tests pass: 97 total (modules 7 + ailst 46 + users 30 + compliance 14). No DB migration. Single commit `C.2.4`. T1/T2 routes from C.2.3 now reachable in production for the first time.

- **2026-05-10 — C.2.3 implemented**: AILST T0/T1/T2 administration views and full flow on top of M4 seed + M5 scoring. New files: `apps/ailst/urls.py`, `apps/ailst/forms.py` (`AilstPageForm` dynamic factory with `TypedChoiceField` per item, full paper-verbatim 5-anchor labels), `apps/ailst/views.py` (4 views — `ailst_entry_view`, `ailst_page_view`, `ailst_complete_view`, `ailst_research_consent_required_view`, `ailst_restart_view` — parameterised on timepoint T0/T1/T2; helpers `_normalise_timepoint`, `_items_for_page`, `_first_incomplete_page`, `_finalise_completion`, `_onboarding_complete`, `_has_research_consent`), 5 templates (`templates/ailst/intro.html`, `page.html`, `_likert_item.html`, `complete.html`, `research_consent_required.html`). State machine: 4 pages, partial-fill resume, cannot-skip-ahead enforcement (going back to a completed page is allowed and pre-populates), select_for_update concurrency guard, idempotent finalisation. CP 8 resolved: mobile Likert renders as stacked card on mobile and reflows to a radio-table grid on desktop via Tailwind responsive utilities; all 5 paper-verbatim anchors visible at every breakpoint (CP 5 reaffirmed). Design decisions captured in `proodos_files/C23_DESIGN_PROPOSAL_20260510.md` (D1-D13). Two methodologically significant decisions: **D4** — individual factor scores are NOT shown to participants during the pilot for any timepoint, to avoid baseline priming and demand characteristics in T1/T2; complete page is acknowledgment-only; post-pilot reveal tracked as TD-010. **D7** — research_consent gating on AILST entry: AILST is the primary research instrument, collecting responses without active research_participation consent would breach GDPR Art. 9; users with `profile.research_consent=False` redirect to a `research_consent_required` explanation page with a path back to profile settings. No auto-delete of partial responses on consent revocation (audit-trail integrity, user-work preservation, demand-characteristics protection); right-to-erasure remains a separate explicit user action. Source of truth for the consent check is `TeacherProfile.research_consent` boolean (M6 sync-cache, kept canonical by `sync_teacher_profile_booleans` signal). Onboarding Summary POST now advances `request.session['onboarding_step']` to 4 (instead of pop) and redirects to `ailst:entry t0=`; `templates/onboarding/summary.html` CTA copy updated to "Continue to AI Literacy baseline". URL convention: lowercase in URL (`/ailst/t0/`), uppercase in DB. C.2.4 (post-M5 / post-M15 module-completion redirects) is a separate ~30 LOC addition that wires the now-functional T1/T2 routes. Tests extended from 16 to 44 in `apps/ailst/tests.py` (28 new view-layer tests across `AilstEntryViewTest`, `AilstPageViewTest`, `AilstStateMachineTest`, `AilstResearchConsentGatingTest`, `AilstCompleteViewTest`, `AilstRestartViewTest`, `AilstTimepointParameterisationTest`, `AilstMobileLikertRenderTest`). All 88 Phase C tests pass (ailst 44 + users 30 + compliance 14). New tech debt entry TD-010 (post-pilot AILST score reveal feature). Implemented as two commits — Commit 1: AILST app self-contained (urls/forms/views/templates/tests/config wiring), Commit 2: onboarding wiring (Summary view + summary.html + this changelog).
