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
    format_juxtaposition_for_prompt,
    pick_juxtaposition_for_stage2,
    should_skip_stage2,
    summarise_stage0_for_dialogue,
)


def _is_m15_completed(user) -> bool:
    """Phase C TD-013 — M15 completion is the prerequisite for entering
    the Epilogue. Helper isolates the dependency on apps.modules so
    the import remains lazy and the test suites stay decoupled.
    """
    from apps.modules.services import user_has_completed_module
    return user_has_completed_module(user, 'M15')


def _current_stage(completion):
    """Derive the current dialogue stage from the row state.

    Returns one of:
      0          - not started (dialogue_entered is False)
      1          - in Stage 1 (Look Back)
      2          - in Stage 2 (Look In)
      'finished' - all implemented dialogue stages past

    Stage 3 (Look Forward) lands in G.2c; until then, stage2_completed_at
    set marks the dialogue as 'finished' (the teacher is now ready to
    submit the Epilogue and route to T2).
    """
    if completion.stage2_completed_at is not None:
        return 'finished'
    if completion.stage1_completed_at is not None:
        return 2
    if completion.dialogue_entered:
        return 1
    return 0


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
                'can_advance': False,
                'next_stage_label': None,
                'current_stage': 0,
                'stage2_skip_record': None,
                'dialogue_error': True,
            })

    current_stage = _current_stage(completion)
    # Visible turns: assistant + teacher turns across all stages up to
    # the current one, in chronological order. System (skip) records
    # are excluded; the skip note is surfaced separately for the
    # template.
    if current_stage == 'finished':
        max_stage_visible = 2
    elif isinstance(current_stage, int):
        max_stage_visible = current_stage
    else:
        max_stage_visible = 0
    visible_turns = [
        t for t in completion.dialogue_turns
        if t.get('role') in ('assistant', 'teacher')
        and t.get('stage', 0) <= max_stage_visible
    ]
    teacher_turns_in_current = sum(
        1 for t in visible_turns
        if t.get('role') == 'teacher' and t.get('stage') == current_stage
    )
    stage2_skip_record = None
    for t in completion.dialogue_turns:
        if t.get('event') == 'stage2_skipped':
            stage2_skip_record = t
            break
    can_respond = (
        current_stage in (1, 2)
        and teacher_turns_in_current < EPILOGUE_DIALOGUE_TURN_CEILING
    )
    # Stage 1 -> Stage 2 advance is available once the teacher has
    # answered the opening at least once. Stage 2 -> Stage 3 is G.2c;
    # for now Stage 2 has no advance, only finish.
    can_advance_from_stage1 = (
        current_stage == 1 and teacher_turns_in_current >= 1
    )
    return render(request, 'epilogue/dialogue.html', {
        'completion': completion,
        'snapshot': completion.stage0_snapshot,
        'turns': visible_turns,
        'current_stage': current_stage,
        'can_respond': can_respond,
        'can_advance': can_advance_from_stage1,
        'next_stage_label': (
            'Continue to Look In' if can_advance_from_stage1 else None
        ),
        'stage2_skip_record': stage2_skip_record,
        'turns_remaining': max(
            0, EPILOGUE_DIALOGUE_TURN_CEILING - teacher_turns_in_current,
        ),
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
        stage = _current_stage(locked)
        if stage not in (1, 2):
            # Not in an active dialogue stage; nothing to handle.
            return redirect('epilogue:dialogue')
        stage_turns = [
            t for t in locked.dialogue_turns
            if t.get('stage') == stage
            and t.get('role') in ('assistant', 'teacher')
        ]
        teacher_turns = sum(
            1 for t in stage_turns if t.get('role') == 'teacher'
        )
        if teacher_turns >= EPILOGUE_DIALOGUE_TURN_CEILING:
            return redirect('epilogue:dialogue')

        history = [
            {'role': t['role'], 'content': t['content']}
            for t in stage_turns
        ]
        history.append({'role': 'teacher', 'content': message})
        summary = summarise_stage0_for_dialogue(locked.stage0_snapshot)
        reply = EpilogueDialogueAgent().extract(
            stage=stage, stage0_summary=summary, history=history,
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
            {'stage': stage, 'role': 'teacher', 'content': message,
             'generated_at': now},
            {'stage': stage, 'role': 'assistant', 'content': reply,
             'model': EpilogueDialogueAgent.model_name,
             'generated_at': now},
        ]
        locked.save(update_fields=['dialogue_turns'])

    return redirect('epilogue:dialogue')


def _advance_dialogue(completion):
    """Advance the dialogue to the next stage.

    For G.2b: from Stage 1 -> Stage 2 (or skip per design proposal v2
    section 6.4). From Stage 2 there is no Stage 3 yet (G.2c); the
    template routes from Stage 2 / 'finished' to /complete directly.

    Returns (success, error_message) - error_message is non-None only
    when the transition could not happen (e.g. Stage 2 opening Gemini
    failure) and the caller surfaces a retry.
    """
    stage = _current_stage(completion)
    if stage == 1:
        return _advance_to_stage2(completion)
    return False, None


def _advance_to_stage2(completion):
    """Transition from Stage 1 to Stage 2. Marks stage1_completed_at,
    then either generates the Stage 2 opening turn (if the snapshot has
    juxtaposition material) or logs a skip record (design proposal v2
    section 6.4).
    """
    now_dt = timezone.now()
    now_iso = now_dt.isoformat()
    snapshot = completion.stage0_snapshot or {}

    if should_skip_stage2(snapshot):
        q = snapshot.get('quantitative') or {}
        completion.dialogue_turns = list(completion.dialogue_turns) + [{
            'stage': 2,
            'role': 'system',
            'event': 'stage2_skipped',
            'reason': 'insufficient_juxtaposition_material',
            'metrics': {
                'distinct_tensions': q.get('distinct_tensions', 0),
                'dtp_composites_with_shift': q.get(
                    'dtp_composites_with_shift', 0,
                ),
            },
            'generated_at': now_iso,
        }]
        completion.stage1_completed_at = now_dt
        completion.stage2_completed_at = now_dt
        completion.save(update_fields=[
            'dialogue_turns', 'stage1_completed_at', 'stage2_completed_at',
        ])
        return True, None

    juxtaposition = pick_juxtaposition_for_stage2(snapshot)
    if juxtaposition is None:
        # No clean juxtaposition; skip with a different reason for the
        # research record.
        completion.dialogue_turns = list(completion.dialogue_turns) + [{
            'stage': 2,
            'role': 'system',
            'event': 'stage2_skipped',
            'reason': 'no_clean_juxtaposition_available',
            'generated_at': now_iso,
        }]
        completion.stage1_completed_at = now_dt
        completion.stage2_completed_at = now_dt
        completion.save(update_fields=[
            'dialogue_turns', 'stage1_completed_at', 'stage2_completed_at',
        ])
        return True, None

    summary = summarise_stage0_for_dialogue(snapshot)
    juxtaposition_text = format_juxtaposition_for_prompt(juxtaposition)
    opening = EpilogueDialogueAgent().extract(
        stage=2,
        stage0_summary=summary,
        history=[],
        juxtaposition=juxtaposition_text,
    )
    if opening is None:
        return False, (
            'The reflective assistant could not start the next stage '
            'just now. Please try again.'
        )

    completion.dialogue_turns = list(completion.dialogue_turns) + [{
        'stage': 2,
        'role': 'assistant',
        'content': opening,
        'model': EpilogueDialogueAgent.model_name,
        'generated_at': now_iso,
    }]
    completion.stage1_completed_at = now_dt
    completion.save(update_fields=[
        'dialogue_turns', 'stage1_completed_at',
    ])
    return True, None


@login_required
@require_POST
def epilogue_dialogue_advance_view(request):
    """POST /epilogue/dialogue/advance/ — explicit transition from the
    current dialogue stage to the next one. Marks the current stage
    complete and, if entering Stage 2, either generates the opening
    turn or logs a skip record per the section 6.4 threshold.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        if not _is_m15_completed(request.user):
            messages.info(
                request,
                'The PROODOS Epilogue is available after you complete Module 15.',
            )
            return redirect('users:dashboard')

    completion = EpilogueCompletion.objects.filter(user=request.user).first()
    if completion is None or not completion.dialogue_entered:
        return redirect('epilogue:dialogue')

    with transaction.atomic():
        locked = EpilogueCompletion.objects.select_for_update().get(
            pk=completion.pk,
        )
        success, error = _advance_dialogue(locked)
        if not success and error:
            messages.warning(request, error)

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
