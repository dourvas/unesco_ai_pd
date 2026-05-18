"""
RAGFeedbackAgent — generates reflection feedback grounded in retrieved
UNESCO framework chunks.

Behaviour parity with rag_query_system.process_reflection +
generate_feedback + store_rag_query. Phase E commit 1 lands this agent
alongside the monolith; commit 2 will swap apps/modules/views.py:812 to
call the agent instead. Tests verify byte-identical prompt construction
and identical rag_queries row contents given the same input + mocked
Gemini output.

CP-3 note: rag_queries pk is obtained via `RETURNING id` on the INSERT
inside _persist, never via SELECT lastval(). The unit test asserts the
SQL string contains `RETURNING id` literally.

Two-row provenance: this agent writes BOTH provenance rows that today
live in two separate atomic blocks (rag_query_system.store_rag_query
writes 'rag_query'; apps/modules/views.py:898 writes 'rag_feedback').
After the refactor they share one atomic block — a tighter invariant
than today.
"""

import json
import time
from typing import Any, Optional

import markdown

from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.db import dict_cursor
from apps.agents.shared.llm_client import GenerationResult, get_llm_client
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost


RAG_MAX_OUTPUT_TOKENS = 2500


class RAGFeedbackAgent(ResearchInstrumentAgent):
    """Reflection feedback generator with pgvector retrieval grounding.

    Public artefact: a UserModuleProgress row with reflection_rag_feedback
    populated (HTML). Secondary artefact: a rag_queries row carrying the
    raw markdown, embedding, retrieved chunks and cost telemetry.

    Provenance rows written:
        1. ('rag_query',    rag_queries.id) — telemetry row
        2. ('rag_feedback', progress.pk)    — user-visible HTML
    """

    artefact_kind = 'rag_feedback'  # primary kind for the dissertation/UI

    # Convenience constant — also the same string used by
    # apps/modules/views.py:23 (PROVENANCE_MODEL_NAME). Kept in sync.
    model_name = 'gemini-2.5-flash'

    def __init__(self):
        # Per-call state. RAGFeedbackAgent instances are single-use:
        # construct, call generate(), discard. These attrs let _persist
        # hand the rag_queries pk to _record_provenance and _track_cost
        # without changing the BaseAIAgent contract signature.
        self._rag_query_pk: Optional[int] = None
        self._last_gen_result: Optional[GenerationResult] = None

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------
    def _do_generate(
        self,
        *,
        reflection_text: str,
        teacher_context: dict,
        top_k: int = 5,
        module_id: Optional[int] = None,
    ) -> dict:
        """Embed reflection, retrieve top-k chunks, generate feedback.

        Returns a composite dict containing every field _persist needs:
            - reflection_text:  passed back so _persist doesn't need it as a kwarg
            - teacher_context:  dict serialized into rag_queries.teacher_context
            - embedding:        768-d vector, stored in rag_queries.query_embedding
            - chunks:           retrieved similarity rows
            - raw_feedback:     Gemini-generated markdown
            - gen_result:       GenerationResult with cost/token accounting
            - processing_time_ms: wall-clock duration of the RAG work
        """
        start_time = time.perf_counter()
        client = get_llm_client()

        embedding = client.embed(reflection_text)
        if embedding is None:
            raise RuntimeError("RAGFeedbackAgent: embedding step returned None")

        subject = teacher_context.get('subject')
        if subject:
            subject = subject.lower()
        chunks = self._search_similar_chunks(
            query_embedding=embedding,
            top_k=top_k,
            module_id=module_id,
            subject=subject,
        )

        prompt = self._build_prompt(reflection_text, teacher_context, chunks)
        gen_result = client.generate(
            prompt,
            model=self.model_name,
            max_output_tokens=RAG_MAX_OUTPUT_TOKENS,
        )
        if gen_result is None:
            raise RuntimeError("RAGFeedbackAgent: Gemini generation returned None")

        self._last_gen_result = gen_result
        # Wall-clock processing time for the rag_queries telemetry row.
        # The live table has CHECK (processing_time_ms IS NULL OR > 0);
        # max(1, ...) keeps it positive even for a sub-millisecond run.
        # Restores the timing the monolith recorded — Phase E dropped it
        # and inserted a hardcoded 0, which the live CHECK rejects.
        processing_time_ms = max(
            1, round((time.perf_counter() - start_time) * 1000),
        )
        return {
            'reflection_text': reflection_text,
            'teacher_context': teacher_context,
            'embedding': embedding,
            'chunks': chunks,
            'raw_feedback': gen_result.text,
            'gen_result': gen_result,
            'processing_time_ms': processing_time_ms,
        }

    # ------------------------------------------------------------------
    # Persistence — overrides default
    # ------------------------------------------------------------------
    def _persist(self, *, output: dict, save_target, save_field: Optional[str]) -> Any:
        """Insert rag_queries row + assign HTML feedback to save_target.

        Order matters for CP-9: rag_queries INSERT first (we need its
        RETURNING id for the 'rag_query' provenance row), then the
        save_target update. Both writes share the outer transaction.atomic
        opened by BaseAIAgent.generate.

        Returns save_target.pk (the primary artefact pk for 'rag_feedback'
        provenance). The 'rag_query' pk is stashed on self for
        _record_provenance.
        """
        if save_target is None or save_field is None:
            raise ValueError(
                "RAGFeedbackAgent.generate requires save_target (e.g. "
                "UserModuleProgress) and save_field (e.g. "
                "'reflection_rag_feedback')."
            )

        user_id = save_target.user_id
        module_id = save_target.module_id

        gen_result: GenerationResult = output['gen_result']
        chunks_payload = [
            {
                'chunk_id': c['id'],
                'distance': float(c['distance']),
                'title': c['title'],
                'text_preview': c['chunk_text'][:200],
            }
            for c in output['chunks']
        ]

        with dict_cursor() as cur:
            # CP-3: pk from RETURNING id, never from SELECT lastval().
            cur.execute(
                """
                INSERT INTO rag_queries (
                    user_id, module_id, reflection_text, teacher_context,
                    query_embedding, retrieved_chunks, num_chunks_retrieved,
                    generated_response, generation_tokens,
                    processing_time_ms, api_cost_eur,
                    created_at, updated_at
                )
                VALUES (%s, %s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id;
                """,
                (
                    user_id,
                    module_id,
                    output['reflection_text'],
                    json.dumps(output['teacher_context']),
                    output['embedding'],
                    json.dumps(chunks_payload),
                    len(output['chunks']),
                    output['raw_feedback'],
                    gen_result.tokens_estimate,
                    output['processing_time_ms'],
                    gen_result.cost_eur_estimate,
                ),
            )
            row = cur.fetchone()
            self._rag_query_pk = row['id']

        feedback_html = markdown.markdown(
            output['raw_feedback'], extensions=['extra', 'nl2br'],
        )
        setattr(save_target, save_field, feedback_html)
        save_target.save(update_fields=[save_field])

        # Expose the HTML on `output` so callers (and tests) can read it
        # without re-rendering.
        output['feedback_html'] = feedback_html
        output['rag_query_pk'] = self._rag_query_pk
        return save_target.pk

    # ------------------------------------------------------------------
    # Provenance — overrides default (writes TWO rows)
    # ------------------------------------------------------------------
    def _record_provenance(self, *, output, artefact_pk, user, module) -> None:
        """Write both 'rag_query' and 'rag_feedback' provenance rows."""
        from django.utils import timezone
        from apps.compliance.services import record_ai_provenance

        now = timezone.now()
        # Telemetry row provenance — references the new rag_queries pk.
        record_ai_provenance(
            artefact_kind='rag_query',
            artefact_pk=self._rag_query_pk,
            user=user,
            module=module,
            model_name=self.model_name,
            generated_at=now,
        )
        # User-visible feedback provenance — references UserModuleProgress.
        record_ai_provenance(
            artefact_kind='rag_feedback',
            artefact_pk=artefact_pk,
            user=user,
            module=module,
            model_name=self.model_name,
            generated_at=now,
        )

    # ------------------------------------------------------------------
    # Cost — overrides default to ensure cost is logged exactly once
    # ------------------------------------------------------------------
    def _track_cost(self, *, output) -> None:
        gen_result: GenerationResult = output['gen_result']
        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=self.artefact_kind,
        ))

    # ------------------------------------------------------------------
    # Internals — pgvector search + prompt construction
    # ------------------------------------------------------------------
    @staticmethod
    def _search_similar_chunks(
        *,
        query_embedding,
        top_k: int,
        module_id: Optional[int],
        subject: Optional[str],
    ) -> list[dict]:
        """Vector similarity search across document_chunks.

        Behaviour-identical to rag_query_system.search_similar_chunks.
        Three SQL variants by filter combination kept verbatim so the
        retrieval contract does not shift mid-refactor.
        """
        with dict_cursor() as cur:
            if module_id and subject:
                cur.execute(
                    """
                    SELECT
                        dc.id,
                        dc.chunk_text,
                        dc.embedding <=> %s::vector AS distance,
                        d.title,
                        d.document_type,
                        d.module_id,
                        dc.metadata->>'subject' as subject
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    WHERE (d.module_id IS NULL OR d.module_id = %s)
                      AND (dc.metadata->>'subject' IS NULL
                           OR LOWER(dc.metadata->>'subject') = LOWER(%s))
                    ORDER BY distance
                    LIMIT %s;
                    """,
                    (query_embedding, module_id, subject, top_k),
                )
            elif module_id:
                cur.execute(
                    """
                    SELECT
                        dc.id,
                        dc.chunk_text,
                        dc.embedding <=> %s::vector AS distance,
                        d.title,
                        d.document_type,
                        d.module_id,
                        dc.metadata->>'subject' as subject
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    WHERE d.module_id IS NULL OR d.module_id = %s
                    ORDER BY distance
                    LIMIT %s;
                    """,
                    (query_embedding, module_id, top_k),
                )
            else:
                cur.execute(
                    """
                    SELECT
                        dc.id,
                        dc.chunk_text,
                        dc.embedding <=> %s::vector AS distance,
                        d.title,
                        d.document_type,
                        dc.metadata->>'subject' as subject
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    ORDER BY distance
                    LIMIT %s;
                    """,
                    (query_embedding, top_k),
                )
            return cur.fetchall()

    @staticmethod
    def _build_prompt(
        reflection_text: str,
        teacher_context: dict,
        chunks: list[dict],
    ) -> str:
        """Construct the Gemini prompt — byte-identical to monolith.

        Kept as a pure function so the prompt-parity unit test can call
        it directly without standing up the full agent. The string must
        match rag_query_system.generate_feedback's prompt construction
        verbatim; the test asserts that.
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['title']}]\n{chunk['chunk_text']}\n"
            )
        context = "\n".join(context_parts)

        teacher_name = teacher_context.get('name', 'Colleague')

        return f"""You are a fellow educator and AI literacy mentor offering collegial reflective dialogue — not evaluation or coaching.

TEACHER CONTEXT:
- Name: {teacher_name}
- Subject: {teacher_context.get('subject', 'General')}
- Grade Level: {teacher_context.get('grade_level', 'Mixed')}
- Experience: {teacher_context.get('experience', 'Not specified')}

TEACHER'S REFLECTION:
{reflection_text}

RELEVANT FRAMEWORK CONTEXT:
{context}

TASK:
Write a warm, conversational response (250-300 words) as if you are a trusted colleague who has just read their reflection over coffee. Your response should:
1. Open with a personal greeting using their name
2. Reflect back what you genuinely found interesting or thought-provoking in what they wrote
3. Make a natural connection to 1-2 ideas from the UNESCO framework — not as requirements, but as "this reminded me of..."
4. Share 1-2 questions or possibilities worth exploring, framed as curiosity ("I wonder what would happen if...", "Have you considered...") rather than directives
5. Close with an encouraging observation about their thinking

CRITICAL TONE GUIDELINES:
- Never use: "you should", "you must", "you need to", "it's important that you"
- Instead use: "I noticed", "what strikes me", "I wonder", "one possibility might be"
- You are NOT grading or evaluating — you are thinking alongside them
- Avoid generic praise ("Great reflection!") — be specific about what you actually noticed

FORMAT YOUR RESPONSE IN MARKDOWN:
- Use **bold** for key terms and UNESCO competencies
- Use *italic* for emphasis
- Use bullet points sparingly — prefer flowing prose
- Use ## for section headers only if truly needed

Begin with: "Dear {teacher_name}," or "Hello {teacher_name}!" (choose based on tone)
End with: "Best,\nThe PROODOS Team"
"""
