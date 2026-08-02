"""
Conversion Dialog - User interface for file conversion
"""

import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from core.converter import FileConverter


class ConversionDialog(QDialog):
    """Dialog for selecting conversion options"""
    
    def __init__(self, input_file, file_type, parent=None):
        super().__init__(parent)
        self.input_file = input_file
        self.file_type = file_type
        self.output_file = None
        
        self.setWindowTitle("Convert File")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        
        self.init_ui()
        self.update_conversion_options()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel("🔄 File Conversion")
        header_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px 0;
        """)
        layout.addWidget(header_label)
        
        # Input file info
        info_group = QGroupBox("Input File")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        info_layout = QVBoxLayout()
        
        file_name = os.path.basename(self.input_file)
        file_size = os.path.getsize(self.input_file)
        size_str = self.format_file_size(file_size)
        
        info_layout.addWidget(QLabel(f"📄 Name: {file_name}"))
        info_layout.addWidget(QLabel(f"📦 Size: {size_str}"))
        info_layout.addWidget(QLabel(f"📂 Type: {self.file_type.upper()}"))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Conversion options
        options_group = QGroupBox("Conversion Options")
        options_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        options_layout = QVBoxLayout()
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Convert to:"))
        self.format_combo = QComboBox()
        self.format_combo.setMinimumWidth(200)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        # Output name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Output name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter output filename (optional)")
        name_layout.addWidget(self.name_edit)
        options_layout.addLayout(name_layout)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                padding: 8px 25px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        self.convert_btn = QPushButton("🔄 Convert")
        self.convert_btn.clicked.connect(self.convert)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                padding: 8px 25px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(self.convert_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def format_file_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def update_conversion_options(self):
        """Update available conversion formats"""
        self.format_combo.clear()
        
        available = FileConverter.get_available_conversions(self.input_file, self.file_type)
        
        for fmt in available:
            format_info = FileConverter.SUPPORTED_FORMATS.get(fmt, {})
            ext = FileConverter.get_extension_for_format(fmt)
            name = format_info.get('name', fmt.upper())
            icon = format_info.get('icon', '📄')
            self.format_combo.addItem(f"{icon} {name} ({ext})", fmt)
        
        if self.format_combo.count() == 0:
            self.format_combo.addItem("No conversions available")
            self.format_combo.setEnabled(False)
            self.convert_btn.setEnabled(False)
    
    def on_format_changed(self, text):
        """Update output filename when format changes"""
        if not text:
            return
        
        # Get the format key
        format_key = self.format_combo.currentData()
        if not format_key:
            return
        
        # Get extension
        ext = FileConverter.get_extension_for_format(format_key)
        
        # Update name suggestion
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        suggested_name = f"{base_name}_converted{ext}"
        self.name_edit.setText(suggested_name)
    
    def convert(self):
        """Perform the conversion"""
        format_key = self.format_combo.currentData()
        if not format_key:
            QMessageBox.warning(self, "No Format", "Please select a conversion format.")
            return
        
        # Get output path
        output_dir = os.path.dirname(self.input_file)
        
        # Use suggested name or custom name
        custom_name = self.name_edit.text().strip()
        if custom_name:
            output_file = os.path.join(output_dir, custom_name)
        else:
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            ext = FileConverter.get_extension_for_format(format_key)
            output_file = os.path.join(output_dir, f"{base_name}_converted{ext}")
        
        # Check if file exists
        if os.path.exists(output_file):
            reply = QMessageBox.question(
                self,
                "File Exists",
                f"File '{os.path.basename(output_file)}' already exists.\nOverwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        try:
            # Show progress
            self.convert_btn.setEnabled(False)
            self.convert_btn.setText("⏳ Converting...")
            QApplication.processEvents()
            
            # Perform conversion
            FileConverter.convert_file(self.input_file, output_file)
            
            self.output_file = output_file
            QMessageBox.information(
                self,
                "Success",
                f"✅ File converted successfully!\n\n📄 Output: {os.path.basename(output_file)}"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Conversion Failed",
                f"❌ Error during conversion:\n\n{str(e)}"
            )
        finally:
            self.convert_btn.setEnabled(True)
            self.convert_btn.setText("🔄 Convert")
    
    def get_output_file(self):
        """Get the output file path"""
        return self.output_file