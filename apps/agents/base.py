"""
BaseAIAgent — the contract every agent in apps/agents/ subclasses.

Establishes by construction the invariants from Phase E proposal v2 §3:

  CP-9 (atomic save + provenance):
        _do_generate -> _persist -> _record_provenance run inside one
        transaction.atomic block. If any step raises, the whole block
        rolls back — no AI output without provenance.

  CP-7 (idempotent provenance):
        _record_provenance delegates to compliance.services.record_ai_
        provenance, which uses get_or_create keyed by (artefact_kind,
        artefact_pk). Re-running a generate call after a partial failure
        is safe.

  CP-3 (RETURNING-only PK):
        Subclasses that own raw INSERTs must obtain the new PK via
        RETURNING id — never SELECT lastval(). Enforced by convention,
        not by code, but the unit test for RAGFeedbackAgent verifies it.

  Cost tracking on 4/4 paths:
        _track_cost is called for every successful generate(). Today the
        monolith only records cost on the RAG path; the base class lifts
        this to all subclasses (commit 1 wires RAG; later commits wire
        RTM/DTP/Peer when they migrate).

The class is abstract — direct instantiation raises NotImplementedError
via _do_generate. Subclasses must set `artefact_kind` (one of the
choices from AIArtefactProvenance.ARTEFACT_KIND_CHOICES).
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Optional

from django.db import transaction
from django.utils import timezone

from apps.agents.shared.audit import audit_log
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.llm_client import GenerationResult


class BaseAIAgent(ABC):
    """Abstract parent for every agent that produces an AI artefact.

    Subclass contract:
      - set `artefact_kind` to a value from
        AIArtefactProvenance.ARTEFACT_KIND_CHOICES
      - implement `_do_generate(**kwargs)` returning the artefact payload
      - either rely on the default `_persist` (assigns to save_target.
        save_field and calls .save) or override for custom persistence
      - optionally override `_record_provenance` if multiple provenance
        rows are needed (RAG writes both 'rag_query' and 'rag_feedback')

    Public API: one method, `generate()`. Everything else is internal.
    """

    artefact_kind: ClassVar[str] = ''
    model_name: ClassVar[str] = 'gemini-2.5-flash'

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def generate(
        self,
        *,
        user,
        module=None,
        save_target=None,
        save_field: Optional[str] = None,
        **kwargs,
    ):
        """Orchestrate a single agent run.

        Args:
            user: auth_user for provenance attribution. Required.
            module: optional Module FK for provenance attribution.
            save_target: model instance the artefact attaches to (e.g.
                UserModuleProgress). May be None if subclass _persist
                creates new rows instead of mutating an existing one.
            save_field: attribute name on save_target to receive the
                artefact. Ignored if subclass overrides _persist.
            **kwargs: passed through to _do_generate.

        Returns: the artefact payload produced by _do_generate.

        Raises: whatever _do_generate / _persist raise. Both happen
        inside transaction.atomic so a failure rolls back both the
        artefact write and any provenance row written before the failure.
        """
        if not self.artefact_kind:
            raise NotImplementedError(
                f"{type(self).__name__} must set artefact_kind on the class."
            )

        audit_log(
            'agent.generate.start',
            agent=type(self).__name__,
            artefact_kind=self.artefact_kind,
            user_id=getattr(user, 'id', None),
            module_id=getattr(module, 'id', None),
        )

        with transaction.atomic():
            output = self._do_generate(**kwargs)
            artefact_pk = self._persist(
                output=output,
                save_target=save_target,
                save_field=save_field,
            )
            self._record_provenance(
                output=output,
                artefact_pk=artefact_pk,
                user=user,
                module=module,
            )

        self._track_cost(output=output)
        audit_log(
            'agent.generate.complete',
            agent=type(self).__name__,
            artefact_kind=self.artefact_kind,
            artefact_pk=str(artefact_pk),
        )
        return output

    # ------------------------------------------------------------------
    # Subclass hooks
    # ------------------------------------------------------------------
    @abstractmethod
    def _do_generate(self, **kwargs) -> Any:
        """Produce the artefact payload. Must be overridden by subclasses.

        Marked @abstractmethod so direct instantiation of BaseAIAgent
        raises TypeError (Python ABC contract). Subclasses become
        instantiable once they provide an implementation.
        """

    def _persist(self, *, output, save_target, save_field) -> Any:
        """Default persistence: setattr save_target, save, return its pk.

        Subclasses with custom persistence (RAG inserts into rag_queries;
        future agents may write to dedicated tables) override this method
        and return the pk of the row that the primary provenance entry
        should reference.
        """
        if save_target is None:
            raise ValueError(
                f"{type(self).__name__}.generate requires save_target "
                "for the default _persist; override _persist or pass save_target."
            )
        if save_field is None:
            raise ValueError(
                f"{type(self).__name__}.generate requires save_field "
                "for the default _persist; override _persist or pass save_field."
            )
        setattr(save_target, save_field, output)
        save_target.save(update_fields=[save_field])
        return save_target.pk

    def _record_provenance(self, *, output, artefact_pk, user, module) -> None:
        """Default provenance: one row for self.artefact_kind / artefact_pk.

        Subclasses that produce multiple provenance rows per call (RAG)
        override and write each row via record_ai_provenance directly.
        All writes must be in this method so they share the surrounding
        transaction.atomic from generate().
        """
        from apps.compliance.services import record_ai_provenance
        record_ai_provenance(
            artefact_kind=self.artefact_kind,
            artefact_pk=artefact_pk,
            user=user,
            module=module,
            model_name=self.model_name,
            generated_at=timezone.now(),
        )

    def _track_cost(self, *, output) -> None:
        """Default cost tracking: read tokens/cost off a GenerationResult.

        If `output` is a GenerationResult, record its fields. Composite
        outputs (DTP, Peer) bypass this and call cost_tracker.track from
        within _do_generate for per-Gemini-call granularity.
        """
        if isinstance(output, GenerationResult):
            track_cost(CostRecord(
                agent=type(self).__name__,
                model=output.model,
                tokens=output.tokens_estimate,
                cost_eur=output.cost_eur_estimate,
                artefact_kind=self.artefact_kind,
            ))
