# Dead Schema Audit Report — 9 May 2026

**Project:** PROODOS EduAI
**Phase:** Γ.0 — Pre-drop discovery audit (read-only)
**Auditor:** Claude Code session
**Reviewed by:** John Dourvas (pending)
**Reference snapshot:** `pre_migration_backup_phaseC_M2_20260509.sql` (50.6 MB, root). Sufficient for rollback if Γ.1 ever introduces unexpected breakage.
**Constraints honoured:** No DDL. No DML. No migration applied. Read-only investigation only.

---

## Executive summary

The PROODOS database contains a parallel raw-SQL user system that was created during an early architectural phase and abandoned when Django models were introduced. Two separate user tables coexist: `users` (raw-SQL, 2 seed rows) and `auth_user` (Django, 6 real users). The raw-SQL system has 19 tables, 2 SQL functions, and 5 triggers, all with FK chains rooted at `users` or `modules` (the dead-schema mirror of `modules_module`). An additional 3 vestigial admin tables (`schema_versions`, `feature_flags`, `system_settings`) survive from the same pre-Django era.

**Verdict: A — CLEAR TO DROP.**

Zero live Python code references any dead-schema table. No Django ORM models map to them. No views in active use depend on them. No triggers attached to them are necessary for live functionality. The two SQL functions (`anonymize_user`, `cleanup_old_analytics`) only operate on dead schema and one of them (`anonymize_user`) is broken: it references columns (`years_experience`, `ai_experience_level`) that do not exist in the actual `teacher_profiles` schema and would fail on call.

Section 6 contains a drop migration draft in correct dependency order. Section 7 contains the recovery plan if Γ.1 introduces unexpected breakage.

The original Migration 1 of Phase C (`apps/compliance/0001_initial.py`, extending `consent_records.valid_consent_type`) becomes **obsolete** once the dead schema is dropped. Recommendation: delete the migration file and the corresponding `django_migrations` row in Γ.1.

---

## Section 1 — DB inventory

### 1.1 All public tables (sorted by classification)

#### Tier 1 — Dead schema with FK to old `users` table (19 tables)

Drop these in Γ.1.

| Table | Rows | Has FK to `users(id)` or chains via `modules(id)` | Notes |
|---|---:|---|---|
| `users` | 2 | ROOT (separate from auth_user) | Seed: john.doe@example.com (id=1), testuser@example.com (id=3) |
| `consent_records` | 0 | direct `users(id)` FK | Created with constraint `valid_consent_type` |
| `user_module_progress` | 2 | direct `users(id)` FK | Seed for users 1 + 3, in_progress / 25%, 80% |
| `forum_posts` | 0 | direct `users(id)` FK (author + flagged_by) | |
| `forum_threads` | 0 | direct `users(id)` FK (creator) + chain via `modules(id)` | |
| `forum_helpful_votes` | 0 | direct `users(id)` FK + chain via `forum_posts` | |
| `analytics_events` | 0 | direct `users(id)` FK + chain via `modules(id)` | |
| `survey_responses` | 0 | direct `users(id)` FK + chain via `modules(id)`, `surveys(id)` | |
| `surveys` | 0 | indirect (referenced by `survey_responses`) | |
| `shared_prompts` | 0 | direct `users(id)` FK (author) + chain via `modules(id)` | |
| `shared_prompt_ratings` | 0 | direct `users(id)` FK (rater) + chain via `shared_prompts` | |
| `shared_prompt_usage` | 0 | direct `users(id)` FK + chain via `shared_prompts` | |
| `user_badges` | 0 | direct `users(id)` FK + chain via `badges(id)` | |
| `badges` | 0 | indirect (referenced by `user_badges`) | |
| `leaderboard_entries` | 0 | direct `users(id)` FK | |
| `user_submissions` | 0 | direct `users(id)` FK + chain via `modules(id)` | |
| `anonymized_profiles` | 0 | indirect (referenced by `anonymize_user` function) | |
| `modules` | 15 | ROOT (separate from `modules_module`) | Seed mirror of UNESCO 15-module list |
| `module_content` | 1 | direct `modules(id)` FK | Seed |

**Total dead-schema rows:** 22 (2 in `users`, 2 in `user_module_progress`, 15 in `modules`, 1 in `module_content`, 0 elsewhere).

#### Tier 1.5 — Pre-Django admin tables (3 tables)

No FK relationships, but originate from the same pre-Django architecture. Drop in Γ.1.

| Table | Rows | Notes |
|---|---:|---|
| `schema_versions` | 1 | One row: `('2.0.0', 'Initial schema - Enhanced Layer 2 architecture with 3-tier RAG', 2026-01-04, NULL)`. Pre-Django manual versioning. Replaced by `django_migrations`. |
| `feature_flags` | 3 | `community_forums=True`, `gamification=False`, `moderation_system=True`. **No Python code reads this table.** Replaced by Django settings + per-app conventions. |
| `system_settings` | 4 | `layer3_enabled_subjects=[]`, `cohort_start_date='2026-03-01'`, `cohort_end_date='2026-04-15'`, `max_participants=100`. **No Python code reads this table.** Out-of-date cohort dates from January 2026. |

#### Tier 2 — Live Django tables (33 tables)

Out of audit scope. Listed for completeness only.

`auth_group`, `auth_group_permissions`, `auth_permission`, `auth_user`, `auth_user_groups`, `auth_user_user_permissions`, `assessments` (Django, FK to auth_user), `community_forumhelpfulvote`, `community_forumpost`, `community_forumthread`, `django_admin_log`, `django_content_type`, `django_migrations`, `django_session`, `document_chunks`, `documents`, `modules_aioutputdispute`, `modules_module`, `modules_modulecontent`, `modules_tab3repositorysubmission`, `modules_usermoduleprogress`, `peer_blog_blogcomment`, `peer_blog_blogpost`, `peer_blog_blogthumbsup`, `peer_reflections`, `rag_documents`, `rag_queries`, `reflection_tensions`, `tab3_prompt_library`, `tab3_user_activity`, `tab3_user_toolkit`, `teacher_profiles`.

#### Tier 3 — Backup tables (out of Γ.0 scope, deferred to Phase H)

These are intentional backups created during Phase A/B work. Different concern from dead schema. Do not drop in Γ.1.

`m1_tab2_backup`, `m12_main_content_backup_apr2026`, `tab3_user_activity_m1_backup`, `modules_modulecontent_backup_citizenship_apr2026`, `modules_modulecontent_backup_climate_apr2026`, `modules_modulecontent_backup_commercial_apr2026`, `modules_modulecontent_backup_disabilities_apr2026`, `modules_modulecontent_backup_m7_layout_apr2026`, `modules_modulecontent_backup_phase_a_tier2_may2026`, `modules_modulecontent_backup_phase_a_tier3_may2026`, `modules_modulecontent_backup_phase_a_tier4_may2026`, `modules_modulecontent_backup_phasea_tier1_cycle1`, `modules_modulecontent_backup_phasea_tier1_cycle2`, `modules_modulecontent_backup_programming_apr2026`, `modules_modulecontent_backup_subjectboxes_apr2026`.

### 1.2 Foreign key constraints on dead schema

All Tier 1 FK constraints will auto-drop when their parent tables are dropped (PostgreSQL handles this automatically with `DROP TABLE` or `DROP TABLE ... CASCADE`).

Source-target map (extracted from full `pg_constraint` query):

```
analytics_events → users, modules
consent_records → users
forum_helpful_votes → users, forum_posts
forum_posts → users (author + flagged_by), forum_posts (parent), forum_threads
forum_threads → users (creator), modules
leaderboard_entries → users
module_content → modules
shared_prompts → users (author), modules
shared_prompt_ratings → users (rater), shared_prompts
shared_prompt_usage → users, shared_prompts
survey_responses → users, surveys, modules
user_badges → users, badges
user_module_progress → users, modules
user_submissions → users, modules
```

No cross-FK from any Tier 2 (Django live) table into any Tier 1 (dead). Verified by full FK enumeration.

### 1.3 SQL functions in `public` schema

Excluding the 100+ `vector`, `halfvec`, `sparsevec`, `gin_*`, `gtrgm_*`, `uuid_*` functions which are part of `vector` and `pg_trgm` extensions and irrelevant to this audit.

Project-defined functions:

| Function | Comment | Operates on dead schema? | Called by? | Action in Γ.1 |
|---|---|---|---|---|
| `anonymize_user(integer)` | "GDPR compliance: Anonymize user while preserving research data" | Yes — modifies `users`, `teacher_profiles`, inserts into `anonymized_profiles`. **BROKEN**: function body references `years_experience` and `ai_experience_level` columns that do not exist on `teacher_profiles` (actual columns are `teaching_years` varchar and `ai_experience` varchar). | No code path. Not in any trigger. No `pg_cron` (extension not installed). | DROP |
| `cleanup_old_analytics()` | "Automated data retention policy execution" | Yes — `DELETE FROM analytics_events`, `UPDATE consent_records`. Both dead. | No code path. Not in any trigger. No scheduler. | DROP |
| `update_updated_at_column()` | (no comment) | No — it is a generic `NEW.updated_at = NOW()` trigger function. | Used by live triggers `trigger_documents_updated_at`, `trigger_rag_queries_updated_at`. Also used by 5 dead-schema triggers (which auto-drop with tables). | **KEEP** |
| `check_tab3_completion()` | (no comment) | Operates on `tab3_user_activity_m1_backup` (a backup table, Tier 3). | Used by trigger `tab3_check_completion` on the backup table. | **OUT OF SCOPE** (Phase H) |
| `update_tab3_activity_timestamp()` | (no comment) | Operates on `tab3_user_activity_m1_backup`. | Used by trigger `tab3_activity_update_timestamp` on the backup table. | **OUT OF SCOPE** (Phase H) |

### 1.4 Views in `public` schema

| View | References | Used by code? | Action in Γ.1 |
|---|---|---|---|
| `tab3_completion_stats` | `tab3_user_activity_m1_backup` (Tier 3 backup) | No Python references. Verified via `grep`. | OUT OF SCOPE (Phase H) — view only matters if backup table survives |
| `tab3_tool_usage` | `tab3_user_activity_m1_backup` | No Python references. | OUT OF SCOPE (Phase H) |
| `tab3_prompt_preferences` | `tab3_user_activity_m1_backup` | No Python references. | OUT OF SCOPE (Phase H) |

### 1.5 Triggers on dead-schema tables

All five auto-drop with their parent table.

| Trigger | Table | Function called |
|---|---|---|
| `update_forum_posts_updated_at` | `forum_posts` | `update_updated_at_column()` |
| `update_forum_threads_updated_at` | `forum_threads` | `update_updated_at_column()` |
| `update_module_content_updated_at` | `module_content` | `update_updated_at_column()` |
| `update_modules_updated_at` | `modules` | `update_updated_at_column()` |
| `update_submissions_updated_at` | `user_submissions` | `update_updated_at_column()` |

Live triggers preserved (on Tier 2 / Tier 3):

- `trigger_documents_updated_at` on `documents` (Tier 2 live)
- `trigger_rag_queries_updated_at` on `rag_queries` (Tier 2 live)
- `tab3_activity_update_timestamp` on `tab3_user_activity_m1_backup` (Tier 3, deferred)
- `tab3_check_completion` on `tab3_user_activity_m1_backup` (Tier 3, deferred)

### 1.6 Extensions and scheduled jobs

Installed extensions: `pg_trgm v1.6`, `plpgsql v1.0`, `uuid-ossp v1.1`, `vector v0.8.1`.

**No `pg_cron` extension installed.** No scheduled jobs in DB. No external scheduler (no `tasks.py` files exist that reference dead schema — verified). The `cleanup_old_analytics()` function therefore is never called. Anywhere.

---

## Section 2 — Codebase references

Searched the entire repository (excluding `venv/` and `.git/`) for references to every dead-schema name.

### 2.1 grep results

Search query (composite of all dead-schema table names + function names + view names):

```
consent_records | anonymize_user | user_module_progress |
forum_posts | forum_threads | forum_helpful_votes |
analytics_events | survey_responses | shared_prompts |
user_badges | leaderboard_entries | user_submissions |
anonymized_profiles | tab3_completion_stats |
tab3_prompt_preferences | tab3_tool_usage |
cleanup_old_analytics
```

Results in `*.py` files (excluding backup `.sql` files and the audit's own scratch files):

| File | Line | Context | Classification |
|---|---|---|---|
| `apps/community/models.py` | 142 | `related_name='forum_posts'` on `ForeignKey(User, ...)` | **DEAD reference (false positive)** — this is a Django reverse-accessor name, not a table reference. The Django table is `community_forumpost`. |
| `apps/community/migrations/0001_initial.py` | 55 | Same as above — Django generates `related_name='forum_posts'` in migration. | **DEAD reference (false positive)** |
| `apps/compliance/migrations/0001_initial.py` | (whole file) | The Phase C M1 migration that extends `consent_records.valid_consent_type`. | **OBSOLETE** — to be deleted in Γ.1 |
| `phaseC_M2_reset_test_users.py` | 11, 112 | Insertion attempt against `consent_records`. The script crashed on FK violation (proof that `consent_records` is dead). | **OBSOLETE** — to be deleted in Γ.1 |
| `apps/community/management/commands/setup_forum_threads.py` | (no matches in body) | Filename matched grep but content uses Django `ForumThread` model, not raw `forum_threads` table. | **DEAD reference (false positive)** |

### 2.2 ingest_*.py files reference `module_content`

The various `ingest_*.py` scripts at repo root reference the string `module_content`, but as a `doc_type` value passed to the RAG `documents` table, not as a table reference:

```python
doc_type="module_content",
```

These insert into the live `documents` table with a string-tagged document type. Not a reference to the dead `module_content` table.

**Classification: DEAD reference (false positive).** No real coupling.

### 2.3 Templates and static files

Searched `*.html`, `*.yml`, `*.yaml`, `*.json`, `*.toml`, `*.cfg`, `*.ini`. No matches against dead-schema names.

### 2.4 Verdict for Section 2

**Zero live code paths reference any dead-schema table or function.** All grep matches resolve to Django reverse-accessor names, my own Phase C work that will be reverted, or string constants that happen to share table names.

---

## Section 3 — Django settings audit

`config/settings.py` reviewed in full.

| Setting | Value | Implication |
|---|---|---|
| `INSTALLED_APPS` | django.contrib.* + apps.users, apps.modules, apps.core, apps.community, apps.peer_blog, apps.compliance, apps.ailst | No app shadows or hooks into dead schema. |
| `MIDDLEWARE` | Standard Django middleware only | No custom middleware that reads dead schema. |
| `DATABASES` | Single `default` PostgreSQL connection at localhost:5432 | No `DATABASE_ROUTERS` configured anywhere in the codebase (verified via grep). Single-DB setup. |
| `AUTH_USER_MODEL` | Not overridden (commented out at line 110: `# AUTH_USER_MODEL = 'users.User'`) | Django uses default `auth.User`. The comment is an aspirational note from an early phase; the model was never created. |
| `TEMPLATES.OPTIONS.context_processors` | Standard + `apps.peer_blog.context_processors.workshop_modules` | No context processor reads dead schema. |
| `USE_TZ` | True | Confirmed timezone-aware. New M2 columns are `timestamp with time zone`. |
| `DEFAULT_AUTO_FIELD` | `django.db.models.BigAutoField` | Standard Django 3.2+ default. |
| `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` | All point to Django views. | No special hooks. |
| `GITHUB_WORKFLOWS_URL` | env-driven config string | Phase A Tier 2 Step 4. Unrelated. |

**No DATABASE_ROUTERS, no custom AUTH backend, no middleware references dead schema.** Django side is clean.

---

## Section 4 — Documentation references

Searched all `*.md` files in the repository.

Matches in 2 markdown files:

| File | Status |
|---|---|
| `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` | This audit's own preceding plan. References `consent_records` and `anonymize_user` as live infrastructure. **Needs correction post-Γ.1**: replace §6.1 (Migration 1) status with "OBSOLETE — superseded by Γ.1". Add §3 audit-finding entry. |
| `PROODOS_UNIFIED_ROADMAP.md` | Roadmap doc. Mentions "GDPR cleanup" as a planned task (Phase B.3 line 121-126: "καθαρισμός migrations/ → sql/ directory"). Does not assert that dead schema is in use. **Minor correction needed post-Γ.1**: add a note in Phase C section that the dead schema was removed and the roadmap entry for Phase B.3 should be marked completed. |

External documentation reviewed:
- `PHASE_C_HANDOFF_FOR_CLAUDE_CODE.md` (in Downloads, not in repo) — its §4.1 misrepresents the dead schema as "existing infrastructure". This document is the source of the original misreading. **Needs annotation** (or full retraction) once Γ.1 is applied. The hand-off was approved before the audit; it cannot be silently corrected. Recommended: add a §0 banner pointing to this audit and to Γ.1.

---

## Section 5 — Drop safety verdict

**Verdict: A — CLEAR TO DROP.**

Justification chain:

1. **Zero live Python references** to any Tier 1 or Tier 1.5 table. All grep matches are Django reverse-accessor strings, false positives in `ingest_*.py` (string constants), or my own obsolete Phase C work.
2. **Zero ORM models** for any Tier 1 or Tier 1.5 table. No Django app maps to them.
3. **Zero scheduled jobs** call `cleanup_old_analytics()`. No `pg_cron`, no `tasks.py` references, no Celery, no other scheduler.
4. **Zero non-broken external invocations** of `anonymize_user`. The function is itself broken (column-mismatch) and would fail on call.
5. **All FK chains are self-contained** within Tier 1. No FK from Tier 2 (live Django) → Tier 1 (dead). Dropping Tier 1 cannot orphan live Django data.
6. **All triggers on dead tables are auto-dropped** by `DROP TABLE`. The shared trigger function `update_updated_at_column()` is preserved because it is also used by live RAG triggers (`documents`, `rag_queries`).
7. **2 functions to drop** (`anonymize_user`, `cleanup_old_analytics`) — both dead. **1 function preserved** (`update_updated_at_column`).
8. **Out-of-scope items are explicit and bounded.** Tier 3 backup tables, the 3 `tab3_*` views, and 2 `tab3_*` trigger functions are deferred to Phase H. They are unrelated to the pre-Django dead schema; they are intentional backups from active Phase A/B/C work.

---

## Section 6 — Drop migration draft (Γ.1)

To be placed at `apps/compliance/migrations/0002_drop_dead_schema.py`. Single migration, single transaction.

```python
"""
Phase C Γ.1 — Drop pre-Django dead schema.

Removes 22 tables and 2 SQL functions that comprise an abandoned
pre-Django architectural layer (raw-SQL `users` table and its FK chain,
plus pre-Django admin tables `schema_versions`, `feature_flags`,
`system_settings`).

Audit: audits/DEAD_SCHEMA_AUDIT_20260509.md establishes zero live
references and verdict A (clear to drop).

This migration also obsoletes apps/compliance/migrations/0001_initial.py
(the constraint extension on `consent_records`). After Γ.1 is applied,
0001_initial.py should be deleted from disk and its row removed from
django_migrations table (handled in this same migration, see
operations[2]).

Reverse SQL: there is no reverse. Dropped data is not recoverable from
a migration alone. Recovery is via the pg_dump backup at the repo root
(see Section 7 of the audit).
"""

from django.db import migrations


SQL_DROP_FORWARD = '''
-- Drop SQL functions first (they reference tables to be dropped)
DROP FUNCTION IF EXISTS public.anonymize_user(integer);
DROP FUNCTION IF EXISTS public.cleanup_old_analytics();

-- Drop tables. CASCADE handles FK auto-drops; triggers and sequences
-- are auto-removed by DROP TABLE. Order chosen to make dependencies
-- explicit even though CASCADE would also work.

-- Forum subgraph (depends on forum_posts -> forum_threads -> users)
DROP TABLE IF EXISTS public.forum_helpful_votes CASCADE;
DROP TABLE IF EXISTS public.forum_posts CASCADE;
DROP TABLE IF EXISTS public.forum_threads CASCADE;

-- Survey subgraph
DROP TABLE IF EXISTS public.survey_responses CASCADE;
DROP TABLE IF EXISTS public.surveys CASCADE;

-- Shared-prompts subgraph
DROP TABLE IF EXISTS public.shared_prompt_usage CASCADE;
DROP TABLE IF EXISTS public.shared_prompt_ratings CASCADE;
DROP TABLE IF EXISTS public.shared_prompts CASCADE;

-- Gamification subgraph
DROP TABLE IF EXISTS public.user_badges CASCADE;
DROP TABLE IF EXISTS public.badges CASCADE;
DROP TABLE IF EXISTS public.leaderboard_entries CASCADE;

-- Submissions / progress / consent
DROP TABLE IF EXISTS public.user_submissions CASCADE;
DROP TABLE IF EXISTS public.user_module_progress CASCADE;
DROP TABLE IF EXISTS public.consent_records CASCADE;

-- Analytics + anonymized
DROP TABLE IF EXISTS public.analytics_events CASCADE;
DROP TABLE IF EXISTS public.anonymized_profiles CASCADE;

-- Module dead-schema (modules / module_content - distinct from modules_module / modules_modulecontent)
DROP TABLE IF EXISTS public.module_content CASCADE;
DROP TABLE IF EXISTS public.modules CASCADE;

-- Root user table (last in this group, since others FK to it)
DROP TABLE IF EXISTS public.users CASCADE;

-- Pre-Django admin tables (no FK relationships, but same era)
DROP TABLE IF EXISTS public.schema_versions CASCADE;
DROP TABLE IF EXISTS public.feature_flags CASCADE;
DROP TABLE IF EXISTS public.system_settings CASCADE;
'''


def remove_obsolete_m1_migration_record(apps, schema_editor):
    """Remove the django_migrations row for compliance.0001_initial.

    The 0001 migration extended a constraint on consent_records, which
    no longer exists after this Γ.1 migration. Removing its row keeps
    `manage.py showmigrations` consistent with the file we will delete
    from disk after this migration is committed.
    """
    schema_editor.execute(
        "DELETE FROM django_migrations "
        "WHERE app = 'compliance' AND name = '0001_initial'"
    )


def restore_obsolete_m1_migration_record(apps, schema_editor):
    """Reverse — re-insert the row if Γ.1 is rolled back. The 0001
    migration file must also be restored on disk for this to be
    coherent. See audit Section 7 for full recovery path.
    """
    schema_editor.execute(
        "INSERT INTO django_migrations (app, name, applied) "
        "VALUES ('compliance', '0001_initial', NOW())"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('compliance', '0001_initial'),
        ('users', '0007_teacherprofile_ai_disclosure_acknowledged_at_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_DROP_FORWARD,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunPython(
            code=remove_obsolete_m1_migration_record,
            reverse_code=restore_obsolete_m1_migration_record,
        ),
    ]
```

After Γ.1 is applied and committed, also:

1. Delete file `apps/compliance/migrations/0001_initial.py` from disk.
2. Delete file `phaseC_M2_reset_test_users.py` (its INSERT into `consent_records` block will fail; the file should be rewritten without the consent_records insert before re-running).
3. Delete the two pre-migration backup SQL files in repo root if disk space matters: `pre_migration_backup_phaseC_M1_20260509.sql`, `pre_migration_backup_phaseC_M2_20260509.sql`. They served their purpose. Keep one consolidated post-Γ.1 backup instead.
4. Update `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md`:
   - §6.1 status: "OBSOLETE — superseded by Γ.1 drop migration. consent_records no longer exists."
   - Add §11 changelog entry for Γ.0 audit + Γ.1 apply.
5. Update `PROODOS_UNIFIED_ROADMAP.md` Phase B.3 entry: mark "καθαρισμός dead schema" completed.

---

## Section 7 — Recovery plan

If Γ.1 introduces unexpected breakage despite this audit, recovery is full DB restore from the pre-audit backup.

### 7.1 Reference snapshot

```
File: pre_migration_backup_phaseC_M2_20260509.sql
Path: C:/Users/dourv/unesco_ai_pd/
Size: 50.6 MB, 24,068 lines
Created: 2026-05-09, before Migration 2 apply
Contents: full pg_dump of unesco_ai_teacher_pd, schema + data
```

This backup precedes Γ.1, so restoring from it returns the DB to the state with Migration 1 applied, Migration 2 applied, but Γ.1 not applied — and importantly with all dead-schema tables intact.

### 7.2 Restore command

```
PGPASSWORD=Django123! "C:/Program Files/PostgreSQL/18/bin/psql.exe" -h localhost -U postgres -d unesco_ai_teacher_pd -f "C:/Users/dourv/unesco_ai_pd/pre_migration_backup_phaseC_M2_20260509.sql"
```

For a clean restore, drop and recreate the database first:

```
PGPASSWORD=Django123! "C:/Program Files/PostgreSQL/18/bin/dropdb.exe" -h localhost -U postgres unesco_ai_teacher_pd
PGPASSWORD=Django123! "C:/Program Files/PostgreSQL/18/bin/createdb.exe" -h localhost -U postgres unesco_ai_teacher_pd
PGPASSWORD=Django123! "C:/Program Files/PostgreSQL/18/bin/psql.exe" -h localhost -U postgres -d unesco_ai_teacher_pd -f "C:/Users/dourv/unesco_ai_pd/pre_migration_backup_phaseC_M2_20260509.sql"
```

After restore:
- `manage.py migrate --fake compliance 0001` (mark Migration 1 as applied without re-running, since the backup already has its effect).
- `manage.py showmigrations` to verify state.

### 7.3 Targeted rollback (if only specific tables need to come back)

Open `pre_migration_backup_phaseC_M2_20260509.sql` and extract the `CREATE TABLE` + `COPY ... FROM stdin` blocks for the specific table(s) needed. Apply manually via `psql`. Less invasive than full restore. Suitable for the rare case where Γ.1 was correct but external tooling assumed a dead-schema table existed.

### 7.4 Post-Γ.1 fresh backup

After Γ.1 succeeds and is verified, create a clean snapshot for future reference:

```
PGPASSWORD=Django123! "C:/Program Files/PostgreSQL/18/bin/pg_dump.exe" -h localhost -U postgres unesco_ai_teacher_pd > "C:/Users/dourv/unesco_ai_pd/post_dead_schema_drop_backup_20260509.sql"
```

This becomes the new Phase C baseline backup.

---

## Appendix A — Memory note for future sessions

To be added to `C:/Users/dourv/.claude/projects/C--Users-dourv-unesco-ai-pd/memory/reference_codebase_quirks.md` after Γ.1 is applied. Replaces the current "Raw-SQL artefacts not in Django migrations" subsection.

```
## Pre-Phase-C dead schema (resolved 2026-05-09)

The PROODOS DB previously contained a parallel raw-SQL user system that was
abandoned during the early architectural phase. It included:

  - `users` table (separate from Django auth_user, only 2 seed rows)
  - 14 raw-SQL tables FK to it: consent_records, user_module_progress,
    forum_posts, forum_threads, forum_helpful_votes, analytics_events,
    survey_responses, surveys, shared_prompts, shared_prompt_ratings,
    shared_prompt_usage, user_badges, badges, leaderboard_entries,
    user_submissions
  - anonymized_profiles, modules (raw-SQL mirror), module_content
  - schema_versions, feature_flags, system_settings (pre-Django admin)
  - SQL functions anonymize_user(integer), cleanup_old_analytics()

This was DROPPED in Phase C Γ.1 on 2026-05-09 after a complete read-only
audit (audits/DEAD_SCHEMA_AUDIT_20260509.md) confirmed zero live code
references.

Future sessions: do NOT recreate any of these. For consent tracking,
GDPR deletion, forums, shared prompts, badges, leaderboards, submissions,
analytics, surveys, or progress: use the Django models in apps/users/,
apps/community/, apps/modules/, apps/peer_blog/, apps/compliance/,
apps/ailst/.

The function update_updated_at_column() was preserved because live RAG
triggers (documents, rag_queries) still use it.

Audit report: audits/DEAD_SCHEMA_AUDIT_20260509.md
Drop migration: apps/compliance/migrations/0002_drop_dead_schema.py
```

---

## Appendix B — Audit scratch files

Created during this audit, kept for traceability:

- `audits/_db_inventory_raw.txt` (341 lines) — full DB inventory dump from `manage.py shell` queries
- `audits/_db_functions_views.txt` — function bodies + view definitions

These are not normative. Authoritative info is in this audit report.

---

---

## Section 8 — Tier 1.5 sample inspection (follow-up 2026-05-09)

Per follow-up Task 1, every Tier 1.5 table was inspected for row count, schema, contents, and last activity timestamp. All three tables show identical staleness signature: last write at **2026-01-04 16:25:40 UTC**, i.e. **124 days, ~22 hours ago** (4 months).

### 8.1 `schema_versions`

| Aspect | Value |
|---|---|
| Row count | 1 |
| Columns | `version` (varchar, NOT NULL), `description` (text, NOT NULL), `applied_at` (timestamp without tz, nullable), `migration_script` (text, nullable) |
| `MAX(applied_at)` | 2026-01-04 16:25:40.382307 |
| Sole row | `('2.0.0', 'Initial schema - Enhanced Layer 2 architecture with 3-tier RAG', 2026-01-04 16:25:40, NULL)` |

This is a pre-Django manual versioning table. Replaced by `django_migrations` (currently 43 rows). One initial entry from project bootstrap, no subsequent writes. **Safe to drop.**

### 8.2 `feature_flags`

| Aspect | Value |
|---|---|
| Row count | 3 |
| Columns | `feature_name` (varchar, NOT NULL), `is_enabled` (boolean, nullable), `description` (text, nullable) |
| Timestamp | None — no last-modified column on this table |
| Rows (full enumeration) | `community_forums=True`, `gamification=False`, `moderation_system=True` |

**Critical follow-up check** — did any Python code read these flag names at runtime?

Searched repository for `community_forums`, `gamification`, `moderation_system` (all flag names) in Python and template files. Results:

- `gamification` matches in `apps/modules/tab3_content_m14.py:151` and 25+ markdown/template/sql files. **All false positives** — these all refer to gamification as a teaching topic in M14 module content (`'c3_gamification_principles'` choices field, M14 SAMR-level discussions about classroom gamification, etc.), NOT to a feature flag. M14 is the "Create" module dedicated to gamification design; the word appears organically.
- `community_forums` and `moderation_system` only appear in this audit's own scratch files and the SQL backups. Zero Python code references.

Cross-check against the live community feature: `apps/community/` is a fully Django-implemented forum system with its own published behaviour; whether posts are pre-moderated is decided by the model defaults (`is_deleted` soft-delete, `is_seeded`), not by reading `feature_flags.moderation_system`. The flag is never consulted at runtime.

**Safe to drop.**

### 8.3 `system_settings`

| Aspect | Value |
|---|---|
| Row count | 4 |
| Columns | `key` (varchar, NOT NULL), `value` (jsonb, NOT NULL), `updated_at` (timestamp without tz, nullable) |
| `MAX(updated_at)` | 2026-01-04 16:25:40.382307 |
| Rows (full enumeration) | `cohort_start_date='2026-03-01'`, `cohort_end_date='2026-04-15'`, `layer3_enabled_subjects=[]`, `max_participants=100` |

**Critical observation** — the `cohort_end_date` value (`2026-04-15`) is **already in the past** as of audit date 2026-05-09. If anything were reading this setting, the platform would be in a "post-cohort" state, which it is not. This is conclusive evidence that no code reads this value.

**Critical follow-up check** — did any Python code read these keys at runtime?

Searched for `cohort_start_date`, `cohort_end_date`, `layer3_enabled_subjects`, `max_participants` in all `.py` files. Results: zero references outside the SQL backups and this audit's own files. The keys are not consulted by any code path. The actual cohort logic (where it exists) lives in module model methods or Django settings, not in this table.

**Safe to drop.**

### 8.4 Tier 1.5 verdict

All three tables are 4 months stale (no writes since 2026-01-04), have zero Python references to either table names or keyed values, and `system_settings` contains values that have already been overtaken by real time. They are safely droppable in Γ.1.

---

## Section 9 — Frontend and non-Python audit (follow-up 2026-05-09)

Per follow-up Task 2, search for dead-schema references outside of Python source.

### 9.1 JavaScript / TypeScript

Search across `*.js`, `*.jsx`, `*.ts`, `*.tsx`. **No matches** against any dead-schema table name. The project is a server-rendered Django app (templates only); there is no SPA front-end with its own analytics SDK. No PostHog, Mixpanel, Amplitude, or custom analytics client identified.

### 9.2 Shell scripts, YAML, TOML, INI, JSON, Dockerfile, docker-compose

Search across `*.sh`, `*.yml`, `*.yaml`, `*.toml`, `*.cfg`, `*.ini`, `*.json`, `Dockerfile`, `docker-compose*`. **No matches** against any dead-schema table name. The project has no Dockerfile, no docker-compose, no shell deployment scripts, no project-level YAML/TOML config files that touch DB schema.

### 9.3 Templates (`*.html`)

Search for raw schema references in templates. Templates are pure presentation; no embedded SQL or direct DB operations. **No matches** against any dead-schema table name.

The `.html` matches that grep returned for `gamification` are pedagogical M14 content (radio button labels for "gamification principle" multiple-choice in the Tab 3 activity). Same false-positive class as Section 8.2.

### 9.4 Django middleware deep check

Searched for `*/middleware.py` files in the repository. **No project middleware exists** — only Django's built-in middleware classes in `venv/`, none of which read dead schema. The project's `MIDDLEWARE` list in `config/settings.py` (Section 3 above) is the standard Django stack with no custom additions.

### 9.5 Direct cursor.execute / raw SQL deep check

Searched for `cursor.execute` and `with connection.cursor` patterns inside `apps/`. Three matches, all in `apps/modules/views.py`:

| Line | Operation | Target table | Classification |
|---|---|---|---|
| 590 | `SELECT EXISTS(SELECT 1 FROM rag_queries ...)` | `rag_queries` | LIVE — RAG query log table |
| 772 | `INSERT INTO peer_reflections (...)` | `peer_reflections` | LIVE — peer reflection community table |
| 2077 | `SELECT rq.reflection_text, m.code FROM rag_queries rq ...` | `rag_queries` | LIVE |

**Zero raw SQL operations** in `apps/` target any dead-schema table.

Broader search: `from django.db import connection`, `psycopg2.connect`, and `.raw(` queries return 30 file matches, all inspected. None write to dead-schema tables. The `ingest_*.py` scripts at repo root use raw psycopg2 to load RAG content into `documents` and `document_chunks` (live tables); the `phaseC_M2_reset_test_users.py` script attempted to write to `consent_records` and crashed with FK violation — that is the script that triggered the Γ.0 audit in the first place.

### 9.6 Celery / async task system

Searched for `tasks.py`, `celery*.py`, and any imports of Celery / RQ / Dramatiq. **No async task system installed.** No `tasks.py` exists in the project. No background job ever runs `cleanup_old_analytics()` or any other dead-schema operation.

### 9.7 Monitoring / observability

Searched for `grafana`, `prometheus`, `monitoring` paths and configs. **No project monitoring configuration.** Matches in `venv/` are Google API client libraries and irrelevant.

### 9.8 Cron / systemd timers

No `cron` or `systemd` configuration is committed to the repository. Local development runs via `manage.py runserver` only. No deployment uses scheduled jobs against the DB. The `cleanup_old_analytics()` function therefore has no caller path — direct, scheduled, or otherwise.

### 9.9 Section 9 verdict

Zero references to any dead-schema table or function exist outside of:

- Django reverse-accessor names (`related_name='forum_posts'`, `related_name='forum_votes'`) on `auth_user` ForeignKey fields — false positives
- String constants `doc_type="module_content"` in RAG ingest scripts — false positives
- This audit's own scratch and report files
- The Phase C M1 migration and reset script that this audit obsoletes
- The pre-migration SQL backup files (read-only data, not code)

The project's non-Python surface (templates, JS, shell, YAML, Docker, monitoring, cron, async tasks) is empty of dead-schema references.

---

## Section 10 — Backup retention rule (follow-up 2026-05-09)

The two pre-migration backup SQL files at the repo root (`pre_migration_backup_phaseC_M1_20260509.sql` and `pre_migration_backup_phaseC_M2_20260509.sql`, ~50 MB each) MUST be retained unchanged until the pilot study completes (estimated post-2027).

**Rationale.** Γ.1 is destructive. If post-pilot reviewers, IRB auditors, or the dissertation committee question the integrity of pre-Phase-C state, the only defensible answer is "here is the byte-exact pre-action snapshot." A research-grade audit trail requires a verifiable artefact, not a description.

**Action items (post-Γ.1 success):**

- DO NOT delete these files after Γ.1 succeeds.
- DO NOT consolidate them into a single "post-Γ.1 baseline" — they document distinct moments in the migration sequence.
- DO move them to a `backups/phase_c/` subdirectory for organisation, e.g. `backups/phase_c/pre_migration_backup_phaseC_M1_20260509.sql`. Update Section 7 restore paths after the move.
- DO add `backups/` to `.gitignore` so future backups don't bloat the repo. The two existing files, having already been committed, remain in git history; they do not need to be removed.
- DO document their existence in the audit report (this section) and in the Γ.1 migration commit message.
- Optional: compute and store SHA-256 hashes in `backups/phase_c/CHECKSUMS.txt` for tamper-evidence:

  ```
  certutil -hashfile pre_migration_backup_phaseC_M1_20260509.sql SHA256 > CHECKSUMS.txt
  certutil -hashfile pre_migration_backup_phaseC_M2_20260509.sql SHA256 >> CHECKSUMS.txt
  ```

A separate post-Γ.1 baseline (`post_dead_schema_drop_backup_20260509.sql`) can be taken AFTER Γ.1 succeeds. It does not replace the pre-Γ.1 backups; it complements them. Together the three files document the before/after of the destructive transition.

**Implementation timing.** This retention rule takes effect at Γ.1 commit time. The backups are currently tracked in git history at commits `06357f2` (M1 backup) and the M2 commit pending; they will remain there permanently regardless of subsequent file moves on disk.

---

## Section 11 — Updated verdict

**Verdict: A CONFIRMED — Γ.1 may proceed.**

All three follow-up checks passed without surfacing any concerning finding:

1. **Tier 1.5 tables are stale and unreferenced.** All three tables (`schema_versions`, `feature_flags`, `system_settings`) have last activity timestamps of 2026-01-04 (124 days ago); zero Python code reads them by table name or by keyed value. The `system_settings.cohort_end_date` is already past, conclusively proving nothing reads it.
2. **Frontend, deployment configs, monitoring, async tasks, middleware, and raw cursors are all clean.** Zero dead-schema references in any non-Python surface, zero raw SQL writes to dead schema in any `apps/` module, zero scheduled or background callers of `anonymize_user` or `cleanup_old_analytics`.
3. **Backup retention rule is documented.** The pre-migration SQL files at the repo root are flagged for permanent retention with explicit rationale tied to dissertation integrity. Action items for post-Γ.1 file management are recorded in Section 10.

**Conditions for proceeding with Γ.1:**

1. Backup retention rule (Section 10) honoured by all subsequent commits.
2. The drop migration (Section 6) is run with the `pg_dump` of the same DB taken immediately before apply, named `pre_migration_backup_phaseC_GAMMA1_20260509.sql`. This is in addition to (not replacement of) the Γ.0 reference snapshot.
3. After Γ.1 succeeds, the obsolete `apps/compliance/migrations/0001_initial.py` and `phaseC_M2_reset_test_users.py` files are deleted from disk and committed in the same Γ.1 PR/commit batch, so the workspace is internally consistent.
4. The audit report (`audits/DEAD_SCHEMA_AUDIT_20260509.md`, this file) is referenced in the Γ.1 commit message for archival traceability.
5. Memory note (Appendix A above) is added to project memory after Γ.1 success, so future sessions cannot misread the historical state.

**Awaiting John's explicit "go Γ.1" before drafting the migration file and proceeding with the apply sequence.**

---

*End of audit. Awaiting John's review and explicit go-ahead before proceeding to Γ.1.*
