"""
DTPAgent — Developmental Trajectory Predictor.

Phase E commit 5 — multi-step orchestration agent. Computes the
developmental signal between a teacher's previous and current
reflections (cosine similarity over Gemini embeddings) and produces
a 60-word descriptive narrative grounded in the inferred thematic
shifts. The composite artefact is persisted to
UserModuleProgress.reflection_dtp as a JSON string.

Architectural notes (vs. RAG / RTM):

  - DTP is the first multi-Gemini-call agent (commits 1-3 each had a
    single LLM call per _do_generate). Two distinct Gemini prompts
    fire per generate(): theme extraction (max_output_tokens=1000,
    temperature=0.3) and narrative generation (max_output_tokens=2000,
    temperature=0.4). Two embed_query calls also fire (one per
    reflection). The base class's _track_cost is overridden to no-op
    because each Gemini sub-call records its own cost event inline —
    this gives per-Gemini-call granularity for the dissertation's
    cost-per-feature breakdown.

  - The artefact is a composite dict (similarity + label + description
    + narrative + themes). Provenance is ONE row per generate() call,
    keyed by ('dtp_narrative', progress.pk) — the default
    _record_provenance suffices. The multi-call structure inside
    _do_generate does NOT translate to multiple provenance rows; the
    user-visible artefact is single.

  - Persistence: JSON-serialise the dict before writing to the
    reflection_dtp TextField. _persist is overridden minimally to do
    json.dumps(output) + setattr + save — matching the existing
    views.py:2306 pattern byte-for-byte.

Failure-mode parity with rag_query_system.compute_dtp:

  - If either embed_query returns None, the full call returns None
    (no atomic block opened — _do_generate raises before _persist).
  - If theme extraction raises or returns malformed JSON, themes
    fall back to {"increased": [], "decreased": [], "stable": []}.
    The composite still succeeds.
  - If narrative generation raises or returns empty text, narrative
    falls back to signal['continuity_description'] (the canned
    sentence for the continuity bucket). The composite still
    succeeds.

  This means generate() returns None only on embedding failure;
  every other partial failure degrades gracefully with the same
  monolith-side defaults. Tests verify each branch.

Bug-preservation contracts (verbatim from monolith):

  - reflection sanitisation: prev[:400].replace('"', "'").replace('\\n', ' ')
    Same for curr. The 400-char cap is a prompt-size budget.
  - max_output_tokens=1000 for theme extraction (CP-9 commit 2a
    discovered Gemini occasionally OOM-streams JSON if uncapped).
  - max_output_tokens=2000 for narrative generation.
  - max(0, count(open) - count(close)) wrappers in the JSON-repair
    fallback for theme extraction — never negative brackets/braces.

Diagnostic for commit 6 (per v6 §8 #7):

  Inspecting the existing DTP write path at
  apps/modules/views.py:2306-2314 confirms NO inconsistency window
  exists today. compute_dtp returns a dict (or None) with no DB
  writes of its own; views.py wraps progress.save() and the
  'dtp_narrative' provenance write in one transaction.atomic.

  --> Commit 6 will be PRESERVATION, not strengthening.
  Analogous to commit 4 (RTM). Documented here so commit 6's
  message can adopt the same framing as commit 4.
"""

import json
import logging
from typing import Any, Optional

from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.json_repair import clean_json_response
from apps.agents.shared.llm_client import GenerationResult, get_llm_client


# Continuity-bucket thresholds — verbatim from monolith
# compute_development_signal. The boundary values define a 3-bucket
# ordinal scale; values are research artefacts and must not drift
# without a separate methodology commit.
DTP_HIGH_THRESHOLD = 0.85
DTP_MODERATE_THRESHOLD = 0.70

# Gemini call configurations — verbatim from monolith
DTP_THEME_TEMPERATURE = 0.3
DTP_THEME_MAX_TOKENS = 1000
DTP_NARRATIVE_TEMPERATURE = 0.4
DTP_NARRATIVE_MAX_TOKENS = 2000

# Prompt-budget cap for each reflection — first 400 chars only fit in
# the theme-extraction prompt body. Larger context would inflate
# Gemini latency without changing theme-detection quality.
DTP_REFLECTION_PROMPT_BUDGET = 400


class DTPAgent(ResearchInstrumentAgent):
    """Developmental Trajectory Predictor.

    Public API: generate() (committed artefact path — DTP writes
    progress.reflection_dtp + 'dtp_narrative' provenance atomically).
    Calling extract() would technically work (extract() is base-class
    behaviour) but produces an unsaved composite; intended use is
    generate().

    Provenance: one row per call, kind='dtp_narrative',
    artefact_pk=progress.pk. CP-7 idempotent on (kind, pk).
    """

    artefact_kind = 'dtp_narrative'
    model_name = 'gemini-2.5-flash'

    # ------------------------------------------------------------------
    # Multi-step orchestration
    # ------------------------------------------------------------------
    def _do_generate(
        self,
        *,
        previous_reflection_text: str,
        current_reflection_text: str,
        previous_module: str = 'M1',
        current_module: str = 'M2',
    ) -> Optional[dict]:
        """Run the full DTP pipeline: embed -> signal -> themes -> narrative.

        Returns the composite dict (shape preserved from monolith
        compute_dtp) on success, or None if embedding fails. Partial
        failures inside theme / narrative steps degrade gracefully —
        the composite still returns.
        """
        logger = logging.getLogger(__name__)
        client = get_llm_client()

        # Step 1: embed both reflections. Raise on failure so the
        # surrounding transaction.atomic from generate() rolls back —
        # no provenance row for a never-computed signal. The caller
        # (views.extract_dtp_view post-commit-6) wraps generate() in
        # a try/except and gracefully degrades (no DTP card rendered).
        emb_prev = client.embed(previous_reflection_text)
        emb_curr = client.embed(current_reflection_text)
        if emb_prev is None or emb_curr is None:
            logger.warning('DTPAgent: embedding failed; aborting')
            raise RuntimeError(
                'DTPAgent: embedding step returned None — aborting '
                'composite generation so the atomic block rolls back.'
            )

        # Step 2: cosine signal
        signal = self.compute_development_signal(emb_prev, emb_curr)

        # Step 3: theme extraction (Gemini call #1)
        themes = self._extract_themes(
            previous_reflection_text, current_reflection_text,
        )

        # Step 4: narrative generation (Gemini call #2)
        narrative = self._generate_narrative(
            signal, themes, previous_module, current_module,
        )

        return {
            'previous_module': previous_module,
            'current_module': current_module,
            'similarity': signal['similarity'],
            'continuity_label': signal['continuity_label'],
            'continuity_description': signal['continuity_description'],
            'narrative': narrative,
            'themes': {
                'increased_themes': themes.get('increased', []),
                'decreased_themes': themes.get('decreased', []),
                'stable_themes': themes.get('stable', []),
            },
        }

    # ------------------------------------------------------------------
    # Persistence — JSON-serialise the composite before writing
    # ------------------------------------------------------------------
    def _persist(self, *, output: dict, save_target, save_field: Optional[str]) -> Any:
        """Write json.dumps(output) to save_target.<save_field>.

        Overrides the default str-direct setattr because the artefact
        is structured (dict) but the underlying field is TextField.
        Matches views.py:2307 byte-identically:
            progress.reflection_dtp = json.dumps(dtp_result)
        """
        if save_target is None or save_field is None:
            raise ValueError(
                "DTPAgent.generate requires save_target (UserModule"
                "Progress) and save_field (e.g. 'reflection_dtp')."
            )
        setattr(save_target, save_field, json.dumps(output))
        save_target.save(update_fields=[save_field])
        return save_target.pk

    # ------------------------------------------------------------------
    # Cost tracking — override default. Each Gemini sub-call records
    # its own cost event inline; the composite output is not a
    # GenerationResult so the default would be a silent no-op anyway,
    # but we override explicitly to make intent clear.
    # ------------------------------------------------------------------
    def _track_cost(self, *, output) -> None:
        return None

    # ==================================================================
    # Public helpers — kept as static methods so tests can exercise
    # them directly without instantiating the full agent.
    # ==================================================================
    @staticmethod
    def compute_development_signal(embedding1, embedding2) -> dict:
        """Cosine similarity + continuity-bucket label/description.

        Mirrors rag_query_system.compute_development_signal verbatim.
        The 0.85 / 0.70 thresholds and the three canned description
        strings are research artefacts of the DTP methodology and
        MUST not drift; constants live at module top so any future
        methodology revision is one place to edit.
        """
        import numpy as np

        v1 = np.array(embedding1)
        v2 = np.array(embedding2)
        similarity = float(
            np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        )

        if similarity >= DTP_HIGH_THRESHOLD:
            label = 'High'
            description = (
                'Your reflections show sustained focus on core pedagogical priorities.'
            )
        elif similarity >= DTP_MODERATE_THRESHOLD:
            label = 'Moderate'
            description = (
                'Your pedagogical focus has evolved, showing deeper engagement '
                'with instructional design.'
            )
        else:
            label = 'Significant'
            description = (
                'Your reflection shows substantial evolution in how you '
                'conceptualize AI in education.'
            )

        return {
            'similarity': round(similarity, 4),
            'continuity_label': label,
            'continuity_description': description,
        }

    # ------------------------------------------------------------------
    # Theme extraction (Gemini call #1)
    # ------------------------------------------------------------------
    def _extract_themes(
        self,
        previous_reflection: str,
        current_reflection: str,
    ) -> dict:
        """Gemini call #1: themes increased / decreased / stable.

        Returns a dict {'increased': [...], 'decreased': [...],
        'stable': [...]}. On any failure (Gemini error, JSON parse
        even after repair, malformed shape), returns the empty-themes
        default so the composite call still produces a narrative.
        """
        logger = logging.getLogger(__name__)
        prompt = self._build_themes_prompt(previous_reflection, current_reflection)

        client = get_llm_client()
        gen_result = client.generate(
            prompt,
            model=self.model_name,
            temperature=DTP_THEME_TEMPERATURE,
            max_output_tokens=DTP_THEME_MAX_TOKENS,
        )
        if gen_result is None:
            return self._empty_themes()

        # Per-Gemini-call cost event — emits 'agent.cost' so the
        # dissertation can report cost-per-LLM-call not just cost-per-
        # agent-call.
        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=self.artefact_kind,
        ))

        result_text = self._strip_markdown_fences(gen_result.text.strip())
        result_text = clean_json_response(result_text)

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            # JSON repair fallback — close any unbalanced braces /
            # brackets / quotes. Uses max(0, ...) guards so we never
            # add negative-count delimiters even on absurd inputs.
            repaired = result_text.rstrip()
            if repaired.count('"') % 2 != 0:
                repaired += '"'
            open_brackets = max(0, repaired.count('[') - repaired.count(']'))
            open_braces = max(0, repaired.count('{') - repaired.count('}'))
            repaired += ']' * open_brackets
            repaired += '}' * open_braces
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as exc:
                logger.warning('DTPAgent theme JSON repair failed: %s', exc)
                return self._empty_themes()

    # ------------------------------------------------------------------
    # Narrative generation (Gemini call #2)
    # ------------------------------------------------------------------
    def _generate_narrative(
        self,
        signal: dict,
        themes: dict,
        previous_module: str,
        current_module: str,
    ) -> str:
        """Gemini call #2: 60-word descriptive paragraph.

        Falls back to signal['continuity_description'] (the canned
        bucket sentence) on any failure. The fallback is itself a
        valid user-facing string, so the composite always has a
        meaningful narrative.
        """
        prompt = self._build_narrative_prompt(
            signal, themes, previous_module, current_module,
        )

        client = get_llm_client()
        gen_result = client.generate(
            prompt,
            model=self.model_name,
            temperature=DTP_NARRATIVE_TEMPERATURE,
            max_output_tokens=DTP_NARRATIVE_MAX_TOKENS,
        )
        if gen_result is None or not gen_result.text.strip():
            return signal['continuity_description']

        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=self.artefact_kind,
        ))

        return gen_result.text.strip()

    # ------------------------------------------------------------------
    # Prompt builders — byte-identical to monolith
    # ------------------------------------------------------------------
    @staticmethod
    def _build_themes_prompt(prev_text: str, curr_text: str) -> str:
        """Theme-extraction prompt. Sanitisation: trim to 400 chars,
        " -> ', literal \\n -> space. Mirrors
        rag_query_system.extract_development_themes verbatim."""
        prev_clean = (
            prev_text[:DTP_REFLECTION_PROMPT_BUDGET]
            .replace('"', "'")
            .replace('\n', ' ')
        )
        curr_clean = (
            curr_text[:DTP_REFLECTION_PROMPT_BUDGET]
            .replace('"', "'")
            .replace('\n', ' ')
        )
        return f"""Compare these two teacher reflections. Return ONLY a JSON object.
PREVIOUS:
{prev_clean}
CURRENT:
{curr_clean}

Return this exact JSON structure with no markdown, no explanation:
{{"increased": [], "decreased": [], "stable": []}}

Fill each array with 2-3 phrases of MAX 3 WORDS EACH. Keep it extremely brief.
Example: {{"increased": ["ethical focus"], "decreased": [], "stable": ["physics context"]}}
If no clear shift exists in a category, leave the array empty."""

    @staticmethod
    def _build_narrative_prompt(
        signal: dict,
        themes: dict,
        previous_module: str,
        current_module: str,
    ) -> str:
        """Narrative prompt. Mirrors
        rag_query_system.generate_development_narrative verbatim.
        Note the monolith fills `increased` / `decreased` variables
        but never references them in the rendered prompt — only
        `stable` makes it into the prompt body. Preserved here to
        keep prompt-parity tests stable; flagged as a monolith
        quirk in §11 of v7 (candidate for commit 9 cleanup)."""
        increased = ', '.join(themes.get('increased', [])) or 'none noted'  # noqa: F841 — preserved for parity
        decreased = ', '.join(themes.get('decreased', [])) or 'none noted'  # noqa: F841 — preserved for parity
        stable = ', '.join(themes.get('stable', [])) or 'none noted'
        return f"""Write a 60-word neutral observation about a teacher's reflective development.

Facts:
- Modules compared: {previous_module} to {current_module}
- Continuity level: {signal['continuity_label']}
- {signal['continuity_description']}
- Stable themes: {stable}

Write a complete paragraph of exactly 60 words. 
Start with: "Across these modules, your reflection demonstrates"
Do not use bullet points. Write in plain prose only."""

    # ------------------------------------------------------------------
    # Helpers (private)
    # ------------------------------------------------------------------
    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Same markdown-fence stripper RTM uses, inlined for parity
        with the monolith DTP path (the monolith does this inline
        rather than calling a shared helper)."""
        if '```json' in text:
            return text.split('```json')[-1].split('```')[0].strip()
        if text.startswith('```'):
            return text[3:].split('```')[0].strip()
        return text

    @staticmethod
    def _empty_themes() -> dict:
        return {'increased': [], 'decreased': [], 'stable': []}
