"""
Embed Seed Reflections for Cross-Specialty Peer Synthesizer
============================================================
Reads peer_reflections with NULL embeddings and generates
768-dimensional vectors using Gemini API.

Run from project root:
    python embed_seed_reflections.py
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import time

load_dotenv()

# ── API Setup (same logic as rag_query_system.py) ──────────────────────────
NEW_GENAI_API = False
try:
    from google import genai as genai_client
    NEW_GENAI_API = True
    print("✓ Using NEW google.genai API")
    client = genai_client.Client(api_key=os.getenv('GEMINI_API_KEY'))
except ImportError:
    import google.generativeai as genai
    print("✓ Using OLD google.generativeai API")
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# ── DB Config (same as rag_query_system.py) ────────────────────────────────
DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

# ── Embed function (same as rag_query_system.py) ───────────────────────────
def embed_text(text):
    try:
        if NEW_GENAI_API:
            result = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text,
                config={"output_dimensionality": 768}
            )
            return result.embeddings[0].values
        else:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
    except Exception as e:
        print(f"  ❌ Embedding error: {e}")
        return None

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch records with no embedding yet
    cursor.execute("""
        SELECT id, subject_area, grade_level, reflection_text
        FROM peer_reflections
        WHERE reflection_embedding IS NULL
        ORDER BY id;
    """)
    records = cursor.fetchall()

    if not records:
        print("✅ All records already have embeddings.")
        conn.close()
        return

    print(f"\n📋 Found {len(records)} records to embed\n")

    update_cursor = conn.cursor()
    success = 0

    for rec in records:
        print(f"  [{rec['id']}] {rec['subject_area']} / {rec['grade_level']} ... ", end="", flush=True)

        embedding = embed_text(rec['reflection_text'])

        if embedding:
            update_cursor.execute("""
                UPDATE peer_reflections
                SET reflection_embedding = %s::vector
                WHERE id = %s;
            """, (embedding, rec['id']))
            conn.commit()
            print("✅")
            success += 1
        else:
            print("❌ skipped")

        time.sleep(0.5)  # Avoid rate limiting

    update_cursor.close()
    cursor.close()
    conn.close()

    print(f"\n{'='*50}")
    print(f"✅ Done: {success}/{len(records)} embeddings stored")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
