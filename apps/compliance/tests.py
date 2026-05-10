"""
Tests for the compliance app.

Phase C M6 introduces:
  - ConsentRecord model with DB CHECK constraint and is_active property
  - record_consent / revoke_consent / migrate_legacy_teacher_consents service helpers
  - sync_teacher_profile_booleans signal (TeacherProfile boolean cache)
  - redact_old_consent_ips management command
  - Data migration 0004 backfilling Step 3 booleans into ConsentRecord rows

Tests cover model lifecycle, DB constraint enforcement, service idempotency,
signal sync correctness, IP redaction command behaviour, and the legacy
boolean migration logic.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.test import TestCase
from django.utils import timezone

from apps.compliance.models import ConsentRecord
from apps.compliance.services import (
    LEGACY_VERSION_TAG,
    migrate_legacy_teacher_consents,
    record_consent,
    revoke_consent,
)
from apps.users.models import TeacherProfile


def _make_user(username='compliance_user'):
    return User.objects.create_user(username=username, password='x')


def _make_profile(user, **overrides):
    """Create a minimum-viable TeacherProfile for the given user."""
    defaults = dict(
        subject_area='mathematics',
        grade_level='primary',
        ai_experience='none',
        research_consent=False,
        consent_data_sharing=False,
        contact_for_research=False,
    )
    defaults.update(overrides)
    return TeacherProfile.objects.create(user=user, **defaults)


class ConsentRecordModelTest(TestCase):
    """Model-level constraints and properties."""

    def setUp(self):
        self.user = _make_user()

    def test_create_basic_consent_record(self):
        cr = ConsentRecord.objects.create(
            user=self.user,
            consent_type='ai_disclosure',
            consent_text='Sample disclosure text',
            version='v1',
        )
        self.assertTrue(cr.is_active)
        self.assertTrue(cr.granted)
        self.assertIsNone(cr.revoked_at)

    def test_is_active_property_state_combinations(self):
        granted = ConsentRecord.objects.create(
            user=self.user, consent_type='ai_disclosure',
            consent_text='x', version='v1', granted=True,
        )
        denied = ConsentRecord.objects.create(
            user=self.user, consent_type='platform_use',
            consent_text='x', version='v1', granted=False,
        )
        granted_then_revoked = ConsentRecord.objects.create(
            user=self.user, consent_type='video_recording',
            consent_text='x', version='v1', granted=True,
            revoked_at=timezone.now(),
        )
        self.assertTrue(granted.is_active)
        self.assertFalse(denied.is_active)
        self.assertFalse(granted_then_revoked.is_active)

    def test_db_check_rejects_invalid_consent_type(self):
        """DB-level CHECK rejects consent_type outside the 5-value vocab.

        Bypasses Django choices validation by inserting raw SQL with a
        bogus consent_type. CHECK constraint must catch it.
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic(), connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO compliance_consentrecord "
                    "(user_id, consent_type, granted, consent_text, version, "
                    " granted_at) "
                    "VALUES (%s, %s, %s, %s, %s, NOW())",
                    [self.user.id, 'bogus_type', True, 'x', 'v1'],
                )

    def test_cascade_delete_on_user_delete(self):
        ConsentRecord.objects.create(
            user=self.user, consent_type='ai_disclosure',
            consent_text='x', version='v1',
        )
        self.assertEqual(ConsentRecord.objects.count(), 1)
        self.user.delete()
        self.assertEqual(ConsentRecord.objects.count(), 0)


class ConsentServiceTest(TestCase):
    """record_consent and revoke_consent helpers."""

    def setUp(self):
        self.user = _make_user()
        self.profile = _make_profile(self.user)

    def test_record_consent_creates_new_row(self):
        cr = record_consent(
            user=self.user, consent_type='ai_disclosure',
            consent_text='Disclosure v1 text', version='v1',
        )
        self.assertEqual(ConsentRecord.objects.count(), 1)
        self.assertTrue(cr.is_active)

    def test_record_consent_is_idempotent_for_same_user_type_version(self):
        first = record_consent(
            user=self.user, consent_type='ai_disclosure',
            consent_text='x', version='v1',
        )
        second = record_consent(
            user=self.user, consent_type='ai_disclosure',
            consent_text='x', version='v1',
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(ConsentRecord.objects.count(), 1)

    def test_revoke_consent_specific_version(self):
        record_consent(user=self.user, consent_type='ai_disclosure',
                       consent_text='v1 text', version='v1')
        record_consent(user=self.user, consent_type='ai_disclosure',
                       consent_text='v2 text', version='v2')
        revoked = revoke_consent(user=self.user, consent_type='ai_disclosure',
                                 version='v1')
        self.assertEqual(revoked, 1)
        v1 = ConsentRecord.objects.get(version='v1')
        v2 = ConsentRecord.objects.get(version='v2')
        self.assertFalse(v1.is_active)
        self.assertTrue(v2.is_active)

    def test_revoke_consent_all_versions(self):
        record_consent(user=self.user, consent_type='ai_disclosure',
                       consent_text='v1', version='v1')
        record_consent(user=self.user, consent_type='ai_disclosure',
                       consent_text='v2', version='v2')
        revoked = revoke_consent(user=self.user, consent_type='ai_disclosure')
        self.assertEqual(revoked, 2)
        for cr in ConsentRecord.objects.all():
            self.assertFalse(cr.is_active)


class LegacyBooleanMigrationTest(TestCase):
    """The data migration logic that backfills ConsentRecord from
    TeacherProfile.research_consent and .consent_data_sharing booleans."""

    def test_migration_creates_consentrecord_for_each_true_boolean(self):
        u = _make_user('legacy_user')
        consent_ts = timezone.now() - timedelta(days=10)
        _make_profile(
            u,
            research_consent=True,
            consent_data_sharing=True,
            contact_for_research=True,  # NOT migrated (preference, not consent)
            consent_timestamp=consent_ts,
        )

        created = migrate_legacy_teacher_consents()

        self.assertEqual(created, 2)
        types = set(ConsentRecord.objects.values_list('consent_type', flat=True))
        self.assertEqual(types, {'research_participation', 'data_sharing'})
        for cr in ConsentRecord.objects.all():
            self.assertEqual(cr.version, LEGACY_VERSION_TAG)
            self.assertEqual(cr.granted_at, consent_ts)
            self.assertIn('Migrated from TeacherProfile', cr.consent_text)

    def test_migration_skips_false_booleans(self):
        u = _make_user('opt_out_user')
        _make_profile(u, research_consent=False, consent_data_sharing=False,
                      consent_timestamp=timezone.now())
        created = migrate_legacy_teacher_consents()
        self.assertEqual(created, 0)
        self.assertEqual(ConsentRecord.objects.count(), 0)

    def test_migration_is_idempotent(self):
        u = _make_user('idempotent_user')
        _make_profile(u, research_consent=True, consent_timestamp=timezone.now())
        first = migrate_legacy_teacher_consents()
        second = migrate_legacy_teacher_consents()
        self.assertEqual(first, 1)
        self.assertEqual(second, 0)
        self.assertEqual(ConsentRecord.objects.count(), 1)


class SignalSyncTest(TestCase):
    """sync_teacher_profile_booleans keeps TeacherProfile booleans in
    sync with canonical ConsentRecord state."""

    def setUp(self):
        self.user = _make_user('signal_user')
        self.profile = _make_profile(self.user)
        # Profile starts with all booleans False per _make_profile defaults.

    def test_create_consent_flips_boolean_true(self):
        record_consent(
            user=self.user, consent_type='research_participation',
            consent_text='x', version='v1',
        )
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.research_consent)

    def test_revoke_consent_flips_boolean_false(self):
        record_consent(
            user=self.user, consent_type='research_participation',
            consent_text='x', version='v1',
        )
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.research_consent)

        revoke_consent(user=self.user, consent_type='research_participation')
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.research_consent)

    def test_unmapped_consent_type_does_not_affect_profile(self):
        record_consent(
            user=self.user, consent_type='ai_disclosure',
            consent_text='x', version='v1',
        )
        self.profile.refresh_from_db()
        # ai_disclosure has no boolean mapping; profile booleans unchanged.
        self.assertFalse(self.profile.research_consent)
        self.assertFalse(self.profile.consent_data_sharing)


class IPRedactionCommandTest(TestCase):
    """redact_old_consent_ips management command behaviour."""

    def setUp(self):
        self.user = _make_user('ip_user')

    def test_dry_run_does_not_modify(self):
        old = ConsentRecord.objects.create(
            user=self.user, consent_type='ai_disclosure',
            consent_text='x', version='v1',
            ip_address='192.0.2.1',
            granted_at=timezone.now() - timedelta(days=60),
        )
        call_command('redact_old_consent_ips')  # default dry-run
        old.refresh_from_db()
        self.assertEqual(old.ip_address, '192.0.2.1')

    def test_commit_redacts_only_old_rows(self):
        old = ConsentRecord.objects.create(
            user=self.user, consent_type='ai_disclosure',
            consent_text='x', version='v1',
            ip_address='192.0.2.1',
            granted_at=timezone.now() - timedelta(days=60),
        )
        recent = ConsentRecord.objects.create(
            user=self.user, consent_type='platform_use',
            consent_text='x', version='v1',
            ip_address='192.0.2.99',
            granted_at=timezone.now() - timedelta(days=5),
        )
        call_command('redact_old_consent_ips', '--commit')
        old.refresh_from_db()
        recent.refresh_from_db()
        self.assertIsNone(old.ip_address)
        self.assertEqual(recent.ip_address, '192.0.2.99')
