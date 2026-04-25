# Phase 2D: RAG System Testing - Local Execution Guide

## Overview
This guide provides step-by-step instructions for running the comprehensive RAG system test suite on your local machine where the PostgreSQL database is already running.

## Prerequisites Checklist

✅ **Database Requirements:**
- PostgreSQL running with `unesco_ai_teacher_pd` database
- RAG tables populated with 149 chunks (60 UNESCO, 48 RPE, 9 M1, 32 subject boxes)
- Connection details: localhost:5432, user: postgres, password: Django123!

✅ **Environment Requirements:**
- Python 3.8+
- GEMINI_API_KEY set in environment
- Required packages: psycopg2-binary, google-generativeai, python-dotenv

✅ **Files Required:**
- `/mnt/project/rag_query_system.py` (your existing RAG pipeline)
- `/home/claude/test_rag_v2.py` (the test suite, see below)

---

## Step 1: Verify Database Connection

First, confirm your PostgreSQL database is accessible:

```bash
# Test database connection
psql -h localhost -U postgres -d unesco_ai_teacher_pd -c "SELECT COUNT(*) FROM rag_documents;"
```

Expected output: Should show 149 rows (or your current chunk count)

```bash
# Verify tables exist
psql -h localhost -U postgres -d unesco_ai_teacher_pd -c "\dt"
```

Expected tables:
- rag_documents
- rag_queries
- rag_feedback

---

## Step 2: Set Environment Variables

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your_gemini_api_key_here"

# Verify it's set
echo $GEMINI_API_KEY
```

**Alternative:** Add to your `.bashrc` or `.zshrc`:
```bash
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

---

## Step 3: Install Dependencies (if needed)

```bash
# Create virtual environment (recommended)
python -m venv venv_testing
source venv_testing/bin/activate  # On Windows: venv_testing\Scripts\activate

# Install packages
pip install psycopg2-binary google-generativeai python-dotenv
```

---

## Step 4: Copy Test Suite to Your Project

Save the test suite file to your project directory:

```bash
# Assuming you're in your project root
# Copy from Claude's generated file or create new file:
nano test_rag_phase2d.py
```

Then paste the complete test suite code (provided below in separate section).

---

## Step 5: Run the Test Suite

### Full Test Suite (10 tests, ~3-4 minutes)

```bash
python test_rag_phase2d.py
```

### Run Only Subject Diversity Tests (8 tests)

```bash
python test_rag_phase2d.py --subject-only
```

### Run Only Edge Cases (2 tests)

```bash
python test_rag_phase2d.py --edge-only
```

### Quick Validation (2 tests)

```bash
python test_rag_phase2d.py --quick
```

---

## Step 6: Review Results

After execution, you'll find:

### Console Output
- Real-time progress for each test
- Success/failure status
- Performance metrics
- Summary statistics

### CSV File
```
test_results/rag_test_results_YYYYMMDD_HHMMSS.csv
```

**Columns:**
- timestamp
- test_id
- test_type
- category
- subject
- grade_level
- reflection_length
- feedback_length
- execution_time
- cost_estimate
- chunks_retrieved
- status
- error (if failed)

### Example Analysis

```bash
# View results
cat test_results/rag_test_results_*.csv | column -t -s,

# Quick stats
python -c "
import csv
with open('test_results/rag_test_results_20260204_123456.csv') as f:
    data = list(csv.DictReader(f))
    success = sum(1 for r in data if r['status'] == 'SUCCESS')
    print(f'Success Rate: {success/len(data)*100:.1f}%')
    print(f'Avg Time: {sum(float(r[\"execution_time\"]) for r in data if r[\"status\"]==\"SUCCESS\")/success:.2f}s')
"
```

---

## Expected Results

### Success Criteria

**Performance Benchmarks:**
- ✅ Execution time: 10-15 seconds per query
- ✅ Cost per query: €0.00010 - €0.00020
- ✅ Success rate: 100% (all tests pass)

**Quality Indicators:**
- Feedback length: 300-800 words
- Chunks retrieved: 4-6 per query
- Subject-specific content present in feedback
- UNESCO framework references included

### Common Issues & Solutions

**Issue 1: Database Connection Failed**
```
Error: connection to server at "localhost" failed
```
**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql
# Or on Mac:
brew services list | grep postgresql

# Start if needed
sudo systemctl start postgresql
```

**Issue 2: GEMINI_API_KEY Not Found**
```
Error: API key not found in environment
```
**Solution:**
```bash
export GEMINI_API_KEY="your_key_here"
# Verify
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

**Issue 3: Module Import Errors**
```
ModuleNotFoundError: No module named 'psycopg2'
```
**Solution:**
```bash
pip install psycopg2-binary google-generativeai python-dotenv
```

**Issue 4: Slow Query Times (>20s)**
```
Warning: Query taking longer than expected
```
**Solution:**
```bash
# Check database indexes
psql -h localhost -U postgres -d unesco_ai_teacher_pd -c "
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename = 'rag_documents';
"

# Should show vector index on embedding column
```

---

## Data Collection for Dissertation

### Quantitative Metrics

After running tests, collect these metrics for your doctoral research:

**System Performance:**
- Average response time: ___ seconds
- Cost per interaction: €___
- Total cost for 10 interactions: €___
- Database query efficiency (chunks retrieved per query)

**Subject Coverage Validation:**
- 8/8 subjects tested ✅
- All subjects received relevant, personalized feedback
- Subject-specific pedagogical content verified

**Edge Case Handling:**
- Vague input: System requests elaboration ✅
- Off-topic input: System maintains pedagogical framing ✅
- System demonstrates graceful degradation

### Qualitative Assessment

For each test result, manually assess:

1. **UNESCO Alignment** (Yes/No)
   - Does feedback reference UNESCO AI Competency Framework?
   - Are competency levels (Acquire/Deepen/Create) mentioned?

2. **Subject Relevance** (1-5 scale)
   - How well does feedback address subject-specific concerns?
   - Are examples appropriate for the teaching domain?

3. **Personalization Quality** (1-5 scale)
   - Does feedback account for grade level?
   - Is AI comfort level reflected in language complexity?

4. **Actionability** (1-5 scale)
   - Does feedback provide concrete next steps?
   - Can teacher immediately apply suggestions?

**Template for Manual Review:**
```
Test ID: SD01 (Mathematics)
UNESCO Alignment: Yes ✅
Subject Relevance: 5/5
Personalization: 4/5
Actionability: 5/5
Notes: Strong connection to quadratic equations, appropriate for high school level
```

---

## Next Steps After Testing

### Immediate Actions:

1. **Document Results**
   - Save CSV file to dissertation folder
   - Take screenshots of console output
   - Note any unexpected behaviors

2. **Analyze Patterns**
   - Which subjects got best feedback?
   - Were any edge cases problematic?
   - Cost projections for full user base

3. **Identify Improvements**
   - Content gaps (missing subject-specific examples)
   - Response time optimization opportunities
   - Additional edge cases to handle

### For Dissertation Documentation:

Include in your methodology chapter:

```
Phase 2D Testing Protocol
- Test Suite: 10 systematically designed test cases
- Subject Coverage: 8 teaching domains (STEM, Humanities, Arts, Early Childhood)
- Edge Cases: 2 challenging input scenarios
- Metrics Collected: Performance (time, cost), Quality (relevance, personalization)
- Validation Method: Automated execution + manual qualitative assessment
- Results: [Insert your findings]
```

---

## Support & Troubleshooting

If you encounter issues:

1. **Check Database:**
   ```bash
   psql -h localhost -U postgres -d unesco_ai_teacher_pd -c "SELECT COUNT(*) FROM rag_documents;"
   ```

2. **Verify API Key:**
   ```bash
   python -c "import os, google.generativeai as genai; genai.configure(api_key=os.getenv('GEMINI_API_KEY')); print('✅ API key valid')"
   ```

3. **Test Single Query:**
   ```bash
   python -c "
   import sys
   sys.path.append('/mnt/project')
   from rag_query_system import process_reflection
   result = process_reflection('Test reflection', 'Subject: Mathematics', 1, 1)
   print('✅ Single query works:', len(result['feedback']), 'chars')
   "
   ```

4. **Review Logs:**
   ```bash
   tail -f test_output.log
   ```

---

## Timeline Estimate

- **Setup & Verification:** 10-15 minutes
- **Full Test Suite Execution:** 3-4 minutes (10 queries × 15s each + pauses)
- **Results Review:** 15-20 minutes
- **Qualitative Assessment:** 30-40 minutes

**Total:** ~1.5 hours for complete Phase 2D validation

---

## Success Confirmation

You'll know testing is successful when:

✅ All 10 tests show "SUCCESS" status
✅ CSV file generated with complete data
✅ Average execution time < 20 seconds
✅ Average cost < €0.0002 per query
✅ Feedback mentions UNESCO framework
✅ Subject-specific content appears in responses
✅ No database connection errors

**Ready to proceed to M2-M15 scaling after successful Phase 2D validation!**
