"""
Phase C Γ.1 — Drop pre-Django dead schema.

Removes 22 tables and 2 SQL functions that comprise an abandoned
pre-Django architectural layer. The dead schema included:

  - A parallel raw-SQL `users` table (separate from Django auth_user)
    with a 14-table FK chain: consent_records, user_module_progress,
    forum_posts, forum_threads, forum_helpful_votes, analytics_events,
    survey_responses, surveys, shared_prompts, shared_prompt_ratings,
    shared_prompt_usage, user_badges, badges, leaderboard_entries,
    user_submissions
  - anonymized_profiles, modules (separate from Django modules_module),
    module_content (separate from modules_modulecontent)
  - Pre-Django admin tables: schema_versions, feature_flags, system_settings
  - Two SQL functions: anonymize_user(integer), cleanup_old_analytics()

Audit:
  audits/DEAD_SCHEMA_AUDIT_20260509.md establishes verdict A
  (clear to drop) on 2026-05-09. Sections 8-11 (follow-up checks)
  confirm zero live references in Python code, frontend, deploy
  configs, monitoring, async tasks, middleware, or templates. Tier
  1.5 tables are 124 days stale with last activity 2026-01-04.

Dependencies:
  On compliance/0001_initial (now an empty placeholder, see that file's
  module docstring) and users/0007 (which adds Phase C personalization
  fields). Originally drafted without dependence on 0001_initial, but
  Django requires a single leaf per app and rejects orphaned siblings
  with `Conflicting migrations detected; multiple leaf nodes`. Keeping
  0001 as an empty placeholder preserves graph integrity; 0001's row
  in django_migrations is left in place.

Reverse:
  None. Drop operations are not migration-reversible. Recovery is
  via the pre-Γ.1 pg_dump backup. See audits/DEAD_SCHEMA_AUDIT_20260509.md
  Section 7.

Function preserved:
  update_updated_at_column() is NOT dropped. Live RAG triggers
  (trigger_documents_updated_at on documents, trigger_rag_queries_updated_at
  on rag_queries) still use it.
"""

from django.db import migrations


SQL_DROP_FORWARD = r"""
-- Drop SQL functions first.
-- update_updated_at_column() is preserved (used by live RAG triggers).
DROP FUNCTION IF EXISTS public.anonymize_user(integer);
DROP FUNCTION IF EXISTS public.cleanup_old_analytics();

-- Drop dependent tables before their referents. CASCADE handles auto-drop
-- of FKs, triggers, and sequences. Order chosen so that dependencies are
-- explicit even though CASCADE would suffice.

-- Forum subgraph (forum_helpful_votes -> forum_posts -> forum_threads -> users)
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

-- Module dead-schema (distinct from Django modules_module / modules_modulecontent)
DROP TABLE IF EXISTS public.module_content CASCADE;
DROP TABLE IF EXISTS public.modules CASCADE;

-- Root user table (last in this group; FK referents above all dropped)
DROP TABLE IF EXISTS public.users CASCADE;

-- Pre-Django admin tables (no FK relationships; same era)
DROP TABLE IF EXISTS public.schema_versions CASCADE;
DROP TABLE IF EXISTS public.feature_flags CASCADE;
DROP TABLE IF EXISTS public.system_settings CASCADE;
"""


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
    ]
