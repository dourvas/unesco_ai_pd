import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Check what subjects we have
cursor.execute("""
    SELECT 
        dc.metadata->>'subject' as subject,
        COUNT(*) as count
    FROM document_chunks dc
    WHERE dc.metadata->>'subject' IS NOT NULL
    GROUP BY dc.metadata->>'subject'
    ORDER BY subject;
""")

print("\n📊 Subjects in Database:\n")
for row in cursor.fetchall():
    print(f"  {row['subject']}: {row['count']} chunks")

# Check if Mathematics exists
cursor.execute("""
    SELECT 
        id,
        LEFT(chunk_text, 100) as preview,
        metadata->>'subject' as subject,
        metadata->>'part' as part
    FROM document_chunks
    WHERE metadata->>'subject' = 'Mathematics'
    LIMIT 3;
""")

print("\n\n📚 Sample Mathematics Chunks:\n")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"  ID {row['id']}: {row['part']}")
        print(f"  Preview: {row['preview']}...")
        print()
else:
    print("  ❌ No Mathematics chunks found!")

cursor.close()
conn.close()