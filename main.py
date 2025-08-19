#!/usr/bin/env python3
"""
SleepSense - Authentication System
Simplified main entry point for authentication only
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.auth.authentication import AuthenticationManager
from src.auth.user_manager import JSONUserManager
from src.utils.logger import setup_logging

class SimpleAuthWindow(QMainWindow):
    """Simple authentication window"""
    
    def __init__(self):
        super().__init__()
        self.auth = AuthenticationManager()
        self.user_manager = JSONUserManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("SleepSense - Authentication")
        self.setGeometry(400, 300, 500, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("SleepSense Authentication")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 16px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 16px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        layout.addWidget(self.password_input)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #21618c;
            }
        """)
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        
        # Register button
        register_btn = QPushButton("Register New User")
        register_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                padding: 12px;
                font-size: 14px;
                border-radius: 6px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        register_btn.clicked.connect(self.register)
        layout.addWidget(register_btn)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.status_label)
        
        # Add some spacing
        layout.addStretch()
        
    def login(self):
        """Handle login attempt"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.status_label.setText("Please enter both username and password")
            return
        
        try:
            # Try authentication with both managers
            auth_result = self.auth.login(username, password)
            if auth_result['success']:
                self.status_label.setText("✅ Login successful!")
                self.status_label.setStyleSheet("color: #27ae60; font-size: 14px; margin-top: 10px;")
                QMessageBox.information(self, "Success", f"Welcome, {username}!")
                return
            
            # Try JSON user manager as fallback
            json_result = self.user_manager.login(username, password)
            if json_result['success']:
                self.status_label.setText("✅ Login successful!")
                self.status_label.setStyleSheet("color: #27ae60; font-size: 14px; margin-top: 10px;")
                QMessageBox.information(self, "Success", f"Welcome, {username}!")
                return
            
            # Both failed
            self.status_label.setText("❌ Invalid username or password")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; margin-top: 10px;")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; margin-top: 10px;")
    
    def register(self):
        """Handle user registration"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.status_label.setText("Please enter both username and password")
            return
        
        if len(password) < 6:
            self.status_label.setText("Password must be at least 6 characters")
            return
        
        try:
            # Use JSON user manager for registration
            result = self.user_manager.register_user(username, f"{username}@example.com", password)
            if result['success']:
                self.status_label.setText("✅ User registered successfully!")
                self.status_label.setStyleSheet("color: #27ae60; font-size: 14px; margin-top: 10px;")
                QMessageBox.information(self, "Success", f"User {username} registered successfully!")
            else:
                self.status_label.setText(f"❌ {result['message']}")
                self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; margin-top: 10px;")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; margin-top: 10px;")

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("SleepSense Auth")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SleepSense")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show authentication window
    auth_window = SimpleAuthWindow()
    auth_window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
