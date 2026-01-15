@echo off
cd /d "%~dp0"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q PyQt6 pyinstaller

echo Building Windows application...
pyinstaller --name="Log Viewer" --windowed --onefile --clean log_viewer.py

echo.
echo Done! Application created at: dist\Log Viewer.exe
pause
