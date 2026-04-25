import psycopg2

# Database connection
try:
    conn = psycopg2.connect(
        dbname="unesco_ai_teacher_pd",
        user="postgres",
        password="Django123!",
        host="localhost",
        port="5432"
    )
    
    cursor = conn.cursor()
    
    # Test 1: Check RAG tables
    cursor.execute("SELECT COUNT(*) FROM documents;")
    print(f"✅ Documents in database: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM document_chunks;")
    print(f"✅ Document chunks in database: {cursor.fetchone()[0]}")
    
    # Test 2: Check if modules table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'modules%';
    """)
    
    tables = cursor.fetchall()
    print(f"\n✅ Module-related tables found:")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Test 3: Try to read M1 content (if table exists)
    try:
        cursor.execute("""
            SELECT id, content 
            FROM modules_modulecontent 
            WHERE module_id = 1 
            LIMIT 1;
        """)
        
        result = cursor.fetchone()
        if result:
            content_id, content = result
            print(f"\n✅ M1 content found!")
            print(f"   - Content ID: {content_id}")
            print(f"   - Length: {len(content)} characters")
            print(f"   - Preview: {content[:150]}...")
        else:
            print("\n⚠️  No M1 content found in database")
            
    except psycopg2.Error as e:
        print(f"\n⚠️  modules_modulecontent table not found or error: {e}")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 Database connection successful!")
    
except psycopg2.Error as e:
    print(f"❌ Database connection failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")