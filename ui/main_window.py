"""
Main Window Module - The main application window
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import fitz
import pandas as pd

from core.file_handler import FileHandler
from core.document_compat import DocumentCompatibility
from core.pdf_viewer import PDFViewerWidget

from editors.word_editor import WordEditor
from editors.pdf_editor import PDFEditor
from editors.image_editor import ImageEditor
from editors.excel_editor import ExcelEditor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.current_file_type = None
        self.pdf_doc = None
        self.pdf_viewer_widget = None
        self.compat = DocumentCompatibility()
        self.text_edit = None
        self.text_edit_for_pptx = None
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0f1f3);
                border: none;
                border-bottom: 1px solid #d0d3d8;
                padding: 5px;
                spacing: 10px;
                min-height: 40px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 12px;
            }
            QToolBar QToolButton:hover {
                background-color: #e8eaed;
            }
            QToolBar QToolButton:pressed {
                background-color: #d2d5d9;
            }
            QListWidget {
                background-color: #ffffff;
                border: none;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-radius: 6px;
                margin: 2px 5px;
            }
            QListWidget::item:hover {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QListWidget::item:selected {
                background-color: #cce5ff;
                color: #004085;
            }
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border-top: 1px solid #dee2e6;
                padding: 3px 10px;
                font-size: 12px;
                color: #495057;
            }
            QStatusBar QLabel {
                padding: 0 10px;
                border-right: 1px solid #dee2e6;
            }
            QStatusBar QLabel:last-child {
                border-right: none;
            }
            QLabel {
                font-weight: 600;
                padding: 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QTextEdit {
                background-color: #ffffff;
                border: none;
                font-size: 12px;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar:horizontal {
                background-color: #f0f0f0;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a0a0a0;
            }
            QSplitter::handle {
                background-color: #dee2e6;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
            QSplitter::handle:pressed {
                background-color: #0078d4;
            }
        """)
        
        self.setWindowTitle("Universal Document Handler - Pro Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Top Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Splitter for sidebar and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Sidebar
        sidebar_widget = self.create_sidebar()
        splitter.addWidget(sidebar_widget)
        
        # Content area
        content_widget = self.create_content_area()
        splitter.addWidget(content_widget)
        
        splitter.setSizes([280, 1120])
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.status_file_label = QLabel("Ready")
        self.statusBar.addWidget(self.status_file_label)
        
        self.status_mode_label = QLabel("⚡ Enhanced Compatibility Mode")
        self.status_mode_label.setStyleSheet("color: #28a745; font-weight: bold;")
        self.statusBar.addPermanentWidget(self.status_mode_label)
        
        self.statusBar.showMessage("Ready - Press F11 for full-screen, Ctrl+Scroll to zoom")
    
    def create_toolbar(self):
        """Create the main toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        # Open button
        open_action = QAction("📂 Open", self)
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut("Ctrl+O")
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # Convert button
        convert_action = QAction("🔄 Convert", self)
        convert_action.triggered.connect(self.show_conversion_dialog)
        convert_action.setShortcut("Ctrl+Shift+C")
        toolbar.addAction(convert_action)
        
        toolbar.addSeparator()
        
        # View mode switcher
        view_label = QLabel("View:")
        view_label.setStyleSheet("font-weight: 600; color: #495057;")
        toolbar.addWidget(view_label)
        
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Normal", "Full Screen", "Presentation"])
        self.view_mode_combo.setMaximumWidth(120)
        self.view_mode_combo.currentTextChanged.connect(self.change_view_mode)
        toolbar.addWidget(self.view_mode_combo)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_out_btn = QAction("🔍-", self)
        zoom_out_btn.triggered.connect(self.zoom_out_global)
        toolbar.addAction(zoom_out_btn)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("font-weight: 600; color: #495057; min-width: 40px;")
        toolbar.addWidget(self.zoom_label)
        
        zoom_in_btn = QAction("🔍+", self)
        zoom_in_btn.triggered.connect(self.zoom_in_global)
        toolbar.addAction(zoom_in_btn)
        
        toolbar.addSeparator()
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        self.file_info_label = QLabel("No file loaded")
        self.file_info_label.setStyleSheet("color: #6c757d; font-weight: 400;")
        toolbar.addWidget(self.file_info_label)
        
        return toolbar
    
    def create_sidebar(self):
        """Create the sidebar with quick access only"""
        sidebar_widget = QWidget()
        sidebar_widget.setMinimumWidth(220)
        sidebar_widget.setMaximumWidth(280)
        sidebar_layout = QVBoxLayout()
        sidebar_widget.setLayout(sidebar_layout)
        
        # App Logo/Title
        app_title = QLabel("📄 UDH Pro")
        app_title.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #0078d4; 
            padding: 15px 10px 10px 10px;
            border-bottom: 2px solid #0078d4;
        """)
        sidebar_layout.addWidget(app_title)
        
        # Quick Access
        quick_access_label = QLabel("📌 Quick Access")
        quick_access_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            padding: 15px 5px 5px 5px; 
            color: #333;
        """)
        sidebar_layout.addWidget(quick_access_label)
        
        quick_access_list = QListWidget()
        quick_access_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #e8f0fe;
            }
            QListWidget::item:selected {
                background-color: #cce5ff;
                color: #004085;
            }
        """)
        
        quick_items = [
            ("🏠 Desktop", "Desktop"),
            ("📄 Documents", "Documents"),
            ("📥 Downloads", "Downloads"),
            ("🖼️ Pictures", "Pictures"),
            ("🎵 Music", "Music"),
            ("🎬 Videos", "Videos")
        ]
        
        for label, path in quick_items:
            quick_access_list.addItem(label)
            quick_access_list.setProperty("path", path)
        
        quick_access_list.itemClicked.connect(self.quick_access_clicked)
        sidebar_layout.addWidget(quick_access_list)
        
        # Recent files section
        recent_label = QLabel("🕐 Recent Files")
        recent_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            padding: 20px 5px 5px 5px; 
            color: #333;
        """)
        sidebar_layout.addWidget(recent_label)
        
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                font-size: 12px;
                color: #555;
            }
            QListWidget::item {
                padding: 8px 15px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        self.recent_list.addItem("No recent files")
        self.recent_list.setEnabled(False)
        sidebar_layout.addWidget(self.recent_list)
        
        sidebar_layout.addStretch()
        
        version_label = QLabel("v2.0 Pro Edition")
        version_label.setStyleSheet("""
            font-size: 11px; 
            color: #999; 
            padding: 10px;
            border-top: 1px solid #eee;
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)
        
        return sidebar_widget
    
    def create_content_area(self):
        """Create the content area with stacked viewers and editors"""
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_widget.setLayout(content_layout)
        
        self.viewer = QStackedWidget()
        content_layout.addWidget(self.viewer)
        
        # Index 0: Welcome page
        welcome_widget = self.create_welcome_page()
        self.viewer.addWidget(welcome_widget)
        
        # Index 1: PDF Viewer (read-only)
        self.pdf_viewer_widget = PDFViewerWidget(parent=self)
        self.viewer.addWidget(self.pdf_viewer_widget)
        
        # Index 2: Word Editor
        self.word_editor = WordEditor(self)
        self.viewer.addWidget(self.word_editor)
        
        # Index 3: Image Editor
        self.image_editor = ImageEditor(self)
        self.viewer.addWidget(self.image_editor)
        
        # Index 4: PDF Editor (Adobe style)
        self.pdf_editor = PDFEditor(self)
        self.viewer.addWidget(self.pdf_editor)
        
        # Index 5: Table viewer (legacy)
        self.table_viewer = self.create_table_viewer()
        self.viewer.addWidget(self.table_viewer)
        
        # Index 6: Excel Editor
        self.excel_editor = ExcelEditor(self)
        self.viewer.addWidget(self.excel_editor)
        
        return content_widget
    
    def create_welcome_page(self):
        """Create the welcome page with Open File button"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel("📄")
        icon_label.setStyleSheet("font-size: 120px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        welcome_label = QLabel("Universal Document Handler")
        welcome_label.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            color: #2c3e50;
            background: transparent;
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        subtitle_label = QLabel("Pro Edition - Full-Screen • Zoom • Smooth Scrolling • Keyboard Shortcuts")
        subtitle_label.setStyleSheet("font-size: 16px; color: #28a745; background: transparent;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(30)
        
        features_box = QFrame()
        features_box.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 25px;
                border: 1px solid #e9ecef;
            }
        """)
        features_box.setMaximumWidth(650)
        features_layout = QVBoxLayout()
        features_box.setLayout(features_layout)
        
        features_text = QLabel("""✨ Premium Features:
• Ctrl+Mouse Wheel = Zoom In/Out
• F11 = Full Screen Mode
• ← → = Previous/Next Page
• Home/End = First/Last Page
• 100+ File Formats Supported
• Excel with Formula Support
• PDF Annotation Tools
• Rich Text Editing
• Convert Between Formats""")
        features_text.setStyleSheet("""
            font-size: 14px; 
            color: #555; 
            line-height: 2.0;
            background-color: transparent;
            padding: 10px;
        """)
        features_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        features_layout.addWidget(features_text)
        layout.addWidget(features_box)
        
        layout.addSpacing(30)
        
        open_btn = QPushButton("📂 Open a File")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 18px 50px;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        open_btn.clicked.connect(self.open_file)
        open_btn.setFixedSize(240, 65)
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(open_btn)
        layout.addLayout(btn_layout)
        
        tip_label = QLabel("💡 Tip: Use Quick Access on the left for common folders")
        tip_label.setStyleSheet("font-size: 12px; color: #888; margin-top: 20px; background: transparent;")
        tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tip_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_table_viewer(self):
        """Create the table viewer for spreadsheets (legacy)"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        table_toolbar = QHBoxLayout()
        self.table_info_label = QLabel("")
        table_toolbar.addWidget(self.table_info_label)
        table_toolbar.addStretch()
        layout.addLayout(table_toolbar)
        
        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        layout.addWidget(self.table_widget)
        
        widget.setLayout(layout)
        return widget
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "All Supported Files (*.pdf *.docx *.xlsx *.xls *.csv *.pptx *.ppt *.txt *.md *.epub *.html *.json *.xml *.yaml *.yml *.rtf *.odt *.ods *.odp *.jpg *.jpeg *.png *.gif *.bmp *.webp);;All Files (*.*)"
        )
        if file_path:
            self.load_file(file_path)
            self.add_recent_file(file_path)
    
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        if self.recent_list.item(0).text() == "No recent files":
            self.recent_list.clear()
            self.recent_list.setEnabled(True)
        
        for i in range(self.recent_list.count()):
            if self.recent_list.item(i).text() == os.path.basename(file_path):
                self.recent_list.takeItem(i)
                break
        
        self.recent_list.insertItem(0, f"📄 {os.path.basename(file_path)}")
        self.recent_list.item(0).setData(Qt.ItemDataRole.UserRole, file_path)
        
        while self.recent_list.count() > 10:
            self.recent_list.takeItem(self.recent_list.count() - 1)
        
        self.recent_list.itemClicked.connect(self.recent_file_clicked)
    
    def recent_file_clicked(self, item):
        """Handle recent file click"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            self.load_file(file_path)
        else:
            self.recent_list.takeItem(self.recent_list.row(item))
            if self.recent_list.count() == 0:
                self.recent_list.addItem("No recent files")
                self.recent_list.setEnabled(False)
    
    def load_file(self, file_path):
        self.current_file = file_path
        self.current_file_type = FileHandler.detect_file_type(file_path)
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        size_str = self.format_file_size(file_size)
        self.file_info_label.setText(f"{file_name} ({size_str})")
        self.status_file_label.setText(f"📄 {file_name}")
        
        self.statusBar.showMessage(f"Loading: {file_name}")
        
        try:
            if self.current_file_type == 'pdf':
                self.pdf_editor.load_pdf(file_path)
                self.viewer.setCurrentIndex(4)
            elif self.current_file_type == 'word':
                self.word_editor.load_document(file_path)
                self.viewer.setCurrentIndex(2)
            elif self.current_file_type in ['excel', 'csv']:
                self.excel_editor.load_file(file_path)
                self.viewer.setCurrentIndex(6)
            elif self.current_file_type == 'powerpoint':
                self.load_powerpoint_enhanced(file_path)
            elif self.current_file_type == 'image':
                self.image_editor.load_image(file_path)
                self.viewer.setCurrentIndex(3)
            elif self.current_file_type == 'text':
                self.load_text(file_path)
            elif self.current_file_type == 'markdown':
                self.load_markdown(file_path)
            elif self.current_file_type == 'epub':
                self.load_epub(file_path)
            elif self.current_file_type in ['html', 'xml', 'json', 'yaml']:
                self.load_code_file(file_path)
            else:
                self.load_unknown_file(file_path)
        except Exception as e:
            self.show_error(f"Error loading file: {str(e)}")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)
                self.word_editor.text_edit.setText(f"[Error loading as {self.current_file_type} - Showing as text]\n\n{content}\n\n[...truncated]")
                self.viewer.setCurrentIndex(2)
            except:
                pass
        
        self.statusBar.showMessage(f"Loaded: {file_name}")
    
    def format_file_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def load_pdf(self, file_path):
        """Load PDF in viewer (read-only)"""
        try:
            self.pdf_doc = fitz.open(file_path)
            self.pdf_viewer_widget.load_document(self.pdf_doc)
            self.viewer.setCurrentIndex(1)
            self.statusBar.showMessage(f"PDF loaded: {os.path.basename(file_path)} - Press F11 for full-screen")
        except Exception as e:
            self.show_error(f"Error loading PDF: {str(e)}")
    
    def load_word_enhanced(self, file_path):
        """Legacy method - kept for compatibility"""
        try:
            html_content = DocumentCompatibility.render_docx_compatibility(file_path)
            self.word_editor.text_edit.setHtml(html_content)
            self.viewer.setCurrentIndex(2)
            self.statusBar.showMessage("Word document loaded with enhanced formatting")
        except Exception as e:
            self.show_error(f"Error loading Word: {str(e)}")
    
    def load_powerpoint_enhanced(self, file_path):
        try:
            text = DocumentCompatibility.render_pptx_compatibility(file_path)
            if self.text_edit_for_pptx is None:
                self.text_edit_for_pptx = QTextEdit()
                self.text_edit_for_pptx.setFont(QFont("Segoe UI", 12))
                self.text_edit_for_pptx.setStyleSheet("""
                    QTextEdit {
                        background-color: #ffffff;
                        border: none;
                        padding: 20px;
                        margin: 0px;
                    }
                """)
                self.text_edit_for_pptx.setReadOnly(True)
                self.viewer.addWidget(self.text_edit_for_pptx)
            
            self.text_edit_for_pptx.setText(text)
            self.viewer.setCurrentIndex(self.viewer.count() - 1)
            self.statusBar.showMessage("PowerPoint loaded with enhanced compatibility")
        except Exception as e:
            self.show_error(f"Error loading PowerPoint: {str(e)}")
    
    def load_spreadsheet_enhanced(self, file_path):
        try:
            if self.current_file_type == 'csv':
                df = pd.read_csv(file_path)
                self.table_info_label.setText(f"📊 CSV: {df.shape[0]} rows × {df.shape[1]} columns")
            else:
                content = DocumentCompatibility.render_excel_compatibility(file_path)
                if "--- Sheet:" in content:
                    self.word_editor.text_edit.setText(content)
                    self.viewer.setCurrentIndex(2)
                    self.statusBar.showMessage("Excel loaded with enhanced compatibility")
                    return
                else:
                    df = pd.read_excel(file_path)
                    self.table_info_label.setText(f"📊 {os.path.basename(file_path)}")
            
            rows, cols = df.shape
            self.table_widget.setRowCount(min(rows, 1000))
            self.table_widget.setColumnCount(cols)
            self.table_widget.setHorizontalHeaderLabels(df.columns.tolist())
            
            for i in range(min(rows, 1000)):
                for j in range(cols):
                    value = str(df.iloc[i, j])
                    self.table_widget.setItem(i, j, QTableWidgetItem(value))
            
            self.table_widget.resizeColumnsToContents()
            self.viewer.setCurrentIndex(5)
            self.statusBar.showMessage("Spreadsheet loaded")
            
        except Exception as e:
            self.show_error(f"Error loading spreadsheet: {str(e)}")
    
    def load_text(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            self.word_editor.text_edit.setText(content)
            self.viewer.setCurrentIndex(2)
            self.statusBar.showMessage(f"Text file loaded: {os.path.basename(file_path)}")
        except Exception as e:
            self.show_error(f"Error loading text: {str(e)}")
    
    def load_markdown(self, file_path):
        try:
            import markdown
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            html_content = markdown.markdown(content)
            self.word_editor.text_edit.setHtml(html_content)
            self.viewer.setCurrentIndex(2)
            self.statusBar.showMessage(f"Markdown loaded: {os.path.basename(file_path)}")
        except Exception as e:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            self.word_editor.text_edit.setText(content)
            self.viewer.setCurrentIndex(2)
    
    def load_epub(self, file_path):
        try:
            import ebooklib
            from ebooklib import epub
            
            book = epub.read_epub(file_path)
            content = []
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    content.append(item.get_content().decode('utf-8', errors='ignore'))
            
            full_text = "\n".join(content[:10])
            self.word_editor.text_edit.setText(f"📚 EPUB: {os.path.basename(file_path)}\n\n{full_text}\n\n[...truncated]")
            self.viewer.setCurrentIndex(2)
            self.statusBar.showMessage(f"EPUB loaded: {os.path.basename(file_path)}")
        except Exception as e:
            self.show_error(f"Error loading EPUB: {str(e)}")
    
    def load_code_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            self.word_editor.text_edit.setText(content)
            self.viewer.setCurrentIndex(2)
            self.statusBar.showMessage(f"Code file loaded: {os.path.basename(file_path)}")
        except Exception as e:
            self.show_error(f"Error loading file: {str(e)}")
    
    def load_image(self, file_path):
        """Legacy method - image editor handles this now"""
        try:
            self.image_editor.load_image(file_path)
            self.viewer.setCurrentIndex(3)
            self.statusBar.showMessage(f"Image loaded: {os.path.basename(file_path)}")
        except Exception as e:
            self.show_error(f"Error loading image: {str(e)}")
    
    def load_unknown_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10000)
            self.word_editor.text_edit.setText(f"[Unsupported file type - Showing as text]\n\n{content}\n\n[...truncated]")
            self.viewer.setCurrentIndex(2)
        except:
            self.show_error(f"Unsupported file type: {self.current_file_type}")
    
    def quick_access_clicked(self, item):
        """Handle quick access click"""
        folder_name = item.text().split(" ")[-1]
        folder_path = os.path.expanduser(f"~/{folder_name}")
        
        if folder_name == "Desktop":
            folder_path = os.path.expanduser("~/Desktop")
        
        if os.path.exists(folder_path):
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                f"Open from {folder_name}",
                folder_path,
                "All Supported Files (*.pdf *.docx *.xlsx *.xls *.csv *.pptx *.ppt *.txt *.md *.epub *.html *.json *.xml *.yaml *.yml *.rtf *.odt *.ods *.odp *.jpg *.jpeg *.png *.gif *.bmp *.webp);;All Files (*.*)"
            )
            if file_path:
                self.load_file(file_path)
                self.add_recent_file(file_path)
    
    def change_view_mode(self, mode):
        """Change view mode"""
        if mode == "Full Screen":
            self.showFullScreen()
        elif mode == "Presentation":
            pass
        else:
            self.showNormal()
    
    def zoom_in_global(self):
        """Global zoom in"""
        current_index = self.viewer.currentIndex()
        if current_index == 1:
            self.pdf_viewer_widget.zoom_in()
        elif current_index == 2:
            self.word_editor.zoom_in()
        elif current_index == 3:
            self.image_editor.zoom_in()
        elif current_index == 4:
            self.pdf_editor.zoom_in()
    
    def zoom_out_global(self):
        """Global zoom out"""
        current_index = self.viewer.currentIndex()
        if current_index == 1:
            self.pdf_viewer_widget.zoom_out()
        elif current_index == 2:
            self.word_editor.zoom_out()
        elif current_index == 3:
            self.image_editor.zoom_out()
        elif current_index == 4:
            self.pdf_editor.zoom_out()
    
    def show_conversion_dialog(self):
        """Open conversion dialog for current file"""
        if not self.current_file:
            QMessageBox.information(self, "No File", "Please open a file first.")
            return
        
        from ui.conversion_dialog import ConversionDialog
        
        dialog = ConversionDialog(self.current_file, self.current_file_type, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            output_file = dialog.get_output_file()
            if output_file:
                reply = QMessageBox.question(
                    self,
                    "Open Converted File",
                    "Would you like to open the converted file?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.load_file(output_file)
    
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.statusBar.showMessage("Error loading file")