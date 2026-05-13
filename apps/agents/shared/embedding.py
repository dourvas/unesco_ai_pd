"""
Standalone embedding helper.

Re-exposes `embed_query` for non-agent callers (apps/modules/views.py:848,
:2178) and for shared use across agents. Delegates to LLMClient so the
NEW/OLD Gemini SDK dispatch lives in one place.

Once Phase E commits 2-10 land, the four import sites of `embed_query` from
rag_query_system shift to this module:
    from apps.agents.shared.embedding import embed_query
"""

from apps.agents.shared.llm_client import (
    DEFAULT_EMBEDDING_DIM,
    get_llm_client,
)


def embed_query(text: str, output_dim: int = DEFAULT_EMBEDDING_DIM):
    """Return a 768-d embedding for `text`, or None on failure.

    Behaviour-identical to rag_query_system.embed_query: prints success/error
    diagnostics, returns None on failure rather than raising. Callers in
    views.py rely on the None-check pattern.
    """
    embedding = get_llm_client().embed(text, output_dim=output_dim)
    if embedding is not None:
        print(f"OK Embedded to {len(embedding)}-dimensional vector")
    return embedding
