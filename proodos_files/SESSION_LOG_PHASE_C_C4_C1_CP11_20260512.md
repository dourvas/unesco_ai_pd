# Phase C Session Log — C.4, C.1, footer wiring, TD-012/013, CP-11 — 11-12 May 2026

**Dates:** 2026-05-11 (late) through 2026-05-12 (evening)
**Session scope:**
  - C.4 (Privacy dashboard: per-consent revocation + GDPR Art. 15 data export + GDPR Art. 17 erasure)
  - C.1 (EU AI Act Article 50 transparency notice, replacing the stub)
  - Footer wiring across `base.html` + `landing.html` + `/profile/privacy/` (entry points to the new transparency notice)
  - TD-012 (sequential module-prerequisite gate)
  - TD-013 (Epilogue gating on M15 completion)
  - CP-11 (pre-pilot non-staff user wipe script)

**Author:** Claude Code session
**Companion logs:**
  - `SESSION_LOG_PHASE_C_M1_M3_20260509.md`
  - `SESSION_LOG_PHASE_C_M4_20260510.md`
  - `SESSION_LOG_PHASE_C_M5_M6_20260510.md`
  - `SESSION_LOG_PHASE_C_C20_C22_20260510.md`
  - `SESSION_LOG_PHASE_C_C23_C25_20260511.md`

**Design proposals captured during the session:**
  - `proodos_files/C4_DESIGN_PROPOSAL_PRIVACY_DASHBOARD.md` (D1-D14, then 8 CP-style refinements applied in a second pass before Commit 1 of C.4).

---

## Phase C status — end of session (2026-05-12 evening)

All code-bearing Phase C pieces are now committed. What remains is external (IHU IRB review of consent + transparency text) and operational (running the CP-11 wipe immediately before pilot launch).

| Piece | Status |
|---|---|
| Scaffolding | DONE `09d0e08` |
| M1 | OBSOLETE placeholder |
| M2 | APPLIED `c5818ef` |
| Γ.1 | APPLIED `02db101` |
| M3 | APPLIED `bbe478d` |
| M4 | APPLIED `223ebf3` |
| M5 | APPLIED `dbb35b7` |
| M6 | APPLIED `a3aa285` |
| C.2.0 AI Disclosure Modal + middleware | DONE |
| C.2.1 Profile Edit extension | DONE |
| C.2.2 Step 3 consent + supersede | DONE |
| C.2.3 AILST T0/T1/T2 flow | DONE |
| C.2.4 M5 → T1 gating | DONE |
| C.2.5 PROODOS Epilogue placeholder + M15 → Epilogue → T2 | DONE |
| C.2.5b Confirm interstitial UX | DONE |
| **C.4 Privacy dashboard** (revocation + Art. 15 + Art. 17) | **DONE** this session |
| **C.1 AI Impact Assessment** (Article 50 transparency notice) | **DONE** this session |
| **C.4 follow-up: footer wiring + IHU name fix** | **DONE** this session |
| **C.6 (TD-012 + TD-013) sequential gates** | **DONE** this session |
| **CP-11 wipe script** (operational) | **READY** to run before pilot |
| CP 7 / CP 10 — IHU IRB review of consent + impact-assessment wording | External dependency |

## Commits this session

| Commit | Title |
|---|---|
| `faa783e` | docs: C.4 design proposal — Privacy dashboard + Art. 15 + Art. 17 |
| `528eb77` | docs: C.4 design — apply John's 8 CP fixes before Commit 1 |
| `eb36db1` | Phase C C.4 commit 1: Privacy dashboard + per-consent revocation endpoints |
| `6055616` | Phase C C.4 commit 2: GDPR Art. 15 data export (JSON) |
| `1dee58b` | Phase C C.4 commit 3: GDPR Art. 17 account erasure (anonymization) |
| `2cd0a04` | fix(compliance): erasure confirmation token DELETE (matches English UI) |
| `f64cbda` | Phase C C.1: EU AI Act Article 50 transparency notice (replaces stub) |
| `22d38ad` | fix(footer): wire entry points to AI Act compliance + IHU name fix |
| `050aba7` | Phase C C.6: pre-pilot sequential gates (TD-012 + TD-013) |
| `950e44a` | Phase C CP-11: pre-pilot non-staff user wipe script |

10 commits. Three of them (`2cd0a04`, `22d38ad`, and the 8-CP-fixes-after-design-proposal `528eb77`) are review-driven corrections — each landed after John spotted something the first draft had gotten wrong. The session pattern of "draft → review → fix → commit" continues to catch issues that unit tests alone would not (UI-language consistency, institution name, stale references).

## Test suite — 183 across the five Phase C apps

| App | Tests | Δ this session |
|---|---|---|
| `apps.compliance` | **84** | +63 (38 C.4 surface + 6 C.1 page + 4 footer-wiring + others) |
| `apps.users` | **23** | +4 (CP-11 wipe tests) |
| `apps.ailst` | **47** | unchanged |
| `apps.modules` | **13** | +6 (SequentialModuleGatingTest) |
| `apps.epilogue` | **16** | +4 (EpilogueM15GatingTest) |

All 183 pass. The full Phase C run takes ~3.5 minutes on the dev DB.

## Notable decisions taken this session

### C.4 — Privacy dashboard

Single sustained ~2000-LOC feature delivered in **three commits** per John's split directive:

  1. **Commit 1** — per-consent revocation endpoints (`/profile/privacy/revoke/ai-disclosure/`, `/research/`, `/data-sharing/`). Each endpoint has its own session semantics (ai_disclosure logs out, the other two stay logged in). The AI Disclosure path is the canonical closure of TD-008: it runs `revoke_consent` + clearing `TeacherProfile.ai_disclosure_acknowledged_at` inside a single `transaction.atomic` + `select_for_update` block so the middleware re-shows the modal on the next request.
  2. **Commit 2** — Art. 15 JSON data export. New `apps.compliance.services.gather_user_export(user)` aggregates every personal-data source: TeacherProfile, ConsentRecord, AilstResponse, UserModuleProgress (including reflection text), EpilogueCompletion, and the AI-output set (RTM positions, DTP narratives, RAG feedback, peer synthesis, raw `rag_queries` rows). The `rag_queries` branch is wrapped in a savepoint-protected `transaction.atomic` block so a missing table in fresh environments is a non-fatal empty result.
  3. **Commit 3** — Art. 17 anonymization. New `apps.compliance.services.anonymize_user(user)` is the explicit Python replacement for the dropped historical DB function (`anonymize_user(integer)` was DROP-ed in Γ.1 migration and was column-broken before that — see `audits/DEAD_SCHEMA_AUDIT_20260509.md`). NULLs PII on TeacherProfile and auth_user, retains the auth_user row to keep FK targets alive for ConsentRecord audit trail + AilstResponse research data + UserModuleProgress metadata, clears reflection-content text fields on UserModuleProgress / ReflectionTension / rag_queries, sets `research_data_opted_out=True` (new flag from migration 0010), then logout + redirect.

The supporting migration `users/0010_research_data_opted_out` is additive only (single nullable boolean default False). Pre-apply pg_dump: `pre_migration_backup_phaseC_C4_20260512.sql`.

The design proposal at `proodos_files/C4_DESIGN_PROPOSAL_PRIVACY_DASHBOARD.md` captured 14 decisions; John applied **8 CP-style refinements** before Commit 1, and two more during implementation:

  - **CP-1** (email constraint): `auth_user.email` verified `NOT NULL` but **NOT UNIQUE** in the live schema. The anonymized email uses the sentinel pattern `f'deleted-{user.id}@anonymized.local'` (collision-free by construction) rather than an empty string. Q3 / line-59 contradiction in the original draft fixed.
  - **CP-2** (data_sharing revoke spec): D9 split into D9a (research_participation) and D9b (data_sharing). D9b references the verbatim `DATA_SHARING_TEXT_V1_PRE_IRB` wording — secondary analyses blocked, primary research participation unaffected, `research_data_opted_out` NOT toggled (narrower scope).
  - **CP-3** (session semantics): explicit table summarising the three revoke flows.
  - **CP-4** (rag_queries verification): grep against `apps.modules.models` confirmed field names; `rag_queries` confirmed as raw-SQL outside ORM. The export + anonymization both gained raw-cursor branches with savepoint protection.
  - **CP-5** (fresh-user export): added a dedicated test asserting all top-level JSON keys are present with empty arrays / null values for a user with zero AILST / module / Epilogue / RAG rows.
  - **CP-6** (concurrent POST → unit test): the originally-planned concurrent-POST race test was unreliable in Django's TestCase runner (no true transaction overlap). Replaced with a direct unit test of `revoke_consent` against two ORM-bypass-created active rows — verifies the same invariant.
  - **CP-7** (IRB audit query post-erasure): added a test asserting `ConsentRecord.objects.filter(consent_type='research_participation', granted=True)` over a now-anonymized user still returns the historical row with `consent_text` / `version` intact.
  - **CP-8** (no JS-disabled submit): the erasure confirmation form's submit button stays always-enabled; server-side validation of the typed token is the single enforcement point. Better accessibility.

Two material reversals **during** implementation:

  - **D6 revised — DELETE not ΔΙΑΓΡΑΦΗ.** The original token was Greek on the reasoning that the participant pool speaks Greek. Mid-implementation review (caught by John) noted that the rest of the UI is in English; asking for a Greek token mid-flow is inconsistent. Final token is `DELETE` with a comment block in the view explaining that localisation to `ΔΙΑΓΡΑΦΗ` should happen when the platform ships a Greek UI through Django's translation system, not as a constant.

  - **anonymize_user implementation strategy.** Plan §3.10 referenced the historical `anonymize_user(integer)` PostgreSQL function. Pre-implementation verification revealed it had been **dropped in Γ.1 migration** (`compliance/0002_drop_dead_schema:51`) and was column-broken before that. C.4 implements `anonymize_user` as a fresh Python service rather than calling the missing DB function.

### C.1 — EU AI Act Article 50 transparency notice

The `/about/ai-act-compliance/` page was a stub since C.2.0 ("This page is being prepared..."). Now it serves the seven-section AI Impact Assessment defined as a list of `{'heading', 'body'}` dicts in `apps.compliance.copy.AI_IMPACT_ASSESSMENT_V1_PRE_IRB`:

  1. What PROODOS is (institution + dissertation framing).
  2. AI components — RAG / RTM / DTP / peer synthesis + the post-pilot Epilogue forward-note.
  3. Risk classification — Limited Risk per Article 50, explicit non-applicability of Article 5 / Annex III.
  4. Mitigation and human oversight — consent, dispute submissions, deterministic AILST scoring, pedagogical framing, ongoing alignment evaluation.
  5. Data handling and retention — GDPR Art. 6(1)(a) + 9(2)(j), 7-year retention, IP redaction after 30 days.
  6. Participant rights mapped to the four operational endpoints in `/profile/privacy/`.
  7. Contact — PI, supervisor, institution.

Template `templates/about/ai_act_compliance.html` extends `base.html` (the chrome-less `_locked_base.html` would have been wrong for a public, footer-linked document). Body text passes through the existing `consent_format` template filter so bullets become proper `<ul>/<li>`. Version pin via `settings.AI_IMPACT_ASSESSMENT_CURRENT_VERSION='v1_pre_irb'`, rendered into the page footer for IRB review traceability.

Per John's instruction during this session — *"theorem-assume Epilogue done + IRB approved; if anything diverges we patch"* — new code from this point onward will not carry "pending review / coming soon / will be revised" caveats. The copy in `AI_IMPACT_ASSESSMENT_V1_PRE_IRB` still does carry those caveats explicitly because John wants them retained as easy-to-grep markers for the eventual IRB-revision pass.

### Footer wiring + IHU name fix

Smoke-test discovery: after the C.1 page landed, the only entry point was the AI Disclosure modal's "Learn more" link — shown once. Authenticated users who already acknowledged the disclosure had no path back to the transparency notice unless they revoked their consent.

Three new entry points were wired in commit `22d38ad`:

  - **`templates/base.html` footer** (every authenticated page): About → `/about/ai-act-compliance/`, Privacy → same URL, Contact → `mailto:idourvas@ihu.gr`. Terms removed (no ToS doc exists).
  - **`apps/users/templates/landing.html` footer** (public landing): identical wiring.
  - **`templates/compliance/privacy_dashboard.html`**: contextual "Read the AI transparency notice →" link alongside the existing "Back to profile" link.

Same commit also fixed `templates/base.html` footer: it used to read *"Research Project - International University of Greece"* — the canonical institution name throughout the codebase is *"International Hellenic University (IHU), Thessaloniki"*. Earlier copy fixes (`fb8f4a3`) had landed the correction in landing.html and register.html but missed this footer.

### C.6 — TD-012 + TD-013 (pre-pilot sequential gates)

Smoke test from the previous session (2026-05-11) showed a logged-in user could navigate directly to `/modules/M5/` and to `/epilogue/` without doing prior modules. Acceptable for development cycle speed, invalidating for the research design at pilot time. Closed both gates in commit `050aba7`:

  - **TD-012**: new `apps/modules/services.py` with `get_module_prerequisite_block(user, module)` and `user_has_completed_module(user, code)` helpers. Two enforcement layers in `apps/modules/views.py`:
    - `ModuleDetailView.get` overrides the dispatch: redirects to the first uncompleted prior module with `messages.info`.
    - `mark_tab_complete` returns HTTP 409 with explanatory JSON when invoked out of sequence (defensive AJAX guard).
    - Prerequisite derivation is from `Module.order_index`, not from the existing-but-unused `Module.prerequisites` JSONField.

  - **TD-013**: `apps/epilogue/views.py::_is_m15_completed` guards both `epilogue_placeholder_view` (GET) and `epilogue_complete_view` (POST defence). A non-staff user without M15 completion is redirected to the dashboard with a flash; no EpilogueCompletion row created.

  - Staff and superusers bypass both gates for support. The existing C.2.4 and C.2.5 tests broke when the gates landed (they exercised AILST routing / Epilogue rendering without completing prior modules); the fix was to elevate the test users in those classes to `is_staff=True` and document why, while keeping the new gating-specific test classes (`SequentialModuleGatingTest`, `EpilogueM15GatingTest`) at `is_staff=False` so the gates actually fire.

### CP-11 — non-staff user wipe script

`scripts/cp11_wipe_test_users.py` (commit `950e44a`) operationalises the Option B decision from plan §2.1. Wipes every non-staff non-superuser auth_user; Django CASCADE clears their TeacherProfile, ConsentRecord, AilstResponse, UserModuleProgress, EpilogueCompletion, ReflectionTension, AIOutputDispute, TeacherProfileHistory rows. The raw-SQL `rag_queries` table is cleaned up via explicit `DELETE FROM rag_queries WHERE user_id = ANY(...)` inside the same atomic transaction.

CLI defaults to dry-run (lists targets + per-table cascade footprint). `--commit` requires an interactive typed `YES` confirmation. Core logic exposed as `wipe_non_staff_users(commit, require_typed_confirmation, output)` for direct test calling without the CLI overhead.

The script will be run by John immediately before pilot recruitment, with a fresh `pg_dump pre_pilot_wipe_<date>.sql` backup as the standard operational precaution.

## Tech debt observations from this session

| ID | Status |
|---|---|
| **TD-008** (AI Disclosure revocation must clear ack timestamp) | RESOLVED — C.4 commit 1 atomic revoke+clear flow |
| **TD-010** (post-pilot AILST score reveal feature) | Active, deferred to post-pilot Phase G/H |
| **TD-011** (full PROODOS Epilogue implementation) | Active, deferred — but per John's session-end framing, treat as "done" in new code |
| **TD-012** (sequential module-prerequisite gating) | RESOLVED — C.6 commit `050aba7` |
| **TD-013** (Epilogue gating on M15 completion) | RESOLVED — C.6 commit `050aba7` |
| **TD-014** (selective deletion of single reflections / AILST responses) | Active, deferred to post-pilot |
| **TD-015** (data export as PDF in addition to JSON) | Active, deferred to post-pilot |
| **TD-016** (7-year ConsentRecord retention cleanup job) | Active, deferred to Phase H |

## Smoke tests performed this session

  - **C.4 commit 1**: Privacy dashboard renders, each Withdraw button hits the right endpoint, AI Disclosure revoke logs the user out and triggers the modal on next login (TD-008 fix end-to-end verified).
  - **C.4 commit 2**: JSON download returns the expected structure; opened in a text editor confirms verbatim consent_text + AILST scores + rag_queries rows.
  - **C.4 commit 3**: erasure confirmation page rejects the wrong token, then accepts `DELETE` (originally tested with `ΔΙΑΓΡΑΦΗ` before the D6 revision); auth_user remains in the DB with sentinel username + email; login is rejected because `is_active=False`.
  - **C.1**: page rendered from anonymous + authenticated + unack states; bullet lists formatted correctly via `consent_format` filter.
  - **Footer wiring**: each of the three new entry points reaches the same `/about/ai-act-compliance/` URL.
  - **TD-012 + TD-013**: not browser-smoke-tested this session (would require seeded module rows); covered by the 10 new tests.
  - **CP-11**: dry-run output looked sane on the dev DB; `--commit` not run yet (will run immediately before pilot launch with a fresh backup).

## What's next

Code-bearing Phase C work is complete. Remaining items are operational and external:

  - **IRB review** (CP 7 + CP 10): IHU IRB feedback on AI Disclosure text, Step 3 consent texts, and the AI Impact Assessment notice. When feedback arrives, mint `V2_IRB_REVISED` constants in `apps/compliance/copy.py` and bump the three version-pin settings (`AI_DISCLOSURE_CURRENT_VERSION`, `RESEARCH_CONSENT_CURRENT_VERSION`, `AI_IMPACT_ASSESSMENT_CURRENT_VERSION`). The supersede pattern in `record_consent` already handles existing-row revocation automatically.
  - **Pilot recruitment** can begin once IRB approval lands and the CP-11 wipe is run on production.
  - **Post-pilot work** (TD-010 / TD-011 / TD-014 / TD-015 / TD-016): all explicitly deferred.

---

*End of session log. Branch `claude/pensive-swartz-ed259d` merged to main at the end of every commit. Working tree clean. 183/183 Phase C tests pass.*
