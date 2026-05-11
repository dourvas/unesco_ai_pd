# PROODOS Epilogue — Implementation Notes (C.2.5 placeholder)

**Date:** 2026-05-11
**Scope:** What was built for the PROODOS Epilogue feature in Phase C C.2.5. This is a **placeholder** implementation that unblocks the post-M15 → T2 routing chain during the pilot. The full Epilogue (Stage 0 Personal Evolution Dashboard, Stages 1-3 Gemini dialogue, Learning Portrait PDF) is tracked as TD-011 in `proodos_files/TECH_DEBT_LOG.md`.
**Companion docs:**
- `M16_CAPSTONE_REFLECTION_SPEC.md` (March 2026) — original pedagogical + technical spec
- *PROODOS Epilogue — Patch Notes (April 2026)* — renaming + Stage 0 Dashboard insertion + architectural separation from modules (supplied by John during the C.2.5 design dialogue; should be filed alongside this doc once received as a file)
- `SESSION_LOG_PHASE_C_C23_C25_20260511.md` — session-level log covering C.2.3 + C.2.4 + C.2.5

---

## 1. Background

The Epilogue is a **methodologically distinct post-completion feature** that synthesises the research corpus generated across M1-M15. It is **not** a 16th module:

- Database code is `EPILOGUE`, not `M16`.
- Lives in a separate Django app (`apps/epilogue/`), not in `apps/modules/`.
- Has its own model, table, URL namespace, and tests.
- Is not assessed; does not count towards the UNESCO 15-module framework.

The April 2026 patch notes resolved two design pivots that drove this implementation:

1. **Renaming** from "M16 Capstone" to "PROODOS Epilogue" — the name "M16" misled because the UNESCO framework has 15 levels and the feature adds synthesis-and-dialogue, not new content.
2. **Stage 0 Personal Evolution Dashboard** inserted in front of the three dialogue stages — live DTP curve + RTM tensions, no input required, the "breath" before the dialogue.

The research-design reason this matters for the pilot: **T2 must capture post-synthesis attitudes, not post-M15-content attitudes**. The Epilogue sits between M15 and T2, so T2 measures the educator after they have looked back across their trajectory, not immediately after the last content module.

---

## 2. Design decisions (C.2.5)

Finalised in chat between Claude and John, 10 May 2026.

| # | Decision | Choice |
|---|---|---|
| **D1** | New app `apps/epilogue/` or feature inside existing app | New app — respects the spec "separate entity" position |
| **D2** | DB tracking via new model or session-only flag | New model `EpilogueCompletion` — research-grade audit trail, parallels `AilstResponse` lifecycle |
| **D3** | Schema scope now (lifecycle only) vs. full stages 0-3 fields | Lifecycle only (started_at / completed_at). Stages 0-3 + dialogue turns + Learning Portrait deferred to TD-011 |
| **D4** | Consent gating on the Epilogue itself | **No** — pedagogical feature, not research instrument. All users see it. The T2 hop downstream remains consent-gated. |
| **D5** | Helper structure for modules → next-feature routing | Two helpers (one in `apps/ailst/services.py`, one in `apps/epilogue/services.py`). Modules view calls both in turn. |
| **D6** | URL prefix | `/epilogue/` (shorter than `/proodos-epilogue/`) |
| **D7** | Placeholder copy on the page | Quotes the patch notes verbatim where possible; explicit "Feature under construction" alert |
| **D8** | Tech debt entry for full implementation | Yes — `TD-011`, post-pilot Phase G/H |
| **D9** | Migration safety | Additive only (new table, no touch on existing data). Standard pg_dump backup before apply. |
| **D10** | Commit organisation | Single commit (~370 LOC). New app + migration + views + tests + modules wiring + service helper rename + plan/TD updates land atomically. |

---

## 3. Files created

| File | Purpose | LOC |
|---|---|---|
| `apps/epilogue/__init__.py` | Empty package marker | 0 |
| `apps/epilogue/apps.py` | `EpilogueConfig` (verbose_name "PROODOS Epilogue") | 6 |
| `apps/epilogue/models.py` | `EpilogueCompletion` model | 70 |
| `apps/epilogue/views.py` | `epilogue_placeholder_view` + `epilogue_complete_view` + `_post_epilogue_destination` helper | 92 |
| `apps/epilogue/urls.py` | URL namespace `epilogue:` + 2 routes | 13 |
| `apps/epilogue/services.py` | Cross-app helper `get_post_module_epilogue_redirect_url` + `POST_MODULE_NEXT_FEATURE` mapping | 51 |
| `apps/epilogue/tests.py` | 12 tests across placeholder/complete views and the routing helper | 143 |
| `apps/epilogue/migrations/__init__.py` | Empty package marker | 0 |
| `apps/epilogue/migrations/0001_initial.py` | Django-generated migration for `epilogue_completions` | 32 |
| `templates/epilogue/placeholder.html` | Placeholder page extending `base.html`, DaisyUI + i18n stubs | 75 |
| **Total new** | | **~482** |

## 4. Files modified

| File | Change | LOC |
|---|---|---|
| `config/settings.py` | Added `'apps.epilogue'` to `INSTALLED_APPS` | +2 |
| `config/urls.py` | Added `path('epilogue/', include('apps.epilogue.urls', namespace='epilogue'))` | +3 |
| `apps/ailst/services.py` | Removed M15 from `POST_MODULE_AILST_TIMEPOINT`; added explanatory comment | +13 / -6 |
| `apps/modules/views.py` | Dual-helper call after `mark_tab_complete`; new `ailst_redirect_label` key in JSON response | +21 / -7 |
| `apps/modules/tests.py` | M15 test now asserts redirect to `/epilogue/` (not `/ailst/t2/`); label assertions added to M5 + M15 tests | +18 / -3 |
| `templates/modules/tabs/tab5_reflection.html` | Reflection JS reads `ailst_redirect_label` for the rewired "Reflection Completed" button | +2 / -1 |
| `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` | C.2.5 changelog entry | +2 |
| `proodos_files/TECH_DEBT_LOG.md` | TD-011 entry for full Epilogue implementation | +37 |
| **Total modified** | | **+98 / -17** |

---

## 5. Database

### New table `epilogue_completions`

```sql
CREATE TABLE "epilogue_completions" (
    "id" bigint NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    "started_at" timestamp with time zone NOT NULL,
    "completed_at" timestamp with time zone NULL,
    "user_id" integer NOT NULL UNIQUE
);

ALTER TABLE "epilogue_completions"
    ADD CONSTRAINT "epilogue_completions_user_id_a165edf9_fk_auth_user_id"
    FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id")
    DEFERRABLE INITIALLY DEFERRED;
```

Schema characteristics:

- **OneToOne** with `auth_user` (UNIQUE constraint on `user_id`). One row per user, period — the Epilogue is one-shot at the data-model level.
- **`started_at`**: timezone-aware, auto-set on row creation (Django `auto_now_add=True`).
- **`completed_at`**: nullable; set when the user clicks "Mark complete and continue" on the placeholder. NULL means "started but not yet completed".
- **CASCADE on auth_user delete**: when a user is deleted (right-to-erasure), their Epilogue row is removed too. Consistent with the existing `AilstResponse` cascade policy.

### Migration

`apps/epilogue/migrations/0001_initial.py` — Django-generated, additive only. Applied 2026-05-11 with pre-apply backup `pre_migration_backup_phaseC_C25_20260511.sql` (49 MB, at repo root).

### Lifecycle states

```
no row              → user has never visited /epilogue/
row, completed_at NULL  → user landed on /epilogue/ at least once but has
                          not yet clicked "Mark complete and continue"
row, completed_at set   → user has completed the Epilogue placeholder
                          and (if eligible) has been forwarded to /ailst/t2/
```

The state machine is observable directly via a single column lookup:

```sql
SELECT user_id, started_at, completed_at,
       CASE
           WHEN completed_at IS NOT NULL THEN 'completed'
           ELSE 'in_progress'
       END AS state
FROM epilogue_completions
ORDER BY started_at DESC;
```

---

## 6. URL routing

Mounted at `/epilogue/` (see `config/urls.py`):

| Method + Path | View | Name | Purpose |
|---|---|---|---|
| GET `/epilogue/` | `epilogue_placeholder_view` | `epilogue:placeholder` | Renders the placeholder. `get_or_create`s the `EpilogueCompletion` row so `started_at` is captured. |
| POST `/epilogue/complete/` | `epilogue_complete_view` | `epilogue:complete` | Flips `completed_at = NOW()` (idempotent) and redirects forward to `/ailst/t2/` or `/dashboard/`. |

GET to `/epilogue/complete/` returns 405 (the view is `@require_POST`).

---

## 7. View behaviour

### `epilogue_placeholder_view`

```python
@login_required
def epilogue_placeholder_view(request):
    EpilogueCompletion.objects.get_or_create(user=request.user)
    completion = EpilogueCompletion.objects.get(user=request.user)
    return render(request, 'epilogue/placeholder.html', {
        'completion': completion,
        'already_completed': completion.completed_at is not None,
    })
```

- Idempotent on revisits — `get_or_create` ensures a row exists, never duplicates.
- Template branches on `already_completed`:
  - **Not yet completed**: shows "Mark complete and continue" button.
  - **Already completed**: shows success alert "You reached the Epilogue on …" + "Continue" button.

### `epilogue_complete_view`

```python
@login_required
@require_POST
def epilogue_complete_view(request):
    with transaction.atomic():
        completion, _ = EpilogueCompletion.objects.select_for_update().get_or_create(
            user=request.user,
        )
        if completion.completed_at is None:
            completion.completed_at = timezone.now()
            completion.save(update_fields=['completed_at'])
    return redirect(_post_epilogue_destination(request.user))
```

- `select_for_update` inside `transaction.atomic` to guard against double-click / parallel-tab races.
- **Idempotent**: a second POST after the row is already completed does NOT move `completed_at` forward — only the first POST flips it. The user still gets routed forward on subsequent POSTs.

### `_post_epilogue_destination` (helper)

```python
def _post_epilogue_destination(user):
    profile = getattr(user, 'teacher_profile', None)
    if profile is None or not profile.research_consent:
        return '/dashboard/'
    t2_completed = AilstResponse.objects.filter(
        user=user, timepoint='T2', completed_at__isnull=False,
    ).exists()
    if t2_completed:
        return '/dashboard/'
    return '/ailst/t2/'
```

- Mirrors the AILST gating philosophy: T2 is reachable only by research-consenting users who have not already completed it.
- The AILST entry view also enforces consent gating; this check exists to avoid the unnecessary redirect hop for non-consenting / already-done users.

---

## 8. Frontend integration

The Epilogue interacts with the modules layer via the existing `mark_tab_complete` AJAX response shape. C.2.4 introduced an `ailst_redirect_url` JSON key for the M5 → T1 redirect; C.2.5 re-uses it for the M15 → /epilogue/ redirect and adds a complementary `ailst_redirect_label` key so the user-visible button text matches the destination.

### Server-side (in `apps/modules/views.py::mark_tab_complete`)

```python
ailst_redirect_url = get_post_module_redirect_url(request.user, module.code)
epilogue_redirect_url = get_post_module_epilogue_redirect_url(request.user, module.code)

if ailst_redirect_url:
    response_data['ailst_redirect_url'] = ailst_redirect_url
    response_data['ailst_redirect_label'] = 'Continue to AI Literacy assessment'
elif epilogue_redirect_url:
    response_data['ailst_redirect_url'] = epilogue_redirect_url
    response_data['ailst_redirect_label'] = 'Continue to PROODOS Epilogue'
```

Both helpers are called every time but only one of them returns a non-None URL for any given module code (`M5` is in the AILST mapping, `M15` is in the Epilogue mapping, all others return None).

### Client-side (in `templates/modules/tabs/tab5_reflection.html`)

```js
if (result.ailst_redirect_url) {
    const label = result.ailst_redirect_label || 'Continue';
    document.querySelectorAll('[data-reflection-continue]').forEach(btn => {
        btn.textContent = label;
        btn.onclick = () => { window.location.href = result.ailst_redirect_url; };
    });
}
```

- The label has a defensive default (`'Continue'`) so an older server that returns `ailst_redirect_url` without `ailst_redirect_label` still produces a sane button.
- The generic JS handlers in `templates/modules/module_detail.html` do not need label awareness because they navigate immediately on success — there is no button to relabel.

---

## 9. Cross-app integration helper

`apps/epilogue/services.py::get_post_module_epilogue_redirect_url` is the canonical integration surface for the modules layer:

```python
POST_MODULE_NEXT_FEATURE = {
    'M15': '/epilogue/',
}


def get_post_module_epilogue_redirect_url(user, module_code):
    if module_code not in POST_MODULE_NEXT_FEATURE:
        return None
    already_completed = EpilogueCompletion.objects.filter(
        user=user, completed_at__isnull=False,
    ).exists()
    if already_completed:
        return None
    return POST_MODULE_NEXT_FEATURE[module_code]
```

- **No research_consent check** (per D4 — Epilogue is open to all users).
- **Idempotency** via the `EpilogueCompletion.completed_at` check: an admin progress reset on M15 that re-completes the module will NOT route the user through the Epilogue again.

The corresponding helper for the AILST direction is `apps/ailst/services.py::get_post_module_redirect_url`, which still drives M5 → T1 but no longer has M15 → T2 in its mapping (the M15 entry was removed in C.2.5 with an explanatory comment pointing at the Epilogue chain).

---

## 10. Tests

**File:** `apps/epilogue/tests.py` — 12 tests across three classes.

### `EpiloguePlaceholderViewTest` (3 tests)
1. First visit creates an `EpilogueCompletion` row and renders the template.
2. Revisit reuses the existing row (no duplicates).
3. Already-completed state shows the success banner in the template.

### `EpilogueCompleteViewTest` (5 tests)
4. POST first time with consent + T2 not done → routes to `/ailst/t2/`.
5. POST routes to `/dashboard/` when `research_consent=False`. Completion row still flipped (Epilogue is open to all).
6. POST routes to `/dashboard/` when T2 already completed.
7. Double-submit is idempotent — `completed_at` does not move forward on the second POST.
8. GET on `/epilogue/complete/` is rejected (405) — view is `@require_POST`.

### `EpilogueRedirectHelperTest` (4 tests)
9. M15 with no completion returns `/epilogue/`.
10. M15 when Epilogue already completed returns `None` (idempotency).
11. M1 / M5 / M14 return `None` (not in the Epilogue mapping).
12. Non-consenting user still gets `/epilogue/` from the helper (D4 invariant — Epilogue is open to all users; the T2 gate fires later).

### Plus one updated integration test in `apps/modules/tests.py`

`test_completing_M15_redirects_to_epilogue_not_to_T2` — replaces the pre-C.2.5 expectation. Asserts:
- `ailst_redirect_url == '/epilogue/'`
- `ailst_redirect_label == 'Continue to PROODOS Epilogue'`

### Test results

All 12 epilogue tests pass on a fresh test DB. Whole Phase C suite: 110/110 (compliance 14 + users 30 + ailst 47 + modules 7 + epilogue 12).

---

## 11. End-to-end user flow

### Path A: research-consenting user, T2 not yet done

```
M15 reflection submitted
    → mark_tab_complete returns:
        {
          success: true,
          module_completed: true,
          next_tab: "completed",
          ailst_redirect_url: "/epilogue/",
          ailst_redirect_label: "Continue to PROODOS Epilogue"
        }
    → Frontend shows RAG feedback inline + button "Continue to PROODOS Epilogue"
    → User clicks button
    → GET /epilogue/ (EpilogueCompletion row created, started_at = NOW)
    → User sees placeholder page with "Mark complete and continue" button
    → User clicks button
    → POST /epilogue/complete/ (completed_at = NOW)
    → Redirect to /ailst/t2/
    → T2 baseline runs
    → /ailst/t2/complete/ → dashboard
```

### Path B: research-consenting user, T2 already done

```
... up through POST /epilogue/complete/ as above ...
    → _post_epilogue_destination sees T2 completed
    → Redirect to /dashboard/
```

### Path C: non-consenting user

```
... up through POST /epilogue/complete/ ...
    → _post_epilogue_destination sees research_consent=False
    → Redirect to /dashboard/ (T2 hop skipped entirely)
```

### Idempotency paths

- Second visit to `/epilogue/` after completion: same template, banner "You reached the Epilogue on …", button label becomes "Continue".
- Repeat POST to `/epilogue/complete/`: `completed_at` not moved, user still routed forward by the same logic.
- Admin resets M15 progress and the user re-completes M15: the `get_post_module_epilogue_redirect_url` helper sees `EpilogueCompletion.completed_at IS NOT NULL` and returns `None`, so the user stays in the normal next-tab flow without being bounced through the Epilogue again.

---

## 12. Browser smoke test

Performed 2026-05-11 against `mavros@example.com` (who already had M5 + T1 completed from the C.2.3 session):

- Direct GET to `/epilogue/` → placeholder page renders. Row created with `started_at`, `completed_at` NULL.
- Click "Mark complete and continue" → POST to `/epilogue/complete/`. Row updated (`completed_at` set). Redirect to `/ailst/t2/`.
- Revisit `/epilogue/` → button text now "Continue", banner "You reached the Epilogue on May 11, 2026" shows.

End-to-end M15 → Epilogue → T2 was not exercised via real M15 completion (the test user had not done M15); covered by the integration test in `apps/modules/tests.py` instead.

---

## 13. Open questions inherited from the April 2026 patch notes

From the patch notes, the following are still unresolved and will need decisions when TD-011 is taken up:

- **Q1-Q3** (original spec): held over without text in this doc.
- **Q4**: Personal Evolution Dashboard (Stage 0) shown once or persistent during dialogue?
- **Q5**: re-entry policy — does the Epilogue refresh data on return, or stay frozen at first-visit state?
- **Q6**: Learning Portrait PDF — embed dashboard screenshot, or narrative text only?

The current placeholder treats the Epilogue as one-shot (OneToOneField on `EpilogueCompletion`, no `last_revisited_at` field). Whether Q5 will require relaxing this constraint is open.

---

## 14. Forward path (TD-011)

The full Epilogue is captured in `proodos_files/TECH_DEBT_LOG.md::TD-011`. Summary of work:

1. **Schema extension** to `epilogue_completions`:
   - Per-stage timestamps (`stage0_seen_at`, `stage1_completed_at` … `stage3_completed_at`)
   - `dialogue_turns` JSONField: `[{role, content, generated_at}]` for the Gemini conversation
   - `learning_portrait_text` (TextField) + `learning_portrait_pdf` (FileField)

2. **Stage 0 — Personal Evolution Dashboard**: read DTP trajectory from `rag_queries`, RTM tensions from `reflection_tensions`. Render as a 4-line chart (one line per AILST factor across T0/T1/T2 + the M2-M15 DTP/RTM trajectory). Silent — no input required.

3. **Stages 1-3 (Look Back / Look In / Look Forward)**: Gemini-driven dialogue, ≤150 words per response, max 5 turns. Context window includes DTP trajectory data + RTM tension summary.

4. **Output: Learning Portrait**: 300-400 word synthesis from the educator's responses, rendered in-page and exported as PDF.

5. **Reusability** (Q5): one-shot vs. refresh-on-return.

Estimated effort: ~1500-2000 LOC (Gemini integration is the heaviest piece; dashboard chart and PDF generation each ~300 LOC; schema migration trivial).

When TD-011 is implemented, the placeholder view becomes the entry point for Stage 0; the `_post_epilogue_destination` helper stays unchanged (T2 routing is independent of how the Epilogue itself is filled in).

---

## 15. Reference paths (quick recap)

| Artefact | Path |
|---|---|
| App code | `apps/epilogue/` |
| Migration | `apps/epilogue/migrations/0001_initial.py` |
| Tests | `apps/epilogue/tests.py` |
| Template | `templates/epilogue/placeholder.html` |
| Cross-app helper | `apps/epilogue/services.py::get_post_module_epilogue_redirect_url` |
| Modules wiring | `apps/modules/views.py::mark_tab_complete` (the block annotated "Phase C C.2.4 + C.2.5") |
| Frontend integration | `templates/modules/tabs/tab5_reflection.html` (the `data-reflection-continue` button + JS handler) |
| AILST mapping (no longer carries M15) | `apps/ailst/services.py::POST_MODULE_AILST_TIMEPOINT` |
| Pre-migration backup | `pre_migration_backup_phaseC_C25_20260511.sql` (repo root, 49 MB) |
| Commit landing the work | `bec8951` ("Phase C C.2.5: PROODOS Epilogue placeholder + M15 → Epilogue → T2 chain") |
| Tech debt | `proodos_files/TECH_DEBT_LOG.md::TD-011` |
| Session log | `proodos_files/SESSION_LOG_PHASE_C_C23_C25_20260511.md` |
| Plan changelog entry | `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` (2026-05-11 C.2.5 entry) |
| Design proposal (C.2.5 decisions D1-D10) | this document + the C.2.5 section of the session log |

---

*End of Epilogue implementation notes.*
