"""
Image Editor - Basic image editing tools with zoom and scroll support
"""

import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PIL import Image, ImageEnhance, ImageFilter
import io


class ImageEditor(QWidget):
    """Basic image editor with common tools and zoom support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.pixmap = None
        self.original_pixmap = None
        self.zoom_factor = 1.0
        self.is_fullscreen = False
        self.init_ui()
        self.setup_shortcuts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Zoom toolbar
        zoom_toolbar = self.create_zoom_toolbar()
        layout.addWidget(zoom_toolbar)
        
        # Image display with scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
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
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #ffffff; padding: 10px;")
        self.image_label.setMinimumSize(400, 300)
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #ddd;
                padding: 2px 10px;
                font-size: 12px;
            }
        """)
        self.image_info_label = QLabel("No image loaded")
        self.status_bar.addWidget(self.image_info_label)
        
        self.zoom_status_label = QLabel("Zoom: 100%")
        self.status_bar.addPermanentWidget(self.zoom_status_label)
        layout.addWidget(self.status_bar)
        
        self.setLayout(layout)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        self.scroll_area.setMouseTracking(True)
    
    def create_zoom_toolbar(self):
        """Create zoom toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                padding: 2px;
                spacing: 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
            }
            QToolBar QToolButton:hover {
                background-color: #e9ecef;
            }
            QComboBox {
                padding: 2px 8px;
                border-radius: 3px;
                border: 1px solid #ccc;
                background-color: white;
                font-size: 12px;
            }
        """)
        
        # Zoom out
        zoom_out_btn = QAction("🔍-", self)
        zoom_out_btn.triggered.connect(self.zoom_out)
        zoom_out_btn.setShortcut("Ctrl+-")
        toolbar.addAction(zoom_out_btn)
        
        # Zoom combo
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "Fit to Window"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.setMaximumWidth(100)
        self.zoom_combo.currentTextChanged.connect(self.zoom_changed)
        toolbar.addWidget(self.zoom_combo)
        
        # Zoom in
        zoom_in_btn = QAction("🔍+", self)
        zoom_in_btn.triggered.connect(self.zoom_in)
        zoom_in_btn.setShortcut("Ctrl++")
        toolbar.addAction(zoom_in_btn)
        
        toolbar.addSeparator()
        
        # Full screen
        fullscreen_btn = QAction("⛶ Full Screen", self)
        fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        fullscreen_btn.setShortcut("F11")
        toolbar.addAction(fullscreen_btn)
        
        # Reset zoom
        reset_btn = QAction("↩ Reset View", self)
        reset_btn.triggered.connect(self.reset_view)
        toolbar.addAction(reset_btn)
        
        return toolbar
    
    def create_toolbar(self):
        """Create image editing toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                padding: 3px;
                spacing: 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QToolBar QToolButton:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Rotate
        rotate_left = QAction("↺ Rotate Left", self)
        rotate_left.triggered.connect(lambda: self.rotate_image(-90))
        toolbar.addAction(rotate_left)
        
        rotate_right = QAction("↻ Rotate Right", self)
        rotate_right.triggered.connect(lambda: self.rotate_image(90))
        toolbar.addAction(rotate_right)
        
        toolbar.addSeparator()
        
        # Flip
        flip_h = QAction("↔ Flip H", self)
        flip_h.triggered.connect(lambda: self.flip_image(True, False))
        toolbar.addAction(flip_h)
        
        flip_v = QAction("↕ Flip V", self)
        flip_v.triggered.connect(lambda: self.flip_image(False, True))
        toolbar.addAction(flip_v)
        
        toolbar.addSeparator()
        
        # Brightness
        brightness_action = QAction("☀️ Brightness", self)
        brightness_action.triggered.connect(self.adjust_brightness)
        toolbar.addAction(brightness_action)
        
        # Contrast
        contrast_action = QAction("◐ Contrast", self)
        contrast_action.triggered.connect(self.adjust_contrast)
        toolbar.addAction(contrast_action)
        
        toolbar.addSeparator()
        
        # Crop
        crop_action = QAction("✂️ Crop", self)
        crop_action.triggered.connect(self.crop_image)
        toolbar.addAction(crop_action)
        
        # Resize
        resize_action = QAction("📐 Resize", self)
        resize_action.triggered.connect(self.resize_image)
        toolbar.addAction(resize_action)
        
        toolbar.addSeparator()
        
        # Blur
        blur_action = QAction("Blur", self)
        blur_action.triggered.connect(lambda: self.apply_filter(ImageFilter.BLUR))
        toolbar.addAction(blur_action)
        
        # Sharpen
        sharpen_action = QAction("Sharpen", self)
        sharpen_action.triggered.connect(lambda: self.apply_filter(ImageFilter.SHARPEN))
        toolbar.addAction(sharpen_action)
        
        toolbar.addSeparator()
        
        # Reset
        reset_action = QAction("↩ Reset Image", self)
        reset_action.triggered.connect(self.reset_image)
        toolbar.addAction(reset_action)
        
        # Save
        save_action = QAction("💾 Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        toolbar.addAction(save_action)
        
        return toolbar
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Zoom shortcuts
        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.zoom_in_shortcut.activated.connect(self.zoom_in)
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(self.zoom_out)
        
        # Full screen
        self.fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        self.fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
    
    def wheelEvent(self, event):
        """Handle Ctrl+Scroll for zoom"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def zoom_changed(self, value):
        """Handle zoom combo box changes"""
        if value == "Fit to Window":
            self.fit_to_window()
        else:
            self.zoom_factor = float(value.replace("%", "")) / 100
            self.display_image()
    
    def zoom_in(self):
        """Zoom in on image"""
        zoom_values = ["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%"]
        current = self.zoom_combo.currentText()
        if current in zoom_values:
            idx = zoom_values.index(current)
            if idx < len(zoom_values) - 1:
                self.zoom_combo.setCurrentText(zoom_values[idx + 1])
        else:
            self.zoom_combo.setCurrentText("100%")
    
    def zoom_out(self):
        """Zoom out on image"""
        zoom_values = ["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%"]
        current = self.zoom_combo.currentText()
        if current in zoom_values:
            idx = zoom_values.index(current)
            if idx > 0:
                self.zoom_combo.setCurrentText(zoom_values[idx - 1])
        else:
            self.zoom_combo.setCurrentText("100%")
    
    def fit_to_window(self):
        """Fit image to window"""
        if self.pixmap:
            # Calculate zoom to fit
            label_width = self.image_label.width() - 20
            label_height = self.image_label.height() - 20
            pixmap_width = self.pixmap.width()
            pixmap_height = self.pixmap.height()
            
            if pixmap_width > 0 and pixmap_height > 0:
                zoom_x = label_width / pixmap_width
                zoom_y = label_height / pixmap_height
                self.zoom_factor = min(zoom_x, zoom_y)
                self.display_image()
                # Update combo box
                percent = int(self.zoom_factor * 100)
                self.zoom_combo.setCurrentText(f"{percent}%")
    
    def reset_view(self):
        """Reset view to 100%"""
        self.zoom_combo.setCurrentText("100%")
        self.scroll_area.verticalScrollBar().setValue(0)
        self.scroll_area.horizontalScrollBar().setValue(0)
    
    def toggle_fullscreen(self):
        """Toggle full-screen mode"""
        parent = self.parent()
        while parent and not isinstance(parent, QMainWindow):
            parent = parent.parent()
        
        if parent:
            self.is_fullscreen = not self.is_fullscreen
            if self.is_fullscreen:
                parent.showFullScreen()
            else:
                parent.showNormal()
    
    def load_image(self, file_path):
        """Load an image for editing"""
        self.current_file = file_path
        self.pixmap = QPixmap(file_path)
        self.original_pixmap = QPixmap(file_path)
        self.zoom_factor = 1.0
        self.zoom_combo.setCurrentText("100%")
        self.display_image()
        
        # Update info
        from PIL import Image
        img = Image.open(file_path)
        self.image_info_label.setText(f"🖼️ {os.path.basename(file_path)}  |  {img.width}×{img.height}  |  {img.format}")
    
    def display_image(self):
        """Display the current image with zoom"""
        if not self.pixmap:
            return
        
        # Apply zoom
        if self.zoom_combo.currentText() == "Fit to Window":
            self.fit_to_window()
            return
        
        width = int(self.pixmap.width() * self.zoom_factor)
        height = int(self.pixmap.height() * self.zoom_factor)
        
        scaled = self.pixmap.scaled(
            width,
            height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled)
        
        # Update zoom status
        percent = int(self.zoom_factor * 100)
        self.zoom_status_label.setText(f"Zoom: {percent}%")
        
        # Update label size
        self.image_label.setMinimumSize(width, height)
    
    def rotate_image(self, degrees):
        """Rotate the image"""
        if self.pixmap:
            transform = QTransform().rotate(degrees)
            self.pixmap = self.pixmap.transformed(transform)
            self.display_image()
    
    def flip_image(self, horizontal, vertical):
        """Flip the image"""
        if self.pixmap:
            transform = QTransform()
            if horizontal:
                transform.scale(-1, 1)
            if vertical:
                transform.scale(1, -1)
            self.pixmap = self.pixmap.transformed(transform)
            self.display_image()
    
    def adjust_brightness(self):
        """Adjust image brightness"""
        if not self.pixmap:
            return
        
        value, ok = QInputDialog.getInt(self, "Brightness", "Enter brightness (0-200):", 100, 0, 200)
        if ok:
            self.apply_pil_operation(ImageEnhance.Brightness, value / 100)
    
    def adjust_contrast(self):
        """Adjust image contrast"""
        if not self.pixmap:
            return
        
        value, ok = QInputDialog.getInt(self, "Contrast", "Enter contrast (0-200):", 100, 0, 200)
        if ok:
            self.apply_pil_operation(ImageEnhance.Contrast, value / 100)
    
    def apply_pil_operation(self, operation_class, factor):
        """Apply a PIL operation to the image"""
        if not self.pixmap:
            return
        
        # Convert QPixmap to PIL Image
        qimage = self.pixmap.toImage()
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        qimage.save(buffer, "PNG")
        
        pil_image = Image.open(io.BytesIO(buffer.data()))
        
        # Apply operation
        enhancer = operation_class(pil_image)
        enhanced = enhancer.enhance(factor)
        
        # Convert back to QPixmap
        buffer = io.BytesIO()
        enhanced.save(buffer, format="PNG")
        buffer.seek(0)
        
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(buffer.read())
        self.display_image()
    
    def apply_filter(self, filter_type):
        """Apply a PIL filter to the image"""
        if not self.pixmap:
            return
        
        # Convert QPixmap to PIL Image
        qimage = self.pixmap.toImage()
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        qimage.save(buffer, "PNG")
        
        pil_image = Image.open(io.BytesIO(buffer.data()))
        
        # Apply filter
        filtered = pil_image.filter(filter_type)
        
        # Convert back to QPixmap
        buffer = io.BytesIO()
        filtered.save(buffer, format="PNG")
        buffer.seek(0)
        
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(buffer.read())
        self.display_image()
    
    def crop_image(self):
        """Crop the image - opens a crop dialog"""
        if not self.pixmap:
            return
        
        # Simple crop dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Crop Image")
        dialog.setModal(True)
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Enter crop coordinates:"))
        
        grid = QGridLayout()
        grid.addWidget(QLabel("X:"), 0, 0)
        x_input = QLineEdit("0")
        grid.addWidget(x_input, 0, 1)
        
        grid.addWidget(QLabel("Y:"), 1, 0)
        y_input = QLineEdit("0")
        grid.addWidget(y_input, 1, 1)
        
        grid.addWidget(QLabel("Width:"), 2, 0)
        w_input = QLineEdit(str(self.pixmap.width()))
        grid.addWidget(w_input, 2, 1)
        
        grid.addWidget(QLabel("Height:"), 3, 0)
        h_input = QLineEdit(str(self.pixmap.height()))
        grid.addWidget(h_input, 3, 1)
        
        layout.addLayout(grid)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                x = int(x_input.text())
                y = int(y_input.text())
                w = int(w_input.text())
                h = int(h_input.text())
                
                if w > 0 and h > 0:
                    cropped = self.pixmap.copy(x, y, w, h)
                    if not cropped.isNull():
                        self.pixmap = cropped
                        self.display_image()
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid crop values!")
    
    def resize_image(self):
        """Resize the image"""
        if not self.pixmap:
            return
        
        width, ok = QInputDialog.getInt(self, "Resize", "Enter new width:", self.pixmap.width(), 1, 5000)
        if ok:
            height, ok2 = QInputDialog.getInt(self, "Resize", "Enter new height:", self.pixmap.height(), 1, 5000)
            if ok2:
                self.pixmap = self.pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.display_image()
    
    def reset_image(self):
        """Reset to original image"""
        if self.original_pixmap:
            self.pixmap = QPixmap(self.original_pixmap)
            self.zoom_factor = 1.0
            self.zoom_combo.setCurrentText("100%")
            self.display_image()
    
    def save_image(self):
        """Save the image"""
        if not self.pixmap:
            return
        
        if not self.current_file:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image",
                "image.png",
                "PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp)"
            )
            if not file_path:
                return
            self.current_file = file_path
        
        try:
            self.pixmap.save(self.current_file)
            QMessageBox.information(self, "Success", "Image saved successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save: {str(e)}")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pixmap and self.zoom_combo.currentText() == "Fit to Window":
            self.fit_to_window()