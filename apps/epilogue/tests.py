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
        # is_staff so the TD-013 M15-completion gate bypasses for the
        # existing C.2.5 test classes. We are exercising the Epilogue
        # placeholder/complete/routing logic, not the gate itself; the
        # gate has its own dedicated EpilogueM15GatingTest below.
        self.user = User.objects.create_user(
            username='epilogue_user', password='pw', is_staff=True,
        )
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
        self.assertTemplateUsed(resp, 'epilogue/stage0.html')
        # Regression: template comments must not leak into the page.
        # A multi-line {# #} is not a valid Django comment and renders
        # as literal text; {% comment %} must be used instead.
        self.assertNotIn('{#', resp.content.decode('utf-8'))
        self.assertTrue(
            EpilogueCompletion.objects.filter(user=self.user).exists(),
            'First GET must create an EpilogueCompletion row so started_at is captured.',
        )
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNone(row.completed_at)
        # G.1: the Stage 0 snapshot is computed and frozen on first entry.
        self.assertEqual(row.stage0_snapshot.get('schema'), 'epilogue_stage0_v1')
        self.assertIsNotNone(row.stage0_seen_at)

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


# ============================================================================
# TD-013 — Epilogue gating on M15 completion
# ============================================================================


class EpilogueM15GatingTest(EpilogueViewBase):
    """The Epilogue must be unreachable until M15 is completed.
    Staff and superusers bypass for support work.

    Tests:
      - Without M15 row: GET /epilogue/ redirects to dashboard.
      - Without M15 row: POST /epilogue/complete/ redirects to dashboard,
        no EpilogueCompletion row created.
      - With M15 completed: both views work normally.
      - Staff users bypass the gate regardless of M15 state.
    """

    def setUp(self):
        super().setUp()
        # Override the base setUp's is_staff=True for the gating tests.
        # The base sets it for the older C.2.5 tests that pre-dated the
        # gate; the gating tests below need the gate to actually fire.
        self.user.is_staff = False
        self.user.save(update_fields=['is_staff'])

    @classmethod
    def setUpTestData(cls):
        from apps.modules.models import Module
        Module.objects.get_or_create(
            code='M15',
            defaults={
                'title': 'M15 for gating', 'description': 'gating',
                'unesco_aspect': 'professional_development',
                'proficiency_level': 'Create',
                'order_index': 215, 'is_published': True,
            },
        )

    def _complete_m15(self):
        from apps.modules.models import Module, UserModuleProgress
        m = Module.objects.get(code='M15')
        UserModuleProgress.objects.update_or_create(
            user=self.user, module=m,
            defaults={'completed_at': timezone.now(),
                      'completion_percentage': 100, 'status': 'completed'},
        )

    def test_get_without_m15_redirects_to_dashboard(self):
        resp = self.client.get(reverse('epilogue:placeholder'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/', resp.url)
        self.assertFalse(
            EpilogueCompletion.objects.filter(user=self.user).exists(),
            'Gate must prevent the EpilogueCompletion row from being created '
            'when the M15 prerequisite is not satisfied.',
        )

    def test_post_complete_without_m15_redirects_to_dashboard(self):
        resp = self.client.post(reverse('epilogue:complete'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/', resp.url)
        self.assertFalse(
            EpilogueCompletion.objects.filter(user=self.user).exists(),
            'Defensive POST guard must not create or flip the completion row.',
        )

    def test_get_with_m15_completed_renders(self):
        self._complete_m15()
        resp = self.client.get(reverse('epilogue:placeholder'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(EpilogueCompletion.objects.filter(user=self.user).exists())

    def test_staff_user_bypasses_m15_gate(self):
        self.user.is_staff = True
        self.user.save()
        resp = self.client.get(reverse('epilogue:placeholder'))
        self.assertEqual(resp.status_code, 200)


# ============================================================================
# Phase G G.1 — Stage 0 Personal Evolution Dashboard
# ============================================================================


class Stage0SnapshotTest(EpilogueViewBase):
    """The Stage 0 snapshot aggregation and its first-entry-only freeze.

    The base user is staff, so the TD-013 M15 gate bypasses — these
    tests exercise the snapshot logic, not the gate.
    """

    def _make_module(self, code, order_index):
        from apps.modules.models import Module
        module, _ = Module.objects.get_or_create(
            code=code,
            defaults={
                'title': f'{code} test', 'description': 'test',
                'unesco_aspect': 'ai_foundations',
                'proficiency_level': 'Acquire',
                'order_index': order_index, 'is_published': True,
            },
        )
        return module

    @staticmethod
    def _dtp_composite(current, increased, decreased, stable, narrative):
        import json
        return json.dumps({
            'schema': 'dtp_dual_v1',
            'current_module': current,
            'narrative': narrative,
            'signals': {
                'temporal': {
                    'comparison_module': 'M_prev',
                    'similarity': 0.7,
                    'themes': {
                        'increased_themes': increased,
                        'decreased_themes': decreased,
                        'stable_themes': stable,
                    },
                },
            },
        })

    def test_build_snapshot_with_no_data_returns_empty_structure(self):
        from apps.epilogue.services_stage0 import build_stage0_snapshot
        snap = build_stage0_snapshot(self.user)
        self.assertEqual(snap['schema'], 'epilogue_stage0_v1')
        self.assertEqual(snap['quantitative']['modules_completed'], 0)
        self.assertEqual(snap['theme_evolution']['grown'], [])
        self.assertEqual(snap['narrative_timeline'], [])
        self.assertEqual(snap['rtm_trajectories'], [])

    def test_build_snapshot_aggregates_dtp_and_rtm(self):
        from apps.epilogue.services_stage0 import build_stage0_snapshot
        from apps.modules.models import ReflectionTension, UserModuleProgress

        m2 = self._make_module('SNAP_M2', 902)
        m3 = self._make_module('SNAP_M3', 903)

        UserModuleProgress.objects.create(
            user=self.user, module=m2, status='completed',
            completed_at=timezone.now(), reflection_completed=True,
            reflection_input_modality='text',
            reflection_dtp=self._dtp_composite(
                'SNAP_M2', ['ethical focus'], [], ['physics context'],
                'Across these modules, your reflection shifted toward ethics.',
            ),
        )
        UserModuleProgress.objects.create(
            user=self.user, module=m3, status='completed',
            completed_at=timezone.now(), reflection_completed=True,
            reflection_input_modality='voice',
            reflection_dtp=self._dtp_composite(
                'SNAP_M3', ['student agency'], ['ethical focus'], [],
                'Across these modules, your focus moved to student agency.',
            ),
        )
        ReflectionTension.objects.create(
            user=self.user, module=m2, tension_label='Control vs autonomy',
            left_pole='control', right_pole='autonomy',
            grounding_quote='q', selected_position=2, position_confirmed=True,
        )
        ReflectionTension.objects.create(
            user=self.user, module=m3, tension_label='Control vs autonomy',
            left_pole='control', right_pole='autonomy',
            grounding_quote='q', selected_position=4, position_confirmed=True,
        )

        snap = build_stage0_snapshot(self.user)

        q = snap['quantitative']
        self.assertEqual(q['modules_completed'], 2)
        self.assertEqual(q['reflections_written'], 2)
        self.assertEqual(q['distinct_tensions'], 1)
        self.assertEqual(q['tensions_engaged'], 2)
        self.assertEqual(q['dtp_composites'], 2)
        self.assertEqual(q['dtp_composites_with_shift'], 2)
        self.assertEqual(q['input_modality']['text'], 1)
        self.assertEqual(q['input_modality']['voice'], 1)

        grown = {i['theme'] for i in snap['theme_evolution']['grown']}
        self.assertIn('ethical focus', grown)
        self.assertIn('student agency', grown)

        self.assertEqual(len(snap['narrative_timeline']), 2)
        self.assertEqual(snap['narrative_timeline'][0]['module'], 'SNAP_M2')

        self.assertEqual(len(snap['rtm_trajectories']), 1)
        traj = snap['rtm_trajectories'][0]
        self.assertEqual(traj['tension_label'], 'Control vs autonomy')
        self.assertTrue(traj['recurring'])
        self.assertEqual(len(traj['points']), 2)

    def test_malformed_dtp_is_skipped_not_fatal(self):
        from apps.epilogue.services_stage0 import build_stage0_snapshot
        from apps.modules.models import UserModuleProgress
        m = self._make_module('SNAP_BAD', 905)
        UserModuleProgress.objects.create(
            user=self.user, module=m, status='completed',
            completed_at=timezone.now(), reflection_completed=True,
            reflection_dtp='{not valid json',
        )
        snap = build_stage0_snapshot(self.user)
        self.assertEqual(snap['quantitative']['dtp_composites'], 0)
        self.assertEqual(snap['narrative_timeline'], [])

    def test_snapshot_frozen_on_first_visit(self):
        resp = self.client.get(reverse('epilogue:placeholder'))
        self.assertEqual(resp.status_code, 200)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertEqual(row.stage0_snapshot.get('schema'), 'epilogue_stage0_v1')
        self.assertIsNotNone(row.stage0_seen_at)

    def test_snapshot_not_recomputed_on_revisit(self):
        row = EpilogueCompletion.objects.create(
            user=self.user, stage0_snapshot={'schema': 'sentinel'},
            stage0_seen_at=timezone.now(),
        )
        original_seen_at = row.stage0_seen_at
        self.client.get(reverse('epilogue:placeholder'))
        row.refresh_from_db()
        self.assertEqual(
            row.stage0_snapshot, {'schema': 'sentinel'},
            'A revisit must not recompute the frozen Stage 0 snapshot.',
        )
        self.assertEqual(row.stage0_seen_at, original_seen_at)
