# Phase 2D Testing - Quick Reference Card

## 🚀 Quick Start (30 seconds)

```bash
# 1. Navigate to project directory
cd /path/to/unesco-ai-teacher-pd

# 2. Set API key
export GEMINI_API_KEY="your_key_here"

# 3. Run quick validation
python test_rag_phase2d.py --quick
```

---

## 📋 Command Cheat Sheet

```bash
# Full test suite (10 tests, ~3-4 min)
python test_rag_phase2d.py

# Subject diversity only (8 tests)
python test_rag_phase2d.py --subject-only

# Edge cases only (2 tests)
python test_rag_phase2d.py --edge-only

# Quick validation (2 tests, ~30 sec)
python test_rag_phase2d.py --quick

# Single test by ID
python test_rag_phase2d.py --test SD01
python test_rag_phase2d.py --test EC02
```

---

## 🔍 Test IDs Reference

### Subject Diversity Tests
- **SD01**: Mathematics (High School) - Word problems
- **SD02**: Computer Science (University) - Python debugging
- **SD03**: Physics (High School) - Simulations for Newton's laws
- **SD04**: Language Arts (Middle School) - AI essay writing
- **SD05**: History (High School) - Timeline generation
- **SD06**: Art (Elementary) - AI art generators
- **SD07**: Physical Education (High School) - Performance analysis
- **SD08**: Kindergarten - Developmentally appropriate AI

### Edge Case Tests
- **EC01**: Vague input ("It was interesting")
- **EC02**: Off-topic/negative ("I hate AI")

---

## 📊 Expected Performance

```
✅ Success Rate: 100%
⏱️  Avg Time: 10-15 seconds per query
💰 Avg Cost: €0.00014 per query
📦 Chunks: 4-6 retrieved per query
📝 Feedback: 300-800 words
```

---

## 🔧 Troubleshooting

### Database not connected?
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### API key not set?
```bash
export GEMINI_API_KEY="your_key"
echo $GEMINI_API_KEY  # Verify
```

### Missing packages?
```bash
pip install psycopg2-binary google-generativeai python-dotenv
```

---

## 📈 Results Location

```
test_results/
└── rag_test_results_YYYYMMDD_HHMMSS.csv
```

**View in terminal:**
```bash
cat test_results/*.csv | column -t -s,
```

**Open in Excel/Sheets:**
- Import CSV
- Analyze metrics
- Create visualizations for dissertation

---

## 📝 Manual Quality Assessment Template

For each test result, document:

```
Test: SD01 (Mathematics)
─────────────────────────────
UNESCO Alignment:     ☑ Yes / ☐ No
Subject Relevance:    ⭐⭐⭐⭐⭐ (1-5)
Personalization:      ⭐⭐⭐⭐☆ (1-5)
Actionability:        ⭐⭐⭐⭐⭐ (1-5)

Notes:
- Strong connection to quadratic equations
- Appropriate for high school level
- Concrete next steps provided
```

---

## 🎯 Success Checklist

Before concluding Phase 2D:

- [ ] All 10 tests executed successfully
- [ ] CSV file saved with complete data
- [ ] Average time < 20 seconds
- [ ] Average cost < €0.0002
- [ ] UNESCO references present in feedback
- [ ] Subject-specific content verified
- [ ] Manual quality assessment completed
- [ ] Results documented for dissertation

---

## 📞 Next Steps

After successful Phase 2D:
1. Document findings in dissertation
2. Identify content gaps for improvement
3. Plan M2-M15 content ingestion
4. Design subject-specific resource strategy
5. Proceed to Phase 3: Multi-Module Scaling
