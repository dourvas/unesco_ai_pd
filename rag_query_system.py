"""
rag_query_system — Phase E TOMBSTONE (commit 9 of 10).

All AI-pipeline functions previously defined in this module were
deleted in Phase E commit 9 (2026-05-13). The behaviour now lives in
the apps/agents/ package, organised around BaseAIAgent's two public
entry points (generate / extract):

    apps/agents/rag_feedback.py        RAGFeedbackAgent (was process_reflection
                                       + generate_feedback + store_rag_query
                                       + search_similar_chunks + embed_query)
    apps/agents/rtm.py                 RTMAgent (was extract_tensions
                                       + validate_tensions)
    apps/agents/dtp.py                 DTPAgent (was compute_dtp
                                       + compute_development_signal
                                       + extract_development_themes
                                       + generate_development_narrative)
    apps/agents/peer.py                PeerSynthesisAgent (was
                                       synthesize_peer_insight
                                       + search_peer_reflections)
    apps/agents/shared/llm_client.py   LLMClient.embed / .generate (was the
                                       NEW/OLD google.genai SDK dispatch
                                       duplicated at 5 call sites)
    apps/agents/shared/embedding.py    embed_query (was the standalone
                                       wrapper used by non-agent callers)
    apps/agents/shared/json_repair.py  clean_json_response

This file is scheduled for outright deletion in Phase E commit 10,
along with the now-unused `sys.path.append` hack at the top of
apps/modules/views.py (already removed in commit 9). The file is
kept as a tombstone for one commit so the deletion narrative in git
history is unambiguous.

Do not reintroduce functions here. Extend the agent hierarchy in
apps/agents/ instead.
"""
