"""
PeerSynthesisAgent — Cross-Specialty Peer Synthesizer.

Phase E commit 7 — second multi-step orchestration agent (after DTP).
Given a teacher's current reflection, finds the most similar reflections
from teachers in DIFFERENT subject areas (cross-specialty) via pgvector
similarity, then asks Gemini to synthesize a 200-250-word cross-
disciplinary insight grounded in the retrieved peer reflections. The
synthesis is persisted to UserModuleProgress.reflection_peer_synthesis
as HTML (markdown-rendered).

Architectural notes:

  - Multi-step (like DTP): embed -> similarity-search -> Gemini call.
    Two LLM-touching operations (one embed, one generate); both emit
    individual 'agent.cost' events for granularity.

  - Three distinct failure modes, each surfacing a different exception
    so the view layer can render the right user-facing message:

      RuntimeError                   -> embed or Gemini failed (LLM-side)
      NoPeerReflectionsAvailable     -> empty similarity result set
                                        (operationally fine — first
                                         user, niche subject, etc.)
      anything else                  -> save/provenance failure
                                        (CP-9 atomic rolled back)

    Critically, NoPeerReflectionsAvailable is NOT a None-return from
    _do_generate. If the agent returned None, BaseAIAgent.generate
    would proceed to _persist and _record_provenance — writing a
    provenance row for an absent synthesis. That would violate the
    CP-9 invariant ("no AI output without provenance, no provenance
    without AI output"). Raising instead aborts the atomic before
    any DB write.

  - Persistence: markdown -> HTML conversion inside _persist (mirrors
    today's flow at views.py:2217-2226). The agent owns the rendering
    decision because the storage format is part of the persistence
    contract.

  - One provenance row per generate() — the default
    _record_provenance suffices. The composite output is a single
    synthesis string, unlike RAG's dual-row case.

Diagnostic for commit 8 (per v8 §8 Aspect 2):

  Inspecting the existing peer-synthesis write path at
  apps/modules/views.py:2224-2234 confirms a single transaction.atomic
  block wrapping progress.save(update_fields=['reflection_peer_
  synthesis']) with record_ai_provenance('peer_synthesis', ...). No
  inconsistency window. Unlike commit 6's DTP path, there is NO
  tolerant inner try/except papering over save failures — the outer
  Exception catch returns success=False honestly.

  --> Commit 8 will be PRESERVATION (NOT hybrid).
  Same architectural shape as commit 4 (RTM cutover). No secondary
  UX tightening to surface.

Monolith oddity preserved verbatim — OLD-API-only Gemini-2.5 -> 1.5
Flash fallback inside synthesize_peer_insight (rag_query_system.py:
404-416). Production runs the NEW API which has no fallback; the
agent matches production. Filed in v9 §11 cleanup list for commit 9.
"""

import logging
from typing import Optional

import markdown

from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.db import dict_cursor
from apps.agents.shared.llm_client import GenerationResult, get_llm_client


# Default similarity-search top_k. Live view passes top_k=2; the
# constant keeps the default visible at the agent layer.
PEER_DEFAULT_TOP_K = 2

# Per-peer reflection-text budget in the prompt. Each retrieved peer
# is truncated to this many chars + "..." to bound prompt size.
PEER_REFLECTION_PROMPT_BUDGET = 400


class NoPeerReflectionsAvailable(Exception):
    """Raised when the similarity search returns no cross-specialty
    peers for the current user's reflection.

    Operationally distinct from RuntimeError (LLM failure) and from
    generic Exception (save/provenance failure). The view layer
    catches each separately so user-visible messages are accurate:
      - "No peer reflections found" for this exception
      - "Peer synthesis temporarily unavailable" for RuntimeError
      - "Synthesis could not be saved. Please try again." for the rest
    """
    pass


class PeerSynthesisAgent(ResearchInstrumentAgent):
    """Cross-specialty peer synthesizer.

    Public API: generate() — owns the atomic block. Calling extract()
    technically works but produces an unsaved composite; intended use
    is generate().

    Provenance: one row per call, kind='peer_synthesis',
    artefact_pk=progress.pk. CP-7 idempotent on (kind, pk).
    """

    artefact_kind = 'peer_synthesis'
    model_name = 'gemini-2.5-flash'

    # ------------------------------------------------------------------
    # Multi-step orchestration
    # ------------------------------------------------------------------
    def _do_generate(
        self,
        *,
        reflection_text: str,
        teacher_context: dict,
        top_k: int = PEER_DEFAULT_TOP_K,
        module_id: Optional[int] = None,
    ) -> str:
        """Embed -> similarity-search -> Gemini synthesis.

        Returns the raw markdown synthesis text. The caller (or
        _persist) is responsible for markdown->HTML rendering.

        Raises:
            RuntimeError                 — embed failed or Gemini failed
            NoPeerReflectionsAvailable   — search returned zero peers
        """
        logger = logging.getLogger(__name__)
        client = get_llm_client()

        # Step 1: embed the user's reflection
        embedding = client.embed(reflection_text)
        if embedding is None:
            raise RuntimeError(
                'PeerSynthesisAgent: embedding step returned None.'
            )

        # Step 2: cross-specialty similarity search
        user_subject = teacher_context.get('subject', 'General')
        peers = self._search_peer_reflections(
            query_embedding=embedding,
            user_subject=user_subject,
            top_k=top_k,
            module_id=module_id,
        )
        if not peers:
            # Distinct from RuntimeError: the LLM is fine, the user
            # is fine, there simply are no cross-specialty peers in
            # the corpus right now. View renders an informative
            # message and skips the peer card. No CP-9 violation
            # (no provenance row written because we never enter
            # _persist / _record_provenance).
            raise NoPeerReflectionsAvailable(
                f'No cross-specialty peer reflections found for subject '
                f'{user_subject!r}.'
            )

        # Step 3: Gemini synthesis
        prompt = self._build_prompt(reflection_text, teacher_context, peers)
        gen_result = client.generate(prompt, model=self.model_name)
        if gen_result is None:
            raise RuntimeError(
                'PeerSynthesisAgent: Gemini generation returned None.'
            )

        # Per-Gemini-call cost event for granularity (same pattern as
        # DTP's two-call cost tracking).
        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=self.artefact_kind,
        ))

        return gen_result.text

    # ------------------------------------------------------------------
    # Persistence — markdown to HTML, then default-style setattr/save
    # ------------------------------------------------------------------
    def _persist(self, *, output: str, save_target, save_field: Optional[str]):
        """Render markdown -> HTML, write to save_target.<save_field>.

        Mirrors views.py:2217-2226 byte-identically:
            html = markdown.markdown(text, extensions=['extra', 'nl2br'])
            progress.reflection_peer_synthesis = html
            progress.save(update_fields=[...])
        """
        if save_target is None or save_field is None:
            raise ValueError(
                'PeerSynthesisAgent.generate requires save_target '
                "(UserModuleProgress) and save_field "
                "(e.g. 'reflection_peer_synthesis')."
            )
        html = markdown.markdown(output, extensions=['extra', 'nl2br'])
        setattr(save_target, save_field, html)
        save_target.save(update_fields=[save_field])
        return save_target.pk

    # ------------------------------------------------------------------
    # Cost tracking — overridden to no-op. Cost is recorded inline in
    # _do_generate at per-Gemini-call granularity (same pattern as
    # DTP). The default base-class _track_cost would see a plain str
    # (not a GenerationResult) and silently no-op anyway, but the
    # explicit override documents intent.
    # ------------------------------------------------------------------
    def _track_cost(self, *, output) -> None:
        return None

    # ==================================================================
    # Public helpers — static for testability + parity with monolith
    # ==================================================================

    # ------------------------------------------------------------------
    # Cross-specialty pgvector search
    # ------------------------------------------------------------------
    @staticmethod
    def _search_peer_reflections(
        *,
        query_embedding,
        user_subject: str,
        top_k: int = PEER_DEFAULT_TOP_K,
        module_id: Optional[int] = None,
    ) -> list[dict]:
        """Vector similarity search excluding the user's own subject.

        Behaviour-identical to rag_query_system.search_peer_reflections.
        Two SQL variants by module_id presence kept verbatim. Uses the
        shared dict_cursor helper (Django connection) — replaces the
        monolith's raw psycopg2 connection-passing pattern, matching
        the Phase E.2 DB-idiom unification goal.
        """
        with dict_cursor() as cur:
            if module_id:
                cur.execute(
                    """
                    SELECT
                        id,
                        subject_area,
                        grade_level,
                        experience_years,
                        reflection_text,
                        reflection_embedding <=> %s::vector AS distance,
                        is_seed_data
                    FROM peer_reflections
                    WHERE LOWER(subject_area) != LOWER(%s)
                      AND module_id = %s
                    ORDER BY distance
                    LIMIT %s;
                    """,
                    (query_embedding, user_subject, module_id, top_k),
                )
            else:
                cur.execute(
                    """
                    SELECT
                        id,
                        subject_area,
                        grade_level,
                        experience_years,
                        reflection_text,
                        reflection_embedding <=> %s::vector AS distance,
                        is_seed_data
                    FROM peer_reflections
                    WHERE LOWER(subject_area) != LOWER(%s)
                    ORDER BY distance
                    LIMIT %s;
                    """,
                    (query_embedding, user_subject, top_k),
                )
            return cur.fetchall()

    # ------------------------------------------------------------------
    # Prompt construction — byte-identical to monolith
    # ------------------------------------------------------------------
    @staticmethod
    def _build_prompt(
        user_reflection: str,
        user_context: dict,
        peer_reflections: list[dict],
    ) -> str:
        """Build the synthesis prompt verbatim from
        rag_query_system.synthesize_peer_insight. Each retrieved peer
        is rendered as a labelled block with reflection truncated to
        400 chars + literal '...'.
        """
        peer_examples = []
        for i, peer in enumerate(peer_reflections, 1):
            peer_examples.append(
                f"**Colleague {i} ({peer['subject_area']} teacher, "
                f"{peer['grade_level']}):**\n"
                f"{peer['reflection_text'][:PEER_REFLECTION_PROMPT_BUDGET]}...\n"
            )

        peer_context = '\n'.join(peer_examples)
        user_name = user_context.get('name', 'Colleague')
        user_subject = user_context.get('subject', 'your subject')

        return f"""You are facilitating cross-disciplinary professional learning among teachers.

CONTEXT: {user_name} is a {user_subject} teacher who just reflected on their AI learning experience. You have identified similar reflections from colleagues in OTHER subject areas who had parallel insights.

USER'S REFLECTION:
{user_reflection}

SIMILAR REFLECTIONS FROM COLLEAGUES IN OTHER SUBJECTS:
{peer_context}

TASK:
Write a brief, engaging synthesis (200-250 words) that:

1. **Opens warmly:** "I noticed something interesting about your reflection..."
2. **Names the pattern:** Identify the pedagogical theme connecting these reflections (e.g., "concern about student dependency," "excitement about differentiation," "worry about assessment integrity")
3. **Draws cross-specialty connection:** Show how a colleague in a DIFFERENT subject wrestled with the same issue
4. **Highlights transferable insight:** Extract one concrete strategy or perspective from the peer reflection that could apply to {user_subject}
5. **Closes with invitation:** Encourage continued cross-disciplinary thinking

STYLE:
- Collegial, not evaluative
- Specific, not generic
- Cross-disciplinary learning framed as valuable professional growth
- Use **bold** for key pedagogical terms
- Keep it concise and actionable

IMPORTANT:
- Do NOT reveal which specific colleague you're quoting (anonymity)
- Frame as "a colleague teaching [Subject]" not "Teacher X"
- Focus on the IDEA, not the person
"""
