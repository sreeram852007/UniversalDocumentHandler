"""
Universal Document Handler - Main Entry Point
A free, professional document viewer, editor, and converter for Windows
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap

from ui.main_window import MainWindow
from ui.styles import ThemeManager


def main():
    """Main application entry point"""
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application metadata
    app.setApplicationName("Universal Document Handler")
    app.setApplicationDisplayName("UDH Pro")
    app.setOrganizationName("UDH")
    app.setOrganizationDomain("udh.app")
    
    # Optional: Set application icon (if you have an icon file)
    # icon_path = os.path.join(os.path.dirname(__file__), "resources", "app.ico")
    # if os.path.exists(icon_path):
    #     app.setWindowIcon(QIcon(icon_path))
    
    # Apply theme (Light by default)
    ThemeManager.apply_theme(app, ThemeManager.LIGHT)
    
    # Optional: Show splash screen
    # splash = QSplashScreen()
    # splash.setPixmap(QPixmap("resources/splash.png"))
    # splash.show()
    # QApplication.processEvents()
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Close splash screen after window shows
    # splash.finish(window)
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()