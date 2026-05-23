"""Tests for the PROODOS Epilogue placeholder feature (C.2.5).

Covers the placeholder view, the completion view, and the routing
helper that connects M15 completion to /epilogue/.
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.agents.shared.llm_client import GenerationResult
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


# ============================================================================
# Phase G G.2a — Stage 1 (Look Back) reflective dialogue
# ============================================================================


_SNAPSHOT = {
    'schema': 'epilogue_stage0_v1',
    'generated_at': '2026-05-21T10:00:00+00:00',
    'quantitative': {
        'modules_completed': 12, 'reflections_written': 12,
        'distinct_tensions': 8, 'tensions_engaged': 4,
        'dtp_composites': 3, 'dtp_composites_with_shift': 3,
        'input_modality': {'text': 12, 'voice': 0, 'mixed': 0,
                           'unspecified': 0},
    },
    'theme_evolution': {
        'grown': [{'theme': 'pedagogical fit', 'count': 2}],
        'recurring': [{'theme': 'teacher oversight', 'count': 3}],
        'faded': [],
    },
    'narrative_timeline': [
        {'module': 'M6', 'order': 6, 'narrative': 'A descriptive note.'},
    ],
    'rtm_trajectories': [],
}


def _mock_gemini(text):
    """A mock LLM client whose generate() returns a canned turn, or
    None to simulate an AI-side failure."""
    mock = MagicMock()
    if text is None:
        mock.generate.return_value = None
    else:
        mock.generate.return_value = GenerationResult(
            text=text, model='gemini-2.5-flash',
            tokens_estimate=50, cost_eur_estimate=0.0,
        )
    return mock


class Stage1DialogueTest(EpilogueViewBase):
    """The Stage 1 (Look Back) dialogue view. The agent's LLM is mocked
    at apps.agents.epilogue_dialogue.get_llm_client; the base user is
    staff, so the TD-013 M15 gate bypasses."""

    def _completion(self, **kwargs):
        defaults = {'stage0_snapshot': _SNAPSHOT}
        defaults.update(kwargs)
        return EpilogueCompletion.objects.create(user=self.user, **defaults)

    # --- summarise_stage0_for_dialogue ---

    def test_summary_renders_snapshot(self):
        from apps.epilogue.services_stage0 import summarise_stage0_for_dialogue
        text = summarise_stage0_for_dialogue(_SNAPSHOT)
        self.assertIn('12 modules', text)
        self.assertIn('teacher oversight', text)

    def test_summary_temporal_direction_is_explicit(self):
        """Bug fix: 'Themes that receded' was ambiguous about time and
        Gemini occasionally misread it as 'less prominent early on'.
        The summary now spells out the early-vs-late direction.
        """
        from apps.epilogue.services_stage0 import summarise_stage0_for_dialogue
        snap = {
            'quantitative': {'modules_completed': 5, 'reflections_written': 5},
            'theme_evolution': {
                'grown': [{'theme': 'pedagogical fit', 'count': 1}],
                'recurring': [{'theme': 'teacher oversight', 'count': 1}],
                'faded': [{'theme': 'LLM mechanics', 'count': 1}],
            },
            'narrative_timeline': [],
            'rtm_trajectories': [],
        }
        text = summarise_stage0_for_dialogue(snap)
        self.assertIn('became more prominent later', text)
        self.assertIn('consistently present throughout', text)
        self.assertIn('prominent in early modules and faded in later ones',
                      text)

    def test_summary_empty_snapshot(self):
        from apps.epilogue.services_stage0 import summarise_stage0_for_dialogue
        self.assertIn('No reflective data', summarise_stage0_for_dialogue({}))

    # --- dialogue GET ---

    def test_get_redirects_to_stage0_without_snapshot(self):
        resp = self.client.get(reverse('epilogue:dialogue'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('epilogue:placeholder'))

    def test_first_get_enters_dialogue_and_generates_opening(self):
        self._completion()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini('An opening synthesis. '
                                             'What stands out to you?')):
            resp = self.client.get(reverse('epilogue:dialogue'))
        self.assertEqual(resp.status_code, 200)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertTrue(row.dialogue_entered)
        stage1 = [t for t in row.dialogue_turns if t.get('stage') == 1]
        self.assertEqual(len(stage1), 1)
        self.assertEqual(stage1[0]['role'], 'assistant')

    def test_get_with_failed_opening_stays_unentered(self):
        self._completion()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini(None)):
            resp = self.client.get(reverse('epilogue:dialogue'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'could not start')
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertFalse(row.dialogue_entered)
        self.assertEqual(row.dialogue_turns, [])

    # --- dialogue POST (one teacher message) ---

    def test_post_message_appends_teacher_and_assistant_turns(self):
        self._completion(
            dialogue_entered=True,
            dialogue_turns=[{
                'stage': 1, 'role': 'assistant', 'content': 'Opening.',
                'model': 'gemini-2.5-flash',
                'generated_at': '2026-05-21T10:00:00',
            }],
        )
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini('A reflective reply. And you?')):
            resp = self.client.post(
                reverse('epilogue:dialogue'),
                {'message': 'My thinking changed at M6.'},
            )
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        roles = [t['role'] for t in row.dialogue_turns if t.get('stage') == 1]
        self.assertEqual(roles, ['assistant', 'teacher', 'assistant'])

    def test_post_empty_message_adds_nothing(self):
        self._completion(dialogue_entered=True, dialogue_turns=[])
        resp = self.client.post(
            reverse('epilogue:dialogue'), {'message': '   '},
        )
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertEqual(row.dialogue_turns, [])

    def test_post_at_turn_ceiling_adds_nothing(self):
        from apps.agents.epilogue_dialogue import (
            EPILOGUE_DIALOGUE_TURN_CEILING,
        )
        turns = []
        for i in range(EPILOGUE_DIALOGUE_TURN_CEILING):
            turns.append({'stage': 1, 'role': 'teacher',
                          'content': f'msg {i}', 'generated_at': 'x'})
            turns.append({'stage': 1, 'role': 'assistant',
                          'content': f'reply {i}', 'generated_at': 'x'})
        self._completion(dialogue_entered=True, dialogue_turns=turns)
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini('Should not be used.')):
            resp = self.client.post(
                reverse('epilogue:dialogue'), {'message': 'one more'},
            )
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertEqual(len(row.dialogue_turns), len(turns))

    def test_post_with_failed_reply_persists_no_partial_turn(self):
        self._completion(dialogue_entered=True, dialogue_turns=[])
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini(None)):
            resp = self.client.post(
                reverse('epilogue:dialogue'), {'message': 'My message.'},
            )
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertEqual(
            row.dialogue_turns, [],
            'A failed reply must not leave the teacher turn persisted.',
        )

    # --- completion marks the Stage 1 phase ---

    def test_complete_marks_stage1_when_dialogue_entered(self):
        self._completion(dialogue_entered=True, dialogue_turns=[])
        self.client.post(reverse('epilogue:complete'))
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.completed_at)
        self.assertIsNotNone(row.stage1_completed_at)

    def test_complete_skips_stage1_when_dialogue_not_entered(self):
        self._completion(dialogue_entered=False)
        self.client.post(reverse('epilogue:complete'))
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.completed_at)
        self.assertIsNone(row.stage1_completed_at)

    # --- Stage 0 invites the dialogue ---

    def test_stage0_offers_begin_dialogue_and_skip(self):
        resp = self.client.get(reverse('epilogue:placeholder'))
        self.assertContains(resp, 'Begin the reflective dialogue')
        self.assertContains(resp, 'Continue without the dialogue')


# ============================================================================
# Phase G G.2b - Stage 2 (Look In) juxtaposition picker + advance flow
# ============================================================================


class Stage2PickerTest(TestCase):
    """The Stage 2 picker, skip threshold and prompt formatter."""

    def test_picker_returns_rtm_with_widest_position_range(self):
        from apps.epilogue.services_stage0 import pick_juxtaposition_for_stage2
        snapshot = {
            'rtm_trajectories': [
                {'tension_label': 'A vs B', 'recurring': True,
                 'points': [
                     {'module': 'M3', 'position': 1,
                      'position_label': 'Strongly Left'},
                     {'module': 'M11', 'position': 5,
                      'position_label': 'Strongly Right'},
                 ]},
                {'tension_label': 'C vs D', 'recurring': True,
                 'points': [
                     {'module': 'M5', 'position': 2,
                      'position_label': 'Leaning Left'},
                     {'module': 'M9', 'position': 3,
                      'position_label': 'Neutral / Middle'},
                 ]},
            ],
        }
        result = pick_juxtaposition_for_stage2(snapshot)
        self.assertEqual(result['kind'], 'rtm_movement')
        # Widest range (5-1=4) wins over (3-2=1).
        self.assertEqual(result['tension_label'], 'A vs B')

    def test_picker_falls_back_to_theme_shift(self):
        from apps.epilogue.services_stage0 import pick_juxtaposition_for_stage2
        snapshot = {
            'rtm_trajectories': [],  # no recurring RTM
            'theme_evolution': {
                'grown': [{'theme': 'pedagogical fit', 'count': 2}],
                'recurring': [],
                'faded': [{'theme': 'LLM mechanics', 'count': 3}],
            },
        }
        result = pick_juxtaposition_for_stage2(snapshot)
        self.assertEqual(result['kind'], 'theme_shift')
        self.assertEqual(result['faded_theme'], 'LLM mechanics')
        self.assertEqual(result['grown_theme'], 'pedagogical fit')

    def test_picker_returns_none_when_no_material(self):
        from apps.epilogue.services_stage0 import pick_juxtaposition_for_stage2
        snapshot = {
            'rtm_trajectories': [],
            'theme_evolution': {'grown': [], 'recurring': [], 'faded': []},
        }
        self.assertIsNone(pick_juxtaposition_for_stage2(snapshot))

    def test_picker_skips_non_recurring_rtm(self):
        from apps.epilogue.services_stage0 import pick_juxtaposition_for_stage2
        snapshot = {
            'rtm_trajectories': [
                {'tension_label': 'Solo', 'recurring': False,
                 'points': [{'module': 'M3', 'position': 1,
                             'position_label': 'Strongly Left'}]},
            ],
            'theme_evolution': {'grown': [], 'recurring': [], 'faded': []},
        }
        self.assertIsNone(pick_juxtaposition_for_stage2(snapshot))

    def test_should_skip_when_both_below_threshold(self):
        from apps.epilogue.services_stage0 import should_skip_stage2
        snap = {'quantitative': {
            'distinct_tensions': 2, 'dtp_composites_with_shift': 2,
        }}
        self.assertTrue(should_skip_stage2(snap))

    def test_should_not_skip_when_tensions_sufficient(self):
        from apps.epilogue.services_stage0 import should_skip_stage2
        snap = {'quantitative': {
            'distinct_tensions': 3, 'dtp_composites_with_shift': 0,
        }}
        self.assertFalse(should_skip_stage2(snap))

    def test_should_not_skip_when_dtp_shift_sufficient(self):
        from apps.epilogue.services_stage0 import should_skip_stage2
        snap = {'quantitative': {
            'distinct_tensions': 0, 'dtp_composites_with_shift': 3,
        }}
        self.assertFalse(should_skip_stage2(snap))

    def test_format_juxtaposition_rtm_movement(self):
        from apps.epilogue.services_stage0 import format_juxtaposition_for_prompt
        jux = {
            'kind': 'rtm_movement',
            'tension_label': 'A vs B',
            'points': [
                {'module': 'M3', 'position_label': 'Strongly Left'},
                {'module': 'M11', 'position_label': 'Strongly Right'},
            ],
        }
        text = format_juxtaposition_for_prompt(jux)
        self.assertIn('A vs B', text)
        self.assertIn('M3 Strongly Left', text)
        self.assertIn('M11 Strongly Right', text)

    def test_format_juxtaposition_theme_shift(self):
        from apps.epilogue.services_stage0 import format_juxtaposition_for_prompt
        jux = {
            'kind': 'theme_shift',
            'faded_theme': 'LLM mechanics',
            'grown_theme': 'pedagogical fit',
        }
        text = format_juxtaposition_for_prompt(jux)
        self.assertIn('LLM mechanics', text)
        self.assertIn('pedagogical fit', text)


class Stage2DialogueTest(EpilogueViewBase):
    """The Stage 1 -> Stage 2 transition and Stage 2 dialogue handling."""

    def _completion(self, **kwargs):
        defaults = {'stage0_snapshot': _SNAPSHOT, 'dialogue_entered': True}
        defaults.update(kwargs)
        return EpilogueCompletion.objects.create(user=self.user, **defaults)

    def test_advance_skips_stage2_when_threshold_triggers(self):
        thin_snapshot = {
            'quantitative': {
                'distinct_tensions': 1, 'dtp_composites_with_shift': 1,
            },
            'rtm_trajectories': [],
            'theme_evolution': {'grown': [], 'recurring': [], 'faded': []},
        }
        self._completion(
            stage0_snapshot=thin_snapshot,
            dialogue_turns=[
                {'stage': 1, 'role': 'teacher', 'content': 'first',
                 'generated_at': 'x'},
            ],
        )
        resp = self.client.post(reverse('epilogue:dialogue_advance'))
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.stage1_completed_at)
        self.assertIsNotNone(row.stage2_completed_at)
        skip = [t for t in row.dialogue_turns
                if t.get('event') == 'stage2_skipped']
        self.assertEqual(len(skip), 1)
        self.assertEqual(skip[0]['reason'],
                         'insufficient_juxtaposition_material')

    def test_advance_skips_stage2_when_no_juxtaposition(self):
        # Threshold passes but no recurring RTM and no theme-shift pair.
        snapshot = {
            'quantitative': {
                'distinct_tensions': 3, 'dtp_composites_with_shift': 3,
            },
            'rtm_trajectories': [],
            'theme_evolution': {'grown': [], 'recurring': [], 'faded': []},
        }
        self._completion(
            stage0_snapshot=snapshot,
            dialogue_turns=[
                {'stage': 1, 'role': 'teacher', 'content': 'first',
                 'generated_at': 'x'},
            ],
        )
        resp = self.client.post(reverse('epilogue:dialogue_advance'))
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.stage2_completed_at)
        skip = [t for t in row.dialogue_turns
                if t.get('event') == 'stage2_skipped']
        self.assertEqual(skip[0]['reason'],
                         'no_clean_juxtaposition_available')

    def test_advance_proceeds_with_rtm_juxtaposition(self):
        rich_snapshot = {
            'quantitative': {
                'distinct_tensions': 3, 'dtp_composites_with_shift': 3,
            },
            'rtm_trajectories': [
                {'tension_label': 'Control vs autonomy', 'recurring': True,
                 'points': [
                     {'module': 'M3', 'position': 1,
                      'position_label': 'Strongly Left'},
                     {'module': 'M11', 'position': 5,
                      'position_label': 'Strongly Right'},
                 ]},
            ],
            'theme_evolution': {'grown': [], 'recurring': [], 'faded': []},
        }
        self._completion(
            stage0_snapshot=rich_snapshot,
            dialogue_turns=[
                {'stage': 1, 'role': 'teacher', 'content': 'first',
                 'generated_at': 'x'},
            ],
        )
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini(
                       'Two of your own moments sit next to each other.')):
            resp = self.client.post(reverse('epilogue:dialogue_advance'))
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.stage1_completed_at)
        self.assertIsNone(row.stage2_completed_at)
        stage2 = [t for t in row.dialogue_turns if t.get('stage') == 2]
        self.assertEqual(len(stage2), 1)
        self.assertEqual(stage2[0]['role'], 'assistant')

    def test_advance_does_not_transition_on_gemini_failure(self):
        rich_snapshot = {
            'quantitative': {
                'distinct_tensions': 3, 'dtp_composites_with_shift': 3,
            },
            'rtm_trajectories': [
                {'tension_label': 'A vs B', 'recurring': True,
                 'points': [
                     {'module': 'M3', 'position': 1,
                      'position_label': 'Strongly Left'},
                     {'module': 'M11', 'position': 5,
                      'position_label': 'Strongly Right'},
                 ]},
            ],
            'theme_evolution': {'grown': [], 'recurring': [], 'faded': []},
        }
        self._completion(
            stage0_snapshot=rich_snapshot,
            dialogue_turns=[
                {'stage': 1, 'role': 'teacher', 'content': 'first',
                 'generated_at': 'x'},
            ],
        )
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini(None)):
            resp = self.client.post(reverse('epilogue:dialogue_advance'))
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        # Stage transition did not happen.
        self.assertIsNone(row.stage1_completed_at)
        # No Stage 2 turns were stored.
        stage2 = [t for t in row.dialogue_turns if t.get('stage') == 2]
        self.assertEqual(stage2, [])

    def test_handle_dialogue_turn_in_stage2(self):
        self._completion(
            stage1_completed_at=timezone.now(),
            dialogue_turns=[
                {'stage': 1, 'role': 'assistant', 'content': 'opening 1',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 1, 'role': 'teacher', 'content': 'reply 1',
                 'generated_at': 'x'},
                {'stage': 2, 'role': 'assistant', 'content': 'opening 2',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
            ],
        )
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini('A Stage 2 reply.')):
            resp = self.client.post(
                reverse('epilogue:dialogue'),
                {'message': 'My take on it.'},
            )
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        stage2 = [t for t in row.dialogue_turns
                  if t.get('stage') == 2
                  and t.get('role') in ('assistant', 'teacher')]
        roles = [t['role'] for t in stage2]
        self.assertEqual(roles, ['assistant', 'teacher', 'assistant'])
