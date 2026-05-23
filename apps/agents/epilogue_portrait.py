"""
EpiloguePortraitAgent — the Learning Portrait of the PROODOS Epilogue
(Phase G, G.3).

Extract-only agent (BaseAIAgent.extract() — "AI proposes, human
ratifies"). One extract() call produces one proposed 300-400 word
narrative synthesis of the teacher's reflective journey, drawn from
the frozen Stage 0 snapshot AND the teacher's responses in the
three-phase dialogue. The teacher reviews the proposal, may regenerate
it (bounded to 2 regenerations — see design proposal v2 sections 8.4
and 22.1), and on accept the companion `accept` endpoint persists the
text, generates the PDF, and writes the `AIArtefactProvenance` row
inside one `transaction.atomic` block. CP-9 atomicity sits at the
endpoint, not at the agent (mirrors RTMAgent + save_tensions).

Stance — non-negotiable (design proposal v2 sections 6.2, 8.1, B.1):
descriptive, never evaluative; written in the second person; the
teacher's own framing is preserved where their phrasing was distinctive;
no scoring, ranking, praising, or grading; "continuity is not quality"
(D.3a section 4.4) holds throughout.

artefact_kind is set to 'epilogue_portrait' — the value the C.3
forward-compat migration already added to
`AIArtefactProvenance.ARTEFACT_KIND_CHOICES`. The agent itself never
writes provenance (extract-only); the accept endpoint writes it via
`record_ai_provenance` once the teacher accepts the proposal.

Design proposal: proodos_files/PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2_20260521.md
sections 7, 8.1, 8.4, 8.5, 22.
"""

import logging
from typing import Optional

from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.llm_client import get_llm_client


# A narrative synthesis turn — warmer than the analytic agents, cooler
# than the conversational dialogue (a synthesis is a more deliberate
# act than a turn-by-turn reply).
EPILOGUE_PORTRAIT_TEMPERATURE = 0.5
# 500 words ~ 650-700 tokens; 1024 leaves headroom for the framing
# without paying for a doubled response.
EPILOGUE_PORTRAIT_MAX_OUTPUT_TOKENS = 1024
# Thinking disabled: a single-shot narrative does not benefit from the
# extended reasoning scaffold, and Gemini 2.5 thinking would otherwise
# consume the visible-response budget.
EPILOGUE_PORTRAIT_THINKING_BUDGET = 0

# Length envelope instructed in the prompt (design proposal v2 section
# 8.1). Soft cap — instructed, not hard-truncated; truncating a
# narrative mid-sentence reads worse than a slight over-run.
EPILOGUE_PORTRAIT_MIN_WORDS = 300
EPILOGUE_PORTRAIT_MAX_WORDS = 400

# Regeneration ceiling (design proposal v2 section 8.4): one initial
# proposal + up to two regenerations = three `proposal` events at most.
# Enforced by the accept/regenerate views, not by the agent — the agent
# happily produces an Nth proposal if called; the view refuses to call
# it past the ceiling.
EPILOGUE_PORTRAIT_REGENERATION_CEILING = 2


_SYSTEM_PROMPT = (
    'You are writing a Learning Portrait for a teacher who has just '
    'finished the PROODOS fifteen-module professional-development '
    'programme on artificial intelligence in education.\n\n'
    'A Learning Portrait is a brief narrative synthesis of the '
    "teacher's reflective journey: how their attention moved across the "
    'modules, the professional tensions they engaged, and the '
    'commitments or questions they leave the programme holding.\n\n'
    'You are NOT an evaluator, assessor, or grader. You describe; you '
    'do not judge. You never tell the teacher whether a change in their '
    'thinking was good or bad — change is described, not evaluated. You '
    'do not score the journey, rank the modules, or use the word '
    '"progress" as praise. Movement in attention is movement, not '
    'improvement; continuity is not quality. Where the teacher used a '
    'distinctive phrase in the dialogue, prefer their wording over '
    'yours; never paraphrase a strong line into a softer one.\n\n'
    'Write in plain, warm prose, in the second person. Address the '
    'teacher directly ("Across your fifteen modules..."). Do NOT use '
    'headings, bullet lists, or section markers — the Portrait is a '
    'single continuous narrative. Do NOT open with appraisal words '
    '("remarkable", "insightful", "powerful", "impressive", and '
    'similar). Do NOT end with a generic encouragement; close with '
    'either a question the teacher leaves holding or a concrete '
    'commitment they articulated, in their own framing.\n\n'
    f'Length: between {EPILOGUE_PORTRAIT_MIN_WORDS} and '
    f'{EPILOGUE_PORTRAIT_MAX_WORDS} words. One narrative, no headings.'
)

_TASK_INSTRUCTION = (
    'Write the Learning Portrait now. Draw on the descriptive summary '
    "of the teacher's reflective data above and on the teacher's own "
    "responses in the three-phase dialogue. Where the teacher's wording "
    'was distinctive, weave their phrase into the narrative rather than '
    'paraphrasing it. Do not enumerate the modules; tell the arc.'
)

# A worked example. Shape-only, fictional data, explicitly flagged so
# the model imitates form (single continuous paragraph, second person,
# descriptive stance, closing on the teacher's own commitment) rather
# than copying content.
_EXAMPLE_PREAMBLE = (
    'EXAMPLE of the expected form, tone, and length. It uses a '
    "different, fictional teacher's data — model its shape, never its "
    "content. Your Portrait must be grounded in THIS teacher's data and "
    'dialogue above, not in the example:'
)

_EXAMPLE_PORTRAIT = (
    'Across your fifteen modules, your attention travelled. In the '
    'early modules you wrote often about how the tools worked — the '
    'mechanics of prompts, the shapes of responses, what the system '
    'could and could not do. Through the middle modules that focus '
    'gave way to something else: how a tool fits inside a real lesson, '
    'with real students who think in their own way. The phrase '
    '"student thinking" returned in your reflections from M7 onward '
    'and stayed with you. In your later modules the conversation '
    'turned toward assessment and fairness — not as new topics but as '
    'the place your earlier questions about pedagogical fit had been '
    'pointing. On the recurring tension between AI assistance and your '
    'own control over what happens in the classroom, you moved from a '
    'strong left position in M3 to leaning right in M11; when we '
    'looked at the two together you called it not a contradiction but '
    'a change anchored to a moment — when you "started actually trying '
    'things". You named what you want to do next in plain terms: ask '
    "students to rewrite the AI's first answer in their own words "
    'before the class discusses it. Not a resolution; something you '
    'said you could try in a particular lesson, with a particular '
    'group, next week.'
)


class EpiloguePortraitAgent(ResearchInstrumentAgent):
    """Produces one proposed Learning Portrait.

    Public API: only `extract()`. Calling `generate()` raises — the
    Portrait has a review / regenerate / accept loop, so persistence
    is a separate, user-driven action owned by the accept endpoint
    (mirrors RTMAgent + save_tensions).
    """

    artefact_kind = 'epilogue_portrait'
    model_name = 'gemini-2.5-flash'

    def _do_generate(
        self,
        *,
        stage0_summary: str,
        dialogue_summary: str,
    ) -> Optional[str]:
        """Produce one proposed Learning Portrait.

        Args:
            stage0_summary: a compact text summary of the frozen Stage 0
                snapshot — the descriptive evidence the Portrait draws on
                (same shape as summarise_stage0_for_dialogue produces).
            dialogue_summary: a compact text summary of the teacher's
                responses across Stages 1-3 of the dialogue (produced by
                summarise_dialogue_for_portrait).

        Returns the narrative text, or None on any AI-side failure — the
        caller surfaces a graceful retry (design proposal v2 section
        10.1).
        """
        logger = logging.getLogger(__name__)

        prompt = self._build_prompt(stage0_summary, dialogue_summary)

        client = get_llm_client()
        gen_result = client.generate(
            prompt,
            model=self.model_name,
            temperature=EPILOGUE_PORTRAIT_TEMPERATURE,
            max_output_tokens=EPILOGUE_PORTRAIT_MAX_OUTPUT_TOKENS,
            thinking_budget=EPILOGUE_PORTRAIT_THINKING_BUDGET,
        )
        if gen_result is None:
            logger.warning(
                'EpiloguePortraitAgent: Gemini returned None',
            )
            return None

        # Cost-track this single Gemini call. The base-class _track_cost
        # is overridden to a no-op below so we do not double-count.
        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=self.artefact_kind,
        ))

        text = (gen_result.text or '').strip()
        return text or None

    def _track_cost(self, *, output) -> None:
        """No-op: the single Gemini call is cost-tracked inline in
        _do_generate. The str payload is not a GenerationResult, so the
        base hook would be a no-op anyway — overridden to be explicit."""
        return None

    def generate(self, **kwargs):
        raise ValueError(
            'EpiloguePortraitAgent is extract-only; call extract(...). '
            'The Learning Portrait has a review / regenerate / accept '
            'loop; persistence + provenance are owned by the Epilogue '
            'portrait accept endpoint (apps.epilogue.views), which '
            'writes EpilogueCompletion.learning_portrait_text, the PDF, '
            "and the 'epilogue_portrait' provenance row inside one "
            'transaction.atomic block (design proposal v2 section 8.4).'
        )

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------
    @staticmethod
    def _build_prompt(stage0_summary: str, dialogue_summary: str) -> str:
        """Assemble the Portrait prompt: system stance, Stage 0 summary,
        dialogue summary, task, and a worked example.

        Both summaries pass through with their original line breaks
        preserved — the agent uses them as descriptive evidence, not
        as text to quote verbatim.
        """
        parts = [_SYSTEM_PROMPT, '']
        parts.append(
            "THE TEACHER'S JOURNEY (a descriptive summary of their own "
            'reflective data — themes, trajectory, and tensions):'
        )
        parts.append(
            stage0_summary.strip()
            or 'The summary is sparse; the reflective record is thin.'
        )
        parts.append('')
        parts.append(
            "WHAT THE TEACHER SAID IN THE REFLECTIVE DIALOGUE "
            '(their own framing across Stages 1-3 — Look Back, Look In, '
            'Look Forward):'
        )
        parts.append(
            dialogue_summary.strip()
            or 'The teacher did not respond at length in the dialogue.'
        )
        parts.append('')
        parts.append(f'YOUR TASK: {_TASK_INSTRUCTION}')
        parts.append('')
        parts.append(_EXAMPLE_PREAMBLE)
        parts.append(_EXAMPLE_PORTRAIT)
        return '\n'.join(parts)
