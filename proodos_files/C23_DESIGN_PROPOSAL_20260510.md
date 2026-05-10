# C.2.3 Design Proposal — AILST T0 Flow

**Written:** 2026-05-10 (start of C.2.3 implementation session)
**Author:** Claude Code, in dialogue with John (PI)
**Status:** DRAFT — awaiting confirmation of open decisions (§16) before code lands
**Companion docs:** `HANDOFF_C23_AILST_FLOW_20260510.md` (parent hand-off), `PHASE_C_MIGRATION_PLAN_v1_20260509.md`

---

## 0. Scope summary

Build the AILST T0 baseline survey flow that fires after onboarding Step 3 (Summary confirmation). 36 items split into 4 pages (perception 10, knowledge_skills 10, applications_innovation 8, ethics 8), with partial-fill state machine, mobile-aware Likert UI, scoring on completion, and a completion handoff to dashboard.

Views are written parameterised on `timepoint` (T0 | T1 | T2) so that C.2.4 (post-M5 and post-M15 redirects) only needs to wire the redirect calls — no new view code. C.2.3 ships T0 reachable from the onboarding Summary; T1/T2 routes exist but are only reachable after C.2.4 wires them.

**Out of scope for C.2.3:**
- Module gating injection (C.2.4 — wires post-M5/M15 redirects)
- Greek (EL) seed (no schema change needed when added; views handle one language at a time per response row)
- CP 11 user wipe execution
- Admin/researcher score-export views (later)

---

## 1. Reusable inventory (confirmed in code)

### Models — exist, do NOT modify
- `apps.ailst.models.AilstItem` — 36 EN seeded rows, `paper_code` joins to JSONB.
- `apps.ailst.models.AilstResponse` — per `(user, timepoint)`, with `responses` JSONField, 5 nullable score columns, `started_at` / `completed_at` / `last_saved_at`, `unique_together = ('user', 'timepoint')`, DB CHECK on `timepoint IN ('T0','T1','T2')`. Method `compute_and_save_scores()` calls `save(update_fields=[...score cols])`.

### Scoring — exists, tested
- `apps.ailst.scoring.compute_factor_scores(responses, items_by_code)` — pure function. Returns dict with 5 score keys; raises `ValueError` on unknown paper_code or out-of-range value. Reverse-scoring (`6 - raw`) applied to K1, A3, E3 only.

### Settings — exist
- `settings.AILST_CURRENT_VERSION = 'ning_2025_v1'` — used at `AilstResponse` row creation.
- `settings.RESEARCH_CONSENT_CURRENT_VERSION` — exists, irrelevant here.

### Middleware — gates the flow
- `AIDisclosureMiddleware` (apps/compliance/middleware.py) — any non-acknowledged user gets redirected to `/onboarding/ai-disclosure/`. `/ailst/` paths are NOT in the bypass set, which is the correct behaviour: a user reaching `/ailst/t0/` must already be acknowledged (anyone bypassing onboarding gets caught by the middleware and bounced back).

### Form/template patterns from C.2.0 — C.2.2 (copy verbatim)
- DaisyUI utility classes throughout (`card bg-base-100 shadow-xl`, `card-body`, `card-actions`, `form-control`, `label`, `progress progress-primary`, `badge`, `alert alert-info`).
- **No inline `<style>` blocks** — verified convention.
- **i18n stubs from day 1**: `{% load i18n %}`, `{% trans %}`, `{% blocktrans %}`, `gettext_lazy as _` in forms/views.
- Item text comes from `AilstItem.item_text` at render — NOT verbatim-stored in the response (the verbatim-storage pattern from C.2.2 consent texts does not apply: AILST items are versioned via `instrument_version`, not snapshotted into each response).

### Test patterns from C.2.1 / C.2.2 (mirror)
- `Client` + `force_login(user)`.
- Pre-acknowledge AI disclosure in `setUp`: `ai_disclosure_acknowledged_at=timezone.now()`.
- For session-state requirements: `session = self.client.session; session['key'] = value; session.save()`.
- Helper methods on test classes like `_post_step3(*, research=False, ...)` — clean call sites.

---

## 2. State machine

### Entry preconditions
A user reaching `/ailst/t0/` must satisfy:
1. Authenticated (`@login_required`).
2. `TeacherProfile.ai_disclosure_acknowledged_at IS NOT NULL` (enforced by middleware, not by view).
3. `request.session['onboarding_step'] >= 3` OR `profile.profile_completed=True` (Step 3 done — see §11 for the session marker policy).

If precondition 3 fails → redirect to `users:onboarding_welcome` with a `messages.warning(...)`.

### Per-request branching at `/ailst/<timepoint>/`
```
GET /ailst/<tp>/ →
  resp = AilstResponse.get(user, timepoint=tp)
  if resp.completed_at is not None:
      → redirect /ailst/<tp>/complete/         (one-shot baseline; cannot retake)
  elif resp exists and partial:
      → redirect /ailst/<tp>/page/<first_incomplete>/   (skip intro on resume)
  else:                 # no row yet
      → render intro.html (T0 only; T1/T2 skip intro — see §8)

POST /ailst/<tp>/ →    (only valid before any row exists; the "Begin" button)
  AilstResponse.objects.create(user, timepoint=tp, language='en', instrument_version=...)
  → redirect /ailst/<tp>/page/1/
```

### Per-page branching at `/ailst/<tp>/page/<n>/`
```
GET → render page form, pre-filled with stored responses for that page
POST →
  with select_for_update():
    resp = AilstResponse.get(user, timepoint=tp)
    validate page form (all N items required, values 1-5)
    if valid:
        merge form.cleaned_data into resp.responses
        resp.save(update_fields=['responses', 'last_saved_at'])
        if page == 4 and len(resp.responses) == 36:
            resp.compute_and_save_scores()       # writes 5 score cols
            resp.completed_at = now()
            resp.save(update_fields=['completed_at'])
            → redirect /ailst/<tp>/complete/
        else:
            → redirect /ailst/<tp>/page/<n+1>/
    else:
        → re-render with errors
```

### Cannot-skip-ahead rule
Direct GET to `/ailst/t0/page/3/` when page 2 has unanswered items:
- View computes `first_incomplete_page(resp)` from the keys in `resp.responses`.
- If `requested_page > first_incomplete_page`, → redirect to `first_incomplete_page` with `messages.info("Please complete page X first.")`.
- Going **back** to an already-answered page (e.g., page 1 after partially filling page 2) IS allowed — the page renders pre-filled and the user can edit and re-submit.

### Resume detection
`first_incomplete_page(resp)` walks pages 1→4. For each page, checks if all expected paper_codes for that page are present in `resp.responses`. First page with any missing key wins. If all 36 present but `completed_at` is NULL (interrupted submit), the entry view triggers `_finalise_completion(resp)` defensively and redirects to complete.

### Decision on intro skip for resume
The intro page is shown only on first visit (no row yet). Resume goes straight to first incomplete page with a small banner: "Resuming where you left off — page X of 4." Rationale: user already saw the intro; sending them back is friction.

---

## 3. URL routing — `apps/ailst/urls.py`

### Proposed (Option A) — recommended

```python
from django.urls import path
from apps.ailst import views


app_name = 'ailst'

urlpatterns = [
    path('<str:timepoint>/',                  views.ailst_entry_view,    name='entry'),
    path('<str:timepoint>/page/<int:page>/',  views.ailst_page_view,     name='page'),
    path('<str:timepoint>/complete/',         views.ailst_complete_view, name='complete'),
]
```

`config/urls.py` addition:
```python
path('ailst/', include('apps.ailst.urls', namespace='ailst')),
```

### Alternative (Option B) — query param

```
/ailst/<timepoint>/?page=2
```

**Comparison:**

| | Option A (path segments) | Option B (query param) |
|---|---|---|
| Browser-back UX | Natural — each page is a distinct URL | Worse — back goes to the entry, not previous page |
| Bookmarkability | Each page bookmarkable | Bookmarks the entry |
| URL clarity | `/ailst/t0/page/2/` is self-describing | `/ailst/t0/?page=2` looks like a parameter to a single page |
| View dispatch | 3 view functions, one URL per concern | 1 view with internal branching on `?page=` |
| Django convention | Standard nested-resource style | Less common for stateful flows |
| Code complexity | Slightly more URL conf | Slightly more view branching |
| Risk: malformed input | Django int converter handles non-int automatically (404) | Manual int() parsing required + error handling |

**Recommendation: A.** Better UX, better matches Django conventions, simpler per-view logic. Phase A flows (onboarding step1/step2/step3) already use path-segment style. Keep consistency.

### Timepoint URL casing
URL uses lowercase (`/ailst/t0/`); view normalises to uppercase before DB lookup. Lowercase is friendlier in URLs and email links; the model still stores `'T0'`. Invalid timepoints (e.g., `/ailst/t9/`) raise `Http404`.

---

## 4. Page-to-items mapping (from M4 seed, confirmed)

| Page | Item numbers | paper_codes | Factor | Count |
|---|---|---|---|---|
| 1 | 1-10 | P1, P2, P3, P4, P5, P6, P7, P8, P9, P10 | perception | 10 |
| 2 | 11-20 | K1, K2, K3, K4, K5, K6, K7, K8, K9, K10 | knowledge_skills | 10 |
| 3 | 21-28 | A3, A4, A5, A6, A7, A8, A9, A10 | applications_innovation | 8 |
| 4 | 29-36 | E1, E3, E4, E5, E7, E8, E9, E10 | ethics | 8 |

Reverse-scored items (K1, A3, E3) appear on pages 2 and 3. They render identically to positive items — reversal is computed at scoring time, not at storage.

Encoded as:

```python
PAGES = 4

PAGE_FACTOR_RANGES = {
    1: ('perception',              1, 10),
    2: ('knowledge_skills',       11, 20),
    3: ('applications_innovation', 21, 28),
    4: ('ethics',                 29, 36),
}
```

Page items are fetched by `item_number BETWEEN lo AND hi` filtered on `language` + `instrument_version`, ordered by `item_number`.

---

## 5. Form design — `apps/ailst/forms.py`

Dynamic form, one `TypedChoiceField` per item on the page:

```python
from django import forms
from django.utils.translation import gettext_lazy as _


# 5-point scale, descending (5 = strongest endorsement). Anchors match
# Ning et al. 2025 paper. Stored value is the integer; label is shown
# at the radio.
LIKERT_CHOICES = [
    (5, _('Fully applicable')),
    (4, _('Applicable')),
    (3, _('Uncertain')),
    (2, _('Not applicable')),
    (1, _('Completely not applicable')),
]


class AilstPageForm(forms.Form):
    """One form per page; fields generated dynamically from items_for_page.

    Field name == paper_code (P1, K10 etc). All fields required: the
    instrument is invalid if any item is skipped.
    """

    def __init__(self, *args, items=None, existing_responses=None, **kwargs):
        super().__init__(*args, **kwargs)
        existing_responses = existing_responses or {}
        for item in items or []:
            self.fields[item.paper_code] = forms.TypedChoiceField(
                choices=LIKERT_CHOICES,
                widget=forms.RadioSelect,
                coerce=int,
                required=True,
                label=item.item_text,
                error_messages={
                    'required': _('Please answer this item before continuing.'),
                },
                initial=existing_responses.get(item.paper_code),
            )
            # Attach paper_code to field for template iteration ordering.
            self.fields[item.paper_code].paper_code = item.paper_code
```

**Why `TypedChoiceField` + `coerce=int`:** Django gives us string-from-radio by default; `coerce=int` ensures `cleaned_data[code]` is an int we can store directly in JSONB. Validation rejects non-1-5 values automatically via `choices`.

**Validation:**
- All fields required (`required=True`) → if user submits page with one item blank, form re-renders with per-field error message ("Please answer this item before continuing.") highlighted on the offending radio group.
- No cross-field validation needed (each item is independent).

---

## 6. View design — `apps/ailst/views.py`

```python
"""
AILST T0/T1/T2 administration views.

Single parameterised set of three views (entry, page, complete) shared
across T0/T1/T2 administrations. T0 is reachable from the onboarding
Summary POST (C.2.3). T1 will be reachable from post-M5 module
completion (C.2.4). T2 will be reachable from post-M15 (C.2.4).
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.ailst.forms import AilstPageForm
from apps.ailst.models import AilstItem, AilstResponse


VALID_TIMEPOINTS = ('T0', 'T1', 'T2')
PAGES = 4
PAGE_FACTOR_RANGES = {
    1: ('perception',              1, 10),
    2: ('knowledge_skills',       11, 20),
    3: ('applications_innovation', 21, 28),
    4: ('ethics',                 29, 36),
}


def _normalise_timepoint(raw):
    tp = (raw or '').upper()
    if tp not in VALID_TIMEPOINTS:
        raise Http404('Invalid AILST timepoint')
    return tp


def _items_for_page(page, *, language='en'):
    if page not in PAGE_FACTOR_RANGES:
        raise Http404('Invalid AILST page number')
    _, lo, hi = PAGE_FACTOR_RANGES[page]
    return list(
        AilstItem.objects.filter(
            language=language,
            instrument_version=settings.AILST_CURRENT_VERSION,
            item_number__gte=lo,
            item_number__lte=hi,
        ).order_by('item_number')
    )


def _first_incomplete_page(resp):
    """Returns the 1-indexed first page with any unanswered paper_code,
    or None if all 36 are answered."""
    answered = set((resp.responses or {}).keys())
    for page in range(1, PAGES + 1):
        codes = {it.paper_code for it in _items_for_page(page, language=resp.language)}
        if not codes.issubset(answered):
            return page
    return None


def _finalise_completion(resp):
    """Idempotent: compute scores + set completed_at. Two DB writes
    (compute_and_save_scores does its own save; we then save completed_at).
    Wrapped in transaction.atomic by the caller."""
    if resp.completed_at is not None:
        return
    resp.compute_and_save_scores()
    resp.completed_at = timezone.now()
    resp.save(update_fields=['completed_at'])


def _can_enter_ailst(request):
    """Step 3 must be done. Either session marker is set or profile_completed."""
    if request.session.get('onboarding_step', 0) >= 3:
        return True
    profile = getattr(request.user, 'teacher_profile', None)
    return bool(profile and profile.profile_completed)


@login_required
def ailst_entry_view(request, timepoint):
    tp = _normalise_timepoint(timepoint)

    if not _can_enter_ailst(request):
        messages.warning(request, _('Please complete the onboarding first.'))
        return redirect('users:onboarding_welcome')

    resp = AilstResponse.objects.filter(user=request.user, timepoint=tp).first()

    if resp and resp.completed_at:
        return redirect('ailst:complete', timepoint=tp.lower())

    if resp:
        first_incomplete = _first_incomplete_page(resp)
        if first_incomplete is None:
            with transaction.atomic():
                _finalise_completion(
                    AilstResponse.objects.select_for_update().get(pk=resp.pk)
                )
            return redirect('ailst:complete', timepoint=tp.lower())
        return redirect('ailst:page', timepoint=tp.lower(), page=first_incomplete)

    if request.method == 'POST':
        AilstResponse.objects.create(
            user=request.user,
            timepoint=tp,
            language='en',  # see Decision D6 — EL pending separate seed
            instrument_version=settings.AILST_CURRENT_VERSION,
        )
        return redirect('ailst:page', timepoint=tp.lower(), page=1)

    return render(request, 'ailst/intro.html', {
        'timepoint': tp,
        'timepoint_url': tp.lower(),
        'total_pages': PAGES,
        'total_items': 36,
    })


@login_required
def ailst_page_view(request, timepoint, page):
    tp = _normalise_timepoint(timepoint)
    if page not in PAGE_FACTOR_RANGES:
        raise Http404('Invalid AILST page')

    resp = AilstResponse.objects.filter(user=request.user, timepoint=tp).first()
    if resp is None:
        return redirect('ailst:entry', timepoint=tp.lower())
    if resp.completed_at:
        return redirect('ailst:complete', timepoint=tp.lower())

    # Cannot-skip-ahead enforcement.
    first_incomplete = _first_incomplete_page(resp)
    if first_incomplete is not None and page > first_incomplete:
        messages.info(request, _('Please complete the earlier pages first.'))
        return redirect('ailst:page', timepoint=tp.lower(), page=first_incomplete)

    items = _items_for_page(page, language=resp.language)

    if request.method == 'POST':
        with transaction.atomic():
            resp = (
                AilstResponse.objects
                .select_for_update()
                .get(user=request.user, timepoint=tp)
            )
            if resp.completed_at:
                return redirect('ailst:complete', timepoint=tp.lower())

            form = AilstPageForm(
                request.POST,
                items=items,
                existing_responses=resp.responses,
            )
            if form.is_valid():
                merged = dict(resp.responses or {})
                for item in items:
                    merged[item.paper_code] = form.cleaned_data[item.paper_code]
                resp.responses = merged
                resp.save(update_fields=['responses', 'last_saved_at'])

                if page == PAGES and len(merged) == 36:
                    _finalise_completion(resp)
                    return redirect('ailst:complete', timepoint=tp.lower())

                return redirect('ailst:page', timepoint=tp.lower(), page=page + 1)
    else:
        form = AilstPageForm(items=items, existing_responses=resp.responses)

    factor_name, _lo, _hi = PAGE_FACTOR_RANGES[page]
    is_resuming = bool(resp.responses) and page == _first_incomplete_page(resp)
    return render(request, 'ailst/page.html', {
        'form': form,
        'items': items,
        'timepoint': tp,
        'timepoint_url': tp.lower(),
        'page': page,
        'total_pages': PAGES,
        'factor_name': factor_name,
        # Entering page N means N-1 pages are done.
        'progress_percentage': int((page - 1) / PAGES * 100),
        'is_resuming': is_resuming,
    })


@login_required
def ailst_complete_view(request, timepoint):
    tp = _normalise_timepoint(timepoint)
    resp = get_object_or_404(
        AilstResponse,
        user=request.user,
        timepoint=tp,
        completed_at__isnull=False,
    )
    return render(request, 'ailst/complete.html', {
        'response': resp,
        'timepoint': tp,
        # See Decision D4: scores are hidden on T0/T1, shown on T2.
        'show_scores': tp == 'T2',
    })
```

**Concurrency note:** the `select_for_update()` in `ailst_page_view` POST is the M5-designed concurrency guard. Two simultaneous POSTs to the same page (double-click, parallel tabs) serialise; the second sees the first's merged responses, validates, and writes its (identical) merge. No duplicate compute, no lost write.

---

## 7. Template plan — 5 templates

| Template | Extends | Purpose |
|---|---|---|
| `templates/ailst/intro.html` | `base.html` | T0 first-visit welcome — what AILST is, time estimate, "Begin" button (POSTs to entry view) |
| `templates/ailst/page.html` | `base.html` | Page of N items. Progress bar at top. List of items via `{% include '_likert_item.html' %}`. Save+Continue button. Resume banner if `is_resuming`. |
| `templates/ailst/_likert_item.html` | (partial) | One item: text + 5 radio buttons. Responsive layout (see §9). |
| `templates/ailst/complete.html` | `base.html` | "Thank you" page. Conditionally shows factor-score cards (only if `show_scores`). Link to dashboard. |
| `templates/ailst/_progress_bar.html` | (partial, optional) | Progress bar markup reused between intro/page/complete. Only extract if 3 places diverge enough to warrant it. Default: inline in each. |

**Why `base.html` and not `_locked_base.html`:** AILST runs after the user has finished onboarding and acknowledged the AI disclosure — they are "in" the platform. `_locked_base.html` is the chip-less chrome used during onboarding lockdown (Step 0 disclosure modal, the onboarding form steps); inappropriate here.

**Generic-page reuse question (Decision D5):** the `page.html` template is parameterised on `factor_name` and `page` already — it works unchanged for T1 and T2 once their routes are reachable. No second template needed.

The `intro.html` template is T0-specific in content (introduces the baseline). For T1/T2 the entry view will skip the intro entirely (resume to page 1 directly, no intro). See Decision D5.

---

## 8. Likert UI design (CP 8) — radio table desktop / stacked card mobile

Five radio buttons + verbal anchors per item. Measurement fidelity (CP 5) requires:
- All 5 anchors visible (not numeric-only).
- Visual style consistent with a radio (not a slider — a slider invites mid-scale dragging that biases responses).

### Proposed `_likert_item.html` layout

**Desktop (`md:` breakpoint and up):**
```
┌─────────────────────────────────────────────────────────────────────────┐
│ Item text (left, ~40% width)              │ ○    ○    ○    ○    ○      │
│                                            │ Fully Appl. Unc. Not  Not  │
│                                            │ appl.            appl. at  │
│                                            │                        all │
└─────────────────────────────────────────────────────────────────────────┘
```

**Mobile (default, < `md:`):**
```
┌────────────────────────────┐
│ Item text                  │
│                            │
│ ○ Fully applicable         │
│ ○ Applicable               │
│ ○ Uncertain                │
│ ○ Not applicable           │
│ ○ Completely not applicable│
└────────────────────────────┘
```

### Implementation strategy
- Tailwind responsive utilities only (no JS, no media-query CSS file).
- Default flow = mobile (stacked). `md:` prefix flips to horizontal grid.
- Each `<label>` wraps a radio + anchor text so the entire row/column is clickable.
- DaisyUI `radio radio-primary` for the radio styling; `cursor-pointer` on labels.
- Field iteration uses `{{ form.<field>.errors }}` and `{{ form.<field> }}`-style access so Django renders the proper `id` / `name` attributes and we get free `aria-describedby` for errors.

**Sketch (representative — final template will use `{% for field in form %}` iteration, not the hand-rolled `<input>` shown below):**

```django
{# templates/ailst/_likert_item.html #}
{% load i18n %}

<div class="form-control mb-6 p-4 bg-base-200 rounded-lg
            md:grid md:grid-cols-5 md:gap-4 md:items-start
            {% if field.errors %}border border-error{% endif %}">

  {# Item text — full width on mobile, 2/5 on desktop #}
  <div class="md:col-span-2 mb-3 md:mb-0">
    <label class="font-medium text-base" for="{{ field.id_for_label }}">
      {{ field.label }}
    </label>
    {% if field.errors %}
      <p class="text-error text-sm mt-1">{{ field.errors|first }}</p>
    {% endif %}
  </div>

  {# Radio options — stacked on mobile, horizontal grid on desktop #}
  <div class="md:col-span-3 grid grid-cols-1 md:grid-cols-5 gap-2 md:gap-1">
    {% for radio in field %}
      <label class="cursor-pointer flex items-center md:flex-col md:items-center md:text-center gap-2">
        {{ radio.tag }}
        <span class="text-sm md:text-xs">{{ radio.choice_label }}</span>
      </label>
    {% endfor %}
  </div>

</div>
```

The `radio.tag` rendering gives us Django-managed `<input type="radio" name="P1" value="5" id="id_P1_0">` — no manual attribute juggling, full a11y (label `for=` ties to input `id=`), and form errors hook in naturally.

### Anchors stay full-text on every breakpoint
Per CP 5 (paper anchors are part of the measurement instrument). On very narrow screens text wraps to two lines — acceptable; better than abbreviating.

---

## 9. Onboarding → AILST integration (§11 in hand-off)

### Current flow
```
Step 1 → Step 2 → Step 3 → Summary (GET review) → Summary POST (sets
profile_completed, pops onboarding_step) → redirect to dashboard
```

### Proposed flow (C.2.3)
```
Step 1 → Step 2 → Step 3 → Summary (GET) → Summary POST (sets
profile_completed AND advances onboarding_step to 4) → redirect to
/ailst/t0/ → user completes T0 → /ailst/t0/complete/ → user clicks
"Continue to dashboard" → /dashboard/
```

### Edits required
- `apps/users/views.py::onboarding_summary` POST: change final redirect from `users:dashboard` to `ailst:entry` (`timepoint='t0'`). Update the session marker policy (see below).
- `templates/onboarding/summary.html`: change the CTA button text from "Complete Profile" to "Continue to AI Literacy baseline". Update the "🎉 Almost done!" copy to mention the upcoming baseline.

### Session marker policy
The current code does `request.session.pop('onboarding_step', None)` at the end of summary POST. I propose changing this to `request.session['onboarding_step'] = 4` so the post-onboarding state is observable.

- `onboarding_step == 3` ⇒ Step 3 done, Summary not yet submitted.
- `onboarding_step == 4` ⇒ Summary submitted, AILST T0 in flight (or done).

The marker can be cleared (popped) only after T0 completion if a clean session is desired. Or left at 4 indefinitely — it's diagnostic, not gating. Recommendation: leave it set; pop only on logout via standard session lifecycle. The AILST entry view does NOT key on the marker (see `_can_enter_ailst`: it accepts `onboarding_step >= 3` OR `profile.profile_completed=True`, since the profile flag is the durable truth).

### What about a user who navigates directly to `/ailst/t0/`?
- If never onboarded: `_can_enter_ailst` returns False, redirect to onboarding welcome.
- If onboarded and T0 not yet started: shows intro, can begin. (This is fine — they may have abandoned the Summary→T0 redirect and come back later via a bookmark.)
- If onboarded and T0 in progress: resumes to first incomplete page.
- If onboarded and T0 done: redirects to T0 complete page.

### What about the dashboard?
The dashboard is reachable independent of T0. In Phase C the recommendation (research design) is to gently nudge users who haven't done T0 (e.g., a banner on dashboard "You haven't completed the AI Literacy baseline yet — [Take it now]"). That nudging banner is **out of scope** for C.2.3 (it's a dashboard UX change, not an AILST flow change) and can be added later as a 10-line edit. Tracking note in TECH_DEBT_LOG.md.

---

## 10. Scoring on completion + complete page content

### What happens at the moment of completion
1. Page 4 POST is valid and `len(merged_responses) == 36`.
2. Inside the same `transaction.atomic()` + `select_for_update()` block:
   - `resp.responses = merged` → `resp.save(update_fields=['responses', 'last_saved_at'])` (1st write)
   - `_finalise_completion(resp)`:
     - `resp.compute_and_save_scores()` → writes 5 score columns (2nd write, internal to M5 method)
     - `resp.completed_at = now()` → `resp.save(update_fields=['completed_at'])` (3rd write)
3. Redirect to `/ailst/t0/complete/`.

Three writes inside one transaction. Acceptable — small row, ms-scale even on Pi. Alternative would be to add a `commit=False` flag to `compute_and_save_scores` (M5 API change). Not worth the change for one redundant write.

### Complete page content (Decision D4)
Three options:

| Option | Behaviour | Trade-off |
|---|---|---|
| A | Always hide scores; show only "Thank you" + dashboard link | Cleanest research-design (no Hawthorne / no priming for T1/T2). Boring UX. |
| B | Always show factor scores + overall | Best self-knowledge UX. But priming risk: a user who sees they scored low on "ethics" at T0 may unconsciously inflate ethics answers at T1/T2. |
| C | Hide on T0/T1, show on T2 | Compromise: T0 baseline stays uncontaminated, T1 (mid-programme) also kept clean, T2 (programme conclusion) doubles as a self-reflection deliverable. |

**Recommendation: C.** The template branches on `timepoint` and conditionally renders score cards. For T0/T1 the complete page is minimal (thank you + dashboard link + optional "what comes next" copy). For T2 it shows the 4 factor cards + overall + a "growth" note (optional later: side-by-side comparison with T0 — out of scope for C.2.3).

---

## 11. AI Disclosure middleware interaction (audit)

`/ailst/...` paths are NOT in `BYPASS_PATHS` / `BYPASS_PREFIXES`. This is correct:
- A user who reaches `/ailst/t0/` must have a `TeacherProfile` with `ai_disclosure_acknowledged_at IS NOT NULL`.
- This is guaranteed for any user past the Disclosure modal, which is required before onboarding Step 1.
- If a user without acknowledgment is somehow constructed (e.g., a staff user before `pre_deploy_c20_acknowledge_staff.py` is run with `--commit`), the middleware will catch the AILST request and redirect to the disclosure modal. Smoke test §16 in the hand-off doc covers this.

No middleware change needed. The AILST URLs flow through the standard middleware chain.

---

## 12. Tests — `apps/ailst/tests.py` extension

Existing tests: 16 (M4 seed-invariant + M5 scoring + lifecycle). Target: +12 view-layer tests = ~28 total. Mirror the C.2.2 setUp:

```python
def setUp(self):
    self.client = Client()
    self.user = User.objects.create_user(username='t0_tester', password='pw')
    TeacherProfile.objects.create(
        user=self.user,
        ai_disclosure_acknowledged_at=timezone.now(),
        profile_completed=True,
        research_consent=True,
    )
    self.client.force_login(self.user)
    session = self.client.session
    session['onboarding_step'] = 4
    session.save()
```

### Test classes & cases

**`AilstEntryViewTest`** (4 tests):
1. GET as user without onboarding done → redirects to onboarding welcome.
2. GET as onboarded user without any AilstResponse → intro page renders, 200.
3. POST entry as onboarded user → creates AilstResponse row + redirects to page 1.
4. GET when AilstResponse exists but partial → redirects to first incomplete page (skips intro).

**`AilstPageViewTest`** (5 tests):
5. GET page 1 → renders 10 items (P1-P10), 200.
6. POST page 1 valid (all 10 items, values 1-5) → responses JSONB has 10 keys, redirects to page 2.
7. POST page 1 with one missing → re-renders with form error on that field, responses unchanged.
8. POST page 4 with full 36 answered → completed_at set, scores computed, redirect to /complete/.
9. Resume: partially-filled page 2 → GET pre-populates the form with stored answers.

**`AilstStateMachineTest`** (3 tests):
10. Direct GET to page 3 when page 2 is incomplete → redirects to page 2 with info message.
11. Direct GET to /ailst/t0/ when T0 is already completed → redirects to /complete/.
12. Idempotency: double-submit of page 1 POST → only one write effectively, no error.

**`AilstTimepointParameterisationTest`** (2 tests):
13. T1 and T2 entry views work the same as T0 (parameterised test).
14. Invalid timepoint `/ailst/t9/` → 404.

**`AilstCompleteViewTest`** (2 tests):
15. GET /complete/ on completed T0 → renders, but factor scores NOT shown in HTML (D4: hide on T0).
16. GET /complete/ on completed T2 → factor scores ARE shown.

**`AilstConcurrencyTest`** (1 test, optional — Django's test runner has limited concurrent-transaction support):
17. Simulate two sequential POSTs of the same page 1 form → no duplicate compute, final state correct. (True double-write race needs threading; deferred to manual smoke test.)

**`AilstMobileLikertRenderTest`** (1 test):
18. Page 1 HTML contains all 5 verbal anchors as text (not just numeric values). Asserts regression on CP 5.

Total: 12 critical view tests + 16 existing model/scoring = **28 tests** in `apps.ailst`. Slightly above the §10 hand-off estimate of 12, but cheap to add and they cover known-risk surfaces (state machine, concurrency, CP 5).

---

## 13. i18n stubs

All user-facing strings wrapped: `gettext_lazy as _` in `forms.py` / `views.py`, `{% trans %}` / `{% blocktrans %}` in templates. Item text from `AilstItem.item_text` is NOT wrapped — it's content from the DB seed, not template literal. EL i18n happens via the EL seed of `ailst_items` rows (separate, deferred).

`makemessages` integration: not required to run as part of C.2.3 (no actual translations to bake in yet — same posture as C.2.0/C.2.1/C.2.2). The wrappers are scaffolding.

---

## 14. Settings additions — none required

The hand-off suggested `AILST_T0_REDIRECT_URL = '/dashboard/'`. Inspection: only one redirect destination at the end of the flow (dashboard), referenced once. Hardcoding `redirect('users:dashboard')` in `ailst_complete_view`'s "continue" button is simpler than a settings indirection. **Recommendation: no new settings.**

If we ever need to swap the post-T0 destination (e.g., to a "next-recommended-module" view), it's a one-liner change in the complete template.

---

## 15. Files to create / modify

### New files (7)
| File | Purpose | LOC est |
|---|---|---|
| `apps/ailst/urls.py` | URL conf, 3 routes | 15 |
| `apps/ailst/forms.py` | `AilstPageForm` dynamic factory | 50 |
| `apps/ailst/views.py` | 3 views + helpers | 240 |
| `templates/ailst/intro.html` | T0 welcome page | 60 |
| `templates/ailst/page.html` | Page of N items + progress | 90 |
| `templates/ailst/_likert_item.html` | One-item partial | 40 |
| `templates/ailst/complete.html` | Completion page (conditional scores) | 80 |

### Modified files (5)
| File | Change | LOC est |
|---|---|---|
| `config/urls.py` | Add `path('ailst/', include('apps.ailst.urls', namespace='ailst'))` | 1 |
| `apps/users/views.py::onboarding_summary` | POST redirect → `ailst:entry t0`, session marker → 4 | 3 |
| `templates/onboarding/summary.html` | CTA text update | 4 |
| `apps/ailst/tests.py` | +12 tests, setUp helpers | 260 |
| `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` | Changelog entry C.2.3 done | 10 |

**Total estimated diff: ~850 LOC** across 12 files. No DB migration. No new app. No new model fields.

---

## 16. Open decisions (await John's confirmation)

| # | Question | Recommended default |
|---|---|---|
| **D1** | T0-only or parameterise T0/T1/T2 in C.2.3? | Parameterise — avoid near-duplicate code in C.2.4. (Per hand-off §2.) |
| **D2** | Skip intro page on resume? | Yes, redirect to first incomplete page with a small banner. |
| **D3** | URL casing: `/ailst/t0/` or `/ailst/T0/`? | Lowercase URL, uppercase in DB. |
| **D4** | Show factor scores on `/complete/`? | T0 hide / T1 hide / T2 show. Open to discussion — research-design call. |
| **D5** | Generic page template for T1/T2 reuse? | Yes — single `page.html`, parameterised on `factor_name` and `page`. Intro is T0-only (T1/T2 skip intro entirely). |
| **D6** | Hardcode `language='en'` until EL seed lands, or read from profile? | Hardcode `'en'` with a TODO. Until an EL seed exists, reading from profile would fail with no items. |
| **D7** | research_consent as gating? | NO — keep T0 reachable for all onboarded users regardless of research_consent flag. Research consent affects data export and analytics inclusion, not whether the user can self-assess. (Hand-off §2 is silent on this; user prompt suggested gating. Defaulting to NO.) |
| **D8** | URL routing: path segments or query param? | Path segments (Option A in §3). |
| **D9** | onboarding_step session marker after summary POST? | Set to 4 (instead of pop), so T0 in-flight state is observable. |
| **D10** | Cannot-skip-ahead enforcement on direct URL access? | Yes — direct GET to `/page/3/` when page 2 is incomplete redirects to page 2 with `messages.info`. Going back to a completed page is allowed (editable). |
| **D11** | New settings constant `AILST_T0_REDIRECT_URL`? | NO — hardcode `redirect('users:dashboard')` in the complete template (one usage). |
| **D12** | Mobile Likert layout? | Radio table on desktop, stacked card on mobile, CSS-only switch via Tailwind responsive classes. Full anchors at every breakpoint. (§8.) |
| **D13** | Commit organisation? | Single commit for C.2.3, same pattern as C.2.0/C.2.1/C.2.2. Split only if work spans sessions. |

---

## 17. Effort + verification

### Effort estimate
| Subpiece | LOC | Notes |
|---|---|---|
| Views + helpers | 240 | Most logic in page POST handler |
| Forms | 50 | One dynamic class |
| URLs | 15 | Trivial |
| Templates (4 + 1 partial) | 270 | |
| Tests | 260 | 12 new tests with setUp |
| Wiring (summary + urls.py + plan changelog) | 15 | |
| **Total** | **~850** | |

**Session time:** 2-3h focused work if no design pivots. Plan: implement → run existing test suite → run new tests → commit → smoke-test in browser per hand-off §16.

### Smoke test sequence (post-implementation)
1. `python scripts/pre_deploy_c20_acknowledge_staff.py --commit` to ack staff
2. Browser visit `/ailst/t0/` as a logged-in user post-onboarding → intro page
3. Click "Begin" → page 1 with 10 P-items
4. Submit all 10 → page 2 with 10 K-items
5. Submit pages 2-4 → land on `/complete/` with no scores shown (T0)
6. Re-visit `/ailst/t0/` → redirects to complete (already done)
7. DB sanity: `SELECT timepoint, completed_at, perception_score, overall_score FROM ailst_responses WHERE user_id=<id>` → row with non-null scores
8. Mobile responsiveness: resize browser narrow → Likert items stack
9. Run full test suite → `manage.py test apps.ailst` → 28 pass

---

## 18. Carry-over for C.2.4

C.2.4 (module gating) will:
1. After M5 completion in `apps/modules/views.py:796`, check if T1 done; if not, redirect to `/ailst/t1/`.
2. After M15 completion, same for T2.

C.2.3 makes T1/T2 routes functional, so C.2.4 is purely a redirect injection (~30 LOC + tests). No new view work.

---

*End of design proposal. Awaiting confirmation of D1-D13 before implementation begins.*
