#!/usr/bin/env python3
"""
Quick Test Script - RAG System Dimension Fix Validation
========================================================
Tests that the embedding dimension fix works correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Now import after Django setup
from rag_query_system import embed_query, search_similar_chunks
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment
load_dotenv()

DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

def test_embedding_dimension():
    """Test 1: Verify embedding produces 768-dimensional vectors"""
    print("\n" + "="*70)
    print("TEST 1: Embedding Dimension Check")
    print("="*70)
    
    test_text = "This is a test reflection about AI in education."
    print(f"Input text: {test_text}")
    print("\nEmbedding...")
    
    embedding = embed_query(test_text)
    
    if embedding is None:
        print("❌ FAILED: Embedding returned None")
        return False
    
    dimension = len(embedding)
    print(f"\n✅ Embedding successful!")
    print(f"   Dimension: {dimension}")
    
    if dimension == 768:
        print("   ✅ PASS: Correct dimension (768)")
        return True
    else:
        print(f"   ❌ FAIL: Expected 768, got {dimension}")
        return False

def test_database_compatibility():
    """Test 2: Verify embedding is compatible with database"""
    print("\n" + "="*70)
    print("TEST 2: Database Compatibility Check")
    print("="*70)
    
    test_text = "Another test about teaching with artificial intelligence."
    print(f"Input text: {test_text}")
    print("\nEmbedding...")
    
    embedding = embed_query(test_text)
    
    if embedding is None:
        print("❌ FAILED: Embedding returned None")
        return False
    
    print("\nConnecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connection successful")
        
        print("\nAttempting vector similarity search...")
        results = search_similar_chunks(conn, embedding, top_k=3)
        
        if results:
            print(f"✅ Retrieved {len(results)} chunks successfully!")
            print("\nSample results:")
            for i, result in enumerate(results[:2], 1):
                print(f"\n   Chunk {i}:")
                print(f"   - Title: {result.get('title', 'N/A')}")
                print(f"   - Distance: {result.get('distance', 'N/A'):.4f}")
                print(f"   - Text preview: {result.get('chunk_text', '')[:80]}...")
            
            conn.close()
            print("\n✅ PASS: Database compatibility confirmed")
            return True
        else:
            print("⚠️  No chunks retrieved (database may be empty)")
            conn.close()
            return True  # Still pass if database is empty
            
    except Exception as e:
        print(f"❌ FAIL: Database error: {e}")
        return False

def test_model_configuration():
    """Test 3: Verify correct model and config are being used"""
    print("\n" + "="*70)
    print("TEST 3: Model Configuration Check")
    print("="*70)
    
    import rag_query_system
    
    # Check if using NEW API
    print(f"Using NEW API: {rag_query_system.NEW_GENAI_API}")
    
    if not rag_query_system.NEW_GENAI_API:
        print("⚠️  WARNING: Using OLD API - dimension reduction may not work")
        return False
    
    # Read source code to verify config
    with open('rag_query_system.py', 'r') as f:
        source = f.read()
    
    checks = {
        'Model name': 'models/gemini-embedding-001' in source,
        'Dimension config': 'output_dimensionality' in source,
        'Dimension value': '768' in source,
    }
    
    print("\nConfiguration checks:")
    all_pass = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}: {'PASS' if result else 'FAIL'}")
        if not result:
            all_pass = False
    
    if all_pass:
        print("\n✅ PASS: All configuration checks passed")
    else:
        print("\n❌ FAIL: Some configuration checks failed")
    
    return all_pass

def test_full_pipeline():
    """Test 4: Full RAG pipeline test"""
    print("\n" + "="*70)
    print("TEST 4: Full Pipeline Test")
    print("="*70)
    
    test_reflection = """
    I found this module on AI foundations very insightful. 
    As a Mathematics teacher in Grade 10, I can see how AI tools 
    like Photomath could help students verify their work. 
    However, I'm concerned about students becoming too dependent 
    on these tools without understanding the underlying concepts.
    """
    
    print("Test reflection:")
    print(test_reflection.strip())
    print("\n" + "-"*70)
    
    try:
        # Import process_reflection
        from rag_query_system import process_reflection
        
        # Create test teacher context
        teacher_context = {
            'name': 'Test Teacher',
            'subject': 'Mathematics',
            'grade_level': 'Grade 10',
            'experience_years': 5,
            'goals': 'Integrate AI tools effectively'
        }
        
        print("\nProcessing reflection through full RAG pipeline...")
        print("(This may take 10-15 seconds)")
        
        result = process_reflection(
            reflection_text=test_reflection,
            teacher_context=teacher_context,
            module_id=1
        )
        
        if result and 'feedback' in result:
            print("\n✅ Pipeline completed successfully!")
            print("\nGenerated feedback preview:")
            print("-" * 70)
            feedback_preview = result['feedback'][:500]
            print(feedback_preview)
            if len(result['feedback']) > 500:
                print(f"\n... (truncated, total length: {len(result['feedback'])} chars)")
            print("-" * 70)
            
            # Check for markdown formatting
            has_markdown = any([
                '**' in result['feedback'],      # Bold
                '- ' in result['feedback'],       # Bullets
                '1.' in result['feedback'],       # Numbered
                'Dear' in result['feedback']      # Greeting
            ])
            
            if has_markdown:
                print("✅ Markdown formatting detected in feedback")
            else:
                print("⚠️  No markdown formatting detected (may need prompt adjustment)")
            
            print("\n✅ PASS: Full pipeline working")
            return True
        else:
            print("❌ FAIL: Pipeline returned no feedback")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("RAG SYSTEM DIMENSION FIX - VALIDATION TEST SUITE")
    print("="*70)
    print("\nThis script validates that the embedding dimension fix works correctly.")
    print("It will test:")
    print("  1. Embedding produces 768-dimensional vectors")
    print("  2. Vectors are compatible with database")
    print("  3. Configuration is correct")
    print("  4. Full RAG pipeline works end-to-end")
    
    input("\nPress ENTER to start tests...")
    
    results = {
        'Embedding Dimension': test_embedding_dimension(),
        'Database Compatibility': test_database_compatibility(),
        'Model Configuration': test_model_configuration(),
        'Full Pipeline': test_full_pipeline()
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! RAG system is ready for production use.")
        print("\nNext steps:")
        print("  1. Test with real user reflection submission")
        print("  2. Verify markdown formatting in browser")
        print("  3. Check database for rag_queries entry")
        print("  4. Monitor costs and response times")
    else:
        print("\n⚠️  SOME TESTS FAILED. Review errors above and fix issues.")
        print("\nRecommended actions:")
        print("  1. Check that all three files have dimension reduction config")
        print("  2. Verify PostgreSQL and pgvector are running")
        print("  3. Confirm GEMINI_API_KEY is set correctly")
        print("  4. Review error messages for specific issues")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
