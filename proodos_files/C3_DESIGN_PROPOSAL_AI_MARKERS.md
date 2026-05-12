# C.3 — Machine-readable AI content markers — Design Proposal

**Phase:** C (EU AI Act compliance)
**Tracks:** TD-017 (to be created in commit 1)
**Author:** Claude Code session, 2026-05-12
**Status:** **APPROVED** — D1-D5 defaults signed off with 10 CP-style corrections (2026-05-12); commit 1 implementation now in scope.
**Spec references:**
  - `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` §5 Συμπλήρωμα 3
  - `PROODOS_UNIFIED_ROADMAP.md` §3.C.3 + §3.C.7
  - `apps/compliance/copy.py::AI_DISCLOSURE_TEXT_V1_PRE_IRB` — verbatim references "Article 50 transparency obligations"
  - `proodos_files/audit_rag_queries_provenance_20260512.md` — pre-flight audit underpinning the backfill strategy (CP-1)

---

## 1. Context

The EU AI Act (Regulation 2024/1689) Article 50(2) requires providers of AI systems that generate synthetic content to mark that content in a machine-readable format. For a Limited-Risk AI system — which PROODOS has classified itself as in the disclosed AI Disclosure text — the obligation is read as a recommendation rather than a strict requirement, but the platform's own copy explicitly commits to user-facing AI provenance ("All AI-generated suggestions are advisory" + "Every AI output can be disputed and corrected through the platform").

C.3 operationalises that commitment with three layers stacked on top of every AI-generated output the platform produces: (1) per-element HTML data-attributes carrying model + timestamp, (2) page-level JSON-LD blocks declaring the AI components present, (3) a reusable `{% ai_provenance %}` template tag that the rest of the codebase pulls in. The provenance metadata is stored once per artefact and consumed by the HTML layer AND by the existing C.4 GDPR Art. 15 export (which gains export_version `'2'` to signal the schema change — CP-8).

The C.4 commit 2 added a *partial forward-compatibility marker* (`data-ai-generated="true"` boolean on 4 cards in `privacy_dashboard.html`) — those four spots will be **superseded** by the full provenance markers in this piece, not preserved.

---

## 2. Verification findings (pre-design)

### V1 — AI rendering sites in the codebase today

| # | Site | Template | Line range | AI type | data-ai-generated today? |
|---|---|---|---|---|---|
| 1 | RAG feedback (post-submit) | `templates/modules/tabs/tab5_reflection.html` | 717-722 | Gemini RAG | NO |
| 2 | Peer synthesis | `templates/modules/tabs/tab5_reflection.html` | 819-827 | Gemini peer synthesis | NO |
| 3 | RTM card (in-form) | `templates/modules/tabs/tab5_reflection.html` | 372-485 | Reflective Tension Mapper | NO |
| 4 | DTP card (in-form) | `templates/modules/tabs/tab5_reflection.html` | 499-567 | Developmental Trajectory Predictor | NO |
| 5 | DTP card (on-demand) | `templates/modules/tabs/tab5_reflection.html` | 573-610 | DTP (post-M2) | NO |
| 6 | RTM card (privacy export panel) | `templates/compliance/privacy_dashboard.html` | 215-228 | RTM summary | YES — partial marker (boolean only) |
| 7 | DTP card (privacy export panel) | `templates/compliance/privacy_dashboard.html` | 230-241 | DTP summary | YES — partial marker (boolean only) |
| 8 | RAG feedback card (privacy export panel) | `templates/compliance/privacy_dashboard.html` | 243-252 | RAG summary | YES — partial marker (boolean only) |
| 9 | rag_queries log card (privacy export panel) | `templates/compliance/privacy_dashboard.html` | 253-265 | Raw log summary | YES — partial marker (boolean only) |
| — | AI Disclosure modal | `templates/onboarding/ai_disclosure.html` | 1-84 | Informational text about AI | N/A — not AI output |
| — | Epilogue placeholder | `templates/epilogue/placeholder.html` | 1-75 | Placeholder | N/A — no AI rendering yet (TD-011) |

**Total in scope:** 9 spots (5 new on tab5, 4 existing partial markers to upgrade on privacy_dashboard).

### V2 — C.4 export already aggregates `ai_outputs`, with provenance gaps

`apps.compliance.services.gather_user_export(user)` (services.py:535) produces a JSON-serialisable dict whose `ai_outputs` key is filled by `_ai_outputs_to_dict` (services.py:415) and contains six sub-keys:

| Key | Source | Provenance fields today |
|---|---|---|
| `rtm_positions` | `ReflectionTension` model rows | none (just module_code + labels + position) |
| `dtp_narratives` | `UserModuleProgress.reflection_dtp` TextField | none (just module_code + text) |
| `rag_feedback` | `UserModuleProgress.reflection_rag_feedback` TextField | none (just module_code + text) |
| `peer_synthesis` | `UserModuleProgress.reflection_peer_synthesis` TextField | none (just module_code + text) |
| `rag_queries` | raw-SQL `rag_queries` table | partial: `generation_tokens`, `processing_time_ms`, `api_cost_eur`, `created_at` — **missing model name** |
| `ai_disputes` | `AIOutputDispute` model rows | n/a (about AI outputs, not AI outputs themselves) |

**Critical implication:** the HTML markers cannot meaningfully *mirror* the export, because the export itself currently has no model name and no per-row generated_at on 4 of the 5 AI-output keys. C.3 introduces a provenance layer that both the export AND the HTML layer consume; the export's top-level `export_version` bumps from `'1'` to `'2'` to signal the new sub-keys (CP-8).

### V3 — `rag_queries` raw-SQL pattern

- `rag_queries` is a raw-SQL table outside the Django ORM.
- `rag_query_system.py:445` writes via raw `INSERT INTO rag_queries (...)` SQL. Per CP-3, the newly-created row's primary key is obtained exclusively via `RETURNING id` on the same statement; `SELECT lastval()` is rejected as race-prone under concurrent inserts.
- The Gemini model identifier `gemini-2.5-flash` is hard-coded in 9 call sites in `rag_query_system.py`; never persisted per row.
- `_rag_queries_to_list` (services.py:483) reads via savepoint-protected `cursor.execute`; on `ProgrammingError` returns an empty list. This savepoint pattern is preserved by any read/write path C.3 adds.
- `anonymize_user` (services.py:687) uses raw `UPDATE rag_queries SET reflection_text=...` — unchanged by C.3.

**Marking-strategy decision (CP-1, audit-backed):** introduce a new Django-managed `AIArtefactProvenance` model with a polymorphic reference `(artefact_kind, artefact_pk)`. No schema change to `rag_queries`. Backfill writes `model_name='gemini-2.5-flash'` constant for all historical rows — defensible because the audit (§3.1 of `audit_rag_queries_provenance_20260512.md`) confirmed (a) no model-standardisation transition in git history and (b) zero rows in the fallback-path proxy bucket.

---

## 3. Design decisions

All five 🛑 decisions approved on defaults with the corrections noted inline. Concrete D6-D12 also stand with the corrections.

### D1 — Provenance storage location ✅ APPROVED (D1a)

New `apps.compliance.models.AIArtefactProvenance` Django model with fields:
  - `artefact_kind`: CharField, choices = `{'rtm_position', 'dtp_narrative', 'rag_feedback', 'peer_synthesis', 'rag_query', 'epilogue_portrait'}` (last value forward-compat for TD-011)
  - `artefact_pk`: PositiveIntegerField (polymorphic — not a Django FK, accepts `rag_queries.id` too)
  - `user`: FK to `auth_user`, `on_delete=CASCADE` (anonymisation clears these rows alongside the user)
  - `module`: FK to `Module`, nullable (rag_queries may have NULL module_id)
  - `model_name`: CharField max 64 (`'gemini-2.5-flash'` in v1)
  - `generated_at`: DateTimeField with tz
  - `prompt_hash`: CharField max 64, nullable (sha256; nullable so retroactive backfill works — CP-7)
  - `created_at`: DateTimeField auto_now_add
  - `unique_together = ('artefact_kind', 'artefact_pk')` — enables `get_or_create` idempotency for the backfill (CP-7)

### D2 — Template tag signature ✅ APPROVED (D2a)

`{% ai_provenance for=provenance_record %}` — view prefetches `AIArtefactProvenance` and passes the record into the template context; the tag renders the visible attribution line and does not perform additional DB lookups. Caller responsibility model keeps prefetching predictable and N+1 patterns visible at the view layer.

### D3 — JSON-LD schema and scope ✅ APPROVED (D3a)

schema.org `CreativeWork` with `creator` set to a `SoftwareApplication` extension (`gemini-2.5-flash`). Page-level `<script type="application/ld+json">` block injected on `tab5_reflection.html` and `privacy_dashboard.html` only. AI Disclosure modal and Epilogue placeholder out of scope.

### D4 — Coverage scope for the pilot ✅ APPROVED (D4a)

All 9 spots from V1. 5 new on `tab5_reflection.html`, 4 upgrades on `privacy_dashboard.html`. AI Disclosure (not AI output) and Epilogue placeholder (no AI rendering yet — TD-011 will carry its own provenance via the same `AIArtefactProvenance` model when the full feature lands; D12 below).

### D5 — Retroactive backfill ✅ APPROVED (D5a + CP-7 strengthening)

Management command `apps/compliance/management/commands/backfill_ai_provenance.py`. CP-7 strengthening:
  - **Never overwrites** existing provenance rows.
  - Implementation uses `AIArtefactProvenance.objects.get_or_create(artefact_kind=..., artefact_pk=..., defaults={...})`. The `defaults={}` carries `model_name`, `generated_at`, `prompt_hash=None`, `user`, `module`. The "get" branch is silent — no warning, no error.
  - Safe under mixed forward/retroactive scenarios: if commit 2a write-path hooks have already created provenance for an artefact, the backfill skips it.
  - `--dry-run` default + `--commit` flag + typed YES confirmation (CP-11 pattern).
  - Output prints (in dry-run): expected new rows per kind, expected get-branch hits (already-existing provenance), and a flag for any `rag_queries` rows with `generation_tokens IS NULL OR = 0` (CP-1 follow-up: early-warning for fallback-path activity).

Backfill model_name strategy per audit: `'gemini-2.5-flash'` constant, justified in `audit_rag_queries_provenance_20260512.md` §4. Orphan `rag_queries` rows (74 found in audit §3.3) are skipped because their `user_id` does not reference a valid `auth_user`.

### D6 — HTML attribute names + value format

Adopt these per-element data-attrs across all 9 spots:

```html
<div data-ai-generated="true"
     data-ai-model="gemini-2.5-flash"
     data-ai-generated-at="2026-05-12T14:23:00Z"
     data-ai-artefact-kind="rag_feedback"
     data-ai-artefact-id="42">
```

  - `data-ai-generated="true"` — boolean compatibility marker (preserves the 4 existing privacy_dashboard markers as a subset)
  - `data-ai-model` — short, free-form model identifier
  - `data-ai-generated-at` — ISO 8601 with tz (UTC)
  - `data-ai-artefact-kind` — enum value matching D1's choices
  - `data-ai-artefact-id` — back-reference to the artefact PK (kept even though the dispute deep-link is dropped — CP-6 — because the id is also useful for log-correlation and future deep-linking)

### D7 — Template tag file location

New file `apps/compliance/templatetags/ai_provenance.py`. Tests in `apps/compliance/tests.py`.

### D8 — Export mirror + version bump (CP-8)

`apps.compliance.services._ai_outputs_to_dict` is amended so each entry of each list grows a `provenance` sub-dict:

```python
{
    'module_code': 'M3',
    'text': '...',
    'provenance': {
        'model_name': 'gemini-2.5-flash',
        'generated_at': '2026-04-12T11:42:00+00:00',
        'prompt_hash': None,
        'artefact_kind': 'rag_feedback',
        'artefact_id': 42,
    },
}
```

  - **`EXPORT_VERSION` is bumped from `'1'` to `'2'`** in `apps/compliance/services.py:292`. The top-level `export_version` key in `gather_user_export` reflects this.
  - **Backward-compatibility note for downstream parsers:** export v2 strictly adds the `provenance` sub-dict to entries that already exist in v1. No keys are renamed, removed, or repositioned. A downstream parser written against v1 will see additional keys it does not consume; it should treat unknown keys as opaque. The version key change is the load-bearing signal to identify v2 in any future schema regression test.
  - **CP-5 fresh-user invariant preserved:** users with zero AI artefacts still have `ai_outputs.<kind>` as an empty list (no `provenance` keys to misread).

### D9 — rag_queries provenance under D1a (CP-3 correction)

The `rag_queries` raw-SQL table is **not** schema-changed.

  - **Write path:** in `rag_query_system.py`, the existing `INSERT INTO rag_queries (...) VALUES (...)` SQL is amended with a `RETURNING id` clause. The returned id is captured by the cursor and passed to `record_ai_provenance(artefact_kind='rag_query', artefact_pk=<returned_id>, ...)`. **`SELECT lastval()` is explicitly rejected (CP-3)** because it is race-prone under concurrent inserts to the same connection/session — `RETURNING id` is the only acceptable id-extraction path.
  - **Read path:** `_rag_queries_to_list` annotates each row with the provenance sub-dict by joining on a prefetched provenance set keyed by `('rag_query', rag_queries.id)`.
  - **Anonymisation:** the `AIArtefactProvenance.user` FK cascade-deletes when `auth_user` is anonymised. The anonymisation function's existing raw `UPDATE rag_queries` block is unchanged.

### D10 — Article 50(1) human-readable transparency — REVISED to Option C (2026-05-12)

**Original plan (rejected during commit 2a implementation):** add a new standalone visible attribution line ("Generated by gemini-2.5-flash on …") under each AI output via `{% blocktrans %}`.

**Pre-implementation discovery:** `templates/modules/tabs/tab5_reflection.html` already carries **XAI disclosure panels** under three of the four AI outputs (live RAG feedback ~L290-314, completed-state RAG ~L730-756, DTP ~L617-640) plus inline EU AI Act Limited Risk mentions for RTM (~L396-400, L893-898, L1458). Each panel includes Model identifier (Gemini 2.5 Flash), Input description, Logic description, Intent, and an explicit "EU AI Act — Limited Risk: No automated decisions are made" sentence. Adjacent to each panel is a HITL dispute UX ("Was this feedback relevant?" + 👍/partial buttons calling `submitDispute(feature_type, rating)`). The existing panels already satisfy Article 50(1) human-readable transparency. A new standalone attribution paragraph would duplicate the same information weaker.

**Option C (APPROVED 2026-05-12):**

  - **C.1** — Drop the standalone `Generated by X on Y` attribution paragraph. The existing XAI panels carry the model identification.
  - **C.2** — Add **one new line** inside each existing XAI panel's `grid grid-cols-[auto_1fr]`: `Generated at: 2026-05-12 14:23` (per-artefact timestamp surfaced from the new `AIArtefactProvenance` row). The current panels say "Model: Gemini 2.5 Flash" generically; adding the per-artefact timestamp makes the panel artefact-specific and closes a real gap (the panel today is identical across all artefacts; provenance metadata is artefact-unique).
  - **C.3** — Add a **new XAI panel for peer synthesis** at the parity position (currently L463-483 + L819-827 render peer synthesis but lack a "How this synthesis was generated" panel). The new panel matches the RAG/DTP pattern (Model / Input / Logic / Intent / Limited Risk / Generated at). This closes a pre-existing inconsistency in the disclosure UX.
  - **C.4 (CP-10 reinterpretation)** — opacity decision: the new "Generated at" row stays in the parent panel's existing scale (`text-xs`) and inherits its grid styling (label uses `text-base-content/60`, value default). No standalone opacity override needed — the original CP-10 concern (the `/50` line being hard to read) does not apply because the line is now inside a panel whose label color is already `/60`.

The template tag from D2 (`{% ai_provenance %}`) is repurposed: instead of emitting a standalone paragraph, it emits **one row in the XAI panel's grid**:

```django
{% ai_provenance for=provenance %}
{# emits: #}
<span class="font-semibold text-base-content/60">Generated at</span>
<span>{{ provenance.generated_at|date:"d M Y H:i" }}</span>
```

The single translatable string concern (CP-5) is reduced to a one-word label ("Generated at"). The full datetime is locale-formatted by Django's `|date` filter; there is no concatenated phrase to translate.

### D11 — Dispute UX affinity (CP-6 follow-up)

Dispute link is **not** emitted by `{% ai_provenance %}`. The existing HITL dispute buttons under each AI output (RAG, RTM, DTP) already provide module-level + feature-type dispute UX (C.2.3-era code). Per CP-6, per-artefact-instance dispute deep-links would require URL pattern change + view change + likely `AIOutputDispute` schema extension; out of scope for Article 50(2) machine-readability. Logged as `TD-018 — Per-artefact-instance AI dispute deep-links` (commit 1 of this piece opened the entry), deferred to post-pilot.

**Peer synthesis dispute UX gap:** peer synthesis currently has no `submitDispute('peer', …)` button in `tab5_reflection.html`. This is a pre-existing UX gap (independent of C.3). Recommended scope for **commit 2b** alongside the new peer XAI panel: add a `submitDispute('peer', …)` button row for parity. If the gap requires `AIOutputDispute` schema extension (to add a 'peer' feature_type), surface as a 🛑 decision in commit 2b's implementation kickoff.

### D12 — Forward-compat with future Epilogue (TD-011)

When TD-011 lands, the same `AIArtefactProvenance` model accepts new `artefact_kind` enum values (`'epilogue_portrait'`, `'epilogue_dialogue_turn'`) — additive change, no migration. The `{% ai_provenance %}` tag works unchanged.

---

## 4. File-by-file impact

| File | Action | Est. LOC | Commit |
|---|---|---|---|
| `apps/compliance/models.py` | New `AIArtefactProvenance` model (D1a) | +45 | 1 |
| `apps/compliance/migrations/0005_aiartefactprovenance.py` (NEW) | Migration for the new model | +30 | 1 |
| `apps/compliance/services.py` (storage helper) | New `record_ai_provenance(...)` write helper | +40 | 1 |
| `apps/compliance/services.py` (export mirror) | Amend `_ai_outputs_to_dict` + bump EXPORT_VERSION → '2' | +50 | 2b |
| `apps/compliance/templatetags/ai_provenance.py` (NEW) | `{% ai_provenance %}` tag | +50 | 3 |
| `apps/compliance/management/commands/backfill_ai_provenance.py` (NEW) | Backfill command + `--dry-run` + typed YES + get_or_create | +140 | 1 |
| `apps/compliance/tests.py` | +30 tests (split across commits) | +280 | 1 + 2a + 2b + 3 |
| `apps/compliance/admin.py` | Register `AIArtefactProvenance` for staff inspection | +10 | 1 |
| `rag_query_system.py` | Amend each `INSERT INTO rag_queries` with `RETURNING id`; capture id; call `record_ai_provenance` inside the same `transaction.atomic` block (CP-9). | +30 | 2a |
| `apps/modules/views.py` (save hooks) | After each save path writing reflection_dtp / reflection_rag_feedback / reflection_peer_synthesis / ReflectionTension, call `record_ai_provenance` inside the same `transaction.atomic` block (CP-9). | +35 | 2a |
| `apps/modules/views.py` (prefetch) | Prefetch `AIArtefactProvenance` in tab5 + privacy_dashboard render views | +20 | 2b |
| `apps/modules/tests.py` | +5 tests verifying provenance row is written on each save path | +60 | 2a |
| `templates/modules/tabs/tab5_reflection.html` | Add `{% load ai_provenance %}` + wrap 5 AI output cards with the data-attrs + visible attribution line | +50 | 2b |
| `templates/compliance/privacy_dashboard.html` | Upgrade the 4 partial markers with the full attribute set + visible attribution line | +25 | 2b |
| `templates/modules/tabs/tab5_reflection.html` (JSON-LD) | Page-level JSON-LD script block | +25 | 3 |
| `templates/compliance/privacy_dashboard.html` (JSON-LD) | Page-level JSON-LD script block | +20 | 3 |
| `proodos_files/TECH_DEBT_LOG.md` | New TD-017 entry (Active) + new TD-018 entry (Active); TD-017 → RESOLVED in commit 3 | +55 | 1 + 3 |
| `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` | Changelog entry per commit | +20 | 1 + 2a + 2b + 3 |
| `PROODOS_UNIFIED_ROADMAP.md` | Move C.3 from §3.C.7 carry-over to §3.C.3 DONE; update §2.8 | +15 | 3 |
| `proodos_files/SESSION_LOG_PHASE_C_C3_20260512.md` (NEW) | Session log | +130 | 3 |
| `proodos_files/audit_rag_queries_provenance_20260512.md` (NEW) | Pre-flight audit (already drafted) | — | 1 |
| `proodos_files/C3_DESIGN_PROPOSAL_AI_MARKERS.md` (THIS FILE) | Design proposal (already drafted) | — | 1 |

**Total estimate: ~1010 LOC** (code + tests + docs).

---

## 5. Commit split — 4 commits, bisectable (CP-4)

### Commit 1 — Provenance storage layer + retroactive backfill

  - New `AIArtefactProvenance` model + migration `0005_aiartefactprovenance` (D1a)
  - `apps.compliance.services.record_ai_provenance(...)` helper. **Helper does NOT open its own `transaction.atomic` block** — it assumes the caller has wrapped its save + provenance call inside one (CP-9 — see commits 2a). The helper does use `get_or_create` for safe idempotency (CP-7).
  - `apps.compliance.management.commands.backfill_ai_provenance` (D5a + CP-7) — dry-run default + `--commit` flag + typed-YES confirmation + `get_or_create` idempotency + fallback-path warning output
  - Admin registration
  - TD-017 entry written into `proodos_files/TECH_DEBT_LOG.md` (state: Active)
  - TD-018 entry written into same file (Per-artefact-instance AI dispute deep-links, deferred to post-pilot, CP-6)
  - Audit doc (`audit_rag_queries_provenance_20260512.md`) referenced from TD-017
  - **Tests:** 9
    - model __str__ + unique constraint
    - `record_ai_provenance` idempotency via `get_or_create` (calling twice with same `(kind, pk)` is silent no-op)
    - `record_ai_provenance` with `module=None` (rag_queries case)
    - anonymisation cascade clears provenance rows when `auth_user` is anonymised
    - backfill dry-run prints expected count, writes nothing
    - backfill commit creates rows for all existing AI-output sources (using a seeded fixture)
    - backfill is idempotent (rerun creates zero new rows)
    - backfill respects fresh-test-DB rag_queries-missing case (ProgrammingError → empty)
    - admin page renders for staff
  - **Pre-apply backup:** `pre_migration_backup_phaseC_C3_20260512.sql`

### Commit 2a — Write paths (forward-write hooks)

  - `rag_query_system.py`: amend each `INSERT INTO rag_queries` with `RETURNING id`; capture; call `record_ai_provenance` inside the same `transaction.atomic` block as the INSERT (CP-9). `SELECT lastval()` NOT used (CP-3).
  - `apps/modules/views.py`: after each save path writing reflection_dtp / reflection_rag_feedback / reflection_peer_synthesis (3 paths) AND after `ReflectionTension.save()` (1 path), call `record_ai_provenance`. The save() + record_ai_provenance() pair must execute inside one `transaction.atomic()` block (CP-9). If `record_ai_provenance` raises, the save() also rolls back — no AI artefact without provenance.
  - **No template changes in this commit** (read paths follow in 2b).
  - **Tests:** 6
    - provenance row written when `mark_tab_complete` saves rag feedback
    - provenance row written when DTP narrative is generated
    - provenance row written when peer synthesis is computed
    - provenance row written when an RTM tension is saved
    - provenance row written when `INSERT INTO rag_queries` runs (via fixture exercising the RAG path)
    - **CP-9 invariant:** monkey-patched `record_ai_provenance` raising → rolled-back save (no AI artefact row created, no provenance row created)

### Commit 2b — Read paths (export mirror + HTML attrs)

  - `apps.compliance.services._ai_outputs_to_dict`: amend each entry of each list with the `provenance` sub-dict (D8)
  - `apps.compliance.services.EXPORT_VERSION`: bump `'1'` → `'2'` (CP-8)
  - `apps/modules/views.py`: prefetch `AIArtefactProvenance` for tab5 view + privacy_dashboard view (avoid N+1)
  - `templates/modules/tabs/tab5_reflection.html`: data-attrs + visible attribution line on the 5 AI output sections (V1 sites 1-5). `{% load ai_provenance %}` reserved for commit 3 (no tag use yet — direct attribute rendering).
  - `templates/compliance/privacy_dashboard.html`: upgrade 4 partial markers (V1 sites 6-9) to full attribute set + visible attribution. `text-base-content/70` opacity (CP-10).
  - **Tests:** 8
    - export includes `provenance` sub-dict on each ai_outputs entry
    - export_version is `'2'`
    - fresh-user export has empty arrays + no provenance keys (CP-5 invariant preserved)
    - tab5 reflection HTML contains all 5 expected data-ai-* attrs on each AI output card
    - privacy dashboard HTML contains the 4 upgraded markers with model + timestamp
    - visible attribution line renders model + timestamp; opacity class is `/70` not `/50` (CP-10)
    - anonymised user's HTML render shows empty AI sections (no attrs leaked from cleared rows)
    - N+1 regression guard: rendering tab5 with 5 AI artefacts hits the DB ≤2 times for provenance

### Commit 3 — Template tag + JSON-LD + Article 50 final wiring + roadmap update

  - `apps/compliance/templatetags/ai_provenance.py`: `{% ai_provenance for=record %}` tag (D2a + D7). The tag emits the visible attribution line using a single `{% blocktrans %}` with placeholders (CP-5) — Greek translation can re-order placeholders without code change.
  - The visible attribution line written in commit 2b is **replaced** by the template tag (the strings are identical; the tag is a refactor target). This keeps commit 2b shippable on its own even if commit 3 slips.
  - Page-level JSON-LD `<script type="application/ld+json">` block on tab5_reflection.html and privacy_dashboard.html, schema.org `CreativeWork` + `SoftwareApplication` creator extension (D3a). View context provides `ai_provenance_jsonld` (list of provenance records); template serialises via Django's `json_script` template tag or via a small filter.
  - `proodos_files/TECH_DEBT_LOG.md`: TD-017 → RESOLVED with cross-reference to commits 1 + 2a + 2b + 3.
  - `PROODOS_UNIFIED_ROADMAP.md`: move C.3 from §3.C.7 to §3.C.3 with DONE badge; §2.8 commit table updated.
  - `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md`: final changelog entry.
  - `proodos_files/SESSION_LOG_PHASE_C_C3_20260512.md`: session log covering all four commits.
  - **Tests:** 7
    - template tag renders model + timestamp via `{% blocktrans %}` correctly
    - template tag handles `provenance=None` gracefully (no crash, attribution line absent)
    - page-level JSON-LD block on tab5 is valid JSON-LD (`json.loads` + schema-type asserts)
    - page-level JSON-LD block on privacy_dashboard is valid JSON-LD
    - JSON-LD lists every AI artefact on the page (cross-reference with provenance prefetch)
    - tag respects USE_I18N=True with translated blocktrans output (snapshot under `LANGUAGE_CODE='el'`)
    - tab5 reflection rendered HTML contains the JSON-LD block exactly once (no duplication if multiple AI cards present)

**Total tests across the four commits: 31** — within the 25-35 range (commit 1 implemented 10 instead of 9 after the storage-model contract was split into three discrete tests).

---

## 6. Test plan summary

| Commit | Tests | Coverage emphasis |
|---|---|---|
| Commit 1 | 10 | Storage model + `get_or_create` idempotency + backfill + admin + cascade |
| Commit 2a | 6 | Write paths + CP-9 transaction-atomic invariant |
| Commit 2b | 8 | Export mirror + version bump + HTML attrs + CP-5 fresh-user + N+1 + opacity |
| Commit 3 | 7 | Template tag + JSON-LD validity + i18n blocktrans + JSON-LD uniqueness |
| **Total** | **31** | All AI rendering sites + export mirror + machine-readable layer |

After commit 3 the full Phase C suite target is **183 + 31 = 214**.

---

## 7. Sign-off ledger

Approved 2026-05-12 by John, with the 10 CP corrections summarised below:

  - ✅ **D1** — separate `AIArtefactProvenance` model
  - ✅ **D2** — `for=record` template tag form
  - ✅ **D3** — schema.org/CreativeWork JSON-LD on tab5 + privacy_dashboard
  - ✅ **D4** — full 9-spot coverage
  - ✅ **D5** — idempotent management command + new deployment order
  - ✅ Commit split into 4 (1 + 2a + 2b + 3) — CP-4
  - ✅ Test target 30 (within 25-35) — CP-4
  - ✅ CP-1 — pre-flight audit drafted (`audit_rag_queries_provenance_20260512.md`)
  - ✅ CP-2 — corrected deployment order: C.3 deploy → backfill → CP-11 wipe → pilot
  - ✅ CP-3 — `RETURNING id` only, never `SELECT lastval()`
  - ✅ CP-5 — single translatable string via `{% blocktrans %}` with placeholders; "Dispute this AI output" replaced by no-link line
  - ✅ CP-6 — dispute deep-link dropped; new TD-018 opened in commit 1
  - ✅ CP-7 — `get_or_create` idempotency on backfill, silent get-branch
  - ✅ CP-8 — `EXPORT_VERSION` bumped `'1'` → `'2'` with backward-compat note
  - ✅ CP-9 — `record_ai_provenance` calls inside `transaction.atomic` blocks at all call sites
  - ✅ CP-10 — opacity `text-base-content/70` (not `/50`)

---

## 8. Rollback considerations

  - **Commit 1** is additive only (new model, new table, new command, new TD entries). Rollback = revert + `python manage.py migrate compliance 0004` + restore from `pre_migration_backup_phaseC_C3_20260512.sql`.
  - **Commit 2a** adds write hooks. Rollback = revert; new save paths revert to writing AI artefacts without provenance. No data loss; the backfill in commit 1 still works to retroactively cover whatever was written under the reverted state.
  - **Commit 2b** is template + service mutations (export schema change). Rollback = revert + EXPORT_VERSION reverts to `'1'`. Downstream parsers fall back to v1; CP-5 invariant preserved.
  - **Commit 3** is pure additive HTML + template tag + doc updates. Rollback = revert.

No commit changes the public URL surface, removes columns, or alters existing read/write paths beyond addition.

---

## 9. Cross-references and forward links

  - **TD-017** — opened Active in commit 1, closed RESOLVED in commit 3
  - **TD-018 (new — CP-6)** — Per-artefact-instance AI dispute deep-links, deferred to post-pilot
  - **TD-011** (full Epilogue) — D12 ensures forward-compat; `'epilogue_portrait'` enum value reserved
  - **TD-015** (data export PDF) — will inherit provenance for free via the export mirror (D8)
  - **C.4 commit 2 partial markers** — superseded in commit 2b (upgraded to full attribute set + attribution line + opacity fix), not preserved
  - **`audit_rag_queries_provenance_20260512.md`** — load-bearing for D5 + R2 closure
  - **C.6 pre-pilot checklist** — adds new step `python manage.py backfill_ai_provenance --commit` **before** CP-11 wipe (CP-2 correction).

**Corrected deployment order (CP-2):**

  1. C.3 deploy (commits 1 + 2a + 2b + 3 land on main; migration 0005 applied)
  2. `python manage.py backfill_ai_provenance --commit` (typed YES; idempotent so safe to rerun)
  3. CP-11 wipe (`scripts/cp11_wipe_test_users.py --commit`)
  4. Pilot recruitment

Rationale: CP-11 cascade-clears non-staff `rag_queries` rows (19 rows per audit §3.3). Running backfill AFTER CP-11 would leave only staff + orphan rows in scope, but more importantly would leave the *interim* window — between C.3 deploy and CP-11 — with inconsistent provenance during staff testing of the export. Running backfill BEFORE CP-11 ensures the export is internally consistent at all times.

---

## 10. Open questions and risks

  - **Q1:** Does the IHU IRB protocol require explicit mention of the per-element AI provenance markers, or is the AI Impact Assessment notice (C.1) sufficient? Pre-IRB decision, low risk; safest path is to mention "machine-readable provenance markers per Article 50(2)" in the V2 IRB-revised copy when CP 7 + CP 10 land.
  - **Q3:** `prompt_hash` is captured forward (commit 2a) and None retroactively (commit 1 backfill). Is the value of prompt-hash audit worth the per-call hash compute? **Decision:** yes — privacy-respecting (sha256 of input text + retrieval context), useful for dispute audit ("the AI saw exactly this prompt"). Kept nullable so backfill works.
  - **~~R2 (was: 1.5-flash fallback rows)~~** — **RESOLVED** by `audit_rag_queries_provenance_20260512.md`. Single-constant backfill is safe.
  - **R1 (N+1):** prefetch + commit 2b's N+1 test guards this.
  - **R3 (template tag failure mode):** must render gracefully if a view forgets to prefetch. Commit 3 test #2 covers this.
  - **R4 (new):** `RETURNING id` syntax availability — PostgreSQL has supported `INSERT … RETURNING` since 8.2 (long-since standard); the project is on Postgres ≥ 14 per CLAUDE.md. No risk.

---

*End of design proposal. Approved. Commit 1 implementation begins next.*
