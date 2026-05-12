"""
Tests for the apps.modules view layer.

Currently scoped to Phase C C.2.4 AILST research-instrument gating:
when a user completes M5 (Acquire phase end) or M15 (programme end),
the mark_tab_complete AJAX response must include an ailst_redirect_url
pointing the frontend to /ailst/t1/ or /ailst/t2/, gated on
research_consent and idempotent on already-completed AilstResponse rows.
"""

import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.ailst.models import AilstResponse
from apps.modules.models import Module, UserModuleProgress
from apps.users.models import TeacherProfile


class AilstModuleGatingTest(TestCase):
    """C.2.4: AILST gating injected into modules.mark_tab_complete.

    These tests submit the reflection tab (the canonical 'final tab'
    for a module — completing it sets progress.completed_at) and assert
    the JSON response includes or omits ailst_redirect_url under the
    relevant conditions.

    Background: the M4 / M5 migrations seed the AILST instrument; we do
    not need to seed modules separately because the Module rows are
    fixture data from earlier phases. Tests look up by `code`.
    """

    @classmethod
    def setUpTestData(cls):
        # No migration seeds Module rows; in production they are loaded
        # manually. The test DB is empty, so we create the three module
        # rows the tests need. order_index must be unique.
        seeds = (
            ('M3',  3,  'ethics',           'Acquire'),
            ('M5',  5,  'ai_foundations',   'Acquire'),
            ('M15', 15, 'professional_development', 'Create'),
        )
        for code, order_index, aspect, level in seeds:
            Module.objects.create(
                code=code,
                title=f'Test {code}',
                description=f'Test description for {code}',
                order_index=order_index,
                unesco_aspect=aspect,
                proficiency_level=level,
                is_published=True,
            )

    def setUp(self):
        self.client = Client()
        # is_staff so the TD-012 sequential prerequisite gate bypasses
        # for this test class. We are exercising the AILST routing logic
        # from mark_tab_complete, not the module ordering gate; the gate
        # has its own dedicated SequentialModuleGatingTest below.
        self.user = User.objects.create_user(
            username='gating_user', password='pw', is_staff=True,
        )
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            ai_disclosure_acknowledged_at=timezone.now(),
            profile_completed=True,
            research_consent=True,
        )
        self.client.force_login(self.user)

    def _ensure_progress_completable(self, module_code):
        """Create a UserModuleProgress with all prior tabs done so that
        the reflection submission flips completed_at to now()."""
        module = Module.objects.get(code=module_code)
        progress = UserModuleProgress.objects.create(
            user=self.user,
            module=module,
            introduction_completed=True,
            introduction_completed_at=timezone.now(),
            main_content_completed=True,
            main_content_completed_at=timezone.now(),
            activity_completed=True,
            activity_completed_at=timezone.now(),
            assessment_completed=True,
            assessment_completed_at=timezone.now(),
        )
        return module, progress

    def _post_reflection(self, module_code, reflection_text):
        url = reverse('modules:mark_tab_complete', kwargs={
            'code': module_code, 'tab_name': 'reflection',
        })
        return self.client.post(
            url,
            data=json.dumps({'reflection_text': reflection_text}),
            content_type='application/json',
        )

    def _valid_reflection_text(self):
        """A 350-word reflection — passes the 300-800 word validator."""
        sentence = (
            "I learned about how AI can support classroom planning and "
            "personalised feedback for students in meaningful ways. "
        )
        # 17 words per sentence; 21 sentences -> 357 words, comfortably valid.
        return (sentence * 21).strip()

    def test_completing_M5_redirects_to_T1_when_consent_and_T1_not_done(self):
        self._ensure_progress_completable('M5')
        resp = self._post_reflection('M5', self._valid_reflection_text())
        data = resp.json()
        # Reflection submission may fail under test conditions (no RAG
        # backend in the test environment) — but the mark_tab_complete
        # logic still runs as long as the validator passed.
        self.assertTrue(data.get('success'), msg=data)
        self.assertTrue(data.get('module_completed'))
        self.assertEqual(data.get('ailst_redirect_url'), '/ailst/t1/')
        self.assertEqual(
            data.get('ailst_redirect_label'),
            'Continue to AI Literacy assessment',
        )

    def test_completing_M5_no_redirect_when_T1_already_completed(self):
        self._ensure_progress_completable('M5')
        # User has already completed T1 in a prior pass.
        AilstResponse.objects.create(
            user=self.user,
            timepoint='T1',
            language='en',
            instrument_version='ning_2025_v1',
            responses={f'P{i}': 4 for i in range(1, 11)},
            completed_at=timezone.now(),
        )
        resp = self._post_reflection('M5', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertNotIn(
            'ailst_redirect_url', data,
            "Idempotency: completed T1 must suppress the redirect.",
        )

    def test_completing_M15_redirects_to_epilogue_not_to_T2(self):
        """C.2.5: T2 is reached via the Epilogue, not directly from M15.

        The mark_tab_complete response now sends a just-completed M15
        user to /epilogue/. The Epilogue completion view is then
        responsible for the (consent-gated) onward redirect to /ailst/t2/.
        """
        self._ensure_progress_completable('M15')
        resp = self._post_reflection('M15', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertEqual(data.get('ailst_redirect_url'), '/epilogue/')
        self.assertEqual(
            data.get('ailst_redirect_label'),
            'Continue to PROODOS Epilogue',
        )

    def test_completing_M5_no_redirect_when_user_lacks_research_consent(self):
        self.profile.research_consent = False
        self.profile.save(update_fields=['research_consent'])
        self._ensure_progress_completable('M5')
        resp = self._post_reflection('M5', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertNotIn(
            'ailst_redirect_url', data,
            "research_consent=False users must not be sent to AILST.",
        )

    def test_completing_non_gating_module_M3_does_not_redirect(self):
        self._ensure_progress_completable('M3')
        resp = self._post_reflection('M3', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertNotIn('ailst_redirect_url', data)

    def test_partial_tab_completion_does_not_redirect(self):
        """If reflection completes but other tabs are not yet done, the
        module is not 'just completed' and no AILST redirect fires."""
        module = Module.objects.get(code='M5')
        # Create progress with only some prior tabs done (no assessment).
        UserModuleProgress.objects.create(
            user=self.user,
            module=module,
            introduction_completed=True,
            introduction_completed_at=timezone.now(),
            main_content_completed=True,
            main_content_completed_at=timezone.now(),
            activity_completed=True,
            activity_completed_at=timezone.now(),
            # assessment_completed left False — module won't flip to done.
        )
        resp = self._post_reflection('M5', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertFalse(data.get('module_completed'))
        self.assertNotIn(
            'ailst_redirect_url', data,
            "Reflection submitted but module not yet completed: no redirect.",
        )

    def test_response_shape_is_backwards_compatible_when_no_redirect(self):
        """When ailst_redirect_url is not set, the JSON keys are exactly
        the pre-C.2.4 shape so old frontends keep working unchanged."""
        self._ensure_progress_completable('M3')
        resp = self._post_reflection('M3', self._valid_reflection_text())
        data = resp.json()
        for key in ('success', 'next_tab', 'module_completed',
                    'completion_percentage'):
            self.assertIn(key, data, f"Missing legacy key {key!r}.")
        self.assertNotIn('ailst_redirect_url', data)


# ============================================================================
# TD-012 — Sequential module-prerequisite gating
# ============================================================================


class SequentialModuleGatingTest(TestCase):
    """The order_index-based prerequisite gate must:
      - Redirect a non-staff user opening M_n out of sequence to the
        first uncompleted prior module.
      - Allow access to M1 unconditionally.
      - Allow access to a module whose prerequisites are all done.
      - Allow staff / superuser bypass for support work.
      - Block the AJAX mark_tab_complete endpoint with 409 when called
        directly out of sequence (defensive AJAX path).
    """

    @classmethod
    def setUpTestData(cls):
        from apps.modules.models import Module
        for code, order_index in (('GT1', 1), ('GT2', 2), ('GT3', 3)):
            Module.objects.get_or_create(
                code=code,
                defaults={
                    'title': 'Gating Test ' + code,
                    'description': 'gating test',
                    'unesco_aspect': 'ethics',
                    'proficiency_level': 'Acquire',
                    'order_index': 50 + order_index,
                    'is_published': True,
                },
            )

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='gate_user', password='pw')
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            ai_disclosure_acknowledged_at=timezone.now(),
            profile_completed=True,
            research_consent=True,
        )
        self.client.force_login(self.user)

    def _complete_module(self, code):
        from apps.modules.models import Module, UserModuleProgress
        m = Module.objects.get(code=code)
        UserModuleProgress.objects.update_or_create(
            user=self.user, module=m,
            defaults={'completed_at': timezone.now(),
                      'completion_percentage': 100, 'status': 'completed'},
        )

    def test_first_module_is_always_accessible(self):
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT1'}))
        self.assertEqual(resp.status_code, 200)

    def test_jumping_to_middle_module_redirects_to_first_uncompleted(self):
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT3'}))
        self.assertRedirects(
            resp, reverse('modules:detail', kwargs={'code': 'GT1'}),
            fetch_redirect_response=False,
        )

    def test_access_allowed_when_prerequisites_are_done(self):
        self._complete_module('GT1')
        self._complete_module('GT2')
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT3'}))
        self.assertEqual(resp.status_code, 200)

    def test_partial_prerequisites_redirects_to_first_uncompleted(self):
        self._complete_module('GT1')
        # GT2 NOT completed. Trying GT3 should redirect to GT2.
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT3'}))
        self.assertRedirects(
            resp, reverse('modules:detail', kwargs={'code': 'GT2'}),
            fetch_redirect_response=False,
        )

    def test_staff_user_bypasses_gate(self):
        self.user.is_staff = True
        self.user.save()
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT3'}))
        self.assertEqual(resp.status_code, 200)

    def test_mark_tab_complete_ajax_blocked_when_out_of_order(self):
        """Defensive AJAX guard: mark_tab_complete must reject calls on
        a module whose prerequisites are not done, even though the
        GET-side gate already redirects."""
        from apps.modules.models import Module, UserModuleProgress
        m = Module.objects.get(code='GT3')
        # Create a progress row directly to simulate the rare case where
        # a user has a UserModuleProgress row for GT3 without finishing
        # GT1/GT2 (e.g. via admin / data migration).
        UserModuleProgress.objects.create(user=self.user, module=m)

        resp = self.client.post(
            reverse('modules:mark_tab_complete',
                    kwargs={'code': 'GT3', 'tab_name': 'introduction'}),
            data=json.dumps({}), content_type='application/json',
        )
        self.assertEqual(resp.status_code, 409)
        data = resp.json()
        self.assertFalse(data['success'])
        self.assertIn('GT1', data['message'])
