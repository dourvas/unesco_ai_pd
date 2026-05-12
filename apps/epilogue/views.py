"""
Views for the PROODOS Epilogue placeholder feature (C.2.5).

Two views:

  - epilogue_placeholder_view (GET): renders templates/epilogue/placeholder.html
    and ensures an EpilogueCompletion row exists for the user (creates
    one on first visit so started_at is captured).
  - epilogue_complete_view (POST): flips completed_at = NOW, then
    redirects to /ailst/t2/ if the user has active research_consent and
    has not yet completed T2; otherwise sends them to the dashboard.

Per D4 of the C.2.5 design proposal, the Epilogue itself has no consent
gate: it is a pedagogical feature, not a research instrument. The T2
gate is enforced downstream by the AILST entry view.

The full Epilogue spec (Stage 0 dashboard, Stages 1-3 Gemini dialogue,
Learning Portrait PDF) is tracked as TD-011 and will replace this
placeholder later.
"""

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.epilogue.models import EpilogueCompletion


def _is_m15_completed(user) -> bool:
    """Phase C TD-013 — M15 completion is the prerequisite for entering
    the Epilogue. Helper isolates the dependency on apps.modules so
    the import remains lazy and the test suites stay decoupled.
    """
    from apps.modules.services import user_has_completed_module
    return user_has_completed_module(user, 'M15')


@login_required
def epilogue_placeholder_view(request):
    """GET /epilogue/ — placeholder page until TD-011 lands.

    Creates an EpilogueCompletion row on first visit so the start
    timestamp is captured for research-design accounting.

    Phase C TD-013: blocked unless the user has completed M15. Staff
    and superusers bypass for support. A blocked user is redirected
    to the dashboard with an informational flash; the dashboard
    nudge banner (when added) can point them at the next-up module.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        if not _is_m15_completed(request.user):
            from django.contrib import messages
            messages.info(
                request,
                'The PROODOS Epilogue is available after you complete Module 15.',
            )
            return redirect('users:dashboard')

    EpilogueCompletion.objects.get_or_create(user=request.user)

    completion = EpilogueCompletion.objects.get(user=request.user)
    return render(request, 'epilogue/placeholder.html', {
        'completion': completion,
        'already_completed': completion.completed_at is not None,
    })


@login_required
@require_POST
def epilogue_complete_view(request):
    """POST /epilogue/complete/ — flip completed_at, then route forward.

    Forward routing:
      - if user has research_consent and T2 not yet completed -> /ailst/t2/
      - otherwise -> /dashboard/

    Idempotent: a second POST after the row is already completed does
    not change completed_at and still routes the user forward according
    to the same rules.

    Phase C TD-013: defensive mirror of the GET gate. Even though a
    crafted POST without M15 completion would fail the GET gate first
    (the user would never see the Submit button), accept the request
    only when M15 is done. Staff and superusers bypass.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        if not _is_m15_completed(request.user):
            from django.contrib import messages
            messages.info(
                request,
                'The PROODOS Epilogue is available after you complete Module 15.',
            )
            return redirect('users:dashboard')

    with transaction.atomic():
        completion, _ = EpilogueCompletion.objects.select_for_update().get_or_create(
            user=request.user,
        )
        if completion.completed_at is None:
            completion.completed_at = timezone.now()
            completion.save(update_fields=['completed_at'])

    return redirect(_post_epilogue_destination(request.user))


def _post_epilogue_destination(user):
    """Compute the URL to send the user to after Epilogue completion.

    Mirrors the AILST gating philosophy: T2 is only reachable for
    research-consenting users who have not already completed it. The
    AILST entry view also enforces this; the check here is to avoid
    the unnecessary redirect hop for the common 'non-consenting' /
    'already done' cases.
    """
    from apps.ailst.models import AilstResponse

    profile = getattr(user, 'teacher_profile', None)
    if profile is None or not profile.research_consent:
        return '/dashboard/'

    t2_completed = AilstResponse.objects.filter(
        user=user, timepoint='T2', completed_at__isnull=False,
    ).exists()
    if t2_completed:
        return '/dashboard/'

    return '/ailst/t2/'
