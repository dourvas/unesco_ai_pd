"""
Extract Subject Boxes from Database
====================================
Retrieves all 32 subject-specific content boxes from M1.
"""

import psycopg2
import json

DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

def extract_subject_boxes():
    """Extract all subject boxes from database."""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Get all subject boxes (part2 and part4)
    cursor.execute("""
        SELECT 
            id,
            content_type,
            subject_area,
            content_data,
            metadata
        FROM modules_modulecontent
        WHERE module_id = 1 
        AND content_type IN ('subject_box_part2', 'subject_box_part4')
        ORDER BY subject_area, content_type;
    """)
    
    boxes = cursor.fetchall()
    
    print(f"\n📦 Found {len(boxes)} subject boxes\n")
    print("="*70)
    
    # Group by subject
    subjects = {}
    for box_id, content_type, subject, content_data, metadata in boxes:
        if subject not in subjects:
            subjects[subject] = {'part2': None, 'part4': None}
        
        part = 'part2' if 'part2' in content_type else 'part4'
        subjects[subject][part] = {
            'id': box_id,
            'content': content_data,
            'length': len(content_data)
        }
    
    # Display summary
    for subject, parts in subjects.items():
        print(f"\n{subject}:")
        if parts['part2']:
            print(f"  Part 2: {parts['part2']['length']} chars")
        if parts['part4']:
            print(f"  Part 4: {parts['part4']['length']} chars")
    
    print("\n" + "="*70)
    print(f"\n✅ Total subjects: {len(subjects)}")
    print(f"✅ Total boxes: {len(boxes)}")
    
    cursor.close()
    conn.close()
    
    return subjects

if __name__ == "__main__":
    subjects = extract_subject_boxes()