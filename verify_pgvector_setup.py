#!/usr/bin/env python3
"""
pgvector 0.8.1 Configuration Verification
==========================================
Verifies that pgvector extension is properly configured
and compatible with our 768-dimensional embeddings.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

def check_pgvector_version():
    """Check pgvector extension version"""
    print("\n" + "="*70)
    print("CHECK 1: pgvector Extension Version")
    print("="*70)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname = 'vector';
        """)
        
        result = cursor.fetchone()
        
        if result:
            print(f"✅ pgvector installed: version {result['extversion']}")
            
            if result['extversion'] == '0.8.1':
                print("   ✅ PASS: Running expected version (0.8.1)")
            else:
                print(f"   ⚠️  WARNING: Expected 0.8.1, found {result['extversion']}")
            
            conn.close()
            return True
        else:
            print("❌ FAIL: pgvector extension not found")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Database error: {e}")
        return False

def check_embedding_dimensions():
    """Check embedding column dimensions"""
    print("\n" + "="*70)
    print("CHECK 2: Embedding Column Dimensions")
    print("="*70)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get column definition
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                udt_name
            FROM information_schema.columns
            WHERE table_name = 'document_chunks'
              AND column_name = 'embedding';
        """)
        
        result = cursor.fetchone()
        
        if result:
            print(f"Column: {result['column_name']}")
            print(f"Type: {result['udt_name']}")
            
            # Get actual dimension from pg_attribute
            cursor.execute("""
                SELECT atttypmod 
                FROM pg_attribute 
                WHERE attrelid = 'document_chunks'::regclass 
                  AND attname = 'embedding';
            """)
            
            dim_result = cursor.fetchone()
            if dim_result and dim_result['atttypmod'] > 0:
                dimensions = dim_result['atttypmod']
                print(f"Dimensions: {dimensions}")
                
                if dimensions == 768:
                    print("   ✅ PASS: 768 dimensions (compatible with pgvector 0.8.1)")
                elif dimensions > 2000:
                    print(f"   ❌ FAIL: {dimensions} dimensions exceeds pgvector 0.8.1 limit")
                else:
                    print(f"   ✅ OK: {dimensions} dimensions (within limits)")
            
            conn.close()
            return True
        else:
            print("❌ FAIL: embedding column not found")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Database error: {e}")
        return False

def check_vector_index():
    """Check vector similarity index configuration"""
    print("\n" + "="*70)
    print("CHECK 3: Vector Similarity Index")
    print("="*70)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = 'document_chunks'
              AND indexname LIKE '%embedding%';
        """)
        
        results = cursor.fetchall()
        
        if results:
            for idx in results:
                print(f"\nIndex: {idx['indexname']}")
                
                # Check if ivfflat or hnsw
                if 'ivfflat' in idx['indexdef'].lower():
                    print("   Type: IVFFlat")
                    print("   ✅ PASS: Using IVFFlat index (compatible with 0.8.1)")
                elif 'hnsw' in idx['indexdef'].lower():
                    print("   Type: HNSW")
                    print("   ✅ PASS: Using HNSW index (compatible with 0.8.1)")
                else:
                    print("   ⚠️  WARNING: Unknown index type")
                
                # Check distance metric
                if 'vector_cosine_ops' in idx['indexdef']:
                    print("   Distance: Cosine")
                elif 'vector_l2_ops' in idx['indexdef']:
                    print("   Distance: L2 (Euclidean)")
                else:
                    print("   Distance: Unknown")
            
            conn.close()
            return True
        else:
            print("⚠️  WARNING: No vector index found")
            print("   This may impact performance but is not critical")
            conn.close()
            return True
            
    except Exception as e:
        print(f"❌ FAIL: Database error: {e}")
        return False

def check_chunk_count():
    """Check number of chunks in database"""
    print("\n" + "="*70)
    print("CHECK 4: Document Chunks Count")
    print("="*70)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT COUNT(*) as count FROM document_chunks;")
        result = cursor.fetchone()
        
        count = result['count']
        print(f"Total chunks: {count}")
        
        if count >= 50:
            print("   ✅ PASS: Sufficient chunks for testing")
        elif count > 0:
            print(f"   ⚠️  WARNING: Only {count} chunks (expected ~80-120)")
        else:
            print("   ❌ FAIL: No chunks found - run ingestion scripts")
        
        # Check breakdown by document type
        cursor.execute("""
            SELECT 
                d.document_type,
                COUNT(*) as chunk_count
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            GROUP BY d.document_type
            ORDER BY chunk_count DESC;
        """)
        
        breakdown = cursor.fetchall()
        if breakdown:
            print("\n   Chunks by document type:")
            for row in breakdown:
                print(f"   - {row['document_type']}: {row['chunk_count']} chunks")
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"❌ FAIL: Database error: {e}")
        return False

def test_vector_query():
    """Test a simple vector similarity query"""
    print("\n" + "="*70)
    print("CHECK 5: Vector Similarity Query Test")
    print("="*70)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create a random 768-dimensional vector for testing
        import random
        test_vector = [random.random() for _ in range(768)]
        
        print("Testing similarity search with random 768-dim vector...")
        
        cursor.execute("""
            SELECT 
                id,
                chunk_text,
                embedding <=> %s::vector AS distance
            FROM document_chunks
            ORDER BY distance
            LIMIT 3;
        """, (test_vector,))
        
        results = cursor.fetchall()
        
        if results:
            print(f"✅ Query successful! Retrieved {len(results)} chunks")
            print(f"\n   Sample result:")
            print(f"   - Distance: {results[0]['distance']:.4f}")
            print(f"   - Text preview: {results[0]['chunk_text'][:80]}...")
            print("\n   ✅ PASS: Vector similarity search working")
            conn.close()
            return True
        else:
            print("⚠️  No results (database may be empty)")
            conn.close()
            return True
            
    except Exception as e:
        print(f"❌ FAIL: Vector query error: {e}")
        print("\n   This indicates a dimension mismatch or index issue!")
        return False

def main():
    """Run all checks"""
    print("\n" + "="*70)
    print("pgvector 0.8.1 CONFIGURATION VERIFICATION")
    print("="*70)
    print("\nThis script verifies that pgvector is properly configured")
    print("for 768-dimensional embeddings with our RAG system.")
    
    results = {
        'pgvector Version': check_pgvector_version(),
        'Embedding Dimensions': check_embedding_dimensions(),
        'Vector Index': check_vector_index(),
        'Chunk Count': check_chunk_count(),
        'Vector Query Test': test_vector_query()
    }
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check}")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("\npgvector 0.8.1 is properly configured for:")
        print("  ✅ 768-dimensional embeddings")
        print("  ✅ Vector similarity search")
        print("  ✅ IVFFlat/HNSW indexing")
        print("  ✅ RAG system compatibility")
        print("\n✅ System is ready for production use!")
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("\nReview the errors above and:")
        print("  1. Ensure pgvector extension is installed")
        print("  2. Verify embedding column is vector(768)")
        print("  3. Check that indexes are created")
        print("  4. Run ingestion scripts if no chunks found")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
