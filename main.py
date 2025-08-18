#!/usr/bin/env python3
"""
SleepSense - Medical Device GUI Application
Main entry point for the application
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MainWindow
from src.utils.logger import setup_logging
from src.config.settings import load_settings

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    
    # Load application settings
    settings = load_settings()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("SleepSense")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SleepSense Medical")
    
    # Set application icon (if available)
    icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    main_window = MainWindow(settings)
    main_window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
