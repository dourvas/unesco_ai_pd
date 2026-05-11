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

## TD-009 — Self-service profile change history view

**Status:** Active. Defer to Phase D.
**Where:** new route `/profile/history/` in `apps/users/urls.py` + view in `apps/users/views.py` + template `templates/users/profile_history.html`.

The M3 migration introduced `TeacherProfileHistory` (signal-driven change tracker; 11 tracked fields, `change_event_id` UUID groups sibling changes per save event, `change_source` records caller). All change history is captured automatically from C.2.1 onwards.

**However, users currently have no way to view their own history.** GDPR Article 15 (right of access) implies users can request this data, but a self-service UI is better than support tickets — and IRB reviewers may ask whether participants can audit what the platform has recorded about them.

**Forward path:** new `/profile/history/` page that shows the user their own `TeacherProfileHistory` rows in a clean timeline format:

- Group by `change_event_id` (one card per save event)
- Within each card, list field-by-field changes (`old_value` → `new_value`)
- Show `changed_at` timestamp and `change_source` (e.g., "Profile edit", "Admin action", "Data migration")
- JSONField fields (`primary_goals`, `student_population_special_needs`) decoded from `_serialize` format for human-readable display

Considered and rejected for C.2.1: showing a "last-modified" timestamp next to each field in the edit form. Reasons: UX clutter, mixing concerns (edit vs audit), premature feature for a pilot of 110 teachers. The audit view route is the right separation.

**Discovered in:** C.2.1 design (10 May 2026).
**Implementation effort:** ~150 LOC + template (similar to a simple list view); no schema change needed (M3 already captures everything).
**Resolved at:** Phase D (post-pilot UX improvements).

---

## TD-010 — Post-pilot AILST score reveal feature

**Status:** Active. Defer to post-pilot Phase G/H (deliverables and user feedback).
**Where:** new route in `apps/ailst/urls.py` + view in `apps/ailst/views.py` + template `templates/ailst/research_summary.html`.

C.2.3 design decision (D4, 10 May 2026): AILST factor scores and overall score are NOT shown to users during the pilot — the `complete.html` page after T0/T1/T2 contains only an acknowledgment message ("Your responses have been recorded.") without numbers.

**Methodological rationale for hiding during the pilot:**

1. **Baseline priming (T0):** showing T0 scores would establish an anchor for the user's self-image of their AI literacy. Subsequent self-assessment at T1/T2 would be biased by the anchor — a classic carryover effect in pre/post designs.
2. **Demand characteristics (T1):** if T1 scores are visible after Module 5, the user can see their current level and may adjust T2 answers to perform "growth" — overestimating in domains they expect the programme to have improved. This produces apparent treatment effects that are artefacts of the measurement context, not of learning.
3. **Asymmetric reveal is worse, not better:** showing only T2 scores forces the user to wonder where they started; showing T1+T2 but hiding T0 makes the trajectory ambiguous; showing all three undermines T1/T2 validity. The only methodologically clean option is: hide all three for the duration of the pilot.

Standard research-ethics practice: participants receive feedback AFTER the study ends, never during. This protects measurement validity and is consistent with how the AILST instrument was originally validated.

**Post-pilot deliverable (this TD):** a "Research participation summary" page that shows the user their T0/T1/T2 trajectory after the dissertation data analysis is complete. Built as part of post-pilot user-facing deliverables.

**Implementation sketch:**

- Route: `/ailst/research-summary/` (single page, no per-timepoint URL).
- Permission: only visible after the pilot's official end date (a single setting or feature flag — e.g., `settings.AILST_RESEARCH_SUMMARY_ENABLED = False` until release-time toggle).
- View: queries the 3 `AilstResponse` rows for the user, ordered by timepoint, with completed_at not null.
- Template: renders factor scores as a 4-line chart (one line per factor across T0/T1/T2) plus a table with the numbers, with reflective context strings ("Your AI Knowledge & Skills score changed from X.X at baseline to Y.Y at programme completion").
- Optional later: add an export-to-PDF button for participants who want a copy of their trajectory.

**Discovered in:** C.2.3 design proposal D4 reversal (10 May 2026, John's decision).
**Implementation effort:** ~120 LOC view + ~150 LOC template + simple chart (could use a small JS library or static SVG generation server-side); no schema change needed (M5 already stores scores; this is pure read-side).
**Resolved at:** Post-pilot Phase G/H.

---

## TD-011 — Full PROODOS Epilogue implementation

**Status:** Active. Defer to post-pilot Phase G/H (or whenever the synthesis-and-dialogue feature is prioritised).
**Where:** `apps/epilogue/` (currently a stub) — needs full Stage 0..3 implementation, Gemini integration, and Learning Portrait PDF export.

C.2.5 (10 May 2026) introduced a placeholder for the PROODOS Epilogue so the post-M15 → T2 redirect chain can be wired research-correctly during the pilot. The current implementation is a single page with a "Mark complete and continue" button that flips `EpilogueCompletion.completed_at` and routes the user to AILST T2 (consent-gated) or the dashboard.

The full feature is specified in:

- `M16_CAPSTONE_REFLECTION_SPEC.md` (March 2026 — pedagogical rationale + 3-stage dialogue + Learning Portrait)
- The April 2026 Patch Notes ("PROODOS Epilogue — Patch Notes", supplied during C.2.5 design):
  - Renames the feature from "M16 Capstone" to "PROODOS Epilogue" (DB code `EPILOGUE`, not `M16`).
  - Adds **Stage 0: Personal Evolution Dashboard** in front of the three dialogue stages (live DTP curve + RTM tensions, no input required).
  - Establishes that the Epilogue is **a separate entity from the 15 UNESCO-aligned modules** (not a 16th module). The dissertation describes it as "a methodologically distinct post-completion feature that synthesises the research corpus generated across M1-M15."

**Forward path:**

1. **Schema extension** to the existing `epilogue_completions` table — add per-stage timestamps (`stage0_seen_at`, `stage1_completed_at` .. `stage3_completed_at`), the Gemini turn log (`dialogue_turns` JSONField, schema: `[{role, content, generated_at}]`), and `learning_portrait_text` (TextField) + `learning_portrait_pdf` (FileField / path).
2. **Stage 0 — Personal Evolution Dashboard**: read DTP trajectory from `rag_queries`, RTM tensions from `reflection_tensions`. Render as a 4-line chart (one line per AILST factor across T0/T1/T2 if available, plus the M2-M15 DTP/RTM trajectory). The dashboard is silent — no input from the educator, just visualization.
3. **Stages 1-3 (Look Back / Look In / Look Forward)**: Gemini-driven dialogue, ≤150 words per response, max 5 turns total. Context window includes DTP trajectory data + RTM tension summary (per Section 3 of the March spec).
4. **Output: Learning Portrait**: 300-400 word synthesis composed from the educator's responses across the three stages, rendered both as in-page text and exported as PDF.
5. **Per-user reusability**: decide whether the Epilogue is one-shot (current model behaviour — `OneToOneField` on `EpilogueCompletion`) or whether the educator can return to refresh the dashboard / re-do the dialogue. The patch notes raised this as an open question (Q5).

**Open questions inherited from the spec (still unresolved):**

- Q1-Q3 from the March spec (academic-original; copied into the implementation when ready).
- Q4: dashboard always-visible vs. one-shot during the dialogue.
- Q5: re-entry policy.
- Q6: Learning Portrait PDF includes dashboard screenshot or text only.

**Effort estimate:** ~1500-2000 LOC (Gemini integration is the heaviest piece; dashboard chart + PDF generation each ~300 LOC; schema migration trivial).

**Discovered / scoped in:** C.2.5 design proposal (10 May 2026).
**Resolved at:** Post-pilot Phase G/H.

---

## TD entry conventions

When adding a new entry:

1. **TD-NNN** sequential id, never recycled
2. **Status:** one of `Active` / `Deferred` / `Fixed in commit <hash>` / `Acknowledged, no fix planned`
3. **Where:** specific file/path/symbol
4. Brief rationale + concrete forward path (so future-you doesn't start from zero)
5. Cross-reference audit reports / commits / memory files where relevant
