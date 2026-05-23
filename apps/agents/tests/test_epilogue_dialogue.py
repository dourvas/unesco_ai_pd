"""Tests for EpilogueDialogueAgent (Phase G, G.2a — Stage 1, Look Back).

Covers:
  - hierarchy / contract (ResearchInstrumentAgent, extract-only)
  - the stage guard (unimplemented stages raise)
  - prompt construction — the descriptive stance, the Stage 0 summary,
    the history, and the per-turn task
  - extract() behaviour with mocked Gemini: turn returned, None on
    failure, no provenance written, audit + cost events emitted

The LLM is mocked throughout via patching
`apps.agents.epilogue_dialogue.get_llm_client` — no live Gemini call.
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase

from apps.agents.epilogue_dialogue import (
    EPILOGUE_DIALOGUE_MAX_OUTPUT_TOKENS,
    EPILOGUE_DIALOGUE_TEMPERATURE,
    EPILOGUE_DIALOGUE_THINKING_BUDGET,
    EpilogueDialogueAgent,
)
from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.llm_client import GenerationResult
from apps.compliance.models import AIArtefactProvenance


_SUMMARY = (
    "Across fifteen modules the teacher's reflective writing moved from "
    "LLM mechanics toward pedagogical fit and learning impact. Teacher "
    "oversight recurred throughout. They positioned themselves on "
    "twenty-two professional tensions."
)
_TURN_TEXT = (
    'Looking back, your reflections seem to have shifted from how the '
    'tools work toward how they fit your teaching. What stands out to '
    'you about that move?'
)


def _capture_client(response_text=_TURN_TEXT):
    """A mock LLM client whose generate() records its prompt + kwargs
    and returns a canned GenerationResult."""
    captured = {}

    def fake_generate(prompt, **kw):
        captured['prompt'] = prompt
        captured['kw'] = kw
        return GenerationResult(
            text=response_text, model='gemini-2.5-flash',
            tokens_estimate=60, cost_eur_estimate=0.0000167,
        )

    mock = MagicMock()
    mock.generate.side_effect = fake_generate
    return mock, captured


class EpilogueDialogueHierarchyTest(SimpleTestCase):

    def test_inherits_from_research_instrument_agent(self):
        self.assertTrue(
            issubclass(EpilogueDialogueAgent, ResearchInstrumentAgent),
        )

    def test_model_name_is_gemini_flash(self):
        self.assertEqual(EpilogueDialogueAgent.model_name, 'gemini-2.5-flash')


class EpilogueDialogueGenerateBlockedTest(SimpleTestCase):

    def test_generate_raises_extract_only(self):
        with self.assertRaises(ValueError) as cm:
            EpilogueDialogueAgent().generate(user=None)
        self.assertIn('extract-only', str(cm.exception))


class EpilogueDialogueStageGuardTest(SimpleTestCase):

    def test_unimplemented_stage_raises(self):
        """Stages 2 / 3 land in G.2b / G.2c — until then a request for
        them must fail loudly, not produce an off-spec turn."""
        with self.assertRaises(ValueError) as cm:
            EpilogueDialogueAgent().extract(stage=2, stage0_summary=_SUMMARY)
        self.assertIn('not implemented', str(cm.exception))


class EpilogueDialoguePromptTest(SimpleTestCase):

    def test_opening_prompt_carries_stance_summary_and_task(self):
        mock, captured = _capture_client()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            EpilogueDialogueAgent().extract(
                stage=1, stage0_summary=_SUMMARY, history=[],
            )
        prompt = captured['prompt']
        # The descriptive, non-evaluative stance (B.1 / D.3a 4.4),
        # including the explicit no-appraisal-opener rule, the opener
        # variety rule, and the explicit evaluation-refusal rule.
        self.assertIn('never judge, grade, praise', prompt)
        self.assertIn('never open a reply by appraising', prompt)
        self.assertIn('Vary how you open', prompt)
        self.assertIn('that is yours to decide', prompt)
        # The phase and the teacher's own data.
        self.assertIn('Look Back', prompt)
        self.assertIn('pedagogical fit', prompt)
        # The opening task (history empty -> opening, not continuing).
        self.assertIn('opening of the Look Back phase', prompt)
        self.assertNotIn('THE DIALOGUE SO FAR', prompt)
        # A worked example anchors the model's output shape, flagged
        # explicitly as shape-only so it is never copied.
        self.assertIn('EXAMPLE of the expected form', prompt)
        self.assertIn('model its shape, never its content', prompt)
        self.assertIn('where your attention travelled', prompt)

    def test_continuing_prompt_carries_history(self):
        history = [
            {'role': 'assistant', 'content': 'An opening synthesis.'},
            {'role': 'teacher',
             'content': 'My view on oversight changed at M6.'},
        ]
        mock, captured = _capture_client()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            EpilogueDialogueAgent().extract(
                stage=1, stage0_summary=_SUMMARY, history=history,
            )
        prompt = captured['prompt']
        self.assertIn('THE DIALOGUE SO FAR:', prompt)
        self.assertIn('My view on oversight changed at M6.', prompt)
        self.assertIn('Teacher: My view on oversight', prompt)
        self.assertIn('Continue the Look Back dialogue', prompt)
        # Refinement (post-sample-review): stay with what the teacher
        # signalled as significant, and vary the move turn to turn
        # rather than repeating the connect-themes question.
        self.assertIn('stay with that rather than steering', prompt)
        self.assertIn('rather than repeatedly asking them to connect themes',
                      prompt)
        # The continuing turn carries two worked teacher-message ->
        # reply examples with distinct openers (varied shape), flagged
        # shape-only.
        self.assertIn('a fitting reply would be:', prompt)
        self.assertIn('model its shape, never its content', prompt)
        self.assertIn('A line runs through what you said', prompt)
        self.assertIn('Stay with that for a moment', prompt)

    def test_generate_called_with_thinking_disabled(self):
        """A short dialogue turn disables Gemini thinking so the whole
        token budget is available for the visible reply."""
        mock, captured = _capture_client()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            EpilogueDialogueAgent().extract(
                stage=1, stage0_summary=_SUMMARY, history=[],
            )
        kw = captured['kw']
        self.assertEqual(kw['thinking_budget'], EPILOGUE_DIALOGUE_THINKING_BUDGET)
        self.assertEqual(kw['temperature'], EPILOGUE_DIALOGUE_TEMPERATURE)
        self.assertEqual(
            kw['max_output_tokens'], EPILOGUE_DIALOGUE_MAX_OUTPUT_TOKENS,
        )


class EpilogueDialogueExtractTest(TestCase):

    def test_extract_returns_turn_text(self):
        mock, _ = _capture_client()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            turn = EpilogueDialogueAgent().extract(
                stage=1, stage0_summary=_SUMMARY, history=[],
            )
        self.assertEqual(turn, _TURN_TEXT)

    def test_extract_returns_none_when_llm_returns_none(self):
        mock = MagicMock()
        mock.generate.return_value = None
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            turn = EpilogueDialogueAgent().extract(
                stage=1, stage0_summary=_SUMMARY, history=[],
            )
        self.assertIsNone(turn)

    def test_extract_writes_no_provenance(self):
        mock, _ = _capture_client()
        before = AIArtefactProvenance.objects.count()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            EpilogueDialogueAgent().extract(
                stage=1, stage0_summary=_SUMMARY, history=[],
            )
        self.assertEqual(
            AIArtefactProvenance.objects.count(), before,
            'The dialogue turn is ephemeral — no provenance row is '
            'written by the agent (design proposal v2 section 6.5).',
        )

    def test_extract_emits_audit_and_cost_events(self):
        mock, _ = _capture_client()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock), \
             self.assertLogs('agents.audit', level='INFO') as cm:
            EpilogueDialogueAgent().extract(
                stage=1, stage0_summary=_SUMMARY, history=[],
            )
        events = [r.getMessage() for r in cm.records]
        self.assertIn('agent.extract.start', events)
        self.assertIn('agent.extract.complete', events)
        self.assertIn('agent.cost', events)


class EpilogueDialogueDedupeTest(SimpleTestCase):
    """Defensive trimming of a Gemini response that duplicates itself.

    Observed live on 2026-05-23 during the §20 sample-review: Gemini
    occasionally returns a reply whose sentences are repeated in order.
    The agent must trim the duplicate so the teacher sees one copy.
    """

    def test_dedupe_trims_doubled_sentences(self):
        from apps.agents.epilogue_dialogue import _dedupe_doubled_response
        doubled = (
            'You are noticing the shift. '
            'What stands out to you most? '
            'You are noticing the shift. '
            'What stands out to you most?'
        )
        self.assertEqual(
            _dedupe_doubled_response(doubled),
            'You are noticing the shift. What stands out to you most?',
        )

    def test_dedupe_passes_through_normal_text(self):
        from apps.agents.epilogue_dialogue import _dedupe_doubled_response
        normal = 'You are noticing the shift. What stands out to you most?'
        self.assertEqual(_dedupe_doubled_response(normal), normal)

    def test_dedupe_passes_through_odd_sentence_count(self):
        from apps.agents.epilogue_dialogue import _dedupe_doubled_response
        odd = 'One. Two. Three.'
        self.assertEqual(_dedupe_doubled_response(odd), odd)

    def test_dedupe_passes_through_when_halves_differ(self):
        from apps.agents.epilogue_dialogue import _dedupe_doubled_response
        four_different = 'One thing. Two things. Three things. Four things.'
        self.assertEqual(_dedupe_doubled_response(four_different), four_different)

    def test_extract_returns_trimmed_turn_when_gemini_doubles(self):
        doubled = (
            'You are noticing the shift. '
            'What stands out to you most? '
            'You are noticing the shift. '
            'What stands out to you most?'
        )
        mock, _ = _capture_client(response_text=doubled)
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            turn = EpilogueDialogueAgent().extract(
                stage=1, stage0_summary=_SUMMARY, history=[],
            )
        self.assertEqual(
            turn,
            'You are noticing the shift. What stands out to you most?',
        )
