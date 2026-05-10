"""
Signal: keep TeacherProfile boolean fields in sync with ConsentRecord state.

Background: pre-Phase-C, three Step 3 consents lived as booleans on
TeacherProfile (research_consent, consent_data_sharing, contact_for_research).
Phase C M6 migrated the first two to ConsentRecord rows. The booleans
remain as a backwards-compat read cache; this signal keeps them in sync
when ConsentRecord state changes (create, revoke, etc.) so legacy code
paths that still read the booleans see the canonical state.

Future: when no code reads the booleans anymore, drop them in a Phase H
cleanup migration. Until then, this signal preserves single-source-of-truth
semantics with the cache.

Caveats:
  - bulk_create() does NOT fire post_save signals. The M6 data migration
    uses bulk-style row creation; the booleans were already True for those
    profiles (that is why we backfilled), so no sync is needed at migration
    time. New writes via record_consent() use .create() which fires the
    signal correctly.
  - The signal queries canonical state (ANY active row for user+type),
    not just `instance.is_active`. This handles the case where multiple
    versions of the same consent_type exist (e.g., a revoked v1 and an
    active v2): the boolean reflects the union.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ConsentRecord


# Reverse map: ConsentRecord.consent_type -> TeacherProfile boolean field.
# Mirrors LEGACY_BOOLEAN_MAP in services.py.
CONSENT_TYPE_TO_BOOLEAN = {
    'research_participation': 'research_consent',
    'data_sharing': 'consent_data_sharing',
}


@receiver(post_save, sender=ConsentRecord)
def sync_teacher_profile_booleans(sender, instance, **kwargs):
    """Mirror canonical consent state to TeacherProfile booleans for legacy reads."""
    field = CONSENT_TYPE_TO_BOOLEAN.get(instance.consent_type)
    if field is None:
        # consent_type not mapped to a legacy boolean (e.g., 'ai_disclosure',
        # 'platform_use', 'video_recording'). Nothing to sync.
        return

    # Canonical state: any granted+non-revoked row for this (user, type)?
    canonical = ConsentRecord.objects.filter(
        user_id=instance.user_id,
        consent_type=instance.consent_type,
        granted=True,
        revoked_at__isnull=True,
    ).exists()

    # Late import to avoid circular dependency at app load time.
    from apps.users.models import TeacherProfile

    try:
        profile = TeacherProfile.objects.get(user_id=instance.user_id)
    except TeacherProfile.DoesNotExist:
        # User has no profile (edge case: ConsentRecord pre-dates profile
        # creation). Nothing to sync.
        return

    current = getattr(profile, field, None)
    if current != canonical:
        setattr(profile, field, canonical)
        profile.save(update_fields=[field])
