#!/usr/bin/env python3
"""
SleepSense - Medical Device GUI Application
Login page implementation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QLinearGradient, QColor

from src.auth.user_manager import JSONUserManager
from src.utils.logger import get_logger

class LoginPage(QWidget):
    """Login page widget with registration capability"""
    
    # Signals
    login_successful = Signal(object)  # Emits user object
    logout_requested = Signal()
    
    def __init__(self, auth_manager: JSONUserManager):
        super().__init__()
        self.auth_manager = auth_manager
        self.logger = get_logger(__name__)
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Connect signals
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left panel (visual/logo area)
        self.setup_left_panel(main_layout)
        
        # Right panel (forms)
        self.setup_right_panel(main_layout)
    
    def setup_left_panel(self, main_layout):
        """Setup the left visual panel"""
        left_panel = QFrame()
        left_panel.setObjectName("left-panel")
        left_panel.setFixedWidth(500)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(60, 80, 60, 80)
        
        # Logo/Title
        logo_label = QLabel("SleepSense")
        logo_label.setObjectName("logo-title")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Medical Device Interface")
        subtitle_label.setObjectName("logo-subtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        desc_label = QLabel("Advanced sleep monitoring and analysis system for medical professionals")
        desc_label.setObjectName("logo-description")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        
        left_layout.addStretch()
        left_layout.addWidget(logo_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addWidget(desc_label)
        left_layout.addStretch()
        
        main_layout.addWidget(left_panel)
    
    def setup_right_panel(self, main_layout):
        """Setup the right forms panel"""
        right_panel = QFrame()
        right_panel.setObjectName("right-panel")
        right_panel.setFixedWidth(500)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 80, 60, 80)
        
        # Stacked widget for login/register forms
        self.forms_stack = QStackedWidget()
        
        # Login form
        self.login_form = self.create_login_form()
        self.forms_stack.addWidget(self.login_form)
        
        # Registration form
        self.register_form = self.create_register_form()
        self.forms_stack.addWidget(self.register_form)
        
        right_layout.addWidget(self.forms_stack)
        
        # Switch between forms
        switch_layout = QHBoxLayout()
        switch_layout.addStretch()
        
        self.switch_to_register_btn = QPushButton("Create Account")
        self.switch_to_register_btn.setObjectName("switch-button")
        self.switch_to_register_btn.clicked.connect(lambda: self.forms_stack.setCurrentWidget(self.register_form))
        
        self.switch_to_login_btn = QPushButton("Already have an account?")
        self.switch_to_login_btn.setObjectName("switch-button")
        self.switch_to_login_btn.clicked.connect(lambda: self.forms_stack.setCurrentWidget(self.login_form))
        self.switch_to_login_btn.hide()  # Initially hidden
        
        switch_layout.addWidget(self.switch_to_register_btn)
        switch_layout.addWidget(self.switch_to_login_btn)
        
        right_layout.addLayout(switch_layout)
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel)
    
    def create_login_form(self):
        """Create the login form"""
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Welcome Back")
        title_label.setObjectName("form-title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setObjectName("form-input")
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(50)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setObjectName("form-input")
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(50)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setObjectName("form-checkbox")
        
        # Login button
        self.login_button = QPushButton("Log In")
        self.login_button.setObjectName("login-button")
        self.login_button.setMinimumHeight(50)
        
        # Forgot password link
        forgot_link = QLabel("Forgot password?")
        forgot_link.setObjectName("form-link")
        forgot_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        form_layout.addWidget(title_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_checkbox)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(forgot_link)
        
        return form_widget
    
    def create_register_form(self):
        """Create the registration form"""
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Create Account")
        title_label.setObjectName("form-title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Username field
        self.reg_username_input = QLineEdit()
        self.reg_username_input.setObjectName("form-input")
        self.reg_username_input.setPlaceholderText("Username (min 3 characters)")
        self.reg_username_input.setMinimumHeight(50)
        
        # Email field
        self.email_input = QLineEdit()
        self.email_input.setObjectName("form-input")
        self.email_input.setPlaceholderText("Email address")
        self.email_input.setMinimumHeight(50)
        
        # Password field
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setObjectName("form-input")
        self.reg_password_input.setPlaceholderText("Password (min 6 characters)")
        self.reg_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password_input.setMinimumHeight(50)
        
        # Confirm password field
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setObjectName("form-input")
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(50)
        
        # Register button
        self.register_button = QPushButton("Create Account")
        self.register_button.setObjectName("register-button")
        self.register_button.setMinimumHeight(50)
        
        form_layout.addWidget(title_label)
        form_layout.addWidget(self.reg_username_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.reg_password_input)
        form_layout.addWidget(self.confirm_password_input)
        form_layout.addWidget(self.register_button)
        
        return form_widget
    
    def connect_signals(self):
        """Connect all signals"""
        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.handle_register)
        
        # Show/hide switch buttons based on current form
        self.forms_stack.currentChanged.connect(self.on_form_changed)
    
    def on_form_changed(self, index):
        """Handle form switching"""
        if index == 0:  # Login form
            self.switch_to_register_btn.show()
            self.switch_to_login_btn.hide()
        else:  # Register form
            self.switch_to_register_btn.hide()
            self.switch_to_login_btn.show()
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
            return
        
        # Attempt login
        result = self.auth_manager.login(username, password)
        
        if result['success']:
            self.logger.info(f"User {username} logged in successfully")
            self.login_successful.emit(result['user'])
        else:
            QMessageBox.warning(self, "Login Failed", result['message'])
    
    def handle_register(self):
        """Handle user registration"""
        username = self.reg_username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.reg_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validation
        if not username or not email or not password or not confirm_password:
            QMessageBox.warning(self, "Registration Error", "Please fill in all fields.")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Registration Error", "Passwords do not match.")
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, "Registration Error", "Username must be at least 3 characters long.")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Registration Error", "Password must be at least 6 characters long.")
            return
        
        # Attempt registration
        result = self.auth_manager.register_user(username, email, password)
        
        if result['success']:
            QMessageBox.information(self, "Registration Successful", 
                                  "Account created successfully! You can now log in.")
            # Clear form and switch to login
            self.clear_register_form()
            self.forms_stack.setCurrentWidget(self.login_form)
        else:
            QMessageBox.warning(self, "Registration Failed", result['message'])
    
    def clear_register_form(self):
        """Clear the registration form fields"""
        self.reg_username_input.clear()
        self.email_input.clear()
        self.reg_password_input.clear()
        self.confirm_password_input.clear()
    
    def clear_login_form(self):
        """Clear the login form fields"""
        self.username_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
    
    def setup_styles(self):
        """Setup the page styles"""
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            #left-panel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:1 #2d2d2d);
                border-right: 1px solid #333333;
            }
            
            #right-panel {
                background-color: #000000;
            }
            
            #logo-title {
                font-size: 48px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 10px;
            }
            
            #logo-subtitle {
                font-size: 24px;
                color: #3498db;
                margin-bottom: 20px;
            }
            
            #logo-description {
                font-size: 16px;
                color: #cccccc;
                line-height: 1.5;
            }
            
            #form-title {
                font-size: 32px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 20px;
            }
            
            #form-input {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 25px;
                padding: 15px 20px;
                font-size: 16px;
                color: #ffffff;
            }
            
            #form-input:focus {
                border-color: #3498db;
                background-color: #1f1f1f;
            }
            
            #form-input::placeholder {
                color: #666666;
            }
            
            #login-button, #register-button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 20px;
            }
            
            #login-button:hover, #register-button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #1f5f8b);
            }
            
            #login-button:pressed, #register-button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1f5f8b, stop:1 #154360);
            }
            
            #form-checkbox {
                font-size: 14px;
                color: #cccccc;
                spacing: 10px;
            }
            
            #form-checkbox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #333333;
                border-radius: 4px;
                background-color: #1a1a1a;
            }
            
            #form-checkbox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            
            #form-link {
                font-size: 14px;
                color: #3498db;
                text-decoration: underline;
            }
            
            #form-link:hover {
                color: #2980b9;
            }
            
            #switch-button {
                background: transparent;
                border: 2px solid #3498db;
                color: #3498db;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #switch-button:hover {
                background-color: #3498db;
                color: #ffffff;
            }
        """)
