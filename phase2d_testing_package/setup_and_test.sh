#!/bin/bash
# Phase 2D Testing - Automated Setup Script
# UNESCO AI Teacher Professional Development Platform

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Phase 2D Testing - Automated Setup                        ║"
echo "║  UNESCO AI Teacher PD Platform                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "🔍 Checking prerequisites..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python3 found: $(python3 --version)"
else
    echo -e "${RED}✗${NC} Python3 not found"
    exit 1
fi

# Check PostgreSQL
echo ""
echo "Checking PostgreSQL connection..."
if psql -h localhost -U postgres -d unesco_ai_teacher_pd -c "SELECT 1" &> /dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL connected"
    
    # Check RAG tables
    ROW_COUNT=$(psql -h localhost -U postgres -d unesco_ai_teacher_pd -t -c "SELECT COUNT(*) FROM rag_documents;" 2>/dev/null | tr -d ' ')
    echo -e "${GREEN}✓${NC} RAG documents: $ROW_COUNT chunks"
else
    echo -e "${RED}✗${NC} PostgreSQL not accessible"
    echo "  Please start PostgreSQL: sudo systemctl start postgresql"
    exit 1
fi

# Check GEMINI_API_KEY
echo ""
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC} GEMINI_API_KEY not set"
    read -p "Enter your Gemini API key: " api_key
    export GEMINI_API_KEY="$api_key"
    echo "export GEMINI_API_KEY='$api_key'" >> ~/.bashrc
    echo -e "${GREEN}✓${NC} API key set and saved to ~/.bashrc"
else
    echo -e "${GREEN}✓${NC} GEMINI_API_KEY is set"
fi

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install psycopg2-binary google-generativeai python-dotenv -q
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create results directory
echo ""
echo "📁 Creating test_results directory..."
mkdir -p test_results
echo -e "${GREEN}✓${NC} Directory created"

# Run quick validation
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Running quick validation (2 tests)..."
echo "════════════════════════════════════════════════════════════════"
echo ""

python3 test_rag_phase2d.py --quick

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Setup complete! ✅"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Review quick validation results above"
echo "  2. Run full test suite: python3 test_rag_phase2d.py"
echo "  3. Analyze results: python3 analyze_results.py test_results/*.csv"
echo ""
echo "For help, see: README_PHASE_2D_TESTING.md"
