# Handoff to Tier 4 Sprint 2 — Cluster B Session

**Date:** 6 May 2026 (end of Sprint 2 Cluster A)
**Predecessor:** Sprint 2 Cluster A — A1–A9 all closed (sequential session executed audit-first methodology, autonomous-wording mode, chrome retro-fix, parallel audits)
**Coverage stamp:** **154 / 170 STRONG (~90.6%)** · 16 / 170 PARTIAL · 0 ABSENT
**Next phase:** Cluster B — 6 medium-effort indicators (2-6h each), all in M5/M9/M10/M13/M14 territory

---

## TL;DR for the new session

**Cluster A is complete** (9 indicators closed: A1–A9 + Sprint 1 audit corrections). **Cluster B has 6 pending indicators** — all medium-effort (~14h subtotal), require substantive new content (not audit-only sync).

**The new session should NOT auto-execute anything.** Wait for John's brief on which Cluster B indicator(s) to tackle first.

**Key methodology to inherit:**
- Audit-first ALWAYS (brief errors caught in 8-of-11 Tier 4 briefs)
- Sub-clause decomposition mandatory
- Autonomous-wording mode viable (3 PoCs: A6/A7/A8) with John's in-flight review
- Chrome Rule 1 (border-l-4 reserved for subject boxes only) — all Cluster A patches use plain `card bg-base-200 p-4 my-4`
- Pattern A/B/D protocols (master docs update guidelines)
- M16 PROODOS Epilogue treated as existing (roadmap module; A8 forward-references it)

---

## Cluster B — 6 pending indicators

Per `proodos_files/PHASE_A_REMAINING_GAPS_POST_TIER3.md` Cluster B section + pattern observations from Cluster A:

| # | Indicator | Module | Effort estimate | Initial pattern hypothesis (verify via audit) |
|---|---|---|---|---|
| **B1** | **CG3.3.2** — open-source vs commercial AI deep critique | M13 | ~2h | Day 3 + Tier 1 (Patch T1.9) added 7-row comparison table; needs depth analysis (advantages/limitations/risks of self-hosted models for school IT). Possible A4 family (standalone subsection) |
| **B2** | **CG4.2.1** — SEL portion (M9 cross-link to M14) | M9 (anchor) + M14 | ~2h | Videos already defendable platform gap; SEL needs ~2h cross-module patch (M9 ↔ M14 referencing). M14 partial-resolved SEL via SDT (Connection dimension). Possible A7 family (cross-aspect/cross-level cross-link) |
| **B3** | **CG4.2.3** — LMS review (M9) | M9 | ~2h | Tier 1 institutional patch added partial. Possible A4 family — M9 Part 5 add subsection on LMS-embedded AI tools (Moodle AI plugins, Google Classroom Gemini) |
| **B4** | **LO4.2.3** — high-stakes assessment (M9) | M9 | ~2h | Formative covered. High-stakes exams not addressed. Possible A4 family — M9 add brief subsection on AI in high-stakes assessment (PISA, university entrance) + cross-link to M6 4 Rights |
| **B5** | **CG5.1.4** — AI-manipulated cocoons (M5) | M5 | ~3h | Content-recommendation biases, AI-manipulated cocoons. Possible A4 family or A2/A6 reinforcement (peer-reviewed research on filter bubbles in education) |
| **B6** | **CG5.2.2 / 5.2.4** — emerging AI PD tools + algorithmic risks (M10) | M10 | ~3h consolidated | UNESCO ζητά ρητά. CG5.2.2 = emerging tools for PD; CG5.2.4 = ethical risks AI platforms (algorithmic). Possible combined patch: M10 add subsection με emerging tools (Khanmigo for educators, MagicSchool, AI tutors) + algorithmic risks (filter bubbles in CoP feeds). Could combine με B5 σε single Tier 4 cluster on AI-manipulated platforms. |

**Subtotal:** ~14 hours · expected +6 STRONG → **160 / 170 = ~94.1%** ceiling

**After Cluster B:** 10 PARTIAL indicators remaining (defendable design choices + Cluster C platform-feature dependencies). Phase A would close at ~94%.

---

## Critical lessons from Sprint 2 Cluster A (9 patches)

### Audit-first methodology — paid off 8-of-11 times

PHASE_A briefs are unreliable. Errors caught at audit/pre-flight in this session alone:

| Patch | Brief errors caught |
|---|---|
| A1 v1 | factual generalisation in Letourneau review wording |
| A2 v1 | Viberg paper author misattribution (5-author claim → actual 4) |
| A4 v1 | scenario numbering wrong (Scenario 4 → 8; M2 has 1-4, M7 has 5-7) |
| A6 brief | CG3.2.2 vs LO3.2.2 conflation |
| A7 brief | M15 DB id wrong (18 → 20) + M11 "Workforce Restructurer" label nonexistent + M15 Action Research location wrong (Part 5 → 3) |
| A8 brief | "M10 has data analytics" + "M13 has ML practice workshop" — **both false** |
| A9 brief | "M2/M7/M12 ethics framework" — only M12 substantively contributes |

**PHASE_A "1h easy text patch" estimates wrong 9-of-9 indicators audited.** Always undercount scope or misidentify modules.

**Implication:** Treat brief as informational guide, not prescriptive specification. Stage 0 pre-flight verification is non-negotiable.

### Sub-clause decomposition is mandatory

Every multi-clause indicator audited surfaced sub-clause undercount in PHASE_A description:
- A6 CG3.2.2: 4 sub-clauses (PHASE_A treated as 1)
- A7 LO4.3.6: 3 sub-clauses (PHASE_A treated as 1)
- A8 CG5.2.3: 5 sub-clauses
- A9 LO5.3.1: 6 sub-clauses (best-distributed-coverage indicator)

**Process:** decompose UNESCO verbatim text from `/tmp/unesco_framework.txt` BEFORE forming verdict. Per-sub-clause matrix per audit dimension 4.

### Autonomous-wording mode validated 3x

Established for indicators where audit guardrails are sharp enough to constrain wording space:

| Patch | Mode | Outcome |
|---|---|---|
| A6 St2B | First autonomous-wording (Gemini check waived) | Clean apply, no errors |
| A7 | Locked v1 from John in apply brief; autonomous from audit | Clean apply, no errors |
| A8 | Autonomous + **first in-flight wording revision** (UNESCO compliance verbiage trimmed mid-apply per John's critique) | Clean apply; RAG improved post-trim (Q2 rank #2 → #1) |

**Pattern:** practitioner-first wording outperforms compliance-language wording on RAG retrieval. Cut UNESCO indicator codes from body text; keep verbatim quotes only when they directly serve the practitioner's understanding.

### Chrome decision tree (Rule 1)

After Cluster A retro-fix batches (Batch 1: 5 sites; Batch 2: 12 sites; Bonus M7: 1 site = **18 patch wrappers cleaned**):

**border-l-4 reserved for subject boxes only.** All patch wrappers use **plain `card bg-base-200 p-4 my-4`** (no border-l-4).

Remaining border-l-4 in main_content rows after Cluster A retro-fix:
- M2: 4 native (bg-green-50/yellow-50/blue-50 inside scenarios)
- M7: 5 native (bg-white/yellow-50 inside scenarios)
- M8: 1 unidentified (`card bg-base-200 border-l-4 border-info p-5 my-6`)
- M12: 1 unidentified
- M15: 1 PATCH (DISABILITIES_FOCUS_PATCH `<aside>` border-accent — Tier 2, lower priority)

**Cluster B patches MUST use plain `card bg-base-200 p-4 my-4` chrome.** Do NOT introduce new border-l-4 stripes.

### Length-band bounds are derivative checks

Brief estimates are conservative. When all substantive content checks pass and length variance is within ±10%, **band relaxation is reasonable** (preserves "don't modify locked v1 wording" hard guardrail).

A7 precedent: brief band [2,800, 3,500] → actual delta +2,594 → relaxed band [2,400, 3,500] → COMMIT clean.

### Q-marginal-fail acceptance pattern

When canonical-query rank-1 is strong (or rank-1 mod-scoped), marginal sim shortfalls on tangential phrasing are accepted:

| Patch | Marginal query | Result | Decision |
|---|---|---|---|
| A6 St2B Q3 | "How are LLMs trained?" rank #1 mod-scoped, sim 0.6830 | accepted | Path 1 |
| A7 Q2 | "Gradebook comments?" rank #1 mod-scoped, sim 0.6935 | accepted | Path 1 |
| A8 Q1 | rank #2 unfiltered+mod-scoped, sim 0.6917 (UNESCO PDF dominates) | accepted | Path 1 |
| A8 Q2 | rank #1 unfiltered+mod-scoped, sim 0.6821 | accepted | Path 1 |

**Rationale:** when domination is by UNESCO PDF chunks (legitimate corpus content) or by lexically-similar but topically-orthogonal module content, marginal shortfalls are structural, not patch-quality issues.

---

## Pattern catalog (refined post-Cluster A)

| Pattern family | Members | Closure shape |
|---|---|---|
| **A3/A5/A9** — audit-only sync | Sprint 1 (3) + A3 + A5 + A9 = 6 patches | Pure docs work (3 master files: MATRIX + PHASE_A + CONTENT_GAPS_LOG); no DB / RAG / code changes; ~30-45 min effort |
| **A1 v2** — operational tool redesign | A1 v2 (Tool 3) | Major content restructure with operational gates (GO/STOP); ~3-4h effort |
| **A2/A6** — Tier 1 LENIENT → reinforcement citation | A2 (CG4.2.2 dual citation) + A6 (CG3.2.2 RLHF) | Peer-reviewed research citation block reinforcing Tier 1 lenient closure; requires upstream paper-level audit; ~2-3h effort |
| **A4** — standalone scenario/subsection | A4 Scenario 8 + A7 admin pragmatism subsection | Concrete content for genuine PARTIAL sub-clause; standalone narrative card or subsection; ~2-3h effort |
| **A7/A8** — cross-aspect/cross-level forward-reference | A7 (Aspect 4 → 5 standalone subsection); A8 (Aspect 5 Deepen → Create forward-ref); A9 (Aspect 5 → M12 Aspect 2 cross-aspect via Designer's Cycle) | Navigational forward-reference card; reduced scope vs A4 family; assumes cross-level/cross-aspect substantive coverage exists; ~1.5-2h effort |
| **Pattern E (rollback)** | A1 v1 → A1 v2 (one instance) | Backup-restore; full Pattern B for v2; v1 metadata preserved with `supersedes` + `rollback_reason` |

### Cluster B pattern hypotheses (verify each via audit)

- **B1 CG3.3.2** (open-source critique M13): A4 family OR A2 family (depending on whether Tier 1 is lenient)
- **B2 CG4.2.1** (SEL M9↔M14): likely A7 family (cross-module forward-reference; M14 has SDT/Connection content)
- **B3 CG4.2.3** (LMS review M9): A4 family (standalone subsection)
- **B4 LO4.2.3** (high-stakes assessment M9): A4 family
- **B5 CG5.1.4** (AI-manipulated cocoons M5): A4 family OR A2/A6 reinforcement
- **B6 CG5.2.2/5.2.4** (emerging AI PD tools + algorithmic risks M10): A4 family combined patch

---

## Critical schema corrections (carry forward)

### Brief-vs-reality column/table names

| Brief says | Reality | Notes |
|---|---|---|
| `main_content` (column) | **`content_data`** | Column name in `modules_modulecontent`. ALWAYS use `content_data`. |
| `modules_ragdocument` (table) | **`documents`** | RAG documents table. Brief A1 v2 / A2 etc. used the wrong name. |
| `modules_ragchunk` (table) | **`document_chunks`** | RAG chunks table. Same issue. |

### Module ID + main_content row ID inventory (verified Sprint 2)

| Module | id | main_content row | Title |
|---|---:|---:|---|
| M1 | 1 | (TBD — verify) | Understanding AI in Education |
| M2 | 4 | 67 | Ethical Foundations in AI Use |
| M3 | 11 | 362 | AI Tools for Educators: Understand, Evaluate & Curate |
| M4 | 15 | 633 | AI Tools for Teaching |
| M5 | 16 | 655 | Prompt Engineering as Reflective Practice |
| M6 | 7 | (TBD — verify) | Human Accountability in AI |
| M7 | 5 | 98 | Navigating Ethical Dilemmas in AI Use |
| M8 | 13 | 447 | Advanced Prompt Engineering |
| M9 | 17 | 723 | AI-Enhanced Lesson Design |
| M10 | 18 | 791 | AI Collaboration and Communities of Practice |
| M11 | 8 | 291 | Your Voice in the AI School |
| M12 | 6 | 129 | Ethics Integration Across Curriculum |
| M13 | 14 | 515 | Multimodal AI Content Creation |
| M14 | 19 | 858 | Gamification and Immersive Learning |
| M15 | 20 | 925 | Professional Transformation and Research Leadership |
| **M16** | — | — | **PROODOS Epilogue (PLANNED, treated as existing per A8 precedent)** |

### Backup table (active)

`modules_modulecontent_backup_phase_a_tier4_may2026` — sprint-scoped backup, captures pre-Tier-4 state. Reusable for Cluster B. **Do NOT re-create.** All Cluster A patches' rollback paths use this table.

### `/tmp/` resolution on Windows

Windows git-bash `/tmp/` resolves to `C:\Users\dourv\AppData\Local\Temp\`. Tools that don't handle bash paths (Read/Write/Edit) need the Windows path.

### Environment

- Working directory: `C:\Users\dourv\unesco_ai_pd` (project root)
- Worktree may be active. New session likely starts fresh.
- Python venv: `./venv/Scripts/python.exe`
- Always prepend `PYTHONIOENCODING=utf-8` for emoji/UTF-8 console output on Windows
- DB credentials: postgres / Django123!
- xhtml2pdf 0.2.17 active; weasyprint broken on Windows (GTK runtime)

---

## Master docs update protocol

These are the source-of-truth docs. Update each Cluster B patch per pattern:

| File | Purpose |
|---|---|
| `proodos_files/CONTENT_VALIDATION_MATRIX.md` | Per-module per-indicator history. ~1700+ lines. |
| `proodos_files/CONTENT_VALIDATION_MATRIX.md` Trajectory table near end. |
| `proodos_files/CONTENT_GAPS_LOG.md` | Per-module gap log. ~1800+ lines. Trajectory table at end (search for "Phase A Tier 3 closure"). |
| `proodos_files/PHASE_A_REMAINING_GAPS_POST_TIER3.md` | Tier 4 scoping inventory. Each row = 1 indicator with status + feasibility. |
| `proodos_files/platform_changes_log.md` | Per-patch detailed log. ~2400+ lines. APPEND new section per patch. |

### Pattern A (audit-only sync)

Update **3 files** (NOT platform_changes_log):
1. CONTENT_VALIDATION_MATRIX — add `Indicators closed via [...]` line with brief evidence
2. PHASE_A_REMAINING_GAPS — strikethrough + ✅ Done with full evidence
3. CONTENT_GAPS_LOG — (a) module section audit-correction note + (b) trajectory rows

### Pattern B (apply patch — full DB + RAG + browser)

Update **all 4 files**:
1-3. Same as Pattern A
4. platform_changes_log — APPEND full per-patch section (use the A8 section as template; ~140 lines)

### Pattern D (reinforcement after split, like A6 Step 2B)

Same as Pattern B, BUT in platform_changes_log reference the Step 2A audit verdict in framing paragraph. After Step 2B applies, **remove "pending Step 2" suffixes** from MATRIX + CONTENT_GAPS_LOG (preserve audit history).

---

## Reusable infrastructure

### `ingest_phaseA_tier4_atomic.py` (project root)

Reusable atomic-chunk RAG helper. CLI:

```bash
cd /c/Users/dourv/unesco_ai_pd
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe ingest_phaseA_tier4_atomic.py --config /tmp/patch_bN_config.json --dry-run
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe ingest_phaseA_tier4_atomic.py --config /tmp/patch_bN_config.json
```

Config fields (required): `module_code`, `doc_title`, `chunk_text`, `patch_id`, `tier`, `indicator`. Optional: `sprint`, `topic_short`.

**Idempotent on `doc_title`** — if rerunning after wording revision, DELETE old doc + chunk first (psycopg2 DELETE chunks WHERE document_id=N + DELETE documents WHERE id=N), then re-ingest.

### Apply script template

Best template: `/tmp/patch_a8_apply.py` (most recent A7-family with anchor-AFTER pattern + 12 post-state checks + 5 ghost checks). For A4-family, use `/tmp/patch_a7_apply.py`. For A2/A6-family (citation reinforcement), use `/tmp/patch_a6_step2b_apply.py`.

Standard 12-check post-state:
- anchor_check (uniqueness preserved)
- idempotency_check (marker_count==2)
- length_band
- marker_open + marker_close
- 6 content checks (heading, key phrases, factual anchors)
- 5 ghost checks (A1/A2/A4/A6/A7 cross-row contamination)

Add **A8 ghost** to running list for Cluster B: `M10_CROSS_REF_M16_EPILOGUE_PATCH` substring or "M16 PROODOS Epilogue" phrase. Adjust per patch identity.

### RAG baseline + verify scripts

Best templates:
- Baseline: `/tmp/patch_a8_rag_baseline.py`
- Verify: `/tmp/patch_a8_rag_verify.py`

Both use Gemini API for embedding (768-dim) + cosine distance (`<=>`).

---

## How John works (preferences observed across full Sprint 2)

- **Greek + English mixed** — John writes briefs in English, talks in chat in Greek+English. Replies should match.
- **Stop-and-report cadence is non-negotiable** — every meaningful step needs a status report + browser-test request before proceeding. Saved many bugs across Sprints 1+2.
- **John approves anchor selection + locked v1 wording** before Stage 1 apply. Audit-first methodology surfaces these for John's call.
- **Standard closure phrase**: "Έγινε και είναι οκ" / "ok" / "ok το browser test" / "Browser test complete. Everything is ok" → mark patch closed, update apply report + platform_changes_log.
- **Practitioner-first critique** — John flags compliance/audit-language ("Ενδιαφέρει το χρήστη εκπαιδευτικό?"). When raised, **trim** the audit-only verbiage. Never expand.
- **Brief authoring style**: terse, structured, locked-wording-driven. John sometimes makes minor mistakes in briefs (factual generalisations, structural conflations, schema name mismatches, module label fabrications). The audit-first check pattern catches these.
- **John defers to my audit verdicts when they're well-justified** — A6 disagreement (chat-side Verdict A vs my Verdict C) was reconciled by John picking Path 1. Audit-first respect is established.
- **Marginal-fail acceptance** — Path 1 (accept marginal scores) is the established response to sub-0.70 sims when canonical query is strong.
- **In-flight revision** — first surfaced in A8 (UNESCO compliance paragraph trimmed mid-apply). John reviews initial card; trim/expand based on practitioner-first critique. Established as part of autonomous-wording mode workflow.
- **No docs for cosmetic-only batches** — chrome retro-fix batches (Cluster A retro-fix) didn't get docs updates per John ("design-level only"). Substantive patches DO get full Pattern B docs.
- **Side-fixes accepted** — when audit surfaces content↔implementation mismatches in adjacent modules (A8 → M15 line-222 cleanup), execute in same cycle.
- **M16 roadmap-existing assumption** — when M16 PROODOS Epilogue references are needed, treat as existing per John's confirmation 6 May 2026 ("Θεωρησε οτι υπάρχει ώστε να μην επιστρέφουμε για αλλαγες").

---

## Pattern-recognition cheat-sheet for Cluster B

```
IF brief identifies < N sub-clauses where UNESCO PDF actually has > N:
   → Sub-clause undercount risk
   → Decompose UNESCO verbatim BEFORE forming verdict
   → 5-of-10 prior audits surfaced this

IF locked wording cites a specific paper / specific author list / specific number:
   → Factual-error risk (3-of-9 prior patches had this)
   → Verify against paper PDF / Crossref / structural reality

IF target indicator is at Deepen/Create level and existing closure is at Acquire level:
   → Lenient-Tier-1 risk (A2/A6 examples)
   → Verdict C STRONG-WITH-RESERVATION; small reinforcement

IF target module has > 2 RAG documents:
   → Atomic-chunk pattern is MANDATORY (use ingest_phaseA_tier4_atomic.py)
   → Generic ingest_module_rag.py would over-clean

IF home-module has 0 native indicator content but another module substantively hosts:
   → A7/A8 family — cross-aspect/cross-level forward-reference
   → Navigational only, NOT substantive content addition

IF brief description claims module X has feature Y:
   → Verify via grep + tab3_content_*.py inspection
   → A8 caught false claims in M10/M13 brief; A7 caught false M11 label

IF locked-wording brief includes UNESCO indicator codes / verbatim quote in body:
   → John will likely flag as audit-only language ("Ενδιαφέρει το χρήστη?")
   → Pre-emptively trim to practitioner-only; keep UNESCO ref in metadata.patches[]

IF M16/Epilogue is the substantive home for the indicator:
   → Treat as existing per John's roadmap confirmation
   → Forward-reference assumes M16 launch; verbatim references don't need flag
```

---

## File locations of key artifacts

### Master docs (committed)

```
C:\Users\dourv\unesco_ai_pd\proodos_files\
├── CONTENT_GAPS_LOG.md            (master gaps log; trajectory table near end)
├── CONTENT_VALIDATION_MATRIX.md   (master audit table per module)
├── PHASE_A_REMAINING_GAPS_POST_TIER3.md (Tier 4 scoping; Cluster B at lines ~125-135)
└── platform_changes_log.md        (per-patch detail; ~2400 lines)
```

### Project-root scripts (committed)

```
C:\Users\dourv\unesco_ai_pd\
├── ingest_phaseA_tier4_atomic.py  (atomic-chunk RAG helper; reusable)
├── ingest_phaseA_tier3_step6_m8.py (Tier 3 canonical; do not modify)
└── ingest_module_rag.py           (generic re-ingest; AVOID for Tier 4 atomic patches)
```

### Pre-flight + apply + audit reports (Temp / `/tmp/`)

Most relevant for Cluster B (template references):

```
C:\Users\dourv\AppData\Local\Temp\
├── unesco_framework.txt                          (UNESCO PDF extracted; line-numbered for grep)
├── cg523_a8_audit.md / lo531_a9_audit.md         (most recent audit deliverables — use as templates)
├── audit_comparative_summary_a8_a9.md            (cross-audit synthesis pattern)
├── lo436_independent_audit.md                    (A7 audit — cross-aspect placement template)
├── ouyang_paper_audit.md                         (A6 paper-level audit template — for A2/B5/B6 if research citation)
├── patch_a8_preflight.py / patch_a8_preflight_report.md (pre-flight discovery template)
├── patch_a8_apply.py / patch_a8_followup.py     (apply + in-flight wording revision template)
├── patch_a8_config.json / patch_a8_config_v2.json (atomic ingest config template)
├── patch_a8_rag_baseline.py / patch_a8_rag_verify.py (RAG baseline + verify templates)
├── chrome_audit_cluster_a.md                    (chrome decision-tree audit; reference for Rule 1)
├── chrome_retrofix_apply.py / chrome_batch2_apply.py (chrome retro-fix templates)
└── (10+ other patch_a*_apply.py / config files for previous patches)
```

### Predecessor handoff docs

```
C:\Users\dourv\unesco_ai_pd\
├── HANDOFF_TO_TIER3_SESSION.md               (historical)
├── HANDOFF_TO_TIER4_SESSION.md               (Phase A Tier 3 → Tier 4 launch)
├── HANDOFF_TO_TIER4_SPRINT2_CONTINUATION.md  (mid-Sprint-2; up to A6 Step 2A)
└── HANDOFF_TO_TIER4_SPRINT2_CLUSTER_B_SESSION.md  (THIS FILE — post-Cluster-A handoff)
```

---

## Coverage trajectory (full Phase A Tier 4)

| Stage | STRONG | % | Notes |
|---|---:|---:|---|
| Post-Tier-3 closure | 142/170 | ~83.5% | Sprint 0 baseline |
| + Sprint 1 (3 audit corrections) | 145/170 | ~85.3% | Pure docs sync |
| + A1 v2 (M4 Tool 3, CG4.1.2) | 146/170 | ~85.9% | Tool-native conversion |
| + A2 (M9 dual citation, CG4.2.2) | 147/170 | ~86.5% | Reinforcement |
| + A3 (M11 sync, CG1.3.2) | 148/170 | ~87.1% | Audit-only sync |
| + A4 (M7 Scenario 8, CG2.2.2 + LO2.2.4) | 149/170 | ~87.6% | Standalone scenario |
| + A5 (M3 sync, LO3.1.1) | 150/170 | ~88.2% | Audit-only sync |
| + A6 (M8 Step 1+2A+2B, CG3.2.2) | 151/170 | ~88.8% | Lenient-T1 → reinforcement (RLHF) |
| + A7 (M15 Part 4, LO4.3.6) | 152/170 | ~89.4% | Cross-aspect standalone subsection |
| + A9 (M15 audit-only, LO5.3.1) | 153/170 | ~90.0% | **First crossing 90% threshold** |
| **+ A8 (M10 → M16 forward-ref, CG5.2.3)** | **154/170** | **~90.6%** | **Cluster A complete** |
| **+ Cluster B (6 indicators)** projected | **160/170** | **~94.1%** | **Phase A target ceiling** |

---

## Recommended workflow for the new session

1. **DO NOT auto-execute anything.** Wait for John's brief on which Cluster B indicator(s) to tackle.
2. **Read this handoff first.** Then `/tmp/cg523_a8_audit.md` + `/tmp/audit_comparative_summary_a8_a9.md` for most recent audit + apply patterns.
3. **For each Cluster B indicator**:
   - Audit-first ALWAYS — produce `/tmp/{indicator}_audit.md` with 6-dimension framework before apply
   - Sub-clause decomposition mandatory
   - Verify all brief claims via grep / tab3_content_*.py / DB queries
   - Determine pattern family (A3/A5/A9 audit-only OR A4 standalone OR A2/A6 citation OR A7/A8 cross-aspect)
   - Stop-and-report at every checkpoint (pre-flight verdict / locked wording / dry-run / commit / RAG verify / browser test)
4. **Browser test is mandatory** before patch closure (except audit-only sync). John executes; new session waits.
5. **Update master docs after every patch** per Pattern A/B/D protocol. Use post-A8 docs as templates (CONTENT_VALIDATION_MATRIX line ~678; PHASE_A row 5.3; CONTENT_GAPS_LOG M10 #2; platform_changes_log most recent).
6. **Chrome Rule 1 enforced** — all new patch wrappers use plain `card bg-base-200 p-4 my-4` (no border-l-4).
7. **Autonomous-wording mode default** — author the locked v1, expect John's in-flight review (especially flagging UNESCO compliance verbiage).
8. **When unsure, ρώτα στο chat.** John drives strategy and reconciles audit disagreements.

---

## Decision points open for John (recorded for transparency)

1. **Cluster B sequencing** — Single patches one-by-one, OR combined patches (e.g., B5+B6 on AI-manipulated platforms territory)?
2. **B2 (CG4.2.1 SEL M9↔M14)** — A7 family forward-reference is likely cleanest (M14 has SDT/Connection content). Verify via audit.
3. **B5 (CG5.1.4 AI-manipulated cocoons M5)** — Does this need peer-reviewed research citation (A2/A6 family) or standalone scenario (A4 family)? Audit will determine.
4. **B6 (CG5.2.2/5.2.4 emerging tools M10)** — combined patch combining sub-clauses (a) emerging tools + (b) algorithmic risks?
5. **M16 PROODOS Epilogue launch timing** — does Cluster B include any indicator that needs M16 to be actually built? CG5.2.3 closure assumes M16 exists; if M16 launch is delayed, A8 forward-reference may need revisit.

---

*Created: 6 May 2026, end of Sprint 2 Cluster A (after A1–A9 all closed; 154/170 / ~90.6%).*
*Predecessor: HANDOFF_TO_TIER4_SPRINT2_CONTINUATION.md (mid-Sprint-2, up to A6 Step 2A).*
*Successor: TBD — written by next session at end of Cluster B (after B1-B6 if pursued).*
*Trust judgement per Tier 1+2+3+4 patterns. When in doubt, audit first.*
