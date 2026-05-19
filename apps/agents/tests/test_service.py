"""Tests for the ServiceAgent marker class (Phase D.3b).

ServiceAgent is the parent of the service-agent branch — agents that
operate on other agents' outputs (XAIAgent is the first concrete
member). It is a sibling of ResearchInstrumentAgent under BaseAIAgent.
"""

from django.test import SimpleTestCase

from apps.agents.base import BaseAIAgent
from apps.agents.research import ResearchInstrumentAgent
from apps.agents.service import ServiceAgent


class ServiceAgentHierarchyTest(SimpleTestCase):

    def test_inherits_from_base_ai_agent(self):
        self.assertTrue(issubclass(ServiceAgent, BaseAIAgent))

    def test_is_not_a_research_instrument_agent(self):
        """The two branches are distinct: a service agent is not a
        research-instrument agent, and vice versa."""
        self.assertFalse(
            issubclass(ServiceAgent, ResearchInstrumentAgent)
        )
        self.assertFalse(
            issubclass(ResearchInstrumentAgent, ServiceAgent)
        )

    def test_cannot_be_instantiated_directly(self):
        """ServiceAgent is still abstract — it does not implement
        _do_generate. Only concrete subclasses become instantiable."""
        with self.assertRaises(TypeError):
            ServiceAgent()
