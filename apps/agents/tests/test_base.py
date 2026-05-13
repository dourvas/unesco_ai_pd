"""Contract tests for BaseAIAgent.

Verifies the invariants spelled out in PHASE_E_DESIGN_PROPOSAL_v2.md §3
Decision 3 + §7 commit 1 acceptance criteria.
"""

import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.agents.base import BaseAIAgent
from apps.agents.shared.llm_client import GenerationResult
from apps.compliance.models import AIArtefactProvenance
from apps.modules.models import Module, UserModuleProgress


# ----------------------------------------------------------------------
# Test-only subclass: minimal concrete agent for contract verification.
# Uses 'rag_feedback' as artefact_kind because the model's choices field
# only accepts the six canonical kinds (see AIArtefactProvenance.
# ARTEFACT_KIND_CHOICES). The base class doesn't care which one — we
# just need a valid value.
# ----------------------------------------------------------------------
class _MinimalAgent(BaseAIAgent):
    artefact_kind = 'rag_feedback'

    def _do_generate(self, *, value: str = 'hello'):
        return value


class _PersistOverrideAgent(BaseAIAgent):
    """Demonstrates the override path: skip default _persist entirely,
    return a static pk for provenance."""
    artefact_kind = 'rag_feedback'
    static_pk = 9999

    def _do_generate(self, **kwargs):
        return 'payload'

    def _persist(self, *, output, save_target, save_field):
        return self.static_pk


class _ProvenanceRaisingAgent(BaseAIAgent):
    """Forces _record_provenance to raise so we can verify rollback."""
    artefact_kind = 'rag_feedback'

    def _do_generate(self, **kwargs):
        return 'payload'

    def _record_provenance(self, **kwargs):
        raise RuntimeError('simulated provenance failure')


class BaseAIAgentAbstractnessTest(TestCase):
    def test_direct_instantiation_raises_typeerror(self):
        """ABCMeta enforces — BaseAIAgent() is not instantiable."""
        with self.assertRaises(TypeError):
            BaseAIAgent()


class BaseAIAgentContractTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('agent_user', password='pw')
        cls.module = Module.objects.create(
            code='AGTEST', title='Agent contract test module',
            description='t', order_index=997,
            unesco_aspect='ethics', proficiency_level='Acquire',
            is_published=True,
        )

    def _make_progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def test_missing_artefact_kind_raises(self):
        class _Naked(BaseAIAgent):
            artefact_kind = ''
            def _do_generate(self, **kwargs): return 'x'
        progress = self._make_progress()
        with self.assertRaises(NotImplementedError):
            _Naked().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_rag_feedback',
            )

    def test_default_persist_assigns_and_saves(self):
        progress = self._make_progress()
        _MinimalAgent().generate(
            user=self.user, module=self.module,
            save_target=progress, save_field='reflection_rag_feedback',
            value='hi there',
        )
        progress.refresh_from_db()
        self.assertEqual(progress.reflection_rag_feedback, 'hi there')

    def test_default_persist_writes_one_provenance_row(self):
        progress = self._make_progress()
        before = AIArtefactProvenance.objects.count()
        _MinimalAgent().generate(
            user=self.user, module=self.module,
            save_target=progress, save_field='reflection_rag_feedback',
            value='hi',
        )
        rows = AIArtefactProvenance.objects.filter(
            artefact_kind='rag_feedback', artefact_pk=str(progress.pk),
        )
        self.assertEqual(rows.count(), 1)
        self.assertEqual(AIArtefactProvenance.objects.count(), before + 1)
        self.assertEqual(rows.first().model_name, 'gemini-2.5-flash')
        self.assertEqual(rows.first().user_id, self.user.id)
        self.assertEqual(rows.first().module_id, self.module.id)

    def test_overridden_persist_is_honoured(self):
        progress = self._make_progress()
        _PersistOverrideAgent().generate(
            user=self.user, module=self.module,
            save_target=progress, save_field=None,
        )
        # static_pk produces the provenance row PK.
        self.assertTrue(
            AIArtefactProvenance.objects.filter(
                artefact_kind='rag_feedback',
                artefact_pk=str(_PersistOverrideAgent.static_pk),
            ).exists()
        )

    def test_provenance_failure_rolls_back_persist(self):
        """CP-9 invariant: a raise inside _record_provenance must roll
        back the prior _persist write so the source field is unchanged."""
        progress = self._make_progress()
        progress.reflection_rag_feedback = 'untouched'
        progress.save(update_fields=['reflection_rag_feedback'])

        with self.assertRaises(RuntimeError):
            _ProvenanceRaisingAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_rag_feedback',
                value='this should not stick',
            )

        progress.refresh_from_db()
        self.assertEqual(
            progress.reflection_rag_feedback,
            'untouched',
            'CP-9: persist must roll back when provenance raises.',
        )

    def test_audit_log_emits_start_and_complete(self):
        progress = self._make_progress()
        with self.assertLogs('agents.audit', level='INFO') as cm:
            _MinimalAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_rag_feedback',
            )
        events = [r.getMessage() for r in cm.records]
        self.assertIn('agent.generate.start', events)
        self.assertIn('agent.generate.complete', events)

    def test_cost_track_fires_only_for_generation_result(self):
        """Default _track_cost is a no-op unless _do_generate returned a
        GenerationResult. _MinimalAgent returns a plain str — no cost log."""
        progress = self._make_progress()
        with self.assertLogs('agents.audit', level='INFO') as cm:
            _MinimalAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_rag_feedback',
            )
        events = [r.getMessage() for r in cm.records]
        self.assertNotIn('agent.cost', events)
