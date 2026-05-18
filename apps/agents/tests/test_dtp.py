"""DTPAgent tests — redefined dual-signal DTP (D.3a).

The DTP was redefined from the Phase E monolith-parity single-signal
form into two independent signals: a Vertical Continuity Signal (VCS,
within-aspect, one proficiency level down) and a Temporal Shift Signal
(TSS, against the immediately preceding module). See
proodos_files/DTP_REDEFINITION_DESIGN_PROPOSAL_v1_20260518.md.

These tests use mocked Gemini calls. They verify plumbing, composite
shape, prompts, cost events and failure modes — NOT the quality of the
generated narrative. Live-output verification with real Gemini calls
is a separate, tracked step (design proposal §12).
"""

import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from apps.agents.dtp import (
    DTP_NARRATIVE_FALLBACK,
    DTP_NARRATIVE_MAX_TOKENS,
    DTP_NARRATIVE_TEMPERATURE,
    DTP_REFLECTION_PROMPT_BUDGET,
    DTP_SCHEMA,
    DTP_THEME_MAX_TOKENS,
    DTP_THEME_TEMPERATURE,
    DTPAgent,
)
from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.llm_client import GenerationResult
from apps.agents.tests._fixtures import load_prompt_fixture
from apps.compliance.models import AIArtefactProvenance
from apps.modules.models import Module, UserModuleProgress


# _VERTICAL is byte-identical to the old test file's _PREV, and
# _CURRENT to the old _CURR — this keeps the unchanged dtp_themes.txt
# fixture valid (the theme-extraction prompt did not change).
_CURRENT = (
    "After three modules I'm finding I assess AI outputs more critically. "
    "The novelty has worn off but my pedagogical evaluation has sharpened."
)
_VERTICAL = (
    "I tried ChatGPT for the first time today to draft quiz questions. "
    "I was excited but worried about over-relying on AI."
)
_TEMPORAL = (
    "This module pushed me to think about fairness when an AI tool grades "
    "student work, and who is accountable for an unfair outcome."
)

# Canonical input for the frozen narrative-prompt fixture
# (prompt_fixtures/dtp_narrative.txt). Regenerating the fixture requires
# re-running DTPAgent._build_narrative_prompt with exactly this input.
_FIXTURE_CURRENT_MODULE = 'M8'
_FIXTURE_SIGNALS = {
    'vertical': {
        'comparison_module': 'M3',
        'similarity': 0.7421,
        'themes': {
            'increased_themes': ['ethical focus'],
            'decreased_themes': [],
            'stable_themes': ['mathematics context'],
        },
    },
    'temporal': {
        'comparison_module': 'M7',
        'similarity': 0.6810,
        'themes': {
            'increased_themes': ['assessment design'],
            'decreased_themes': ['novelty'],
            'stable_themes': [],
        },
    },
}


def _gen_result(text, tokens=100, cost=0.0000279):
    return GenerationResult(
        text=text, model='gemini-2.5-flash',
        tokens_estimate=tokens, cost_eur_estimate=cost,
    )


def _theme_json(increased=None, decreased=None, stable=None):
    return json.dumps({
        'increased': increased or [],
        'decreased': decreased or [],
        'stable': stable or [],
    })


# A well-formed structured narrative response (the <synthesis> block is
# what the agent keeps; the analysis blocks are chain-of-thought scaffold).
_NARRATIVE_RESPONSE = (
    '<vertical_analysis>The competency framing held steady.</vertical_analysis>\n'
    '<temporal_analysis>Focus moved toward ethics.</temporal_analysis>\n'
    '<synthesis>Across these modules, your reflection sustains a subject '
    'framing while shifting attention toward the ethical dimensions of '
    'AI use in your teaching.</synthesis>'
)
_SYNTHESIS_TEXT = (
    'Across these modules, your reflection sustains a subject framing '
    'while shifting attention toward the ethical dimensions of AI use '
    'in your teaching.'
)


def _mock_llm(generate_results, embed_vector=None):
    """LLMClient mock: a fixed embedding vector for every embed() call,
    and a fixed sequence of GenerationResults for generate()."""
    mock = MagicMock()
    mock.embed.return_value = embed_vector if embed_vector is not None else [0.1] * 768
    mock.generate.side_effect = list(generate_results)
    return mock


# ----------------------------------------------------------------------
# Hierarchy and constants
# ----------------------------------------------------------------------
class DTPHierarchyTest(SimpleTestCase):
    def test_inherits_from_research_instrument_agent(self):
        self.assertTrue(issubclass(DTPAgent, ResearchInstrumentAgent))

    def test_artefact_kind(self):
        self.assertEqual(DTPAgent.artefact_kind, 'dtp_narrative')

    def test_model_name(self):
        self.assertEqual(DTPAgent.model_name, 'gemini-2.5-flash')


class DTPConstantsTest(SimpleTestCase):
    """Gemini-call parameters carry over from the Phase E DTP. The
    continuity thresholds do NOT: the redefined DTP ships no thresholds
    and no label (design proposal §7.4)."""

    def test_gemini_call_constants(self):
        self.assertEqual(DTP_THEME_TEMPERATURE, 0.3)
        self.assertEqual(DTP_THEME_MAX_TOKENS, 1000)
        self.assertEqual(DTP_NARRATIVE_TEMPERATURE, 0.4)
        self.assertEqual(DTP_NARRATIVE_MAX_TOKENS, 2000)
        self.assertEqual(DTP_REFLECTION_PROMPT_BUDGET, 400)

    def test_schema_tag(self):
        self.assertEqual(DTP_SCHEMA, 'dtp_dual_v1')

    def test_no_continuity_thresholds(self):
        """The redefinition removed the 0.85 / 0.70 thresholds; the
        module must not expose them (design proposal §7.4)."""
        import apps.agents.dtp as dtp_module
        self.assertFalse(hasattr(dtp_module, 'DTP_HIGH_THRESHOLD'))
        self.assertFalse(hasattr(dtp_module, 'DTP_MODERATE_THRESHOLD'))


# ----------------------------------------------------------------------
# Cosine similarity (pure function)
# ----------------------------------------------------------------------
class DTPCosineSimilarityTest(SimpleTestCase):
    """_cosine_similarity returns a rounded cosine and nothing else —
    no label, no bucketing (design proposal §7.4)."""

    @staticmethod
    def _vec_with_similarity(target):
        import math
        theta = math.acos(target)
        return [1.0, 0.0], [math.cos(theta), math.sin(theta)]

    def test_returns_cosine_similarity(self):
        v1, v2 = self._vec_with_similarity(0.90)
        self.assertAlmostEqual(DTPAgent._cosine_similarity(v1, v2), 0.90, places=4)

    def test_identical_vectors_score_one(self):
        vec = [0.1] * 16
        self.assertEqual(DTPAgent._cosine_similarity(vec, vec), 1.0)

    def test_similarity_rounded_to_4_decimals(self):
        v1, v2 = self._vec_with_similarity(0.5)
        result = DTPAgent._cosine_similarity(v1, v2)
        self.assertEqual(result, round(result, 4))


# ----------------------------------------------------------------------
# Theme-extraction prompt — unchanged from the Phase E DTP
# ----------------------------------------------------------------------
class DTPThemesPromptTest(SimpleTestCase):
    """The theme-extraction prompt is a generic two-reflection thematic
    extractor; it is unchanged, so the dtp_themes.txt fixture still
    holds."""

    def test_themes_prompt_matches_frozen_snapshot(self):
        expected = load_prompt_fixture('dtp_themes')
        actual = DTPAgent._build_themes_prompt(_VERTICAL, _CURRENT)
        self.assertEqual(actual, expected)

    def test_themes_prompt_layer0(self):
        prompt = DTPAgent._build_themes_prompt(_VERTICAL, _CURRENT)
        self.assertIn('PREVIOUS:', prompt)
        self.assertIn('CURRENT:', prompt)
        self.assertIn('{"increased": [], "decreased": [], "stable": []}', prompt)
        self.assertIn('Fill each array with 2-3 phrases of MAX 3 WORDS EACH.', prompt)

    def test_themes_prompt_sanitises_400_char_cap(self):
        long_text = 'x' * 600 + 'AFTER_CAP'
        prompt = DTPAgent._build_themes_prompt(long_text, _CURRENT)
        self.assertNotIn('AFTER_CAP', prompt)

    def test_themes_prompt_quote_and_newline_sanitisation(self):
        text = 'She said "AI is helpful"\nthen continued reflecting.'
        prompt = DTPAgent._build_themes_prompt(text, _CURRENT)
        self.assertIn("She said 'AI is helpful'", prompt)
        self.assertNotIn("'AI is helpful'\nthen", prompt)


# ----------------------------------------------------------------------
# Narrative prompt — the redefined structured dual-signal prompt
# ----------------------------------------------------------------------
class DTPNarrativePromptTest(SimpleTestCase):

    def test_narrative_prompt_matches_frozen_snapshot(self):
        expected = load_prompt_fixture('dtp_narrative')
        actual = DTPAgent._build_narrative_prompt(
            _FIXTURE_CURRENT_MODULE, _FIXTURE_SIGNALS,
        )
        self.assertEqual(actual, expected)

    def test_narrative_prompt_layer0(self):
        prompt = DTPAgent._build_narrative_prompt(
            _FIXTURE_CURRENT_MODULE, _FIXTURE_SIGNALS,
        )
        self.assertIn('Describe only what changed', prompt)
        self.assertIn('do not evaluate quality', prompt)
        self.assertIn('<synthesis>', prompt)
        self.assertIn('</synthesis>', prompt)
        self.assertIn('Across these modules, your reflection', prompt)
        self.assertIn('VERTICAL comparison', prompt)
        self.assertIn('TEMPORAL comparison', prompt)
        self.assertIn('current module (M8)', prompt)

    def test_narrative_prompt_temporal_only_omits_vertical_block(self):
        """With no VCS available (an Acquire module), the prompt has
        only the temporal block and only the temporal analysis tag."""
        signals = {'temporal': _FIXTURE_SIGNALS['temporal']}
        prompt = DTPAgent._build_narrative_prompt('M2', signals)
        self.assertNotIn('VERTICAL comparison', prompt)
        self.assertNotIn('<vertical_analysis>', prompt)
        self.assertIn('TEMPORAL comparison', prompt)
        self.assertIn('<temporal_analysis>', prompt)
        self.assertIn('<synthesis>', prompt)


# ----------------------------------------------------------------------
# Theme JSON repair
# ----------------------------------------------------------------------
class DTPThemeJsonRepairTest(SimpleTestCase):

    def test_clean_json_response_invoked_for_theme_step(self):
        from apps.agents.shared.json_repair import (
            clean_json_response as real_clean,
        )
        mock_client = _mock_llm([
            _gen_result('```json\n{"increased":[],"decreased":[],"stable":[]}\n```'),
            _gen_result(_NARRATIVE_RESPONSE),
        ])
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client), \
             patch('apps.agents.dtp.clean_json_response',
                   wraps=real_clean) as spy:
            DTPAgent()._do_generate(
                current_reflection_text=_CURRENT,
                current_module='M2',
                temporal_reflection_text=_TEMPORAL,
                temporal_module='M1',
            )
        spy.assert_called()

    def test_theme_json_repair_fallback_on_unbalanced_braces(self):
        truncated = '{"increased": ["focus"], "decreased": [], "stable":'
        mock_client = _mock_llm([_gen_result(truncated)])
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            themes = DTPAgent()._extract_themes(_TEMPORAL, _CURRENT)
        self.assertIn('increased', themes)
        self.assertIn('decreased', themes)
        self.assertIn('stable', themes)


# ----------------------------------------------------------------------
# Cost tracking — one cost event per Gemini sub-call
# ----------------------------------------------------------------------
class DTPCostTrackingTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('dtp_cost_user', password='pw')
        cls.module = Module.objects.create(
            code='AGDTPC', title='DTP cost test', description='t',
            order_index=990, unesco_aspect='ethics',
            proficiency_level='Deepen', is_published=True,
        )

    def _progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def _cost_events(self, cm):
        return [r for r in cm.records if r.getMessage() == 'agent.cost']

    def test_three_cost_events_for_dual_signal(self):
        """Both signals available: two theme calls + one narrative call."""
        progress = self._progress()
        mock_client = _mock_llm([
            _gen_result(_theme_json()),       # vertical themes
            _gen_result(_theme_json()),       # temporal themes
            _gen_result(_NARRATIVE_RESPONSE),  # narrative
        ])
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client), \
             self.assertLogs('agents.audit', level='INFO') as cm:
            DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                current_reflection_text=_CURRENT, current_module='M8',
                vertical_reflection_text=_VERTICAL, vertical_module='M3',
                temporal_reflection_text=_TEMPORAL, temporal_module='M7',
            )
        self.assertEqual(len(self._cost_events(cm)), 3)

    def test_two_cost_events_for_single_signal(self):
        """Only the temporal signal: one theme call + one narrative call."""
        progress = self._progress()
        mock_client = _mock_llm([
            _gen_result(_theme_json()),       # temporal themes
            _gen_result(_NARRATIVE_RESPONSE),  # narrative
        ])
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client), \
             self.assertLogs('agents.audit', level='INFO') as cm:
            DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                current_reflection_text=_CURRENT, current_module='M2',
                temporal_reflection_text=_TEMPORAL, temporal_module='M1',
            )
        self.assertEqual(len(self._cost_events(cm)), 2)


# ----------------------------------------------------------------------
# Failure modes
# ----------------------------------------------------------------------
class DTPFailureModesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('dtp_fail_user', password='pw')
        cls.module = Module.objects.create(
            code='AGDTPF', title='DTP fail test', description='t',
            order_index=991, unesco_aspect='ethics',
            proficiency_level='Deepen', is_published=True,
        )

    def _progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def test_current_embedding_failure_raises_and_rolls_back(self):
        """CP-9: if the current-reflection embed returns None,
        _do_generate raises so the atomic rolls back — reflection_dtp
        untouched, no provenance row."""
        mock_client = MagicMock()
        mock_client.embed.return_value = None

        progress = self._progress()
        progress.reflection_dtp = '__untouched__'
        progress.save(update_fields=['reflection_dtp'])
        before = AIArtefactProvenance.objects.count()

        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            with self.assertRaises(RuntimeError):
                DTPAgent().generate(
                    user=self.user, module=self.module,
                    save_target=progress, save_field='reflection_dtp',
                    current_reflection_text=_CURRENT, current_module='M8',
                    temporal_reflection_text=_TEMPORAL, temporal_module='M7',
                )

        progress.refresh_from_db()
        self.assertEqual(progress.reflection_dtp, '__untouched__')
        self.assertEqual(AIArtefactProvenance.objects.count(), before)

    def test_comparison_embedding_failure_raises(self):
        """If a comparison-reflection embed returns None, the call
        raises RuntimeError (atomic rollback)."""
        mock_client = MagicMock()
        # First embed (current) succeeds, second (comparison) fails.
        mock_client.embed.side_effect = [[0.1] * 768, None]

        progress = self._progress()
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            with self.assertRaises(RuntimeError):
                DTPAgent().generate(
                    user=self.user, module=self.module,
                    save_target=progress, save_field='reflection_dtp',
                    current_reflection_text=_CURRENT, current_module='M8',
                    temporal_reflection_text=_TEMPORAL, temporal_module='M7',
                )

    def test_theme_extraction_empty_default_on_gemini_none(self):
        """When a theme Gemini call returns None, that signal's themes
        default to empty and the composite still completes."""
        progress = self._progress()
        mock_client = _mock_llm([
            None,                              # temporal themes call fails
            _gen_result(_NARRATIVE_RESPONSE),  # narrative
        ])
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            result = DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                current_reflection_text=_CURRENT, current_module='M2',
                temporal_reflection_text=_TEMPORAL, temporal_module='M1',
            )
        themes = result['signals']['temporal']['themes']
        self.assertEqual(themes['increased_themes'], [])
        self.assertEqual(themes['decreased_themes'], [])
        self.assertEqual(themes['stable_themes'], [])

    def test_narrative_falls_back_when_gemini_returns_none(self):
        """When the narrative Gemini call returns None, the narrative
        falls back to the canned descriptive sentence."""
        progress = self._progress()
        mock_client = _mock_llm([
            _gen_result(_theme_json()),  # temporal themes
            None,                        # narrative call fails
        ])
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            result = DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                current_reflection_text=_CURRENT, current_module='M2',
                temporal_reflection_text=_TEMPORAL, temporal_module='M1',
            )
        self.assertEqual(result['narrative'], DTP_NARRATIVE_FALLBACK)


# ----------------------------------------------------------------------
# Composite shape, persistence and provenance
# ----------------------------------------------------------------------
class DTPCompositeShapeTest(TestCase):
    """Behaviour-identical with mocked Gemini: the dual-signal composite
    shape, JSON persistence and the single provenance row."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('dtp_e2e_user', password='pw')
        cls.module = Module.objects.create(
            code='AGDTPE', title='DTP end-to-end test', description='t',
            order_index=992, unesco_aspect='ai_foundations',
            proficiency_level='Deepen', is_published=True,
        )

    def _progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def test_dual_signal_composite_shape_and_persistence(self):
        progress = self._progress()
        mock_client = _mock_llm([
            _gen_result(_theme_json(increased=['ethical focus'])),    # vertical
            _gen_result(_theme_json(decreased=['novelty'])),          # temporal
            _gen_result(_NARRATIVE_RESPONSE),                         # narrative
        ])
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            result = DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                current_reflection_text=_CURRENT, current_module='M8',
                vertical_reflection_text=_VERTICAL, vertical_module='M3',
                temporal_reflection_text=_TEMPORAL, temporal_module='M7',
            )

        # Top-level composite shape.
        self.assertEqual(result['schema'], DTP_SCHEMA)
        self.assertEqual(result['current_module'], 'M8')
        self.assertEqual(result['narrative'], _SYNTHESIS_TEXT)
        self.assertEqual(sorted(result['signals'].keys()), ['temporal', 'vertical'])

        # Each signal carries comparison_module, similarity, themes.
        vertical = result['signals']['vertical']
        self.assertEqual(vertical['comparison_module'], 'M3')
        self.assertIsInstance(vertical['similarity'], float)
        self.assertEqual(
            sorted(vertical['themes'].keys()),
            ['decreased_themes', 'increased_themes', 'stable_themes'],
        )
        self.assertEqual(vertical['themes']['increased_themes'], ['ethical focus'])
        self.assertEqual(
            result['signals']['temporal']['comparison_module'], 'M7',
        )

        # Persistence: progress.reflection_dtp holds the JSON dump.
        progress.refresh_from_db()
        round_tripped = json.loads(progress.reflection_dtp)
        self.assertEqual(round_tripped['current_module'], 'M8')
        self.assertEqual(round_tripped['schema'], DTP_SCHEMA)

        # One provenance row, keyed by ('dtp_narrative', progress.pk).
        self.assertTrue(
            AIArtefactProvenance.objects.filter(
                artefact_kind='dtp_narrative',
                artefact_pk=str(progress.pk),
                user=self.user,
                model_name='gemini-2.5-flash',
            ).exists()
        )

    def test_temporal_only_composite_has_no_vertical_signal(self):
        """An Acquire module supplies only the temporal signal; the
        composite then carries no 'vertical' key (design proposal §5)."""
        progress = self._progress()
        mock_client = _mock_llm([
            _gen_result(_theme_json()),        # temporal themes
            _gen_result(_NARRATIVE_RESPONSE),  # narrative
        ])
        with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
            result = DTPAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp',
                current_reflection_text=_CURRENT, current_module='M2',
                temporal_reflection_text=_TEMPORAL, temporal_module='M1',
            )
        self.assertEqual(list(result['signals'].keys()), ['temporal'])
        self.assertNotIn('vertical', result['signals'])

    def test_provenance_idempotent_on_rerun(self):
        """Re-running generate() replaces the composite but the
        'dtp_narrative' provenance row stays a single row (CP-7)."""
        progress = self._progress()

        def _run():
            mock_client = _mock_llm([
                _gen_result(_theme_json()),
                _gen_result(_NARRATIVE_RESPONSE),
            ])
            with patch('apps.agents.dtp.get_llm_client', return_value=mock_client):
                DTPAgent().generate(
                    user=self.user, module=self.module,
                    save_target=progress, save_field='reflection_dtp',
                    current_reflection_text=_CURRENT, current_module='M2',
                    temporal_reflection_text=_TEMPORAL, temporal_module='M1',
                )

        _run()
        _run()
        self.assertEqual(
            AIArtefactProvenance.objects.filter(
                artefact_kind='dtp_narrative',
                artefact_pk=str(progress.pk),
            ).count(),
            1,
        )
