"""
Tests for the users app.

Phase C C.2.1 introduces tests for the Profile Edit extension:
3 new personalization fields wired into ProfileEditForm + integration
with the M3 history signal (TeacherProfileHistory rows + change_source
attribution).
"""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.users.models import TeacherProfile, TeacherProfileHistory


class ProfileEditPhaseCFieldsTest(TestCase):
    """Phase C C.2.1 — Profile Edit form extended with 3 personalization fields.

    Setup: create a user with a fully-populated 'baseline' profile so that
    submitting the same baseline values via the form produces ZERO changes.
    Tests then override specific fields to verify the change is recorded
    correctly by the M3 signal.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='editor', password='x')
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            subject_area='mathematics',
            grade_level='primary',
            teaching_years='6-15',
            school_location='urban',
            average_class_size='medium',
            ai_experience='basic',
            preferred_communication_style='balanced',
            # Pre-acknowledge AI disclosure so the middleware doesn't redirect.
            ai_disclosure_acknowledged_at=timezone.now(),
        )
        self.client.force_login(self.user)
        self.url = reverse('users:profile_edit')

    def _post(self, **overrides):
        """Build a baseline-matching POST payload, with overrides applied.

        Default payload submits the SAME values as the profile's setUp
        baseline, so without overrides the form produces no changes and
        no history rows. Each test overrides only the fields under test.
        """
        data = {
            'subject_area':                  'mathematics',
            'grade_level':                   'primary',
            'teaching_years':                '6-15',
            'school_location':               'urban',
            'average_class_size':            'medium',
            'ai_experience':                 'basic',
            'preferred_communication_style': 'balanced',
            # Phase C new fields — defaults match an unset profile (NULL/empty).
            'current_curriculum_pressure':   '',
            'institutional_ai_policy':       '',
            'student_population_special_needs': [],
        }
        data.update(overrides)
        return self.client.post(self.url, data)

    def test_edit_stores_three_new_fields(self):
        """All 3 new Phase C fields persist correctly after a valid edit."""
        response = self._post(
            current_curriculum_pressure='high',
            institutional_ai_policy='restrictive',
            student_population_special_needs=['gifted', 'language_minority'],
        )
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.current_curriculum_pressure, 'high')
        self.assertEqual(self.profile.institutional_ai_policy, 'restrictive')
        self.assertEqual(
            sorted(self.profile.student_population_special_needs),
            ['gifted', 'language_minority'],
        )

    def test_edit_triggers_teacher_profile_history_rows(self):
        """M3 signal records history rows for changed Phase C fields."""
        self.assertEqual(
            TeacherProfileHistory.objects.filter(user=self.user).count(), 0,
        )
        self._post(
            current_curriculum_pressure='high',
            institutional_ai_policy='restrictive',
        )
        rows = TeacherProfileHistory.objects.filter(user=self.user)
        changed_fields = set(rows.values_list('field_name', flat=True))
        self.assertIn('current_curriculum_pressure', changed_fields)
        self.assertIn('institutional_ai_policy', changed_fields)
        # student_population_special_needs was [] before and after → no row.
        self.assertNotIn('student_population_special_needs', changed_fields)

    def test_change_source_propagated_to_history_rows(self):
        """View sets _change_source='profile_edit' so all history rows from
        this save event carry that attribution."""
        self._post(current_curriculum_pressure='high')
        rows = TeacherProfileHistory.objects.filter(user=self.user)
        self.assertGreater(rows.count(), 0)
        for row in rows:
            self.assertEqual(row.change_source, 'profile_edit')

    def test_sen_none_with_others_rejected(self):
        """Form-level validation: 'none' cannot combine with other SEN values."""
        response = self._post(
            student_population_special_needs=['none', 'gifted'],
        )
        self.assertEqual(response.status_code, 200)  # form re-rendered with error
        self.assertContains(response, 'leave the other options unchecked')
        self.profile.refresh_from_db()
        # Profile NOT updated due to validation failure.
        self.assertEqual(self.profile.student_population_special_needs, [])

    def test_sen_valid_combinations_accepted(self):
        """Multiple non-'none' values are stored as a list."""
        response = self._post(
            student_population_special_needs=['learning_disability', 'language_minority'],
        )
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(
            sorted(self.profile.student_population_special_needs),
            ['language_minority', 'learning_disability'],
        )

    def test_three_fields_editable_independently(self):
        """Each Phase C field can be edited without affecting the other two."""
        # Edit 1: only current_curriculum_pressure
        self._post(current_curriculum_pressure='variable')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.current_curriculum_pressure, 'variable')
        self.assertIsNone(self.profile.institutional_ai_policy)

        # Edit 2: only institutional_ai_policy (preserve curriculum_pressure)
        self._post(
            current_curriculum_pressure='variable',
            institutional_ai_policy='explicit_supportive',
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.institutional_ai_policy, 'explicit_supportive')
        self.assertEqual(self.profile.current_curriculum_pressure, 'variable')

        # Edit 3: only student_population_special_needs
        self._post(
            current_curriculum_pressure='variable',
            institutional_ai_policy='explicit_supportive',
            student_population_special_needs=['gifted'],
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.student_population_special_needs, ['gifted'])


# ============================================================
# Phase C C.2.2 — Onboarding Step 3 research consent flow
# ============================================================

from apps.compliance.models import ConsentRecord


class OnboardingStep3ConsentTest(TestCase):
    """Phase C C.2.2 — Step 3 writes consents via record_consent / revoke_consent
    instead of direct boolean writes. The M6 sync signal keeps the
    TeacherProfile booleans in sync as a backwards-compat read cache.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='step3_user', password='x')
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            subject_area='mathematics', grade_level='primary',
            teaching_years='6-15',
            school_location='urban',
            average_class_size='medium',
            ai_experience='basic',
            preferred_communication_style='balanced',
            # Explicit override of the legacy research_consent default=True.
            # We want a clean baseline matching "no active ConsentRecord row"
            # so the M6 signal's True/False transitions are observable.
            research_consent=False,
            consent_data_sharing=False,
            # Pre-acknowledge AI disclosure so the middleware doesn't redirect.
            ai_disclosure_acknowledged_at=timezone.now(),
        )
        self.client.force_login(self.user)

        # Step 3 view requires session marker indicating Step 2 was completed.
        session = self.client.session
        session['onboarding_step'] = 2
        session.save()

        self.url = reverse('users:onboarding_step3')

    def _post_step3(self, *, research=False, data_sharing=False, contact=False,
                    **extra):
        """Build a Step-3 POST payload. Boolean fields use 'on' when checked."""
        data = {
            'preferred_communication_style': 'balanced',
        }
        if research:
            data['consent_research_participation'] = 'on'
        if data_sharing:
            data['consent_data_sharing'] = 'on'
        if contact:
            data['contact_for_research'] = 'on'
        data.update(extra)
        return self.client.post(self.url, data)

    def test_research_consent_checked_creates_consentrecord(self):
        response = self._post_step3(research=True)
        self.assertEqual(response.status_code, 302)
        cr = ConsentRecord.objects.get(
            user=self.user, consent_type='research_participation',
        )
        self.assertTrue(cr.is_active)
        self.assertEqual(cr.version, 'v1_pre_irb')

    def test_research_consent_unchecked_does_not_create_consentrecord(self):
        self._post_step3(research=False)
        self.assertEqual(
            ConsentRecord.objects.filter(
                user=self.user, consent_type='research_participation',
            ).count(),
            0,
        )

    def test_data_sharing_independent_of_research_participation(self):
        """User can consent to data_sharing without research_participation
        (and vice versa). The two consents are evaluated independently."""
        self._post_step3(research=False, data_sharing=True)
        self.assertTrue(
            ConsentRecord.objects.filter(
                user=self.user, consent_type='data_sharing',
                granted=True, revoked_at__isnull=True,
            ).exists()
        )
        self.assertFalse(
            ConsentRecord.objects.filter(
                user=self.user, consent_type='research_participation',
                granted=True, revoked_at__isnull=True,
            ).exists()
        )

    def test_unchecking_previously_granted_consent_revokes_it(self):
        """Re-submission of Step 3 with checkbox unchecked must revoke the
        prior active row. The legacy boolean cache flips to False via the
        M6 signal."""
        self._post_step3(research=True)
        self.assertTrue(
            ConsentRecord.objects.filter(
                user=self.user, consent_type='research_participation',
                granted=True, revoked_at__isnull=True,
            ).exists()
        )
        self._post_step3(research=False)
        self.assertFalse(
            ConsentRecord.objects.filter(
                user=self.user, consent_type='research_participation',
                granted=True, revoked_at__isnull=True,
            ).exists()
        )
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.research_consent)

    def test_consent_text_stored_verbatim_matches_copy_module(self):
        """Regression: stored consent_text == RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB
        verbatim. Catches text drift without an explicit version bump.
        """
        from apps.compliance.copy import RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB

        self._post_step3(research=True)
        cr = ConsentRecord.objects.get(
            user=self.user, consent_type='research_participation',
        )
        self.assertEqual(cr.consent_text, RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB)

    def test_signal_syncs_booleans_after_step3_submission(self):
        """M6 signal updates TeacherProfile.research_consent boolean to mirror
        canonical ConsentRecord state."""
        self.assertFalse(self.profile.research_consent)
        self._post_step3(research=True)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.research_consent)

    def test_double_submission_does_not_create_duplicate_consents(self):
        """Browser back + resubmit with identical checkbox state must not
        create duplicate ConsentRecord rows."""
        self._post_step3(research=True, data_sharing=True)
        initial_count = ConsentRecord.objects.filter(user=self.user).count()
        self._post_step3(research=True, data_sharing=True)
        self.assertEqual(
            ConsentRecord.objects.filter(user=self.user).count(),
            initial_count,
        )
