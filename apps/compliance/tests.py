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

    def test_record_consent_supersedes_prior_version(self):
        """C.2.2 supersede pattern: granting a NEW version revokes any prior
        active versions of the same (user, consent_type), so exactly one
        active row exists per consent identity. Audit rows preserved.
        """
        v1 = record_consent(
            user=self.user, consent_type='ai_disclosure',
            consent_text='v1 text', version='v1',
        )
        self.assertTrue(v1.is_active)
        v2 = record_consent(
            user=self.user, consent_type='ai_disclosure',
            consent_text='v2 text', version='v2',
        )
        v1.refresh_from_db()
        self.assertFalse(v1.is_active, "v1 must be revoked after v2 supersede")
        self.assertTrue(v2.is_active)
        # Audit trail preserved
        self.assertEqual(
            ConsentRecord.objects.filter(
                user=self.user, consent_type='ai_disclosure',
            ).count(),
            2,
        )

    def test_record_consent_same_version_is_idempotent_no_supersede(self):
        """Re-recording the SAME version returns existing row, does not
        spuriously revoke-and-recreate."""
        first = record_consent(
            user=self.user, consent_type='ai_disclosure',
            consent_text='same text', version='v1',
        )
        second = record_consent(
            user=self.user, consent_type='ai_disclosure',
            consent_text='same text', version='v1',
        )
        self.assertEqual(first.id, second.id)
        first.refresh_from_db()
        self.assertTrue(first.is_active, "Same-version replay must not revoke")
        self.assertEqual(
            ConsentRecord.objects.filter(
                user=self.user, consent_type='ai_disclosure',
            ).count(),
            1,
        )

    def test_revoke_consent_specific_version_via_direct_orm(self):
        """Explicit revoke_consent(version='X') targets only that version.
        Uses direct ORM creates to bypass the supersede pattern (under which
        record_consent normally keeps at most one active row).
        """
        cr1 = ConsentRecord.objects.create(
            user=self.user, consent_type='ai_disclosure',
            consent_text='manual v1', version='manual_v1', granted=True,
        )
        cr2 = ConsentRecord.objects.create(
            user=self.user, consent_type='ai_disclosure',
            consent_text='manual v2', version='manual_v2', granted=True,
        )
        revoked = revoke_consent(
            user=self.user, consent_type='ai_disclosure', version='manual_v1',
        )
        self.assertEqual(revoked, 1)
        cr1.refresh_from_db()
        cr2.refresh_from_db()
        self.assertFalse(cr1.is_active)
        self.assertTrue(cr2.is_active)

    def test_revoke_consent_all_versions_via_direct_orm(self):
        """revoke_consent without version revokes ALL active rows for
        (user, consent_type). Uses direct ORM creates to set up multiple
        active rows (record_consent's supersede would normally keep one)."""
        cr1 = ConsentRecord.objects.create(
            user=self.user, consent_type='ai_disclosure',
            consent_text='v1', version='v1', granted=True,
        )
        cr2 = ConsentRecord.objects.create(
            user=self.user, consent_type='ai_disclosure',
            consent_text='v2', version='v2', granted=True,
        )
        revoked = revoke_consent(user=self.user, consent_type='ai_disclosure')
        self.assertEqual(revoked, 2)
        cr1.refresh_from_db()
        cr2.refresh_from_db()
        self.assertFalse(cr1.is_active)
        self.assertFalse(cr2.is_active)


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


# ============================================================
# Phase C C.2.0 — AI Disclosure middleware + view tests
# ============================================================

from django.test import Client


class AIDisclosureMiddlewareTest(TestCase):
    """Middleware redirect logic across user states and request types."""

    def setUp(self):
        self.client = Client()
        self.unack_user = User.objects.create_user(
            username='middleware_unack', password='x',
        )
        TeacherProfile.objects.create(
            user=self.unack_user,
            subject_area='mathematics', grade_level='primary',
            ai_experience='none',
        )
        self.ack_user = User.objects.create_user(
            username='middleware_ack', password='x',
        )
        TeacherProfile.objects.create(
            user=self.ack_user,
            subject_area='mathematics', grade_level='primary',
            ai_experience='none',
            ai_disclosure_acknowledged_at=timezone.now(),
        )

    def test_anonymous_user_no_disclosure_redirect(self):
        response = self.client.get('/')
        # Landing or 200; in any case NOT redirected to disclosure.
        location = response.get('Location', '')
        self.assertNotIn('/onboarding/ai-disclosure/', location)

    def test_unacknowledged_user_redirected_from_dashboard(self):
        self.client.force_login(self.unack_user)
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/onboarding/ai-disclosure/', response['Location'])
        self.assertIn('next=/dashboard/', response['Location'])

    def test_acknowledged_user_passes_through(self):
        self.client.force_login(self.ack_user)
        response = self.client.get('/dashboard/')
        location = response.get('Location', '')
        self.assertNotIn('/onboarding/ai-disclosure/', location)

    def test_user_with_no_teacher_profile_redirected(self):
        no_profile = User.objects.create_user(
            username='middleware_noprofile', password='x',
        )
        self.client.force_login(no_profile)
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/onboarding/ai-disclosure/', response['Location'])

    def test_disclosure_url_itself_not_redirected(self):
        self.client.force_login(self.unack_user)
        response = self.client.get('/onboarding/ai-disclosure/')
        self.assertEqual(response.status_code, 200)

    def test_logout_url_not_redirected(self):
        self.client.force_login(self.unack_user)
        response = self.client.get('/logout/')
        location = response.get('Location', '')
        self.assertNotIn('/onboarding/ai-disclosure/', location)

    def test_static_prefix_not_redirected(self):
        self.client.force_login(self.unack_user)
        response = self.client.get('/static/css/main.css')
        # 404 is acceptable; the requirement is that we did NOT redirect
        # to disclosure.
        self.assertNotIn(
            '/onboarding/ai-disclosure/',
            response.get('Location', ''),
        )

    def test_ajax_request_returns_403_json(self):
        self.client.force_login(self.unack_user)
        response = self.client.get(
            '/dashboard/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body['error'], 'ai_disclosure_required')
        self.assertEqual(body['redirect_url'], '/onboarding/ai-disclosure/')

    def test_about_ai_act_compliance_bypassed(self):
        """The 'Learn more' stub URL must be reachable from the modal."""
        self.client.force_login(self.unack_user)
        response = self.client.get('/about/ai-act-compliance/')
        # Stub renders; 200 expected, but in any case NOT a redirect to
        # disclosure (which would be a loop).
        self.assertNotIn(
            '/onboarding/ai-disclosure/',
            response.get('Location', ''),
        )


class AIDisclosureViewTest(TestCase):
    """The disclosure view itself: GET renders, POST acknowledges."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='view_user', password='x')

    def test_get_renders_modal_page(self):
        self.client.force_login(self.user)
        response = self.client.get('/onboarding/ai-disclosure/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Important: AI Use Disclosure')
        self.assertContains(response, 'I acknowledge and continue')

    def test_post_creates_consent_record_and_acknowledges(self):
        self.client.force_login(self.user)
        response = self.client.post('/onboarding/ai-disclosure/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/dashboard/')

        cr = ConsentRecord.objects.get(
            user=self.user, consent_type='ai_disclosure',
        )
        self.assertTrue(cr.is_active)
        self.assertEqual(cr.version, 'v1_pre_irb')

        profile = TeacherProfile.objects.get(user=self.user)
        self.assertIsNotNone(profile.ai_disclosure_acknowledged_at)

    def test_post_idempotent_re_acknowledgment(self):
        self.client.force_login(self.user)
        self.client.post('/onboarding/ai-disclosure/')
        self.client.post('/onboarding/ai-disclosure/')
        self.assertEqual(
            ConsentRecord.objects.filter(
                user=self.user, consent_type='ai_disclosure',
            ).count(),
            1,
        )

    def test_stored_consent_text_matches_copy_module_exactly(self):
        """Regression: stored consent_text == AI_DISCLOSURE_TEXT_V1_PRE_IRB
        verbatim. Guards against text edits without a version bump.
        """
        from apps.compliance.copy import AI_DISCLOSURE_TEXT_V1_PRE_IRB

        self.client.force_login(self.user)
        self.client.post('/onboarding/ai-disclosure/')
        cr = ConsentRecord.objects.get(
            user=self.user, consent_type='ai_disclosure',
        )
        self.assertEqual(cr.consent_text, AI_DISCLOSURE_TEXT_V1_PRE_IRB)


# ============================================================================
# C.2.5 follow-up: consent_format template filter tests
# ============================================================================


class ConsentFormatFilterTest(TestCase):
    """Verify the consent_format template filter handles the structural
    cases that appear in apps.compliance.copy: paragraphs separated by
    blank lines, bullet lists with a lead-in line, and continuation
    lines under a bullet."""

    def _render(self, text):
        from apps.compliance.templatetags.consent_format import consent_format
        return consent_format(text)

    def test_empty_text_returns_empty(self):
        self.assertEqual(self._render(''), '')
        self.assertEqual(self._render(None), '')

    def test_single_paragraph_joins_soft_wraps_with_spaces(self):
        text = (
            "PROODOS is the empirical instrument of a doctoral dissertation\n"
            "at the International Hellenic University, Thessaloniki."
        )
        out = self._render(text)
        # Soft-wrap newline inside a paragraph collapses to one space.
        self.assertIn('doctoral dissertation at the', out)
        self.assertNotIn('<br', out)
        self.assertTrue(out.startswith('<p>'))
        self.assertTrue(out.endswith('</p>'))

    def test_double_newline_starts_new_paragraph(self):
        text = "First paragraph.\n\nSecond paragraph."
        out = self._render(text)
        self.assertEqual(out, '<p>First paragraph.</p><p>Second paragraph.</p>')

    def test_bullet_list_with_lead_in_renders_p_plus_ul(self):
        text = (
            "Your platform interactions are research data. This includes:\n"
            "  - Your responses to module activities\n"
            "  - Your AILST questionnaire responses\n"
            "  - Your module progress and completion data"
        )
        out = self._render(text)
        self.assertIn('<p>Your platform interactions are research data. This includes:</p>', out)
        self.assertIn('<ul', out)
        self.assertIn('<li>Your responses to module activities</li>', out)
        self.assertIn('<li>Your AILST questionnaire responses</li>', out)
        self.assertIn('<li>Your module progress and completion data</li>', out)

    def test_bullet_continuation_line_joins_with_space(self):
        text = (
            "What participation involves:\n"
            "  - Completing the AI Literacy Scale (AILST) at three\n"
            "    points: T0, T1, T2. Each takes about 7 minutes."
        )
        out = self._render(text)
        # Continuation line is folded into the same <li>.
        self.assertIn(
            '<li>Completing the AI Literacy Scale (AILST) at three points: T0, T1, T2. Each takes about 7 minutes.</li>',
            out,
        )

    def test_html_is_escaped(self):
        text = "Bad <script>alert('x')</script> text."
        out = self._render(text)
        self.assertNotIn('<script>', out)
        self.assertIn('&lt;script&gt;', out)

    def test_real_consent_text_produces_no_brs(self):
        """Regression on the original bug: the verbatim Research
        Participation text used to render with <br> tags every ~80
        chars, creating a tall column with a large right-side gap.
        The filter must produce no <br>s at all."""
        from apps.compliance.copy import RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB
        out = self._render(RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB)
        self.assertNotIn('<br', out)
        # And it must produce both paragraph and list elements.
        self.assertIn('<p>', out)
        self.assertIn('<ul', out)
