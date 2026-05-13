"""
ResearchInstrumentAgent — intermediate parent class for agents whose
outputs become part of the platform's research corpus.

Promoted in Phase E commit 3 when RTMAgent joined RAGFeedbackAgent as
the second concrete agent. Per the v2/v3/v4 design discipline ("don't
abstract until the second concrete reveals what is shared"), the
parent is intentionally thin — what matters is the type tag, not new
behaviour. Existing invariants are inherited from BaseAIAgent.

What this class communicates:

  1. The agent's output (whether persisted via generate() or proposed
     via extract()) eventually becomes research data. A future
     dashboard listing research-instrument agents — vs. service
     agents like the XAIAgent introduced in D.3 — can use
     `isinstance(agent, ResearchInstrumentAgent)` to filter.

  2. The agent operates on a teacher's reflection or related learning
     artefact, not on another agent's output. This rules out service
     agents (XAI explains other agents' outputs; cost-aggregator
     summarises across agents).

  3. The agent is in scope for the dissertation's "multi-agent
     architecture" chapter. Service agents are in scope for the
     "explainability / cross-cutting concerns" chapter.

What this class does NOT add:

  - No new abstractmethod. RAG and RTM have different persistence
    lifecycles (RAG persists immediately in generate(); RTM is
    extract-only). There is no method both must implement that is
    not already required by BaseAIAgent.

  - No new instance state.

  - No constructor.

If a third concrete reveals additional shared behaviour (e.g. a
common "anonymise for research corpus" step), promote it here at
that point — not speculatively.
"""

from apps.agents.base import BaseAIAgent


class ResearchInstrumentAgent(BaseAIAgent):
    """Marker class for agents whose outputs feed the research corpus.

    Subclasses: RAGFeedbackAgent (Phase E commit 1, refactored in
    commit 3), RTMAgent (Phase E commit 3). DTPAgent and
    PeerSynthesisAgent will join in commits 5 and 7 respectively.

    Service agents (future XAIAgent, cost-aggregator, etc.) inherit
    directly from BaseAIAgent — not from this class.
    """
    pass
