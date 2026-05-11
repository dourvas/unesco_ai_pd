"""Tests for the PROODOS Epilogue placeholder feature (C.2.5).

Covers the placeholder view, the completion view, and the routing
helper that connects M15 completion to /epilogue/.
"""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.ailst.models import AilstResponse
from apps.epilogue.models import EpilogueCompletion
from apps.epilogue.services import get_post_module_epilogue_redirect_url
from apps.users.models import TeacherProfile


class EpilogueViewBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='epilogue_user', password='pw')
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            ai_disclosure_acknowledged_at=timezone.now(),
            profile_completed=True,
            research_consent=True,
        )
        self.client.force_login(self.user)


class EpiloguePlaceholderViewTest(EpilogueViewBase):

    def test_first_visit_creates_completion_row_and_renders(self):
        resp = self.client.get(reverse('epilogue:placeholder'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'epilogue/placeholder.html')
        self.assertTrue(
            EpilogueCompletion.objects.filter(user=self.user).exists(),
            'First GET must create an EpilogueCompletion row so started_at is captured.',
        )
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNone(row.completed_at)

    def test_revisit_reuses_existing_row(self):
        EpilogueCompletion.objects.create(user=self.user)
        original_count = EpilogueCompletion.objects.filter(user=self.user).count()
        self.client.get(reverse('epilogue:placeholder'))
        new_count = EpilogueCompletion.objects.filter(user=self.user).count()
        self.assertEqual(original_count, new_count, 'Revisit must not duplicate the row.')

    def test_already_completed_shows_completion_state(self):
        row = EpilogueCompletion.objects.create(user=self.user)
        row.completed_at = timezone.now()
        row.save(update_fields=['completed_at'])
        resp = self.client.get(reverse('epilogue:placeholder'))
        self.assertEqual(resp.status_code, 200)
        # The template shows a success banner when already_completed.
        self.assertIn('reached the Epilogue on', resp.content.decode('utf-8'))


class EpilogueCompleteViewTest(EpilogueViewBase):

    def test_post_first_time_with_consent_routes_to_T2(self):
        resp = self.client.post(reverse('epilogue:complete'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/ailst/t2/')
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.completed_at)

    def test_post_routes_to_dashboard_when_consent_false(self):
        self.profile.research_consent = False
        self.profile.save(update_fields=['research_consent'])
        resp = self.client.post(reverse('epilogue:complete'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/dashboard/')
        # Completion row still flipped — Epilogue is open to non-consenting users.
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.completed_at)

    def test_post_routes_to_dashboard_when_T2_already_completed(self):
        AilstResponse.objects.create(
            user=self.user,
            timepoint='T2',
            language='en',
            instrument_version='ning_2025_v1',
            responses={f'P{i}': 4 for i in range(1, 11)},
            completed_at=timezone.now(),
        )
        resp = self.client.post(reverse('epilogue:complete'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/dashboard/')

    def test_post_is_idempotent_on_double_submit(self):
        first = self.client.post(reverse('epilogue:complete'))
        original_completed_at = EpilogueCompletion.objects.get(
            user=self.user,
        ).completed_at

        second = self.client.post(reverse('epilogue:complete'))
        later_completed_at = EpilogueCompletion.objects.get(
            user=self.user,
        ).completed_at

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(
            original_completed_at, later_completed_at,
            'Double-submit must not move completed_at forward.',
        )

    def test_get_is_rejected(self):
        resp = self.client.get(reverse('epilogue:complete'))
        # require_POST returns 405 for GETs.
        self.assertEqual(resp.status_code, 405)


class EpilogueRedirectHelperTest(EpilogueViewBase):

    def test_M15_with_no_completion_returns_epilogue_url(self):
        url = get_post_module_epilogue_redirect_url(self.user, 'M15')
        self.assertEqual(url, '/epilogue/')

    def test_M15_when_epilogue_already_completed_returns_none(self):
        row = EpilogueCompletion.objects.create(user=self.user)
        row.completed_at = timezone.now()
        row.save(update_fields=['completed_at'])
        url = get_post_module_epilogue_redirect_url(self.user, 'M15')
        self.assertIsNone(url, 'Idempotency: completed Epilogue blocks re-redirect.')

    def test_other_modules_return_none(self):
        for code in ('M1', 'M5', 'M14'):
            self.assertIsNone(
                get_post_module_epilogue_redirect_url(self.user, code),
                f'{code} is not in the Epilogue mapping.',
            )

    def test_non_consenting_user_still_gets_epilogue_redirect(self):
        """Epilogue is open to all users (D4): no consent gate at the
        modules layer for Epilogue routing. The T2 gate fires later."""
        self.profile.research_consent = False
        self.profile.save(update_fields=['research_consent'])
        url = get_post_module_epilogue_redirect_url(self.user, 'M15')
        self.assertEqual(url, '/epilogue/')
