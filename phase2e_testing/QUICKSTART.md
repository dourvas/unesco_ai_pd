# Phase 2E Quick Start Guide

## 🚀 Getting Started (Windows)

### Prerequisites
- ✅ PostgreSQL running (Docker container)
- ✅ Virtual environment activated
- ✅ In `unesco_ai_pd` project directory

### Installation

1. **Copy files to your project:**
   ```powershell
   # In your unesco_ai_pd directory
   mkdir phase2e_testing
   # Copy the 3 files here:
   #   - test_rag_phase2e.py
   #   - analyze_results_phase2e.py
   #   - README_PHASE2E.md
   ```

2. **Verify setup:**
   ```powershell
   # Check PostgreSQL
   docker ps | Select-String "postgres-unesco"
   
   # Activate venv
   .\venv\Scripts\Activate.ps1
   
   # Test imports
   python -c "import django; print('Django OK')"
   ```

## 📝 Step-by-Step Execution

### Step 1: Run Tests (~3-4 minutes)

```powershell
# Navigate to test directory
cd phase2e_testing

# Run tests
python test_rag_phase2e.py
```

**What happens:**
1. Runs 10 test cases (8 subjects + 2 edge cases)
2. Calls RAG system for each reflection
3. Tracks response time, tokens, costs
4. Saves results to CSV

**Output location:**
```
phase2e_testing/test_results/rag_test_results_phase2e_YYYYMMDD_HHMMSS.csv
```

### Step 2: Analyze Results (~10 seconds)

```powershell
# Replace with your actual filename
python analyze_results_phase2e.py test_results/rag_test_results_phase2e_20260205_143022.csv
```

**What happens:**
1. Reads CSV with actual costs
2. Calculates statistics
3. Generates dissertation summary
4. Creates visualization data files

**Output files:**
```
test_results/
├── analysis_report_phase2e_YYYYMMDD_HHMMSS.txt
├── viz_response_times.csv
├── viz_costs.csv
└── viz_retrieval_accuracy.csv
```

### Step 3: Review Results

**Open in Excel:**
```
rag_test_results_phase2e_*.csv
```

**Key columns to check:**
- ✅ `total_cost_eur` - Should have actual values (not 0.000136)
- ✅ `embedding_cost_eur` - Split cost component
- ✅ `generation_cost_eur` - Split cost component
- ✅ `total_tokens` - Token usage
- ✅ `response_time_seconds` - Performance

**Read analysis:**
```
analysis_report_phase2e_*.txt
```

Look for:
- Success rate (target: 100%)
- Average cost (target: <€0.0002)
- Average time (target: <20s)
- Budget projections

## ✅ Expected Results (Based on Phase 2D)

### Performance
```
✅ Success Rate: 100% (10/10)
✅ Avg Response Time: ~11.4s
✅ Min Time: ~9s
✅ Max Time: ~14s
```

### Cost (Phase 2E will show actual values)
```
✅ Avg Cost per Query: ~€0.00014
✅ Cost per User (M1): ~€0.00014
✅ Cost per User (15 modules): ~€0.0021
✅ Cost for 110 Users: ~€0.23
✅ Budget Utilization: 0.2%
✅ Budget Remaining: €109.77 (99.8%)
```

### Quality
```
✅ Avg Chunks Retrieved: 3-5
✅ Avg Similarity Score: 0.75-0.85
✅ Subject Coverage: 8 domains
```

## 🐛 Troubleshooting

### Error: ModuleNotFoundError: django
**Fix:**
```powershell
.\venv\Scripts\Activate.ps1  # Make sure venv is active
pip list | Select-String "Django"  # Verify Django installed
```

### Error: Connection refused (PostgreSQL)
**Fix:**
```powershell
docker start postgres-unesco
docker ps  # Verify it's running
```

### Error: No such table: document_chunks
**Fix:**
```powershell
# RAG tables not created, run Phase 2A first
python manage.py shell < setup_rag_tables.py
```

### Error: Permission denied
**Fix:**
```powershell
# Run PowerShell as Administrator, or
# Check file permissions in phase2e_testing/
```

## 📊 What's Fixed in Phase 2E

### Phase 2D Issues ❌
```csv
# Old CSV had:
embedding_cost_eur,generation_cost_eur,total_cost_eur
0.000136,0.000136,0.000136  # Placeholders!
```

### Phase 2E Fixes ✅
```csv
# New CSV has:
embedding_cost_eur,generation_cost_eur,total_cost_eur
0.000010,0.000126,0.000136  # Actual costs!
```

**Why this matters:**
- Accurate budget projections
- Cost optimization insights
- Proper statistical analysis
- Dissertation validity

## 📈 Next Steps After Phase 2E-A

### B) Create Visualizations
Use the prepared CSV files to create:

1. **Response Time Chart**
   ```python
   import pandas as pd
   import matplotlib.pyplot as plt
   
   df = pd.read_csv('test_results/viz_response_times.csv')
   df.plot(x='test_id', y='response_time_seconds', kind='bar')
   plt.title('Response Time by Test Case')
   plt.ylabel('Seconds')
   plt.show()
   ```

2. **Cost Breakdown Chart**
   ```python
   df = pd.read_csv('test_results/viz_costs.csv')
   df.plot(x='test_id', y=['embedding_cost', 'generation_cost'], kind='bar', stacked=True)
   plt.title('Cost Breakdown by Component')
   plt.ylabel('EUR')
   plt.show()
   ```

3. **Retrieval Accuracy Chart**
   ```python
   df = pd.read_csv('test_results/viz_retrieval_accuracy.csv')
   df.plot(x='subject', y='similarity_score', kind='bar')
   plt.title('Retrieval Accuracy by Subject')
   plt.ylabel('Similarity Score')
   plt.show()
   ```

### C) Full M1 Testing
After visualizations, test the complete user journey:
- Onboarding form → Profile creation
- Tab 1 → Read introduction
- Tab 2 → View personalized examples
- Tab 3 → Complete activity
- Tab 4 → Take assessment
- Tab 5 → Write reflection & get feedback

## 💡 Tips

1. **Save your CSV files** - They're valuable research data
2. **Compare with Phase 2D** - Check if costs match expectations
3. **Look for outliers** - Any test >€0.0002 or >20s?
4. **Subject analysis** - Which subjects perform best?
5. **Document everything** - This goes in your dissertation

## 📞 Need Help?

**Common Issues:**
- Database connection → Check Docker
- Import errors → Check venv
- No results → Check console output
- Cost values = 0 → Check Gemini API key

**Success Indicators:**
- ✅ All 10 tests pass
- ✅ CSV has actual cost values
- ✅ Analysis report generated
- ✅ 3 viz files created

---

**Ready to start?**
```powershell
cd phase2e_testing
python test_rag_phase2e.py
```

**Good luck! 🚀**
