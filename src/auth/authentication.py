"""
Authentication system for SleepSense application
"""

import hashlib
import secrets
import sqlite3
import time
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class User:
    """User data structure"""
    id: int
    username: str
    email: str
    role: str
    created_at: str
    last_login: str
    is_active: bool

class AuthenticationManager:
    """Manages user authentication and sessions"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.current_user: Optional[User] = None
        self.session_token: Optional[str] = None
        self.session_expiry: Optional[float] = None
        self._init_database()
    
    def _get_connection(self):
        """Get a database connection with proper timeout and error handling"""
        try:
            # Set timeout to 30 seconds to handle database locks
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            # Set journal mode to WAL for better concurrency
            conn.execute("PRAGMA journal_mode = WAL")
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def _init_database(self):
        """Initialize the user database"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create default admin user if no users exist
            cursor.execute('SELECT COUNT(*) FROM users')
            if cursor.fetchone()[0] == 0:
                self._create_default_admin()
            
            conn.commit()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_password = "admin123"  # Change this in production!
        password_hash = self._hash_password(admin_password)
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', ('admin', 'admin@sleepsense.com', password_hash, 'admin'))
            conn.commit()
        except Exception as e:
            print(f"Error creating default admin: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get user by username
            cursor.execute('''
                SELECT id, username, email, role, created_at, last_login, is_active
                FROM users WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, self._hash_password(password)))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                ''', (user_data[0],))
                
                # Create user object
                self.current_user = User(*user_data)
                
                # Generate session
                session_result = self._create_session(user_data[0])
                
                conn.commit()
                
                return {
                    'success': True,
                    'user': self.current_user,
                    'session_token': session_result['token'],
                    'message': 'Login successful'
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid username or password'
                }
                
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                return {
                    'success': False,
                    'message': 'Database is temporarily locked. Please try again in a moment.'
                }
            else:
                return {
                    'success': False,
                    'message': f'Database error: {str(e)}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Login error: {str(e)}'
            }
        finally:
            if conn:
                conn.close()
    
    def _create_session(self, user_id: int) -> Dict[str, Any]:
        """Create a new user session"""
        token = self._generate_session_token()
        expires_at = time.time() + 1800  # 30 minutes
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Clean up expired sessions
            cursor.execute('DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP')
            
            # Create new session
            cursor.execute('''
                INSERT INTO sessions (user_id, token, expires_at)
                VALUES (?, ?, datetime(?, 'unixepoch'))
            ''', (user_id, token, expires_at))
            
            conn.commit()
            
            self.session_token = token
            self.session_expiry = expires_at
            
            return {
                'token': token,
                'expires_at': expires_at
            }
        except Exception as e:
            print(f"Error creating session: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def validate_session(self, token: str) -> bool:
        """Validate if a session token is still valid"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, expires_at FROM sessions 
                WHERE token = ? AND expires_at > CURRENT_TIMESTAMP
            ''', (token,))
            
            session_data = cursor.fetchone()
            
            if session_data:
                user_id, expires_at = session_data
                # Update current user if needed
                if not self.current_user or self.current_user.id != user_id:
                    self._load_user_by_id(user_id)
                return True
            
            return False
            
        except Exception as e:
            print(f"Session validation error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def _load_user_by_id(self, user_id: int):
        """Load user data by ID"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, role, created_at, last_login, is_active
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user_data = cursor.fetchone()
            
            if user_data:
                self.current_user = User(*user_data)
                
        except Exception as e:
            print(f"Error loading user: {e}")
        finally:
            if conn:
                conn.close()
    
    def logout(self):
        """Logout current user and invalidate session"""
        if self.session_token:
            conn = None
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM sessions WHERE token = ?', (self.session_token,))
                conn.commit()
            except Exception as e:
                print(f"Logout error: {e}")
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()
        
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
    
    def reset_database(self):
        """Reset the database (useful for testing)"""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            self._init_database()
            print("Database reset successfully")
        except Exception as e:
            print(f"Error resetting database: {e}")
