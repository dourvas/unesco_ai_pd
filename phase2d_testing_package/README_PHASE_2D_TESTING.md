# Phase 2D: RAG System Testing & Validation

**Complete Testing Package for UNESCO AI Teacher Professional Development Platform**

---

## 📦 Package Contents

This package contains everything needed to conduct comprehensive Phase 2D testing on your local machine:

### Core Files

1. **`test_rag_phase2d.py`** (19KB) - Main test suite
   - 10 comprehensive test cases
   - Command-line interface
   - Automated CSV logging
   - Performance metrics collection

2. **`PHASE_2D_TESTING_GUIDE.md`** (9KB) - Complete setup guide
   - Step-by-step instructions
   - Prerequisites checklist
   - Troubleshooting section
   - Expected results documentation

3. **`TESTING_QUICK_REFERENCE.md`** (3KB) - Quick reference card
   - Command cheat sheet
   - Test IDs reference
   - Expected performance benchmarks
   - Success checklist

4. **`analyze_results.py`** (7KB) - Results analysis script
   - Automated statistics generation
   - Dissertation-ready summaries
   - Subject breakdown analysis
   - Cost projections

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Copy files to your project directory
cp test_rag_phase2d.py /path/to/your/project/
cp analyze_results.py /path/to/your/project/

# 2. Set environment variable
export GEMINI_API_KEY="your_gemini_api_key"

# 3. Run quick validation (2 tests, ~30 seconds)
python test_rag_phase2d.py --quick

# 4. Review results
python analyze_results.py test_results/rag_test_results_*.csv
```

**Expected Output:**
```
✅ 2/2 tests passed
⏱️  Avg time: 12.5s
💰 Avg cost: €0.00014
```

---

## 📋 Full Testing Workflow

### Step 1: Pre-flight Check (2 min)

```bash
# Verify database is running
psql -h localhost -U postgres -d unesco_ai_teacher_pd -c "SELECT COUNT(*) FROM rag_documents;"
# Expected: 149 rows

# Verify API key
echo $GEMINI_API_KEY
# Expected: Your API key
```

### Step 2: Run Test Suite (3-4 min)

**Option A: Full suite (recommended for dissertation)**
```bash
python test_rag_phase2d.py
```

**Option B: Subject diversity only**
```bash
python test_rag_phase2d.py --subject-only
```

**Option C: Edge cases only**
```bash
python test_rag_phase2d.py --edge-only
```

**Option D: Single test**
```bash
python test_rag_phase2d.py --test SD01
```

### Step 3: Analyze Results (1 min)

```bash
# Generate statistical summary
python analyze_results.py test_results/rag_test_results_20260204_123456.csv

# View CSV in terminal
cat test_results/*.csv | column -t -s,

# Or open in Excel/Google Sheets for visualization
```

### Step 4: Manual Quality Assessment (30 min)

For each test result, document:
- UNESCO Alignment (Yes/No)
- Subject Relevance (1-5)
- Personalization Quality (1-5)
- Actionability (1-5)

See `PHASE_2D_TESTING_GUIDE.md` for detailed assessment template.

---

## 📊 Test Coverage

### Subject Diversity Tests (8 tests)

| Test ID | Subject | Grade Level | Focus Area |
|---------|---------|-------------|------------|
| SD01 | Mathematics | High School | Word problems, real-world connections |
| SD02 | Computer Science | University | Scaffolding vs dependency |
| SD03 | Physics | High School | Simulations, beginner guidance |
| SD04 | Language Arts | Middle School | Assessment validity, critical thinking |
| SD05 | History | High School | Research skills, source evaluation |
| SD06 | Art | Elementary | Creativity definition, skill development |
| SD07 | Physical Education | High School | Technology integration, performance |
| SD08 | Kindergarten | Kindergarten | Developmental appropriateness |

### Edge Case Tests (2 tests)

| Test ID | Category | Description |
|---------|----------|-------------|
| EC01 | Vague Input | Minimal reflection ("It was interesting") |
| EC02 | Off-Topic | Negative sentiment ("I hate AI") |

---

## 🎯 Expected Performance Benchmarks

**System Performance:**
- ✅ Success Rate: 100%
- ⏱️ Average Response Time: 10-15 seconds
- 💰 Average Cost: €0.00014 per query
- 📦 Chunks Retrieved: 4-6 per query
- 📝 Feedback Length: 300-800 words

**Quality Indicators:**
- UNESCO framework references present
- Subject-specific pedagogical content
- Grade-appropriate language
- Actionable next steps provided

---

## 📈 Results Output

### CSV File Structure

```csv
timestamp,test_id,test_type,category,subject,grade_level,reflection_length,feedback_length,execution_time,cost_estimate,chunks_retrieved,elements_found,status
2026-02-04T12:34:56,SD01,subject_diversity,STEM - Mathematics,Mathematics,High School,150,542,13.45,0.000142,5,4/4,SUCCESS
```

### Analysis Summary

```
PHASE 2D TEST RESULTS ANALYSIS
======================================================================
Total Tests:        10
Successful:         10 (100.0%)
Failed:             0 (0.0%)

Average Response Time:      12.34 seconds
Average Cost per Query:     €0.000145
Projected Cost (1000 users):€0.15

Subject Coverage:           8 teaching domains validated
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start if needed
sudo systemctl start postgresql
```

**2. GEMINI_API_KEY Not Found**
```bash
# Set environment variable
export GEMINI_API_KEY="your_key_here"

# Verify
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

**3. Module Import Errors**
```bash
# Install dependencies
pip install psycopg2-binary google-generativeai python-dotenv
```

**4. Slow Query Times (>20s)**
```bash
# Check database indexes
psql -h localhost -U postgres -d unesco_ai_teacher_pd -c "
SELECT indexname FROM pg_indexes WHERE tablename = 'rag_documents';
"
```

---

## 📚 Documentation for Dissertation

### Methodology Chapter Content

**Phase 2D Testing Protocol:**
- Test Suite: 10 systematically designed test cases
- Subject Coverage: 8 teaching domains (STEM, Humanities, Arts, Early Childhood)
- Edge Cases: 2 challenging input scenarios
- Metrics Collected: 
  - Performance: execution time, cost per query
  - Quality: relevance, personalization, UNESCO alignment
- Validation Method: Automated execution + manual qualitative assessment

**Sample Results Citation:**

```
The RAG system was validated through 10 test cases covering 8 teaching 
domains. All tests executed successfully (100% success rate) with an 
average response time of 12.3 seconds and cost of €0.00014 per query. 
Subject-specific content was verified through manual assessment, with 
all responses demonstrating appropriate pedagogical framing and UNESCO 
framework alignment (see Appendix D for complete test results).
```

### Appendix Materials

Include in dissertation appendices:
1. Complete test case definitions (`test_rag_phase2d.py` excerpt)
2. CSV results file (anonymized if needed)
3. Analysis summary output
4. Manual quality assessment ratings
5. Sample feedback responses (1-2 examples per subject)

---

## ✅ Success Criteria Checklist

Before concluding Phase 2D:

- [ ] All 10 tests executed successfully (100% pass rate)
- [ ] CSV file generated with complete metrics
- [ ] Average execution time < 20 seconds
- [ ] Average cost < €0.0002 per query
- [ ] UNESCO references present in all feedback
- [ ] Subject-specific content verified for all 8 domains
- [ ] Edge cases handled gracefully
- [ ] Manual quality assessment completed
- [ ] Results documented for dissertation
- [ ] Analysis summary generated

**When all criteria are met → Proceed to Phase 3: Multi-Module Scaling**

---

## 🔄 Next Steps

After successful Phase 2D validation:

1. **Document Findings**
   - Add results to dissertation methodology chapter
   - Create visualizations (charts/graphs) from CSV data
   - Document any unexpected behaviors or edge cases

2. **Identify Improvements**
   - Content gaps for specific subjects
   - Response time optimization opportunities
   - Additional edge cases to handle in future iterations

3. **Plan M2-M15 Scaling**
   - Design content ingestion strategy for remaining modules
   - Consider subject-specific resource additions
   - Plan for cross-module RAG query handling

4. **Cost Projection**
   - Calculate total cost for 15 modules
   - Validate €1/user target remains feasible
   - Document assumptions for dissertation

---

## 📞 Support

For questions or issues:

1. Check `PHASE_2D_TESTING_GUIDE.md` for detailed instructions
2. Review `TESTING_QUICK_REFERENCE.md` for quick command reference
3. Verify database and API key setup
4. Test with single query first: `python test_rag_phase2d.py --test SD01`

---

## 📄 File Descriptions

**Core Testing Files:**
- `test_rag_phase2d.py` - Main test suite with CLI
- `analyze_results.py` - Results analysis script

**Documentation Files:**
- `PHASE_2D_TESTING_GUIDE.md` - Complete setup guide
- `TESTING_QUICK_REFERENCE.md` - Quick reference card
- `README_PHASE_2D_TESTING.md` - This file

**Generated Files (after testing):**
- `test_results/rag_test_results_*.csv` - Test results data
- `test_results/analysis_summary_*.txt` - Analysis summary

---

## 🎓 Academic Context

This testing package is part of the doctoral dissertation research on:

**"Development and Validation of a UNESCO AI Competency Framework-Aligned 
Teacher Professional Development Platform Demonstrating AI-Powered 
Personalization at Scale"**

Phase 2D validates the core RAG system's ability to:
1. Generate personalized, subject-specific feedback
2. Maintain UNESCO framework alignment
3. Handle diverse teaching contexts and grade levels
4. Operate within cost constraints (€1/user target)
5. Demonstrate feasibility for scaling to 15 modules

Results from Phase 2D provide empirical evidence for the dissertation's 
feasibility claims regarding personalized professional development at scale.

---

**Version:** 1.0  
**Date:** February 4, 2026  
**Status:** Ready for local execution
