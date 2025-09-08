"""
Application settings and configuration management
"""

import os
from pathlib import Path
from .constants import *


class AppSettings:
    """Application settings management"""
    
    def __init__(self):
        self.screen_width = 1920
        self.screen_height = 1080
        self.is_small_screen = False
        self.window_size = DEFAULT_WINDOW_SIZE
        self.min_window_size = MIN_WINDOW_SIZE
        self.max_window_size = 3600.0
        self.sample_rate = DEFAULT_SAMPLE_RATE
        self.current_view_mode = 'all'
        self.comparison_mode = False
        self.sync_time_navigation = True
        self.comparison_time_offset = 0.0
        self.osa_analysis_mode = False
        self.signal_offsets = SIGNAL_OFFSETS.copy()
        self.signal_scales = DEFAULT_SIGNAL_SCALES.copy()
        # Absolute study bounds (do not mutate during navigation)
        self.data_start_time = 0.0
        self.data_end_time = 0.0
        
    def update_screen_dimensions(self, width, height):
        """Update screen dimensions and adjust settings accordingly"""
        self.screen_width = width
        self.screen_height = height
        self.is_small_screen = width < 1024
        
    def get_window_geometry(self):
        """Get appropriate window geometry based on screen size"""
        if self.screen_width < 1024:  # Small screens
            return (50, 50, int(self.screen_width * 0.95), int(self.screen_height * 0.9))
        elif self.screen_width < 1440:  # Medium screens
            return (100, 100, int(self.screen_width * 0.85), int(self.screen_height * 0.85))
        else:  # Large screens
            return (100, 100, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    
    def get_minimum_size(self):
        """Get minimum window size based on screen size"""
        if self.is_small_screen:
            return (MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        else:
            return (1000, 700)
    
    def get_font_size(self):
        """Get appropriate font size based on screen size"""
        return "12px" if not self.is_small_screen else "11px"
    
    def get_button_height(self):
        """Get appropriate button height based on screen size"""
        return "40px" if not self.is_small_screen else "45px"
    
    def get_downloads_path(self):
        """Get the Downloads folder path with fallbacks"""
        try:
            # Method 1: Standard user Downloads
            downloads_path = str(Path.home() / DEFAULT_DOWNLOADS_PATH)
            if os.path.exists(downloads_path):
                return downloads_path
            
            # Method 2: Windows specific
            downloads_path = os.path.join(os.path.expanduser("~"), DEFAULT_DOWNLOADS_PATH)
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
