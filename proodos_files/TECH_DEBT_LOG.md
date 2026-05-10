# Tech Debt Log

**Started:** 2026-05-10 (during Phase C M6)
**Purpose:** Single living document tracking deferred technical work that is intentionally NOT addressed in the current phase. Each entry includes a rationale for deferral and a concrete forward path.

This file complements `~/.claude/projects/.../memory/reference_codebase_quirks.md` which records *current codebase facts to know*. The tech debt log records *deferred fixes we plan to do*.

---

## TD-001 — Consent audit retention if user is deleted

**Status:** Deferred. Phase H or later, only if IRB requires.
**Where:** `apps/compliance/models.py::ConsentRecord` `on_delete=CASCADE`.

Currently, when a user is deleted (right-to-erasure), all their `ConsentRecord` rows cascade-delete. This is the simplest path and is acceptable for the pilot. If a future IRB or regulator argues that "proof of consent at time T" must survive user deletion, the upgrade path is:

1. Add a `consent_audit` table with no user_id, only:
   `(consent_type, version, granted, granted_at, revoked_at, ip_address_hash)`
2. Pre-delete signal on `ConsentRecord` copies an anonymized row into `consent_audit`.
3. Cascade still proceeds for the original `ConsentRecord` row.
4. `consent_audit` rows survive user deletion; `ip_address_hash` is a one-way hash so subject re-identification is infeasible.

Decision deferred because the pilot is research-grade but not yet a regulated CRM, and the IRB has not flagged this concern in any prior approval.

---

## TD-002 — TeacherProfile boolean cache (research_consent, consent_data_sharing)

**Status:** Deferred. Phase H, after all read paths migrate to ConsentRecord.
**Where:** `apps/users/models.py::TeacherProfile.research_consent` and `.consent_data_sharing`.

After Phase C M6, two booleans on `TeacherProfile` are kept in sync with `ConsentRecord` via the `sync_teacher_profile_booleans` signal in `apps/compliance/signals.py`. This is a transitional measure: legacy code paths still read the booleans, so they must reflect canonical state.

Once all read sites have migrated to query `ConsentRecord` directly (likely during Phase H consolidation), the booleans can be removed via a Django migration that:

1. Drops the columns from `TeacherProfile`
2. Removes the signal handler (no longer needed)
3. Updates documentation

`contact_for_research` (a contact preference, not a consent) stays on `TeacherProfile` indefinitely.

---

## TD-003 — Timezone naive timestamps on legacy teacher_profiles columns

**Status:** Deferred. Phase H.
**Where:** `teacher_profiles.profile_completion_date`, `created_at`, `consent_timestamp`, `updated_at`, `last_profile_update`.

Several DateTimeField columns on `teacher_profiles` were created when `USE_TZ=False` was the project default. They are stored as `timestamp without time zone` in PostgreSQL. New columns (Phase A Tier 3, Phase C M2 personalization) are `timestamp with time zone` because Django now uses `USE_TZ=True`.

**Symptom:** RuntimeWarning during data migrations or queries that mix the legacy naive timestamps into timezone-aware contexts. Not functionally breaking. PostgreSQL silently coerces naive timestamps to UTC.

**Observed during M6 backfill** (`compliance/0004_migrate_teacherprofile_consents`): the migration emitted 6 RuntimeWarnings while reading `consent_timestamp` from each TeacherProfile. The data was stored correctly; the warning is hygiene.

**Fix path** (when Phase H comes):

```sql
ALTER TABLE teacher_profiles
ALTER COLUMN <col> TYPE timestamp with time zone
USING <col> AT TIME ZONE 'UTC';
```

Loop over the 5 affected columns. Backup before. The `AT TIME ZONE 'UTC'` clause matches what Django's implicit coercion is already doing, so semantics are preserved.

---

## TD-004 — Tier 3 backup tables (15 tables + dependent views/triggers)

**Status:** Deferred. Phase H.
**Where:** `tab3_user_activity_m1_backup`, `m1_tab2_backup`, `m12_main_content_backup_apr2026`, `modules_modulecontent_backup_*` (10 tables).
**Plus:** views `tab3_completion_stats`, `tab3_tool_usage`, `tab3_prompt_preferences` (all reference `tab3_user_activity_m1_backup`).
**Plus:** trigger functions `check_tab3_completion()`, `update_tab3_activity_timestamp()`.

These are intentional backups created during Phase A/B/C work. They are NOT part of the pre-Phase-C dead schema (which was dropped in Γ.1). They contain genuine snapshots from specific milestones (e.g., M1 baseline, M12 content backup before April 2026 changes).

**Forward path (Phase H):** survey each backup table with John, decide which can be dropped. Document the keepers in `audits/`. For backups that must be retained, consider moving to a `backups` schema namespace to declutter the public schema.

Audit reference: `audits/DEAD_SCHEMA_AUDIT_20260509.md` §1.1 Tier 3.

---

## TD-005 — `rag_query_system.py` cp1253 print encoding

**Status:** Deferred. Convenience fix anytime.
**Where:** `rag_query_system.py:26` and similar near `print("✓ Using NEW google.genai API")`.

The checkmark character `✓` cannot be encoded in `cp1253` (Greek Windows shell default). Crashes any `manage.py` invocation from a Bash shell that inherits cp1253 encoding.

**Workaround in current use:** prefix every Bash invocation with `PYTHONIOENCODING=utf-8`.

**Permanent fix:**

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

Add at top of `rag_query_system.py` before any print. Or replace `✓` with ASCII `[OK]`. Either is fine.

---

## TD-006 — Ephemeral artefacts at repo root → .gitignore

**Status:** Deferred. Convenience cleanup anytime.
**Where:** `m13_canvas_export_smoke.pdf`, `proodos_matrix_files.zip`.

Both files are untracked test/export outputs that periodically clutter `git status`. Add to `.gitignore` (with explicit per-file patterns or a generic `*.zip` / `_smoke.pdf` rule per project preference).

---

## TD-007 — Migration M1 placeholder + obsolete reset script naming

**Status:** Acknowledged, no fix planned.
**Where:** `apps/compliance/migrations/0001_initial.py` (empty placeholder).

After Γ.1 the M1 migration was rewritten as an empty no-op placeholder (Django requires importable nodes for any migration in `dependencies`). The file is functionally inert but visually misleading ("0001_initial" suggests it does something).

**Forward path (Phase H or later):** consider squashing 0001-0004 of the compliance app into a single 0001 via Django's `squashmigrations`. This would eliminate the placeholder and clean up the migration history. Risk: breaks dependencies in M2 + M3 + M4 + M5 + M6 if not done carefully. Defer until migration count grows enough to justify the squash.

---

## TD-008 — AI Disclosure revocation must clear acknowledgment timestamp

**Status:** Active. Must be implemented in C.4 Privacy dashboard.
**Where:** `apps/compliance/views.py` C.4 revocation endpoint (not yet written).

When a user revokes the `ai_disclosure` consent (e.g., via the C.4 Privacy dashboard's "withdraw consent" action), `revoke_consent(user, consent_type='ai_disclosure')` will set `revoked_at=NOW()` on the active row. **However, that does NOT update `TeacherProfile.ai_disclosure_acknowledged_at`** — and the `AIDisclosureMiddleware` checks the latter, not the former. So a user who revokes ai_disclosure consent through C.4 would continue to pass through the middleware, contradicting their revocation.

**Required fix in C.4 implementation:** the revocation view must do BOTH:

```python
revoke_consent(user=request.user, consent_type='ai_disclosure')
profile = request.user.teacher_profile
profile.ai_disclosure_acknowledged_at = None
profile.save(update_fields=['ai_disclosure_acknowledged_at'])
```

After that, the user's next request hits the middleware, gets redirected back to the disclosure modal, must re-acknowledge to continue. This matches the spirit of revocation.

**Test required (C.4):**
1. Authenticate user, acknowledge → ack_user is acknowledged
2. Revoke via Privacy dashboard endpoint
3. Next request to `/dashboard/` → redirect to `/onboarding/ai-disclosure/`

**Discovered in:** C.2.0 design (10 May 2026).
**Resolved in:** C.4 implementation (pending).

---

## TD entry conventions

When adding a new entry:

1. **TD-NNN** sequential id, never recycled
2. **Status:** one of `Active` / `Deferred` / `Fixed in commit <hash>` / `Acknowledged, no fix planned`
3. **Where:** specific file/path/symbol
4. Brief rationale + concrete forward path (so future-you doesn't start from zero)
5. Cross-reference audit reports / commits / memory files where relevant
