"""
Add Feedback Rating - Phase 2C
================================
Allows users to rate RAG feedback (1-5 stars)
"""

import psycopg2
from datetime import datetime

DB_CONFIG = {
    'dbname': 'unesco_ai_teacher_pd',
    'user': 'postgres',
    'password': 'Django123!',
    'host': 'localhost',
    'port': '5432'
}

def add_feedback(query_id, rating, comments=None):
    """
    Add user feedback to a RAG query.
    
    Args:
        query_id: ID of the RAG query
        rating: 1-5 stars
        comments: Optional text feedback
    """
    if not (1 <= rating <= 5):
        print("❌ Rating must be between 1 and 5")
        return False
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE rag_queries
            SET feedback_rating = %s,
                feedback_comments = %s,
                feedback_timestamp = %s,
                updated_at = NOW()
            WHERE id = %s;
        """, (rating, comments, datetime.now(), query_id))
        
        conn.commit()
        
        print(f"✅ Feedback added successfully!")
        print(f"   Query ID: {query_id}")
        print(f"   Rating: {rating} stars")
        if comments:
            print(f"   Comments: {comments}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Test: Add 5-star rating to query ID 1
    add_feedback(
        query_id=1,
        rating=5,
        comments="Excellent feedback! Very personalized and helpful."
    )