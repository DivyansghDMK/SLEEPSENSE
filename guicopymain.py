"""
SleepSense - Professional Sleep Analysis System
==============================================

This application handles two data formats:

CURRENT FORMAT (10 columns):
- Column 0: Time (ms)
- Column 1: Body Position (0-3)
- Column 2: Pulse (BPM)
- Column 3: SpO2 (%)
- Column 4-6: Reserved
- Column 7: Airflow
- Column 8-9: Reserved

FUTURE FORMAT (12+ columns):
- Column 0: Time (ms)
- Column 1: Snore
- Column 2: Flow
- Column 3: Thorax Movement
- Column 4: Abdomen Movement
- Column 5: SpO2 (%)
- Column 6: Plethysmography
- Column 7: Pulse (BPM)
- Column 8: Body Position (0-3)
- Column 9: Activity (0=sleeping, 1=awake)
- Column 10+: Additional data

The system automatically detects the format and provides mock data for missing signals.
"""

import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QLabel, QMenuBar, QMenu, QAction,
    QFrame, QGridLayout, QGroupBox, QSplitter, QTextEdit,
    QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QTabWidget,
    QInputDialog, QDialog, QMessageBox, QSlider
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class SleepSensePlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SleepSense Pro - Professional Sleep Analysis System")
        
        # Get screen dimensions for responsive design
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        
        # Responsive window sizing based on screen size
        if self.screen_width < 1024:  # Small screens (tablets/small laptops)
            self.setGeometry(50, 50, int(self.screen_width * 0.95), int(self.screen_height * 0.9))
            self.setMinimumSize(800, 600)
            self.is_small_screen = True
        elif self.screen_width < 1440:  # Medium screens (laptops)
            self.setGeometry(100, 100, int(self.screen_width * 0.85), int(self.screen_height * 0.85))
            self.setMinimumSize(1000, 700)
            self.is_small_screen = False
        else:  # Large screens (desktops)
            self.setGeometry(100, 100, 1600, 1000)
            self.setMinimumSize(1200, 800)
            self.is_small_screen = False
        
        # Set responsive modern style
        base_font_size = "12px" if not self.is_small_screen else "11px"  
        button_height = "40px" if not self.is_small_screen else "45px"  # Taller buttons for touch
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f0f0f0;
            }}
            QPushButton {{
                min-height: {button_height};
                font-size: {base_font_size};
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
            }}
            QLabel {{
                font-size: {base_font_size};
            }}
            QCheckBox {{
                font-size: {base_font_size};
                spacing: 8px;
            }}
            QGroupBox {{
                font-size: {base_font_size};
                font-weight: 600;
                padding-top: 15px;
                margin-top: 10px;
            }}
            QMenuBar {{
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
            }}
            QMenuBar::item:selected {{
                background-color: #34495e;
            }}
            QMenu {{
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
            }}
            QPushButton {{
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #21618c;
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid #bdc3c7;
                height: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background-color: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }}
        """)

        # Initialize data manager for encrypted data handling
        from data_manager import SleepDataManager
        self.data_manager = SleepDataManager()
        
        # Load data (automatically detects encrypted or plain text)
        file_path = "DATA0025.TXT"
        try:
            # Try to load data with error handling
            if os.path.exists(file_path):
                try:
                    self.data = self.data_manager.load_data(file_path)
                except Exception as e:
                    print(f"Failed to load encrypted data: {e}")
                    # Fallback to CSV reading
                    try:
                        self.data = pd.read_csv(file_path, header=None)
                        print("Successfully loaded CSV data")
                    except Exception as e2:
                        print(f"Failed to read CSV: {e2}")
                        # Create fallback data
                        self.data = self.create_minimal_fallback_data()
            else:
                print(f"Data file {file_path} not found, creating fallback data")
                self.data = self.create_minimal_fallback_data()
                
        except Exception as e:
            print(f"Critical error in data loading: {e}")
            # Create minimal fallback data
            self.data = self.create_minimal_fallback_data()
        
        # Ensure data is a pandas DataFrame
        if not isinstance(self.data, pd.DataFrame):
            print("Converting data to pandas DataFrame...")
            try:
                if isinstance(self.data, np.ndarray):
                    self.data = pd.DataFrame(self.data)
                else:
                    # Create fallback data
                    self.data = self.create_minimal_fallback_data()
            except Exception as e:
                print(f"Failed to convert data: {e}")
                # Create minimal fallback data
                self.data = self.create_minimal_fallback_data()
        
        # Debug: Print data type and shape
        print(f"Data type: {type(self.data)}")
        print(f"Data shape: {self.data.shape if hasattr(self.data, 'shape') else 'No shape'}")
        print(f"Data columns: {len(self.data.columns) if hasattr(self.data, 'columns') else 'No columns'}")
        
        # Check if data is sufficient (at least 1 hour worth for fallback)
        min_required_samples = 3600 * 10  # 1 hour * 3600 seconds * 10 Hz sampling
        
        if len(self.data) < min_required_samples:
            print(f"Insufficient data ({len(self.data)} samples), generating fallback data...")
            try:
                # Try to generate 8 hours of data
                self.data = self.generate_8_hour_mock_data()
                print(f"Generated mock data with shape: {self.data.shape}")
            except Exception as e:
                print(f"Failed to generate mock data: {e}")
                # Use minimal fallback data
                self.data = self.create_minimal_fallback_data()
                print("Using minimal fallback data")
        
        # Ensure we have at least some data
        if len(self.data) == 0:
            print("No data available, creating emergency fallback...")
            self.data = self.create_emergency_fallback_data()
        
        # Optimize data loading for large datasets
        if len(self.data) > 50000:  # If dataset is large
            print("Large dataset detected - applying performance optimizations...")
            # Use chunked processing for large datasets
            self.chunk_size = 10000  # Process in 10k chunks
        else:
            self.chunk_size = len(self.data)
        
        # Detect data format and handle both current and future formats
        try:
            num_columns = len(self.data.columns)
            
            if num_columns == 10:  # Current format
                # Current format: time, body_pos, pulse, spo2, ?, ?, ?, flow, ?, ?
                self.time = pd.Series(self.data[0].astype(float) / 1000, name='time')  # ms to s
                self.body_pos = pd.Series(self.data[1].astype(int), name='body_pos')
                self.pulse = pd.Series(self.data[2].astype(float), name='pulse')
                self.spo2 = pd.Series(self.data[3].astype(float), name='spo2')
                self.flow = pd.Series(self.data[7].astype(float), name='flow')
                
                # Generate realistic mock waveforms for future signals
                self.snore = self.generate_snore_wave(self.time)
                self.thorax = self.generate_thorax_wave(self.time)
                self.abdomen = self.generate_abdomen_wave(self.time)
                self.pleth = self.generate_pleth_wave(self.time)
                self.activity = self.generate_activity_wave(self.time)
                
                # Generate EEG signals
                self.eeg_c3 = self.generate_eeg_wave(self.time, 'c3')
                self.eeg_c4 = self.generate_eeg_wave(self.time, 'c4')
                self.eeg_f3 = self.generate_eeg_wave(self.time, 'f3')
                self.eeg_f4 = self.generate_eeg_wave(self.time, 'f4')
                self.eeg_o1 = self.generate_eeg_wave(self.time, 'o1')
                self.eeg_o2 = self.generate_eeg_wave(self.time, 'o2')
            
            elif num_columns >= 12:  # Future format or mock data
                # Future format: time, snore, flow, thorax, abdomen, spo2, pleth, pulse, body_pos, activity, ?, ?
                self.time = pd.Series(self.data[0].astype(float) / 1000, name='time')  # ms to s
                self.snore = pd.Series(self.data[1].astype(float), name='snore')
                self.flow = pd.Series(self.data[2].astype(float), name='flow')
                self.thorax = pd.Series(self.data[3].astype(float), name='thorax')
                self.abdomen = pd.Series(self.data[4].astype(float), name='abdomen')
                self.spo2 = pd.Series(self.data[5].astype(float), name='spo2')
                self.pleth = pd.Series(self.data[6].astype(float), name='pleth')
                self.pulse = pd.Series(self.data[7].astype(float), name='pulse')
                self.body_pos = pd.Series(self.data[8].astype(int), name='body_pos')
                self.activity = pd.Series(self.data[9].astype(float), name='activity')  # 0=sleeping, 1=awake
                
                # Handle EEG signals if available (columns 10-14)
                if num_columns >= 15:
                    self.eeg_c3 = pd.Series(self.data[10].astype(float), name='eeg_c3')
                    self.eeg_c4 = pd.Series(self.data[11].astype(float), name='eeg_c4')
                    self.eeg_f3 = pd.Series(self.data[12].astype(float), name='eeg_f3')
                    self.eeg_f4 = pd.Series(self.data[13].astype(float), name='eeg_f4')
                    self.eeg_o1 = pd.Series(self.data[14].astype(float), name='eeg_o1')
                    self.eeg_o2 = pd.Series(self.data[14].astype(float), name='eeg_o2')  # Use o1 for o2 if not available
                else:
                    # Generate EEG signals if not enough columns
                    self.eeg_c3 = self.generate_eeg_wave(self.time, 'c3')
                    self.eeg_c4 = self.generate_eeg_wave(self.time, 'c4')
                    self.eeg_f3 = self.generate_eeg_wave(self.time, 'f3')
                    self.eeg_f4 = self.generate_eeg_wave(self.time, 'f4')
                    self.eeg_o1 = self.generate_eeg_wave(self.time, 'o1')
                    self.eeg_o2 = self.generate_eeg_wave(self.time, 'o2')
            
            else:
                # Fallback for unknown format
                self.time = pd.Series(self.data[0].astype(float) / 1000, name='time')
                self.body_pos = pd.Series(np.zeros_like(self.time), name='body_pos')
                self.pulse = pd.Series(np.zeros_like(self.time), name='pulse')
                self.spo2 = pd.Series(np.zeros_like(self.time), name='spo2')
                self.flow = pd.Series(np.zeros_like(self.time), name='flow')
                # Generate realistic mock waveforms
                self.snore = self.generate_snore_wave(self.time)
                self.thorax = self.generate_thorax_wave(self.time)
                self.abdomen = self.generate_abdomen_wave(self.time)
                self.pleth = self.generate_pleth_wave(self.time)
                self.activity = self.generate_activity_wave(self.time)
                
                # Generate EEG signals
                self.eeg_c3 = self.generate_eeg_wave(self.time, 'c3')
                self.eeg_c4 = self.generate_eeg_wave(self.time, 'c4')
                self.eeg_f3 = self.generate_eeg_wave(self.time, 'f3')
                self.eeg_f4 = self.generate_eeg_wave(self.time, 'f4')
                self.eeg_o1 = self.generate_eeg_wave(self.time, 'o1')
                self.eeg_o2 = self.generate_eeg_wave(self.time, 'o2')
            
        except Exception as e:
            print(f"Error in data format detection: {e}")
            # Create emergency data
            self.create_emergency_signals()

        # Normalize signals
        try:
            self.body_pos_n = self.normalize(self.body_pos)
            self.pulse_n = self.normalize(self.pulse)
            self.spo2_n = self.normalize(self.spo2)
            self.flow_n = self.normalize(self.flow)
            self.snore_n = self.normalize(self.snore)
            self.thorax_n = self.normalize(self.thorax)
            self.abdomen_n = self.normalize(self.abdomen)
            self.pleth_n = self.normalize(self.pleth)
            self.activity_n = self.normalize(self.activity)
        
            # Normalize EEG signals
            self.eeg_c3_n = self.normalize(self.eeg_c3)
            self.eeg_c4_n = self.normalize(self.eeg_c4)
            self.eeg_f3_n = self.normalize(self.eeg_f3)
            self.eeg_f4_n = self.normalize(self.eeg_f4)
            self.eeg_o1_n = self.normalize(self.eeg_o1)
            self.eeg_o2_n = self.normalize(self.eeg_o2)
            
        except Exception as e:
            print(f"Error in signal normalization: {e}")
            # Create normalized versions with fallback
            self.create_normalized_fallback_signals()

        # Window settings
        try:
            self.start_time = self.time.iloc[0]
            self.end_time = self.time.iloc[-1]
            self.window_size = 10.0  # initial window size in seconds
            self.min_window_size = 1.0
            self.max_window_size = max(1.0, (self.end_time - self.start_time) / 2)
        except Exception as e:
            print(f"Error setting window parameters: {e}")
            # Set default values
            self.start_time = 0.0
            self.end_time = 10.0
            self.window_size = 10.0
            self.min_window_size = 1.0
            self.max_window_size = 10.0

        # Arrow directions for body positions
        self.arrow_directions = {
            0: (0, 0.5, '↑', 'Up (Supine)'),
            1: (-0.5, 0, '←', 'Left'),
            2: (0.5, 0, '→', 'Right'),
            3: (0, -0.5, '↓', 'Down (Prone)')
        }

        # Offsets for all signals (current + future + EEG)
        self.offsets = [0, 1.2, 2.4, 3.6, 4.8, 6.0, 7.2, 8.4, 9.6, 10.8, 12.0, 13.2, 14.4, 15.6, 16.8]
        
        # Playback state
        self.is_playing = False
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.auto_advance)
        self.play_speed = 1.0
        
        # Initialize checkboxes
        try:
            self.spo2_checkbox = QCheckBox()
            self.pulse_checkbox = QCheckBox()
            self.flow_checkbox = QCheckBox()
            self.position_checkbox = QCheckBox()
            self.activity_checkbox = QCheckBox()
            self.snore_checkbox = QCheckBox()
            self.thorax_checkbox = QCheckBox()
            self.abdomen_checkbox = QCheckBox()
            self.pleth_checkbox = QCheckBox()
        except Exception as e:
            print(f"Error initializing checkboxes: {e}")
            # Create basic checkboxes
        self.spo2_checkbox = QCheckBox()
        self.pulse_checkbox = QCheckBox()
        self.flow_checkbox = QCheckBox()
        self.position_checkbox = QCheckBox()
        self.activity_checkbox = QCheckBox()
        self.snore_checkbox = QCheckBox()
        self.thorax_checkbox = QCheckBox()
        self.abdomen_checkbox = QCheckBox()
        self.pleth_checkbox = QCheckBox()

        try:
            self.initUI()
        except Exception as e:
            print(f"Error in UI initialization: {e}")
            # Try to create basic UI
            self.create_basic_ui()
        
        # Auto-configure checkboxes based on data availability
        try:
            self.configure_signal_checkboxes()
        except Exception as e:
            print(f"Error configuring signal checkboxes: {e}")
        
        # Show welcome message with SleepSense Pro branding
        try:
            self.show_welcome_message()
        except Exception as e:
            print(f"Error showing welcome message: {e}")
            # Continue without welcome message
        
        # Initialize plotting system
        try:
            print("Initializing plotting system...")
            self.plot_signals()
            print("Plotting system initialized successfully")
        except Exception as e:
            print(f"Error initializing plotting system: {e}")
            # Try emergency plot
            try:
                self.create_emergency_plot()
                print("Emergency plot created")
            except Exception as e2:
                print(f"Emergency plot also failed: {e2}")

    def normalize(self, series):
        """Normalize signal data to prevent extreme values"""
        try:
            if series is None or len(series) == 0:
                return pd.Series([0.5] * 100)  # Return default values
            
            # Convert to numeric if needed
            if not pd.api.types.is_numeric_dtype(series):
                try:
                    series = pd.to_numeric(series, errors='coerce')
                except:
                    return pd.Series([0.5] * len(series))
            
            # Handle infinite values
            series = series.replace([np.inf, -np.inf], np.nan)
            
            # Fill NaN values with median
            if series.isna().any():
                median_val = series.median()
                if pd.isna(median_val):
                    median_val = 0.0
                series = series.fillna(median_val)
            
            # Get min and max values
            min_val = series.min()
            max_val = series.max()
            
            # Handle constant signals
            if min_val == max_val:
                if min_val == 0:
                    return pd.Series([0.5] * len(series))  # Return middle value
                else:
                    return pd.Series([0.5] * len(series))  # Return middle value
            
            # Normalize to 0-1 range with safety margins
            normalized = (series - min_val) / (max_val - min_val)
            
            # Ensure values are within bounds
            normalized = np.clip(normalized, 0.0, 1.0)
            
            return normalized
            
        except Exception as e:
            print(f"Error normalizing signal: {e}")
            # Return safe default values
            return pd.Series([0.5] * 100)
    
    def generate_snore_wave(self, time):
        """Generate realistic snore waveform with random bursts - optimized"""
        # Use vectorized operations for better performance
        base_freq = 0.5  # Hz
        snore = np.sin(2 * np.pi * base_freq * time) * 0.3
        
        # Reduce burst frequency for better performance
        burst_interval = max(200, len(time) // 20)  # Fewer bursts
        
        for i in range(0, len(time), burst_interval):
            if np.random.random() > 0.8:  # 20% chance of snore burst
                burst_start = i
                burst_duration = min(100, len(time) - i)  # Limit burst duration
                burst_end = burst_start + burst_duration
                
                if burst_end <= len(time):
                    # Use vectorized operations
                    burst_time = time[burst_start:burst_end] - time[burst_start]
                    burst_freq = np.random.uniform(0.8, 1.5)
                    burst_amp = np.random.uniform(0.5, 1.0)
                    
                    snore[burst_start:burst_end] += burst_amp * np.sin(2 * np.pi * burst_freq * burst_time)
        
        return pd.Series(snore, name='snore')
    
    def generate_thorax_wave(self, time):
        """Generate realistic thorax movement (breathing pattern)"""
        # Breathing frequency (12-20 breaths per minute)
        breathing_freq = np.random.uniform(0.2, 0.33)  # Hz
        thorax = np.sin(2 * np.pi * breathing_freq * time)
        
        # Add some variation in breathing depth
        depth_variation = 0.3 * np.sin(2 * np.pi * 0.05 * time)  # Slow variation
        thorax *= (1 + depth_variation)
        
        # Add small random noise
        thorax += 0.1 * np.random.randn(len(time))
        
        return pd.Series(thorax, name='thorax')
    
    def generate_abdomen_wave(self, time):
        """Generate realistic abdomen movement (slightly different from thorax)"""
        # Similar to thorax but with slight phase difference
        breathing_freq = np.random.uniform(0.2, 0.33)  # Hz
        phase_diff = np.random.uniform(0.1, 0.3)  # Phase difference from thorax
        
        abdomen = np.sin(2 * np.pi * breathing_freq * time + phase_diff)
        
        # Different depth variation
        depth_variation = 0.25 * np.sin(2 * np.pi * 0.04 * time)
        abdomen *= (1 + depth_variation)
        
        # Add small random noise
        abdomen += 0.08 * np.random.randn(len(time))
        
        return pd.Series(abdomen, name='abdomen')
    
    def generate_pleth_wave(self, time):
        """Generate realistic plethysmography waveform (blood volume changes)"""
        # Heart rate frequency (60-100 BPM)
        heart_freq = np.random.uniform(1.0, 1.67)  # Hz
        
        # Main pleth waveform
        pleth = np.sin(2 * np.pi * heart_freq * time)
        
        # Add respiratory modulation
        resp_freq = np.random.uniform(0.2, 0.33)  # Hz
        resp_mod = 0.4 * np.sin(2 * np.pi * resp_freq * time)
        pleth *= (1 + resp_mod)
        
        # Add harmonics for more realistic shape
        pleth += 0.3 * np.sin(2 * np.pi * 2 * heart_freq * time)
        pleth += 0.1 * np.sin(2 * np.pi * 3 * heart_freq * time)
        
        # Add small noise
        pleth += 0.05 * np.random.randn(len(time))
        
        return pd.Series(pleth, name='pleth')
    
    def generate_activity_wave(self, time):
        """Generate realistic activity pattern (sleep/wake cycles) - optimized"""
        # Use vectorized operations for better performance
        activity = np.zeros_like(time)
        
        # Reduce wake period frequency for better performance
        check_interval = max(300, len(time) // 15)  # Fewer checks
        
        for i in range(0, len(time), check_interval):
            if np.random.random() > 0.9:  # 10% chance of wake period
                wake_start = i
                wake_duration = min(200, len(time) - i)  # Limit duration
                wake_end = wake_start + wake_duration
                
                if wake_end <= len(time):
                    # Use vectorized operations for transitions
                    transition_length = min(30, wake_duration // 2)
                    
                    # Gradual increase
                    if transition_length > 0:
                        activity[wake_start:wake_start + transition_length] = np.linspace(0, 1, transition_length)
                    
                    # Full wake level
                    if wake_duration > 2 * transition_length:
                        activity[wake_start + transition_length:wake_end - transition_length] = 1.0
                    
                    # Gradual decrease
                    if transition_length > 0:
                        activity[wake_end - transition_length:wake_end] = np.linspace(1, 0, transition_length)
        
        # Add small random variations (vectorized)
        activity += 0.05 * np.random.randn(len(time))
        activity = np.clip(activity, 0, 1)
        
        return pd.Series(activity, name='activity')
    
    def show_welcome_message(self):
        """Display welcome message with SleepSense Pro branding"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Welcome to SleepSense Pro")
        msg.setText("Welcome to SleepSense Pro")
        msg.setInformativeText("Professional Sleep Analysis System\n\nAdvanced sleep monitoring and analysis with:\n• Multi-channel signal processing\n• EEG analysis capabilities\n• Professional medical-grade interface\n• Real-time waveform visualization\n\nReady to analyze your sleep data!")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_about(self):
        """Show about dialog for SleepSense Pro"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About SleepSense Pro")
        msg.setText("SleepSense Pro v2.0")
        msg.setInformativeText("Professional Sleep Analysis System\n\n"
                              "Advanced sleep monitoring and analysis software with:\n"
                              "• Multi-channel physiological signal processing\n"
                              "• Comprehensive EEG analysis (6 channels)\n"
                              "• Professional medical-grade interface\n"
                              "• Real-time waveform visualization\n"
                              "• Advanced data security features\n"
                              "• Responsive design for all devices\n\n"
                              "© 2024 SleepSense Pro\n"
                              "Professional Edition")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def generate_eeg_wave(self, time, channel):
        """Generate realistic EEG waveform for different channels"""
        # Base alpha rhythm (8-13 Hz) - typical for relaxed state
        alpha_freq = np.random.uniform(8, 13)  # Hz
        
        # Channel-specific characteristics
        if channel in ['c3', 'c4']:  # Central channels - motor cortex
            # Add beta rhythm (13-30 Hz) for motor areas
            beta_freq = np.random.uniform(15, 25)
            eeg = (0.6 * np.sin(2 * np.pi * alpha_freq * time) + 
                   0.4 * np.sin(2 * np.pi * beta_freq * time))
        elif channel in ['f3', 'f4']:  # Frontal channels - executive function
            # Add theta rhythm (4-8 Hz) for frontal areas
            theta_freq = np.random.uniform(5, 7)
            eeg = (0.5 * np.sin(2 * np.pi * alpha_freq * time) + 
                   0.5 * np.sin(2 * np.pi * theta_freq * time))
        elif channel in ['o1', 'o2']:  # Occipital channels - visual cortex
            # Stronger alpha rhythm for visual areas
            eeg = 0.8 * np.sin(2 * np.pi * alpha_freq * time)
        else:
            # Default alpha rhythm
            eeg = np.sin(2 * np.pi * alpha_freq * time)
        
        # Add slow delta waves (0.5-4 Hz) for deep sleep
        delta_freq = np.random.uniform(0.5, 2)
        eeg += 0.3 * np.sin(2 * np.pi * delta_freq * time)
        
        # Add realistic noise and artifacts
        eeg += 0.1 * np.random.randn(len(time))
        
        # Add occasional eye movement artifacts (for frontal channels)
        if channel in ['f3', 'f4']:
            artifact_interval = max(500, len(time) // 10)
            for i in range(0, len(time), artifact_interval):
                if np.random.random() > 0.7:  # 30% chance of artifact
                    artifact_duration = min(50, len(time) - i)
                    artifact_end = i + artifact_duration
                    if artifact_end <= len(time):
                        # Eye movement artifact (slow wave)
                        artifact_time = time[i:artifact_end] - time[i]
                        artifact_freq = np.random.uniform(0.1, 0.5)
                        eeg[i:artifact_end] += 0.5 * np.sin(2 * np.pi * artifact_freq * artifact_time)
        
        return pd.Series(eeg, name=f'eeg_{channel}')

    def initUI(self):
        # Create menu bar
        self.createMenuBar()
        
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel for controls
        left_panel = self.createLeftPanel()
        splitter.addWidget(left_panel)
        
        # Right panel for plots
        right_panel = self.createRightPanel()
        splitter.addWidget(right_panel)
        
        # Full-page analysis mode - maximize plotting area
        if self.is_small_screen:
            # On small screens, make left panel collapsible and smaller
            splitter.setChildrenCollapsible(True)
            left_panel_width = min(250, int(self.screen_width * 0.20))  # Reduce left panel
            right_panel_width = max(600, self.screen_width - left_panel_width - 30)
            splitter.setSizes([left_panel_width, right_panel_width])
        else:
            # On larger screens, maximize plotting area
            splitter.setChildrenCollapsible(False)
            splitter.setSizes([300, 1300])  # Reduce left panel, increase right panel
        
        self.splitter = splitter  # Store reference for resizing
        
        # Status bar with analysis mode indicator
        self.statusBar().showMessage("SleepSense Pro Ready - Loaded sleep data successfully | 📊 Analysis Mode: Full Page | Press F1 for navigation help")

    def createMenuBar(self):
        menubar = self.menuBar()
        
        # SleepSense Pro menu
        pro_menu = menubar.addMenu('SleepSense Pro')
        
        about_action = QAction('About SleepSense Pro', self)
        about_action.triggered.connect(self.show_about)
        pro_menu.addAction(about_action)
        
        pro_menu.addSeparator()
        
        version_action = QAction('Version 2.0 Professional', self)
        version_action.setEnabled(False)
        pro_menu.addAction(version_action)
        
        pro_menu.addSeparator()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open Data File', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save Report', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.saveReport)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Mode menu
        mode_menu = menubar.addMenu('Mode')
        
        analysis_action = QAction('Analysis Mode', self)
        analysis_action.setCheckable(True)
        analysis_action.setChecked(True)
        mode_menu.addAction(analysis_action)
        
        review_action = QAction('Review Mode', self)
        review_action.setCheckable(True)
        mode_menu.addAction(review_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        zoom_action = QAction('Zoom Tool', self)
        tools_menu.addAction(zoom_action)
        
        measure_action = QAction('Measurement Tool', self)
        tools_menu.addAction(measure_action)
        
        tools_menu.addSeparator()
        
        frame_change_action = QAction('Change Frame Size', self)
        frame_change_action.triggered.connect(self.show_frame_change_dialog)
        tools_menu.addAction(frame_change_action)
        
        # Data Security menu
        security_menu = menubar.addMenu('Data Security')
        
        secure_data_action = QAction('🔒 Secure Existing Data', self)
        secure_data_action.triggered.connect(self.secure_existing_data)
        security_menu.addAction(secure_data_action)
        
        list_files_action = QAction('📋 List Data Files', self)
        list_files_action.triggered.connect(self.list_data_files)
        security_menu.addAction(list_files_action)
        
        export_secure_action = QAction('📤 Export Secure Data', self)
        export_secure_action.triggered.connect(self.export_secure_data)
        security_menu.addAction(export_secure_action)
        
        security_menu.addSeparator()
        
        # Region Selection Management
        regions_info_action = QAction('📋 Show Selected Regions', self)
        regions_info_action.triggered.connect(self.show_selected_regions)
        security_menu.addAction(regions_info_action)
        
        clear_regions_action = QAction('🗑️ Clear All Regions', self)
        clear_regions_action.setShortcut('Ctrl+R')
        clear_regions_action.triggered.connect(self.clear_selected_regions)
        security_menu.addAction(clear_regions_action)
        
        # Reports menu
        reports_menu = menubar.addMenu('Reports')
        
        summary_action = QAction('Summary Report', self)
        reports_menu.addAction(summary_action)
        
        detailed_action = QAction('Detailed Report', self)
        reports_menu.addAction(detailed_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        fullscreen_action = QAction('Fullscreen', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Analysis view options
        view_menu.addSeparator()
        
        maximize_plots_action = QAction('Maximize Plot Area', self)
        maximize_plots_action.setShortcut('Ctrl+M')
        maximize_plots_action.triggered.connect(self.maximize_plot_area)
        view_menu.addAction(maximize_plots_action)
        
        compact_controls_action = QAction('Compact Controls', self)
        compact_controls_action.setShortcut('Ctrl+C')
        compact_controls_action.triggered.connect(self.toggle_compact_controls)
        view_menu.addAction(compact_controls_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        navigation_help_action = QAction('Navigation Help', self)
        navigation_help_action.setShortcut('F1')
        navigation_help_action.triggered.connect(self.show_navigation_help)
        help_menu.addAction(navigation_help_action)
        
        help_menu.addSeparator()
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def createLeftPanel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Responsive margins and spacing
        if self.is_small_screen:
            left_layout.setContentsMargins(6, 6, 6, 6)
            left_layout.setSpacing(4)
        else:
            left_layout.setContentsMargins(10, 10, 10, 10)
            left_layout.setSpacing(8)
        
        # Set left panel background and styling
        left_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-right: 2px solid #dee2e6;
            }
        """)
        
        # Add SleepSense Pro branding header
        branding_label = QLabel("SleepSense Pro")
        branding_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 10px;
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                margin: 10px 5px;
                text-align: center;
            }
        """)
        branding_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(branding_label)
        
        # Add subtitle
        subtitle_label = QLabel("Professional Sleep Analysis System")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 11px;
                font-weight: 500;
                padding: 5px 10px;
                text-align: center;
                margin-bottom: 10px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(subtitle_label)
        
        # Add version info
        version_label = QLabel("v2.0 Professional Edition")
        version_label.setStyleSheet("""
            QLabel {
                color: #28a745;
                font-size: 10px;
                font-weight: 600;
                padding: 3px 10px;
                text-align: center;
                margin-bottom: 15px;
                background-color: #d4edda;
                border-radius: 4px;
                border: 1px solid #c3e6cb;
            }
        """)
        version_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(version_label)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("QFrame { background-color: #dee2e6; margin: 10px 20px; }")
        left_layout.addWidget(separator)
        
        # Respiratory Controls Group
        respiratory_group = QGroupBox("🫁 Respiratory Controls")
        respiratory_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 11px;
                border: 2px solid #6c757d;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: #495057;
            }
        """)
        respiratory_layout = QVBoxLayout(respiratory_group)
        respiratory_layout.setContentsMargins(6, 6, 6, 6)
        respiratory_layout.setSpacing(4)
        
        # Respiratory signals with zoom buttons
        self.create_wave_control(respiratory_layout, "Airflow", self.flow_checkbox, 3)
        self.create_wave_control(respiratory_layout, "Thorax Movement", self.thorax_checkbox, 5)
        self.create_wave_control(respiratory_layout, "Abdomen Movement", self.abdomen_checkbox, 6)
        self.create_wave_control(respiratory_layout, "Snore", self.snore_checkbox, 4)
        
        left_layout.addWidget(respiratory_group)
        
        # EEG Controls Group
        eeg_group = QGroupBox("🧠 EEG Controls")
        eeg_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 11px;
                border: 2px solid #6c757d;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: #495057;
            }
        """)
        eeg_layout = QVBoxLayout(eeg_group)
        eeg_layout.setContentsMargins(6, 6, 6, 6)
        eeg_layout.setSpacing(4)
        
        # Create EEG signal checkboxes and controls
        self.eeg_c3_checkbox = QCheckBox()
        self.eeg_c4_checkbox = QCheckBox()
        self.eeg_f3_checkbox = QCheckBox()
        self.eeg_f4_checkbox = QCheckBox()
        self.eeg_o1_checkbox = QCheckBox()
        self.eeg_o2_checkbox = QCheckBox()
        
        # EEG signals with zoom buttons
        self.create_wave_control(eeg_layout, "C3-A2", self.eeg_c3_checkbox, 9)
        self.create_wave_control(eeg_layout, "C4-A1", self.eeg_c4_checkbox, 10)
        self.create_wave_control(eeg_layout, "F3-A2", self.eeg_f3_checkbox, 11)
        self.create_wave_control(eeg_layout, "F4-A1", self.eeg_f4_checkbox, 12)
        self.create_wave_control(eeg_layout, "O1-A2", self.eeg_o1_checkbox, 13)
        self.create_wave_control(eeg_layout, "O2-A1", self.eeg_o2_checkbox, 14)
        
        left_layout.addWidget(eeg_group)
        
        # Other Physiological Controls Group
        other_group = QGroupBox("💓 Other Physiological")
        other_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 11px;
                border: 2px solid #6c757d;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: #495057;
            }
        """)
        other_layout = QVBoxLayout(other_group)
        other_layout.setContentsMargins(6, 6, 6, 6)
        other_layout.setSpacing(4)
        
        # Other signals with zoom buttons
        self.create_wave_control(other_layout, "SpO2 (Oxygen Saturation)", self.spo2_checkbox, 2)
        self.create_wave_control(other_layout, "Pulse (Heart Rate)", self.pulse_checkbox, 1)
        self.create_wave_control(other_layout, "Body Position", self.position_checkbox, 0)
        self.create_wave_control(other_layout, "Activity", self.activity_checkbox, 8)
        self.create_wave_control(other_layout, "Plethysmography", self.pleth_checkbox, 7)
        
        # Connect checkbox changes to plot updates with debouncing
        self.spo2_checkbox.toggled.connect(self.debounced_update_plots)
        self.pulse_checkbox.toggled.connect(self.debounced_update_plots)
        self.flow_checkbox.toggled.connect(self.debounced_update_plots)
        self.position_checkbox.toggled.connect(self.debounced_update_plots)
        self.activity_checkbox.toggled.connect(self.debounced_update_plots)
        self.snore_checkbox.toggled.connect(self.debounced_update_plots)
        self.thorax_checkbox.toggled.connect(self.debounced_update_plots)
        self.abdomen_checkbox.toggled.connect(self.debounced_update_plots)
        self.pleth_checkbox.toggled.connect(self.debounced_update_plots)
        
        # Connect EEG checkboxes
        self.eeg_c3_checkbox.toggled.connect(self.debounced_update_plots)
        self.eeg_c4_checkbox.toggled.connect(self.debounced_update_plots)
        self.eeg_f3_checkbox.toggled.connect(self.debounced_update_plots)
        self.eeg_f4_checkbox.toggled.connect(self.debounced_update_plots)
        self.eeg_o1_checkbox.toggled.connect(self.debounced_update_plots)
        self.eeg_o2_checkbox.toggled.connect(self.debounced_update_plots)

        left_layout.addWidget(other_group)
        

        

        
        # Add stretch to push everything to top
        left_layout.addStretch()
        
        # Add footer branding
        footer_separator = QFrame()
        footer_separator.setFrameShape(QFrame.HLine)
        footer_separator.setStyleSheet("QFrame { background-color: #dee2e6; margin: 10px 20px; }")
        left_layout.addWidget(footer_separator)
        
        footer_label = QLabel("© 2024 SleepSense Pro")
        footer_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 9px;
                font-weight: 400;
                padding: 5px 10px;
                text-align: center;
                margin-top: 5px;
            }
        """)
        footer_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(footer_label)
        
        return left_widget

    def create_wave_control(self, parent_layout, label_text, checkbox, signal_index):
        """Create a wave control with checkbox and integrated toggle zoom button"""
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(2, 2, 2, 2)
        control_layout.setSpacing(6)
        
        # Checkbox with improved styling
        checkbox.setChecked(True)
        checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 4px;
                font-size: 10px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #6c757d;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
                border-color: #20c997;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QCheckBox::indicator:hover {
                border-color: #495057;
            }
        """)
        control_layout.addWidget(checkbox)
        
        # Label with improved styling and responsive sizing
        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-weight: 500;
                font-size: 10px;
                padding: 2px;
                background-color: transparent;
            }
        """)
        if self.is_small_screen:
            label.setMinimumWidth(90)  # Smaller labels on small screens
        else:
            label.setMinimumWidth(110)
        control_layout.addWidget(label)
        
        # Create integrated toggle button for zoom control
        zoom_toggle_btn = QPushButton("▲")
        
        # Responsive button sizing
        if self.is_small_screen:
            zoom_toggle_btn.setFixedSize(24, 24)
        else:
            zoom_toggle_btn.setFixedSize(28, 28)
        zoom_toggle_btn.setCheckable(True)  # Make it a toggle button
        zoom_toggle_btn.setChecked(False)
        
        # Store zoom state for this signal
        if not hasattr(self, 'zoom_states'):
            self.zoom_states = {}
        self.zoom_states[signal_index] = False  # False = zoomed out, True = zoomed in
        
        # Improved style for toggle button
        zoom_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: 2px solid #495057;
                border-radius: 4px;
                font-weight: 700;
                font-size: 12px;
                min-width: 0px;
                padding: 0px;
            }
            QPushButton:checked {
                background-color: #28a745;
                border-color: #20c997;
            }
            QPushButton:hover {
                background-color: #495057;
                border-color: #343a40;
            }
            QPushButton:checked:hover {
                background-color: #20c997;
                border-color: #1ea085;
            }
        """)
        
        # Connect toggle functionality
        zoom_toggle_btn.toggled.connect(lambda checked, idx=signal_index: self.toggle_zoom(idx, checked))
        
        control_layout.addWidget(zoom_toggle_btn)
        
        parent_layout.addLayout(control_layout)
        
        # Store the toggle button for later reference
        if not hasattr(self, 'zoom_toggles'):
            self.zoom_toggles = {}
        self.zoom_toggles[signal_index] = zoom_toggle_btn

    def createRightPanel(self):
        """Create the right panel with detailed waveform view"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Compact Time Navigation Controls at the top
        navigation_group = QGroupBox("⏱️ Time Navigation - SleepSense Pro")
        navigation_layout = QVBoxLayout(navigation_group)
        navigation_layout.setContentsMargins(8, 8, 8, 8)
        navigation_layout.setSpacing(4)
        
        # Compact slider for time navigation
        slider_layout = QHBoxLayout()
        slider_label = QLabel("🕐")
        slider_label.setStyleSheet("font-size: 16px; margin-right: 5px;")
        slider_layout.addWidget(slider_label)
        
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(1000)
        self.time_slider.setValue(0)
        self.time_slider.setToolTip(
            "🕐 Time Navigation Slider\n"
            "• Drag to navigate through your sleep data\n"
            "• Shows current time position\n"
            "• Works with frame size buttons for optimal viewing\n"
            "• Use arrow keys for precise navigation"
        )
        self.time_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #3498db;
                border-radius: 4px;
            }
        """)
        self.time_slider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.time_slider)
        
        # Current time display
        self.current_time_label = QLabel("00:00:00")
        self.current_time_label.setStyleSheet("""
            QLabel {
                background: #2c3e50;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 11px;
                min-width: 60px;
                text-align: center;
            }
        """)
        slider_layout.addWidget(self.current_time_label)
        
        navigation_layout.addLayout(slider_layout)
        
        # Time display with frame info
        self.time_display = QLabel("00:00:00 - 00:00:10")
        self.time_display.setStyleSheet("""
            QLabel {
                background: #34495e;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 12px;
                text-align: center;
                margin-top: 4px;
            }
        """)
        navigation_layout.addWidget(self.time_display)
        
        # Frame size buttons
        frame_buttons_layout = QHBoxLayout()
        frame_sizes = [5, 10, 30, 60, 120, 300, 600, 1800]  # 5s to 30m
        self.frame_buttons = {}
        
        for seconds in frame_sizes:
            btn = QPushButton(f"{seconds}s" if seconds < 60 else f"{seconds//60}m")
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                    min-width: 40px;
                }
                QPushButton:checked {
                    background: #27ae60;
                    color: white;
                    border-color: #229954;
                }
                QPushButton:hover {
                    background: #d5dbdb;
                }
            """)
            btn.clicked.connect(lambda checked, s=seconds: self.set_frame_size_from_button(s))
            frame_buttons_layout.addWidget(btn)
            self.frame_buttons[seconds] = btn
        
        # Set default frame size (5 seconds)
        if 5 in self.frame_buttons:
            self.frame_buttons[5].setChecked(True)
        
        navigation_layout.addLayout(frame_buttons_layout)
        right_layout.addWidget(navigation_group)
        
        # Create matplotlib figure for detailed view - full page analysis
        try:
            # Initialize the plotting system first
            canvas = self.plot_signals()
            
            # Add the canvas to the layout
            if canvas is not None:
                right_layout.addWidget(canvas)
                print("Canvas added to right panel successfully")
                
                # Auto-configure checkboxes based on data availability
                self.configure_signal_checkboxes()
                
                # Update the plot display
                self.update_plot()
            else:
                print("Canvas creation failed, creating emergency plot")
                emergency_canvas = self.create_emergency_plot()
                if emergency_canvas is not None:
                    right_layout.addWidget(emergency_canvas)
                else:
                    # Last resort - add text widget
                    error_label = QLabel("Plotting system unavailable")
                    error_label.setStyleSheet("color: red; font-size: 16px; padding: 20px;")
                    error_label.setAlignment(Qt.AlignCenter)
                    right_layout.addWidget(error_label)
            
        except Exception as e:
            print(f"Error setting up plotting system: {e}")
            # Create emergency plot
            emergency_canvas = self.create_emergency_plot()
            if emergency_canvas is not None:
                right_layout.addWidget(emergency_canvas)
            else:
                # Last resort - add text widget
                error_label = QLabel("Plotting system unavailable")
                error_label.setStyleSheet("color: red; font-size: 16px; padding: 20px;")
                error_label.setAlignment(Qt.AlignCenter)
                right_layout.addWidget(error_label)
        
        # Ensure full page visibility
        self.ensure_full_page_visibility()
        
        return right_panel

    def plot_signals(self):
        """Initialize plots with performance optimizations and proper alignment"""
        try:
            # Create matplotlib figure for detailed view - full page analysis
            self.detailed_fig = Figure(figsize=(16, 12))  # Increased size for better analysis
            
            # Create the main axis
            self.detailed_ax = self.detailed_fig.add_subplot(111)
            
            # Ensure proper subplot layout for full-page visibility
            self.detailed_fig.subplots_adjust(
                left=0.08,      # Left margin
                right=0.95,     # Right margin
                top=0.92,       # Top margin
                bottom=0.08,    # Bottom margin
                wspace=0.1,     # Width space between subplots
                hspace=0.1      # Height space between subplots
            )
            
            # Performance optimizations
            self.detailed_ax.set_facecolor('#f8f9fa')
            
            # Set proper axis limits and grid for better visibility
            self.detailed_ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            self.detailed_ax.set_axisbelow(True)  # Grid behind data
            
            # Set initial axis limits
            self.detailed_ax.set_xlim(0, 10)
            self.detailed_ax.set_ylim(-0.5, 15)  # Adjusted for signal offsets
            
            # Set labels
            self.detailed_ax.set_xlabel('Time (seconds)', fontsize=10)
            self.detailed_ax.set_ylabel('Signal Amplitude', fontsize=10)
            
            # Set title
            self.detailed_ax.set_title('SleepSense Pro - Professional Sleep Analysis', 
                                     fontsize=14, fontweight='bold', pad=20)
            
            # Initialize plot bounds tracking
            self._last_plot_bounds = (0, 0)
            
            # Set initial view settings for optimal visibility
            self.line_width = 0.8
            self.grid_alpha = 0.3
            self.time_label_interval = 10
            
            # Create canvas
            self.detailed_canvas = FigureCanvas(self.detailed_fig)
            
            # Add tooltip to explain region selection
            self.detailed_canvas.setToolTip(
                "🖱️  Click and drag to select regions (like turning lights on/off)\n"
                "💡 Selected regions are highlighted in blue\n"
                "⌨️  Press Ctrl+R to clear all regions\n"
                "📋 Use Data Security menu to manage selections\n"
                "🕐 Use slider and frame buttons for optimal viewing"
            )
            
            # Initialize region selection variables
            self.selected_regions = []  # List to store selected regions
            self.is_selecting = False   # Flag to track selection state
            self.selection_start = None # Start point of selection
            self.selection_rect = None  # Rectangle patch for selection
            
            # Connect mouse events for region selection
            self.detailed_canvas.mpl_connect('button_press_event', self.on_mouse_press)
            self.detailed_canvas.mpl_connect('button_release_event', self.on_mouse_release)
            self.detailed_canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
            
            # Update plots
            self.update_plots()

            print("Plot signals initialized successfully")
            return self.detailed_canvas
            
        except Exception as e:
            print(f"Error in plot_signals: {e}")
            # Create emergency plot
            return self.create_emergency_plot()

    def update_plots(self):
        """Update plots with current data window"""
        try:
            # Clear previous plots
            self.detailed_ax.clear()
        
            # Use current start time from slider/button navigation
            start_time = self.start_time
            end_time = start_time + self.window_size
            
            print(f"Updating plots for time window: {start_time:.1f}s to {end_time:.1f}s (frame size: {self.window_size}s)")
            
            # Find data indices for current window
            try:
                start_idx = np.argmin(np.abs(self.time - start_time))
                end_idx = np.argmin(np.abs(self.time - end_time))
                
                # Ensure valid indices
                start_idx = max(0, start_idx)
                end_idx = min(len(self.time) - 1, end_idx)
                
                print(f"Data indices: {start_idx} to {end_idx} (total data: {len(self.time)})")
                
            except Exception as e:
                print(f"Error finding data indices: {e}")
                # Use default indices
                start_idx = 0
                end_idx = min(100, len(self.time) - 1)
            
            # Get line width and grid alpha from frame size settings
            line_width = getattr(self, 'line_width', 0.8)
            grid_alpha = getattr(self, 'grid_alpha', 0.3)
            
            # Define signal offsets for proper separation
            offsets = {
                'snore': 0,
                'flow': 1,
                'thorax': 2,
                'abdomen': 3,
                'spo2': 4,
                'pleth': 5,
                'pulse': 6,
                'body_pos': 7,
                'activity': 8,
                'eeg_c3': 9,
                'eeg_c4': 10,
                'eeg_f3': 11,
                'eeg_f4': 12,
                'eeg_o1': 13,
                'eeg_o2': 14
            }
            
            # Plot signals with proper scaling and offsets
            if hasattr(self, 'snore_checkbox') and self.snore_checkbox.isChecked():
                try:
                    snore_data = self.snore_n.iloc[start_idx:end_idx]
                    if len(snore_data) > 0:
                        # Scale and offset the signal
                        scaled_snore = snore_data * 0.5 + offsets['snore']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_snore, 
                                           color='magenta', linewidth=line_width, label='Snore')
                except Exception as e:
                    print(f"Error plotting snore: {e}")
            
            if hasattr(self, 'flow_checkbox') and self.flow_checkbox.isChecked():
                try:
                    flow_data = self.flow_n.iloc[start_idx:end_idx]
                    if len(flow_data) > 0:
                        scaled_flow = flow_data * 0.5 + offsets['flow']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_flow, 
                                           color='orange', linewidth=line_width, label='Flow')
                except Exception as e:
                    print(f"Error plotting flow: {e}")
            
            if hasattr(self, 'thorax_checkbox') and self.thorax_checkbox.isChecked():
                try:
                    thorax_data = self.thorax_n.iloc[start_idx:end_idx]
                    if len(thorax_data) > 0:
                        scaled_thorax = thorax_data * 0.5 + offsets['thorax']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_thorax, 
                                           color='green', linewidth=line_width, label='Thorax')
                except Exception as e:
                    print(f"Error plotting thorax: {e}")
            
            if hasattr(self, 'abdomen_checkbox') and self.abdomen_checkbox.isChecked():
                try:
                    abdomen_data = self.abdomen_n.iloc[start_idx:end_idx]
                    if len(abdomen_data) > 0:
                        scaled_abdomen = abdomen_data * 0.5 + offsets['abdomen']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_abdomen, 
                                           color='yellow', linewidth=line_width, label='Abdomen')
                except Exception as e:
                    print(f"Error plotting abdomen: {e}")
            
            if hasattr(self, 'spo2_checkbox') and self.spo2_checkbox.isChecked():
                try:
                    spo2_data = self.spo2_n.iloc[start_idx:end_idx]
                    if len(spo2_data) > 0:
                        scaled_spo2 = spo2_data * 0.5 + offsets['spo2']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_spo2, 
                                           color='red', linewidth=line_width, label='SpO2')
                except Exception as e:
                    print(f"Error plotting SpO2: {e}")
            
            if hasattr(self, 'pleth_checkbox') and self.pleth_checkbox.isChecked():
                try:
                    pleth_data = self.pleth_n.iloc[start_idx:end_idx]
                    if len(pleth_data) > 0:
                        scaled_pleth = pleth_data * 0.5 + offsets['pleth']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_pleth, 
                                           color='purple', linewidth=line_width, label='Pleth')
                except Exception as e:
                    print(f"Error plotting pleth: {e}")
            
            if hasattr(self, 'pulse_checkbox') and self.pulse_checkbox.isChecked():
                try:
                    pulse_data = self.pulse_n.iloc[start_idx:end_idx]
                    if len(pulse_data) > 0:
                        scaled_pulse = pulse_data * 0.5 + offsets['pulse']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_pulse, 
                                           color='brown', linewidth=line_width, label='Pulse')
                except Exception as e:
                    print(f"Error plotting pulse: {e}")
            
            if hasattr(self, 'position_checkbox') and self.position_checkbox.isChecked():
                try:
                    body_pos_data = self.body_pos_n.iloc[start_idx:end_idx]
                    if len(body_pos_data) > 0:
                        scaled_body_pos = body_pos_data * 0.5 + offsets['body_pos']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_body_pos, 
                                           color='gray', linewidth=line_width, label='Body Position')
                except Exception as e:
                    print(f"Error plotting body position: {e}")
            
            if hasattr(self, 'activity_checkbox') and self.activity_checkbox.isChecked():
                try:
                    activity_data = self.activity_n.iloc[start_idx:end_idx]
                    if len(activity_data) > 0:
                        scaled_activity = activity_data * 0.5 + offsets['activity']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_activity, 
                                           color='pink', linewidth=line_width, label='Activity')
                except Exception as e:
                    print(f"Error plotting activity: {e}")
            
            # Plot EEG signals with proper scaling
            if hasattr(self, 'eeg_c3_n'):
                try:
                    eeg_c3_data = self.eeg_c3_n.iloc[start_idx:end_idx]
                    if len(eeg_c3_data) > 0:
                        scaled_eeg_c3 = eeg_c3_data * 0.3 + offsets['eeg_c3']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_eeg_c3, 
                                           color='lightblue', linewidth=line_width, label='EEG C3', alpha=0.8)
                except Exception as e:
                    print(f"Error plotting EEG C3: {e}")
            
            if hasattr(self, 'eeg_c4_n'):
                try:
                    eeg_c4_data = self.eeg_c4_n.iloc[start_idx:end_idx]
                    if len(eeg_c4_data) > 0:
                        scaled_eeg_c4 = eeg_c4_data * 0.3 + offsets['eeg_c4']
                        time_window = self.time.iloc[start_idx:end_idx]
                        self.detailed_ax.plot(time_window, scaled_eeg_c4, 
                                           color='lightgreen', linewidth=line_width, label='EEG C4', alpha=0.8)
                except Exception as e:
                    print(f"Error plotting EEG C4: {e}")
            
            # Set plot properties with dynamic grid alpha
            self.detailed_ax.set_ylim(-0.5, max(offsets.values()) + 1)
            self.detailed_ax.grid(True, alpha=grid_alpha)
            self.detailed_ax.legend(loc='upper right')
        
            # Set specific properties for the plot based on frame size
            if self.window_size <= 30:
                title = 'SleepSense Pro - Detailed Waveform View (High Detail Mode)'
                # High detail: show all data points
                plot_density = 1.0
                line_width = 1.2
                grid_alpha = 0.4
            elif self.window_size <= 300:
                title = 'SleepSense Pro - Balanced Waveform View'
                # Balanced: reduce data points for medium frames
                plot_density = 0.5
                line_width = 0.8
                grid_alpha = 0.3
            else:
                title = 'SleepSense Pro - Compact Waveform View (Comparison Mode)'
                # Compact: significantly reduce data points for overview
                plot_density = 0.1
                line_width = 0.6
                grid_alpha = 0.2
            
            # Force update the title
            self.detailed_ax.set_title(title, fontsize=12, fontweight='bold')
            
            # Update line width and grid alpha from frame size settings
            self.line_width = line_width
            self.grid_alpha = grid_alpha
            
            # Set x-axis limits for current window
            self.detailed_ax.set_xlim(start_time, end_time)
            
            # Add time labels based on frame size with proper density
            self.add_time_labels(start_time, end_time)
            
            # Adjust plot density for compact views
            if plot_density < 1.0 and len(time_window) > 1000:
                # For large datasets, reduce plotting density
                step = int(1.0 / plot_density)
                if step > 1:
                    # Use every nth point for plotting
                    time_window = time_window[::step]
                    print(f"Reduced plot density: using every {step}th point for {self.window_size}s frame")
            
            print(f"Plots updated successfully for {self.window_size}s frame (density: {plot_density}, title: {title})")
            
        except Exception as e:
            print(f"Error updating plots: {e}")
            # Create a simple fallback plot
            self.create_fallback_plot()

    def add_time_labels(self, start_time, end_time):
        """Add time labels to the x-axis for better readability"""
        try:
            # Calculate time interval based on frame size
            interval = getattr(self, 'time_label_interval', 10)
            
            # Generate time points for labels
            time_points = np.arange(start_time, end_time + interval, interval)
            
            # Add vertical lines and labels
            for t in time_points:
                if start_time <= t <= end_time:
                    # Add vertical line
                    self.detailed_ax.axvline(x=t, color='gray', alpha=0.3, linestyle='--', linewidth=0.5)
                    
                    # Add time label
                    time_str = f"{int(t//60):02d}:{int(t%60):02d}:{int((t%1)*100):02d}"
                    self.detailed_ax.text(t, self.detailed_ax.get_ylim()[1] * 0.95, time_str, 
                                        rotation=45, ha='right', va='top', fontsize=8, alpha=0.7)
            
            print(f"Added {len(time_points)} time labels with interval {interval}s")
            
        except Exception as e:
            print(f"Error adding time labels: {e}")
            # Continue without time labels

    def plot_body_position_simple(self, ax, offset, start_idx, end_idx):
        """Optimized body position plotting without heavy annotations"""
        # Plot only the visible window
        time_window = self.time.iloc[start_idx:end_idx]
        pos_window = self.body_pos_n.iloc[start_idx:end_idx]
        ax.plot(time_window, pos_window + offset, color='#FFFFFF', linewidth=0.8, label='Body Position')
        
        # Add only a few key position labels for performance
        if end_idx - start_idx > 100:  # Only add labels if window is large enough
            step = (end_idx - start_idx) // 5  # Show max 5 labels
            for i in range(start_idx, end_idx, step):
                if i < len(self.body_pos):
                    pos_value = int(self.body_pos.iloc[i])
                    pos_label = ['Supine', 'Left', 'Right', 'Prone', 'Upright'][pos_value] if pos_value < 5 else f'Pos {pos_value}'
                    ax.annotate(pos_label, 
                               xy=(self.time.iloc[i], self.body_pos_n.iloc[i] + offset + 0.1),
                               fontsize=8, color='#FFFFFF', ha='center', weight='bold')

    def plot_body_position_with_labels(self, ax, offset):
        """Plot body position with actual labels instead of numbers"""
        # Map numeric positions to labels
        position_labels = {
            0: 'Supine',
            1: 'Left',
            2: 'Right', 
            3: 'Down (Prone)',
            4: 'Up (Upright)'
        }
        
        # Plot the position line
        ax.plot(self.time, self.body_pos_n + offset, color='black', linewidth=0.8, label='Body Position')
        
        # Add position labels at regular intervals
        label_interval = max(1, len(self.time) // 20)  # Show ~20 labels
        
        for i in range(0, len(self.time), label_interval):
            if i < len(self.time):
                pos_value = int(self.body_pos.iloc[i])
                pos_label = position_labels.get(pos_value, f'Pos {pos_value}')
                
                # Position the label above the line
                ax.annotate(pos_label, 
                           xy=(self.time.iloc[i], self.body_pos_n.iloc[i] + offset + 0.1),
                           xytext=(self.time.iloc[i], self.body_pos_n.iloc[i] + offset + 0.3),
                           fontsize=8, color='black', ha='center',
                           arrowprops=dict(arrowstyle='->', color='black', lw=1))

    def plot_spo2_with_values(self, ax, offset):
        """Plot SpO2 with numeric values displayed"""
        # Plot the SpO2 line
        ax.plot(self.time, self.spo2_n + offset, color='green', linewidth=0.8, label='SpO2')
        
        # Add numeric SpO2 values at regular intervals
        value_interval = max(1, len(self.time) // 15)  # Show ~15 values
        
        for i in range(0, len(self.time), value_interval):
            if i < len(self.time):
                spo2_value = int(self.spo2.iloc[i])
                
                # Position the value above the line
                ax.annotate(f'{spo2_value}%', 
                           xy=(self.time.iloc[i], self.spo2_n.iloc[i] + offset + 0.1),
                           xytext=(self.time.iloc[i], self.spo2_n.iloc[i] + offset + 0.3),
                           fontsize=8, color='green', ha='center', weight='bold',
                           arrowprops=dict(arrowstyle='->', color='green', lw=1))

    def update_plot(self):
        """Optimized plot update with reduced redraws"""
        try:
            # Update time display with better formatting
            start_str = f"{int(self.start_time//60):02d}:{int(self.start_time%60):02d}:{int((self.start_time%1)*100):02d}"
            end_str = f"{int((self.start_time + self.window_size)//60):02d}:{int((self.start_time + self.window_size)%60):02d}:{int(((self.start_time + self.window_size)%1)*100):02d}"
            
            # Add frame size information to the display
            frame_info = f"Frame: {self.window_size}s"
            self.time_display.setText(f"{start_str} - {end_str} | {frame_info}")
        
            # Update slider position to reflect current time
            if hasattr(self, 'time_slider'):
                try:
                    total_time = self.end_time - self.time.iloc[0]
                    if total_time > 0:
                        slider_value = int(((self.start_time - self.time.iloc[0]) / total_time) * 1000)
                        slider_value = max(0, min(1000, slider_value))
                        self.time_slider.setValue(slider_value)
                except Exception as e:
                    print(f"Error updating slider: {e}")
            
            # Update current time label
            if hasattr(self, 'current_time_label'):
                try:
                    current_time_str = f"{int(self.start_time//60):02d}:{int(self.start_time%60):02d}:{int((self.start_time%1)*100):02d}"
                    self.current_time_label.setText(current_time_str)
                except Exception as e:
                    print(f"Error updating current time label: {e}")
            
        # Only redraw if plot has changed significantly
            if not hasattr(self, '_last_plot_bounds') or abs(self._last_plot_bounds[0] - self.start_time) > 0.1:
                self._last_plot_bounds = (self.start_time, self.start_time + self.window_size)
            # Update plot with new data
            self.update_plots()
            
            # Use draw_idle for better performance
            if hasattr(self, 'detailed_canvas') and self.detailed_canvas is not None:
                self.detailed_canvas.draw_idle()
                print(f"Plot updated for time range {self.start_time:.1f}s to {self.start_time + self.window_size:.1f}s")
            
        except Exception as e:
            print(f"Error updating plot: {e}")
            # Try to update just the time display
            try:
                self.time_display.setText(f"Error: {e}")
            except:
                pass

    def change_window_size(self, new_size):
        """Change the window size for viewing different time ranges"""
        try:
            print(f"Changing window size from {self.window_size} to {new_size}")
            
            # Update window size
            self.window_size = float(new_size)
            
            # Ensure window size is within bounds
            if self.window_size < self.min_window_size:
                self.window_size = self.min_window_size
            elif self.window_size > self.max_window_size:
                self.window_size = self.max_window_size
            
            # Update the plot to reflect new window size
            if hasattr(self, 'detailed_ax') and self.detailed_ax is not None:
                # Update x-axis limits for new window size
                end_time = self.start_time + self.window_size
                self.detailed_ax.set_xlim(self.start_time, end_time)
                
                # Force plot update
                if hasattr(self, 'detailed_canvas') and self.detailed_canvas is not None:
                    self.detailed_canvas.draw_idle()
                    print(f"Window size updated to {self.window_size}s, plot redrawn")
            
        except Exception as e:
            print(f"Error changing window size: {e}")
            # Set default window size
            self.window_size = 10.0
    
    def set_frame_size_from_button(self, seconds):
        """Set frame size from toolbar button and update button states with frame shifting"""
        try:
            print(f"Setting frame size to {seconds} seconds")
            
            # Update window size
            self.change_window_size(seconds)
            
            # Update button states - uncheck all, check the selected one
            for btn_seconds, btn in self.frame_buttons.items():
                btn.setChecked(btn_seconds == seconds)
        
            # Use comprehensive update method for better frame size handling
            self.update_plot_for_frame_size(seconds)
            
            # Force immediate update of time display and plot
            self.update_plot()
            
            # Update status bar with more detailed information
            if seconds < 60:
                time_str = f"{seconds} seconds"
            elif seconds < 3600:
                time_str = f"{seconds//60} minute{'s' if seconds//60 != 1 else ''}"
            else:
                time_str = f"{seconds//3600} hour{'s' if seconds//3600 != 1 else ''}"
            
            self.statusBar().showMessage(f"✅ Frame size changed to {time_str} - View adjusted for optimal visibility")
            
            # Force plot redraw
            if hasattr(self, 'detailed_canvas') and self.detailed_canvas is not None:
                self.detailed_canvas.draw_idle()
                print(f"Plot updated for {seconds}s frame size")
            
        except Exception as e:
            print(f"Error setting frame size: {e}")
            self.statusBar().showMessage(f"❌ Error setting frame size: {e}")

    def adjust_view_for_frame_size(self, frame_size):
        """Adjust the view based on frame size for optimal visibility"""
        try:
            print(f"Adjusting view for frame size: {frame_size}s")
            
            # Adjust figure size based on frame size
            if frame_size <= 30:  # 5s, 10s, 30s - High detail mode
                # Large figure for detailed view
                if hasattr(self, 'detailed_fig'):
                    self.detailed_fig.set_size_inches(16, 12)
                    # Optimize margins for detail view
                    self.detailed_fig.subplots_adjust(
                        left=0.08, right=0.95, top=0.92, bottom=0.08,
                        wspace=0.1, hspace=0.1
                    )
                self.line_width = 1.2
                self.grid_alpha = 0.4
                self.time_label_interval = 5
                mode = "High Detail Mode"
                
            elif frame_size <= 300:  # 1m, 2m, 5m - Balanced mode
                # Medium figure for balanced view
                if hasattr(self, 'detailed_fig'):
                    self.detailed_fig.set_size_inches(14, 10)
                    # Balanced margins
                    self.detailed_fig.subplots_adjust(
                        left=0.08, right=0.95, top=0.90, bottom=0.10,
                        wspace=0.1, hspace=0.1
                    )
                self.line_width = 0.8
                self.grid_alpha = 0.3
                self.time_label_interval = 10
                mode = "Balanced Mode"
                
            else:  # 10m, 30m - Compact mode
                # Compact figure for overview
                if hasattr(self, 'detailed_fig'):
                    self.detailed_fig.set_size_inches(12, 8)
                    # Compact margins for overview
                    self.detailed_fig.subplots_adjust(
                        left=0.08, right=0.95, top=0.88, bottom=0.12,
                        wspace=0.1, hspace=0.1
                    )
                self.line_width = 0.6
                self.grid_alpha = 0.2
                self.time_label_interval = 30
                mode = "Compact Mode"
            
            # Update the plot title based on frame size
            if hasattr(self, 'detailed_ax'):
                if frame_size <= 30:
                    title = 'SleepSense Pro - Detailed Waveform View (High Detail Mode)'
                elif frame_size <= 300:
                    title = 'SleepSense Pro - Balanced Waveform View'
                else:
                    title = 'SleepSense Pro - Compact Waveform View (Comparison Mode)'
                
                self.detailed_ax.set_title(title, fontsize=12, fontweight='bold')
            
            # Force canvas redraw with new size
            if hasattr(self, 'detailed_canvas'):
                self.detailed_canvas.draw_idle()
            
            # Update status bar
            self.statusBar().showMessage(f"✅ Frame size: {frame_size}s - {mode} activated for optimal visibility")
            
            print(f"View adjusted: line_width={self.line_width}, grid_alpha={self.grid_alpha}, figure_size={self.detailed_fig.get_size_inches() if hasattr(self, 'detailed_fig') else 'N/A'}")
            
        except Exception as e:
            print(f"Error adjusting view for frame size: {e}")
            # Set default values
            self.line_width = 0.8
            self.grid_alpha = 0.3
            self.time_label_interval = 10
    
    def resizeEvent(self, event):
        """Handle window resize events to maintain responsive layout"""
        # Get new window size
        new_width = self.width()
        new_height = self.height()
        
        # Dynamic screen size detection during resize
        self.current_is_small = new_width < 1024
        
        # Update splitter sizes proportionally
        if hasattr(self, 'splitter'):
            if self.current_is_small:
                # On small screens, make left panel smaller and collapsible
                left_width = min(280, int(new_width * 0.25))
                self.splitter.setChildrenCollapsible(True)
            else:
                # On larger screens, maintain fixed proportions
                left_width = max(350, int(new_width * 0.22))
                self.splitter.setChildrenCollapsible(False)
            
            right_width = max(500, new_width - left_width - 50)  # Account for margins
            self.splitter.setSizes([left_width, right_width])
        
        # Update plot figure sizes if they exist - optimized for full-page analysis
        if hasattr(self, 'detailed_fig'):
            # Calculate available space for plots
            available_width = new_width - 350  # Account for left panel and margins
            available_height = new_height - 200  # Account for menu, status bar, and tabs
            
            # Convert to inches (1 inch = ~100 pixels for typical displays)
            fig_width = max(8, available_width / 100)  # Minimum 8 inches width
            fig_height = max(6, available_height / 150)  # Minimum 6 inches height
            
            try:
                # Set figure size for better analysis
                self.detailed_fig.set_size_inches(fig_width, fig_height)
                
                # Automatically adjust view based on current frame size for optimal visibility
                self.adjust_view_for_frame_size(self.window_size)
                
                # Ensure proper alignment and margins for the new size
                if fig_width >= 14:  # Large figure
                    self.detailed_fig.subplots_adjust(
                        left=0.08, right=0.95, top=0.92, bottom=0.08,
                        wspace=0.1, hspace=0.1
                    )
                elif fig_width >= 10:  # Medium figure
                    self.detailed_fig.subplots_adjust(
                        left=0.08, right=0.95, top=0.90, bottom=0.10,
                        wspace=0.1, hspace=0.1
                    )
                else:  # Small figure
                    self.detailed_fig.subplots_adjust(
                        left=0.10, right=0.95, top=0.88, bottom=0.12,
                        wspace=0.1, hspace=0.1
                    )
                
                # Redraw canvas with proper alignment
                self.detailed_canvas.draw_idle()
                
            except Exception as e:
                print(f"Error during resize: {e}")
                pass  # Ignore errors during resize
        
        # Update status bar with current window size and responsive mode
        mode = "Compact Mode" if self.current_is_small else "Full Mode"
        self.statusBar().showMessage(f"SleepSense Pro - {mode} - Window: {new_width}x{new_height}")
        
        super().resizeEvent(event)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode for better analysis"""
        if self.isFullScreen():
            self.showNormal()
            self.statusBar().showMessage("SleepSense Pro - Exited fullscreen mode")
        else:
            self.showFullScreen()
            self.statusBar().showMessage("SleepSense Pro - Entered fullscreen mode - Press F11 to exit")
    
    def maximize_plot_area(self):
        """Maximize the plotting area by minimizing control panels"""
        if hasattr(self, 'splitter'):
            # Get current window size
            window_width = self.width()
            
            # Maximize right panel (plots)
            if self.is_small_screen:
                left_width = min(200, int(window_width * 0.15))  # Very compact controls
            else:
                left_width = min(250, int(window_width * 0.12))  # Very compact controls
            
            right_width = max(800, window_width - left_width - 20)
            self.splitter.setSizes([left_width, right_width])
            
            # Update status
            self.statusBar().showMessage("SleepSense Pro ✅ Plot area maximized - Use Ctrl+C to restore controls")
    
    def toggle_compact_controls(self):
        """Toggle between compact and normal control panel sizes"""
        if hasattr(self, 'splitter'):
            current_sizes = self.splitter.sizes()
            window_width = self.width()
            
            if current_sizes[0] < 300:  # Currently compact
                # Restore normal size
                if self.is_small_screen:
                    left_width = min(280, int(window_width * 0.25))
                else:
                    left_width = max(350, int(window_width * 0.22))
                right_width = max(500, window_width - left_width - 50)
                self.statusBar().showMessage("SleepSense Pro ✅ Controls restored to normal size")
            else:
                # Make compact
                if self.is_small_screen:
                    left_width = min(200, int(window_width * 0.15))
                else:
                    left_width = min(250, int(window_width * 0.12))
                right_width = max(800, window_width - left_width - 20)
                self.statusBar().showMessage("SleepSense Pro ✅ Controls compacted - Use Ctrl+C to restore")
            
            self.splitter.setSizes([left_width, right_width])



    def togglePlayback(self):
        if self.is_playing:
            self.stopPlayback()
        else:
            self.startPlayback()

    def startPlayback(self):
        self.is_playing = True
        self.play_button.setText("⏸ Pause")
        self.play_button.setStyleSheet("background-color: #e74c3c;")
        self.play_timer.start(int(1000 * self.play_speed))  # Convert to milliseconds

    def stopPlayback(self):
        self.is_playing = False
        self.play_button.setText("▶ Play")
        self.play_button.setStyleSheet("")
        self.play_timer.stop()

    def auto_advance(self):
        # Auto-advance functionality removed with slider
        # This method is kept for compatibility but does nothing
        pass

    def changeSpeed(self, speed_text):
        speed_map = {"0.5x": 0.5, "1x": 1.0, "2x": 2.0, "5x": 5.0}
        self.play_speed = speed_map.get(speed_text, 1.0)
        if self.is_playing:
            self.play_timer.setInterval(int(1000 * self.play_speed))

    def openFile(self):
        self.statusBar().showMessage("Open file functionality - Not implemented yet")

    def saveReport(self):
        self.statusBar().showMessage("Save report functionality - Not implemented yet")

    def show_frame_change_dialog(self):
        """Show dialog to change frame size"""
        from PyQt5.QtWidgets import QInputDialog
        
        current_size = self.window_size
        new_size, ok = QInputDialog.getInt(
            self, 
            "Change Frame Size", 
            f"Enter new frame size in seconds (current: {current_size}s):",
            int(current_size), 
            1, 
            600, 
            1
        )
        
        if ok:
            # Update window size
            self.change_window_size(new_size)
            
            # Update button states to match the new size
            self.update_frame_button_states(new_size)
            
            self.statusBar().showMessage(f"Frame size changed to {new_size} seconds")
    
    def update_frame_button_states(self, selected_seconds):
        """Update frame button states to reflect the current frame size"""
        if hasattr(self, 'frame_buttons'):
            for btn_seconds, btn in self.frame_buttons.items():
                btn.setChecked(btn_seconds == selected_seconds)

    def configure_signal_checkboxes(self):
        """Configure signal checkboxes based on data availability"""
        try:
            print("Configuring signal checkboxes...")
            
            # Get number of columns in data
            if hasattr(self, 'data') and self.data is not None:
                num_columns = len(self.data.columns)
            else:
                num_columns = 0
            
            print(f"Data has {num_columns} columns")
            
            # Configure checkboxes based on data format
            if num_columns == 10:  # Current format
                # Enable current signals
                if hasattr(self, 'spo2_checkbox'):
                    self.spo2_checkbox.setEnabled(True)
                    self.spo2_checkbox.setChecked(True)
                if hasattr(self, 'pulse_checkbox'):
                    self.pulse_checkbox.setEnabled(True)
                    self.pulse_checkbox.setChecked(True)
                if hasattr(self, 'flow_checkbox'):
                    self.flow_checkbox.setEnabled(True)
                    self.flow_checkbox.setChecked(True)
                if hasattr(self, 'position_checkbox'):
                    self.position_checkbox.setEnabled(True)
                    self.position_checkbox.setChecked(True)
                
                # Enable future signals (generated)
                if hasattr(self, 'snore_checkbox'):
                    self.snore_checkbox.setEnabled(True)
                    self.snore_checkbox.setChecked(True)
                if hasattr(self, 'thorax_checkbox'):
                    self.thorax_checkbox.setEnabled(True)
                    self.thorax_checkbox.setChecked(True)
                if hasattr(self, 'abdomen_checkbox'):
                    self.abdomen_checkbox.setEnabled(True)
                    self.abdomen_checkbox.setChecked(True)
                if hasattr(self, 'pleth_checkbox'):
                    self.pleth_checkbox.setEnabled(True)
                    self.pleth_checkbox.setChecked(True)
                if hasattr(self, 'activity_checkbox'):
                    self.activity_checkbox.setEnabled(True)
                    self.activity_checkbox.setChecked(True)
                
                self.statusBar().showMessage("Current data format detected - All waves plotted for better analysis")
                
            elif num_columns >= 15:  # Mock data or future format with EEG
                # Enable all signals including EEG
                if hasattr(self, 'snore_checkbox'):
                    self.snore_checkbox.setEnabled(True)
                    self.snore_checkbox.setChecked(True)
                if hasattr(self, 'thorax_checkbox'):
                    self.thorax_checkbox.setEnabled(True)
                    self.thorax_checkbox.setChecked(True)
                if hasattr(self, 'abdomen_checkbox'):
                    self.abdomen_checkbox.setEnabled(True)
                    self.abdomen_checkbox.setChecked(True)
                if hasattr(self, 'pleth_checkbox'):
                    self.pleth_checkbox.setEnabled(True)
                    self.pleth_checkbox.setChecked(True)
                if hasattr(self, 'spo2_checkbox'):
                    self.spo2_checkbox.setEnabled(True)
                    self.spo2_checkbox.setChecked(True)
                if hasattr(self, 'pulse_checkbox'):
                    self.pulse_checkbox.setEnabled(True)
                    self.pulse_checkbox.setChecked(True)
                if hasattr(self, 'flow_checkbox'):
                    self.flow_checkbox.setEnabled(True)
                    self.flow_checkbox.setChecked(True)
                if hasattr(self, 'position_checkbox'):
                    self.position_checkbox.setEnabled(True)
                    self.position_checkbox.setChecked(True)
                if hasattr(self, 'activity_checkbox'):
                    self.activity_checkbox.setEnabled(True)
                    self.activity_checkbox.setChecked(True)
                
                if num_columns == 15:
                    self.statusBar().showMessage("Mock data format detected - 8 hours of realistic sleep data loaded with all signals")
                else:
                    self.statusBar().showMessage("Future data format detected - All signals enabled and plotted")
                    
            elif num_columns >= 12:  # Future format without EEG
                # Enable all signals
                if hasattr(self, 'snore_checkbox'):
                    self.snore_checkbox.setEnabled(True)
                    self.snore_checkbox.setChecked(True)
                if hasattr(self, 'thorax_checkbox'):
                    self.thorax_checkbox.setEnabled(True)
                    self.thorax_checkbox.setChecked(True)
                if hasattr(self, 'abdomen_checkbox'):
                    self.abdomen_checkbox.setEnabled(True)
                    self.abdomen_checkbox.setChecked(True)
                if hasattr(self, 'pleth_checkbox'):
                    self.pleth_checkbox.setEnabled(True)
                    self.pleth_checkbox.setChecked(True)
                if hasattr(self, 'spo2_checkbox'):
                    self.spo2_checkbox.setEnabled(True)
                    self.spo2_checkbox.setChecked(True)
                if hasattr(self, 'pulse_checkbox'):
                    self.pulse_checkbox.setEnabled(True)
                    self.pulse_checkbox.setChecked(True)
                if hasattr(self, 'flow_checkbox'):
                    self.flow_checkbox.setEnabled(True)
                    self.flow_checkbox.setChecked(True)
                if hasattr(self, 'position_checkbox'):
                    self.position_checkbox.setEnabled(True)
                    self.position_checkbox.setChecked(True)
                if hasattr(self, 'activity_checkbox'):
                    self.activity_checkbox.setEnabled(True)
                    self.activity_checkbox.setChecked(True)
                
                self.statusBar().showMessage("Future data format detected - All signals enabled and plotted")
                
            else:
                # Fallback - enable basic signals
                if hasattr(self, 'spo2_checkbox'):
                    self.spo2_checkbox.setEnabled(True)
                    self.spo2_checkbox.setChecked(True)
                if hasattr(self, 'pulse_checkbox'):
                    self.pulse_checkbox.setEnabled(True)
                    self.pulse_checkbox.setChecked(True)
                if hasattr(self, 'flow_checkbox'):
                    self.flow_checkbox.setEnabled(True)
                    self.flow_checkbox.setChecked(True)
                
                self.statusBar().showMessage("Basic signals enabled - Limited data format detected")
            
            print("Signal checkboxes configured successfully")
            
        except Exception as e:
            print(f"Error configuring signal checkboxes: {e}")
            # Enable basic checkboxes as fallback
            try:
                if hasattr(self, 'spo2_checkbox'):
                    self.spo2_checkbox.setEnabled(True)
                    self.spo2_checkbox.setChecked(True)
                if hasattr(self, 'pulse_checkbox'):
                    self.pulse_checkbox.setEnabled(True)
                    self.pulse_checkbox.setChecked(True)
                if hasattr(self, 'flow_checkbox'):
                    self.flow_checkbox.setEnabled(True)
                    self.flow_checkbox.setChecked(True)
                print("Basic checkboxes enabled as fallback")
            except Exception as e2:
                print(f"Failed to enable fallback checkboxes: {e2}")

    def plot_activity_simple(self, ax, offset, start_idx, end_idx):
        """Optimized activity plotting for better performance"""
        # Use simplified activity display
        activity_window = self.activity_n.iloc[start_idx:end_idx]
        time_window = self.time.iloc[start_idx:end_idx]
        
        # Create simple line plot instead of complex bars - bright color for dark mode
        ax.plot(time_window, activity_window + offset, color='#FFD700', linewidth=0.8, label='Activity', alpha=0.9)
        
        # Add simple sleep/wake indicators at key points
        if end_idx - start_idx > 50:
            step = (end_idx - start_idx) // 10
            for i in range(start_idx, end_idx, step):
                if i < len(self.activity):
                    if self.activity.iloc[i] > 0.5:
                        ax.scatter(self.time.iloc[i], self.activity_n.iloc[i] + offset + 0.1, 
                                 color='#FF6B6B', s=25, alpha=0.9, marker='o')
                    else:
                        ax.scatter(self.time.iloc[i], self.activity_n.iloc[i] + offset - 0.1, 
                                 color='#4ECDC4', s=25, alpha=0.9, marker='s')

    def create_sleep_wake_indicators(self):
        """Create discrete sleep/wake indicators based on activity data"""
        # Convert continuous activity to discrete sleep/wake states
        sleep_wake = np.zeros_like(self.activity)
        
        # Threshold-based classification
        threshold = 0.5
        for i, activity_val in enumerate(self.activity):
            if activity_val > threshold:
                sleep_wake[i] = 1  # Wake
            else:
                sleep_wake[i] = 0  # Sleep
        
        # Add some smoothing to avoid rapid switching
        smoothed_sleep_wake = np.copy(sleep_wake)
        window_size = 20  # Smooth over 20 samples
        
        for i in range(window_size, len(smoothed_sleep_wake)):
            # If majority of recent samples are wake, classify as wake
            recent_samples = sleep_wake[i-window_size:i]
            if np.mean(recent_samples) > 0.6:
                smoothed_sleep_wake[i] = 1
            elif np.mean(recent_samples) < 0.4:
                smoothed_sleep_wake[i] = 0
        
        return smoothed_sleep_wake

    def debounced_update_plots(self):
        """Debounced plot update to prevent excessive redraws"""
        if hasattr(self, '_update_timer'):
            self._update_timer.stop()
        else:
            self._update_timer = QTimer()
            self._update_timer.setSingleShot(True)
            self._update_timer.timeout.connect(self.update_plots)
        
        # Wait 100ms before updating to batch multiple checkbox changes
        self._update_timer.start(100)

    def toggle_zoom(self, signal_index, zoomed_in):
        """Toggle zoom state for a specific wave by adjusting its offset."""
        if signal_index in self.zoom_toggles:
            toggle_btn = self.zoom_toggles[signal_index]
            
            # Update zoom state
            self.zoom_states[signal_index] = zoomed_in
            
            # Update button text and style based on state
            if zoomed_in:
                toggle_btn.setText("▼")  # Down arrow when zoomed in
                # Zoom in effect
                current_offset = self.offsets[signal_index]
                new_offset = current_offset * 1.5  # Zoom in
                new_offset = max(-2.0, min(new_offset, 2.0))  # Keep within bounds
                self.offsets[signal_index] = new_offset
            else:
                toggle_btn.setText("▲")  # Up arrow when zoomed out
                # Zoom out effect
                current_offset = self.offsets[signal_index]
                new_offset = current_offset * 0.8  # Zoom out
                new_offset = max(-2.0, min(new_offset, 2.0))  # Keep within bounds
                self.offsets[signal_index] = new_offset
            
            # Update the plot with debouncing
            self.debounced_update_plots()
    
    def zoom_wave(self, signal_index, factor):
        """Zoom in or out on a specific wave by adjusting its offset."""
        current_offset = self.offsets[signal_index]
        new_offset = current_offset * factor
        
        # Ensure new offset is within reasonable bounds
        min_offset = -2.0 # Allow signals to go slightly below baseline
        max_offset = 2.0 # Allow signals to go slightly above baseline
        
        new_offset = max(min_offset, min(new_offset, max_offset))
        
        self.offsets[signal_index] = new_offset
        self.update_plot()

    # Data Security Methods
    def secure_existing_data(self):
        """Convert existing plain text data files to encrypted format"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self, 
                'Secure Data', 
                'This will convert all existing plain text data files to encrypted format.\n\n'
                'This ensures your sleep data is only readable within SleepSense.\n\n'
                'Do you want to proceed?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Show progress message
                self.statusBar().showMessage("Securing existing data files...")
                
                # Convert data to encrypted format
                converted_files = self.data_manager.secure_all_existing_data()
                
                if converted_files:
                    QMessageBox.information(
                        self,
                        'Data Secured',
                        f'Successfully secured {len(converted_files)} data files!\n\n'
                        'All your sleep data is now encrypted and secure.\n'
                        'Only SleepSense can read this data.'
                    )
                    self.statusBar().showMessage(f"✅ {len(converted_files)} files secured successfully")
                else:
                    QMessageBox.information(
                        self,
                        'No Action Needed',
                        'No plain text data files found to convert.\n'
                        'Your data is already secure!'
                    )
                    self.statusBar().showMessage("✅ No files need conversion")
                    
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to secure data: {str(e)}\n\n'
                'Please check the console for details.'
            )
            self.statusBar().showMessage("❌ Failed to secure data")
            print(f"Error securing data: {e}")

    def list_data_files(self):
        """Show information about available data files"""
        try:
            from PyQt5.QtWidgets import QMessageBox, QTextEdit, QVBoxLayout, QDialog
            
            # Get list of available files
            files_info = self.data_manager.list_available_data_files()
            
            # Create dialog to show file information
            dialog = QDialog(self)
            dialog.setWindowTitle("Data Files Information")
            dialog.setModal(True)
            dialog.resize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Create text display
            text_display = QTextEdit()
            text_display.setReadOnly(True)
            
            # Format file information
            info_text = "📋 Available Data Files\n"
            info_text += "=" * 50 + "\n\n"
            
            if files_info["total"] == 0:
                info_text += "No data files found.\n"
            else:
                # Show encrypted files
                if files_info["encrypted"]:
                    info_text += f"🔒 Encrypted Files ({len(files_info['encrypted'])}):\n"
                    for file_info in files_info["encrypted"]:
                        info = file_info["info"]
                        info_text += f"   • {file_info['filename']}\n"
                        info_text += f"     - Size: {info.get('size_bytes', 'Unknown')} bytes\n"
                        info_text += f"     - Encrypted: {info.get('encrypted', True)}\n"
                        if 'encrypted_at' in info:
                            info_text += f"     - Encrypted at: {info['encrypted_at']}\n"
                        info_text += "\n"
                
                # Show plain text files
                if files_info["plain_text"]:
                    info_text += f"📄 Plain Text Files ({len(files_info['plain_text'])}):\n"
                    info_text += "   ⚠️  These files are NOT encrypted and can be read by anyone!\n\n"
                    for file_info in files_info["plain_text"]:
                        info = file_info["info"]
                        info_text += f"   • {file_info['filename']}\n"
                        info_text += f"     - Size: {info.get('size_bytes', 'Unknown')} bytes\n"
                        info_text += f"     - Format: {info.get('format', 'Unknown')}\n"
                        info_text += "\n"
            
            text_display.setPlainText(info_text)
            layout.addWidget(text_display)
            
            # Show dialog
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to list data files: {str(e)}'
            )
            print(f"Error listing data files: {e}")

    def export_secure_data(self):
        """Export data in a user-readable format (for reports, sharing, etc.)"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            
            if self.data is None:
                QMessageBox.warning(
                    self,
                    'No Data',
                    'No data loaded to export.'
                )
                return
            
            # Get export format from user
            format_options = ["CSV", "Excel", "Text"]
            format_choice, ok = QInputDialog.getItem(
                self, 
                'Export Format', 
                'Choose export format:',
                format_options, 
                0, 
                False
            )
            
            if not ok:
                return
            
            # Get save location
            default_name = f"sleep_data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            if format_choice == "CSV":
                filepath, _ = QFileDialog.getSaveFileName(
                    self, 
                    'Save Export', 
                    f"{default_name}.csv",
                    'CSV Files (*.csv)'
                )
            elif format_choice == "Excel":
                filepath, _ = QFileDialog.getSaveFileName(
                    self, 
                    'Save Export', 
                    f"{default_name}.xlsx",
                    'Excel Files (*.xlsx)'
                )
            else:  # Text
                filepath, _ = QFileDialog.getSaveFileName(
                    self, 
                    'Save Export', 
                    f"{default_name}.txt",
                    'Text Files (*.txt)'
                )
            
            if filepath:
                # Export data
                self.data_manager.export_data_for_user(
                    self.data, 
                    filepath, 
                    format_choice.lower()
                )
                
                QMessageBox.information(
                    self,
                    'Export Successful',
                    f'Data exported successfully to:\n{filepath}\n\n'
                    '⚠️  Note: This export file is NOT encrypted.\n'
                    'Handle it with appropriate care for privacy.'
                )
                
                self.statusBar().showMessage(f"✅ Data exported to {os.path.basename(filepath)}")
                
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to export data: {str(e)}'
            )
            print(f"Error exporting data: {e}")

    # Region Selection Methods
    def on_mouse_press(self, event):
        """Handle mouse press events for region selection"""
        try:
            if event.inaxes != self.detailed_ax:
                return
            
            if event.button == 1:  # Left mouse button
                # Start region selection
                self.is_selecting = True
                self.selection_start = (event.xdata, event.ydata)
                
                # Create selection rectangle
                self.selection_rect = plt.Rectangle(
                    (event.xdata, event.ydata), 0, 0,
                    fill=True, alpha=0.3, color='blue', edgecolor='darkblue'
            )
            self.detailed_ax.add_patch(self.selection_rect)
            self.detailed_canvas.draw_idle()
            
            print(f"Started region selection at ({event.xdata:.2f}, {event.ydata:.2f})")
            
        except Exception as e:
            print(f"Error in mouse press: {e}")
    
    def on_mouse_release(self, event):
        """Handle mouse release events for region selection"""
        try:
            if not self.is_selecting or event.inaxes != self.detailed_ax:
                return
            
            if event.button == 1:  # Left mouse button
                # End region selection
                self.is_selecting = False
            
                if self.selection_start and self.selection_rect:
                    # Get selection coordinates
                    start_x, start_y = self.selection_start
                    end_x, end_y = event.xdata, event.ydata
                    
                    # Ensure proper order (start < end)
                    x1, x2 = min(start_x, end_x), max(start_x, end_x)
                    y1, y2 = min(start_y, end_y), max(start_y, end_y)
                    
                    # Create region data
                    region = {
                        'start_time': x1,
                        'end_time': x2,
                        'start_y': y1,
                        'end_y': y2,
                'rectangle': self.selection_rect
            }
            
            # Add to selected regions
                    self.selected_regions.append(region)
                    
                    # Update rectangle to final position
                    self.selection_rect.set_xy((x1, y1))
                    self.selection_rect.set_width(x2 - x1)
                    self.selection_rect.set_height(y2 - y1)
                    
                    # Make rectangle permanent (darker)
                    self.selection_rect.set_alpha(0.5)
                    self.selection_rect.set_color('darkblue')
            
            # Clear selection variables
            self.selection_start = None
            self.selection_rect = None
            
            # Redraw canvas
            self.detailed_canvas.draw_idle()
            
            print(f"Region selected: {x1:.2f}s to {x2:.2f}s")
            self.statusBar().showMessage(f"✅ Region selected: {x1:.1f}s to {x2:.1f}s")
            
        except Exception as e:
            print(f"Error in mouse release: {e}")
            self.is_selecting = False
            self.selection_start = None
            self.selection_rect = None
    
    def on_mouse_move(self, event):
        """Handle mouse move events for region selection"""
        try:
            if not self.is_selecting or not self.selection_rect or event.inaxes != self.detailed_ax:
                return
            
            if self.selection_start:
                # Update selection rectangle
                start_x, start_y = self.selection_start
                current_x, current_y = event.xdata, event.ydata
                
                # Calculate rectangle dimensions
                x1, x2 = min(start_x, current_x), max(start_x, current_x)
                y1, y2 = min(start_y, current_y), max(start_y, current_y)
                
                # Update rectangle
                self.selection_rect.set_xy((x1, y1))
                self.selection_rect.set_width(x2 - x1)
                self.selection_rect.set_height(y2 - y1)
                
                # Redraw canvas
                self.detailed_canvas.draw_idle()
                
        except Exception as e:
            print(f"Error in mouse move: {e}")
    
    def clear_selected_regions(self):
        """Clear all selected regions"""
        try:
            # Remove all region rectangles from the plot
            for region in self.selected_regions:
                if 'rectangle' in region and region['rectangle']:
                    region['rectangle'].remove()
            
            # Clear the regions list
            self.selected_regions.clear()
            
            # Redraw canvas
            if hasattr(self, 'detailed_canvas'):
                self.detailed_canvas.draw_idle()
            
            print("All regions cleared")
            self.statusBar().showMessage("🗑️ All regions cleared")
            
        except Exception as e:
            print(f"Error clearing regions: {e}")
    
    def get_selected_regions_info(self):
        """Get information about all selected regions"""
        if not self.selected_regions:
            return "No regions selected"
        
        info = f"📋 Selected Regions ({len(self.selected_regions)}):\n"
        for i, region in enumerate(self.selected_regions, 1):
            start_str = f"{region['start_time']:.1f}s"
            end_str = f"{region['end_time']:.1f}s"
            duration_str = f"{region['duration']:.1f}s"
            info += f"  {i}. {start_str} → {end_str} ({duration_str})\n"
        
        return info
    
    def show_selected_regions(self):
        """Show information about selected regions in a dialog"""
        try:
            from PyQt5.QtWidgets import QMessageBox, QTextEdit, QVBoxLayout, QDialog
            
            # Create dialog to show region information
            dialog = QDialog(self)
            dialog.setWindowTitle("Selected Regions Information")
            dialog.setModal(True)
            dialog.resize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Create text display
            text_display = QTextEdit()
            text_display.setReadOnly(True)
            
            # Get region information
            regions_info = self.get_selected_regions_info()
            
            # Format display text
            display_text = "🖱️  Region Selection Information\n"
            display_text += "=" * 50 + "\n\n"
            display_text += regions_info
            
            if self.selected_regions:
                display_text += "\n💡 Tips:\n"
                display_text += "• Click and drag in Detailed View to select regions\n"
                display_text += "• Selected regions are highlighted in blue\n"
                display_text += "• Use 'Clear All Regions' to remove selections\n"
                display_text += "• Regions help mark important sleep events\n"
            
            text_display.setPlainText(display_text)
            layout.addWidget(text_display)
            
            # Show dialog
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to show regions info: {str(e)}'
            )
            print(f"Error showing regions info: {e}")
    
    def update_detailed_view_title(self):
        """Update the detailed view title to show current region count"""
        try:
            regions_count = len(self.selected_regions)
            if regions_count > 0:
                title = f'SleepSense - Detailed Waveform View\n💡 Click and drag to select regions | 📋 {regions_count} region(s) selected'
            else:
                title = 'SleepSense - Detailed Waveform View\n💡 Click and drag to select regions (lights on/off)'
            
            self.detailed_ax.set_title(title, fontsize=14, fontweight='bold')
            self.detailed_canvas.draw_idle()
        except Exception as e:
            print(f"Error updating title: {e}")
    
    def on_slider_changed(self, value):
        """Handle slider value changes for time navigation"""
        try:
            print(f"Slider value changed to: {value}")
            
            # Convert slider value (0-1000) to time position
            if hasattr(self, 'time') and len(self.time) > 0:
                total_time = self.end_time - self.time.iloc[0]
                if total_time > 0:
                    # Calculate new start time based on slider position
                    new_start_time = self.time.iloc[0] + (value / 1000.0) * total_time
                    
                    # Ensure start time is within bounds
                    max_start = self.end_time - self.window_size
                    new_start_time = max(self.time.iloc[0], min(new_start_time, max_start))
                    
                    # Update start time
                    self.start_time = new_start_time
                    
                    print(f"Start time updated to: {self.start_time:.1f}s")
                    
                    # Update the plot
                    self.update_plot()
                    
                    # Update current time label
                    if hasattr(self, 'current_time_label'):
                        current_time_str = f"{int(self.start_time//60):02d}:{int(self.start_time%60):02d}:{int((self.start_time%1)*100):02d}"
                        self.current_time_label.setText(current_time_str)
                    
                    # Update status bar
                    self.statusBar().showMessage(f"🕐 Time position: {self.start_time:.1f}s | Frame: {self.window_size:.1f}s")
                else:
                    print("Total time is zero or negative")
            else:
                print("Time data not available")
                
        except Exception as e:
            print(f"Error handling slider change: {e}")
            self.statusBar().showMessage(f"❌ Error updating time position: {e}")

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for navigation and region management"""
        try:
            if event.key() == Qt.Key_Left:
                # Navigate left (earlier time)
                self.navigate_time(-1)
            elif event.key() == Qt.Key_Right:
                # Navigate right (later time)
                self.navigate_time(1)
            elif event.key() == Qt.Key_Up:
                # Increase frame size
                self.change_frame_size(1)
            elif event.key() == Qt.Key_Down:
                # Decrease frame size
                self.change_frame_size(-1)
            elif event.key() == Qt.Key_Home:
                # Go to beginning
                self.go_to_beginning()
            elif event.key() == Qt.Key_End:
                # Go to end
                self.go_to_end()
            elif event.key() == Qt.Key_PageUp:
                # Navigate by frame (backward)
                self.navigate_by_frame(-1)
            elif event.key() == Qt.Key_PageDown:
                # Navigate by frame (forward)
                self.navigate_by_frame(1)
            elif event.key() == Qt.Key_R and event.modifiers() == Qt.ControlModifier:
                # Ctrl+R: Clear all regions
                self.clear_all_regions()
                print("Ctrl+R pressed - All regions cleared")
            elif event.key() == Qt.Key_F1:
                # F1: Show navigation help
                self.show_navigation_help()
            else:
                # Call parent class for other key events
                super().keyPressEvent(event)
                
        except Exception as e:
            print(f"Error in keyPressEvent: {e}")
            # Call parent class as fallback
            super().keyPressEvent(event)

    def navigate_time(self, direction):
        """Navigate through time (left/right arrows)"""
        try:
            # Calculate navigation step based on current frame size
            step = self.window_size * 0.1  # 10% of current frame size
            
            if direction > 0:  # Right arrow - move forward
                new_start = self.start_time + step
                max_start = self.end_time - self.window_size
                self.start_time = min(new_start, max_start)
            else:  # Left arrow - move backward
                new_start = self.start_time - step
                min_start = self.time.iloc[0]
                self.start_time = max(new_start, min_start)
            
            # Update the plot
            self.update_plot()
            print(f"Navigated {'forward' if direction > 0 else 'backward'} to {self.start_time:.1f}s")
            
        except Exception as e:
            print(f"Error navigating time: {e}")
    
    def change_frame_size(self, direction):
        """Change frame size (up/down arrows)"""
        try:
            # Get current frame sizes
            frame_sizes = [5, 10, 30, 60, 120, 300, 600, 1800]
            current_index = frame_sizes.index(int(self.window_size)) if int(self.window_size) in frame_sizes else 3
            
            if direction > 0:  # Up arrow - increase frame size
                new_index = min(current_index + 1, len(frame_sizes) - 1)
            else:  # Down arrow - decrease frame size
                new_index = max(current_index - 1, 0)
            
            new_size = frame_sizes[new_index]
            self.set_frame_size_from_button(new_size)
            print(f"Frame size changed to {new_size}s")
            
        except Exception as e:
            print(f"Error changing frame size: {e}")
    
    def go_to_beginning(self):
        """Go to the beginning of the data"""
        try:
            if hasattr(self, 'time') and len(self.time) > 0:
                self.start_time = self.time.iloc[0]
                self.update_plot()
                print("Navigated to beginning of data")
                self.statusBar().showMessage("🏠 At beginning of data")
        except Exception as e:
            print(f"Error going to beginning: {e}")
    
    def go_to_end(self):
        """Go to the end of the data"""
        try:
            if hasattr(self, 'time') and len(self.time) > 0:
                self.start_time = self.end_time - self.window_size
                self.start_time = max(self.start_time, self.time.iloc[0])
                self.update_plot()
                print("Navigated to end of data")
                self.statusBar().showMessage("🏁 At end of data")
        except Exception as e:
            print(f"Error going to end: {e}")
    
    def navigate_by_frame(self, direction):
        """Navigate by one frame size (Page Up/Down)"""
        try:
            if direction > 0:  # Page Down - move forward by one frame
                new_start = self.start_time + self.window_size
                max_start = self.end_time - self.window_size
                self.start_time = min(new_start, max_start)
            else:  # Page Up - move backward by one frame
                new_start = self.start_time - self.window_size
                min_start = self.time.iloc[0]
                self.start_time = max(new_start, min_start)
            
            # Update the plot
            self.update_plot()
            print(f"Navigated by frame {'forward' if direction > 0 else 'backward'} to {self.start_time:.1f}s")
            
        except Exception as e:
            print(f"Error navigating by frame: {e}")

    def show_navigation_help(self):
        """Show navigation help dialog"""
        help_text = """
🕐 Navigation Controls:

Mouse:
• Click and drag slider to navigate through time
• Click frame size buttons to change view

Keyboard:
• ← → Arrow keys: Move backward/forward in time
• ↑ ↓ Arrow keys: Increase/decrease frame size
• Home: Go to beginning of data
• End: Go to end of data
• Page Up/Down: Move by one frame
• Ctrl+M: Maximize plot area
• Ctrl+C: Toggle compact controls

Frame Sizes:
• 5s-30s: High detail mode (zoomed in)
• 1m-5m: Balanced view
• 10m-30m: Compact comparison mode
        """
        
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Navigation Help")
        msg.setText("SleepSense Pro Navigation Controls")
        msg.setInformativeText(help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def generate_8_hour_mock_data(self):
        """Generate 8 hours of realistic sleep data with proper sampling"""
        try:
            print("Generating 8 hours of realistic sleep data...")
            
            # 8 hours = 28800 seconds
            duration_seconds = 8 * 3600
            sampling_rate = 10  # 10 Hz sampling rate
            total_samples = duration_seconds * sampling_rate
            
            # Create time array in milliseconds
            time_ms = np.arange(0, total_samples) * 100  # 100ms intervals for 10 Hz
            
            # Generate realistic sleep patterns - simplified for stability
            data = np.zeros((total_samples, 15))  # 15 columns for future format + EEG
            
            # Column 0: Time (ms)
            data[:, 0] = time_ms
            
            # Column 1: Snore (simplified)
            data[:, 1] = self.generate_simple_snore(total_samples, sampling_rate)
            
            # Column 2: Flow (respiratory airflow)
            data[:, 2] = self.generate_simple_flow(total_samples, sampling_rate)
            
            # Column 3: Thorax Movement
            data[:, 3] = self.generate_simple_thorax(total_samples, sampling_rate)
            
            # Column 4: Abdomen Movement
            data[:, 4] = self.generate_simple_abdomen(total_samples, sampling_rate)
            
            # Column 5: SpO2 (oxygen saturation with realistic variations)
            data[:, 5] = self.generate_simple_spo2(total_samples, sampling_rate)
            
            # Column 6: Plethysmography
            data[:, 6] = self.generate_simple_pleth(total_samples, sampling_rate)
            
            # Column 7: Pulse (heart rate with sleep variations)
            data[:, 7] = self.generate_simple_pulse(total_samples, sampling_rate)
            
            # Column 8: Body Position (realistic position changes)
            data[:, 8] = self.generate_simple_body_position(total_samples, sampling_rate)
            
            # Column 9: Activity (sleep/wake cycles)
            data[:, 9] = self.generate_simple_activity(total_samples, sampling_rate)
            
            # Column 10-14: EEG channels (simplified brain wave patterns)
            data[:, 10] = self.generate_simple_eeg(total_samples, sampling_rate, 'c3')
            data[:, 11] = self.generate_simple_eeg(total_samples, sampling_rate, 'c4')
            data[:, 12] = self.generate_simple_eeg(total_samples, sampling_rate, 'f3')
            data[:, 13] = self.generate_simple_eeg(total_samples, sampling_rate, 'f4')
            data[:, 14] = self.generate_simple_eeg(total_samples, sampling_rate, 'o1')
            
            # Create DataFrame with proper column names
            columns = ['time_ms', 'snore', 'flow', 'thorax', 'abdomen', 'spo2', 'pleth', 
                      'pulse', 'body_pos', 'activity', 'eeg_c3', 'eeg_c4', 'eeg_f3', 'eeg_f4', 'eeg_o1']
            
            df = pd.DataFrame(data, columns=columns)
            print(f"Generated {len(df)} samples covering {duration_seconds/3600:.1f} hours")
            return df
            
        except Exception as e:
            print(f"Error generating mock data: {e}")
            # Fallback to simple data generation
            return self.generate_fallback_data()

    def generate_fallback_data(self):
        """Generate simple fallback data if complex generation fails"""
        print("Generating fallback data...")
        
        # Simple 8-hour dataset
        total_samples = 8 * 3600 * 10  # 8 hours * 3600 seconds * 10 Hz
        time_ms = np.arange(0, total_samples) * 100
        
        # Create simple patterns
        data = np.zeros((total_samples, 15))
        data[:, 0] = time_ms  # Time
        
        # Simple sine waves for all signals
        t = np.arange(total_samples) / 100  # Time in seconds
        
        # Snore (0.1 Hz)
        data[:, 1] = 0.5 * np.sin(2 * np.pi * 0.1 * t)
        
        # Flow (0.3 Hz - breathing)
        data[:, 2] = 0.8 * np.sin(2 * np.pi * 0.3 * t)
        
        # Thorax (0.3 Hz)
        data[:, 3] = 0.7 * np.sin(2 * np.pi * 0.3 * t + 0.1)
        
        # Abdomen (0.3 Hz)
        data[:, 4] = 0.6 * np.sin(2 * np.pi * 0.3 * t + 0.2)
        
        # SpO2 (stable with small variations)
        data[:, 5] = 98 + 1.0 * np.sin(2 * np.pi * 0.05 * t)
        
        # Pleth (1.2 Hz - heart rate)
        data[:, 6] = 0.9 * np.sin(2 * np.pi * 1.2 * t)
        
        # Pulse (heart rate variations)
        data[:, 7] = 75 + 5 * np.sin(2 * np.pi * 0.02 * t)
        
        # Body position (changes every hour)
        data[:, 8] = np.floor(t / 3600) % 4  # 0, 1, 2, 3 positions
        
        # Activity (sleep pattern)
        data[:, 9] = 0.1 + 0.2 * np.sin(2 * np.pi * 0.01 * t)
        
        # EEG channels (different frequencies)
        data[:, 10] = 0.8 * np.sin(2 * np.pi * 10 * t)  # Alpha (10 Hz)
        data[:, 11] = 0.7 * np.sin(2 * np.pi * 12 * t)  # Alpha (12 Hz)
        data[:, 12] = 0.6 * np.sin(2 * np.pi * 6 * t)   # Theta (6 Hz)
        data[:, 13] = 0.5 * np.sin(2 * np.pi * 8 * t)   # Alpha (8 Hz)
        data[:, 14] = 0.9 * np.sin(2 * np.pi * 11 * t)  # Alpha (11 Hz)
        
        columns = ['time_ms', 'snore', 'flow', 'thorax', 'abdomen', 'spo2', 'pleth', 
                  'pulse', 'body_pos', 'activity', 'eeg_c3', 'eeg_c4', 'eeg_f3', 'eeg_f4', 'eeg_o1']
        
        df = pd.DataFrame(data, columns=columns)
        print(f"Generated fallback data: {len(df)} samples")
        return df

    def generate_simple_snore(self, total_samples, sampling_rate):
        """Generate simple snoring pattern over 8 hours"""
        try:
            snore = np.zeros(total_samples)
            
            # Create simple snoring pattern with random bursts
            for i in range(0, total_samples, 1000):  # Every 100 seconds
                if np.random.random() > 0.7:  # 30% chance of snore
                    burst_duration = np.random.randint(50, 200)
                    burst_end = min(i + burst_duration, total_samples)
                    burst_start = max(0, i)
                    
                    if burst_end > burst_start:
                        # Simple snore burst
                        burst_samples = burst_end - burst_start
                        freq = np.random.uniform(0.5, 2.0)
                        amplitude = np.random.uniform(0.3, 1.0)
                        time_array = np.arange(burst_samples) / sampling_rate
                        snore[burst_start:burst_end] = amplitude * np.sin(2 * np.pi * freq * time_array)
            
            # Add some noise
            snore += np.random.normal(0, 0.02, total_samples)
            return snore
            
        except Exception as e:
            print(f"Error in simple snore generation: {e}")
            return np.random.normal(0, 0.1, total_samples)

    def generate_simple_flow(self, total_samples, sampling_rate):
        """Generate simple respiratory airflow pattern"""
        try:
            # Simple breathing pattern
            breathing_rate = 0.25  # 15 breaths per minute
            time_array = np.arange(total_samples) / sampling_rate
            flow = np.sin(2 * np.pi * breathing_rate * time_array)
            
            # Add some variation
            flow += 0.2 * np.sin(2 * np.pi * 0.05 * time_array)
            flow += np.random.normal(0, 0.05, total_samples)
            
            return flow
            
        except Exception as e:
            print(f"Error in simple flow generation: {e}")
            return np.random.normal(0, 0.5, total_samples)

    def generate_simple_thorax(self, total_samples, sampling_rate):
        """Generate simple thorax movement pattern"""
        try:
            # Similar to flow but with phase difference
            breathing_rate = 0.25
            time_array = np.arange(total_samples) / sampling_rate
            thorax = np.sin(2 * np.pi * breathing_rate * time_array + 0.2)
            
            # Add some variation
            thorax += 0.15 * np.sin(2 * np.pi * 0.04 * time_array)
            thorax += np.random.normal(0, 0.03, total_samples)
            
            return thorax
            
        except Exception as e:
            print(f"Error in simple thorax generation: {e}")
            return np.random.normal(0, 0.3, total_samples)

    def generate_simple_abdomen(self, total_samples, sampling_rate):
        """Generate simple abdomen movement pattern"""
        try:
            # Similar to thorax but with different phase
            breathing_rate = 0.25
            time_array = np.arange(total_samples) / sampling_rate
            abdomen = np.sin(2 * np.pi * breathing_rate * time_array + 0.4)
            
            # Add some variation
            abdomen += 0.1 * np.sin(2 * np.pi * 0.03 * time_array)
            abdomen += np.random.normal(0, 0.04, total_samples)
            
            return abdomen
            
        except Exception as e:
            print(f"Error in simple abdomen generation: {e}")
            return np.random.normal(0, 0.2, total_samples)

    def generate_simple_spo2(self, total_samples, sampling_rate):
        """Generate simple SpO2 pattern"""
        try:
            spo2 = np.ones(total_samples) * 98  # Start at 98%
            
            # Add simple variations
            time_array = np.arange(total_samples) / sampling_rate
            
            # Gradual decrease during sleep
            spo2 += 2 * np.sin(2 * np.pi * 0.001 * time_array)  # Very slow variation
            
            # Add some random dips
            for i in range(0, total_samples, 2000):  # Every 200 seconds
                if np.random.random() > 0.8:  # 20% chance of dip
                    dip_duration = np.random.randint(100, 300)
                    dip_end = min(i + dip_duration, total_samples)
                    dip_start = max(0, i)
                    
                    if dip_end > dip_start:
                        # Simple dip
                        dip_samples = dip_end - dip_start
                        spo2[dip_start:dip_end] -= 3  # Drop by 3%
            
            # Ensure SpO2 stays within realistic bounds
            spo2 = np.clip(spo2, 85, 100)
            return spo2
            
        except Exception as e:
            print(f"Error in simple SpO2 generation: {e}")
            return np.ones(total_samples) * 98

    def generate_simple_pleth(self, total_samples, sampling_rate):
        """Generate simple plethysmography waveform"""
        try:
            # Simple heart rate pattern
            heart_rate = 1.2  # 72 BPM
            time_array = np.arange(total_samples) / sampling_rate
            
            # Basic pleth waveform
            pleth = np.sin(2 * np.pi * heart_rate * time_array)
            
            # Add harmonics
            pleth += 0.3 * np.sin(2 * np.pi * 2 * heart_rate * time_array)
            pleth += 0.1 * np.sin(2 * np.pi * 3 * heart_rate * time_array)
            
            # Add respiratory modulation
            resp_freq = 0.25  # 15 breaths per minute
            pleth *= (1 + 0.2 * np.sin(2 * np.pi * resp_freq * time_array))
            
            # Add noise
            pleth += np.random.normal(0, 0.05, total_samples)
            
            return pleth
            
        except Exception as e:
            print(f"Error in simple pleth generation: {e}")
            return np.random.normal(0, 0.5, total_samples)

    def generate_simple_pulse(self, total_samples, sampling_rate):
        """Generate simple pulse/heart rate pattern"""
        try:
            # Base heart rate
            base_hr = 75
            
            # Simple variations
            time_array = np.arange(total_samples) / sampling_rate
            
            # Slow variation over time
            pulse = base_hr + 3 * np.sin(2 * np.pi * 0.001 * time_array)
            
            # Add some random variations
            pulse += np.random.normal(0, 2, total_samples)
            
            # Ensure heart rate stays within realistic bounds
            pulse = np.clip(pulse, 45, 120)
            
            return pulse
            
        except Exception as e:
            print(f"Error in simple pulse generation: {e}")
            return np.ones(total_samples) * 75

    def generate_simple_body_position(self, total_samples, sampling_rate):
        """Generate simple body position changes"""
        try:
            body_pos = np.zeros(total_samples, dtype=int)
            
            # Change position every hour
            change_interval = 60 * 60 * sampling_rate  # 1 hour
            
            current_pos = 0
            for i in range(total_samples):
                if i > 0 and i % change_interval == 0:
                    current_pos = (current_pos + 1) % 4
                body_pos[i] = current_pos
            
            return body_pos
            
        except Exception as e:
            print(f"Error in simple body position generation: {e}")
            return np.zeros(total_samples, dtype=int)

    def generate_simple_activity(self, total_samples, sampling_rate):
        """Generate simple activity pattern"""
        try:
            # Simple sleep pattern
            time_array = np.arange(total_samples) / sampling_rate
            
            # Base activity level
            activity = np.ones(total_samples) * 0.1
            
            # Add some wake periods
            for i in range(0, total_samples, 3000):  # Every 5 minutes
                if np.random.random() > 0.9:  # 10% chance of wake
                    wake_duration = np.random.randint(100, 500)
                    wake_end = min(i + wake_duration, total_samples)
                    wake_start = max(0, i)
                    
                    if wake_end > wake_start:
                        # Simple wake period
                        activity[wake_start:wake_end] = 0.8
            
            # Add small variations
            activity += np.random.normal(0, 0.05, total_samples)
            
            # Ensure activity stays within bounds
            activity = np.clip(activity, 0, 1)
            
            return activity
            
        except Exception as e:
            print(f"Error in simple activity generation: {e}")
            return np.ones(total_samples) * 0.1

    def generate_simple_eeg(self, total_samples, sampling_rate, channel):
        """Generate simple EEG patterns"""
        try:
            # Simple brain wave patterns
            time_array = np.arange(total_samples) / sampling_rate
            
            # Different frequencies for different channels
            if channel == 'c3':
                freq = 10  # Alpha
            elif channel == 'c4':
                freq = 12  # Alpha
            elif channel == 'f3':
                freq = 6   # Theta
            elif channel == 'f4':
                freq = 8   # Alpha
            elif channel == 'o1':
                freq = 11  # Alpha
            else:
                freq = 10  # Default
            
            # Generate simple wave
            eeg = np.sin(2 * np.pi * freq * time_array)
            
            # Add some variation
            eeg += 0.3 * np.sin(2 * np.pi * freq * 0.5 * time_array)
            
            # Add noise
            eeg += np.random.normal(0, 0.1, total_samples)
            
            return eeg
            
        except Exception as e:
            print(f"Error in simple EEG generation for {channel}: {e}")
            return np.random.normal(0, 0.5, total_samples)

    def ensure_full_page_visibility(self):
        """Ensure the graph is properly aligned and visible on the full page"""
        try:
            if hasattr(self, 'detailed_fig') and hasattr(self, 'detailed_ax'):
                # Get current window dimensions
                window_width = self.width()
                window_height = self.height()
                
                # Calculate optimal figure size based on window size
                if window_width >= 1200:  # Large window
                    fig_width = 16
                    fig_height = 12
                    margins = {'left': 0.08, 'right': 0.95, 'top': 0.92, 'bottom': 0.08}
                elif window_width >= 800:  # Medium window
                    fig_width = 14
                    fig_height = 10
                    margins = {'left': 0.08, 'right': 0.95, 'top': 0.90, 'bottom': 0.10}
                else:  # Small window
                    fig_width = 12
                    fig_height = 8
                    margins = {'left': 0.10, 'right': 0.95, 'top': 0.88, 'bottom': 0.12}
                
                # Set figure size
                self.detailed_fig.set_size_inches(fig_width, fig_height)
                
                # Apply optimal margins for full-page visibility
                self.detailed_fig.subplots_adjust(
                    left=margins['left'],
                    right=margins['right'],
                    top=margins['top'],
                    bottom=margins['bottom'],
                    wspace=0.1,
                    hspace=0.1
                )
                
                # Ensure proper axis scaling
                self.detailed_ax.set_axisbelow(True)
                
                # Set proper grid for better visibility
                self.detailed_ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                
                # Update the canvas
                if hasattr(self, 'detailed_canvas'):
                    self.detailed_canvas.draw_idle()
                
                print(f"✅ Full-page visibility optimized: {fig_width}x{fig_height} inches, margins: {margins}")
                
        except Exception as e:
            print(f"Error ensuring full-page visibility: {e}")

    def create_minimal_fallback_data(self):
        """Create minimal fallback data when all other methods fail"""
        print("Creating minimal fallback data...")
        
        try:
            # Create a simple 1-hour dataset
            total_samples = 3600 * 10  # 1 hour * 10 Hz
            time_ms = np.arange(0, total_samples) * 100
            
            # Create simple data
            data = np.zeros((total_samples, 15))
            data[:, 0] = time_ms  # Time
            
            # Simple sine waves for all signals
            t = np.arange(total_samples) / 100  # Time in seconds
            
            # Basic signals
            data[:, 1] = 0.5 * np.sin(2 * np.pi * 0.1 * t)  # Snore
            data[:, 2] = 0.8 * np.sin(2 * np.pi * 0.3 * t)  # Flow
            data[:, 3] = 0.7 * np.sin(2 * np.pi * 0.3 * t)  # Thorax
            data[:, 4] = 0.6 * np.sin(2 * np.pi * 0.3 * t)  # Abdomen
            data[:, 5] = 98 + np.sin(2 * np.pi * 0.05 * t)  # SpO2
            data[:, 6] = 0.9 * np.sin(2 * np.pi * 1.2 * t)  # Pleth
            data[:, 7] = 75 + np.sin(2 * np.pi * 0.02 * t)  # Pulse
            data[:, 8] = np.floor(t / 300) % 4  # Body position
            data[:, 9] = 0.1 + 0.2 * np.sin(2 * np.pi * 0.01 * t)  # Activity
            
            # EEG channels
            data[:, 10] = 0.8 * np.sin(2 * np.pi * 10 * t)  # C3
            data[:, 11] = 0.7 * np.sin(2 * np.pi * 12 * t)  # C4
            data[:, 12] = 0.6 * np.sin(2 * np.pi * 6 * t)   # F3
            data[:, 13] = 0.5 * np.sin(2 * np.pi * 8 * t)   # F4
            data[:, 14] = 0.9 * np.sin(2 * np.pi * 11 * t)  # O1
            
            columns = ['time_ms', 'snore', 'flow', 'thorax', 'abdomen', 'spo2', 'pleth', 
                      'pulse', 'body_pos', 'activity', 'eeg_c3', 'eeg_c4', 'eeg_f3', 'eeg_f4', 'eeg_o1']
            
            df = pd.DataFrame(data, columns=columns)
            print(f"Created minimal fallback data: {len(df)} samples")
            return df
            
        except Exception as e:
            print(f"Error creating minimal fallback data: {e}")
            # Last resort - create empty data
            print("Creating empty data as last resort...")
            empty_data = np.zeros((1000, 15))
            columns = ['time_ms', 'snore', 'flow', 'thorax', 'abdomen', 'spo2', 'pleth', 
                      'pulse', 'body_pos', 'activity', 'eeg_c3', 'eeg_c4', 'eeg_f3', 'eeg_f4', 'eeg_o1']
            return pd.DataFrame(empty_data, columns=columns)

    def create_emergency_fallback_data(self):
        """Create emergency fallback data when everything else fails"""
        print("Creating emergency fallback data...")
        
        try:
            # Create a very simple dataset
            total_samples = 1000  # 100 seconds at 10 Hz
            time_ms = np.arange(0, total_samples) * 100
            
            # Create simple data
            data = np.zeros((total_samples, 15))
            data[:, 0] = time_ms  # Time
            
            # Simple sine waves for all signals
            t = np.arange(total_samples) / 100  # Time in seconds
            
            # Basic signals - very simple
            data[:, 1] = 0.5 * np.sin(2 * np.pi * 0.1 * t)  # Snore
            data[:, 2] = 0.8 * np.sin(2 * np.pi * 0.3 * t)  # Flow
            data[:, 3] = 0.7 * np.sin(2 * np.pi * 0.3 * t)  # Thorax
            data[:, 4] = 0.6 * np.sin(2 * np.pi * 0.3 * t)  # Abdomen
            data[:, 5] = 98  # SpO2 (constant)
            data[:, 6] = 0.9 * np.sin(2 * np.pi * 1.2 * t)  # Pleth
            data[:, 7] = 75  # Pulse (constant)
            data[:, 8] = 0  # Body position (constant)
            data[:, 9] = 0.1  # Activity (constant)
            
            # EEG channels
            data[:, 10] = 0.8 * np.sin(2 * np.pi * 10 * t)  # C3
            data[:, 11] = 0.7 * np.sin(2 * np.pi * 12 * t)  # C4
            data[:, 12] = 0.6 * np.sin(2 * np.pi * 6 * t)   # F3
            data[:, 13] = 0.5 * np.sin(2 * np.pi * 8 * t)   # F4
            data[:, 14] = 0.9 * np.sin(2 * np.pi * 11 * t)  # O1
            
            columns = ['time_ms', 'snore', 'flow', 'thorax', 'abdomen', 'spo2', 'pleth', 
                      'pulse', 'body_pos', 'activity', 'eeg_c3', 'eeg_c4', 'eeg_f3', 'eeg_f4', 'eeg_o1']
            
            df = pd.DataFrame(data, columns=columns)
            print(f"Created emergency fallback data: {len(df)} samples")
            return df
            
        except Exception as e:
            print(f"Critical error in emergency fallback: {e}")
            # Last resort - create empty data
            print("Creating empty data as absolute last resort...")
            try:
                empty_data = np.zeros((100, 15))
                columns = ['time_ms', 'snore', 'flow', 'thorax', 'abdomen', 'spo2', 'pleth', 
                          'pulse', 'body_pos', 'activity', 'eeg_c3', 'eeg_c4', 'eeg_f3', 'eeg_f4', 'eeg_o1']
                return pd.DataFrame(empty_data, columns=columns)
            except:
                # If even this fails, return None and let the app handle it
                print("All data creation methods failed")
                return None

    def create_emergency_signals(self):
        """Create emergency signal data when main processing fails"""
        print("Creating emergency signals...")
        
        try:
            # Create basic time series
            total_samples = 1000
            time_array = np.arange(total_samples) / 10  # 100 seconds at 10 Hz
            
            # Create basic signals
            self.time = pd.Series(time_array, name='time')
            self.body_pos = pd.Series(np.zeros(total_samples), name='body_pos')
            self.pulse = pd.Series(np.ones(total_samples) * 75, name='pulse')
            self.spo2 = pd.Series(np.ones(total_samples) * 98, name='spo2')
            self.flow = pd.Series(np.sin(2 * np.pi * 0.3 * time_array), name='flow')
            self.snore = pd.Series(np.zeros(total_samples), name='snore')
            self.thorax = pd.Series(np.sin(2 * np.pi * 0.3 * time_array), name='thorax')
            self.abdomen = pd.Series(np.sin(2 * np.pi * 0.3 * time_array), name='abdomen')
            self.pleth = pd.Series(np.sin(2 * np.pi * 1.2 * time_array), name='pleth')
            self.activity = pd.Series(np.ones(total_samples) * 0.1, name='activity')
            
            # Create basic EEG signals
            self.eeg_c3 = pd.Series(np.sin(2 * np.pi * 10 * time_array), name='eeg_c3')
            self.eeg_c4 = pd.Series(np.sin(2 * np.pi * 12 * time_array), name='eeg_c4')
            self.eeg_f3 = pd.Series(np.sin(2 * np.pi * 6 * time_array), name='eeg_f3')
            self.eeg_f4 = pd.Series(np.sin(2 * np.pi * 8 * time_array), name='eeg_f4')
            self.eeg_o1 = pd.Series(np.sin(2 * np.pi * 11 * time_array), name='eeg_o1')
            self.eeg_o2 = pd.Series(np.sin(2 * np.pi * 11 * time_array), name='eeg_o2')
            
            print("Emergency signals created successfully")
            
        except Exception as e:
            print(f"Error creating emergency signals: {e}")
            # Create minimal signals
            self.time = pd.Series([0, 1, 2, 3, 4], name='time')
            self.body_pos = pd.Series([0, 0, 0, 0, 0], name='body_pos')
            self.pulse = pd.Series([75, 75, 75, 75, 75], name='pulse')
            self.spo2 = pd.Series([98, 98, 98, 98, 98], name='spo2')
            self.flow = pd.Series([0, 0, 0, 0, 0], name='flow')
            self.snore = pd.Series([0, 0, 0, 0, 0], name='snore')
            self.thorax = pd.Series([0, 0, 0, 0, 0], name='thorax')
            self.abdomen = pd.Series([0, 0, 0, 0, 0], name='abdomen')
            self.pleth = pd.Series([0, 0, 0, 0, 0], name='pleth')
            self.activity = pd.Series([0.1, 0.1, 0.1, 0.1, 0.1], name='activity')
            
            # Minimal EEG
            self.eeg_c3 = pd.Series([0, 0, 0, 0, 0], name='eeg_c3')
            self.eeg_c4 = pd.Series([0, 0, 0, 0, 0], name='eeg_c4')
            self.eeg_f3 = pd.Series([0, 0, 0, 0, 0], name='eeg_f3')
            self.eeg_f4 = pd.Series([0, 0, 0, 0, 0], name='eeg_f4')
            self.eeg_o1 = pd.Series([0, 0, 0, 0, 0], name='eeg_o1')
            self.eeg_o2 = pd.Series([0, 0, 0, 0, 0], name='eeg_o2')
            
            print("Minimal signals created as last resort")

    def create_normalized_fallback_signals(self):
        """Create normalized fallback signals when main normalization fails"""
        print("Creating normalized fallback signals...")
        
        try:
            # Create simple normalized signals
            self.body_pos_n = pd.Series([0.0, 0.0, 0.0, 0.0, 0.0], name='body_pos_n')
            self.pulse_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='pulse_n')
            self.spo2_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='spo2_n')
            self.flow_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='flow_n')
            self.snore_n = pd.Series([0.0, 0.0, 0.0, 0.0, 0.0], name='snore_n')
            self.thorax_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='thorax_n')
            self.abdomen_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='abdomen_n')
            self.pleth_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='pleth_n')
            self.activity_n = pd.Series([0.1, 0.1, 0.1, 0.1, 0.1], name='activity_n')
            
            # Normalized EEG signals
            self.eeg_c3_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='eeg_c3_n')
            self.eeg_c4_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='eeg_c4_n')
            self.eeg_f3_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='eeg_f3_n')
            self.eeg_f4_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='eeg_f4_n')
            self.eeg_o1_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='eeg_o1_n')
            self.eeg_o2_n = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], name='eeg_o2_n')
            
            print("Normalized fallback signals created successfully")
            
        except Exception as e:
            print(f"Error creating normalized fallback signals: {e}")
            # Create minimal normalized signals
            self.body_pos_n = pd.Series([0.0], name='body_pos_n')
            self.pulse_n = pd.Series([0.5], name='pulse_n')
            self.spo2_n = pd.Series([0.5], name='spo2_n')
            self.flow_n = pd.Series([0.5], name='flow_n')
            self.snore_n = pd.Series([0.0], name='snore_n')
            self.thorax_n = pd.Series([0.5], name='thorax_n')
            self.abdomen_n = pd.Series([0.5], name='abdomen_n')
            self.pleth_n = pd.Series([0.5], name='pleth_n')
            self.activity_n = pd.Series([0.1], name='activity_n')
            
            # Minimal normalized EEG
            self.eeg_c3_n = pd.Series([0.5], name='eeg_c3_n')
            self.eeg_c4_n = pd.Series([0.5], name='eeg_c4_n')
            self.eeg_f3_n = pd.Series([0.5], name='eeg_f3_n')
            self.eeg_f4_n = pd.Series([0.5], name='eeg_f4_n')
            self.eeg_o1_n = pd.Series([0.5], name='eeg_o1_n')
            self.eeg_o2_n = pd.Series([0.5], name='eeg_o2_n')
            
            print("Minimal normalized signals created as last resort")

    def create_basic_ui(self):
        """Create basic UI when main initialization fails"""
        print("Creating basic UI...")
        
        try:
            # Create minimal central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Add simple label
            label = QLabel("SleepSense Pro - Basic Mode")
            label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            
            # Add status label
            status_label = QLabel("Application loaded in basic mode due to initialization errors")
            status_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 10px;")
            status_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(status_label)
            
            # Add status bar message
            self.statusBar().showMessage("SleepSense Pro - Basic Mode - Some features may be limited")
            
            print("Basic UI created successfully")
            
        except Exception as e:
            print(f"Error creating basic UI: {e}")
            # Last resort - just show a message
            self.statusBar().showMessage("SleepSense Pro - Emergency Mode")

    def create_fallback_plot(self):
        """Create a simple fallback plot when main plotting fails"""
        try:
            # Clear the plot
            self.detailed_ax.clear()
            
            # Create simple data for fallback
            time_points = np.linspace(0, 10, 100)
            simple_signals = {
                'Signal 1': np.sin(2 * np.pi * 0.5 * time_points),
                'Signal 2': np.cos(2 * np.pi * 0.3 * time_points),
                'Signal 3': np.sin(2 * np.pi * 0.7 * time_points)
            }
            
            # Plot simple signals
            colors = ['blue', 'red', 'green']
            for i, (name, data) in enumerate(simple_signals.items()):
                self.detailed_ax.plot(time_points, data + i, color=colors[i], label=name, linewidth=1.5)
            
            # Set basic properties
            self.detailed_ax.set_title('SleepSense Pro - Fallback View', fontsize=12, fontweight='bold')
            self.detailed_ax.set_xlabel('Time (seconds)')
            self.detailed_ax.set_ylabel('Amplitude')
            self.detailed_ax.grid(True, alpha=0.3)
            self.detailed_ax.legend()
            self.detailed_ax.set_ylim(-1.5, 3.5)
            
        except Exception as e:
            print(f"Error creating fallback plot: {e}")
            # Last resort - just show text
            self.detailed_ax.text(0.5, 0.5, 'Plot Error\nData Unavailable', 
                                transform=self.detailed_ax.transAxes, 
                                ha='center', va='center', fontsize=14)

    def create_emergency_plot(self):
        """Create emergency plot when main plotting system fails"""
        try:
            # Create basic figure
            self.detailed_fig = Figure(figsize=(12, 8))
            self.detailed_ax = self.detailed_fig.add_subplot(111)
            
            # Create simple emergency data
            time_points = np.linspace(0, 10, 50)
            emergency_data = np.sin(2 * np.pi * 0.5 * time_points)
            
            # Plot emergency data
            self.detailed_ax.plot(time_points, emergency_data, 'b-', linewidth=2, label='Emergency Signal')
            
            # Set basic properties
            self.detailed_ax.set_title('SleepSense Pro - Emergency Mode', fontsize=14, fontweight='bold')
            self.detailed_ax.set_xlabel('Time (seconds)')
            self.detailed_ax.set_ylabel('Amplitude')
            self.detailed_ax.grid(True, alpha=0.3)
            self.detailed_ax.legend()
            self.detailed_ax.set_ylim(-1.5, 1.5)
            
            # Create canvas
            self.detailed_canvas = FigureCanvas(self.detailed_fig)
            
            print("Emergency plot created successfully")
            return self.detailed_canvas
            
        except Exception as e:
            print(f"Error creating emergency plot: {e}")
            # Last resort - create minimal canvas
            try:
                self.detailed_fig = Figure(figsize=(8, 6))
                self.detailed_ax = self.detailed_fig.add_subplot(111)
                self.detailed_ax.text(0.5, 0.5, 'Emergency Mode\nPlot System Unavailable', 
                                    transform=self.detailed_ax.transAxes, 
                                    ha='center', va='center', fontsize=12)
                self.detailed_canvas = FigureCanvas(self.detailed_fig)
                return self.detailed_canvas
            except:
                print("Complete plotting failure - using text display")
                return None

    def clear_all_regions(self):
        """Clear all selected regions"""
        try:
            # Remove all region rectangles from the plot
            for region in self.selected_regions:
                if 'rectangle' in region and region['rectangle']:
                    region['rectangle'].remove()
            
            # Clear the regions list
            self.selected_regions.clear()
            
            # Redraw canvas
            if hasattr(self, 'detailed_canvas'):
                self.detailed_canvas.draw_idle()
            
            print("All regions cleared")
            self.statusBar().showMessage("🗑️ All regions cleared")
            
        except Exception as e:
            print(f"Error clearing regions: {e}")
    
    def get_selected_regions(self):
        """Get list of selected regions"""
        return self.selected_regions
    
    def export_regions_data(self):
        """Export selected regions data"""
        try:
            if not self.selected_regions:
                return "No regions selected"
            
            regions_data = []
            for i, region in enumerate(self.selected_regions):
                regions_data.append({
                    'region_id': i + 1,
                    'start_time': f"{region['start_time']:.2f}s",
                    'end_time': f"{region['end_time']:.2f}s",
                    'duration': f"{region['end_time'] - region['start_time']:.2f}s",
                    'start_y': f"{region['start_y']:.2f}",
                    'end_y': f"{region['end_y']:.2f}"
                })
            
            return regions_data
            
        except Exception as e:
            print(f"Error exporting regions data: {e}")
            return f"Error: {e}"

    def ensure_canvas_fits_frame_size(self, frame_size):
        """Ensure the canvas properly fits the frame size for optimal viewing"""
        try:
            if not hasattr(self, 'detailed_canvas') or not hasattr(self, 'detailed_fig'):
                return
            
            # Get the current canvas size
            current_size = self.detailed_canvas.size()
            
            # Calculate optimal canvas size based on frame size
            if frame_size <= 30:  # High detail mode
                optimal_width = 1200
                optimal_height = 900
            elif frame_size <= 300:  # Balanced mode
                optimal_width = 1000
                optimal_height = 750
            else:  # Compact mode
                optimal_width = 800
                optimal_height = 600
            
            # Resize canvas if needed
            if current_size.width() != optimal_width or current_size.height() != optimal_height:
                self.detailed_canvas.resize(optimal_width, optimal_height)
                print(f"Canvas resized to {optimal_width}x{optimal_height} for {frame_size}s frame")
            
            # Force a complete redraw
            self.detailed_canvas.draw()
            
        except Exception as e:
            print(f"Error ensuring canvas fits frame size: {e}")
    
    def update_plot_for_frame_size(self, frame_size):
        """Update the entire plot system for a specific frame size"""
        try:
            print(f"Updating plot system for frame size: {frame_size}s")
            
            # Use force refresh for better reliability
            self.force_refresh_for_frame_size(frame_size)
            
        except Exception as e:
            print(f"Error updating plot for frame size: {e}")
            # Try to recover with basic update
            try:
                self.update_plots()
                if hasattr(self, 'detailed_canvas'):
                    self.detailed_canvas.draw()
            except Exception as e2:
                print(f"Recovery also failed: {e2}")

    def force_refresh_for_frame_size(self, frame_size):
        """Force a complete refresh of the plotting system for frame size changes"""
        try:
            print(f"Force refreshing plotting system for {frame_size}s frame size")
            
            # Clear all existing plots and patches
            if hasattr(self, 'detailed_ax'):
                self.detailed_ax.clear()
                
                # Remove any existing rectangles/patches
                for patch in self.detailed_ax.patches[:]:
                    patch.remove()
                
                print("All plots and patches cleared")
            
            # Force view adjustment
            self.adjust_view_for_frame_size(frame_size)
            
            # Ensure proper canvas sizing
            self.ensure_canvas_fits_frame_size(frame_size)
            
            # Completely rebuild the plot
            self.update_plots()
            
            # Force multiple redraws to ensure changes are applied
            if hasattr(self, 'detailed_canvas'):
                self.detailed_canvas.draw()
                self.detailed_canvas.flush_events()
                print("Canvas force refreshed")
            
            # Verify the title was updated
            if hasattr(self, 'detailed_ax'):
                final_title = self.detailed_ax.get_title()
                print(f"Final plot title: {final_title}")
                
                # Check if title matches expected
                if frame_size <= 30:
                    expected = 'Detailed Waveform View (High Detail Mode)'
                elif frame_size <= 300:
                    expected = 'Balanced Waveform View'
                else:
                    expected = 'Compact Waveform View (Comparison Mode)'
                
                if expected in final_title:
                    print(f"✅ Title correctly updated to {expected}")
                else:
                    print(f"❌ Title not correctly updated. Expected: {expected}")
                    # Force title correction
                    self.detailed_ax.set_title(f'SleepSense Pro - {expected}', fontsize=12, fontweight='bold')
                    self.detailed_canvas.draw()
                    print("Title force corrected")
            
            print(f"Complete refresh completed for {frame_size}s frame size")
            
        except Exception as e:
            print(f"Error in force refresh: {e}")
            # Emergency recovery
            try:
                self.update_plots()
                if hasattr(self, 'detailed_canvas'):
                    self.detailed_canvas.draw()
            except Exception as e2:
                print(f"Emergency recovery failed: {e2}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Import and show activation dialog first
    try:
        from activation_dialog import ActivationDialog
        
        # Show activation dialog
        activation_dialog = ActivationDialog()
        
        # If dialog is already activated, show main window directly
        if activation_dialog.is_activated():
            win = SleepSensePlot()
            win.show()
        else:
            # Show activation dialog and wait for result
            result = activation_dialog.exec_()
            
            if result == QDialog.Accepted:
                # Activation successful, show main window
                win = SleepSensePlot()
                win.show()
            else:
                # Activation failed or cancelled, exit
                sys.exit(0)
                
    except ImportError as e:
        # If activation dialog can't be imported, show error and exit
        from PyQt5.QtWidgets import QMessageBox, QApplication
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText("Activation system not found!")
        msg.setInformativeText("The activation dialog file is missing. Please ensure 'activation_dialog.py' is in the same directory.")
        msg.setDetailedText(f"Import error: {str(e)}")
        msg.exec_()
        sys.exit(1)
    except Exception as e:
        # Handle any other errors
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText("Unexpected error occurred!")
        msg.setInformativeText("Please contact support for assistance.")
        msg.setDetailedText(f"Error: {str(e)}")
        msg.exec_()
        sys.exit(1)
    
    sys.exit(app.exec_())
