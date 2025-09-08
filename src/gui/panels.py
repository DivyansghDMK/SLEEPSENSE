"""
UI panels for SleepSense Pro
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, 
    QLabel, QPushButton, QSlider, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

from ..config.constants import SIGNAL_COLORS, FRAME_SIZES


class LeftPanel(QWidget):
    """Left control panel with signal checkboxes"""
    
    signal_toggled = pyqtSignal()
    zoom_toggled = pyqtSignal(str, bool)
    view_mode_changed = pyqtSignal(str)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the left panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.setStyleSheet("background-color: #f8f9fa; border-right: 2px solid #dee2e6;")
        
        # Branding
        branding_label = QLabel("SleepSense Pro")
        branding_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; background-color: #3498db; color: white; border-radius: 8px; margin-bottom: 5px;")
        branding_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(branding_label)
        
        # Signal Groups
        self.create_signal_groups(layout)
        
        layout.addStretch()
    
    def create_signal_groups(self, parent_layout):
        """Create signal control groups"""
        # Respiratory Group
        respiratory_group = QGroupBox("🫁 Respiratory")
        respiratory_layout = QVBoxLayout(respiratory_group)
        self.flow_checkbox = QCheckBox()
        self.thorax_checkbox = QCheckBox()
        self.abdomen_checkbox = QCheckBox()
        self.snore_checkbox = QCheckBox()
        self.create_wave_control(respiratory_layout, "Airflow", self.flow_checkbox, 'flow')
        self.create_wave_control(respiratory_layout, "Thorax", self.thorax_checkbox, 'thorax')
        self.create_wave_control(respiratory_layout, "Abdomen", self.abdomen_checkbox, 'abdomen')
        self.create_wave_control(respiratory_layout, "Snore", self.snore_checkbox, 'snore')
        parent_layout.addWidget(respiratory_group)
        
        # EEG Group
        eeg_group = QGroupBox("🧠 EEG")
        eeg_layout = QVBoxLayout(eeg_group)
        self.eeg_c3_checkbox, self.eeg_c4_checkbox = QCheckBox(), QCheckBox()
        self.eeg_f3_checkbox, self.eeg_f4_checkbox = QCheckBox(), QCheckBox()
        self.eeg_o1_checkbox, self.eeg_o2_checkbox = QCheckBox(), QCheckBox()
        self.create_wave_control(eeg_layout, "C3-A2", self.eeg_c3_checkbox, 'eeg_c3')
        self.create_wave_control(eeg_layout, "C4-A1", self.eeg_c4_checkbox, 'eeg_c4')
        self.create_wave_control(eeg_layout, "F3-A2", self.eeg_f3_checkbox, 'eeg_f3')
        self.create_wave_control(eeg_layout, "F4-A1", self.eeg_f4_checkbox, 'eeg_f4')
        self.create_wave_control(eeg_layout, "O1-A2", self.eeg_o1_checkbox, 'eeg_o1')
        self.create_wave_control(eeg_layout, "O2-A1", self.eeg_o2_checkbox, 'eeg_o2')
        parent_layout.addWidget(eeg_group)
        
        # Other Group
        other_group = QGroupBox("💓 Other")
        other_layout = QVBoxLayout(other_group)
        self.spo2_checkbox = QCheckBox()
        self.pulse_checkbox = QCheckBox()
        self.position_checkbox = QCheckBox()
        self.activity_checkbox = QCheckBox()
        self.pleth_checkbox = QCheckBox()
        self.create_wave_control(other_layout, "SpO2", self.spo2_checkbox, 'spo2')
        self.create_wave_control(other_layout, "Pulse", self.pulse_checkbox, 'pulse')
        self.create_wave_control(other_layout, "Position", self.position_checkbox, 'body_pos')
        self.create_wave_control(other_layout, "Activity", self.activity_checkbox, 'activity')
        self.create_wave_control(other_layout, "Pleth", self.pleth_checkbox, 'pleth')
        parent_layout.addWidget(other_group)
    
    def create_wave_control(self, parent_layout, label_text, checkbox, signal_key):
        """Create a wave control with checkbox and integrated toggle zoom button"""
        control_layout = QHBoxLayout()
        checkbox.setChecked(True)
        control_layout.addWidget(checkbox)
        label = QLabel(label_text)
        label.setMinimumWidth(90 if self.settings.is_small_screen else 110)
        control_layout.addWidget(label)
        
        zoom_toggle_btn = QPushButton("🔍")
        zoom_toggle_btn.setFixedSize(28, 28)
        zoom_toggle_btn.setCheckable(True)
        zoom_toggle_btn.setToolTip("Toggle Zoom for this signal")
        zoom_toggle_btn.setStyleSheet("""
            QPushButton { background-color: #6c757d; border-radius: 14px; min-width: 0px; padding: 0px; }
            QPushButton:checked { background-color: #28a745; }
        """)
        zoom_toggle_btn.toggled.connect(lambda checked, key=signal_key: self.zoom_toggled.emit(key, checked))
        control_layout.addWidget(zoom_toggle_btn)
        parent_layout.addLayout(control_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect all checkboxes to the update function
        all_checkboxes = [
            self.flow_checkbox, self.thorax_checkbox, self.abdomen_checkbox, self.snore_checkbox,
            self.eeg_c3_checkbox, self.eeg_c4_checkbox, self.eeg_f3_checkbox, self.eeg_f4_checkbox,
            self.eeg_o1_checkbox, self.eeg_o2_checkbox, self.spo2_checkbox, self.pulse_checkbox,
            self.position_checkbox, self.activity_checkbox, self.pleth_checkbox
        ]
        for cb in all_checkboxes:
            cb.toggled.connect(self.signal_toggled.emit)
    
    def configure_signal_checkboxes(self):
        """Configure signal checkboxes - all signals are available"""
        for child in self.findChildren(QCheckBox):
            child.setEnabled(True)
            child.setChecked(True)
    
    def get_checked_signals(self):
        """Get list of checked signal keys"""
        signal_mapping = {
            'flow': self.flow_checkbox,
            'thorax': self.thorax_checkbox,
            'abdomen': self.abdomen_checkbox,
            'snore': self.snore_checkbox,
            'eeg_c3': self.eeg_c3_checkbox,
            'eeg_c4': self.eeg_c4_checkbox,
            'eeg_f3': self.eeg_f3_checkbox,
            'eeg_f4': self.eeg_f4_checkbox,
            'eeg_o1': self.eeg_o1_checkbox,
            'eeg_o2': self.eeg_o2_checkbox,
            'spo2': self.spo2_checkbox,
            'pulse': self.pulse_checkbox,
            'body_pos': self.position_checkbox,
            'activity': self.activity_checkbox,
            'pleth': self.pleth_checkbox
        }
        
        return [key for key, checkbox in signal_mapping.items() if checkbox.isChecked()]


class RightPanel(QWidget):
    """Right panel with navigation controls and plots"""
    
    window_size_changed = pyqtSignal(float)
    time_changed = pyqtSignal(float)
    comparison_toggled = pyqtSignal(bool)
    osa_analysis_toggled = pyqtSignal(bool)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the right panel UI"""
        layout = QVBoxLayout(self)
        
        # Navigation Controls
        self.create_navigation_controls(layout)
        
        # Plots Container (will be managed by PlotManager)
        self.plots_container = QWidget()
        layout.addWidget(self.plots_container, 1)
    
    def create_navigation_controls(self, parent_layout):
        """Create navigation controls"""
        navigation_group = QGroupBox("⏱️ Navigation & Time Frames")
        navigation_group.setMaximumHeight(95)
        navigation_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                font-size: 11px;
            }
        """)
        navigation_layout = QVBoxLayout(navigation_group)
        navigation_layout.setContentsMargins(8, 8, 8, 6)
        navigation_layout.setSpacing(6)
        
        # Time slider and display
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)
        
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 1000)
        self.time_slider.setMaximumHeight(20)
        self.time_slider.setStyleSheet(self.get_slider_style())
        controls_layout.addWidget(self.time_slider)
        
        self.current_time_label = QLabel("00:00:00")
        self.current_time_label.setStyleSheet(self.get_time_label_style())
        self.current_time_label.setMaximumHeight(20)
        self.current_time_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self.current_time_label)
        
        navigation_layout.addLayout(controls_layout)
        
        # Time frame buttons
        self.create_timeframe_buttons(navigation_layout)
        
        parent_layout.addWidget(navigation_group)
    
    def create_timeframe_buttons(self, parent_layout):
        """Create time frame selection buttons"""
        timeframe_container = QHBoxLayout()
        timeframe_container.setSpacing(4)
        
        timeframe_label = QLabel("⏳")
        timeframe_label.setStyleSheet("""
            QLabel {
                color: #5d6d7e;
                font-size: 12px;
                padding: 2px;
            }
        """)
        timeframe_label.setToolTip("Select time window duration")
        timeframe_container.addWidget(timeframe_label)
        
        frame_buttons_layout = QHBoxLayout()
        frame_buttons_layout.setSpacing(4)
        self.frame_buttons = {}
        
        button_style = self.get_button_style()
        
        for seconds in FRAME_SIZES:
            if seconds < 60:
                btn_text = f"{seconds}s"
            elif seconds < 3600:
                btn_text = f"{seconds//60}m"
            else:
                btn_text = f"{seconds//3600}h"
            
            btn = QPushButton(btn_text)
            btn.setCheckable(True)
            btn.setStyleSheet(button_style)
            btn.setToolTip(f"Set time window to {btn_text}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, s=seconds: self.set_frame_size_from_button(s))
            frame_buttons_layout.addWidget(btn)
            self.frame_buttons[seconds] = btn
        
        self.frame_buttons[10].setChecked(True)
        
        timeframe_container.addLayout(frame_buttons_layout)
        timeframe_container.addStretch()
        
        parent_layout.addLayout(timeframe_container)
    
    def get_slider_style(self):
        """Get slider stylesheet"""
        return """
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #d5dbdb);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: 2px solid #2471a3;
                width: 20px;
                margin: -3px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
                border: 2px solid #1f618d;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #85c1e9, stop:1 #5dade2);
                border: 1px solid #2980b9;
                border-radius: 4px;
            }
        """
    
    def get_time_label_style(self):
        """Get time label stylesheet"""
        return """
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34495e, stop:1 #2c3e50);
                color: white;
                padding: 4px 8px;
                border-radius: 6px;
                font-family: 'Courier New', 'Monaco', monospace;
                font-size: 10px;
                font-weight: bold;
                min-width: 70px;
                border: 1px solid #1a252f;
            }
        """
    
    def get_button_style(self):
        """Get button stylesheet"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 2px solid #dee2e6;
                border-radius: 8px;
                font-size: 10px;
                font-weight: 600;
                color: #495057;
                padding: 4px 8px;
                min-width: 40px;
                min-height: 28px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e3f2fd, stop:1 #bbdefb);
                border: 2px solid #2196f3;
                color: #1976d2;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                border: 2px solid #2e7d32;
                color: white;
                font-weight: bold;
            }
            QPushButton:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:1 #4caf50);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c8e6c9, stop:1 #a5d6a7);
            }
        """
    
    def setup_connections(self):
        """Setup signal connections"""
        self.time_slider.valueChanged.connect(self.on_slider_changed)
    
    def set_frame_size_from_button(self, seconds):
        """Set frame size from button click"""
        self.settings.window_size = float(seconds)
        for s, btn in self.frame_buttons.items():
            btn.setChecked(s == seconds)
        # Clamp start time to valid range after window size change
        data_start = getattr(self.settings, 'data_start_time', self.settings.start_time)
        data_end = getattr(self.settings, 'data_end_time', self.settings.end_time)
        max_start = max(data_start, data_end - self.settings.window_size)
        if self.settings.start_time > max_start:
            self.settings.start_time = max_start
        # Notify listeners
        self.window_size_changed.emit(seconds)
        self.time_changed.emit(self.settings.start_time)
    
    def on_slider_changed(self, value):
        """Handle slider value change"""
        data_start = getattr(self.settings, 'data_start_time', self.settings.start_time)
        data_end = getattr(self.settings, 'data_end_time', self.settings.end_time)
        available_range = max(0.0, (data_end - data_start) - self.settings.window_size)
        if available_range <= 0:
            self.settings.start_time = data_start
            self.time_changed.emit(self.settings.start_time)
            return
        new_start_time = data_start + (value / 1000.0) * available_range
        new_start_time = max(data_start, min(new_start_time, data_end - self.settings.window_size))
        self.settings.start_time = new_start_time
        self.time_changed.emit(self.settings.start_time)
    
    def update_time_display(self, start_time, end_time):
        """Update the time display label"""
        start_str = f"{int(start_time//3600):02d}:{int((start_time%3600)//60):02d}:{int(start_time%60):02d}"
        end_str = f"{int(end_time//3600):02d}:{int((end_time%3600)//60):02d}:{int(end_time%60):02d}"
        self.current_time_label.setText(f"{start_str}-{end_str}")
    
    def update_slider_position(self, start_time):
        """Update slider position based on start time"""
        data_start = getattr(self.settings, 'data_start_time', self.settings.start_time)
        data_end = getattr(self.settings, 'data_end_time', self.settings.end_time)
        available_range = max(0.0, (data_end - data_start) - self.settings.window_size)
        if available_range <= 0:
            slider_pos = 0
        else:
            slider_pos = int(((start_time - data_start) / available_range) * 1000)
            slider_pos = max(0, min(1000, slider_pos))
        self.time_slider.blockSignals(True)
        self.time_slider.setValue(slider_pos)
        self.time_slider.blockSignals(False)
