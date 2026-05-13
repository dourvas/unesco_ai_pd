"""
Unified raw-SQL helper for the agent layer.

Today the codebase carries three DB-connection idioms:
  1. rag_query_system.DB_CONFIG     — psycopg2 with hardcoded creds
  2. apps/modules/views.py          — psycopg2 with settings.DATABASES
  3. apps/compliance/services.py    — Django ORM `connection`

Idiom 1 is a security smell (the password lives in the repo). All three
also bypass Django's transaction management, so they can't join a
caller's transaction.atomic block.

This module exposes idiom 3 — Django's connection — as the single way
agents reach raw SQL. Joins the request transaction, no credential leak,
no separate connection lifecycle.
"""

from contextlib import contextmanager

from django.db import connection


@contextmanager
def dict_cursor():
    """Yield a Django cursor that returns rows as dicts.

    Used by agents that need RealDictCursor-style result rows (the RAG
    similarity search returns 7 columns by name). Equivalent to
    psycopg2.extras.RealDictCursor but goes through Django.
    """
    with connection.cursor() as cur:
        yield _DictCursorAdapter(cur)


class _DictCursorAdapter:
    """Minimal RealDictCursor adapter on top of a Django cursor.

    Only `execute`, `fetchall`, `fetchone`, `close` are needed by the
    code paths migrating from psycopg2.extras.RealDictCursor.
    """

    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=None):
        return self._cur.execute(sql, params)

    def _row_to_dict(self, row):
        if row is None:
            return None
        cols = [d[0] for d in self._cur.description]
        return dict(zip(cols, row))

    def fetchall(self):
        return [self._row_to_dict(r) for r in self._cur.fetchall()]

    def fetchone(self):
        return self._row_to_dict(self._cur.fetchone())

    def close(self):
        # Django manages cursor lifecycle via the context manager; no-op.
        pass
