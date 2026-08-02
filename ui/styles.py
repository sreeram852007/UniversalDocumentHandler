"""
Premium UI Styles for Universal Document Handler
- Adobe Dark/Light Theme
- Microsoft Office Ribbon Style
"""

# ============ MAIN APPLICATION STYLES ============

MAIN_STYLE = """
    /* Global Reset */
    * {
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    }
    
    QMainWindow {
        background-color: #f5f6fa;
    }
    
    /* ===== PREMIUM RIBBON TOOLBAR ===== */
    QToolBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:0.5 #f8f9fa, stop:1 #e9ecef);
        border: none;
        border-bottom: 2px solid #0078d4;
        padding: 3px 5px;
        spacing: 3px;
        min-height: 45px;
        font-size: 12px;
    }
    
    QToolBar::separator {
        width: 2px;
        background: #dee2e6;
        margin: 5px 3px;
    }
    
    QToolBar QToolButton {
        background-color: transparent;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: 500;
        font-size: 12px;
        color: #2c3e50;
        min-width: 32px;
        min-height: 28px;
    }
    
    QToolBar QToolButton:hover {
        background-color: #e8eaed;
        border: 1px solid #d0d3d8;
    }
    
    QToolBar QToolButton:pressed {
        background-color: #cce5ff;
        border: 1px solid #0078d4;
    }
    
    QToolBar QToolButton:checked {
        background-color: #cce5ff;
        border: 1px solid #0078d4;
        border-radius: 4px;
    }
    
    QToolBar QToolButton[class="ribbon"] {
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    QToolBar QToolButton[class="ribbon"]:hover {
        background-color: #e8eaed;
        border: 1px solid #d0d3d8;
    }
    
    /* ===== MODERN STATUS BAR ===== */
    QStatusBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f8f9fa, stop:1 #e9ecef);
        border-top: 2px solid #0078d4;
        padding: 4px 12px;
        font-size: 12px;
        color: #495057;
        min-height: 28px;
    }
    
    QStatusBar::item {
        border: none;
    }
    
    QStatusBar QLabel {
        padding: 0 12px;
        border-right: 1px solid #dee2e6;
    }
    
    QStatusBar QLabel:last-child {
        border-right: none;
    }
    
    /* ===== SIDEBAR ===== */
    QListWidget {
        background-color: #ffffff;
        border: none;
        font-size: 13px;
        outline: none;
    }
    
    QListWidget::item {
        padding: 10px 16px;
        border-radius: 6px;
        margin: 2px 6px;
    }
    
    QListWidget::item:hover {
        background-color: #e8f0fe;
        color: #1a73e8;
    }
    
    QListWidget::item:selected {
        background-color: #cce5ff;
        color: #004085;
    }
    
    /* ===== SCROLLBARS ===== */
    QScrollBar:vertical {
        background-color: #f0f0f0;
        width: 14px;
        border-radius: 7px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #c1c1c1;
        border-radius: 7px;
        min-height: 30px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #a0a0a0;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    
    QScrollBar:horizontal {
        background-color: #f0f0f0;
        height: 14px;
        border-radius: 7px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #c1c1c1;
        border-radius: 7px;
        min-width: 30px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #a0a0a0;
    }
    
    /* ===== BUTTONS ===== */
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
    
    QPushButton[class="primary"] {
        background-color: #0078d4;
    }
    
    QPushButton[class="success"] {
        background-color: #28a745;
    }
    
    QPushButton[class="danger"] {
        background-color: #dc3545;
    }
    
    QPushButton[class="warning"] {
        background-color: #ffc107;
        color: #212529;
    }
    
    /* ===== COMBOBOX ===== */
    QComboBox {
        padding: 5px 12px;
        border: 1px solid #ced4da;
        border-radius: 4px;
        background-color: white;
        font-size: 12px;
        min-height: 28px;
    }
    
    QComboBox:hover {
        border-color: #0078d4;
    }
    
    QComboBox:focus {
        border-color: #0078d4;
        outline: none;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    
    QComboBox QAbstractItemView {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 4px;
        background-color: white;
    }
    
    /* ===== LINE EDIT ===== */
    QLineEdit {
        padding: 5px 12px;
        border: 1px solid #ced4da;
        border-radius: 4px;
        font-size: 12px;
        min-height: 28px;
        background-color: white;
    }
    
    QLineEdit:focus {
        border-color: #0078d4;
        outline: none;
    }
    
    /* ===== TAB WIDGET ===== */
    QTabWidget::pane {
        border: 1px solid #dee2e6;
        border-radius: 6px;
        background-color: white;
        margin-top: -1px;
    }
    
    QTabBar::tab {
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        background-color: #f8f9fa;
        font-weight: 500;
        font-size: 13px;
    }
    
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 2px solid #0078d4;
    }
    
    QTabBar::tab:hover {
        background-color: #e8eaed;
    }
    
    /* ===== TABLE WIDGET ===== */
    QTableWidget {
        background-color: white;
        border: none;
        gridline-color: #dee2e6;
        font-size: 12px;
    }
    
    QTableWidget::item {
        padding: 6px 10px;
    }
    
    QTableWidget::item:selected {
        background-color: #cce5ff;
        color: #004085;
    }
    
    QHeaderView::section {
        background-color: #f8f9fa;
        padding: 6px 12px;
        border: 1px solid #dee2e6;
        font-weight: 600;
        font-size: 12px;
    }
    
    /* ===== SPLITTER ===== */
    QSplitter::handle {
        background-color: #dee2e6;
        width: 3px;
    }
    
    QSplitter::handle:hover {
        background-color: #0078d4;
    }
    
    /* ===== MENU BAR ===== */
    QMenuBar {
        background-color: #ffffff;
        border-bottom: 1px solid #dee2e6;
        padding: 2px 5px;
        font-size: 13px;
    }
    
    QMenuBar::item {
        padding: 5px 12px;
        border-radius: 4px;
    }
    
    QMenuBar::item:selected {
        background-color: #e8eaed;
    }
    
    QMenu {
        background-color: white;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 6px 30px 6px 20px;
        border-radius: 4px;
    }
    
    QMenu::item:selected {
        background-color: #e8eaed;
    }
    
    QMenu::separator {
        height: 1px;
        background: #dee2e6;
        margin: 4px 8px;
    }
"""

# ============ PDF EDITOR STYLE (Adobe-like) ============

PDF_EDITOR_STYLE = """
    QScrollArea {
        background-color: #e8e8e8;
        border: none;
    }
    
    QToolBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #2c3e50, stop:1 #34495e);
        border: none;
        border-bottom: 2px solid #3498db;
        padding: 3px 5px;
        min-height: 40px;
    }
    
    QToolBar QToolButton {
        background-color: transparent;
        padding: 5px 10px;
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
    }
    
    QLineEdit:focus {
        border-color: #3498db;
    }
    
    QLabel {
        color: #ecf0f1;
        font-weight: 500;
    }
    
    QPushButton {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: 600;
    }
    
    QPushButton:hover {
        background-color: #2980b9;
    }
"""

# ============ WORD EDITOR STYLE (MS Word-like) ============

WORD_EDITOR_STYLE = """
    QTextEdit {
        background-color: white;
        border: none;
        padding: 40px 50px;
        font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
        font-size: 12pt;
        line-height: 1.6;
        color: #1a1a1a;
    }
    
    QTextEdit:focus {
        border: none;
    }
    
    QScrollArea {
        background-color: #e8e8e8;
        border: none;
    }
    
    QToolBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #f0f1f3);
        border: none;
        border-bottom: 2px solid #0078d4;
        padding: 2px 5px;
        min-height: 38px;
    }
    
    QToolBar QToolButton {
        background-color: transparent;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
        font-size: 12px;
        color: #2c3e50;
    }
    
    QToolBar QToolButton:hover {
        background-color: #e8eaed;
    }
    
    QToolBar QToolButton:checked {
        background-color: #cce5ff;
        border: 1px solid #0078d4;
    }
    
    QComboBox {
        padding: 3px 8px;
        border: 1px solid #ced4da;
        border-radius: 4px;
        background-color: white;
        font-size: 12px;
        min-height: 24px;
    }
    
    QComboBox:hover {
        border-color: #0078d4;
    }
    
    QStatusBar {
        background: #f8f9fa;
        border-top: 1px solid #dee2e6;
        padding: 2px 10px;
        font-size: 12px;
        color: #495057;
        min-height: 24px;
    }
"""

# ============ EXCEL EDITOR STYLE ============

EXCEL_EDITOR_STYLE = """
    QToolBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:0.5 #f8f9fa, stop:1 #e9ecef);
        border: none;
        border-bottom: 2px solid #217346;
        padding: 2px 5px;
        min-height: 38px;
    }
    
    QToolBar QToolButton {
        background-color: transparent;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
        font-size: 12px;
        color: #2c3e50;
    }
    
    QToolBar QToolButton:hover {
        background-color: #e8eaed;
    }
    
    QToolBar QToolButton:checked {
        background-color: #d4edda;
        border: 1px solid #217346;
    }
    
    QTableWidget {
        background-color: white;
        border: none;
        gridline-color: #dee2e6;
        font-size: 12px;
    }
    
    QTableWidget::item {
        padding: 4px 8px;
    }
    
    QTableWidget::item:selected {
        background-color: #cce5ff;
        color: #004085;
    }
    
    QHeaderView::section {
        background-color: #f8f9fa;
        padding: 4px 8px;
        border: 1px solid #dee2e6;
        font-weight: 600;
        font-size: 11px;
    }
    
    QLineEdit {
        padding: 3px 8px;
        border: 2px solid #217346;
        border-radius: 0px;
        font-size: 13px;
        background-color: white;
    }
    
    QLineEdit:focus {
        border-color: #0078d4;
    }
"""

# ============ IMAGE EDITOR STYLE ============

IMAGE_EDITOR_STYLE = """
    QScrollArea {
        background-color: #e8e8e8;
        border: none;
    }
    
    QToolBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #2c3e50, stop:1 #34495e);
        border: none;
        border-bottom: 2px solid #e74c3c;
        padding: 2px 5px;
        min-height: 38px;
    }
    
    QToolBar QToolButton {
        background-color: transparent;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
        font-size: 12px;
        color: #ecf0f1;
    }
    
    QToolBar QToolButton:hover {
        background-color: #3d566e;
    }
    
    QToolBar QToolButton:checked {
        background-color: #e74c3c;
    }
"""

# ============ DARK THEME ============

DARK_THEME = """
    QMainWindow {
        background-color: #1a1a2e;
    }
    
    QToolBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #2d2d44, stop:1 #1a1a2e);
        border-bottom: 2px solid #4a4a6a;
    }
    
    QToolBar QToolButton {
        color: #e0e0e0;
    }
    
    QToolBar QToolButton:hover {
        background-color: #3d3d5a;
    }
    
    QStatusBar {
        background: #1a1a2e;
        border-top: 1px solid #4a4a6a;
        color: #a0a0a0;
    }
    
    QListWidget {
        background-color: #16213e;
        color: #e0e0e0;
    }
    
    QListWidget::item:hover {
        background-color: #2d3d6a;
        color: #ffffff;
    }
    
    QListWidget::item:selected {
        background-color: #4a6a8a;
        color: #ffffff;
    }
    
    QTextEdit {
        background-color: #1a1a2e;
        color: #e0e0e0;
    }
    
    QTableWidget {
        background-color: #1a1a2e;
        color: #e0e0e0;
        gridline-color: #4a4a6a;
    }
    
    QTableWidget::item:selected {
        background-color: #4a6a8a;
        color: #ffffff;
    }
    
    QHeaderView::section {
        background-color: #2d2d44;
        color: #e0e0e0;
        border: 1px solid #4a4a6a;
    }
    
    QComboBox {
        background-color: #2d2d44;
        color: #e0e0e0;
        border: 1px solid #4a4a6a;
    }
    
    QComboBox:hover {
        border-color: #6a8aaa;
    }
    
    QLineEdit {
        background-color: #2d2d44;
        color: #e0e0e0;
        border: 1px solid #4a4a6a;
    }
    
    QLineEdit:focus {
        border-color: #6a8aaa;
    }
    
    QMenuBar {
        background-color: #1a1a2e;
        color: #e0e0e0;
        border-bottom: 1px solid #4a4a6a;
    }
    
    QMenuBar::item:selected {
        background-color: #2d2d44;
    }
    
    QMenu {
        background-color: #1a1a2e;
        color: #e0e0e0;
        border: 1px solid #4a4a6a;
    }
    
    QMenu::item:selected {
        background-color: #2d2d44;
    }
    
    QTabWidget::pane {
        background-color: #1a1a2e;
        border: 1px solid #4a4a6a;
    }
    
    QTabBar::tab {
        background-color: #2d2d44;
        color: #a0a0a0;
    }
    
    QTabBar::tab:selected {
        background-color: #1a1a2e;
        color: #ffffff;
        border-bottom: 2px solid #6a8aaa;
    }
    
    QTabBar::tab:hover {
        background-color: #3d3d5a;
    }
    
    QScrollBar:vertical {
        background-color: #1a1a2e;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4a4a6a;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #6a8aaa;
    }
    
    QPushButton {
        background-color: #4a6a8a;
        color: white;
    }
    
    QPushButton:hover {
        background-color: #5a7a9a;
    }
"""

# ============ THEME MANAGER ============

class ThemeManager:
    """Manage application themes"""
    
    LIGHT = "light"
    DARK = "dark"
    
    @staticmethod
    def apply_theme(app, theme=LIGHT):
        """Apply theme to application"""
        if theme == ThemeManager.LIGHT:
            app.setStyleSheet(MAIN_STYLE)
        elif theme == ThemeManager.DARK:
            app.setStyleSheet(MAIN_STYLE + DARK_THEME)
    
    @staticmethod
    def get_editor_style(editor_type):
        """Get editor-specific style"""
        styles = {
            "pdf": PDF_EDITOR_STYLE,
            "word": WORD_EDITOR_STYLE,
            "excel": EXCEL_EDITOR_STYLE,
            "image": IMAGE_EDITOR_STYLE,
        }
        return styles.get(editor_type, "")