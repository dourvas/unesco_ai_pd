"""
RTMAgent — Reflective Tension Mapper extraction agent.

Phase E commit 3 — extract-only agent (BaseAIAgent.extract() entry
point, not generate()). The AI output (a list of validated pedagogical
tensions, each with label + left_pole + right_pole + grounding_quote)
is ephemeral until the user submits their positioning via the
save_tensions endpoint, at which point ReflectionTension rows are
written with 'rtm_position' provenance.

This agent does NOT write to the DB. It does NOT write provenance.
Callers invoke `extract()`, render the suggestions to the frontend,
and the user's accept/modify/discard decision drives persistence
through a separate request lifecycle (views.save_tensions).

Behaviour parity with rag_query_system.extract_tensions:
  - 800-word truncation safety cap, preserved verbatim
  - Double-quote -> single-quote sanitisation before prompt construction
  - Gemini temperature=0.3 (analytic, not creative)
  - max_output_tokens=2500
  - JSON repair via apps/agents/shared/json_repair.clean_json_response
  - Robust outer-brace extraction post-cleanup
  - Validation rules from monolith validate_tensions, kept verbatim:
        Rule 1: grounding_quote >= 20 chars
        Rule 2: quote grounded — >= 3 significant (>=4 char) words found
                in the reflection's normalised text
        Rule 3: label <= 6 words
        Rule 4: poles >= 10 chars each
        Return first 2 valid, or None if none pass.

Monolith oddity preserved: the system_message string defined in
rag_query_system.extract_tensions is never actually sent to Gemini
(monolith calls `contents=user_message` only). The agent preserves
this byte-identically — only the user_message reaches Gemini. A future
commit may decide to actually send the system message; for now,
behaviour parity is the invariant the prompt-identical test enforces.
"""

import json
import logging
from typing import Optional

from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.json_repair import clean_json_response
from apps.agents.shared.llm_client import GenerationResult, get_llm_client


RTM_TEMPERATURE = 0.3
RTM_MAX_OUTPUT_TOKENS = 2500
RTM_MAX_REFLECTION_WORDS = 800
RTM_MAX_VALID_TENSIONS = 2

# Validation rule thresholds — kept as named constants so a future
# tightening (e.g. require longer quotes) is a single-line edit.
RTM_MIN_QUOTE_CHARS = 20
RTM_MIN_GROUNDED_SIGNIFICANT_WORDS = 3
RTM_SIGNIFICANT_WORD_MIN_LEN = 4
RTM_MAX_LABEL_WORDS = 6
RTM_MIN_POLE_CHARS = 10


class RTMAgent(ResearchInstrumentAgent):
    """Pedagogical-tension extractor.

    Public API: only `extract()` (inherited from BaseAIAgent).
    Calling `generate()` on this agent raises ValueError — RTM has no
    save_target at extraction time; persistence is owned by the
    save_tensions endpoint.

    artefact_kind is set to 'rtm_position' proactively even though
    extract() does not write provenance, so:
      (a) audit-log entries carry the intended kind for traceability,
      (b) a future migration of RTM to save-owning agent (Phase F+)
          has the constant already declared.
    """

    artefact_kind = 'rtm_position'
    model_name = 'gemini-2.5-flash'

    def _do_generate(
        self,
        *,
        reflection_text: str,
        teacher_context: dict,
    ) -> Optional[list[dict]]:
        """Extract validated pedagogical tensions from a reflection.

        Returns a list of 1-2 tension dicts (each with label, left_pole,
        right_pole, grounding_quote) on success, or None on any failure
        (Gemini error, JSON parse error, no valid tensions). Matches
        the monolith's return contract; views.extract_tensions_view
        already branches on None/truthy.
        """
        logger = logging.getLogger(__name__)
        client = get_llm_client()

        # Truncation safety cap — long reflections occasionally produce
        # OOM-style Gemini responses; the monolith truncated at 800
        # words and we preserve that boundary.
        words = reflection_text.split()
        if len(words) > RTM_MAX_REFLECTION_WORDS:
            reflection_text = ' '.join(words[:RTM_MAX_REFLECTION_WORDS])

        prompt = self._build_prompt(reflection_text, teacher_context)

        gen_result = client.generate(
            prompt,
            model=self.model_name,
            temperature=RTM_TEMPERATURE,
            max_output_tokens=RTM_MAX_OUTPUT_TOKENS,
        )
        if gen_result is None:
            return None

        # Cost-track this single Gemini call. extract() only calls
        # _track_cost on the composite output, but RTM has exactly one
        # LLM call per extraction, so we record it here for symmetry
        # with the multi-call agents that land in commits 5/7.
        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=self.artefact_kind,
        ))

        result_text = self._strip_markdown_fences(gen_result.text)
        result_text = clean_json_response(result_text)
        result_text = self._trim_to_outer_braces(result_text)

        try:
            tensions_json = json.loads(result_text)
        except json.JSONDecodeError as exc:
            logger.warning('RTMAgent JSON parse error: %s', exc)
            return None

        return self.validate_tensions(tensions_json, reflection_text)

    # ------------------------------------------------------------------
    # Override _track_cost — already done inline in _do_generate to
    # match the per-call granularity of the future multi-Gemini agents.
    # Without this override, the base class would track again on the
    # composite list-or-None output (no-op since output is not a
    # GenerationResult, but cleaner to be explicit).
    # ------------------------------------------------------------------
    def _track_cost(self, *, output) -> None:
        return None

    # ------------------------------------------------------------------
    # generate() blocker — RTM is extract-only by contract.
    # ------------------------------------------------------------------
    def generate(self, **kwargs):
        raise ValueError(
            "RTMAgent is extract-only; call extract(...) instead. "
            "Persistence of validated tensions is owned by the "
            "save_tensions endpoint (apps.modules.views.save_tensions), "
            "which writes ReflectionTension rows + 'rtm_position' "
            "provenance after the user submits their positioning."
        )

    # ------------------------------------------------------------------
    # Prompt construction — byte-identical to monolith extract_tensions
    # ------------------------------------------------------------------
    @staticmethod
    def _build_prompt(reflection_text: str, teacher_context: dict) -> str:
        """Build the user_message exactly as the monolith does.

        Note: rag_query_system.extract_tensions also defines a
        system_message but never sends it to Gemini (the call uses
        contents=user_message only). We preserve this byte-identically
        so the prompt-parity test passes against the monolith. teacher_
        context is accepted for signature parity but not used inside
        the prompt — the monolith uses it for logging only.
        """
        reflection_for_prompt = reflection_text.replace('"', "'")

        return f"""Reflection:
{reflection_for_prompt}
IMPORTANT RULES:
1. Return EXACTLY 2 tensions, no more, no less.
2. Do NOT use quotes or apostrophes inside the JSON string values.
3. Do NOT use escaped characters like \\" or \\' in your response.
4. Keep left_pole and right_pole SHORT (max 8 words each).
5. Keep grounding_quote SHORT (max 15 words).

- Keep ALL field values SHORT: label max 6 words, poles max 8 words each, grounding_quote max 10 words

Return JSON in this exact format:

{{
  "tensions": [
    {{
      "label": "Short label max 6 words",
      "left_pole": "Max 8 words",
      "right_pole": "Max 8 words",
      "grounding_quote": "Max 10 words from reflection"
    }},
    {{
      "label": "...",
      "left_pole": "...",
      "right_pole": "...",
      "grounding_quote": "..."
    }}
  ]
}}

If no meaningful tension is identifiable, return: {{"tensions": []}}"""

    # ------------------------------------------------------------------
    # JSON cleanup helpers — same algorithm the monolith uses inline
    # ------------------------------------------------------------------
    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        text = text.strip()
        if '```json' in text:
            text = text.split('```json')[-1].split('```')[0].strip()
        elif text.startswith('```'):
            text = text[3:].split('```')[0].strip()
        return text

    @staticmethod
    def _trim_to_outer_braces(text: str) -> str:
        """Trim to the outermost {...} so trailing prose after valid
        JSON does not break json.loads."""
        brace_start = text.find('{')
        brace_end = text.rfind('}')
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            return text[brace_start:brace_end + 1]
        return text

    # ------------------------------------------------------------------
    # Validation — pure function, mirrors monolith validate_tensions
    # ------------------------------------------------------------------
    @staticmethod
    def validate_tensions(
        tensions_json: dict,
        reflection_text: str,
    ) -> Optional[list[dict]]:
        """Apply the four validation rules. Return up to 2 valid, or None.

        Static method so tests can exercise it directly without spinning
        up the full agent. Behaviour-identical to
        rag_query_system.validate_tensions — rules and thresholds kept
        verbatim. The 4-char "significant word" cutoff for the quote-
        grounding rule is preserved (filters out function words like
        "the", "and", "for" that would inflate the grounded-words count
        spuriously).
        """
        logger = logging.getLogger(__name__)

        if not tensions_json.get('tensions'):
            return None

        valid: list[dict] = []
        reflection_normalised = _normalise(reflection_text)

        for tension in tensions_json['tensions']:
            label = tension.get('label', '')
            quote = tension.get('grounding_quote', '')
            left = tension.get('left_pole', '')
            right = tension.get('right_pole', '')

            # Rule 1: quote substantial enough to be auditable
            if len(quote) < RTM_MIN_QUOTE_CHARS:
                continue

            # Rule 2: quote grounded in the reflection — at least 3 of
            # its significant (>=4 char) words must appear in the
            # reflection's normalised text. Guards against AI making
            # up quotes wholesale.
            quote_words = _normalise(quote).split()
            if len(quote_words) >= 3:
                significant = [
                    w for w in quote_words
                    if len(w) >= RTM_SIGNIFICANT_WORD_MIN_LEN
                ]
                found_count = sum(
                    1 for w in significant if w in reflection_normalised
                )
                if found_count < RTM_MIN_GROUNDED_SIGNIFICANT_WORDS:
                    continue

            # Rule 3: label concise (display constraint)
            if len(label.split()) > RTM_MAX_LABEL_WORDS:
                continue

            # Rule 4: poles substantial enough to read as polarities
            if len(left) < RTM_MIN_POLE_CHARS or len(right) < RTM_MIN_POLE_CHARS:
                continue

            valid.append(tension)

        if not valid:
            return None
        return valid[:RTM_MAX_VALID_TENSIONS]


# ----------------------------------------------------------------------
# Module-level helper — kept private to this file.
# ----------------------------------------------------------------------
def _normalise(text: str) -> str:
    """Lower-case + smart-quote/dash/escape normalisation, then collapse
    whitespace. Used by both the grounding-rule check and the prompt
    sanitisation step. Mirrors the inline `normalize` from
    rag_query_system.validate_tensions verbatim.
    """
    text = text.lower()
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('—', '-').replace('–', '-')
    text = text.replace("\\'", "'")
    text = text.replace('\\n', ' ')
    text = ' '.join(text.split())
    return text
