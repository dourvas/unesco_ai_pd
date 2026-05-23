"""Tests for EpiloguePortraitAgent (Phase G, G.3a — Learning Portrait).

Covers:
  - hierarchy / contract (ResearchInstrumentAgent, extract-only,
    artefact_kind = 'epilogue_portrait')
  - prompt construction — the descriptive stance, the Stage 0 summary,
    the dialogue summary, the worked example
  - extract() behaviour with mocked Gemini: text returned, None on
    failure, no provenance written, cost tracking via cost_tracker

The LLM is mocked throughout via patching
`apps.agents.epilogue_portrait.get_llm_client` — no live Gemini call.
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase

from apps.agents.epilogue_portrait import (
    EPILOGUE_PORTRAIT_MAX_OUTPUT_TOKENS,
    EPILOGUE_PORTRAIT_MAX_WORDS,
    EPILOGUE_PORTRAIT_MIN_WORDS,
    EPILOGUE_PORTRAIT_REGENERATION_CEILING,
    EPILOGUE_PORTRAIT_TEMPERATURE,
    EPILOGUE_PORTRAIT_THINKING_BUDGET,
    EpiloguePortraitAgent,
)
from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.llm_client import GenerationResult
from apps.compliance.models import AIArtefactProvenance


_STAGE0_SUMMARY = (
    "The teacher completed 15 modules and wrote 15 reflections. "
    "Themes that became more prominent later: student thinking, "
    "assessment, fairness. Themes consistent throughout: teacher "
    "oversight. Themes prominent early and faded later: tool mechanics."
)
_DIALOGUE_SUMMARY = (
    'In Stage 1 (Look Back):\n'
    '  The teacher said: "By M10 I felt like I was performing '
    'reflection more than doing it."\n'
    'In Stage 2 (Look In):\n'
    '  The juxtaposition the teacher responded to: "On the recurring '
    'tension between AI assistance and pedagogical control..."\n'
    '  The teacher said: "It is not a contradiction, it is a change '
    'anchored to a moment."\n'
    'In Stage 3 (Look Forward):\n'
    "  The teacher said: \"I want to ask students to rewrite the AI's "
    'first answer in their own words before we discuss it."'
)
_PORTRAIT_TEXT = (
    'Across your fifteen modules, your attention travelled. Early on '
    'you wrote about how the tools worked; later your reflections '
    'turned to how those tools fit a real lesson. You named one '
    'moment plainly: by M10 you felt you were performing reflection '
    'more than doing it. When we looked at the tension between AI '
    'assistance and your own pedagogical control across the modules, '
    'you called what you saw not a contradiction but a change '
    'anchored to a moment. You leave the programme holding one '
    "concrete step: to ask students to rewrite the AI's first answer "
    'in their own words before the class discusses it.'
)


def _capture_client(response_text=_PORTRAIT_TEXT):
    """A mock LLM client whose generate() records its prompt + kwargs
    and returns a canned GenerationResult."""
    captured = {}

    def fake_generate(prompt, **kw):
        captured['prompt'] = prompt
        captured['kw'] = kw
        return GenerationResult(
            text=response_text, model='gemini-2.5-flash',
            tokens_estimate=550, cost_eur_estimate=0.000153,
        )

    mock = MagicMock()
    mock.generate.side_effect = fake_generate
    return mock, captured


class EpiloguePortraitHierarchyTest(SimpleTestCase):

    def test_inherits_from_research_instrument_agent(self):
        self.assertTrue(
            issubclass(EpiloguePortraitAgent, ResearchInstrumentAgent),
        )

    def test_model_name_is_gemini_flash(self):
        self.assertEqual(
            EpiloguePortraitAgent.model_name, 'gemini-2.5-flash',
        )

    def test_artefact_kind_is_epilogue_portrait(self):
        """The C.3 forward-compat migration already added this choice;
        the agent must use it verbatim so the accept endpoint's
        provenance write does not raise."""
        self.assertEqual(
            EpiloguePortraitAgent.artefact_kind, 'epilogue_portrait',
        )

    def test_artefact_kind_is_a_valid_provenance_choice(self):
        """Belt-and-braces guard: the constant must be one of the
        choices the AIArtefactProvenance model accepts."""
        valid = {kind for kind, _ in AIArtefactProvenance.ARTEFACT_KIND_CHOICES}
        self.assertIn(EpiloguePortraitAgent.artefact_kind, valid)


class EpiloguePortraitGenerateBlockedTest(SimpleTestCase):

    def test_generate_raises_extract_only(self):
        with self.assertRaises(ValueError) as cm:
            EpiloguePortraitAgent().generate(user=None)
        self.assertIn('extract-only', str(cm.exception))
        # The error message points the developer at the accept endpoint
        # so the persistence path is not invisible.
        self.assertIn('accept', str(cm.exception).lower())


class EpiloguePortraitConstantsTest(SimpleTestCase):

    def test_length_envelope_matches_proposal(self):
        """Design proposal v2 section 8.1 specifies 300-400 words."""
        self.assertEqual(EPILOGUE_PORTRAIT_MIN_WORDS, 300)
        self.assertEqual(EPILOGUE_PORTRAIT_MAX_WORDS, 400)

    def test_regeneration_ceiling_is_two(self):
        """Design proposal v2 section 8.4 / 22.1 bound regenerations
        to 2 (one initial proposal + up to two regenerations)."""
        self.assertEqual(EPILOGUE_PORTRAIT_REGENERATION_CEILING, 2)


class EpiloguePortraitPromptTest(SimpleTestCase):

    def test_prompt_carries_stance_summary_dialogue_task_example(self):
        mock, captured = _capture_client()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            EpiloguePortraitAgent().extract(
                stage0_summary=_STAGE0_SUMMARY,
                dialogue_summary=_DIALOGUE_SUMMARY,
            )
        prompt = captured['prompt']
        # The descriptive, non-evaluative stance — same family of
        # guards as the dialogue agent (B.1 / D.3a 4.4).
        self.assertIn('You describe; you do not judge', prompt)
        self.assertIn('continuity is not quality', prompt)
        self.assertIn('movement, not improvement', prompt)
        # Length envelope is instructed, not just enforced post-hoc.
        self.assertIn('300', prompt)
        self.assertIn('400', prompt)
        # No headings / bullets / appraisal openers / generic closes.
        self.assertIn('no headings', prompt)
        self.assertIn('appraisal', prompt)
        # The teacher's data and dialogue land in named blocks.
        self.assertIn("THE TEACHER'S JOURNEY", prompt)
        self.assertIn('THE TEACHER SAID IN THE REFLECTIVE DIALOGUE', prompt)
        # The Stage 0 summary and dialogue summary are both included.
        self.assertIn('student thinking', prompt)
        self.assertIn('change anchored to a moment', prompt)
        # Worked example explicitly flagged as shape-only.
        self.assertIn('EXAMPLE', prompt)
        self.assertIn('never its content', prompt)

    def test_prompt_uses_configured_gemini_params(self):
        mock, captured = _capture_client()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            EpiloguePortraitAgent().extract(
                stage0_summary=_STAGE0_SUMMARY,
                dialogue_summary=_DIALOGUE_SUMMARY,
            )
        kw = captured['kw']
        self.assertEqual(kw['model'], 'gemini-2.5-flash')
        self.assertEqual(kw['temperature'], EPILOGUE_PORTRAIT_TEMPERATURE)
        self.assertEqual(
            kw['max_output_tokens'], EPILOGUE_PORTRAIT_MAX_OUTPUT_TOKENS,
        )
        self.assertEqual(
            kw['thinking_budget'], EPILOGUE_PORTRAIT_THINKING_BUDGET,
        )

    def test_empty_stage0_summary_renders_graceful_placeholder(self):
        """A teacher with a thin reflective record should still
        produce a runnable prompt — the agent inserts a neutral
        sentence rather than passing an empty block to Gemini."""
        mock, captured = _capture_client()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            EpiloguePortraitAgent().extract(
                stage0_summary='',
                dialogue_summary=_DIALOGUE_SUMMARY,
            )
        self.assertIn('reflective record is thin', captured['prompt'])

    def test_empty_dialogue_summary_renders_graceful_placeholder(self):
        """Defensive: if the dialogue was somehow empty (should not
        happen post-Stage 3, but possible in edge cases), the prompt
        still composes without falling back to silence."""
        mock, captured = _capture_client()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            EpiloguePortraitAgent().extract(
                stage0_summary=_STAGE0_SUMMARY,
                dialogue_summary='',
            )
        self.assertIn(
            'did not respond at length',
            captured['prompt'],
        )


class EpiloguePortraitExtractTest(TestCase):

    def test_extract_returns_text_on_success(self):
        mock, _ = _capture_client()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            result = EpiloguePortraitAgent().extract(
                stage0_summary=_STAGE0_SUMMARY,
                dialogue_summary=_DIALOGUE_SUMMARY,
            )
        self.assertEqual(result, _PORTRAIT_TEXT.strip())

    def test_extract_returns_none_when_gemini_returns_none(self):
        mock = MagicMock()
        mock.generate.return_value = None
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            result = EpiloguePortraitAgent().extract(
                stage0_summary=_STAGE0_SUMMARY,
                dialogue_summary=_DIALOGUE_SUMMARY,
            )
        self.assertIsNone(result)

    def test_extract_returns_none_when_gemini_returns_empty_text(self):
        """Empty / whitespace-only Gemini output is treated as failure
        so the caller cannot accidentally persist a blank Portrait."""
        mock = MagicMock()
        mock.generate.return_value = GenerationResult(
            text='   ', model='gemini-2.5-flash',
            tokens_estimate=0, cost_eur_estimate=0.0,
        )
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            result = EpiloguePortraitAgent().extract(
                stage0_summary=_STAGE0_SUMMARY,
                dialogue_summary=_DIALOGUE_SUMMARY,
            )
        self.assertIsNone(result)

    def test_extract_does_not_write_provenance(self):
        """Extract-only contract: provenance is written by the accept
        endpoint, not by the agent."""
        mock, _ = _capture_client()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            EpiloguePortraitAgent().extract(
                stage0_summary=_STAGE0_SUMMARY,
                dialogue_summary=_DIALOGUE_SUMMARY,
            )
        self.assertFalse(
            AIArtefactProvenance.objects.filter(
                artefact_kind='epilogue_portrait',
            ).exists()
        )

    def test_extract_tracks_cost_for_the_one_gemini_call(self):
        """One extract() call = one Gemini call = one cost record.

        Patches the local `track_cost` import in epilogue_portrait
        (the agent does `from cost_tracker import track as
        track_cost`), so patching the source module would miss the
        binding. Same approach the RTM tests use.
        """
        mock, _ = _capture_client()
        with patch('apps.agents.epilogue_portrait.get_llm_client',
                   return_value=mock):
            with patch('apps.agents.epilogue_portrait.track_cost') as tracked:
                EpiloguePortraitAgent().extract(
                    stage0_summary=_STAGE0_SUMMARY,
                    dialogue_summary=_DIALOGUE_SUMMARY,
                )
        kinds = [
            call.args[0].artefact_kind
            for call in tracked.call_args_list
        ]
        self.assertIn('epilogue_portrait', kinds)
        self.assertEqual(tracked.call_count, 1)
