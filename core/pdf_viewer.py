"""
Premium PDF Viewer - Adobe-like Interface
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import fitz


class PDFViewerWidget(QWidget):
    """Premium PDF viewer with Adobe-like interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_factor = 1.0
        self.is_fullscreen = False
        self.page_labels = []
        self.scroll_area = None
        self.pages_container = None
        self.pages_layout = None
        self.toolbar = None
        self.zoom_combo = None
        self.page_label = None
        self.page_input = None
        self.go_btn = None
        self.is_annotating = False
        self.annotation_color = QColor(255, 255, 0, 100)
        self.highlight_btn = None
        self.underline_btn = None
        self.note_btn = None
        self.draw_btn = None
        self.current_tool = "select"
        
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # === Adobe-like Toolbar ===
        self.toolbar = self.create_adobe_toolbar()
        layout.addWidget(self.toolbar)
        
        # === Main Scroll Area ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #e8e8e8;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 14px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 7px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar:horizontal {
                background-color: #f0f0f0;
                height: 14px;
            }
            QScrollBar::handle:horizontal {
                background-color: #c1c1c1;
                border-radius: 7px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a0a0a0;
            }
        """)
        
        self.pages_container = QWidget()
        self.pages_layout = QVBoxLayout()
        self.pages_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pages_layout.setSpacing(15)
        self.pages_layout.setContentsMargins(20, 20, 20, 20)
        self.pages_container.setLayout(self.pages_layout)
        
        self.scroll_area.setWidget(self.pages_container)
        layout.addWidget(self.scroll_area)
        
        # === Bottom Status Bar ===
        status_bar = QHBoxLayout()
        status_bar.setContentsMargins(10, 4, 10, 4)
        status_bar.setSpacing(15)
        
        self.page_info_label = QLabel("Page 1 of 1")
        self.page_info_label.setStyleSheet("font-weight: 600; color: #495057; font-size: 12px;")
        status_bar.addWidget(self.page_info_label)
        
        status_bar.addStretch()
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("font-weight: 600; color: #0078d4; font-size: 12px;")
        status_bar.addWidget(self.zoom_label)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        status_bar.addWidget(self.status_label)
        
        status_widget = QWidget()
        status_widget.setStyleSheet("background-color: #f8f9fa; border-top: 1px solid #dee2e6;")
        status_widget.setLayout(status_bar)
        layout.addWidget(status_widget)
        
        self.setLayout(layout)
        
        # Install event filter for wheel events
        self.scroll_area.viewport().installEventFilter(self)
    
    def create_adobe_toolbar(self):
        """Create Adobe-like toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: none;
                border-bottom: 2px solid #3498db;
                padding: 3px 5px;
                min-height: 42px;
                spacing: 3px;
            }
            QToolBar::separator {
                width: 2px;
                background: #4a6a8a;
                margin: 5px 3px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                padding: 4px 10px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 12px;
                color: #ecf0f1;
            }
            QToolBar QToolButton:hover {
                background-color: #3d566e;
            }
            QToolBar QToolButton:pressed {
                background-color: #4a6a8a;
            }
            QToolBar QToolButton:checked {
                background-color: #3498db;
                border-radius: 4px;
            }
            QComboBox {
                padding: 3px 8px;
                border: 1px solid #5a7a9a;
                border-radius: 4px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 12px;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QLineEdit {
                padding: 3px 8px;
                border: 1px solid #5a7a9a;
                border-radius: 4px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 12px;
                min-height: 24px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QLabel {
                color: #ecf0f1;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # === Navigation Group ===
        prev_btn = QAction("◀", self)
        prev_btn.triggered.connect(self.prev_page)
        prev_btn.setToolTip("Previous Page (←)")
        prev_btn.setShortcut("Left")
        toolbar.addAction(prev_btn)
        
        self.page_label = QLabel("0 / 0")
        toolbar.addWidget(self.page_label)
        
        next_btn = QAction("▶", self)
        next_btn.triggered.connect(self.next_page)
        next_btn.setToolTip("Next Page (→)")
        next_btn.setShortcut("Right")
        toolbar.addAction(next_btn)
        
        toolbar.addSeparator()
        
        # === Zoom Group ===
        zoom_out_btn = QAction("−", self)
        zoom_out_btn.triggered.connect(self.zoom_out)
        zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        zoom_out_btn.setShortcut("Ctrl+-")
        toolbar.addAction(zoom_out_btn)
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.setMaximumWidth(80)
        self.zoom_combo.currentTextChanged.connect(self.zoom_changed)
        toolbar.addWidget(self.zoom_combo)
        
        zoom_in_btn = QAction("+", self)
        zoom_in_btn.triggered.connect(self.zoom_in)
        zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        zoom_in_btn.setShortcut("Ctrl++")
        toolbar.addAction(zoom_in_btn)
        
        toolbar.addSeparator()
        
        # === Fit Options ===
        fit_page_btn = QAction("Fit Page", self)
        fit_page_btn.triggered.connect(self.fit_to_page)
        fit_page_btn.setToolTip("Fit Page to Window")
        toolbar.addAction(fit_page_btn)
        
        fit_width_btn = QAction("Fit Width", self)
        fit_width_btn.triggered.connect(self.fit_to_width)
        fit_width_btn.setToolTip("Fit Width to Window")
        toolbar.addAction(fit_width_btn)
        
        toolbar.addSeparator()
        
        # === Annotation Tools ===
        self.highlight_btn = QAction("🟡 Highlight", self)
        self.highlight_btn.setCheckable(True)
        self.highlight_btn.triggered.connect(lambda: self.set_tool("highlight"))
        toolbar.addAction(self.highlight_btn)
        
        self.underline_btn = QAction("U̲ Underline", self)
        self.underline_btn.setCheckable(True)
        self.underline_btn.triggered.connect(lambda: self.set_tool("underline"))
        toolbar.addAction(self.underline_btn)
        
        self.note_btn = QAction("📝 Note", self)
        self.note_btn.setCheckable(True)
        self.note_btn.triggered.connect(lambda: self.set_tool("note"))
        toolbar.addAction(self.note_btn)
        
        toolbar.addSeparator()
        
        # === Full Screen ===
        fullscreen_btn = QAction("⛶ Full Screen", self)
        fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        fullscreen_btn.setToolTip("Full Screen (F11)")
        fullscreen_btn.setShortcut("F11")
        toolbar.addAction(fullscreen_btn)
        
        # === Spacer ===
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # === Go to Page ===
        toolbar.addWidget(QLabel("Go to:"))
        self.page_input = QLineEdit()
        self.page_input.setMaximumWidth(50)
        self.page_input.setPlaceholderText("Page")
        self.page_input.returnPressed.connect(self.go_to_page)
        toolbar.addWidget(self.page_input)
        
        self.go_btn = QPushButton("Go")
        self.go_btn.clicked.connect(self.go_to_page)
        self.go_btn.setMaximumWidth(40)
        toolbar.addWidget(self.go_btn)
        
        return toolbar
    
    def set_tool(self, tool):
        """Set the current annotation tool"""
        self.current_tool = tool
        # Reset all buttons
        self.highlight_btn.setChecked(False)
        self.underline_btn.setChecked(False)
        self.note_btn.setChecked(False)
        
        if tool == "highlight":
            self.highlight_btn.setChecked(True)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        elif tool == "underline":
            self.underline_btn.setChecked(True)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        elif tool == "note":
            self.note_btn.setChecked(True)
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                delta = event.angleDelta().y()
                if delta > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()
                return True
        return super().eventFilter(obj, event)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.home_shortcut = QShortcut(QKeySequence("Home"), self)
        self.home_shortcut.activated.connect(self.go_to_first_page)
        self.end_shortcut = QShortcut(QKeySequence("End"), self)
        self.end_shortcut.activated.connect(self.go_to_last_page)
        self.page_up_shortcut = QShortcut(QKeySequence("PgUp"), self)
        self.page_up_shortcut.activated.connect(self.prev_page)
        self.page_down_shortcut = QShortcut(QKeySequence("PgDown"), self)
        self.page_down_shortcut.activated.connect(self.next_page)
    
    def load_document(self, doc):
        self.doc = doc
        self.total_pages = doc.page_count
        self.current_page = 0
        self.zoom_combo.setCurrentText("100%")
        self.render_pages()
        self.update_page_info()
    
    def render_pages(self):
        self.clear_pages()
        self.render_single_page()
    
    def clear_pages(self):
        for item in self.page_labels:
            self.pages_layout.removeWidget(item)
            item.deleteLater()
        self.page_labels.clear()
    
    def render_single_page(self):
        if not self.doc or self.current_page >= self.total_pages:
            return
        
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        
        pixmap = self.render_page_to_pixmap(self.current_page)
        if pixmap:
            label.setPixmap(pixmap)
        
        self.pages_layout.addWidget(label)
        self.page_labels.append(label)
    
    def render_page_to_pixmap(self, page_num):
        try:
            if not self.doc or page_num >= self.total_pages:
                return None
            
            page = self.doc[page_num]
            zoom_text = self.zoom_combo.currentText()
            zoom = float(zoom_text.replace("%", "")) / 100
            zoom = max(0.1, min(4.0, zoom))
            
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            return pixmap
            
        except Exception as e:
            print(f"Error rendering page {page_num}: {e}")
            return None
    
    def update_page_info(self):
        if self.total_pages > 0:
            self.page_label.setText(f"{self.current_page + 1} / {self.total_pages}")
            self.page_info_label.setText(f"Page {self.current_page + 1} of {self.total_pages}")
        else:
            self.page_label.setText("0 / 0")
            self.page_info_label.setText("No document loaded")
        
        zoom = self.zoom_combo.currentText()
        self.zoom_label.setText(zoom)
    
    def zoom_changed(self, value):
        self.render_pages()
        self.update_page_info()
    
    def zoom_in(self):
        current = self.zoom_combo.currentText()
        zoom_values = ["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%"]
        if current in zoom_values:
            idx = zoom_values.index(current)
            if idx < len(zoom_values) - 1:
                self.zoom_combo.setCurrentText(zoom_values[idx + 1])
                self.render_pages()
                self.update_page_info()
    
    def zoom_out(self):
        current = self.zoom_combo.currentText()
        zoom_values = ["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%"]
        if current in zoom_values:
            idx = zoom_values.index(current)
            if idx > 0:
                self.zoom_combo.setCurrentText(zoom_values[idx - 1])
                self.render_pages()
                self.update_page_info()
    
    def fit_to_page(self):
        self.zoom_combo.setCurrentText("100%")
        self.render_pages()
        self.update_page_info()
    
    def fit_to_width(self):
        self.zoom_combo.setCurrentText("100%")
        self.render_pages()
        self.update_page_info()
    
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.parent_window.showFullScreen()
            self.toolbar.hide()
        else:
            self.parent_window.showNormal()
            self.toolbar.show()
        self.render_pages()
    
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_pages()
            self.update_page_info()
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_pages()
            self.update_page_info()
    
    def go_to_page(self):
        try:
            page_num = int(self.page_input.text()) - 1
            if 0 <= page_num < self.total_pages:
                self.current_page = page_num
                self.render_pages()
                self.update_page_info()
                self.page_input.clear()
        except ValueError:
            pass
    
    def go_to_first_page(self):
        self.current_page = 0
        self.render_pages()
        self.update_page_info()
    
    def go_to_last_page(self):
        self.current_page = self.total_pages - 1
        self.render_pages()
        self.update_page_info()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.doc:
            self.render_pages()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
            event.accept()
        else:
            super().keyPressEvent(event)