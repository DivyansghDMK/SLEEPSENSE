#!/usr/bin/env python3
"""
SleepSense - Medical Device GUI Application
Main window implementation
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QLabel, QPushButton, QMenuBar, 
    QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from src.auth.user_manager import JSONUserManager
from src.gui.login_page import LoginPage
from src.gui.medical_data_page import MedicalDataPage
from src.gui.waveforms_page import WaveformsPage
from src.utils.logger import get_logger

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Initialize authentication manager
        self.auth_manager = JSONUserManager()
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.apply_theme()
        
        # Connect signals
        self.login_page.login_successful.connect(self.on_login_successful)
        # self.login_page.logout_requested.connect(self.on_logout_requested)  # Commented out - no longer needed
        
        # Show login page initially
        self.stacked_widget.setCurrentWidget(self.login_page)
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("SleepSense - Medical Device")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.setup_header()
        main_layout.addWidget(self.header_widget)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.create_pages()
    
    def setup_header(self):
        """Setup the application header"""
        self.header_widget = QWidget()
        self.header_widget.setObjectName("header")
        self.header_widget.setFixedHeight(80)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo/Title
        title_label = QLabel("SleepSense")
        title_label.setObjectName("header-title")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: white;
                background: transparent;
            }
        """)
        
        # Spacer
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # User info and logout button removed since we stay on login page
        # self.user_info_label = QLabel()
        # self.logout_button = QPushButton("Logout")
        # ... (commented out - no longer needed)
    
    def create_pages(self):
        """Create application pages"""
        # Login page
        self.login_page = LoginPage(self.auth_manager)
        self.stacked_widget.addWidget(self.login_page)
        
        # Medical data page - shows after authentication
        self.medical_data_page = MedicalDataPage(self.auth_manager, self.settings, self)
        self.stacked_widget.addWidget(self.medical_data_page)
        
        # Waveforms page
        self.waveforms_page = WaveformsPage(self.auth_manager, self.settings, self)
        self.stacked_widget.addWidget(self.waveforms_page)
    
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_recording_action = QAction("New Recording", self)
        new_recording_action.setShortcut("Ctrl+N")
        new_recording_action.triggered.connect(self.new_recording)
        file_menu.addAction(new_recording_action)
        
        open_file_action = QAction("Open File", self)
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        medical_data_action = QAction("Medical Data", self)
        medical_data_action.triggered.connect(self.show_medical_data_page)
        tools_menu.addAction(medical_data_action)
        
        analyze_action = QAction("Analyze Data", self)
        analyze_action.triggered.connect(self.show_waveforms_page)
        tools_menu.addAction(analyze_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def apply_theme(self):
        """Apply the application theme"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:1 #2d2d2d);
            }
            
            #header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-bottom: 2px solid #3498db;
            }
            
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                color: white;
                border: none;
            }
            
            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
            }
            
            QMenuBar::item:selected {
                background: rgba(52, 152, 219, 0.3);
                border-radius: 4px;
            }
            
            QMenu {
                background: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
            }
            
            QMenu::item {
                padding: 8px 20px;
            }
            
            QMenu::item:selected {
                background: rgba(52, 152, 219, 0.3);
            }
            
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                color: white;
                border-top: 1px solid #34495e;
            }
        """)
    
    def on_login_successful(self, user):
        """Handle successful login"""
        if user:
            # Show success popup
            QMessageBox.information(self, "Sign In Successful", 
                                  f"Welcome, {user.username}! You have been successfully authenticated.")
            
            # Switch to medical data page
            self.stacked_widget.setCurrentWidget(self.medical_data_page)
            
            # Update status bar
            self.status_bar.showMessage(f"Signed in as {user.username}")
            
            # Clear login form
            self.login_page.clear_login_form()
        else:
            self.logger.error("Login successful but user object is None")
    
    def on_logout_requested(self):
        """Handle logout request - no longer used"""
        # This method is no longer needed since we stay on login page
        pass
    
    def new_recording(self):
        """Start a new recording"""
        self.status_bar.showMessage("Starting new recording...")
        # TODO: Implement recording functionality
    
    def open_file(self):
        """Open a file"""
        self.status_bar.showMessage("Opening file...")
        # TODO: Implement file opening functionality
    
    def show_medical_data_page(self):
        """Show the medical data page"""
        self.stacked_widget.setCurrentWidget(self.medical_data_page)
        self.status_bar.showMessage("Showing medical data")
    
    def show_waveforms_page(self):
        """Show the waveforms page"""
        self.stacked_widget.setCurrentWidget(self.waveforms_page)
        self.status_bar.showMessage("Showing waveforms")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About SleepSense", 
                         "SleepSense Medical Device GUI\nVersion 1.0.0\n\n"
                         "A comprehensive medical device interface for sleep analysis.")
