#!/usr/bin/env python3
"""
Phase 2E: RAG System Testing with Enhanced CSV Export
======================================================

Improvements over Phase 2D:
- Actual cost values in CSV (not placeholders)
- Better column naming for analysis
- Token usage tracking
- Enhanced error reporting
- Timestamp formatting

Author: John Dourvas
Date: February 5, 2026
"""

import os
import sys
import time
import json
import csv
from datetime import datetime
from pathlib import Path

# Add project root to path
# Script is in: unesco_ai_pd/phase2e_testing/
# Project root is: unesco_ai_pd/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unesco_ai_pd.settings')
import django
django.setup()

from rag_system.rag_query_system import generate_personalized_feedback

# Test cases from Phase 2D
TEST_CASES = [
    {
        "id": "TC01",
        "name": "Mathematics Teacher - Positive Reflection",
        "subject": "Mathematics",
        "grade_level": "High School (Grades 10-12)",
        "reflection": "I tried using AI to generate practice problems for my algebra students. The problems were well-structured and appropriately challenging. Students engaged more than with traditional textbook exercises. I'm impressed by how the AI understood the difficulty level I needed.",
        "expected_quality": "High"
    },
    {
        "id": "TC02",
        "name": "Computer Science - Technical Depth",
        "subject": "Computer Science",
        "grade_level": "High School (Grades 10-12)",
        "reflection": "Used AI to help students debug their Python code. The AI explanations were too simple for my advanced students. I had to supplement with more technical details about recursion and time complexity. Need to find ways to adjust the AI's technical level.",
        "expected_quality": "Medium-High"
    },
    {
        "id": "TC03",
        "name": "Physics - Cross-Disciplinary",
        "subject": "Physics",
        "grade_level": "High School (Grades 10-12)",
        "reflection": "I experimented with using AI to explain kinematics through real-world examples. Students loved seeing how physics applies to sports and everyday life. The AI suggested some creative demonstrations I hadn't thought of.",
        "expected_quality": "High"
    },
    {
        "id": "TC04",
        "name": "Language Arts - Creative Writing",
        "subject": "Language Arts",
        "grade_level": "Middle School (Grades 7-9)",
        "reflection": "My students used AI as a brainstorming partner for their creative writing. Some became too dependent on AI suggestions instead of developing their own voice. I need strategies to balance AI assistance with student originality.",
        "expected_quality": "High"
    },
    {
        "id": "TC05",
        "name": "History - Critical Thinking",
        "subject": "History",
        "grade_level": "Middle School (Grades 7-9)",
        "reflection": "Used AI to generate alternative history scenarios for discussion. Students analyzed what-if questions about historical events. This sparked great debates about causation and historical interpretation. Very effective for developing critical thinking.",
        "expected_quality": "High"
    },
    {
        "id": "TC06",
        "name": "Visual Arts - AI Image Generation",
        "subject": "Visual Arts",
        "grade_level": "High School (Grades 10-12)",
        "reflection": "Introduced students to AI image generation tools. Some created stunning digital art, but others felt it 'wasn't real art.' We had important discussions about creativity, originality, and what it means to be an artist in the AI age.",
        "expected_quality": "High"
    },
    {
        "id": "TC07",
        "name": "Physical Education - Personalized Plans",
        "subject": "Physical Education",
        "grade_level": "Primary School (Grades 1-6)",
        "reflection": "Used AI to create personalized fitness plans for different student ability levels. The plans were good starting points but didn't account for some physical limitations. I had to manually adjust several plans.",
        "expected_quality": "Medium-High"
    },
    {
        "id": "TC08",
        "name": "Kindergarten - Age Appropriateness",
        "subject": "Kindergarten",
        "grade_level": "Kindergarten",
        "reflection": "Experimented with AI storytelling tools with my kindergarten class. The vocabulary was sometimes too advanced, but the stories were engaging. I learned to pre-screen content before presenting to 5-year-olds.",
        "expected_quality": "Medium-High"
    },
    {
        "id": "TC09",
        "name": "Edge Case - Very Short Reflection",
        "subject": "Mathematics",
        "grade_level": "High School (Grades 10-12)",
        "reflection": "AI worked well.",
        "expected_quality": "Low-Medium"
    },
    {
        "id": "TC10",
        "name": "Edge Case - Negative Experience",
        "subject": "Computer Science",
        "grade_level": "High School (Grades 10-12)",
        "reflection": "The AI tool crashed three times during my lesson. Students were frustrated and I felt unprepared. This technology seems unreliable for classroom use.",
        "expected_quality": "Medium"
    }
]


def run_test_case(test_case):
    """
    Run a single test case and return detailed results.
    
    Returns dict with:
    - test_id, name, subject, grade_level, reflection
    - response_time, response_text
    - input_tokens, output_tokens, total_tokens
    - embedding_cost, generation_cost, total_cost
    - chunks_retrieved, top_chunk_similarity
    - status, error (if any)
    """
    print(f"\n{'='*70}")
    print(f"Running: {test_case['id']} - {test_case['name']}")
    print(f"Subject: {test_case['subject']} | Grade: {test_case['grade_level']}")
    print(f"{'='*70}")
    
    result = {
        "test_id": test_case['id'],
        "test_name": test_case['name'],
        "subject": test_case['subject'],
        "grade_level": test_case['grade_level'],
        "reflection_text": test_case['reflection'],
        "reflection_length": len(test_case['reflection']),
        "expected_quality": test_case['expected_quality'],
    }
    
    try:
        # Mock user_id (for testing)
        user_id = 1
        
        # Time the request
        start_time = time.time()
        
        # Call RAG system
        response = generate_personalized_feedback(
            user_id=user_id,
            reflection_text=test_case['reflection'],
            module_id=1,
            subject=test_case['subject'],
            grade_level=test_case['grade_level']
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Extract response details
        result.update({
            "status": "SUCCESS",
            "response_time_seconds": round(response_time, 2),
            "response_text": response.get('feedback', 'N/A'),
            "response_length": len(response.get('feedback', '')),
            
            # Token usage
            "input_tokens": response.get('input_tokens', 0),
            "output_tokens": response.get('output_tokens', 0),
            "total_tokens": response.get('input_tokens', 0) + response.get('output_tokens', 0),
            
            # Costs (actual calculation)
            "embedding_cost_eur": response.get('embedding_cost', 0),
            "generation_cost_eur": response.get('generation_cost', 0),
            "total_cost_eur": response.get('total_cost', 0),
            
            # Retrieval info
            "chunks_retrieved": len(response.get('chunks', [])),
            "top_chunk_source": response.get('chunks', [{}])[0].get('source', 'N/A') if response.get('chunks') else 'N/A',
            "top_chunk_similarity": round(response.get('chunks', [{}])[0].get('similarity', 0), 4) if response.get('chunks') else 0,
            
            # Database info
            "query_id": response.get('query_id', None),
            "error": None
        })
        
        print(f"✅ SUCCESS - {response_time:.2f}s - {result['response_length']} chars")
        print(f"💰 Cost: €{result['total_cost_eur']:.6f} (input: €{result['embedding_cost_eur']:.6f}, gen: €{result['generation_cost_eur']:.6f})")
        print(f"📊 Tokens: {result['total_tokens']} ({result['input_tokens']} in + {result['output_tokens']} out)")
        print(f"📚 Retrieved: {result['chunks_retrieved']} chunks from {result['top_chunk_source']}")
        
    except Exception as e:
        result.update({
            "status": "FAILED",
            "response_time_seconds": 0,
            "response_text": None,
            "response_length": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "embedding_cost_eur": 0,
            "generation_cost_eur": 0,
            "total_cost_eur": 0,
            "chunks_retrieved": 0,
            "top_chunk_source": None,
            "top_chunk_similarity": 0,
            "query_id": None,
            "error": str(e)
        })
        print(f"❌ FAILED - {str(e)}")
    
    return result


def save_to_csv(results, output_dir):
    """Save results to CSV with proper formatting."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rag_test_results_phase2e_{timestamp}.csv"
    filepath = output_dir / filename
    
    # Define CSV columns
    fieldnames = [
        "test_id",
        "test_name",
        "subject",
        "grade_level",
        "reflection_length",
        "expected_quality",
        "status",
        "response_time_seconds",
        "response_length",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "embedding_cost_eur",
        "generation_cost_eur",
        "total_cost_eur",
        "chunks_retrieved",
        "top_chunk_source",
        "top_chunk_similarity",
        "query_id",
        "error"
    ]
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Only write the fields we want in CSV
            csv_row = {k: result.get(k, '') for k in fieldnames}
            writer.writerow(csv_row)
    
    print(f"\n💾 Results saved to: {filepath}")
    return filepath


def print_summary(results):
    """Print summary statistics."""
    successful = [r for r in results if r['status'] == 'SUCCESS']
    failed = [r for r in results if r['status'] == 'FAILED']
    
    print(f"\n{'='*70}")
    print(f"PHASE 2E TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        avg_time = sum(r['response_time_seconds'] for r in successful) / len(successful)
        total_cost = sum(r['total_cost_eur'] for r in successful)
        avg_cost = total_cost / len(successful)
        total_tokens = sum(r['total_tokens'] for r in successful)
        
        print(f"\n📊 Performance Metrics:")
        print(f"  Average Response Time: {avg_time:.2f}s")
        print(f"  Total Cost: €{total_cost:.6f}")
        print(f"  Average Cost per Query: €{avg_cost:.6f}")
        print(f"  Total Tokens Used: {total_tokens}")
        
        # Cost projections
        cost_per_user_15_modules = avg_cost * 15
        cost_110_users = cost_per_user_15_modules * 110
        
        print(f"\n💰 Cost Projections:")
        print(f"  Cost per user (15 modules): €{cost_per_user_15_modules:.4f}")
        print(f"  Cost for 110 users: €{cost_110_users:.2f}")
        print(f"  Budget remaining: €{110 - cost_110_users:.2f} ({((110-cost_110_users)/110*100):.1f}%)")
    
    if failed:
        print(f"\n❌ Failed Tests:")
        for r in failed:
            print(f"  - {r['test_id']}: {r['error']}")
    
    print(f"{'='*70}\n")


def main():
    """Main test execution."""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                     RAG SYSTEM TESTING - PHASE 2E                     ║
║                   Enhanced CSV Export & Analytics                     ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Create output directory
    output_dir = Path(__file__).parent / 'test_results'
    output_dir.mkdir(exist_ok=True)
    
    # Run all tests
    results = []
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}]", end=" ")
        result = run_test_case(test_case)
        results.append(result)
        time.sleep(0.5)  # Brief pause between tests
    
    # Save results
    csv_path = save_to_csv(results, output_dir)
    
    # Print summary
    print_summary(results)
    
    print(f"✅ Phase 2E testing complete!")
    print(f"📁 Results: {csv_path}")
    print(f"\nNext: Run analyze_results_phase2e.py for detailed analysis")


if __name__ == "__main__":
    main()
