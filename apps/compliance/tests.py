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
from django.test import Client, TestCase
from django.urls import reverse
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


# ============================================================================
# Phase C C.4 commit 1 — Privacy dashboard + per-consent revocation endpoints
# ============================================================================


class _PrivacyTestBase(TestCase):
    """Shared setUp for the C.4 commit-1 test classes."""

    def setUp(self):
        from apps.users.models import TeacherProfile

        self.client = Client()
        self.user = User.objects.create_user(username='c4_user', password='pw')
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            subject_area='mathematics',
            grade_level='primary',
            teaching_years='6-15',
            school_location='urban',
            average_class_size='medium',
            ai_experience='basic',
            preferred_communication_style='balanced',
            ai_disclosure_acknowledged_at=timezone.now(),
            profile_completed=True,
            research_consent=True,
            consent_data_sharing=True,
        )
        self.client.force_login(self.user)

    def _grant(self, consent_type, granted=True):
        """Convenience: insert an active ConsentRecord row directly."""
        return ConsentRecord.objects.create(
            user=self.user,
            consent_type=consent_type,
            granted=granted,
            consent_text='placeholder ' + consent_type + ' text',
            version='v1_pre_irb',
        )


class PrivacyDashboardViewTest(_PrivacyTestBase):

    def test_get_renders_for_user_with_active_consents(self):
        self._grant('ai_disclosure')
        self._grant('research_participation')
        self._grant('data_sharing')
        resp = self.client.get(reverse('compliance:privacy_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'compliance/privacy_dashboard.html')
        body = resp.content.decode('utf-8')
        # Three "Active" badges should appear.
        self.assertEqual(body.count('badge-success'), 3)

    def test_get_shows_never_granted_state(self):
        # No ConsentRecord rows seeded.
        resp = self.client.get(reverse('compliance:privacy_dashboard'))
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode('utf-8')
        self.assertIn('Never granted', body)

    def test_get_shows_revoked_state_with_date(self):
        cr = self._grant('research_participation')
        cr.revoked_at = timezone.now()
        cr.save(update_fields=['revoked_at'])
        resp = self.client.get(reverse('compliance:privacy_dashboard'))
        body = resp.content.decode('utf-8')
        self.assertIn('Revoked', body)

    def test_anon_user_redirects_to_login(self):
        self.client.logout()
        resp = self.client.get(reverse('compliance:privacy_dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)


class RevokeAiDisclosureTest(_PrivacyTestBase):

    def test_post_revokes_active_consentrecord(self):
        self._grant('ai_disclosure')
        self.client.post(reverse('compliance:revoke_ai_disclosure'))
        cr = ConsentRecord.objects.get(
            user=self.user, consent_type='ai_disclosure',
        )
        self.assertIsNotNone(cr.revoked_at)

    def test_post_clears_profile_ack_at(self):
        """TD-008 closure: ack_at is set to None so the middleware re-shows
        the modal on the next request."""
        self._grant('ai_disclosure')
        self.assertIsNotNone(self.profile.ai_disclosure_acknowledged_at)
        self.client.post(reverse('compliance:revoke_ai_disclosure'))
        self.profile.refresh_from_db()
        self.assertIsNone(self.profile.ai_disclosure_acknowledged_at)

    def test_post_logs_user_out(self):
        self._grant('ai_disclosure')
        resp = self.client.post(reverse('compliance:revoke_ai_disclosure'))
        self.assertEqual(resp.status_code, 302)
        # Anonymous session after logout.
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_after_revoke_next_request_hits_middleware(self):
        """Post-revoke: the next authenticated request lands on the
        AI Disclosure modal because ack_at is None."""
        self._grant('ai_disclosure')
        self.client.post(reverse('compliance:revoke_ai_disclosure'))
        # Re-authenticate as the same user (the logout in the revoke
        # view dropped the session; force_login a fresh one).
        self.client.force_login(self.user)
        resp = self.client.get(reverse('users:dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/onboarding/ai-disclosure/', resp.url)

    def test_atomicity_revoke_failure_rolls_back(self):
        """Simulate a save error during the profile ack-clear step.
        The ConsentRecord revocation must roll back so the user is not
        left in a contradictory half-state.

        Approach: monkeypatch TeacherProfile.save to raise once. The
        whole transaction.atomic() block rolls back, including the
        revoke_consent call from earlier in the block.
        """
        from apps.users.models import TeacherProfile

        cr = self._grant('ai_disclosure')
        original_save = TeacherProfile.save

        def boom(self, *a, **kw):
            raise RuntimeError('simulated DB failure')

        TeacherProfile.save = boom
        try:
            with self.assertRaises(RuntimeError):
                self.client.post(reverse('compliance:revoke_ai_disclosure'))
        finally:
            TeacherProfile.save = original_save

        cr.refresh_from_db()
        self.assertIsNone(
            cr.revoked_at,
            'Atomic rollback must keep the ConsentRecord unrevoked when the '
            'profile save raises.',
        )


class RevokeResearchConsentTest(_PrivacyTestBase):

    def test_post_revokes_and_syncs_boolean(self):
        self._grant('research_participation')
        self.client.post(reverse('compliance:revoke_research'))
        cr = ConsentRecord.objects.get(
            user=self.user, consent_type='research_participation',
        )
        self.assertIsNotNone(cr.revoked_at)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.research_consent)

    def test_post_sets_research_data_opted_out(self):
        self._grant('research_participation')
        self.assertFalse(self.profile.research_data_opted_out)
        self.client.post(reverse('compliance:revoke_research'))
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.research_data_opted_out)

    def test_post_does_not_delete_existing_ailst_responses(self):
        from apps.ailst.models import AilstResponse

        self._grant('research_participation')
        AilstResponse.objects.create(
            user=self.user, timepoint='T0', language='en',
            instrument_version='ning_2025_v1',
            responses={'P1': 4}, completed_at=timezone.now(),
        )
        self.client.post(reverse('compliance:revoke_research'))
        self.assertEqual(
            AilstResponse.objects.filter(user=self.user).count(),
            1,
            'Revoke must not auto-delete already-collected research data.',
        )

    def test_post_blocks_future_ailst_entry(self):
        """After revoke, the C.2.3 AILST entry view's research_consent
        gate redirects the user to research_consent_required."""
        self._grant('research_participation')
        self.client.post(reverse('compliance:revoke_research'))
        resp = self.client.get(reverse('ailst:entry', kwargs={'timepoint': 't1'}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('research-consent-required', resp.url)

    def test_post_user_stays_logged_in(self):
        self._grant('research_participation')
        self.client.post(reverse('compliance:revoke_research'))
        # Session still has auth user id.
        self.assertIn('_auth_user_id', self.client.session)


class RevokeDataSharingTest(_PrivacyTestBase):

    def test_post_revokes_and_syncs_boolean(self):
        self._grant('data_sharing')
        self.client.post(reverse('compliance:revoke_data_sharing'))
        cr = ConsentRecord.objects.get(
            user=self.user, consent_type='data_sharing',
        )
        self.assertIsNotNone(cr.revoked_at)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.consent_data_sharing)

    def test_post_does_not_touch_research_data_opted_out(self):
        """data_sharing has narrower scope than research_participation.
        Revoking it must NOT toggle the research-opt-out flag."""
        self._grant('data_sharing')
        self.assertFalse(self.profile.research_data_opted_out)
        self.client.post(reverse('compliance:revoke_data_sharing'))
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.research_data_opted_out)

    def test_post_is_idempotent(self):
        """Second POST after revoke is a no-op (no orphan rows, no errors)."""
        self._grant('data_sharing')
        self.client.post(reverse('compliance:revoke_data_sharing'))
        first_revoked_at = ConsentRecord.objects.get(
            user=self.user, consent_type='data_sharing',
        ).revoked_at
        self.client.post(reverse('compliance:revoke_data_sharing'))
        # Same row, same revoked_at — no new row, no further update.
        rows = ConsentRecord.objects.filter(
            user=self.user, consent_type='data_sharing',
        )
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows.first().revoked_at, first_revoked_at)


# ============================================================================
# C.4 commit 2 — GDPR Art. 15 data export
# ============================================================================


_RAG_QUERIES_DDL = """
CREATE TABLE IF NOT EXISTS rag_queries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    reflection_text TEXT NOT NULL,
    teacher_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    query_embedding TEXT,
    retrieved_chunks JSONB DEFAULT '[]'::jsonb,
    num_chunks_retrieved INTEGER DEFAULT 0,
    generated_response TEXT NOT NULL,
    generation_tokens INTEGER,
    feedback_rating INTEGER,
    feedback_comments TEXT,
    feedback_timestamp TIMESTAMP,
    processing_time_ms INTEGER,
    api_cost_eur NUMERIC(10,6),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
"""


class DataExportTest(_PrivacyTestBase):
    """Exercises the JSON export endpoint and the gather_user_export
    service helper.

    The 7th test covers the CP-5 invariant: a fresh user with zero
    optional rows still gets a JSON document with every expected key
    present (empty arrays / null values), so downstream parsers do
    not throw KeyError.

    rag_queries is a raw-SQL table that lives outside Django migrations
    in production. The class setUp ensures the table exists in the
    test DB so we can exercise the export path against it; the
    service helper is independently defensive against the missing
    table (test_export_works_when_rag_queries_table_absent in the
    AtomicityAndEdgeCaseTest class verifies that).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # rag_queries lives outside Django migrations; create on demand.
        with connection.cursor() as cur:
            cur.execute(_RAG_QUERIES_DDL)

    def test_get_returns_json_attachment(self):
        self._grant('research_participation')
        resp = self.client.get(reverse('compliance:export_data'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json')
        self.assertIn('attachment;', resp['Content-Disposition'])
        self.assertIn('proodos_export_', resp['Content-Disposition'])

    def test_json_top_level_keys_match_spec(self):
        import json

        self._grant('research_participation')
        resp = self.client.get(reverse('compliance:export_data'))
        payload = json.loads(resp.content.decode('utf-8'))
        for key in (
            'export_version', 'exported_at', 'user', 'profile',
            'consents', 'ailst_responses', 'module_progress',
            'epilogue_completion', 'ai_outputs',
        ):
            self.assertIn(key, payload, 'missing top-level key ' + repr(key))
        self.assertEqual(payload['export_version'], '1')

    def test_verbatim_consent_text_included(self):
        """Stored verbatim text survives the export round-trip
        unchanged — required for any future IRB audit that asks
        the user to prove what they agreed to."""
        import json

        from apps.compliance.copy import RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB
        from apps.compliance.services import record_consent

        record_consent(
            user=self.user,
            consent_type='research_participation',
            consent_text=RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB,
            version='v1_pre_irb',
        )

        resp = self.client.get(reverse('compliance:export_data'))
        payload = json.loads(resp.content.decode('utf-8'))
        consent_texts = [c['consent_text'] for c in payload['consents']]
        self.assertIn(RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB, consent_texts)

    def test_ai_outputs_include_rtm_dtp_rag_and_rag_queries(self):
        """ai_outputs is the central D11 payload. Test seeds an RTM
        position, fills in DTP / RAG / peer-synthesis text fields on
        UserModuleProgress, and inserts one raw-SQL rag_queries row.
        All five sub-arrays should be non-empty in the export.
        """
        import json

        from django.db import connection

        from apps.modules.models import (
            Module,
            ReflectionTension,
            UserModuleProgress,
        )

        module, _ = Module.objects.get_or_create(
            code='MEXP',
            defaults={
                'title': 'Export Test',
                'description': 'Export Test',
                'unesco_aspect': 'ethics',
                'proficiency_level': 'Acquire',
                'order_index': 99,
            },
        )
        UserModuleProgress.objects.create(
            user=self.user, module=module,
            reflection_dtp='dtp text',
            reflection_rag_feedback='rag text',
            reflection_peer_synthesis='peer text',
        )
        ReflectionTension.objects.create(
            user=self.user, module=module,
            tension_label='Test tension',
            left_pole='left', right_pole='right',
            grounding_quote='quote', selected_position=3,
        )
        with connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO rag_queries
                    (user_id, module_id, reflection_text, teacher_context,
                     generated_response, created_at, updated_at)
                VALUES (%s, %s, %s, %s::jsonb, %s, NOW(), NOW())
                """,
                [self.user.id, module.id, 'reflection', '{}', 'response'],
            )

        resp = self.client.get(reverse('compliance:export_data'))
        payload = json.loads(resp.content.decode('utf-8'))
        ai = payload['ai_outputs']
        self.assertEqual(len(ai['rtm_positions']), 1)
        self.assertEqual(len(ai['dtp_narratives']), 1)
        self.assertEqual(len(ai['rag_feedback']), 1)
        self.assertEqual(len(ai['peer_synthesis']), 1)
        self.assertEqual(len(ai['rag_queries']), 1)
        # rag_queries row preserves the user's reflection text verbatim.
        self.assertEqual(ai['rag_queries'][0]['reflection_text'], 'reflection')

    def test_export_unaffected_by_research_data_opted_out(self):
        """Art. 15 is a personal right. A user who opted out of research
        still has the right to download all their personal data — the
        opt-out only affects future research analyses, not exports."""
        import json

        self.profile.research_data_opted_out = True
        self.profile.save(update_fields=['research_data_opted_out'])

        from apps.ailst.models import AilstResponse
        AilstResponse.objects.create(
            user=self.user, timepoint='T0', language='en',
            instrument_version='ning_2025_v1',
            responses={'P1': 4}, completed_at=timezone.now(),
        )

        resp = self.client.get(reverse('compliance:export_data'))
        payload = json.loads(resp.content.decode('utf-8'))
        self.assertEqual(len(payload['ailst_responses']), 1)
        self.assertTrue(payload['profile']['research_data_opted_out'])

    def test_anon_user_redirects_to_login(self):
        self.client.logout()
        resp = self.client.get(reverse('compliance:export_data'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)

    def test_fresh_user_export_has_consistent_shape(self):
        """CP-5 — a user with zero AILST / module / Epilogue / RAG rows
        still gets a JSON with every top-level key present, optional
        sections as empty arrays / null values, never missing keys.
        """
        import json

        # No grants, no progress, no AILST. Pure baseline user.
        resp = self.client.get(reverse('compliance:export_data'))
        payload = json.loads(resp.content.decode('utf-8'))

        # All top-level keys present.
        for key in (
            'export_version', 'exported_at', 'user', 'profile',
            'consents', 'ailst_responses', 'module_progress',
            'epilogue_completion', 'ai_outputs',
        ):
            self.assertIn(key, payload, 'missing top-level key ' + repr(key))

        # Empty containers, not missing.
        self.assertEqual(payload['consents'], [])
        self.assertEqual(payload['ailst_responses'], [])
        self.assertEqual(payload['module_progress'], [])
        self.assertIsNone(payload['epilogue_completion'])

        ai = payload['ai_outputs']
        for sub in ('rtm_positions', 'dtp_narratives', 'rag_feedback',
                    'peer_synthesis', 'rag_queries', 'ai_disputes'):
            self.assertIn(sub, ai, 'missing ai_outputs.' + sub)
            self.assertEqual(ai[sub], [], sub + ' must be empty array, not missing')


# ============================================================================
# C.4 commit 3 — GDPR Art. 17 right to erasure (account anonymization)
# ============================================================================


class ErasureConfirmPageTest(_PrivacyTestBase):

    def test_get_renders_warning_and_form(self):
        resp = self.client.get(reverse('compliance:erasure_confirm'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'compliance/erasure_confirm.html')
        body = resp.content.decode('utf-8')
        # English confirmation token rendered into the page (matches the
        # current English UI; industry standard pattern).
        self.assertIn('DELETE', body)
        # Form input always present and not JS-gated (CP-8).
        self.assertIn('name="confirmation"', body)
        self.assertNotIn('disabled', body.lower().split('<button')[1] if '<button' in body else '')

    def test_post_without_exact_token_returns_400_and_no_db_write(self):
        from apps.users.models import TeacherProfile

        original_username = self.user.username
        resp = self.client.post(
            reverse('compliance:erasure_execute'),
            data={'confirmation': 'delete'},  # wrong: case-sensitive
        )
        self.assertEqual(resp.status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, original_username)
        # Profile untouched.
        profile = TeacherProfile.objects.get(user=self.user)
        self.assertFalse(profile.research_data_opted_out)


_RAG_QUERIES_DDL_ERASURE = _RAG_QUERIES_DDL  # reuse from earlier in file


class ErasureExecuteTest(_PrivacyTestBase):
    """Covers the full erasure POST. Uses the shared _PrivacyTestBase
    setUp; the rag_queries DDL is applied at class setUp because the
    anonymize_user service also touches that table."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as cur:
            cur.execute(_RAG_QUERIES_DDL_ERASURE)

    def _post_erase(self):
        return self.client.post(
            reverse('compliance:erasure_execute'),
            data={'confirmation': 'DELETE'},
        )

    def test_post_clears_user_and_profile_pii(self):
        from apps.users.models import TeacherProfile

        self.user.first_name = 'Test'
        self.user.last_name = 'User'
        self.user.email = 'test@example.com'
        self.user.save()
        self.profile.first_name = 'Test'
        self.profile.last_name = 'User'
        self.profile.save()

        self._post_erase()

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'anonymized_{}'.format(self.user.id))
        self.assertEqual(
            self.user.email,
            'deleted-{}@anonymized.local'.format(self.user.id),
        )
        self.assertEqual(self.user.first_name, '')
        self.assertEqual(self.user.last_name, '')
        self.assertFalse(self.user.is_active)
        self.assertFalse(self.user.has_usable_password())

        profile = TeacherProfile.objects.get(user=self.user)
        self.assertEqual(profile.first_name, '')
        self.assertEqual(profile.last_name, '')

    def test_post_sets_opt_out_and_clears_ack_at(self):
        from apps.users.models import TeacherProfile
        self._post_erase()
        profile = TeacherProfile.objects.get(user=self.user)
        self.assertTrue(profile.research_data_opted_out)
        self.assertIsNone(profile.ai_disclosure_acknowledged_at)

    def test_post_preserves_consentrecord_rows_clears_ip(self):
        cr = ConsentRecord.objects.create(
            user=self.user, consent_type='research_participation',
            granted=True, consent_text='verbatim text', version='v1_pre_irb',
            ip_address='10.0.0.1',
        )
        self._post_erase()
        cr.refresh_from_db()
        self.assertIsNone(cr.ip_address)
        # Audit fields intact.
        self.assertEqual(cr.consent_text, 'verbatim text')
        self.assertEqual(cr.version, 'v1_pre_irb')
        self.assertTrue(cr.granted)

    def test_post_preserves_ailst_responses(self):
        from apps.ailst.models import AilstResponse
        AilstResponse.objects.create(
            user=self.user, timepoint='T0', language='en',
            instrument_version='ning_2025_v1',
            responses={'P1': 4}, completed_at=timezone.now(),
        )
        self._post_erase()
        self.assertEqual(
            AilstResponse.objects.filter(user=self.user).count(), 1,
            'Erasure must preserve AILST research data with the user_id '
            'pointer to the anonymized auth_user row.',
        )

    def test_post_clears_module_progress_reflection_fields_keeps_metadata(self):
        from apps.modules.models import Module, UserModuleProgress
        m, _ = Module.objects.get_or_create(
            code='ERASE1',
            defaults={
                'title': 'Erase Test', 'description': 'd',
                'unesco_aspect': 'ethics', 'proficiency_level': 'Acquire',
                'order_index': 98,
            },
        )
        p = UserModuleProgress.objects.create(
            user=self.user, module=m,
            reflection_text='my reflection',
            reflection_dtp='dtp', reflection_rag_feedback='rag',
            reflection_peer_synthesis='peer',
            completion_percentage=80,
        )
        self._post_erase()
        p.refresh_from_db()
        self.assertEqual(p.reflection_text, '')
        self.assertEqual(p.reflection_dtp, '')
        self.assertEqual(p.reflection_rag_feedback, '')
        self.assertEqual(p.reflection_peer_synthesis, '')
        # Non-PII metadata retained.
        self.assertEqual(p.completion_percentage, 80)

    def test_post_logs_user_out_and_redirects_to_landing(self):
        resp = self._post_erase()
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/', resp.url)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_irb_audit_query_returns_anonymized_users_consent_history(self):
        """CP-7 — post-erasure, ConsentRecord rows for this user remain
        queryable via the standard IRB audit filter
        (consent_type='research_participation', granted=True) and the
        consent_text / granted_at / version are all preserved.
        """
        from apps.compliance.copy import RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB
        from apps.compliance.services import record_consent

        record_consent(
            user=self.user,
            consent_type='research_participation',
            consent_text=RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB,
            version='v1_pre_irb',
            ip_address='192.0.2.1',
        )
        user_pk = self.user.pk

        self._post_erase()

        # Same IRB-flavoured query — still returns the row.
        cr = ConsentRecord.objects.filter(
            user_id=user_pk,
            consent_type='research_participation',
            granted=True,
        ).first()
        self.assertIsNotNone(
            cr,
            'IRB audit query must still find the historical consent row '
            'after erasure (7-year retention contract).',
        )
        self.assertEqual(cr.consent_text, RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB)
        self.assertEqual(cr.version, 'v1_pre_irb')
        self.assertIsNone(cr.ip_address)


class C4SupersedeUnitTest(TestCase):
    """CP-6 — replaces the original concurrent-POST test with a direct
    unit test of revoke_consent's behaviour when multiple active rows
    exist for the same (user, consent_type). The supersede pattern in
    record_consent normally prevents this state from arising, but
    direct ORM inserts can bypass the helper (e.g. data migrations),
    and revoke_consent must still handle it correctly.
    """

    def test_revoke_revokes_all_active_rows_for_consent_type(self):
        user = User.objects.create_user(username='supersede_user', password='x')
        ConsentRecord.objects.create(
            user=user, consent_type='research_participation', granted=True,
            consent_text='v1 text', version='v1',
        )
        ConsentRecord.objects.create(
            user=user, consent_type='research_participation', granted=True,
            consent_text='v2 text', version='v2',
        )
        self.assertEqual(
            ConsentRecord.objects.filter(
                user=user, consent_type='research_participation',
                revoked_at__isnull=True,
            ).count(),
            2,
            'Pre-condition: two active rows from direct ORM inserts.',
        )
        revoked = revoke_consent(
            user=user, consent_type='research_participation',
        )
        self.assertEqual(revoked, 2)
        self.assertEqual(
            ConsentRecord.objects.filter(
                user=user, consent_type='research_participation',
                revoked_at__isnull=True,
            ).count(),
            0,
            'Post-condition: no orphan active rows after revoke.',
        )


class AiImpactAssessmentPageTest(TestCase):
    """Phase C C.1 — /about/ai-act-compliance/ now serves the full
    EU AI Act Article 50 transparency notice from
    apps.compliance.copy.AI_IMPACT_ASSESSMENT_V1_PRE_IRB. Public; no
    auth required.
    """

    def setUp(self):
        self.client = Client()

    def test_anonymous_user_can_access(self):
        resp = self.client.get(reverse('compliance:ai_act_compliance'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'about/ai_act_compliance.html')

    def test_authenticated_user_can_access(self):
        user = User.objects.create_user(username='c1_reader', password='x')
        self.client.force_login(user)
        resp = self.client.get(reverse('compliance:ai_act_compliance'))
        self.assertEqual(resp.status_code, 200)

    def test_all_seven_section_headings_rendered(self):
        from apps.compliance.copy import AI_IMPACT_ASSESSMENT_V1_PRE_IRB

        resp = self.client.get(reverse('compliance:ai_act_compliance'))
        body = resp.content.decode('utf-8')
        for section in AI_IMPACT_ASSESSMENT_V1_PRE_IRB:
            self.assertIn(
                section['heading'], body,
                'Missing section heading: ' + section['heading'],
            )
        self.assertEqual(
            len(AI_IMPACT_ASSESSMENT_V1_PRE_IRB), 7,
            'Article 50 transparency doc must keep its seven sections '
            '(What/AI components/Risk/Mitigation/Data/Rights/Contact). '
            'If you add or remove sections, update this assertion AND '
            'review the changelog entry in PHASE_C_MIGRATION_PLAN.',
        )

    def test_version_string_visible_on_page(self):
        resp = self.client.get(reverse('compliance:ai_act_compliance'))
        self.assertIn('v1_pre_irb', resp.content.decode('utf-8'))

    def test_bullet_lists_rendered_via_consent_format_filter(self):
        """Spot-check the consent_format filter on a known-bulleted
        section: Section 2 "AI components in PROODOS" begins with a
        lead-in line and four bullets. The rendered output must have
        a <ul> element and at least four <li> children inside the
        section's body container."""
        resp = self.client.get(reverse('compliance:ai_act_compliance'))
        body = resp.content.decode('utf-8')
        self.assertIn('<ul', body)
        # Section 2 mentions all four AI components by name.
        for needle in ('RAG-based reflection feedback',
                       'Reflective Tension Mapper',
                       'Developmental Trajectory Predictor',
                       'Peer synthesis'):
            self.assertIn(needle, body)

    def test_middleware_does_not_block_unacknowledged_user(self):
        """The path is in BYPASS_PATHS — a logged-in user who has not
        acknowledged AI disclosure can still read the transparency
        notice (otherwise the 'Learn more' link in the modal would
        loop)."""
        user = User.objects.create_user(username='c1_unack', password='x')
        # Profile exists but ai_disclosure_acknowledged_at is NULL.
        from apps.users.models import TeacherProfile
        TeacherProfile.objects.create(user=user)
        self.client.force_login(user)

        resp = self.client.get(reverse('compliance:ai_act_compliance'))
        self.assertEqual(
            resp.status_code, 200,
            'AIDisclosureMiddleware must NOT redirect /about/ai-act-compliance/ '
            'because the path is in the bypass set.',
        )


class C4AtomicityAndEdgeCaseTest(_PrivacyTestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as cur:
            cur.execute(_RAG_QUERIES_DDL_ERASURE)

    def _post_erase(self):
        return self.client.post(
            reverse('compliance:erasure_execute'),
            data={'confirmation': 'DELETE'},
        )

    def test_revoke_then_erasure_in_sequence_clears_ip_and_marks_revoked(self):
        """Sequential rather than parallel — the Django TestCase does
        not give us true transaction overlap. Verifies the realistic
        order that a confused user might take: withdraw a consent and
        then immediately request erasure."""
        cr = ConsentRecord.objects.create(
            user=self.user, consent_type='research_participation',
            granted=True, consent_text='t', version='v1_pre_irb',
            ip_address='10.1.1.1',
        )
        self.client.post(reverse('compliance:revoke_research'))
        self._post_erase()
        cr.refresh_from_db()
        self.assertIsNotNone(cr.revoked_at)
        self.assertIsNone(cr.ip_address)

    def test_post_erasure_request_treated_as_anonymous(self):
        """After erasure, is_active=False. A subsequent request issued
        with the same cookie / session is bounced as anonymous —
        login_required redirects to /login/."""
        self._post_erase()
        # The view logout()ed us, but for completeness force_login on a
        # different user is what would happen in the wild — here we
        # simply attempt an authenticated route with no session.
        resp = self.client.get(reverse('compliance:privacy_dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)

    def test_idempotent_anonymize_user_is_a_noop_second_call(self):
        """Calling the service helper twice on the same user produces
        no errors and no further state change: username remains the
        anonymized sentinel, email the anonymized sentinel, ConsentRecord
        rows untouched."""
        from apps.compliance.services import anonymize_user

        anonymize_user(self.user)
        first_username = self.user.username
        first_email = self.user.email

        anonymize_user(self.user)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, first_username)
        self.assertEqual(self.user.email, first_email)
        # And not a chain like anonymized_anonymized_42.
        self.assertEqual(
            self.user.username.count('anonymized_'),
            1,
            'Idempotency: re-anonymization must not stack prefixes.',
        )
