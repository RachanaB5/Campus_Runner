@echo off
REM Complete setup script for CampusCanteen (Windows)

echo.
echo CampusCanteen Setup Script
echo ===========================
echo.

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found. Please install Node.js v18+
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% found
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% found
echo.

REM Install frontend dependencies
echo Installing frontend dependencies...
call npm install --legacy-peer-deps
if errorlevel 1 (
    echo Error: Frontend installation failed
    exit /b 1
)
echo [OK] Frontend dependencies installed
echo.

REM Create Python virtual environment
echo Setting up Python virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment and install Python packages
echo Installing Python dependencies...
call .venv\Scripts\activate.bat
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo Error: Python installation failed
    exit /b 1
)
echo [OK] Python dependencies installed
echo.

REM Initialize database
echo Initializing database...
python backend\init_db.py
if errorlevel 1 (
    echo Error: Database initialization failed
    exit /b 1
)
echo [OK] Database initialized
echo.

echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Open Command Prompt 1 and run:
echo    .venv\Scripts\activate.bat
echo    python backend\app.py
echo.
echo 2. Open Command Prompt 2 and run:
echo    npm run dev
echo.
echo 3. Open browser:
echo    http://localhost:5173
echo.
echo Documentation:
echo - START_HERE.md - Quick overview
echo - QUICK_START_GUIDE.md - 2-minute setup
echo - README_SETUP.md - Detailed guide
echo - IMPLEMENTATION_GUIDE.md - Architecture
echo.

call .venv\Scripts\deactivate.bat
pause
