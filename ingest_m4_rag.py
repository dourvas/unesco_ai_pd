"""
M4 RAG Ingest Script
====================
Module: AI Tools for Teaching
UNESCO Aspect 4: AI Pedagogy | Level: Acquire

Ingests:
  1. M4 Main Content (Universal) from modules_modulecontent
  2. M4 Subject-Specific Examples (subject_box_part2 + subject_box_part4)

Run from project root:
    python ingest_m4_rag.py

Prerequisites:
    - .env with GEMINI_API_KEY
    - M4 module record exists in modules_module
    - M4 main_content + subject_box records exist in modules_modulecontent
    - documents + document_chunks tables exist (same schema as M1/M2/M3/M6/M7/M12)
"""

import os
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

CHUNK_SIZE = 800    # tokens (~600 words)
CHUNK_OVERLAP = 100


# ======================================================================
# HELPERS — identical to M3 ingest
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
            time.sleep(5.0)  # Rate limiting — free tier
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
# M4-SPECIFIC PROCESSING FUNCTIONS
# ======================================================================

def process_module_content(conn, module_code, title):
    """Process module main content from database."""
    print(f"\n{'='*70}")
    print(f"Processing: {title}")
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

    embeddings = generate_embeddings_batch(chunks)

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


def process_module_subject_examples(conn, module_code, title):
    """Process subject boxes (part2 + part4)."""
    print(f"\n{'='*70}")
    print(f"Processing: {title}")
    print(f"{'='*70}")

    cursor = conn.cursor()
    cursor.execute("""
        SELECT mc.subject_area, mc.content_type, mc.content_data, m.id
        FROM modules_modulecontent mc
        JOIN modules_module m ON mc.module_id = m.id
        WHERE m.code = %s
        AND mc.content_type IN ('subject_box_part2', 'subject_box_part4')
        ORDER BY mc.subject_area, mc.content_type;
    """, (module_code,))
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        print(f"  No subject examples found for {module_code}!")
        return False

    module_id = rows[0][3]
    chunks = []
    for subject_area, content_type, content_data, _ in rows:
        text = f"Subject: {subject_area}\nType: {content_type}\n{clean_text(content_data)}"
        if len(text) > 100:
            chunks.append(text)

    print(f"  Created {len(chunks)} subject chunks from {len(rows)} records")

    embeddings = generate_embeddings_batch(chunks)

    doc_id = store_document(
        conn,
        title=title,
        doc_type="module_content",
        module_id=module_id,
        file_path="database",
        metadata={'source': 'modules_modulecontent', 'module': module_code, 'type': 'subject_examples'}
    )
    store_chunks(conn, doc_id, chunks, embeddings)

    print(f"COMPLETE: {title}")
    return True


# ======================================================================
# MAIN
# ======================================================================

def main():
    print("\n" + "="*70)
    print("M4 RAG INGEST — AI Tools for Teaching")
    print("="*70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    conn = psycopg2.connect(**DB_CONFIG)
    success_count = 0

    try:
        # -- Pre-flight check ------------------------------------------
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM modules_module WHERE code = 'M4';")
        row = cursor.fetchone()
        if not row:
            print("ERROR: M4 module record not found in modules_module!")
            print("Run the M4 TAB2 SQL insert first.")
            conn.close()
            return

        cursor.execute("""
            SELECT content_type, COUNT(*)
            FROM modules_modulecontent mc
            JOIN modules_module m ON mc.module_id = m.id
            WHERE m.code = 'M4'
            GROUP BY content_type
            ORDER BY content_type;
        """)
        content_summary = cursor.fetchall()
        cursor.close()

        print("M4 content in modules_modulecontent:")
        for ct, count in content_summary:
            print(f"  {ct}: {count} records")
        print()

        # -- Verify expected content -----------------------------------
        expected = {
            'main_content':       1,
            'subject_box_part2': 16,
            'subject_box_part4': 16,
            'assessment':         1,
            'reflection':        17,
        }
        content_dict = dict(content_summary)
        all_ok = True
        for ct, expected_count in expected.items():
            actual = content_dict.get(ct, 0)
            status = "✅" if actual >= expected_count else "⚠️"
            print(f"  {status} {ct}: {actual} (expected {expected_count})")
            if actual < expected_count:
                all_ok = False

        if not all_ok:
            print("\n⚠️  Some content missing — proceeding with available content.")
        print()

        # -- Ingest 1: Main Content ------------------------------------
        if process_module_content(
            conn,
            'M4',
            'M4: AI Tools for Teaching - Main Content'
        ):
            success_count += 1

        # -- Ingest 2: Subject Examples --------------------------------
        if process_module_subject_examples(
            conn,
            'M4',
            'M4: AI Tools for Teaching - Subject Examples'
        ):
            success_count += 1

        # -- Summary ---------------------------------------------------
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.title, COUNT(dc.id) as chunks
            FROM documents d
            LEFT JOIN document_chunks dc ON d.id = dc.document_id
            WHERE d.title LIKE 'M4%'
            GROUP BY d.id, d.title
            ORDER BY d.id;
        """)
        m4_stats = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM document_chunks;")
        total_chunks = cursor.fetchone()[0]
        cursor.close()

        print("\n" + "="*70)
        print("M4 INGEST COMPLETE")
        print("="*70)
        print(f"Successful: {success_count}/2")
        print()
        print("M4 documents ingested:")
        for title, chunks in m4_stats:
            print(f"  {title}: {chunks} chunks")
        print(f"\nTotal chunks in database (all modules): {total_chunks}")
        print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Cost estimate
        m4_chunks = sum(c for _, c in m4_stats)
        cost = (m4_chunks * 600 / 1_000_000) * 0.02
        print(f"Estimated embedding cost: EUR {cost:.4f}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
