"""
M4 RAG Incremental Ingest Script
=================================
Module: AI Tools for Teaching
UNESCO Aspect 4: AI Pedagogy | Level: Acquire

Ingests ONLY the new subject_box_part3 records added April 2026:
  - 16 discipline-specific teacher judgment vs AI scenarios (one per subject)

Does NOT re-ingest main_content or existing subject_box_part2/part4
(those are already in the RAG corpus).

Run from project root:
    python ingest_m4_part3_rag.py

Prerequisites:
    - .env with GEMINI_API_KEY
    - M4 module record exists in modules_module
    - 16 subject_box_part3 records exist in modules_modulecontent
    - documents + document_chunks tables exist
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


# ======================================================================
# HELPERS
# ======================================================================

def clean_text(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
    return text.strip()


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
# M4-SPECIFIC: subject_box_part3 only
# ======================================================================

def process_m4_part3_examples(conn):
    """
    Ingest the 16 subject_box_part3 records for M4.
    Each record is a discipline-specific scenario illustrating
    where AI helps and where teacher judgment is irreplaceable.
    Added April 2026 as part of the platform optimization.
    """
    print(f"\n{'='*70}")
    print("Processing: M4 subject_box_part3 — Teacher Judgment Scenarios")
    print(f"{'='*70}")

    cursor = conn.cursor()

    cursor.execute("SELECT id FROM modules_module WHERE code = 'M4';")
    row = cursor.fetchone()
    if not row:
        print("ERROR: M4 module record not found!")
        cursor.close()
        return False
    module_id = row[0]

    cursor.execute("""
        SELECT subject_area, content_data
        FROM modules_modulecontent
        WHERE module_id = %s
        AND content_type = 'subject_box_part3'
        ORDER BY subject_area;
    """, (module_id,))
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        print("ERROR: No subject_box_part3 records found for M4!")
        print("Run the M4 subject_box_part3 SQL inserts first.")
        return False

    print(f"  Found {len(rows)} subject_box_part3 records")

    chunks = []
    for subject_area, content_data in rows:
        text = (
            f"Module: M4 — AI Tools for Teaching\n"
            f"Subject: {subject_area}\n"
            f"Type: Discipline-specific teacher judgment vs AI scenario (Selecting AI Tools — Part 2)\n"
            f"{clean_text(content_data)}"
        )
        if len(text) > 100:
            chunks.append(text)
            print(f"  ✓ {subject_area}")

    print(f"\n  Created {len(chunks)} chunks")

    embeddings = generate_embeddings_batch(chunks)

    doc_id = store_document(
        conn,
        title='M4: AI Tools for Teaching - Teacher Judgment Scenarios by Subject (Apr 2026)',
        doc_type="module_content",
        module_id=module_id,
        file_path="database",
        metadata={
            'source': 'modules_modulecontent',
            'module': 'M4',
            'type': 'subject_box_part3',
            'added': 'April 2026',
            'description': 'Discipline-specific scenarios showing AI division of labour vs teacher judgment'
        }
    )
    store_chunks(conn, doc_id, chunks, embeddings)

    print(f"\nCOMPLETE: M4 subject_box_part3 ingested as document id={doc_id}")
    return True


# ======================================================================
# MAIN
# ======================================================================

def main():
    print("\n" + "="*70)
    print("M4 INCREMENTAL RAG INGEST — subject_box_part3 (April 2026)")
    print("="*70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    conn = psycopg2.connect(**DB_CONFIG)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM modules_modulecontent mc
            JOIN modules_module m ON mc.module_id = m.id
            WHERE m.code = 'M4'
            AND mc.content_type = 'subject_box_part3';
        """)
        count = cursor.fetchone()[0]
        print(f"subject_box_part3 records in DB: {count} (expected 16)")

        if count < 16:
            print("⚠️  Less than 16 records found — some subjects may be missing.")
        elif count == 16:
            print("✅ All 16 subject records present")

        cursor.execute("""
            SELECT id, title, total_chunks
            FROM documents
            WHERE title LIKE '%M4%part3%'
            OR title LIKE '%M4%Judgment%';
        """)
        existing = cursor.fetchall()
        cursor.close()

        if existing:
            print("\n⚠️  Found existing M4 part3 document(s):")
            for doc_id, title, chunks in existing:
                print(f"   id={doc_id}: {title} ({chunks} chunks)")
            print("   Proceeding will add a NEW document alongside existing ones.")
            print("   If you want to replace, manually DELETE FROM documents WHERE id=X first.\n")

        success = process_m4_part3_examples(conn)

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
        print("INGEST SUMMARY")
        print("="*70)
        print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print()
        print("M4 documents in RAG corpus:")
        for title, chunks in m4_stats:
            print(f"  {title}: {chunks} chunks")
        print(f"\nTotal chunks in database (all modules): {total_chunks}")
        print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        new_chunks = sum(c for _, c in m4_stats if 'part3' in _ or 'Judgment' in _)
        cost = (new_chunks * 600 / 1_000_000) * 0.02
        print(f"Estimated embedding cost for this ingest: EUR {cost:.4f}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
