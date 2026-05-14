"""DTPAgent parity + multi-call cost tests vs the monolith compute_dtp.

Two-layer invariant from PHASE_E_DESIGN_PROPOSAL_v5 §5 (inherits v2):
  (1) Prompt-identical with rag_query_system per Gemini sub-call
  (2) Behaviour-identical given mocked Gemini outputs

Plus the contract checks specific to commit 5 (DTP is the first
multi-Gemini-call agent):
  - 2 'agent.cost' events per generate() (theme + narrative)
  - Embedding failure -> None
  - Theme JSON parse failure -> empty themes default (composite still
    completes with the canned continuity_description as narrative)
  - Narrative empty -> fallback to continuity_description
  - JSON repair fallback for theme extraction (max(0, ...) wrappers)
  - clean_json_response invoked via the agent's import site
"""

import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from apps.agents.dtp import (
    DTP_HIGH_THRESHOLD,
    DTP_MODERATE_THRESHOLD,
    DTP_NARRATIVE_MAX_TOKENS,
    DTP_NARRATIVE_TEMPERATURE,
    DTP_THEME_MAX_TOKENS,
    DTP_THEME_TEMPERATURE,
    DTPAgent,
)
from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.llm_client import GenerationResult
from apps.compliance.models import AIArtefactProvenance
from apps.modules.models import Module, UserModuleProgress


_PREV = (
    "I tried ChatGPT for the first time today to draft quiz questions. "
    "I was excited but worried about over-relying on AI."
)
_CURR = (
    "After three modules I'm finding I assess AI outputs more critically. "
    "The novelty has worn off but my pedagogical evaluation has sharpened."
)


# ----------------------------------------------------------------------
# Helpers — multi-call Gemini mocks.
# ----------------------------------------------------------------------
def _gen_result(text: str, tokens: int = 100, cost: float = 0.0000279):
    return GenerationResult(
        text=text, model='gemini-2.5-flash',
        tokens_estimate=tokens, cost_eur_estimate=cost,
    )


def _mock_llm_for_full_run(theme_json: str, narrative_text: str):
    """LLMClient mock that returns:
      - embed: a fixed 768-d vector on every call
      - generate: side_effect that alternates theme then narrative
    """
    mock = MagicMock()
    mock.embed.return_value = [0.1] * 768
    mock.generate.side_effect = [
        _gen_result(theme_json),
        _gen_result(narrative_text),
    ]
    return mock


class DTPHierarchyTest(SimpleTestCase):
    def test_inherits_from_research_instrument_agent(self):
        self.assertTrue(issubclass(DTPAgent, ResearchInstrumentAgent))

    def test_artefact_kind(self):
        self.assertEqual(DTPAgent.artefact_kind, 'dtp_narrative')

    def test_model_name(self):
        self.assertEqual(DTPAgent.model_name, 'gemini-2.5-flash')

    def test_constants_match_monolith(self):
        """Continuity thresholds and Gemini-call parameters are
        research artefacts — must not drift without a methodology
        commit. These values come from rag_query_system.compute_
        development_signal / extract_development_themes / generate_
        development_narrative."""
        self.assertEqual(DTP_HIGH_THRESHOLD, 0.85)
        self.assertEqual(DTP_MODERATE_THRESHOLD, 0.70)
        self.assertEqual(DTP_THEME_TEMPERATURE, 0.3)
        self.assertEqual(DTP_THEME_MAX_TOKENS, 1000)
        self.assertEqual(DTP_NARRATIVE_TEMPERATURE, 0.4)
        self.assertEqual(DTP_NARRATIVE_MAX_TOKENS, 2000)


class DTPDevelopmentSignalTest(SimpleTestCase):
    """Pure-function tests on the cosine signal — no mocks needed."""

    def _vec_with_similarity(self, target_similarity: float):
        """Return two unit-length 2-d vectors whose dot product equals
        target_similarity exactly. Used to hit each branch boundary."""
        import math
        theta = math.acos(target_similarity)
        v1 = [1.0, 0.0]
        v2 = [math.cos(theta), math.sin(theta)]
        return v1, v2

    def test_high_continuity_branch(self):
        v1, v2 = self._vec_with_similarity(0.90)
        out = DTPAgent.compute_development_signal(v1, v2)
        self.assertEqual(out['continuity_label'], 'High')
        self.assertIn('sustained focus', out['continuity_description'])

    def test_moderate_continuity_branch(self):
        v1, v2 = self._vec_with_similarity(0.78)
        out = DTPAgent.compute_development_signal(v1, v2)
        self.assertEqual(out['continuity_label'], 'Moderate')
        self.assertIn('evolved', out['continuity_description'])

    def test_significant_continuity_branch(self):
        v1, v2 = self._vec_with_similarity(0.50)
        out = DTPAgent.compute_development_signal(v1, v2)
        self.assertEqual(out['continuity_label'], 'Significant')
        self.assertIn('substantial evolution', out['continuity_description'])

    def test_boundary_at_high_threshold_inclusive(self):
        """0.85 exactly is 'High' (>= comparison)."""
        v1, v2 = self._vec_with_similarity(0.85)
        out = DTPAgent.compute_development_signal(v1, v2)
        self.assertEqual(out['continuity_label'], 'High')

    def test_boundary_at_moderate_threshold_inclusive(self):
        """0.70 exactly is 'Moderate'."""
        v1, v2 = self._vec_with_similarity(0.70)
        out = DTPAgent.compute_development_signal(v1, v2)
        self.assertEqual(out['continuity_label'], 'Moderate')

    def test_similarity_rounded_to_4_decimals(self):
        v1, v2 = self._vec_with_similarity(0.50)
        out = DTPAgent.compute_development_signal(v1, v2)
        # Round-trip via str to count decimal places.
        s = f"{out['similarity']:.6f}"
        # Last two digits should be zero (4-decimal precision).
        self.assertEqual(s[-2:], '00')


class DTPPromptParityTest(SimpleTestCase):
    """Layer-1 invariant: each agent prompt == monolith prompt."""

    def test_themes_prompt_matches_monolith(self):
        import rag_query_system as monolith

        captured = {}

        def fake_generate_content(**kwargs):
            captured['contents'] = kwargs.get('contents')
            response = MagicMock()
            response.text = '{"increased": [], "decreased": [], "stable": []}'
            return response

        with patch.object(monolith, 'NEW_GENAI_API', True), \
             patch.object(monolith, 'client') as mock_client:
            mock_client.models.generate_content = fake_generate_content
            monolith.extract_development_themes(_PREV, _CURR)

        monolith_prompt = captured['contents']
        agent_prompt = DTPAgent._build_themes_prompt(_PREV, _CURR)
        self.assertEqual(monolith_prompt, agent_prompt)

    def test_narrative_prompt_matches_monolith(self):
        import rag_query_system as monolith

        captured = {}

        def fake_generate_content(**kwargs):
            captured['contents'] = kwargs.get('contents')
            response = MagicMock()
            response.text = 'Across these modules, your reflection demonstrates...'
            return response

        signal = {
            'similarity': 0.78, 'continuity_label': 'Moderate',
            'continuity_description': (
                'Your pedagogical focus has evolved, showing deeper engagement '
                'with instructional design.'
            ),
        }
        themes = {'increased': ['ethical focus'], 'decreased': [], 'stable': ['differentiation']}

        with patch.object(monolith, 'NEW_GENAI_API', True), \
             patch.object(monolith, 'client') as mock_client:
            mock_client.models.generate_content = fake_generate_content
            monolith.generate_development_narrative(signal, themes, 'M1', 'M2')

        monolith_prompt = captured['contents']
        agent_prompt = DTPAgent._build_narrative_prompt(signal, themes, 'M1', 'M2')
        self.assertEqual(monolith_prompt, agent_prompt)


class DTPLayer0BoilerplateTest(SimpleTestCase):
    """Layer-0 (commit-2 invariant): exact-string assertions for
    boilerplate prone to escape / wording drift."""

    def test_themes_prompt_layer0(self):
        prompt = DTPAgent._build_themes_prompt(_PREV, _CURR)
        self.assertIn('PREVIOUS:', prompt)
        self.assertIn('CURRENT:', prompt)
        self.assertIn(
            '{"increased": [], "decreased": [], "stable": []}', prompt,
        )
        self.assertIn('Fill each array with 2-3 phrases of MAX 3 WORDS EACH.', prompt)
        self.assertIn(
            '{"increased": ["ethical focus"], "decreased": [], "stable": ["physics context"]}',
            prompt,
        )

    def test_narrative_prompt_layer0(self):
        signal = {
            'continuity_label': 'High',
            'continuity_description': 'Test description for layer-0 test.',
        }
        themes = {'increased': [], 'decreased': [], 'stable': ['x']}
        prompt = DTPAgent._build_narrative_prompt(signal, themes, 'M3', 'M4')
        self.assertIn(
            'Write a complete paragraph of exactly 60 words.', prompt,
        )
        self.assertIn(
            'Start with: "Across these modules, your reflection demonstrates"',
            prompt,
        )
        self.assertIn('Do not use bullet points. Write in plain prose only.', prompt)
        # Module-pair interpolation
        self.assertIn('Modules compared: M3 to M4', prompt)

    def test_themes_prompt_sanitises_400_char_cap(self):
        long_text = 'x' * 600 + 'AFTER_CAP'
        prompt = DTPAgent._build_themes_prompt(long_text, _CURR)
        # The 'AFTER_CAP' marker is past the 400-char budget and
        # must not appear in the prompt.
        self.assertNotIn('AFTER_CAP', prompt)

    def test_themes_prompt_quote_and_newline_sanitisation(self):
        text = 'She said "AI is helpful"\nthen continued reflecting.'
        prompt = DTPAgent._build_themes_prompt(text, _CURR)
        # " -> '
        self.assertIn("She said 'AI is helpful'", prompt)
        # \n -> space (the literal newline character)
        self.assertNotIn("'AI is helpful'\nthen", prompt)


class DTPJsonRepairContractTest(SimpleTestCase):
    """Per v5 §5 Layer-0 rule, patch at agent import site."""

    def test_clean_json_response_invoked_for_theme_step(self):
        from apps.agents.shared.json_repair import (
            clean_json_response as real_clean,
        )

        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        # Theme returns fenced JSON (needs cleanup); narrative is plain.
        mock_client.generate.side_effect = [
            _gen_result('```json\n{"increased":[],"decreased":[],"stable":[]}\n```'),
            _gen_result('Narrative text here.'),
        ]
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client), \
             patch('apps.agents.dtp.clean_json_response',
                   wraps=real_clean) as spy:
            DTPAgent()._do_generate(
                previous_reflection_text=_PREV,
                current_reflection_text=_CURR,
            )
        spy.assert_called()

    def test_theme_json_repair_fallback_on_unbalanced_braces(self):
        """When themes response is truncated, the JSON repair fallback
        kicks in. Verifies the max(0, ...) wrappers don't crash."""
        truncated = '{"increased": ["focus"], "decreased": [], "stable":'

        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        mock_client.generate.side_effect = [
            _gen_result(truncated),
            _gen_result('Narrative text.'),
        ]
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            agent = DTPAgent()
            themes = agent._extract_themes(_PREV, _CURR)
        # Repair adds closing brackets/braces — best-effort recovery.
        # Either we recovered something or we fell back to empty.
        self.assertIn('increased', themes)
        self.assertIn('decreased', themes)
        self.assertIn('stable', themes)


class DTPMultiCallCostTrackingTest(TestCase):
    """One generate() = two 'agent.cost' events (theme + narrative).

    DTP is the test case for per-Gemini-call cost granularity. Future
    Peer Synthesis (commit 7) follows the same pattern."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('dtp_user', password='pw')
        cls.module = Module.objects.create(
            code='AGDTP', title='DTP agent test',
            description='t', order_index=995,
            unesco_aspect='ethics', proficiency_level='Acquire',
            is_published=True,
        )

    def _make_progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def test_two_cost_events_per_generate(self):
        progress = self._make_progress()
        mock_client = _mock_llm_for_full_run(
            theme_json='{"increased":[],"decreased":[],"stable":[]}',
            narrative_text='Narrative paragraph.',
        )
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client), \
             self.assertLogs('agents.audit', level='INFO') as cm:
            DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                previous_reflection_text=_PREV,
                current_reflection_text=_CURR,
                previous_module='M1', current_module='M2',
            )

        cost_events = [
            r for r in cm.records if r.getMessage() == 'agent.cost'
        ]
        self.assertEqual(
            len(cost_events), 2,
            'DTP should emit exactly two agent.cost events per '
            'generate(): one for theme extraction, one for narrative.',
        )
        # Both events must carry the correct model and agent.
        for record in cost_events:
            self.assertEqual(record.agent, 'DTPAgent')
            self.assertEqual(record.model, 'gemini-2.5-flash')
            self.assertEqual(record.artefact_kind, 'dtp_narrative')


class DTPFailureModesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('dtp_fail_user', password='pw')
        cls.module = Module.objects.create(
            code='AGDTP2', title='DTP fail test',
            description='t', order_index=994,
            unesco_aspect='ethics', proficiency_level='Acquire',
            is_published=True,
        )

    def _make_progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def test_embedding_failure_raises_and_rolls_back(self):
        """CP-9 invariant: if either embed_query returns None,
        _do_generate raises RuntimeError so the surrounding atomic
        rolls back. No provenance row, no progress.reflection_dtp
        mutation. Matches RAGFeedbackAgent's embedding-failure
        contract for symmetry."""
        mock_client = MagicMock()
        mock_client.embed.return_value = None  # Both embeds fail.

        progress = self._make_progress()
        progress.reflection_dtp = '__untouched__'
        progress.save(update_fields=['reflection_dtp'])
        before = AIArtefactProvenance.objects.count()

        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            with self.assertRaises(RuntimeError):
                DTPAgent().generate(
                    user=self.user, module=self.module,
                    save_target=progress, save_field='reflection_dtp',
                    previous_reflection_text=_PREV,
                    current_reflection_text=_CURR,
                )

        # CP-9: progress.reflection_dtp untouched, no provenance row.
        progress.refresh_from_db()
        self.assertEqual(progress.reflection_dtp, '__untouched__')
        self.assertEqual(AIArtefactProvenance.objects.count(), before)

    def test_theme_extraction_returns_empty_default_on_gemini_none(self):
        """When the theme Gemini call returns None, themes default to
        the empty shape and the composite still completes."""
        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        mock_client.generate.side_effect = [
            None,  # Theme call fails
            _gen_result('Narrative text.'),
        ]
        progress = self._make_progress()
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            result = DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                previous_reflection_text=_PREV,
                current_reflection_text=_CURR,
            )
        self.assertEqual(result['themes']['increased_themes'], [])
        self.assertEqual(result['themes']['stable_themes'], [])

    def test_narrative_falls_back_to_continuity_description_on_gemini_none(self):
        """When the narrative Gemini call returns None, narrative
        falls back to signal['continuity_description']."""
        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        mock_client.generate.side_effect = [
            _gen_result('{"increased":[],"decreased":[],"stable":[]}'),
            None,  # Narrative call fails
        ]
        progress = self._make_progress()
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            result = DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                previous_reflection_text=_PREV,
                current_reflection_text=_CURR,
            )
        # The fallback is the bucket-specific canned sentence.
        self.assertIn(result['narrative'], (
            'Your reflections show sustained focus on core pedagogical priorities.',
            'Your pedagogical focus has evolved, showing deeper engagement '
            'with instructional design.',
            'Your reflection shows substantial evolution in how you '
            'conceptualize AI in education.',
        ))

    def test_narrative_falls_back_on_empty_text(self):
        """Empty/whitespace narrative -> same fallback."""
        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        mock_client.generate.side_effect = [
            _gen_result('{"increased":[],"decreased":[],"stable":[]}'),
            _gen_result('   '),  # Empty narrative
        ]
        progress = self._make_progress()
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            result = DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                previous_reflection_text=_PREV,
                current_reflection_text=_CURR,
            )
        self.assertNotEqual(result['narrative'], '')


class DTPEndToEndTest(TestCase):
    """Behaviour-identical with mocked Gemini: composite shape +
    persistence + provenance — all as today's views.py path produces."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('dtp_e2e_user', password='pw')
        cls.module = Module.objects.create(
            code='AGDTP3', title='DTP end-to-end test',
            description='t', order_index=993,
            unesco_aspect='ethics', proficiency_level='Acquire',
            is_published=True,
        )

    def _make_progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def test_full_generate_persists_json_and_writes_provenance(self):
        progress = self._make_progress()
        mock_client = _mock_llm_for_full_run(
            theme_json=json.dumps({
                'increased': ['ethical focus'],
                'decreased': ['novelty hype'],
                'stable': ['mathematics context'],
            }),
            narrative_text=(
                'Across these modules, your reflection demonstrates a deepening '
                'engagement with the ethical dimensions of AI in your teaching, '
                'while sustaining your subject-specific framing in mathematics. '
                'The novelty of AI tools appears to have given way to a more '
                'measured pedagogical evaluation, which is a meaningful shift '
                'in how you situate AI within your classroom practice.'
            ),
        )

        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            result = DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                previous_reflection_text=_PREV,
                current_reflection_text=_CURR,
                previous_module='M1', current_module='M4',
            )

        # Composite shape parity with monolith compute_dtp return
        self.assertIn('previous_module', result)
        self.assertIn('current_module', result)
        self.assertIn('similarity', result)
        self.assertIn('continuity_label', result)
        self.assertIn('continuity_description', result)
        self.assertIn('narrative', result)
        self.assertEqual(
            sorted(result['themes'].keys()),
            ['decreased_themes', 'increased_themes', 'stable_themes'],
        )
        self.assertEqual(result['previous_module'], 'M1')
        self.assertEqual(result['current_module'], 'M4')

        # Persistence: progress.reflection_dtp holds the JSON dump.
        progress.refresh_from_db()
        self.assertIsNotNone(progress.reflection_dtp)
        round_tripped = json.loads(progress.reflection_dtp)
        self.assertEqual(round_tripped['current_module'], 'M4')

        # Provenance row exists, keyed by ('dtp_narrative', progress.pk).
        self.assertTrue(
            AIArtefactProvenance.objects.filter(
                artefact_kind='dtp_narrative',
                artefact_pk=str(progress.pk),
                user=self.user,
                model_name='gemini-2.5-flash',
            ).exists()
        )

    def test_persist_field_overwrite_preserves_atomic_invariant(self):
        """Re-running generate() on the same progress row replaces the
        reflection_dtp content. The 'dtp_narrative' provenance row is
        get_or_create-d on (kind, pk), so the count stays at 1."""
        progress = self._make_progress()

        def _run_with(theme_json):
            mock = _mock_llm_for_full_run(theme_json, 'Narrative text.')
            with patch('apps.agents.dtp.get_llm_client', return_value=mock):
                DTPAgent().generate(
                    user=self.user, module=self.module,
                    save_target=progress, save_field='reflection_dtp',
                    previous_reflection_text=_PREV,
                    current_reflection_text=_CURR,
                )

        _run_with('{"increased":["a"],"decreased":[],"stable":[]}')
        _run_with('{"increased":["b"],"decreased":[],"stable":[]}')

        progress.refresh_from_db()
        latest = json.loads(progress.reflection_dtp)
        self.assertEqual(latest['themes']['increased_themes'], ['b'])

        # Idempotent provenance: still exactly one row.
        self.assertEqual(
            AIArtefactProvenance.objects.filter(
                artefact_kind='dtp_narrative',
                artefact_pk=str(progress.pk),
            ).count(),
            1,
        )
