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
    """
    Generate 768-dimensional embedding for query text.
    Uses dimension reduction to maintain compatibility with existing database schema.
    """
    try:
        if NEW_GENAI_API:
            # NEW API - use client object
            result = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text,
                config={"output_dimensionality": 768}  # Reduce from 3072 to 768
            )
            # Extract embedding from result
            if hasattr(result, 'embeddings') and len(result.embeddings) > 0:
                embedding = result.embeddings[0].values
                print(f"✅ Embedded to {len(embedding)}-dimensional vector")
                return embedding
            else:
                # Fallback: try dict access
                embedding = result if isinstance(result, list) else result.get('embedding', result)
                print(f"✅ Embedded to {len(embedding)}-dimensional vector")
                return embedding
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
    prompt = f"""You are a fellow educator and AI literacy mentor offering collegial reflective dialogue — not evaluation or coaching.

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
Write a warm, conversational response (250-300 words) as if you are a trusted colleague who has just read their reflection over coffee. Your response should:
1. Open with a personal greeting using their name
2. Reflect back what you genuinely found interesting or thought-provoking in what they wrote
3. Make a natural connection to 1-2 ideas from the UNESCO framework — not as requirements, but as "this reminded me of..."
4. Share 1-2 questions or possibilities worth exploring, framed as curiosity ("I wonder what would happen if...", "Have you considered...") rather than directives
5. Close with an encouraging observation about their thinking

CRITICAL TONE GUIDELINES:
- Never use: "you should", "you must", "you need to", "it's important that you"
- Instead use: "I noticed", "what strikes me", "I wonder", "one possibility might be"
- You are NOT grading or evaluating — you are thinking alongside them
- Avoid generic praise ("Great reflection!") — be specific about what you actually noticed

FORMAT YOUR RESPONSE IN MARKDOWN:
- Use **bold** for key terms and UNESCO competencies
- Use *italic* for emphasis
- Use bullet points sparingly — prefer flowing prose
- Use ## for section headers only if truly needed

Begin with: "Dear {teacher_name}," or "Hello {teacher_name}!" (choose based on tone)
End with: "Best,\nThe PROODOS Team"
"""

    try:
        if NEW_GENAI_API:
            from google.genai import types as genai_types
            print(f"   → Using Gemini 2.5 Flash (NEW API)")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    max_output_tokens=2500
                )
            )
            print(f"   ✅ Generated with Gemini 2.5 Flash")
            
            if not response or not response.candidates:
                print(f"   ❌ Empty response from Gemini")
                return None
            
            result_text = response.text
            if not result_text or not result_text.strip():
                print(f"   ❌ Empty text in response")
                return None
            
            return result_text
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
# CROSS-SPECIALTY PEER SYNTHESIZER FUNCTIONS
# ============================================================================

def search_peer_reflections(conn, query_embedding, user_subject, top_k=3, module_id=None):
    """
    Search for similar peer reflections from DIFFERENT subject areas.
    
    Args:
        conn: Database connection
        query_embedding: 768-dimensional vector of current user's reflection
        user_subject: Current user's subject (e.g., 'Mathematics')
        top_k: Number of peer reflections to return
        module_id: Filter by module (None = all modules)
    
    Returns:
        List of dicts with peer reflection info
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Search EXCLUDING user's own subject (cross-specialty)
    if module_id:
        sql = """
            SELECT 
                id,
                subject_area,
                grade_level,
                experience_years,
                reflection_text,
                reflection_embedding <=> %s::vector AS distance,
                is_seed_data
            FROM peer_reflections
            WHERE LOWER(subject_area) != LOWER(%s)
              AND module_id = %s
            ORDER BY distance
            LIMIT %s;
        """
        cursor.execute(sql, (query_embedding, user_subject, module_id, top_k))
    else:
        sql = """
            SELECT 
                id,
                subject_area,
                grade_level,
                experience_years,
                reflection_text,
                reflection_embedding <=> %s::vector AS distance,
                is_seed_data
            FROM peer_reflections
            WHERE LOWER(subject_area) != LOWER(%s)
            ORDER BY distance
            LIMIT %s;
        """
        cursor.execute(sql, (query_embedding, user_subject, top_k))
    
    results = cursor.fetchall()
    cursor.close()
    
    return results


def synthesize_peer_insight(user_reflection, user_context, peer_reflections):
    """
    Generate cross-specialty insight by synthesizing peer reflections.
    
    Args:
        user_reflection: Current user's reflection text
        user_context: Dict with user's subject, grade_level, etc.
        peer_reflections: List of similar reflections from other subjects
    
    Returns:
        String with synthesized peer insight (200-250 words)
    """
    if not peer_reflections:
        return None
    
    # Build peer context
    peer_examples = []
    for i, peer in enumerate(peer_reflections, 1):
        peer_examples.append(
            f"**Colleague {i} ({peer['subject_area']} teacher, {peer['grade_level']}):**\n"
            f"{peer['reflection_text'][:400]}...\n"  # Truncate for prompt size
        )
    
    peer_context = "\n".join(peer_examples)
    
    # Get user name for personalization
    user_name = user_context.get('name', 'Colleague')
    user_subject = user_context.get('subject', 'your subject')
    
    # Build synthesis prompt
    prompt = f"""You are facilitating cross-disciplinary professional learning among teachers.

CONTEXT: {user_name} is a {user_subject} teacher who just reflected on their AI learning experience. You have identified similar reflections from colleagues in OTHER subject areas who had parallel insights.

USER'S REFLECTION:
{user_reflection}

SIMILAR REFLECTIONS FROM COLLEAGUES IN OTHER SUBJECTS:
{peer_context}

TASK:
Write a brief, engaging synthesis (200-250 words) that:

1. **Opens warmly:** "I noticed something interesting about your reflection..."
2. **Names the pattern:** Identify the pedagogical theme connecting these reflections (e.g., "concern about student dependency," "excitement about differentiation," "worry about assessment integrity")
3. **Draws cross-specialty connection:** Show how a colleague in a DIFFERENT subject wrestled with the same issue
4. **Highlights transferable insight:** Extract one concrete strategy or perspective from the peer reflection that could apply to {user_subject}
5. **Closes with invitation:** Encourage continued cross-disciplinary thinking

STYLE:
- Collegial, not evaluative
- Specific, not generic
- Cross-disciplinary learning framed as valuable professional growth
- Use **bold** for key pedagogical terms
- Keep it concise and actionable

IMPORTANT:
- Do NOT reveal which specific colleague you're quoting (anonymity)
- Frame as "a colleague teaching [Subject]" not "Teacher X"
- Focus on the IDEA, not the person
"""

    try:
        if NEW_GENAI_API:
            print(f"   → Generating peer synthesis with Gemini 2.5 Flash")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            print(f"   ✅ Peer synthesis generated")
            return response.text
        else:
            try:
                print(f"   → Generating peer synthesis with Gemini 2.5 Flash")
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                print(f"   ✅ Peer synthesis generated")
                return response.text
            except Exception:
                print(f"   ⚠️  Gemini 2.5 not available, trying 1.5 Flash...")
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                print(f"   ✅ Peer synthesis generated (fallback)")
                return response.text
    except Exception as e:
        print(f"   ❌ Peer synthesis error: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# STEP 4: STORE QUERY
# ============================================================================

def store_rag_query(conn, user_id, module_id, reflection_text, teacher_context,
                    query_embedding, retrieved_chunks, generated_response,
                    generation_tokens, processing_time_ms, api_cost_eur):
    """Store RAG query in database for research analysis.

    Phase C C.3 commit 2a — CP-9 invariant: the rag_queries INSERT and
    the matching AIArtefactProvenance write must happen in one atomic
    block, so a provenance write failure rolls back the rag_queries row
    (no AI output without provenance). The raw psycopg2 `conn` parameter
    is kept for backward compatibility with the function signature but
    is NOT used for the rag_queries INSERT — Django's connection is
    used instead so the INSERT can join Django's transaction.atomic
    block with the provenance write.
    """
    from django.db import connection as django_conn, transaction
    from django.utils import timezone
    from django.contrib.auth.models import User
    from apps.modules.models import Module
    from apps.compliance.services import record_ai_provenance

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

    with transaction.atomic():
        with django_conn.cursor() as cur:
            cur.execute("""
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
            query_id = cur.fetchone()[0]

        # CP-9: same atomic block as the INSERT. CP-3: id obtained
        # exclusively via RETURNING above — never SELECT lastval().
        user = User.objects.get(pk=user_id)
        module = Module.objects.filter(pk=module_id).first() if module_id else None
        record_ai_provenance(
            artefact_kind='rag_query',
            artefact_pk=query_id,
            user=user,
            module=module,
            model_name='gemini-2.5-flash',
            generated_at=timezone.now(),
        )

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
        
        # print(f"   ✅ Generated {len(generated_response)} characters")
        # print(f"   💰 Estimated cost: €{api_cost_eur:.6f}")
        
        # Step 3.5: Peer Synthesis moved to async endpoint
        peer_synthesis = None

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
            'peer_synthesis': peer_synthesis,  # NEW
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
# RTM: REFLECTIVE TENSION MAPPER
# ============================================================================

def validate_tensions(tensions_json, reflection_text):
    """
    Validate AI-extracted tensions before displaying to user.
    
    Rules:
    1. grounding_quote must be >= 20 chars
    2. grounding_quote must exist verbatim in reflection text
    3. tension label must be <= 6 words
    4. left_pole and right_pole must each be >= 10 chars
    5. Must have exactly 2 valid tensions to proceed
    
    Returns:
        List of 2 valid tension dicts, or None (to hide RTM card)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not tensions_json.get('tensions'):
        logger.info("RTM validate: empty tensions array returned by AI")
        return None
    
    valid_tensions = []
    
    for tension in tensions_json['tensions']:
        label = tension.get('label', '')
        quote = tension.get('grounding_quote', '')
        left  = tension.get('left_pole', '')
        right = tension.get('right_pole', '')
        
        # Rule 1: Quote must be substantial
        if len(quote) < 20:
            print(f"      ⚠️ RTM rejected '{label}': quote too short ({len(quote)} chars)")
            continue
        
        # Rule 2: Quote must exist in reflection (normalized comparison)
        # Rule 2: Quote must exist in reflection (normalized comparison)
        # Rule 2: Soft quote validation - check 3 consecutive words exist
        def normalize(text):
            text = text.lower()
            text = text.replace('\u2019', "'").replace('\u2018', "'")
            text = text.replace('\u201c', '"').replace('\u201d', '"')
            text = text.replace('\u2014', '-').replace('\u2013', '-')
            text = text.replace("\\'", "'")
            text = text.replace('\\n', ' ')
            text = ' '.join(text.split())
            return text
        
        quote_words = normalize(quote).split()
        reflection_normalized = normalize(reflection_text)
        if len(quote_words) >= 3:
            significant_words = [w for w in quote_words if len(w) >= 4]
            found = sum(
                1 for w in significant_words
                if w in reflection_normalized
            ) >= 3  # τουλάχιστον 3 significant words να υπάρχουν
            if not found:
                print(f"      ⚠️ RTM rejected '{label}': quote not grounded in reflection")
                continue
        
        # Rule 3: Label must be concise
        if len(label.split()) > 6:
            print(f"      ⚠️ RTM rejected '{label}': label too long ({len(label.split())} words)")
            continue
        
        # Rule 4: Poles must be substantial
        if len(left) < 10 or len(right) < 10:
            print(f"      ⚠️ RTM rejected '{label}': poles too brief")
            continue
        
        valid_tensions.append(tension)
    
    # Must have exactly 2 valid tensions - CHANGE HERE TO AT LEAST 1
    # Need at least 2 valid tensions — take first 2
    # Need at least 1 valid tension NEW
    if len(valid_tensions) >= 1:
        print(f"      ✅ RTM validated {len(valid_tensions)} tension(s)")
        return valid_tensions[:2]
    else:
        print(f"      ⚠️ RTM invalid count: 0 tensions")
        return None

def clean_json_response(text):
    """Clean Gemini JSON response to handle quotes and special chars."""
    import re
    
    # Remove markdown fences
    text = text.strip()
    if '```json' in text:
        text = text.split('```json')[-1].split('```')[0].strip()
    elif text.startswith('```'):
        text = text[3:].split('```')[0].strip()
    
    # Find JSON object boundaries
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    
    # Replace smart quotes with straight quotes
    text = text.replace('\u201c', '\\"').replace('\u201d', '\\"')
    text = text.replace('\u2018', "\\'").replace('\u2019', "\\'")
    
    # Fix unescaped double quotes inside string values
    # Replace any " inside a JSON value with '
    def fix_inner_quotes(match):
        return match.group(0).replace('"', "'")
    
    # Match string values and fix inner quotes
    text = re.sub(r':\s*"(.*?)"(?=\s*[,}\]])', 
                  lambda m: ': "' + m.group(1).replace('"', "'") + '"',
                  text, flags=re.DOTALL)
    
    return text

def extract_tensions(reflection_text, teacher_context):
    """
    Extract exactly 2 pedagogical tensions from a teacher's reflection.
    
    Uses Gemini at temperature=0.3 (analytic, not creative).
    Validates grounding quotes to prevent hallucination.
    
    Args:
        reflection_text: Teacher's reflection text (350-800 words)
        teacher_context: Dict with subject, grade_level, etc. (for logging)
    
    Returns:
        List of 2 validated tension dicts, or None (RTM card will be hidden)
    
    Each tension dict contains:
        - label:           Short descriptive label (max 6 words)
        - left_pole:       Left pole grounded in teacher's wording
        - right_pole:      Right pole grounded in teacher's wording
        - grounding_quote: Verbatim quote from reflection (audit trail)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Truncate very long reflections (safety measure)
    words = reflection_text.split()
    if len(words) > 800:
        reflection_text = ' '.join(words[:800])
        print("   ⚠️ RTM: reflection truncated to 800 words")
    
    reflection_for_prompt = reflection_text.replace('"', "'")
    
    system_message = """You are an educational research analysis engine.
Your task is to identify exactly two pedagogical tensions explicitly present or strongly implied in the teacher's reflection.

A pedagogical tension is a meaningful opposition between two educational values, approaches, or concerns expressed in the text.

You must:
- Base tensions only on the teacher's words
- Not introduce new concepts not grounded in the text
- Avoid abstract or generic tensions
- Return output strictly in JSON format

If no meaningful tension is identifiable, return {"tensions": []}"""

    user_message = f"""Reflection:
{reflection_for_prompt}
IMPORTANT RULES:
1. Return EXACTLY 2 tensions, no more, no less.
2. Do NOT use quotes or apostrophes inside the JSON string values.
3. Do NOT use escaped characters like \\" or \\' in your response.
4. Keep left_pole and right_pole SHORT (max 8 words each).
5. Keep grounding_quote SHORT (max 15 words).

- Keep ALL field values SHORT: label max 6 words, poles max 8 words each, grounding_quote max 10 words

Return JSON in this exact format:

{{
  "tensions": [
    {{
      "label": "Short label max 6 words",
      "left_pole": "Max 8 words",
      "right_pole": "Max 8 words",
      "grounding_quote": "Max 10 words from reflection"
    }},
    {{
      "label": "...",
      "left_pole": "...",
      "right_pole": "...",
      "grounding_quote": "..."
    }}
  ]
}}

If no meaningful tension is identifiable, return: {{"tensions": []}}"""

    try:
        print("\n   4️⃣.5️⃣ RTM: Extracting pedagogical tensions...")
        
        if NEW_GENAI_API:
            from google.genai import types as genai_types
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_message,
                config=genai_types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=2500
                )
            )
            result_text = response.text
            
        else:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                user_message,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2500
                )
            )
            result_text = response.text
        
        # Clean potential markdown code fences
        result_text = result_text.strip()
        if '```json' in result_text:
            result_text = result_text.split('```json')[-1]
            result_text = result_text.split('```')[0].strip()
        elif result_text.startswith('```'):
            result_text = result_text[3:]
            result_text = result_text.split('```')[0].strip()
        
        result_text = clean_json_response(result_text)
        # Robust extraction — handles trailing text after valid JSON
        brace_start = result_text.find('{')
        brace_end = result_text.rfind('}')
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            result_text = result_text[brace_start:brace_end + 1]
        print(f"   🔍 RTM raw: {repr(result_text)}")
        tensions_json = json.loads(result_text)
        
        # Validate
        valid_tensions = validate_tensions(tensions_json, reflection_text)
        
        if valid_tensions:
            subject = teacher_context.get('subject', 'Unknown')
            print(f"   ✅ RTM: {len(valid_tensions)} tension(s) extracted for {subject} teacher")
            for i, t in enumerate(valid_tensions, 1):
                print(f"      {i}. {t['label']}")
            return valid_tensions
        else:
            print(f"   ⚠️ RTM: No valid tensions — card will be hidden")
            return None
    
    except json.JSONDecodeError as e:
        print(f"   ❌ RTM JSON parse error: {e}")
        logger.error(f"RTM JSON parse error for user context {teacher_context}: {e}")
        return None
    except Exception as e:
        print(f"   ❌ RTM extraction error: {e}")
        logger.error(f"RTM extraction error: {e}")
        return None

# ============================================================================
# DTP: DEVELOPMENTAL TRAJECTORY PREDICTOR
# ============================================================================

def compute_development_signal(embedding1, embedding2):
    """
    Compute cosine similarity between two reflection embeddings.
    Returns similarity score and continuity label.
    """
    import numpy as np
    
    v1 = np.array(embedding1)
    v2 = np.array(embedding2)
    
    similarity = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    
    if similarity >= 0.85:
        label = "High"
        description = "Your reflections show sustained focus on core pedagogical priorities."
    elif similarity >= 0.70:
        label = "Moderate"
        description = "Your pedagogical focus has evolved, showing deeper engagement with instructional design."
    else:
        label = "Significant"
        description = "Your reflection shows substantial evolution in how you conceptualize AI in education."
    
    return {
        'similarity': round(similarity, 4),
        'continuity_label': label,
        'continuity_description': description
    }


def extract_development_themes(previous_reflection, current_reflection):
    """
    Use Gemini to extract thematic shifts between two reflections.
    Returns increased/decreased/stable themes.
    """
    # Sanitize reflections to prevent JSON corruption in prompt
    prev_clean = previous_reflection[:400].replace('"', "'").replace('\n', ' ')
    curr_clean = current_reflection[:400].replace('"', "'").replace('\n', ' ')
    
    prompt = f"""Compare these two teacher reflections. Return ONLY a JSON object.
PREVIOUS:
{prev_clean}
CURRENT:
{curr_clean}

Return this exact JSON structure with no markdown, no explanation:
{{"increased": [], "decreased": [], "stable": []}}

Fill each array with 2-3 phrases of MAX 3 WORDS EACH. Keep it extremely brief.
Example: {{"increased": ["ethical focus"], "decreased": [], "stable": ["physics context"]}}
If no clear shift exists in a category, leave the array empty."""

    try:
        if NEW_GENAI_API:
            from google.genai import types as genai_types
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            result_text = response.text.strip()
        else:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            result_text = response.text.strip()
        
        # Clean markdown fences if present
        if '```json' in result_text:
            result_text = result_text.split('```json')[-1].split('```')[0].strip()
        elif result_text.startswith('```'):
            result_text = result_text[3:].split('```')[0].strip()
        
        result_text = clean_json_response(result_text)
        print(f"   🔍 DTP themes raw: {repr(result_text[:200])}")
        
        # Repair truncated JSON
        try:
            themes = json.loads(result_text)
        except json.JSONDecodeError:
            # Try to salvage partial JSON by closing open structures
            repaired = result_text.rstrip()
            # Close any open string
            if repaired.count('"') % 2 != 0:
                repaired += '"'
            # Close any open arrays/objects
            open_brackets = max(0, repaired.count('[') - repaired.count(']'))
            open_braces = max(0, repaired.count('{') - repaired.count('}'))
            repaired += ']' * open_brackets
            repaired += '}' * open_braces
            try:
                themes = json.loads(repaired)
                print(f"   ⚠️ DTP themes repaired successfully")
            except:
                return {"increased": [], "decreased": [], "stable": []}
        print(f"   ✅ DTP themes extracted: {themes}")
        return themes
    
    except Exception as e:
        print(f"   ❌ DTP theme extraction error: {e}")
        return {"increased": [], "decreased": [], "stable": []}


def generate_development_narrative(signal, themes, previous_module, current_module):
    """
    Generate a brief descriptive narrative about reflective development.
    NO scores, NO evaluation — purely descriptive.
    """
    increased = ", ".join(themes.get("increased", [])) or "none noted"
    decreased = ", ".join(themes.get("decreased", [])) or "none noted"
    stable = ", ".join(themes.get("stable", [])) or "none noted"
    
    prompt = f"""Write a 60-word neutral observation about a teacher's reflective development.

Facts:
- Modules compared: {previous_module} to {current_module}
- Continuity level: {signal['continuity_label']}
- {signal['continuity_description']}
- Stable themes: {stable}

Write a complete paragraph of exactly 60 words. 
Start with: "Across these modules, your reflection demonstrates"
Do not use bullet points. Write in plain prose only."""

    try:
        if NEW_GENAI_API:
            from google.genai import types as genai_types
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=2000
                )
            )
            # ΠΡΟΣΩΡΙΝΟ DEBUG
            # print(f"   🔍 Raw response: '{response.text}'")
            # print(f"   🔍 Candidates: {response.candidates}")
            narrative = response.text.strip()
        else:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            narrative = response.text.strip()
        
        print(f"   ✅ DTP narrative generated ({len(narrative)} chars)")
        return narrative
    
    except Exception as e:
        print(f"   ❌ DTP narrative error: {e}")
        import traceback
        traceback.print_exc()
        return signal['continuity_description']


def compute_dtp(previous_reflection_text, current_reflection_text, 
                previous_module="M1", current_module="M2"):
    """
    Main DTP function — orchestrates the full developmental signal computation.
    
    Args:
        previous_reflection_text: Text of previous module's reflection
        current_reflection_text: Text of current module's reflection
        previous_module: Module code of previous reflection (e.g. "M1")
        current_module: Module code of current reflection (e.g. "M2")
    
    Returns:
        Dict with full DTP signal, or None on failure
    """
    print(f"\n   📈 DTP: Computing development signal ({previous_module} → {current_module})...")
    
    try:
        # Step 1: Embed both reflections
        print(f"   → Embedding previous reflection...")
        emb1 = embed_query(previous_reflection_text)
        
        print(f"   → Embedding current reflection...")
        emb2 = embed_query(current_reflection_text)
        
        if not emb1 or not emb2:
            print(f"   ❌ DTP: Embedding failed")
            return None
        
        # Step 2: Compute similarity signal
        signal = compute_development_signal(emb1, emb2)
        print(f"   ✅ DTP similarity: {signal['similarity']} ({signal['continuity_label']})")
        
        # Step 3: Extract themes
        themes = extract_development_themes(
            previous_reflection_text, 
            current_reflection_text
        )
        
        # Step 4: Generate narrative
        narrative = generate_development_narrative(
            signal, themes, previous_module, current_module
        )
        
        return {
            'previous_module': previous_module,
            'current_module': current_module,
            'similarity': signal['similarity'],
            'continuity_label': signal['continuity_label'],
            'continuity_description': signal['continuity_description'],
            'narrative': narrative,
            'themes': {
                'increased_themes': themes.get('increased', []),
                'decreased_themes': themes.get('decreased', []),
                'stable_themes': themes.get('stable', [])
            }
        }
    
    except Exception as e:
        print(f"   ❌ DTP error: {e}")
        import traceback
        traceback.print_exc()
        return None

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
        'experience': '5 years',
        'enable_peer_synthesis': True
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

    if 'peer_synthesis' in result and result['peer_synthesis']:
        print("\n" + "="*70)
        print("🤝 PEER INSIGHTS (Cross-Specialty):")
        print("="*70)
        print(result['peer_synthesis'])
        print("="*70)

if __name__ == "__main__":
    test_rag_system()