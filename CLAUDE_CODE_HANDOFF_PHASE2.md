# Claude Code Handoff: Subject Intro Hooks — Phase 2 (Backend)

## Context

You are working on the PROODOS EduAI platform — a Django-based teacher PD platform. The project root is `unesco_pd`. This is doctoral research. The platform has 15 modules (M1–M15) aligned to the UNESCO AI Competency Framework for Teachers.

We are implementing a new feature called **Subject Intro Hooks** — small discipline-specific cards that appear in TAB1 (the introduction tab) of each module. The cards reduce subject-related resistance before teachers reach the main content. Each card is personalised to the user's `subject_area` from their `TeacherProfile`.

A complete architecture spec exists at `SUBJECT_INTRO_HOOKS_PATCH_APR2026.md`. **Read this file first before doing anything else.** Everything in it is authoritative.

## Your task: Phase 2 only

Phase 2 is backend code only. **No content writing, no SQL data INSERTs.** Those come in later phases. Your job is to build the rails so that when SQL data arrives later, it just works.

### Three deliverables

1. **New view** `subject_intro_view` in `apps/modules/views.py`
2. **New URL pattern** in `apps/modules/urls.py`
3. **New template partial** at `templates/modules/partials/subject_intro_card.html`, included in the existing `tab_introduction.html`

### Acceptance criteria

When you finish, the following must be true:

- A GET request to `/modules/modules/<code>/subject-intro/` returns JSON with shape `{success: bool, html: str, subject: str}` for any logged-in user with a `TeacherProfile`
- The view filters `ModuleContent` by `content_type='subject_intro'`, the user's `subject_area`, and `grade_level='all'`
- If no subject-specific record exists, the view falls back to `subject_area='Universal'`
- If neither exists, the view returns `{success: False}` with a sensible message
- The TAB1 page includes the new partial directly below the "About this module" card and above the forum trigger
- The partial fetches the JSON via AJAX on page load and renders the HTML, or hides itself silently on failure
- No existing functionality breaks. M1–M15 TAB1 still loads. M2–M15 TAB2/3/4/5 still work.
- Tests pass (if a test suite exists). If none exists, do not create one — note the gap in your summary.

### Patterns to follow

The architecture mirrors the existing `thread_info` AJAX pattern used by the forum trigger card. Find it in the codebase and copy its style for:

- View decorators and error handling
- URL parameter naming (`code` not `module_code` for AJAX endpoints)
- JSON response shape
- Template loading pattern (fetch + innerHTML)
- Silent failure (hide card if no data, never show error to user)

### What to NOT touch

- Do not modify any existing view function
- Do not modify any existing URL pattern
- Do not modify any existing template except `tab_introduction.html` (one include line)
- Do not run database migrations — no schema changes are needed, only new rows in existing table
- Do not write SQL INSERTs — content is a separate phase
- Do not modify RAG ingest scripts — `subject_intro` is explicitly excluded from RAG
- Do not modify settings, requirements, or dependencies
- Do not refactor existing code, even if you see something improvable

### Before you start

Run these checks and report back:

1. `git status` — is the repo clean? If not, stop and ask the user.
2. `git log --oneline -5` — what's the latest commit?
3. Does `apps/modules/views.py` exist? (It should)
4. Does `apps/modules/urls.py` exist? (It should)
5. Does `templates/modules/partials/` exist? (It should)
6. Does `templates/modules/tab_introduction.html` exist? Find the exact location of the "About this module" card include or block — the new card goes right below it.
7. Find the `thread_info` view and the URL pattern. Confirm the AJAX pattern matches what's described in the spec (Section 4 of the patch document).

If any of these checks fail or surprise you, **stop and report**. Do not proceed.

### After you finish

Report back:

1. Files modified (list)
2. Files created (list)
3. Any deviations from the spec (and why)
4. How you tested it (manual GET request, browser load, Django shell, etc.)
5. Any issues or open questions
6. A suggested git commit message

Do NOT commit yet. The user will review and commit themselves.

### Reference reading order

1. `SUBJECT_INTRO_HOOKS_PATCH_APR2026.md` — full spec (read sections 2, 3, 4 carefully)
2. `MODULE_CONTENT_GUIDE.md` — context on `modules_modulecontent` table conventions
3. `FORUM_THREAD_INFO_GUIDE.md` — the AJAX pattern to mimic
4. The existing `thread_info` view and template partial — the canonical example

### One thing to remember

This is doctoral research. The codebase serves a real pilot of ~110 teachers. Conservative changes only. When in doubt, ask.

---

End of handoff.
