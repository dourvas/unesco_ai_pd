"""Tests for the CP-11 pre-pilot user wipe script.

Phase C plan §2.1 CP 11 — Option B. Verifies that
`scripts/cp11_wipe_test_users.py::wipe_non_staff_users`:

  - Dry-run mode does not change the DB.
  - Commit mode deletes only non-staff non-superuser users.
  - Cascade deletion takes out TeacherProfile, ConsentRecord,
    AilstResponse, UserModuleProgress, EpilogueCompletion, etc.
  - Raw-SQL rag_queries rows are removed via explicit DELETE (the
    table has no Django-managed FK cascade).
  - Empty DB is a no-op.
"""

import importlib.util
import os

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.utils import timezone

from apps.ailst.models import AilstResponse
from apps.compliance.models import ConsentRecord
from apps.users.models import TeacherProfile


# The script is at scripts/cp11_wipe_test_users.py outside the apps
# package; load it dynamically so it is importable from the test runner.
SCRIPTS_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, 'scripts',
))
_spec = importlib.util.spec_from_file_location(
    'cp11_wipe_test_users',
    os.path.join(SCRIPTS_DIR, 'cp11_wipe_test_users.py'),
)
cp11 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp11)


_RAG_QUERIES_DDL = """
CREATE TABLE IF NOT EXISTS rag_queries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
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


class Cp11WipeTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as cur:
            cur.execute(_RAG_QUERIES_DDL)

    def setUp(self):
        # Three users: one staff, one superuser, one regular pilot user.
        self.staff = User.objects.create_user(
            username='cp11_staff', password='x', is_staff=True,
        )
        self.superuser = User.objects.create_user(
            username='cp11_super', password='x', is_superuser=True,
        )
        self.participant = User.objects.create_user(
            username='cp11_participant', password='x',
        )
        TeacherProfile.objects.create(user=self.participant)

    def _add_research_data_to(self, user):
        """Attach AILST + Consent + a raw rag_queries row to user."""
        AilstResponse.objects.create(
            user=user, timepoint='T0', language='en',
            instrument_version='ning_2025_v1',
            responses={'P1': 4}, completed_at=timezone.now(),
        )
        ConsentRecord.objects.create(
            user=user, consent_type='research_participation', granted=True,
            consent_text='x', version='v1_pre_irb',
        )
        from apps.modules.models import Module
        m, _ = Module.objects.get_or_create(
            code='M0',
            defaults={
                'title': 'M0 for cp11 test', 'description': 'test',
                'unesco_aspect': 'ethics', 'proficiency_level': 'Acquire',
                'order_index': 100, 'is_published': True,
            },
        )
        with connection.cursor() as cur:
            cur.execute(
                "INSERT INTO rag_queries (user_id, module_id, reflection_text, "
                "generated_response, created_at, updated_at) "
                "VALUES (%s, %s, 'r', 'g', NOW(), NOW())",
                [user.id, m.id],
            )

    def test_dry_run_makes_no_changes(self):
        self._add_research_data_to(self.participant)

        before_users = User.objects.count()
        before_consents = ConsentRecord.objects.count()
        before_ailst = AilstResponse.objects.count()

        summary = cp11.wipe_non_staff_users(
            commit=False, require_typed_confirmation=False,
            output=lambda *_: None,
        )

        self.assertEqual(summary['examined'], 1)
        self.assertEqual(summary['wiped'], 0)
        self.assertEqual(User.objects.count(), before_users)
        self.assertEqual(ConsentRecord.objects.count(), before_consents)
        self.assertEqual(AilstResponse.objects.count(), before_ailst)

    def test_commit_removes_participant_only(self):
        self._add_research_data_to(self.participant)

        summary = cp11.wipe_non_staff_users(
            commit=True, require_typed_confirmation=False,
            output=lambda *_: None,
        )

        self.assertEqual(summary['examined'], 1)
        self.assertGreater(summary['wiped'], 0)

        # Staff and superuser preserved.
        self.assertTrue(User.objects.filter(username='cp11_staff').exists())
        self.assertTrue(User.objects.filter(username='cp11_super').exists())
        # Participant gone.
        self.assertFalse(User.objects.filter(username='cp11_participant').exists())
        # Cascade footprint: their TeacherProfile, AilstResponse,
        # ConsentRecord are also gone.
        self.assertFalse(TeacherProfile.objects.filter(user__username='cp11_participant').exists())
        self.assertEqual(AilstResponse.objects.count(), 0)
        self.assertEqual(
            ConsentRecord.objects.filter(consent_text='x').count(), 0,
        )

    def test_rag_queries_rows_removed_for_wiped_users(self):
        self._add_research_data_to(self.participant)

        with connection.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM rag_queries WHERE user_id = %s",
                [self.participant.id],
            )
            self.assertEqual(cur.fetchone()[0], 1)

        summary = cp11.wipe_non_staff_users(
            commit=True, require_typed_confirmation=False,
            output=lambda *_: None,
        )

        self.assertEqual(summary['rag_queries_removed'], 1)

        with connection.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM rag_queries WHERE user_id = %s",
                [self.participant.id],
            )
            self.assertEqual(
                cur.fetchone()[0], 0,
                'rag_queries rows for the wiped user must be removed '
                'via the explicit raw-SQL DELETE (no Django CASCADE).',
            )

    def test_empty_db_is_a_noop(self):
        # Remove the seeded participant so only staff + superuser remain.
        TeacherProfile.objects.filter(user=self.participant).delete()
        self.participant.delete()

        summary = cp11.wipe_non_staff_users(
            commit=True, require_typed_confirmation=False,
            output=lambda *_: None,
        )
        self.assertEqual(summary['examined'], 0)
        self.assertEqual(summary['wiped'], 0)
        # Staff and superuser still there.
        self.assertEqual(User.objects.count(), 2)
