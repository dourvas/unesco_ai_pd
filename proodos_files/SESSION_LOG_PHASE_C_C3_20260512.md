# Phase C Session Log — C.3 machine-readable AI markers — 12 May 2026

**Date:** 2026-05-12
**Session scope:** Phase C C.3 — Machine-readable AI content markers (EU AI Act Article 50(2)). Four-commit arc, end-to-end.

**Author:** Claude Code session
**Companion logs:**
  - `SESSION_LOG_PHASE_C_M1_M3_20260509.md`
  - `SESSION_LOG_PHASE_C_M4_20260510.md`
  - `SESSION_LOG_PHASE_C_M5_M6_20260510.md`
  - `SESSION_LOG_PHASE_C_C20_C22_20260510.md`
  - `SESSION_LOG_PHASE_C_C23_C25_20260511.md`
  - `SESSION_LOG_PHASE_C_C4_C1_CP11_20260512.md`

**Design proposal:** `proodos_files/C3_DESIGN_PROPOSAL_AI_MARKERS.md` (D1-D12 approved with 10 CP-style corrections; D10 revised mid-arc to Option C after the pre-implementation discovery of existing XAI panels).
**Pre-flight audit:** `proodos_files/audit_rag_queries_provenance_20260512.md` (CP-1) — validates single-constant `gemini-2.5-flash` backfill strategy.

---

## Phase C status — end of session

C.3 is complete. Phase C code-bearing work fully done. Remaining: external IRB review (CP 7 + CP 10) and the operational CP-11 wipe before pilot recruitment.

| Piece | Status |
|---|---|
| All Phase C migrations | APPLIED |
| C.2.0–C.2.5b | DONE (prior arc) |
| C.4 Privacy dashboard | DONE (prior arc, `eb36db1` + `6055616` + `1dee58b`) |
| C.1 AI Impact Assessment | DONE (prior arc, `f64cbda`) |
| C.6 Sequential gates (TD-012 + TD-013) | DONE (prior arc, `050aba7`) |
| CP-11 wipe script | READY (prior arc, `950e44a`) |
| **C.3 Machine-readable markers** | **DONE this session — four commits** |
| CP 7 / CP 10 IHU IRB review | External dependency |

## Commits this session

| Commit | Title |
|---|---|
| `6b9ec09` | C.3 commit 1: AIArtefactProvenance storage layer + retroactive backfill |
| `1bc8e55` | C.3 commit 2a: forward-write hooks for AI provenance |
| `0d91191` | C.3 commit 2b: export mirror + HTML data-attrs + Option C XAI work |
| (this) | C.3 commit 3: template tags + page-level JSON-LD + close-out |

Four commits. Two of them landed review-driven corrections during implementation (D10 revised to Option C after pre-implementation discovery of existing XAI panels; the export_version regression test fix during 2b's full-suite run). The pattern of "draft → discover existing state → refine → commit" caught at least one redundant-UX outcome and one regression that would otherwise have shipped.

## Test suite — 214 across the five Phase C apps

| App | Tests | Δ this session |
|---|---|---|
| `apps.compliance` | **115** | +31 (10 commit 1 + 8 commit 2b + 7 commit 3 + 6 commit 2a regression-fix lift + 1 export_version fix) |
| `apps.users` | **23** | unchanged |
| `apps.ailst` | **47** | unchanged |
| `apps.modules` | **19** | +6 (commit 2a forward-write hooks) |
| `apps.epilogue` | **16** | unchanged |

The 6 new modules tests are in `AIProvenanceWriteHookTest` (5 happy-path tests, one per save site, plus the CP-9 invariant rollback test).

## Notable decisions and discoveries

### Pre-flight audit (CP-1)

Before commit 1, an empirical audit of `rag_queries.created_at` + git blame on `rag_query_system.py` established the backfill strategy:

  - 98 historical `rag_queries` rows over ~13 weeks. 24 with current owners (5 staff + 19 non-staff); 74 orphan rows whose `user_id` predates current `auth_user` rows.
  - Git blame shows the `gemini-2.5-flash` literal was introduced in the initial baseline commit `6b090fa`; no model-standardisation transition appears in tracked history.
  - The fallback-path proxy bucket (`generation_tokens IS NULL OR = 0`) is empty.
  - Decision: single-constant backfill `model_name='gemini-2.5-flash'`. Orphan rows skipped (FK to auth_user required).

The audit doc `proodos_files/audit_rag_queries_provenance_20260512.md` is referenced from TD-017 and from the design proposal §3 D5a.

### Design proposal — 10 CP-style corrections before commit 1

D1-D5 defaults approved on the first round; ten CP-style corrections applied before any code:

  - CP-1 — pre-flight audit (the work described above)
  - CP-2 — deployment order: C.3 deploy → backfill → CP-11 wipe → pilot (not the originally-proposed "between CP-11 wipe and pilot" — backfill would have no work after wipe)
  - CP-3 — `RETURNING id` is the sole id-extraction path for `rag_queries` INSERT; `SELECT lastval()` rejected as race-prone under concurrent inserts
  - CP-4 — commit 2 split into 2a (write hooks) + 2b (read paths), four commits total, each bisectable
  - CP-5 — visible attribution line uses `{% blocktrans %}` with named placeholders so Greek translation can re-order them
  - CP-6 — pre-implementation verification of the `modules:dispute` URL: existing pattern is keyed on module code + `feature_type` body param, not per-artefact; per-artefact deep-links opened as TD-018
  - CP-7 — backfill uses `get_or_create` semantics keyed on `(artefact_kind, artefact_pk)`; silent get branch; safe for mixed forward + retroactive scenarios
  - CP-8 — `EXPORT_VERSION` bumped `'1'` → `'2'` with backward-compat note in services.py docstring
  - CP-9 — `record_ai_provenance` calls wrapped in the same `transaction.atomic` block as the source-row save at every call site
  - CP-10 — opacity decision: attribution text uses `text-base-content/70` (later reinterpreted under Option C — the line lives inside an existing XAI panel grid using `/60` labels, so the standalone-opacity concern is moot)

### Mid-arc Option C revision

Pre-implementation verification of `templates/modules/tabs/tab5_reflection.html` (during commit 2a) revealed that **existing XAI disclosure panels already cover three of the four AI outputs** (RAG live, RAG completed, DTP) plus an RTM panel further down. Each carries Model + Input + Logic + Intent + EU AI Act Limited Risk language. The originally-planned standalone attribution line ("Generated by gemini-2.5-flash on …") would have duplicated this material with weaker copy.

D10 was revised to Option C:

  - C.1 — Drop the standalone attribution paragraph
  - C.2 — Add one new row inside each existing XAI panel's grid: "Generated at: <timestamp>". The current panels say "Model: Gemini 2.5 Flash" generically; the timestamp surfaces per-artefact uniqueness
  - C.3 — Add a NEW XAI panel for peer synthesis (parity with RAG/DTP/RTM — peer was previously rendering without disclosure)
  - C.4 — Opacity concern from CP-10 moots out under the new layout (label uses panel's `/60` color class)

This decision is documented in the design proposal §3 D10 with the rationale and in commit 2a's message.

### TDs opened during the arc

  - **TD-018** (commit 1) — Per-artefact-instance AI dispute deep-links. The existing `modules:dispute` URL is module + feature-type keyed; adding per-artefact deep-links requires URL pattern change + view extension + likely `AIOutputDispute` schema work. Out of scope for Article 50(2); deferred post-pilot.
  - **TD-019** (commit 2b) — Peer-synthesis dispute UX. `AIOutputDispute.FEATURE_CHOICES` does not include `'peer'`; the new peer XAI panel doesn't get a `submitDispute('peer', …)` button row. Adding it requires migration. Deferred post-pilot.

Both TDs are documented with concrete forward paths.

### Regression caught during commit 2b

The full-suite run of commit 2b surfaced a single failure in the pre-existing C.4 test `test_json_top_level_keys_match_spec`, which hard-coded `payload['export_version'] == '1'`. The 2b commit bumps EXPORT_VERSION to `'2'`, so the assertion needed to follow. Fix added in the same commit; comment cross-references the bump.

This is exactly the kind of issue that the four-way commit split (CP-4) was designed to surface — running the full Phase C suite after each commit instead of waiting until the end.

## Architectural decisions captured

  - **D1a (chosen):** new `AIArtefactProvenance` Django model with polymorphic `(artefact_kind, artefact_pk)` reference. `artefact_pk` is `CharField(max_length=64)` because ReflectionTension uses UUIDField for its PK while UserModuleProgress + rag_queries use BigAutoField — heterogeneous source types ruled out an integer column.
  - **D2a (chosen):** template tag accepts `for=record` and emits one row in an existing XAI panel grid. `{% blocktrans %}` reduced to the single-word label ("Generated at"); the timestamp is locale-formatted by Django's `|date` filter.
  - **D3a (chosen):** schema.org `CreativeWork` JSON-LD with `SoftwareApplication` creator. Page-level block injected on tab5 + privacy_dashboard. Per-artefact identification via `identifier: "<kind>#<pk>"`.
  - **D4a (chosen):** full 9-spot coverage (5 tab5 sites + 4 privacy dashboard cards).
  - **D5a + CP-7 (chosen):** management command backfill with `--dry-run` default + `--commit` + typed YES + `get_or_create` idempotency + fallback-path proxy warning.
  - **D10 Option C (revised mid-arc):** drop standalone attribution line; instead surface per-artefact `Generated at` row inside existing XAI panels + add parity panel for peer synthesis.

## Tech debt observations from this session

| ID | Status |
|---|---|
| **TD-017** (machine-readable AI markers) | RESOLVED — four-commit C.3 arc |
| **TD-018** (per-artefact dispute deep-links) | Active, deferred post-pilot |
| **TD-019** (peer-synthesis dispute UX) | Active, deferred post-pilot |
| TD-010 / TD-011 / TD-014 / TD-015 / TD-016 | Active, all explicitly deferred |

## Smoke tests performed this session

  - Backfill dry-run on dev DB after commit 1: produces 112 expected new provenance rows (34 RTM + 14 DTP + 22 RAG + 18 peer + 24 rag_query) — matches the audit numbers row-for-row; 74 orphan rag_queries rows skipped by the INNER JOIN to auth_user.
  - 6 new tests in `AIProvenanceWriteHookTest` (commit 2a) covering each forward-write hook + the CP-9 rollback invariant.
  - tab5 render with 4 prefetched provenance rows: data-ai-* attrs present on the expected containers, `Generated at` row visible in 3 panels (commit 2b).
  - privacy_dashboard render: 4 summary cards carry kind + model + latest_generated_at; no per-artefact id leaked (D2b-4 invariant; commit 2b).
  - Template tag + JSON-LD render and parse as valid JSON-LD with the expected `@type` and `@graph` count (commit 3).

## What's next

  - **IRB review** (CP 7 + CP 10): IHU IRB feedback on AI Disclosure text, Step 3 consent texts, and the AI Impact Assessment notice. When feedback arrives, mint `V2_IRB_REVISED` constants in `apps/compliance/copy.py` per the §3.C.5 checklist.
  - **Pilot recruitment** can begin once IRB approval lands and the CP-11 wipe is run on production. Operational deployment order: C.3 deploy → backfill_ai_provenance --commit → cp11_wipe_test_users.py --commit → pilot recruitment.
  - **Post-pilot work** TD-010 / TD-011 / TD-014 / TD-015 / TD-016 / TD-018 / TD-019: all explicitly deferred.

Phase C is structurally complete.

---

*End of session log. Branch `claude/distracted-hodgkin-0d4988` synced to main at the end of every commit. Working tree clean. 214/214 Phase C tests pass.*
