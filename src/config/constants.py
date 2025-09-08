"""
Constants and configuration values for SleepSense Pro
"""

# Signal Configuration
SIGNAL_OFFSETS = {
    'body_pos': 0, 'pulse': 1.2, 'spo2': 2.4, 'flow': 3.6, 'snore': 4.8,
    'thorax': 6.0, 'abdomen': 7.2, 'pleth': 8.4, 'activity': 9.6,
    'eeg_c3': 10.8, 'eeg_c4': 12.0, 'eeg_f3': 13.2, 'eeg_f4': 14.4,
    'eeg_o1': 15.6, 'eeg_o2': 16.8
}

# Default Signal Scales
DEFAULT_SIGNAL_SCALES = {key: 1.0 for key in SIGNAL_OFFSETS}

# Window Settings
DEFAULT_WINDOW_SIZE = 10.0
MIN_WINDOW_SIZE = 1.0
DEFAULT_SAMPLE_RATE = 10.0

# Frame Sizes (in seconds)
FRAME_SIZES = [5, 10, 30, 60, 120, 300, 600, 1800]

# Analysis Thresholds
APNEA_THRESHOLD = 0.1  # 90% reduction
HYPOPNEA_THRESHOLD = 0.3  # 70% reduction
MIN_EVENT_DURATION = 10.0  # seconds

# UI Colors
COLORS = {
    'primary': '#3498db',
    'secondary': '#2c3e50',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Signal Colors
SIGNAL_COLORS = {
    'Position': '#9e9e9e',
    'Pulse': '#f44336',
    'SpO2': '#2196f3',
    'Airflow': '#ff9800',
    'Snore': '#e91e63',
    'Thorax': '#4caf50',
    'Abdomen': '#cddc39',
    'Pleth': '#9c27b0',
    'Activity': '#ffeb3b',
    'C3-A2': '#00bcd4',
    'C4-A1': '#009688',
    'F3-A2': '#8bc34a',
    'F4-A1': '#ffc107',
    'O1-A2': '#795548',
    'O2-A1': '#607d8b'
}

# File Paths
DEFAULT_DATA_FILE = "DATA0025.TXT"
DEFAULT_DOWNLOADS_PATH = "Downloads"

# UI Dimensions
DEFAULT_WINDOW_WIDTH = 1600
DEFAULT_WINDOW_HEIGHT = 1000
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600
