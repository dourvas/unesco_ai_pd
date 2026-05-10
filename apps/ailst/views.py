"""
AILST T0/T1/T2 administration views.

Three views, parameterised by timepoint ('T0' | 'T1' | 'T2'):

  - ailst_entry_view   — intro page for first visit; resume redirect
                         for in-progress; complete redirect when done.
  - ailst_page_view    — render one page of items (GET) or persist
                         submitted page (POST). select_for_update guard
                         against concurrent submits.
  - ailst_complete_view — acknowledgment page. Per design decision D4
                         (C.2.3 design proposal, 2026-05-10), factor
                         scores are NOT shown to participants during
                         the pilot (avoids baseline priming and demand
                         characteristics for T1/T2). TD-010 tracks the
                         post-pilot score reveal feature.

  - ailst_research_consent_required_view — explanation page for users
                         with research_consent=False. AILST is the
                         primary research instrument; collecting data
                         without active consent would breach GDPR
                         Art. 9 and IRB participation requirements.

T0 is reachable from the onboarding Summary POST (C.2.3 wiring). T1
and T2 routes exist here but only become reachable once C.2.4 wires
the post-M5 and post-M15 module-completion redirects.
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

# (factor name, item_number lower bound, item_number upper bound)
# Item numbers map 1-1 onto the M4 seed:
#   P1-P10  → perception              (page 1)
#   K1-K10  → knowledge_skills        (page 2)
#   A3-A10  → applications_innovation (page 3, 8 items — A1/A2 removed by paper EFA)
#   E1+E3-E10 → ethics                (page 4, 8 items — E2/E6 removed by paper EFA)
PAGE_FACTOR_RANGES = {
    1: ('perception',              1, 10),
    2: ('knowledge_skills',       11, 20),
    3: ('applications_innovation', 21, 28),
    4: ('ethics',                 29, 36),
}


def _normalise_timepoint(raw):
    """Accept t0/T0 etc., return 'T0'. Raise Http404 for invalid input."""
    tp = (raw or '').upper()
    if tp not in VALID_TIMEPOINTS:
        raise Http404('Invalid AILST timepoint')
    return tp


def _items_for_page(page, *, language='en'):
    """Return the AilstItem queryset for one page, ordered by item_number."""
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
    """Walk pages 1-4 and return the first one with any missing answer.

    Returns None if all 36 paper_codes are present in resp.responses
    (i.e., the row is ready for finalisation even if completed_at is
    still NULL — an interrupted submit case).
    """
    answered = set((resp.responses or {}).keys())
    for page in range(1, PAGES + 1):
        codes = {it.paper_code for it in _items_for_page(page, language=resp.language)}
        if not codes.issubset(answered):
            return page
    return None


def _finalise_completion(resp):
    """Compute the 5 scores and set completed_at. Idempotent.

    Caller must hold the row under select_for_update inside a
    transaction.atomic block. compute_and_save_scores itself does a
    save(update_fields=[...score cols]); we then save completed_at.
    """
    if resp.completed_at is not None:
        return
    resp.compute_and_save_scores()
    resp.completed_at = timezone.now()
    resp.save(update_fields=['completed_at'])


def _onboarding_complete(request):
    """Step 3 must have been confirmed at least once.

    Either the in-session marker reached 3+ (live navigation from
    Summary), or the durable profile flag is set (later returns —
    bookmark, direct URL, post-logout login).
    """
    if request.session.get('onboarding_step', 0) >= 3:
        return True
    profile = getattr(request.user, 'teacher_profile', None)
    return bool(profile and profile.profile_completed)


def _has_research_consent(request):
    """Read research-participation consent state for AILST gating.

    Source of truth: TeacherProfile.research_consent boolean cache.

    Why the boolean cache and not a direct ConsentRecord query:

      1. The cache is kept canonical by sync_teacher_profile_booleans
         (apps/compliance/signals.py), which fires on every
         record_consent / revoke_consent for consent_type
         'research_participation'. The cache is therefore always in
         lockstep with the latest ConsentRecord state.
      2. Reading a boolean column on an already-fetched TeacherProfile
         avoids an extra DB query on every AILST request.
      3. AILST is a hot path during data collection. Cheap reads matter.

    This convention also prevents the "let me query ConsentRecord
    directly" temptation from a future contributor who does not know
    about the M6 sync design.
    """
    profile = getattr(request.user, 'teacher_profile', None)
    return bool(profile and profile.research_consent)


@login_required
def ailst_entry_view(request, timepoint):
    tp = _normalise_timepoint(timepoint)

    if not _onboarding_complete(request):
        messages.warning(request, _('Please complete the onboarding first.'))
        return redirect('users:onboarding_welcome')

    if not _has_research_consent(request):
        # GDPR audit-trail policy: if a partial AilstResponse exists for
        # this user-timepoint, it is NOT deleted on consent revocation.
        # The row is preserved with completed_at=NULL so that:
        #   (a) the audit trail can answer "what data existed at the
        #       time consent was withdrawn?",
        #   (b) the user can resume from where they left off if they
        #       re-grant consent later (no destruction of their work),
        #   (c) demand-characteristics protection — a forced restart
        #       would contaminate the original first-pass responses
        #       with memory effects.
        # Right-to-erasure is a separate, explicit user action via the
        # Privacy dashboard (Phase C.4); it is not triggered by a
        # consent toggle.
        return redirect('ailst:research_consent_required', timepoint=tp.lower())

    resp = AilstResponse.objects.filter(user=request.user, timepoint=tp).first()

    if resp and resp.completed_at:
        return redirect('ailst:complete', timepoint=tp.lower())

    if resp:
        next_page = _first_incomplete_page(resp)
        if next_page is None:
            # All 36 answered but completed_at NULL — finalise defensively.
            with transaction.atomic():
                locked = (
                    AilstResponse.objects.select_for_update().get(pk=resp.pk)
                )
                _finalise_completion(locked)
            return redirect('ailst:complete', timepoint=tp.lower())
        return redirect('ailst:page', timepoint=tp.lower(), page=next_page)

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
        'total_pages': PAGES,
        'total_items': 36,
    })


@login_required
def ailst_page_view(request, timepoint, page):
    tp = _normalise_timepoint(timepoint)
    if page not in PAGE_FACTOR_RANGES:
        raise Http404('Invalid AILST page')

    if not _onboarding_complete(request):
        messages.warning(request, _('Please complete the onboarding first.'))
        return redirect('users:onboarding_welcome')

    if not _has_research_consent(request):
        return redirect('ailst:research_consent_required', timepoint=tp.lower())

    resp = AilstResponse.objects.filter(user=request.user, timepoint=tp).first()
    if resp is None:
        return redirect('ailst:entry', timepoint=tp.lower())
    if resp.completed_at:
        return redirect('ailst:complete', timepoint=tp.lower())

    # Cannot-skip-ahead: a direct GET to page N when an earlier page is
    # incomplete redirects to that earlier page. Going BACK to a fully
    # answered page is allowed (the form pre-populates and the user can
    # edit and re-submit).
    next_page = _first_incomplete_page(resp)
    if next_page is not None and page > next_page:
        messages.info(request, _('Please complete the earlier pages first.'))
        return redirect('ailst:page', timepoint=tp.lower(), page=next_page)

    items = _items_for_page(page, language=resp.language)

    if request.method == 'POST':
        with transaction.atomic():
            locked = (
                AilstResponse.objects
                .select_for_update()
                .get(user=request.user, timepoint=tp)
            )
            if locked.completed_at:
                return redirect('ailst:complete', timepoint=tp.lower())

            form = AilstPageForm(
                request.POST,
                items=items,
                existing_responses=locked.responses,
            )
            if form.is_valid():
                merged = dict(locked.responses or {})
                for item in items:
                    merged[item.paper_code] = form.cleaned_data[item.paper_code]
                locked.responses = merged
                locked.save(update_fields=['responses', 'last_saved_at'])

                if page == PAGES and len(merged) == 36:
                    _finalise_completion(locked)
                    return redirect('ailst:complete', timepoint=tp.lower())

                return redirect('ailst:page', timepoint=tp.lower(), page=page + 1)
    else:
        form = AilstPageForm(items=items, existing_responses=resp.responses)

    factor_name, _lo, _hi = PAGE_FACTOR_RANGES[page]
    is_resuming = bool(resp.responses) and page == next_page

    return render(request, 'ailst/page.html', {
        'form': form,
        'items': items,
        'timepoint': tp,
        'timepoint_url': tp.lower(),
        'page': page,
        'total_pages': PAGES,
        'factor_name': factor_name,
        # Progress reported as pages completed before this one.
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
    # D4 (C.2.3 design): scores hidden for all timepoints during the
    # pilot. Post-pilot reveal is TD-010.
    return render(request, 'ailst/complete.html', {
        'response': resp,
        'timepoint': tp,
        'timepoint_url': tp.lower(),
    })


@login_required
def ailst_research_consent_required_view(request, timepoint):
    """Explanation page shown when research_consent=False blocks AILST.

    Provides a path back to profile settings where the user can update
    consent. No data is collected on this page.
    """
    tp = _normalise_timepoint(timepoint)
    return render(request, 'ailst/research_consent_required.html', {
        'timepoint': tp,
        'timepoint_url': tp.lower(),
    })


@login_required
def ailst_restart_view(request, timepoint):
    """Explicit user-initiated restart of an in-progress administration.

    POST-only. Deletes the partial AilstResponse row (only if
    completed_at IS NULL) and redirects to the entry view, where the
    user starts again from the intro page.

    Why this is allowed even though we never auto-delete on consent
    revocation: this is an EXPLICIT user action ("discard my previous
    answers and start over"), not a silent system action triggered by
    a different policy (consent toggle). Two distinct paths, two
    distinct rights — explicit reset is fine; silent deletion is not.

    Completed responses (completed_at IS NOT NULL) cannot be reset
    here: T0/T1/T2 are one-shot baselines and a completed
    administration is the canonical research datum for that timepoint.
    A request against a completed row redirects silently to the
    complete page.
    """
    tp = _normalise_timepoint(timepoint)
    if request.method != 'POST':
        return redirect('ailst:entry', timepoint=tp.lower())

    with transaction.atomic():
        resp = (
            AilstResponse.objects
            .select_for_update()
            .filter(user=request.user, timepoint=tp)
            .first()
        )
        if resp is None:
            return redirect('ailst:entry', timepoint=tp.lower())
        if resp.completed_at is not None:
            return redirect('ailst:complete', timepoint=tp.lower())
        resp.delete()

    messages.info(request, _('Your previous answers were discarded. You can start over now.'))
    return redirect('ailst:entry', timepoint=tp.lower())
