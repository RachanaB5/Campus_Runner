#!/bin/bash
# Complete setup script for CampusCanteen

echo "🚀 CampusCanteen Setup Script"
echo "=============================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Node.js
echo -e "\n${BLUE}Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js v18+"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node -v) found${NC}"

# Check Python
echo -e "\n${BLUE}Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi
echo -e "${GREEN}✓ Python3 $(python3 --version) found${NC}"

# Install frontend dependencies
echo -e "\n${BLUE}Installing frontend dependencies...${NC}"
npm install --legacy-peer-deps
if [ $? -ne 0 ]; then
    echo "❌ Frontend installation failed"
    exit 1
fi
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Create Python virtual environment
echo -e "\n${BLUE}Setting up Python virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment and install Python packages
echo -e "\n${BLUE}Installing Python dependencies...${NC}"
source .venv/bin/activate
pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Python installation failed"
    exit 1
fi
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Initialize database
echo -e "\n${BLUE}Initializing database...${NC}"
python3 backend/init_db.py
if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed"
    exit 1
fi
echo -e "${GREEN}✓ Database initialized${NC}"

echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Open Terminal 1 and run:"
echo "   source .venv/bin/activate"
echo "   python3 backend/app.py"
echo ""
echo "2. Open Terminal 2 and run:"
echo "   npm run dev"
echo ""
echo "3. Open browser:"
echo "   http://localhost:5173"

echo -e "\n${BLUE}Documentation:${NC}"
echo "- START_HERE.md - Quick overview"
echo "- QUICK_START_GUIDE.md - 2-minute setup"
echo "- README_SETUP.md - Detailed guide"
echo "- IMPLEMENTATION_GUIDE.md - Architecture"

deactivate
