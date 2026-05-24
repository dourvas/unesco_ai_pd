"""Tests for the PROODOS Epilogue placeholder feature (C.2.5).

Covers the placeholder view, the completion view, and the routing
helper that connects M15 completion to /epilogue/.
"""

import unittest
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


# Phase G closure (2026-05-24) — the Aletheia reflective dialogue
# (Stages 1-3) and the Learning Portrait HITL flow were removed from
# the Epilogue. The test classes that exercise the deleted views are
# decorated with this constant so the skip reason is uniform across
# the file. See:
#   proodos_files/PHASE_G_DIALOGUE_DEPRECATION_20260524.md §4.1
#   proodos_files/PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2_20260521.md §25
DEACTIVATED_PHASE_G_CLOSURE = (
    'Deactivated in Phase G closure 2026-05-24 — see '
    'PHASE_G_DIALOGUE_DEPRECATION_20260524.md'
)


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
        # The template shows a completion banner when already_completed.
        # Copy reworded in G.6b: "reached the Epilogue on" → "reached
        # this synthesis on" (the magazine register naming + the label-
        # leak sweep that hides the internal 'Epilogue' label from the
        # teacher; G.6 proposal §5).
        self.assertIn('reached this synthesis on', resp.content.decode('utf-8'))


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


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
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
        """The Stage 0 page invites the teacher into the dialogue and
        offers a clear skip path. Copy reworded in G.6b: introduces
        Aletheia by name (G.6 proposal §3.3 — narrative copy uses the
        persona name) and refers to the dialogue as 'the conversation
        with Aletheia' so the reflective partner is established before
        the dialogue surface loads."""
        resp = self.client.get(reverse('epilogue:placeholder'))
        self.assertContains(resp, 'Begin the conversation with Aletheia')
        self.assertContains(resp, 'Continue without the conversation')


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


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
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


# ============================================================================
# Phase G G.2c - Stage 3 (Look Forward) + dialogue completion
# ============================================================================


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
class Stage3DialogueTest(EpilogueViewBase):
    """Stage 2 -> Stage 3 transition, Stage 3 dialogue, and completion
    marking the right stage timestamps."""

    def _completion(self, **kwargs):
        defaults = {'stage0_snapshot': _SNAPSHOT, 'dialogue_entered': True}
        defaults.update(kwargs)
        return EpilogueCompletion.objects.create(user=self.user, **defaults)

    def test_summarise_prior_stages_for_stage3(self):
        from apps.epilogue.services_stage0 import (
            summarise_prior_stages_for_stage3,
        )
        turns = [
            {'stage': 1, 'role': 'assistant', 'content': 'opening'},
            {'stage': 1, 'role': 'teacher', 'content': 'first thought'},
            {'stage': 1, 'role': 'teacher', 'content': 'last stage1 thought'},
            {'stage': 2, 'role': 'assistant', 'content': 'juxtaposition'},
            {'stage': 2, 'role': 'teacher', 'content': 'stage2 reply'},
        ]
        text = summarise_prior_stages_for_stage3(turns)
        self.assertIn('Stage 1', text)
        self.assertIn('last stage1 thought', text)
        self.assertIn('Stage 2', text)
        self.assertIn('stage2 reply', text)
        # Earlier stage-1 message is overwritten by the last one.
        self.assertNotIn('first thought', text)

    def test_summarise_prior_stages_handles_skipped_stage2(self):
        """Stage 2 skip records have role='system' and must not be
        treated as teacher messages in the prior-stages summary."""
        from apps.epilogue.services_stage0 import (
            summarise_prior_stages_for_stage3,
        )
        turns = [
            {'stage': 1, 'role': 'teacher', 'content': 'a stage1 reply'},
            {'stage': 2, 'role': 'system', 'event': 'stage2_skipped',
             'reason': 'insufficient_juxtaposition_material'},
        ]
        text = summarise_prior_stages_for_stage3(turns)
        self.assertIn('a stage1 reply', text)
        self.assertNotIn('Stage 2', text)

    # ------------------------------------------------------------------
    # summarise_dialogue_for_portrait (G.3a — Learning Portrait input)
    # ------------------------------------------------------------------
    def test_summarise_dialogue_for_portrait_full_three_stages(self):
        from apps.epilogue.services_stage0 import (
            summarise_dialogue_for_portrait,
        )
        turns = [
            {'stage': 1, 'role': 'assistant', 'content': 'opening synth'},
            {'stage': 1, 'role': 'teacher', 'content': 'I felt I was performing'},
            {'stage': 1, 'role': 'assistant', 'content': 'follow-up Q'},
            {'stage': 1, 'role': 'teacher', 'content': 'M10 was the moment'},
            {'stage': 2, 'role': 'assistant',
             'content': 'M3 strongly left, M11 leaning right'},
            {'stage': 2, 'role': 'teacher',
             'content': 'A change anchored to a moment'},
            {'stage': 2, 'role': 'assistant', 'content': 'tell me more'},
            {'stage': 3, 'role': 'assistant', 'content': 'what is one step'},
            {'stage': 3, 'role': 'teacher',
             'content': 'Rewrite the AI first answer'},
        ]
        text = summarise_dialogue_for_portrait(turns)
        # Per-stage headings are present in order.
        self.assertIn('Stage 1 (Look Back)', text)
        self.assertIn('Stage 2 (Look In)', text)
        self.assertIn('Stage 3 (Look Forward)', text)
        s1 = text.index('Stage 1')
        s2 = text.index('Stage 2')
        s3 = text.index('Stage 3')
        self.assertLess(s1, s2)
        self.assertLess(s2, s3)
        # Teacher messages from every stage are present verbatim.
        self.assertIn('I felt I was performing', text)
        self.assertIn('M10 was the moment', text)
        self.assertIn('A change anchored to a moment', text)
        self.assertIn('Rewrite the AI first answer', text)
        # The Stage 2 juxtaposition opener is included so the
        # Portrait knows what the teacher was responding to.
        self.assertIn('M3 strongly left, M11 leaning right', text)

    def test_summarise_dialogue_for_portrait_omits_continuing_agent_turns(self):
        """The Portrait prompt is teacher-led — only the Stage 2
        opener is preserved from the assistant; Stage 1 / Stage 3
        agent turns are not included so the prompt stays focused on
        the teacher's own framing."""
        from apps.epilogue.services_stage0 import (
            summarise_dialogue_for_portrait,
        )
        turns = [
            {'stage': 1, 'role': 'assistant', 'content': 'opening agent line'},
            {'stage': 1, 'role': 'teacher', 'content': 'teacher line 1'},
            {'stage': 3, 'role': 'assistant', 'content': 'a stage3 agent line'},
            {'stage': 3, 'role': 'teacher', 'content': 'teacher line 3'},
        ]
        text = summarise_dialogue_for_portrait(turns)
        self.assertIn('teacher line 1', text)
        self.assertIn('teacher line 3', text)
        self.assertNotIn('opening agent line', text)
        self.assertNotIn('a stage3 agent line', text)

    def test_summarise_dialogue_for_portrait_skipped_stage2(self):
        """A teacher who hit the Stage 2 skip path has no Stage 2
        teacher messages; the Stage 2 block shows '(no responses)'
        so the Portrait agent does not invent material."""
        from apps.epilogue.services_stage0 import (
            summarise_dialogue_for_portrait,
        )
        turns = [
            {'stage': 1, 'role': 'teacher', 'content': 'a stage1 reply'},
            {'stage': 2, 'role': 'system', 'event': 'stage2_skipped',
             'reason': 'insufficient_juxtaposition_material'},
            {'stage': 3, 'role': 'teacher', 'content': 'a stage3 reply'},
        ]
        text = summarise_dialogue_for_portrait(turns)
        self.assertIn('Stage 2 (Look In)', text)
        self.assertIn('(no responses)', text)
        # The system skip record itself must not be quoted.
        self.assertNotIn('insufficient_juxtaposition_material', text)

    def test_summarise_dialogue_for_portrait_empty(self):
        from apps.epilogue.services_stage0 import (
            summarise_dialogue_for_portrait,
        )
        self.assertEqual(summarise_dialogue_for_portrait([]), '')
        self.assertEqual(summarise_dialogue_for_portrait(None), '')

    def test_summarise_dialogue_for_portrait_ignores_unknown_stages(self):
        """Defensive: a future 'portrait'-stage event in dialogue_turns
        (G.3 §22.1) must not pollute the dialogue summary."""
        from apps.epilogue.services_stage0 import (
            summarise_dialogue_for_portrait,
        )
        turns = [
            {'stage': 1, 'role': 'teacher', 'content': 'real stage1'},
            {'stage': 'portrait', 'role': 'assistant',
             'event': 'proposal', 'content': 'a proposed portrait'},
        ]
        text = summarise_dialogue_for_portrait(turns)
        self.assertIn('real stage1', text)
        self.assertNotIn('a proposed portrait', text)

    def test_advance_from_stage2_to_stage3_generates_opening(self):
        self._completion(
            stage1_completed_at=timezone.now(),
            dialogue_turns=[
                {'stage': 2, 'role': 'assistant', 'content': 'juxtaposition',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 2, 'role': 'teacher', 'content': 'my take',
                 'generated_at': 'x'},
            ],
        )
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini(
                       'Across everything you have looked at, what is '
                       'one specific thing you will try?')):
            resp = self.client.post(reverse('epilogue:dialogue_advance'))
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.stage2_completed_at)
        self.assertIsNone(row.stage3_completed_at)
        stage3 = [t for t in row.dialogue_turns
                  if t.get('stage') == 3
                  and t.get('role') == 'assistant']
        self.assertEqual(len(stage3), 1)

    def test_advance_from_stage3_with_no_turns_enters_stage3(self):
        """After Stage 2 auto-skip, current_stage=3 with no Stage 3
        turns. Clicking 'Continue to Look Forward' enters Stage 3."""
        self._completion(
            stage1_completed_at=timezone.now(),
            stage2_completed_at=timezone.now(),
            dialogue_turns=[
                {'stage': 1, 'role': 'teacher', 'content': 'a stage1 reply',
                 'generated_at': 'x'},
                {'stage': 2, 'role': 'system', 'event': 'stage2_skipped',
                 'reason': 'insufficient_juxtaposition_material',
                 'generated_at': 'x'},
            ],
        )
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini('Stage 3 opening.')):
            resp = self.client.post(reverse('epilogue:dialogue_advance'))
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        stage3 = [t for t in row.dialogue_turns
                  if t.get('stage') == 3
                  and t.get('role') == 'assistant']
        self.assertEqual(len(stage3), 1)

    def test_handle_dialogue_turn_in_stage3(self):
        self._completion(
            stage1_completed_at=timezone.now(),
            stage2_completed_at=timezone.now(),
            dialogue_turns=[
                {'stage': 3, 'role': 'assistant', 'content': 'opening 3',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
            ],
        )
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=_mock_gemini('A Stage 3 reply.')):
            resp = self.client.post(
                reverse('epilogue:dialogue'),
                {'message': 'I will rewrite the AI output on Monday.'},
            )
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        stage3 = [t for t in row.dialogue_turns
                  if t.get('stage') == 3
                  and t.get('role') in ('assistant', 'teacher')]
        roles = [t['role'] for t in stage3]
        self.assertEqual(roles, ['assistant', 'teacher', 'assistant'])

    def test_complete_marks_stage2_when_in_stage2(self):
        self._completion(
            stage1_completed_at=timezone.now(),
            dialogue_turns=[
                {'stage': 2, 'role': 'assistant', 'content': 'opening',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
            ],
        )
        self.client.post(reverse('epilogue:complete'))
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.stage2_completed_at)
        self.assertIsNone(row.stage3_completed_at)

    def test_complete_marks_stage3_when_in_stage3(self):
        self._completion(
            stage1_completed_at=timezone.now(),
            stage2_completed_at=timezone.now(),
            dialogue_turns=[
                {'stage': 3, 'role': 'assistant', 'content': 'opening',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
            ],
        )
        self.client.post(reverse('epilogue:complete'))
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertIsNotNone(row.stage3_completed_at)


# ======================================================================
# G.3b — Learning Portrait views (review / regenerate / accept / pdf)
# ======================================================================

_PORTRAIT_TEXT_A = (
    'Across your fifteen modules, your attention travelled. You '
    'wrote often about pedagogical fit and teacher oversight; you '
    'leave with one concrete step: to ask students to rewrite the '
    "AI's first answer in their own words."
)
_PORTRAIT_TEXT_B = (
    'Looking back across your reflections, a few threads stand out. '
    'You returned to teacher oversight; you named M10 as the moment '
    'reflection felt performative. You will rewrite the AI first '
    'answer in your own words next week.'
)
_PORTRAIT_TEXT_C = (
    'Your fifteen modules trace a movement of attention. Where '
    'pedagogical fit recurred, oversight remained. Your next step '
    'is concrete: rewrite the AI answer first, then discuss.'
)


def _mock_portrait_gemini(text):
    """Mock for EpiloguePortraitAgent's LLM client. Pattern mirrors
    `_mock_gemini` but lives here for the longer Portrait texts."""
    mock = MagicMock()
    if text is None:
        mock.generate.return_value = None
    else:
        mock.generate.return_value = GenerationResult(
            text=text, model='gemini-2.5-flash',
            tokens_estimate=400, cost_eur_estimate=0.0,
        )
    return mock


class PortraitViewBase(EpilogueViewBase):
    """Reusable fixture: a teacher who has finished Stage 3 of the
    dialogue and is ready for the Learning Portrait step.

    The dialogue is mocked at the agent level for all earlier tests in
    this file; here we set the row state directly so the Portrait view
    can be exercised without re-running the dialogue.
    """

    def _completion_post_stage3(self, **overrides):
        defaults = {
            'stage0_snapshot': _SNAPSHOT,
            'dialogue_entered': True,
            'stage1_completed_at': timezone.now(),
            'stage2_completed_at': timezone.now(),
            'stage3_completed_at': timezone.now(),
            'dialogue_turns': [
                {'stage': 1, 'role': 'assistant', 'content': 's1 open',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 1, 'role': 'teacher',
                 'content': 'I felt I was performing reflection.',
                 'generated_at': 'x'},
                {'stage': 2, 'role': 'assistant', 'content': 'jux',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 2, 'role': 'teacher',
                 'content': 'A change anchored to a moment.',
                 'generated_at': 'x'},
                {'stage': 3, 'role': 'assistant', 'content': 's3 open',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 3, 'role': 'teacher',
                 'content': 'Rewrite the AI first answer next week.',
                 'generated_at': 'x'},
            ],
        }
        defaults.update(overrides)
        return EpilogueCompletion.objects.create(user=self.user, **defaults)


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
class PortraitViewGatingTest(PortraitViewBase):
    """The Portrait page gates: dialogue must have been entered, and
    Stage 3 must have been completed (design proposal v2 §22.2)."""

    def test_no_completion_row_redirects_to_placeholder(self):
        resp = self.client.get(reverse('epilogue:portrait'))
        self.assertRedirects(
            resp, reverse('epilogue:placeholder'),
            fetch_redirect_response=False,
        )

    def test_skip_dialogue_teacher_does_not_see_portrait(self):
        """A teacher who skipped the dialogue (dialogue_entered=False)
        is bounced back to the Stage 0 page — they go through
        /complete/ instead (§22.2)."""
        EpilogueCompletion.objects.create(
            user=self.user,
            stage0_snapshot=_SNAPSHOT,
            dialogue_entered=False,
        )
        resp = self.client.get(reverse('epilogue:portrait'))
        self.assertRedirects(
            resp, reverse('epilogue:placeholder'),
            fetch_redirect_response=False,
        )
        self.assertFalse(
            EpilogueCompletion.objects.filter(
                user=self.user,
            ).exclude(learning_portrait_text='').exists()
        )

    def test_stage3_not_complete_redirects_to_dialogue(self):
        """Stage 3 not yet started: no teacher turn in Stage 3, so the
        Portrait page bounces back to the dialogue. The G.3.1 hotfix
        only fills in stage3_completed_at when there is substantive
        Stage 3 engagement; an empty Stage 3 still gates correctly."""
        EpilogueCompletion.objects.create(
            user=self.user,
            stage0_snapshot=_SNAPSHOT,
            dialogue_entered=True,
            stage1_completed_at=timezone.now(),
        )
        resp = self.client.get(reverse('epilogue:portrait'))
        self.assertRedirects(
            resp, reverse('epilogue:dialogue'),
            fetch_redirect_response=False,
        )

    def test_stage3_in_progress_visiting_portrait_sets_completed_at(self):
        """G.3.1 hotfix (2026-05-24): the post-G.3 UX changed the
        Stage 3 finish-button into a GET link ('Continue to your
        Learning Portrait'). The pre-G.3 G.2c flow had this as a
        POST to /complete/ which set stage3_completed_at as a side
        effect; the GET link does not. Surfaced during the live §23
        verification walkthrough against mavros 2026-05-24 — the
        teacher had Stage 3 teacher turns but stage3_completed_at
        was still NULL, so the Portrait page silently redirected
        back to the dialogue.

        Fix: in epilogue_portrait_view, if the teacher has ≥1
        Stage 3 teacher turn but stage3_completed_at is NULL, treat
        the Portrait visit as the implicit Stage 3 completion event
        and set the timestamp under a row lock.

        This test exercises the actual click path the user followed
        — it does NOT use the _completion_post_stage3 fixture
        shortcut (which short-circuits the bug by pre-setting
        stage3_completed_at). It must FAIL on pre-hotfix code and
        PASS on post-hotfix code.
        """
        ec = EpilogueCompletion.objects.create(
            user=self.user,
            stage0_snapshot=_SNAPSHOT,
            dialogue_entered=True,
            stage1_completed_at=timezone.now(),
            stage2_completed_at=timezone.now(),
            # stage3_completed_at intentionally NULL — the bug scenario.
            dialogue_turns=[
                {'stage': 3, 'role': 'assistant',
                 'content': 'opening of Stage 3 from the agent',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 3, 'role': 'teacher',
                 'content': 'a substantive Stage 3 commitment reply',
                 'generated_at': 'x'},
                {'stage': 3, 'role': 'assistant',
                 'content': 'continuing turn from the agent',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
            ],
        )
        self.assertIsNone(ec.stage3_completed_at)

        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            resp = self.client.get(reverse('epilogue:portrait'))

        # Hotfix outcome: stage3_completed_at now set + Portrait
        # renders normally (proposal generated) — no redirect loop.
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'epilogue/portrait.html')
        ec.refresh_from_db()
        self.assertIsNotNone(
            ec.stage3_completed_at,
            'G.3.1 hotfix must fill stage3_completed_at on Portrait '
            'entry when there is a Stage 3 teacher turn.',
        )
        # First Portrait proposal was also generated (the same first-
        # entry behaviour as the existing test_first_get_generates_
        # proposal_and_renders, but here triggered by the hotfix
        # path instead of the fixture path).
        proposals = [
            t for t in ec.dialogue_turns
            if t.get('stage') == 'portrait'
            and t.get('event') == 'proposal'
        ]
        self.assertEqual(len(proposals), 1)

    def test_stage3_only_assistant_turn_still_redirects(self):
        """Defensive: stage3_completed_at gate must only auto-fill
        when there is a TEACHER turn in Stage 3. An assistant-only
        Stage 3 (the dialogue advanced but the teacher never
        replied) is still 'Stage 3 in progress' and should bounce
        back to the dialogue, not jump straight to the Portrait."""
        EpilogueCompletion.objects.create(
            user=self.user,
            stage0_snapshot=_SNAPSHOT,
            dialogue_entered=True,
            stage1_completed_at=timezone.now(),
            stage2_completed_at=timezone.now(),
            dialogue_turns=[
                {'stage': 3, 'role': 'assistant',
                 'content': 'opening of Stage 3, no teacher reply yet',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
            ],
        )
        resp = self.client.get(reverse('epilogue:portrait'))
        self.assertRedirects(
            resp, reverse('epilogue:dialogue'),
            fetch_redirect_response=False,
        )


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
class PortraitGenerateAndRenderTest(PortraitViewBase):
    """First-entry generation + subsequent revisit rendering."""

    def test_first_get_generates_proposal_and_renders(self):
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            resp = self.client.get(reverse('epilogue:portrait'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'epilogue/portrait.html')
        self.assertContains(resp, 'pedagogical fit')
        row = EpilogueCompletion.objects.get(user=self.user)
        proposals = [
            t for t in row.dialogue_turns
            if t.get('stage') == 'portrait'
            and t.get('event') == 'proposal'
        ]
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0]['content'], _PORTRAIT_TEXT_A)
        # The teacher has not accepted yet, so:
        self.assertEqual(row.learning_portrait_text, '')
        self.assertIsNone(row.learning_portrait_generated_at)

    def test_revisit_does_not_re_extract(self):
        """Second GET must reuse the stored proposal, not call Gemini
        again (proposals are research evidence; a silent re-extract
        would make the record unreliable)."""
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            self.client.get(reverse('epilogue:portrait'))
        mock = _mock_portrait_gemini(_PORTRAIT_TEXT_B)
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            resp = self.client.get(reverse('epilogue:portrait'))
        self.assertEqual(resp.status_code, 200)
        # Mock for the second visit must not have been called.
        mock.generate.assert_not_called()
        # Still only one proposal on record.
        row = EpilogueCompletion.objects.get(user=self.user)
        proposals = [
            t for t in row.dialogue_turns
            if t.get('event') == 'proposal'
        ]
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0]['content'], _PORTRAIT_TEXT_A)

    def test_gemini_failure_renders_retry_state(self):
        """Gemini returning None must not persist a proposal event."""
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(None)):
            resp = self.client.get(reverse('epilogue:portrait'))
        self.assertEqual(resp.status_code, 200)
        # No proposal event written.
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertFalse(any(
            t.get('event') == 'proposal'
            for t in row.dialogue_turns
        ))
        # Page surfaces the retry state.
        self.assertContains(resp, 'could not be generated')


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
class PortraitRegenerateTest(PortraitViewBase):
    """Regeneration is bounded to 2 (design proposal v2 §22.1)."""

    def _generate_initial(self):
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            self.client.get(reverse('epilogue:portrait'))

    def test_regenerate_appends_a_new_proposal(self):
        self._completion_post_stage3()
        self._generate_initial()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_B)):
            resp = self.client.post(reverse('epilogue:portrait_regenerate'))
        self.assertRedirects(
            resp, reverse('epilogue:portrait'),
            fetch_redirect_response=False,
        )
        row = EpilogueCompletion.objects.get(user=self.user)
        proposals = [
            t['content'] for t in row.dialogue_turns
            if t.get('event') == 'proposal'
        ]
        self.assertEqual(proposals, [_PORTRAIT_TEXT_A, _PORTRAIT_TEXT_B])

    def test_third_regeneration_is_refused(self):
        """1 initial + 2 regenerations = 3 proposals max. A fourth
        proposal must NOT be written; Gemini must NOT be called."""
        self._completion_post_stage3()
        self._generate_initial()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_B)):
            self.client.post(reverse('epilogue:portrait_regenerate'))
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_C)):
            self.client.post(reverse('epilogue:portrait_regenerate'))
        mock_fourth = _mock_portrait_gemini('SHOULD NOT BE PERSISTED')
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock_fourth):
            resp = self.client.post(reverse('epilogue:portrait_regenerate'))
        self.assertRedirects(
            resp, reverse('epilogue:portrait'),
            fetch_redirect_response=False,
        )
        mock_fourth.generate.assert_not_called()
        row = EpilogueCompletion.objects.get(user=self.user)
        proposals = [
            t['content'] for t in row.dialogue_turns
            if t.get('event') == 'proposal'
        ]
        self.assertEqual(len(proposals), 3)
        self.assertNotIn('SHOULD NOT BE PERSISTED', proposals)

    def test_regenerate_after_accept_is_refused(self):
        self._completion_post_stage3(
            learning_portrait_text=_PORTRAIT_TEXT_A,
            learning_portrait_generated_at=timezone.now(),
        )
        mock = _mock_portrait_gemini(_PORTRAIT_TEXT_B)
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            self.client.post(reverse('epilogue:portrait_regenerate'))
        mock.generate.assert_not_called()

    def test_regenerate_gemini_failure_does_not_consume_a_slot(self):
        """A failed regeneration must not be counted toward the ceiling."""
        self._completion_post_stage3()
        self._generate_initial()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(None)):
            self.client.post(reverse('epilogue:portrait_regenerate'))
        row = EpilogueCompletion.objects.get(user=self.user)
        proposals = [
            t for t in row.dialogue_turns
            if t.get('event') == 'proposal'
        ]
        self.assertEqual(len(proposals), 1)


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
class PortraitAcceptTest(PortraitViewBase):
    """Accept persists the text + PDF + provenance + completion in one
    atomic block (design proposal v2 §8.4)."""

    def test_accept_persists_text_pdf_provenance_and_completion(self):
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            self.client.get(reverse('epilogue:portrait'))
        # Accept now lands back on /epilogue/portrait/ so the teacher
        # sees the Download PDF + Continue buttons (UX feedback,
        # 2026-05-23). Forward routing happens on the Continue click.
        resp = self.client.post(reverse('epilogue:portrait_accept'))
        self.assertRedirects(
            resp, reverse('epilogue:portrait'),
            fetch_redirect_response=False,
        )

        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertEqual(row.learning_portrait_text, _PORTRAIT_TEXT_A)
        self.assertIsNotNone(row.learning_portrait_generated_at)
        self.assertIsNotNone(row.completed_at)
        # PDF was generated and stored (xhtml2pdf runs live in tests).
        self.assertTrue(bool(row.learning_portrait_pdf))
        # Provenance row written.
        from apps.compliance.models import AIArtefactProvenance
        prov = AIArtefactProvenance.objects.get(
            artefact_kind='epilogue_portrait',
            artefact_pk=str(row.pk),
        )
        self.assertEqual(prov.user_id, self.user.id)
        self.assertEqual(prov.model_name, 'gemini-2.5-flash')
        # `accepted` system event appended to dialogue_turns.
        accepted = [
            t for t in row.dialogue_turns
            if t.get('event') == 'accepted'
        ]
        self.assertEqual(len(accepted), 1)
        self.assertIn('accepted_proposal_index', accepted[0])

    def test_accept_idempotent_second_post(self):
        self._completion_post_stage3(
            learning_portrait_text=_PORTRAIT_TEXT_A,
            learning_portrait_generated_at=timezone.now(),
            completed_at=timezone.now(),
        )
        resp = self.client.post(reverse('epilogue:portrait_accept'))
        self.assertEqual(resp.status_code, 302)
        # An already-accepted second POST routes forward (not back to
        # the portrait), since there is nothing more to review.
        self.assertEqual(resp.url, '/ailst/t2/')
        # Re-POST must not duplicate the provenance row.
        self.client.post(reverse('epilogue:portrait_accept'))
        from apps.compliance.models import AIArtefactProvenance
        count = AIArtefactProvenance.objects.filter(
            artefact_kind='epilogue_portrait',
            artefact_pk=str(EpilogueCompletion.objects.get(
                user=self.user,
            ).pk),
        ).count()
        # Either 0 (no proposal was generated so accept is a no-op) or 1.
        self.assertIn(count, (0, 1))

    def test_continue_after_accept_routes_to_T2(self):
        """The 'Continue' button on the accepted-state portrait page
        POSTs to /epilogue/complete/ — which routes to T2 (or dashboard)
        via _post_epilogue_destination. The two-step pattern was added
        2026-05-23 so the teacher could see the Download-PDF button
        before continuing forward."""
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            self.client.get(reverse('epilogue:portrait'))
        self.client.post(reverse('epilogue:portrait_accept'))
        # Now the teacher clicks "Continue".
        resp = self.client.post(reverse('epilogue:complete'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/ailst/t2/')

    def test_accepted_portrait_page_shows_download_and_continue(self):
        """Belt-and-braces: the accepted state of the portrait page
        renders both the Download as PDF link and the Continue form."""
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            self.client.get(reverse('epilogue:portrait'))
        self.client.post(reverse('epilogue:portrait_accept'))
        resp = self.client.get(reverse('epilogue:portrait'))
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode('utf-8')
        self.assertIn(reverse('epilogue:portrait_pdf'), body)
        self.assertIn(reverse('epilogue:complete'), body)

    def test_accept_without_a_proposal_redirects_with_warning(self):
        self._completion_post_stage3()
        resp = self.client.post(reverse('epilogue:portrait_accept'))
        self.assertRedirects(
            resp, reverse('epilogue:portrait'),
            fetch_redirect_response=False,
        )
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertEqual(row.learning_portrait_text, '')

    def test_accept_pdf_failure_still_persists_text(self):
        """The PDF is best-effort: a pisa failure must not roll back
        the text / provenance writes (design proposal v2 §10.1)."""
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            self.client.get(reverse('epilogue:portrait'))
        with patch(
            'apps.epilogue.views._generate_portrait_pdf',
            side_effect=RuntimeError('forced pisa failure'),
        ):
            resp = self.client.post(reverse('epilogue:portrait_accept'))
        self.assertEqual(resp.status_code, 302)
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertEqual(row.learning_portrait_text, _PORTRAIT_TEXT_A)
        self.assertIsNotNone(row.completed_at)
        # PDF was not saved.
        self.assertFalse(bool(row.learning_portrait_pdf))
        # Provenance still written.
        from apps.compliance.models import AIArtefactProvenance
        self.assertTrue(
            AIArtefactProvenance.objects.filter(
                artefact_kind='epilogue_portrait',
                artefact_pk=str(row.pk),
            ).exists()
        )


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
class PortraitPDFDownloadTest(PortraitViewBase):

    def test_pdf_view_404_when_no_portrait(self):
        EpilogueCompletion.objects.create(user=self.user)
        resp = self.client.get(reverse('epilogue:portrait_pdf'))
        self.assertEqual(resp.status_code, 404)

    def test_pdf_view_serves_attachment(self):
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            self.client.get(reverse('epilogue:portrait'))
        self.client.post(reverse('epilogue:portrait_accept'))
        resp = self.client.get(reverse('epilogue:portrait_pdf'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertIn('attachment', resp['Content-Disposition'])

    def test_pdf_view_regenerates_on_demand_when_file_missing(self):
        """If accept persisted the text but the PDF blob is absent
        (pisa failure during accept), the download view regenerates
        from the stored text and saves before serving."""
        self._completion_post_stage3(
            learning_portrait_text=_PORTRAIT_TEXT_A,
            learning_portrait_generated_at=timezone.now(),
        )
        # Confirm we are starting from "text present, file absent".
        row = EpilogueCompletion.objects.get(user=self.user)
        self.assertFalse(bool(row.learning_portrait_pdf))
        resp = self.client.get(reverse('epilogue:portrait_pdf'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        # The PDF blob is now persisted for future requests.
        row.refresh_from_db()
        self.assertTrue(bool(row.learning_portrait_pdf))


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
class PortraitPDFArticle50MetadataTest(PortraitViewBase):
    """Strict variant — JSON-LD inside the PDF body plus PDF document
    metadata (design proposal v2 §22.3)."""

    def _accepted_pdf_bytes(self):
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            self.client.get(reverse('epilogue:portrait'))
        self.client.post(reverse('epilogue:portrait_accept'))
        resp = self.client.get(reverse('epilogue:portrait_pdf'))
        return resp.getvalue() if hasattr(resp, 'getvalue') else b''.join(resp.streaming_content)

    def test_pdf_html_render_carries_jsonld_block(self):
        """The HTML source that pisa renders to PDF carries the
        Article 50(2) JSON-LD block. We assert against the HTML
        (the truthful layer) rather than the PDF bytes — pisa
        compresses content streams (ASCII85/Flate), so a literal
        grep against the raw PDF bytes is the wrong test. The
        metadata test below covers the strict Article 50(2) layer
        in the PDF Info dict (which is NOT compressed)."""
        self._completion_post_stage3()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=_mock_portrait_gemini(_PORTRAIT_TEXT_A)):
            self.client.get(reverse('epilogue:portrait'))
        self.client.post(reverse('epilogue:portrait_accept'))
        from django.template.loader import render_to_string
        from apps.compliance.models import AIArtefactProvenance
        row = EpilogueCompletion.objects.get(user=self.user)
        provenance = AIArtefactProvenance.objects.get(
            artefact_kind='epilogue_portrait',
            artefact_pk=str(row.pk),
        )
        html = render_to_string('pdf/learning_portrait.html', {
            'portrait_text': row.learning_portrait_text,
            'snapshot': row.stage0_snapshot,
            'teacher_display': self.user.username,
            'generated_at': row.learning_portrait_generated_at,
            'model_name': 'gemini-2.5-flash',
            'provenance': provenance,
            'provenances': [provenance],
        })
        self.assertIn('application/ld+json', html)
        self.assertIn('epilogue_portrait', html)
        self.assertIn('SoftwareApplication', html)
        self.assertIn('gemini-2.5-flash', html)

    def test_pdf_carries_document_metadata(self):
        """PDF Info dict carries Title / Author / Subject / Keywords
        / Creator from the <meta> tags in the template head."""
        pdf_bytes = self._accepted_pdf_bytes()
        # The PDF info layer carries these strings literally (PDF
        # is a binary format, but textual /Info entries are visible).
        self.assertIn(b'PROODOS Learning Portrait', pdf_bytes)
        self.assertIn(b'EU AI Act Article 50', pdf_bytes)
        self.assertIn(b'gemini-2.5-flash', pdf_bytes)


# ======================================================================
# G.6b — Teacher-facing label-leak guard (proposal §9.4)
# ======================================================================

class TeacherFacingLabelLeakTest(EpilogueViewBase):
    """Platform-wide rule (memory: feedback_ui_internal_labels):
    no internal research labels in teacher-visible text. Implements
    the §9.4 specification of the G.6 design proposal — strictly
    scoped to **teacher-visible text**, not the full HTML stream
    (the Article 50(2) JSON-LD block and the C.3 <meta> tags
    legitimately contain identifiers like 'epilogue_portrait',
    'gemini-2.5-flash', and 'AILST' — those are machine-readable
    compliance markers, not teacher copy).

    Phase G closure (2026-05-24) — dialogue + portrait fixtures
    removed together with their views. The Stage 0 surface remains
    the only teacher-facing Epilogue page; the label-leak check on
    it stays active. See
    proodos_files/PHASE_G_DIALOGUE_DEPRECATION_20260524.md §4.2.
    """

    # Word-boundary patterns — bare 'T0/T1/T2' would match prose like
    # 'the T2 closing reflection'; the exact-word form catches the
    # bureaucratic label without false positives. Patterns from
    # G.6 proposal §9.4.
    FORBIDDEN_PATTERNS = [
        r'\bStage\s*[0-3]\b',
        r'\bDTP\b',
        r'\bRTM\b',
        r'\bAILST\b',
        r'\bT[012]\b',
        r'\bTab\s*[125]\b',
    ]

    def _visible_text(self, html):
        """Strip machine-readable and head content; return only what
        the teacher reads on the page. The JSON-LD <script>, <meta>
        tags, <style>, and the entire <head> are all dropped — those
        carry compliance markers and CSS, not teacher copy."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style', 'meta', 'head', 'link']):
            tag.decompose()
        return soup.get_text(separator=' ')

    def _assert_no_leaks(self, url_name, label_for_error=''):
        import re
        resp = self.client.get(reverse(url_name))
        self.assertEqual(resp.status_code, 200)
        visible = self._visible_text(resp.content.decode('utf-8'))
        for pattern in self.FORBIDDEN_PATTERNS:
            match = re.search(pattern, visible)
            self.assertIsNone(
                match,
                f"{label_for_error or url_name} leaks pattern "
                f"{pattern!r} at: ...{visible[max(0, match.start()-60):match.end()+60]!r}..."
                if match else f"{label_for_error or url_name} OK",
            )

    # --- Stage 0 surface (G.6b) ---

    def test_stage0_page_no_leaks(self):
        """Stage 0 page (the magazine-redesigned hero + standfirst +
        action buttons + included _stage0_panel.html partial)
        contains no teacher-visible forbidden labels."""
        self._assert_no_leaks('epilogue:placeholder')

    def test_stage0_page_already_completed_no_leaks(self):
        """The already-completed banner variant of the Stage 0 page
        also must not leak labels."""
        row = EpilogueCompletion.objects.create(user=self.user)
        row.completed_at = timezone.now()
        row.save(update_fields=['completed_at'])
        self._assert_no_leaks('epilogue:placeholder')

    # --- Dialogue + Portrait fixtures removed in Phase G closure ---
    # The Stages 1-3 Aletheia dialogue and the Learning Portrait HITL
    # flow were deactivated on 2026-05-24. The corresponding fixtures
    # and label-leak tests
    #   _dialogue_completion / test_dialogue_page_no_leaks_stage{1,2,3}_active
    # were removed together with the views they exercised. The fixture
    # patterns are recoverable from git history (commit before this
    # closure) if Phase J ever re-introduces a teacher-facing chatbot
    # surface that warrants the same label-leak guarantee.


@unittest.skip(DEACTIVATED_PHASE_G_CLOSURE)
class DialoguePhaseSeamTest(EpilogueViewBase):
    """G.6c phase-as-chapter regression guard (proposal §9.3).

    The pre-G.6c dialogue layout rendered every turn in a flat
    chronological scroll. At a stage transition (Stage 1 → Stage 2 or
    Stage 2 → Stage 3) the closing assistant turn of stage N and the
    opening assistant turn of stage N+1 appeared as two consecutive
    .chat.chat-start bubbles — the phase-seam bug surfaced by the PI
    on 2026-05-23.

    The fix groups turns per phase and renders prior phases inside
    <details> elements. The two boundary assistant turns end up on
    opposite sides of a <details> wall — never visually adjacent.

    This test verifies the structure structurally (not visually): the
    rendered HTML, with <details> open in source, must not contain
    two assistant turn elements for different stages within the same
    <details>-less container.
    """

    def test_stage_transition_does_not_produce_consecutive_assistant_bubbles(self):
        """At Stage 3 active with Stages 1+2 collapsed, the active
        Stage 3 chapter contains its own opening assistant turn but
        the prior Stages 1/2 opening + reply turns are inside the
        collapsed <details>. Even with the details open in the
        source HTML, the active phase's chapter (.phase-chapter:
        not(.phase-chapter--collapsed)) cannot contain assistant
        turns from any stage other than the active one — proven by
        checking the source pattern."""
        from apps.epilogue.tests import _SNAPSHOT  # noqa
        EpilogueCompletion.objects.create(
            user=self.user,
            stage0_snapshot=_SNAPSHOT,
            dialogue_entered=True,
            stage1_completed_at=timezone.now(),
            stage2_completed_at=timezone.now(),
            dialogue_turns=[
                # Stage 1: opening + teacher reply
                {'stage': 1, 'role': 'assistant', 'content': 'S1 opening.',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 1, 'role': 'teacher', 'content': 'S1 reply.',
                 'generated_at': 'x'},
                # Stage 2: opening + teacher reply
                {'stage': 2, 'role': 'assistant', 'content': 'S2 opening.',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 2, 'role': 'teacher', 'content': 'S2 reply.',
                 'generated_at': 'x'},
                # Stage 3: opening only (active)
                {'stage': 3, 'role': 'assistant', 'content': 'S3 opening.',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
            ],
        )
        resp = self.client.get(reverse('epilogue:dialogue'))
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode('utf-8')

        # The active chapter is a <article class="phase-chapter
        # rfx-screen-in"> WITHOUT the --collapsed modifier. The
        # collapsed prior chapters are <details class="phase-chapter
        # phase-chapter--collapsed">. The phase-seam fix means the
        # active <article> can contain ONLY the active stage's turns.
        # We verify by extracting the active <article> block and
        # asserting it does not contain the prior stages' content.
        import re
        active_match = re.search(
            r'<article\b[^>]*class="[^"]*phase-chapter[^"]*rfx-screen-in[^"]*"[^>]*>(.*?)</article>',
            body, re.DOTALL,
        )
        self.assertIsNotNone(
            active_match,
            'The dialogue page must render an active phase chapter '
            'with the rfx-screen-in class (G.6c §4.2).',
        )
        active_inner = active_match.group(1)
        self.assertIn(
            'S3 opening.', active_inner,
            'Active chapter must contain its own opening turn.',
        )
        self.assertNotIn(
            'S1 opening.', active_inner,
            'PHASE-SEAM REGRESSION: the active chapter must not '
            'contain prior Stage 1 turns — those belong to a '
            'collapsed <details>.',
        )
        self.assertNotIn(
            'S2 opening.', active_inner,
            'PHASE-SEAM REGRESSION: the active chapter must not '
            'contain prior Stage 2 turns.',
        )

    def test_collapsed_prior_phases_render_as_details(self):
        """Each prior phase must render as a <details class="…
        phase-chapter--collapsed"> (the G.6c collapse pattern). The
        <summary> shows the phase numeral + name + last-teacher
        preview."""
        from apps.epilogue.tests import _SNAPSHOT  # noqa
        EpilogueCompletion.objects.create(
            user=self.user,
            stage0_snapshot=_SNAPSHOT,
            dialogue_entered=True,
            stage1_completed_at=timezone.now(),
            stage2_completed_at=timezone.now(),
            dialogue_turns=[
                {'stage': 1, 'role': 'assistant', 'content': 'S1 open.',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 1, 'role': 'teacher',
                 'content': 'S1 teacher final reply.', 'generated_at': 'x'},
                {'stage': 2, 'role': 'assistant', 'content': 'S2 open.',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
                {'stage': 2, 'role': 'teacher',
                 'content': 'S2 teacher final reply.', 'generated_at': 'x'},
                {'stage': 3, 'role': 'assistant', 'content': 'S3 open.',
                 'model': 'gemini-2.5-flash', 'generated_at': 'x'},
            ],
        )
        resp = self.client.get(reverse('epilogue:dialogue'))
        body = resp.content.decode('utf-8')
        # Two collapsed <details> for the two prior phases.
        self.assertEqual(
            body.count('phase-chapter--collapsed'), 2,
            'Stages 1 and 2 must both render as collapsed chapters.',
        )
        # The teacher's last reply per prior phase appears in the
        # collapsed summary as a 1-line preview.
        self.assertIn('S1 teacher final reply.', body)
        self.assertIn('S2 teacher final reply.', body)
