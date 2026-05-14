"""RAGFeedbackAgent parity tests vs the monolith.

Two-layer invariant from PHASE_E_DESIGN_PROPOSAL_v2.md §5:
  (1) Prompt-identical with rag_query_system.generate_feedback
  (2) Behaviour-identical given mocked Gemini output

Layer 2 also verifies CP-3 (RETURNING id literal in the INSERT) and CP-9
(both provenance rows written inside one atomic block).
"""

import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.db import connection as django_conn
from django.test import TestCase

from apps.agents.rag_feedback import RAGFeedbackAgent
from apps.agents.shared.llm_client import GenerationResult
from apps.compliance.models import AIArtefactProvenance
from apps.modules.models import Module, UserModuleProgress


# Reuse the simplified DDL from apps/modules/tests.py so the agent's
# INSERT can run against the test DB. query_embedding TEXT means we can
# pass a Python list and psycopg2 stores its repr — fine for unit tests
# that don't care about pgvector semantics.
_RAG_QUERIES_DDL = """
CREATE TABLE IF NOT EXISTS rag_queries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    module_id INTEGER,
    reflection_text TEXT NOT NULL,
    teacher_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    query_embedding TEXT,
    retrieved_chunks JSONB DEFAULT '[]'::jsonb,
    num_chunks_retrieved INTEGER DEFAULT 0,
    generated_response TEXT NOT NULL,
    generation_tokens INTEGER,
    feedback_rating INTEGER,
    feedback_comments TEXT,
    feedback_timestamp TIMESTAMP,
    processing_time_ms INTEGER,
    api_cost_eur NUMERIC(10,6),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
"""

# Representative inputs reused across tests.
_REFLECTION = (
    "I tried using ChatGPT to help me create a quiz for my 8th grade "
    "Mathematics class on quadratic equations."
)
_CONTEXT = {
    'name': 'Maria',
    'subject': 'Mathematics',
    'grade_level': 'Secondary',
    'experience': '5 years',
}
_CHUNKS = [
    {
        'id': 1, 'title': 'UNESCO Framework Pillar 1',
        'chunk_text': 'AI literacy includes critical evaluation of AI outputs.',
        'distance': 0.2,
        'document_type': 'framework', 'module_id': None, 'subject': None,
    },
    {
        'id': 2, 'title': 'Differentiation Strategies',
        'chunk_text': 'Adapting difficulty levels is essential for inclusion.',
        'distance': 0.3,
        'document_type': 'guidance', 'module_id': None, 'subject': None,
    },
]


class RAGPromptParityTest(TestCase):
    """Layer-1 invariant: agent's prompt == frozen monolith snapshot.

    Pre-commit-9 this test invoked the live monolith to compute the
    expected prompt. Commit 9 deleted rag_query_system.py, so the
    expected string is now loaded from prompt_fixtures/rag_feedback.txt
    — a byte-identical snapshot captured the moment before deletion.
    Future prompt drift in RAGFeedbackAgent._build_prompt produces a
    visible diff against the fixture. Updating the fixture is an
    explicit, reviewable commit (no silent prompt drift possible).
    """

    def test_build_prompt_matches_frozen_monolith_snapshot(self):
        from apps.agents.tests._fixtures import load_prompt_fixture
        expected = load_prompt_fixture('rag_feedback')
        agent_prompt = RAGFeedbackAgent._build_prompt(
            _REFLECTION, _CONTEXT, _CHUNKS,
        )
        self.assertEqual(agent_prompt, expected)

    def test_build_prompt_contains_teacher_name_and_chunks(self):
        prompt = RAGFeedbackAgent._build_prompt(_REFLECTION, _CONTEXT, _CHUNKS)
        self.assertIn('Maria', prompt)
        self.assertIn('Mathematics', prompt)
        self.assertIn('UNESCO Framework Pillar 1', prompt)
        self.assertIn('AI literacy includes critical evaluation', prompt)
        # Closing newline-then-name signature — sanity guard against the
        # \\n vs \n escaping bug fixed during commit 1.
        self.assertIn('Best,\nThe PROODOS Team', prompt)

    def test_build_prompt_defaults_unknown_fields(self):
        # Missing name → 'Colleague' default, matching the monolith's
        # `teacher_context.get('name', 'Colleague')` line.
        prompt = RAGFeedbackAgent._build_prompt(
            _REFLECTION, {'subject': 'History'}, _CHUNKS,
        )
        self.assertIn('Colleague', prompt)
        self.assertIn('Mixed', prompt)  # grade_level default
        self.assertIn('Not specified', prompt)  # experience default


class RAGEndToEndTest(TestCase):
    """Layer-2 invariant: with mocked Gemini, generate() produces:
       - rag_queries row matching what store_rag_query would insert
       - both 'rag_query' and 'rag_feedback' provenance rows
       - all writes inside one atomic block"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with django_conn.cursor() as cur:
            cur.execute(_RAG_QUERIES_DDL)

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('rag_user', password='pw')
        cls.module = Module.objects.create(
            code='AGRAG', title='RAG agent test',
            description='t', order_index=996,
            unesco_aspect='ethics', proficiency_level='Acquire',
            is_published=True,
        )

    def _make_progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def _mock_llm_client(self):
        """Return a MagicMock that emulates LLMClient.embed + generate."""
        mock = MagicMock()
        mock.embed.return_value = [0.1] * 768
        mock.generate.return_value = GenerationResult(
            text='**Hello Maria,** thanks for sharing.\n\nBest,\nThe PROODOS Team',
            model='gemini-2.5-flash',
            tokens_estimate=100,
            cost_eur_estimate=0.0000279,
        )
        return mock

    def test_full_generate_writes_both_provenance_rows(self):
        progress = self._make_progress()
        mock_client = self._mock_llm_client()

        with patch('apps.agents.rag_feedback.get_llm_client',
                   return_value=mock_client), \
             patch.object(RAGFeedbackAgent, '_search_similar_chunks',
                          return_value=_CHUNKS):
            RAGFeedbackAgent().generate(
                user=self.user, module=self.module,
                save_target=progress,
                save_field='reflection_rag_feedback',
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
                module_id=self.module.id,
            )

        # Provenance row 1: rag_query (for the rag_queries telemetry row).
        rag_query_rows = AIArtefactProvenance.objects.filter(
            artefact_kind='rag_query', user=self.user,
        )
        self.assertEqual(rag_query_rows.count(), 1)

        # Provenance row 2: rag_feedback (for the user-visible HTML).
        feedback_rows = AIArtefactProvenance.objects.filter(
            artefact_kind='rag_feedback', user=self.user,
            artefact_pk=str(progress.pk),
        )
        self.assertEqual(feedback_rows.count(), 1)

        # Both should reference the same model.
        self.assertEqual(rag_query_rows.first().model_name, 'gemini-2.5-flash')
        self.assertEqual(feedback_rows.first().model_name, 'gemini-2.5-flash')

    def test_full_generate_populates_progress_with_html(self):
        progress = self._make_progress()
        mock_client = self._mock_llm_client()

        with patch('apps.agents.rag_feedback.get_llm_client',
                   return_value=mock_client), \
             patch.object(RAGFeedbackAgent, '_search_similar_chunks',
                          return_value=_CHUNKS):
            RAGFeedbackAgent().generate(
                user=self.user, module=self.module,
                save_target=progress,
                save_field='reflection_rag_feedback',
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
                module_id=self.module.id,
            )

        progress.refresh_from_db()
        self.assertIn('<strong>Hello Maria,</strong>',
                      progress.reflection_rag_feedback)

    def test_full_generate_inserts_rag_queries_row(self):
        progress = self._make_progress()
        mock_client = self._mock_llm_client()

        with patch('apps.agents.rag_feedback.get_llm_client',
                   return_value=mock_client), \
             patch.object(RAGFeedbackAgent, '_search_similar_chunks',
                          return_value=_CHUNKS):
            RAGFeedbackAgent().generate(
                user=self.user, module=self.module,
                save_target=progress,
                save_field='reflection_rag_feedback',
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
                module_id=self.module.id,
            )

        with django_conn.cursor() as cur:
            cur.execute(
                "SELECT generated_response, num_chunks_retrieved, "
                "       generation_tokens, user_id, module_id "
                "FROM rag_queries WHERE user_id = %s ORDER BY id DESC LIMIT 1",
                [self.user.id],
            )
            row = cur.fetchone()
        self.assertIsNotNone(row)
        generated_response, num_chunks, tokens, user_id, module_id = row
        self.assertIn('Hello Maria', generated_response)
        self.assertEqual(num_chunks, len(_CHUNKS))
        self.assertEqual(tokens, 100)
        self.assertEqual(user_id, self.user.id)
        self.assertEqual(module_id, self.module.id)

    def test_insert_uses_returning_id(self):
        """CP-3 — verify the agent's INSERT SQL contains RETURNING id."""
        import inspect
        source = inspect.getsource(RAGFeedbackAgent._persist)
        self.assertIn('RETURNING id', source,
                      'CP-3: rag_queries pk must come from RETURNING id, '
                      'never SELECT lastval().')

    def test_cp9_rollback_when_provenance_raises(self):
        """A raise inside _record_provenance must roll back the
        rag_queries INSERT AND the progress field update."""
        progress = self._make_progress()
        progress.reflection_rag_feedback = 'untouched'
        progress.save(update_fields=['reflection_rag_feedback'])
        mock_client = self._mock_llm_client()

        rag_count_before = self._count_rag_queries()

        with patch('apps.agents.rag_feedback.get_llm_client',
                   return_value=mock_client), \
             patch.object(RAGFeedbackAgent, '_search_similar_chunks',
                          return_value=_CHUNKS), \
             patch('apps.compliance.services.record_ai_provenance',
                   side_effect=RuntimeError('simulated provenance failure')):
            with self.assertRaises(RuntimeError):
                RAGFeedbackAgent().generate(
                    user=self.user, module=self.module,
                    save_target=progress,
                    save_field='reflection_rag_feedback',
                    reflection_text=_REFLECTION,
                    teacher_context=_CONTEXT,
                    module_id=self.module.id,
                )

        progress.refresh_from_db()
        self.assertEqual(progress.reflection_rag_feedback, 'untouched')
        self.assertEqual(
            self._count_rag_queries(), rag_count_before,
            'CP-9: rag_queries INSERT must roll back when provenance raises.',
        )

    def _count_rag_queries(self) -> int:
        with django_conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM rag_queries WHERE user_id = %s',
                        [self.user.id])
            return cur.fetchone()[0]
