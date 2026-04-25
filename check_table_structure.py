import psycopg2

conn = psycopg2.connect(
    dbname="unesco_ai_teacher_pd",
    user="postgres",
    password="Django123!",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

# Get table structure
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name = 'modules_modulecontent'
    ORDER BY ordinal_position;
""")

print("📋 modules_modulecontent table structure:\n")
columns = cursor.fetchall()
for col in columns:
    col_name, data_type, max_length = col
    length_info = f" ({max_length})" if max_length else ""
    print(f"   - {col_name}: {data_type}{length_info}")

# Try to see sample data
print("\n📊 Sample data (first row):\n")
cursor.execute("SELECT * FROM modules_modulecontent LIMIT 1;")

row = cursor.fetchone()
if row:
    for i, col in enumerate(columns):
        col_name = col[0]
        value = row[i]
        
        # Show preview for long text
        if isinstance(value, str) and len(value) > 100:
            print(f"   - {col_name}: {value[:100]}... (length: {len(value)})")
        else:
            print(f"   - {col_name}: {value}")
else:
    print("   (No data found)")

cursor.close()
conn.close()

print("\n✅ Done!")