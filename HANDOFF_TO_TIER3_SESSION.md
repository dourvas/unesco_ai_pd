# Handoff to Tier 3 Session

**Author:** Claude (closing Tier 2 session) → Claude (opening Tier 3 session)
**Date:** 2026-05-02
**Purpose:** Single-document briefing so a fresh Claude instance can start Tier 3 without losing institutional knowledge.

> **READ THIS FILE FIRST.** Then read the 2 referenced logs only if you need depth.

---

## 1. Project in 60 seconds

**PROODOS** — Greek-English (UI in English, dev comments mixed) Django platform for K-12 teacher AI professional development, aligned to UNESCO AI Competency Framework for Teachers (2024).

15 modules (M1-M15) × 4 tabs each. The work focus is:
- **TAB2 (main_content)** — long HTML stored in `modules_modulecontent.content_data` text field
- **TAB3 (activity)** — interactive challenges; content lives in Python files (`apps/modules/tab3_content_m*.py`) + templates (`templates/modules/tabs/tab3_activity_m*.html`); user submissions stored in `tab3_user_activity.challenge_data` JSONB

**Goal of Phase A:** raise UNESCO indicator coverage from baseline → ≥80% STRONG. Tier 2 closed at **~81.2% STRONG (138/170)**. Tier 3 candidates aim for ~84%.

**Methodology:** atomic surgical patches inside HTML blobs (UPDATE with REPLACE on unique anchor strings) + atomic RAG chunks per patch. Never invent patterns — match what's already in the codebase.

---

## 2. Quick start coordinates

```
Project root:   C:\Users\dourv\unesco_ai_pd
Worktree:       C:\Users\dourv\unesco_ai_pd\.claude\worktrees\keen-kepler-defc6c
Test user:      argyris.dourvas2013@gmail.com (id=7)
DB:             postgresql://postgres:Django123!@localhost:5432/unesco_ai_teacher_pd
Python venv:    C:\Users\dourv\unesco_ai_pd\venv\Scripts\python.exe (Python 3.13.5)
.env location:  project root (load via `load_dotenv(find_dotenv(usecwd=True))`)
```

```
Latest migration:   apps/modules/migrations/0011_alter_modulecontent_subject_area_and_more.py
Latest backup:      modules_modulecontent_backup_phase_a_tier2_may2026 (1258 rows, post-Tier-2)
RAG corpus:         938 chunks, document_chunks table, 768-d embedding via gemini-embedding-001
PDF backend:        xhtml2pdf 0.2.17 (weasyprint installed but UNUSED — Windows GTK blocked)
GitHub repo:        https://github.com/dourvas/proodos-eduai-teacher-workflows (live, MIT, public)
```

```
Encoding gotcha (Windows):  always run scripts with PYTHONIOENCODING=utf-8 or use psql via venv python
                            cp1253 default breaks emoji/Greek prints
DB column reality check:    modules_modulecontent has columns:
                              id, content_type, subject_area, grade_level,
                              content_data (TEXT), metadata (JSONB),
                              created_at, updated_at, module_id
                            (NOT section_key / display_order / content_html — old specs got these wrong)
```

---

## 3. Established patterns (the playbook)

### 3.1 DB UPDATE pattern for TAB2 patches

Every TAB2 patch follows this transaction:

```python
import psycopg2, json
DB = dict(dbname='unesco_ai_teacher_pd', user='postgres', password='Django123!',
          host='localhost', port='5432')

ANCHOR = '<exact unique HTML string from current content_data>'
NEW_BLOCK = '<!-- MARKER apr2026 -->\n<div class="card ...">...</div>\n<!-- /MARKER -->\n\n'
REPLACEMENT = NEW_BLOCK + ANCHOR  # or ANCHOR + NEW_BLOCK depending on placement

PATCH_META = {
    "id": "<patch_id>", "phase": "A_tier3_<step>",
    "indicator": "<UNESCO code>", "applied_at": "2026-05-XX",
}

# Open transaction with autocommit=False + SELECT ... FOR UPDATE
# Pre-checks: anchor count == 1, marker NOT pre-existing
# Apply: REPLACE() + jsonb_set + COALESCE for metadata.patches[] append
# Post-checks: marker present, length in expected band, patches array length correct
# COMMIT only if all checks pass; ROLLBACK on any failure
```

**Why anchor count == 1:** patches MUST be idempotent. If anchor matches multiple places, you'd duplicate content.
**Why marker pre-existence check:** prevents re-applying the same patch (silent corruption).
**Why jsonb_set + COALESCE pattern:** preserves existing patches[] entries when appending new ones (initially used shallow `||` merge, switched to jsonb_set after Day 1 lessons).

### 3.2 Anchor discovery protocol (CRITICAL — Tier 1 Cycle 1 lost time to anchor mismatches)

Before writing any UPDATE:
1. Read the actual `content_data` from DB
2. Find candidate anchor regions
3. **Verify anchor uniqueness via `blob.count(anchor)` — must equal exactly 1**
4. Show the anchor seam (200 chars before + after) to confirm placement is what you intended
5. If anchor isn't unique, widen it (combine with adjacent unique element like an H2/H3)

**Spec-vs-reality drift is common.** Tier 2 had 6 blockers — M5 "Iceberg" didn't exist in main_content (re-targeted to Part 1), M4 Part 3/4 had different content than spec assumed (SVGs re-designed). Always verify.

### 3.3 RAG ingest pattern

Atomic chunks — **one chunk per patch**:

```python
# Use ingest_*_apr2026.py / ingest_phaseA_*.py pattern from worktree
# - Extract HTML between patch markers from updated row
# - clean_text() strips HTML/whitespace/non-word chars
# - Build chunk_text with header: Module + Subject + Type + UNESCO Indicators + Patch ID + cleaned text
# - Generate 768-d embedding via gemini-embedding-001
# - Insert into documents (with metadata) + document_chunks (with embedding)
# - Sleep 5.0s between embeddings (rate-limit hygiene)
# - Idempotency: skip if document with same title already exists
```

Verification: 3 retrieval queries per patch, target #1 unfiltered AND mod-scoped. Sim ≥ 0.78 is desirable but not strict — clean #1 retrieval matters more than sim threshold.

**SVGs: skip RAG ingest** (joint decision Tier 2 Step 3) — visualisations are not net-new conceptual content; cleaned text is mostly labels.

### 3.4 TAB3 patch pattern

When patching TAB3 (challenge content):
- Edit Python file `apps/modules/tab3_content_m*.py` (data structures)
- Edit template `templates/modules/tabs/tab3_activity_m*.html` (rendering + JS)
- View handlers (`submit_challenge1/2/3`, `submit_reflection`) are **generic** — they accept any keys in JSON body and persist to `Tab3UserActivity.challenge_data` JSONB as `challenge<N>_<key>`
- Use `audit_version: 2` flag in submit body for backward compat (old submissions = v1, new = v2)
- For backward-compat in templates use Django default filters: `{{ data.field|default:legacy_value }}`

### 3.5 File naming conventions

| Pattern | Example |
|---|---|
| Apply scripts | `phaseA_tier{N}_step{M}_apply.py` or `day{N}_p{M}_apply.py` |
| Dry-run scripts | `..._dryrun.py` (uses BEGIN..ROLLBACK) |
| Ingest scripts | `ingest_<patch_id>_<date>.py` |
| Verify scripts | `verify_<patch_id>_<date>.py` |
| Patch markers in HTML | `<!-- <NAME>_PATCH apr2026 -->` ... `<!-- /<NAME>_PATCH -->` |
| Backup tables | `modules_modulecontent_backup_<phase>_<date>` |

---

## 4. What's been applied (compact summary)

### Module-by-module patch state (post-Tier-2)

| Module | Row | Length | metadata.patches |
|---|---|---|---|
| M1 | 1 | 40 064 | (untouched) |
| **M2** | 67 | 30 244 | sustainability_regulation_apr2026 (Day 2) |
| **M3** | 362 | 39 280 | ai_lifecycle_apr2026 (Day 3) |
| **M4** | 633 | 54 111 | m4_svg1/m4_svg2/m4_svg3 (Tier 2 Step 3) |
| **M5** | 655 | 30 223 | m5_disabilities_focus (Tier 2 Step 2) |
| M6 | 258 | 40 984 | (untouched — Tier 3 candidate) |
| **M7** | 98 | 45 500 | deepfake_dilemma_apr2026 (Day 2) |
| M8 | 447 | 42 278 | (untouched — Tier 3 candidate) |
| **M9** | 723 | 55 905 | backward_design_citation (Tier 1) |
| **M10** | 791 | 42 769 | master_teachers_acknowledgment (Tier 1) + m10_disabilities_focus (Tier 2) |
| **M11** | 291 | 55 739 | disabilities_apr2026 + citizenship_apr2026 + commercial_apr2026 + global_frameworks (4 patches) |
| **M12** | 129 | 62 361 | climate_apr2026 + eu_ai_act_human_oversight + master_teachers_advocates (3) |
| **M13** | 515 | 89 595 | customisation_continuum_apr2026 + oss_vs_commercial (2) |
| **M14** | 858 | 39 133 | triangular_interactions + standalone_vs_institutional (2) |
| **M15** | 925 | 53 993 | disabilities_apr2026 + m15_disabilities_focus (2) |

13 of 15 modules patched. **Untouched: M1, M6, M8** (M1 has minor metadata only).

### TAB3 changes
- **M2 TAB3:** added 6th audit question (environmental footprint + M12 cross-ref) — Tier 1 Cycle 2 Q1
- **M13 TAB3:** Repository Submission CTA on Challenge 2 — 3 buttons (PDF / Submit for Peer Review / GitHub) + submission modal — Tier 2 Step 4
- **M15 TAB3:** Tier 5 Training Module on Challenge 2 — yes/no gate + optional 5th column + soft-mandatory description + completed-state display — Tier 2 Step 5

### New backend (Tier 2 Step 4)
- `Tab3RepositorySubmission` model + `0011` migration
- `submit_to_repository` + `export_canvas_pdf` views
- 2 new URL routes
- `GITHUB_WORKFLOWS_URL` settings constant
- Django admin με 3 actions (approve/reject/needs_revision) — **currently admin-only** (peer review evolution = Tier 3 candidate)
- `templates/pdf/m13_canvas_export.html`

### RAG corpus growth
- Day 1-3: 917 → 926 (+9)
- Tier 1 Cycle 1: 926 → 933 (+7)
- Tier 1 Cycle 2: 933 → 935 (+2)
- Tier 2 Step 2: 935 → 938 (+3)
- **Total: 938 chunks**

### Backups available
- `modules_modulecontent_backup_disabilities_apr2026` (Day 1 morning)
- `modules_modulecontent_backup_citizenship_apr2026` (Day 1 evening)
- `modules_modulecontent_backup_climate_apr2026` (Day 2 morning)
- `modules_modulecontent_backup_commercial_apr2026` (Day 2 afternoon)
- `modules_modulecontent_backup_m7_layout_apr2026` (Day 2 layout refactor)
- `modules_modulecontent_backup_programming_apr2026` (Day 3)
- `modules_modulecontent_backup_phaseA_tier1_cycle1` (Tier 1 C1)
- `modules_modulecontent_backup_phaseA_tier1_cycle2` (Tier 1 C2)
- `modules_modulecontent_backup_phase_a_tier2_may2026` (Tier 2 — most recent)

---

## 5. Tier 3 candidates (open work)

Per the 2 logs and conversation:

### 5.1 Peer review evolution (Tier 3 highest-priority candidate)
- **Why:** mismatch between current admin-only review and CONTRIBUTING.md "master teachers" aspirational language; PROODOS philosophy alignment
- **Level 1 (recommended):** ~1.5h
  - Add `is_subject_reviewer = BooleanField(default=False)` to `apps.users.models.TeacherProfile`
  - Custom admin class filtering `subject_area = request.user.teacher_profile.subject_area`
  - Update `CONTRIBUTING.md` to align με implementation
- **Level 2:** custom teacher-facing dashboard (~6-8h, separate sprint)
- **Level 3:** full peer-review ecosystem (sprint-scale)
- See `PLATFORM_CHANGES_LOG_TIER2_APPEND.md` "Future Evolution Notes — Peer Review" for full design conversation

### 5.2 M6 (Human Accountability) coverage check
- 0 patches in any Phase A tier
- Worth a coverage audit: which CG6.x.x / LO6.x.x indicators are PARTIAL?

### 5.3 M8 (Advanced Prompt Engineering) coverage check
- 0 patches in any Phase A tier
- Same audit needed for CG8.x.x / LO8.x.x

### 5.4 RAG selective ingest reserve
- M4 SVG 3 (Student-AI Control Spectrum) has coined term "Walled Garden" not present elsewhere in corpus — could ingest if visual-named queries fail
- Defer until retrieval gap surfaces

---

## 6. Critical institutional knowledge / gotchas

### 6.1 Spec-vs-reality drift
Spec authors sometimes wrote against an older module structure. **Always pre-flight verify**:
- Anchor existence + uniqueness
- Module Part headings (often renumbered after restructures)
- Whether referenced models / views / templates actually exist

Tier 2 caught 6 such mismatches before applying. Tier 3 will likely have a few more.

### 6.2 Generic TAB3 view handlers
`submit_challenge1/2/3` views accept ANY keys in POST JSON and store as `challenge<N>_<key>` in JSONB. No per-module view changes needed for new TAB3 fields. Just update the JS submit body.

### 6.3 Backward compatibility via JSONB + audit_version
When extending existing TAB3 fields, send `audit_version: 2` in submit body. Templates use Django `default:` filter to handle missing keys for legacy users. Avoids data migration.

### 6.4 weasyprint vs xhtml2pdf
- weasyprint is the cleaner HTML renderer, but Windows GTK runtime is missing in this dev env
- xhtml2pdf is the working fallback (pure Python, no system deps)
- For production deployment on Linux, weasyprint may be preferred — both libraries installed in venv
- See `templates/pdf/m13_canvas_export.html` for the template format that works with xhtml2pdf

### 6.5 The hidden Cycle 1 Q4 anchor mismatch
Tier 1 Cycle 1 SQL had wrong CSS class for M12 Designer's Cycle H3 anchor. Caught via anchor pre-audit. **Always audit before applying** — don't trust spec class strings without verification.

### 6.6 M15 Portfolio Builder is 4-column × 8-card mapping (NOT pick-one-tier)
The Tier 2 spec assumed Portfolio = "pick one of 4 transformation tiers". Reality = "map each of 8 artefact cards to one of 4 columns". Tier 5 (Training Module) was adapted as 5th OPTIONAL column gated by yes/no question, with soft-mandatory description textarea.

### 6.7 GitHub repo URL deviation
Spec said `proodos-eduai/teacher-workflows` (org). Real URL is `dourvas/proodos-eduai-teacher-workflows` (John's user account). `GITHUB_WORKFLOWS_URL` settings constant matches reality.

---

## 7. How to start Tier 3 cleanly

### Suggested opening prompt
> "Phase A Tier 3 starts. Read these in order:
> 1. `HANDOFF_TO_TIER3_SESSION.md` (this file) — full briefing
> 2. `PLATFORM_CHANGES_LOG_TIER2_APPEND.md` — depth on Tier 2 + peer review evolution notes
> 3. `CONTENT_GAPS_LOG_TIER2_UPDATE.md` — coverage state
> 4. [paste Tier 3 spec doc]
>
> Confirm you have full context, then:
> - Generate consolidated pre-flight covering all Tier 3 patches
> - Stop and report blockers / decisions needed
> - Wait for sign-off before any apply"

### First 3 actions for the new instance
1. **Verify environment is alive** — `psql` connect, `manage.py check`, `pip show xhtml2pdf weasyprint`
2. **Confirm latest backup** — `SELECT COUNT(*) FROM modules_modulecontent_backup_phase_a_tier2_may2026;` (should be 1258)
3. **Confirm RAG corpus baseline** — `SELECT COUNT(*) FROM document_chunks;` (should be 938)

If any of these don't match, something changed since 2026-05-02 — investigate before proceeding.

### Stop-and-report cadence (proven)
- After EVERY apply step → status report + browser test request → wait for sign-off
- Pre-flight all patches consolidated upfront → STOP for blocker discussion
- Every dry-run shown before apply → STOP for green light

---

## 8. Worktree contents

The worktree (`.claude/worktrees/keen-kepler-defc6c/`) contains all working scripts:
- `phase*_*_dryrun.py` / `phase*_*_apply.py` — DB transaction scripts
- `ingest_*_apr2026.py` / `ingest_phaseA_*.py` — RAG ingest scripts
- `verify_*.py` — RAG verification scripts
- `m4_svgs_preview.html` — preview file used in Tier 2 Step 3
- `m13_canvas_export_smoke.pdf` — sample PDF artefact
- `github_staging/teacher-workflows/` — local mirror of GitHub repo (already pushed)

Reference these as templates for Tier 3 scripts.

---

## 9. Closing reminders for the Tier 3 instance

1. **Trust the established patterns.** They've proven robust across 9 patches × 3 tiers.
2. **Always backup before first apply** — name the table `modules_modulecontent_backup_phase_a_tier3_may2026`.
3. **Anchor pre-audit is non-negotiable.** 4 mismatches in Cycle 1 v1 cost real time.
4. **Stop-and-report after each apply** — John has been engaged in every step verification.
5. **The 2 detailed log files contain the depth** — read them once for context, then refer back as needed.
6. **Test user reset is your friend** — see Tier 2 Step 4/5 for how to reset M13/M15 challenge state via SQL when re-testing.
7. **Greek + English mixed** in conversation is normal. UI is English. Comments may be Greek.
8. **John's review style** — direct, decision-fast, requires evidence (DB queries showing actual state, not assertions).

---

*Handoff prepared 2026-05-02. Good luck with Tier 3.*
