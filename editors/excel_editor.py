"""
Excel Editor - Full Microsoft Excel Style Interface
Complete with Ribbon, Formula Bar, Sheet Tabs, and All Excel Features
"""

import os
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ui.styles import ThemeManager


class ExcelEditor(QWidget):
    """Complete Microsoft Excel-like spreadsheet editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.df = None
        self.table_widget = None
        self.is_modified = False
        self.formula_bar = None
        self.cell_ref_label = None
        self.status_label = None
        self.status_info_label = None
        self.loading_dialog = None
        self.max_rows_to_display = 10000
        self.sheet_tabs = None
        self.current_sheet = 0
        self.sheet_names = ["Sheet1"]
        self.copied_cells = []
        self.current_ribbon_tab = "Home"
        self.zoom_level = 100
        self.find_text = ""
        
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setStyleSheet(ThemeManager.get_editor_style("excel") + """
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        
        # === Excel Ribbon ===
        ribbon = self.create_excel_ribbon()
        layout.addWidget(ribbon)
        
        # === Warning Bar (for CSV compatibility) ===
        warning_bar = self.create_warning_bar()
        layout.addWidget(warning_bar)
        
        # === Formula Bar ===
        formula_widget = self.create_formula_bar()
        layout.addWidget(formula_widget)
        
        # === Table with Column Headers ===
        self.create_table_widget()
        layout.addWidget(self.table_widget, 1)  # 1 = stretch factor
        
        # === Sheet Tabs ===
        sheet_widget = self.create_sheet_tabs()
        layout.addWidget(sheet_widget)
        
        # === Status Bar ===
        status_widget = self.create_status_bar()
        layout.addWidget(status_widget)
        
        self.setLayout(layout)
    
    def create_excel_ribbon(self):
        """Create full Excel-like ribbon toolbar"""
        ribbon = QToolBar()
        ribbon.setMovable(False)
        ribbon.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.5 #f8f9fa, stop:1 #e9ecef);
                border: none;
                border-bottom: 2px solid #217346;
                padding: 2px 8px;
                min-height: 48px;
                spacing: 4px;
            }
            QToolBar::separator {
                width: 2px;
                background: #dee2e6;
                margin: 4px 8px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                padding: 5px 12px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 11px;
                color: #2c3e50;
                min-height: 28px;
            }
            QToolBar QToolButton:hover {
                background-color: #e8eaed;
            }
            QToolBar QToolButton:checked {
                background-color: #d4edda;
                border: 1px solid #217346;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px 14px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 12px;
                color: #2c3e50;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
            QPushButton:checked {
                background-color: #d4edda;
                border-bottom: 2px solid #217346;
            }
            QComboBox {
                padding: 3px 8px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                background-color: white;
                font-size: 11px;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #217346;
            }
        """)
        
        # === Ribbon Tabs ===
        ribbon_tabs = ["File", "Home", "Insert", "Page Layout", "Formulas", "Data", "Review", "View"]
        for tab in ribbon_tabs:
            btn = QPushButton(tab)
            btn.setCheckable(True)
            if tab == "Home":
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, t=tab: self.switch_ribbon_tab(t))
            ribbon.addWidget(btn)
        
        ribbon.addSeparator()
        
        # === File Group ===
        save_action = QAction("💾 Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        ribbon.addAction(save_action)
        
        save_as_action = QAction("📄 Save As", self)
        save_as_action.triggered.connect(self.save_as_file)
        ribbon.addAction(save_as_action)
        
        ribbon.addSeparator()
        
        # === Clipboard Group ===
        paste_action = QAction("📄 Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste_cells)
        ribbon.addAction(paste_action)
        
        cut_action = QAction("✂️ Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut_cells)
        ribbon.addAction(cut_action)
        
        copy_action = QAction("📋 Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_cells)
        ribbon.addAction(copy_action)
        
        ribbon.addSeparator()
        
        # === Font Group ===
        font_label = QLabel("Font:")
        font_label.setStyleSheet("font-weight: 600; font-size: 11px; color: #495057; padding: 0 5px;")
        ribbon.addWidget(font_label)
        
        bold_btn = QAction("B", self)
        bold_btn.setCheckable(True)
        bold_btn.triggered.connect(lambda: self.apply_formatting("bold"))
        bold_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        ribbon.addAction(bold_btn)
        
        italic_btn = QAction("I", self)
        italic_btn.setCheckable(True)
        italic_btn.triggered.connect(lambda: self.apply_formatting("italic"))
        italic_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal, True))
        ribbon.addAction(italic_btn)
        
        underline_btn = QAction("U", self)
        underline_btn.setCheckable(True)
        underline_btn.triggered.connect(lambda: self.apply_formatting("underline"))
        ribbon.addAction(underline_btn)
        
        # Font Color
        font_color_action = QAction("A", self)
        font_color_action.triggered.connect(self.choose_font_color)
        font_color_action.setToolTip("Font Color")
        ribbon.addAction(font_color_action)
        
        # Fill Color
        fill_color_action = QAction("◼", self)
        fill_color_action.triggered.connect(self.choose_fill_color)
        fill_color_action.setToolTip("Fill Color")
        ribbon.addAction(fill_color_action)
        
        ribbon.addSeparator()
        
        # === Alignment Group ===
        align_left = QAction("⇐", self)
        align_left.triggered.connect(lambda: self.apply_alignment(Qt.AlignmentFlag.AlignLeft))
        ribbon.addAction(align_left)
        
        align_center = QAction("⇔", self)
        align_center.triggered.connect(lambda: self.apply_alignment(Qt.AlignmentFlag.AlignCenter))
        ribbon.addAction(align_center)
        
        align_right = QAction("⇒", self)
        align_right.triggered.connect(lambda: self.apply_alignment(Qt.AlignmentFlag.AlignRight))
        ribbon.addAction(align_right)
        
        # Wrap Text
        wrap_text_btn = QAction("Wrap Text", self)
        wrap_text_btn.setCheckable(True)
        wrap_text_btn.triggered.connect(self.toggle_wrap_text)
        ribbon.addAction(wrap_text_btn)
        
        ribbon.addSeparator()
        
        # === Number Group ===
        number_label = QLabel("Number:")
        number_label.setStyleSheet("font-weight: 600; font-size: 11px; color: #495057; padding: 0 5px;")
        ribbon.addWidget(number_label)
        
        number_format_combo = QComboBox()
        number_format_combo.addItems(["General", "Number", "Currency", "Accounting", "Date", "Time", "Percentage"])
        number_format_combo.setMaximumWidth(120)
        number_format_combo.currentTextChanged.connect(self.change_number_format)
        ribbon.addWidget(number_format_combo)
        
        ribbon.addSeparator()
        
        # === Cells Group ===
        insert_row_btn = QAction("➕ Row", self)
        insert_row_btn.triggered.connect(self.insert_row)
        ribbon.addAction(insert_row_btn)
        
        insert_col_btn = QAction("➕ Column", self)
        insert_col_btn.triggered.connect(self.insert_column)
        ribbon.addAction(insert_col_btn)
        
        delete_row_btn = QAction("➖ Row", self)
        delete_row_btn.triggered.connect(self.delete_row)
        ribbon.addAction(delete_row_btn)
        
        delete_col_btn = QAction("➖ Column", self)
        delete_col_btn.triggered.connect(self.delete_column)
        ribbon.addAction(delete_col_btn)
        
        ribbon.addSeparator()
        
        # === Editing Group ===
        sort_asc_btn = QAction("⬆ Sort A→Z", self)
        sort_asc_btn.triggered.connect(lambda: self.sort_data(True))
        ribbon.addAction(sort_asc_btn)
        
        sort_desc_btn = QAction("⬇ Sort Z→A", self)
        sort_desc_btn.triggered.connect(lambda: self.sort_data(False))
        ribbon.addAction(sort_desc_btn)
        
        ribbon.addSeparator()
        
        # === Find & Select ===
        find_action = QAction("🔍 Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        ribbon.addAction(find_action)
        
        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        ribbon.addAction(select_all_action)
        
        ribbon.addSeparator()
        
        # === Export ===
        export_action = QAction("📤 Export", self)
        export_action.triggered.connect(self.export_csv)
        ribbon.addAction(export_action)
        
        return ribbon
    
    def create_warning_bar(self):
        """Create warning bar for CSV files"""
        self.warning_bar = QWidget()
        self.warning_bar.setStyleSheet("""
            QWidget {
                background-color: #fff3cd;
                border: 1px solid #ffc107;
            }
        """)
        self.warning_bar.setVisible(False)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 5, 15, 5)
        
        warning_icon = QLabel("⚠️")
        warning_icon.setStyleSheet("font-size: 18px;")
        layout.addWidget(warning_icon)
        
        warning_text = QLabel("POSSIBLE DATA LOSS: Some features might be lost if you save this workbook in the comma-delimited (.csv) format. To preserve these features, save it in an Excel file format.")
        warning_text.setStyleSheet("""
            color: #856404;
            font-size: 12px;
            font-weight: 500;
        """)
        warning_text.setWordWrap(True)
        layout.addWidget(warning_text, 1)
        
        close_btn = QPushButton("✕")
        close_btn.setMaximumWidth(30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-weight: bold;
                color: #856404;
            }
            QPushButton:hover {
                background-color: #ffe8a1;
                border-radius: 4px;
            }
        """)
        close_btn.clicked.connect(lambda: self.warning_bar.setVisible(False))
        layout.addWidget(close_btn)
        
        self.warning_bar.setLayout(layout)
        return self.warning_bar
    
    def create_formula_bar(self):
        """Create formula bar with cell reference and formula input"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(5)
        
        # Cell reference
        self.cell_ref_label = QLabel("A1")
        self.cell_ref_label.setFixedWidth(60)
        self.cell_ref_label.setStyleSheet("""
            font-weight: bold; 
            color: #2c3e50; 
            background-color: #e9ecef;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 12px;
            border: 1px solid #ced4da;
            min-height: 26px;
        """)
        layout.addWidget(self.cell_ref_label)
        
        # FX label
        fx_label = QLabel("fx")
        fx_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            color: #217346; 
            background: transparent;
            padding: 0 8px;
            min-width: 25px;
        """)
        layout.addWidget(fx_label)
        
        # Formula input
        self.formula_bar = QLineEdit()
        self.formula_bar.setPlaceholderText("Enter formula or value...")
        self.formula_bar.returnPressed.connect(self.apply_formula)
        self.formula_bar.setStyleSheet("""
            QLineEdit {
                padding: 4px 10px;
                border: 2px solid #217346;
                border-radius: 0px;
                font-size: 13px;
                background-color: white;
                min-height: 28px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        layout.addWidget(self.formula_bar, 1)
        
        # Function button
        func_btn = QPushButton("fx")
        func_btn.setMaximumWidth(35)
        func_btn.setStyleSheet("""
            QPushButton {
                background-color: #217346;
                color: white;
                border: none;
                padding: 4px 10px;
                font-weight: bold;
                border-radius: 3px;
                min-height: 26px;
            }
            QPushButton:hover {
                background-color: #1a5c38;
            }
        """)
        func_btn.clicked.connect(self.show_function_help)
        layout.addWidget(func_btn)
        
        # Cancel/Enter buttons
        cancel_btn = QPushButton("✕")
        cancel_btn.setMaximumWidth(25)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #dc3545;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f8d7da;
                border-radius: 3px;
            }
        """)
        cancel_btn.clicked.connect(self.cancel_formula)
        layout.addWidget(cancel_btn)
        
        enter_btn = QPushButton("✓")
        enter_btn.setMaximumWidth(25)
        enter_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #28a745;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d4edda;
                border-radius: 3px;
            }
        """)
        enter_btn.clicked.connect(self.apply_formula)
        layout.addWidget(enter_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_table_widget(self):
        """Create the main table widget"""
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: #d0d7de;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTableWidget::item {
                padding: 4px 6px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #cce5ff;
                color: #004085;
            }
            QTableWidget::item:selected:!active {
                background-color: #e8eaed;
            }
            QTableWidget::item:editing {
                background-color: #ffffe0;
            }
            QTableWidget::item:selected:active {
                background-color: #cce5ff;
            }
            QHeaderView::section {
                background-color: #f3f5f7;
                padding: 4px 8px;
                border: 1px solid #d0d7de;
                font-weight: 600;
                font-size: 11px;
                min-height: 28px;
                min-width: 40px;
            }
            QHeaderView::section:horizontal {
                background-color: #f3f5f7;
                border-bottom: 2px solid #d0d7de;
            }
            QHeaderView::section:vertical {
                background-color: #f3f5f7;
                border-right: 2px solid #d0d7de;
                min-width: 35px;
                max-width: 35px;
            }
            QHeaderView::section:checked {
                background-color: #cce5ff;
            }
            QTableCornerButton::section {
                background-color: #f3f5f7;
                border: 1px solid #d0d7de;
            }
        """)
        self.table_widget.setAlternatingRowColors(False)
        self.table_widget.setSortingEnabled(False)
        self.table_widget.itemChanged.connect(self.on_cell_changed)
        self.table_widget.currentCellChanged.connect(self.on_cell_selected)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table_widget.verticalHeader().setDefaultSectionSize(28)
        self.table_widget.verticalHeader().setMinimumWidth(35)
        self.table_widget.horizontalHeader().setDefaultSectionSize(100)
        self.table_widget.horizontalHeader().setMinimumHeight(28)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | 
                                          QTableWidget.EditTrigger.EditKeyPressed |
                                          QTableWidget.EditTrigger.AnyKeyPressed)
        
        # Show column names as headers instead of letters
        self.table_widget.horizontalHeader().setSectionsClickable(True)
        
        self.table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def create_sheet_tabs(self):
        """Create sheet tabs at the bottom"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                min-height: 32px;
            }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(2)
        
        # Left navigation arrows
        left_arrow_btn = QPushButton("◄")
        left_arrow_btn.setMaximumWidth(30)
        left_arrow_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px 5px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        layout.addWidget(left_arrow_btn)
        
        right_arrow_btn = QPushButton("►")
        right_arrow_btn.setMaximumWidth(30)
        right_arrow_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px 5px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        layout.addWidget(right_arrow_btn)
        
        # Sheet tabs
        self.sheet_tabs = QTabWidget()
        self.sheet_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                padding: 4px 18px;
                margin-right: 2px;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                background-color: #f1f3f5;
                font-weight: 500;
                font-size: 11px;
                min-height: 26px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #217346;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        self.sheet_tabs.currentChanged.connect(self.sheet_changed)
        layout.addWidget(self.sheet_tabs, 1)
        
        # Add sheet button
        add_sheet_btn = QPushButton("+")
        add_sheet_btn.setMaximumWidth(35)
        add_sheet_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-weight: bold;
                padding: 2px 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        add_sheet_btn.clicked.connect(self.add_sheet)
        layout.addWidget(add_sheet_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_status_bar(self):
        """Create status bar with information"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                min-height: 28px;
            }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(15)
        
        # Mode indicator
        self.mode_label = QLabel("Ready")
        self.mode_label.setStyleSheet("""
            color: #495057; 
            font-size: 11px; 
            font-weight: 500;
            min-width: 60px;
        """)
        layout.addWidget(self.mode_label)
        
        # Cell info
        self.cell_info_label = QLabel("")
        self.cell_info_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        layout.addWidget(self.cell_info_label)
        
        layout.addStretch()
        
        # Sheet info
        self.sheet_info_label = QLabel("")
        self.sheet_info_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        layout.addWidget(self.sheet_info_label)
        
        # Zoom slider
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("color: #495057; font-size: 11px;")
        layout.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setMaximumWidth(100)
        self.zoom_slider.valueChanged.connect(self.zoom_changed)
        layout.addWidget(self.zoom_slider)
        
        self.zoom_status = QLabel("100%")
        self.zoom_status.setStyleSheet("color: #495057; font-size: 11px; min-width: 40px;")
        layout.addWidget(self.zoom_status)
        
        widget.setLayout(layout)
        return widget
    
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_file)
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.redo)
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(self.copy_cells)
        QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(self.paste_cells)
        QShortcut(QKeySequence("Ctrl+X"), self).activated.connect(self.cut_cells)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_find_dialog)
        QShortcut(QKeySequence("Ctrl+A"), self).activated.connect(self.select_all)
    
    def switch_ribbon_tab(self, tab_name):
        self.current_ribbon_tab = tab_name
        self.mode_label.setText(f"Ready - {tab_name} tab")
    
    def show_loading_dialog(self):
        self.loading_dialog = QProgressDialog("Loading file...", "Cancel", 0, 100, self)
        self.loading_dialog.setWindowTitle("Loading")
        self.loading_dialog.setModal(True)
        self.loading_dialog.setMinimumDuration(0)
        self.loading_dialog.setValue(0)
        QApplication.processEvents()
    
    def hide_loading_dialog(self):
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None
        QApplication.processEvents()
    
    def load_file(self, file_path):
        self.current_file = file_path
        self.warning_bar.setVisible(file_path.endswith('.csv'))
        
        try:
            self.show_loading_dialog()
            
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            self.mode_label.setText(f"Loading: {os.path.basename(file_path)}...")
            QApplication.processEvents()
            
            if file_path.endswith('.csv'):
                if file_size > 10 * 1024 * 1024:
                    chunk_size = 50000
                    chunks = []
                    total_rows = 0
                    
                    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                        chunks.append(chunk)
                        total_rows += len(chunk)
                        progress = min(90, int((total_rows / 100000) * 100))
                        if self.loading_dialog:
                            self.loading_dialog.setValue(progress)
                        QApplication.processEvents()
                    
                    self.df = pd.concat(chunks, ignore_index=True)
                else:
                    self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            
            if self.loading_dialog:
                self.loading_dialog.setValue(95)
            QApplication.processEvents()
            
            if len(self.df) > self.max_rows_to_display:
                self.mode_label.setText(f"File has {len(self.df)} rows. Showing first {self.max_rows_to_display}.")
                self.df = self.df.head(self.max_rows_to_display)
            
            self.display_dataframe()
            self.is_modified = False
            
            if self.loading_dialog:
                self.loading_dialog.setValue(100)
            
            self.mode_label.setText("Ready")
            self.sheet_info_label.setText(f"Rows: {len(self.df)}, Columns: {len(self.df.columns)}")
            
            self.hide_loading_dialog()
            
        except Exception as e:
            self.hide_loading_dialog()
            QMessageBox.warning(self, "Error", f"Failed to load file: {str(e)}")
    
    def display_dataframe(self):
        if self.df is None or self.df.empty:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return
        
        self.table_widget.blockSignals(True)
        
        try:
            rows, cols = self.df.shape
            
            self.table_widget.setRowCount(rows)
            self.table_widget.setColumnCount(cols)
            
            # Set column headers from DataFrame (player_id, player_nar, etc.)
            self.table_widget.setHorizontalHeaderLabels(self.df.columns.tolist())
            
            # Set row numbers (1, 2, 3, ...)
            for i in range(rows):
                self.table_widget.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
            
            # Fill data
            for i in range(rows):
                for j in range(cols):
                    value = str(self.df.iloc[i, j]) if not pd.isna(self.df.iloc[i, j]) else ""
                    item = QTableWidgetItem(value)
                    self.table_widget.setItem(i, j, item)
                
                if i % 1000 == 0 and i > 0:
                    QApplication.processEvents()
            
            self.table_widget.resizeColumnsToContents()
            
            # Set minimum column width
            for i in range(cols):
                if self.table_widget.columnWidth(i) < 60:
                    self.table_widget.setColumnWidth(i, 60)
            
        finally:
            self.table_widget.blockSignals(False)
    
    def get_column_letter(self, col):
        result = ""
        col += 1
        while col > 0:
            col -= 1
            result = chr(col % 26 + 65) + result
            col //= 26
        return result
    
    def on_cell_changed(self, item):
        self.is_modified = True
        row = item.row()
        col = item.column()
        value = item.text()
        
        if self.df is not None and row < len(self.df):
            try:
                self.df.iloc[row, col] = value if value else None
            except:
                pass
    
    def on_cell_selected(self, row, col, prev_row, prev_col):
        if row >= 0 and col >= 0 and self.df is not None and col < len(self.df.columns):
            col_letter = self.get_column_letter(col)
            col_name = self.df.columns[col] if col < len(self.df.columns) else col_letter
            self.cell_ref_label.setText(f"{col_name}")
            
            item = self.table_widget.item(row, col)
            if item:
                self.formula_bar.setText(item.text())
            else:
                self.formula_bar.clear()
            
            self.cell_info_label.setText(f"Cell: {col_name}{row + 1}")
    
    def copy_cells(self):
        selected = self.table_widget.selectedItems()
        if selected:
            self.copied_cells = selected
            self.mode_label.setText(f"Copied {len(selected)} cells")
    
    def cut_cells(self):
        selected = self.table_widget.selectedItems()
        if selected:
            self.copied_cells = selected
            for item in selected:
                item.setText("")
            self.is_modified = True
            self.mode_label.setText(f"Cut {len(selected)} cells")
    
    def paste_cells(self):
        if hasattr(self, 'copied_cells') and self.copied_cells:
            current = self.table_widget.currentItem()
            if current:
                row_offset = current.row() - self.copied_cells[0].row()
                col_offset = current.column() - self.copied_cells[0].column()
                
                for item in self.copied_cells:
                    new_row = item.row() + row_offset
                    new_col = item.column() + col_offset
                    if new_row < self.table_widget.rowCount() and new_col < self.table_widget.columnCount():
                        new_item = QTableWidgetItem(item.text())
                        self.table_widget.setItem(new_row, new_col, new_item)
                
                self.is_modified = True
                self.mode_label.setText("Cells pasted")
    
    def apply_formatting(self, format_type):
        selected = self.table_widget.selectedItems()
        if not selected:
            return
        
        for item in selected:
            font = item.font()
            if format_type == "bold":
                font.setBold(not font.bold())
            elif format_type == "italic":
                font.setItalic(not font.italic())
            elif format_type == "underline":
                font.setUnderline(not font.underline())
            item.setFont(font)
        
        self.is_modified = True
        self.mode_label.setText(f"Applied {format_type}")
    
    def apply_alignment(self, alignment):
        selected = self.table_widget.selectedItems()
        if not selected:
            return
        
        for item in selected:
            item.setTextAlignment(alignment)
        
        self.is_modified = True
        self.mode_label.setText("Alignment applied")
    
    def choose_font_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            selected = self.table_widget.selectedItems()
            for item in selected:
                item.setForeground(QBrush(color))
    
    def choose_fill_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            selected = self.table_widget.selectedItems()
            for item in selected:
                item.setBackground(QBrush(color))
    
    def toggle_wrap_text(self, checked):
        self.mode_label.setText("Wrap text " + ("enabled" if checked else "disabled"))
    
    def change_number_format(self, format_type):
        selected = self.table_widget.selectedItems()
        if not selected:
            return
        
        for item in selected:
            text = item.text()
            try:
                if format_type == "General":
                    pass
                elif format_type == "Number":
                    item.setText(f"{float(text):.2f}")
                elif format_type == "Currency":
                    item.setText(f"${float(text):.2f}")
                elif format_type == "Percentage":
                    item.setText(f"{float(text):.1%}")
            except:
                pass
    
    def apply_formula(self):
        formula = self.formula_bar.text()
        if not formula:
            return
        
        current = self.table_widget.currentItem()
        if current:
            current.setText(formula)
            self.is_modified = True
            self.mode_label.setText("Formula applied")
    
    def cancel_formula(self):
        self.formula_bar.clear()
        self.mode_label.setText("Cancelled")
    
    def show_function_help(self):
        QMessageBox.information(self, "Functions Help", 
            "📊 Available Functions:\n\n"
            "=SUM(range) - Sum of values\n"
            "=AVERAGE(range) - Average of values\n"
            "=COUNT(range) - Count of values\n"
            "=MIN(range) - Minimum value\n"
            "=MAX(range) - Maximum value\n"
            "=IF(condition, true, false) - Conditional\n\n"
            "📝 Examples:\n"
            "=SUM(A1:A10)\n"
            "=AVERAGE(B1:B20)\n"
            "=IF(A1>10, 'Yes', 'No')")
    
    def show_find_dialog(self):
        text, ok = QInputDialog.getText(self, "Find", "Enter text to find:")
        if ok and text:
            self.find_text = text
            found = False
            for row in range(self.table_widget.rowCount()):
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    if item and text.lower() in item.text().lower():
                        self.table_widget.setCurrentCell(row, col)
                        self.table_widget.scrollToItem(item)
                        found = True
                        self.mode_label.setText(f"Found '{text}' at row {row+1}, col {col+1}")
                        return
            if not found:
                QMessageBox.information(self, "Find", f"'{text}' not found")
    
    def select_all(self):
        self.table_widget.selectAll()
        self.mode_label.setText("All cells selected")
    
    def insert_row(self):
        selected = self.table_widget.currentRow()
        if selected < 0:
            selected = self.table_widget.rowCount()
        self.table_widget.insertRow(selected)
        
        for i in range(selected, self.table_widget.rowCount()):
            self.table_widget.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
        
        self.is_modified = True
        self.mode_label.setText(f"Row inserted at {selected + 1}")
    
    def insert_column(self):
        selected = self.table_widget.currentColumn()
        if selected < 0:
            selected = self.table_widget.columnCount()
        self.table_widget.insertColumn(selected)
        
        self.is_modified = True
        self.mode_label.setText(f"Column inserted at {selected + 1}")
    
    def delete_row(self):
        selected = self.table_widget.currentRow()
        if selected >= 0:
            self.table_widget.removeRow(selected)
            for i in range(selected, self.table_widget.rowCount()):
                self.table_widget.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
            self.is_modified = True
            self.mode_label.setText(f"Row {selected + 1} deleted")
    
    def delete_column(self):
        selected = self.table_widget.currentColumn()
        if selected >= 0:
            self.table_widget.removeColumn(selected)
            self.is_modified = True
            self.mode_label.setText(f"Column {selected + 1} deleted")
    
    def sort_data(self, ascending=True):
        col = self.table_widget.currentColumn()
        if col < 0:
            return
        
        self.table_widget.sortItems(col, 
            Qt.SortOrder.AscendingOrder if ascending else Qt.SortOrder.DescendingOrder)
        self.mode_label.setText(f"Sorted column {col + 1}")
    
    def add_sheet(self):
        sheet_name = f"Sheet{len(self.sheet_names) + 1}"
        self.sheet_names.append(sheet_name)
        self.sheet_tabs.addTab(QWidget(), sheet_name)
        self.mode_label.setText(f"Added new sheet: {sheet_name}")
    
    def sheet_changed(self, index):
        self.current_sheet = index
        if index < len(self.sheet_names):
            self.mode_label.setText(f"Switched to sheet: {self.sheet_names[index]}")
    
    def zoom_changed(self, value):
        self.zoom_level = value
        self.zoom_status.setText(f"{value}%")
        # Apply zoom to table
        font = self.table_widget.font()
        font.setPointSize(int(9 * value / 100))
        self.table_widget.setFont(font)
    
    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            "export.csv",
            "CSV Files (*.csv)"
        )
        if file_path and self.df is not None:
            try:
                self.df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", "CSV exported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Export failed: {str(e)}")
    
    def save_file(self):
        if self.current_file and self.df is not None:
            try:
                if self.current_file.endswith('.csv'):
                    self.df.to_csv(self.current_file, index=False)
                else:
                    self.df.to_excel(self.current_file, index=False)
                self.is_modified = False
                self.mode_label.setText("File saved successfully!")
                QMessageBox.information(self, "Success", "File saved!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save: {str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            "spreadsheet.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if file_path:
            self.current_file = file_path
            self.save_file()
    
    def undo(self):
        self.mode_label.setText("Undo (simplified)")
    
    def redo(self):
        self.mode_label.setText("Redo (simplified)")