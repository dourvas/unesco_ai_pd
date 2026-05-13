"""RTMAgent parity tests vs the monolith extract_tensions.

Two-layer invariant from PHASE_E_DESIGN_PROPOSAL_v4 §5 (inherits v2):
  (1) Prompt-identical with rag_query_system.extract_tensions
  (2) Behaviour-identical given mocked Gemini output

Plus the contract checks specific to commit 3:
  - RTMAgent.generate() raises (extract-only contract)
  - RTMAgent.extract() does not write any provenance
  - RTMAgent uses shared.json_repair.clean_json_response
  - Validation rules from monolith validate_tensions preserved verbatim
  - 800-word truncation preserved
  - Layer-0 boilerplate: JSON-format markers, RULES text byte-identical
"""

import json
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase

from apps.agents.research import ResearchInstrumentAgent
from apps.agents.rtm import (
    RTM_MAX_REFLECTION_WORDS,
    RTMAgent,
    _normalise,
)
from apps.agents.shared.llm_client import GenerationResult
from apps.compliance.models import AIArtefactProvenance


# Representative inputs used across tests.
_REFLECTION = (
    "I tried using ChatGPT to help differentiate quadratic equations "
    "questions for my mixed-ability classroom. Some students wanted "
    "harder problems while others struggled with the basics. "
    "The AI generated reasonable variants but the assessment alignment "
    "to my learning objectives was inconsistent."
)
_CONTEXT = {'name': 'Maria', 'subject': 'Mathematics'}


class RTMHierarchyTest(SimpleTestCase):
    def test_inherits_from_research_instrument_agent(self):
        """RTMAgent participates in the research-instrument family —
        verified by isinstance for future dashboard filtering."""
        self.assertTrue(issubclass(RTMAgent, ResearchInstrumentAgent))

    def test_artefact_kind_is_rtm_position(self):
        """Proactive — even though extract() does not write provenance,
        the kind is declared for audit-log clarity + forward-compat."""
        self.assertEqual(RTMAgent.artefact_kind, 'rtm_position')

    def test_model_name_matches_phase_c_constant(self):
        """Same model identifier as PROVENANCE_MODEL_NAME in views.py
        and as RAGFeedbackAgent — single source of model truth."""
        self.assertEqual(RTMAgent.model_name, 'gemini-2.5-flash')


class RTMGenerateBlockedTest(SimpleTestCase):
    def test_generate_raises_with_extract_only_message(self):
        with self.assertRaises(ValueError) as cm:
            RTMAgent().generate(user=None)
        self.assertIn('extract-only', str(cm.exception))
        self.assertIn('save_tensions', str(cm.exception))


class RTMPromptParityTest(SimpleTestCase):
    """Layer-1 invariant: agent's prompt == monolith's prompt."""

    def test_build_prompt_matches_monolith_extract_tensions(self):
        """The monolith builds user_message inline inside
        extract_tensions and sends it as `contents=user_message`. We
        intercept that call and compare against the agent's
        _build_prompt output."""
        import rag_query_system as monolith

        captured = {}

        def fake_generate_content(**kwargs):
            captured['contents'] = kwargs.get('contents')
            # Return a valid-looking tension JSON so the monolith path
            # completes without raising.
            response = MagicMock()
            response.candidates = [MagicMock()]
            response.text = '{"tensions": []}'
            return response

        with patch.object(monolith, 'NEW_GENAI_API', True), \
             patch.object(monolith, 'client') as mock_client:
            mock_client.models.generate_content = fake_generate_content
            monolith.extract_tensions(_REFLECTION, _CONTEXT)

        monolith_prompt = captured['contents']
        agent_prompt = RTMAgent._build_prompt(_REFLECTION, _CONTEXT)
        self.assertEqual(monolith_prompt, agent_prompt)

    def test_build_prompt_layer0_boilerplate(self):
        """Layer-0 (post-commit-2 invariant): assert exact-string
        match for any boilerplate that's prone to escape-bug
        regression. The JSON-format markers, IMPORTANT RULES list
        and the empty-tensions fallback all qualify."""
        prompt = RTMAgent._build_prompt(_REFLECTION, _CONTEXT)
        self.assertIn('IMPORTANT RULES:', prompt)
        self.assertIn('Return EXACTLY 2 tensions, no more, no less.', prompt)
        self.assertIn('"grounding_quote": "Max 10 words from reflection"', prompt)
        self.assertIn(
            'If no meaningful tension is identifiable, return: {"tensions": []}',
            prompt,
        )

    def test_build_prompt_sanitises_double_quotes(self):
        reflection_with_quotes = 'She said "AI is helpful" yesterday.'
        prompt = RTMAgent._build_prompt(reflection_with_quotes, _CONTEXT)
        # The sanitiser converts " to ' in the reflection portion so
        # the JSON instructions later in the prompt are unambiguous.
        self.assertIn("She said 'AI is helpful' yesterday.", prompt)
        self.assertNotIn('"AI is helpful"', prompt)


class RTMValidationRulesTest(SimpleTestCase):
    """Each of the four validation rules from monolith validate_tensions
    has its own rejection test."""

    BASE = {
        'label': 'Differentiation vs alignment',
        'left_pole': 'support struggling students with simpler problems',
        'right_pole': 'challenge advanced students with harder variants',
        'grounding_quote': 'differentiate quadratic equations questions for mixed-ability',
    }

    def _payload(self, **overrides):
        t = dict(self.BASE)
        t.update(overrides)
        return {'tensions': [t]}

    def test_returns_none_when_tensions_key_missing(self):
        self.assertIsNone(
            RTMAgent.validate_tensions({}, _REFLECTION),
        )

    def test_returns_none_when_tensions_empty(self):
        self.assertIsNone(
            RTMAgent.validate_tensions({'tensions': []}, _REFLECTION),
        )

    def test_rule1_rejects_short_quote(self):
        # Less than 20 chars — rejected by rule 1.
        out = RTMAgent.validate_tensions(
            self._payload(grounding_quote='too short'),
            _REFLECTION,
        )
        self.assertIsNone(out)

    def test_rule2_rejects_ungrounded_quote(self):
        # Quote is long enough but contains no significant (>=4 char)
        # words that appear in the reflection — fabricated.
        out = RTMAgent.validate_tensions(
            self._payload(
                grounding_quote='completely unrelated fabricated rhetoric '
                                'nonexistent disconnected scattered',
            ),
            _REFLECTION,
        )
        self.assertIsNone(out)

    def test_rule3_rejects_long_label(self):
        out = RTMAgent.validate_tensions(
            self._payload(label='this is far too many words for a label here'),
            _REFLECTION,
        )
        self.assertIsNone(out)

    def test_rule4_rejects_short_pole(self):
        out = RTMAgent.validate_tensions(
            self._payload(left_pole='short'),
            _REFLECTION,
        )
        self.assertIsNone(out)

    def test_accepts_valid_tension(self):
        out = RTMAgent.validate_tensions(self._payload(), _REFLECTION)
        self.assertIsNotNone(out)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['label'], 'Differentiation vs alignment')

    def test_returns_at_most_two_tensions(self):
        # Monolith caps at 2 even if AI returns more.
        three = {'tensions': [dict(self.BASE) for _ in range(3)]}
        out = RTMAgent.validate_tensions(three, _REFLECTION)
        self.assertEqual(len(out), 2)


class RTMTruncationTest(SimpleTestCase):
    def test_long_reflection_truncated_in_do_generate(self):
        """800-word safety cap from rag_query_system preserved."""
        long_reflection = ' '.join(['word'] * (RTM_MAX_REFLECTION_WORDS + 100))
        captured = {}

        def fake_generate(prompt, **kw):
            captured['prompt'] = prompt
            return GenerationResult(
                text='{"tensions": []}', model='gemini-2.5-flash',
                tokens_estimate=10, cost_eur_estimate=0.0,
            )

        mock_client = MagicMock()
        mock_client.generate.side_effect = fake_generate
        with patch('apps.agents.rtm.get_llm_client', return_value=mock_client):
            RTMAgent().extract(
                reflection_text=long_reflection,
                teacher_context=_CONTEXT,
            )

        # The captured prompt embeds the truncated reflection — count
        # the 'word ' occurrences in the reflection-text portion.
        # Cap is 800 words. Allow margin for the literal 'word'
        # appearing in boilerplate (e.g. "max 6 words"); the pre-
        # truncation reflection had 900 occurrences.
        word_count = captured['prompt'].count('word')
        self.assertLess(word_count, 850)


class RTMJsonRepairContractTest(SimpleTestCase):
    """Verify RTMAgent threads Gemini output through
    apps.agents.shared.json_repair.clean_json_response — the shared
    helper that lives in commit-1 scaffolding and is used by RTM here
    + DTP in commit 5."""

    def test_clean_json_response_invoked_on_raw_text(self):
        # Patch at the import site (apps.agents.rtm.clean_json_response),
        # NOT at the source module (apps.agents.shared.json_repair). RTM
        # binds the name at import time, so patching the source has no
        # effect on the already-resolved reference.
        from apps.agents.shared.json_repair import (
            clean_json_response as real_clean,
        )

        mock_client = MagicMock()
        mock_client.generate.return_value = GenerationResult(
            text='```json\n{"tensions": []}\n```',
            model='gemini-2.5-flash', tokens_estimate=10, cost_eur_estimate=0.0,
        )
        with patch('apps.agents.rtm.get_llm_client', return_value=mock_client), \
             patch('apps.agents.rtm.clean_json_response',
                   wraps=real_clean) as spy:
            RTMAgent().extract(
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )
        # Verify the shared helper actually got called — confirms RTM
        # does not carry its own private copy of JSON repair logic.
        spy.assert_called()


class RTMExtractEndToEndTest(TestCase):
    """Behaviour-identical with mocked Gemini: same parsed tensions,
    no provenance row, audit log emits extract.start + extract.complete
    + cost."""

    def _mock_gemini_with(self, text):
        mock = MagicMock()
        mock.generate.return_value = GenerationResult(
            text=text, model='gemini-2.5-flash',
            tokens_estimate=100, cost_eur_estimate=0.0000279,
        )
        return mock

    def test_extract_returns_validated_tensions(self):
        valid_json = json.dumps({
            'tensions': [
                {
                    'label': 'Personalised feedback vs scale',
                    'left_pole': 'tailored feedback to individual students',
                    'right_pole': 'automated feedback at classroom scale',
                    'grounding_quote': (
                        'differentiate quadratic equations questions for mixed-ability'
                    ),
                },
                {
                    'label': 'AI assistance vs pedagogical control',
                    'left_pole': 'leverage AI to save preparation time',
                    'right_pole': 'preserve direct pedagogical judgement',
                    'grounding_quote': (
                        'assessment alignment to my learning objectives was inconsistent'
                    ),
                },
            ]
        })
        mock_client = self._mock_gemini_with(valid_json)

        with patch('apps.agents.rtm.get_llm_client', return_value=mock_client):
            tensions = RTMAgent().extract(
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )

        self.assertIsNotNone(tensions)
        self.assertEqual(len(tensions), 2)
        self.assertEqual(tensions[0]['label'], 'Personalised feedback vs scale')

    def test_extract_writes_no_provenance(self):
        valid_json = json.dumps({'tensions': []})
        mock_client = self._mock_gemini_with(valid_json)

        before = AIArtefactProvenance.objects.count()
        with patch('apps.agents.rtm.get_llm_client', return_value=mock_client):
            RTMAgent().extract(
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )
        self.assertEqual(
            AIArtefactProvenance.objects.count(), before,
            'RTM extract is ephemeral — provenance is written by '
            'save_tensions, not by the extraction agent.',
        )

    def test_extract_returns_none_on_json_parse_failure(self):
        mock_client = self._mock_gemini_with('this is not json at all')
        with patch('apps.agents.rtm.get_llm_client', return_value=mock_client):
            tensions = RTMAgent().extract(
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )
        self.assertIsNone(tensions)

    def test_extract_returns_none_when_llm_returns_none(self):
        mock_client = MagicMock()
        mock_client.generate.return_value = None
        with patch('apps.agents.rtm.get_llm_client', return_value=mock_client):
            tensions = RTMAgent().extract(
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )
        self.assertIsNone(tensions)

    def test_extract_emits_audit_events(self):
        mock_client = self._mock_gemini_with('{"tensions": []}')
        with patch('apps.agents.rtm.get_llm_client', return_value=mock_client), \
             self.assertLogs('agents.audit', level='INFO') as cm:
            RTMAgent().extract(
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )
        events = [r.getMessage() for r in cm.records]
        self.assertIn('agent.extract.start', events)
        self.assertIn('agent.extract.complete', events)
        # Cost is logged inline in _do_generate per the commit comment.
        self.assertIn('agent.cost', events)


class RTMNormaliseHelperTest(SimpleTestCase):
    """Mirror the monolith validate_tensions inline `normalize` so the
    grounding-rule (rule 2) behaves identically."""

    def test_lowercases(self):
        self.assertEqual(_normalise('Hello World'), 'hello world')

    def test_collapses_whitespace(self):
        self.assertEqual(_normalise('a   b\t c\n'), 'a b c')

    def test_normalises_smart_quotes(self):
        # Curly apostrophe -> straight apostrophe
        self.assertEqual(_normalise('don’t'), "don't")

    def test_normalises_em_and_en_dashes(self):
        self.assertEqual(_normalise('long—dash'), 'long-dash')
        self.assertEqual(_normalise('short–dash'), 'short-dash')
