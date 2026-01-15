@echo off
cd /d "%~dp0"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -q -r requirements.txt
)

python log_viewer.py
pause
