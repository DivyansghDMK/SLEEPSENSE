"""
Helper functions for SleepSense Pro
"""

import os
from pathlib import Path


def get_downloads_path():
    """Get the Downloads folder path with fallbacks"""
    try:
        # Method 1: Standard user Downloads
        downloads_path = str(Path.home() / "Downloads")
        if os.path.exists(downloads_path):
            return downloads_path
        
        # Method 2: Windows specific
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(downloads_path):
            return downloads_path
        
        # Method 3: Desktop as fallback
        downloads_path = str(Path.home() / "Desktop")
        if os.path.exists(downloads_path):
            return downloads_path
        
        # Method 4: Current directory
        return os.getcwd()
    except Exception:
        return os.getcwd()


def format_time(seconds):
    """Format time in HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_time_range(start_time, end_time):
    """Format time range as start-end"""
    start_str = format_time(start_time)
    end_str = format_time(end_time)
    return f"{start_str}-{end_str}"


def validate_data_file(file_path):
    """Validate if data file exists and is readable"""
    if not os.path.exists(file_path):
        return False, f"File {file_path} does not exist"
    
    if not os.access(file_path, os.R_OK):
        return False, f"File {file_path} is not readable"
    
    return True, "File is valid"


def create_directory_if_not_exists(directory_path):
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True, f"Directory {directory_path} created or already exists"
    except Exception as e:
        return False, f"Error creating directory {directory_path}: {e}"


def get_file_size_mb(file_path):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
    except Exception:
        return 0.0
