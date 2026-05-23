"""
Models for the PROODOS Epilogue feature.

The Epilogue is a methodologically distinct post-completion feature that
sits AFTER M1-M15 and is NOT a 16th module. The full spec
(M16_CAPSTONE_REFLECTION_SPEC.md + April 2026 patch) defines four stages:

    Stage 0: Personal Evolution Dashboard
    Stage 1: Look Back  (Gemini dialogue, ≤150 words per response)
    Stage 2: Look In    (tension surfacing, ≤5 turns total)
    Stage 3: Look Forward (commitment to change)
    Output:  Learning Portrait PDF (300-400 words)

Phase C C.2.5 introduces a placeholder implementation: a single
completion row per user that is flipped to completed_at = NOW when the
user clicks the "Mark complete and continue" button on the placeholder
page. This unblocks the T2 AILST trigger reroute (M15 -> Epilogue -> T2)
without committing to the final UI / Gemini dialogue / PDF export
mechanics. TD-011 tracks the full implementation.

Lifecycle states:
    just-visited:  started_at=NOW, completed_at=NULL  (row exists, page seen)
    completed:     started_at, completed_at both set  (user clicked through)
"""

from django.contrib.auth.models import User
from django.db import models


class EpilogueCompletion(models.Model):
    """One row per user. Tracks the lifecycle of the Epilogue feature.

    OneToOne with auth.User: a user either has not started the Epilogue
    (no row), is in progress (row exists, completed_at NULL), or has
    completed (completed_at set). The Epilogue is one-shot; the OneToOne
    constraint enforces that invariant at the database level. Replay is
    out of pilot scope — see TD-022.

    Phase G (G.0) extends this model with the frozen Stage 0 snapshot,
    the three-phase dialogue log, and the Learning Portrait fields.
    Design: proodos_files/PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2_20260521.md.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='epilogue_completion',
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Set when the user first lands on /epilogue/.',
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            'Set when the user finishes the Epilogue — after Stage 3 and '
            'Learning Portrait acceptance, or when they skip the dialogue. '
            'NULL means started but not yet finished.'
        ),
    )

    # --- Phase G (G.0): Stage 0 — Personal Evolution Dashboard ---
    stage0_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            'Frozen Stage 0 semantic payload (DTP theme-evolution, RTM '
            'tension trajectories, quantitative summary). Computed once on '
            'first entry and rendered live from this JSON; never HTML.'
        ),
    )
    stage0_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Set when the user first views the Stage 0 dashboard.',
    )

    # --- Phase G (G.0): Stages 1-3 — reflective dialogue ---
    dialogue_entered = models.BooleanField(
        default=False,
        help_text=(
            'True once the user enters the Stage 1-3 dialogue; False means '
            'they chose to skip it. Q5 measured variable.'
        ),
    )
    stage1_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Set when Stage 1 (Look Back) finishes.',
    )
    stage2_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Set when Stage 2 (Look In) finishes or is skipped.',
    )
    stage3_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Set when Stage 3 (Look Forward) finishes.',
    )
    dialogue_turns = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            'Conversation log: [{stage, role, content, model, '
            'generated_at}], plus any stage-skip records.'
        ),
    )
    # G.3 (design proposal v2 section 22.1): `dialogue_turns` also stores
    # the portrait-stage proposal / accepted events
    #   {stage: 'portrait', role: 'assistant', event: 'proposal',
    #    content, model, generated_at}
    #   {stage: 'portrait', role: 'system', event: 'accepted',
    #    accepted_proposal_index, generated_at}
    # The help_text above is kept unchanged so this is a code-only
    # documentation change — no migration generated (the field shape
    # is identical).

    # --- Phase G (G.0): Learning Portrait ---
    learning_portrait_text = models.TextField(
        blank=True,
        default='',
        help_text='The accepted Learning Portrait narrative (300-400 words).',
    )
    learning_portrait_pdf = models.FileField(
        upload_to='epilogue_portraits/',
        null=True,
        blank=True,
        help_text='Generated Learning Portrait PDF.',
    )
    learning_portrait_generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Set when the user accepts the Learning Portrait.',
    )

    class Meta:
        db_table = 'epilogue_completions'
        verbose_name = 'PROODOS Epilogue completion'
        verbose_name_plural = 'PROODOS Epilogue completions'
        ordering = ['-started_at']

    def __str__(self):
        state = 'completed' if self.completed_at else 'in progress'
        return f'{self.user.username} | Epilogue [{state}]'
