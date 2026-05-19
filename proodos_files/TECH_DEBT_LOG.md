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

**Status:** RESOLVED in Phase E commit 1.5 (2026-05-13). Fix applied at `manage.py:11-16` — `sys.stdout`/`sys.stderr` reconfigured to UTF-8 with `errors='replace'` at the top of `main()`. Covers every Django CLI command (test, runserver, migrate, shell, custom management commands), not just the test runner. The `errors='replace'` mode keeps a hypothetical future un-encodable char from crashing the CLI instead of merely substituting it.

Chosen over the v3 proposal's alternative (edit `rag_query_system.py` directly) because manage.py is the single entry point for every CLI invocation, and the monolith disappears in Phase E commit 10 anyway — patching it would be wasted work.

**Original analysis (kept for context):**

The checkmark character `✓` (at `rag_query_system.py:26, 32, 36`) cannot be encoded in `cp1253` (Greek Windows shell default). Before the fix, any `manage.py` invocation from a shell inheriting cp1253 crashed at module import time when the monolith printed its API-detection banner. Workaround was `PYTHONIOENCODING=utf-8` prefix on every invocation — now obsolete.

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

**Status:** RESOLVED in Phase C C.4 commit 1 (2026-05-12). The `revoke_ai_disclosure_view` in `apps/compliance/views.py` now runs an atomic transaction that calls `revoke_consent` AND clears `TeacherProfile.ai_disclosure_acknowledged_at`, then logs the user out. Verified by `apps/compliance/tests.py::RevokeAiDisclosureTest::test_post_clears_profile_ack_at` and the load-bearing `test_after_revoke_next_request_hits_middleware`.

Original analysis kept below for historical context.

**Status (historical):** Active. Must be implemented in C.4 Privacy dashboard.
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

## TD-012 — Sequential module-prerequisite gating (M1 → M2 → … → M15)

**Status:** RESOLVED in Phase C C.6 (2026-05-12). New helper `apps/modules/services.py::get_module_prerequisite_block` walks `Module.order_index` ascending and returns the first prior module the user has not completed (or None if the path is clear). The helper is called from two enforcement points: `ModuleDetailView.get` (GET-side redirect to the first uncompleted prior module with an info flash) and `mark_tab_complete` (defensive AJAX guard returning HTTP 409 with an explanatory JSON body). Staff and superuser bypass for support work. Verified by `apps/modules/tests.py::SequentialModuleGatingTest` (6 tests: M1 always accessible, jumping ahead redirects to first uncompleted, full prereqs cleared, partial prereqs redirects to the gap, staff bypass, AJAX 409 defence).

Original analysis kept below for historical context.

**Status (historical):** Active. Defer to **pre-pilot** (must close before recruiting real participants).
**Where:** `apps/modules/views.py::ModuleDetailView.get` — pre-render check; possibly also a guard inside `mark_tab_complete`.

Discovered during the 2026-05-11 smoke test: a logged-in user with the right consent state can navigate directly to `/modules/M5/` (or any module URL) without having started, let alone completed, the preceding modules. There is currently no enforcement that M_n requires M_{n-1}.completed_at IS NOT NULL.

This is convenient for the C.2.3 / C.2.4 / C.2.5 smoke tests (the tester can jump to M5 to verify the M5 → T1 redirect chain in seconds rather than completing four prior modules). **It must NOT survive into the real pilot** — research design requires sequential progression: each AILST timepoint measures the educator after a specific dose of the intervention, and skipping modules invalidates that measurement.

**Forward path:**

1. Add a helper `apps.modules.services.get_module_prerequisite_block(user, module)` that returns the first uncompleted prerequisite Module (or None if the path is clear).
2. In `ModuleDetailView.get` (and in `mark_tab_complete` as a second-line defence against direct AJAX), call the helper. If it returns a Module, redirect to that module's detail page with a flash message ("Please complete <code> before opening <target>.").
3. Decide whether to use the existing `Module.prerequisites` JSONField (which currently holds module-id lists per the model docstring but is not consulted at runtime), or derive prerequisites purely from `order_index` (M_n requires every module with smaller order_index). The simpler order_index approach matches the linear UNESCO progression and avoids stale prerequisite metadata.
4. Add tests: M5 GET without M4 done → redirect to M4; M2 GET without M1 done → redirect to M1; M1 GET with no prior modules → renders; admin or staff bypass if needed for support.

**Why this is also a research-design concern:** the AILST T1 administration captures the participant's literacy AFTER the Acquire phase (M1-M5). If the participant jumped straight to M5, the T1 measurement is contaminated. Same for T2 after the full programme.

**Estimated effort:** ~60-100 LOC + tests. Trivial against the value.

**Discovered in:** smoke test 2026-05-11 (John reached M5 directly, was able to complete it and trigger T1 without doing M1-M4).
**Resolved at:** pre-pilot hardening pass (before user wipe CP 11 + real participant recruitment).

---

## TD-013 — Gate `/epilogue/` on M15 completion

**Status:** RESOLVED in Phase C C.6 (2026-05-12). New `_is_m15_completed(user)` helper in `apps/epilogue/views.py` (lazy import of `apps.modules.services.user_has_completed_module` to avoid app coupling) guards both `epilogue_placeholder_view` (GET) and `epilogue_complete_view` (POST defence). A non-staff user without M15 completion is redirected to the dashboard with an informational flash; no `EpilogueCompletion` row is created. Staff and superuser bypass. Verified by `apps/epilogue/tests.py::EpilogueM15GatingTest` (4 tests: GET without M15 redirects + no row created, POST defence, full access with M15 done, staff bypass).

Original analysis kept below for historical context.

**Status (historical):** Active. Defer to **pre-pilot** (same window as TD-012).
**Where:** `apps/epilogue/views.py::epilogue_placeholder_view` — add a prerequisite check at the top.

Discovered during the same 2026-05-11 smoke test: a logged-in user can navigate directly to `/epilogue/` without having completed M15 (or, given TD-012, without having completed M1-M14 either). The placeholder page renders, the user clicks "Mark complete and continue", `EpilogueCompletion.completed_at` is flipped, and they are forwarded to `/ailst/t2/`. This skips the entire intervention.

Currently the view's only guard is `@login_required`. The C.2.5 services helper `get_post_module_epilogue_redirect_url` correctly returns `/epilogue/` only after M15 completion, but the URL itself is open.

**Forward path:**

1. At the top of `epilogue_placeholder_view`, check whether the user has a `UserModuleProgress` row for M15 with `completed_at IS NOT NULL`.
2. If not, redirect to `/dashboard/` (or to whatever the next-up module is, if TD-012 lands first and we want a coherent forward path) with a flash message ("Please complete Module 15 before opening the Epilogue.").
3. Mirror the guard in `epilogue_complete_view` (POST) as a second-line defence against the user crafting the POST directly via curl.
4. Tests: GET without M15 done → redirect; GET with M15 done → renders; POST without M15 done → redirect, no completion row written.

**Coupling with TD-010 (full Epilogue):** when TD-010 lands (Stage 0 dashboard, Gemini dialogue, Learning Portrait), this gate must remain — otherwise the Personal Evolution Dashboard would render with incomplete trajectory data.

**Estimated effort:** ~30-50 LOC + tests.

**Discovered in:** smoke test 2026-05-11 (John reached `/epilogue/` via direct URL after only M5).
**Resolved at:** pre-pilot hardening pass (paired with TD-012).

---

## TD-014 — Selective deletion of individual reflections / AILST responses

**Status:** Active. Defer to post-pilot Phase G/H.
**Where:** new buttons in `/profile/privacy/` and per-item endpoints in `apps/compliance/views.py`.

C.4 ships full account anonymization (Art. 17) as the only deletion path. GDPR Art. 17 is satisfied by erasure of "the data"; participants can already remove everything via that one action. The fine-grained "delete this specific reflection" / "delete this specific AILST response" experience requires additional UX and per-type cascade rules (clearing a reflection also clears its RAG feedback and DTP narrative; deleting an AILST response also clears the cached factor scores), plus consistency rules between selective delete and the JSON export.

Out of scope for C.4. Implement in Phase G/H when the platform has lived data from the pilot and the question "which items would participants actually want to delete?" can be answered empirically.

---

## TD-015 — Data export as PDF (in addition to JSON)

**Status:** Active. Defer to post-pilot Phase G/H.
**Where:** `apps/compliance/services.py` + `apps/compliance/views.py`.

C.4 ships GDPR Art. 15 right-of-access as a JSON download. Some participants — particularly older educators less comfortable with raw JSON — would benefit from a human-readable PDF version (sections per data category, table of consents, narrative summary, etc.). Requires reportlab or weasyprint integration, page-break and pagination logic, embedded fonts for Greek text rendering.

The JSON form is the canonical Art. 15 deliverable and is enough for compliance. PDF is a UX nicety.

---

## TD-016 — 7-year ConsentRecord retention cleanup

**Status:** Active. Defer to Phase H (production-scale operations).
**Where:** `apps/compliance/management/commands/expire_old_consents.py` (new) + scheduled task.

ConsentRecord rows are kept indefinitely post-erasure per D12 of the C.4 design (IRB / GDPR audit window of 7 years). Beyond 7 years, rows can and should be deleted under data minimisation. This needs:

  - Management command `expire_old_consents --commit` that deletes rows where `granted_at < NOW - INTERVAL '7 years'` AND the linked user is anonymized (auth_user with `is_active=False` and the anonymized-username sentinel).
  - Nightly schedule (or weekly) via cron / systemd timer / Django-Q.
  - Dry-run mode by default; explicit `--commit` flag to perform deletes.
  - Mirror the pattern of the existing `redact_old_consent_ips` command.

Trivial implementation — ~80 LOC — but no urgency until the platform has been live for years. Bundle with the broader Phase H retention-policy work.

---

## TD-017 — Machine-readable AI content markers (Article 50(2)) — C.3

**Status:** RESOLVED in Phase C C.3, four-commit arc (2026-05-12). Commits `6b9ec09` (storage + backfill) + `1bc8e55` (write hooks) + `0d91191` (export mirror + HTML data-attrs) + this commit (`{% ai_provenance %}` + `{% ai_provenance_jsonld %}` template tags + page-level JSON-LD on tab5 + privacy_dashboard). Verified by 31 tests across `apps/compliance/tests.py` (storage, export mirror, HTML rendering, JSON-LD validity, template-tag fallbacks) + 6 tests in `apps/modules/tests.py` (forward-write hooks + CP-9 transaction-atomic invariant). Full Phase C suite passes at 214.

The original Active status block is kept below for historical context.

**Status (historical):** Active. Phase C C.3 piece in flight (2026-05-12). Commit 1 of 4 in progress at the time of this entry.
**Where:** `apps/compliance/models.py::AIArtefactProvenance`, `apps/compliance/services.py::record_ai_provenance`, `apps/compliance/management/commands/backfill_ai_provenance.py`, `apps/compliance/templatetags/ai_provenance.py` (commit 3), `rag_query_system.py` write paths (commit 2a), `apps/modules/views.py` save hooks (commit 2a), `templates/modules/tabs/tab5_reflection.html` (commit 2b), `templates/compliance/privacy_dashboard.html` (commit 2b).

EU AI Act Article 50(2) recommends that providers of AI systems mark generated content in a machine-readable format. The platform's own AI Disclosure text (`AI_DISCLOSURE_TEXT_V1_PRE_IRB`) explicitly references "Article 50 transparency obligations". C.3 operationalises this commitment with three layers: HTML data-attributes, page-level JSON-LD, and a reusable `{% ai_provenance %}` template tag. Provenance metadata is stored in the new `AIArtefactProvenance` Django model and consumed by both the HTML layer and the C.4 GDPR Art. 15 export (`export_version` bumps `'1'` → `'2'`).

**Design proposal:** `proodos_files/C3_DESIGN_PROPOSAL_AI_MARKERS.md` (D1-D12; D1-D5 approved 2026-05-12 with 10 CP-style corrections).
**Pre-flight audit:** `proodos_files/audit_rag_queries_provenance_20260512.md` (CP-1) — established that `'gemini-2.5-flash'` single-constant backfill is safe (no model-standardisation transition in git history; zero rows in the fallback-path proxy bucket).
**Commit split (CP-4):**
  - Commit 1 (this one): storage model + migration `0005_aiartefactprovenance` + `record_ai_provenance` helper + `backfill_ai_provenance` management command + admin registration + TD-017 + TD-018 entries.
  - Commit 2a: forward-write hooks in `rag_query_system.py` (with `RETURNING id` — CP-3 rejected `SELECT lastval()`) and `apps/modules/views.py`. CP-9 transaction-atomic invariant: `save() + record_ai_provenance()` wrapped in one block at every call site.
  - Commit 2b: HTML data-attrs across all 9 AI rendering sites + export mirror (`_ai_outputs_to_dict` grows a `provenance` sub-dict; EXPORT_VERSION `'1'` → `'2'`) + opacity fix `text-base-content/70` (CP-10).
  - Commit 3: page-level JSON-LD (schema.org/CreativeWork) + `{% ai_provenance %}` template tag using `{% blocktrans %}` (CP-5: single translatable string with placeholders, Greek-word-order safe) + close-out (roadmap + plan changelog + session log).

**Deployment order (CP-2):** C.3 deploy → `backfill_ai_provenance --commit` → CP-11 wipe → pilot recruitment. Backfill runs BEFORE CP-11 because CP-11 cascade-clears the 19 non-staff `rag_queries` rows in scope; running backfill after CP-11 would leave the interim window between deploy and CP-11 with inconsistent provenance during staff testing.

**Resolved at:** commit 3 of this piece (status block will be moved to RESOLVED form, with hash references for commits 1 + 2a + 2b + 3).

---

## TD-018 — Per-artefact-instance AI dispute deep-links

**Status:** Active. Defer to post-pilot Phase G/H.
**Where:** `apps/modules/urls.py` (URL pattern), `apps/modules/views.py::save_ai_dispute`, `apps/modules/models.py::AIOutputDispute` (likely schema extension), `templates/modules/tabs/tab5_reflection.html` (UI deep-link).

The existing dispute flow is keyed on `(user, module, feature_type)` where `feature_type ∈ {'RAG', 'RTM', 'DTP'}` — one dispute row per user/module/feature, not per artefact instance. A teacher who wants to dispute "this specific DTP narrative" must do so at module level; there is no per-artefact-instance deep-link.

The C.3 design proposal initially planned to emit a per-artefact dispute link from the `{% ai_provenance %}` template tag using `(kind, id)` URL parameters. Pre-implementation verification (CP-6) showed the URL pattern doesn't carry those parameters today, and adding per-artefact-instance disputing would require:

  - New URL pattern: `modules/<str:code>/dispute/<str:kind>/<int:id>/`
  - View extension to look up the artefact by `(kind, id)`
  - `AIOutputDispute` schema extension: drop `unique_together=(user, module, feature_type)` in favour of one row per artefact instance (or, alternatively, add `artefact_kind` + `artefact_pk` columns and switch unique_together)
  - UI change: deep-link button next to each AI artefact in `tab5_reflection.html`

That work is >100 LOC of dispute infrastructure not strictly required for Article 50(2) machine-readability. The existing module-level dispute UI remains accessible to participants during the pilot.

**Discovered in:** C.3 design pre-implementation verification, 2026-05-12.
**Implementation effort:** ~150-200 LOC + tests + migration if `AIOutputDispute` schema changes.
**Resolved at:** post-pilot Phase G/H, once the pilot answers "do participants want to dispute specific artefacts or whole feature classes?".

---

## TD-019 — Peer synthesis dispute UX

**Status:** Resolved (redefined) — 2026-05-19.
**Where:** `apps/modules/models.py::AIOutputDispute`, `templates/modules/tabs/tab5_reflection.html` peer synthesis card, `apps/modules/views.py::save_ai_dispute`, `apps/modules/tests.py::PeerDisputeFeedbackTest`.

Discovered during C.3 commit 2b pre-implementation verification (2026-05-12): `AIOutputDispute` carried `FEATURE_CHOICES = [('rag',…),('rtm',…),('dtp',…)]` and the dispute UX was wired only on the RAG/RTM/DTP surfaces — peer synthesis had neither a choice nor a UI.

**Redefinition (2026-05-19).** When TD-019 was scoped for D.1 (the perceived-relevance research profile), a construct-validity review changed its shape. RAG/RTM/DTP each make a claim about the teacher's *own* reflection, so a relevance rating is a clean AI-alignment signal. Peer synthesis makes no claim about the teacher — it aggregates anonymised peer reflections — so a relevance rating there would conflate "the AI synthesised well" with "the cohort happened to be relevant to me". A peer rating is therefore **not** added to the D.1 alignment instrument. Instead, peer synthesis gets a distinct, honestly-named **usefulness** question ("Did you find this synthesis useful?"), kept out of the D.1 profile.

**Resolved by** (2 commits, 2026-05-19):
  - `('peer', 'Peer Synthesis')` added to `FEATURE_CHOICES`; the `AIOutputDispute` docstring now documents the two distinct constructs sharing the table; metadata-only migration `0014` (Django choices create no DB CHECK constraint — `sqlmigrate` confirmed a no-op).
  - `save_ai_dispute` whitelist extended to `'peer'`; `dispute_peer` loaded into the TAB5 context; a usefulness HITL block added to the peer synthesis card (no `reason` dropdown — the existing alignment-flavoured reasons do not fit usefulness); `PeerDisputeFeedbackTest` (3 tests).

The D.1 perceived-relevance aggregation must whitelist `rag/rtm/dtp` only — peer rows are a separate construct.

---

## TD-020 — Post-hoc career-stage exploratory analysis

**Status:** Active. Defer to post-pilot research analysis (Phase I dissertation work).
**Where:** No code site. Statistical analysis plan addendum to be drafted alongside the dissertation's results chapter.

**Origin.** During Phase C planning, "Career Stage RAG personalisation" was scoped as the second half of C.2 Step 2 — add a `career_stage` parameter to the RAG prompt builder, derive it from `teacher_profile.teaching_years`, and differentiate feedback emphasis (early-career → ethics framing, experienced → workload relief). On 2026-05-13 the decision was taken NOT to implement this pre-pilot (Option A). The four rationale points are recorded in `PROODOS_UNIFIED_ROADMAP.md` §3.C.2 Step 2: (a) the dissertation chapter §8.1 already documents the absence of career-stage personalisation as an acknowledged scope limitation; (b) the proposed mapping lacks documented theoretical/empirical backing and would create an unjustified design claim; (c) introducing differentiated treatment now requires IRB protocol amendment + statistical plan update + per-stage stratified analysis underpowered at ~25 users/stage; (d) Phase C is structurally complete and frozen for IRB review, and adding new AI behaviour risks delaying IRB submission.

**What this TD captures.** The platform DOES collect `teaching_years` at onboarding (existing M2 field) and the value is stored per participant for the full pilot duration. This is enough data to run an EXPLORATORY (not confirmatory) post-hoc analysis after the pilot completes:

  - **Question 1:** Do participants in different career-stage bins (early-career 0-5 / mid-career 6-15 / experienced 16-25 / veteran 25+ years) show differential AILST T2-T0 deltas (overall and per factor: K, A, U, E)?
  - **Question 2:** Are RTM tension patterns (which tensions get surfaced, how they are positioned) systematically different across career-stage bins?
  - **Question 3:** Is reflection quality (length, depth indicators) correlated with career stage?
  - **Question 4:** Does the dispute-rating distribution (👍 / partial / no) vary by career stage — i.e., do experienced teachers reject AI feedback at different rates?

These are framed as **post-hoc exploratory** questions, NOT as primary research hypotheses, because the platform did not apply differentiated treatment. Career stage becomes a *predictor* in the analysis, not a *treatment factor*. Reporting must explicitly disclose this framing to avoid spurious confirmatory inference.

**Effort:** ~3-5 days of statistical work post-pilot (SQL queries against the existing `teacher_profiles` + `ailst_responses` + `reflection_tensions` + `user_module_progress` tables; visualisation in the dissertation's results chapter; an honest "exploratory analysis" caveat block).

**Dependencies:** none. The data is already being collected.

**Resolved at:** post-pilot Phase I (dissertation results chapter). The TD entry is closed once the analysis is written up.

---

## TD entry conventions

When adding a new entry:

1. **TD-NNN** sequential id, never recycled
2. **Status:** one of `Active` / `Deferred` / `Fixed in commit <hash>` / `Acknowledged, no fix planned`
3. **Where:** specific file/path/symbol
4. Brief rationale + concrete forward path (so future-you doesn't start from zero)
5. Cross-reference audit reports / commits / memory files where relevant
