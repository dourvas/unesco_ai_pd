"""
XAIAgent — natural-language explanation of the DTP's output (Phase D.3b).

The first concrete ServiceAgent. It does not operate on a teacher's
reflection; it operates on the output of another agent — the redefined
DTP's composite — and explains, in domain-driven natural language, why
that teacher's developmental signal looks the way it does.

Design and rationale:
proodos_files/DTP_XAI_NARRATIVE_DESIGN_PROPOSAL_v1_20260519.md.

Two governing principles
------------------------
Explanation faithfulness (design proposal §4)
    The agent explains the DTP composite and nothing else. Its only
    inputs are the stored composite and the UNESCO competency-aspect
    label of the current module (a fact about the module, not a
    re-interpretation of the reflection). It never re-reads the
    teacher's reflection text. An explanation untethered from what the
    DTP computed would be an over-inference (Guo et al., 2024).

Domain-driven explanation (design proposal §5.2)
    The explanation speaks in UNESCO-competency and pedagogical terms,
    not in cosine-similarity numbers or embedding mechanics. The raw
    similarity value is therefore deliberately NOT fed to the prompt —
    only the thematic shifts, which are the explainable substance.
    Domain-driven explanations outperform data-driven ones for teacher
    understandability and trust (Feldman-Maggor et al., 2025).

The explanation also reframes a theme appearing less as a movement of
reflective attention — not a regression or a loss of competence
(continuity is not quality — §4.4 of the DTP redefinition proposal).

Agent contract
--------------
  - artefact_kind = 'xai_narrative'; generate() persists the
    explanation to UserModuleProgress.reflection_dtp_xai and writes one
    'xai_narrative' provenance row, atomically (CP-9). Default _persist
    and _record_provenance suffice — the explanation is plain text and
    there is a single provenance row.
  - The single Gemini call records its own cost event inline;
    _track_cost is overridden to a no-op (as in DTPAgent).
  - On Gemini failure the explanation degrades to a safe, non-evaluative
    fallback sentence; generate() still succeeds.
"""

import logging
import re

from apps.agents.service import ServiceAgent
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.llm_client import get_llm_client


XAI_TEMPERATURE = 0.4
XAI_MAX_TOKENS = 2000

# Safe, non-evaluative fallback used when the Gemini call fails or
# returns nothing. It is itself a valid user-facing sentence.
XAI_FALLBACK = (
    'This explanation describes which themes your reflection brought '
    'into focus and which moved to the background between the modules '
    'compared. A theme receiving less emphasis is a shift of attention, '
    'not a decline.'
)


class XAIAgent(ServiceAgent):
    """Explains a teacher's DTP composite in domain-driven language.

    Public API: generate() — persists the explanation to
    UserModuleProgress.reflection_dtp_xai and writes an 'xai_narrative'
    provenance row. The input is the stored DTP composite; the agent
    does not see the teacher's reflection text (faithfulness).
    """

    artefact_kind = 'xai_narrative'
    model_name = 'gemini-2.5-flash'

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------
    def _do_generate(self, *, dtp_composite: dict, aspect_label: str) -> str:
        """Produce a domain-driven explanation of the DTP composite.

        Args:
            dtp_composite: the stored `dtp_dual_v1` dict.
            aspect_label: the UNESCO competency aspect of the current
                module (e.g. 'Human-Centred Mindset').

        Returns the explanation text. On Gemini failure, or when the
        composite carries no signal, returns the safe fallback so a
        composite explanation always exists.
        """
        logger = logging.getLogger(__name__)

        if not dtp_composite.get('signals'):
            logger.warning('XAIAgent: composite has no signals; using fallback')
            return XAI_FALLBACK

        prompt = self._build_prompt(dtp_composite, aspect_label)

        client = get_llm_client()
        gen_result = client.generate(
            prompt,
            model=self.model_name,
            temperature=XAI_TEMPERATURE,
            max_output_tokens=XAI_MAX_TOKENS,
        )
        if gen_result is None or not gen_result.text.strip():
            logger.warning('XAIAgent: Gemini returned nothing; using fallback')
            return XAI_FALLBACK

        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=self.artefact_kind,
        ))
        return self._parse_explanation(gen_result.text)

    # ------------------------------------------------------------------
    # Cost tracking — override default. The single Gemini call records
    # its own cost event inline; the output is a plain string, so the
    # base-class GenerationResult path would be a silent no-op anyway.
    # ------------------------------------------------------------------
    def _track_cost(self, *, output) -> None:
        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_explanation(text: str) -> str:
        """Extract the <explanation>...</explanation> block — the
        teacher-facing text. The <reasoning> block is a chain-of-thought
        scaffold and is discarded. Falls back to the whole stripped
        text, then to the canned fallback."""
        match = re.search(
            r'<explanation>(.*?)</explanation>', text,
            re.DOTALL | re.IGNORECASE,
        )
        if match and match.group(1).strip():
            return match.group(1).strip()
        return text.strip() or XAI_FALLBACK

    @staticmethod
    def _build_prompt(dtp_composite: dict, aspect_label: str) -> str:
        """Domain-driven, faithfulness-bounded explanation prompt.

        Lays out only what the DTP composite contains — the thematic
        shifts of each available signal, never the cosine value. The
        model reasons in a <reasoning> block and gives the
        teacher-facing text in an <explanation> block; only the latter
        is surfaced.
        """
        current_module = dtp_composite.get('current_module', '')
        signals = dtp_composite.get('signals', {})
        blocks = []

        vertical = signals.get('vertical')
        if vertical:
            blocks.append(XAIAgent._signal_block(
                'Within the same UNESCO competency area '
                f'({aspect_label}), comparing the earlier proficiency '
                f"level (module {vertical['comparison_module']}) with "
                f'the current module ({current_module})',
                vertical['themes'],
            ))
        temporal = signals.get('temporal')
        if temporal:
            blocks.append(XAIAgent._signal_block(
                'Comparing the immediately preceding module '
                f"(module {temporal['comparison_module']}) with the "
                f'current module ({current_module})',
                temporal['themes'],
            ))

        comparisons = '\n\n'.join(blocks)
        return (
            'You are explaining, to a teacher, why their developmental '
            'signal looks the way it does. You are given the signal the '
            'platform computed; explain only that — do not add causes, '
            'do not re-interpret, and do not evaluate whether the '
            'teacher has improved or worsened.\n\n'
            'Rules:\n'
            '- Speak in pedagogical and competency terms, never in '
            'numbers or technical mechanics.\n'
            '- A theme appearing with less emphasis is a shift of '
            'reflective attention — not a decline or loss of competence, '
            'and equally not progress, advancement, improvement, or '
            'growing sophistication. Describe where attention moved, '
            'never whether the teacher has become better, worse, or '
            'more advanced.\n'
            '- Stay strictly within the comparisons given below; '
            'introduce nothing else.\n\n'
            f'{comparisons}\n\n'
            'Respond in exactly this format:\n'
            '<reasoning>Brief notes on what the comparisons show.'
            '</reasoning>\n'
            '<explanation>A short paragraph addressed to the teacher, '
            'in plain prose with no bullet points, explaining what the '
            'signal reflects and why a shift of emphasis is a normal '
            'part of development at this stage.</explanation>'
        )

    @staticmethod
    def _signal_block(heading: str, themes: dict) -> str:
        """Render one signal's thematic shifts for the prompt body."""
        def _line(key: str) -> str:
            items = themes.get(key, [])
            return ', '.join(items) if items else 'none noted'

        return (
            f'{heading}:\n'
            f'  themes given more emphasis: {_line("increased_themes")}\n'
            f'  themes given less emphasis: {_line("decreased_themes")}\n'
            f'  themes held steady: {_line("stable_themes")}'
        )
