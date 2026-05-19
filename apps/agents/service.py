"""
ServiceAgent — intermediate parent for agents that operate on the
outputs of other agents rather than on a teacher's reflection.

Introduced in Phase D.3b together with XAIAgent, its first concrete
member. ServiceAgent is a sibling of ResearchInstrumentAgent: both are
thin marker classes under BaseAIAgent.

The distinction this class draws
--------------------------------
A ResearchInstrumentAgent (RAGFeedbackAgent, RTMAgent, DTPAgent,
PeerSynthesisAgent) operates on a teacher's reflection — it reads what
the teacher wrote and produces a new artefact about their learning.
Its output is primary research data.

A ServiceAgent operates on another agent's output. It does not generate
primary research data; it serves, summarises, or explains the work of
other agents. The XAIAgent reads the DTP's stored composite and explains
it — it never re-reads the teacher's reflection to form an opinion of
its own (explanation faithfulness; see
proodos_files/DTP_XAI_NARRATIVE_DESIGN_PROPOSAL_v1_20260519.md §4).

What this class communicates
----------------------------
  1. Cross-cutting code (dashboards, audit aggregators) can filter
     agents by `isinstance(agent, ServiceAgent)` vs
     `isinstance(agent, ResearchInstrumentAgent)`.
  2. The two branches map onto two dissertation concerns: research
     instruments belong to the multi-agent architecture chapter;
     service agents belong to the explainability / cross-cutting
     concern (architecture chapter §4.5).

What this class does NOT add
----------------------------
No new abstractmethod, no instance state, no constructor. Like
ResearchInstrumentAgent it is intentionally thin; it earns its place
through the type tag and the docstring contract. Behaviour and
invariants are inherited from BaseAIAgent.

A future second concrete service agent — e.g. a cost-aggregator, or a
validator / refiner agent of the kind described by Guo et al. (2024) —
joins here without restructuring the hierarchy.
"""

from apps.agents.base import BaseAIAgent


class ServiceAgent(BaseAIAgent):
    """Marker class for agents that operate on other agents' outputs.

    Subclasses: XAIAgent (Phase D.3b — explains the DTP composite).

    Research-instrument agents inherit from ResearchInstrumentAgent and
    operate on a teacher's reflection; service agents inherit from this
    class and operate on the output of another agent.
    """
    pass
