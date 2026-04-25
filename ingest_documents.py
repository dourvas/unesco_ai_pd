"""
Document Ingestion Script - Phase 2B (Updated)
================================================
Ingests PDFs and M1 content into RAG system.

Documents:
1. UNESCO AI Competency Framework (PDF)
2. RPE Framework (PDF)
3. M1 Main Content (Database)

Updates:
- Fixed JSON/dict adaptation for PostgreSQL
- Support for both old and new Gemini API
"""

import os
import psycopg2
from psycopg2.extras import execute_values
import json
from dotenv import load_dotenv
import PyPDF2
import re
from datetime import datetime
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

# Configuration
DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

PDF_FOLDER = 'pdf'
CHUNK_SIZE = 800  # tokens (approx 600 words)
CHUNK_OVERLAP = 100  # tokens overlap for context

# ============================================================================
# STEP 1: PDF EXTRACTION
# ============================================================================

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    print(f"  📄 Reading: {os.path.basename(pdf_path)}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            text = ""
            for page_num in range(total_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                text += page_text + "\n\n"
                
                # Progress indicator
                if (page_num + 1) % 10 == 0:
                    print(f"    → Processed {page_num + 1}/{total_pages} pages")
            
            print(f"  ✅ Extracted {len(text):,} characters from {total_pages} pages")
            return text
            
    except Exception as e:
        print(f"  ❌ Error reading PDF: {e}")
        return None

# ============================================================================
# STEP 2: TEXT CLEANING
# ============================================================================

def clean_text(text):
    """Clean and normalize text."""
    # Remove HTML tags (from M1 content)
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep periods, commas
    text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
    
    return text.strip()

# ============================================================================
# STEP 3: TEXT CHUNKING
# ============================================================================

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into chunks with overlap."""
    # Approximate: 1 token ≈ 0.75 words ≈ 4 characters
    chars_per_chunk = chunk_size * 4
    chars_overlap = overlap * 4
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chars_per_chunk
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for period within last 200 chars
            period_pos = text.rfind('.', end - 200, end)
            if period_pos > start:
                end = period_pos + 1
        
        chunk = text[start:end].strip()
        if len(chunk) > 100:  # Only add substantial chunks
            chunks.append(chunk)
        
        start = end - chars_overlap
    
    return chunks

# ============================================================================
# STEP 4: EMBEDDING GENERATION
# ============================================================================

def generate_embedding(text, retry_count=3):
    """Generate embedding using Gemini API with retry logic."""
    for attempt in range(retry_count):
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
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2
                print(f"    ⚠️  Retry {attempt + 1}/{retry_count} in {wait_time}s... ({str(e)[:50]})")
                time.sleep(wait_time)
            else:
                print(f"    ❌ Failed after {retry_count} attempts: {e}")
                return None

def generate_embeddings_batch(chunks, batch_size=10):
    """Generate embeddings for chunks in batches."""
    embeddings = []
    total = len(chunks)
    
    print(f"  🔮 Generating embeddings for {total} chunks...")
    
    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        batch_end = min(i + batch_size, total)
        
        print(f"    → Processing chunks {i+1}-{batch_end}/{total}")
        
        for chunk in batch:
            embedding = generate_embedding(chunk)
            embeddings.append(embedding)
            time.sleep(5.0)  # Rate limiting
        
        # Progress update
        progress = (batch_end / total) * 100
        print(f"    ✅ Progress: {progress:.1f}%")
    
    # Count successful embeddings
    successful = sum(1 for e in embeddings if e is not None)
    print(f"  ✅ Generated {successful}/{len(embeddings)} embeddings")
    
    return embeddings

# ============================================================================
# STEP 5: DATABASE STORAGE
# ============================================================================

def store_document(conn, title, doc_type, module_id, file_path, metadata):
    """Store document metadata."""
    cursor = conn.cursor()
    
    # Convert metadata dict to JSON string
    metadata_json = json.dumps(metadata)
    
    cursor.execute("""
        INSERT INTO documents (title, document_type, module_id, file_path, metadata, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), NOW())
        RETURNING id;
    """, (title, doc_type, module_id, file_path, metadata_json))
    
    doc_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    
    return doc_id

def store_chunks(conn, doc_id, chunks, embeddings):
    """Store chunks with embeddings in bulk."""
    cursor = conn.cursor()
    
    print(f"  💾 Storing chunks in database...")
    
    # Prepare data - only include chunks with successful embeddings
    data = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        if embedding is not None:  # Only store if embedding generated successfully
            # Convert embedding list to PostgreSQL array format
            data.append((
                doc_id,
                chunk,
                idx,
                embedding,
                json.dumps({})  # Empty metadata as JSON
            ))
    
    if not data:
        print(f"  ❌ No valid embeddings to store!")
        cursor.close()
        return
    
    print(f"  💾 Storing {len(data)} chunks (skipped {len(chunks) - len(data)} failed embeddings)...")
    
    # Bulk insert
    execute_values(
        cursor,
        """
        INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding, metadata, created_at)
        VALUES %s
        """,
        data,
        template="(%s, %s, %s, %s, %s::jsonb, NOW())"
    )
    
    # Update document total_chunks
    cursor.execute("""
        UPDATE documents 
        SET total_chunks = %s, updated_at = NOW()
        WHERE id = %s;
    """, (len(data), doc_id))
    
    conn.commit()
    cursor.close()
    
    print(f"  ✅ Stored {len(data)} chunks in database")

# ============================================================================
# STEP 6: MAIN PROCESSING FUNCTIONS
# ============================================================================

def process_pdf(conn, pdf_path, doc_type, title):
    """Process a PDF document."""
    print(f"\n{'='*70}")
    print(f"📚 Processing: {title}")
    print(f"{'='*70}")
    
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return False
    
    # Clean text
    print(f"  🧹 Cleaning text...")
    text = clean_text(text)
    print(f"  ✅ Cleaned: {len(text):,} characters")
    
    # Chunk text
    print(f"  ✂️  Chunking text...")
    chunks = chunk_text(text)
    print(f"  ✅ Created {len(chunks)} chunks")
    
    # Generate embeddings
    embeddings = generate_embeddings_batch(chunks)
    
    # Store in database
    doc_id = store_document(
        conn,
        title=title,
        doc_type=doc_type,
        module_id=None,  # Universal
        file_path=pdf_path,
        metadata={'pages': len(text) // 3000, 'source': 'pdf'}
    )
    
    store_chunks(conn, doc_id, chunks, embeddings)
    
    print(f"✅ {title} - COMPLETE!")
    return True

def process_m1_content(conn):
    """Process M1 main content from database."""
    print(f"\n{'='*70}")
    print(f"📚 Processing: M1 Main Content (from database)")
    print(f"{'='*70}")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content_data
        FROM modules_modulecontent
        WHERE module_id = 1 AND content_type = 'main_content';
    """)
    
    row = cursor.fetchone()
    cursor.close()
    
    if not row:
        print("  ❌ No M1 main content found!")
        return False
    
    text = row[0]
    print(f"  ✅ Retrieved {len(text):,} characters")
    
    # Clean text
    print(f"  🧹 Cleaning text...")
    text = clean_text(text)
    print(f"  ✅ Cleaned: {len(text):,} characters")
    
    # Chunk text
    print(f"  ✂️  Chunking text...")
    chunks = chunk_text(text)
    print(f"  ✅ Created {len(chunks)} chunks")
    
    # Generate embeddings
    embeddings = generate_embeddings_batch(chunks)
    
    
    doc_id = store_document(
        conn,
        title="M1: AI Foundations - Main Content",
        doc_type="module_content",
        module_id=1,
        file_path="database",
        metadata={'source': 'modules_modulecontent', 'module': 'M1'}
    )
    
    store_chunks(conn, doc_id, chunks, embeddings)
    
    print(f"✅ M1 Main Content - COMPLETE!")
    return True

def process_module_content(conn, module_code, title):
    """Process any module's main content from database."""
    print(f"\n{'='*70}")
    print(f"📚 Processing: {title} (from database)")
    print(f"{'='*70}")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mc.content_data, m.id
        FROM modules_modulecontent mc
        JOIN modules_module m ON mc.module_id = m.id
        WHERE m.code = %s AND mc.content_type = 'main_content';
    """, (module_code,))
    
    row = cursor.fetchone()
    cursor.close()
    
    if not row:
        print(f"  ❌ No main content found for {module_code}!")
        return False
    
    text, module_id = row
    print(f"  ✅ Retrieved {len(text):,} characters")
    
    text = clean_text(text)
    chunks = chunk_text(text)
    print(f"  ✅ Created {len(chunks)} chunks")
    
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
    
    print(f"✅ {title} - COMPLETE!")
    return True

def process_module_subject_examples(conn, module_code, title):
    """Process subject-specific content for a module."""
    print(f"\n{'='*70}")
    print(f"📚 Processing: {title}")
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
        print(f"  ❌ No subject examples found for {module_code}!")
        return False
    
    module_id = rows[0][3]
    chunks = []
    for subject_area, content_type, content_data, _ in rows:
        text = f"Subject: {subject_area}\nType: {content_type}\n{clean_text(content_data)}"
        if len(text) > 100:
            chunks.append(text)
    
    print(f"  ✅ Created {len(chunks)} subject chunks")
    
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
    
    print(f"✅ {title} - COMPLETE!")
    return True

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main ingestion process."""
    print("\n" + "="*70)
    print("🚀 PHASE 2B: DOCUMENT INGESTION")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    
    success_count = 0
    total_count = 3
    
    try:
        # Process PDF 1: UNESCO Framework
        
        
        # Process PDF 2: RPE Framework
        
        
        # Process M1 Content
       
        # Process M2 Content
        # if process_module_content(conn, 'M2', 'M2: AI Ethics - Main Content'):
        #     success_count += 1

        # Process M7 Content  
        # if process_module_content(conn, 'M7', 'M7: Applied Ethics - Main Content'):
        #     success_count += 1

        # Process M12 Content
        # if process_module_content(conn, 'M12', 'M12: Ethics Policy Design - Main Content'):
        #     success_count += 1

        # Process Subject-Specific Examples for M2/M7/M12
        if process_module_subject_examples(conn, 'M2', 'M2: Subject-Specific Ethics Examples'):
            success_count += 1

        if process_module_subject_examples(conn, 'M7', 'M7: Subject-Specific Ethics Examples'):
            success_count += 1

        if process_module_subject_examples(conn, 'M12', 'M12: Subject-Specific Ethics Examples'):
            success_count += 1
        # Summary
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents;")
        total_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM document_chunks;")
        total_chunks = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT 
                d.title,
                d.document_type,
                COUNT(dc.id) as chunk_count
            FROM documents d
            LEFT JOIN document_chunks dc ON d.id = dc.document_id
            GROUP BY d.id, d.title, d.document_type
            ORDER BY d.id;
        """)
        
        doc_stats = cursor.fetchall()
        cursor.close()
        
        print("\n" + "="*70)
        print("🎉 INGESTION COMPLETE!")
        print("="*70)
        print(f"Successfully processed: {success_count}/{total_count} documents")
        print(f"Total documents in database: {total_docs}")
        print(f"Total chunks in database: {total_chunks}")
        print()
        
        if doc_stats:
            print("📊 Document Statistics:")
            for title, doc_type, chunks in doc_stats:
                print(f"  • {title}")
                print(f"    Type: {doc_type}, Chunks: {chunks}")
        
        print()
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        # Estimate cost
        total_tokens = total_chunks * 600  # Approx 600 words per chunk
        cost_estimate = (total_tokens / 1_000_000) * 0.02  # $0.02 per 1M tokens
        print(f"💰 Estimated cost: €{cost_estimate:.4f}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
