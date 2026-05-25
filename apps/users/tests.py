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
        # Phase H H.6 (2026-05-25): version bumped from v1_pre_irb to
        # v2_followup_bundled when the follow-up-pool permission was
        # bundled into the research_participation consent text.
        self.assertEqual(cr.version, 'v2_followup_bundled')

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
        """Regression: stored consent_text matches the active V2 constant
        verbatim. Catches text drift without an explicit version bump.

        Phase H H.6 (2026-05-25): bumped from V1 to V2 when the
        follow-up-pool permission was bundled into the consent text.
        """
        from apps.compliance.copy import (
            RESEARCH_PARTICIPATION_TEXT_V2_FOLLOWUP_BUNDLED,
        )

        self._post_step3(research=True)
        cr = ConsentRecord.objects.get(
            user=self.user, consent_type='research_participation',
        )
        self.assertEqual(
            cr.consent_text,
            RESEARCH_PARTICIPATION_TEXT_V2_FOLLOWUP_BUNDLED,
        )

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


# ============================================================================
# C.2.5b: separate confirm interstitial after Step 3
# ============================================================================


class OnboardingConfirmInterstitialTest(TestCase):
    """Phase C C.2.5b — Step 3 POST now redirects to /onboarding/confirm/,
    the short interstitial that hosts the "Continue to AI Literacy
    baseline" CTA. The summary page (/onboarding/summary/) becomes a
    read-only drill-down with no state-change responsibilities.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='confirm_user', password='x')
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            subject_area='mathematics', grade_level='primary',
            teaching_years='6-15',
            school_location='urban',
            average_class_size='medium',
            ai_experience='basic',
            preferred_communication_style='balanced',
            research_consent=False,
            consent_data_sharing=False,
            ai_disclosure_acknowledged_at=timezone.now(),
        )
        self.client.force_login(self.user)

    def _set_step(self, n):
        session = self.client.session
        session['onboarding_step'] = n
        session.save()

    def test_step3_post_redirects_to_confirm_not_summary(self):
        """Step 3 POST should send the user to the confirm interstitial."""
        self._set_step(2)
        resp = self.client.post(
            reverse('users:onboarding_step3'),
            data={'preferred_communication_style': 'balanced'},
        )
        self.assertRedirects(
            resp,
            reverse('users:onboarding_confirm'),
            fetch_redirect_response=False,
        )

    def test_confirm_get_renders_for_completed_steps(self):
        self._set_step(3)
        resp = self.client.get(reverse('users:onboarding_confirm'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'onboarding/confirm.html')
        body = resp.content.decode('utf-8')
        # All three CTA labels must appear.
        self.assertIn('Continue to AI Literacy baseline', body)
        self.assertIn('Review my profile', body)
        self.assertIn('Back to Step 3', body)

    def test_confirm_get_redirects_when_steps_incomplete(self):
        self._set_step(1)
        resp = self.client.get(reverse('users:onboarding_confirm'))
        self.assertRedirects(
            resp,
            reverse('users:onboarding_step1'),
            fetch_redirect_response=False,
        )

    def test_confirm_post_completes_profile_and_redirects_to_AILST(self):
        self._set_step(3)
        resp = self.client.post(reverse('users:onboarding_confirm'))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/ailst/t0/'))

        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_completed)
        self.assertIsNotNone(self.profile.profile_completion_date)

        # Session marker advances to 4.
        self.assertEqual(self.client.session.get('onboarding_step'), 4)

    def test_summary_get_renders_readonly_with_back_to_confirm_link(self):
        self._set_step(3)
        resp = self.client.get(reverse('users:onboarding_summary'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'onboarding/summary.html')
        body = resp.content.decode('utf-8')
        # The "Continue to AI Literacy baseline" CTA must be GONE from
        # the summary page — it lives on confirm only.
        self.assertNotIn('Continue to AI Literacy baseline', body)
        # And a navigation back to confirm must exist.
        self.assertIn('Back to confirmation', body)


# ============================================================================
# Phase H.7 — Dashboard redesign tests (TD-021 resolution)
# ============================================================================

from django.urls import reverse
from django.utils import timezone as _tz

from apps.ailst.models import AilstResponse
from apps.epilogue.models import EpilogueCompletion
from apps.modules.models import Module, UserModuleProgress
from apps.users.services import (
    build_personal_unesco_matrix,
    certificate_state_for_dashboard,
    next_action_for_dashboard,
)


def _h7_seed_modules():
    """15 published modules across the 5x3 grid; required by the matrix."""
    grid = [
        ('human_centered', 'Acquire'), ('ethics', 'Acquire'),
        ('ai_foundations', 'Acquire'), ('ai_pedagogy', 'Acquire'),
        ('professional_development', 'Acquire'),
        ('human_centered', 'Deepen'), ('ethics', 'Deepen'),
        ('ai_foundations', 'Deepen'), ('ai_pedagogy', 'Deepen'),
        ('professional_development', 'Deepen'),
        ('human_centered', 'Create'), ('ethics', 'Create'),
        ('ai_foundations', 'Create'), ('ai_pedagogy', 'Create'),
        ('professional_development', 'Create'),
    ]
    for i, (aspect, level) in enumerate(grid, start=1):
        Module.objects.create(
            code=f'M{i}', unesco_aspect=aspect, proficiency_level=level,
            title=f'Module {i} title', description='-', order_index=i,
            is_published=True,  # default is False; matrix filters on it
        )


def _h7_make_user(username='h7_user'):
    user = User.objects.create_user(username=username, password='pw')
    TeacherProfile.objects.create(
        user=user, subject_area='mathematics', grade_level='primary',
        teaching_years='6-15', school_location='urban',
        average_class_size='medium', ai_experience='basic',
        preferred_communication_style='balanced',
        ai_disclosure_acknowledged_at=_tz.now(),
        profile_completed=True, research_consent=True,
    )
    return user


class PersonalUnescoMatrixTest(TestCase):
    """Per-teacher 5x3 matrix classifies each cell as locked / in_progress / complete."""

    def setUp(self):
        _h7_seed_modules()
        self.user = _h7_make_user()

    def test_all_cells_locked_when_no_progress(self):
        m = build_personal_unesco_matrix(self.user)
        self.assertEqual(m['kind'], 'personal')
        states = [cell['state']
                  for row in m['rows'] for cell in row['cells'] if cell]
        self.assertEqual(set(states), {'locked'})

    def test_started_module_is_in_progress(self):
        m1 = Module.objects.get(code='M1')
        UserModuleProgress.objects.create(user=self.user, module=m1)
        matrix = build_personal_unesco_matrix(self.user)
        m1_cell = matrix['rows'][0]['cells'][0]
        self.assertEqual(m1_cell['state'], 'in_progress')

    def test_completed_module_is_complete(self):
        m1 = Module.objects.get(code='M1')
        UserModuleProgress.objects.create(
            user=self.user, module=m1, completed_at=_tz.now(),
        )
        matrix = build_personal_unesco_matrix(self.user)
        self.assertEqual(matrix['rows'][0]['cells'][0]['state'], 'complete')

    def test_cell_carries_module_link(self):
        matrix = build_personal_unesco_matrix(self.user)
        self.assertIn('/modules/M1/', matrix['rows'][0]['cells'][0]['url'])

    def test_outer_shape_matches_cohort(self):
        """Same outer keys as analytics.cohort_unesco_matrix so the
        shared partial can render both interchangeably."""
        m = build_personal_unesco_matrix(self.user)
        for key in ('kind', 'levels', 'rows', 'total_teachers'):
            self.assertIn(key, m)


class NextActionForDashboardTest(TestCase):
    """4 contextual states ordered by precedence."""

    def setUp(self):
        _h7_seed_modules()
        self.user = _h7_make_user('next_user')

    def test_state_continue_module_when_modules_remain(self):
        action = next_action_for_dashboard(self.user)
        self.assertEqual(action['state'], 'continue_module')
        self.assertIn('M1', action['title'])
        self.assertIn('/modules/M1/', action['cta_url'])

    def test_state_visit_epilogue_after_all_modules_complete(self):
        for m in Module.objects.all():
            UserModuleProgress.objects.create(
                user=self.user, module=m, completed_at=_tz.now(),
            )
        action = next_action_for_dashboard(self.user)
        self.assertEqual(action['state'], 'visit_epilogue')
        self.assertEqual(action['cta_url'], '/epilogue/')

    def test_state_complete_ailst_t2_after_epilogue_completed(self):
        for m in Module.objects.all():
            UserModuleProgress.objects.create(
                user=self.user, module=m, completed_at=_tz.now(),
            )
        EpilogueCompletion.objects.create(
            user=self.user, completed_at=_tz.now(),
        )
        action = next_action_for_dashboard(self.user)
        self.assertEqual(action['state'], 'complete_ailst_t2')
        self.assertEqual(action['cta_url'], '/ailst/t2/')

    def test_state_programme_complete_after_t2(self):
        for m in Module.objects.all():
            UserModuleProgress.objects.create(
                user=self.user, module=m, completed_at=_tz.now(),
            )
        EpilogueCompletion.objects.create(
            user=self.user, completed_at=_tz.now(),
        )
        AilstResponse.objects.create(
            user=self.user, timepoint='T2', completed_at=_tz.now(),
            responses={f'P{i}': 4 for i in range(1, 37)},
            instrument_version='ning_2025_v1',
        )
        action = next_action_for_dashboard(self.user)
        self.assertEqual(action['state'], 'programme_complete')
        self.assertEqual(action['cta_url'], '/certification/download/')

    def test_teacher_facing_text_does_not_leak_internal_labels(self):
        """Per the no-internal-labels rule: no 'Stage 0/1/2/3', 'T2',
        'AILST', 'DTP', 'RTM' in teacher-facing copy."""
        for m in Module.objects.all():
            UserModuleProgress.objects.create(
                user=self.user, module=m, completed_at=_tz.now(),
            )
        EpilogueCompletion.objects.create(
            user=self.user, completed_at=_tz.now(),
        )
        action = next_action_for_dashboard(self.user)
        combined = (action['title'] + action['body'] + action['cta_label'])
        for label in ('Stage 0', 'Stage 1', 'Stage 2', 'Stage 3',
                      'AILST', 'T2', 'T0', 'T1', 'DTP', 'RTM'):
            self.assertNotIn(label, combined,
                             f'Internal label {label!r} leaked: {combined!r}')


class CertificateStateForDashboardTest(TestCase):
    """Three states: locked (pre-T2), available (T2 done, no cert), issued."""

    def setUp(self):
        _h7_seed_modules()
        self.user = _h7_make_user('cert_state_user')

    def test_locked_when_no_t2(self):
        s = certificate_state_for_dashboard(self.user)
        self.assertEqual(s['state'], 'locked')
        self.assertIsNone(s['verification_code'])

    def test_available_after_t2_no_cert_yet(self):
        AilstResponse.objects.create(
            user=self.user, timepoint='T2', completed_at=_tz.now(),
            responses={f'P{i}': 4 for i in range(1, 37)},
            instrument_version='ning_2025_v1',
        )
        s = certificate_state_for_dashboard(self.user)
        self.assertEqual(s['state'], 'available')
        self.assertIsNone(s['verification_code'])

    def test_issued_after_certificate_row_exists(self):
        AilstResponse.objects.create(
            user=self.user, timepoint='T2', completed_at=_tz.now(),
            responses={f'P{i}': 4 for i in range(1, 37)},
            instrument_version='ning_2025_v1',
        )
        from apps.certification.services import get_or_issue_certificate
        cert = get_or_issue_certificate(self.user)
        s = certificate_state_for_dashboard(self.user)
        self.assertEqual(s['state'], 'issued')
        self.assertEqual(s['verification_code'], cert.verification_code)
        self.assertIsNotNone(s['issued_at'])


class DashboardViewRedesignTest(TestCase):
    """The /dashboard/ view drops modules_with_progress and renders the
    redesigned home.html with the personal matrix, the next-action card,
    and the certificate panel."""

    def setUp(self):
        _h7_seed_modules()
        self.user = _h7_make_user('dashboard_user')
        self.client.force_login(self.user)

    def test_context_drops_modules_with_progress(self):
        resp = self.client.get(reverse('users:dashboard'))
        self.assertEqual(resp.status_code, 200)
        # Old context key must NOT appear; new ones must.
        self.assertNotIn('modules_with_progress', resp.context)
        self.assertIn('personal_matrix', resp.context)
        self.assertIn('next_action', resp.context)
        self.assertIn('certificate_state', resp.context)

    def test_renders_matrix_partial(self):
        resp = self.client.get(reverse('users:dashboard'))
        body = resp.content.decode('utf-8')
        # Shared partial puts the 15 module codes into the matrix cells.
        for i in range(1, 16):
            self.assertIn(f'>M{i}<', body)

    def test_renders_certificate_locked_pre_t2(self):
        resp = self.client.get(reverse('users:dashboard'))
        body = resp.content.decode('utf-8')
        self.assertIn('Locked', body)
        self.assertIn('closing self-assessment', body)

    def test_inline_emojis_removed(self):
        """Per workflow rule 5 (no emojis in code) — the previous
        home.html had inline emojis (📊 📚 🚀 ✓). The redesign removes
        them."""
        resp = self.client.get(reverse('users:dashboard'))
        body = resp.content.decode('utf-8')
        for em in ('📊', '📚', '🚀', '✓'):
            self.assertNotIn(em, body,
                             f'Emoji {em!r} should have been removed.')


class AnalyticsCohortMatrixRegressionTest(TestCase):
    """Verify the analytics cohort matrix still renders correctly after the
    partial-lift refactor (the shared partial must handle both kinds)."""

    def setUp(self):
        _h7_seed_modules()
        self.staff = User.objects.create_user(
            username='analytics_staff', password='pw',
            is_staff=True,
        )
        TeacherProfile.objects.create(
            user=self.staff, subject_area='mathematics', grade_level='primary',
            teaching_years='6-15', school_location='urban',
            average_class_size='medium', ai_experience='basic',
            preferred_communication_style='balanced',
            ai_disclosure_acknowledged_at=_tz.now(),
            profile_completed=True, research_consent=True,
        )
        self.client.force_login(self.staff)

    def test_cohort_matrix_still_renders(self):
        resp = self.client.get('/analytics/')
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode('utf-8')
        # All 15 module codes should appear in the matrix.
        for i in range(1, 16):
            self.assertIn(f'>M{i}<', body)

    def test_cohort_matrix_has_rate_shading(self):
        """Cohort branch of the partial uses the green-rate shading."""
        resp = self.client.get('/analytics/')
        body = resp.content.decode('utf-8')
        self.assertIn('rgba(34,197,94', body)
