"""
RAG System Test Suite - Phase 2D (Windows Compatible)
UNESCO AI Teacher Professional Development Platform

USAGE:
    python test_rag_phase2d.py                    # Run all tests
    python test_rag_phase2d.py --subject-only     # Subject diversity only
    python test_rag_phase2d.py --edge-only        # Edge cases only
    python test_rag_phase2d.py --quick            # Quick validation (2 tests)
    python test_rag_phase2d.py --test SD01        # Single test by ID
"""

import sys
import time
import csv
import argparse
import os
from datetime import datetime
from pathlib import Path

# Import the RAG query system - Windows compatible path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from rag_query_system import process_reflection

# ============================================================================
# TEST CASE DEFINITIONS
# ============================================================================

SUBJECT_DIVERSITY_TESTS = [
    {
        "test_id": "SD01",
        "category": "STEM - Mathematics",
        "teacher_profile": {
            "subject": "Mathematics",
            "grade_level": "High School",
            "years_experience": 8,
            "ai_comfort": "Intermediate"
        },
        "reflection": "I tried using AI to generate word problems for quadratic equations, but my students found them too abstract and disconnected from real-world applications. They struggled to see the relevance.",
        "expected_elements": ["mathematics", "real-world", "quadratic", "concrete examples"]
    },
    {
        "test_id": "SD02",
        "category": "STEM - Computer Science",
        "teacher_profile": {
            "subject": "Computer Science",
            "grade_level": "University",
            "years_experience": 5,
            "ai_comfort": "Advanced"
        },
        "reflection": "I used ChatGPT to help students debug their Python code. Some students became overly reliant on it and stopped trying to understand the errors themselves. How can I use AI as a learning scaffold rather than a crutch?",
        "expected_elements": ["scaffolding", "autonomy", "programming", "debugging"]
    },
    {
        "test_id": "SD03",
        "category": "STEM - Physics",
        "teacher_profile": {
            "subject": "Physics",
            "grade_level": "High School",
            "years_experience": 12,
            "ai_comfort": "Beginner"
        },
        "reflection": "I'm teaching Newton's laws and wondering if AI could help create simulations or visualizations. I don't know where to start with this technology.",
        "expected_elements": ["visualization", "simulation", "physics", "beginner"]
    },
    {
        "test_id": "SD04",
        "category": "Humanities - Language Arts",
        "teacher_profile": {
            "subject": "Language Arts",
            "grade_level": "Middle School",
            "years_experience": 15,
            "ai_comfort": "Intermediate"
        },
        "reflection": "My students used AI to write essays about Greek mythology. The writing was grammatically perfect but lacked personal voice and critical thinking. I'm concerned about assessment validity.",
        "expected_elements": ["writing", "assessment", "critical thinking", "authenticity"]
    },
    {
        "test_id": "SD05",
        "category": "Humanities - History",
        "teacher_profile": {
            "subject": "History",
            "grade_level": "High School",
            "years_experience": 20,
            "ai_comfort": "Beginner"
        },
        "reflection": "I asked AI to create a timeline of Ancient Greek history for my class. It was accurate but I worry students won't develop research skills if everything is handed to them.",
        "expected_elements": ["research skills", "history", "source evaluation", "student learning"]
    },
    {
        "test_id": "SD06",
        "category": "Arts - Visual Arts",
        "teacher_profile": {
            "subject": "Art",
            "grade_level": "Elementary",
            "years_experience": 7,
            "ai_comfort": "Intermediate"
        },
        "reflection": "Students experimented with AI art generators (DALL-E, Midjourney). Some created beautiful images but I'm questioning: is this still 'art education' or just prompt writing? What skills are they actually developing?",
        "expected_elements": ["creativity", "art", "skill development", "artistic process"]
    },
    {
        "test_id": "SD07",
        "category": "Vocational - Physical Education",
        "teacher_profile": {
            "subject": "Physical Education",
            "grade_level": "High School",
            "years_experience": 10,
            "ai_comfort": "Beginner"
        },
        "reflection": "I heard about AI apps that analyze sports performance. Could this help my students improve their basketball technique? I'm not sure how to integrate technology into physical activities.",
        "expected_elements": ["physical education", "performance", "technology integration", "sports"]
    },
    {
        "test_id": "SD08",
        "category": "Early Childhood - Kindergarten",
        "teacher_profile": {
            "subject": "Kindergarten Generalist",
            "grade_level": "Kindergarten",
            "years_experience": 5,
            "ai_comfort": "Beginner"
        },
        "reflection": "I'm teaching 5-year-olds and wondering if AI tools are even appropriate for this age group. What would developmentally appropriate AI integration look like in early childhood education?",
        "expected_elements": ["early childhood", "developmental", "age appropriate", "kindergarten"]
    }
]

EDGE_CASE_TESTS = [
    {
        "test_id": "EC01",
        "category": "Vague Input",
        "teacher_profile": {
            "subject": "Mathematics",
            "grade_level": "Middle School",
            "years_experience": 5,
            "ai_comfort": "Intermediate"
        },
        "reflection": "It was interesting.",
        "expected_behavior": "Should request elaboration while still providing value"
    },
    {
        "test_id": "EC02",
        "category": "Off-Topic Input",
        "teacher_profile": {
            "subject": "Science",
            "grade_level": "High School",
            "years_experience": 10,
            "ai_comfort": "Advanced"
        },
        "reflection": "I hate AI and I don't think it belongs in education at all. This whole module is a waste of time.",
        "expected_behavior": "Should acknowledge concern, address pedagogically, maintain UNESCO alignment"
    }
]

QUICK_VALIDATION_TESTS = [
    SUBJECT_DIVERSITY_TESTS[0],  # SD01 - Mathematics
    EDGE_CASE_TESTS[0]            # EC01 - Vague input
]

# ============================================================================
# TESTING FRAMEWORK
# ============================================================================

class RAGTestSuite:
    """Comprehensive testing framework for RAG system validation"""
    
    def __init__(self, output_dir="test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        
    def run_test(self, test_case, test_type):
        """Execute a single test case and collect metrics"""
        print(f"\n{'='*70}")
        print(f"Test: {test_case['test_id']} - {test_case['category']}")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        try:
            # Build teacher context as dictionary (required by process_reflection)
            teacher_context = {
                'subject': test_case['teacher_profile']['subject'],
                'grade_level': test_case['teacher_profile']['grade_level'],
                'years_experience': test_case['teacher_profile']['years_experience'],
                'ai_comfort': test_case['teacher_profile']['ai_comfort']
            }
            
            # Execute RAG query
            result = process_reflection(
                reflection_text=test_case['reflection'],
                teacher_context=teacher_context,
                user_id=1,
                module_id=1
            )
            
            execution_time = time.time() - start_time
            
            # Display concise results
            print(f"\n📋 Profile: {test_case['teacher_profile']['subject']} | {test_case['teacher_profile']['grade_level']}")
            print(f"📝 Reflection: {test_case['reflection'][:100]}...")
            print(f"💬 Feedback: {result['feedback'][:200]}...")
            print(f"⏱️  Time: {execution_time:.2f}s | 💰 Cost: €{result.get('cost_estimate', 0):.6f}")
            
            # Check expected elements for subject diversity tests
            elements_found = 0
            if 'expected_elements' in test_case:
                feedback_lower = result['feedback'].lower()
                elements_found = sum(
                    1 for elem in test_case['expected_elements']
                    if elem.lower() in feedback_lower
                )
                print(f"✓ Expected Elements: {elements_found}/{len(test_case['expected_elements'])}")
            
            # Collect result data
            test_result = {
                'timestamp': datetime.now().isoformat(),
                'test_id': test_case['test_id'],
                'test_type': test_type,
                'category': test_case['category'],
                'subject': test_case['teacher_profile']['subject'],
                'grade_level': test_case['teacher_profile']['grade_level'],
                'reflection_length': len(test_case['reflection']),
                'feedback_length': len(result['feedback']),
                'execution_time': round(execution_time, 2),
                'cost_estimate': result.get('cost_estimate', 0),
                'chunks_retrieved': result.get('chunks_used', 0),
                'elements_found': f"{elements_found}/{len(test_case.get('expected_elements', []))}" if 'expected_elements' in test_case else 'N/A',
                'status': 'SUCCESS'
            }
            
            self.results.append(test_result)
            print(f"\n✅ Test {test_case['test_id']} PASSED")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"\n❌ Test {test_case['test_id']} FAILED: {str(e)}")
            
            test_result = {
                'timestamp': datetime.now().isoformat(),
                'test_id': test_case['test_id'],
                'test_type': test_type,
                'category': test_case['category'],
                'subject': test_case['teacher_profile']['subject'],
                'grade_level': test_case['teacher_profile'].get('grade_level', 'N/A'),
                'execution_time': round(execution_time, 2),
                'status': 'FAILED',
                'error': str(e)[:200]  # Truncate long errors
            }
            
            self.results.append(test_result)
            return None
    
    def run_suite(self, test_selection='all'):
        """Run test suite with specified selection"""
        print("\n" + "="*70)
        print("RAG SYSTEM TEST SUITE - PHASE 2D")
        print("UNESCO AI Teacher Professional Development Platform")
        print("="*70)
        
        total_tests = 0
        
        if test_selection in ['all', 'subject']:
            print(f"\n📊 Running Subject Diversity Tests ({len(SUBJECT_DIVERSITY_TESTS)} tests)...")
            for test_case in SUBJECT_DIVERSITY_TESTS:
                self.run_test(test_case, 'subject_diversity')
                total_tests += 1
                time.sleep(1)  # Brief pause between tests
        
        if test_selection in ['all', 'edge']:
            print(f"\n⚠️  Running Edge Case Tests ({len(EDGE_CASE_TESTS)} tests)...")
            for test_case in EDGE_CASE_TESTS:
                self.run_test(test_case, 'edge_case')
                total_tests += 1
                time.sleep(1)
        
        if test_selection == 'quick':
            print(f"\n🚀 Running Quick Validation ({len(QUICK_VALIDATION_TESTS)} tests)...")
            for test_case in QUICK_VALIDATION_TESTS:
                test_type = 'subject_diversity' if test_case['test_id'].startswith('SD') else 'edge_case'
                self.run_test(test_case, test_type)
                total_tests += 1
                time.sleep(1)
        
        print(f"\n{'='*70}")
        print(f"Test Suite Complete: {total_tests} tests executed")
        print(f"{'='*70}")
        
        self.save_results()
        self.generate_summary()
    
    def run_single_test(self, test_id):
        """Run a single test by ID"""
        # Find test case
        test_case = None
        test_type = None
        
        for tc in SUBJECT_DIVERSITY_TESTS:
            if tc['test_id'] == test_id:
                test_case = tc
                test_type = 'subject_diversity'
                break
        
        if not test_case:
            for tc in EDGE_CASE_TESTS:
                if tc['test_id'] == test_id:
                    test_case = tc
                    test_type = 'edge_case'
                    break
        
        if not test_case:
            print(f"❌ Test ID '{test_id}' not found!")
            print(f"Available tests: {', '.join([t['test_id'] for t in SUBJECT_DIVERSITY_TESTS + EDGE_CASE_TESTS])}")
            return
        
        print(f"\n🎯 Running single test: {test_id}")
        self.run_test(test_case, test_type)
        self.save_results()
        self.generate_summary()
    
    def save_results(self):
        """Save detailed results to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.output_dir / f"rag_test_results_{timestamp}.csv"
        
        if not self.results:
            print("\n⚠️  No results to save")
            return
        
        fieldnames = list(self.results[0].keys())
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"\n💾 Results saved to: {csv_path}")
        return csv_path
    
    def generate_summary(self):
        """Generate summary statistics"""
        if not self.results:
            return
        
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] == 'SUCCESS')
        failed = total - successful
        
        print(f"\n📊 Execution Statistics:")
        print(f"  Total Tests: {total}")
        print(f"  Successful: {successful} ({successful/total*100:.1f}%)")
        print(f"  Failed: {failed} ({failed/total*100:.1f}%)")
        
        successful_results = [r for r in self.results if r['status'] == 'SUCCESS']
        
        if successful_results:
            avg_time = sum(r['execution_time'] for r in successful_results) / len(successful_results)
            total_cost = sum(r.get('cost_estimate', 0) for r in successful_results)
            
            print(f"\n⚡ Performance Metrics:")
            print(f"  Average Execution Time: {avg_time:.2f}s")
            print(f"  Total Cost: €{total_cost:.6f}")
            print(f"  Average Cost per Query: €{total_cost/len(successful_results):.6f}")
            
            # Subject breakdown
            subjects = {}
            for r in successful_results:
                subj = r.get('subject', 'Unknown')
                if subj not in subjects:
                    subjects[subj] = {'count': 0, 'avg_time': 0}
                subjects[subj]['count'] += 1
                subjects[subj]['avg_time'] += r['execution_time']
            
            if subjects:
                print(f"\n🎯 Subject Coverage:")
                for subj, data in sorted(subjects.items()):
                    avg_t = data['avg_time'] / data['count']
                    print(f"  {subj}: {data['count']} test(s), avg {avg_t:.2f}s")
        
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for r in self.results:
                if r['status'] == 'FAILED':
                    print(f"  {r['test_id']}: {r.get('error', 'Unknown error')[:100]}")
        
        print("\n" + "="*70)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main test execution with CLI arguments"""
    parser = argparse.ArgumentParser(
        description='RAG System Test Suite - Phase 2D',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_rag_phase2d.py                    # Run all tests
  python test_rag_phase2d.py --subject-only     # Subject diversity only
  python test_rag_phase2d.py --edge-only        # Edge cases only
  python test_rag_phase2d.py --quick            # Quick validation
  python test_rag_phase2d.py --test SD01        # Single test
        """
    )
    
    parser.add_argument('--subject-only', action='store_true',
                       help='Run only subject diversity tests')
    parser.add_argument('--edge-only', action='store_true',
                       help='Run only edge case tests')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick validation (2 tests)')
    parser.add_argument('--test', type=str,
                       help='Run specific test by ID (e.g., SD01)')
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  RAG SYSTEM TEST SUITE - PHASE 2D                           ║
    ║  UNESCO AI Teacher Professional Development Platform        ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize test suite
    suite = RAGTestSuite()
    
    # Determine test selection
    if args.test:
        suite.run_single_test(args.test)
    elif args.quick:
        suite.run_suite('quick')
    elif args.subject_only:
        suite.run_suite('subject')
    elif args.edge_only:
        suite.run_suite('edge')
    else:
        suite.run_suite('all')
    
    print("\n✅ Testing complete! Check test_results/ directory for detailed CSV output.")
    print("📊 Import CSV into Excel/Google Sheets for analysis.")

if __name__ == "__main__":
    main()
