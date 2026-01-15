#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -q PyQt6 pyinstaller

echo "Building macOS application..."
pyinstaller --name="Log Viewer" --windowed --onefile --clean log_viewer.py

echo ""
echo "✅ Done! Application created at: dist/Log Viewer.app"
echo "You can now drag it to your Applications folder"
