"""
Certification models for PROODOS Phase H.3.

The `CertificateOfAttendance` model is the durable record of a teacher's
completion of the 15-module PROODOS programme. Issuance is gated on
AilstResponse.completed_at__isnull=False for timepoint=T2 (the closing
AILST administration), per the consent text at
apps/compliance/copy.py:101-102 ("You cannot ... receive a completion
certificate without completing T2"). The certificate carries no AILST
scores — it attests to participation, not performance.

Design proposal: proodos_files/PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md
§5 (Certificate of Attendance).

Frozen-state pattern: teacher_display + modules_summary are snapshots
of the user's state at issue time. If the teacher renames their
profile or M15 content is edited post-pilot, the certificate keeps
the values it was issued with — matches the same pattern that
EpilogueCompletion.stage0_snapshot uses (PROODOS Epilogue v2 §5.4).
"""

import secrets

from django.contrib.auth.models import User
from django.db import models


def generate_verification_code():
    """Return a unique 16-char URL-safe verification code.

    Mathematical collision probability at n=110 issued certs over a
    96-bit code space is ~6e-26; the retry loop is a defensive guard
    against the (vanishingly unlikely) IntegrityError on the
    `unique=True` index, not an expected hot path.

    Raises RuntimeError after 5 failed attempts — would only happen
    under code-space-exhaustion conditions that warrant a real
    investigation rather than silent retry.
    """
    for _ in range(5):
        code = secrets.token_urlsafe(12)[:16]
        if not CertificateOfAttendance.objects.filter(
            verification_code=code,
        ).exists():
            return code
    raise RuntimeError(
        "Could not generate unique verification code after 5 attempts; "
        "investigate code-space exhaustion."
    )


class CertificateOfAttendance(models.Model):
    """One certificate per teacher. Issued on first download request,
    after T2 eligibility passes; subsequent downloads re-render from
    the frozen row.

    OneToOneField enforces one-cert-per-teacher at the DB level
    (matches the EpilogueCompletion pattern). Revisions to the PDF
    output handled by bumping `pdf_metadata_version` on re-render;
    no new row issued. The Greek translation lands in a follow-up
    commit (Path A from proposal §5.5) and may flip a
    `certificate_translation_status` JSON-LD key without requiring
    a new model field.

    on_delete=PROTECT: refusing to cascade-destroy a certificate
    when the teacher is hard-deleted. In practice teachers are
    anonymised (services.anonymize_user, not deleted) so PROTECT
    rarely fires; if a real DELETE is attempted, the certificate
    record blocks it as an audit-defence.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='certificate_of_attendance',
    )
    issued_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Set on first issuance; never changes on re-render.',
    )
    verification_code = models.CharField(
        max_length=16,
        unique=True,
        help_text=(
            "16-char URL-safe random code used in the public "
            "/certification/verify/<code>/ endpoint. Generated via "
            "generate_verification_code() helper with retry-on-collision."
        ),
    )

    # Frozen-state fields — snapshots at issuance.
    teacher_display = models.CharField(
        max_length=255,
        help_text=(
            'Frozen at issuance. Built from user.get_full_name() or '
            'user.username; survives later profile renames.'
        ),
    )
    modules_summary = models.JSONField(
        help_text=(
            'Frozen list of the 15 modules at issuance, each entry '
            '{"code": "M1", "title": "...", "aspect": "Human-Centred '
            'Mindset", "level": "Acquire"}. Survives later edits to '
            'Module rows.'
        ),
    )

    # Version pins — what was true at the moment of issuance.
    instrument_version_t2 = models.CharField(
        max_length=20,
        help_text=(
            "AilstResponse.instrument_version of the T2 row that "
            "triggered issuance (typically 'ning_2025_v1')."
        ),
    )
    pdf_metadata_version = models.CharField(
        max_length=20,
        default='v1',
        help_text=(
            'Bumped on PDF template revisions (e.g. when the Greek '
            'translation lands per Phase H Path A) without requiring '
            'a new row. The Article 50(2) JSON-LD body block reflects '
            'this version.'
        ),
    )

    class Meta:
        db_table = 'certification_certificate_of_attendance'
        verbose_name = 'Certificate of Attendance'
        verbose_name_plural = 'Certificates of Attendance'
        ordering = ['-issued_at']

    def __str__(self):
        return (
            f'{self.teacher_display} | issued {self.issued_at:%Y-%m-%d} '
            f'| code {self.verification_code}'
        )
