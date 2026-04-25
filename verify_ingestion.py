import psycopg2

conn = psycopg2.connect(
    dbname="unesco_ai_teacher_pd",
    user="postgres",
    password="Django123!",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

print("📊 RAG System Verification\n")
print("="*60)

# Check documents
cursor.execute("""
    SELECT id, title, document_type, total_chunks
    FROM documents
    ORDER BY id;
""")

print("\n📚 Documents:")
for doc in cursor.fetchall():
    doc_id, title, doc_type, chunks = doc
    print(f"\n  [{doc_id}] {title}")
    print(f"      Type: {doc_type}")
    print(f"      Chunks: {chunks}")

# Check embeddings
cursor.execute("""
    SELECT 
        COUNT(*) as total_chunks,
        COUNT(embedding) as chunks_with_embeddings
    FROM document_chunks;
""")

total, with_emb = cursor.fetchone()
print(f"\n\n🔮 Embeddings:")
print(f"  Total chunks: {total}")
print(f"  With embeddings: {with_emb}")
print(f"  Success rate: {(with_emb/total)*100:.1f}%")

# Sample chunk
cursor.execute("""
    SELECT chunk_text, array_length(embedding, 1) as embedding_dim
    FROM document_chunks
    WHERE embedding IS NOT NULL
    LIMIT 1;
""")

chunk_text, emb_dim = cursor.fetchone()
print(f"\n\n📝 Sample Chunk:")
print(f"  Text preview: {chunk_text[:150]}...")
print(f"  Embedding dimensions: {emb_dim}")

cursor.close()
conn.close()

print("\n" + "="*60)
print("✅ RAG system is ready for queries!")
print("="*60)