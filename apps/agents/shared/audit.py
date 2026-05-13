"""
Structured audit logger for the agent layer.

Replaces the print()-everywhere pattern in rag_query_system.py with a
JSON-record logger that the dissertation analysis pipeline can parse.

Backed by stdlib `logging` with a custom JSON formatter — no new heavy
dependency. The logger name is 'agents.audit'. config/settings.py wires
this up in commit 1 so structured records appear on stdout in DEBUG and
can be redirected to a file in production.
"""

import json
import logging
from typing import Any


_LOGGER_NAME = 'agents.audit'


class JSONFormatter(logging.Formatter):
    """Emit each record as a one-line JSON object.

    Fields: timestamp, level, event, plus whatever was passed in extras.
    Keeps the output greppable and machine-parseable.
    """

    RESERVED = {
        'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
        'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
        'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
        'processName', 'process', 'message', 'asctime', 'taskName',
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            'ts': self.formatTime(record, '%Y-%m-%dT%H:%M:%S'),
            'level': record.levelname,
            'event': record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key in self.RESERVED or key.startswith('_'):
                continue
            if value is None:
                continue
            try:
                json.dumps(value)
                payload[key] = value
            except (TypeError, ValueError):
                payload[key] = repr(value)
        return json.dumps(payload, ensure_ascii=False)


def audit_log(event: str, **fields: Any) -> None:
    """Emit one structured record to the agents audit log.

    `event` is the canonical event name (e.g. 'agent.generate.start',
    'agent.cost', 'agent.provenance.write'). Extra kwargs become fields
    in the JSON payload — None values are dropped by the formatter.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    logger.info(event, extra=fields)
