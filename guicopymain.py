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
    QInputDialog, QDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
            self.data = self.data_manager.load_data(file_path)
        except Exception as e:
            print(f"Failed to load data: {e}")
            # Fallback to original method
            self.data = pd.read_csv(file_path, header=None)
        
        # Ensure data is a pandas DataFrame
        if not isinstance(self.data, pd.DataFrame):
            print("Converting data to pandas DataFrame...")
            if isinstance(self.data, np.ndarray):
                self.data = pd.DataFrame(self.data)
            else:
                # If it's still not a DataFrame, create one from scratch
                self.data = pd.read_csv(file_path, header=None)
        
        # Debug: Print data type and shape
        print(f"Data type: {type(self.data)}")
        print(f"Data shape: {self.data.shape if hasattr(self.data, 'shape') else 'No shape'}")
        print(f"Data columns: {len(self.data.columns) if hasattr(self.data, 'columns') else 'No columns'}")
        
        # Optimize data loading for large datasets
        if len(self.data) > 50000:  # If dataset is large
            print("Large dataset detected - applying performance optimizations...")
            # Use chunked processing for large datasets
            self.chunk_size = 10000  # Process in 10k chunks
        else:
            self.chunk_size = len(self.data)
        
        # Detect data format and handle both current and future formats
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
            
        elif num_columns >= 12:  # Future format
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
            self.activity = pd.Series(self.data[9].astype(int), name='activity')  # 0=sleeping, 1=awake
            
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

        # Normalize signals
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

        # Window settings
        self.start_time = self.time.iloc[0]
        self.end_time = self.time.iloc[-1]
        self.window_size = 10.0  # initial window size in seconds
        self.min_window_size = 1.0
        self.max_window_size = (self.end_time - self.start_time) / 2

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
        self.spo2_checkbox = QCheckBox()
        self.pulse_checkbox = QCheckBox()
        self.flow_checkbox = QCheckBox()
        self.position_checkbox = QCheckBox()
        self.activity_checkbox = QCheckBox()
        self.snore_checkbox = QCheckBox()
        self.thorax_checkbox = QCheckBox()
        self.abdomen_checkbox = QCheckBox()
        self.pleth_checkbox = QCheckBox()

        self.initUI()
        
        # Show welcome message with SleepSense Pro branding
        self.show_welcome_message()

    def normalize(self, series):
        return (series - series.min()) / (series.max() - series.min())
    
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
        self.statusBar().showMessage("SleepSense Pro Ready - Loaded sleep data successfully | 📊 Analysis Mode: Full Page | Press Ctrl+M to maximize plots")

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
        
        about_action = QAction('About', self)
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
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Time Navigation Controls at the top
        navigation_group = QGroupBox("⏱️ Time Navigation - SleepSense Pro")
        navigation_group.setStyleSheet("""
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
        navigation_layout = QVBoxLayout(navigation_group)
        navigation_layout.setContentsMargins(8, 8, 8, 8)  # Reduce margins
        navigation_layout.setSpacing(4)  # Reduce spacing between elements
        

        
        # Time display
        self.time_display = QLabel("00:00:00 - 00:00:10")
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1; 
                padding: 3px 8px; 
                border-radius: 3px;
                font-size: 10px;
                font-weight: 500;
                color: #495057;
                border: 1px solid #bdc3c7;
            }
        """)
        navigation_layout.addWidget(self.time_display)
        
        # Frame size buttons
        frame_size_label = QLabel("Frame Size:")
        frame_size_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                font-weight: 500;
                color: #495057;
                margin-top: 8px;
                margin-bottom: 4px;
            }
        """)
        navigation_layout.addWidget(frame_size_label)
        
        # Create frame size buttons layout
        frame_buttons_layout = QHBoxLayout()
        frame_buttons_layout.setContentsMargins(0, 0, 0, 0)
        frame_buttons_layout.setSpacing(4)
        
        # Frame size options in seconds
        frame_sizes = [
            ("5s", 5),
            ("10s", 10),
            ("30s", 30),
            ("1m", 60),
            ("2m", 120),
            ("5m", 300),
            ("10m", 600),
            ("30m", 1800)
        ]
        
        # Create frame size buttons
        self.frame_buttons = {}
        for label, seconds in frame_sizes:
            btn = QPushButton(label)
            btn.setFixedSize(40, 28)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: 2px solid #495057;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 9px;
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
            
            # Connect button to frame size change
            btn.clicked.connect(lambda checked, sec=seconds: self.set_frame_size_from_button(sec))
            
            # Add tooltip
            btn.setToolTip(f"Set frame size to {label}")
            
            # Set 10s as default selected
            if seconds == 10:
                btn.setChecked(True)
            
            frame_buttons_layout.addWidget(btn)
            self.frame_buttons[seconds] = btn
        
        navigation_layout.addLayout(frame_buttons_layout)
        
        right_layout.addWidget(navigation_group)
        
        # Create matplotlib figure for detailed view - full page analysis
        self.detailed_fig = Figure(figsize=(16, 12))  # Increased size for better analysis
        self.detailed_canvas = FigureCanvas(self.detailed_fig)
        
        # Add tooltip to explain region selection
        self.detailed_canvas.setToolTip(
            "🖱️  Click and drag to select regions (like turning lights on/off)\n"
            "💡 Selected regions are highlighted in blue\n"
            "⌨️  Press Ctrl+R to clear all regions\n"
            "📋 Use Data Security menu to manage selections"
        )
        
        right_layout.addWidget(self.detailed_canvas)
        
        # Initialize plots
        self.plot_signals()
        self.update_plot()
        
        # Auto-configure checkboxes based on data availability
        self.configure_signal_checkboxes()
        
        return right_widget

    def plot_signals(self):
        """Initialize plots with performance optimizations"""
        # Configure matplotlib for better performance
        import matplotlib.pyplot as plt
        try:
            plt.style.use('fast')  # Use fast style if available
        except:
            # Fallback to default style if 'fast' is not available
            pass
        
        # Detailed plot
        self.detailed_ax = self.detailed_fig.add_subplot(111)
        self.detailed_fig.subplots_adjust(bottom=0.1, top=0.9)
        
        # Performance optimizations
        self.detailed_ax.set_facecolor('#f8f9fa')
        
        # Initialize region selection variables
        self.selected_regions = []  # List to store selected regions
        self.is_selecting = False   # Flag to track selection state
        self.selection_start = None # Start point of selection
        self.selection_rect = None  # Rectangle patch for selection
        
        # Connect mouse events for region selection
        self.detailed_canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.detailed_canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.detailed_canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Initialize plot bounds tracking
        self._last_plot_bounds = (0, 0)
        
        self.update_plots()

    def update_plots(self):
        """Optimized plot update with reduced redraws and better performance"""
        # Only update if detailed plot is visible
        if not hasattr(self, 'detailed_ax'):
            return
            
        # Clear plot efficiently
        self.detailed_ax.clear()
        
        # Get current window limits for efficient plotting
        # Use fixed start index from beginning of data
        start_idx = 0
        
        # Calculate actual sampling rate from data
        if len(self.time) > 1:
            sampling_rate = 1.0 / (self.time.iloc[1] - self.time.iloc[0])  # Hz
            window_samples = int(self.window_size * sampling_rate)
        else:
            window_samples = 1000  # Fallback
            
        # Ensure end_idx doesn't exceed data bounds
        end_idx = min(len(self.time), start_idx + window_samples)
        
        # If the window is too small, adjust start_idx
        if end_idx - start_idx < 100:  # Minimum window size
            start_idx = max(0, end_idx - 1000)
        
        # Use only visible data range for better performance
        time_window = self.time.iloc[start_idx:end_idx]
        
        # Plot signals efficiently with reduced data points
        if self.position_checkbox.isChecked():
            self.plot_body_position_simple(self.detailed_ax, self.offsets[0], start_idx, end_idx)
            
        if self.pulse_checkbox.isChecked():
            pulse_window = self.pulse_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, pulse_window + self.offsets[1], color='#FF6B6B', label='Pulse', linewidth=0.6)
            
        if self.spo2_checkbox.isChecked():
            spo2_window = self.spo2_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, spo2_window + self.offsets[2], color='#4ECDC4', label='SpO2', linewidth=0.6)
            
        if self.flow_checkbox.isChecked():
            flow_window = self.flow_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, flow_window + self.offsets[3], color='#45B7D1', label='Airflow', linewidth=0.6)
            
        if self.snore_checkbox.isChecked():
            snore_window = self.snore_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, snore_window + self.offsets[4], color='#96CEB4', label='Snore', linewidth=0.6)
            
        if self.thorax_checkbox.isChecked():
            thorax_window = self.thorax_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, thorax_window + self.offsets[5], color='#FFEAA7', label='Thorax', linewidth=0.6)
            
        if self.abdomen_checkbox.isChecked():
            abdomen_window = self.abdomen_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, abdomen_window + self.offsets[6], color='#DDA0DD', label='Abdomen', linewidth=0.6)
            
        if self.pleth_checkbox.isChecked():
            pleth_window = self.pleth_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, pleth_window + self.offsets[7], color='#F8BBD9', label='Pleth', linewidth=0.6)
            
        if self.activity_checkbox.isChecked():
            # Simplified activity display for better performance
            self.plot_activity_simple(self.detailed_ax, self.offsets[8], start_idx, end_idx)
        
        # Plot EEG signals if checked - using bright neon colors for dark mode visibility
        if hasattr(self, 'eeg_c3_checkbox') and self.eeg_c3_checkbox.isChecked():
            eeg_c3_window = self.eeg_c3_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, eeg_c3_window + 10.8, color='#00FFFF', label='EEG C3', linewidth=0.6)
            
        if hasattr(self, 'eeg_c4_checkbox') and self.eeg_c4_checkbox.isChecked():
            eeg_c4_window = self.eeg_c4_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, eeg_c4_window + 12.0, color='#FF00FF', label='EEG C4', linewidth=0.6)
            
        if hasattr(self, 'eeg_f3_checkbox') and self.eeg_f3_checkbox.isChecked():
            eeg_f3_window = self.eeg_f3_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, eeg_f3_window + 13.2, color='#FFFF00', label='EEG F3', linewidth=0.6)
            
        if hasattr(self, 'eeg_f4_checkbox') and self.eeg_f4_checkbox.isChecked():
            eeg_f4_window = self.eeg_f4_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, eeg_f4_window + 14.4, color='#00FF00', label='EEG F4', linewidth=0.6)
            
        if hasattr(self, 'eeg_o1_checkbox') and self.eeg_o1_checkbox.isChecked():
            eeg_o1_window = self.eeg_o1_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, eeg_o1_window + 15.6, color='#FFA500', label='EEG O1', linewidth=0.6)
            
        if hasattr(self, 'eeg_c4_checkbox') and self.eeg_o2_checkbox.isChecked():
            eeg_o2_window = self.eeg_o2_n.iloc[start_idx:end_idx]
            self.detailed_ax.plot(time_window, eeg_o2_window + 16.8, color='#FF1493', label='EEG O2', linewidth=0.6)

        # Set plot properties
        self.detailed_ax.set_ylim(-0.5, max(self.offsets) + 1)
        self.detailed_ax.grid(True, alpha=0.3)
        self.detailed_ax.legend(loc='upper right')
        
        # Set specific properties for the plot
        self.detailed_ax.set_title('SleepSense Pro - Detailed Waveform View', fontsize=12, fontweight='bold')
        
        # Set x-axis limits for current window
        start_time = self.time.iloc[start_idx]
        end_time = self.time.iloc[end_idx-1] if end_idx > start_idx else start_time + self.window_size
        self.detailed_ax.set_xlim(start_time, end_time)

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
        # Use fixed time window starting from beginning
        start = self.start_time
        end = start + self.window_size
        
        # Update time display with better formatting
        start_str = f"{int(start//60):02d}:{int(start%60):02d}:{int((start%1)*100):02d}"
        end_str = f"{int(end//60):02d}:{int(end%60):02d}:{int((end%1)*100):02d}"
        
        # Add frame size information to the display
        frame_info = f"Frame: {self.window_size}s"
        self.time_display.setText(f"{start_str} - {end_str} | {frame_info}")
        
        # Only redraw if plot has changed significantly
        if not hasattr(self, '_last_plot_bounds') or abs(self._last_plot_bounds[0] - start) > 0.1:
            self._last_plot_bounds = (start, end)
            # Update plot with new data
            self.update_plots()
            
            # Use draw_idle for better performance
            self.detailed_canvas.draw_idle()

    def change_window_size(self, size):
        """Change the time window size and update all related components"""
        # Validate and set the new window size
        new_size = float(size)
        self.window_size = max(self.min_window_size, min(new_size, self.max_window_size))
        
        # Debug information
        print(f"Changing window size to: {size} seconds")
        print(f"Final window size: {self.window_size} seconds")
        print(f"Time range: {self.start_time:.1f}s to {self.start_time + self.window_size:.1f}s")
        
        # Update the plot to reflect the new window size
        self.update_plot()
        
        # Update frame button states to reflect the new size
        if hasattr(self, 'frame_buttons'):
            self.update_frame_button_states(int(self.window_size))
    
    def set_frame_size_from_button(self, seconds):
        """Set frame size from toolbar button and update button states"""
        # Update window size
        self.change_window_size(seconds)
        
        # Update button states - uncheck all, check the selected one
        for btn_seconds, btn in self.frame_buttons.items():
            btn.setChecked(btn_seconds == seconds)
        
        # Force immediate update of time display and plot
        self.update_plot()
        
        # Update status bar with more detailed information
        if seconds < 60:
            time_str = f"{seconds} seconds"
        elif seconds < 3600:
            time_str = f"{seconds//60} minute{'s' if seconds//60 != 1 else ''}"
        else:
            time_str = f"{seconds//3600} hour{'s' if seconds//3600 != 1 else ''}"
        
        self.statusBar().showMessage(f"✅ Frame size changed to {time_str} - Time window updated")
    
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
                
                # Redraw canvas
                self.detailed_canvas.draw_idle()
            except:
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
        """Automatically configure checkboxes based on data availability"""
        num_columns = len(self.data.columns)
        
        # Ensure all signals are checked by default for better analysis
        self.spo2_checkbox.setChecked(True)
        self.pulse_checkbox.setChecked(True)
        self.flow_checkbox.setChecked(True)
        self.position_checkbox.setChecked(True)
        self.activity_checkbox.setChecked(True)
        self.snore_checkbox.setChecked(True)
        self.thorax_checkbox.setChecked(True)
        self.abdomen_checkbox.setChecked(True)
        self.pleth_checkbox.setChecked(True)
        
        # Check EEG signals by default
        if hasattr(self, 'eeg_c3_checkbox'):
            self.eeg_c3_checkbox.setChecked(True)
            self.eeg_c4_checkbox.setChecked(True)
            self.eeg_f3_checkbox.setChecked(True)
            self.eeg_f4_checkbox.setChecked(True)
            self.eeg_o1_checkbox.setChecked(True)
            self.eeg_o2_checkbox.setChecked(True)
        
        if num_columns == 10:  # Current format
            # Keep all signals enabled to show generated waves
            self.snore_checkbox.setEnabled(True)
            self.thorax_checkbox.setEnabled(True)
            self.abdomen_checkbox.setEnabled(True)
            self.pleth_checkbox.setEnabled(True)
            

            
            # Show status message
            self.statusBar().showMessage("Current data format detected - All waves plotted for better analysis")
            
        elif num_columns >= 12:  # Future format
            # Enable all signals
            self.snore_checkbox.setEnabled(True)
            self.thorax_checkbox.setEnabled(True)
            self.abdomen_checkbox.setEnabled(True)
            self.pleth_checkbox.setEnabled(True)
            

            
            # Auto-check future signals if they have real data
            if np.any(self.snore != 0):
                self.snore_checkbox.setChecked(True)
            if np.any(self.thorax != 0):
                self.thorax_checkbox.setChecked(True)
            if np.any(self.abdomen != 0):
                self.abdomen_checkbox.setChecked(True)
            if np.any(self.pleth != 0):
                self.pleth_checkbox.setChecked(True)
            
            self.statusBar().showMessage("Future data format detected - All signals enabled and plotted")

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
        if event.inaxes != self.detailed_ax:
            return
        
        if event.button == 1:  # Left mouse button
            self.is_selecting = True
            self.selection_start = event.xdata
            self.statusBar().showMessage("🖱️  Click and drag to select region (release to finish)")
    
    def on_mouse_move(self, event):
        """Handle mouse movement during region selection"""
        if not self.is_selecting or event.inaxes != self.detailed_ax:
            return
        
        if self.selection_start is not None:
            # Remove previous selection rectangle
            if self.selection_rect:
                self.selection_rect.remove()
                self.selection_rect = None
            
            # Create new selection rectangle
            start_x = min(self.selection_start, event.xdata)
            end_x = max(self.selection_start, event.xdata)
            
            # Create rectangle patch - black background for dark mode
            from matplotlib.patches import Rectangle
            self.selection_rect = Rectangle(
                (start_x, self.detailed_ax.get_ylim()[0]), 
                end_x - start_x, 
                self.detailed_ax.get_ylim()[1] - self.detailed_ax.get_ylim()[0],
                alpha=0.8, 
                color='black', 
                edgecolor='white',
                linewidth=2
            )
            self.detailed_ax.add_patch(self.selection_rect)
            self.detailed_canvas.draw_idle()
    
    def on_mouse_release(self, event):
        """Handle mouse release events to finalize region selection"""
        if not self.is_selecting or event.inaxes != self.detailed_ax:
            return
        
        if event.button == 1 and self.selection_start is not None:  # Left mouse button
            self.is_selecting = False
            
            # Get selection boundaries
            start_x = min(self.selection_start, event.xdata)
            end_x = max(self.selection_start, event.xdata)
            
            # Convert time to indices
            start_idx = (np.abs(self.time - start_x)).argmin()
            end_idx = (np.abs(self.time - end_x)).argmin()
            
            # Create region info
            region_info = {
                'start_time': start_x,
                'end_time': end_x,
                'start_idx': start_idx,
                'end_idx': end_idx,
                'duration': end_x - start_x,
                'rectangle': self.selection_rect
            }
            
            # Add to selected regions
            self.selected_regions.append(region_info)
            
            # Change color to indicate selection is complete - keep black background for dark mode
            self.selection_rect.set_facecolor('black')
            self.selection_rect.set_edgecolor('white')
            self.selection_rect.set_alpha(0.9)
            
            # Update status
            duration_str = f"{region_info['duration']:.1f}s"
            start_str = f"{start_x:.1f}s"
            end_str = f"{end_x:.1f}s"
            
            self.statusBar().showMessage(
                f"✅ Region selected: {start_str} to {end_str} ({duration_str}) - "
                f"Total regions: {len(self.selected_regions)}"
            )
            
            # Clear selection variables
            self.selection_start = None
            self.selection_rect = None
            
            # Redraw canvas
            self.detailed_canvas.draw_idle()
            
            # Update title to show new region count
            self.update_detailed_view_title()
    
    def clear_selected_regions(self):
        """Clear all selected regions"""
        for region in self.selected_regions:
            if region['rectangle']:
                region['rectangle'].remove()
        self.selected_regions.clear()
        self.detailed_canvas.draw_idle()
        self.statusBar().showMessage("🗑️  All selected regions cleared")
        
        # Update title to show new region count
        self.update_detailed_view_title()
    
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
