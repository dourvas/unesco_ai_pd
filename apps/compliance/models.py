"""
Compliance models for PROODOS.

Phase C M6 introduces ConsentRecord — GDPR-compliant consent tracking.
Replaces the dropped raw-SQL `consent_records` table (which had FK to a
separate raw-SQL `users` table, now defunct). New table FK is to
`auth_user`.

Phase C C.3 (commit 1) introduces AIArtefactProvenance — machine-readable
provenance metadata for every AI-generated artefact the platform produces
(EU AI Act Article 50(2)).
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
        # Phase H H.6 (2026-05-25 redesign): the separate
        # 'followup_recruitment' consent_type added in migration 0007 was
        # rolled back in migration 0008. The follow-up email-retention
        # permission now bundles into the research_participation consent
        # V2 (RESEARCH_PARTICIPATION_TEXT_V2_FOLLOWUP_BUNDLED) as one
        # bullet under "What participation involves:". One unified
        # consent, clearer IRB packet.
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
                # Phase H H.6 (2026-05-25 redesign): removed
                # 'followup_recruitment' here when migration 0008
                # rolled back the separate consent_type. Bundled into
                # research_participation V2. Keep this list in sync
                # with CONSENT_TYPE_CHOICES above; changes here require
                # a DB migration (the constraint is enforced at the
                # database level, not just at form validation level).
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


class AIArtefactProvenance(models.Model):
    """One row per AI-generated artefact the platform produces.

    Captures the model identifier and generation timestamp so the platform
    can satisfy EU AI Act Article 50(2) (machine-readable provenance) and
    so the C.4 GDPR Art. 15 export can attribute every AI output.

    The `(artefact_kind, artefact_pk)` pair is polymorphic — it references
    rows in five different sources without a Django FK, because one of the
    sources (`rag_queries`) lives outside the ORM as a raw-SQL table.
    Cascade on user deletion is the only ORM-level relation enforced; the
    artefact rows themselves are cleared by their own paths (Django CASCADE
    for the ORM-managed sources; explicit raw-SQL DELETE for rag_queries
    in `cp11_wipe_test_users.py` and `anonymize_user`).

    Idempotency: `unique_together = ('artefact_kind', 'artefact_pk')` plus
    `get_or_create` in the helper means the backfill command and the
    forward-write hooks can both run without colliding.
    """

    ARTEFACT_KIND_CHOICES = [
        ('rtm_position', 'RTM tension position'),
        ('dtp_narrative', 'DTP developmental trajectory narrative'),
        ('xai_narrative', 'DTP XAI explanation narrative'),
        ('rag_feedback', 'RAG reflection feedback'),
        ('peer_synthesis', 'Peer reflection synthesis'),
        ('rag_query', 'Raw rag_queries telemetry row'),
        ('epilogue_portrait', 'Epilogue Learning Portrait (forward-compat)'),
    ]

    artefact_kind = models.CharField(
        max_length=24,
        choices=ARTEFACT_KIND_CHOICES,
    )
    artefact_pk = models.CharField(
        max_length=64,
        help_text=(
            "Primary key in the source table for this artefact_kind, "
            "stored as string. Not a Django FK because rag_queries is "
            "raw-SQL; integrity is enforced at write time. CharField "
            "(not int) because the five source tables use heterogeneous "
            "pk types: ReflectionTension uses UUIDField, UserModuleProgress "
            "and rag_queries use BigAutoField. The helper coerces to str."
        ),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_artefact_provenance',
    )
    module = models.ForeignKey(
        'modules.Module',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ai_artefact_provenance',
        help_text="Nullable: rag_queries rows may carry a NULL module_id.",
    )
    model_name = models.CharField(
        max_length=64,
        help_text="AI model identifier, e.g., 'gemini-2.5-flash'.",
    )
    generated_at = models.DateTimeField(
        help_text="When the artefact was generated. For backfill, the source row's created_at.",
    )
    prompt_hash = models.CharField(
        max_length=64, null=True, blank=True,
        help_text=(
            "sha256 of the prompt text + retrieval context (privacy-respecting). "
            "Nullable for retroactive backfill where the prompt is not reconstructible."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'AI Artefact Provenance'
        verbose_name_plural = 'AI Artefact Provenance'
        constraints = [
            models.UniqueConstraint(
                fields=['artefact_kind', 'artefact_pk'],
                name='uq_ai_provenance_kind_pk',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'artefact_kind'],
                         name='idx_ai_prov_user_kind'),
            models.Index(fields=['module', 'artefact_kind'],
                         name='idx_ai_prov_module_kind'),
        ]
        ordering = ['-generated_at']

    def __str__(self):
        return (
            f'{self.artefact_kind}#{self.artefact_pk} '
            f'[{self.model_name} @ {self.generated_at:%Y-%m-%d %H:%M}]'
        )
