"""
Views for the PROODOS Epilogue placeholder feature (C.2.5).

Two views:

  - epilogue_placeholder_view (GET): renders Stage 0, the Personal
    Evolution Dashboard (templates/epilogue/stage0.html). On the user's
    first entry it aggregates and freezes the Stage 0 snapshot.
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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.agents.epilogue_dialogue import (
    EPILOGUE_DIALOGUE_TURN_CEILING,
    EpilogueDialogueAgent,
)
from apps.epilogue.models import EpilogueCompletion
from apps.epilogue.services_stage0 import (
    build_stage0_snapshot,
    summarise_stage0_for_dialogue,
)


def _is_m15_completed(user) -> bool:
    """Phase C TD-013 — M15 completion is the prerequisite for entering
    the Epilogue. Helper isolates the dependency on apps.modules so
    the import remains lazy and the test suites stay decoupled.
    """
    from apps.modules.services import user_has_completed_module
    return user_has_completed_module(user, 'M15')


@login_required
def epilogue_placeholder_view(request):
    """GET /epilogue/ — the PROODOS Epilogue entry point (Stage 0).

    Phase G G.1: renders Stage 0, the Personal Evolution Dashboard.
    On the user's first entry the Stage 0 snapshot is aggregated from
    their DTP and RTM data and frozen into
    EpilogueCompletion.stage0_snapshot (first-entry-only — design
    proposal v2 section 5.4). Revisits render the stored snapshot
    unchanged, so the Learning Portrait stays reproducible.

    Phase C TD-013: blocked unless the user has completed M15. Staff
    and superusers bypass for support; a blocked user is redirected to
    the dashboard with an informational flash.
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
        # First-entry-only freeze: compute the Stage 0 snapshot once.
        if not completion.stage0_snapshot:
            completion.stage0_snapshot = build_stage0_snapshot(request.user)
            completion.stage0_seen_at = timezone.now()
            completion.save(
                update_fields=['stage0_snapshot', 'stage0_seen_at'],
            )

    return render(request, 'epilogue/stage0.html', {
        'completion': completion,
        'snapshot': completion.stage0_snapshot,
        'already_completed': completion.completed_at is not None,
    })


@login_required
def epilogue_dialogue_view(request):
    """GET + POST /epilogue/dialogue/ — Stage 1 (Look Back) of the
    Epilogue reflective dialogue (Phase G, G.2a).

    GET renders the dialogue; on first entry it marks dialogue_entered
    and generates the opening assistant turn. POST handles one teacher
    message (Post/Redirect/Get). The dialogue is optional (Q5) and is
    reached from Stage 0; the M15 gate still applies.

    Stages 2 and 3 land in G.2b / G.2c; G.2a runs Stage 1 only.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        if not _is_m15_completed(request.user):
            messages.info(
                request,
                'The PROODOS Epilogue is available after you complete Module 15.',
            )
            return redirect('users:dashboard')

    completion = EpilogueCompletion.objects.filter(user=request.user).first()
    if completion is None or not completion.stage0_snapshot:
        # The dialogue builds on the frozen Stage 0 snapshot; if the
        # user has not been through Stage 0, send them there first.
        return redirect('epilogue:placeholder')

    if request.method == 'POST':
        return _handle_dialogue_turn(request, completion)

    if not completion.dialogue_entered:
        if not _enter_dialogue(completion):
            return render(request, 'epilogue/dialogue.html', {
                'completion': completion,
                'snapshot': completion.stage0_snapshot,
                'turns': [],
                'can_respond': False,
                'dialogue_error': True,
            })

    stage1_turns = [
        t for t in completion.dialogue_turns if t.get('stage') == 1
    ]
    teacher_turns = sum(
        1 for t in stage1_turns if t.get('role') == 'teacher'
    )
    return render(request, 'epilogue/dialogue.html', {
        'completion': completion,
        'snapshot': completion.stage0_snapshot,
        'turns': stage1_turns,
        'can_respond': teacher_turns < EPILOGUE_DIALOGUE_TURN_CEILING,
        'turns_remaining': EPILOGUE_DIALOGUE_TURN_CEILING - teacher_turns,
        'dialogue_error': False,
    })


def _enter_dialogue(completion) -> bool:
    """Generate the Stage 1 opening turn and mark the dialogue entered.

    Returns False if the opening turn could not be generated (Gemini
    failure); dialogue_entered stays False so a page reload retries
    (design proposal v2 section 10.1).
    """
    with transaction.atomic():
        locked = EpilogueCompletion.objects.select_for_update().get(
            pk=completion.pk,
        )
        if locked.dialogue_entered:
            completion.refresh_from_db()
            return True

        summary = summarise_stage0_for_dialogue(locked.stage0_snapshot)
        opening = EpilogueDialogueAgent().extract(
            stage=1, stage0_summary=summary, history=[],
        )
        if opening is None:
            return False

        locked.dialogue_turns = list(locked.dialogue_turns) + [{
            'stage': 1,
            'role': 'assistant',
            'content': opening,
            'model': EpilogueDialogueAgent.model_name,
            'generated_at': timezone.now().isoformat(),
        }]
        locked.dialogue_entered = True
        locked.save(update_fields=['dialogue_turns', 'dialogue_entered'])

    completion.refresh_from_db()
    return True


def _handle_dialogue_turn(request, completion):
    """Process one teacher message in the Stage 1 dialogue.

    Stores the teacher message and the agent's reply together — never a
    partial turn (design proposal v2 section 10.1). Enforces the
    per-phase turn ceiling (G-D5). Post/Redirect/Get throughout.
    """
    message = (request.POST.get('message') or '').strip()
    if not message:
        return redirect('epilogue:dialogue')

    with transaction.atomic():
        locked = EpilogueCompletion.objects.select_for_update().get(
            pk=completion.pk,
        )
        stage1_turns = [
            t for t in locked.dialogue_turns if t.get('stage') == 1
        ]
        teacher_turns = sum(
            1 for t in stage1_turns if t.get('role') == 'teacher'
        )
        if teacher_turns >= EPILOGUE_DIALOGUE_TURN_CEILING:
            return redirect('epilogue:dialogue')

        history = [
            {'role': t['role'], 'content': t['content']}
            for t in stage1_turns
        ]
        history.append({'role': 'teacher', 'content': message})
        summary = summarise_stage0_for_dialogue(locked.stage0_snapshot)
        reply = EpilogueDialogueAgent().extract(
            stage=1, stage0_summary=summary, history=history,
        )
        if reply is None:
            messages.warning(
                request,
                'The reflective assistant could not respond just now. '
                'Please send your message again.',
            )
            return redirect('epilogue:dialogue')

        now = timezone.now().isoformat()
        locked.dialogue_turns = list(locked.dialogue_turns) + [
            {'stage': 1, 'role': 'teacher', 'content': message,
             'generated_at': now},
            {'stage': 1, 'role': 'assistant', 'content': reply,
             'model': EpilogueDialogueAgent.model_name,
             'generated_at': now},
        ]
        locked.save(update_fields=['dialogue_turns'])

    return redirect('epilogue:dialogue')


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
        update_fields = []
        if completion.completed_at is None:
            completion.completed_at = timezone.now()
            update_fields.append('completed_at')
        # G.2a: finishing the Epilogue from within the dialogue marks
        # the Stage 1 (Look Back) phase complete, for the research
        # record (design proposal v2 section 13). A user who skipped
        # the dialogue has dialogue_entered False and no stage timestamp.
        if completion.dialogue_entered and completion.stage1_completed_at is None:
            completion.stage1_completed_at = timezone.now()
            update_fields.append('stage1_completed_at')
        if update_fields:
            completion.save(update_fields=update_fields)

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
