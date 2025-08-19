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
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider,
    QPushButton, QHBoxLayout, QLabel, QMenuBar, QMenu, QAction,
    QFrame, QGridLayout, QGroupBox, QSplitter, QTextEdit,
    QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class SleepSensePlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SleepSense - Professional Sleep Analysis System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set modern style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
            }
            QMenu {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
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
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
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
                margin: -2px 0;
                border-radius: 9px;
            }
        """)

        # Load data (adjust path)
        file_path = "DATA0025.TXT"
        self.data = pd.read_csv(file_path, header=None)
        
        # Detect data format and handle both current and future formats
        num_columns = len(self.data.columns)
        
        if num_columns == 10:  # Current format
            # Current format: time, body_pos, pulse, spo2, ?, ?, ?, flow, ?, ?
            self.time = self.data[0].astype(float) / 1000  # ms to s
            self.body_pos = self.data[1].astype(int)
            self.pulse = self.data[2].astype(float)
            self.spo2 = self.data[3].astype(float)
            self.flow = self.data[7].astype(float)
            
            # Generate realistic mock waveforms for future signals
            self.snore = self.generate_snore_wave(self.time)
            self.thorax = self.generate_thorax_wave(self.time)
            self.abdomen = self.generate_abdomen_wave(self.time)
            self.pleth = self.generate_pleth_wave(self.time)
            self.activity = self.generate_activity_wave(self.time)
            
        elif num_columns >= 12:  # Future format
            # Future format: time, snore, flow, thorax, abdomen, spo2, pleth, pulse, body_pos, activity, ?, ?
            self.time = self.data[0].astype(float) / 1000  # ms to s
            self.snore = self.data[1].astype(float)
            self.flow = self.data[2].astype(float)
            self.thorax = self.data[3].astype(float)
            self.abdomen = self.data[4].astype(float)
            self.spo2 = self.data[5].astype(float)
            self.pleth = self.data[6].astype(float)
            self.pulse = self.data[7].astype(float)
            self.body_pos = self.data[8].astype(int)
            self.activity = self.data[9].astype(int)  # 0=sleeping, 1=awake
            
        else:
            # Fallback for unknown format
            self.time = self.data[0].astype(float) / 1000
            self.body_pos = np.zeros_like(self.time)
            self.pulse = np.zeros_like(self.time)
            self.spo2 = np.zeros_like(self.time)
            self.flow = np.zeros_like(self.time)
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

        # Offsets for all signals (current + future)
        self.offsets = [0, 1.2, 2.4, 3.6, 4.8, 6.0, 7.2, 8.4, 9.6]
        
        # Playback state
        self.is_playing = False
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.auto_advance)
        self.play_speed = 1.0

        self.initUI()

    def normalize(self, series):
        return (series - series.min()) / (series.max() - series.min())
    
    def generate_snore_wave(self, time):
        """Generate realistic snore waveform with random bursts"""
        # Base frequency for snoring (low frequency)
        base_freq = 0.5  # Hz
        snore = np.sin(2 * np.pi * base_freq * time) * 0.3
        
        # Add random snore bursts
        for i in range(0, len(time), 100):  # Every ~100 samples
            if np.random.random() > 0.7:  # 30% chance of snore burst
                burst_start = i
                burst_duration = np.random.randint(50, 200)
                burst_end = min(burst_start + burst_duration, len(time))
                
                # Create burst pattern
                burst_time = time[burst_start:burst_end] - time[burst_start]
                burst_freq = np.random.uniform(0.8, 1.5)  # Random frequency
                burst_amp = np.random.uniform(0.5, 1.0)   # Random amplitude
                
                snore[burst_start:burst_end] += burst_amp * np.sin(2 * np.pi * burst_freq * burst_time)
        
        return snore
    
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
        
        return thorax
    
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
        
        return abdomen
    
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
        
        return pleth
    
    def generate_activity_wave(self, time):
        """Generate realistic activity pattern (sleep/wake cycles)"""
        # Base activity level (mostly sleeping)
        activity = np.zeros_like(time)
        
        # Add random wake periods
        for i in range(0, len(time), 200):  # Check every ~200 samples
            if np.random.random() > 0.85:  # 15% chance of wake period
                wake_start = i
                wake_duration = np.random.randint(100, 500)
                wake_end = min(wake_start + wake_duration, len(time))
                
                # Create wake pattern with gradual transitions
                for j in range(wake_start, wake_end):
                    if j < len(time):
                        # Gradual increase to wake level
                        if j - wake_start < 50:
                            activity[j] = (j - wake_start) / 50.0
                        # Gradual decrease back to sleep
                        elif wake_end - j < 50:
                            activity[j] = (wake_end - j) / 50.0
                        else:
                            activity[j] = 1.0  # Full wake level
        
        # Add small random variations
        activity += 0.05 * np.random.randn(len(time))
        activity = np.clip(activity, 0, 1)  # Keep between 0 and 1
        
        return activity

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
        
        # Set splitter proportions
        splitter.setSizes([300, 1100])
        
        # Status bar
        self.statusBar().showMessage("Ready - Loaded sleep data successfully")

    def createMenuBar(self):
        menubar = self.menuBar()
        
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
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        help_menu.addAction(about_action)

    def createLeftPanel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Patient Information Group
        patient_group = QGroupBox("Patient Information")
        patient_layout = QGridLayout(patient_group)
        
        patient_layout.addWidget(QLabel("Name:"), 0, 0)
        patient_layout.addWidget(QLabel("Rajeev Ranjan"), 0, 1)
        
        patient_layout.addWidget(QLabel("Date:"), 1, 0)
        patient_layout.addWidget(QLabel("07-08-2025"), 1, 1)
        
        patient_layout.addWidget(QLabel("Duration:"), 2, 0)
        duration_label = QLabel("3 min 34 sec")
        duration_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        patient_layout.addWidget(duration_label, 2, 1)
        
        # Data format information
        patient_layout.addWidget(QLabel("Data Format:"), 3, 0)
        self.format_label = QLabel("Current (10 cols)")
        self.format_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        patient_layout.addWidget(self.format_label, 3, 1)
        
        left_layout.addWidget(patient_group)
        
        # Signal Display Controls
        signals_group = QGroupBox("Signal Display")
        signals_layout = QVBoxLayout(signals_group)
        
        self.spo2_checkbox = QCheckBox("SpO2 (Oxygen Saturation)")
        self.spo2_checkbox.setChecked(True)
        signals_layout.addWidget(self.spo2_checkbox)
        
        self.pulse_checkbox = QCheckBox("Pulse (Heart Rate)")
        self.pulse_checkbox.setChecked(True)
        signals_layout.addWidget(self.pulse_checkbox)
        
        self.flow_checkbox = QCheckBox("Airflow")
        self.flow_checkbox.setChecked(True)
        signals_layout.addWidget(self.flow_checkbox)
        
        self.position_checkbox = QCheckBox("Body Position")
        self.position_checkbox.setChecked(True)
        signals_layout.addWidget(self.position_checkbox)
        
        self.activity_checkbox = QCheckBox("Activity")
        self.activity_checkbox.setChecked(True)
        signals_layout.addWidget(self.activity_checkbox)
        
        # Future signals checkboxes
        self.snore_checkbox = QCheckBox("Snore")
        self.snore_checkbox.setChecked(True)  # Enabled to show generated waves
        signals_layout.addWidget(self.snore_checkbox)
        
        self.thorax_checkbox = QCheckBox("Thorax Movement")
        self.thorax_checkbox.setChecked(True)  # Enabled to show generated waves
        signals_layout.addWidget(self.thorax_checkbox)
        
        self.abdomen_checkbox = QCheckBox("Abdomen Movement")
        self.abdomen_checkbox.setChecked(True)  # Enabled to show generated waves
        signals_layout.addWidget(self.abdomen_checkbox)
        
        self.pleth_checkbox = QCheckBox("Plethysmography")
        self.pleth_checkbox.setChecked(True)  # Enabled to show generated waves
        signals_layout.addWidget(self.pleth_checkbox)
        
        left_layout.addWidget(signals_group)
        
        # Time Navigation Controls
        navigation_group = QGroupBox("Time Navigation")
        navigation_layout = QVBoxLayout(navigation_group)
        
        # Time slider
        time_label = QLabel("Time Position:")
        navigation_layout.addWidget(time_label)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int((self.end_time - self.start_time - self.window_size) * 100))
        self.slider.setValue(0)
        self.slider.setTickInterval(100)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.update_plot)
        navigation_layout.addWidget(self.slider)
        
        # Time display
        self.time_display = QLabel("00:00:00 - 00:00:10")
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setStyleSheet("background-color: #ecf0f1; padding: 5px; border-radius: 3px;")
        navigation_layout.addWidget(self.time_display)
        
        left_layout.addWidget(navigation_group)
        
        # Playback Controls
        playback_group = QGroupBox("Playback Controls")
        playback_layout = QVBoxLayout(playback_group)
        
        # Play/Pause button
        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.togglePlayback)
        playback_layout.addWidget(self.play_button)
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "1x", "2x", "5x"])
        self.speed_combo.setCurrentText("1x")
        self.speed_combo.currentTextChanged.connect(self.changeSpeed)
        speed_layout.addWidget(self.speed_combo)
        playback_layout.addLayout(speed_layout)
        
        left_layout.addWidget(playback_group)
        
        # Window Size Controls
        window_group = QGroupBox("Window Size")
        window_layout = QGridLayout(window_group)
        
        window_sizes = [5, 10, 15, 30, 60, 120, 300]
        for i, size in enumerate(window_sizes):
            row = i // 2
            col = i % 2
            label = f"{size//60}m" if size >= 60 else f"{size}s"
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, s=size: self.change_window_size(s))
            if size == 10:  # Highlight default
                btn.setStyleSheet("background-color: #27ae60;")
            window_layout.addWidget(btn, row, col)
        
        left_layout.addWidget(window_group)
        
        # Zoom Controls
        zoom_group = QGroupBox("Zoom Controls")
        zoom_layout = QHBoxLayout(zoom_group)
        
        zoom_out_btn = QPushButton("🔍-")
        zoom_out_btn.setFixedWidth(60)
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        zoom_in_btn = QPushButton("🔍+")
        zoom_in_btn.setFixedWidth(60)
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        left_layout.addWidget(zoom_group)
        
        # Add stretch to push everything to top
        left_layout.addStretch()
        
        return left_widget

    def createRightPanel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        right_layout.addWidget(self.tab_widget)
        
        # Summary view tab
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        
        # Summary data display
        summary_data = QFrame()
        summary_data.setFrameStyle(QFrame.Box)
        summary_data.setStyleSheet("background-color: white; border: 1px solid #bdc3c7;")
        summary_layout.addWidget(summary_data)
        
        # Create matplotlib figure for summary
        self.summary_fig = Figure(figsize=(12, 4))
        self.summary_canvas = FigureCanvas(self.summary_fig)
        summary_layout.addWidget(self.summary_canvas)
        
        self.tab_widget.addTab(summary_tab, "Summary Data")
        
        # Detailed view tab
        detailed_tab = QWidget()
        detailed_layout = QVBoxLayout(detailed_tab)
        
        # Create matplotlib figure for detailed view
        self.detailed_fig = Figure(figsize=(12, 8))
        self.detailed_canvas = FigureCanvas(self.detailed_fig)
        detailed_layout.addWidget(self.detailed_canvas)
        
        self.tab_widget.addTab(detailed_tab, "Detailed Waveforms")
        
        # Initialize plots
        self.plot_signals()
        self.update_plot()
        
        # Auto-configure checkboxes based on data availability
        self.configure_signal_checkboxes()
        
        return right_widget

    def plot_signals(self):
        # Summary plot
        self.summary_ax = self.summary_fig.add_subplot(111)
        self.summary_fig.subplots_adjust(bottom=0.2, top=0.85)
        
        # Detailed plot
        self.detailed_ax = self.detailed_fig.add_subplot(111)
        self.detailed_fig.subplots_adjust(bottom=0.1, top=0.9)
        
        self.update_plots()

    def update_plots(self):
        # Update summary plot
        self.summary_ax.clear()
        
        # Plot normalized signals with offsets
        if self.position_checkbox.isChecked():
            self.summary_ax.plot(self.time, self.body_pos_n + self.offsets[0], color='black', label='Body Position', linewidth=2)
        if self.pulse_checkbox.isChecked():
            self.summary_ax.plot(self.time, self.pulse_n + self.offsets[1], color='red', label='Pulse', linewidth=2)
        if self.spo2_checkbox.isChecked():
            self.summary_ax.plot(self.time, self.spo2_n + self.offsets[2], color='green', label='SpO2', linewidth=2)
        if self.flow_checkbox.isChecked():
            self.summary_ax.plot(self.time, self.flow_n + self.offsets[3], color='blue', label='Airflow', linewidth=2)
        if self.snore_checkbox.isChecked():
            self.summary_ax.plot(self.time, self.snore_n + self.offsets[4], color='purple', label='Snore', linewidth=2)
        if self.thorax_checkbox.isChecked():
            self.summary_ax.plot(self.time, self.thorax_n + self.offsets[5], color='orange', label='Thorax', linewidth=2)
        if self.abdomen_checkbox.isChecked():
            self.summary_ax.plot(self.time, self.abdomen_n + self.offsets[6], color='brown', label='Abdomen', linewidth=2)
        if self.pleth_checkbox.isChecked():
            self.summary_ax.plot(self.time, self.pleth_n + self.offsets[7], color='pink', label='Pleth', linewidth=2)
        if self.activity_checkbox.isChecked():
            self.summary_ax.plot(self.time, self.activity_n + self.offsets[8], color='cyan', label='Activity', linewidth=2)

        # Y-axis labels for all signals
        all_signals = [self.body_pos_n, self.pulse_n, self.spo2_n, self.flow_n, 
                      self.snore_n, self.thorax_n, self.abdomen_n, self.pleth_n, self.activity_n]
        yticks_pos = [np.mean(sig) + offset for sig, offset in zip(all_signals, self.offsets)]
        yticks_labels = ['Body Position', 'Pulse (BPM)', 'SpO2 (%)', 'Airflow', 
                        'Snore', 'Thorax', 'Abdomen', 'Pleth', 'Activity']
        self.summary_ax.set_yticks(yticks_pos)
        self.summary_ax.set_yticklabels(yticks_labels, fontsize=10)
        self.summary_ax.set_ylim(-0.5, max(self.offsets) + 1)
        self.summary_ax.set_xlabel('Time (s)')
        self.summary_ax.set_title('SleepSense - Summary Data View', fontsize=14, fontweight='bold')
        self.summary_ax.grid(True, alpha=0.3)

        # Update detailed plot
        self.detailed_ax.clear()
        
        # Plot detailed waveforms
        if self.position_checkbox.isChecked():
            self.detailed_ax.plot(self.time, self.body_pos_n + self.offsets[0], color='black', label='Body Position', linewidth=1.5)
        if self.pulse_checkbox.isChecked():
            self.detailed_ax.plot(self.time, self.pulse_n + self.offsets[1], color='red', label='Pulse', linewidth=1.5)
        if self.spo2_checkbox.isChecked():
            self.detailed_ax.plot(self.time, self.spo2_n + self.offsets[2], color='green', label='SpO2', linewidth=1.5)
        if self.flow_checkbox.isChecked():
            self.detailed_ax.plot(self.time, self.flow_n + self.offsets[3], color='blue', label='Airflow', linewidth=1.5)
        if self.snore_checkbox.isChecked():
            self.detailed_ax.plot(self.time, self.snore_n + self.offsets[4], color='purple', label='Snore', linewidth=1.5)
        if self.thorax_checkbox.isChecked():
            self.detailed_ax.plot(self.time, self.thorax_n + self.offsets[5], color='orange', label='Thorax', linewidth=1.5)
        if self.abdomen_checkbox.isChecked():
            self.detailed_ax.plot(self.time, self.abdomen_n + self.offsets[6], color='brown', label='Abdomen', linewidth=1.5)
        if self.pleth_checkbox.isChecked():
            self.detailed_ax.plot(self.time, self.pleth_n + self.offsets[7], color='pink', label='Pleth', linewidth=1.5)
        if self.activity_checkbox.isChecked():
            self.detailed_ax.plot(self.time, self.activity_n + self.offsets[8], color='cyan', label='Activity', linewidth=1.5)

        self.detailed_ax.set_yticks(yticks_pos)
        self.detailed_ax.set_yticklabels(yticks_labels, fontsize=10)
        self.detailed_ax.set_ylim(-0.5, max(self.offsets) + 1)
        self.detailed_ax.set_xlabel('Time (s)')
        self.detailed_ax.set_title('SleepSense - Detailed Waveform View', fontsize=14, fontweight='bold')
        self.detailed_ax.grid(True, alpha=0.3)
        self.detailed_ax.legend()

        # Add arrows for body position
        if self.position_checkbox.isChecked():
            self.add_position_arrows()

    def add_position_arrows(self):
        arrow_y = self.offsets[0] + 0.5
        interval = 5  # seconds between arrows
        dt = self.time.iloc[1] - self.time.iloc[0]
        sampling_step = max(int(interval / dt), 1)
        arrow_times = self.time[::sampling_step]

        for t in arrow_times:
            idx = (np.abs(self.time - t)).argmin()
            pos = self.body_pos.iloc[idx]
            dx, dy, arrow_char, label = self.arrow_directions.get(pos, (0, 0, '?', 'Unknown'))
            
            # Add to both plots
            for ax in [self.summary_ax, self.detailed_ax]:
                ax.annotate(
                    arrow_char,
                    xy=(self.time.iloc[idx], arrow_y),
                    xytext=(self.time.iloc[idx] + dx, arrow_y + dy),
                    fontsize=16,
                    color='blue',
                    ha='center',
                    va='center',
                    arrowprops=dict(arrowstyle='->', color='green', lw=2)
                )

    def update_plot(self):
        slider_val = self.slider.value() / 100  # slider scaled to seconds
        # Clamp slider max to avoid window overflow
        max_start = self.end_time - self.window_size
        start = self.start_time + min(slider_val, max_start - self.start_time)
        end = start + self.window_size
        
        # Update both plots
        self.summary_ax.set_xlim(start, end)
        self.detailed_ax.set_xlim(start, end)
        
        # Update time display
        start_str = f"{int(start//60):02d}:{int(start%60):02d}:{int((start%1)*100):02d}"
        end_str = f"{int(end//60):02d}:{int(end%60):02d}:{int((end%1)*100):02d}"
        self.time_display.setText(f"{start_str} - {end_str}")
        
        # Redraw canvases
        self.summary_canvas.draw_idle()
        self.detailed_canvas.draw_idle()

    def change_window_size(self, size):
        self.window_size = float(size)
        self.window_size = max(self.min_window_size, min(self.window_size, self.max_window_size))
        max_slider_val = int((self.end_time - self.start_time - self.window_size) * 100)
        self.slider.setMaximum(max_slider_val)
        if self.slider.value() > max_slider_val:
            self.slider.setValue(max_slider_val)
        else:
            self.update_plot()

    def zoom_in(self):
        new_size = self.window_size / 1.5  # zoom in by reducing window size
        if new_size < self.min_window_size:
            new_size = self.min_window_size
        self.window_size = new_size
        max_slider_val = int((self.end_time - self.start_time - self.window_size) * 100)
        self.slider.setMaximum(max_slider_val)
        self.update_plot()

    def zoom_out(self):
        new_size = self.window_size * 1.5  # zoom out by increasing window size
        if new_size > self.max_window_size:
            new_size = self.max_window_size
        self.window_size = new_size
        max_slider_val = int((self.end_time - self.start_time - self.window_size) * 100)
        self.slider.setMaximum(max_slider_val)
        self.update_plot()

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
        current_val = self.slider.value()
        max_val = self.slider.maximum()
        if current_val < max_val:
            self.slider.setValue(current_val + 1)
        else:
            self.stopPlayback()

    def changeSpeed(self, speed_text):
        speed_map = {"0.5x": 0.5, "1x": 1.0, "2x": 2.0, "5x": 5.0}
        self.play_speed = speed_map.get(speed_text, 1.0)
        if self.is_playing:
            self.play_timer.setInterval(int(1000 * self.play_speed))

    def openFile(self):
        self.statusBar().showMessage("Open file functionality - Not implemented yet")

    def saveReport(self):
        self.statusBar().showMessage("Save report functionality - Not implemented yet")

    def configure_signal_checkboxes(self):
        """Automatically configure checkboxes based on data availability"""
        num_columns = len(self.data.columns)
        
        if num_columns == 10:  # Current format
            # Keep all signals enabled to show generated waves
            self.snore_checkbox.setEnabled(True)
            self.thorax_checkbox.setEnabled(True)
            self.abdomen_checkbox.setEnabled(True)
            self.pleth_checkbox.setEnabled(True)
            
            # Update format label
            self.format_label.setText("Current (10 cols) + Generated Waves")
            self.format_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            
            # Show status message
            self.statusBar().showMessage("Current data format detected - Future signals show generated realistic waveforms")
            
        elif num_columns >= 12:  # Future format
            # Enable all signals
            self.snore_checkbox.setEnabled(True)
            self.thorax_checkbox.setEnabled(True)
            self.abdomen_checkbox.setEnabled(True)
            self.pleth_checkbox.setEnabled(True)
            
            # Update format label
            self.format_label.setText(f"Future ({num_columns} cols)")
            self.format_label.setStyleSheet("color: #e67e22; font-weight: bold;")
            
            # Auto-check future signals if they have real data
            if np.any(self.snore != 0):
                self.snore_checkbox.setChecked(True)
            if np.any(self.thorax != 0):
                self.thorax_checkbox.setChecked(True)
            if np.any(self.abdomen != 0):
                self.abdomen_checkbox.setChecked(True)
            if np.any(self.pleth != 0):
                self.pleth_checkbox.setChecked(True)
            
            self.statusBar().showMessage("Future data format detected - All signals enabled")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SleepSensePlot()
    win.show()
    sys.exit(app.exec_())
