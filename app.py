import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import ThemeManager

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Apply theme
    ThemeManager.apply_theme(app, ThemeManager.LIGHT)  # or ThemeManager.DARK
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()