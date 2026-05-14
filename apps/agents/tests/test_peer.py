"""PeerSynthesisAgent parity + three-failure-mode tests.

Two-layer invariant from v5 §5:
  (1) Prompt-identical with rag_query_system.synthesize_peer_insight
  (2) Behaviour-identical given mocked search results + mocked Gemini

Plus the commit-7-specific contract checks:
  - Three distinct exception types for three distinct failure modes
    (RuntimeError = LLM, NoPeerReflectionsAvailable = empty search,
     Exception = save/provenance) so the view layer can render the
    right user-facing message per failure
  - Markdown -> HTML conversion happens inside _persist (not in views)
  - Per-Gemini-call cost event
  - search_peer_reflections subject-exclusion contract preserved
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from apps.agents.peer import (
    NoPeerReflectionsAvailable,
    PEER_DEFAULT_TOP_K,
    PEER_REFLECTION_PROMPT_BUDGET,
    PeerSynthesisAgent,
)
from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.llm_client import GenerationResult
from apps.compliance.models import AIArtefactProvenance
from apps.modules.models import Module, UserModuleProgress


_REFLECTION = (
    "I tried using ChatGPT to differentiate quadratic equations questions "
    "for my mixed-ability classroom. The results were mixed — some students "
    "appreciated the variety, others felt the AI's choices were arbitrary."
)
_CONTEXT = {'name': 'Maria', 'subject': 'Mathematics'}

_PEER_ROWS = [
    {
        'id': 101,
        'subject_area': 'History',
        'grade_level': 'Secondary',
        'experience_years': '5-10',
        'reflection_text': (
            'I used ChatGPT to generate primary-source analysis prompts. '
            'Students engaged with the variety but I noticed shallow '
            'critical thinking in their responses.'
        ),
        'distance': 0.21,
        'is_seed_data': True,
    },
    {
        'id': 102,
        'subject_area': 'Science',
        'grade_level': 'Secondary',
        'experience_years': '10+',
        'reflection_text': (
            'AI generated lab procedure variations were technically correct '
            'but missed the pedagogical scaffolding I would design myself.'
        ),
        'distance': 0.28,
        'is_seed_data': True,
    },
]


def _gen_result(text: str, tokens: int = 200, cost: float = 0.0000558):
    return GenerationResult(
        text=text, model='gemini-2.5-flash',
        tokens_estimate=tokens, cost_eur_estimate=cost,
    )


class PeerHierarchyTest(SimpleTestCase):
    def test_inherits_from_research_instrument_agent(self):
        self.assertTrue(issubclass(PeerSynthesisAgent, ResearchInstrumentAgent))

    def test_artefact_kind(self):
        self.assertEqual(PeerSynthesisAgent.artefact_kind, 'peer_synthesis')

    def test_model_name(self):
        self.assertEqual(PeerSynthesisAgent.model_name, 'gemini-2.5-flash')

    def test_default_top_k(self):
        """Live view at views.py:2199 passes top_k=2; the agent
        default matches that for symmetry."""
        self.assertEqual(PEER_DEFAULT_TOP_K, 2)


class PeerPromptParityTest(SimpleTestCase):
    """Layer-1 invariant: agent prompt == frozen monolith snapshot.

    Pre-commit-9 the expected prompt came from a live call to
    rag_query_system.synthesize_peer_insight. Commit 9 deleted that
    function; the byte-identical snapshot lives at
    prompt_fixtures/peer.txt.
    """

    def test_build_prompt_matches_frozen_monolith_snapshot(self):
        from apps.agents.tests._fixtures import load_prompt_fixture
        expected = load_prompt_fixture('peer')
        agent_prompt = PeerSynthesisAgent._build_prompt(
            _REFLECTION, _CONTEXT, _PEER_ROWS,
        )
        self.assertEqual(agent_prompt, expected)


class PeerLayer0BoilerplateTest(SimpleTestCase):
    """Exact-string assertions for boilerplate prone to drift."""

    def test_contains_facilitator_framing(self):
        prompt = PeerSynthesisAgent._build_prompt(
            _REFLECTION, _CONTEXT, _PEER_ROWS,
        )
        self.assertIn(
            'You are facilitating cross-disciplinary professional learning '
            'among teachers.',
            prompt,
        )

    def test_contains_task_block_with_numbered_steps(self):
        prompt = PeerSynthesisAgent._build_prompt(
            _REFLECTION, _CONTEXT, _PEER_ROWS,
        )
        self.assertIn('Write a brief, engaging synthesis (200-250 words)', prompt)
        # The five numbered steps each have a bold-marked label
        for marker in (
            '1. **Opens warmly:**',
            '2. **Names the pattern:**',
            '3. **Draws cross-specialty connection:**',
            '4. **Highlights transferable insight:**',
            '5. **Closes with invitation:**',
        ):
            self.assertIn(marker, prompt)

    def test_anonymity_directive(self):
        prompt = PeerSynthesisAgent._build_prompt(
            _REFLECTION, _CONTEXT, _PEER_ROWS,
        )
        self.assertIn(
            'Do NOT reveal which specific colleague you\'re quoting (anonymity)',
            prompt,
        )

    def test_peer_truncation_at_400_chars(self):
        long_peer = dict(_PEER_ROWS[0])
        long_peer['reflection_text'] = 'X' * 600 + 'AFTER_CAP'
        prompt = PeerSynthesisAgent._build_prompt(
            _REFLECTION, _CONTEXT, [long_peer],
        )
        # AFTER_CAP is past the 400-char budget — must be cut off.
        self.assertNotIn('AFTER_CAP', prompt)
        # The literal "..." trailer is appended by the prompt builder.
        self.assertIn('XXX...', prompt)

    def test_user_name_and_subject_interpolated(self):
        prompt = PeerSynthesisAgent._build_prompt(
            _REFLECTION,
            {'name': 'Alex', 'subject': 'Physics'},
            _PEER_ROWS,
        )
        self.assertIn('Alex is a Physics teacher', prompt)
        # Step 4 interpolates user_subject too.
        self.assertIn('could apply to Physics', prompt)

    def test_default_name_when_missing(self):
        prompt = PeerSynthesisAgent._build_prompt(
            _REFLECTION,
            {'subject': 'Music'},  # name missing
            _PEER_ROWS,
        )
        self.assertIn('Colleague is a Music teacher', prompt)

    def test_default_subject_when_missing(self):
        prompt = PeerSynthesisAgent._build_prompt(
            _REFLECTION,
            {'name': 'Alex'},  # subject missing
            _PEER_ROWS,
        )
        self.assertIn('Alex is a your subject teacher', prompt)


class PeerFailureModesTest(TestCase):
    """Three distinct exception types for three distinct failure modes —
    so the view layer renders the right user message per failure."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('peer_fail_user', password='pw')
        cls.module = Module.objects.create(
            code='AGPEER1', title='Peer fail test',
            description='t', order_index=992,
            unesco_aspect='ethics', proficiency_level='Acquire',
            is_published=True,
        )

    def _make_progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def test_embed_failure_raises_runtime_error(self):
        mock_client = MagicMock()
        mock_client.embed.return_value = None

        progress = self._make_progress()
        with patch('apps.agents.peer.get_llm_client', return_value=mock_client):
            with self.assertRaises(RuntimeError) as cm:
                PeerSynthesisAgent().generate(
                    user=self.user, module=self.module,
                    save_target=progress,
                    save_field='reflection_peer_synthesis',
                    reflection_text=_REFLECTION,
                    teacher_context=_CONTEXT,
                )
        self.assertIn('embedding', str(cm.exception).lower())

        # CP-9: atomic rolled back — no provenance row.
        self.assertFalse(
            AIArtefactProvenance.objects.filter(
                artefact_kind='peer_synthesis',
                artefact_pk=str(progress.pk),
            ).exists()
        )

    def test_no_peers_raises_no_peer_reflections_available(self):
        """Empty similarity result — distinct exception type so the
        view can render "No peer reflections found" instead of an
        error message."""
        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768

        progress = self._make_progress()
        with patch('apps.agents.peer.get_llm_client', return_value=mock_client), \
             patch.object(
                 PeerSynthesisAgent, '_search_peer_reflections',
                 return_value=[],
             ):
            with self.assertRaises(NoPeerReflectionsAvailable) as cm:
                PeerSynthesisAgent().generate(
                    user=self.user, module=self.module,
                    save_target=progress,
                    save_field='reflection_peer_synthesis',
                    reflection_text=_REFLECTION,
                    teacher_context=_CONTEXT,
                )
        self.assertIn('cross-specialty', str(cm.exception).lower())

        # CP-9: atomic rolled back — no provenance row.
        self.assertFalse(
            AIArtefactProvenance.objects.filter(
                artefact_kind='peer_synthesis',
                artefact_pk=str(progress.pk),
            ).exists()
        )

    def test_gemini_failure_raises_runtime_error(self):
        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        mock_client.generate.return_value = None  # Gemini fails

        progress = self._make_progress()
        with patch('apps.agents.peer.get_llm_client', return_value=mock_client), \
             patch.object(
                 PeerSynthesisAgent, '_search_peer_reflections',
                 return_value=_PEER_ROWS,
             ):
            with self.assertRaises(RuntimeError) as cm:
                PeerSynthesisAgent().generate(
                    user=self.user, module=self.module,
                    save_target=progress,
                    save_field='reflection_peer_synthesis',
                    reflection_text=_REFLECTION,
                    teacher_context=_CONTEXT,
                )
        self.assertIn('gemini', str(cm.exception).lower())

    def test_no_peer_reflections_available_is_distinct_from_runtime_error(self):
        """Sanity: the three failure exception classes do not share a
        common ancestor that would make the view's separate handlers
        collapse."""
        self.assertFalse(issubclass(NoPeerReflectionsAvailable, RuntimeError))
        self.assertTrue(issubclass(NoPeerReflectionsAvailable, Exception))
        self.assertTrue(issubclass(RuntimeError, Exception))


class PeerCostTrackingTest(TestCase):
    """One generate() = one 'agent.cost' event (single Gemini call
    per Peer call, unlike DTP's two)."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('peer_cost_user', password='pw')
        cls.module = Module.objects.create(
            code='AGPEER2', title='Peer cost test',
            description='t', order_index=991,
            unesco_aspect='ethics', proficiency_level='Acquire',
            is_published=True,
        )

    def _make_progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def test_one_cost_event_per_generate(self):
        progress = self._make_progress()
        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        mock_client.generate.return_value = _gen_result(
            'I noticed something interesting about your reflection. '
            'A colleague teaching **History** wrestled with the same '
            'tension you describe...',
        )

        with patch('apps.agents.peer.get_llm_client', return_value=mock_client), \
             patch.object(
                 PeerSynthesisAgent, '_search_peer_reflections',
                 return_value=_PEER_ROWS,
             ), \
             self.assertLogs('agents.audit', level='INFO') as cm:
            PeerSynthesisAgent().generate(
                user=self.user, module=self.module,
                save_target=progress,
                save_field='reflection_peer_synthesis',
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )

        cost_events = [
            r for r in cm.records if r.getMessage() == 'agent.cost'
        ]
        self.assertEqual(
            len(cost_events), 1,
            'PeerSynthesisAgent should emit exactly one agent.cost '
            'event per generate() (single Gemini call).',
        )
        self.assertEqual(cost_events[0].agent, 'PeerSynthesisAgent')
        self.assertEqual(cost_events[0].artefact_kind, 'peer_synthesis')


class PeerEndToEndTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('peer_e2e_user', password='pw')
        cls.module = Module.objects.create(
            code='AGPEER3', title='Peer end-to-end',
            description='t', order_index=990,
            unesco_aspect='ethics', proficiency_level='Acquire',
            is_published=True,
        )

    def _make_progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def _mock_setup(self, synthesis_markdown: str):
        mock_client = MagicMock()
        mock_client.embed.return_value = [0.1] * 768
        mock_client.generate.return_value = _gen_result(synthesis_markdown)
        return mock_client

    def test_full_generate_renders_html_to_progress(self):
        """Markdown -> HTML conversion happens inside _persist, mirroring
        today's views.py:2217-2220 flow. After cutover, the view never
        touches markdown directly."""
        progress = self._make_progress()
        mock_client = self._mock_setup(
            'I noticed something **interesting** about your reflection.\n'
            'A colleague teaching *History* wrestled with the same tension.'
        )

        with patch('apps.agents.peer.get_llm_client', return_value=mock_client), \
             patch.object(
                 PeerSynthesisAgent, '_search_peer_reflections',
                 return_value=_PEER_ROWS,
             ):
            PeerSynthesisAgent().generate(
                user=self.user, module=self.module,
                save_target=progress,
                save_field='reflection_peer_synthesis',
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )

        progress.refresh_from_db()
        self.assertIsNotNone(progress.reflection_peer_synthesis)
        # markdown.markdown renders **bold** as <strong> via the
        # 'extra' extension.
        self.assertIn('<strong>interesting</strong>',
                      progress.reflection_peer_synthesis)
        self.assertIn('<em>History</em>',
                      progress.reflection_peer_synthesis)

    def test_full_generate_writes_one_provenance_row(self):
        progress = self._make_progress()
        mock_client = self._mock_setup('A synthesis paragraph.')

        with patch('apps.agents.peer.get_llm_client', return_value=mock_client), \
             patch.object(
                 PeerSynthesisAgent, '_search_peer_reflections',
                 return_value=_PEER_ROWS,
             ):
            PeerSynthesisAgent().generate(
                user=self.user, module=self.module,
                save_target=progress,
                save_field='reflection_peer_synthesis',
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )

        rows = AIArtefactProvenance.objects.filter(
            artefact_kind='peer_synthesis',
            artefact_pk=str(progress.pk),
            user=self.user,
        )
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows.first().model_name, 'gemini-2.5-flash')

    def test_idempotent_provenance_on_regenerate(self):
        """Re-running generate() updates the field but does NOT create
        a second provenance row (CP-7 idempotency via get_or_create
        keyed on (kind, pk))."""
        progress = self._make_progress()
        mock_client = self._mock_setup('First synthesis.')

        with patch('apps.agents.peer.get_llm_client', return_value=mock_client), \
             patch.object(
                 PeerSynthesisAgent, '_search_peer_reflections',
                 return_value=_PEER_ROWS,
             ):
            PeerSynthesisAgent().generate(
                user=self.user, module=self.module,
                save_target=progress,
                save_field='reflection_peer_synthesis',
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )

        mock_client.generate.return_value = _gen_result('Second synthesis.')
        with patch('apps.agents.peer.get_llm_client', return_value=mock_client), \
             patch.object(
                 PeerSynthesisAgent, '_search_peer_reflections',
                 return_value=_PEER_ROWS,
             ):
            PeerSynthesisAgent().generate(
                user=self.user, module=self.module,
                save_target=progress,
                save_field='reflection_peer_synthesis',
                reflection_text=_REFLECTION,
                teacher_context=_CONTEXT,
            )

        progress.refresh_from_db()
        self.assertIn('Second synthesis', progress.reflection_peer_synthesis)
        # Exactly one provenance row despite two generates.
        self.assertEqual(
            AIArtefactProvenance.objects.filter(
                artefact_kind='peer_synthesis',
                artefact_pk=str(progress.pk),
            ).count(),
            1,
        )


class PeerConstantsTest(SimpleTestCase):
    """Pin the truncation budget — research artefact, methodology
    decision worth flagging if it ever changes."""

    def test_reflection_prompt_budget_400(self):
        self.assertEqual(PEER_REFLECTION_PROMPT_BUDGET, 400)
