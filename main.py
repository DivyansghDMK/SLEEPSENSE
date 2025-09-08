#!/usr/bin/env python3
"""
SleepSense Pro - Professional Sleep Analysis System
Modular Architecture Version

Main entry point for the application.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import SleepSenseMainWindow


def main():
    """Main entry point for SleepSense Pro"""
    # Set High DPI scaling before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("SleepSense Pro")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("SleepSense Pro Team")
    
    try:
        # Create and show main window
        window = SleepSenseMainWindow()
        window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error starting SleepSense Pro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
