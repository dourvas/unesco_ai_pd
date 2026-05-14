"""Frozen monolith-prompt snapshots — Layer-1 regression oracle.

Phase E commit 9 deleted rag_query_system.py, so the prompt-parity
tests (test_rag_feedback, test_rtm, test_dtp, test_peer) can no longer
use a live monolith call as the byte-identical oracle. Each captured
prompt was snapshotted to prompt_fixtures/*.txt the moment before
deletion — the files store exactly what rag_query_system.X produced
given the test inputs on commit-9 day.

Going forward, an agent's _build_prompt drifting from its snapshot
fires a clear test failure. Updating a fixture requires explicit
re-capture + commit, so prompt changes can never slip in silently —
the same Layer-1 invariant the live-oracle tests enforced.

Files in prompt_fixtures/:
  rag_feedback.txt   — RAGFeedbackAgent._build_prompt
  rtm.txt            — RTMAgent._build_prompt
  dtp_themes.txt     — DTPAgent._build_themes_prompt
  dtp_narrative.txt  — DTPAgent._build_narrative_prompt
  peer.txt           — PeerSynthesisAgent._build_prompt
"""

import pathlib


_FIXTURE_DIR = pathlib.Path(__file__).parent / 'prompt_fixtures'


def load_prompt_fixture(name: str) -> str:
    """Read a frozen monolith-prompt snapshot.

    Uses `newline=''` so trailing whitespace and exact newline
    characters survive round-trip. Critical for the DTP narrative
    fixture which preserves a literal trailing space after
    "exactly 60 words." (monolith oddity from rag_query_system.py:988,
    deleted in commit 9 but the byte-for-byte snapshot is forever).
    """
    path = _FIXTURE_DIR / f'{name}.txt'
    return path.read_text(encoding='utf-8')
