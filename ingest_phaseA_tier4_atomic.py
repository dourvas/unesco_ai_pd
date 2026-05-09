"""
Phase A Tier 4 — Atomic chunk RAG ingest helper

Canonical Tier 3 pattern (from ``ingest_phaseA_tier3_step6_m8.py``) generalised
into a reusable Tier 4 helper for atomic-chunk patches.

USE WHEN:
- Patch is a self-contained text addition (citation footer, callout, cross-link)
- Target module has multiple existing RAG documents that must NOT be disturbed
- Want deterministic atomic-chunk RAG retrieval signal

DO NOT USE WHEN:
- Patch is a substantial main_content rewrite (use generic re-ingest instead)
- Patch is structural (subject_box, SVG, table) covered by existing ingest patterns

INPUTS (config dict or JSON):
    module_code   str   e.g. "M4"
    doc_title     str   e.g. "M4: Scholarly Research Citation Patch (Phase A Tier 4 A1)"
    chunk_text    str   plain-text body for the atomic chunk (will be wrapped
                        with the canonical Tier-3 header).
    patch_id      str   short id, e.g. "scholarly_research_citation_patch"
    tier          str   e.g. "phase_a_tier_4"
    indicator     str   UNESCO indicator, e.g. "CG4.1.2"
    sprint        str   optional sprint label, e.g. "sprint_2_cycle_2_1"
    topic_short   str   optional one-line topic descriptor for retrieval header

OUTPUTS (printed + returned):
    doc_id, chunk_id, embedding_length, status

IDEMPOTENCY:
    Aborts (status='skip') if a document with the same ``doc_title`` already exists.

TABLES (verified May 2026):
    ``documents`` (NOT ``modules_ragdocument``)
    ``document_chunks`` (NOT ``modules_ragchunk``)

Reused by: A1 (M4), A2 (M9), A3 (M11), A4 (M7), A5 (M3+M8), A6 (M15),
           A7 (M10), A8 (M15) — see Tier 4 Cluster A inventory.

CLI usage:
    python ingest_phaseA_tier4_atomic.py --config patch_a1_config.json
    python ingest_phaseA_tier4_atomic.py --config patch_a1_config.json --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime

import psycopg2
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

NEW_GENAI_API = False
try:
    from google import genai as _genai_client
    NEW_GENAI_API = True
    _client = _genai_client.Client(api_key=os.getenv("GEMINI_API_KEY"))
except ImportError:
    import google.generativeai as _genai
    _genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    _client = None

DB = dict(
    dbname="unesco_ai_teacher_pd",
    user="postgres",
    password="Django123!",
    host="localhost",
    port="5432",
)


def embed(text: str, retry: int = 3):
    """Generate a 768-dim Gemini embedding for ``text`` with retry."""
    for attempt in range(retry):
        try:
            if NEW_GENAI_API:
                r = _client.models.embed_content(
                    model="models/gemini-embedding-001",
                    contents=text,
                    config={"output_dimensionality": 768},
                )
                if hasattr(r, "embeddings") and r.embeddings:
                    return r.embeddings[0].values
                return r if isinstance(r, list) else r.get("embedding", r)
            return _genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
            )["embedding"]
        except Exception:
            if attempt < retry - 1:
                time.sleep((attempt + 1) * 2)
            else:
                raise


def ingest_atomic_patch(
    *,
    module_code: str,
    doc_title: str,
    chunk_text: str,
    patch_id: str,
    tier: str,
    indicator: str,
    sprint: str | None = None,
    topic_short: str | None = None,
    dry_run: bool = False,
):
    """Insert a single new ``documents`` row + one ``document_chunks`` row.

    Returns a dict with status/doc_id/chunk_id/embedding_length.
    Idempotent: if ``doc_title`` exists, returns status='skip'.
    """
    conn = psycopg2.connect(**DB)
    try:
        with conn.cursor() as cur:
            # Idempotency
            cur.execute(
                "SELECT id FROM documents WHERE title = %s;", (doc_title,),
            )
            existing = cur.fetchone()
            if existing:
                return {
                    "status": "skip",
                    "reason": f"document with title already exists (id={existing[0]})",
                    "doc_id": existing[0],
                    "chunk_id": None,
                    "embedding_length": None,
                }

            # Resolve module_id
            cur.execute(
                "SELECT id, title FROM modules_module WHERE code = %s;",
                (module_code,),
            )
            row = cur.fetchone()
            if row is None:
                return {
                    "status": "error",
                    "reason": f"module_code {module_code!r} not found",
                    "doc_id": None,
                    "chunk_id": None,
                    "embedding_length": None,
                }
            module_id, module_title = row

        # Build the canonical Tier-3 header + body chunk
        header_topic = topic_short or f"Atomic patch: {patch_id}"
        full_chunk = (
            f"Module: {module_code} — {module_title}\n"
            f"Subject: Universal\n"
            f"Type: {header_topic}\n"
            f"UNESCO Indicator: {indicator}\n"
            f"Phase: {tier}{('  Sprint: ' + sprint) if sprint else ''}  "
            f"Patch: {patch_id}\n"
            f"{chunk_text}"
        )

        if dry_run:
            return {
                "status": "dry_run",
                "doc_title": doc_title,
                "module_id": module_id,
                "chunk_text_length": len(full_chunk),
                "preview_first_300": full_chunk[:300],
            }

        # Embed
        emb = embed(full_chunk)
        emb_str = "[" + ",".join(repr(float(v)) for v in emb) + "]"
        # Rate-limit hygiene per HANDOFF
        time.sleep(5.0)

        doc_metadata = {
            "source": "modules_modulecontent",
            "module": module_code,
            "type": f"{patch_id}_patch",
            "phase": tier,
            "patch_id": patch_id,
            "unesco_indicators": [indicator],
            "topic_short": header_topic,
        }
        if sprint:
            doc_metadata["sprint"] = sprint

        chunk_metadata = {
            "patch_date": datetime.utcnow().date().isoformat(),
            "phase": tier,
            "patch_id": patch_id,
            "unesco_indicators": [indicator],
            "atomic": True,
        }
        if sprint:
            chunk_metadata["sprint"] = sprint

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (title, document_type, module_id, file_path, "
                "metadata, created_at, updated_at) "
                "VALUES (%s, 'module_content', %s, 'database', %s::jsonb, NOW(), NOW()) "
                "RETURNING id;",
                (doc_title, module_id, json.dumps(doc_metadata)),
            )
            doc_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO document_chunks (document_id, chunk_text, chunk_index, "
                "embedding, metadata, created_at) "
                "VALUES (%s, %s, 0, %s::vector, %s::jsonb, NOW()) RETURNING id;",
                (doc_id, full_chunk, emb_str, json.dumps(chunk_metadata)),
            )
            chunk_id = cur.fetchone()[0]
            cur.execute(
                "UPDATE documents SET total_chunks = 1, updated_at = NOW() WHERE id = %s;",
                (doc_id,),
            )
            conn.commit()

        return {
            "status": "ok",
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "embedding_length": len(emb),
            "chunk_text_length": len(full_chunk),
        }
    except Exception as exc:
        conn.rollback()
        return {"status": "error", "reason": repr(exc)}
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n", 1)[0])
    parser.add_argument("--config", required=True,
                        help="Path to JSON config with the patch fields.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build the chunk and report length, no DB writes.")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    required = ("module_code", "doc_title", "chunk_text", "patch_id",
                "tier", "indicator")
    missing = [k for k in required if k not in config]
    if missing:
        print(f"❌ config is missing required keys: {missing}")
        return 2

    print("=" * 78)
    print(f"Tier 4 atomic ingest  ({'DRY-RUN' if args.dry_run else 'COMMIT'})")
    print("=" * 78)
    print(f"  module       : {config['module_code']}")
    print(f"  doc_title    : {config['doc_title']}")
    print(f"  patch_id     : {config['patch_id']}")
    print(f"  indicator    : {config['indicator']}")
    print(f"  tier         : {config['tier']}")
    if config.get("sprint"):
        print(f"  sprint       : {config['sprint']}")
    print()

    result = ingest_atomic_patch(dry_run=args.dry_run, **config)
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("status") in ("ok", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
