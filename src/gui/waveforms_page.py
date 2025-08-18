"""
Waveforms page for SleepSense application
"""

import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QComboBox, QSlider, QSpinBox,
    QTabWidget, QScrollArea, QGroupBox, QCheckBox, QSplitter
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QIcon

import pyqtgraph as pg
from pyqtgraph import PlotWidget, PlotItem

from ..auth.user_manager import JSONUserManager
from ..utils.logger import get_logger

class WaveformsPage(QWidget):
    """Waveforms page widget"""
    
    def __init__(self, auth_manager: JSONUserManager, settings, main_window):
        super().__init__()
        self.auth_manager = auth_manager
        self.settings = settings
        self.main_window = main_window
        self.logger = get_logger(__name__)
        
        # Initialize data
        self.sample_rate = settings.get('data.sample_rate', 256)
        self.channels = settings.get('data.channels', ['EEG', 'EOG', 'EMG', 'ECG'])
        self.recording_duration = settings.get('data.recording_duration', 3600)
        
        # Data storage
        self.time_data = np.linspace(0, 10, self.sample_rate * 10)  # 10 seconds of data
        self.channel_data = {}
        self.recording = False
        
        self.setup_ui()
        self.setup_plots()
        self.setup_timer()
        self.generate_sample_data()
    
    def setup_ui(self):
        """Setup the waveforms page user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Enhanced page title with gradient text effect
        title_label = QLabel("Waveform Analysis")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-align: center;
                margin-bottom: 20px;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a2a6b, stop:0.5 #b21f1f, stop:1 #fdbb2d);
                border-radius: 15px;
                border: 2px solid rgba(255, 255, 255, 0.2);
            }
        """)
        main_layout.addWidget(title_label)
        
        # Control panel
        self.create_control_panel(main_layout)
        
        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Channel selection and settings
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Waveform display
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([300, 900])
        main_layout.addWidget(content_splitter)
    
    def create_control_panel(self, main_layout):
        """Create the enhanced control panel"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        control_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e3f2fd;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        control_layout = QHBoxLayout(control_frame)
        control_layout.setSpacing(25)
        
        # Enhanced Recording controls
        recording_group = QGroupBox("Recording")
        recording_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
                border: 2px solid #e3f2fd;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1a2a6b;
                font-weight: bold;
            }
        """)
        
        recording_layout = QHBoxLayout(recording_group)
        
        # Enhanced Record button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c0392b, stop:1 #a93226);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a93226, stop:1 #8b291a);
                border: 2px solid rgba(255, 255, 255, 0.7);
            }
        """)
        self.record_button.clicked.connect(self.toggle_recording)
        recording_layout.addWidget(self.record_button)
        
        self.recording_status_label = QLabel("Stopped")
        self.recording_status_label.setStyleSheet("""
            color: #e74c3c; 
            font-weight: bold; 
            font-size: 14px;
            padding: 8px 15px;
            background: rgba(231, 76, 60, 0.1);
            border-radius: 15px;
            border: 1px solid rgba(231, 76, 60, 0.3);
        """)
        recording_layout.addWidget(self.recording_status_label)
        
        control_layout.addWidget(recording_group)
        
        # Enhanced Display controls
        display_group = QGroupBox("Display")
        display_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
                border: 2px solid #e3f2fd;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1a2a6b;
                font-weight: bold;
            }
        """)
        
        display_layout = QHBoxLayout(display_group)
        
        display_layout.addWidget(QLabel("Time Window:"))
        self.time_window_spin = QSpinBox()
        self.time_window_spin.setRange(5, 60)
        self.time_window_spin.setValue(10)
        self.time_window_spin.setSuffix(" s")
        self.time_window_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #e3f2fd;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                font-weight: 500;
            }
            QSpinBox:focus {
                border: 2px solid #3498db;
                box-shadow: 0 0 10px rgba(52, 152, 219, 0.2);
            }
        """)
        self.time_window_spin.valueChanged.connect(self.update_time_window)
        display_layout.addWidget(self.time_window_spin)
        
        display_layout.addWidget(QLabel("Amplitude:"))
        self.amplitude_slider = QSlider(Qt.Orientation.Horizontal)
        self.amplitude_slider.setRange(1, 10)
        self.amplitude_slider.setValue(5)
        self.amplitude_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 2px solid #e3f2fd;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: 2px solid #ffffff;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #21618c);

            }
        """)
        self.amplitude_slider.valueChanged.connect(self.update_amplitude)
        display_layout.addWidget(self.amplitude_slider)
        
        control_layout.addWidget(display_group)
        
        # Enhanced Analysis controls
        analysis_group = QGroupBox("Analysis")
        analysis_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
                border: 2px solid #e3f2fd;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1a2a6b;
                font-weight: bold;
            }
        """)
        
        analysis_layout = QHBoxLayout(analysis_group)
        
        self.auto_scale_checkbox = QCheckBox("Auto Scale")
        self.auto_scale_checkbox.setChecked(True)
        self.auto_scale_checkbox.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #e3f2fd;
                background: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #3498db;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
            }
        """)
        self.auto_scale_checkbox.stateChanged.connect(self.toggle_auto_scale)
        analysis_layout.addWidget(self.auto_scale_checkbox)
        
        self.filter_checkbox = QCheckBox("Apply Filters")
        self.filter_checkbox.setChecked(True)
        self.filter_checkbox.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #e3f2fd;
                background: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #3498db;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
            }
        """)
        self.filter_checkbox.stateChanged.connect(self.toggle_filters)
        analysis_layout.addWidget(self.filter_checkbox)
        
        control_layout.addWidget(analysis_group)
        
        control_layout.addStretch()
        main_layout.addWidget(control_frame)
    
    def create_left_panel(self):
        """Create the enhanced left panel with channel selection and settings"""
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e3f2fd;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
        """)
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(20)
        
        # Enhanced Channel selection
        channels_group = QGroupBox("Channels")
        channels_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
                border: 2px solid #e3f2fd;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1a2a6b;
                font-weight: bold;
            }
        """)
        
        channels_layout = QVBoxLayout(channels_group)
        
        self.channel_checkboxes = {}
        for channel in self.channels:
            checkbox = QCheckBox(channel)
            checkbox.setChecked(True)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #2c3e50;
                    font-size: 14px;
                    font-weight: 500;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    padding: 8px;
                    border-radius: 8px;
                }
                QCheckBox:hover {
                    background: rgba(52, 152, 219, 0.1);
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 5px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #e3f2fd;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #3498db;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db, stop:1 #2980b9);
                }
            """)
            checkbox.stateChanged.connect(self.toggle_channel)
            self.channel_checkboxes[channel] = checkbox
            channels_layout.addWidget(checkbox)
        
        left_layout.addWidget(channels_group)
        
        # Enhanced Channel settings
        settings_group = QGroupBox("Channel Settings")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
                border: 2px solid #e3f2fd;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1a2a6b;
                font-weight: bold;
            }
        """)
        
        settings_layout = QGridLayout(settings_group)
        settings_layout.setSpacing(12)
        
        # Channel selection for settings
        settings_layout.addWidget(QLabel("Channel:"), 0, 0)
        self.settings_channel_combo = QComboBox()
        self.settings_channel_combo.addItems(self.channels)
        self.settings_channel_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #e3f2fd;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
                box-shadow: 0 0 10px rgba(52, 152, 219, 0.2);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iIzM0OThkYiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==);
                width: 12px;
                height: 12px;
            }
        """)
        self.settings_channel_combo.currentTextChanged.connect(self.update_channel_settings)
        settings_layout.addWidget(self.settings_channel_combo, 0, 1)
        
        # Gain setting
        settings_layout.addWidget(QLabel("Gain:"), 1, 0)
        self.gain_spin = QSpinBox()
        self.gain_spin.setRange(1, 100)
        self.gain_spin.setValue(10)
        self.gain_spin.setSuffix("x")
        self.gain_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #e3f2fd;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 2px solid #3498db;
                box-shadow: 0 0 10px rgba(52, 152, 219, 0.2);
            }
        """)
        self.gain_spin.valueChanged.connect(self.update_gain)
        settings_layout.addWidget(self.gain_spin, 1, 1)
        
        # Offset setting
        settings_layout.addWidget(QLabel("Offset:"), 2, 0)
        self.offset_spin = QSpinBox()
        self.offset_spin.setRange(-100, 100)
        self.offset_spin.setValue(0)
        self.offset_spin.setSuffix(" μV")
        self.offset_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #e3f2fd;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 2px solid #3498db;
                box-shadow: 0 0 10px rgba(52, 152, 219, 0.2);
            }
        """)
        self.offset_spin.valueChanged.connect(self.update_offset)
        settings_layout.addWidget(self.offset_spin, 2, 1)
        
        left_layout.addWidget(settings_group)
        
        # Enhanced Analysis tools
        tools_group = QGroupBox("Analysis Tools")
        tools_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2c3e50;
                border: 2px solid #e3f2fd;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1a2a6b;
                font-weight: bold;
            }
        """)
        
        tools_layout = QVBoxLayout(tools_group)
        
        # Enhanced Analysis tool buttons
        fft_btn = QPushButton("FFT Analysis")
        fft_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #21618c);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #21618c, stop:1 #1b4f72);
                border: 2px solid rgba(255, 255, 255, 0.7);
            }
        """)
        
        sleep_stage_btn = QPushButton("Sleep Stage")
        sleep_stage_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:1 #8e44ad);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8e44ad, stop:1 #7d3c98);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7d3c98, stop:1 #6c3483);
                border: 2px solid rgba(255, 255, 255, 0.7);
            }
        """)
        
        artifact_btn = QPushButton("Artifact Detection")
        artifact_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #229954, stop:1 #27ae60);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e8449, stop:1 #229954);
                border: 2px solid rgba(255, 255, 255, 0.7);
            }
        """)
        
        export_btn = QPushButton("Export Data")
        export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e67e22, stop:1 #d35400);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #d35400, stop:1 #ba4a00);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ba4a00, stop:1 #a04000);
                border: 2px solid rgba(255, 255, 255, 0.7);
            }
        """)
        
        tools_layout.addWidget(fft_btn)
        tools_layout.addWidget(sleep_stage_btn)
        tools_layout.addWidget(artifact_btn)
        tools_layout.addWidget(export_btn)
        
        left_layout.addWidget(tools_group)
        
        left_layout.addStretch()
        return left_frame
    
    def create_right_panel(self):
        """Create the enhanced right panel with waveform display"""
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e3f2fd;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
        """)
        
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)
        
        # Enhanced Waveform display area
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Amplitude (μV)', color='#2c3e50', size='12pt')
        self.plot_widget.setLabel('bottom', 'Time (s)', color='#2c3e50', size='12pt')
        self.plot_widget.setTitle('SleepSense Waveforms', size='16pt', color='#1a2a6b')
        
        # Enhanced plot styling
        self.plot_widget.getAxis('left').setTextPen(pg.mkPen(color='#2c3e50'))
        self.plot_widget.getAxis('bottom').setTextPen(pg.mkPen(color='#2c3e50'))
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='#e3f2fd', width=2))
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='#e3f2fd', width=2))
        
        right_layout.addWidget(self.plot_widget)
        
        return right_frame
    
    def setup_plots(self):
        """Setup the waveform plots"""
        self.plot_curves = {}
        self.plot_colors = {
            'EEG': '#e74c3c',      # Red
            'EOG': '#3498db',      # Blue
            'EMG': '#27ae60',      # Green
            'ECG': '#9b59b6'       # Purple
        }
        
        for channel in self.channels:
            pen = pg.mkPen(color=self.plot_colors[channel], width=2)
            curve = self.plot_widget.plot(pen=pen, name=channel)
            self.plot_curves[channel] = curve
    
    def setup_timer(self):
        """Setup timer for real-time updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_waveforms)
        self.update_timer.start(100)  # Update every 100ms
    
    def generate_sample_data(self):
        """Generate sample waveform data"""
        for channel in self.channels:
            if channel == 'EEG':
                # Alpha waves (8-13 Hz) + noise
                data = (np.sin(2 * np.pi * 10 * self.time_data) * 50 + 
                       np.random.normal(0, 5, len(self.time_data)))
            elif channel == 'EOG':
                # Eye movement artifacts
                data = (np.sin(2 * np.pi * 2 * self.time_data) * 30 + 
                       np.random.normal(0, 8, len(self.time_data)))
            elif channel == 'EMG':
                # Muscle activity
                data = (np.sin(2 * np.pi * 20 * self.time_data) * 20 + 
                       np.random.normal(0, 10, len(self.time_data)))
            elif channel == 'ECG':
                # Heart rate (60-100 BPM)
                data = (np.sin(2 * np.pi * 1.2 * self.time_data) * 100 + 
                       np.random.normal(0, 3, len(self.time_data)))
            
            self.channel_data[channel] = data
    
    def update_waveforms(self):
        """Update the waveform display"""
        if not self.recording:
            return
        
        # Update time data (scrolling effect)
        self.time_data = np.roll(self.time_data, -1)
        self.time_data[-1] = self.time_data[-2] + 1.0 / self.sample_rate
        
        # Update channel data
        for channel in self.channels:
            if channel in self.channel_checkboxes and self.channel_checkboxes[channel].isChecked():
                # Generate new data point
                if channel == 'EEG':
                    new_point = (np.sin(2 * np.pi * 10 * self.time_data[-1]) * 50 + 
                               np.random.normal(0, 5))
                elif channel == 'EOG':
                    new_point = (np.sin(2 * np.pi * 2 * self.time_data[-1]) * 30 + 
                               np.random.normal(0, 8))
                elif channel == 'EMG':
                    new_point = (np.sin(2 * np.pi * 20 * self.time_data[-1]) * 20 + 
                               np.random.normal(0, 10))
                elif channel == 'ECG':
                    new_point = (np.sin(2 * np.pi * 1.2 * self.time_data[-1]) * 100 + 
                               np.random.normal(0, 3))
                
                # Roll data and add new point
                self.channel_data[channel] = np.roll(self.channel_data[channel], -1)
                self.channel_data[channel][-1] = new_point
                
                # Update plot
                curve = self.plot_curves[channel]
                curve.setData(self.time_data, self.channel_data[channel])
    
    def toggle_recording(self):
        """Toggle recording state with enhanced styling"""
        self.recording = not self.recording
        
        if self.recording:
            self.record_button.setText("Stop Recording")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #27ae60, stop:1 #229954);
                    color: white;
                    border: none;
                    padding: 15px 25px;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #229954, stop:1 #1e8449);
                    border: 2px solid rgba(255, 255, 255, 0.5);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1e8449, stop:1 #196f3d);
                    border: 2px solid rgba(255, 255, 255, 0.7);
                }
            """)
            self.recording_status_label.setText("Recording")
            self.recording_status_label.setStyleSheet("""
                color: #27ae60; 
                font-weight: bold; 
                font-size: 14px;
                padding: 8px 15px;
                background: rgba(39, 174, 96, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(39, 174, 96, 0.3);
            """)
        else:
            self.record_button.setText("Start Recording")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #e74c3c, stop:1 #c0392b);
                    color: white;
                    border: none;
                    padding: 15px 25px;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #c0392b, stop:1 #a93226);
                    border: 2px solid rgba(255, 255, 255, 0.5);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #a93226, stop:1 #8b291a);
                    border: 2px solid rgba(255, 255, 255, 0.7);
                }
            """)
            self.recording_status_label.setText("Stopped")
            self.recording_status_label.setStyleSheet("""
                color: #e74c3c; 
                font-weight: bold; 
                font-size: 14px;
                padding: 8px 15px;
                background: rgba(231, 76, 60, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(231, 76, 60, 0.3);
            """)
    
    def toggle_channel(self):
        """Toggle channel visibility"""
        for channel, checkbox in self.channel_checkboxes.items():
            curve = self.plot_curves[channel]
            if checkbox.isChecked():
                curve.show()
            else:
                curve.hide()
    
    def update_time_window(self, value):
        """Update the time window display"""
        # This would update the x-axis range
        pass
    
    def update_amplitude(self, value):
        """Update the amplitude scaling"""
        # This would update the y-axis range
        pass
    
    def toggle_auto_scale(self, state):
        """Toggle auto-scaling"""
        if state == Qt.CheckState.Checked:
            self.plot_widget.enableAutoRange()
        else:
            self.plot_widget.disableAutoRange()
    
    def toggle_filters(self, state):
        """Toggle signal filters"""
        # This would apply/remove signal processing filters
        pass
    
    def update_channel_settings(self, channel):
        """Update channel-specific settings"""
        # This would update gain, offset, etc. for the selected channel
        pass
    
    def update_gain(self, value):
        """Update channel gain"""
        # This would update the gain for the selected channel
        pass
    
    def update_offset(self, value):
        """Update channel offset"""
        # This would update the offset for the selected channel
        pass
    
    def show_fft_analysis(self):
        """Show FFT analysis window"""
        # This would open a new window with FFT analysis
        pass
    
    def show_sleep_stage_analysis(self):
        """Show sleep stage analysis window"""
        # This would open a new window with sleep stage analysis
        pass
