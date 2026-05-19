"""XAIAgent tests — the DTP XAI narrative service agent (Phase D.3b).

The XAIAgent is the first concrete ServiceAgent. It explains a teacher's
stored DTP composite in domain-driven natural language. These tests use
mocked Gemini calls — they verify hierarchy, the prompt, parsing,
persistence, provenance and the failure fallback, NOT the quality of the
generated explanation (that is the separate live-output check, design
proposal §9).
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from apps.agents.base import BaseAIAgent
from apps.agents.research import ResearchInstrumentAgent
from apps.agents.service import ServiceAgent
from apps.agents.shared.llm_client import GenerationResult
from apps.agents.tests._fixtures import load_prompt_fixture
from apps.agents.xai import XAI_FALLBACK, XAIAgent
from apps.compliance.models import AIArtefactProvenance
from apps.modules.models import Module, UserModuleProgress


# Canonical input for the frozen xai.txt prompt fixture. Regenerating
# the fixture requires re-running XAIAgent._build_prompt with exactly
# this input.
_FIXTURE_ASPECT = 'Human-Centred Mindset'
_FIXTURE_COMPOSITE = {
    'schema': 'dtp_dual_v1',
    'current_module': 'M6',
    'narrative': 'Across these modules, your reflection ...',
    'signals': {
        'vertical': {
            'comparison_module': 'M1',
            'similarity': 0.8832,
            'themes': {
                'increased_themes': ['pedagogical fit', 'auditing rigor'],
                'decreased_themes': ['technical focus'],
                'stable_themes': ['human judgment'],
            },
        },
        'temporal': {
            'comparison_module': 'M5',
            'similarity': 0.8717,
            'themes': {
                'increased_themes': ['impact awareness'],
                'decreased_themes': ['general reliability'],
                'stable_themes': ['AI context'],
            },
        },
    },
}

_EXPLANATION_RESPONSE = (
    '<reasoning>Focus moved toward pedagogy.</reasoning>\n'
    '<explanation>Your reflection has shifted its emphasis toward the '
    'pedagogical fit of AI while keeping human judgment steady. A theme '
    'appearing with less emphasis is a movement of attention, not a '
    'decline.</explanation>'
)
_EXPLANATION_TEXT = (
    'Your reflection has shifted its emphasis toward the pedagogical fit '
    'of AI while keeping human judgment steady. A theme appearing with '
    'less emphasis is a movement of attention, not a decline.'
)


def _gen_result(text):
    return GenerationResult(
        text=text, model='gemini-2.5-flash',
        tokens_estimate=120, cost_eur_estimate=0.0000335,
    )


# ----------------------------------------------------------------------
# Hierarchy
# ----------------------------------------------------------------------
class XAIHierarchyTest(SimpleTestCase):

    def test_is_a_service_agent(self):
        self.assertTrue(issubclass(XAIAgent, ServiceAgent))

    def test_is_a_base_ai_agent(self):
        self.assertTrue(issubclass(XAIAgent, BaseAIAgent))

    def test_is_not_a_research_instrument_agent(self):
        """The XAIAgent belongs to the service-agent branch, not the
        research-instrument branch."""
        self.assertFalse(issubclass(XAIAgent, ResearchInstrumentAgent))

    def test_artefact_kind(self):
        self.assertEqual(XAIAgent.artefact_kind, 'xai_narrative')

    def test_model_name(self):
        self.assertEqual(XAIAgent.model_name, 'gemini-2.5-flash')


# ----------------------------------------------------------------------
# Prompt
# ----------------------------------------------------------------------
class XAIPromptTest(SimpleTestCase):

    def test_prompt_matches_frozen_fixture(self):
        expected = load_prompt_fixture('xai')
        actual = XAIAgent._build_prompt(_FIXTURE_COMPOSITE, _FIXTURE_ASPECT)
        self.assertEqual(actual, expected)

    def test_prompt_layer0(self):
        prompt = XAIAgent._build_prompt(_FIXTURE_COMPOSITE, _FIXTURE_ASPECT)
        # Non-evaluative instruction.
        self.assertIn('do not evaluate whether the', prompt)
        # Symmetric non-evaluation — no decline AND no progress framing.
        self.assertIn('growing sophistication', prompt)
        # Domain-driven instruction (no numbers).
        self.assertIn('never in numbers', prompt)
        # Structured output tag.
        self.assertIn('<explanation>', prompt)
        # The UNESCO aspect label is interpolated.
        self.assertIn('Human-Centred Mindset', prompt)
        # The cosine similarity value is NOT fed to the prompt.
        self.assertNotIn('0.8832', prompt)

    def test_temporal_only_omits_vertical_block(self):
        """An Acquire module supplies only the temporal signal; the
        prompt then has no vertical-comparison block."""
        composite = {
            'current_module': 'M2',
            'signals': {
                'temporal': _FIXTURE_COMPOSITE['signals']['temporal'],
            },
        }
        prompt = XAIAgent._build_prompt(composite, 'Ethics')
        self.assertNotIn('Within the same UNESCO competency area', prompt)
        self.assertIn('immediately preceding module', prompt)
        self.assertIn('<explanation>', prompt)


# ----------------------------------------------------------------------
# Explanation parsing
# ----------------------------------------------------------------------
class XAIParseTest(SimpleTestCase):

    def test_extracts_explanation_block(self):
        self.assertEqual(
            XAIAgent._parse_explanation(_EXPLANATION_RESPONSE),
            _EXPLANATION_TEXT,
        )

    def test_falls_back_to_whole_text_when_no_tag(self):
        self.assertEqual(
            XAIAgent._parse_explanation('  plain explanation  '),
            'plain explanation',
        )

    def test_falls_back_to_canned_when_empty(self):
        self.assertEqual(XAIAgent._parse_explanation('   '), XAI_FALLBACK)

    def test_truncated_reasoning_scaffold_is_not_leaked(self):
        """A response cut off inside the <reasoning> block (no
        <explanation> reached) must not surface the raw scaffold to the
        teacher — it degrades to the canned fallback."""
        truncated = (
            '<reasoning>The signal indicates a developmental shift in the '
            "teacher's focus. Comparing M1 to M6, there is a clear increase "
            'in attention on the practical pedagogical application, and '
            'comparing M'
        )
        self.assertEqual(
            XAIAgent._parse_explanation(truncated), XAI_FALLBACK,
        )


# ----------------------------------------------------------------------
# generate() — persistence, provenance, cost, fallback
# ----------------------------------------------------------------------
class XAIGenerateTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('xai_user', password='pw')
        cls.module = Module.objects.create(
            code='AGXAI', title='XAI agent test', description='t',
            order_index=988, unesco_aspect='human_centered',
            proficiency_level='Deepen', is_published=True,
        )

    def _progress(self):
        return UserModuleProgress.objects.create(
            user=self.user, module=self.module,
        )

    def _generate(self, progress, mock_client):
        with patch('apps.agents.xai.get_llm_client', return_value=mock_client):
            return XAIAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp_xai',
                dtp_composite=_FIXTURE_COMPOSITE,
                aspect_label='Human-Centred Mindset',
            )

    def test_generate_persists_explanation_and_provenance(self):
        progress = self._progress()
        mock_client = MagicMock()
        mock_client.generate.return_value = _gen_result(_EXPLANATION_RESPONSE)

        result = self._generate(progress, mock_client)

        self.assertEqual(result, _EXPLANATION_TEXT)
        progress.refresh_from_db()
        self.assertEqual(progress.reflection_dtp_xai, _EXPLANATION_TEXT)
        self.assertTrue(
            AIArtefactProvenance.objects.filter(
                artefact_kind='xai_narrative',
                artefact_pk=str(progress.pk),
                user=self.user,
                model_name='gemini-2.5-flash',
            ).exists(),
            'Expected an xai_narrative provenance row.',
        )

    def test_one_cost_event_per_generate(self):
        progress = self._progress()
        mock_client = MagicMock()
        mock_client.generate.return_value = _gen_result(_EXPLANATION_RESPONSE)
        with patch('apps.agents.xai.get_llm_client', return_value=mock_client), \
             self.assertLogs('agents.audit', level='INFO') as cm:
            XAIAgent().generate(
                user=self.user, module=self.module,
                save_target=progress, save_field='reflection_dtp_xai',
                dtp_composite=_FIXTURE_COMPOSITE,
                aspect_label='Human-Centred Mindset',
            )
        cost_events = [r for r in cm.records if r.getMessage() == 'agent.cost']
        self.assertEqual(len(cost_events), 1)

    def test_fallback_when_gemini_returns_none(self):
        """A Gemini failure degrades to the canned fallback; generate()
        still persists and still writes provenance."""
        progress = self._progress()
        mock_client = MagicMock()
        mock_client.generate.return_value = None

        result = self._generate(progress, mock_client)

        self.assertEqual(result, XAI_FALLBACK)
        progress.refresh_from_db()
        self.assertEqual(progress.reflection_dtp_xai, XAI_FALLBACK)
        self.assertTrue(
            AIArtefactProvenance.objects.filter(
                artefact_kind='xai_narrative',
                artefact_pk=str(progress.pk),
            ).exists()
        )
