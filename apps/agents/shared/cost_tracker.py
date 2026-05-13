"""
Per-call cost tracker for agents.

Today's monolith only records api_cost_eur for the RAG path (rag_queries.
api_cost_eur). RTM, DTP and Peer have zero cost visibility. Phase E.2
goal: every agent call produces a structured cost record, so the
dissertation can quote per-feature cost-per-user.

For Phase E commit 1 the tracker emits cost records through the audit
logger only — a future commit can promote this to a dedicated CostLog
table without changing the call-site API.
"""

from dataclasses import dataclass

from apps.agents.shared.audit import audit_log


@dataclass
class CostRecord:
    """One LLM call's cost accounting."""
    agent: str
    model: str
    tokens: int
    cost_eur: float
    artefact_kind: str = ''


def track(record: CostRecord) -> None:
    """Emit a cost record. Structured-log only in commit 1.

    Callers: BaseAIAgent._track_cost (default), or any sub-call inside a
    multi-step _do_generate that wants per-Gemini-call granularity.
    """
    audit_log(
        event='agent.cost',
        agent=record.agent,
        model=record.model,
        tokens=record.tokens,
        cost_eur=round(record.cost_eur, 8),
        artefact_kind=record.artefact_kind or None,
    )
