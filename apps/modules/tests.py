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
        self.user = User.objects.create_user(username='gating_user', password='pw')
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

    def test_completing_M15_redirects_to_T2_when_consent_and_T2_not_done(self):
        self._ensure_progress_completable('M15')
        resp = self._post_reflection('M15', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertEqual(data.get('ailst_redirect_url'), '/ailst/t2/')

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
