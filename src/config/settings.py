"""
Configuration settings for SleepSense application
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class Settings:
    """Application settings manager"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.settings = self._load_default_settings()
        self.load_settings()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings"""
        return {
            "app": {
                "name": "SleepSense",
                "version": "1.0.0",
                "theme": "dark",
                "language": "en"
            },
            "gui": {
                "window_width": 1200,
                "window_height": 800,
                "fullscreen": False,
                "auto_save": True
            },
            "data": {
                "sample_rate": 256,
                "channels": ["EEG", "EOG", "EMG", "ECG"],
                "recording_duration": 3600,  # seconds
                "data_format": "edf"
            },
            "security": {
                "session_timeout": 1800,  # 30 minutes
                "max_login_attempts": 3,
                "password_min_length": 8
            },
            "paths": {
                "data_directory": "data",
                "logs_directory": "logs",
                "exports_directory": "exports"
            }
        }
    
    def load_settings(self):
        """Load settings from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_settings = json.load(f)
                    self._merge_settings(file_settings)
        except Exception as e:
            print(f"Warning: Could not load settings file: {e}")
    
    def save_settings(self):
        """Save current settings to configuration file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save settings file: {e}")
    
    def _merge_settings(self, new_settings: Dict[str, Any]):
        """Merge new settings with existing ones"""
        def merge_dict(base, update):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self.settings, new_settings)
    
    def get(self, key_path: str, default=None):
        """Get a setting value using dot notation (e.g., 'app.name')"""
        keys = key_path.split('.')
        value = self.settings
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value):
        """Set a setting value using dot notation"""
        keys = key_path.split('.')
        current = self.settings
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value

def load_settings() -> Settings:
    """Load and return application settings"""
    return Settings()

# Global settings instance
settings = load_settings()
