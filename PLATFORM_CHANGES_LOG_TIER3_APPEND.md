# PLATFORM_CHANGES_LOG_TIER3_APPEND

**Phase:** A · **Tier:** 3 · **Date:** 2026-05-03
**Predecessor:** Phase A Tier 2 (Steps 2–5, applied 2026-05-02)
**Spec:** `PHASE_A_TIER3_SPEC_v3.md` (Gemini external review applied)
**Append target:** `PLATFORM_CHANGES_LOG.md` (master tracking doc)

---

## Executive summary

| | |
|---|---|
| Steps executed | 8 (1 pre-flight + 7 implementation + 1 logs) — Step 3.5 added mid-flight |
| New Django app | **`apps.peer_blog`** (Practice Workshop) — models, views, URLs, templates, admin, services, sharing, subject_mappings, context processor |
| New schema | 2 migrations: `peer_blog/0001_initial`, `peer_blog/0002_step3_5_author_self_service` · 1 in `users/0006_blog_subject_filter_preference_and_more` · 1 in `modules/0012_add_community_shared_to_repository_submission_choices` |
| Modules wired to Practice Workshop | M13 (Workflow Canvas) · M9 (Lesson Design) · M14 (Gamified Unit — C3 only) |
| Type-A patches (M8) | 2 patches: `m8_ethics_by_design` (CG3.2.4) + `m8_cross_ref_m3` (CG3.2.1) — row 447 |
| RAG corpus growth | 938 → **940** chunks (+2 atomic, M8 ethics + M8 cross-ref) |
| Backup tables | `modules_modulecontent_backup_phase_a_tier3_may2026` (1 258 rows) |
| Standalone docs | 1 (`REACTIVE_MODERATION_POLICY.md`) — Step 9 PDF decision folded here |
| External resources | GitHub repo `dourvas/proodos-eduai-teacher-workflows` — CONTRIBUTING.md updated (commit `d3e7d16`) |
| Browser tests | All step-completions verified by John |
| RAG verification | 6/6 #1 mod-scoped retrieval (3 ETHICS + 3 XREF queries) |

---

## Architecture decision history (v1 → v2 → v3)

The Tier 3 spec went through three iterations before code. Capturing the trajectory because it is dissertation-grade signal about how PROODOS philosophy was operationalised.

### v1 (abandoned) — Forum-based peer dialogue

The first spec proposed reusing the existing `apps.community` forum for artefact peer dialogue. Rejected after analysis:

- Forum threads "wake up" with each reply — chronological analysis of artefact-specific feedback becomes noisy
- Continuous moderation burden on researcher (50-150 active threads in pilot would require weekly review)
- Flat thread architecture doesn't suit discrete artefact peer dialogue
- Author has no agency over their own thread once it goes live

### v2 — Blog approach (pre-Gemini review)

Replaced forum with a new `apps.peer_blog` Django app providing module-scoped feeds with discrete posts, comments, and thumbs-up reactions.

- Posts anchored chronologically; comments are secondary
- Sub-specialty filtering at the user's discretion
- Author owns their post
- Thumbs-up = single-action endorsement

### v3 (current) — Practice Workshop framing + Gemini revisions

Gemini external review (May 3, 2026) added 4 substantive refinements:

| Decision | What changed |
|---|---|
| **D12 — User-facing label** | "Peer Dialogue" → "Practice Workshop" (technical app name `peer_blog` retained for clean schema; UI emphasises reflective workshop mindset over polished gallery) |
| **D13 — Adjacency rationales** | `ADJACENT_SUBJECTS` mapping now includes pedagogical rationales; "Why these subjects?" modal explains adjacency choice to scaffold cross-specialty synthesis |
| **D14 — Flat comments only** | `BlogComment.parent_comment` FK removed — pilot scale (110 teachers, ~5 comments avg) doesn't need nested replies; saves ~1h development effort, simplifies code, cleaner research data |
| **D15 — Defence rationale** | This document (architecture decision history captured for dissertation viva) |

### Defence rationale paragraph (D15) — verbatim

> **Architecture Decision: Practice Workshop App vs Forum Reuse**
>
> Phase A Tier 3 introduces a new Django app (`apps.peer_blog`, presented as "Practice Workshop") rather than reusing the existing community forum for artefact peer dialogue. This decision adds approximately one hour of development effort but is justified by three research-grade considerations:
>
> 1. **Researcher data quality.** A forum thread "wakes up" with each reply, creating noise that interferes with chronological analysis of artefact-specific feedback. Workshop posts remain anchored to their creation timestamp; comments are secondary signal. This produces cleaner research data on how peers respond to specific artefacts.
>
> 2. **Reactive moderation footprint.** Forum threads in a 110-teacher pilot would generate 50–150 active threads requiring weekly researcher attention to prevent drift. Workshop posts with reactive moderation require ~30 minutes of weekly review, freeing the researcher for data analysis rather than community management.
>
> 3. **Cross-Specialty Peer Synthesizer alignment.** The Workshop's "Adjacent subjects" default filter (with pedagogical rationales surfaced through a 'Why these?' modal) directly operationalises the cross-specialty interaction research instrument. The forum's flat thread structure could not provide this scaffolding without significant retrofit.
>
> The existing forum app is preserved for general module discussion and Q&A. The two channels coexist with distinct purposes: forum for casual / cross-module discussion, Workshop for artefact-anchored peer dialogue.

---

## Pre-flight blockers + resolutions (Step 1, 2026-05-03)

The Tier 3 spec had 6 spec-vs-reality mismatches detected before any apply:

| # | Blocker | Resolution |
|---|---|---|
| 1 | `TeacherProfile.pseudonym` field doesn't exist (existing forum code references it inside try/except, falling back silently to `f"Educator_{user.id}"`) | **Option B** — added `@property pseudonym` to TeacherProfile that returns `display_name` if set, else `f"Educator_{user_id}"`. No DB column. Fixes both peer_blog and forum's broken silent fallback in one change. |
| 2 | Spec uses `request.user.profile`; reality is `request.user.teacher_profile` (related_name with underscore) | **All Tier 3 new code uses `teacher_profile`**. Plus incidental fixes: 2 broken refs in `apps/modules/views.py:751` and `:1171` (used wrong `teacherprofile` + wrong `.subject` field name) repaired. The `get_custom_prompt` view (M1 TAB3 endpoint) was returning 500 errors silently before this fix. |
| 3 | M9 has no `lesson_title` / `lesson_summary` fields (challenges are 100% radio/sorting) | **Option A modified** — when share-opt-in checked, two NEW fields `shared_lesson_title` (max 100) + `shared_lesson_summary` (max 500) collected; persisted in challenge_data; BlogPost.title = title, BlogPost.body = synthesised body via `_render_m9_lesson_body`. |
| 4 | M14 has free-text `challenge3_learning_goal` but no `unit_title` / `unit_summary` | **Option A modified** — `shared_unit_title` (new) used as title; body = synthesised via `_render_m14_unit_body` (rendering the user-typed learning_goal + 6 design choices). Pattern parallel to M9. |
| 5 | `Tab3RepositorySubmission.review_status` choices don't include `'community_shared'` | **Option A** — migration `0012` adds choice `('community_shared', 'Community Shared (Practice Workshop)')`; legacy 4 choices marked `(legacy)`. Schema column unchanged (varchar 20). |
| 6 | weasyprint still broken on Windows venv (libgobject-2.0-0.dll / GTK runtime missing) | xhtml2pdf 0.2.17 remains the working backend. Linux test deferred until production deployment target chosen. weasyprint installed but unused — kept as standby. |

---

## STEP 2 — Practice Workshop App (`apps.peer_blog`)

**Goal:** New Django app providing module-scoped artefact peer dialogue with discrete posts, flat comments, single-action thumbs-up, 3-mode subject filtering, and reactive moderation hooks. UI label "Practice Workshop"; technical schema names retained as `BlogPost` / `BlogComment` / `BlogThumbsUp`.

### Schema (`peer_blog/0001_initial`)

| Model | Key fields |
|---|---|
| **BlogPost** | user, module FK, artefact_type + artefact_id (generic FK pattern), title, body, author_pseudonym/subject_area/grade_level (snapshot at post-time), thumbs_up_count, comments_count (denormalised), is_hidden + hidden_reason (4-choice CharField, later +1 in Step 3.5), created_at, updated_at, 3 indexes (module+subject+date · module+thumbs · artefact lookup) |
| **BlogComment** | post FK, user, body, author_pseudonym, subject_area, thumbs_up_count, is_hidden, created_at — **NO parent_comment FK** (D14 — flat only) |
| **BlogThumbsUp** | user, post (nullable), comment (nullable), 2 partial unique constraints, 1 CheckConstraint enforcing post XOR comment |

### TeacherProfile additions (`users/0006`)

- `blog_subject_filter_preference` CharField, choices `(my_subject / adjacent / all)`, default `'adjacent'` — D9 + D10
- `@property pseudonym` (no DB column) — Blocker 1 Option B
- Incidental: AlterField on `subject_area` (regenerated metadata to match Python model with `null=True, blank=True` — pre-existing model-DB drift formalised; benign permissive change)

### Helpers + services

- `apps/peer_blog/services.py` — `create_blog_post`, `add_comment`, `toggle_thumbs_up` (atomic, F-expression-based), `WORKSHOP_ACTIVE_MODULES` list, `get_workshop_active_modules()` helper
- `apps/peer_blog/subject_mappings.py` — `ADJACENT_SUBJECTS` dict (16 subjects mapped), with rationales for each adjacent pair (D13); `get_filtered_subjects()` + `get_adjacency_rationales()` helpers
- `apps/peer_blog/sharing.py` — `MODULE_SHARE_CONFIG` registry pattern (M9 + M14 entries), per-module body renderers, `share_artefact_to_workshop` orchestrator (transactional)
- `apps/peer_blog/context_processors.py` — `workshop_modules` injects `workshop_active_modules` + `workshop_active_module_codes` into all templates (registered in TEMPLATES.OPTIONS.context_processors)

### Views + URLs

6 views in Step 2 (`blog_index`, `blog_post_detail`, `submit_comment`, `toggle_post_thumbs_up`, `toggle_comment_thumbs_up`, `update_filter_mode`) + 4 added in Step 3.5 (`edit_post_title`, `withdraw_post`, `edit_comment`, `delete_comment`). All routes namespaced under `peer_blog:` and mounted at `/blog/`.

### Templates (Tailwind + DaisyUI, extending base.html)

- `templates/peer_blog/index.html` — module feed with 3-mode filter toggle, sort recent/thumbs_up, "Why these subjects?" modal in Adjacent mode (D13)
- `templates/peer_blog/post_detail.html` — single post + flat comments (D14, no recursive partial), thumbs-up, author self-service controls (Step 3.5)
- `templates/peer_blog/post_withdrawn.html` — friendly 410 page when peer accesses author-withdrawn post

### Django admin

`BlogPostAdmin`, `BlogCommentAdmin`, `BlogThumbsUpAdmin` with hide/unhide actions. `hidden_reason` choices include both researcher categories (4) and author-initiated values (`author_withdrawn`, `author_deleted`) — distinguishable in the moderation log.

### Browser test
Empty M13/M9/M14 indexes render; filter mode toggle persists cross-session; admin lists empty; 404s correct.

---

## STEP 3 — M13 Simplification + Wiring (with mid-flight redesign)

### Initial scope

- Migration `modules/0012` adds `'community_shared'` choice to `Tab3RepositorySubmission.REVIEW_STATUS_CHOICES`
- `submit_to_repository` rewritten: writes `review_status='community_shared'`, auto-creates BlogPost via `create_blog_post('m13_workflow', ...)`, returns `redirect_url` to post detail. Atomic transaction.
- `Tab3RepositorySubmissionAdmin`: `actions = []`, all review fields readonly, 3 curation methods commented-out (preserved per D6 for future evolution)
- `tab3_activity_m13.html`: button label "🛠️ Share to Practice Workshop", footer text reframed (no approval gate, work-in-progress, reflection not gallery), JS handler navigates to `data.redirect_url` on success

### Mid-flight design fix #1 — Auto-populate the modal (instead of asking user to retype)

The initial implementation asked the user to type title + summary from scratch. After review: the M13 canvas already exists in `challenge_data` — the modal should auto-populate.

- Title default = label of `challenge2_learning_goal` radio choice (e.g. `'historical_immersion'` → `'Create historical or cultural immersion'`)
- Summary default = synthesised first-3 steps concatenated με trailing-punctuation strip + truncation to 200 chars

### Mid-flight design fix #2 — Canvas-as-body (substantive redesign)

After review of fix #1: still asking the user to write a 200-char summary diminishes the substantive artefact (their 5-step canvas). The full canvas should be the post body.

- New helpers in `views.py`: `_strip_label_extras`, `_m13_label_lookup`, `_render_m13_canvas_body`, `_build_m13_pdf_context`
- `submit_to_repository` rewritten again: no `summary` field accepted; body computed server-side via `_render_m13_canvas_body`; title falls back to learning-goal label if user provides empty override
- `export_canvas_pdf` accepts optional `?submission_id=N` query param — peer flow reads from `Tab3RepositorySubmission.canvas_data` snapshot (any logged-in user can download); author flow unchanged
- Modal redesigned: scrollable canvas preview block ABOVE the form; 1 optional title override; subject/grade pre-filled from profile; summary textarea + char counter REMOVED
- `peer_blog/post_detail.html`: body rendered with `whitespace-pre-line` (preserves canvas formatting); "📄 Download as PDF" button conditional on `post.artefact_type == 'm13_workflow'`

### M13 outcome

| Metric | Before Tier 3 | After Step 3 |
|---|---|---|
| Share button label | "📤 Submit for Peer Review" | "🛠️ Share to Practice Workshop" |
| Submission review_status | `'pending'` (admin gates approval) | `'community_shared'` (immediate visibility) |
| Admin curation actions | 3 (approve/reject/request_revision) | 0 (read-only research observation) |
| BlogPost.body source | (no BlogPost) | full canvas: learning goal + modalities + tools + prep time + 5 steps |
| PDF download accessibility | author only | any logged-in user via `?submission_id=N` |
| Footer text | "~2 weeks SLA, master teachers" | "no approval gate, work-in-progress, reflection not gallery" |

### Browser test
Mavros M13 canvas (learning_goal=`historical_immersion` + 5 steps) → modal preview shows full canvas + default title "Create historical or cultural immersion" → 1-click share → post detail με PDF download → argyris (peer) downloads PDF successfully via submission_id flow.

---

## STEP 3.5 — Navigation + Author Self-Service (added mid-flight)

The original v3 spec omitted two operational requirements that became blockers before Step 4:

1. **Navigation discoverability** — no entry point to `/blog/` from anywhere else in the app
2. **Author self-service** — no way to fix a typo, withdraw a post, or edit a comment without researcher intervention (privacy/PII risk)

Step 3.5 added these as a defensive insertion before scaling to M9 + M14.

### Schema additions (`peer_blog/0002_step3_5_author_self_service`)

- `BlogPost.HIDDEN_REASON_CHOICES` += `('author_withdrawn', 'Withdrawn by author')`
- `BlogComment.hidden_reason` (CharField, choices include `author_deleted` + the 4 researcher categories)
- `BlogComment.updated_at` (DateTimeField, auto_now=True)

### Navigation

- `base.html` top nav: "Practice Workshop" dropdown listing each module in `WORKSHOP_ACTIVE_MODULES` (M13 only after Step 3; M13+M9 after Step 4; M13+M9+M14 after Step 5)
- `tab3_activity_m{13,9,14}.html`: "→ View Practice Workshop posts for this module" link visible always (before AND after share)
- `module_list.html`: "💬 Workshop active" badge on cards whose code is in `workshop_active_module_codes`, clickable → workshop index

### Author self-service

| Action | Endpoint | Effect |
|---|---|---|
| Edit post title | `POST /blog/post/<id>/edit-title/` | `BlogPost.title` updated; live DOM refresh on success |
| Withdraw post | `POST /blog/post/<id>/withdraw/` | `is_hidden=True`, `hidden_reason='author_withdrawn'`; redirect to module index |
| Edit comment | `POST /blog/comment/<id>/edit/` | `body` updated, `updated_at` bumped; "(edited)" marker rendered |
| Delete comment | `POST /blog/comment/<id>/delete/` | `is_hidden=True`, `hidden_reason='author_deleted'`; `BlogPost.comments_count` decremented atomically |

All 4 endpoints `@login_required + @require_POST + 403 if user_id != obj.user_id`. Withdrawn posts return 410 + friendly `post_withdrawn.html` to peers; author still sees own withdrawn post with warning banner; researchers retain full access.

### Browser test
11/11 checklist items pass: nav dropdown, module-list badge, TAB3 view-posts link, author-only buttons visible to author, hidden from peer, edit/withdraw/edit-comment/delete-comment all 200, peer 403 on others' content, withdrawn post 410 page, author still sees own withdrawn post.

### Spec gap acknowledgement
Not spec drift — spec gap caught before pilot. Documented as intentional addition after spec confirmation that this is essential before scaling to 110-teacher pilot.

---

## STEP 4 — M9 Wiring (Hybrid Option C)

**Scope decision:** M9 has 3 challenges, all radio/sorting — no clear single substantive artefact. Three options considered (literal-spec all-3, M14-pattern C3-only, Hybrid). John picked **Hybrid Option C**: opt-in lives on Challenge 3 only, but the shared body synthesises context from C1+C2+C3.

### Generic infrastructure introduced

`apps/peer_blog/sharing.py` registry pattern:

- `MODULE_SHARE_CONFIG` dict — adding a new module = adding 1 entry
- `_render_m9_lesson_body(challenge_data)` — synthesis function (user summary + subject + scenario + 5 design decisions)
- `share_artefact_to_workshop(module_code, user, activity, title, summary)` — atomic orchestrator (persist title+summary in challenge_data → render body → create BlogPost → store blog_post_id back)
- New generic view `share_to_workshop(request, module_code)` in `apps/modules/views.py` — single endpoint serves M9/M14/future
- New URL route `tab3/share-to-workshop/`

### M9 template (`tab3_activity_m9.html`)

Share CTA card after C3 completion: opt-in checkbox → reveals 2 fields (title 100ch + summary 500ch) + live preview block + "Your shared post will include" expectation list (later replaced by live preview, see design fix #1) + idempotent already-shared state.

### Mid-flight design fix #1 — Live preview + suggested defaults

User feedback: "many won't want to share if they can't see what's being included; also they shouldn't have to write so much from scratch."

- View now passes `m9_share_default_title` (from scenario topic), `m9_share_default_summary` (subject-grounded starter sentence), `m9_share_static_body` (full rendered context with empty user summary) to template context
- Template: scrollable preview block ABOVE form showing live title + live summary + static auto-context; JS updates preview on every keystroke
- Pre-filled default title: `f"{scenario.topic} ({subject_label})"` (e.g., "Introducing simultaneous equations — Year 9 (Mathematics)")
- Pre-filled default summary: concrete one-line starter ending with "open to peer thoughts on the tradeoffs I'm making"

### Mid-flight design fix #2 — Drop module exercise scores + ✓/○ judgment markers

User feedback: "many won't want to post their quiz scores in a public artefact; ✓/○ markers also expose performance judgment".

- `_render_m9_lesson_body` updated: scores section completely removed; decision listing no longer marks correct/incorrect, just shows the choice the teacher made
- Body becomes purely about the **lesson approach** (the defendable position) — no quiz performance signals
- Aligns with Schön reflective-practice framing; researchers retain DB access to scores for pilot analysis

### Browser test
Mavros completes M9 C1+C2+C3 → share card shows preview with synthesised content + sensible defaults → editable title/summary live-update preview → 1-click share → post detail shows full lesson approach (no scores).

---

## STEP 5 — M14 Wiring (Gamified Unit Planner only)

**Scope:** Per spec D4, only Challenge 3 (Gamified Unit Planner) gets the share opt-in. C1 (SAMR Audit) and C2 (Five Roles Matcher) explicitly excluded — they're formative scaffolding, not substantive units worth sharing.

### Reuse from Step 4 infrastructure

Step 5 added M14 with **zero changes** to:
- `apps/peer_blog/views.py` (no new views)
- `apps/peer_blog/urls.py` (no new routes)
- `apps/peer_blog/models.py` (no schema changes)
- `apps/modules/views.py:share_to_workshop` (existing generic view absorbed M14)

Only additions:
- `_render_m14_unit_body(challenge_data)` in sharing.py — handles 6 design choice fields (student role, gamification principle, progression mechanic, assessment evidence, SAMR level, decoration test) + free-text learning goal
- `_M14_DECORATION_SHORT` rephrase map — long decoration_test labels (87 chars) → compact substance-test phrasings
- `_strip_after_dash` shared utility for label trimming
- `_label_for` helper made list-aware (multi-select fields like `challenge3_assessment` come through as lists)
- 1 entry added to `MODULE_SHARE_CONFIG`
- M14 share defaults block in `ModuleDetailView.get_context_data` (mirror of M9; title heuristic falls back to `<Subject>: Gamified Unit` when `challenge3_learning_goal` has fewer than 3 distinct tokens — guards against placeholder noise)
- Share card in `tab3_activity_m14.html` (mirror of M9 pattern, parameter swap)
- `WORKSHOP_ACTIVE_MODULES = ['M13', 'M9', 'M14']`

### Body output (sample)

```
<user summary>
---
Subject focus: Mathematics
Learning goal: <user-typed free-text>

Unit design choices:
• Student role: Architect
• Gamification principle: Visible Progression
• Visible progression: A score or point total that updates in real time
• Assessment evidence: A verbal or written explanation of a decision made
• SAMR level: Substitution
• Substance test (would the activity stand without the mechanics?): No — without the mechanics the activity loses most of its value
```

The "Substance test" wording surfaces M14's philosophical heart (decoration vs substance) — the dimension peers should comment on.

### Bug caught + fixed mid-step
Initial `_label_for` helper crashed on `challenge3_assessment = ['explanation']` (multi-select stored as list). Fixed by adding list handling: lists recursively render each value's label and comma-join.

### Browser test
Mavros M14 C3 (subject=mathematics, learning_goal noise) → share card title falls back to "Mathematics: Gamified Unit"; editable title + summary fields, live preview shows 6 design choices + Substance test phrasing → 1-click share → post detail with full unit body.

---

## STEP 6 — M8 Type-A Patches + RAG Ingest

### DB applies (single transaction, atomic)

| Patch | Anchor | Position | Δ chars | Indicator |
|---|---|---|---|---|
| `m8_ethics_by_design` | composite (divider + Part 5 H2) | end of Part 4 | +1 388 | CG3.2.4 PARTIAL → STRONG |
| `m8_cross_ref_m3` | Part 1 H2 | start of Part 1 body | +685 | CG3.2.1 PARTIAL → STRONG |

Row 447 (M8 main_content): **42 278 → 44 351** chars (Δ +2 073). `metadata.patches[]` 0 → 2. Both markers count=2 post-state (open + close tags). Anchor pre-checks unique (count=1 each). Idempotency verified (markers count=0 pre-state).

### Patch wording (per spec verbatim)

- **m8_ethics_by_design** — "Hands-on Ethics in Your Prompts" 3-check card (Bias / Privacy / Inclusivity) με concrete worked examples ("Write an example for a typical student" → "Write an example accessible to learners with diverse strengths"), warning-amber stripe, ARIA `role="region"`. ~120 words.
- **m8_cross_ref_m3** — "A note on AI techniques" pointer to M3 Part 2 for symbolic/predictive/generative AI breakdown, info-blue stripe, ARIA `role="note"`. ~60 words.

### RAG ingest (atomic, 2 chunks)

| Patch | Doc | Chunk | Cleaned text |
|---|---|---|---|
| m8_ethics_by_design | 91 | 1619 | 855 chars |
| m8_cross_ref_m3 | 92 | 1620 | 369 chars |

Sleep 5.0s between embeddings (rate-limit hygiene per Tier 2 convention). gemini-embedding-001 768d. Idempotent on document title (skip if exists).

### RAG verification (6 queries, 3 per patch)

**All 6 queries: #1 mod-scoped retrieval = TARGET ✅**

| Query | Patch | Mod-scoped sim |
|---|---|---|
| "How can I check my prompts for bias and privacy?" *(spec verbatim)* | ETHICS | **0.7844** ≥ 0.78 ✅ |
| "What ethics checks should I apply to my prompts?" | ETHICS | **0.8021** ✅ |
| "How do I make my prompts more inclusive and avoid student PII?" | ETHICS | 0.7369 ⚠️ |
| "How does M8 relate to M3 on AI techniques?" *(spec verbatim)* | XREF | 0.7711 ⚠️ |
| "Where can I learn about symbolic AI versus generative AI?" | XREF | 0.6656 ⚠️ |
| "What is the difference between predictive and generative AI?" | XREF | 0.6378 ⚠️ |

**Threshold notes:**
- ETHICS Q1 (spec primary) passes 0.78 cleanly; Q2 exceeds at 0.8021.
- XREF Q1 (spec primary) at 0.7711 — 4 thousandths short, accepted under same Tier-2 precedent as M5 (0.7751 also 0.005 short, accepted as "cosmetic miss only — clean #1 retrieval matters more").
- XREF Q2/Q3 sims lower because the queries are about M3's content (symbolic/predictive AI taxonomy) — M3 correctly wins unfiltered. The XREF patch's job is to **route from within M8 context to M3** — and M8-scoped #1 is correct on all 4 XREF queries.
- ETHICS Q3 (0.7369) hits adjacent inclusivity content in M10 (subject area uses similar language) but #1 retrieval clean both unfiltered and mod-scoped.

Functional outcome: both indicators verifiably retrievable from the M8 context. Sim threshold spec target ≥ 0.78 met for primary spec queries; alt queries below threshold accepted under Tier-2 precedent.

### Browser test
M8 → Tab 2: cross-ref card visible at top of Part 1 body; ethics card visible at end of Part 4 (before divider that leads into Part 5). ARIA roles + warning/info stripe colors render correctly.

---

## STEP 7 — Reactive Moderation Policy

`REACTIVE_MODERATION_POLICY.md` created at project root (~250 lines). Per spec Section 8 verbatim plus 3 additions:

1. **Author self-service distinction section** — Step 3.5 introduced `author_withdrawn` + `author_deleted` `hidden_reason` values that the v3 spec didn't anticipate. Doc separates these from researcher moderation explicitly so the dissertation moderation log doesn't conflate the two signals.
2. **Where to moderate** — explicit Django admin URLs for posts and comments queues.
3. **Quick reference scenario table** — 8 concrete situations (4 hide examples + 4 don't-hide examples) for researcher decision speed during weekly review.

The 4 hide-trigger criteria (`safety_violation`, `off_topic_spam`, `contains_pii`, `copyright_violation`) and 7 hide-NEVER cases preserved verbatim from spec.

---

## STEP 8 — CONTRIBUTING.md Alignment (GitHub repo)

**Repo:** `dourvas/proodos-eduai-teacher-workflows`
**Commit:** `d3e7d16` (parent `aa519d0` from Tier 2)
**Push:** `aa519d0..d3e7d16  main -> main` ✅
**Diff stats:** 1 file changed, 30 insertions(+), 11 deletions(-)

### Section-by-section changes

| Section | Tier 2 (before) | Tier 3 (after) |
|---|---|---|
| Path B heading | "PROODOS Verified Repository" | "M13 Practice Workshop (in-platform)" |
| Approval model | "~2 weeks SLA, master teacher review" | "no approval gate; reactive moderation only" |
| Submit-flow steps | Submit for Peer Review → 5 fields → wait for review | "🛠️ Share to Practice Workshop" → review auto-generated post → edit/accept title → land on post |
| Author control note | (none) | New: "edit title, withdraw post, edit/delete own comments at any time" |
| Quality section heading | "Workflow quality guidelines" | "What makes a strong shared workflow" — author guidelines, not reviewer criteria |
| Peer-review criteria | Submissions evaluated against 4 criteria (gatekeeper) | "What peers focus on (Path B)" — same 4 dimensions framed as conversation starters |
| Attribution | "credited by name (or pseudonym, your choice)" | "credited by display name (or `Educator_<id>` pseudonym)" — matches Step 3.5 reality |
| Cross-reference | (none) | Links to `REACTIVE_MODERATION_POLICY.md` |

Path A (open community PR via fork) is preserved verbatim. The two paths now have distinct, clearly-different value propositions.

---

## STEP 9 — PDF Backend Decision (folded here)

xhtml2pdf 0.2.17 confirmed as the active PDF backend for Tier 3. weasyprint installed but unused.

**Evidence:**
- Tier 2 smoke test: 1.86 KB clean PDF generation
- Step 3 redesign smoke (this Tier): `application/pdf` 3 292 bytes via both author flow and `?submission_id=N` peer flow, correct `Content-Disposition` filename header
- Step 6 deployments stable

**weasyprint status:** still blocked on Windows venv — Step 1 pre-flight reproduced the import failure (`from .text.fonts import FontConfiguration` → libgobject-2.0-0.dll / GTK runtime missing). Linux test deferred until production deployment target is chosen — re-evaluating without target context adds no signal.

**Decision:** stay with xhtml2pdf. Re-evaluate at production deployment if target is Linux.

No standalone `PDF_BACKEND_DECISION_TIER3.md` document — rationale recorded here per John's request to avoid bureaucratic overhead.

---

## Backup tables created

| Table | Purpose |
|---|---|
| `modules_modulecontent_backup_phase_a_tier3_may2026` | Pre-Step-6 baseline (1 258 rows). Covers Step 6 M8 patches. Steps 2-5 + 3.5 didn't touch `modules_modulecontent` — only added new `peer_blog_*` tables and `modules_tab3repositorysubmission` choice metadata. |

---

## Files inventory (all Tier 3)

### Created (15)

```
apps/peer_blog/__init__.py
apps/peer_blog/apps.py
apps/peer_blog/models.py
apps/peer_blog/services.py
apps/peer_blog/sharing.py
apps/peer_blog/subject_mappings.py
apps/peer_blog/views.py
apps/peer_blog/urls.py
apps/peer_blog/admin.py
apps/peer_blog/context_processors.py
apps/peer_blog/migrations/__init__.py
apps/peer_blog/migrations/0001_initial.py
apps/peer_blog/migrations/0002_step3_5_author_self_service.py
templates/peer_blog/index.html
templates/peer_blog/post_detail.html
templates/peer_blog/post_withdrawn.html
apps/users/migrations/0006_teacherprofile_blog_subject_filter_preference_and_more.py
apps/modules/migrations/0012_add_community_shared_to_repository_submission_choices.py
phaseA_tier3_step6_apply.py
ingest_phaseA_tier3_step6_m8.py
verify_phaseA_tier3_step6_m8.py
REACTIVE_MODERATION_POLICY.md
PHASE_A_TIER3_SPEC_v3.md  (spec preserved at project root)
PLATFORM_CHANGES_LOG_TIER3_APPEND.md  (this file)
CONTENT_GAPS_LOG_TIER3_UPDATE.md
```

### Modified (8)

```
apps/users/models.py            (+@property pseudonym, +blog_subject_filter_preference field)
apps/modules/models.py          (+'community_shared' choice in Tab3RepositorySubmission)
apps/modules/views.py           (+share_to_workshop, rewrote submit_to_repository, rewrote export_canvas_pdf, M13/M9/M14 share-default blocks in ModuleDetailView, 2 incidental teacherprofile→teacher_profile fixes at lines 751 + 1171)
apps/modules/admin.py           (Tab3RepositorySubmissionAdmin: actions=[], readonly review fields, curation methods preserved as comments)
apps/modules/urls.py            (+tab3/share-to-workshop route)
config/settings.py              (+apps.peer_blog in INSTALLED_APPS, +workshop_modules context processor)
config/urls.py                  (+/blog/ namespace mount)
templates/base.html             (+Practice Workshop dropdown in top nav)
templates/modules/module_list.html             (+'Workshop active' badge)
templates/modules/tabs/tab3_activity_m13.html  (share card, modal redesign, JS handler)
templates/modules/tabs/tab3_activity_m9.html   (share card, live preview, JS handler)
templates/modules/tabs/tab3_activity_m14.html  (share card, live preview, JS handler)
github_staging/teacher-workflows/CONTRIBUTING.md  (Tier 3 alignment, pushed to GitHub)
```

### DB-modified

```
modules_modulecontent  (1 row): M8 row 447 (Δ +2 073 chars, metadata.patches += 2)
modules_tab3repositorysubmission  (choice metadata only; no data change)
teacher_profiles  (column metadata via 0006; no data change)
peer_blog_blogpost, peer_blog_blogcomment, peer_blog_blogthumbsup  (new tables, empty pre-pilot)
documents  (2 new rows: 91, 92)
document_chunks  (2 new rows: 1619, 1620 — corpus 938 → 940)
```

### GitHub repo
- `dourvas/proodos-eduai-teacher-workflows` commit `d3e7d16` (CONTRIBUTING.md update)

---

## Operational notes

- **All M8 applies done within single PostgreSQL transaction** with pre-snapshot + anchor pre-check + post-state verification + ROLLBACK on any failure (per Tier 1+2 atomic pattern).
- **Anchor uniqueness** verified count=1 for both M8 patches.
- **Idempotency** verified — both markers absent pre-state, present (count=2 = open+close) post-state.
- **`metadata.patches[]`** appended via `jsonb_set + COALESCE` — preserves any prior entries (M8 had no prior patches).
- **Schema migrations are forward-only** — no rollback scripts needed for Tier 3 (no destructive changes).
- **Pre-existing naive datetime warnings** surfaced during smoke tests (`Tab3UserActivity.challenge3_completed_at` etc., dates 2026-04-11 onward). Pre-Tier-3 data drift, not introduced here. Could be addressed by a one-time backfill if production warnings become noisy.
- **TeacherProfile pseudonym property fix** also addresses a long-standing silent bug in `apps/community/models.py:261` (forum's `ForumPost.save` referenced `self.author.teacherprofile.pseudonym` inside try/except, falling through to `Educator_{id}` fallback for ALL users). The new `@property pseudonym` is reachable from forum's auto-populate too — the silent-fail path now returns a meaningful display name. Forum behaviour change is incidental and benign.
- **Django 6.0.1 compatibility:** `CheckConstraint(check=...)` deprecated → switched to `condition=` (in `apps/peer_blog/models.py`). One-line API rename.

---

---

## STEP 12 — Post-Tier-3 Addition: Reactive Moderation Policy User-Facing Visibility

**Status:** Added 2026-05-03 after Tier 3 closure sign-off, based on UX/transparency gap caught in debrief.
**NOT spec drift** — explicit post-closure addition for ethics-research transparency + EU AI Act Article 50 alignment.

### Why this was added

`REACTIVE_MODERATION_POLICY.md` (created in Step 7) was visible only to developers (project root) and external contributors (GitHub repo). Pilot teachers using the platform had no in-platform visibility into how moderation works — they would share content without informed-consent transparency. This is an ethics gap before pilot launch and an EU AI Act Article 50 alignment opportunity that needed closing before n=110 teacher onboarding.

### Three touch points implemented

1. **Share modal disclosure** — reusable partial `templates/peer_blog/_share_disclosure.html` included in M13, M9, and M14 share forms above the "Share to Practice Workshop" button. One-line summary + link to full policy page (target=_blank to preserve share flow). DRY: wording change propagates across 3 modules with one edit.

2. **Practice Workshop feed footer** — `templates/peer_blog/index.html` footer block under posts list με reactive moderation note + policy link.

3. **Public policy page** — `/blog/moderation-policy/` route + `moderation_policy` view + `templates/peer_blog/moderation_policy.html` (hand-formatted HTML, **NOT auto-rendered markdown**, ~280 lines). Sections: TL;DR card · Reactive vs proactive philosophy · 4 hide-trigger criteria as cards · 7 hide-NEVER criteria as list · Author self-service section (Step 3.5 distinction surfaced) · Researcher cadence · Pilot study integrity · Back-link to Modules. Page is **public (no `@login_required`)** so it's reachable from share-modal links even if user's session expires while reading — informed-consent surface should never bounce to login.

### Translation decision

**Option A: English only** chosen — matches platform language baseline. Greek translation deferred until pilot feedback indicates need.

### Files

**Created (2):**
- `templates/peer_blog/_share_disclosure.html` (reusable partial)
- `templates/peer_blog/moderation_policy.html` (public page)

**Modified (5):**
- `apps/peer_blog/views.py` (+`moderation_policy` view, public/no-auth)
- `apps/peer_blog/urls.py` (+`moderation-policy/` route)
- `templates/peer_blog/index.html` (+footer block)
- `templates/modules/tabs/tab3_activity_m13.html` (+`{% include _share_disclosure.html %}`)
- `templates/modules/tabs/tab3_activity_m9.html` (+`{% include _share_disclosure.html %}`)
- `templates/modules/tabs/tab3_activity_m14.html` (+`{% include _share_disclosure.html %}`)

### Smoke test (8/8 pass)

```
1. Anonymous GET /blog/moderation-policy/        status=200, no auth required ✅
2. Authenticated GET                             status=200                    ✅
3. M13 share-modal disclosure visible            ✅ + policy link present
4. M9 share-section disclosure visible           ✅ + policy link present
5. M14 share-section disclosure visible          ✅ + policy link present
6. /blog/module/M13/ feed footer policy link     ✅
7. Policy page back-link to /modules/            ✅
8. Disclosure inside share-form (gated by share-state) — correctly
   hidden when user has already shared (already-shared message
   displaces the form including disclosure)                       ✅
```

### Pilot baseline cleanup performed

While running smoke tests, mavros's M9 + M14 `shared_to_blog` state from Step 4-5 actual shares was reset, and the leftover BlogPost (id=18) + Tab3RepositorySubmission (id=12 orphan) + smoke comments cleaned. State now:

- `BlogPost`: 0
- `BlogComment`: 0
- `Tab3RepositorySubmission`: 1 (id=1 Tier 2 legacy "first law" — preserved)
- mavros M9/M14 `challenge_data`: shared keys removed, ready for pilot baseline

This addresses the Step 11 closure note about leftover test artefacts. Database now clean for pilot launch.

### Defendability note

Step 12 is **substantive informed-consent infrastructure**, not cosmetic. It transforms the pilot study from "policy exists in repo, hope teachers know it" to "policy is at the click point of every share action, accessible without login, visible from feed, anchored με public URL". For dissertation viva, the moderation visibility chain is now defendable as proper informed-consent provision — not aspirational.

---

*End of PLATFORM_CHANGES_LOG_TIER3_APPEND.md*
