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

| # | App | Type | Purpose | Reversible? |
|---|-----|------|---------|-------------|
| M1 | compliance | RunSQL | Extend `consent_records.valid_consent_type` to include `'ai_disclosure'`. | Yes (reverse SQL drops + re-adds old constraint) |
| M2 | users | AlterField + AddField | Add 4 new columns to `teacher_profiles`. | Yes (DROP COLUMN) |
| M3 | users | CreateModel + signal | Create `teacher_profile_history` + Django signal in `apps/users/signals.py`. | Yes (DROP TABLE) |
| M4 | ailst | CreateModel + RunPython | Create `ailst_items` + seed EN-only data from paper Appendix. | Yes (DROP TABLE) |
| M5 | ailst | CreateModel | Create `ailst_responses`. | Yes (DROP TABLE) |

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

### 6.4 Migration 4 — `apps/ailst/migrations/0001_initial.py`

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

### 6.5 Migration 5 — `apps/ailst/migrations/0002_*.py`

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
