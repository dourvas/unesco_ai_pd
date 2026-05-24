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

    def test_all_three_stage_briefs_present(self):
        """G.2a Stage 1 (Look Back), G.2b Stage 2 (Look In), G.2c Stage 3
        (Look Forward)."""
        from apps.agents.epilogue_dialogue import _STAGE_BRIEF
        self.assertEqual(_STAGE_BRIEF[1]['name'], 'Look Back')
        self.assertEqual(_STAGE_BRIEF[2]['name'], 'Look In')
        self.assertEqual(_STAGE_BRIEF[3]['name'], 'Look Forward')
        self.assertNotIn(4, _STAGE_BRIEF)


class EpilogueDialogueGenerateBlockedTest(SimpleTestCase):

    def test_generate_raises_extract_only(self):
        with self.assertRaises(ValueError) as cm:
            EpilogueDialogueAgent().generate(user=None)
        self.assertIn('extract-only', str(cm.exception))


class EpilogueDialogueStageGuardTest(SimpleTestCase):

    def test_unimplemented_stage_raises(self):
        """Stages 1-3 are implemented; an out-of-range stage must fail
        loudly so a mis-wire never produces an off-spec turn."""
        with self.assertRaises(ValueError) as cm:
            EpilogueDialogueAgent().extract(stage=4, stage0_summary=_SUMMARY)
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
        # §24 — the old "Vary how you open" rule was loose and not
        # honoured in the live walkthrough (five consecutive replies
        # opened with "You [verb]..."). The new testable rule forbids
        # two consecutive replies with the same opening word, and the
        # three-shape system provides the move variety. Assert on the
        # new pattern.
        self.assertIn('Do NOT begin two consecutive replies', prompt)
        self.assertIn('that is yours to decide', prompt)
        # §24 three-shape closing default — the structural source of
        # non-interrogation behaviour. All three shape names must be
        # present in the prompt so the model can route per turn.
        self.assertIn('MIRROR', prompt)
        self.assertIn('OBSERVATION', prompt)
        self.assertIn('OPEN QUESTION', prompt)
        # §24 system-wide honour-uncertainty rule (Q3 dual-reviewer
        # convergence). Must fire across all phases, not only at close.
        self.assertIn('When the teacher expresses uncertainty', prompt)
        self.assertIn('IS a reflective position', prompt)
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
        # §24-revised Stage 1 continuing brief — references three-
        # shape system + observation priority + mirror with anchor
        # (NEVER bare) + honour-uncertainty cue.
        self.assertIn('stay with that rather than steering', prompt)
        self.assertIn('three shapes from the system prompt', prompt)
        self.assertIn('observation has priority over mirror', prompt)
        self.assertIn('never bare verbatim repetition', prompt)
        self.assertIn('Honour uncertainty', prompt)
        # §24 four worked examples — three shapes + one
        # uncertainty-handling Stage 0 pivot example. Each carries
        # an explicit shape label per §24.5.
        self.assertIn('a fitting reply would be:', prompt)
        self.assertIn('model its shape, never its content', prompt)
        self.assertIn('EXAMPLE — MIRROR', prompt)
        self.assertIn('EXAMPLE — OBSERVATION', prompt)
        self.assertIn('EXAMPLE — OPEN QUESTION', prompt)
        self.assertIn('EXAMPLE — UNCERTAINTY', prompt)
        # Specific phrases from the new examples (shape-confirming)
        self.assertIn('Performing reflection more than doing it', prompt)
        self.assertIn('A line runs through what you said', prompt)
        self.assertIn('Trying things — a turning point', prompt)
        self.assertIn('Not being sure is a true place', prompt)

    def test_stage2_opening_prompt_includes_juxtaposition(self):
        """G.2b: Stage 2 opening carries the pre-computed juxtaposition
        as a dedicated prompt section, framed as neutral data."""
        mock, captured = _capture_client()
        juxtaposition_text = (
            "On the recurring tension 'A vs B', the teacher positioned "
            "themselves as follows: M3 Strongly Left, M11 Strongly Right."
        )
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            EpilogueDialogueAgent().extract(
                stage=2, stage0_summary=_SUMMARY, history=[],
                juxtaposition=juxtaposition_text,
            )
        prompt = captured['prompt']
        self.assertIn('Look In', prompt)
        self.assertIn('THE JUXTAPOSITION TO SURFACE', prompt)
        self.assertIn('A vs B', prompt)
        self.assertIn('do not label it a contradiction', prompt.lower())
        # Stage 2 opening also uses the system stance.
        self.assertIn('never judge, grade, praise', prompt)

    def test_stage3_opening_prompt_includes_prior_stages(self):
        """G.2c: Stage 3 carries a prior_stages carry-forward of what
        the teacher said in Stages 1 and 2."""
        mock, captured = _capture_client()
        prior = (
            'In Stage 1 (Look Back) the teacher said: "I think I have '
            'been growing." In Stage 2 (Look In) the teacher said: "It '
            'was just an order, not a contradiction."'
        )
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            EpilogueDialogueAgent().extract(
                stage=3, stage0_summary=_SUMMARY, history=[],
                prior_stages=prior,
            )
        prompt = captured['prompt']
        self.assertIn('Look Forward', prompt)
        self.assertIn('EARLIER IN THIS EPILOGUE', prompt)
        self.assertIn('I think I have been growing', prompt)
        self.assertIn('just an order, not a contradiction', prompt)

    def test_stage2_continuing_omits_juxtaposition_section(self):
        """Continuing turns carry the juxtaposition through the history,
        not through a dedicated prompt section."""
        history = [
            {'role': 'assistant',
             'content': 'Two of your own moments sit here.'},
            {'role': 'teacher',
             'content': 'I think they are different things.'},
        ]
        mock, captured = _capture_client()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            EpilogueDialogueAgent().extract(
                stage=2, stage0_summary=_SUMMARY, history=history,
                juxtaposition='UNUSED on continuing turns',
            )
        prompt = captured['prompt']
        self.assertNotIn('THE JUXTAPOSITION TO SURFACE', prompt)
        self.assertIn('THE DIALOGUE SO FAR:', prompt)
        self.assertIn('Continue the Look In dialogue', prompt)

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

    def test_persona_guards_present(self):
        """The v2 §23 Aletheia persona enforcement adds four
        anti-anthropomorphisation rules to the system prompt:

          1. No self-naming as "Aletheia" inside the dialogue.
          2. No first-person language anywhere — emotional, cognitive,
             or perceptual variants all forbidden.
          3. No in-dialogue AI / model / system / chatbot self-reference.
          4. Prefer impersonal phrasing, with a concrete example
             showing the positive form ("a thread runs through what
             you said") versus the forbidden form ("I notice a
             thread").

        See PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2 §23.2 for the design
        rationale. The four guards are *additive* to the existing
        descriptive-non-evaluative stance — the §23.6 layer-2
        regression check guards against drift on the prior stance.
        """
        mock, captured = _capture_client()
        with patch('apps.agents.epilogue_dialogue.get_llm_client',
                   return_value=mock):
            EpilogueDialogueAgent().extract(
                stage=1, stage0_summary=_SUMMARY, history=[],
            )
        prompt = captured['prompt']
        # Guard 1: no self-naming.
        self.assertIn('do NOT introduce, name, or refer to', prompt)
        self.assertIn('by that name in the conversation', prompt)
        # Guard 2: no first-person, covering all three families.
        self.assertIn('Do not begin replies with "I"', prompt)
        self.assertIn('avoid first-person language anywhere', prompt)
        self.assertIn('emotional', prompt)
        self.assertIn('cognitive', prompt)
        self.assertIn('perceptual', prompt)
        # Concrete first-person examples named in the prompt so the
        # model has explicit targets to avoid.
        self.assertIn('"I feel"', prompt)
        self.assertIn('"I notice"', prompt)
        self.assertIn('"I see"', prompt)
        # Guard 3: no in-dialogue AI self-reference.
        self.assertIn('Do not refer to being an AI', prompt)
        self.assertIn('model, a system, an assistant, or a chatbot', prompt)
        # Guard 4: positive contrastive example — impersonal vs
        # self-reference — anchors the positive form for the model
        # to mimic.
        self.assertIn('a thread runs through what you said', prompt)
        self.assertIn('"I notice a thread"', prompt)
        # Existing descriptive-non-evaluative stance is preserved
        # (this prompt addition is append, not replace — §23.1).
        self.assertIn('never judge, grade, praise', prompt)
        self.assertIn('never open a reply by appraising', prompt)


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
