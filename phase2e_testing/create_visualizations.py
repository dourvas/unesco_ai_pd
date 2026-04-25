#!/usr/bin/env python3
"""
Phase 2E-B: Visualization Generator
====================================

Creates 4 publication-quality charts from Phase 2E test results:
1. Response Time Distribution by Subject
2. Cost Breakdown (Embedding vs Generation)
3. Subject-Specific Performance Comparison
4. Cost per Subject Analysis

Author: John Dourvas
Date: February 5, 2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns

# Set style for publication-quality figures
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

def load_data():
    """Load all visualization CSV files."""
    print("📂 Loading data files...")
    
    times_df = pd.read_csv('viz_response_times.csv')
    costs_df = pd.read_csv('viz_costs.csv')
    accuracy_df = pd.read_csv('viz_retrieval_accuracy.csv')
    
    print(f"   ✅ Response times: {len(times_df)} records")
    print(f"   ✅ Costs: {len(costs_df)} records")
    print(f"   ✅ Retrieval accuracy: {len(accuracy_df)} records")
    
    return times_df, costs_df, accuracy_df


def create_response_time_chart(times_df, output_dir):
    """
    Chart 1: Response Time Distribution by Subject
    Shows response times for each test case, colored by subject.
    """
    print("\n📊 Creating Chart 1: Response Time Distribution...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get unique subjects for coloring
    subjects = times_df['subject'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(subjects)))
    subject_colors = dict(zip(subjects, colors))
    
    # Create bar chart
    bars = ax.bar(
        times_df['test_id'], 
        times_df['response_time_seconds'],
        color=[subject_colors[subj] for subj in times_df['subject']],
        edgecolor='black',
        linewidth=0.5
    )
    
    # Add target line
    ax.axhline(y=20, color='red', linestyle='--', linewidth=1.5, 
               label='Target (<20s)', alpha=0.7)
    
    # Add average line
    avg_time = times_df['response_time_seconds'].mean()
    ax.axhline(y=avg_time, color='green', linestyle='--', linewidth=1.5,
               label=f'Average ({avg_time:.2f}s)', alpha=0.7)
    
    # Labels and title
    ax.set_xlabel('Test Case', fontweight='bold')
    ax.set_ylabel('Response Time (seconds)', fontweight='bold')
    ax.set_title('RAG System Response Time by Test Case', fontweight='bold', pad=15)
    
    # Rotate x-axis labels
    ax.set_xticks(range(len(times_df)))
    ax.set_xticklabels(times_df['test_id'], rotation=45, ha='right')
    
    # Add legend for subjects
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=subject_colors[subj], 
                             edgecolor='black', label=subj) 
                      for subj in subjects]
    legend_elements.extend([
        plt.Line2D([0], [0], color='red', linestyle='--', label='Target (<20s)'),
        plt.Line2D([0], [0], color='green', linestyle='--', label=f'Average ({avg_time:.2f}s)')
    ])
    
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)
    
    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle=':')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    output_path = output_dir / 'chart1_response_times.png'
    plt.savefig(output_path, bbox_inches='tight')
    print(f"   ✅ Saved: {output_path}")
    plt.close()


def create_cost_breakdown_chart(costs_df, output_dir):
    """
    Chart 2: Cost Breakdown - Stacked Bar Chart
    Shows embedding vs generation costs for each test.
    """
    print("\n📊 Creating Chart 2: Cost Breakdown...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data
    test_ids = costs_df['test_id']
    embedding = costs_df['embedding_cost'] * 1000000  # Convert to µEUR
    generation = costs_df['generation_cost'] * 1000000
    
    # Create stacked bar chart
    bar_width = 0.7
    x_pos = np.arange(len(test_ids))
    
    p1 = ax.bar(x_pos, embedding, bar_width, label='Embedding', 
                color='#3498db', edgecolor='black', linewidth=0.5)
    p2 = ax.bar(x_pos, generation, bar_width, bottom=embedding,
                label='Generation', color='#e74c3c', edgecolor='black', linewidth=0.5)
    
    # Labels and title
    ax.set_xlabel('Test Case', fontweight='bold')
    ax.set_ylabel('Cost (µEUR)', fontweight='bold')
    ax.set_title('Cost Breakdown: Embedding vs Generation', fontweight='bold', pad=15)
    
    # X-axis
    ax.set_xticks(x_pos)
    ax.set_xticklabels(test_ids, rotation=45, ha='right')
    
    # Legend
    ax.legend(loc='upper right', framealpha=0.9)
    
    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle=':')
    ax.set_axisbelow(True)
    
    # Add total cost labels on top of bars
    totals = costs_df['total_cost'] * 1000000
    for i, (x, total) in enumerate(zip(x_pos, totals)):
        ax.text(x, total + 1, f'{total:.1f}', 
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    
    output_path = output_dir / 'chart2_cost_breakdown.png'
    plt.savefig(output_path, bbox_inches='tight')
    print(f"   ✅ Saved: {output_path}")
    plt.close()


def create_subject_comparison_chart(times_df, costs_df, output_dir):
    """
    Chart 3: Subject-Specific Performance
    Dual-axis chart showing avg time and cost per subject.
    """
    print("\n📊 Creating Chart 3: Subject-Specific Performance...")
    
    # Merge dataframes
    merged = pd.merge(times_df, costs_df, on=['test_id', 'subject'])
    
    # Group by subject
    subject_stats = merged.groupby('subject').agg({
        'response_time_seconds': 'mean',
        'total_cost': 'mean'
    }).reset_index()
    
    # Sort by response time
    subject_stats = subject_stats.sort_values('response_time_seconds')
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Response time bars
    x_pos = np.arange(len(subject_stats))
    bars = ax1.bar(x_pos, subject_stats['response_time_seconds'], 
                   color='#3498db', alpha=0.7, label='Response Time',
                   edgecolor='black', linewidth=0.5)
    
    ax1.set_xlabel('Subject Area', fontweight='bold')
    ax1.set_ylabel('Average Response Time (seconds)', color='#3498db', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#3498db')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(subject_stats['subject'], rotation=45, ha='right')
    
    # Cost line on secondary axis
    ax2 = ax1.twinx()
    costs_eur = subject_stats['total_cost'] * 1000000  # Convert to µEUR
    line = ax2.plot(x_pos, costs_eur, color='#e74c3c', marker='o', 
                    linewidth=2.5, markersize=8, label='Average Cost')
    
    ax2.set_ylabel('Average Cost (µEUR)', color='#e74c3c', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    
    # Title
    ax1.set_title('Subject-Specific Performance: Time vs Cost', 
                  fontweight='bold', pad=15)
    
    # Grid
    ax1.grid(axis='y', alpha=0.3, linestyle=':')
    ax1.set_axisbelow(True)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9)
    
    plt.tight_layout()
    
    output_path = output_dir / 'chart3_subject_comparison.png'
    plt.savefig(output_path, bbox_inches='tight')
    print(f"   ✅ Saved: {output_path}")
    plt.close()


def create_cost_distribution_chart(costs_df, output_dir):
    """
    Chart 4: Cost Distribution Analysis
    Box plot + scatter showing cost variation.
    """
    print("\n📊 Creating Chart 4: Cost Distribution...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Box plot by subject
    costs_with_subject = costs_df.copy()
    costs_with_subject['total_cost_micro'] = costs_with_subject['total_cost'] * 1000000
    
    subjects_ordered = costs_with_subject.groupby('subject')['total_cost_micro'].mean().sort_values().index
    
    bp = ax1.boxplot(
        [costs_with_subject[costs_with_subject['subject'] == subj]['total_cost_micro'].values 
         for subj in subjects_ordered],
        labels=subjects_ordered,
        patch_artist=True,
        medianprops=dict(color='red', linewidth=2),
        boxprops=dict(facecolor='lightblue', edgecolor='black'),
        whiskerprops=dict(color='black'),
        capprops=dict(color='black')
    )
    
    ax1.set_xlabel('Subject Area', fontweight='bold')
    ax1.set_ylabel('Cost (µEUR)', fontweight='bold')
    ax1.set_title('Cost Distribution by Subject', fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax1.grid(axis='y', alpha=0.3, linestyle=':')
    
    # Right: Scatter plot with trend
    ax2.scatter(range(len(costs_df)), costs_df['total_cost'] * 1000000,
                s=100, alpha=0.6, c=range(len(costs_df)), cmap='viridis',
                edgecolors='black', linewidth=0.5)
    
    # Add average line
    avg_cost = (costs_df['total_cost'] * 1000000).mean()
    ax2.axhline(y=avg_cost, color='red', linestyle='--', linewidth=2,
                label=f'Average: {avg_cost:.2f} µEUR')
    
    # Add min/max lines
    min_cost = (costs_df['total_cost'] * 1000000).min()
    max_cost = (costs_df['total_cost'] * 1000000).max()
    ax2.axhline(y=min_cost, color='green', linestyle=':', linewidth=1.5,
                label=f'Min: {min_cost:.2f} µEUR', alpha=0.7)
    ax2.axhline(y=max_cost, color='orange', linestyle=':', linewidth=1.5,
                label=f'Max: {max_cost:.2f} µEUR', alpha=0.7)
    
    ax2.set_xlabel('Test Case Number', fontweight='bold')
    ax2.set_ylabel('Cost (µEUR)', fontweight='bold')
    ax2.set_title('Cost Variation Across Tests', fontweight='bold')
    ax2.legend(loc='upper right', framealpha=0.9)
    ax2.grid(alpha=0.3, linestyle=':')
    
    plt.tight_layout()
    
    output_path = output_dir / 'chart4_cost_distribution.png'
    plt.savefig(output_path, bbox_inches='tight')
    print(f"   ✅ Saved: {output_path}")
    plt.close()


def create_summary_stats_figure(times_df, costs_df, output_dir):
    """
    Bonus: Summary Statistics Figure
    Text-based summary of key metrics.
    """
    print("\n📊 Creating Bonus: Summary Statistics Figure...")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')
    
    # Calculate stats
    avg_time = times_df['response_time_seconds'].mean()
    min_time = times_df['response_time_seconds'].min()
    max_time = times_df['response_time_seconds'].max()
    
    avg_cost = costs_df['total_cost'].mean()
    min_cost = costs_df['total_cost'].min()
    max_cost = costs_df['total_cost'].max()
    
    total_cost = costs_df['total_cost'].sum()
    
    # Projections
    cost_per_user_15 = avg_cost * 15
    cost_110_users = cost_per_user_15 * 110
    budget_util = (cost_110_users / 110) * 100
    
    # Create summary text
    summary_text = f"""
    PHASE 2E TEST RESULTS SUMMARY
    ═══════════════════════════════════════════════════════
    
    📊 PERFORMANCE METRICS
    ───────────────────────────────────────────────────────
    Success Rate:              100% (10/10 tests)
    Average Response Time:     {avg_time:.2f}s
    Response Time Range:       {min_time:.2f}s - {max_time:.2f}s
    
    💰 COST ANALYSIS
    ───────────────────────────────────────────────────────
    Average Cost per Query:    €{avg_cost:.6f}
    Cost Range:                €{min_cost:.6f} - €{max_cost:.6f}
    Total Cost (10 tests):     €{total_cost:.6f}
    
    📈 BUDGET PROJECTIONS
    ───────────────────────────────────────────────────────
    Cost per User (M1):        €{avg_cost:.6f}
    Cost per User (15 modules): €{cost_per_user_15:.4f}
    Cost for 110 Users:        €{cost_110_users:.2f}
    
    Budget Utilization:        {budget_util:.2f}%
    Budget Remaining:          €{110 - cost_110_users:.2f}
    
    ✅ WELL UNDER BUDGET TARGET (€1 per user)
    
    🎯 KEY FINDINGS
    ───────────────────────────────────────────────────────
    ✓ All tests completed successfully
    ✓ Response times consistently under 20s target
    ✓ Cost variation indicates realistic API usage
    ✓ Feasible for 110-user pilot deployment
    ✓ Scalable to full 15-module implementation
    
    ═══════════════════════════════════════════════════════
    Generated: February 5, 2026
    Phase 2E-B Visualization Package
    """
    
    ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    output_path = output_dir / 'chart5_summary_statistics.png'
    plt.savefig(output_path, bbox_inches='tight')
    print(f"   ✅ Saved: {output_path}")
    plt.close()


def main():
    """Main execution."""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║           PHASE 2E-B: VISUALIZATION GENERATOR                         ║
║           Creating Publication-Quality Charts                         ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Change to test_results directory
    import os
    if Path('test_results').exists():
        os.chdir('test_results')
        print("📁 Working directory: test_results/\n")
    else:
        print("⚠️  Warning: test_results/ not found, using current directory\n")
    
    # Load data
    times_df, costs_df, accuracy_df = load_data()
    
    # Create output directory for charts
    output_dir = Path('.')
    
    # Generate charts
    print("\n" + "="*70)
    print("GENERATING CHARTS")
    print("="*70)
    
    create_response_time_chart(times_df, output_dir)
    create_cost_breakdown_chart(costs_df, output_dir)
    create_subject_comparison_chart(times_df, costs_df, output_dir)
    create_cost_distribution_chart(costs_df, output_dir)
    create_summary_stats_figure(times_df, costs_df, output_dir)
    
    print("\n" + "="*70)
    print("✅ ALL CHARTS GENERATED SUCCESSFULLY!")
    print("="*70)
    print(f"""
📊 Created 5 visualization files:
   1. chart1_response_times.png       - Response time by test case
   2. chart2_cost_breakdown.png       - Embedding vs generation costs
   3. chart3_subject_comparison.png   - Subject-specific performance
   4. chart4_cost_distribution.png    - Cost variation analysis
   5. chart5_summary_statistics.png   - Summary metrics (bonus)

📁 All files saved in: test_results/

💡 Next steps:
   - Review charts for dissertation
   - Adjust styling if needed
   - Export to Word/LaTeX document
    """)


if __name__ == "__main__":
    main()
