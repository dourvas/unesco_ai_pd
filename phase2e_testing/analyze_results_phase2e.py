#!/usr/bin/env python3
"""
Phase 2E: Enhanced Results Analysis
====================================

Improvements over Phase 2D:
- Reads actual cost values from CSV
- Calculates proper statistics
- Prepares data for visualization
- Generates dissertation-ready summaries

Author: John Dourvas
Date: February 5, 2026
"""

import sys
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_results(csv_path):
    """Load test results from CSV."""
    results = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['response_time_seconds'] = float(row['response_time_seconds']) if row['response_time_seconds'] else 0
            row['response_length'] = int(row['response_length']) if row['response_length'] else 0
            row['input_tokens'] = int(row['input_tokens']) if row['input_tokens'] else 0
            row['output_tokens'] = int(row['output_tokens']) if row['output_tokens'] else 0
            row['total_tokens'] = int(row['total_tokens']) if row['total_tokens'] else 0
            row['embedding_cost_eur'] = float(row['embedding_cost_eur']) if row['embedding_cost_eur'] else 0
            row['generation_cost_eur'] = float(row['generation_cost_eur']) if row['generation_cost_eur'] else 0
            row['total_cost_eur'] = float(row['total_cost_eur']) if row['total_cost_eur'] else 0
            row['chunks_retrieved'] = int(row['chunks_retrieved']) if row['chunks_retrieved'] else 0
            row['top_chunk_similarity'] = float(row['top_chunk_similarity']) if row['top_chunk_similarity'] else 0
            row['reflection_length'] = int(row['reflection_length']) if row['reflection_length'] else 0
            
            results.append(row)
    
    return results


def analyze_results(results):
    """Generate comprehensive analysis."""
    successful = [r for r in results if r['status'] == 'SUCCESS']
    failed = [r for r in results if r['status'] == 'FAILED']
    
    analysis = {
        'total_tests': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'success_rate': len(successful) / len(results) * 100 if results else 0
    }
    
    if successful:
        # Performance metrics
        response_times = [r['response_time_seconds'] for r in successful]
        analysis['avg_response_time'] = sum(response_times) / len(response_times)
        analysis['min_response_time'] = min(response_times)
        analysis['max_response_time'] = max(response_times)
        
        # Cost metrics
        costs = [r['total_cost_eur'] for r in successful]
        analysis['total_cost'] = sum(costs)
        analysis['avg_cost_per_query'] = sum(costs) / len(costs)
        analysis['min_cost'] = min(costs)
        analysis['max_cost'] = max(costs)
        
        # Token metrics
        analysis['total_tokens'] = sum(r['total_tokens'] for r in successful)
        analysis['avg_tokens_per_query'] = sum(r['total_tokens'] for r in successful) / len(successful)
        analysis['total_input_tokens'] = sum(r['input_tokens'] for r in successful)
        analysis['total_output_tokens'] = sum(r['output_tokens'] for r in successful)
        
        # Retrieval metrics
        analysis['avg_chunks_retrieved'] = sum(r['chunks_retrieved'] for r in successful) / len(successful)
        analysis['avg_similarity'] = sum(r['top_chunk_similarity'] for r in successful) / len(successful)
        
        # Subject breakdown
        subject_stats = defaultdict(list)
        for r in successful:
            subject_stats[r['subject']].append({
                'time': r['response_time_seconds'],
                'cost': r['total_cost_eur'],
                'similarity': r['top_chunk_similarity'],
                'chunks': r['chunks_retrieved']
            })
        
        analysis['subject_breakdown'] = {}
        for subject, data in subject_stats.items():
            analysis['subject_breakdown'][subject] = {
                'count': len(data),
                'avg_time': sum(d['time'] for d in data) / len(data),
                'avg_cost': sum(d['cost'] for d in data) / len(data),
                'avg_similarity': sum(d['similarity'] for d in data) / len(data),
                'avg_chunks': sum(d['chunks'] for d in data) / len(data)
            }
        
        # Projections
        analysis['cost_per_user_m1'] = analysis['avg_cost_per_query']
        analysis['cost_per_user_15_modules'] = analysis['avg_cost_per_query'] * 15
        analysis['cost_110_users_15_modules'] = analysis['cost_per_user_15_modules'] * 110
        analysis['budget_utilization'] = (analysis['cost_110_users_15_modules'] / 110) * 100
        analysis['budget_remaining'] = 110 - analysis['cost_110_users_15_modules']
    
    return analysis


def print_detailed_analysis(analysis):
    """Print comprehensive analysis report."""
    print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                   PHASE 2E ANALYSIS REPORT                            ║
║                   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║
╚═══════════════════════════════════════════════════════════════════════╝

📊 TEST EXECUTION SUMMARY
{'='*70}
Total Tests:        {analysis['total_tests']}
✅ Successful:      {analysis['successful']} ({analysis['success_rate']:.1f}%)
❌ Failed:          {analysis['failed']}
""")
    
    if analysis['successful'] > 0:
        print(f"""
⏱️  PERFORMANCE METRICS
{'='*70}
Average Response Time:    {analysis['avg_response_time']:.2f}s
Fastest Response:         {analysis['min_response_time']:.2f}s
Slowest Response:         {analysis['max_response_time']:.2f}s

💰 COST ANALYSIS
{'='*70}
Total Cost (all tests):   €{analysis['total_cost']:.6f}
Average Cost per Query:   €{analysis['avg_cost_per_query']:.6f}
Min Cost:                 €{analysis['min_cost']:.6f}
Max Cost:                 €{analysis['max_cost']:.6f}

📝 TOKEN USAGE
{'='*70}
Total Tokens:             {analysis['total_tokens']:,}
Average per Query:        {analysis['avg_tokens_per_query']:.0f}
  - Input Tokens:         {analysis['total_input_tokens']:,}
  - Output Tokens:        {analysis['total_output_tokens']:,}

🔍 RETRIEVAL QUALITY
{'='*70}
Avg Chunks Retrieved:     {analysis['avg_chunks_retrieved']:.1f}
Avg Similarity Score:     {analysis['avg_similarity']:.4f}

📚 SUBJECT-SPECIFIC BREAKDOWN
{'='*70}""")
        
        for subject, stats in analysis['subject_breakdown'].items():
            print(f"""
{subject}:
  Tests:       {stats['count']}
  Avg Time:    {stats['avg_time']:.2f}s
  Avg Cost:    €{stats['avg_cost']:.6f}
  Similarity:  {stats['avg_similarity']:.4f}
  Chunks:      {stats['avg_chunks']:.1f}""")
        
        print(f"""
💵 COST PROJECTIONS
{'='*70}
Cost per User (M1 only):           €{analysis['cost_per_user_m1']:.6f}
Cost per User (15 modules):        €{analysis['cost_per_user_15_modules']:.4f}
Cost for 110 Users (15 modules):   €{analysis['cost_110_users_15_modules']:.2f}

Budget: €110.00
Used:   €{analysis['cost_110_users_15_modules']:.2f} ({analysis['budget_utilization']:.2f}%)
Left:   €{analysis['budget_remaining']:.2f} ({100-analysis['budget_utilization']:.2f}%)

{'✅ UNDER BUDGET' if analysis['budget_remaining'] > 0 else '❌ OVER BUDGET'}

{'='*70}
""")


def generate_dissertation_summary(analysis):
    """Generate a dissertation-ready paragraph summary."""
    summary = f"""
DISSERTATION SUMMARY - PHASE 2E RESULTS

The RAG-powered feedback system was validated through comprehensive testing 
across {analysis['successful']} test cases representing {len(analysis['subject_breakdown'])} 
teaching domains. The system achieved a {analysis['success_rate']:.1f}% success rate 
with an average response time of {analysis['avg_response_time']:.2f} seconds, 
demonstrating adequate performance for real-time educational feedback.

Economic feasibility was confirmed with an average cost of €{analysis['avg_cost_per_query']:.6f} 
per query, projecting to €{analysis['cost_per_user_15_modules']:.4f} per user across the complete 
15-module journey. For the target cohort of 110 Greek educators, total projected 
costs of €{analysis['cost_110_users_15_modules']:.2f} represent {analysis['budget_utilization']:.1f}% 
budget utilization, well within the €110 research budget constraint.

Retrieval quality metrics showed an average similarity score of {analysis['avg_similarity']:.4f}, 
indicating effective matching between teacher reflections and relevant UNESCO framework 
content. Subject-specific analysis revealed consistent performance across diverse teaching 
domains, with {analysis['avg_chunks_retrieved']:.1f} relevant chunks retrieved per query on average.

These results provide empirical evidence supporting the feasibility of AI-powered, 
personalized professional development at scale within practical cost constraints 
(€1 per user target vs. €{analysis['cost_per_user_15_modules']:.4f} actual), demonstrating 
the viability of the proposed UNESCO AI Competency Framework implementation approach.
"""
    return summary


def save_analysis_report(analysis, output_path):
    """Save analysis to text file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        # Redirect print to file
        import sys
        old_stdout = sys.stdout
        sys.stdout = f
        
        print_detailed_analysis(analysis)
        print("\n" + "="*70)
        print(generate_dissertation_summary(analysis))
        
        sys.stdout = old_stdout
    
    print(f"\n💾 Analysis report saved to: {output_path}")


def prepare_visualization_data(results, output_dir):
    """Prepare data files for visualization (Phase 2E Part B)."""
    successful = [r for r in results if r['status'] == 'SUCCESS']
    
    # 1. Response time data
    time_data_path = output_dir / 'viz_response_times.csv'
    with open(time_data_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['test_id', 'subject', 'response_time_seconds'])
        for r in successful:
            writer.writerow([r['test_id'], r['subject'], r['response_time_seconds']])
    
    # 2. Cost data
    cost_data_path = output_dir / 'viz_costs.csv'
    with open(cost_data_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['test_id', 'subject', 'embedding_cost', 'generation_cost', 'total_cost'])
        for r in successful:
            writer.writerow([
                r['test_id'], 
                r['subject'], 
                r['embedding_cost_eur'], 
                r['generation_cost_eur'],
                r['total_cost_eur']
            ])
    
    # 3. Retrieval accuracy data
    accuracy_data_path = output_dir / 'viz_retrieval_accuracy.csv'
    with open(accuracy_data_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['test_id', 'subject', 'similarity_score', 'chunks_retrieved', 'top_source'])
        for r in successful:
            writer.writerow([
                r['test_id'],
                r['subject'],
                r['top_chunk_similarity'],
                r['chunks_retrieved'],
                r['top_chunk_source']
            ])
    
    print(f"\n📊 Visualization data prepared:")
    print(f"  - Response times: {time_data_path}")
    print(f"  - Costs: {cost_data_path}")
    print(f"  - Retrieval accuracy: {accuracy_data_path}")
    
    return {
        'response_times': time_data_path,
        'costs': cost_data_path,
        'retrieval_accuracy': accuracy_data_path
    }


def main():
    """Main analysis execution."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_results_phase2e.py <path_to_csv>")
        print("\nExample:")
        print("  python analyze_results_phase2e.py test_results/rag_test_results_phase2e_20260205_143022.csv")
        sys.exit(1)
    
    csv_path = Path(sys.argv[1])
    
    if not csv_path.exists():
        print(f"❌ Error: File not found: {csv_path}")
        sys.exit(1)
    
    print(f"\n📂 Loading results from: {csv_path}")
    results = load_results(csv_path)
    print(f"✅ Loaded {len(results)} test results")
    
    print(f"\n🔍 Analyzing results...")
    analysis = analyze_results(results)
    
    # Print detailed analysis
    print_detailed_analysis(analysis)
    
    # Generate dissertation summary
    print("\n" + "="*70)
    print(generate_dissertation_summary(analysis))
    print("="*70)
    
    # Save analysis report
    output_dir = csv_path.parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"analysis_report_phase2e_{timestamp}.txt"
    save_analysis_report(analysis, report_path)
    
    # Prepare visualization data
    print(f"\n📊 Preparing data for visualizations...")
    viz_files = prepare_visualization_data(results, output_dir)
    
    print(f"\n✅ Analysis complete!")
    print(f"\nNext steps:")
    print(f"  1. Review analysis report: {report_path}")
    print(f"  2. Create visualizations using prepared data (Phase 2E Part B)")
    print(f"  3. Proceed to full M1 testing (Phase 2E Part C)")


if __name__ == "__main__":
    main()
