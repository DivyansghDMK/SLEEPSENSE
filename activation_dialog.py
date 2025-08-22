"""
SleepSense Activation Dialog
============================

This dialog requires users to enter a valid activation key before they can access the main software.
"""

import sys
import hashlib
import json
import os
import datetime
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QMessageBox, QFrame,
    QTextEdit, QCheckBox, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap


class ActivationDialog(QDialog):
    """Dialog for entering activation key before accessing the main software"""
    
    # Signal emitted when activation is successful
    activation_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SleepSense - Activation Required")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Set window flags to make it stay on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        
        # Activation key storage file
        self.activation_file = "activation.json"
        
        # Valid activation keys (in production, these would be stored securely)
        self.valid_keys = [
            "SLEEPSENSE-2024-PRO-001",
            "SLEEPSENSE-2024-PRO-002", 
            "SLEEPSENSE-2024-PRO-003",
            "SLEEPSENSE-2024-STANDARD-001",
            "SLEEPSENSE-2024-STANDARD-002",
            "DEMO-KEY-2024-TEST"
        ]
        
        # Check if already activated
        if self.is_activated():
            self.activation_successful.emit()
            return
            
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        # Set modern style
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel("🔐 SleepSense Activation")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            font-size: 24px;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(header_label)
        
        # Subtitle
        subtitle_label = QLabel("Professional Sleep Analysis System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: #7f8c8d;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(subtitle_label)
        
        # Activation key input group
        key_group = QGroupBox("Enter Activation Key")
        key_layout = QVBoxLayout(key_group)
        
        # Key input field
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter your activation key here...")
        self.key_input.setMaxLength(50)
        self.key_input.returnPressed.connect(self.activate_key)
        self.key_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                font-weight: normal;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #ffffff;
                border-width: 3px;
            }
            QLineEdit:hover {
                border-color: #95a5a6;
            }
        """)
        
        # Ensure text is visible
        self.key_input.setText("")
        self.key_input.setClearButtonEnabled(True)
        
        key_layout.addWidget(self.key_input)
        
        # Key format hint
        format_hint = QLabel("Format: SLEEPSENSE-YYYY-TYPE-XXX")
        format_hint.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            font-style: italic;
        """)
        key_layout.addWidget(format_hint)
        
        main_layout.addWidget(key_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Activate button
        self.activate_btn = QPushButton("🔑 Activate")
        self.activate_btn.clicked.connect(self.activate_key)
        button_layout.addWidget(self.activate_btn)
        
        # Demo button
        demo_btn = QPushButton("🎯 Try Demo")
        demo_btn.setStyleSheet("""
            background-color: #27ae60;
        """)
        demo_btn.clicked.connect(self.use_demo_key)
        button_layout.addWidget(demo_btn)
        
        # Exit button
        exit_btn = QPushButton("❌ Exit")
        exit_btn.setStyleSheet("""
            background-color: #e74c3c;
        """)
        exit_btn.clicked.connect(self.reject)
        button_layout.addWidget(exit_btn)
        
        main_layout.addLayout(button_layout)
        
        # Information group
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(100)
        info_text.setPlainText(
            "SleepSense is a professional sleep analysis system that provides:\n"
            "• Real-time sleep data visualization\n"
            "• Multiple signal analysis (SpO2, Pulse, Airflow, etc.)\n"
            "• Advanced waveform processing\n"
            "• Professional reporting tools\n\n"
            "Contact support for activation keys or licensing information."
        )
        info_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
                font-size: 12px;
            }
        """)
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            padding: 10px;
            border-radius: 4px;
        """)
        main_layout.addWidget(self.status_label)
        
        # Set focus to key input
        self.key_input.setFocus()
        
        # Connect key input changes
        self.key_input.textChanged.connect(self.on_key_changed)
        
        # Test text input functionality
        self.key_input.textChanged.connect(self.debug_text_input)
        
        # Test text input with a sample
        QTimer.singleShot(1000, self.test_text_input)
        
    def on_key_changed(self, text):
        """Handle key input changes"""
        if text.strip():
            self.activate_btn.setEnabled(True)
            self.status_label.setText("")
            self.status_label.setStyleSheet("")
        else:
            self.activate_btn.setEnabled(False)
            
    def debug_text_input(self, text):
        """Debug method to verify text input is working"""
        print(f"Text input changed: '{text}' (length: {len(text)})")
        # Update status to show what's being typed
        if text:
            self.status_label.setText(f"Typing: {text}")
            self.status_label.setStyleSheet("""
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            """)
        else:
            self.status_label.setText("")
            self.status_label.setStyleSheet("")
            
    def test_text_input(self):
        """Test method to verify text input is working"""
        print("Testing text input...")
        self.key_input.setText("TEST-INPUT")
        print(f"Text input value: '{self.key_input.text()}'")
        # Clear after 2 seconds
        QTimer.singleShot(2000, lambda: self.key_input.setText(""))
            
    def activate_key(self):
        """Attempt to activate with the entered key"""
        key = self.key_input.text().strip().upper()
        
        if not key:
            self.show_status("Please enter an activation key", "error")
            return
            
        if self.validate_key(key):
            self.save_activation(key)
            self.show_status("✅ Activation successful! Starting SleepSense...", "success")
            
            # Auto-close after showing success message
            QTimer.singleShot(2000, self.accept_activation)
        else:
            self.show_status("❌ Invalid activation key. Please try again.", "error")
            self.key_input.selectAll()
            self.key_input.setFocus()
            
    def use_demo_key(self):
        """Use demo key for testing"""
        demo_key = "DEMO-KEY-2024-TEST"
        self.key_input.setText(demo_key)
        self.activate_key()
        
    def validate_key(self, key):
        """Validate the activation key"""
        # Check if key is in valid keys list
        if key in self.valid_keys:
            return True
            
        # Additional validation logic could be added here
        # For example, checking against a server, validating checksums, etc.
        
        return False
        
    def save_activation(self, key):
        """Save activation information to file"""
        activation_data = {
            "activated": True,
            "key": key,
            "timestamp": str(datetime.datetime.now()),
            "version": "2024.1.0"
        }
        
        try:
            with open(self.activation_file, 'w') as f:
                json.dump(activation_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save activation file: {e}")
            
    def is_activated(self):
        """Check if software is already activated"""
        if not os.path.exists(self.activation_file):
            return False
            
        try:
            with open(self.activation_file, 'r') as f:
                data = json.load(f)
                return data.get("activated", False)
        except Exception:
            return False
            
    def show_status(self, message, status_type):
        """Show status message with appropriate styling"""
        self.status_label.setText(message)
        
        if status_type == "success":
            self.status_label.setStyleSheet("""
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            """)
        elif status_type == "error":
            self.status_label.setStyleSheet("""
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            """)
            
    def accept_activation(self):
        """Accept the dialog and emit success signal"""
        self.accept()
        self.activation_successful.emit()
        
    def closeEvent(self, event):
        """Handle close event"""
        reply = QMessageBox.question(
            self, 
            'Exit SleepSense', 
            'Are you sure you want to exit? You need to activate the software to use it.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit(0)
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ActivationDialog()
    
    # If already activated, don't show dialog
    if not dialog.is_activated():
        result = dialog.exec_()
        if result == QDialog.Accepted:
            print("Activation successful!")
        else:
            print("Activation cancelled or failed.")
    else:
        print("Already activated!")
        
    sys.exit(0)
