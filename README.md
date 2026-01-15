# High-Performance Log Viewer

A desktop application for viewing and analyzing large log files (1M+ lines) with multi-pattern regex search, built with PyQt6.

![Log Viewer](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## What is this?

This is a high-performance log file viewer designed for developers, system administrators, and anyone who needs to analyze large log files efficiently. Unlike traditional text editors that struggle with large files, this viewer uses memory mapping and virtual scrolling to handle files with millions of lines without consuming excessive RAM.

## Key Features

- **Handles massive files**: Open 10M+ line log files in under 500ms
- **Memory efficient**: Uses ~200MB RAM regardless of file size
- **Multi-pattern search**: Add multiple regex patterns with custom colors
- **Visual match indicators**: Scrollbar shows match locations with pattern colors
- **Fast navigation**: Jump between matches across all patterns
- **Text selection**: Select and copy log lines
- **Dark theme**: Easy on the eyes for long analysis sessions
- **Adjustable font**: Change text size on the fly

## Installation

### Quick Start (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/sadityaaa/Log-Viewer.git
cd Log-Viewer
```

2. **Run the application:**

**Windows:**
```bash
run_log_viewer.bat
```

**macOS/Linux:**
```bash
chmod +x run_log_viewer.sh
./run_log_viewer.sh
```

The scripts automatically:
- Create a virtual environment
- Install PyQt6 dependencies
- Launch the application

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python log_viewer.py
```

## Building Standalone Applications

### macOS App Bundle

Create a double-clickable .app:

```bash
chmod +x build_app.sh
./build_app.sh
```

This creates `dist/Log Viewer.app` which you can:
- Double-click to run
- Drag to Applications folder
- Launch from Spotlight

### Windows Executable

Create a standalone .exe:

```bash
build_app.bat
```

This creates `dist/Log Viewer.exe` which runs without Python installed.

## How to Use

### Basic Workflow

1. **Open a log file**
   - Click "Open" button
   - Select your .log or .txt file
   - File loads instantly even if it's gigabytes

2. **Add search patterns**
   - Click "[+]" to add a new pattern
   - Type a regex pattern (e.g., `ERROR`, `\d{3}\.\d{3}\.\d{3}\.\d{3}` for IPs)
   - Press Enter to apply
   - Matches highlight in the assigned color

3. **Navigate matches**
   - Use ◀ / ▶ buttons to jump between matches
   - Scrollbar shows colored markers where matches occur

4. **Customize**
   - Click color box to change highlight color
   - Use +/- buttons to adjust font size
   - Click 👁 to temporarily hide a pattern
   - Click ✕ to remove a pattern

5. **Copy text**
   - Click and drag to select lines
   - Press Ctrl+C (Cmd+C on Mac) to copy
   - Press Escape to clear selection

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Copy selected text | Ctrl+C (Cmd+C on Mac) |
| Clear selection | Escape |
| Apply pattern | Enter |

### Tips

- **Regex patterns**: Use standard regex syntax (e.g., `ERROR|WARN`, `\[\d{4}-\d{2}-\d{2}\]`)
- **Multiple patterns**: Add as many as you need - they all work together
- **Auto-scroll**: When selecting text near edges, the view auto-scrolls
- **Pattern colors**: Each pattern gets a unique color on the scrollbar

## Technical Architecture

### Core Components

**1. Memory-Mapped File Handler**
- Uses Python's `mmap` module
- Builds line offset index for O(1) access
- Loads multi-million line files without RAM bloat

**2. Virtual Scrolling Engine**
- Based on `QAbstractScrollArea`
- Only renders visible lines (viewport height ÷ line height)
- Maintains constant memory usage
- Achieves 60 FPS scrolling

**3. Multi-Pattern Search**
- Background `QThread` for non-blocking search
- Regex compilation and matching in separate thread
- Results cached for instant re-highlighting
- Scrollbar markers show match density

**4. Unified Navigation**
- Merges all pattern matches into sorted list
- Binary search for next/prev navigation
- Jumps to nearest match across all patterns

### Data Flow

```
File → mmap → Line Index → Virtual Viewport → Screen
                              ↓
Pattern → Background Thread → Match Index → Highlights + Scrollbar Markers
```

### Performance Metrics

- **File open**: <500ms for 10M lines
- **Scrolling**: 60 FPS smooth
- **Search**: <2s for 1M lines (background, non-blocking)
- **Memory**: ~200MB constant regardless of file size

## Requirements

- Python 3.8 or higher
- PyQt6
- Works on Windows, macOS, and Linux

## Project Structure

```
Log-Viewer/
├── log_viewer.py           # Main application
├── requirements.txt        # Python dependencies
├── run_log_viewer.sh       # macOS/Linux launcher
├── run_log_viewer.bat      # Windows launcher
├── build_app.sh            # macOS app builder
├── build_app.bat           # Windows exe builder
├── setup.py                # py2app configuration
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Troubleshooting

**Application won't start:**
- Ensure Python 3.8+ is installed: `python --version`
- Try manual installation steps above

**File won't open:**
- Check file permissions
- Ensure file is text-based (.log, .txt)

**Search is slow:**
- Complex regex patterns take longer
- Search runs in background - UI stays responsive

**Can't copy text:**
- Select lines by clicking and dragging
- Use Ctrl+C (Cmd+C) after selecting

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use in your projects

## Author

Created for efficient log file analysis

## Support

For issues or questions, please open a GitHub issue.
