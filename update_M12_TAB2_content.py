"""
Update M12 TAB2 main_content in modules_modulecontent
Run from project root: python update_M12_TAB2_content.py

Reads the fixed HTML file and updates the existing record in the database.
"""

import psycopg2
import os
import sys

# ── Config ────────────────────────────────────────────────────────────────────
HTML_FILE = "M12_TAB2_content_fixed.html"  # place in same folder as this script

DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

# ── Read HTML ─────────────────────────────────────────────────────────────────
if not os.path.exists(HTML_FILE):
    print(f"❌ File not found: {HTML_FILE}")
    print("   Place M12_TAB2_content_fixed.html in the same directory as this script.")
    sys.exit(1)

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    new_content = f.read()

print(f"✅ Read {len(new_content):,} characters from {HTML_FILE}")

# ── Connect & Update ──────────────────────────────────────────────────────────
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # First: verify the record exists
    cursor.execute("""
        SELECT id, LENGTH(content_data) as current_length
        FROM modules_modulecontent
        WHERE module_id = (SELECT id FROM modules_module WHERE code = 'M12')
          AND content_type = 'main_content'
          AND subject_area = 'Universal'
    """)
    row = cursor.fetchone()

    if not row:
        print("❌ No main_content record found for M12 / Universal.")
        print("   Run an INSERT instead — the record does not exist yet.")
        conn.close()
        sys.exit(1)

    record_id, current_length = row
    print(f"✅ Found record id={record_id}, current size={current_length:,} chars")

    # Perform the UPDATE
    cursor.execute("""
        UPDATE modules_modulecontent
        SET content_data = %s,
            updated_at   = NOW()
        WHERE id = %s
    """, (new_content, record_id))

    conn.commit()

    # Verify
    cursor.execute("SELECT LENGTH(content_data) FROM modules_modulecontent WHERE id = %s", (record_id,))
    new_length = cursor.fetchone()[0]
    print(f"✅ UPDATE successful — new size: {new_length:,} chars")
    print(f"   (was {current_length:,} → now {new_length:,})")

    cursor.close()
    conn.close()
    print("\n✅ Done. Refresh M12 TAB2 in the browser to verify.")

except psycopg2.Error as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)
