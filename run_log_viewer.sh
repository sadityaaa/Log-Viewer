#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if ! python -c "import PyQt6" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi

python log_viewer.py
