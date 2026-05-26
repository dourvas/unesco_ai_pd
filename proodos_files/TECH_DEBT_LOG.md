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

**Status:** RESOLVED in Phase G (2026-05-21 → 2026-05-23). The full Epilogue feature shipped across seven commits matching the v2 §19 commit plan (G.0 schema, G.1 Stage 0 dashboard, G.2a/b/c three-phase dialogue, G.3 Learning Portrait + PDF). All four design questions from the C.2.5 placeholder spec — Stage 0 visualisation, three-phase dialogue, Learning Portrait, re-entry policy — are answered in `proodos_files/PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2_20260521.md` (PI-approved 2026-05-21, two implementation-correction amendments §22/§23 added during G.3 and before G.6a). The one-shot invariant from this TD's spec is preserved (`OneToOneField`); post-pilot replay is logged as TD-022 (below) with an explicit mechanical migration path. The G.6 magazine design upgrade follows in design-proposal form (`PHASE_G_G6_DESIGN_PROPOSAL_v2_20260523.md`); G.6a-e implementation is the next code-bearing block.

Final test count after Phase G G.3: 470/470 platform tests pass (96 Epilogue + dialogue + portrait + agent tests added by Phase G).

Original analysis kept below for historical context.

**Status (historical):** Active. Defer to post-pilot Phase G/H (or whenever the synthesis-and-dialogue feature is prioritised).
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

**Status:** Scheduled to resolve in Phase H — see `PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md` §8. Command name finalised as `prune_old_consent_records` (parallels existing `redact_old_consent_ips`); dry-run by default, `--apply` flag to delete.
**Where:** `apps/compliance/management/commands/prune_old_consent_records.py` (new) + external scheduler (cron / Windows Task Scheduler).

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

## TD-021 — Teacher dashboard duplicates the Modules menu

**Status:** Scheduled to resolve in Phase H — see `PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md` §7. Decision finalised as **option (a) + slim (b) hybrid**: per-teacher UNESCO 5×3 progress matrix (lift of the D.4 cohort matrix to individual grain) + next-action card + certificate panel (the H.3 download landing point). Reaffirms the hard constraint: dashboard remains completion-structure, NOT developmental-evolution (Epilogue Stage 0 owns evolution).
**Where:** `apps/users/views.py::dashboard`, `templates/home.html`, the Modules navigation menu.

**Problem.** The teacher dashboard (`/dashboard/`, rendering `home.html`) builds `modules_with_progress` — every published module with its per-module completion percentage — and displays it. This is the same information the Modules navigation menu already presents. The dashboard, as it stands, is a second module list, not a distinct surface. Raised by John, 2026-05-20.

**Constraint — what it cannot become.** The dashboard must NOT be turned into a "personal evolution" view (per-teacher DTP curve + RTM tension trajectories). That view is, by an explicit April 2026 design decision, the PROODOS Epilogue's Stage 0 — the "Personal Evolution Dashboard"; the Epilogue patch notes state that building it in a second place would be an architectural mistake. The Epilogue owns developmental *evolution*; the teacher dashboard must not duplicate it.

**Forward path — options to weigh in the UX pass:**
  - **(a) Per-teacher UNESCO 5×3 progress matrix.** Re-present the dashboard as the teacher's own competency-grid progress (5 aspects × 3 levels), reusing the visual component built for D.4's cohort matrix at the individual grain. A genuinely different presentation from the Modules menu's flat list, and — being completion-structure, not developmental-evolution — it does not collide with the Epilogue.
  - **(b) Slim the dashboard** to a landing / orientation surface (next action, announcements, links) and drop the redundant module list.
  - **(c) Remove the dashboard** and route `/dashboard/` to the Modules menu.

Decision deferred; needs a short design note (grounded in the learning-analytics-dashboard literature) before implementation.

**Dependencies:** D.4's UNESCO-matrix visual component (option a would reuse it).

**Resolved at:** a dedicated UX pass — see status line.

---

## TD-022 — Epilogue replay (post-pilot)

**Status:** Active. Defer to **post-pilot** (re-entry policy decision needed after pilot data is analysed).
**Where:** `apps/epilogue/models.py::EpilogueCompletion` (the `OneToOneField` to `auth.User`) + `apps/epilogue/views.py::epilogue_placeholder_view` (the row creation + first-entry freeze).

Phase G shipped with the **one-shot Epilogue** invariant enforced at the DB level via `OneToOneField` (PROODOS Epilogue v2 §9 + Q1 decision). This was chosen for research-design integrity during the pilot: the Stage 0 snapshot is frozen on first entry (v2 §5.4), the dialogue runs once, the Learning Portrait is generated and accepted once. Every participant's Epilogue artefacts are therefore a single coherent snapshot in time — methodologically the cleanest position for the pilot's qualitative analysis (v2 §13 research variables).

Post-pilot, however, some teachers may benefit from re-entering the Epilogue — refreshing the Stage 0 snapshot as their teaching evolves, re-running the dialogue against newer reflections, regenerating a fresh Learning Portrait. The current model forbids this at the database level; revisiting requires a migration.

**Forward path (post-pilot, fully mechanical):**

1. Drop the `OneToOneField` unique constraint on `epilogue_completions.user_id` — convert to `ForeignKey`.
2. Add an `is_active: BooleanField(default=True)` column, plus a partial unique index `(user_id) WHERE is_active = TRUE` so at most one Epilogue row is active per user at any time.
3. Add a "Start a new Epilogue" action on the user dashboard (only visible when an `is_active=True` row exists with `completed_at` set, i.e. the prior one is finished). The action flips the prior row's `is_active=False` and creates a new row with `is_active=True`.
4. The Stage 0 snapshot and Learning Portrait flows are unchanged — they continue to operate on the active row.
5. The dissertation methodology chapter discloses that replay was disabled during the pilot to keep per-participant Epilogue artefacts singular; post-pilot replay is described as a teacher-facing affordance, not a research instrument.

**Why deferred:** the pilot's research questions (v2 §13) treat the Epilogue as a single synthesis event per participant. Replay introduces a `replay_index` covariate that the pre-registered analysis plan does not currently account for. Better to ship the one-shot model, complete the pilot, then enable replay for the post-pilot user community without contaminating the research record.

**Estimated effort:** ~80-120 LOC + 1 additive migration + UI on dashboard. Tests: covered by the existing G.3 test surface plus a new "second Epilogue allowed once prior is_active=False" assertion.

**Discovered / scoped in:** PROODOS Epilogue design proposal v2 §9 + §18 (B.2 review item), 2026-05-21.
**Resolved at:** Post-pilot release.

---

## TD-023 — M15 RAG corpus versioning (defensive)

**Status:** Acknowledged, no fix planned (under the pilot feature-freeze). To be re-evaluated only if M15 content is ever edited mid-pilot.
**Where:** `apps/modules/main_content` row for M15 + the RAG ingestion pipeline that feeds the `rag_queries` retrieval corpus from module main_content text.

Phase G v2 §12 mandates a one-time M15 content alignment (G.4) — rewriting the pre-D.3a DTP description (Similarity Curve SVG + High/Moderate/Significant table) for the D.3a dual-signal DTP, plus a small Part 5 Epilogue notice clarification. The content edit is followed by a one-time **M15 RAG re-ingest** so the retrieval corpus matches what teachers see in TAB2.

The risk this TD logs is **contamination of the RAG retrieval corpus across content versions**: if two teachers in the same pilot retrieve from M15 against two different versions of the corpus, their AI feedback is comparable on different evidence bases — a hidden methodological variable.

**v2 §12.1 resolution: timing, not versioning.** Phase G is pre-pilot work. Per the v2 commit plan, every code-bearing phase and C.5/C.6 run **before** participant recruitment. The M15 content edit + RAG re-ingest therefore happens while there is no pilot participant; current M15 completions are test data. The C.6 pre-pilot operational sequence (PROODOS_UNIFIED_ROADMAP.md §3.C.6) is amended in G.4 to include a "confirm M15 content edit + RAG re-ingest done" step.

**RAG-corpus versioning is unnecessary under the pilot feature-freeze.** This TD logs the assumption explicitly: if M15 content is ever edited **mid-pilot** (in violation of the feature-freeze), RAG-corpus versioning per `RAGQuery` row becomes necessary — every persisted RAG query needs to remember which content version it retrieved against, and analyses must group queries by version.

**Forward path (only if mid-pilot M15 edit is ever needed):**

1. Add `rag_corpus_version: CharField(max_length=20)` to the raw-SQL `rag_queries` schema; mint a `RAG_CORPUS_CURRENT_VERSION` constant in settings; bump on every M15 (or any module) main_content edit.
2. Stamp every new `rag_queries` row with the current corpus version at insert time.
3. Update the C.4 export (gather_user_export) to include the corpus version per query.
4. Update analysis scripts to group by corpus version before computing aggregates.

**Estimated effort (only if triggered):** ~40 LOC + 1 raw-SQL `ALTER TABLE` + version-bump discipline. The discipline is the load-bearing piece, not the schema.

**Discovered / scoped in:** PROODOS Epilogue design proposal v2 §12.1 + §18 (B.5 review item), 2026-05-21.
**Resolved at:** N/A under pilot feature-freeze; logged so the assumption is explicit.

---

## TD-024 — Local-dev secrets in source + git history before production deploy

**Status:** Acknowledged, **deferred to production-deploy moment** (post-pilot). The repo is currently private + single-developer; production deploy is the natural trigger to harden these.
**Where:** `config/settings.py` (lines around `SECRET_KEY` and `DATABASES`) + ~30 `ingest_*.py` scripts at repo root + various utility scripts (`add_feedback_rating.py`, `check_table_structure.py`, `embed_seed_reflections.py`, `extract_subject_boxes.py`, `get_m1_content.py`, `batch_ingest_part3_apr2026.py`) + helper handoff docs (`HANDOFF_TO_TIER*_SESSION.md`) + `audits/DEAD_SCHEMA_AUDIT_20260509.md`.

The first GitHub push on 2026-05-24 (155 commits, https://github.com/dourvas/unesco_ai_pd, **private**) surfaced two pre-existing hardcoded local-dev credentials:

- **`Django123!`** — PostgreSQL password for the local `unesco_ai_teacher_pd` database. Used by `localhost` PostgreSQL only; embedded literally in `config/settings.py::DATABASES['default']['PASSWORD']` and in every standalone ingest/utility script that opens a `psycopg2.connect(...)` call directly (i.e. bypasses Django's ORM). Present in every commit from the **Initial baseline** (`6b090fa`, 2026-04-25) onward; 7 history commits modify it.
- **`SECRET_KEY = 'django-insecure-sx*zgjka*(ev+pi)qw)rj*vz%+z9ex!*6y4j7ope^5icxfp4#u'`** — Django session/CSRF/signing key. Marked with Django's own `django-insecure-` convention prefix, meaning Django itself flags it as a development-only key not safe for production.

**Risk assessment under current state:**

- Repo visibility = **private** (only the PI account has access). External leak surface = none.
- `Django123!` works only against `localhost` PostgreSQL on the PI's dev machine — no production DB exposure.
- `SECRET_KEY` is dev-only; production deploy will need a fresh key regardless (cookies/CSRF tokens are tied to it).
- **Real risk only materialises** if (a) the repo visibility is flipped public, (b) access is granted to a third party who could mirror history, or (c) production deploy reuses these literal values.

**Forward path (do all three before any production deploy):**

1. **Rotate the local DB password.** New value lives in `.env` (already gitignored). Update `config/settings.py::DATABASES` to read via `os.environ['DB_PASSWORD']` or `python-decouple` / `django-environ`. Update each standalone `ingest_*.py` script to read from the same env var instead of the hardcoded literal.
2. **Regenerate `SECRET_KEY`.** `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` → set as `DJANGO_SECRET_KEY` env var → `SECRET_KEY = os.environ['DJANGO_SECRET_KEY']` in settings.
3. **Decide history-rewrite vs leave-in-history** (only if repo visibility may ever become public or org-shared). `git-filter-repo --replace-text` can scrub `Django123!` from every historical commit; cost is that every commit SHA after the first occurrence changes, breaking any references to commits elsewhere (dissertation, chat logs, other clones). For a research repo that stays private through the dissertation period, **leaving the dev password in history is an acceptable tradeoff** — the credentials are dev-only, the repo is private, and history-rewrite has costs that exceed the benefit.

**Estimated effort:** 30-60 minutes for steps 1-2 (~30 files, mostly find-and-replace of two literals into env-var reads + new lines in `.env`). Step 3 (optional history rewrite): 1-2 hours including a clean reclone verification afterwards.

**Discovered / scoped in:** First-push secrets audit, 2026-05-24, immediately before pushing to `https://github.com/dourvas/unesco_ai_pd` for the first time.
**Resolved at:** Production deploy preparation (post-pilot, before any non-PI account is granted repo access).

---

## TD-025 — Large SQL backups in git history + gitignore pattern gap

**Status:** Partially-fixed (forward-prevention done in commit "Tech-debt hygiene after first GitHub push"). History cleanup deferred.
**Where:** `.gitignore` (forward fix landed in same commit as this entry) + 7 historical commits containing `pre_migration_backup_phaseC_*.sql` files (~48MB each, ~338MB cumulative).

Phase C migrations followed the established workflow rule (memory: `feedback_workflow.md`) of taking a `pg_dump` backup before each migration apply. The backup naming convention is `pre_migration_backup_<phase>_<step>_<date>.sql`. Seven such files from the Phase C M1-M6 + GAMMA1 migrations were inadvertently committed to git history before the first GitHub push:

```
48.3 MB  pre_migration_backup_phaseC_GAMMA1_20260509.sql
48.3 MB  pre_migration_backup_phaseC_M2_20260509.sql
48.3 MB  pre_migration_backup_phaseC_M1_20260509.sql
48.2 MB  pre_migration_backup_phaseC_M6_20260510.sql
48.2 MB  pre_migration_backup_phaseC_M5_20260510.sql
48.2 MB  pre_migration_backup_phaseC_M4_20260510.sql
48.2 MB  pre_migration_backup_phaseC_M3_20260509.sql
```

**Root cause:** the `.gitignore` had `proodos_backup_*.sql` (a different naming pattern) but did not cover `pre_*.sql` — so the pg_dump backups slipped through. Other `pre_*.sql` files that escaped commit by chance are sitting untracked in the working tree (`pre_phaseG_G4_20260524.sql`, `pre_g6c_review_revert_20260524.sql`, `pre_v23_verification_revert_20260524.sql`, etc.).

**Risk:** the backups contain real (test-account) DB content — schema + Phase C test data including hashed passwords + RTM responses. Risk surface mirrors TD-024: bounded under the private-repo assumption, materialises only if visibility flips. Plus the cumulative ~338MB inflates every clone of the repo.

**Forward fix (landed in same commit as this entry):**

- `.gitignore` extended with `pre_*.sql` (catches the entire pg_dump-before-migration naming convention going forward) + `_commit_msg.txt` / `_*.txt` (ephemeral HEREDOC artefacts) + `*_smoke.pdf` + `proodos_matrix_files.zip` (ad-hoc dev outputs that had been sitting untracked).
- All future backups generated by the `pg_dump unesco_ai_teacher_pd > pre_phaseH_*.sql` pattern will be ignored automatically.

**History cleanup (deferred, optional):**

If/when the 338MB clone size becomes a real annoyance OR repo visibility changes:

1. `git-filter-repo --path-glob 'pre_migration_backup_*.sql' --invert-paths` removes the 7 files from every commit they appear in.
2. Rewrites change every SHA after the first impacted commit — same constraint as TD-024 step 3.
3. Anyone with a clone needs to re-clone after the rewrite.

Until then: backups remain in git history; they don't slow normal development.

**Estimated effort:** forward fix = done (5 minutes, this commit). History rewrite (if ever triggered) = 30 minutes + clean reclone verification.

**Discovered / scoped in:** First-push size audit, 2026-05-24, immediately before pushing to `https://github.com/dourvas/unesco_ai_pd` for the first time.
**Resolved at:** Forward-prevention resolved 2026-05-24 in commit alongside this entry; historical cleanup remains optional and deferred.

---

## TD-026 — Certificate of Attendance copy revision (Phase H.3 follow-up)

**Status:** Active. PI feedback during browser test 2026-05-26 — three
edits to the bilingual `templates/pdf/certificate_of_attendance.html`
template before the certificate is finalised for the pilot.

**Where:** `templates/pdf/certificate_of_attendance.html` (the EN
front-face body block + Greek parallel block), parallel changes in
both languages.

**Three edits:**

1. **Remove the AILST prerequisite paragraph.** Current body text
   ends with:
   > "The closing AI Literacy Scale for Teachers (AILST,
   > Ning et al., 2025; version `ning_2025_v1`) self-assessment was
   > completed as the certification prerequisite."
   PI feedback: this is not relevant to the recipient of a
   participation certificate and reads as research-instrument
   bleed-through (an internal label leak per the project-wide rule).
   Drop the paragraph entirely from both EN and EL blocks. The fact
   that a closing measurement was taken is already implicit in
   "completed the 15-module PROODOS programme" — no need to name
   the instrument on the certificate face.

2. **Add programme duration in weeks.** A new line under the
   standfirst showing the total programme length. **Provisional
   value committed 2026-05-26: 15 weeks** (PI-set, pending TD-027
   bibliographic refinement).

3. **Add total programme hours.** A second new line showing the
   aggregate teacher hours. **Provisional value committed
   2026-05-26: 75 hours** (15 weeks × ~5h/week). The 75h figure
   contradicts the `Module.estimated_hours=4` default — TD-027
   resolves whether the per-module default flips to 5, or hours
   become non-uniform per module and the total is recomputed
   from the sum.

**Effort:** ~1 hour once TD-027 lands (template edit + EN/EL
parallel + tests).

**Discovered in:** Phase H.3 browser test pass, 2026-05-26.

---

## TD-027 — Bibliographic-grounded re-design of programme duration

**Status:** Resolved (aggregate) 2026-05-26 — see
`proodos_files/PROODOS_PROGRAMME_DURATION_METHODOLOGY_v1_20260526.md`
for the full bibliographically-grounded methodology document. The
aggregate workload (75 hours / 15 weeks / 2.5 ECTS) is settled and
shipped via `settings.CERTIFICATE_PROGRAMME_*` constants. Per-module
non-uniform hour allocation remains open pending the TAB1 audit
(see "What remains" below).

**Original status (historical):** Active. Open research question raised by PI 2026-05-26.

**Where:** `apps/modules/models.py::Module.estimated_hours` (current
default = 4h per module, set at C.2 initial model creation; no
bibliographic justification was attached at the time), the implicit
total programme length (currently undocumented anywhere), and the
two duration values that TD-026 will print on the certificate.

**The question (PI wording, 2026-05-26):**
> "The matter of the total programme duration and the hours
> required per module must be re-negotiated and we should look at
> it with reference to the literature so we can take decisions."

**Why this matters:**

- The certificate (TD-026) prints "Programme duration: N weeks" and
  "Total study hours: N hours" — these are claims that ΕΗΔΕ ΔΙ.ΠΑ.Ε.
  may scrutinise and that the participant will use externally
  (portfolio, professional credit). The values must be defensible.
- The current `Module.estimated_hours = 4` default is a
  placeholder, not a bibliographically-grounded estimate.
- Teacher professional-development literature (Darling-Hammond,
  Hyler & Gardner 2017; Desimone 2009; Yoon et al. 2007) has
  established findings on effective PD duration thresholds —
  typically at least 14-20 contact hours, often spread over weeks
  for sustained-impact PD. PROODOS should sit within (or above)
  the empirically-supported range and justify the choice.

**Forward path:**

1. **Literature exploration** in `Literature_Review_Synthesis_Note(1).md` —
   new section on effective TPD duration. Verify candidates:
   Darling-Hammond et al. 2017 (Learning Policy Institute review),
   Desimone 2009 (5-feature PD framework + duration), Yoon et al.
   2007 (meta-analysis — 14h threshold), plus the Erhardt et al.
   2025 systematic review already in the lit-note for cross-
   reference. Each reference verified before citation per the
   project standing rule.
2. **Decision dialogue** between PI and the lit-note evidence —
   what duration profile does PROODOS commit to? Per-module hours,
   spread across how many weeks?
3. **Update `Module.estimated_hours`** values + add a model-level
   docstring citing the lit-note section. If per-module hours are
   not uniform (e.g., Acquire modules lighter than Create modules),
   the seed data needs editing too.
4. **Compute total programme hours + weeks** from the per-module
   values (helper function in `apps/modules/services.py`).
5. **Feed back into TD-026** — the certificate prints these
   bibliographically-grounded values.
6. **Mirror into the dissertation methods chapter** — the duration
   defence becomes part of the doctoral argument.

**Effort:** ~1 day for the lit-note exploration + decision; ~0.5
day for model + service + certificate edits.

**What remains (TAB1-audit-dependent):**
- Per-module `Module.estimated_hours` non-uniformity, if the audit
  reveals modules whose Tab content distribution genuinely diverges
  from the methodology's §4 default decomposition (5h uniform).
- Possible flip of `Module.estimated_hours` default from 4 → 5
  (one additive migration) if the audit confirms uniform 5h works
  for all 15 modules.
- TAB1 Learning Objectives + About this Module per-module update
  is tracked separately under TD-028 (TAB1 audit, created
  2026-05-26).

**Discovered in:** Phase H.3 browser test pass, 2026-05-26 — the
certificate copy revision (TD-026) surfaced the implicit
unjustified-defaults problem.

---

## TD-028 — TAB1 audit (Learning Objectives + About this Module vs CONTENT_VALIDATION_MATRIX)

**Status:** Active. New session. Raised by PI 2026-05-26
alongside TD-027 resolution.

**Where:** Per-module TAB1 content. Authoritative reference:
`proodos_files/CONTENT_VALIDATION_MATRIX.md` §74 "Αναλυτική
Τεκμηρίωση ανά Module" — the per-module justification of
content choices. The TAB1 fields *Learning Objectives* and
*About this Module* must mirror that justification accurately.

**Why this matters.** After the large content pass across all 15
modules during Phases A–G, the static TAB1 fields may no longer
reflect the current TAB content distribution. PI observation:
"μετά από το μεγάλο πέρασμα στο περιεχόμενο που κάναμε από όλες
τις ενότητες ίσως δεν αντικατοπτρίζει την αλήθεια" (2026-05-26).
Two consequences if left unchecked: (a) onboarding teachers see
outdated module orientations and form wrong expectations, (b) any
viva examiner who cross-reads TAB1 against the methodology
document or against the CONTENT_VALIDATION_MATRIX will hit an
inconsistency.

**Forward path:**

1. **Per-module read** of CONTENT_VALIDATION_MATRIX §74 entry for
   M1 through M15 in order.
2. **Per-module compare** with the current TAB1 fields stored on
   the Module model (`Module.about_this_module`,
   `Module.learning_objectives` or whichever fields hold these
   values — confirm the exact field names at audit start).
3. **Per-module update** where the matrix entry and the current
   TAB1 content diverge. Updates are content-only; no schema
   change.
4. **Per-module Tab-distribution check** for the purposes of
   resolving TD-027's open per-module hour-allocation question.
   If a module's Tab content distribution genuinely diverges from
   the methodology's §4 default decomposition
   (`PROODOS_PROGRAMME_DURATION_METHODOLOGY_v1_20260526.md`),
   record the divergence so Module.estimated_hours can be set
   non-uniformly with the 75h total preserved.
5. **TD-027 close** once the audit lands. TD-026 (certificate
   copy revision) also closes at that point — the certificate
   prints the methodology's settled values.

**Effort:** ~1 day (15 modules × ~3 minutes each per audit cell +
~10 minutes per module needing a real rewrite + the Tab-distribution
check). Best done in a session focused on this single task.

**Dependencies:**
- `proodos_files/CONTENT_VALIDATION_MATRIX.md` (read-only reference).
- `proodos_files/PROODOS_PROGRAMME_DURATION_METHODOLOGY_v1_20260526.md`
  (read-only reference; supplies the §4 Tab-distribution baseline).

**Resolved at:** future session — separate from TD-027 commit.

---

## TD entry conventions

When adding a new entry:

1. **TD-NNN** sequential id, never recycled
2. **Status:** one of `Active` / `Deferred` / `Fixed in commit <hash>` / `Acknowledged, no fix planned`
3. **Where:** specific file/path/symbol
4. Brief rationale + concrete forward path (so future-you doesn't start from zero)
5. Cross-reference audit reports / commits / memory files where relevant
