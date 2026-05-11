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
    completed (completed_at set). The Epilogue is one-shot; replays are
    not currently allowed at the data model level.

    Future expansion (TD-011): add per-stage timestamps
    (stage0_completed_at .. stage3_completed_at), Gemini turn log
    (JSONField), generated Learning Portrait text + PDF path.
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
            'Set when the user clicks "Mark complete and continue" on the '
            'placeholder page (or, in the future spec, when Stage 3 is '
            'finished and the Learning Portrait is generated).'
        ),
    )

    class Meta:
        db_table = 'epilogue_completions'
        verbose_name = 'PROODOS Epilogue completion'
        verbose_name_plural = 'PROODOS Epilogue completions'
        ordering = ['-started_at']

    def __str__(self):
        state = 'completed' if self.completed_at else 'in progress'
        return f'{self.user.username} | Epilogue [{state}]'
