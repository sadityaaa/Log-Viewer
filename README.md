# High-Performance Log Viewer

A PyQt6-based log viewer optimized for files with 1M+ lines using memory mapping and virtual scrolling.

![Log Viewer](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Features

- **Memory-mapped I/O**: Handles multi-million line files without RAM bloat
- **Virtual scrolling**: Only renders visible lines (60 FPS)
- **Multi-pattern search**: Add unlimited regex patterns with color coding
- **Unified navigation**: Jump to next/prev match across all patterns
- **Scrollbar markers**: Visual density map of matches with pattern colors
- **Line numbers**: Automatic line numbering
- **Text selection**: Select and copy log lines (Ctrl+C / Cmd+C)
- **Dark theme**: Black background with white text for reduced eye strain
- **Font controls**: Adjustable font size (8-24pt)

## Installation

### Quick Start (All Platforms)

```bash
git clone https://github.com/sadityaaa/Log-Viewer.git
cd Log-Viewer
```

**Windows:**
```bash
run_log_viewer.bat
```

**macOS/Linux:**
```bash
./run_log_viewer.sh
```

The scripts automatically create a virtual environment and install dependencies on first run.

### Manual Installation

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python log_viewer.py
```

## Building Standalone Application

### macOS App Bundle

```bash
bash build_app.sh
```

This creates `dist/Log Viewer.app` which you can drag to Applications.

### Windows Executable

```bash
pip install pyinstaller
pyinstaller --name="Log Viewer" --windowed --onefile log_viewer.py
```

This creates `dist/Log Viewer.exe`.

## Usage

1. **Open File**: Click "Open" button to load a .log or .txt file
2. **Add Pattern**: Click "[+]" to create a search filter
3. **Enter Pattern**: Type regex pattern and press Enter
4. **Navigate**: Use ◀ / ▶ buttons to jump between matches
5. **Adjust Font**: Use +/- buttons to change text size
6. **Change Color**: Click color box to customize highlight color
7. **Toggle Pattern**: Click 👁 to show/hide pattern
8. **Remove Pattern**: Click ✕ to delete pattern
9. **Select Text**: Click and drag to select lines, press Ctrl+C (Cmd+C) to copy
10. **Clear Selection**: Press Escape

## Controls

| Action | Shortcut |
|--------|----------|
| Copy selected text | Ctrl+C (Cmd+C on Mac) |
| Clear selection | Escape |
| Apply pattern | Enter |

## Performance

- Opens 10M line files in <500ms
- Constant memory usage (~200MB)
- Smooth 60 FPS scrolling
- Background threaded search

## Requirements

- Python 3.8+
- PyQt6

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details.

## License

MIT License

## Contributing

Pull requests are welcome! For major changes, please open an issue first.
