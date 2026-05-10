# Hand-off Document for C.2.3 — AILST T0 Flow (4 pages)

**Written:** 2026-05-10 (end of session that closed C.2.2)
**For:** the next Claude Code session that will design + implement C.2.3
**Reading time:** ~15 minutes
**Implementation effort estimate:** ~600-800 LOC across views, forms, templates, tests + 4-5 templates. Bigger than any single C.2.x piece so far.

---

## 0. How to read this document

Read end-to-end before starting code. The hand-off captures:
- What is already done and reusable
- The architecture decisions taken in earlier C.2.x pieces that apply here
- C.2.3-specific design questions with proposed defaults
- A file-by-file implementation plan

Each `🛑 DECIDE` marker is a design question you should propose-and-confirm with John before coding past it (same workflow established throughout Phase C).

Tone for produced code: factual, no emojis in code/commits, no `successfully implemented` framing. The dissertation committee will read this codebase.

---

## 1. What is reusable from earlier C.2.x

### Models (M4 + M5) — these exist, do not modify

- **`apps.ailst.models.AilstItem`** — 36 EN seeded items, `paper_code` field is the join key to responses JSONB.
- **`apps.ailst.models.AilstResponse`** — per-(user, timepoint), with:
  - `responses` JSONField (paper-code-keyed dict, e.g., `{"P1": 4, "K10": 2, ...}`)
  - 5 score columns (DecimalField, max_digits=4, decimal_places=2, nullable)
  - `started_at` (default=timezone.now), `completed_at` (nullable), `last_saved_at` (auto_now)
  - `unique_together = [('user', 'timepoint')]`
  - DB CHECK constraint `valid_timepoint` (`T0` / `T1` / `T2` only)
  - Model method `compute_and_save_scores(items_by_code=None)` already implemented (M5)

### Scoring (M5) — pure function, already tested

- **`apps.ailst.scoring.compute_factor_scores(responses, items_by_code)`** — returns dict with the 5 score keys; raises ValueError on unknown paper_code or out-of-range value.
- CP 5 anchor mapping: `5='Fully applicable'`, `1='Completely not applicable'`. Reverse-scoring (6-raw) applies to **K1, A3, E3** only.
- CP 6: `overall_score = mean(factor_scores)` if ALL four factors have values, else `None`.

### Settings — already set

- `settings.AILST_CURRENT_VERSION = 'ning_2025_v1'` — read by C.2.3 when creating a new AilstResponse row's `instrument_version`.
- (No new settings needed for C.2.3.)

### Middleware (C.2.0) — gates the flow

- `AIDisclosureMiddleware` redirects any user without `teacher_profile.ai_disclosure_acknowledged_at` to the disclosure modal. C.2.3 routes will need to either:
  - Be bypassed (not appropriate — AILST is post-disclosure)
  - OR ensure all C.2.3 routes are accessed by acknowledged users (correct — middleware will redirect anyone unauthorized)

### Forms / template patterns (C.2.1 + C.2.2) — copy these

- Use **DaisyUI utility classes** throughout: `card bg-base-100 shadow-xl`, `card-body`, `card-actions`, `form-control`, `label`, `divider`, `btn btn-primary`, `progress progress-primary`, `badge`, `alert alert-info`, etc.
- **No inline `<style>` blocks** — verified existing convention.
- **i18n stubs from day 1**: `{% load i18n %}`, `{% trans %}`, `{% blocktrans %}`, `gettext_lazy as _` in forms/views.
- **Verbatim text stored when relevant** — but AILST item text is NOT a consent text (the verbatim-storage pattern from C.2.0/C.2.2 does not apply here; the items live in `ailst_items` DB rows and are joined at render time).

### Test patterns (C.2.1 + C.2.2) — mirror these

- `Client + force_login(user)` pattern
- Pre-acknowledge AI disclosure in test setUp: `ai_disclosure_acknowledged_at=timezone.now()` to bypass middleware
- For session-marker requirements: `session = self.client.session; session['key'] = value; session.save()`
- Helper method `_post_step3(*, research=False, data_sharing=False, ...)` style — clean call sites

---

## 2. C.2.3 scope decision (first thing to confirm with John)

🛑 **DECIDE 1:** Implement T0 only, OR design views to handle all three timepoints (T0/T1/T2) parameterized?

**Recommendation:** Parameterized for all three. Reasoning:
- The views are identical except for the `timepoint` value passed to `AilstResponse`
- 36 items are the same set for all three administrations (same instrument_version)
- C.2.4 (module gating) needs the T1 and T2 routes to exist when wiring `apps/modules/views.py:796`
- Building them parameterised now avoids near-duplicate code later

**Scope of C.2.3 then:**
- Views support T0/T1/T2 via a single timepoint URL parameter
- C.2.3 deploys ALL three routes
- T0 is reachable now (from Step 3 → Summary → T0 redirect — see §7 for routing)
- T1 is reachable only after C.2.4 wires post-M5 redirect
- T2 is reachable only after C.2.4 wires post-M15 redirect

---

## 3. Flow design — state machine

```
User completes Step 3 → onboarding_summary view → redirect to /ailst/t0/
                                                           ↓
                                                  (if no AilstResponse row yet)
                                                           ↓
                                                  T0 INTRO PAGE (/ailst/t0/)
                                                           ↓
                                                  user clicks "Begin"
                                                           ↓
                                                  get_or_create AilstResponse(user, t0)
                                                           ↓
                                              redirect to first incomplete page
                                                           ↓
                              PAGE 1 (perception, items P1-P10)
                              ↓ (POST → validate all 10 answered → save JSONB)
                              PAGE 2 (knowledge_skills, items K1-K10)
                              ↓ (POST → ...)
                              PAGE 3 (applications_innovation, items A3-A10)
                              ↓ (POST → ...)
                              PAGE 4 (ethics, items E1+E3-E10)
                              ↓ (POST → all 36 keys present →
                                 compute_and_save_scores() →
                                 set completed_at = now())
                              redirect to Summary or Dashboard
```

**Resume on re-entry:**
- GET /ailst/t0/ checks `AilstResponse.objects.filter(user, timepoint='T0').first()`
  - No row → show intro page
  - Row with `completed_at IS NOT NULL` → show "already completed" page (T0 baseline is one-shot)
  - Row with partial responses → redirect to first incomplete page
- Partial detection: parse `len(responses)` keys → determine page (10 → page 2, 20 → page 3, 28 → page 4, 36 → completed)

🛑 **DECIDE 2:** Should the intro page be skippable for users who have already started but not completed (i.e., go straight to their resume page)?

**Recommendation:** Skip the intro page on resume. User has already seen it; sending them to their last-incomplete page is faster UX. Show a small "Resuming from page 2 of 4" banner.

---

## 4. URL design

```
/ailst/<timepoint>/                  GET → intro page (or resume to first incomplete)
/ailst/<timepoint>/<int:page>/       GET → render page; POST → submit page responses
/ailst/<timepoint>/done/             GET → completion confirmation; redirect target after compute
```

With `<timepoint>` constrained to one of `T0`, `T1`, `T2` (in `urls.py` use a regex path or in the view raise 404 for invalid).

**`apps/ailst/urls.py`** (new file):

```python
from django.urls import path
from apps.ailst import views


app_name = 'ailst'

urlpatterns = [
    path('<str:timepoint>/', views.ailst_entry_view, name='entry'),
    path('<str:timepoint>/<int:page>/', views.ailst_page_view, name='page'),
    path('<str:timepoint>/done/', views.ailst_done_view, name='done'),
]
```

**`config/urls.py`** addition:
```python
path('ailst/', include('apps.ailst.urls', namespace='ailst')),
```

🛑 **DECIDE 3:** URL-style for timepoint — `t0` (lowercase) or `T0` (uppercase) in the URL? Model stores `'T0'`. URL is user-facing.

**Recommendation:** Lowercase in URL (`/ailst/t0/`), normalised to uppercase before DB query. Friendlier URLs (`T` in URLs looks Mongo-y).

---

## 5. Page-to-items mapping (from M4 seed)

| Page | Item number range | paper_codes | Factor | Count |
|---|---|---|---|---|
| 1 | 1-10 | P1, P2, P3, P4, P5, P6, P7, P8, P9, P10 | perception | 10 |
| 2 | 11-20 | K1, K2, K3, K4, K5, K6, K7, K8, K9, K10 | knowledge_skills | 10 |
| 3 | 21-28 | A3, A4, A5, A6, A7, A8, A9, A10 | applications_innovation | 8 |
| 4 | 29-36 | E1, E3, E4, E5, E7, E8, E9, E10 | ethics | 8 |

Reverse-scored items (K1, A3, E3) appear on pages 2 and 3 — display the same way as positive items (the reversal happens at compute time, not at storage time).

---

## 6. Form design — dynamic form per page

`apps/ailst/forms.py` (new file):

```python
from django import forms
from django.utils.translation import gettext_lazy as _


LIKERT_CHOICES = [
    (5, _('Fully applicable')),
    (4, _('Applicable')),
    (3, _('Uncertain')),
    (2, _('Not applicable')),
    (1, _('Completely not applicable')),
]


class AilstPageForm(forms.Form):
    """Dynamically generates a form with one RadioSelect per item on the page.

    Each field is named after the paper_code (P1, K10, A3 etc.). Field
    value type is int (1-5). All fields required (cannot submit a partial
    page).
    """

    def __init__(self, *args, items=None, existing_responses=None, **kwargs):
        super().__init__(*args, **kwargs)
        existing_responses = existing_responses or {}
        for item in items or []:
            field = forms.TypedChoiceField(
                choices=LIKERT_CHOICES,
                widget=forms.RadioSelect(attrs={'class': 'ailst-likert-radio'}),
                coerce=int,
                required=True,
                label=item.item_text,
                error_messages={'required': _('Please answer this item before continuing.')},
                initial=existing_responses.get(item.paper_code),
            )
            field.paper_code = item.paper_code  # attach for template ordering
            self.fields[item.paper_code] = field
```

Form factory: `AilstPageForm(items=items_for_page, existing_responses=existing_dict, data=request.POST or None)`.

---

## 7. View design — three views

`apps/ailst/views.py` (replaces stub):

```python
"""
AILST T0/T1/T2 administration views.

Single set of views parameterised by timepoint. T0 is reachable from
onboarding Summary; T1 is reachable from post-M5 module completion
(C.2.4); T2 is reachable from post-M15 module completion (C.2.4).
"""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

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
    """Accept t0/T0 etc. -> 'T0'; raise Http404 if not in valid set."""
    tp = (raw or '').upper()
    if tp not in VALID_TIMEPOINTS:
        raise Http404('Invalid AILST timepoint')
    return tp


def _items_for_page(page):
    """36 items split into 4 factor-blocks. Returns queryset ordered by item_number."""
    _, lo, hi = PAGE_FACTOR_RANGES[page]
    return AilstItem.objects.filter(
        language='en',  # TODO: pin from user.teacher_profile.language_primary when EL seed lands
        instrument_version=settings.AILST_CURRENT_VERSION,
        item_number__gte=lo,
        item_number__lte=hi,
    ).order_by('item_number')


def _first_incomplete_page(response_obj):
    """Walk pages 1-4, return the first one with any unanswered item, or
    None if all 36 items are answered (i.e., the response is complete).
    """
    answered = set((response_obj.responses or {}).keys())
    for page, (_, lo, hi) in PAGE_FACTOR_RANGES.items():
        items = _items_for_page(page).values_list('paper_code', flat=True)
        if not set(items).issubset(answered):
            return page
    return None  # all 36 answered


@login_required
def ailst_entry_view(request, timepoint):
    """GET /ailst/<timepoint>/ — intro page or redirect to resume."""
    tp = _normalise_timepoint(timepoint)
    resp = AilstResponse.objects.filter(user=request.user, timepoint=tp).first()

    if resp and resp.completed_at:
        return redirect('ailst:done', timepoint=tp.lower())

    if resp:
        next_page = _first_incomplete_page(resp)
        if next_page is None:
            # Edge: all 36 answered but completed_at not set (interrupted submit).
            # Trigger completion finalisation then go to done.
            _finalise_completion(resp)
            return redirect('ailst:done', timepoint=tp.lower())
        # Resume directly without intro page (DECIDE 2 default).
        return redirect('ailst:page', timepoint=tp.lower(), page=next_page)

    # First visit — show intro page; entry POST creates the AilstResponse row.
    if request.method == 'POST':
        AilstResponse.objects.create(
            user=request.user,
            timepoint=tp,
            language='en',
            instrument_version=settings.AILST_CURRENT_VERSION,
        )
        return redirect('ailst:page', timepoint=tp.lower(), page=1)

    return render(request, 'ailst/intro.html', {
        'timepoint': tp,
        'timepoint_url': tp.lower(),
    })


@login_required
def ailst_page_view(request, timepoint, page):
    """GET — render page form; POST — validate + save partial."""
    tp = _normalise_timepoint(timepoint)
    if page not in PAGE_FACTOR_RANGES:
        raise Http404('Invalid AILST page')

    items = list(_items_for_page(page))
    if not items:
        raise Http404('No items configured for this page')

    if request.method == 'POST':
        with transaction.atomic():
            resp = (
                AilstResponse.objects
                .select_for_update()  # concurrency guard against double-click
                .filter(user=request.user, timepoint=tp)
                .first()
            )
            if resp is None:
                return redirect('ailst:entry', timepoint=tp.lower())
            if resp.completed_at:
                return redirect('ailst:done', timepoint=tp.lower())

            form = AilstPageForm(
                request.POST,
                items=items,
                existing_responses=resp.responses,
            )
            if form.is_valid():
                # Merge new page answers into responses JSONB.
                merged = dict(resp.responses or {})
                for item in items:
                    merged[item.paper_code] = form.cleaned_data[item.paper_code]
                resp.responses = merged
                resp.save(update_fields=['responses', 'last_saved_at'])

                # Check if this submission completes the instrument.
                if page == PAGES and len(merged) == 36:
                    _finalise_completion(resp)
                    return redirect('ailst:done', timepoint=tp.lower())

                return redirect('ailst:page', timepoint=tp.lower(), page=page + 1)
    else:
        resp = AilstResponse.objects.filter(user=request.user, timepoint=tp).first()
        if resp is None:
            return redirect('ailst:entry', timepoint=tp.lower())
        if resp.completed_at:
            return redirect('ailst:done', timepoint=tp.lower())
        form = AilstPageForm(items=items, existing_responses=resp.responses)

    factor_name, _lo, _hi = PAGE_FACTOR_RANGES[page]
    return render(request, 'ailst/page.html', {
        'form': form,
        'items': items,
        'timepoint': tp,
        'timepoint_url': tp.lower(),
        'page': page,
        'total_pages': PAGES,
        'factor_name': factor_name,
        'progress_percentage': int((page - 1) / PAGES * 100),  # entering page N
    })


def _finalise_completion(response_obj):
    """Atomic: compute scores + set completed_at. Idempotent if called twice."""
    if response_obj.completed_at is not None:
        return
    response_obj.compute_and_save_scores()
    from django.utils import timezone
    response_obj.completed_at = timezone.now()
    response_obj.save(update_fields=['completed_at'])


@login_required
def ailst_done_view(request, timepoint):
    """Completion confirmation — minimal stats + redirect target."""
    tp = _normalise_timepoint(timepoint)
    resp = get_object_or_404(
        AilstResponse, user=request.user, timepoint=tp, completed_at__isnull=False,
    )
    return render(request, 'ailst/done.html', {
        'response': resp,
        'timepoint': tp,
    })
```

---

## 8. Template plan

| Template | Purpose |
|---|---|
| `templates/ailst/intro.html` | Welcome + what to expect + "Begin" button. Renders only on T0; for T1/T2 we go straight to page 1 (no intro). |
| `templates/ailst/page.html` | One page of N items (uses `_likert_item.html` partial). Top progress bar, items list, Save+Continue button. |
| `templates/ailst/_likert_item.html` | One item rendered as item_text + 5 radio buttons. Mobile-responsive (see §9). |
| `templates/ailst/done.html` | Completion confirmation with summary scores (perception/knowledge/etc. each as a small DaisyUI stat card). Link to dashboard or next step. |

All extend `base.html` (NOT `_locked_base.html` — by the time the user is at AILST they have navigated past the AI Disclosure middleware and the platform chrome is fine to show).

🛑 **DECIDE 4:** Show the computed factor scores to the user on the done page (transparency / self-knowledge UX) OR keep them hidden (no Hawthorne effect bias for T1/T2)?

**Recommendation:** Hide on T0 (don't bias subsequent self-assessment), show on T2 (programme conclusion + self-knowledge benefit). T1 hide. So `done.html` checks `timepoint` and conditionally renders scores. Worth raising with John — research-design question.

---

## 9. Mobile Likert (CP 8) — design proposal

5 radio buttons + verbal anchors. Three layout options:

| Layout | Desktop | Mobile | Pros / cons |
|---|---|---|---|
| A. Horizontal row + labels under | Item on left, 5 radios + labels horizontal | Stacked vertically (item, then radios+labels) | Most space-efficient on desktop; mobile gets long |
| B. Slider-like horizontal across both | Same | Same horizontal but shorter labels | Cleaner mobile; might look like slider (CP 5 risk) |
| **C. Radio table** | Tabular: item rows, 5 columns (anchors as headers) | Each item becomes a card: text + 5 stacked radios with full labels | Clearest measurement intent, slightly more vertical space |

**Recommendation: C — radio table on desktop, stacked card on mobile.** Preserves measurement fidelity (paper used radios, not slider). Tailwind responsive: `md:table-row` desktop, `card` on mobile.

Markup sketch for `_likert_item.html`:

```html
{# Desktop: row in a table; mobile: stacked card via responsive utility classes #}
<div class="mb-4 md:table-row">
    <div class="md:table-cell md:pr-4 md:align-top md:w-2/5">
        <p class="font-medium">{{ item.item_text }}</p>
    </div>
    <div class="md:table-cell">
        <div class="grid grid-cols-5 gap-1">
            {% for value, label in form.field.field.choices %}
                <label class="cursor-pointer text-center text-xs md:text-sm">
                    <input type="radio" name="{{ form.field.name }}" value="{{ value }}"
                           class="radio radio-primary radio-sm mb-1"
                           {% if form.field.value|stringformat:"s" == value|stringformat:"s" %}checked{% endif %}>
                    <span class="block">{{ label }}</span>
                </label>
            {% endfor %}
        </div>
    </div>
</div>
```

Wrap pages in a parent `md:table` for the table layout; mobile gets natural block flow with `<label>` blocks per item.

The 5 anchors stay full-text (1=Completely not applicable through 5=Fully applicable per CP 5). On very narrow screens (<400px), anchors might wrap — acceptable; do not abbreviate (paper used full anchors).

---

## 10. Tests — `apps/ailst/tests.py` extension

Target: 10-12 additional tests on top of the 16 existing seed-invariant + scoring + lifecycle tests. Bring total `apps.ailst` test count to ~26-28.

Test classes:
- **`AilstEntryViewTest`** (3 tests):
  - GET intro page for first-time user
  - GET redirects to resume page for in-progress user
  - GET redirects to done page for completed user
- **`AilstPageViewTest`** (5 tests):
  - GET page 1 renders 10 items (perception)
  - POST page 1 valid → redirect to page 2 + responses JSONB has 10 keys
  - POST page 1 with one item missing → form re-rendered with error, JSONB unchanged
  - POST page 4 with all 36 → completed_at set + scores computed
  - Resume from page 2 with partial state → form pre-populated with stored answers
- **`AilstConcurrencyTest`** (1 test):
  - Two simultaneous POSTs to same page (simulate double-click) → no duplicate compute, scores correct
- **`AilstAllTimepointsTest`** (2 tests):
  - Parameterised: T0 / T1 / T2 each can run independently
  - Invalid timepoint (e.g., `/ailst/t9/`) → 404
- **`AilstDoneViewTest`** (1 test):
  - Done page renders for completed response; raises 404 if not completed

Mirror the C.2.2 setUp pattern (force_login + pre-acknowledge AI disclosure + session marker if needed).

---

## 11. Wiring into onboarding Summary

After Step 3 → Summary → currently `redirect('users:dashboard')`. C.2.3 needs to route to T0 instead.

Two options:

**A.** Modify `onboarding_summary` view to `redirect('ailst:entry', timepoint='t0')` instead of `dashboard`.

**B.** Add a separate "Step 4 placeholder" in the onboarding flow that explains AILST and links to it, then dashboard after T0.

**Recommendation: A** — direct redirect. The intro page on `/ailst/t0/` IS the "Step 4 explainer". Avoid double pages.

Edit `apps/users/views.py::onboarding_summary` POST handler: change the final redirect target.

Also update the `onboarding_summary` template to indicate "Next: AI Literacy baseline" so the user knows what's coming when they click the submit button.

---

## 12. C.2.4 dependency note (do not implement in C.2.3)

C.2.4 is module gating injection. The hook is at `apps/modules/views.py:796` (per audit). When M5 is just completed, redirect to `/ailst/t1/`. When M15 is completed, redirect to `/ailst/t2/`. Idempotency check: skip redirect if `AilstResponse.objects.filter(user, timepoint=tp, completed_at__isnull=False).exists()`.

C.2.3 must ensure T1 and T2 routes are functional (they will be, since views are parameterised). C.2.4 is a separate ~30-LOC change in modules/views.py.

---

## 13. Open challenge points carried into C.2.3

| CP | Source | What |
|---|---|---|
| **CP 8** | Hand-off doc | Mobile Likert rendering. §9 above proposes radio-table-desktop / stacked-card-mobile. Confirm with John before coding the template. |
| **CP 11 wipe execution** | Hand-off + M2 session log | Decision was Option B (wipe non-staff). NOT YET EXECUTED. Original reset script deleted in Γ.1. Fresh wipe script needed before real pilot — just `User.objects.filter(is_staff=False, is_superuser=False).delete()`. Not C.2.3 scope, but pre-pilot task. |

Other CPs (1, 2, 3, 4, 5, 6, 7, 9, 10) are resolved or addressed in earlier C.2.x pieces.

---

## 14. File-by-file implementation plan

| File | Action |
|---|---|
| `apps/ailst/views.py` | REPLACE — implement 3 views (entry, page, done) + helpers |
| `apps/ailst/forms.py` | NEW — `AilstPageForm` dynamic form factory |
| `apps/ailst/urls.py` | NEW — 3 URL patterns |
| `config/urls.py` | EDIT — `include('apps.ailst.urls', namespace='ailst')` |
| `templates/ailst/intro.html` | NEW — DaisyUI intro page |
| `templates/ailst/page.html` | NEW — page-of-items |
| `templates/ailst/_likert_item.html` | NEW — partial for one item |
| `templates/ailst/done.html` | NEW — completion confirmation |
| `apps/users/views.py` | EDIT — `onboarding_summary` redirect target → `ailst:entry` |
| `templates/onboarding/summary.html` | EDIT — small text update "Next: AI Literacy baseline" |
| `apps/ailst/tests.py` | EXTEND — ~12 new tests |
| `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` | EDIT — changelog entry C.2.3 |

No DB migration. No schema change. No new app. Pure view+form+template+test work.

---

## 15. Commit organisation

**Recommendation: 1 commit for C.2.3.** Same pattern as C.2.0 / C.2.1 / C.2.2. ~800 LOC + 4 templates + 12 tests. Reviewable as a single piece.

If the work gets bigger than expected, split into:
1. Views + forms + URL routing + tests
2. Templates + onboarding redirect wiring

But aim for single commit unless the diff exceeds ~1000 lines or the work spans multiple sessions.

---

## 16. Smoke test sequence for John (post-implementation)

After commit, before declaring done:

1. **Run pre-deploy script with --commit** to acknowledge staff (avoids redirect on next browser load): `python scripts/pre_deploy_c20_acknowledge_staff.py --commit`
2. **Browser visit `/ailst/t0/`**: should see intro page
3. **Click "Begin"**: should land on page 1 with 10 P-items
4. **Answer all 10, submit**: should land on page 2 with 10 K-items
5. **Answer pages 2-4**: at page 4 submit, lands on done page with scores
6. **Re-visit `/ailst/t0/`**: should land on done page (already completed)
7. **DB sanity:** `SELECT timepoint, completed_at, perception_score, overall_score FROM ailst_responses WHERE user_id=<your_id>` → row exists with non-null scores
8. **Mobile**: resize browser narrow OR open on phone, verify Likert items are usable
9. **Run full test suite**: 60+12 = ~72 tests, all pass

---

## 17. Estimated effort

| Subpiece | LOC | Notes |
|---|---|---|
| views.py (3 views + helpers) | ~250 | Most logic is in the page POST handler |
| forms.py | ~50 | Single dynamic form factory |
| urls.py | ~15 | Trivial |
| intro.html | ~50 | Static text + Begin button |
| page.html | ~80 | Progress bar, form rendering, navigation |
| _likert_item.html | ~30 | One partial |
| done.html | ~80 | Scores cards + next-step link |
| tests.py extension | ~250 | 12 tests with setUp |
| Wiring (summary redirect) | ~10 | One-line edit |
| **Total** | **~815** | Plus the test setUp boilerplate |

**Session time estimate:** 2-3 hours focused work if no design pivots. Plan for design pass first (you can use this hand-off doc instead of a separate proposal pass if you trust the defaults), then implement, then verify.

---

## 18. Key reference paths (quick recap)

| Artefact | Path |
|---|---|
| Migration plan | `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` |
| Tech debt log | `proodos_files/TECH_DEBT_LOG.md` |
| Dead schema audit | `audits/DEAD_SCHEMA_AUDIT_20260509.md` |
| AILST source paper | `~/Desktop/.../Development_and_validation_of_the_Artificial_Intel-1-1.pdf` |
| AILST EN seed | `apps/ailst/seeds/ning_2025_v1_en.json` |
| AILST scoring | `apps/ailst/scoring.py` |
| AILST models | `apps/ailst/models.py` (AilstItem, AilstResponse) |
| Companion session logs | `proodos_files/SESSION_LOG_PHASE_C_*.md` |
| Memory files (auto-loaded) | `~/.claude/projects/C--Users-dourv-unesco-ai-pd/memory/` |

---

*End of hand-off. Next session: read this doc, propose design with your refinements (or skip directly to implement if defaults are acceptable to John), then go.*
