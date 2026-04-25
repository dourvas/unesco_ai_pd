# Phase 2E: RAG System Refinements

## Overview

Phase 2E improves upon Phase 2D testing with enhanced CSV export, proper cost tracking, and visualization preparation.

## Improvements Over Phase 2D

### ✅ Fixed Issues
1. **CSV Export Now Includes Actual Costs**
   - `embedding_cost_eur` - actual cost from Gemini API
   - `generation_cost_eur` - actual cost from Gemini API
   - `total_cost_eur` - sum of both costs
   
2. **Better Column Naming**
   - Clear, analysis-friendly column names
   - Proper data types for all metrics
   
3. **Token Usage Tracking**
   - `input_tokens` - tokens in query
   - `output_tokens` - tokens in response
   - `total_tokens` - sum of both

4. **Enhanced Error Reporting**
   - Detailed error messages in CSV
   - Status field for each test

### 🆕 New Features

1. **Visualization Data Preparation**
   - Separate CSV files for each viz type
   - Ready for matplotlib/plotly
   
2. **Dissertation-Ready Summaries**
   - Auto-generated research paragraph
   - Statistical analysis for methodology chapter

3. **Subject-Specific Breakdown**
   - Performance by teaching domain
   - Cost analysis per subject

## Files

```
phase2e_testing/
├── test_rag_phase2e.py           # Main test script (improved)
├── analyze_results_phase2e.py     # Analysis script (improved)
├── README_PHASE2E.md              # This file
└── test_results/                  # Output directory
    ├── rag_test_results_phase2e_*.csv
    ├── analysis_report_phase2e_*.txt
    ├── viz_response_times.csv
    ├── viz_costs.csv
    └── viz_retrieval_accuracy.csv
```

## Usage

### Step 1: Run Tests

```bash
# Navigate to project
cd /path/to/unesco_ai_pd

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows

# Ensure PostgreSQL is running
docker ps | grep postgres-unesco

# Run tests
python test_rag_phase2e.py
```

**Expected Output:**
- Console output showing each test
- CSV file in `test_results/` directory
- ~3-4 minutes for complete test suite

### Step 2: Analyze Results

```bash
# Run analysis on the generated CSV
python analyze_results_phase2e.py test_results/rag_test_results_phase2e_20260205_143022.csv
```

**Expected Output:**
- Detailed analysis printed to console
- Analysis report saved as `.txt` file
- Three visualization data files created

### Step 3: Review Results

1. **CSV File** (`rag_test_results_phase2e_*.csv`)
   - Open in Excel/Google Sheets
   - All metrics with actual values
   - Ready for statistical analysis

2. **Analysis Report** (`analysis_report_phase2e_*.txt`)
   - Comprehensive statistics
   - Dissertation-ready paragraph
   - Subject breakdowns

3. **Visualization Data** (3 CSV files)
   - `viz_response_times.csv` - for time analysis charts
   - `viz_costs.csv` - for cost breakdown charts
   - `viz_retrieval_accuracy.csv` - for quality metrics charts

## CSV Schema

### Main Results File

| Column | Type | Description |
|--------|------|-------------|
| test_id | string | Test case identifier (TC01-TC10) |
| test_name | string | Descriptive test name |
| subject | string | Teaching subject |
| grade_level | string | Target grade level |
| reflection_length | int | Characters in reflection |
| expected_quality | string | Expected quality level |
| status | string | SUCCESS or FAILED |
| response_time_seconds | float | **Total response time** |
| response_length | int | Characters in feedback |
| input_tokens | int | **Tokens in input** |
| output_tokens | int | **Tokens in output** |
| total_tokens | int | **Total tokens used** |
| embedding_cost_eur | float | **Actual embedding cost (€)** |
| generation_cost_eur | float | **Actual generation cost (€)** |
| total_cost_eur | float | **Actual total cost (€)** |
| chunks_retrieved | int | Number of chunks retrieved |
| top_chunk_source | string | Source of best match |
| top_chunk_similarity | float | Similarity score (0-1) |
| query_id | int | Database query ID |
| error | string | Error message (if failed) |

## Key Metrics

### Performance
- **Target:** <20s average response time
- **Actual:** ~11-12s (from Phase 2D)

### Cost
- **Target:** <€0.0002 per query
- **Actual:** ~€0.00014 (from Phase 2D)
- **Projection:** €0.0021 per user (15 modules)
- **110 users:** ~€0.23 (0.2% of €110 budget)

### Quality
- **Success Rate:** 100% (10/10 tests)
- **Avg Similarity:** ~0.75-0.85
- **Chunks Retrieved:** 3-5 per query

## Next Steps

After completing Phase 2E Part A (this):

### Part B: Create Visualizations
- Use `viz_*.csv` files to create charts
- Response time distribution
- Cost breakdown by component
- Retrieval accuracy by subject

### Part C: Full M1 Module Testing
- Test complete user journey
- Onboarding → Tab 1-5 flow
- Real teacher scenarios
- Quality assessment

## Troubleshooting

### Issue: Import errors
**Solution:** Ensure you're in the correct directory and virtual environment is activated

### Issue: Database connection failed
**Solution:** Check PostgreSQL container is running:
```bash
docker ps | grep postgres-unesco
docker start postgres-unesco  # if not running
```

### Issue: No results in CSV
**Solution:** Check console output for errors, ensure RAG system is properly configured

## Cost Tracking Notes

The cost calculations use Gemini's pricing:
- **Embeddings:** text-embedding-004
  - Input: €0.00001 per 1K tokens
  
- **Generation:** gemini-2.5-flash
  - Input: €0.000075 per 1K tokens
  - Output: €0.00030 per 1K tokens

These are fetched from the RAG system response and stored accurately in the CSV.

## Research Value

This testing provides:

1. **Empirical Validation**
   - System works across diverse subjects
   - Performance metrics documented
   - Cost feasibility proven

2. **Dissertation Evidence**
   - Statistical analysis ready
   - Tables for methodology chapter
   - Reproducible results

3. **Design Insights**
   - Subject-specific patterns
   - Cost-performance tradeoffs
   - Quality metrics baseline

## Status

- ✅ **Part A: CSV Export Fix** - READY TO TEST
- ⏳ **Part B: Visualizations** - NEXT
- ⏳ **Part C: Full M1 Testing** - AFTER B

---

**Created:** February 5, 2026  
**Author:** John Dourvas  
**Version:** 1.0
