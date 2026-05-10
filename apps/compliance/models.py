"""
Compliance models for PROODOS.

Phase C M6 introduces ConsentRecord — GDPR-compliant consent tracking.
Replaces the dropped raw-SQL `consent_records` table (which had FK to a
separate raw-SQL `users` table, now defunct). New table FK is to
`auth_user`.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ConsentRecord(models.Model):
    """One row per consent event.

    Captures the verbatim text the user agreed to, the version label, and
    the active/revoked state. IRB-defensible: "what exactly did the user
    agree to on this date" is answerable from a single row.

    Lifecycle:
      - granted=True,  revoked_at=NULL → active consent
      - granted=False, revoked_at=NULL → user denied (active denial)
      - granted=True,  revoked_at=NOT NULL → granted then revoked
      - granted=False, revoked_at=NOT NULL → unusual but allowed (denial then later state change)

    Use the `is_active` property in call sites to avoid repeating the
    two-condition check.
    """

    CONSENT_TYPE_CHOICES = [
        ('platform_use', 'Platform terms of use'),
        ('research_participation', 'Research participation'),
        ('data_sharing', 'Data sharing with affiliated researchers'),
        ('video_recording', 'Video recording (interviews/focus groups)'),
        ('ai_disclosure', 'EU AI Act Article 50 disclosure acknowledgment'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consent_records',
    )
    consent_type = models.CharField(max_length=30, choices=CONSENT_TYPE_CHOICES)
    granted = models.BooleanField(default=True)
    consent_text = models.TextField(
        help_text=(
            "Verbatim copy of the text the user agreed to at consent time. "
            "Never re-edited. Source of truth for IRB / legal defensibility "
            "('what exactly did the user agree to on this date?')."
        ),
    )
    version = models.CharField(
        max_length=20,
        help_text="Version label of the consent text, e.g., 'v1', 'v2_irb_revised'.",
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text=(
            "Redacted (set NULL) after 30 days per GDPR data minimization. "
            "See manage.py redact_old_consent_ips."
        ),
    )
    granted_at = models.DateTimeField(
        default=timezone.now,
        help_text=(
            "When the consent was granted. Default is NOW; explicit override "
            "allowed for backfill migrations (e.g., legacy boolean migration)."
        ),
    )
    revoked_at = models.DateTimeField(
        null=True, blank=True,
        help_text=(
            "Set if user revokes this consent (e.g., via Privacy dashboard). "
            "Row preserved; granted_at..revoked_at delimits active period."
        ),
    )

    class Meta:
        verbose_name = 'Consent Record'
        verbose_name_plural = 'Consent Records'
        indexes = [
            models.Index(fields=['user', 'consent_type', '-granted_at'],
                         name='idx_consent_user_type_time'),
            models.Index(fields=['consent_type', 'granted'],
                         name='idx_consent_type_granted'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(consent_type__in=[
                    'platform_use', 'research_participation', 'data_sharing',
                    'video_recording', 'ai_disclosure',
                ]),
                name='valid_consent_type',
            ),
        ]
        ordering = ['-granted_at']

    def __str__(self):
        if self.revoked_at:
            state = 'revoked'
        elif self.granted:
            state = 'granted'
        else:
            state = 'denied'
        return f'{self.user.username} | {self.consent_type} [{state} {self.granted_at:%Y-%m-%d}]'

    @property
    def is_active(self) -> bool:
        """True if this consent is currently active: granted AND not revoked.

        Use at call sites instead of repeating `granted and not revoked_at`.
        """
        return self.granted and self.revoked_at is None
