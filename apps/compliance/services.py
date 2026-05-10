"""
Service helpers for the compliance app.

Centralised write/revoke path for ConsentRecord. C.2 AI Disclosure
middleware, C.4 Privacy dashboard, and the legacy-boolean data migration
all flow through these helpers. Keeps business logic out of views and
out of migrations.
"""

from typing import Optional

from django.utils import timezone


LEGACY_BOOLEAN_MAP = {
    # TeacherProfile boolean field -> ConsentRecord consent_type
    'research_consent': 'research_participation',
    'consent_data_sharing': 'data_sharing',
    # NOTE: TeacherProfile.contact_for_research is a CONTACT PREFERENCE
    # ('available for research interviews'), not a consent. It is not
    # migrated to ConsentRecord.
}

LEGACY_VERSION_TAG = 'v0_pre_phase_c'
LEGACY_CONSENT_TEXT_TEMPLATE = (
    "Migrated from TeacherProfile.{boolean_field} on {migration_date}. "
    "Original Step 3 consent text was not preserved (pre-Phase-C limitation: "
    "consent was tracked as a boolean field without verbatim text storage). "
    "User had this boolean set to True at the time of the M6 backfill data "
    "migration. Granted_at reflects the user's TeacherProfile.consent_timestamp "
    "(when available) or TeacherProfile.created_at (fallback)."
)


def record_consent(*, user, consent_type, consent_text, version,
                   granted=True, ip_address=None):
    """Idempotent helper to write a ConsentRecord row, with supersede semantics.

    Two cases:

    1. SAME (user, consent_type, version) row already active:
       Return that row. No new write. (Idempotency for replays — e.g., a
       user double-clicking 'I acknowledge' on the AI Disclosure modal.)

    2. DIFFERENT version: revoke any prior active rows of the same
       (user, consent_type), then create the new row. The new version
       'supersedes' the prior one. Audit trail is preserved (old rows
       remain in the table with revoked_at set); current state is clean
       (exactly one active row per consent_type per user).

    The supersede pattern:
      - Mirrors how GDPR / IRB consent updates work in practice: a new
        text version supersedes the previous one once explicitly agreed.
      - Keeps the M6 sync_teacher_profile_booleans signal simple: the
        canonical state remains "any active row of this consent_type".
      - Avoids accumulating multiple active rows per consent_type, which
        would muddy queries and analytics.

    Per-row save() (not bulk update) when revoking prior active versions
    so that the post_save signal fires correctly.

    Args:
        user: Django User instance.
        consent_type: One of CONSENT_TYPE_CHOICES values.
        consent_text: Verbatim text shown to the user.
        version: Version tag (e.g., 'v1_pre_irb').
        granted: True if user consented, False if explicitly denied.
        ip_address: Optional IP at consent time. Auto-redacted after 30 days
            via manage.py redact_old_consent_ips.

    Returns:
        ConsentRecord row (newly created, or pre-existing if same version
        was already active).
    """
    from .models import ConsentRecord

    # Idempotency: same version already active for this (user, type)?
    existing = ConsentRecord.objects.filter(
        user=user,
        consent_type=consent_type,
        version=version,
        revoked_at__isnull=True,
    ).first()
    if existing:
        return existing

    # Supersede: revoke any active rows of OTHER versions for the same
    # (user, consent_type). Per-row save() so the M6 sync signal fires.
    now = timezone.now()
    prior_active = ConsentRecord.objects.filter(
        user=user,
        consent_type=consent_type,
        revoked_at__isnull=True,
    )
    for cr in prior_active:
        cr.revoked_at = now
        cr.save(update_fields=['revoked_at'])

    # Create the new row.
    return ConsentRecord.objects.create(
        user=user,
        consent_type=consent_type,
        granted=granted,
        consent_text=consent_text,
        version=version,
        ip_address=ip_address,
    )


def revoke_consent(*, user, consent_type, version: Optional[str] = None) -> int:
    """Mark active consents as revoked.

    If `version` is None, revokes ALL active rows for (user, consent_type) —
    note that the supersede pattern in record_consent normally keeps at most
    one active row per (user, consent_type), so version=None typically
    revokes 0 or 1 rows. The 'all versions' wording reflects the legal
    intent: one user's withdrawal of consent for a consent_type covers
    every active row of that type, regardless of historical text version.
    Otherwise revokes only matching version (used by tests that bypass
    supersede via direct ORM creation).

    Returns count of rows revoked.

    Implementation note: per-row save() (not bulk update()) so that the
    sync_teacher_profile_booleans post_save signal fires and the legacy
    boolean cache stays in sync. Bulk update() bypasses signals.
    """
    from .models import ConsentRecord

    qs = ConsentRecord.objects.filter(
        user=user,
        consent_type=consent_type,
        revoked_at__isnull=True,
    )
    if version is not None:
        qs = qs.filter(version=version)

    now = timezone.now()
    count = 0
    for cr in qs:
        cr.revoked_at = now
        cr.save(update_fields=['revoked_at'])
        count += 1
    return count


def migrate_legacy_teacher_consents(*, TeacherProfile=None, ConsentRecord=None):
    """Backfill ConsentRecord rows for pre-Phase-C TeacherProfile booleans.

    For each TeacherProfile where research_consent=True or
    consent_data_sharing=True, create a corresponding ConsentRecord row
    with version='v0_pre_phase_c' and an explanatory consent_text.

    Idempotent: re-running skips users who already have an active
    ConsentRecord row for the matching (user, consent_type, version).

    Note on contact_for_research: this is a contact preference, not a
    consent. Not migrated.

    Args:
        TeacherProfile: optional model class. Defaults to live model.
            Pass apps.get_model('users','TeacherProfile') in migrations.
        ConsentRecord: optional model class. Defaults to live model.

    Returns:
        int — number of new ConsentRecord rows created.
    """
    if TeacherProfile is None:
        from apps.users.models import TeacherProfile as TeacherProfile  # noqa
    if ConsentRecord is None:
        from .models import ConsentRecord as ConsentRecord  # noqa

    today = timezone.now()
    created_count = 0

    for profile in TeacherProfile.objects.all():
        for boolean_field, consent_type in LEGACY_BOOLEAN_MAP.items():
            if not getattr(profile, boolean_field, False):
                continue

            # Idempotency guard: skip if active row already exists for this
            # (user, type, version) tuple.
            already_exists = ConsentRecord.objects.filter(
                user_id=profile.user_id,
                consent_type=consent_type,
                version=LEGACY_VERSION_TAG,
                revoked_at__isnull=True,
            ).exists()
            if already_exists:
                continue

            granted_at_raw = (
                profile.consent_timestamp
                or profile.created_at
                or today
            )
            # Legacy TeacherProfile.consent_timestamp / created_at may be
            # naive datetimes (pre-USE_TZ=True era). Coerce to aware (UTC)
            # so PostgreSQL stores under the modern timezone-aware contract.
            # See proodos_files/TECH_DEBT_LOG.md for the planned full fix.
            from django.utils.timezone import is_naive, make_aware
            granted_at = (
                make_aware(granted_at_raw)
                if is_naive(granted_at_raw)
                else granted_at_raw
            )
            consent_text = LEGACY_CONSENT_TEXT_TEMPLATE.format(
                boolean_field=boolean_field,
                migration_date=today.strftime('%Y-%m-%d'),
            )
            ConsentRecord.objects.create(
                user_id=profile.user_id,
                consent_type=consent_type,
                granted=True,
                consent_text=consent_text,
                version=LEGACY_VERSION_TAG,
                granted_at=granted_at,
                ip_address=None,
            )
            created_count += 1

    return created_count
