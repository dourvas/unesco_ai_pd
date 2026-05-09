# Handoff to Tier 4 Session — Post-Tier-3 + Step 12 Closure

**Date:** 3 Μαΐου 2026
**Predecessor session:** Phase A Tier 3 + Step 12 (executed in this same project, prior Claude Code session)
**Coverage stamp:** 142 / 170 STRONG indicators (~83.5%) · 28 / 170 PARTIAL (~16.5%) · 0 ABSENT
**Predecessor handoff:** `HANDOFF_TO_TIER3_SESSION.md` (now historical)

---

## TL;DR for the new session

Phase A is fully closed at 83.5% STRONG. The previous session executed Tier 3 (12 spec steps + 1 mid-flight + 1 post-closure) and merged 4 master documentation files. Δεν υπάρχει ξεκρέμαστη work-in-progress — όλα τα Tier 3 artefacts είναι browser-tested, committed, και documented.

**Tier 4 is OPTIONAL.** John drives strategy and ordering with Claude chat as planning partner. This document gives the new Claude Code session the technical/operational context to execute whatever Tier 4 patches John picks.

The strategic gap analysis already exists at:
**`proodos_files/PHASE_A_REMAINING_GAPS_POST_TIER3.md`** — 28 PARTIAL indicators classified σε 5 feasibility clusters (A–E). This is your source-of-truth for what's left.

---

## What just happened (Tier 3 + Step 12 summary)

### Tier 3 (12 steps)

| Step | Output | Status |
|---|---|---|
| 1 | Pre-flight (6 blockers caught + resolved) | ✅ |
| 2 | New Django app `apps.peer_blog` (Practice Workshop) | ✅ |
| 3 | M13 simplification + canvas-as-body redesign | ✅ |
| 3.5 | Navigation + author self-service (added mid-flight) | ✅ |
| 4 | M9 wiring (Hybrid Option C, opt-in C3-only) | ✅ |
| 5 | M14 wiring (Gamified Unit C3-only) | ✅ |
| 6 | M8 Type-A patches (CG3.2.4 ethics + CG3.2.1 cross-ref) + RAG ingest | ✅ |
| 7 | `REACTIVE_MODERATION_POLICY.md` (project root) | ✅ |
| 8 | `CONTRIBUTING.md` aligned + pushed to GitHub (commit `d3e7d16`) | ✅ |
| 9 | PDF backend decision (folded into logs) | ✅ |
| 10 | Logs + audit projection update | ✅ |
| 11 | Final summary report | ✅ |
| 12 | Reactive moderation policy user-facing visibility (post-closure) | ✅ |

### Master docs merged (post-Tier-3)

| File | What was merged |
|---|---|
| `proodos_files/CONTENT_GAPS_LOG.md` | Tier 3 update section + 5 inline indicator updates + projection table refresh |
| `proodos_files/platform_changes_log.md` | Tier 3 append verbatim (Steps 2-12, defence rationale D15) |
| `proodos_files/CONTENT_VALIDATION_MATRIX.md` | All 14 M*_MATRIX_ENTRY files inserted in place of placeholders + bibliography 19 → 53 references |
| `proodos_files/PHASE_A_REMAINING_GAPS_POST_TIER3.md` (new) | 28 PARTIAL indicators classified με Tier 4 scoping options α/β/γ/δ |

---

## Where everything lives (file map)

### Project root

```
C:\Users\dourv\unesco_ai_pd\
├── HANDOFF_TO_TIER4_SESSION.md           ← this file
├── HANDOFF_TO_TIER3_SESSION.md           ← historical (Tier 3 starting point)
├── PHASE_A_TIER3_SPEC_v3.md              ← Tier 3 spec (just executed)
├── PLATFORM_CHANGES_LOG_TIER3_APPEND.md  ← Tier 3 platform log (also merged in master)
├── CONTENT_GAPS_LOG_TIER3_UPDATE.md      ← Tier 3 gaps update (also merged in master)
├── REACTIVE_MODERATION_POLICY.md         ← researcher-facing policy (Step 7)
├── PLATFORM_CHANGES_LOG_TIER2_APPEND.md  ← Tier 2 historical
├── CONTENT_GAPS_LOG_TIER2_UPDATE.md      ← Tier 2 historical
├── apps/                                  ← Django apps
│   ├── users/                             (TeacherProfile + new @property pseudonym)
│   ├── modules/                           (main modules + ModuleDetailView)
│   ├── community/                         (forum — UNTOUCHED in Tier 3)
│   └── peer_blog/                         ★ NEW APP από Tier 3 (Practice Workshop)
├── templates/
│   ├── base.html                          (top-nav Practice Workshop dropdown added)
│   ├── peer_blog/                         ★ NEW (5 templates)
│   └── modules/tabs/                      (M13/M9/M14 share cards added)
├── config/
│   ├── settings.py                        (apps.peer_blog + workshop_modules context processor)
│   └── urls.py                            (/blog/ namespace mount)
├── phaseA_tier3_step6_apply.py            ← M8 patch script (executable, --dry-run flag)
├── ingest_phaseA_tier3_step6_m8.py        ← RAG ingest script
├── verify_phaseA_tier3_step6_m8.py        ← RAG verification script
└── proodos_files/                         ← Master documentation directory
    ├── CONTENT_GAPS_LOG.md                ★ master gaps log (Tier 1+2+3 merged)
    ├── platform_changes_log.md            ★ master platform log (Tier 1+2+3 merged)
    ├── CONTENT_VALIDATION_MATRIX.md       ★ full 15-module matrix
    ├── PHASE_A_REMAINING_GAPS_POST_TIER3.md ★ Tier 4 scoping inventory (28 PARTIAL classified)
    ├── M2_MATRIX_ENTRY.md ... M15_MATRIX_ENTRY.md  ← per-module detail (already merged into matrix)
    └── CONTENT_VALIDATION_MATRIX_BACKUP.md (if any)
```

### Critical paths Tier 4 may touch

- **`apps/modules/views.py`** — `ModuleDetailView.get_context_data` is the central context dispatcher (M9/M14 share blocks + M13 PDF defaults live here). Pre-Tier-3 has 2 incidental fixes at lines 751 + 1171 (`teacher_profile` rename).
- **`apps/peer_blog/sharing.py`** — `MODULE_SHARE_CONFIG` registry (M9/M14). Add new module entries here for Workshop wiring.
- **`apps/modules/tab3_content_m{N}.py`** — per-module TAB3 data. M9/M14 are wired; M2/M3/M4/M5/M6/M7/M11/M12 not in Workshop.
- **`templates/modules/tabs/tab3_activity_m{N}.html`** — per-module TAB3 templates.
- **modules_modulecontent table** — main TAB2 content. Atomic patches go here (Type A = HTML insertion, Type B = subject_box).

---

## Operational baseline

### Database (PostgreSQL 5432, dbname=unesco_ai_teacher_pd, user=postgres, password=Django123!)

```
modulecontent_rows                      1258  (matches Tier 2/3 baseline)
modules_modulecontent_backup_phase_a_tier2_may2026   1258  (Tier 2 baseline preserved)
modules_modulecontent_backup_phase_a_tier3_may2026   1258  (Tier 3 baseline preserved)
document_chunks (RAG corpus)             940  (Tier 2 baseline 938 + 2 Tier 3 M8 patches)
M8 row id=447 length                  44 351  chars (was 42 278, +2 073 from Tier 3 patches)
M8 row 447 metadata.patches[]              2  (m8_ethics_by_design + m8_cross_ref_m3)
peer_blog_blogpost                         1  (id=19, hidden — your Step 12 admin moderation test)
peer_blog_blogcomment                      0
Tab3RepositorySubmission                   1  (id=1 Tier 2 legacy "first law", preserved)
```

**Pre-Tier-4 cleanup option:** delete BlogPost id=19 (`DELETE FROM peer_blog_blogpost WHERE id=19;`) for completely clean pilot baseline. Optional.

### Backup conventions

- **Take a defensive backup before any DB-modifying step**: `CREATE TABLE modules_modulecontent_backup_phase_a_tier4_<topic>_may2026 AS SELECT * FROM modules_modulecontent;`
- For non-DB changes (template/view edits), no backup needed — git provides recovery.

### Environment (Windows + git-bash)

```bash
PYTHONIOENCODING=utf-8                        # mandatory for emoji/UTF-8 console output
GEMINI_API_KEY (in .env, loaded via dotenv)    # for RAG embedding
xhtml2pdf 0.2.17                              # active PDF backend
weasyprint 68.1                               # installed but BROKEN on Windows venv (GTK runtime missing)
Django 6.0.1                                  # CheckConstraint uses condition=, not check=
PostgreSQL 5432                               # standard creds above
psql binary path: /c/Program\ Files/PostgreSQL/*/bin/psql.exe
```

### Test users (email · username · subject · grade)

```
admin@unesco.local · admin · — · —                   (id=1, superuser, last login 2026-05-02)
testuser@example.com · testuser · — · —              (id=2, staff)
maria@test.com · maria@test.com · — · —              (id=3, staff)
mavros@example.com · mavros · mathematics · upper    (id=6, ★ TIER 3 TEST USER, has all 15 modules' Tab3 data)
argyris.dourvas2013@gmail.com · argyris.dourvas2013 · physics · upper (id=7, peer test user)
```

`admin` password: was reset by John during Step 12 (he picked it; not recorded here).

### Useful Django management commands

```bash
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe manage.py check
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe manage.py shell
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe manage.py makemigrations
PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe manage.py migrate
```

---

## Tier 4 candidate inventory (from `proodos_files/PHASE_A_REMAINING_GAPS_POST_TIER3.md`)

**Read that doc first.** It's your authoritative Tier 4 source. Headline:

| Cluster | # indicators | Effort | Expected Δ | Decision posture |
|---|---|---|---|---|
| 🟢 **A — Easy text patches** | 10 | ~9h total | +10 STRONG → ~89% | Prime Tier 4 candidates |
| 🟡 **B — Medium effort cross-module** | 6 | ~14h total | +5 STRONG → ~92% | Optional second wave |
| 🟠 **C — Platform features** | 3 | sprint-scale | +variable | **Defer until post-pilot** |
| 📌 **D — Defendable design choices** | 7 | doc-only | 0 (intentional) | Document explicitly, don't patch |
| 📋 **E — Audit-correction candidates** | 3 | ~1.5h docs | +3 STRONG | Quickest wins (no platform work) |

**Recommended order** (in the gap analysis doc):

1. **Cluster E** first — 3 audit corrections, ~1.5h, +3 STRONG (no platform changes, just docs)
2. **Cluster A** next — 10 easy patches similar to Tier 3 atomic patches (~9h, +10 STRONG)
3. **Cluster B** if time/appetite — 6 medium patches (~14h, +5 STRONG)
4. Cluster C deferred to post-pilot
5. Cluster D defended explicitly in dissertation, not closed

**Strategic option δ (the one I recommended):** run pilot first, scope Tier 4 from real engagement signal. John may or may not adopt this.

---

## Patterns to follow (proven across Tier 1 + 2 + 3)

### Atomic DB patch pattern (Type A)

For any TAB2 content patch (M8 ethics-by-design is the canonical Tier 3 example):

```python
import psycopg2, json
DB = dict(dbname='unesco_ai_teacher_pd', user='postgres', password='Django123!',
          host='localhost', port='5432')

ANCHOR = '<exact unique HTML string from current content_data>'
NEW_BLOCK = '<!-- MARKER -->\n<div class="card ...">...</div>\n<!-- /MARKER -->\n\n'
REPLACEMENT = NEW_BLOCK + ANCHOR  # or ANCHOR + NEW_BLOCK depending on placement

PATCH_META = {
    "id": "<patch_id>", "phase": "A_tier4_<step>",
    "indicator": "<UNESCO code>", "applied_at": "2026-05-XX",
}

# Open transaction with autocommit=False
# Pre-checks: anchor count == 1, marker NOT pre-existing
# Apply: REPLACE() in SQL + jsonb_set + COALESCE for metadata.patches[] append
# Post-checks: marker present (count == 2 — open + close), length in expected band
# COMMIT only if all checks pass; ROLLBACK on any failure
```

Reference: `phaseA_tier3_step6_apply.py` is the canonical example. Use it as a template.

### Anchor pre-flight (non-negotiable)

Always verify anchor count == 1 και marker count == 0 BEFORE applying. Tier 1+2 caught 6+ blockers με this pattern. Use Python (not psql) for anchor inspection — psql byte-position vs char-position misalignment with emojis. Sample 200-300 chars before+after each candidate anchor.

### RAG ingest pattern (atomic chunks)

Reference: `ingest_phaseA_tier3_step6_m8.py` is the Tier 3 canonical pattern. Key points:
- One chunk per patch
- `clean_text()` strips HTML/whitespace/non-word chars
- `chunk_text` includes header: Module + Subject + Type + UNESCO Indicator + Patch ID + cleaned text
- 768-d embedding via `gemini-embedding-001` με `output_dimensionality=768`
- `time.sleep(5.0)` between embeddings (rate-limit hygiene)
- Idempotent on document title (skip if exists)
- Insert into `documents` (with metadata) + `document_chunks` (with embedding)

### RAG verification pattern

Reference: `verify_phaseA_tier3_step6_m8.py`. Run 3 queries per patch (1 spec primary + 2 alts). Target: #1 mod-scoped retrieval = TARGET (functional success criterion). Sim threshold ≥ 0.78 desirable; 0.005 short accepted as cosmetic miss per Tier 2 M5 precedent (0.7751 was accepted).

### Dry-run before COMMIT (mandatory)

Every DB-modifying script MUST support `--dry-run` mode (rolls back at end). Show diffs to John, get sign-off, THEN run without `--dry-run` to commit.

### Stop-and-report cadence

After every meaningful step:
1. Status report in chat (what was applied, what was verified)
2. Browser test request (specific URL + expected behavior)
3. Wait for John's sign-off before next step

This is non-negotiable for Tier 1+2+3 work. Saved many bugs.

---

## Critical gotchas — DON'T re-introduce

| Bug | Symptom | Fix |
|---|---|---|
| **Multi-line `{# ... #}` Django comment** | Comment text renders literally on page | Use `{% comment %}...{% endcomment %}` for multi-line. Single-line `{# ... #}` is fine. |
| **Django 6.0.1 `CheckConstraint(check=...)` deprecated** | Migration crashes με `TypeError: unexpected keyword argument 'check'` | Use `condition=` instead |
| **`request.user.teacherprofile`** (no underscore) | AttributeError — silent fallback | Use `request.user.teacher_profile` (related_name has underscore). 2 broken refs already fixed in views.py (Tier 3 incidental); don't write new ones. |
| **Multi-select fields come through as lists** | `_label_for` helper crashed on `['explanation']` | Add `if isinstance(value, list)` branch to label-lookup helpers |
| **DaisyUI `alert alert-info` + `link link-info`** | Blue text on blue background — invisible without hover | Use `card bg-base-200 border-l-4 border-info` pattern with `text-base-content` body + `link link-info` on anchor (high contrast) |
| **psql byte-position emoji misalignment** | `position()`/`substring()` returns wrong offsets when content has emojis | Inspect content via Python string slicing, not psql substring |
| **Naive datetime warnings** in legacy Tab3UserActivity rows | Runtime warnings during smoke tests | Pre-existing data drift (dates 2026-04-11 onward). Not Tier 3-introduced. Could be cleaned με one-time backfill if production warnings noisy. |
| **`PYTHONIOENCODING=utf-8`** | Console crashes on emoji output | Always prepend to commands on Windows |
| **weasyprint** | Import fails on Windows GTK runtime | xhtml2pdf 0.2.17 is the working backend. Linux test deferred until production deployment target known. |
| **Spec assumes `profile.pseudonym` field** | Doesn't exist | Tier 3 added `@property pseudonym` to TeacherProfile (returns `display_name` or `f"Educator_{user_id}"`). No DB column. |

---

## Decision points open for John

These are recorded so the new session is aware:

1. **Tier 4 launch decision**: Option α (audit + easy = ~12h) vs Option β (+ medium = 26h) vs Option δ (pilot first, Tier 4 informed by signal). Recommendation in gap analysis doc was Option δ. John will decide.
2. **Pre-Tier-4 cleanup**: BlogPost id=19 (Step 12 moderation test artefact) optional removal για clean pilot baseline.
3. **Master log re-merge cadence**: when Tier 4 patches happen, do they re-merge into `proodos_files/` master docs immediately or batched at Tier 4 close?
4. **Tier 4 documentation pattern**: should Tier 4 follow the Tier 3 pattern (separate `_TIER4_APPEND` files initially, then merge into master)? Or write directly into master? Tier 3 used the separate-file-then-merge pattern.

---

## Recommended workflow for Tier 4 patches

1. **Read** `proodos_files/PHASE_A_REMAINING_GAPS_POST_TIER3.md` carefully. Pick Cluster + indicator(s).
2. **Pre-flight**: locate the target module. Verify anchor candidate count == 1. Verify marker not pre-existing. Sample 200-300 chars around anchor.
3. **Stop-report**: tell John the planned wording + anchor + expected indicator status change. Get sign-off.
4. **Dry-run** the apply script. Show diffs. Get sign-off.
5. **Apply** (COMMIT). Verify post-state.
6. **RAG ingest** if it's a TAB2 content patch. Sleep 5s between embeddings.
7. **RAG verify** με 3 queries. Report sims.
8. **Browser test** request. Wait for John's confirmation.
9. **Update logs** (write Tier 4 append doc; merge into master at Tier 4 close).

If just writing audit-correction docs (Cluster E):
- Skip apply/RAG/browser test
- Update CONTENT_GAPS_LOG.md inline + add to projection table
- Show diff to John

---

## Quick reference: Tier 3 anchor patterns reused

### M8 patch anchors (already used in Tier 3 — for reference)

```python
P5_ANCHOR = (
    '<div class="divider my-8"></div>\n\n'
    '<h2 class="text-3xl font-bold text-info mb-6">🧭 Part 5: From Library to Live — Orchestrating Your Prompts in Real Time</h2>'
)
P1_ANCHOR = '<h2 class="text-3xl font-bold text-primary mb-6">🔄 Part 1: From Knowing to Doing</h2>'
```

### Common anchor pattern in PROODOS

`<h2 class="text-3xl font-bold text-{color} mb-6">{emoji} Part {N}: {title}</h2>` — typically unique per module, count == 1.

For composite anchors (e.g., divider + H2 to land patch BEFORE the divider), include both elements as one string.

---

## Module reference quick map

| Module | mod_id | main_content row id | Aspect | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|---|---|---|
| M1 | 1 | (varies) | 1 Acquire | — | — | — |
| M2 | 2 | (varies) | 2 Acquire | sustainability_apr2026, eu_ai_act_apr2026 | — | — |
| M3 | 3 | (varies) | 3 Acquire | M3_lifecycle_apr2026 (Day 3) | — | — |
| M4 | 4 | (varies) | 4 Acquire | — | M4 SVG normalisation (3 SVGs) | — |
| **M5** | 11 | (varies) | 5 Acquire | — | m5_disabilities_focus | — |
| **M6** | 12 | (varies) | 1 Deepen | — | — | — (CG1.2.4 audit-correction) |
| **M7** | 13 | (varies) | 2 Deepen | deepfake_dilemma_apr2026 | — | — |
| **M8** | 14 (NB: M14 module is mod_id=19, M8 is mod_id 13... wait let me re-check) | **447** | 3 Deepen | — | — | **m8_ethics_by_design + m8_cross_ref_m3** |

**WARNING for the new session**: I'm not 100% sure of every mod_id mapping. The Tier 3 pre-flight verified M8 = mod_id 13 + main_content row id = 447. M9 = mod_id 17. M14 = mod_id 19. M13 = mod_id 14 (per the seed canvas test from Step 3). Always verify with a fresh DB query before relying on these:

```sql
SELECT id, code, title FROM modules_module ORDER BY order_index;
SELECT id, module_id, content_type, length(content_data) FROM modules_modulecontent WHERE content_type='main_content' ORDER BY module_id;
```

---

## Connection to the Practice Workshop (peer_blog) infrastructure

If Tier 4 wants to wire additional modules to the Workshop (currently M13/M9/M14):

1. Add entry to `apps/peer_blog/services.py:WORKSHOP_ACTIVE_MODULES`
2. Add config dict to `apps/peer_blog/sharing.py:MODULE_SHARE_CONFIG`
3. Write `_render_m{N}_body(challenge_data)` helper function in `sharing.py`
4. Add module-specific share defaults block in `apps/modules/views.py:ModuleDetailView.get_context_data` (mirror M9/M14 patterns)
5. Add share card section to `templates/modules/tabs/tab3_activity_m{N}.html`
6. Browser test με mavros user

The infrastructure absorbs new modules cleanly (verified in Step 5 — M14 added with zero new views/routes/schema, only 1 new entry).

---

## What NOT to do

- **Don't re-run Tier 3 spec** — already executed and committed. Use `PHASE_A_REMAINING_GAPS_POST_TIER3.md` as source for new work.
- **Don't modify `apps.community` (forum)** — out of scope. Forum follows its own conventions.
- **Don't take backups of every minor template change** — git tracks those. DB-modifying scripts get backups.
- **Don't skip `--dry-run`** — saved 6+ blockers across Tier 1+2+3.
- **Don't commit changes to Github CONTRIBUTING.md** without being asked — Tier 3 commit `d3e7d16` already aligned it; future iterations need John's sign-off.

---

## What success looks like for Tier 4

If John picks **Option α** (~12h target):
- 3 Cluster E audit-corrections done in `proodos_files/CONTENT_GAPS_LOG.md`
- 10 Cluster A easy patches applied (similar to Tier 3 atomic pattern)
- RAG corpus 940 → ~950 chunks (1 ingest per content patch)
- Browser tests verified for each patch
- Coverage 142 → 155 STRONG (~91%)
- New `PLATFORM_CHANGES_LOG_TIER4_APPEND.md` + `CONTENT_GAPS_LOG_TIER4_UPDATE.md` written
- Master docs re-merged at Tier 4 close
- Total time: 1-2 sessions

If John picks **Option δ** (pilot first):
- No Tier 4 patches yet
- Pilot launches με 142/170 baseline
- Tier 4 scoping informed by ~6-month pilot data
- This handoff doc remains relevant for Tier 4 whenever it happens

---

*Created: 3 Μαΐου 2026 — end of Phase A Tier 3 + Step 12 closure*
*Predecessor: `HANDOFF_TO_TIER3_SESSION.md`*
*Successor: TBD — written by next session at Tier 4 close*
*Trust judgement per Tier 1+2+3 patterns. When stuck, read `PHASE_A_REMAINING_GAPS_POST_TIER3.md` and the Tier 3 reference scripts. When unsure, ρώτα στο chat — John drives strategy.*
