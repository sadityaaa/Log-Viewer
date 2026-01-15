import sys
import mmap
import re
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QAbstractScrollArea, 
                              QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLineEdit, QLabel, QFileDialog, QColorDialog, QStatusBar, QScrollBar)
from PyQt6.QtCore import Qt, QRect, QThread, pyqtSignal, QTimer, QEvent
from PyQt6.QtGui import QPainter, QColor, QFont, QFontMetrics, QPalette

COLORS = ['#FFFF00', '#00FF00', '#FF00FF', '#00FFFF', '#FFA500', '#FF69B4']

class MatchScrollBar(QScrollBar):
    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Vertical, parent)
        self.pattern_matches = {}
        self.total_lines = 0
    
    def set_pattern_matches(self, pattern_matches, total):
        self.pattern_matches = pattern_matches
        self.total_lines = total
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.pattern_matches or not self.total_lines:
            return
        painter = QPainter(self)
        for pattern_id, (color, matches) in self.pattern_matches.items():
            for line_idx in matches:
                y = int((line_idx / self.total_lines) * self.height())
                painter.fillRect(self.width() - 4, y, 4, 2, QColor(color))
        painter.end()

class SearchWorker(QThread):
    finished = pyqtSignal(str, list)
    
    def __init__(self, indexer, pattern, pattern_id):
        super().__init__()
        self.indexer = indexer
        self.pattern = pattern
        self.pattern_id = pattern_id
        
    def run(self):
        try:
            regex = re.compile(self.pattern, re.IGNORECASE)
            matches = []
            for i in range(self.indexer.total_lines()):
                line = self.indexer.get_line(i)
                if regex.search(line):
                    matches.append(i)
            self.finished.emit(self.pattern_id, matches)
        except Exception as e:
            print(f"Search error: {e}")
            self.finished.emit(self.pattern_id, [])

class LineIndexer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(filepath, 'rb')
        self.mmap = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
        self.line_offsets = [0]
        self._build_index()
        
    def _build_index(self):
        pos = 0
        while True:
            pos = self.mmap.find(b'\n', pos)
            if pos == -1:
                break
            self.line_offsets.append(pos + 1)
            pos += 1
            
    def get_line(self, idx):
        if idx >= len(self.line_offsets):
            return ""
        start = self.line_offsets[idx]
        end = self.line_offsets[idx + 1] - 1 if idx + 1 < len(self.line_offsets) else len(self.mmap)
        return self.mmap[start:end].decode('utf-8', errors='ignore')
    
    def total_lines(self):
        return len(self.line_offsets)
    
    def iter_lines(self):
        for i in range(self.total_lines()):
            yield self.get_line(i)
    
    def close(self):
        self.mmap.close()
        self.file.close()

class VirtualLogView(QAbstractScrollArea):
    def __init__(self):
        super().__init__()
        self.indexer = None
        self.font = QFont("Courier", 12)
        self.fm = QFontMetrics(self.font)
        self.line_height = self.fm.height()
        self.char_width = self.fm.horizontalAdvance('0')
        self.patterns = {}
        self.all_matches = []
        self.current_match_idx = -1
        self.current_line = 0
        self.workers = []
        self.viewport().setStyleSheet("background-color: black;")
        
        # Custom scrollbar
        self.match_scrollbar = MatchScrollBar()
        self.setVerticalScrollBar(self.match_scrollbar)
        
        # Selection support
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        self.setMouseTracking(True)
        
    def load_file(self, filepath):
        if self.indexer:
            self.indexer.close()
        self.indexer = LineIndexer(filepath)
        self.verticalScrollBar().setMaximum(max(0, self.indexer.total_lines() - 1))
        self.viewport().update()
        
    def paintEvent(self, event):
        if not self.indexer:
            return
            
        painter = QPainter(self.viewport())
        painter.setFont(self.font)
        
        viewport_height = self.viewport().height()
        first_line = self.verticalScrollBar().value()
        visible_lines = (viewport_height // self.line_height) + 2
        
        line_num_width = len(str(self.indexer.total_lines())) * self.char_width + 20
        
        for i in range(visible_lines):
            line_idx = first_line + i
            if line_idx >= self.indexer.total_lines():
                break
                
            y = i * self.line_height
            line_text = self.indexer.get_line(line_idx)
            
            # Draw background
            painter.fillRect(0, y, self.viewport().width(), self.line_height, QColor('black'))
            
            # Draw selection highlight
            if self.selection_start is not None and self.selection_end is not None:
                start = min(self.selection_start, self.selection_end)
                end = max(self.selection_start, self.selection_end)
                if start <= line_idx <= end:
                    painter.fillRect(0, y, self.viewport().width(), self.line_height, QColor(70, 70, 120))
            
            # Highlight matches
            for pattern_id, data in self.patterns.items():
                if len(data) < 3 or not data[2]:
                    continue
                pattern, color = data[0], data[1]
                try:
                    for match in re.finditer(pattern, line_text, re.IGNORECASE):
                        x_start = line_num_width + match.start() * self.char_width
                        width = (match.end() - match.start()) * self.char_width
                        painter.fillRect(x_start, y, width, self.line_height, QColor(color))
                except:
                    pass
            
            # Line number
            painter.setPen(Qt.GlobalColor.darkGray)
            painter.drawText(5, y + self.fm.ascent(), str(line_idx + 1))
            
            # Line text
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(line_num_width, y + self.fm.ascent(), line_text[:200])

            
    def add_pattern(self, pattern_id, pattern, color):
        self.patterns[pattern_id] = (pattern, color, True)
        if self.indexer:
            worker = SearchWorker(self.indexer, pattern, pattern_id)
            worker.finished.connect(self._on_search_complete)
            worker.finished.connect(worker.deleteLater)
            self.workers.append(worker)
            worker.start()
    
    def _on_search_complete(self, pattern_id, matches):
        if pattern_id in self.patterns:
            pattern, color, _ = self.patterns[pattern_id]
            self.patterns[pattern_id] = (pattern, color, True, matches)
            self._rebuild_match_list()
            self.viewport().update()
    
    def _rebuild_match_list(self):
        all_matches = set()
        pattern_matches = {}
        for pattern_id, data in self.patterns.items():
            if len(data) > 3 and data[2]:
                all_matches.update(data[3])
                pattern_matches[pattern_id] = (data[1], data[3])
        self.all_matches = sorted(all_matches)
        if self.indexer:
            self.match_scrollbar.set_pattern_matches(pattern_matches, self.indexer.total_lines())
        
    def remove_pattern(self, pattern_id):
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            self._rebuild_match_list()
            self.viewport().update()
    
    def toggle_pattern(self, pattern_id):
        if pattern_id in self.patterns:
            pattern, color, enabled, *matches = self.patterns[pattern_id]
            self.patterns[pattern_id] = (pattern, color, not enabled, *matches)
            self._rebuild_match_list()
            self.viewport().update()
    
    def next_match(self):
        if not self.all_matches:
            return
        current = self.verticalScrollBar().value()
        for i, line_idx in enumerate(self.all_matches):
            if line_idx > current:
                self.current_match_idx = i
                self.verticalScrollBar().setValue(line_idx)
                self.viewport().update()
                return
        self.verticalScrollBar().setValue(self.all_matches[0])
        
    def prev_match(self):
        if not self.all_matches:
            return
        current = self.verticalScrollBar().value()
        for i in range(len(self.all_matches) - 1, -1, -1):
            if self.all_matches[i] < current:
                self.current_match_idx = i
                self.verticalScrollBar().setValue(self.all_matches[i])
                self.viewport().update()
                return
        self.verticalScrollBar().setValue(self.all_matches[-1])
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            line_idx = self.verticalScrollBar().value() + (event.pos().y() // self.line_height)
            self.selection_start = line_idx
            self.selection_end = line_idx
            self.is_selecting = True
            self.viewport().update()
    
    def mouseMoveEvent(self, event):
        if self.is_selecting:
            line_idx = self.verticalScrollBar().value() + (event.pos().y() // self.line_height)
            self.selection_end = line_idx
            
            # Auto-scroll when selecting near edges
            if event.pos().y() < self.line_height:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 1)
            elif event.pos().y() > self.viewport().height() - self.line_height:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 1)
            
            self.viewport().update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = False
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.selection_start = None
            self.selection_end = None
            self.viewport().update()
        elif event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._copy_selection()
    
    def _copy_selection(self):
        if self.selection_start is None or not self.indexer:
            return
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)
        lines = []
        for i in range(start, end + 1):
            if i < self.indexer.total_lines():
                lines.append(self.indexer.get_line(i))
        text = '\n'.join(lines)
        QApplication.clipboard().setText(text)

class LogViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("High-Performance Log Viewer")
        self.resize(1200, 800)
        
        self.log_view = VirtualLogView()
        self.setCentralWidget(self.log_view)
        
        self.pattern_counter = 0
        self.pattern_widgets = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Bottom dock
        dock = QWidget()
        dock_layout = QVBoxLayout(dock)
        
        # Navigation
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("◀")
        prev_btn.setFixedWidth(35)
        prev_btn.clicked.connect(self.log_view.prev_match)
        next_btn = QPushButton("▶")
        next_btn.setFixedWidth(35)
        next_btn.clicked.connect(self.log_view.next_match)
        
        # Font size controls
        font_label = QLabel("Font:")
        minus_btn = QPushButton("-")
        minus_btn.setFixedWidth(25)
        minus_btn.clicked.connect(lambda: self._change_font_size(-1))
        plus_btn = QPushButton("+")
        plus_btn.setFixedWidth(25)
        plus_btn.clicked.connect(lambda: self._change_font_size(1))
        
        open_btn = QPushButton("Open")
        open_btn.setFixedWidth(60)
        open_btn.clicked.connect(self._open_file)
        
        add_btn = QPushButton("[+]")
        add_btn.setFixedWidth(40)
        add_btn.clicked.connect(self._add_pattern)
        
        nav_layout.addWidget(open_btn)
        nav_layout.addWidget(add_btn)
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(next_btn)
        nav_layout.addWidget(font_label)
        nav_layout.addWidget(minus_btn)
        nav_layout.addWidget(plus_btn)
        nav_layout.addStretch()
        
        # Pattern area
        pattern_scroll = QWidget()
        self.pattern_layout = QVBoxLayout(pattern_scroll)
        self.pattern_layout.setContentsMargins(0, 0, 0, 0)
        
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidget(pattern_scroll)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(100)
        
        # Add pattern button
        add_layout = QHBoxLayout()
        
        dock_layout.addLayout(nav_layout)
        dock_layout.addWidget(scroll_area)
        
        # Add dock to main window
        dock.setMaximumHeight(150)
        self.setStatusBar(self.status)
        
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.addWidget(self.log_view)
        main_layout.addWidget(dock)
        self.setCentralWidget(container)
        
    def _open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Log File", "", "Log Files (*.log *.txt)")
        if filepath:
            self.log_view.load_file(filepath)
            size = Path(filepath).stat().st_size
            lines = self.log_view.indexer.total_lines()
            self.status.showMessage(f"File: {filepath} | Size: {size:,} bytes | Lines: {lines:,}")
    
    def _add_pattern(self):
        pattern_id = f"pattern_{self.pattern_counter}"
        self.pattern_counter += 1
        color = COLORS[self.pattern_counter % len(COLORS)]
        
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        
        color_btn = QPushButton()
        color_btn.setFixedSize(25, 25)
        color_btn.setStyleSheet(f"background-color: {color}")
        color_btn.clicked.connect(lambda: self._change_color(pattern_id, color_btn))
        
        pattern_input = QLineEdit()
        pattern_input.setPlaceholderText("Enter regex pattern...")
        pattern_input.returnPressed.connect(lambda: self._apply_pattern(pattern_id, pattern_input.text(), color))
        
        toggle_btn = QPushButton("👁")
        toggle_btn.setFixedWidth(30)
        toggle_btn.clicked.connect(lambda: self.log_view.toggle_pattern(pattern_id))
        
        remove_btn = QPushButton("✕")
        remove_btn.setFixedWidth(30)
        remove_btn.clicked.connect(lambda: self._remove_pattern(pattern_id, row))
        
        layout.addWidget(color_btn)
        layout.addWidget(pattern_input)
        layout.addWidget(toggle_btn)
        layout.addWidget(remove_btn)
        
        self.pattern_layout.addWidget(row)
        self.pattern_widgets[pattern_id] = (row, color_btn, pattern_input)
        
    def _apply_pattern(self, pattern_id, pattern, color):
        if pattern and self.log_view.indexer:
            try:
                # Test compile the regex first
                re.compile(pattern, re.IGNORECASE)
                self.log_view.add_pattern(pattern_id, pattern, color)
            except Exception as e:
                self.status.showMessage(f"Invalid pattern: {e}", 3000)
        elif pattern and not self.log_view.indexer:
            self.status.showMessage("Please open a file first!", 3000)
            
    def _change_color(self, pattern_id, btn):
        color = QColorDialog.getColor()
        if color.isValid():
            btn.setStyleSheet(f"background-color: {color.name()}")
            if pattern_id in self.pattern_widgets:
                _, _, input_widget = self.pattern_widgets[pattern_id]
                self._apply_pattern(pattern_id, input_widget.text(), color.name())
    
    def _remove_pattern(self, pattern_id, widget):
        self.log_view.remove_pattern(pattern_id)
        self.pattern_layout.removeWidget(widget)
        widget.deleteLater()
        del self.pattern_widgets[pattern_id]
    
    def _change_font_size(self, delta):
        current_size = self.log_view.font.pointSize()
        new_size = max(8, min(24, current_size + delta))
        self.log_view.font.setPointSize(new_size)
        self.log_view.fm = QFontMetrics(self.log_view.font)
        self.log_view.line_height = self.log_view.fm.height()
        self.log_view.char_width = self.log_view.fm.horizontalAdvance('0')
        self.log_view.viewport().update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogViewerWindow()
    window.show()
    sys.exit(app.exec())
