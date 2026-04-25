import psycopg2

conn = psycopg2.connect(
    dbname="unesco_ai_teacher_pd",
    user="postgres",
    password="Django123!",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

# Get M1 main content
cursor.execute("""
    SELECT id, content_type, content_data, metadata
    FROM modules_modulecontent
    WHERE module_id = 1
    ORDER BY id;
""")

rows = cursor.fetchall()

print(f"📊 Found {len(rows)} content entries for Module 1:\n")

total_chars = 0
main_content_parts = []

for row in rows:
    content_id, content_type, content_data, metadata = row
    content_length = len(content_data) if content_data else 0
    total_chars += content_length
    
    print(f"ID {content_id}: {content_type}")
    print(f"  Length: {content_length} characters")
    
    # Check metadata
    if metadata and 'title' in metadata:
        print(f"  Title: {metadata['title']}")
    
    # Show preview
    if content_data:
        preview = content_data[:100].replace('\n', ' ')
        print(f"  Preview: {preview}...")
    
    print()
    
    # Collect main_content
    if content_type == 'main_content':
        main_content_parts.append({
            'id': content_id,
            'content': content_data,
            'metadata': metadata
        })

print(f"\n📈 Summary:")
print(f"  Total entries: {len(rows)}")
print(f"  Total characters: {total_chars:,}")
print(f"  Main content parts: {len(main_content_parts)}")

if main_content_parts:
    print(f"\n✅ Found {len(main_content_parts)} main_content entries!")
    print("   These will be used for RAG embeddings.")
    
    total_main = sum(len(p['content']) for p in main_content_parts)
    print(f"   Total main content: {total_main:,} characters")
else:
    print("\n⚠️  No main_content entries found!")
    print("   We'll use all content for now.")

cursor.close()
conn.close()