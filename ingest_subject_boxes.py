"""
Ingest Subject Boxes - Phase 2C Enhancement
============================================
Embeds 32 subject-specific boxes into RAG system.
"""

import os
import psycopg2
from psycopg2.extras import execute_values
import json
from dotenv import load_dotenv
import re
import time

# Load environment first
load_dotenv()

# Try to import and configure APIs
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

DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clean_text(text):
    """Clean HTML and normalize text."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def generate_embedding(text):
    """Generate embedding using Gemini API."""
    try:
        if NEW_GENAI_API:
            # NEW API
            result = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text,
                config={"output_dimensionality": 768}
            )
            if hasattr(result, 'embeddings') and len(result.embeddings) > 0:
                return result.embeddings[0].values
            else:
                return result if isinstance(result, list) else result.get('embedding', result)
        else:
            # OLD API
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
    except Exception as e:
        print(f"    ❌ Embedding error: {e}")
        return None

# ============================================================================
# MAIN INGESTION
# ============================================================================

def ingest_subject_boxes():
    """Ingest all subject boxes from database."""
    
    print("\n" + "="*70)
    print("📦 INGESTING SUBJECT BOXES")
    print("="*70)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("\n1️⃣ Retrieving subject boxes from database...")
        
        cursor.execute("""
            SELECT 
                id,
                content_type,
                subject_area,
                content_data,
                metadata
            FROM modules_modulecontent
            WHERE module_id = 1 
            AND content_type IN ('subject_box_part2', 'subject_box_part4')
            ORDER BY subject_area, content_type;
        """)
        
        boxes = cursor.fetchall()
        print(f"   ✅ Found {len(boxes)} subject boxes")
        
        # Step 2: Create document entry for subject boxes collection
        print("\n2️⃣ Creating document entry...")
        
        cursor.execute("""
            INSERT INTO documents (
                title, document_type, module_id, file_path, 
                metadata, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), NOW())
            RETURNING id;
        """, (
            "M1: Subject-Specific Examples",
            "module_content",
            2,  # M1 (FIXED)
            "database",
            json.dumps({'source': 'subject_boxes', 'count': len(boxes)})
        ))
        
        doc_id = cursor.fetchone()[0]
        conn.commit()
        print(f"   ✅ Document ID: {doc_id}")
        
        # Step 3: Process each box
        print("\n3️⃣ Processing and embedding boxes...")
        
        chunks_data = []
        successful = 0
        
        for idx, (box_id, content_type, subject, content_data, metadata) in enumerate(boxes):
            part = 'Part 2' if 'part2' in content_type else 'Part 4'
            
            # Clean content
            cleaned = clean_text(content_data)
            
            if len(cleaned) < 100:  # Skip if too short
                print(f"   ⚠️  Skipping {subject} {part} (too short)")
                continue
            
            # Generate embedding
            print(f"   → [{idx+1}/{len(boxes)}] {subject} - {part} ({len(cleaned)} chars)")
            embedding = generate_embedding(cleaned)
            
            if embedding:
                chunks_data.append((
                    doc_id,
                    cleaned,
                    idx,
                    embedding,
                    json.dumps({
                        'subject': subject,
                        'part': part,
                        'type': 'subject_example',
                        'box_id': box_id
                    })
                ))
                successful += 1
            
            time.sleep(5.0)  # Rate limiting
        
        print(f"\n   ✅ Successfully embedded: {successful}/{len(boxes)}")
        
        # Step 4: Bulk insert chunks
        print("\n4️⃣ Storing chunks in database...")
        
        execute_values(
            cursor,
            """
            INSERT INTO document_chunks (
                document_id, chunk_text, chunk_index, 
                embedding, metadata, created_at
            )
            VALUES %s
            """,
            chunks_data,
            template="(%s, %s, %s, %s, %s::jsonb, NOW())"
        )
        
        # Update document total_chunks
        cursor.execute("""
            UPDATE documents 
            SET total_chunks = %s, updated_at = NOW()
            WHERE id = %s;
        """, (len(chunks_data), doc_id))
        
        conn.commit()
        print(f"   ✅ Stored {len(chunks_data)} chunks")
        
        # Step 5: Verify
        print("\n5️⃣ Verification...")
        
        cursor.execute("SELECT COUNT(*) FROM document_chunks;")
        total_chunks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents;")
        total_docs = cursor.fetchone()[0]
        
        print(f"   ✅ Total documents: {total_docs}")
        print(f"   ✅ Total chunks: {total_chunks}")
        
        print("\n" + "="*70)
        print("🎉 SUBJECT BOXES INGESTION COMPLETE!")
        print("="*70)
        print(f"\nAdded: {successful} subject-specific chunks")
        print(f"New total: {total_chunks} chunks")
        print(f"Cost: ~€{successful * 0.00001:.6f}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    ingest_subject_boxes()
