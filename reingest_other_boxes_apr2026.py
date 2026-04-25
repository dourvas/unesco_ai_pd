"""
PROODOS Re-Ingest: 'other' Subject Boxes (April 2026)
======================================================
Re-ingests the updated subject_box_part2 and subject_box_part4 records
for the 'other' subject area (Primary School Generalist — Dimitris)
across all modules M1–M15.

Strategy:
  1. For each module, find existing document_chunks that came from
     'other' subject_box records (by searching chunk_text for the module code
     and 'other' subject area marker).
  2. Delete those chunks from document_chunks.
  3. If the parent document now has 0 chunks, delete it too.
  4. Re-embed the updated content and store fresh chunks.

Run from project root:
    python reingest_other_boxes_apr2026.py
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

# All updated 'other' box IDs grouped by module
OTHER_BOX_IDS = {
    'M1':  [50, 51],
    'M2':  [88, 89],
    'M3':  [410, 426],
    'M4':  [631, 632],
    'M5':  [671, 687],
    'M6':  [289, 290],
    'M7':  [119, 120],
    'M8':  [478, 496],
    'M9':  [739, 755],
    'M10': [807, 839],
    'M11': [322, 323],
    'M12': [150, 151],
    'M13': [531, 547],
    'M14': [874, 906],
    'M15': [957],
}


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
                print(f"      Retry {attempt + 1}/{retry_count} in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"      Failed: {e}")
                return None


def remove_old_other_chunks(conn, module_code, module_id):
    """
    Remove existing chunks for 'other' subject_box_part2/part4
    from this module's documents. Searches chunk_text for the
    subject area marker.
    """
    cursor = conn.cursor()

    # Find document_chunks where chunk_text contains module code AND 'other'
    # These are the chunks from previous ingests of the 'other' boxes
    cursor.execute("""
        SELECT dc.id, dc.document_id
        FROM document_chunks dc
        JOIN documents d ON dc.document_id = d.id
        WHERE d.module_id = %s
        AND dc.chunk_text LIKE %s
        AND (
            dc.chunk_text LIKE '%%subject_box_part2%%'
            OR dc.chunk_text LIKE '%%subject_box_part4%%'
            OR dc.chunk_text LIKE '%%Subject: other%%'
        );
    """, (module_id, f'%{module_code}%'))

    rows = cursor.fetchall()

    if not rows:
        # Try broader search — chunk may not contain content_type label
        cursor.execute("""
            SELECT dc.id, dc.document_id
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.module_id = %s
            AND dc.chunk_text LIKE '%%Subject: other%%';
        """, (module_id,))
        rows = cursor.fetchall()

    if rows:
        chunk_ids = [r[0] for r in rows]
        doc_ids = list(set(r[1] for r in rows))
        print(f"    Removing {len(chunk_ids)} old 'other' chunk(s)...")
        cursor.execute(
            "DELETE FROM document_chunks WHERE id = ANY(%s);",
            (chunk_ids,)
        )
        # Update total_chunks on affected documents
        for doc_id in doc_ids:
            cursor.execute(
                "UPDATE documents SET total_chunks = (SELECT COUNT(*) FROM document_chunks WHERE document_id = %s), updated_at = NOW() WHERE id = %s;",
                (doc_id, doc_id)
            )
        conn.commit()
    else:
        print(f"    No existing 'other' chunks found for {module_code} — will add fresh")

    cursor.close()
    return len(rows) if rows else 0


def get_or_create_document(conn, module_code, module_id):
    """
    Get the existing main subject_box document for this module,
    or create a new one if none exists.
    """
    cursor = conn.cursor()

    # Look for existing subject_box document for this module
    cursor.execute("""
        SELECT id, title FROM documents
        WHERE module_id = %s
        AND document_type = 'module_content'
        AND (title LIKE %s OR title LIKE %s)
        ORDER BY id DESC
        LIMIT 1;
    """, (module_id, f'{module_code}:%', f'%{module_code}%subject_box%'))

    row = cursor.fetchone()

    if row:
        doc_id, doc_title = row
        print(f"    Using existing document id={doc_id}: {doc_title[:60]}...")
        cursor.close()
        return doc_id
    else:
        # Create a new document for the 'other' box updates
        title = f"{module_code}: Subject Box Updates - Other (Primary Generalist) (Apr 2026)"
        cursor.execute("""
            INSERT INTO documents (title, document_type, module_id, file_path, metadata, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), NOW())
            RETURNING id;
        """, (title, 'module_content', module_id, 'database',
              json.dumps({'source': 'modules_modulecontent', 'module': module_code,
                         'type': 'subject_box_other_update', 'added': 'April 2026'})))
        doc_id = cursor.fetchone()[0]
        conn.commit()
        print(f"    Created new document id={doc_id}")
        cursor.close()
        return doc_id


def process_module_other_boxes(conn, module_code, record_ids):
    print(f"\n  {'='*58}")
    print(f"  {module_code} — other boxes: {record_ids}")
    print(f"  {'='*58}")

    # Get module_id
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM modules_module WHERE code = %s;", (module_code,))
    row = cursor.fetchone()
    if not row:
        print(f"  ❌ Module not found: {module_code}")
        cursor.close()
        return False
    module_id = row[0]

    # Fetch the updated content
    placeholders = ','.join(['%s'] * len(record_ids))
    cursor.execute(f"""
        SELECT mc.id, mc.content_type, mc.subject_area, mc.content_data
        FROM modules_modulecontent mc
        WHERE mc.id IN ({placeholders});
    """, record_ids)
    records = cursor.fetchall()
    cursor.close()

    if not records:
        print(f"  ❌ No records found for IDs: {record_ids}")
        return False

    # Remove old chunks
    remove_old_other_chunks(conn, module_code, module_id)

    # Build new chunks
    chunks = []
    for rec_id, content_type, subject_area, content_data in records:
        text = (
            f"Module: {module_code}\n"
            f"Subject: {subject_area}\n"
            f"Type: {content_type} — Primary School Generalist update (Apr 2026)\n"
            f"{clean_text(content_data)}"
        )
        if len(text) > 100:
            chunks.append(text)
            print(f"    ✓ Prepared: {content_type}")

    if not chunks:
        print(f"  ⚠️  No valid chunks built for {module_code}")
        return False

    # Generate embeddings
    print(f"    Generating {len(chunks)} embedding(s)...")
    embeddings = []
    for chunk in chunks:
        emb = generate_embedding(chunk)
        embeddings.append(emb)
        time.sleep(5.0)

    successful = sum(1 for e in embeddings if e is not None)
    print(f"    Generated {successful}/{len(embeddings)} embeddings")

    # Get or create document
    doc_id = get_or_create_document(conn, module_code, module_id)

    # Store new chunks
    cursor = conn.cursor()
    # Get current max chunk_index for this document
    cursor.execute(
        "SELECT COALESCE(MAX(chunk_index), -1) FROM document_chunks WHERE document_id = %s;",
        (doc_id,)
    )
    start_idx = cursor.fetchone()[0] + 1

    data = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        if embedding is not None:
            data.append((doc_id, chunk, start_idx + idx, embedding, json.dumps({})))

    if data:
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
            UPDATE documents SET
                total_chunks = (SELECT COUNT(*) FROM document_chunks WHERE document_id = %s),
                updated_at = NOW()
            WHERE id = %s;
        """, (doc_id, doc_id))
        conn.commit()
        print(f"    ✅ Stored {len(data)} new chunk(s) in document id={doc_id}")

    cursor.close()
    return True


def main():
    print("\n" + "="*70)
    print("PROODOS RE-INGEST — 'other' Subject Boxes (April 2026)")
    print("Modules: M1–M15 | Subject: Primary School Generalist (Dimitris)")
    print("="*70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    conn = psycopg2.connect(**DB_CONFIG)
    results = {}

    try:
        for module_code, record_ids in OTHER_BOX_IDS.items():
            success = process_module_other_boxes(conn, module_code, record_ids)
            results[module_code] = '✅' if success else '❌'

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM document_chunks;")
        total_chunks = cursor.fetchone()[0]
        cursor.close()

        print("\n" + "="*70)
        print("RE-INGEST SUMMARY")
        print("="*70)
        for code, status in results.items():
            print(f"  {status} {code}")
        print(f"\nTotal chunks in database (all modules): {total_chunks}")
        print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Cost estimate: ~29 records × ~500 tokens
        cost = (29 * 500 / 1_000_000) * 0.02
        print(f"Estimated embedding cost: EUR {cost:.4f}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
