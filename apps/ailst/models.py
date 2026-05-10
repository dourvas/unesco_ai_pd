"""
AILST instrument storage models.

AILST = AI Literacy Scale for Teachers (Ning et al. 2025,
Education and Information Technologies 30:17769-17803).

Phase C M4 introduced AilstItem. Phase C M5 introduces AilstResponse
(per-user-per-timepoint) and the scoring helper at apps.ailst.scoring.
"""

from django.contrib.auth.models import User
from django.db import models


class AilstItem(models.Model):
    """One row per (item, language, instrument_version) of the AILST scale.

    Source: Ning et al. 2025 Appendix. EN seed at C.2 launch; EL added
    later via separate seed load (no schema change needed, just new rows
    with language='el').

    Two identifiers are kept:
      - item_number (1-36, monotonic): drives UI ordering and progress
        ('Question N of 36'). Within the EN/v1 dataset:
          1-10  = P1-P10  (perception)
          11-20 = K1-K10  (knowledge_skills)
          21-28 = A3-A10  (applications_innovation; A1+A2 removed by paper EFA)
          29-36 = E1, E3-E5, E7-E10 (ethics; E2+E6 removed)
      - paper_code (P1, K10, A3, E7 etc.): the paper's semantic label.
        Used as key in AilstResponse.responses JSONB. Joins items to responses.
    """

    FACTOR_CHOICES = [
        ('perception', 'AI Perception'),
        ('knowledge_skills', 'AI Knowledge and Skills'),
        ('applications_innovation', 'AI Applications and Innovation'),
        ('ethics', 'AI Ethics'),
    ]
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('el', 'Greek'),
    ]

    item_number = models.IntegerField(
        help_text=(
            "Monotonic 1-36 within (language, instrument_version). "
            "Drives UI ordering and 'Question N of 36' progress."
        ),
    )
    paper_code = models.CharField(
        max_length=10,
        help_text=(
            "Paper's semantic label (P1, K10, A3, E7 etc.). Used as key "
            "in AilstResponse.responses JSONB. Joins items to responses."
        ),
    )
    factor = models.CharField(max_length=30, choices=FACTOR_CHOICES)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    item_text = models.TextField(
        help_text=(
            "The Likert prompt the teacher reads. Must NOT be edited "
            "post-deployment (validated instrument; altering invalidates "
            "measurement). For corrections or translations, mint a new "
            "instrument_version instead."
        ),
    )
    is_reverse_scored = models.BooleanField(
        default=False,
        help_text=(
            "If True, scoring computes 6 - raw response. Per Ning et al. 2025, "
            "exactly K1, A3, E3 are reverse-scored (negation-framed items)."
        ),
    )
    instrument_version = models.CharField(
        max_length=20,
        default='ning_2025_v1',
        help_text=(
            "Versioning anchor. Future cultural/IRB adaptations get new "
            "version strings (e.g., 'ning_2025_v1_ihu_adapted'). Existing "
            "responses keep their version, preserving comparability. "
            "Current platform default is set in settings.AILST_CURRENT_VERSION."
        ),
    )

    class Meta:
        db_table = 'ailst_items'
        verbose_name = 'AILST Item'
        verbose_name_plural = 'AILST Items'
        unique_together = [
            ('item_number', 'language', 'instrument_version'),
            ('paper_code', 'language', 'instrument_version'),
        ]
        indexes = [
            models.Index(
                fields=['language', 'instrument_version', 'factor', 'item_number'],
                name='idx_ailst_items_lookup',
            ),
            models.Index(
                fields=['paper_code'],
                name='idx_ailst_items_papercode',
            ),
        ]
        ordering = ['language', 'instrument_version', 'item_number']

    def __str__(self):
        return f'{self.paper_code} [{self.language}/{self.instrument_version}]'


class AilstResponse(models.Model):
    """One row per (user, timepoint) administration of the AILST.

    Lifecycle states:
      - just-started: started_at=NOW, completed_at=NULL, responses={}
      - in-progress:  responses contains 1-35 paper_code keys, completed_at=NULL
      - completed:    responses has all 36 keys, scores filled, completed_at=NOW

    Raw responses are the source of truth. Score columns are derived/cached
    for fast analytics; recomputable from `responses` via management command
    `recompute_ailst_scores` if the scoring formula ever changes.

    Concurrency: at submit time, views must hold `select_for_update()` on the
    row to avoid race conditions on partial-fill double-submits.
    """

    TIMEPOINT_CHOICES = [
        ('T0', 'T0 - post-onboarding baseline'),
        ('T1', 'T1 - post-M5'),
        ('T2', 'T2 - post-M15'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ailst_responses',
    )
    timepoint = models.CharField(max_length=3, choices=TIMEPOINT_CHOICES)
    language = models.CharField(
        max_length=5,
        default='en',
        help_text="Mirrors AilstItem.language for the items shown to this user.",
    )
    instrument_version = models.CharField(
        max_length=20,
        default='ning_2025_v1',
        help_text=(
            "Pinned at row creation; immutable thereafter. View layer reads "
            "settings.AILST_CURRENT_VERSION at first save."
        ),
    )

    # Raw responses — source of truth, paper-code keyed.
    responses = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            '{"P1": 4, "K10": 2, ..., "E10": 3} with raw 1-5 values. Anchor '
            "mapping: 5=Fully applicable, 1=Completely not applicable. "
            "Reverse-scoring (K1, A3, E3) applied at compute time, not at "
            "storage."
        ),
    )

    # Derived/cached scores. Filled by compute_and_save_scores().
    perception_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    knowledge_skills_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    applications_innovation_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    ethics_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    overall_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    # Lifecycle timestamps.
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_saved_at = models.DateTimeField(
        auto_now=True,
        help_text=(
            "Touched on every page save during partial fill. Useful for "
            "abandonment analytics: completed_at=NULL AND last_saved_at < "
            "NOW - 7d implies abandoned."
        ),
    )

    class Meta:
        db_table = 'ailst_responses'
        verbose_name = 'AILST Response'
        verbose_name_plural = 'AILST Responses'
        unique_together = [('user', 'timepoint')]
        indexes = [
            # (user, timepoint) unique already provides a composite index
            # for user lookups; no separate user-only index needed.
            models.Index(fields=['timepoint', 'completed_at'],
                         name='idx_ailst_resp_timepoint_done'),
        ]
        constraints = [
            # Research design constant: 3 timepoints fixed. DB-level CHECK
            # protects against typos / raw-SQL inserts that would silently
            # break the M1/M6/certificate gating logic.
            models.CheckConstraint(
                condition=models.Q(timepoint__in=['T0', 'T1', 'T2']),
                name='valid_timepoint',
            ),
        ]
        ordering = ['-started_at']

    def __str__(self):
        if self.completed_at:
            state = 'completed'
        else:
            state = f'in progress ({len(self.responses or {})}/36)'
        return f'{self.user.username} | {self.timepoint} [{state}]'

    def compute_and_save_scores(self, items_by_code=None):
        """Compute factor + overall scores from self.responses, persist.

        Idempotent: running twice on unchanged responses yields identical
        scores. Caller responsibility: only invoke when self.responses has
        all 36 keys (full instrument completed). Partial-fill compute is
        defensive — overall_score is None unless all four factors have
        scores.

        Args:
            items_by_code: optional dict {paper_code: AilstItem} to avoid
                re-querying when batch-recomputing. If None, queries items
                matching self.language + self.instrument_version.
        """
        from .scoring import compute_factor_scores

        if items_by_code is None:
            items_by_code = {
                it.paper_code: it
                for it in AilstItem.objects.filter(
                    language=self.language,
                    instrument_version=self.instrument_version,
                )
            }

        scores = compute_factor_scores(self.responses, items_by_code)
        for field, value in scores.items():
            setattr(self, field, value)
        self.save(update_fields=list(scores.keys()))
