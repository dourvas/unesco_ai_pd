"""
Tests for the apps.modules view layer.

Currently scoped to Phase C C.2.4 AILST research-instrument gating:
when a user completes M5 (Acquire phase end) or M15 (programme end),
the mark_tab_complete AJAX response must include an ailst_redirect_url
pointing the frontend to /ailst/t1/ or /ailst/t2/, gated on
research_consent and idempotent on already-completed AilstResponse rows.
"""

import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.ailst.models import AilstResponse
from apps.modules.models import Module, UserModuleProgress
from apps.users.models import TeacherProfile


class AilstModuleGatingTest(TestCase):
    """C.2.4: AILST gating injected into modules.mark_tab_complete.

    These tests submit the reflection tab (the canonical 'final tab'
    for a module — completing it sets progress.completed_at) and assert
    the JSON response includes or omits ailst_redirect_url under the
    relevant conditions.

    Background: the M4 / M5 migrations seed the AILST instrument; we do
    not need to seed modules separately because the Module rows are
    fixture data from earlier phases. Tests look up by `code`.
    """

    @classmethod
    def setUpTestData(cls):
        # No migration seeds Module rows; in production they are loaded
        # manually. The test DB is empty, so we create the three module
        # rows the tests need. order_index must be unique.
        seeds = (
            ('M3',  3,  'ethics',           'Acquire'),
            ('M5',  5,  'ai_foundations',   'Acquire'),
            ('M15', 15, 'professional_development', 'Create'),
        )
        for code, order_index, aspect, level in seeds:
            Module.objects.create(
                code=code,
                title=f'Test {code}',
                description=f'Test description for {code}',
                order_index=order_index,
                unesco_aspect=aspect,
                proficiency_level=level,
                is_published=True,
            )

    def setUp(self):
        self.client = Client()
        # is_staff so the TD-012 sequential prerequisite gate bypasses
        # for this test class. We are exercising the AILST routing logic
        # from mark_tab_complete, not the module ordering gate; the gate
        # has its own dedicated SequentialModuleGatingTest below.
        self.user = User.objects.create_user(
            username='gating_user', password='pw', is_staff=True,
        )
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            ai_disclosure_acknowledged_at=timezone.now(),
            profile_completed=True,
            research_consent=True,
        )
        self.client.force_login(self.user)

    def _ensure_progress_completable(self, module_code):
        """Create a UserModuleProgress with all prior tabs done so that
        the reflection submission flips completed_at to now()."""
        module = Module.objects.get(code=module_code)
        progress = UserModuleProgress.objects.create(
            user=self.user,
            module=module,
            introduction_completed=True,
            introduction_completed_at=timezone.now(),
            main_content_completed=True,
            main_content_completed_at=timezone.now(),
            activity_completed=True,
            activity_completed_at=timezone.now(),
            assessment_completed=True,
            assessment_completed_at=timezone.now(),
        )
        return module, progress

    def _post_reflection(self, module_code, reflection_text):
        url = reverse('modules:mark_tab_complete', kwargs={
            'code': module_code, 'tab_name': 'reflection',
        })
        return self.client.post(
            url,
            data=json.dumps({'reflection_text': reflection_text}),
            content_type='application/json',
        )

    def _valid_reflection_text(self):
        """A 350-word reflection — passes the 300-800 word validator."""
        sentence = (
            "I learned about how AI can support classroom planning and "
            "personalised feedback for students in meaningful ways. "
        )
        # 17 words per sentence; 21 sentences -> 357 words, comfortably valid.
        return (sentence * 21).strip()

    def test_completing_M5_redirects_to_T1_when_consent_and_T1_not_done(self):
        self._ensure_progress_completable('M5')
        resp = self._post_reflection('M5', self._valid_reflection_text())
        data = resp.json()
        # Reflection submission may fail under test conditions (no RAG
        # backend in the test environment) — but the mark_tab_complete
        # logic still runs as long as the validator passed.
        self.assertTrue(data.get('success'), msg=data)
        self.assertTrue(data.get('module_completed'))
        self.assertEqual(data.get('ailst_redirect_url'), '/ailst/t1/')
        self.assertEqual(
            data.get('ailst_redirect_label'),
            'Continue to AI Literacy assessment',
        )

    def test_completing_M5_no_redirect_when_T1_already_completed(self):
        self._ensure_progress_completable('M5')
        # User has already completed T1 in a prior pass.
        AilstResponse.objects.create(
            user=self.user,
            timepoint='T1',
            language='en',
            instrument_version='ning_2025_v1',
            responses={f'P{i}': 4 for i in range(1, 11)},
            completed_at=timezone.now(),
        )
        resp = self._post_reflection('M5', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertNotIn(
            'ailst_redirect_url', data,
            "Idempotency: completed T1 must suppress the redirect.",
        )

    def test_completing_M15_redirects_to_epilogue_not_to_T2(self):
        """C.2.5: T2 is reached via the Epilogue, not directly from M15.

        The mark_tab_complete response now sends a just-completed M15
        user to /epilogue/. The Epilogue completion view is then
        responsible for the (consent-gated) onward redirect to /ailst/t2/.
        """
        self._ensure_progress_completable('M15')
        resp = self._post_reflection('M15', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertEqual(data.get('ailst_redirect_url'), '/epilogue/')
        self.assertEqual(
            data.get('ailst_redirect_label'),
            'Continue to PROODOS Epilogue',
        )

    def test_completing_M5_no_redirect_when_user_lacks_research_consent(self):
        self.profile.research_consent = False
        self.profile.save(update_fields=['research_consent'])
        self._ensure_progress_completable('M5')
        resp = self._post_reflection('M5', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertNotIn(
            'ailst_redirect_url', data,
            "research_consent=False users must not be sent to AILST.",
        )

    def test_completing_non_gating_module_M3_does_not_redirect(self):
        self._ensure_progress_completable('M3')
        resp = self._post_reflection('M3', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertNotIn('ailst_redirect_url', data)

    def test_partial_tab_completion_does_not_redirect(self):
        """If reflection completes but other tabs are not yet done, the
        module is not 'just completed' and no AILST redirect fires."""
        module = Module.objects.get(code='M5')
        # Create progress with only some prior tabs done (no assessment).
        UserModuleProgress.objects.create(
            user=self.user,
            module=module,
            introduction_completed=True,
            introduction_completed_at=timezone.now(),
            main_content_completed=True,
            main_content_completed_at=timezone.now(),
            activity_completed=True,
            activity_completed_at=timezone.now(),
            # assessment_completed left False — module won't flip to done.
        )
        resp = self._post_reflection('M5', self._valid_reflection_text())
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertFalse(data.get('module_completed'))
        self.assertNotIn(
            'ailst_redirect_url', data,
            "Reflection submitted but module not yet completed: no redirect.",
        )

    def test_response_shape_is_backwards_compatible_when_no_redirect(self):
        """When ailst_redirect_url is not set, the JSON keys are exactly
        the pre-C.2.4 shape so old frontends keep working unchanged."""
        self._ensure_progress_completable('M3')
        resp = self._post_reflection('M3', self._valid_reflection_text())
        data = resp.json()
        for key in ('success', 'next_tab', 'module_completed',
                    'completion_percentage'):
            self.assertIn(key, data, f"Missing legacy key {key!r}.")
        self.assertNotIn('ailst_redirect_url', data)


# ============================================================================
# TD-012 — Sequential module-prerequisite gating
# ============================================================================


class SequentialModuleGatingTest(TestCase):
    """The order_index-based prerequisite gate must:
      - Redirect a non-staff user opening M_n out of sequence to the
        first uncompleted prior module.
      - Allow access to M1 unconditionally.
      - Allow access to a module whose prerequisites are all done.
      - Allow staff / superuser bypass for support work.
      - Block the AJAX mark_tab_complete endpoint with 409 when called
        directly out of sequence (defensive AJAX path).
    """

    @classmethod
    def setUpTestData(cls):
        from apps.modules.models import Module
        for code, order_index in (('GT1', 1), ('GT2', 2), ('GT3', 3)):
            Module.objects.get_or_create(
                code=code,
                defaults={
                    'title': 'Gating Test ' + code,
                    'description': 'gating test',
                    'unesco_aspect': 'ethics',
                    'proficiency_level': 'Acquire',
                    'order_index': 50 + order_index,
                    'is_published': True,
                },
            )

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='gate_user', password='pw')
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            ai_disclosure_acknowledged_at=timezone.now(),
            profile_completed=True,
            research_consent=True,
        )
        self.client.force_login(self.user)

    def _complete_module(self, code):
        from apps.modules.models import Module, UserModuleProgress
        m = Module.objects.get(code=code)
        UserModuleProgress.objects.update_or_create(
            user=self.user, module=m,
            defaults={'completed_at': timezone.now(),
                      'completion_percentage': 100, 'status': 'completed'},
        )

    def test_first_module_is_always_accessible(self):
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT1'}))
        self.assertEqual(resp.status_code, 200)

    def test_jumping_to_middle_module_redirects_to_first_uncompleted(self):
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT3'}))
        self.assertRedirects(
            resp, reverse('modules:detail', kwargs={'code': 'GT1'}),
            fetch_redirect_response=False,
        )

    def test_access_allowed_when_prerequisites_are_done(self):
        self._complete_module('GT1')
        self._complete_module('GT2')
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT3'}))
        self.assertEqual(resp.status_code, 200)

    def test_partial_prerequisites_redirects_to_first_uncompleted(self):
        self._complete_module('GT1')
        # GT2 NOT completed. Trying GT3 should redirect to GT2.
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT3'}))
        self.assertRedirects(
            resp, reverse('modules:detail', kwargs={'code': 'GT2'}),
            fetch_redirect_response=False,
        )

    def test_staff_user_bypasses_gate(self):
        self.user.is_staff = True
        self.user.save()
        resp = self.client.get(reverse('modules:detail', kwargs={'code': 'GT3'}))
        self.assertEqual(resp.status_code, 200)

    def test_mark_tab_complete_ajax_blocked_when_out_of_order(self):
        """Defensive AJAX guard: mark_tab_complete must reject calls on
        a module whose prerequisites are not done, even though the
        GET-side gate already redirects."""
        from apps.modules.models import Module, UserModuleProgress
        m = Module.objects.get(code='GT3')
        # Create a progress row directly to simulate the rare case where
        # a user has a UserModuleProgress row for GT3 without finishing
        # GT1/GT2 (e.g. via admin / data migration).
        UserModuleProgress.objects.create(user=self.user, module=m)

        resp = self.client.post(
            reverse('modules:mark_tab_complete',
                    kwargs={'code': 'GT3', 'tab_name': 'introduction'}),
            data=json.dumps({}), content_type='application/json',
        )
        self.assertEqual(resp.status_code, 409)
        data = resp.json()
        self.assertFalse(data['success'])
        self.assertIn('GT1', data['message'])


# ============================================================================
# Phase C C.3 commit 2a — AI provenance forward-write hooks
# ============================================================================
#
# CP-9 invariant: every AI artefact save path also writes an
# AIArtefactProvenance row inside the same transaction.atomic block.
# If the provenance write raises, the source-row save rolls back too.

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


class AIProvenanceWriteHookTest(TestCase):
    """Forward-write hooks: each AI output save path produces a
    matching AIArtefactProvenance row in the same atomic block.

    Covers four ORM-managed save paths (RAG feedback, DTP narrative,
    peer synthesis inline, RTM position) plus the raw-SQL rag_queries
    INSERT path. The sixth test exercises the CP-9 rollback invariant.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from django.db import connection as _conn
        with _conn.cursor() as cur:
            cur.execute(_RAG_QUERIES_DDL)

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='prov_writer', password='pw', is_staff=True,
        )
        TeacherProfile.objects.create(
            user=self.user,
            subject_area='mathematics', grade_level='primary',
            ai_experience='none',
            ai_disclosure_acknowledged_at=timezone.now(),
            profile_completed=True,
            research_consent=True,
        )
        self.module = Module.objects.create(
            code='MZ', title='Provenance test module',
            description='Test', order_index=999,
            unesco_aspect='ethics', proficiency_level='Acquire',
            is_published=True,
        )
        self.client.force_login(self.user)

    def _make_progress(self):
        return UserModuleProgress.objects.create(
            user=self.user,
            module=self.module,
            introduction_completed=True,
            introduction_completed_at=timezone.now(),
            main_content_completed=True,
            main_content_completed_at=timezone.now(),
            activity_completed=True,
            activity_completed_at=timezone.now(),
            assessment_completed=True,
            assessment_completed_at=timezone.now(),
        )

    def test_rag_feedback_save_writes_provenance(self):
        """mark_tab_complete reflection path produces a rag_feedback
        provenance row.

        Phase E commit 2: this test was migrated from patching
        apps.modules.views.process_reflection (now unused at the view
        layer) to patching RAGFeedbackAgent's LLMClient and
        _search_similar_chunks. Same pattern as
        apps/agents/tests/test_rag_feedback.py — exercises the real
        agent _persist + _record_provenance paths inside the view's
        request lifecycle, which strengthens CP-9 end-to-end coverage
        rather than weakening it.
        """
        from unittest.mock import MagicMock, patch
        from apps.agents.rag_feedback import RAGFeedbackAgent
        from apps.agents.shared.llm_client import GenerationResult
        from apps.compliance.models import AIArtefactProvenance

        progress = self._make_progress()
        reflection_text = ('I reflected on my classroom teaching practice today and '
                           'considered new approaches to AI literacy support. '
                           ) * 22  # ~352 words — passes the 300-800 validator

        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        mock_client.generate.return_value = GenerationResult(
            text='Mocked AI feedback markdown.',
            model='gemini-2.5-flash',
            tokens_estimate=100,
            cost_eur_estimate=0.0000279,
        )

        with patch('apps.agents.rag_feedback.get_llm_client',
                   return_value=mock_client), \
             patch.object(RAGFeedbackAgent, '_search_similar_chunks',
                          return_value=[]):
            resp = self.client.post(
                reverse('modules:mark_tab_complete',
                        kwargs={'code': 'MZ', 'tab_name': 'reflection'}),
                data=json.dumps({'reflection_text': reflection_text}),
                content_type='application/json',
            )

        self.assertEqual(resp.status_code, 200, msg=resp.content)
        self.assertTrue(resp.json().get('success'), msg=resp.content)
        self.assertTrue(
            AIArtefactProvenance.objects.filter(
                artefact_kind='rag_feedback',
                artefact_pk=str(progress.pk),
                user=self.user,
                model_name='gemini-2.5-flash',
            ).exists(),
            'Expected rag_feedback provenance row for the UserModuleProgress.',
        )

    def test_rtm_position_save_writes_provenance(self):
        """save_tensions creates a provenance row per tension."""
        from apps.compliance.models import AIArtefactProvenance
        from apps.modules.models import ReflectionTension

        # save_tensions requires an existing UserModuleProgress (404 otherwise).
        self._make_progress()
        tensions_payload = {
            'tensions': [{
                'tension_label': 'Test tension',
                'left_pole': 'Left',
                'right_pole': 'Right',
                'grounding_quote': 'Quote',
                'position': 3,
                'comment': '',
            }],
        }
        resp = self.client.post(
            reverse('modules:save_tensions', kwargs={'code': 'MZ'}),
            data=json.dumps(tensions_payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200, msg=resp.content)
        tension = ReflectionTension.objects.get(user=self.user, module=self.module)
        self.assertTrue(
            AIArtefactProvenance.objects.filter(
                artefact_kind='rtm_position',
                artefact_pk=str(tension.pk),
                user=self.user,
                model_name='gemini-2.5-flash',
            ).exists(),
            'Expected rtm_position provenance row for the saved ReflectionTension.',
        )

    def test_dtp_narrative_save_writes_provenance(self):
        """Direct unit test of the dtp_narrative save + provenance
        atomic pair. The view's upstream raw psycopg2 SELECT against
        rag_queries cannot see the test-DB-only DDL (separate connection,
        uncommitted schema in TestCase outer transaction). The patched
        site itself — `progress.save()` + `record_ai_provenance` inside
        one `transaction.atomic()` — is exactly what we test here, the
        same structure the view uses."""
        from django.db import transaction as _txn
        from apps.compliance.models import AIArtefactProvenance
        from apps.compliance.services import record_ai_provenance

        progress = self._make_progress()
        dtp_result = {'trajectory': 'mock'}
        with _txn.atomic():
            progress.reflection_dtp = json.dumps(dtp_result)
            progress.save()
            record_ai_provenance(
                artefact_kind='dtp_narrative',
                artefact_pk=progress.pk,
                user=progress.user,
                module=progress.module,
                model_name='gemini-2.5-flash',
                generated_at=timezone.now(),
            )
        self.assertTrue(
            AIArtefactProvenance.objects.filter(
                artefact_kind='dtp_narrative',
                artefact_pk=str(progress.pk),
                user=self.user,
            ).exists(),
            'Expected dtp_narrative provenance row.',
        )

    # Phase E commit 2: test_peer_synthesis_inline_save_writes_provenance
    # was removed here. Investigation found it exercised a code path that
    # had been dead since `peer_synthesis = None` was hardcoded in
    # rag_query_system.py:559-560 — process_reflection has never returned
    # a real peer_synthesis value in production. The test passed pre-cutover
    # only because its mock injected a synthetic peer_synthesis into the
    # rag_result dict, re-animating dead code. The inline save block at
    # views.py:965-984 is scheduled for removal in commit 7 alongside the
    # PeerSynthesisAgent migration, at which point the live async path
    # (extract_peer_synthesis_view, which DOES write peer_synthesis
    # provenance — see views.py:2216) becomes the sole writer.

    def test_rag_queries_insert_writes_provenance_in_same_atomic(self):
        """The raw-SQL rag_queries INSERT writes an AIArtefactProvenance
        row of kind 'rag_query' inside one atomic block — verifies the
        RETURNING id path (CP-3) and the same-transaction guarantee
        (CP-9).

        Phase E commit 9: this test was migrated from calling the
        deleted monolith function `rag_query_system.store_rag_query`
        directly to invoking RAGFeedbackAgent. The agent's _persist
        owns the rag_queries INSERT + 'rag_query' provenance write
        in one atomic block — exactly the invariant this test
        guards. Mocking the LLM client + similarity search avoids
        the live Gemini call, same pattern as
        test_rag_feedback_save_writes_provenance and
        apps/agents/tests/test_rag_feedback.RAGEndToEndTest.
        """
        from unittest.mock import MagicMock, patch
        from apps.agents.rag_feedback import RAGFeedbackAgent
        from apps.agents.shared.llm_client import GenerationResult
        from apps.compliance.models import AIArtefactProvenance

        progress = self._make_progress()
        before = AIArtefactProvenance.objects.filter(
            artefact_kind='rag_query'
        ).count()

        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        mock_client.generate.return_value = GenerationResult(
            text='Mock AI response.',
            model='gemini-2.5-flash',
            tokens_estimate=100,
            cost_eur_estimate=0.001,
        )

        with patch('apps.agents.rag_feedback.get_llm_client',
                   return_value=mock_client), \
             patch.object(RAGFeedbackAgent, '_search_similar_chunks',
                          return_value=[]):
            RAGFeedbackAgent().generate(
                user=self.user,
                module=self.module,
                save_target=progress,
                save_field='reflection_rag_feedback',
                reflection_text='r',
                teacher_context={'subject': 'mathematics'},
                module_id=self.module.id,
            )

        # Exactly one new 'rag_query' provenance row written by the
        # agent's _persist (the kind=rag_query row references the new
        # rag_queries.id obtained via RETURNING id — CP-3 — and is
        # written in the same transaction.atomic as the INSERT — CP-9).
        self.assertEqual(
            AIArtefactProvenance.objects.filter(
                artefact_kind='rag_query'
            ).count(),
            before + 1,
            'Expected exactly one new rag_query provenance row from '
            'RAGFeedbackAgent._persist.',
        )

    def test_cp9_rollback_when_provenance_raises_during_rtm_save(self):
        """CP-9 invariant: when record_ai_provenance raises during the
        atomic block, the source-row save is rolled back too — no
        ReflectionTension created, no provenance created.

        Uses RTM save_tensions as the exercise path because it is fully
        ORM-managed and does not require AI mocking."""
        from unittest.mock import patch
        from apps.compliance.models import AIArtefactProvenance
        from apps.modules.models import ReflectionTension

        # save_tensions requires UserModuleProgress.
        self._make_progress()
        tensions_payload = {
            'tensions': [{
                'tension_label': 'CP-9 invariant tension',
                'left_pole': 'L', 'right_pole': 'R',
                'grounding_quote': 'q', 'position': 4, 'comment': '',
            }],
        }
        # save_tensions's outer try/except swallows the RuntimeError and
        # returns a 500 JSON. The load-bearing CP-9 assertion is on DB
        # state — the source row must NOT exist post-call.
        with patch(
            'apps.modules.views.record_ai_provenance',
            side_effect=RuntimeError('simulated provenance failure'),
        ):
            resp = self.client.post(
                reverse('modules:save_tensions', kwargs={'code': 'MZ'}),
                data=json.dumps(tensions_payload),
                content_type='application/json',
            )
        self.assertEqual(
            resp.status_code, 500,
            'View should propagate provenance failure as 500.',
        )
        self.assertFalse(
            ReflectionTension.objects.filter(
                user=self.user, module=self.module,
                tension_label='CP-9 invariant tension',
            ).exists(),
            'CP-9 invariant: ReflectionTension save must have been rolled back.',
        )
        self.assertEqual(
            AIArtefactProvenance.objects.filter(
                artefact_kind='rtm_position', user=self.user,
            ).count(),
            0,
            'CP-9 invariant: no provenance row created when the write raised.',
        )
