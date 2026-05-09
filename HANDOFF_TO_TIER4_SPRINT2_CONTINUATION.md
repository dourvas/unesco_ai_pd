# Handoff to Tier 4 Sprint 2 Continuation Session

**Date:** 4 May 2026 (afternoon)
**Predecessor session:** Tier 4 Sprint 2 Cycles 2.1 — Patches A1-A4 closed + A5/A6 Step 1 done + A6 Step 2A audit done
**Coverage stamp:** **151 / 170 STRONG (~88.8%)** · 19 / 170 PARTIAL · 0 ABSENT
**Next pending action:** **A6 Step 2B brief from John** (M8 reinforcement patch with Ouyang et al. 2022 InstructGPT citation) — Step 2A audit verdict is SUITABLE, paper details + 4 verbatim citable claims + 3 risk flags ready in `/tmp/ouyang_paper_audit.md`

---

## TL;DR for the new session

Phase A Tier 4 Sprint 2 is in progress. **6 of 10 Cluster A patches are done** (A1, A2, A3, A4, A5, A6 Step 1); **A6 Step 2B is pending wording draft**; **A7-A10 + A11 (Cluster B) are not yet started**.

The previous session executed:
- Sprint 1 (3 audit corrections — CG2.1.3, CG4.3.4, CG5.3.4)
- A1 v1 → ROLLBACK → A1 v2 (M4 Tool 3 conversion)
- A2 (M9 dual citation, Aravantinos + Viberg)
- A3 (M11 audit-only sync, CG1.3.2)
- A4 (M7 Scenario 8, AI-amplified bullying)
- A5 (M3 audit-only sync, LO3.1.1)
- A6 Step 1 (M8 interim sync, CG3.2.2 with "pending Step 2" marker)
- A6 Step 2A (Ouyang InstructGPT paper audit — SUITABLE verdict)

**Where John left off:** asked for this handoff because the previous session was getting context-heavy. The next brief from John should be either:
1. **A6 Step 2B** (wording draft + Gemini check + apply reinforcement patch in M8 Part 1)
2. **A7 audit brief** (LO4.3.6 administrative AI streamlining in M15) — if John defers A6 Step 2B
3. **A8 audit brief** (CG5.2.3 data analytics forward-link in M10)
4. Other — John drives priority

The new session should **NOT pre-emptively start anything**. Wait for John's brief.

---

## Current state (verified end of session)

### Database (PostgreSQL 5432, dbname=unesco_ai_teacher_pd, user=postgres, password=Django123!)

```
modules_modulecontent rows                            1258  (Tier 3 baseline preserved)
modules_modulecontent_backup_phase_a_tier4_may2026    1258  (sprint backup, created start of A1)
documents (RAG corpus docs)                             66  (60 baseline + Tier 1 atomic doc 76 + Tier 4 atomic docs 94/95/96 + Tier 1 atomic docs 82/83 + 1 other)
document_chunks (RAG corpus chunks)                    943  (940 baseline + 3 Tier 4 atomic chunks)
```

Use psql binary: `/c/Program\ Files/PostgreSQL/18/bin/psql.exe` on Windows git-bash. Postgres server runs in WSL/Debian (per earlier verification).

### Backup table

`modules_modulecontent_backup_phase_a_tier4_may2026` — sprint-scoped backup created at start of A1, captures **post-Tier-1 / pre-Tier-4 state**. Used for both apply baselines AND A1 v1 → v2 rollback. Reusable for A6 Step 2B + A7-A11. **Do NOT re-create.**

### Patches applied to `modules_modulecontent` (Tier 4 only — Tier 1-3 patches inherited intact)

| Row id | Module | Patch marker | Date | Length delta | Status |
|---:|---|---|---|---:|---|
| 633 | M4 | `SCHOLARLY_RESEARCH_CITATION_PATCH_V2:OPEN/CLOSE` (A1 v2 Tool 3) | 4 May 2026 | +3,819 | ✅ closed |
| 723 | M9 | `AI_EMPIRICAL_RESEARCH_CITATION_PATCH:OPEN/CLOSE` (A2 dual citation Aravantinos + Viberg) | 4 May 2026 | +3,081 | ✅ closed |
| (none) | M11 | A3 — audit-only sync, no DB change | 4 May 2026 | 0 | ✅ closed |
| 98 | M7 | `AI_BULLYING_SCENARIO_PATCH:OPEN/CLOSE` (A4 Scenario 8) | 4 May 2026 | +3,025 | ✅ closed |
| (none) | M3 | A5 — audit-only sync, no DB change | 4 May 2026 | 0 | ✅ closed |
| (none) | M8 | A6 Step 1 — audit-only sync, no DB change | 4 May 2026 | 0 | ✅ Step 1 closed |
| 447 | M8 | A6 Step 2B — pending wording draft | — | TBD | ⏳ pending |

A1 v1 was applied then rolled back same-day (factual error in locked wording — see Lessons Learned below).

### RAG atomic chunks added (Tier 4 only)

| doc_id | chunk_id | Title | Date |
|---:|---:|---|---|
| ~~93~~ | ~~1621~~ | M4 Scholarly Research Citation Patch (A1 v1) — DELETED | 4 May 2026 (deleted same day after rollback) |
| 94 | 1622 | M4: Tool 3 Evidence Check Patch (Phase A Tier 4 A1 v2) | 4 May 2026 |
| 95 | 1623 | M9: AI-Empirical Research Base Patch (Phase A Tier 4 A2) | 4 May 2026 |
| 96 | 1624 | M7: AI-Amplified Bullying Scenario Patch (Phase A Tier 4 A4) | 4 May 2026 |

If John approves A6 Step 2B, the next atomic chunk will be doc_id=97, chunk_id=1625 (M8 reinforcement).

---

## Sprint 2 coverage trajectory

| Stage | STRONG | % | Notes |
|---|---:|---:|---|
| Post-Tier-3 closure (predecessor) | 142/170 | ~83.5% | baseline |
| + Sprint 1 (CG2.1.3, CG4.3.4, CG5.3.4 audit corrections) | 145/170 | ~85.3% | pure docs sync |
| + A1 v2 (M4 Tool 3, CG4.1.2) | 146/170 | ~85.9% | Tool-native conversion (after A1 v1 rollback) |
| + A2 (M9 dual citation, CG4.2.2) | 147/170 | ~86.5% | reinforcement |
| + A3 (M11 sync, CG1.3.2) | 148/170 | ~87.1% | audit-only sync |
| + A4 (M7 Scenario 8, CG2.2.2 + LO2.2.4) | 149/170 | ~87.6% | standalone scenario |
| + A5 (M3 sync, LO3.1.1) | 150/170 | ~88.2% | audit-only sync |
| **+ A6 Step 1 (M8 interim sync, CG3.2.2)** | **151/170** | **~88.8%** | **interim — Step 2B pending** |
| + A6 Step 2B (M8 reinforcement) | 151/170 | ~88.8% | same count, stronger defendability under strict UNESCO reading |
| + A7-A10 hypothetical | 155/170 | ~91.2% | projected if all 4 land cleanly |
| + A11 Cluster B hypothetical | 156/170 | ~91.8% | projected ceiling for current sprint scope |

---

## Pending Cluster A patches (after A6 Step 2B)

| # | Indicator | Module | Effort | Pattern hypothesis |
|---|---|---|---|---|
| A7 | LO4.3.6 — administrative AI streamlining | M15 | ~1h | Likely audit-only or small text reinforcement |
| A8 | CG5.2.3 — data analytics forward-link | M10 | ~1h | Likely small forward-reference patch (DTP/RTM exists in M15) |
| A9 | LO5.3.1 — ethical-rule iteration cross-link | M15 | ~1h | Likely cross-reference to M12 ethical-rule iteration |
| A10 | (was A7 in original gap analysis — CG4.2.2 — DONE as A2) | M9 | done | ✅ already done as A2 |
| A11 | CG3.3.2 — open-source critique (Cluster B medium) | M13 | ~2h | Likely medium reinforcement |

**Note:** the original gap analysis listed ~10 Cluster A patches. After A2 closed CG4.2.2 (which was originally listed twice — as a citation patch in M9 and as part of A2's reinforcement), the actual remaining count is 4 Cluster A + 1 Cluster B = **5 patches** to fully exhaust Sprint 2.

---

## How A6 Step 2B should be executed (when John sends the brief)

The Ouyang audit (`/tmp/ouyang_paper_audit.md`) is complete. Step 2B will be a small reinforcement patch in M8. Expected approach:

### Anchor

M8 row 447 has these existing patches in Part 1:
- Lines 54-60: `M8_CROSS_REF_M3_PATCH` (Tier 3, routes to M3 Part 2 for AI techniques)
- Lines 425-450: `M8_ETHICS_BY_DESIGN_PATCH` (Tier 3, end of Part 4)

Recommended anchor for Step 2B: **AFTER the M8_CROSS_REF_M3_PATCH closing tag, BEFORE the next paragraph** in Part 1. Anchor = `<!-- /M8_CROSS_REF_M3_PATCH -->` or the first paragraph after it (`<p class="mb-4">There is a gap between understanding a framework and using it fluently...`).

Pre-flight discovery should verify uniqueness via SQL. Same pattern as A1/A2.

### Patch marker

Recommended: `LLM_TRAINING_RESEARCH_CITATION_PATCH:OPEN/CLOSE` (suffix convention from A1 v2 / A2)

### Wording skeleton (NOT locked — John will lock after Gemini check)

Small (~50-100 word) inline citation block. Same chrome family as T1.4/T1.5/A2 (italic `<p>` + `text-sm italic text-base-content/70` + reference paragraph `text-xs text-base-content/60`).

Body should:
- Cite Ouyang et al. (2022) "Training language models to follow instructions with human feedback" NeurIPS 2022
- Name the **3-stage RLHF methodology** at conceptual level (SFT → reward modelling → RL via PPO)
- Use the headline finding "Making language models bigger does not inherently make them better at following a user's intent" — strongest hook for M8's prompt-engineering stance
- Preserve the 3 risk flags from Step 2A audit:
  1. NOT generalise InstructGPT findings to all LLMs
  2. NOT overstate truthfulness/toxicity improvements (mitigations not eliminations)
  3. NOT overshoot "1.3B beats 175B" outside labeler-evaluation context

### RAG ingest

Same `ingest_phaseA_tier4_atomic.py` helper. Atomic chunk for the new doc. Expected doc_id=97, chunk_id=1625.

### RAG verification queries (suggested)

- Q1: "How are LLMs like ChatGPT trained?" — should match A6 chunk
- Q2: "What is RLHF and why does it matter for prompt engineering?" — should match A6 chunk

### Browser test

M8 Part 1 — verify the new citation block lands AFTER the m8_cross_ref_m3 patch and BEFORE the rest of Part 1 body. Check that the Ouyang authors are cited correctly (20-author OpenAI team — reference can use "Ouyang et al." abbreviation).

---

## Reusable infrastructure (battle-tested across A1-A4)

### `ingest_phaseA_tier4_atomic.py`

Project-root helper at `C:\Users\dourv\unesco_ai_pd\ingest_phaseA_tier4_atomic.py`. Modeled on Tier 3 canonical pattern (`ingest_phaseA_tier3_step6_m8.py`). CLI:

```bash
cd /c/Users/dourv/unesco_ai_pd
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe ingest_phaseA_tier4_atomic.py --config /tmp/patch_aN_config.json --dry-run
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe ingest_phaseA_tier4_atomic.py --config /tmp/patch_aN_config.json
```

Config JSON fields (required): `module_code`, `doc_title`, `chunk_text`, `patch_id`, `tier`, `indicator`. Optional: `sprint`, `topic_short`.

The helper inserts ONE new `documents` row + ONE atomic `document_chunks` row. Idempotent on `doc_title` collision. **NO existing M{N} docs touched.** Used 3 times (A1 v2, A2, A4) — proven clean.

### Apply script template

Each patch has its own apply script at `C:\Users\dourv\AppData\Local\Temp\patch_aN_apply.py` (or v2 equivalent). Standard structure:
- ANCHOR string (with uniqueness verified pre-flight)
- NEW_BLOCK string (locked wording)
- 12-13 post-state checks: anchor uniqueness + idempotency + length band + marker count + open marker + close marker + heading present + UNESCO/citation phrases present + ghost checks for prior patches' factual errors
- `--dry-run` / `--commit` modes (CLI mutually exclusive group)
- Updates `metadata.patches[]` JSONB array via `jsonb_set` + `COALESCE` pattern

Template file to clone: `/tmp/patch_a4_apply.py` (most recent, has all 13 post-state checks including ghost checks for A1 + A2 + A4 numbering).

### Post-state ghost checks (running list, as of A4)

Every Tier 4+ apply should defensively check:
- `LIKE '%upper secondary contexts producing the strongest gains%'` — A1 v1 ghost (factual error)
- `LIKE '%Kizilcec, Wise%'` — A2 v1 ghost (wrong author surnames)
- `LIKE '%Scenario 4 — The Anonymous Class Group Chat%'` — A4 v1 ghost (wrong scenario number)

Add the next ghost as A6 Step 2B applies (and any subsequent factual errors caught).

---

## Master documentation files (proodos_files/)

These are the source-of-truth docs. Update each Tier 4 patch (apply OR audit-only sync):

| File | Purpose |
|---|---|
| `proodos_files/CONTENT_GAPS_LOG.md` | Per-module per-indicator history. ~1700+ lines. Trajectory table near end. |
| `proodos_files/CONTENT_VALIDATION_MATRIX.md` | Master audit table per module. Each module has indicator-level closure status. |
| `proodos_files/PHASE_A_REMAINING_GAPS_POST_TIER3.md` | Tier 4 scoping inventory. Each row = 1 indicator with status + feasibility. Update row to ✅ Done after closure. |
| `proodos_files/platform_changes_log.md` | Per-patch detailed log. ~2000+ lines. Append new section per patch. |

### Master docs update protocol — what goes where, per patch type

**This is the operational checklist. Apply rigorously per patch.**

#### Pattern A — Audit-only sync (no DB/RAG, e.g. A3, A5, Sprint 1)

Update 3 files (NOT platform_changes_log — that's for actual platform changes):

1. **`CONTENT_VALIDATION_MATRIX.md`** — locate `### M{N} — ` heading. Update the `**Indicators with partial/no coverage:**` line by removing the indicator. If a closed-line already exists (e.g., from another Tier 4 patch), append the indicator to it; otherwise add a new line:
   ```
   **Indicators closed via [Tier 1 + Tier 4 audit / Day 3 + Tier 4 audit / Tier 1 + Tier 4 audit + distributed cumulative]:** {INDICATOR} ({brief evidence summary with sub-clause count + key sources + RAG sims if available})
   ```

2. **`PHASE_A_REMAINING_GAPS_POST_TIER3.md`** — locate the row by indicator. Replace the entire row with strikethrough + closure:
   ```
   | {row#} | ~~**{INDICATOR}**~~ — {original gap description} | {anchor module + cumulative modules} | ✅ **RESOLVED Tier 4 Sprint 2 A{N} ({date}).** Promoted PARTIAL → 📋 STRONG (DISTRIBUTED) via audit-table sync. {Per-sub-clause evidence summary}. {Pattern note: Sprint 1 / A3 sync residue, not substantive gap.} {Note on stale "1h easy patch" estimate if applicable.} | ✅ Done |
   ```

3. **`CONTENT_GAPS_LOG.md`** — TWO updates:
   - **(a)** Locate `### M{N}` heading + the relevant `#### Κενό #X` section. ADD a Tier 4 audit-correction note AFTER the existing closure status line:
     ```
     **Tier 4 A{N} audit-correction note ({date}):** Independent paper-grounded audit (`/tmp/{audit_filename}.md`) {decomposition finding if more sub-clauses surfaced} {per-sub-clause matrix if relevant} {pattern note}. Master matrix + PHASE_A_REMAINING_GAPS_POST_TIER3.md updated to reflect closure.
     ```
   - **(b)** Locate the **trajectory table at the END of the file** (search for "Phase A Tier 3 closure" — table is ~50 lines below first match). Append 2 new rows: one for the patch row, one for the cumulative-after row.
     ```
     | **Phase A Tier 4 — Sprint 2 Patch A{N} (M{N} {indicator} audit-only sync)** | **+1 STRONG** | **~{X.X}%** | {brief description + pattern note + cumulative count statement} |
     | **Post-A{N} cumulative** | **{NEW_TOTAL} / 170** | **~{X.X}%** | {patches done so far + remaining + lessons reinforced} |
     ```

#### Pattern B — Apply patch (DB + RAG + browser test, e.g. A1 v2, A2, A4)

Update **all 4 files**:

1. **`CONTENT_VALIDATION_MATRIX.md`** — same as Pattern A (move indicator from "partial" to "closed via"), but the closed-line text mentions the patch markers + RAG sims:
   ```
   **Indicators closed via Tier 1 + Tier 4 reinforcement:** {INDICATOR} (Tier 1 patch X + Tier 4 A{N} {patch_marker_id} ..., RAG sim {Q1} #1 on {query type}, {complementary coverage description})
   ```

2. **`PHASE_A_REMAINING_GAPS_POST_TIER3.md`** — same as Pattern A (strikethrough + ✅ Done), but evidence list includes patch marker + RAG sim + length delta + pre-flight blocker note if applicable:
   ```
   | {row#} | ~~**{INDICATOR}**~~ — {desc} | M{N} (anchor) {+ distributed if relevant} | ✅ **RESOLVED Tier 4 Sprint 2 A{N} ({date}).** {Patch marker} added to row {ID}. Length delta +{N} chars. RAG verified Q1 sim {X.XXXX} (#1 unfiltered + mod-scoped). {Pre-flight blocker caught — describe if applicable}. | ✅ Done |
   ```

3. **`CONTENT_GAPS_LOG.md`** — TWO updates:
   - **(a)** M{N} Κενό #X section: add `**🎯 Tier 4 A{N} reinforcement ({date}):**` paragraph with patch markers + length delta + RAG sims + cross-module evidence + pre-flight blocker note if applicable.
   - **(b)** Trajectory table: append the patch row + cumulative row (same format as Pattern A but with patch markers + RAG sim numbers).

4. **`platform_changes_log.md`** — APPEND a new section (look for the most recent `## 🎯 Phase A Tier 4 — Patch AN` and insert the new section after it). Full per-patch entry format:
   ```markdown
   ---

   ## 🎯 Phase A Tier 4 — Patch A{N} ({date})

   ### Sprint 2 Cycle 2.1 — {indicator + module + topic}

   {1-2 paragraph framing of what the patch does + which sub-clauses it closes}

   ### Patch A{N} — {patch title}

   - **Status:** 🎯 **Verified** ({date}) — DB COMMITTED + RAG verified; browser test {pending/passed}
   - **Module:** M{N} ({Aspect}, {Acquire/Deepen/Create}), DB id={module_id}, content row id={row_id}
   - **Section:** {placement description}
   - **Implementation:** UPDATE row id={row_id} με REPLACE() σε anchor `{anchor}` (uniqueness verified)
   - **Length change:** {pre} → {post} chars (+{delta})
   - **Content type:** {description of HTML structure / chrome family}
   - **Word count:** ~{N} words
   - **UNESCO indicators newly addressed:** {list with sub-clauses}
   - **Key citations used (factually verified before apply):** {list with verbatim quotes if applicable}
   - **Distinctive features:** {bullets}
   - **Patch markers:** `{:OPEN}` ... `{:CLOSE}`
   - **Backup:** {table name} — {rollback target description}
   - **DB apply:** ✅ Applied {date}. All pre-flight checks PASS + N post-state checks PASS — including {key checks}. metadata.patches[] grew {old_count} → {new_count}.
   - **RAG ingest:** ✅ Atomic chunk via `ingest_phaseA_tier4_atomic.py`. New doc_id={X}, chunk_id={Y}, chunk_text_length={Z}. Total corpus: {old} → {new}. Existing M{N} docs byte-identical.
   - **RAG verification ({number} queries):** {per-query results with sims, ranks, margins, verdict}
   - **Browser tested:** {⏸️ pending / ✅ Passed (John, {date} — {what was confirmed})}
   - **Patch closure:** {✅ Patch A{N} CLOSED. {indicator} status change}.

   ### Pre-flight blocker caught (if applicable)

   {Describe the locked-wording issue + how it was reconciled.}

   ### Tier 4 Sprint 2 — coverage trajectory (revised post-A{N})

   | Stage | STRONG | % | Notes |
   |---|---:|---:|---|
   | Post-A{N-1} cumulative | {old}/170 | ~{X.X}% | ... |
   | **Post-A{N} cumulative** | **{new}/170** | **~{X.X}%** | ... |

   ### Lessons learned from A{N} (if applicable)

   - ...
   ```

   **Browser-test-passed update**: when John confirms browser test, edit the section's "Browser tested:" line to `✅ Passed (John, {date} — {confirmed elements})` AND add `Patch closure:` line right after with `✅ Patch A{N} CLOSED. {status change summary}.` Also update the apply report header `Status:` line.

#### Pattern C — Interim sync (Step 1 of split, e.g. A2 Step 1, A6 Step 1)

Same as Pattern A (3 file updates, no platform_changes_log entry yet), BUT use **explicit "pending Step 2" suffix**:

1. **`CONTENT_VALIDATION_MATRIX.md`** — closed-line text uses `closed via Day 3 + Tier 3 + Tier 4 audit (Step 1) + Tier 4 reinforcement (Step 2 pending):` and includes `pending Tier 4 Step 2B reinforcement patch with {citation type} — {paper-level audit status}` at end.

2. **`PHASE_A_REMAINING_GAPS_POST_TIER3.md`** — row is **NOT** marked ✅ Done yet. Use `⏳ Step 2 in progress` with description of what Step 2B will add.

3. **`CONTENT_GAPS_LOG.md`** — M{N} Κενό #X section: add `**Tier 4 A{N} reinforcement note ({date}):**` paragraph explaining why interim sync isn't sufficient under strict reading + what Step 2B will add. Also add Step 1 + Step 2 trajectory rows (Step 2 = "0 net" but stronger defendability).

#### Pattern D — Reinforcement patch (Step 2B of split, after audit)

Same as Pattern B (full apply), BUT in `platform_changes_log.md` reference the predecessor Step 2A audit + verdict in the framing paragraph. After Step 2B applies, also remove "pending Step 2" suffixes from MATRIX + CONTENT_GAPS_LOG entries (preserve the audit history).

#### Pattern E — Rollback (e.g. A1 v1 → ROLLBACK → A1 v2)

Update `platform_changes_log.md` only initially (mark v1 ROLLED BACK with reason). After v2 applies, full Pattern B for v2 in same section, with `supersedes: v1_patch_id` + `rollback_reason: ...` in metadata.patches[]. Master matrix + remaining-gaps + gaps log get the FINAL v2 entry; v1 isn't separately recorded except in platform_changes_log.

#### metadata.patches[] convention (DB-side)

Apply scripts append to `modules_modulecontent.metadata.patches[]` JSONB array using:
```sql
UPDATE modules_modulecontent
SET metadata = jsonb_set(
  COALESCE(metadata, '{}'::jsonb),
  '{patches}',
  COALESCE(metadata->'patches', '[]'::jsonb) || %s::jsonb
)
WHERE id = {row_id};
```

Standard fields: `id`, `tier`, `sprint`, `date`, `indicator`, `module`, `part`, `type`, `references`, `dimensions_addressed`. Add `supersedes` + `rollback_reason` if revising a prior patch.

### Convention for "interim" closures (when Step 2 reinforcement is pending)

Per A2 + A6 Step 1 precedent: use **explicit "pending Step 2" suffix** in the matrix line and `⏳ Step 2 in progress` in the PHASE_A_REMAINING row. Remove the suffix once Step 2B commits.

Example MATRIX line for CG3.2.2 (current state):
```
**Indicators closed via Day 3 + Tier 3 + Tier 4 audit (Step 1) + Tier 4 reinforcement (Step 2 pending):** CG3.2.2 (... pending Tier 4 Step 2B reinforcement patch with peer-reviewed LLM training methodology citation — Ouyang et al. 2022 InstructGPT/RLHF paper-level audit in progress)
```

---

## Audit-first methodology (PROODOS principle, 5 cycles deep)

**Every Tier 4+ patch citing empirical research requires independent paper-grounded audit BEFORE wording lock.** LLM-only wording checks (Gemini) approve factual errors that paper audit catches.

### Errors caught (4 of 6 patches in Tier 4)

1. **A1 v1**: factual generalisation — "upper secondary contexts producing the strongest gains" — Létourneau review actually finds OPPOSITE pattern (middle school > high school in corpus framing). Caught by paper fetch + per-claim audit.
2. **A2 v1**: author misattribution — "Viberg, Kizilcec, Wise, Gašević and Khosravi" — actual paper has 4 authors (Viberg, Poquet, Kovanovic, Khosravi). Caught by Crossref + OpenAlex + paper title page cross-check.
3. **A4 v1**: scenario numbering inconsistency — locked wording said "Scenario 4" but M7 Part 4 has 5/6/7 (Scenarios 1-4 are in M2). Caught by structural audit of existing Part 4 layout.
4. **A6 verdict disagreement** (with chat-side hypothesis): chat-side predicted Verdict A audit-only; my audit found Verdict C (CG3.2.2 sub-clause 2 "research-based learning" is genuinely thin under strict UNESCO reading; same A2 pattern). John approved Path 1 (split treatment) over Path 2 (unified A3-style sync).

### Pre-flight check matrix (now standard)

For each Tier 4 patch:
1. ✅ UNESCO indicator verbatim — quote vs PDF
2. ✅ Locked-wording author/factual cross-verification (Crossref + OpenAlex + paper title page if research citation)
3. ✅ Structure-grounded check (numbering, sequence, position relative to existing items)
4. ✅ Anchor uniqueness in target row (uniqueness=1 required)
5. ✅ Idempotency check (marker absent table-wide)
6. ✅ Length check (current + projected)
7. ✅ Existing module RAG document inventory (atomic-chunk pattern is mandatory if module has > 2 docs)
8. ✅ Backup verification
9. ✅ RAG baseline (1-2 queries, capture sims for post-apply comparison)

---

## Critical schema corrections (carry forward)

### Brief vs reality

The original Tier 4 brief authoring (and subsequent per-patch briefs) sometimes use wrong column/table names. **Pre-flight should always verify and adapt:**

| Brief says | Reality | Notes |
|---|---|---|
| `main_content` (column) | **`content_data`** | Column name in `modules_modulecontent`. ALWAYS use `content_data`. |
| `modules_ragdocument` (table) | **`documents`** | RAG documents table. Brief A1 v2 / A2 etc. use the wrong name. |
| `modules_ragchunk` (table) | **`document_chunks`** | RAG chunks table. Same issue. |

These are documented now in apply scripts. Successor session will inherit the corrected scripts.

### `/tmp/` resolution on Windows

Windows git-bash `/tmp/` resolves to `C:\Users\dourv\AppData\Local\Temp\`. Tools that don't handle bash paths (Read/Write/Edit) need the Windows path.

### Environment

- Working directory: `C:\Users\dourv\unesco_ai_pd` (project root)
- Worktree may be active (e.g., `.claude\worktrees\inspiring-shtern-a18471`) — current session was running in a worktree. New session will likely start fresh.
- Python venv: `./venv/Scripts/python.exe`
- Always prepend `PYTHONIOENCODING=utf-8` for emoji/UTF-8 console output on Windows
- DB credentials: postgres / Django123!
- xhtml2pdf 0.2.17 active; weasyprint broken on Windows (GTK runtime)
- Django 6.0.1 — uses `condition=` not `check=` in `CheckConstraint`

---

## File locations of key artifacts

### Master docs (committed)

```
C:\Users\dourv\unesco_ai_pd\proodos_files\
├── CONTENT_GAPS_LOG.md            (master gaps log, updated after each patch)
├── CONTENT_VALIDATION_MATRIX.md   (master audit table, per-module)
├── PHASE_A_REMAINING_GAPS_POST_TIER3.md (Tier 4 scoping)
├── platform_changes_log.md        (master platform log, per-patch detail)
└── M*_MATRIX_ENTRY.md            (per-module deep-dive — historical, already merged)
```

### Project-root scripts (committed)

```
C:\Users\dourv\unesco_ai_pd\
├── ingest_phaseA_tier4_atomic.py  (Tier 4 atomic-chunk RAG helper, reusable)
├── ingest_phaseA_tier3_step6_m8.py (Tier 3 canonical reference, do not modify)
└── ingest_module_rag.py           (generic re-ingest, AVOID for Tier 4 — would over-clean)
```

### Pre-flight reports + apply reports (Temp, /tmp equivalent)

```
C:\Users\dourv\AppData\Local\Temp\
├── unesco_framework.txt                  (UNESCO PDF extracted via pdftotext, line-numbered)
├── m{N}_main.html or m{N}_main_postrollback.html  (per-module dumps for inspection)
├── patch_a1_preflight_report.md          (A1 v1)
├── patch_a1_apply_report.md              (A1 v1 — superseded)
├── patch_a1_v2_apply_report.md           (A1 v2 — final)
├── patch_a1_tool3_review.md              (A1 Tool 3 review during conversion)
├── patch_a2_preflight_report.md          (A2)
├── patch_a2_apply_report.md              (A2)
├── patch_a4_preflight_report.md          (A4)
├── patch_a4_apply_report.md              (A4)
├── cg422_independent_audit.md            (A2 audit)
├── m9_structure_audit.md                 (A2 placement audit)
├── m9_2nd_citation_audit.md              (A2 Viberg paper audit)
├── aravantinos_paper_audit.md            (A2 Aravantinos paper audit)
├── cg132_independent_audit.md            (A3 audit)
├── lo311_cg322_independent_audit.md      (A5+A6 audit — combined)
├── ouyang_paper_audit.md                 (A6 Step 2A audit — SUITABLE verdict)
├── sprint1_independent_audit.md          (Sprint 1 audit)
├── patch_a*_apply.py                     (apply scripts per patch)
├── patch_a*_baseline.py                  (RAG baseline scripts per patch)
├── patch_a*_config.json                  (RAG ingest configs per patch)
└── patch_a*_v2_*.py / .json              (v2 variants for A1)
```

The successor session will need to read several of these as context. Most relevant for A6 Step 2B continuation:
- `lo311_cg322_independent_audit.md` (the disagreement audit)
- `ouyang_paper_audit.md` (the paper audit with verdict + citable claims)

### Predecessor handoff doc

```
C:\Users\dourv\unesco_ai_pd\HANDOFF_TO_TIER4_SESSION.md   (original Phase A Tier 3 → Tier 4 handoff)
C:\Users\dourv\unesco_ai_pd\HANDOFF_TO_TIER3_SESSION.md   (historical)
C:\Users\dourv\unesco_ai_pd\HANDOFF_TO_TIER4_SPRINT2_CONTINUATION.md (this file)
```

---

## How John works (preferences observed across 6 cycles)

- **Greek + English mixed** — John writes briefs in English, talks in chat in Greek+English. Replies should match (ok to mix).
- **Stop-and-report cadence is non-negotiable** — every meaningful step needs a status report + browser-test request before proceeding. Saved many bugs across Tier 1+2+3+4.
- **John explicitly approves anchor selection + chrome divergences + factual reconciliations** — the audit-first methodology surfaces these for John's call. Do NOT auto-decide.
- **Standard closure phrase**: "Έγινε και είναι οκ" / "ok το browser test" / "Browser test complete. Everrything is ok" → mark patch closed, update apply report + platform_changes_log to reflect ✅ Browser tested + Patch closed.
- **Brief authoring style**: terse, structured, locked-wording-driven. John sometimes makes minor mistakes in briefs (factual generalisations, structural conflations, schema name mismatches). The audit-first check pattern catches these.
- **John defers to my audit verdicts when they're well-justified** — A6 disagreement (chat-side Verdict A vs my Verdict C) was reconciled by John picking Path 1 (split treatment). Audit-first respect is established.

---

## Patterns catalog (5 distinct closure patterns surfaced in Tier 4)

| Pattern | Example | Indicator | Notes |
|---|---|---|---|
| Tool-native conversion (citation footer → operational tool) | A1 v2 | CG4.1.2 | A1 v1 was citation footer → fit issues + factual error → rolled back → re-applied as Tool 3 with GO/STOP gates |
| Dual-citation reinforcement (continuation 1/2-2/2) | A2 | CG4.2.2 | 2 references in one block, complementary coverage of multiple sub-clauses |
| Audit-only sync (distributed STRONG, sub-clause decomposition) | A3, A5, Sprint 1 indicators | CG1.3.2, LO3.1.1, CG2.1.3, CG4.3.4, CG5.3.4 | Pure docs work, no DB/RAG. Most common pattern (~50% of Tier 4 closures) |
| Standalone narrative scenario (red gravity stripe) | A4 | CG2.2.2, LO2.2.4 | Distinct visual chrome to signal serious dilemma |
| Interim sync + reinforcement (Step 1 docs + Step 2 patch) | A2, A6 | CG4.2.2, CG3.2.2 | When sub-clause-2 (research-based) needs AI-empirical citation that distributed coverage doesn't provide |

The successor session should pattern-match each new indicator before drafting.

---

## A6 Step 2B specifics — what's ready, what's pending

### Ready (in `/tmp/ouyang_paper_audit.md`)

- Verified bibliographic details (NeurIPS 2022 Main Conference Track, peer-reviewed, 20 authors OpenAI, arXiv 2203.02155)
- 4 verbatim citable claims with risk flags
- 3 factual-overclaim risks identified pre-emptively
- Pedagogical translation guidance (3-stage RLHF as teacher-accessible loop)
- Recommended chrome (T1.4/T1.5/A2 family — italic `<p>` + text-sm + opacity)

### Pending (when John sends Step 2B brief)

- Locked wording draft (~50-100 words)
- Anchor selection in M8 Part 1 (recommended: AFTER m8_cross_ref_m3 close marker)
- Patch marker name (recommended: `LLM_TRAINING_RESEARCH_CITATION_PATCH:OPEN/CLOSE`)
- Apply script (clone from `/tmp/patch_a4_apply.py` template)
- RAG config + baseline queries (suggested: "How are LLMs like ChatGPT trained?" + "What is RLHF...?")
- Browser test request

The Step 2B brief should follow the pattern of A2's Step 2 (apply brief after audit verdict). John may iterate on wording with Gemini before locking.

---

## Decision points open for John (recorded for transparency)

1. **A6 Step 2B timing** — execute now or defer to after A7-A10? Audit verdict is ready, so Step 2B is ready when John is.
2. **A7 prioritisation** — LO4.3.6 (M15) might be audit-only; could be quick. Or could be substantive if M15 doesn't have administrative-AI content.
3. **Audit-first frequency** — pattern is established (5 cycles). Should every patch get full pre-flight + paper audit, or fast-track simple sync patches? My recommendation: keep full audit-first for any patch with empirical citation; light pre-flight (anchor + idempotency only) for pure audit-only syncs.
4. **Sprint 2 closure target** — currently 6/10 done = 60%. If A6 Step 2B + A7 + A8 + A9 + A10 + A11 all land, sprint hits ~91.8%. John may want to defer the 6 Cluster B patches to Sprint 3.

---

## Recommended workflow for the new session

1. **DO NOT auto-execute anything.** Wait for John's brief.
2. **Read this handoff first.** Then `/tmp/lo311_cg322_independent_audit.md` and `/tmp/ouyang_paper_audit.md` if Step 2B is the next brief.
3. **For every Tier 4+ patch citing empirical research:** apply paper-grounded audit BEFORE wording lock. The 3-of-6 error rate has held — methodology is paying off.
4. **For audit-only syncs:** light pre-flight (anchor + idempotency check), fast docs sync, no DB/RAG. Same pattern as A3, A5, Sprint 1.
5. **Anchor uniqueness, length band, ghost checks** are the standard apply-script defenses. Keep them.
6. **Stop-and-report at every checkpoint.** Don't batch closures.
7. **Update master docs after every patch.** The 4 master docs (CONTENT_GAPS_LOG, CONTENT_VALIDATION_MATRIX, PHASE_A_REMAINING_GAPS_POST_TIER3, platform_changes_log) need consistent updates per patch.
8. **Browser test is mandatory before patch closure.** John executes; new session waits for confirmation.
9. **When unsure, ρώτα στο chat.** John drives strategy and reconciles audit disagreements.

---

## Pattern-recognition cheat-sheet for incoming patches

For each new indicator brief:

```
IF brief identifies < N sub-clauses where UNESCO PDF actually has > N:
   → Sub-clause undercount risk (A3, A5, A6 examples)
   → Decompose UNESCO verbatim before forming verdict

IF locked wording cites a specific paper / specific author list / specific number:
   → Factual-error risk (A1 v1, A2 v1, A4 v1 examples)
   → Verify against paper PDF / Crossref / structural reality
   → 3-of-6 patches had locked-wording errors caught this way

IF target indicator is at Deepen level and existing closure is at Acquire level:
   → Lenient-Tier-1 risk (A2 example for CG4.2.2; A6 example for CG3.2.2)
   → Verdict C STRONG-WITH-RESERVATION likely; small reinforcement worth doing

IF target module has > 2 RAG documents:
   → Atomic-chunk pattern is MANDATORY (A1 lesson, M4 had 3 docs; M9 had 5; M7 had 4)
   → Generic ingest_module_rag.py would over-clean
   → Use ingest_phaseA_tier4_atomic.py helper

IF chat-side prediction is "Verdict A audit-only":
   → Skepticism warranted if the target indicator wording is more demanding than the chat-side framing recognises
   → A6 is the example: chat predicted A, my audit found C. John picked split treatment.
```

---

*Created: 4 May 2026, end of Tier 4 Sprint 2 Cycle 2.1 (after A1-A6 Step 1 + A6 Step 2A).*
*Predecessor: HANDOFF_TO_TIER4_SESSION.md (Phase A Tier 3 closure → Tier 4 launch).*
*Successor: TBD — written by next session at end of Sprint 2 (after A6 Step 2B + A7-A11 if pursued).*
*Trust judgement per Tier 1+2+3+4 patterns. When in doubt, audit first.*
