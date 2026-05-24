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

import logging

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
from apps.agents.epilogue_portrait import (
    EPILOGUE_PORTRAIT_REGENERATION_CEILING,
    EpiloguePortraitAgent,
)
from apps.epilogue.models import EpilogueCompletion
from apps.epilogue.services_stage0 import (
    build_stage0_snapshot,
    count_portrait_proposals,
    format_juxtaposition_for_prompt,
    latest_portrait_proposal,
    pick_juxtaposition_for_stage2,
    should_skip_stage2,
    summarise_dialogue_for_portrait,
    summarise_prior_stages_for_stage3,
    summarise_stage0_for_dialogue,
)


def _is_m15_completed(user) -> bool:
    """Phase C TD-013 — M15 completion is the prerequisite for entering
    the Epilogue. Helper isolates the dependency on apps.modules so
    the import remains lazy and the test suites stay decoupled.
    """
    from apps.modules.services import user_has_completed_module
    return user_has_completed_module(user, 'M15')


# G.6c — phase-as-chapter view helper (proposal §4.2).
# Builds the per-phase structured data the dialogue template iterates
# over. Replaces the pre-G.6c flat-scroll layout where every turn from
# every stage rendered in one continuous list — that layout had the
# phase-seam bug (two back-to-back assistant bubbles at a stage
# boundary). The new layout groups turns by phase, marks each phase
# 'collapsed' / 'active' / 'upcoming', and lets the template render
# prior phases as <details> summaries + the active phase as an open
# chapter card with chat bubbles.
_PHASE_DEFINITIONS = [
    (1, 'I',   'Look Back'),
    (2, 'II',  'Look In'),
    (3, 'III', 'Look Forward'),
]


def _build_dialogue_phases(completion, current_stage) -> list[dict]:
    """Group dialogue_turns by phase, mark each phase's display status.

    Returns one record per phase (Stages 1 / 2 / 3), regardless of
    whether that phase has any turns. The template consumes the list
    via _phase_chapter.html — collapsed phases render as <details>
    summaries with a one-line preview; the active phase renders as an
    open chapter card.

    Mapping current_stage → per-phase status:
      - current_stage == 0      → all three phases are 'upcoming'
                                  (dialogue not entered yet — but in
                                  practice the template renders the
                                  dialogue-not-entered path before
                                  this list is built)
      - current_stage == 1      → 1 active, 2/3 upcoming
      - current_stage == 2      → 1 collapsed, 2 active, 3 upcoming
      - current_stage == 3      → 1/2 collapsed, 3 active
      - current_stage =='finished' → all three collapsed (the teacher
                                  is past Stage 3 and ready for the
                                  Portrait button)

    Stage 2 is treated specially when the skip-record applies — its
    record is attached to the phase 2 dict so the template can render
    an editorial skip card in place of the chat bubbles.
    """
    turns = completion.dialogue_turns or []
    skip_record = next(
        (t for t in turns if t.get('event') == 'stage2_skipped'),
        None,
    )

    phases = []
    for number, numeral, name in _PHASE_DEFINITIONS:
        # Status mapping.
        if current_stage == 'finished':
            status = 'collapsed'
        elif isinstance(current_stage, int) and number < current_stage:
            status = 'collapsed'
        elif current_stage == number:
            status = 'active'
        else:
            status = 'upcoming'

        # Visible turns for this phase only (assistant + teacher),
        # in chronological (storage) order.
        phase_turns = [
            t for t in turns
            if t.get('stage') == number
            and t.get('role') in ('assistant', 'teacher')
        ]

        # Last teacher message — used as the collapsed-summary preview
        # so the teacher can recognise prior phases without re-opening
        # them. None if the phase had no teacher reply (e.g. skipped
        # Stage 2 or an interrupted Stage 3).
        teacher_msgs = [
            (t.get('content') or '').strip()
            for t in phase_turns
            if t.get('role') == 'teacher'
        ]
        last_teacher_preview = teacher_msgs[-1] if teacher_msgs else ''

        # Teacher-turn count for the per-phase ceiling (G-D5).
        teacher_turn_count = len(teacher_msgs)

        # Skip-record attaches to Stage 2 only.
        has_skip_record = (number == 2) and (skip_record is not None)

        phases.append({
            'number': number,
            'numeral': numeral,
            'name': name,
            'status': status,
            'turns': phase_turns,
            'last_teacher_preview': last_teacher_preview,
            'teacher_turn_count': teacher_turn_count,
            'has_skip_record': has_skip_record,
            'skip_record': skip_record if has_skip_record else None,
        })

    return phases


def _current_stage(completion):
    """Derive the current dialogue stage from the row state.

    Returns one of:
      0          - not started (dialogue_entered is False)
      1          - in Stage 1 (Look Back)
      2          - in Stage 2 (Look In)
      3          - in Stage 3 (Look Forward)
      'finished' - all three dialogue stages past
    """
    if completion.stage3_completed_at is not None:
        return 'finished'
    if completion.stage2_completed_at is not None:
        return 3
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
                'phases': _build_dialogue_phases(completion, 0),
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
        max_stage_visible = 3
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
        current_stage in (1, 2, 3)
        and teacher_turns_in_current < EPILOGUE_DIALOGUE_TURN_CEILING
    )
    # Advance buttons (G.2c):
    #   Stage 1 -> Stage 2: available once teacher has 1+ Stage 1 reply.
    #   Stage 2 -> Stage 3: available once teacher has 1+ Stage 2 reply.
    #   Stage 3 (no turns yet, after Stage 2 auto-skip): "Continue to
    #     Look Forward" button enters Stage 3.
    #   Stage 3 (with turns): no advance, only finish.
    has_stage3_turns = any(
        t.get('stage') == 3 and t.get('role') in ('assistant', 'teacher')
        for t in completion.dialogue_turns
    )
    if current_stage == 1 and teacher_turns_in_current >= 1:
        can_advance = True
        next_stage_label = 'Continue to Look In'
    elif current_stage == 2 and teacher_turns_in_current >= 1:
        can_advance = True
        next_stage_label = 'Continue to Look Forward'
    elif current_stage == 3 and not has_stage3_turns:
        can_advance = True
        next_stage_label = 'Continue to Look Forward'
    else:
        can_advance = False
        next_stage_label = None
    # G.6c phase-as-chapter context: groups turns per phase and marks
    # each phase's display status. The template renders prior phases
    # as <details> summaries + the active phase as an open chapter
    # card (proposal §4.2 — fixes the phase-seam bug). The flat
    # `turns` / `stage2_skip_record` / `turns_remaining` keys are
    # retained for the (now-removed) pre-G.6c fallback rendering and
    # for backward-compatible tests; the template no longer reads
    # them directly but reading them does no harm.
    phases = _build_dialogue_phases(completion, current_stage)
    return render(request, 'epilogue/dialogue.html', {
        'completion': completion,
        'snapshot': completion.stage0_snapshot,
        'turns': visible_turns,
        'phases': phases,
        'current_stage': current_stage,
        'can_respond': can_respond,
        'can_advance': can_advance,
        'next_stage_label': next_stage_label,
        'stage2_skip_record': stage2_skip_record,
        'turns_remaining': max(
            0, EPILOGUE_DIALOGUE_TURN_CEILING - teacher_turns_in_current,
        ),
        'dialogue_error': False,
    })


# G.6c.4 — after every POST-redirect-GET round-trip, the new page would
# otherwise render at the top — hiding the just-generated assistant reply
# below the sticky header + the Stage 0 evidence panel + the collapsed
# prior phases. The fragment anchor lands the browser on the active
# phase chapter (`id="dialogue-active"` in _phase_chapter.html); the
# scroll-margin-top rule in epilogue.css §7 keeps the chapter clear of
# the sticky header. Used by every redirect TO the dialogue page from
# a POST handler.
from django.urls import reverse as _reverse


def _dialogue_redirect():
    """Redirect to the dialogue page anchored on the active phase
    chapter, so the teacher lands where the conversation is and not
    at the top of the page (proposal §4.2 + G.6c.4 follow-up)."""
    return redirect(_reverse('epilogue:dialogue') + '#dialogue-active')


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
        if stage not in (1, 2, 3):
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
        # G.6c.6 — when the just-appended teacher reply brings the
        # teacher_turn_count to the per-phase ceiling, the agent's
        # response is the structural close of the phase (no more
        # teacher replies possible). Pass the flag so the prompt
        # overrides the default one-open-question rule with a
        # settling acknowledgment. Surfaced from a live Stage 1
        # walkthrough 2026-05-24 where the ceiling-hit reply hung
        # an unanswerable question.
        will_be_final = (
            (teacher_turns + 1) >= EPILOGUE_DIALOGUE_TURN_CEILING
        )
        summary = summarise_stage0_for_dialogue(locked.stage0_snapshot)
        reply = EpilogueDialogueAgent().extract(
            stage=stage, stage0_summary=summary, history=history,
            is_final_in_phase=will_be_final,
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

    return _dialogue_redirect()


def _advance_dialogue(completion):
    """Advance the dialogue to the next stage.

    G.2c: stage 1 -> stage 2 (or skip per section 6.4); stage 2 -> stage 3;
    stage 3 (no turns yet, e.g. after Stage 2 auto-skip) -> enter Stage 3.
    Stage 3 with turns has no advance — the "Finish the Epilogue" form
    routes to /complete instead.

    Returns (success, error_message). error_message is non-None only
    when the transition could not happen (e.g. Gemini failure) and the
    caller surfaces a retry.
    """
    stage = _current_stage(completion)
    if stage == 1:
        return _advance_to_stage2(completion)
    if stage == 2 or stage == 3:
        return _advance_to_stage3(completion)
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


def _advance_to_stage3(completion):
    """Enter Stage 3 (Look Forward). Marks stage2_completed_at if not
    already set, then generates the Stage 3 opening turn. Idempotent:
    if a Stage 3 turn already exists, no-op success.

    Stage 3 has no skip threshold — once reached, it always runs. The
    prior_stages kwarg carries the teacher's last messages from
    Stages 1 and 2 so the agent has their own framing to build on
    (design proposal v2 section 6.3).
    """
    has_stage3 = any(
        t.get('stage') == 3 for t in completion.dialogue_turns
    )
    if has_stage3:
        return True, None

    now_dt = timezone.now()
    now_iso = now_dt.isoformat()
    snapshot = completion.stage0_snapshot or {}
    summary = summarise_stage0_for_dialogue(snapshot)
    prior = summarise_prior_stages_for_stage3(completion.dialogue_turns)
    opening = EpilogueDialogueAgent().extract(
        stage=3,
        stage0_summary=summary,
        history=[],
        prior_stages=prior,
    )
    if opening is None:
        return False, (
            'The reflective assistant could not start the next stage '
            'just now. Please try again.'
        )

    completion.dialogue_turns = list(completion.dialogue_turns) + [{
        'stage': 3,
        'role': 'assistant',
        'content': opening,
        'model': EpilogueDialogueAgent.model_name,
        'generated_at': now_iso,
    }]
    fields = ['dialogue_turns']
    if completion.stage2_completed_at is None:
        completion.stage2_completed_at = now_dt
        fields.append('stage2_completed_at')
    completion.save(update_fields=fields)
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

    return _dialogue_redirect()


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
        # G.2a/b/c: finishing the Epilogue from within the dialogue
        # marks whichever stage the teacher is currently in as
        # complete, for the research record (design proposal v2
        # section 13). A user who skipped the dialogue has
        # dialogue_entered False and no stage timestamp is touched.
        if completion.dialogue_entered:
            stage = _current_stage(completion)
            stage_now = timezone.now()
            if stage == 1 and completion.stage1_completed_at is None:
                completion.stage1_completed_at = stage_now
                update_fields.append('stage1_completed_at')
            elif stage == 2 and completion.stage2_completed_at is None:
                completion.stage2_completed_at = stage_now
                update_fields.append('stage2_completed_at')
            elif stage == 3 and completion.stage3_completed_at is None:
                completion.stage3_completed_at = stage_now
                update_fields.append('stage3_completed_at')
        if update_fields:
            completion.save(update_fields=update_fields)

    return redirect(_post_epilogue_destination(request.user))


# ======================================================================
# G.3 — Learning Portrait (review / regenerate / accept / PDF)
# ======================================================================
#
# Four views implement the Learning Portrait HITL contract from design
# proposal v2 sections 8.4 / 22.1:
#
#   GET  /epilogue/portrait/            -> review the current proposal
#   POST /epilogue/portrait/regenerate/ -> request a fresh proposal
#                                          (bounded to 2 regenerations)
#   POST /epilogue/portrait/accept/     -> accept; atomic write of text
#                                          + PDF + provenance + complete
#   GET  /epilogue/portrait/pdf/        -> download (regen-on-demand)
#
# The "current proposal" and "regen counter" live in
# `EpilogueCompletion.dialogue_turns` as `portrait`-stage events — no
# new schema field, per design proposal v2 section 22.1.

_PORTRAIT_PROPOSAL_CEILING = 1 + EPILOGUE_PORTRAIT_REGENERATION_CEILING

# Cap on PDF regeneration attempts per HTTP request — guards against
# pisa errors quietly looping. One try is enough; an error returns an
# explicit HTTP 500 so the support path is visible.


def _has_completed_dialogue(completion) -> bool:
    """True iff the teacher entered the dialogue AND finished Stage 3.

    The Portrait depends on the dialogue (design proposal v2 sections
    8.1 and 22.2); a skip-dialogue teacher does not see the Portrait at
    all.
    """
    return (
        completion is not None
        and completion.dialogue_entered
        and completion.stage3_completed_at is not None
    )


def _build_portrait_context(completion) -> dict:
    """Stage 0 summary + dialogue summary — the two inputs the Portrait
    agent's `extract()` consumes (design proposal v2 section 8.1)."""
    return {
        'stage0_summary': summarise_stage0_for_dialogue(
            completion.stage0_snapshot or {},
        ),
        'dialogue_summary': summarise_dialogue_for_portrait(
            completion.dialogue_turns or [],
        ),
    }


def _append_portrait_proposal(completion, text: str) -> None:
    """Append a portrait `proposal` event to `dialogue_turns`.

    Mutates the row's `dialogue_turns` in place and calls .save with
    update_fields. The caller is responsible for holding a row lock
    (`select_for_update`) so concurrent regenerations cannot interleave.
    """
    completion.dialogue_turns = list(completion.dialogue_turns) + [{
        'stage': 'portrait',
        'role': 'assistant',
        'event': 'proposal',
        'content': text,
        'model': EpiloguePortraitAgent.model_name,
        'generated_at': timezone.now().isoformat(),
    }]
    completion.save(update_fields=['dialogue_turns'])


@login_required
def epilogue_portrait_view(request):
    """GET /epilogue/portrait/ — the Learning Portrait review page.

    On first entry (no portrait proposal yet) the view generates the
    first proposal via `EpiloguePortraitAgent.extract()`. Subsequent
    visits render the most recent proposal — regeneration happens via
    the companion POST endpoint.

    Gates:
      - M15 completion (TD-013, like the rest of the Epilogue).
      - Dialogue entered AND Stage 3 completed (design proposal v2
        sections 8.1 and 22.2). A skip-dialogue teacher is redirected
        to /epilogue/complete/ — the Portrait does not apply.
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
        return redirect('epilogue:placeholder')
    if not completion.dialogue_entered:
        # Skip-dialogue teachers do not see the Portrait (§22.2).
        return redirect('epilogue:placeholder')

    # G.3.1 hotfix (2026-05-24): the post-G.3 UX changed the Stage 3
    # finish-button into a GET link ("Continue to your Learning
    # Portrait" → GET /epilogue/portrait/). The pre-G.3 G.2c flow had
    # this button as a POST to /epilogue/complete/, which set
    # stage3_completed_at as a side effect; the new GET link does not.
    # So a teacher who clicks Continue-to-Portrait after a substantive
    # Stage 3 exchange (≥1 teacher turn) would hit the gate below with
    # stage3_completed_at = NULL and silently bounce back to the
    # dialogue — surfaced 2026-05-24 during the live §23 verification
    # walkthrough against mavros. Fix here in the same view: if the
    # teacher has at least one Stage 3 teacher turn, treat the visit
    # to the Portrait page as the implicit Stage 3 completion event
    # and set the timestamp idempotently under a row lock. Stage-3
    # research record (turn count + transcript) is unaffected — only
    # the missing timestamp is filled in.
    if completion.stage3_completed_at is None:
        has_stage3_teacher_turn = any(
            t.get('stage') == 3 and t.get('role') == 'teacher'
            for t in completion.dialogue_turns or []
        )
        if not has_stage3_teacher_turn:
            return redirect('epilogue:dialogue')
        with transaction.atomic():
            locked = EpilogueCompletion.objects.select_for_update().get(
                pk=completion.pk,
            )
            if locked.stage3_completed_at is None:
                locked.stage3_completed_at = timezone.now()
                locked.save(update_fields=['stage3_completed_at'])
        completion.refresh_from_db()

    proposal_failed = False

    # First-entry-only proposal generation. If already accepted, do
    # NOT re-extract — the teacher is just viewing the accepted state.
    if (
        latest_portrait_proposal(completion.dialogue_turns) is None
        and not completion.learning_portrait_text
    ):
        with transaction.atomic():
            locked = EpilogueCompletion.objects.select_for_update().get(
                pk=completion.pk,
            )
            if (
                latest_portrait_proposal(locked.dialogue_turns) is None
                and not locked.learning_portrait_text
            ):
                ctx = _build_portrait_context(locked)
                proposed = EpiloguePortraitAgent().extract(**ctx)
                if proposed is None:
                    proposal_failed = True
                else:
                    _append_portrait_proposal(locked, proposed)
        completion.refresh_from_db()

    proposal = latest_portrait_proposal(completion.dialogue_turns)
    proposal_count = count_portrait_proposals(completion.dialogue_turns)
    regenerations_used = max(0, proposal_count - 1)
    regenerations_remaining = max(
        0, EPILOGUE_PORTRAIT_REGENERATION_CEILING - regenerations_used,
    )
    already_accepted = bool(completion.learning_portrait_text)

    # Article 50(2) machine-readable provenance — only after accept.
    # The same lookup is reused in _generate_portrait_pdf; kept inline
    # here to avoid one extra round-trip on the common GET path.
    accepted_provenance = None
    if already_accepted:
        from apps.compliance.models import AIArtefactProvenance
        accepted_provenance = AIArtefactProvenance.objects.filter(
            artefact_kind=EpiloguePortraitAgent.artefact_kind,
            artefact_pk=str(completion.pk),
            user=request.user,
        ).first()

    return render(request, 'epilogue/portrait.html', {
        'completion': completion,
        'snapshot': completion.stage0_snapshot,
        'proposal': proposal,
        'proposal_text': (
            completion.learning_portrait_text
            if already_accepted
            else (proposal.get('content') if proposal else '')
        ),
        'proposal_count': proposal_count,
        'regenerations_used': regenerations_used,
        'regenerations_remaining': regenerations_remaining,
        'already_accepted': already_accepted,
        'proposal_failed': proposal_failed,
        'can_regenerate': (
            not already_accepted and regenerations_remaining > 0
        ),
        'accepted_provenance': accepted_provenance,
        'accepted_provenances': (
            [accepted_provenance] if accepted_provenance else []
        ),
    })


@login_required
@require_POST
def epilogue_portrait_regenerate_view(request):
    """POST /epilogue/portrait/regenerate/ — request a fresh proposal.

    Bounded to `EPILOGUE_PORTRAIT_REGENERATION_CEILING` regenerations
    (design proposal v2 sections 8.4 / 22.1). A POST past the ceiling
    is refused with an informational flash; nothing is written.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        if not _is_m15_completed(request.user):
            messages.info(
                request,
                'The PROODOS Epilogue is available after you complete Module 15.',
            )
            return redirect('users:dashboard')

    completion = EpilogueCompletion.objects.filter(user=request.user).first()
    if completion is None or not _has_completed_dialogue(completion):
        return redirect('epilogue:placeholder')
    if completion.learning_portrait_text:
        # Already accepted; regeneration is closed.
        return redirect('epilogue:portrait')

    with transaction.atomic():
        locked = EpilogueCompletion.objects.select_for_update().get(
            pk=completion.pk,
        )
        if locked.learning_portrait_text:
            return redirect('epilogue:portrait')
        if count_portrait_proposals(
            locked.dialogue_turns,
        ) >= _PORTRAIT_PROPOSAL_CEILING:
            messages.info(
                request,
                'You have used both regenerations. Please review the '
                'current Portrait and accept it, or keep it as your '
                'final version.',
            )
            return redirect('epilogue:portrait')

        ctx = _build_portrait_context(locked)
        proposed = EpiloguePortraitAgent().extract(**ctx)
        if proposed is None:
            messages.warning(
                request,
                'The Portrait could not be regenerated just now. '
                'Please try again.',
            )
            return redirect('epilogue:portrait')
        _append_portrait_proposal(locked, proposed)

    return redirect('epilogue:portrait')


@login_required
@require_POST
def epilogue_portrait_accept_view(request):
    """POST /epilogue/portrait/accept/ — atomic accept + persist + PDF
    + provenance + completion (design proposal v2 section 8.4).

    Atomicity contract (CP-9): the text write, the provenance row, and
    the completion timestamp are inside one `transaction.atomic` block.
    The PDF generation is best-effort inside the block — a pisa failure
    does NOT roll back the text/provenance writes; the PDF view
    regenerates on demand (design proposal v2 section 10.1: "The
    teacher never loses the portrait").

    Idempotent: a second POST after the row is already accepted no-ops
    the writes and re-routes via `_post_epilogue_destination`.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        if not _is_m15_completed(request.user):
            messages.info(
                request,
                'The PROODOS Epilogue is available after you complete Module 15.',
            )
            return redirect('users:dashboard')

    completion = EpilogueCompletion.objects.filter(user=request.user).first()
    if completion is None or not _has_completed_dialogue(completion):
        return redirect('epilogue:placeholder')

    with transaction.atomic():
        locked = EpilogueCompletion.objects.select_for_update().get(
            pk=completion.pk,
        )
        if locked.learning_portrait_text:
            # Idempotent: already accepted; just route forward.
            return redirect(_post_epilogue_destination(request.user))

        proposal = latest_portrait_proposal(locked.dialogue_turns)
        if proposal is None:
            messages.warning(
                request,
                'There is no Portrait to accept yet. Please generate '
                'one first.',
            )
            return redirect('epilogue:portrait')

        now = timezone.now()
        accepted_text = (proposal.get('content') or '').strip()
        proposals = [
            i for i, t in enumerate(locked.dialogue_turns)
            if t.get('stage') == 'portrait'
            and t.get('role') == 'assistant'
            and t.get('event') == 'proposal'
        ]
        accepted_idx = proposals[-1] if proposals else 0

        locked.learning_portrait_text = accepted_text
        locked.learning_portrait_generated_at = now
        locked.dialogue_turns = list(locked.dialogue_turns) + [{
            'stage': 'portrait',
            'role': 'system',
            'event': 'accepted',
            'accepted_proposal_index': accepted_idx,
            'generated_at': now.isoformat(),
        }]
        if locked.completed_at is None:
            locked.completed_at = now

        from apps.compliance.services import record_ai_provenance
        record_ai_provenance(
            artefact_kind=EpiloguePortraitAgent.artefact_kind,
            artefact_pk=locked.pk,
            user=request.user,
            module=None,
            model_name=EpiloguePortraitAgent.model_name,
            generated_at=now,
        )

        # PDF generation is best-effort; a pisa error must not roll
        # back the text/provenance writes.
        try:
            pdf_bytes, pdf_filename = _generate_portrait_pdf(
                locked, request.user,
            )
            from django.core.files.base import ContentFile
            locked.learning_portrait_pdf.save(
                pdf_filename, ContentFile(pdf_bytes), save=False,
            )
        except Exception as exc:
            logging.getLogger(__name__).warning(
                'Learning Portrait PDF generation failed for user %s: %s',
                request.user.pk, exc,
            )

        locked.save(update_fields=[
            'learning_portrait_text',
            'learning_portrait_generated_at',
            'learning_portrait_pdf',
            'dialogue_turns',
            'completed_at',
        ])

    # Land on the same page after accept so the teacher can see
    # the "Download as PDF" and "Continue" buttons in the accepted
    # state (user-facing feedback, 2026-05-23). Routing forward to
    # T2/dashboard happens on the Continue click, which posts to
    # /epilogue/complete/ — already idempotent for completed_at.
    return redirect('epilogue:portrait')


@login_required
def epilogue_portrait_pdf_view(request):
    """GET /epilogue/portrait/pdf/ — download the Learning Portrait PDF.

    Regenerate-on-demand semantics (design proposal v2 section 10.1):
    if `learning_portrait_pdf` is missing but `learning_portrait_text`
    exists, the PDF is regenerated from the stored text and saved
    before being served. The teacher never loses the Portrait.
    """
    completion = EpilogueCompletion.objects.filter(user=request.user).first()
    if completion is None or not completion.learning_portrait_text:
        from django.http import Http404
        raise Http404('No Learning Portrait on record yet.')

    if not completion.learning_portrait_pdf:
        try:
            pdf_bytes, pdf_filename = _generate_portrait_pdf(
                completion, request.user,
            )
        except Exception as exc:
            from django.http import HttpResponse
            logging.getLogger(__name__).error(
                'Learning Portrait PDF regeneration failed for user %s: %s',
                request.user.pk, exc,
            )
            return HttpResponse(
                'The Learning Portrait PDF could not be generated.',
                status=500,
            )
        from django.core.files.base import ContentFile
        with transaction.atomic():
            locked = EpilogueCompletion.objects.select_for_update().get(
                pk=completion.pk,
            )
            if not locked.learning_portrait_pdf:
                locked.learning_portrait_pdf.save(
                    pdf_filename, ContentFile(pdf_bytes), save=True,
                )
            completion = locked

    from django.http import FileResponse
    completion.learning_portrait_pdf.open('rb')
    return FileResponse(
        completion.learning_portrait_pdf,
        as_attachment=True,
        filename=f'PROODOS_Learning_Portrait_{request.user.username}.pdf',
        content_type='application/pdf',
    )


def _generate_portrait_pdf(completion, user) -> tuple:
    """Render the Learning Portrait as a PDF via xhtml2pdf.

    Returns `(pdf_bytes, filename)`. Raises on pisa error so the caller
    can decide between "fail this request" (download view) and
    "swallow and let regen-on-demand handle it later" (accept view).

    Article 50(2) marker (design proposal v2 sections 8.5 and 22.3):
    the rendered HTML carries the `{% ai_provenance_jsonld %}` block;
    PDF document metadata (Title / Author / Subject / Creator) is set
    via `<meta>` tags in the template head — xhtml2pdf reads these and
    writes them into the PDF metadata layer.
    """
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa
    import io

    from apps.compliance.models import AIArtefactProvenance

    provenance = AIArtefactProvenance.objects.filter(
        artefact_kind=EpiloguePortraitAgent.artefact_kind,
        artefact_pk=str(completion.pk),
        user=user,
    ).first()

    teacher_display = (
        user.get_full_name() or user.username or 'PROODOS teacher'
    )

    context = {
        'portrait_text': completion.learning_portrait_text,
        'snapshot': completion.stage0_snapshot or {},
        'teacher_display': teacher_display,
        'generated_at': completion.learning_portrait_generated_at,
        'model_name': EpiloguePortraitAgent.model_name,
        'provenance': provenance,
        'provenances': [provenance] if provenance else [],
    }
    html = render_to_string('pdf/learning_portrait.html', context)

    buf = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buf, encoding='utf-8')
    if result.err:
        raise RuntimeError(f'pisa.CreatePDF reported {result.err} errors')

    filename = f'PROODOS_Learning_Portrait_{user.username}.pdf'
    return buf.getvalue(), filename


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
