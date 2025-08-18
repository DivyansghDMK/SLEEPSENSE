"""
JSON-based user management system for SleepSense application
"""

import json
import hashlib
import secrets
import time
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

@dataclass
class User:
    """User data structure"""
    id: str
    username: str
    email: str
    password_hash: str
    role: str
    created_at: str
    last_login: Optional[str]
    is_active: bool

class JSONUserManager:
    """Manages users using JSON file storage"""
    
    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        self.session_token: Optional[str] = None
        self.session_expiry: Optional[float] = None
        self._load_users()
        self._ensure_default_admin()
    
    def _load_users(self):
        """Load users from JSON file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                    self.users = {}
                    for user_id, user_data in users_data.items():
                        self.users[user_id] = User(**user_data)
            else:
                self.users = {}
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = {}
    
    def _save_users(self):
        """Save users to JSON file"""
        try:
            users_data = {}
            for user_id, user in self.users.items():
                users_data[user_id] = asdict(user)
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving users: {e}")
            raise
    
    def _ensure_default_admin(self):
        """Ensure default admin user exists"""
        if not any(user.role == 'admin' for user in self.users.values()):
            self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_id = self._generate_user_id()
        admin_password = "admin123"  # Change this in production!
        password_hash = self._hash_password(admin_password)
        
        admin_user = User(
            id=admin_id,
            username="admin",
            email="admin@sleepsense.com",
            password_hash=password_hash,
            role="admin",
            created_at=datetime.now().isoformat(),
            last_login=None,
            is_active=True
        )
        
        self.users[admin_id] = admin_user
        self._save_users()
        print("Default admin user created")
    
    def _generate_user_id(self) -> str:
        """Generate a unique user ID"""
        return secrets.token_urlsafe(16)
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def register_user(self, username: str, email: str, password: str, role: str = "user") -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if username already exists
            if any(user.username == username for user in self.users.values()):
                return {
                    'success': False,
                    'message': 'Username already exists'
                }
            
            # Check if email already exists
            if any(user.email == email for user in self.users.values()):
                return {
                    'success': False,
                    'message': 'Email already exists'
                }
            
            # Validate password strength
            if len(password) < 6:
                return {
                    'success': False,
                    'message': 'Password must be at least 6 characters long'
                }
            
            # Create new user
            user_id = self._generate_user_id()
            password_hash = self._hash_password(password)
            
            new_user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                created_at=datetime.now().isoformat(),
                last_login=None,
                is_active=True
            )
            
            self.users[user_id] = new_user
            self._save_users()
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': new_user
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Registration error: {str(e)}'
            }
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            # Find user by username
            user = None
            for u in self.users.values():
                if u.username == username and u.is_active:
                    user = u
                    break
            
            if not user:
                return {
                    'success': False,
                    'message': 'Invalid username or password'
                }
            
            # Check password
            if user.password_hash != self._hash_password(password):
                return {
                    'success': False,
                    'message': 'Invalid username or password'
                }
            
            # Update last login
            user.last_login = datetime.now().isoformat()
            self._save_users()
            
            # Set current user
            self.current_user = user
            
            # Generate session
            session_result = self._create_session(user.id)
            
            return {
                'success': True,
                'user': user,
                'session_token': session_result['token'],
                'message': 'Login successful'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Login error: {str(e)}'
            }
    
    def _create_session(self, user_id: str) -> Dict[str, Any]:
        """Create a new user session"""
        token = self._generate_session_token()
        expires_at = time.time() + 1800  # 30 minutes
        
        self.session_token = token
        self.session_expiry = expires_at
        
        return {
            'token': token,
            'expires_at': expires_at
        }
    
    def validate_session(self, token: str) -> bool:
        """Validate if a session token is still valid"""
        if not self.session_token or token != self.session_token:
            return False
        
        if time.time() > self.session_expiry:
            self.logout()
            return False
        
        return True
    
    def logout(self):
        """Logout current user and invalidate session"""
        self.current_user = None
        self.session_token = None
        self.session_expiry = None
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        if not self.current_user or not self.session_token:
            return False
        
        if time.time() > self.session_expiry:
            self.logout()
            return False
        
        return True
    
    def has_role(self, role: str) -> bool:
        """Check if current user has the specified role"""
        return self.is_authenticated() and self.current_user.role == role
    
    def get_current_user(self) -> Optional[User]:
        """Get current authenticated user"""
        return self.current_user if self.is_authenticated() else None
    
    def get_all_users(self) -> List[User]:
        """Get all users (admin only)"""
        if not self.has_role('admin'):
            return []
        return list(self.users.values())
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user information (admin only)"""
        if not self.has_role('admin'):
            return False
        
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ['id', 'password_hash']:
                setattr(user, key, value)
        
        self._save_users()
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user (admin only)"""
        if not self.has_role('admin'):
            return False
        
        if user_id not in self.users:
            return False
        
        # Don't allow admin to delete themselves
        if self.current_user and self.current_user.id == user_id:
            return False
        
        del self.users[user_id]
        self._save_users()
        return True
    
    def reset_database(self):
        """Reset the user database (useful for testing)"""
        try:
            if os.path.exists(self.users_file):
                os.remove(self.users_file)
            self.users = {}
            self._ensure_default_admin()
            print("User database reset successfully")
        except Exception as e:
            print(f"Error resetting database: {e}")
