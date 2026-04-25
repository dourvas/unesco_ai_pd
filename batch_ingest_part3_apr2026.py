"""
PROODOS Batch RAG Ingest — April 2026
=====================================
Runs incremental ingest for all modules with pending subject_box_part3 records.

Modules covered: M2, M3, M4, M6, M7, M9, M11, M12, M13
Already ingested: M5, M8

Skips any module that already has a matching document in the RAG corpus.

Run from project root:
    python batch_ingest_part3_apr2026.py

Prerequisites:
    - .env with GEMINI_API_KEY
    - All subject_box_part3 SQL inserts already executed
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

# ============================================================
# Module definitions — code, title, part3 theme, doc title
# ============================================================

MODULES = [
    {
        'code': 'M2',
        'title': 'Ethics of AI in Education',
        'part3_type': 'Discipline-specific AI bias example (Key Challenges — Part 3)',
        'doc_title': 'M2: Ethics of AI in Education - AI Bias Examples by Subject (Apr 2026)',
        'skip_if_exists': ['M2%Bias', 'M2%part3'],
    },
    {
        'code': 'M3',
        'title': 'AI Tools for Educators: Understand, Evaluate & Curate',
        'part3_type': 'Discipline-specific AI reliability failure scenario (Reliability Framework — Part 3)',
        'doc_title': 'M3: AI Tools for Educators - Reliability Failure Scenarios by Subject (Apr 2026)',
        'skip_if_exists': ['M3%Reliability', 'M3%part3'],
    },
    {
        'code': 'M4',
        'title': 'AI Tools for Teaching',
        'part3_type': 'Discipline-specific teacher judgment vs AI scenario (Selecting AI Tools — Part 2)',
        'doc_title': 'M4: AI Tools for Teaching - Teacher Judgment Scenarios by Subject (Apr 2026)',
        'skip_if_exists': ['M4%Judgment', 'M4%part3'],
    },
    {
        'code': 'M6',
        'title': 'Human Accountability in AI',
        'part3_type': 'Discipline-specific accountability moment scenario (Human Accountability — Part 3)',
        'doc_title': 'M6: Human Accountability in AI - Accountability Moment Scenarios by Subject (Apr 2026)',
        'skip_if_exists': ['M6%Accountability', 'M6%part3'],
    },
    {
        'code': 'M7',
        'title': 'Navigating Ethical Dilemmas in AI Use',
        'part3_type': 'Discipline-specific academic integrity dilemma (Academic Integrity — Part 2)',
        'doc_title': 'M7: Navigating Ethical Dilemmas - Academic Integrity Dilemmas by Subject (Apr 2026)',
        'skip_if_exists': ['M7%Integrity', 'M7%part3'],
    },
    {
        'code': 'M9',
        'title': 'AI-Enhanced Lesson Design',
        'part3_type': 'Discipline-specific AI-enhanced lesson design scenario (Differentiation at Scale — Part 3)',
        'doc_title': 'M9: AI-Enhanced Lesson Design - Differentiation Scenarios by Subject (Apr 2026)',
        'skip_if_exists': ['M9%Lesson Design', 'M9%part3'],
    },
    {
        'code': 'M11',
        'title': 'Your Voice in the AI School',
        'part3_type': 'Discipline-specific AI leadership moment scenario (Propose Change — Part 4)',
        'doc_title': 'M11: Your Voice in the AI School - Leadership Moment Scenarios by Subject (Apr 2026)',
        'skip_if_exists': ['M11%Leadership', 'M11%part3'],
    },
    {
        'code': 'M12',
        'title': 'Ethics Create: Designing Ethical AI Systems',
        'part3_type': 'Discipline-specific AI policy design moment (Policy Development — Part 3)',
        'doc_title': 'M12: Ethics Create - AI Policy Design Moment Scenarios by Subject (Apr 2026)',
        'skip_if_exists': ['M12%Policy', 'M12%part3'],
    },
    {
        'code': 'M13',
        'title': 'Multimodal AI Content Creation',
        'part3_type': 'Discipline-specific multimodal AI creation moment (Video & Audio Creation — Part 3)',
        'doc_title': 'M13: Multimodal AI Content Creation - Creation Moment Scenarios by Subject (Apr 2026)',
        'skip_if_exists': ['M13%Creation', 'M13%part3'],
    },
]


# ============================================================
# HELPERS
# ============================================================

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
                print(f"      Retry {attempt + 1}/{retry_count} in {wait_time}s... ({str(e)[:50]})")
                time.sleep(wait_time)
            else:
                print(f"      Failed after {retry_count} attempts: {e}")
                return None


def generate_embeddings_batch(chunks, batch_size=10):
    embeddings = []
    total = len(chunks)
    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        batch_end = min(i + batch_size, total)
        print(f"    Chunks {i+1}-{batch_end}/{total}...")
        for chunk in batch:
            embedding = generate_embedding(chunk)
            embeddings.append(embedding)
            time.sleep(5.0)
    successful = sum(1 for e in embeddings if e is not None)
    print(f"    Generated {successful}/{len(embeddings)} embeddings")
    return embeddings


def store_document(conn, title, module_id, metadata):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (title, document_type, module_id, file_path, metadata, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), NOW())
        RETURNING id;
    """, (title, 'module_content', module_id, 'database', json.dumps(metadata)))
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
        cursor.close()
        return 0
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
    return len(data)


def already_ingested(conn, doc_title, patterns):
    """Check if a document with this exact title or matching LIKE patterns already exists."""
    cursor = conn.cursor()
    # Exact title match first
    cursor.execute("SELECT COUNT(*) FROM documents WHERE title = %s;", (doc_title,))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        return True
    # LIKE pattern fallback
    for pattern in patterns:
        cursor.execute("SELECT COUNT(*) FROM documents WHERE title LIKE %s;", (pattern,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            return True
    cursor.close()
    return False


def process_module(conn, module_def):
    code = module_def['code']
    title = module_def['title']
    part3_type = module_def['part3_type']
    doc_title = module_def['doc_title']
    skip_patterns = module_def['skip_if_exists']

    print(f"\n  {'='*60}")
    print(f"  {code}: {title}")
    print(f"  {'='*60}")

    # Pre-flight: already ingested?
    if already_ingested(conn, doc_title, skip_patterns):
        print(f"  ⏭  Already ingested — skipping {code}")
        return True

    # Get module_id
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM modules_module WHERE code = %s;", (code,))
    row = cursor.fetchone()
    if not row:
        print(f"  ❌ Module record not found for {code}")
        cursor.close()
        return False
    module_id = row[0]

    # Get part3 records
    cursor.execute("""
        SELECT subject_area, content_data
        FROM modules_modulecontent
        WHERE module_id = %s AND content_type = 'subject_box_part3'
        ORDER BY subject_area;
    """, (module_id,))
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        print(f"  ❌ No subject_box_part3 records found for {code}")
        return False

    count = len(rows)
    print(f"  Found {count} subject_box_part3 records")
    if count < 16:
        print(f"  ⚠️  Expected 16, found {count}")

    # Build chunks
    chunks = []
    for subject_area, content_data in rows:
        text = (
            f"Module: {code} — {title}\n"
            f"Subject: {subject_area}\n"
            f"Type: {part3_type}\n"
            f"{clean_text(content_data)}"
        )
        if len(text) > 100:
            chunks.append(text)

    print(f"  Generating embeddings for {len(chunks)} chunks...")
    embeddings = generate_embeddings_batch(chunks)

    doc_id = store_document(conn, doc_title, module_id, {
        'source': 'modules_modulecontent',
        'module': code,
        'type': 'subject_box_part3',
        'added': 'April 2026',
    })

    stored = store_chunks(conn, doc_id, chunks, embeddings)
    print(f"  ✅ {code} complete — document id={doc_id}, {stored} chunks stored")
    return True


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "="*70)
    print("PROODOS BATCH RAG INGEST — subject_box_part3 (April 2026)")
    print("Modules: M2 M3 M4 M6 M7 M9 M11 M12 M13")
    print("="*70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    conn = psycopg2.connect(**DB_CONFIG)

    results = {}

    try:
        for module_def in MODULES:
            success = process_module(conn, module_def)
            results[module_def['code']] = '✅' if success else '❌'

        # Summary
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM document_chunks;")
        total_chunks = cursor.fetchone()[0]
        cursor.close()

        print("\n" + "="*70)
        print("BATCH INGEST SUMMARY")
        print("="*70)
        for code, status in results.items():
            print(f"  {status} {code}")
        print(f"\nTotal chunks in database (all modules): {total_chunks}")
        print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Cost estimate — 16 chunks × 9 modules × ~600 tokens
        new_chunks = 16 * len(MODULES) * 600
        cost = (new_chunks / 1_000_000) * 0.02
        print(f"Estimated total embedding cost: EUR {cost:.4f}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
