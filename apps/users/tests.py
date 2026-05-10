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
