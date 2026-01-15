# High-Performance Log Viewer - Technical Architecture

## Core Components

### 1. Memory-Mapped File Handler
- **Technology**: Python `mmap` module
- **Purpose**: Load multi-million line files without consuming RAM
- **Strategy**: Read file in chunks, maintain line offset index for O(1) line access

### 2. Virtual Scrolling Engine
- **Base**: `QAbstractScrollArea` with custom painting
- **Rendering**: Only visible lines (viewport height / line height)
- **Line Cache**: LRU cache for recently accessed lines
- **Performance**: Constant memory regardless of file size

### 3. Multi-Pattern Search Engine
- **Threading**: `QThread` for background regex compilation and searching
- **Index Structure**: Dict mapping pattern → list of line numbers
- **Incremental**: Build index on-demand, cache results
- **Scrollbar Markers**: Paint tick marks at scaled positions

### 4. Unified Navigation System
- **Merge Strategy**: Combine all pattern matches into sorted list
- **Binary Search**: O(log n) lookup for next/prev from current position
- **State**: Track current match index across all patterns

## Data Flow

```
File → mmap → Line Index Builder → Virtual Viewport
                                  ↓
User Pattern → Background Thread → Match Index → Highlight Renderer
                                                ↓
                                          Scrollbar Markers
```

## Performance Targets
- File open: <500ms for 10M lines
- Scroll: 60 FPS
- Search: <2s for 1M lines (background)
- Memory: <200MB for any file size
