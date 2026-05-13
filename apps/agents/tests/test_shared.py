"""Unit tests for apps/agents/shared/ infrastructure."""

import json
import logging
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.agents.shared.audit import JSONFormatter, audit_log
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.json_repair import clean_json_response


class JsonRepairTest(SimpleTestCase):
    def test_strips_markdown_json_fence(self):
        raw = '```json\n{"a": 1}\n```'
        cleaned = clean_json_response(raw)
        self.assertEqual(json.loads(cleaned), {'a': 1})

    def test_strips_bare_markdown_fence(self):
        raw = '```\n{"a": 1}\n```'
        cleaned = clean_json_response(raw)
        self.assertEqual(json.loads(cleaned), {'a': 1})

    def test_trims_to_brace_boundaries(self):
        raw = 'preamble {"k": "v"} trailing garbage'
        cleaned = clean_json_response(raw)
        self.assertEqual(json.loads(cleaned), {'k': 'v'})

    def test_replaces_inner_double_quotes_with_singles(self):
        # Gemini sometimes emits unescaped " inside string values;
        # the repair converts them to ' so json.loads succeeds.
        raw = '{"quote": "He said "hi" loudly"}'
        cleaned = clean_json_response(raw)
        parsed = json.loads(cleaned)
        self.assertEqual(parsed['quote'], "He said 'hi' loudly")


class AuditFormatterTest(SimpleTestCase):
    def test_emits_one_line_json_with_extras(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name='agents.audit',
            level=logging.INFO,
            pathname='/x',
            lineno=1,
            msg='agent.generate.complete',
            args=(),
            exc_info=None,
        )
        record.agent = 'RAGFeedbackAgent'
        record.artefact_kind = 'rag_feedback'
        record.skipped_none = None  # should be dropped

        line = formatter.format(record)
        payload = json.loads(line)
        self.assertEqual(payload['event'], 'agent.generate.complete')
        self.assertEqual(payload['agent'], 'RAGFeedbackAgent')
        self.assertEqual(payload['artefact_kind'], 'rag_feedback')
        self.assertEqual(payload['level'], 'INFO')
        self.assertNotIn('skipped_none', payload)


class AuditLogTest(SimpleTestCase):
    def test_emits_through_named_logger(self):
        with self.assertLogs('agents.audit', level='INFO') as cm:
            audit_log('agent.test', foo='bar', n=3)
        self.assertEqual(len(cm.records), 1)
        record = cm.records[0]
        self.assertEqual(record.getMessage(), 'agent.test')
        self.assertEqual(record.foo, 'bar')
        self.assertEqual(record.n, 3)


class CostTrackerTest(SimpleTestCase):
    def test_track_emits_structured_audit_record(self):
        with self.assertLogs('agents.audit', level='INFO') as cm:
            track_cost(CostRecord(
                agent='RAGFeedbackAgent',
                model='gemini-2.5-flash',
                tokens=1234,
                cost_eur=0.0003456789,
                artefact_kind='rag_feedback',
            ))
        record = cm.records[0]
        self.assertEqual(record.getMessage(), 'agent.cost')
        self.assertEqual(record.agent, 'RAGFeedbackAgent')
        self.assertEqual(record.tokens, 1234)
        self.assertEqual(record.cost_eur, 0.00034568)
        self.assertEqual(record.artefact_kind, 'rag_feedback')


class LLMClientWrapperTest(SimpleTestCase):
    """Patch the get_llm_client singleton to verify the cost calculation
    in GenerationResult, without hitting Gemini."""

    def test_get_llm_client_is_singleton(self):
        from apps.agents.shared.llm_client import (
            get_llm_client, reset_llm_client_for_tests,
        )
        reset_llm_client_for_tests()
        with patch(
            'apps.agents.shared.llm_client.LLMClient.__init__',
            return_value=None,
        ):
            a = get_llm_client()
            b = get_llm_client()
            self.assertIs(a, b)
        reset_llm_client_for_tests()
