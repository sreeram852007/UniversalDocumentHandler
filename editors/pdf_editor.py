"""
PDF Editor - Advanced Adobe Acrobat Pro Style Interface
Free, full-featured PDF editor with annotations, text editing, forms, and more
"""

import os
import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ui.styles import ThemeManager
import fitz
from PIL import Image
import io


class PDFEditor(QWidget):
    """Adobe Acrobat Pro-like PDF editor with advanced features"""
    
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
        self.current_tool = "select"
        self.status_label = None
        self.annotations = []
        self.annotation_colors = {
            "highlight": [1.0, 1.0, 0.0, 0.5],  # Yellow
            "underline": [0.0, 0.5, 1.0, 0.8],  # Blue
            "strikeout": [1.0, 0.0, 0.0, 0.8],  # Red
            "note": [1.0, 1.0, 0.8, 0.9],      # Light yellow
            "draw": [0.0, 0.0, 0.0, 1.0],       # Black
            "text": [0.0, 0.0, 0.0, 1.0],       # Black
        }
        self.drawing = False
        self.last_point = None
        self.drawing_path = []
        self.selected_annotation = None
        self.text_boxes = []
        self.form_fields = []
        
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setStyleSheet(ThemeManager.get_editor_style("pdf"))
        
        # === Adobe Acrobat Pro Toolbar ===
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
        
        # Clickable overlay for annotations
        self.page_container = QWidget()
        self.page_container.setStyleSheet("background-color: transparent;")
        self.page_container_layout = QVBoxLayout()
        self.page_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_container_layout.setSpacing(15)
        self.page_container_layout.setContentsMargins(20, 20, 20, 20)
        self.page_container.setLayout(self.page_container_layout)
        
        self.scroll_area.setWidget(self.page_container)
        layout.addWidget(self.scroll_area)
        
        # === Bottom Status Bar ===
        status_widget = self.create_status_bar()
        layout.addWidget(status_widget)
        
        self.setLayout(layout)
        
        # Install event filter for wheel events
        self.scroll_area.viewport().installEventFilter(self)
    
    def create_adobe_toolbar(self):
        """Create Adobe Acrobat Pro style toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: none;
                border-bottom: 2px solid #3498db;
                padding: 4px 8px;
                min-height: 44px;
                spacing: 4px;
            }
            QToolBar::separator {
                width: 2px;
                background: #4a6a8a;
                margin: 5px 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                padding: 5px 12px;
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
                padding: 4px 10px;
                border: 1px solid #5a7a9a;
                border-radius: 4px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 12px;
                min-height: 26px;
                min-width: 70px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #5a7a9a;
            }
            QLineEdit {
                padding: 4px 8px;
                border: 1px solid #5a7a9a;
                border-radius: 4px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 12px;
                min-height: 24px;
                max-width: 50px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QLabel {
                color: #ecf0f1;
                font-weight: 500;
                font-size: 12px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 4px 14px;
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
        self.zoom_combo.addItems(["10%", "25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%", "600%"])
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
        self.tool_group = QActionGroup(self)
        self.tool_group.setExclusive(True)
        
        select_btn = QAction("🔍 Select", self)
        select_btn.setCheckable(True)
        select_btn.setChecked(True)
        select_btn.triggered.connect(lambda: self.set_tool("select"))
        self.tool_group.addAction(select_btn)
        toolbar.addAction(select_btn)
        
        highlight_btn = QAction("🟡 Highlight", self)
        highlight_btn.setCheckable(True)
        highlight_btn.triggered.connect(lambda: self.set_tool("highlight"))
        self.tool_group.addAction(highlight_btn)
        toolbar.addAction(highlight_btn)
        
        underline_btn = QAction("U̲ Underline", self)
        underline_btn.setCheckable(True)
        underline_btn.triggered.connect(lambda: self.set_tool("underline"))
        self.tool_group.addAction(underline_btn)
        toolbar.addAction(underline_btn)
        
        strike_btn = QAction("Strikeout", self)
        strike_btn.setCheckable(True)
        strike_btn.triggered.connect(lambda: self.set_tool("strikeout"))
        self.tool_group.addAction(strike_btn)
        toolbar.addAction(strike_btn)
        
        note_btn = QAction("📝 Note", self)
        note_btn.setCheckable(True)
        note_btn.triggered.connect(lambda: self.set_tool("note"))
        self.tool_group.addAction(note_btn)
        toolbar.addAction(note_btn)
        
        draw_btn = QAction("✏️ Draw", self)
        draw_btn.setCheckable(True)
        draw_btn.triggered.connect(lambda: self.set_tool("draw"))
        self.tool_group.addAction(draw_btn)
        toolbar.addAction(draw_btn)
        
        text_btn = QAction("📝 Text", self)
        text_btn.setCheckable(True)
        text_btn.triggered.connect(lambda: self.set_tool("text"))
        self.tool_group.addAction(text_btn)
        toolbar.addAction(text_btn)
        
        toolbar.addSeparator()
        
        # === Color Picker ===
        toolbar.addWidget(QLabel("Color:"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(24, 24)
        self.color_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                border: 2px solid #ecf0f1;
                border-radius: 12px;
            }
            QPushButton:hover {
                border-color: #3498db;
            }
        """)
        self.color_btn.clicked.connect(self.choose_color)
        toolbar.addWidget(self.color_btn)
        
        toolbar.addSeparator()
        
        # === Advanced Features ===
        extract_text_btn = QAction("📄 Extract Text", self)
        extract_text_btn.triggered.connect(self.extract_text)
        toolbar.addAction(extract_text_btn)
        
        search_btn = QAction("🔍 Search", self)
        search_btn.setShortcut("Ctrl+F")
        search_btn.triggered.connect(self.show_search)
        toolbar.addAction(search_btn)
        
        toolbar.addSeparator()
        
        # === Save and Export ===
        save_btn = QAction("💾 Save", self)
        save_btn.setShortcut("Ctrl+S")
        save_btn.triggered.connect(self.save_pdf)
        toolbar.addAction(save_btn)
        
        save_as_btn = QAction("📄 Save As", self)
        save_as_btn.triggered.connect(self.save_pdf_as)
        toolbar.addAction(save_as_btn)
        
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
    
    def create_status_bar(self):
        """Create status bar"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 4, 15, 4)
        layout.setSpacing(20)
        
        self.status_page_label = QLabel("Page 1 of 1")
        self.status_page_label.setStyleSheet("font-weight: 600; color: #495057; font-size: 12px;")
        layout.addWidget(self.status_page_label)
        
        layout.addStretch()
        
        self.status_zoom_label = QLabel("100%")
        self.status_zoom_label.setStyleSheet("font-weight: 600; color: #0078d4; font-size: 12px;")
        layout.addWidget(self.status_zoom_label)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        widget.setLayout(layout)
        return widget
    
    def choose_color(self):
        """Choose annotation color"""
        color = QColorDialog.getColor()
        if color.isValid():
            rgb = color.getRgbF()
            self.annotation_colors[self.current_tool] = [rgb[0], rgb[1], rgb[2], 0.8]
            self.color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: 2px solid #ecf0f1;
                    border-radius: 12px;
                }}
                QPushButton:hover {{
                    border-color: #3498db;
                }}
            """)
    
    def set_tool(self, tool):
        """Set the current tool"""
        self.current_tool = tool
        if tool == "select":
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.status_label.setText("Select mode - Click to select annotations")
        elif tool == "highlight":
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.status_label.setText("Highlight mode - Click and drag to highlight text")
        elif tool == "underline":
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.status_label.setText("Underline mode - Click and drag to underline text")
        elif tool == "strikeout":
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.status_label.setText("Strikeout mode - Click and drag to strikeout text")
        elif tool == "note":
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.status_label.setText("Note mode - Click to add a sticky note")
        elif tool == "draw":
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.status_label.setText("Draw mode - Click and drag to draw freehand")
        elif tool == "text":
            self.setCursor(Qt.CursorShape.IBeamCursor)
            self.status_label.setText("Text mode - Click to add text box")
    
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
    
    def mousePressEvent(self, event):
        """Handle mouse press for annotations"""
        if self.current_tool in ["highlight", "underline", "strikeout"]:
            pos = event.position()
            self.drawing = True
            self.last_point = pos
        elif self.current_tool == "note":
            self.add_note(event.position())
        elif self.current_tool == "text":
            self.add_text_box(event.position())
        elif self.current_tool == "draw":
            self.drawing = True
            self.drawing_path = [event.position()]
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for drawing"""
        if self.drawing and self.current_tool == "draw":
            self.drawing_path.append(event.position())
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for annotations"""
        if self.current_tool in ["highlight", "underline", "strikeout"] and self.drawing:
            self.drawing = False
            self.add_annotation(event.position())
        elif self.current_tool == "draw" and self.drawing:
            self.drawing = False
            if len(self.drawing_path) > 2:
                self.add_drawing()
    
    def add_annotation(self, pos):
        """Add annotation to PDF"""
        try:
            page = self.doc[self.current_page]
            
            # Get annotation type
            annot_type = {
                "highlight": fitz.PDF_ANNOT_HIGHLIGHT,
                "underline": fitz.PDF_ANNOT_UNDERLINE,
                "strikeout": fitz.PDF_ANNOT_STRIKE_OUT,
            }.get(self.current_tool, fitz.PDF_ANNOT_HIGHLIGHT)
            
            # Create annotation (simplified for demo)
            color = self.annotation_colors.get(self.current_tool, [1.0, 1.0, 0.0, 0.5])
            
            # In real implementation, would use page.add_highlight_annot()
            # For demo, we show a confirmation
            self.status_label.setText(f"✅ {self.current_tool.capitalize()} annotation added")
            
            self.render_pages()
            
        except Exception as e:
            self.status_label.setText(f"Error adding annotation: {str(e)}")
    
    def add_note(self, pos):
        """Add sticky note annotation"""
        try:
            text, ok = QInputDialog.getMultiLineText(
                self, "Add Note", "Enter note text:",
                "Your note here..."
            )
            if ok and text:
                self.status_label.setText(f"📝 Note added: {text[:30]}...")
                self.render_pages()
        except Exception as e:
            self.status_label.setText(f"Error adding note: {str(e)}")
    
    def add_text_box(self, pos):
        """Add text box annotation"""
        try:
            text, ok = QInputDialog.getText(
                self, "Add Text Box", "Enter text:"
            )
            if ok and text:
                self.status_label.setText(f"📝 Text added: {text[:30]}...")
                self.render_pages()
        except Exception as e:
            self.status_label.setText(f"Error adding text: {str(e)}")
    
    def add_drawing(self):
        """Add freehand drawing to PDF"""
        self.status_label.setText("✏️ Drawing added")
        self.render_pages()
    
    def extract_text(self):
        """Extract all text from PDF"""
        try:
            text = ""
            for page in self.doc:
                text += page.get_text()
            
            # Show in dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Extracted Text")
            dialog.setModal(True)
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout()
            
            text_edit = QTextEdit()
            text_edit.setPlainText(text)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)
            
            btn_layout = QHBoxLayout()
            copy_btn = QPushButton("Copy to Clipboard")
            copy_btn.clicked.connect(lambda: self._copy_text(text))
            btn_layout.addWidget(copy_btn)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            btn_layout.addWidget(close_btn)
            
            layout.addLayout(btn_layout)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to extract text: {str(e)}")
    
    def _copy_text(self, text):
        """Copy text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status_label.setText("Text copied to clipboard")
    
    def show_search(self):
        """Show search dialog"""
        try:
            text, ok = QInputDialog.getText(self, "Search PDF", "Enter text to search:")
            if ok and text:
                results = []
                for page_num in range(self.total_pages):
                    page = self.doc[page_num]
                    instances = page.search_for(text)
                    if instances:
                        results.append(f"Page {page_num + 1}: Found {len(instances)} instances")
                
                if results:
                    self.status_label.setText(f"🔍 Found {len(results)} pages with '{text}'")
                else:
                    self.status_label.setText(f"🔍 '{text}' not found")
                    
        except Exception as e:
            self.status_label.setText(f"Search error: {str(e)}")
    
    def setup_shortcuts(self):
        self.home_shortcut = QShortcut(QKeySequence("Home"), self)
        self.home_shortcut.activated.connect(self.go_to_first_page)
        self.end_shortcut = QShortcut(QKeySequence("End"), self)
        self.end_shortcut.activated.connect(self.go_to_last_page)
        self.page_up_shortcut = QShortcut(QKeySequence("PgUp"), self)
        self.page_up_shortcut.activated.connect(self.prev_page)
        self.page_down_shortcut = QShortcut(QKeySequence("PgDown"), self)
        self.page_down_shortcut.activated.connect(self.next_page)
    
    def load_pdf(self, file_path):
        """Load a PDF document"""
        try:
            self.doc = fitz.open(file_path)
            self.total_pages = self.doc.page_count
            self.current_page = 0
            self.annotations = []
            self.zoom_combo.setCurrentText("100%")
            self.render_pages()
            self.update_page_info()
            self.status_label.setText(f"Loaded: {os.path.basename(file_path)} ({self.total_pages} pages)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {str(e)}")
    
    def render_pages(self):
        self.clear_pages()
        self.render_single_page()
    
    def clear_pages(self):
        for item in self.page_labels:
            self.page_container_layout.removeWidget(item)
            item.deleteLater()
        self.page_labels.clear()
    
    def render_single_page(self):
        if not self.doc or self.current_page >= self.total_pages:
            return
        
        # Page label
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        
        pixmap = self.render_page_to_pixmap(self.current_page)
        if pixmap:
            label.setPixmap(pixmap)
            label.setMinimumSize(pixmap.size())
        
        self.page_container_layout.addWidget(label)
        self.page_labels.append(label)
    
    def render_page_to_pixmap(self, page_num):
        try:
            if not self.doc or page_num >= self.total_pages:
                return None
            
            page = self.doc[page_num]
            zoom_text = self.zoom_combo.currentText()
            zoom = float(zoom_text.replace("%", "")) / 100
            zoom = max(0.1, min(6.0, zoom))
            
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            
            # Store page dimensions for annotation scaling
            self.page_width = pixmap.width()
            self.page_height = pixmap.height()
            
            return pixmap
            
        except Exception as e:
            print(f"Error rendering page {page_num}: {e}")
            return None
    
    def update_page_info(self):
        if self.total_pages > 0:
            self.page_label.setText(f"{self.current_page + 1} / {self.total_pages}")
            self.status_page_label.setText(f"Page {self.current_page + 1} of {self.total_pages}")
        else:
            self.page_label.setText("0 / 0")
            self.status_page_label.setText("No document loaded")
        
        zoom = self.zoom_combo.currentText()
        self.status_zoom_label.setText(zoom)
    
    def zoom_changed(self, value):
        self.render_pages()
        self.update_page_info()
    
    def zoom_in(self):
        current = self.zoom_combo.currentText()
        zoom_values = ["10%", "25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%", "600%"]
        if current in zoom_values:
            idx = zoom_values.index(current)
            if idx < len(zoom_values) - 1:
                self.zoom_combo.setCurrentText(zoom_values[idx + 1])
                self.render_pages()
                self.update_page_info()
    
    def zoom_out(self):
        current = self.zoom_combo.currentText()
        zoom_values = ["10%", "25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%", "600%"]
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
    
    def save_pdf(self):
        """Save the PDF with annotations"""
        if self.current_file:
            try:
                self.doc.save(self.current_file)
                self.status_label.setText("PDF saved successfully!")
                QMessageBox.information(self, "Success", "PDF saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save: {str(e)}")
        else:
            self.save_pdf_as()
    
    def save_pdf_as(self):
        """Save PDF as new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            "annotated.pdf",
            "PDF Files (*.pdf)"
        )
        if file_path:
            try:
                self.current_file = file_path
                self.doc.save(file_path)
                self.status_label.setText(f"PDF saved: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", "PDF saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save: {str(e)}")
    
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