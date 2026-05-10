"""
AILST instrument storage models.

AILST = AI Literacy Scale for Teachers (Ning et al. 2025,
Education and Information Technologies 30:17769-17803).

Phase C M4 introduces AilstItem (this file). Phase C M5 will introduce
AilstResponse (per-user-per-timepoint) in a separate migration.
"""

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
