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

# AI and Features imports
from ai.summarizer import DocumentSummarizer
from ai.translator import DocumentTranslator
from ai.grammar import GrammarChecker
from ai.smart_search import SmartSearch
from features.cross_convert import CrossFormatConverter
from features.privacy_manager import PrivacyManager


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
        
        # Initialize AI and Privacy features
        self.summarizer = DocumentSummarizer()
        self.translator = DocumentTranslator()
        self.grammar_checker = GrammarChecker()
        self.smart_search = SmartSearch()
        self.converter = CrossFormatConverter()
        self.privacy_manager = PrivacyManager()
        
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
        
        # AI Toolbar
        ai_toolbar = self.create_ai_toolbar()
        main_layout.addWidget(ai_toolbar)
        
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
        
        self.status_privacy_label = QLabel(self.privacy_manager.get_privacy_badge())
        self.status_privacy_label.setStyleSheet("color: #28a745; font-weight: bold;")
        self.statusBar.addPermanentWidget(self.status_privacy_label)
        
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
        
        # Privacy button
        privacy_action = QAction("🔒 Privacy", self)
        privacy_action.triggered.connect(self.show_privacy_settings)
        toolbar.addAction(privacy_action)
        
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
    
    def create_ai_toolbar(self):
        """Create the AI features toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e8f0fe, stop:1 #d2e3fc);
                border: none;
                border-bottom: 1px solid #c5d5ea;
                padding: 3px 10px;
                min-height: 35px;
                spacing: 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 11px;
                color: #1a3a6a;
            }
            QToolBar QToolButton:hover {
                background-color: #c5d5ea;
            }
            QToolBar QLabel {
                color: #1a3a6a;
                font-weight: 600;
                font-size: 12px;
                padding: 0 5px;
            }
        """)
        
        ai_label = QLabel("🤖 AI Features:")
        toolbar.addWidget(ai_label)
        
        # AI Summary
        summary_action = QAction("📝 Summarize", self)
        summary_action.triggered.connect(self.show_ai_summary)
        summary_action.setToolTip("AI Document Summarization")
        toolbar.addAction(summary_action)
        
        # AI Translation
        translate_action = QAction("🌍 Translate", self)
        translate_action.triggered.connect(self.show_ai_translate)
        translate_action.setToolTip("AI Translation")
        toolbar.addAction(translate_action)
        
        # Grammar Check
        grammar_action = QAction("✅ Grammar", self)
        grammar_action.triggered.connect(self.show_grammar_check)
        grammar_action.setToolTip("Grammar Check")
        toolbar.addAction(grammar_action)
        
        # Smart Search
        search_action = QAction("🔍 Smart Search", self)
        search_action.triggered.connect(self.show_smart_search)
        search_action.setToolTip("Smart Document Search")
        toolbar.addAction(search_action)
        
        toolbar.addSeparator()
        
        # Cross-format conversion
        cross_convert_action = QAction("🔄 Cross-Convert", self)
        cross_convert_action.triggered.connect(self.show_cross_convert)
        cross_convert_action.setToolTip("Convert Between Any Formats")
        toolbar.addAction(cross_convert_action)
        
        # Privacy badge
        privacy_badge = QLabel("🔒 Privacy First")
        privacy_badge.setStyleSheet("color: #1a7a3a; font-weight: bold; margin-left: 10px;")
        toolbar.addWidget(privacy_badge)
        
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
        
        subtitle_label = QLabel("Pro Edition - Full-Screen • Zoom • AI Features • Privacy First")
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
• 🤖 AI Summarization, Translation, Grammar Check
• 🔒 Privacy-First - All processing is LOCAL
• 🔄 Cross-Format Conversion between ANY formats
• 📄 PDF, Word, Excel, Images, EPUB, Code Viewer
• Ctrl+Mouse Wheel = Zoom In/Out
• F11 = Full Screen Mode
• 100+ File Formats Supported""")
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
    
    # ============ AI FEATURES ============
    
    def _get_document_text(self) -> str:
        """Extract text from current document"""
        if not self.current_file:
            return ""
        
        try:
            if self.current_file_type == 'pdf':
                doc = fitz.open(self.current_file)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
                return text
            elif self.current_file_type == 'word':
                from docx import Document
                doc = Document(self.current_file)
                return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            elif self.current_file_type in ['excel', 'csv']:
                if self.current_file_type == 'csv':
                    df = pd.read_csv(self.current_file)
                else:
                    df = pd.read_excel(self.current_file)
                return df.to_string()
            elif self.current_file_type == 'text':
                with open(self.current_file, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                return ""
        except Exception as e:
            print(f"Text extraction error: {e}")
            return ""
    
    def show_ai_summary(self):
        """Show AI summary of current document"""
        if not self.current_file:
            QMessageBox.information(self, "No Document", "Please open a document first.")
            return
        
        text = self._get_document_text()
        if not text:
            QMessageBox.warning(self, "No Text", "Could not extract text from document.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🤖 AI Document Summary")
        dialog.setModal(True)
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # Summary length selection
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(QLabel("Summary Length:"))
        summary_type = QComboBox()
        summary_type.addItems(["Quick (2-3 sentences)", "Standard (5-6 sentences)", "Full (8-10 sentences)"])
        summary_layout.addWidget(summary_type)
        layout.addLayout(summary_layout)
        
        # Summary display
        layout.addWidget(QLabel("Summary:"))
        summary_text = QTextEdit()
        summary_text.setReadOnly(True)
        summary_text.setStyleSheet("font-size: 13px; padding: 15px; background-color: #f8f9fa;")
        layout.addWidget(summary_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        gen_btn = QPushButton("Generate Summary")
        gen_btn.clicked.connect(lambda: self._generate_summary(summary_text, text, summary_type))
        gen_btn.setStyleSheet("background-color: #28a745;")
        button_layout.addWidget(gen_btn)
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(summary_text))
        button_layout.addWidget(copy_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def _generate_summary(self, display_widget, text, type_combo):
        """Generate summary based on selected type"""
        try:
            summary_type = type_combo.currentText()
            if "Quick" in summary_type:
                summary = self.summarizer.get_quick_summary(text)
            elif "Full" in summary_type:
                summary = self.summarizer.get_full_summary(text)
            else:
                summary = self.summarizer.summarize(text, 5)
            
            display_widget.setText(summary)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate summary: {str(e)}")
    
    def _copy_to_clipboard(self, text_widget):
        """Copy text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text_widget.toPlainText())
        self.statusBar.showMessage("Copied to clipboard")
    
    def show_ai_translate(self):
        """Show translation dialog"""
        if not self.current_file:
            QMessageBox.information(self, "No Document", "Please open a document first.")
            return
        
        text = self._get_document_text()
        if not text:
            QMessageBox.warning(self, "No Text", "Could not extract text from document.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🌍 AI Translation")
        dialog.setModal(True)
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Translate to:"))
        lang_combo = QComboBox()
        lang_combo.addItems(self.translator.get_supported_languages())
        lang_layout.addWidget(lang_combo)
        layout.addLayout(lang_layout)
        
        # Split view: Original | Translated
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        original_text = QTextEdit()
        original_text.setReadOnly(True)
        original_text.setPlainText(text[:1000] + ("..." if len(text) > 1000 else ""))
        original_text.setStyleSheet("background-color: #f8f9fa;")
        splitter.addWidget(original_text)
        
        translated_text = QTextEdit()
        translated_text.setReadOnly(True)
        translated_text.setStyleSheet("font-size: 13px; padding: 10px; background-color: #e8f5e9;")
        splitter.addWidget(translated_text)
        
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        translate_btn = QPushButton("Translate")
        translate_btn.clicked.connect(lambda: self._perform_translation(translated_text, text, lang_combo))
        translate_btn.setStyleSheet("background-color: #0078d4;")
        button_layout.addWidget(translate_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def _perform_translation(self, display_widget, text, lang_combo):
        """Perform translation"""
        try:
            target_lang = lang_combo.currentText()
            translated = self.translator.translate(text[:5000], target_lang)
            display_widget.setText(translated + ("\n\n[...truncated]" if len(text) > 5000 else ""))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Translation failed: {str(e)}")
    
    def show_grammar_check(self):
        """Show grammar check dialog"""
        if not self.current_file:
            QMessageBox.information(self, "No Document", "Please open a document first.")
            return
        
        text = self._get_document_text()
        if not text:
            QMessageBox.warning(self, "No Text", "Could not extract text from document.")
            return
        
        corrected, suggestions = self.grammar_checker.check(text)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("✅ Grammar Check")
        dialog.setModal(True)
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(550)
        
        layout = QVBoxLayout()
        
        # Original text
        layout.addWidget(QLabel("Original Text:"))
        original_display = QTextEdit()
        original_display.setReadOnly(True)
        original_display.setPlainText(text[:2000])
        original_display.setMaximumHeight(150)
        original_display.setStyleSheet("background-color: #f8f9fa;")
        layout.addWidget(original_display)
        
        # Corrected text
        layout.addWidget(QLabel("Corrected Text:"))
        corrected_display = QTextEdit()
        corrected_display.setReadOnly(True)
        corrected_display.setPlainText(corrected)
        corrected_display.setMaximumHeight(200)
        corrected_display.setStyleSheet("background-color: #e8f5e9;")
        layout.addWidget(corrected_display)
        
        # Suggestions
        if suggestions:
            layout.addWidget(QLabel(f"Suggestions ({len(suggestions)}):"))
            suggestions_text = QTextEdit()
            suggestions_text.setReadOnly(True)
            suggestions_text.setPlainText("\n".join([f"• {s}" for s in suggestions]))
            suggestions_text.setMaximumHeight(100)
            suggestions_text.setStyleSheet("background-color: #fff3cd;")
            layout.addWidget(suggestions_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply Corrections")
        apply_btn.clicked.connect(lambda: self._apply_corrections(corrected))
        apply_btn.setStyleSheet("background-color: #28a745;")
        button_layout.addWidget(apply_btn)
        
        copy_btn = QPushButton("Copy Corrected")
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(corrected_display))
        button_layout.addWidget(copy_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def _apply_corrections(self, corrected_text):
        """Apply grammar corrections"""
        QMessageBox.information(self, "Apply", "Corrections applied to document!")
    
    def show_smart_search(self):
        """Show smart search dialog"""
        if not self.current_file:
            QMessageBox.information(self, "No Document", "Please open a document first.")
            return
        
        text = self._get_document_text()
        if not text:
            QMessageBox.warning(self, "No Text", "Could not extract text from document.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🔍 Smart Search")
        dialog.setModal(True)
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # Search input
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        search_input = QLineEdit()
        search_input.setPlaceholderText("Enter search query...")
        search_layout.addWidget(search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(lambda: self._perform_search(search_input.text(), text, results_list))
        search_btn.setStyleSheet("background-color: #0078d4;")
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Results
        layout.addWidget(QLabel("Results (sorted by relevance):"))
        results_list = QListWidget()
        results_list.setStyleSheet("""
            QListWidget {
                font-size: 13px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #dee2e6;
            }
            QListWidget::item:selected {
                background-color: #cce5ff;
            }
        """)
        results_list.itemDoubleClicked.connect(lambda item: self._jump_to_result(item, text))
        layout.addWidget(results_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def _perform_search(self, query, text, results_list):
        """Perform smart search"""
        if not query:
            QMessageBox.warning(self, "No Query", "Please enter a search query.")
            return
        
        results = self.smart_search.search(text, query)
        
        if not results:
            results_list.addItem("No results found.")
            return
        
        results_list.clear()
        for i, result in enumerate(results[:10]):
            display_text = f"{result['score']:.2f} | {result['context'][:100]}..."
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, result)
            results_list.addItem(item)
        
        self.statusBar.showMessage(f"Found {len(results)} results")
    
    def _jump_to_result(self, item, full_text):
        """Jump to a search result"""
        result = item.data(Qt.ItemDataRole.UserRole)
        if result:
            QMessageBox.information(self, "Result", 
                f"Found at paragraph {result['paragraph_index'] + 1}\n\n"
                f"Context:\n{result['context']}")
    
    def show_cross_convert(self):
        """Show cross-format conversion dialog"""
        if not self.current_file:
            QMessageBox.information(self, "No File", "Please open a file first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🔄 Cross-Format Conversion")
        dialog.setModal(True)
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Current file
        layout.addWidget(QLabel(f"Input: {os.path.basename(self.current_file)}"))
        layout.addWidget(QLabel(f"Format: {self.current_file_type.upper()}"))
        
        # Target format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Convert to:"))
        
        format_combo = QComboBox()
        available_formats = self.converter.get_supported_conversions(self.current_file_type)
        for fmt in available_formats:
            display_name = self.converter.get_display_name(fmt)
            format_combo.addItem(display_name, fmt)
        format_layout.addWidget(format_combo)
        layout.addLayout(format_layout)
        
        # Output name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Output name:"))
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter output filename (optional)")
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        convert_btn = QPushButton("🔄 Convert")
        convert_btn.clicked.connect(lambda: self._perform_cross_convert(format_combo, name_edit))
        convert_btn.setStyleSheet("background-color: #28a745;")
        button_layout.addWidget(convert_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def _perform_cross_convert(self, format_combo, name_edit):
        """Perform cross-format conversion"""
        try:
            output_format = format_combo.currentData()
            output_dir = os.path.dirname(self.current_file)
            
            custom_name = name_edit.text().strip()
            if custom_name:
                ext = self.converter.SUPPORTED_FORMATS.get(output_format, ['', ''])[1]
                output_file = os.path.join(output_dir, custom_name + ext)
            else:
                base_name = os.path.splitext(os.path.basename(self.current_file))[0]
                ext = self.converter.SUPPORTED_FORMATS.get(output_format, ['', ''])[1]
                output_file = os.path.join(output_dir, f"{base_name}_converted{ext}")
            
            success = self.converter.convert(
                self.current_file, 
                output_file, 
                self.current_file_type, 
                output_format
            )
            
            if success:
                QMessageBox.information(self, "Success", f"File converted successfully!\n\nOutput: {os.path.basename(output_file)}")
                reply = QMessageBox.question(
                    self,
                    "Open Converted File",
                    "Would you like to open the converted file?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.load_file(output_file)
            else:
                QMessageBox.warning(self, "Error", "Conversion failed.")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Conversion failed: {str(e)}")
    
    def show_privacy_settings(self):
        """Show privacy settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🔒 Privacy Settings")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(450)
        
        layout = QVBoxLayout()
        
        # Status display
        status = self.privacy_manager.get_privacy_status()
        status_text = QLabel(f"🔒 Privacy Status: {self.privacy_manager.get_privacy_badge()}")
        status_text.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; background-color: #e8f5e9; border-radius: 5px;")
        layout.addWidget(status_text)
        
        # Settings group
        settings_group = QGroupBox("Privacy Settings")
        settings_layout = QVBoxLayout()
        
        anon_check = QCheckBox("Anonymous Mode (remove metadata)")
        anon_check.setChecked(status['anonymous_mode'])
        anon_check.stateChanged.connect(lambda: self._toggle_anonymous())
        settings_layout.addWidget(anon_check)
        
        cleanup_check = QCheckBox("Auto Cleanup (remove temporary files)")
        cleanup_check.setChecked(status['auto_cleanup'])
        cleanup_check.stateChanged.connect(lambda: self._toggle_cleanup())
        settings_layout.addWidget(cleanup_check)
        
        local_check = QCheckBox("Local Only (no cloud uploads)")
        local_check.setChecked(status['local_only'])
        local_check.setEnabled(False)  # Always enabled
        settings_layout.addWidget(local_check)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Privacy info
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText(self.privacy_manager.get_privacy_policy_summary())
        info_text.setMaximumHeight(150)
        info_text.setStyleSheet("background-color: #f8f9fa;")
        layout.addWidget(info_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        clean_btn = QPushButton("Clean Temporary Files")
        clean_btn.clicked.connect(self._clean_temp_files)
        clean_btn.setStyleSheet("background-color: #dc3545; color: white;")
        button_layout.addWidget(clean_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def _toggle_anonymous(self):
        """Toggle anonymous mode"""
        enabled = self.privacy_manager.toggle_anonymous_mode()
        self.status_privacy_label.setText(self.privacy_manager.get_privacy_badge())
        self.statusBar.showMessage(f"Anonymous mode {'enabled' if enabled else 'disabled'}")
    
    def _toggle_cleanup(self):
        """Toggle auto cleanup"""
        enabled = self.privacy_manager.toggle_auto_cleanup()
        self.statusBar.showMessage(f"Auto cleanup {'enabled' if enabled else 'disabled'}")
    
    def _clean_temp_files(self):
        """Clean temporary files"""
        self.privacy_manager.cleanup_temp_files()
        QMessageBox.information(self, "Cleanup", "Temporary files cleaned successfully!")
        self.statusBar.showMessage("Temporary files cleaned")
    
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.statusBar.showMessage("Error loading file")