"""
Module RAG Ingest Script — Generic
====================================
Ingests module main content + subject-specific examples into the RAG system.

Works for any module. Replaces module-specific scripts (ingest_m5_rag.py, etc).

Run from project root:
    python ingest_module_rag.py M5             # full re-ingest of M5
    python ingest_module_rag.py M8             # full re-ingest of M8
    python ingest_module_rag.py M5 --dry-run   # show what would happen
    python ingest_module_rag.py M5 --no-delete # incremental (NOT recommended)

Prerequisites:
    - .env with GEMINI_API_KEY
    - Module record exists in modules_module
    - Content records exist in modules_modulecontent
    - documents + document_chunks tables exist

Default behaviour: Deletes existing documents/chunks for the module, then
re-ingests. This is safe for re-running after content updates.
"""

import os
import sys
import argparse
import psycopg2
from psycopg2.extras import execute_values
import json
from dotenv import load_dotenv
import re
from datetime import datetime
import time

load_dotenv()

# -- API setup ---------------------------------------------------------
NEW_GENAI_API = False
try:
    from google import genai as genai_client
    NEW_GENAI_API = True
    print("Using NEW google.genai API")
    client = genai_client.Client(api_key=os.getenv('GEMINI_API_KEY'))
except ImportError:
    import google.generativeai as genai
    print("Using OLD google.generativeai API")
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Subject-box content types this script knows about.
# Add new types here when introducing new section patterns.
KNOWN_SUBJECT_BOX_TYPES = {
    'subject_box_part2': 'Tacit Knowledge / GenAI capabilities',
    'subject_box_part3': 'Subject-specific case study',
    'subject_box_part4': 'Reflection on Professional Thinking',
    'subject_box_orchestration': 'Orchestration Move',
    # Future: 'subject_box_part5': '...',
}


# ======================================================================
# HELPERS
# ======================================================================

def clean_text(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
    return text.strip()


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chars_per_chunk = chunk_size * 4
    chars_overlap = overlap * 4
    chunks = []
    start = 0
    while start < len(text):
        end = start + chars_per_chunk
        if end < len(text):
            period_pos = text.rfind('.', end - 200, end)
            if period_pos > start:
                end = period_pos + 1
        chunk = text[start:end].strip()
        if len(chunk) > 100:
            chunks.append(chunk)
        start = end - chars_overlap
    return chunks


def generate_embedding(text, retry_count=3):
    for attempt in range(retry_count):
        try:
            if NEW_GENAI_API:
                result = client.models.embed_content(
                    model="models/gemini-embedding-001",
                    contents=text,
                    config={"output_dimensionality": 768}
                )
                if hasattr(result, 'embeddings') and len(result.embeddings) > 0:
                    return result.embeddings[0].values
                return result if isinstance(result, list) else result.get('embedding', result)
            else:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                return result['embedding']
        except Exception as e:
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2
                print(f"    Retry {attempt + 1}/{retry_count} in {wait_time}s... ({str(e)[:50]})")
                time.sleep(wait_time)
            else:
                print(f"    Failed after {retry_count} attempts: {e}")
                return None


def generate_embeddings_batch(chunks, batch_size=10):
    embeddings = []
    total = len(chunks)
    print(f"  Generating embeddings for {total} chunks...")
    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        batch_end = min(i + batch_size, total)
        print(f"    Processing chunks {i+1}-{batch_end}/{total}")
        for chunk in batch:
            embedding = generate_embedding(chunk)
            embeddings.append(embedding)
            time.sleep(5.0)
        print(f"    Progress: {(batch_end / total * 100):.1f}%")
    successful = sum(1 for e in embeddings if e is not None)
    print(f"  Generated {successful}/{len(embeddings)} embeddings successfully")
    return embeddings


def store_document(conn, title, doc_type, module_id, file_path, metadata):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (title, document_type, module_id, file_path, metadata, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), NOW())
        RETURNING id;
    """, (title, doc_type, module_id, file_path, json.dumps(metadata)))
    doc_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    return doc_id


def store_chunks(conn, doc_id, chunks, embeddings):
    cursor = conn.cursor()
    data = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        if embedding is not None:
            data.append((doc_id, chunk, idx, embedding, json.dumps({})))
    if not data:
        print("  No valid embeddings to store!")
        cursor.close()
        return
    print(f"  Storing {len(data)} chunks (skipped {len(chunks) - len(data)} failed)...")
    execute_values(
        cursor,
        """
        INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding, metadata, created_at)
        VALUES %s
        """,
        data,
        template="(%s, %s, %s, %s, %s::jsonb, NOW())"
    )
    cursor.execute("""
        UPDATE documents SET total_chunks = %s, updated_at = NOW() WHERE id = %s;
    """, (len(data), doc_id))
    conn.commit()
    cursor.close()
    print(f"  Stored {len(data)} chunks in database")


# ======================================================================
# DELETE EXISTING (for safe re-ingest)
# ======================================================================

def delete_existing_module_documents(conn, module_code, dry_run=False):
    """Remove all RAG documents and chunks for a given module.

    Cascade delete via ON DELETE CASCADE assumed. If not, we delete chunks first.
    """
    cursor = conn.cursor()

    # Find existing documents for this module
    cursor.execute("""
        SELECT d.id, d.title, COUNT(dc.id) AS chunks
        FROM documents d
        LEFT JOIN document_chunks dc ON d.id = dc.document_id
        WHERE d.title LIKE %s
        GROUP BY d.id, d.title
        ORDER BY d.id;
    """, (f"{module_code}:%",))
    existing = cursor.fetchall()

    if not existing:
        print(f"  No existing documents for {module_code} — nothing to delete.")
        cursor.close()
        return 0

    print(f"\n  Found {len(existing)} existing document(s) for {module_code}:")
    total_chunks = 0
    for doc_id, title, chunks in existing:
        print(f"    [{doc_id}] {title} ({chunks} chunks)")
        total_chunks += chunks

    if dry_run:
        print(f"  DRY RUN — would delete {len(existing)} documents and {total_chunks} chunks.")
        cursor.close()
        return total_chunks

    # Delete chunks first (in case CASCADE not set)
    cursor.execute("""
        DELETE FROM document_chunks
        WHERE document_id IN (
            SELECT id FROM documents WHERE title LIKE %s
        );
    """, (f"{module_code}:%",))
    chunks_deleted = cursor.rowcount

    # Then delete documents
    cursor.execute("""
        DELETE FROM documents WHERE title LIKE %s;
    """, (f"{module_code}:%",))
    docs_deleted = cursor.rowcount

    conn.commit()
    cursor.close()

    print(f"  DELETED: {docs_deleted} documents, {chunks_deleted} chunks.")
    return chunks_deleted


# ======================================================================
# PROCESSING FUNCTIONS
# ======================================================================

def process_module_content(conn, module_code, module_title, dry_run=False):
    """Process module main content from database."""
    print(f"\n{'='*70}")
    print(f"Processing main content: {module_code}")
    print(f"{'='*70}")

    cursor = conn.cursor()
    cursor.execute("""
        SELECT mc.content_data, m.id
        FROM modules_modulecontent mc
        JOIN modules_module m ON mc.module_id = m.id
        WHERE m.code = %s AND mc.content_type = 'main_content'
        AND mc.subject_area = 'Universal';
    """, (module_code,))
    row = cursor.fetchone()
    cursor.close()

    if not row:
        print(f"  No main content found for {module_code}!")
        return False

    text, module_id = row
    print(f"  Retrieved {len(text):,} characters")

    text = clean_text(text)
    chunks = chunk_text(text)
    print(f"  Created {len(chunks)} chunks")

    if dry_run:
        print(f"  DRY RUN — would generate {len(chunks)} embeddings and store.")
        return True

    embeddings = generate_embeddings_batch(chunks)

    title = f"{module_code}: {module_title} - Main Content"
    doc_id = store_document(
        conn,
        title=title,
        doc_type="module_content",
        module_id=module_id,
        file_path="database",
        metadata={'source': 'modules_modulecontent', 'module': module_code}
    )
    store_chunks(conn, doc_id, chunks, embeddings)

    print(f"COMPLETE: {title}")
    return True


def process_module_subject_examples(conn, module_code, module_title, dry_run=False):
    """Process all subject_box_* records for the module."""
    print(f"\n{'='*70}")
    print(f"Processing subject examples: {module_code}")
    print(f"{'='*70}")

    cursor = conn.cursor()
    placeholder = ','.join(['%s'] * len(KNOWN_SUBJECT_BOX_TYPES))
    cursor.execute(f"""
        SELECT mc.subject_area, mc.content_type, mc.content_data, m.id
        FROM modules_modulecontent mc
        JOIN modules_module m ON mc.module_id = m.id
        WHERE m.code = %s
        AND mc.content_type IN ({placeholder})
        ORDER BY mc.subject_area, mc.content_type;
    """, (module_code, *KNOWN_SUBJECT_BOX_TYPES.keys()))
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        print(f"  No subject examples found for {module_code}!")
        return False

    module_id = rows[0][3]

    # Breakdown
    by_type = {}
    for _, ct, _, _ in rows:
        by_type[ct] = by_type.get(ct, 0) + 1
    print(f"  Found {len(rows)} subject records:")
    for ct, count in sorted(by_type.items()):
        label = KNOWN_SUBJECT_BOX_TYPES.get(ct, ct)
        print(f"    {ct} ({label}): {count}")

    chunks = []
    for subject_area, content_type, content_data, _ in rows:
        type_label = KNOWN_SUBJECT_BOX_TYPES.get(content_type, content_type)
        text = (
            f"Subject: {subject_area}\n"
            f"Type: {type_label}\n"
            f"{clean_text(content_data)}"
        )
        if len(text) > 100:
            chunks.append(text)

    print(f"  Created {len(chunks)} subject chunks")

    if dry_run:
        print(f"  DRY RUN — would generate {len(chunks)} embeddings and store.")
        return True

    embeddings = generate_embeddings_batch(chunks)

    title = f"{module_code}: {module_title} - Subject Examples"
    doc_id = store_document(
        conn,
        title=title,
        doc_type="module_content",
        module_id=module_id,
        file_path="database",
        metadata={
            'source': 'modules_modulecontent',
            'module': module_code,
            'type': 'subject_examples',
            'content_types_included': list(by_type.keys()),
        }
    )
    store_chunks(conn, doc_id, chunks, embeddings)

    print(f"COMPLETE: {title}")
    return True


# ======================================================================
# MAIN
# ======================================================================

def get_module_title(conn, module_code):
    """Look up the human-readable title from the modules_module table."""
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM modules_module WHERE code = %s;", (module_code,))
    row = cursor.fetchone()
    cursor.close()
    return row[0] if row else module_code


def main():
    parser = argparse.ArgumentParser(description='Generic module RAG ingest.')
    parser.add_argument('module_code', help='Module code (e.g. M5, M8, M14)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would happen without making changes')
    parser.add_argument('--no-delete', action='store_true',
                        help='Skip deletion of existing documents (incremental — NOT recommended for re-ingest)')
    args = parser.parse_args()

    module_code = args.module_code.upper()

    print("\n" + "="*70)
    print(f"MODULE RAG INGEST — {module_code}")
    print("="*70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.dry_run:
        print("MODE: DRY RUN (no changes will be made)")
    if args.no_delete:
        print("MODE: NO DELETE (incremental ingest — may cause duplicates!)")
    print()

    conn = psycopg2.connect(**DB_CONFIG)
    success_count = 0

    try:
        # Pre-flight check
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM modules_module WHERE code = %s;", (module_code,))
        row = cursor.fetchone()
        if not row:
            print(f"ERROR: Module {module_code} not found in modules_module!")
            conn.close()
            return

        module_title = get_module_title(conn, module_code)
        print(f"Module: {module_code} — {module_title}")

        # Show content summary
        cursor.execute("""
            SELECT content_type, COUNT(*)
            FROM modules_modulecontent mc
            JOIN modules_module m ON mc.module_id = m.id
            WHERE m.code = %s
            GROUP BY content_type
            ORDER BY content_type;
        """, (module_code,))
        content_summary = cursor.fetchall()
        cursor.close()

        print(f"\n{module_code} content in modules_modulecontent:")
        for ct, count in content_summary:
            ingest_marker = ""
            if ct == 'main_content':
                ingest_marker = "  [will ingest]"
            elif ct in KNOWN_SUBJECT_BOX_TYPES:
                ingest_marker = f"  [will ingest as: {KNOWN_SUBJECT_BOX_TYPES[ct]}]"
            print(f"  {ct}: {count} records{ingest_marker}")
        print()

        # Delete existing (unless --no-delete)
        if not args.no_delete:
            delete_existing_module_documents(conn, module_code, dry_run=args.dry_run)

        # Ingest 1: Main Content
        if process_module_content(conn, module_code, module_title, dry_run=args.dry_run):
            success_count += 1

        # Ingest 2: Subject Examples
        if process_module_subject_examples(conn, module_code, module_title, dry_run=args.dry_run):
            success_count += 1

        # Summary
        if not args.dry_run:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.title, COUNT(dc.id) as chunks
                FROM documents d
                LEFT JOIN document_chunks dc ON d.id = dc.document_id
                WHERE d.title LIKE %s
                GROUP BY d.id, d.title
                ORDER BY d.id;
            """, (f"{module_code}:%",))
            stats = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM document_chunks;")
            total_chunks = cursor.fetchone()[0]
            cursor.close()

            print("\n" + "="*70)
            print(f"{module_code} INGEST COMPLETE")
            print("="*70)
            print(f"Successful: {success_count}/2 ingests")
            print()
            print(f"{module_code} documents now in DB:")
            for title, chunks in stats:
                print(f"  {title}: {chunks} chunks")
            print(f"\nTotal chunks across all modules: {total_chunks}")

            module_chunks = sum(c for _, c in stats)
            cost = (module_chunks * 600 / 1_000_000) * 0.02
            print(f"Estimated embedding cost for this run: EUR {cost:.4f}")

        print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
