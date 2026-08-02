"""
Excel Editor - Microsoft Excel Style Interface
Optimized for large files with chunked loading
"""

import os
import pandas as pd
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ui.styles import ThemeManager


class ExcelEditor(QWidget):
    """Microsoft Excel-like spreadsheet editor with optimized loading"""
    
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
        self.max_rows_to_display = 10000  # Limit rows for performance
        
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setStyleSheet(ThemeManager.get_editor_style("excel"))
        
        # === Excel Ribbon ===
        ribbon = self.create_excel_ribbon()
        layout.addWidget(ribbon)
        
        # === Formula Bar ===
        formula_widget = QWidget()
        formula_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
        """)
        formula_layout = QHBoxLayout()
        formula_layout.setContentsMargins(8, 3, 8, 3)
        formula_layout.setSpacing(5)
        
        fx_label = QLabel("fx")
        fx_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #217346; background: transparent;")
        fx_label.setFixedWidth(30)
        formula_layout.addWidget(fx_label)
        
        self.cell_ref_label = QLabel("A1")
        self.cell_ref_label.setFixedWidth(50)
        self.cell_ref_label.setStyleSheet("font-weight: bold; color: #2c3e50; background: transparent;")
        formula_layout.addWidget(self.cell_ref_label)
        
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
        formula_layout.addWidget(self.formula_bar)
        
        formula_widget.setLayout(formula_layout)
        layout.addWidget(formula_widget)
        
        # === Table ===
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
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
                min-height: 24px;
            }
            QTableWidget::item:editing {
                background-color: #ffffe0;
            }
        """)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.itemChanged.connect(self.on_cell_changed)
        self.table_widget.currentCellChanged.connect(self.on_cell_selected)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        
        layout.addWidget(self.table_widget)
        
        # === Status Bar ===
        status_widget = QWidget()
        status_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 3, 10, 3)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #495057; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.status_info_label = QLabel("")
        self.status_info_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        status_layout.addWidget(self.status_info_label)
        
        status_widget.setLayout(status_layout)
        layout.addWidget(status_widget)
        
        self.setLayout(layout)
    
    def create_excel_ribbon(self):
        """Create Excel-like ribbon toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.5 #f8f9fa, stop:1 #e9ecef);
                border: none;
                border-bottom: 2px solid #217346;
                padding: 2px 5px;
                min-height: 38px;
                spacing: 2px;
            }
            QToolBar::separator {
                width: 2px;
                background: #dee2e6;
                margin: 4px 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                padding: 4px 10px;
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
            QComboBox {
                padding: 3px 8px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                background-color: white;
                font-size: 12px;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #217346;
            }
        """)
        
        # Save
        save_action = QAction("💾 Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Formatting
        bold_btn = QAction("B", self)
        bold_btn.setCheckable(True)
        bold_btn.triggered.connect(lambda: self.apply_formatting("bold"))
        bold_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        toolbar.addAction(bold_btn)
        
        italic_btn = QAction("I", self)
        italic_btn.setCheckable(True)
        italic_btn.triggered.connect(lambda: self.apply_formatting("italic"))
        italic_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal, True))
        toolbar.addAction(italic_btn)
        
        underline_btn = QAction("U", self)
        underline_btn.setCheckable(True)
        underline_btn.triggered.connect(lambda: self.apply_formatting("underline"))
        toolbar.addAction(underline_btn)
        
        toolbar.addSeparator()
        
        # Alignment
        align_left = QAction("⇐", self)
        align_left.triggered.connect(lambda: self.apply_alignment(Qt.AlignmentFlag.AlignLeft))
        toolbar.addAction(align_left)
        
        align_center = QAction("⇔", self)
        align_center.triggered.connect(lambda: self.apply_alignment(Qt.AlignmentFlag.AlignCenter))
        toolbar.addAction(align_center)
        
        align_right = QAction("⇒", self)
        align_right.triggered.connect(lambda: self.apply_alignment(Qt.AlignmentFlag.AlignRight))
        toolbar.addAction(align_right)
        
        toolbar.addSeparator()
        
        # Insert
        insert_row = QAction("➕ Row", self)
        insert_row.triggered.connect(self.insert_row)
        toolbar.addAction(insert_row)
        
        insert_col = QAction("➕ Column", self)
        insert_col.triggered.connect(self.insert_column)
        toolbar.addAction(insert_col)
        
        delete_row = QAction("➖ Row", self)
        delete_row.triggered.connect(self.delete_row)
        toolbar.addAction(delete_row)
        
        delete_col = QAction("➖ Column", self)
        delete_col.triggered.connect(self.delete_column)
        toolbar.addAction(delete_col)
        
        toolbar.addSeparator()
        
        # Sort
        sort_asc = QAction("⬆ Sort A→Z", self)
        sort_asc.triggered.connect(lambda: self.sort_data(True))
        toolbar.addAction(sort_asc)
        
        sort_desc = QAction("⬇ Sort Z→A", self)
        sort_desc.triggered.connect(lambda: self.sort_data(False))
        toolbar.addAction(sort_desc)
        
        toolbar.addSeparator()
        
        # Export
        export_action = QAction("📤 Export", self)
        export_action.triggered.connect(self.export_csv)
        toolbar.addAction(export_action)
        
        return toolbar
    
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_file)
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.redo)
    
    def show_loading_dialog(self):
        """Show loading progress dialog"""
        self.loading_dialog = QProgressDialog("Loading file...", "Cancel", 0, 100, self)
        self.loading_dialog.setWindowTitle("Loading")
        self.loading_dialog.setModal(True)
        self.loading_dialog.setMinimumDuration(0)
        self.loading_dialog.setValue(0)
        QApplication.processEvents()
    
    def hide_loading_dialog(self):
        """Hide loading dialog"""
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None
        QApplication.processEvents()
    
    def load_file(self, file_path):
        """Load Excel or CSV file with optimized loading"""
        self.current_file = file_path
        
        try:
            self.show_loading_dialog()
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            self.status_label.setText(f"Loading: {os.path.basename(file_path)} ({file_size_mb:.1f} MB)...")
            QApplication.processEvents()
            
            # Load based on file type
            if file_path.endswith('.csv'):
                # For CSV, use chunked loading for large files
                if file_size > 10 * 1024 * 1024:  # > 10MB
                    # Load with chunking
                    chunk_size = 50000
                    chunks = []
                    total_rows = 0
                    
                    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                        chunks.append(chunk)
                        total_rows += len(chunk)
                        # Update progress
                        progress = min(90, int((total_rows / 100000) * 100))
                        if self.loading_dialog:
                            self.loading_dialog.setValue(progress)
                        QApplication.processEvents()
                    
                    self.df = pd.concat(chunks, ignore_index=True)
                else:
                    self.df = pd.read_csv(file_path)
            else:
                # For Excel, load normally (Excel files are usually smaller)
                self.df = pd.read_excel(file_path)
            
            if self.loading_dialog:
                self.loading_dialog.setValue(95)
            QApplication.processEvents()
            
            # Truncate if too large
            if len(self.df) > self.max_rows_to_display:
                self.status_label.setText(f"File has {len(self.df)} rows. Showing first {self.max_rows_to_display} rows.")
                self.df = self.df.head(self.max_rows_to_display)
            
            self.display_dataframe()
            self.is_modified = False
            
            if self.loading_dialog:
                self.loading_dialog.setValue(100)
            
            self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.status_info_label.setText(f"Rows: {len(self.df)}, Columns: {len(self.df.columns)}")
            
            self.hide_loading_dialog()
            
        except Exception as e:
            self.hide_loading_dialog()
            QMessageBox.warning(self, "Error", f"Failed to load file: {str(e)}")
    
    def display_dataframe(self):
        """Display the DataFrame in the table with optimizations"""
        if self.df is None or self.df.empty:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return
        
        # Disable sorting and updates during population
        self.table_widget.setSortingEnabled(False)
        self.table_widget.blockSignals(True)
        
        try:
            rows, cols = self.df.shape
            self.table_widget.setRowCount(rows)
            self.table_widget.setColumnCount(cols)
            self.table_widget.setHorizontalHeaderLabels(self.df.columns.tolist())
            
            # Fill data row by row with optimized method
            for i in range(rows):
                for j in range(cols):
                    value = str(self.df.iloc[i, j]) if not pd.isna(self.df.iloc[i, j]) else ""
                    item = QTableWidgetItem(value)
                    self.table_widget.setItem(i, j, item)
                
                # Update status every 1000 rows
                if i % 1000 == 0:
                    self.status_label.setText(f"Displaying row {i+1} of {rows}...")
                    QApplication.processEvents()
            
            self.table_widget.resizeColumnsToContents()
            
        finally:
            # Re-enable sorting and signals
            self.table_widget.setSortingEnabled(True)
            self.table_widget.blockSignals(False)
    
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
            col_letter = chr(65 + col) if col < 26 else f"{chr(64 + col // 26)}{chr(65 + col % 26)}"
            self.cell_ref_label.setText(f"{col_letter}{row + 1}")
            
            item = self.table_widget.item(row, col)
            if item:
                self.formula_bar.setText(item.text())
            else:
                self.formula_bar.clear()
    
    def apply_formula(self):
        formula = self.formula_bar.text()
        if not formula:
            return
        
        selected = self.table_widget.selectedItems()
        if not selected:
            return
        
        for item in selected:
            item.setText(formula)
            self.is_modified = True
        
        self.status_label.setText("Formula applied")
    
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
    
    def apply_alignment(self, alignment):
        selected = self.table_widget.selectedItems()
        if not selected:
            return
        
        for item in selected:
            item.setTextAlignment(alignment)
        
        self.is_modified = True
    
    def insert_row(self):
        selected = self.table_widget.currentRow()
        if selected < 0:
            selected = self.table_widget.rowCount()
        self.table_widget.insertRow(selected)
        self.is_modified = True
    
    def insert_column(self):
        selected = self.table_widget.currentColumn()
        if selected < 0:
            selected = self.table_widget.columnCount()
        self.table_widget.insertColumn(selected)
        self.is_modified = True
    
    def delete_row(self):
        selected = self.table_widget.currentRow()
        if selected >= 0:
            self.table_widget.removeRow(selected)
            self.is_modified = True
    
    def delete_column(self):
        selected = self.table_widget.currentColumn()
        if selected >= 0:
            self.table_widget.removeColumn(selected)
            self.is_modified = True
    
    def sort_data(self, ascending=True):
        col = self.table_widget.currentColumn()
        if col < 0:
            return
        
        self.table_widget.sortItems(col, 
            Qt.SortOrder.AscendingOrder if ascending else Qt.SortOrder.DescendingOrder)
    
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
                self.status_label.setText("File saved successfully!")
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
        self.status_label.setText("Undo (simplified)")
    
    def redo(self):
        self.status_label.setText("Redo (simplified)")