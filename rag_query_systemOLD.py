"""
RAG Query System - Phase 2C (Updated)
======================================
Processes teacher reflections and generates personalized feedback
using retrieval-augmented generation.

Compatible with both OLD (google.generativeai) and NEW (google.genai) APIs
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from dotenv import load_dotenv
import time

# Load environment first
load_dotenv()

# Try to import and configure APIs
NEW_GENAI_API = False
try:
    # Try NEW API first
    from google import genai as genai_client
    NEW_GENAI_API = True
    print("✓ Using NEW google.genai API")
    client = genai_client.Client(api_key=os.getenv('GEMINI_API_KEY'))
except ImportError:
    # Fallback to OLD API
    try:
        import google.generativeai as genai
        print("✓ Using OLD google.generativeai API")
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    except ImportError:
        print("❌ ERROR: Neither google.genai nor google.generativeai is installed!")
        print("   Install one with: pip install google-genai  OR  pip install google-generativeai")
        exit(1)

# Database configuration
DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

# ============================================================================
# STEP 1: EMBED QUERY
# ============================================================================

def embed_query(text):
    """Generate embedding for query text."""
    try:
        if NEW_GENAI_API:
            # NEW API syntax
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                config={"output_dimensionality": 768}  # Reduce from 3072 to 768
            )
            embedding = result if isinstance(result, list) else result.get('embedding', result)
            print(f"      ✅ Embedded to {len(embedding)}-dimensional vector")
            return embedding
            # Extract embedding values
            if hasattr(result, 'embeddings') and len(result.embeddings) > 0:
                return result.embeddings[0].values
            else:
                print(f"❌ Unexpected embedding format: {type(result)}")
                return None
        else:
            # OLD API syntax
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# STEP 2: SIMILARITY SEARCH
# ============================================================================

def search_similar_chunks(conn, query_embedding, top_k=5, module_id=None, subject=None):
    """
    Search for most similar chunks using vector similarity.
    
    Args:
        conn: Database connection
        query_embedding: 768-dimensional vector
        top_k: Number of results to return
        module_id: Filter by module (None for universal + specific)
        subject: Filter by subject area (e.g., 'Mathematics')
    
    Returns:
        List of dicts with chunk info
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Build query with subject filtering
    if module_id and subject:
        # Filter by both module and subject
        sql = """
            SELECT 
                dc.id,
                dc.chunk_text,
                dc.embedding <=> %s::vector AS distance,
                d.title,
                d.document_type,
                d.module_id,
                dc.metadata->>'subject' as subject
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE (d.module_id IS NULL OR d.module_id = %s)
              AND (dc.metadata->>'subject' IS NULL OR LOWER(dc.metadata->>'subject') = LOWER(%s))
            ORDER BY distance
            LIMIT %s;
        """
        cursor.execute(sql, (query_embedding, module_id, subject, top_k))
    elif module_id:
        # Filter only by module (existing logic)
        sql = """
            SELECT 
                dc.id,
                dc.chunk_text,
                dc.embedding <=> %s::vector AS distance,
                d.title,
                d.document_type,
                d.module_id,
                dc.metadata->>'subject' as subject
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.module_id IS NULL OR d.module_id = %s
            ORDER BY distance
            LIMIT %s;
        """
        cursor.execute(sql, (query_embedding, module_id, top_k))
    else:
        # No filtering (universal search)
        sql = """
            SELECT 
                dc.id,
                dc.chunk_text,
                dc.embedding <=> %s::vector AS distance,
                d.title,
                d.document_type,
                dc.metadata->>'subject' as subject
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            ORDER BY distance
            LIMIT %s;
        """
        cursor.execute(sql, (query_embedding, top_k))
    
    results = cursor.fetchall()
    cursor.close()
    
    return results

# ============================================================================
# STEP 3: GENERATE FEEDBACK
# ============================================================================

def generate_feedback(reflection_text, teacher_context, retrieved_chunks):
    """
    Generate personalized feedback using Gemini with retrieved context.
    Now includes name personalization and markdown formatting.
    """
    # Build context from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_parts.append(f"[Source {i}: {chunk['title']}]\n{chunk['chunk_text']}\n")
    
    context = "\n".join(context_parts)
    
    # Get teacher name for personalized greeting
    teacher_name = teacher_context.get('name', 'Colleague')
    
    # Build prompt with name and markdown instructions
    prompt = f"""You are an AI education expert providing personalized feedback to a teacher based on the UNESCO AI Competency Framework.

TEACHER CONTEXT:
- Name: {teacher_name}
- Subject: {teacher_context.get('subject', 'General')}
- Grade Level: {teacher_context.get('grade_level', 'Mixed')}
- Experience: {teacher_context.get('experience', 'Not specified')}

TEACHER'S REFLECTION:
{reflection_text}

RELEVANT FRAMEWORK CONTEXT:
{context}

TASK:
Provide personalized, constructive feedback (250-300 words) that:
1. Opens with a warm, personalized greeting using the teacher's name
2. Acknowledges specific strengths from their reflection
3. References relevant UNESCO competencies from the context above
4. Offers 2-3 concrete, actionable suggestions for growth
5. Uses their subject/grade context naturally throughout
6. Maintains an encouraging, collegial tone

FORMAT YOUR RESPONSE IN MARKDOWN:
- Use **bold** for key terms and UNESCO competencies
- Use *italic* for emphasis
- Use bullet points (- ) for lists
- Use numbered lists (1. 2. 3.) for sequential suggestions
- Use ## for section headers if needed (sparingly)

IMPORTANT:
- Begin with: "Dear {teacher_name}," or "Hello {teacher_name}!" (choose based on tone)
- Write as a supportive colleague, not as an evaluator
- Be specific and actionable, not generic
- Ground suggestions in the UNESCO framework context provided
"""

    try:
        if NEW_GENAI_API:
            # NEW API syntax
            print(f"   → Using Gemini 2.5 Flash (NEW API)")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            print(f"   ✅ Generated with Gemini 2.5 Flash")
            return response.text
        else:
            # OLD API syntax - try 2.5 first, fallback to 1.5
            try:
                print(f"   → Using Gemini 2.5 Flash (OLD API)")
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                print(f"   ✅ Generated with Gemini 2.5 Flash")
                return response.text
            except Exception as e:
                # Fallback to 1.5 Flash
                print(f"   ⚠️  Gemini 2.5 not available, trying 1.5 Flash...")
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                print(f"   ✅ Generated with Gemini 1.5 Flash (fallback)")
                return response.text
    except Exception as e:
        print(f"   ❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# STEP 4: STORE QUERY
# ============================================================================

def store_rag_query(conn, user_id, module_id, reflection_text, teacher_context, 
                    query_embedding, retrieved_chunks, generated_response, 
                    generation_tokens, processing_time_ms, api_cost_eur):
    """Store RAG query in database for research analysis."""
    cursor = conn.cursor()
    
    # Prepare retrieved chunks for storage
    chunks_data = [
        {
            'chunk_id': chunk['id'],
            'distance': float(chunk['distance']),
            'title': chunk['title'],
            'text_preview': chunk['chunk_text'][:200]
        }
        for chunk in retrieved_chunks
    ]
    
    cursor.execute("""
        INSERT INTO rag_queries (
            user_id, module_id, reflection_text, teacher_context,
            query_embedding, retrieved_chunks, num_chunks_retrieved,
            generated_response, generation_tokens,
            processing_time_ms, api_cost_eur,
            created_at, updated_at
        )
        VALUES (%s, %s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id;
    """, (
        user_id, module_id, reflection_text, json.dumps(teacher_context),
        query_embedding, json.dumps(chunks_data), len(retrieved_chunks),
        generated_response, generation_tokens,
        processing_time_ms, api_cost_eur
    ))
    
    query_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    
    return query_id

# ============================================================================
# MAIN PROCESS
# ============================================================================

def process_reflection(reflection_text, teacher_context, user_id=1, module_id=1):
    """
    Complete RAG process: embed, search, generate, store.
    
    Args:
        reflection_text: Teacher's reflection
        teacher_context: Dict with subject, grade_level, experience
        user_id: User ID (default 1 for testing)
        module_id: Module ID (default 1 for M1)
    
    Returns:
        Dict with feedback and metadata
    """
    start_time = time.time()
    
    print("\n" + "="*70)
    print("🔮 RAG QUERY PROCESSING")
    print("="*70)
    
    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        # Step 1: Embed query
        print("\n1️⃣ Embedding reflection...")
        query_embedding = embed_query(reflection_text)
        if not query_embedding:
            return {"error": "Failed to embed reflection"}
        print(f"   ✅ Embedded to {len(query_embedding)}-dimensional vector")
        
        # Step 2: Search similar chunks
        print("\n2️⃣ Searching for relevant content...")
        # Get subject from context
        subject = teacher_context.get('subject', None)
        if subject:
            subject = subject.lower()

        # Search with subject filtering
        retrieved_chunks = search_similar_chunks(
            conn, query_embedding, 
            top_k=5, 
            module_id=module_id,
            subject=subject
        )
        print(f"   ✅ Found {len(retrieved_chunks)} relevant chunks:")
        for i, chunk in enumerate(retrieved_chunks, 1):
            subject_label = f" [{chunk['subject']}]" if chunk.get('subject') else ""
            print(f"      {i}. {chunk['title']}{subject_label} (distance: {chunk['distance']:.4f})")
        
        # Step 3: Generate feedback
        print("\n3️⃣ Generating personalized feedback...")
        generated_response = generate_feedback(reflection_text, teacher_context, retrieved_chunks)
        if not generated_response:
            return {"error": "Failed to generate feedback"}
        
        # Estimate tokens and cost
        generation_tokens = len(generated_response.split()) * 1.3  # Rough estimate
        api_cost_eur = (generation_tokens / 1_000_000) * 0.30 * 0.93  # Gemini pricing in EUR
        
        print(f"   ✅ Generated {len(generated_response)} characters")
        print(f"   💰 Estimated cost: €{api_cost_eur:.6f}")
        
        # Step 4: Store query
        print("\n4️⃣ Storing query for research...")
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        query_id = store_rag_query(
            conn, user_id, module_id, reflection_text, teacher_context,
            query_embedding, retrieved_chunks, generated_response,
            int(generation_tokens), processing_time_ms, api_cost_eur
        )
        
        print(f"   ✅ Stored as query ID: {query_id}")
        print(f"   ⏱️  Total processing time: {processing_time_ms}ms")
        
        print("\n" + "="*70)
        print("✅ RAG QUERY COMPLETE")
        print("="*70)
        
        return {
            'query_id': query_id,
            'feedback': generated_response,
            'retrieved_chunks': len(retrieved_chunks),
            'processing_time_ms': processing_time_ms,
            'cost_eur': api_cost_eur
        }
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
        
    finally:
        conn.close()

# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_rag_system():
    """Test the RAG system with a sample reflection."""
    
    # Sample reflection
    reflection = """
    I tried using ChatGPT to help me create a quiz for my 8th grade Mathematics class 
    on quadratic equations. I gave it the learning objectives and asked it to generate 
    10 multiple-choice questions. The results were impressive - the questions were 
    well-structured and covered the key concepts. However, I noticed that some questions 
    were too easy while others were quite challenging. I had to manually adjust the 
    difficulty levels to match my students' abilities.
    
    This experience made me realize that while AI can save time, I still need to review 
    and customize the output to ensure it's appropriate for my specific classroom context.
    """
    
    # Teacher context
    context = {
        'subject': 'Mathematics',
        'grade_level': 'Secondary',
        'experience': '5 years'
    }
    
    # Process
    result = process_reflection(reflection, context)
    
    # Display feedback
    if 'feedback' in result:
        print("\n" + "="*70)
        print("📝 GENERATED FEEDBACK:")
        print("="*70)
        print(result['feedback'])
        print("\n" + "="*70)
        print(f"📊 Metadata:")
        print(f"   Query ID: {result['query_id']}")
        print(f"   Chunks retrieved: {result['retrieved_chunks']}")
        print(f"   Processing time: {result['processing_time_ms']}ms")
        print(f"   Cost: €{result['cost_eur']:.6f}")
        print("="*70)

if __name__ == "__main__":
    test_rag_system()