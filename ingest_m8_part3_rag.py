"""
M8 RAG Incremental Ingest Script
=================================
Module: Harnessing the EduPrompt Studio (Scaffolding & Design)
UNESCO Aspect: Pedagogy | Level: Deepen

Ingests ONLY the new subject_box_part3 records for M8:
  - 16 discipline-specific pedagogical scaffolding scenarios
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

# API Configuration (Matches your M7 logic)
NEW_GENAI_API = False
try:
    from google import genai as genai_client
    NEW_GENAI_API = True
    client = genai_client.Client(api_key=os.getenv('GEMINI_API_KEY'))
except ImportError:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

def clean_text(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
    return text.strip()

def generate_embedding(text, retry_count=3):
    # Logic preserved from your M7 script
    for attempt in range(retry_count):
        try:
            if NEW_GENAI_API:
                result = client.models.embed_content(
                    model="models/gemini-embedding-001",
                    contents=text,
                    config={"output_dimensionality": 768}
                )
                return result.embeddings[0].values if hasattr(result, 'embeddings') else result
            else:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                return result['embedding']
        except Exception as e:
            if attempt < retry_count - 1:
                time.sleep((attempt + 1) * 2)
            else:
                return None

def process_m8_part3_examples(conn):
    print(f"\nProcessing: M8 subject_box_part3 — Pedagogical Scaffolding Scenarios")
    
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM modules_module WHERE code = 'M8';")
    row = cursor.fetchone()
    if not row:
        print("ERROR: M8 module record not found!")
        return False
    module_id = row[0]

    # Fetch the 16 discipline-specific records we just updated
    cursor.execute("""
        SELECT subject_area, content_data
        FROM modules_modulecontent
        WHERE module_id = %s
        AND content_type = 'subject_box_part3'
        ORDER BY subject_area;
    """, (module_id,))
    rows = cursor.fetchall()
    
    if not rows:
        print("ERROR: No subject_box_part3 records found for M8!")
        return False

    chunks = []
    for subject_area, content_data in rows:
        # Structured text for the RAG to understand the pedagogical context
        text = (
            f"Module: M8 — Harnessing the EduPrompt Studio\n"
            f"Subject: {subject_area}\n"
            f"Type: Pedagogical Scaffolding & Studio Strategy (Part 3)\n"
            f"Content: {clean_text(content_data)}"
        )
        chunks.append(text)
        print(f"  ✓ Prepared chunk for: {subject_area}")

    # Batch embedding generation
    embeddings = []
    for chunk in chunks:
        embedding = generate_embedding(chunk)
        embeddings.append(embedding)
        time.sleep(1.0) # Rate limiting safety

    # Store in RAG schema
    cursor.execute("""
        INSERT INTO documents (title, document_type, module_id, file_path, metadata, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), NOW())
        RETURNING id;
    """, (
        'M8: EduPrompt Studio - Pedagogical Scaffolding by Subject (Apr 2026)',
        'module_content',
        module_id,
        'database',
        json.dumps({'source': 'modules_modulecontent', 'module': 'M8', 'type': 'subject_box_part3'})
    ))
    doc_id = cursor.fetchone()[0]

    # Store Chunks
    data = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        if embedding is not None:
            data.append((doc_id, chunk, idx, embedding, json.dumps({})))
    
    execute_values(
        cursor,
        "INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding, metadata, created_at) VALUES %s",
        data,
        template="(%s, %s, %s, %s, %s::jsonb, NOW())"
    )
    
    conn.commit()
    cursor.close()
    print(f"\nCOMPLETE: M8 subject_box_part3 ingested as document id={doc_id}")
    return True

if __name__ == "__main__":
    connection = psycopg2.connect(**DB_CONFIG)
    try:
        process_m8_part3_examples(connection)
    finally:
        connection.close()