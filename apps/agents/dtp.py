"""
DTPAgent — Developmental Trajectory Predictor (redefined, D.3a).

This is the redefined dual-signal DTP. It supersedes the Phase E
monolith-parity DTP. Design and rationale:
proodos_files/DTP_REDEFINITION_DESIGN_PROPOSAL_v1_20260518.md.

What changed from the Phase E DTP
---------------------------------
The previous DTP compared the current reflection against the most
recent reflection from any other module. Because the 15 modules span
five UNESCO competency aspects, that comparison routinely crossed
aspects and reported topic difference as developmental change — a
construct-validity problem (design proposal §2).

The redefined DTP computes up to two independent signals:

  Vertical Continuity Signal (VCS)
      current reflection vs the teacher's reflection at the
      immediately lower proficiency level of the same UNESCO aspect
      (Deepen vs Acquire, Create vs Deepen). Isolates within-aspect
      conceptual continuity / shift.

  Temporal Shift Signal (TSS)
      current reflection vs the reflection at the immediately
      preceding module. A focus-continuity measure across the module
      sequence.

Which signals exist is decided by the caller (extract_dtp_view): it
passes only the comparison reflections that exist. An Acquire module
has no VCS; the first module has neither (the view does not call the
agent at all). See design proposal §5.

Pilot scope
-----------
The redefined DTP is descriptive only. Each signal carries its raw
cosine similarity (stored, not displayed) and its thematic shifts.
There is NO three-category continuity label and NO thresholds — the
label is a post-pilot research-analysis artefact (design proposal
§7.4). A cosine similarity measures conceptual continuity, not the
quality of development (design proposal §4.4).

Composite shape (persisted to UserModuleProgress.reflection_dtp as a
JSON string):

    {
      "schema": "dtp_dual_v1",
      "current_module": "M8",
      "narrative": "<~60-word descriptive synthesis>",
      "signals": {
        "vertical": {"comparison_module": "M3",
                     "similarity": 0.7421,
                     "themes": {"increased_themes": [...],
                                "decreased_themes": [...],
                                "stable_themes": [...]}},
        "temporal": {"comparison_module": "M7",
                     "similarity": 0.6810,
                     "themes": {...}}
      }
    }

A signal key is absent when that signal is not available.

Agent contract (unchanged from Phase E)
---------------------------------------
DTPAgent uses generate() — it owns the save + provenance atomic block
(CP-9). Provenance is one row per call, kind 'dtp_narrative', keyed by
progress.pk. _do_generate raises RuntimeError on any embedding failure
so the surrounding atomic rolls back. Each Gemini sub-call records its
own cost event inline; _track_cost is overridden to a no-op.
"""

import json
import logging
import re
from typing import Any, Optional

from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.json_repair import clean_json_response
from apps.agents.shared.llm_client import get_llm_client


# Gemini call configurations — carried over from the Phase E DTP.
DTP_THEME_TEMPERATURE = 0.3
DTP_THEME_MAX_TOKENS = 1000
DTP_NARRATIVE_TEMPERATURE = 0.4
DTP_NARRATIVE_MAX_TOKENS = 2000

# Prompt-budget cap for each reflection in the theme-extraction prompt.
DTP_REFLECTION_PROMPT_BUDGET = 400

# Composite schema tag — distinguishes the redefined dual-signal
# composite from the superseded Phase E single-signal shape.
DTP_SCHEMA = 'dtp_dual_v1'

# Descriptive fallback used when the narrative Gemini call fails or
# returns nothing. It is itself a valid, non-evaluative user-facing
# sentence (design proposal §4.4 — describe, do not evaluate).
DTP_NARRATIVE_FALLBACK = (
    'Across these modules, your reflection shows a mix of continuity '
    'and shift in the themes noted below.'
)


class DTPAgent(ResearchInstrumentAgent):
    """Developmental Trajectory Predictor — redefined dual-signal form.

    Public API: generate() (committed artefact path — DTP writes
    progress.reflection_dtp + 'dtp_narrative' provenance atomically).

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
        current_reflection_text: str,
        current_module: str,
        vertical_reflection_text: Optional[str] = None,
        vertical_module: Optional[str] = None,
        temporal_reflection_text: Optional[str] = None,
        temporal_module: Optional[str] = None,
    ) -> dict:
        """Compute the dual-signal DTP composite.

        The caller passes the current reflection plus whichever
        comparison reflections exist. At least one of the vertical /
        temporal pairs must be supplied — the view does not invoke the
        agent for the first module, which has neither.

        Raises RuntimeError on any embedding failure so the surrounding
        transaction.atomic from generate() rolls back (no provenance
        row for a never-computed composite).
        """
        logger = logging.getLogger(__name__)
        client = get_llm_client()

        # Assemble the requested signals. The first element is the
        # composite key ('vertical' / 'temporal').
        requested = []
        if vertical_reflection_text and vertical_module:
            requested.append(
                ('vertical', vertical_reflection_text, vertical_module)
            )
        if temporal_reflection_text and temporal_module:
            requested.append(
                ('temporal', temporal_reflection_text, temporal_module)
            )
        if not requested:
            raise RuntimeError(
                'DTPAgent: no comparison signal supplied — the caller '
                'must pass at least one of the vertical / temporal pairs.'
            )

        # Step 1: embed the current reflection once.
        emb_current = client.embed(current_reflection_text)
        if emb_current is None:
            logger.warning('DTPAgent: current-reflection embedding failed')
            raise RuntimeError(
                'DTPAgent: embedding of the current reflection returned '
                'None — aborting so the atomic block rolls back.'
            )

        # Step 2: per signal — embed comparison, cosine similarity,
        # theme extraction (one Gemini call per signal).
        signals = {}
        for kind, comparison_text, comparison_module in requested:
            emb_comparison = client.embed(comparison_text)
            if emb_comparison is None:
                logger.warning(
                    'DTPAgent: %s comparison embedding failed', kind,
                )
                raise RuntimeError(
                    f'DTPAgent: embedding of the {kind} comparison '
                    'reflection returned None — aborting so the atomic '
                    'block rolls back.'
                )
            similarity = self._cosine_similarity(emb_current, emb_comparison)
            # The comparison reflection is the earlier text ("previous"),
            # the current reflection is the later text ("current").
            themes = self._extract_themes(
                comparison_text, current_reflection_text,
            )
            signals[kind] = {
                'comparison_module': comparison_module,
                'similarity': similarity,
                'themes': {
                    'increased_themes': themes.get('increased', []),
                    'decreased_themes': themes.get('decreased', []),
                    'stable_themes': themes.get('stable', []),
                },
            }

        # Step 3: one narrative synthesising every available signal.
        narrative = self._generate_narrative(current_module, signals)

        return {
            'schema': DTP_SCHEMA,
            'current_module': current_module,
            'narrative': narrative,
            'signals': signals,
        }

    # ------------------------------------------------------------------
    # Persistence — JSON-serialise the composite before writing
    # ------------------------------------------------------------------
    def _persist(self, *, output: dict, save_target, save_field: Optional[str]) -> Any:
        """Write json.dumps(output) to save_target.<save_field>.

        The artefact is a structured dict; the underlying field
        (UserModuleProgress.reflection_dtp) is a TextField.
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
    # Cost tracking — override default. Each Gemini sub-call records its
    # own cost event inline; the composite output is not a
    # GenerationResult so the default would be a silent no-op anyway.
    # ------------------------------------------------------------------
    def _track_cost(self, *, output) -> None:
        return None

    # ==================================================================
    # Signal computation
    # ==================================================================
    @staticmethod
    def _cosine_similarity(embedding1, embedding2) -> float:
        """Cosine similarity of two embedding vectors, rounded to 4 dp.

        The continuity-bucket label / description that the Phase E DTP
        derived from this value is intentionally removed: the redefined
        DTP ships no thresholds and no label (design proposal §7.4).
        The raw similarity is stored for the post-pilot calibration but
        is not displayed to the teacher.
        """
        import numpy as np

        v1 = np.array(embedding1)
        v2 = np.array(embedding2)
        similarity = float(
            np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        )
        return round(similarity, 4)

    # ------------------------------------------------------------------
    # Theme extraction (one Gemini call per signal)
    # ------------------------------------------------------------------
    def _extract_themes(
        self,
        previous_reflection: str,
        current_reflection: str,
    ) -> dict:
        """Gemini call: themes increased / decreased / stable.

        Returns a dict {'increased': [...], 'decreased': [...],
        'stable': [...]}. On any failure (Gemini error, JSON parse even
        after repair, malformed shape), returns the empty-themes default
        so the composite call still produces a narrative.

        The prompt is unchanged from the Phase E DTP — a generic
        two-reflection thematic-shift extractor — so it is reused
        verbatim for both the vertical and the temporal signal.
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
        # dissertation can report cost-per-LLM-call.
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
    # Narrative generation (one Gemini call for the whole composite)
    # ------------------------------------------------------------------
    def _generate_narrative(self, current_module: str, signals: dict) -> str:
        """One Gemini call: a ~60-word descriptive synthesis of every
        available signal.

        The structured prompt makes the model analyse each signal
        separately before synthesising (chain-of-thought scaffold); only
        the <synthesis> block is kept. Falls back to a canned descriptive
        sentence on any failure, so the composite always has a narrative.
        """
        prompt = self._build_narrative_prompt(current_module, signals)

        client = get_llm_client()
        gen_result = client.generate(
            prompt,
            model=self.model_name,
            temperature=DTP_NARRATIVE_TEMPERATURE,
            max_output_tokens=DTP_NARRATIVE_MAX_TOKENS,
        )
        if gen_result is None or not gen_result.text.strip():
            return DTP_NARRATIVE_FALLBACK

        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=self.artefact_kind,
        ))

        return self._parse_synthesis(gen_result.text)

    @staticmethod
    def _parse_synthesis(text: str) -> str:
        """Extract the <synthesis>...</synthesis> block from the model
        response. Falls back to the whole stripped text if the tag is
        absent, and to the canned descriptive sentence if nothing
        usable remains."""
        match = re.search(
            r'<synthesis>(.*?)</synthesis>', text, re.DOTALL | re.IGNORECASE,
        )
        if match:
            inner = match.group(1).strip()
            if inner:
                return inner
        stripped = text.strip()
        return stripped or DTP_NARRATIVE_FALLBACK

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------
    @staticmethod
    def _build_themes_prompt(prev_text: str, curr_text: str) -> str:
        """Theme-extraction prompt. Sanitisation: trim to 400 chars,
        " -> ', literal \\n -> space. Unchanged from the Phase E DTP."""
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
    def _build_narrative_prompt(current_module: str, signals: dict) -> str:
        """Structured dual-signal narrative prompt (design proposal §7.2).

        The model analyses each available signal in its own tagged block
        and then synthesises; only <synthesis> is surfaced to the
        teacher. The prompt is descriptive, not evaluative (design
        proposal §4.4): it asks for continuity and shift, never quality.

        The vertical block is omitted when no VCS is available (Acquire
        modules), so the prompt is well-formed with a single signal too.
        """
        blocks = []
        analysis_tags = []

        vertical = signals.get('vertical')
        if vertical:
            blocks.append(
                'VERTICAL comparison — same UNESCO competency, earlier '
                f"proficiency level (module {vertical['comparison_module']}) "
                f'vs the current module ({current_module}):\n'
                f"  increased: {DTPAgent._theme_line(vertical['themes']['increased_themes'])}\n"
                f"  decreased: {DTPAgent._theme_line(vertical['themes']['decreased_themes'])}\n"
                f"  stable: {DTPAgent._theme_line(vertical['themes']['stable_themes'])}"
            )
            analysis_tags.append(
                '<vertical_analysis>one sentence on the vertical '
                'comparison</vertical_analysis>'
            )

        temporal = signals.get('temporal')
        if temporal:
            blocks.append(
                'TEMPORAL comparison — the immediately preceding module '
                f"(module {temporal['comparison_module']}) vs the current "
                f'module ({current_module}):\n'
                f"  increased: {DTPAgent._theme_line(temporal['themes']['increased_themes'])}\n"
                f"  decreased: {DTPAgent._theme_line(temporal['themes']['decreased_themes'])}\n"
                f"  stable: {DTPAgent._theme_line(temporal['themes']['stable_themes'])}"
            )
            analysis_tags.append(
                '<temporal_analysis>one sentence on the temporal '
                'comparison</temporal_analysis>'
            )

        comparisons = '\n\n'.join(blocks)
        analysis_format = '\n'.join(analysis_tags)
        return (
            "You are describing a teacher's reflective development across "
            'modules. Describe only what changed; do not judge whether it '
            'is good or bad.\n\n'
            f'{comparisons}\n\n'
            'Reason about each comparison separately, then synthesise. '
            'Respond in exactly this format:\n'
            f'{analysis_format}\n'
            '<synthesis>One paragraph of about 60 words, plain prose, no '
            'bullet points. Start with "Across these modules, your '
            'reflection". Describe continuity and shift only. Do not '
            'frame the change as improvement, progress, advancement, or '
            'growing sophistication, nor as decline — describe what '
            'shifted, not whether the teacher is better or worse.</synthesis>'
        )

    # ------------------------------------------------------------------
    # Helpers (private)
    # ------------------------------------------------------------------
    @staticmethod
    def _theme_line(themes_list) -> str:
        """Render a theme list for the narrative prompt body."""
        return ', '.join(themes_list) if themes_list else 'none noted'

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Strip ```json fences from a model response."""
        if '```json' in text:
            return text.split('```json')[-1].split('```')[0].strip()
        if text.startswith('```'):
            return text[3:].split('```')[0].strip()
        return text

    @staticmethod
    def _empty_themes() -> dict:
        return {'increased': [], 'decreased': [], 'stable': []}
