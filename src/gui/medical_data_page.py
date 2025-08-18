#!/usr/bin/env python3
"""
SleepSense - Medical Device GUI Application
Medical Data Page - Displays medical channels with mock waves
"""

import os
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QGroupBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

import pyqtgraph as pg

from ..auth.user_manager import JSONUserManager
from ..utils.logger import get_logger

class MedicalDataPage(QWidget):
    """Medical data page widget displaying various medical channels with mock waves"""
    
    def __init__(self, auth_manager: JSONUserManager, settings, main_window):
        super().__init__()
        self.auth_manager = auth_manager
        self.settings = settings
        self.main_window = main_window
        self.logger = get_logger(__name__)
        
        # Initialize data
        self.sample_rate = 64
        self.time_window = 60  # 1 minute window
        self.time_data = np.linspace(0, self.time_window, self.sample_rate * self.time_window)
        
        # Store plot widgets and curves (for common graph)
        self.plot_widgets = {}
        self.plot_curves = {}
        
        # Load real sleep data
        self.sleep_data = None
        self.current_data_index = 0
        
        self.setup_ui()
        self.load_sleep_data()
        self.update_plots()
        
        # Setup timer for automatic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_update)
        self.update_timer.start(3000)  # Update every 3 seconds
    
    def auto_update(self):
        """Automatically update data and plots"""
        if self.sleep_data:
            self.current_data_index = (self.current_data_index + 1) % len(self.sleep_data)
            self.update_parameters_display()
            self.update_plots()
            self.update_footer_info()
    
    def update_footer_info(self):
        """Update footer information"""
        if hasattr(self, 'footer_data_label') and self.sleep_data:
            current_data = self.sleep_data[self.current_data_index]
            time_key = list(current_data.keys())[0] if current_data else 'N/A'
            data_info = f"Data: {self.current_data_index + 1}/{len(self.sleep_data)} | Time: {time_key}"
            self.footer_data_label.setText(data_info)
    
    def setup_ui(self):
        """Setup the medical data visualization interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Header
        self.setup_header(main_layout)
        
        # Main content area with splitter
        content_splitter = QHBoxLayout()
        content_splitter.setSpacing(20)
        
        # Left panel - Parameters list
        left_panel = self.create_parameters_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Common graph
        right_panel = self.create_common_graph_panel()
        content_splitter.addWidget(right_panel)
        
        # Set proportions (30% left, 70% right)
        content_splitter.setStretch(0, 3)
        content_splitter.setStretch(1, 7)
        
        main_layout.addLayout(content_splitter)
        
        # Footer
        self.setup_footer(main_layout)
    
    def setup_header(self, main_layout):
        """Setup the page header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("Medical Data Monitoring")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Back button
        back_btn = QPushButton("← Back to Login")
        back_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        back_btn.clicked.connect(self.go_back_to_login)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(back_btn)
        
        main_layout.addWidget(header_frame)
    
    def create_parameters_panel(self):
        """Create the left panel with parameters list"""
        panel = QFrame()
        panel.setObjectName("parameters-panel")
        panel.setStyleSheet("""
            #parameters-panel {
                background: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Store layout reference for updates
        self.parameters_layout = layout
        
        # Title with current time
        title_label = QLabel("Parameters")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(title_label)
        
        # Current time display
        self.time_display_label = QLabel("Time: Loading...")
        self.time_display_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                font-style: italic;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(self.time_display_label)
        
        # Parameters list - will be populated with real data
        parameters = self.get_current_parameter_values()
        
        for param_name, value, color in parameters:
            param_widget = self.create_parameter_item(param_name, value, color)
            layout.addWidget(param_widget)
        
        layout.addStretch()
        
        # Add refresh button
        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
        
        return panel
    
    def create_parameter_item(self, name, value, color):
        """Create a single parameter item widget"""
        item_widget = QFrame()
        item_widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #3498db;
                background: #f8f9fa;
            }
        """)
        
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Parameter name
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(value_label)
        
        return item_widget
    
    def load_sleep_data(self):
        """Load sleep data from the file"""
        try:
            file_path = "sleep_report_simulated.txt"
            if not os.path.exists(file_path):
                self.logger.error(f"Sleep data file not found: {file_path}")
                return
            
            # Read the data file
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Parse header and data
            if len(lines) < 2:
                self.logger.error("Invalid sleep data file format")
                return
            
            header = lines[0].strip().split('\t')
            data_lines = [line.strip().split('\t') for line in lines[1:] if line.strip()]
            
            # Convert to structured data
            self.sleep_data = []
            for line in data_lines:
                if len(line) == len(header):
                    data_point = {}
                    for i, col in enumerate(header):
                        try:
                            if col in ['SW', 'Position']:
                                data_point[col] = line[i]  # Keep as string
                            else:
                                data_point[col] = float(line[i])
                        except ValueError:
                            data_point[col] = 0.0
                    self.sleep_data.append(data_point)
            
            self.logger.info(f"Loaded {len(self.sleep_data)} sleep data points")
            
        except Exception as e:
            self.logger.error(f"Error loading sleep data: {e}")
            self.sleep_data = []
    
    def get_current_parameter_values(self):
        """Get current parameter values from sleep data"""
        if not self.sleep_data or self.current_data_index >= len(self.sleep_data):
            return self.get_default_values()
        
        data = self.sleep_data[self.current_data_index]
        
        # Convert data to display format
        sw_status = "Awake" if data.get('SW', 'Wake') == 'Wake' else "Sleep"
        snore_value = f"{data.get('Snore', 0):.1f}"
        flow_value = f"{data.get('Flow', 0):.2f} OCMHFR"
        spo2_events = f"{int(data.get('SpO2_Events', 0))}"
        hr_value = f"{data.get('HR', 0):.1f} BPM"
        position_value = data.get('Position', 'Unknown')
        activity_value = f"{data.get('Activity', 0):.1f}"
        spo2_value = f"{data.get('SpO2', 0):.1f}%"
        thorax_value = f"{data.get('Thorax', 0):.2f}"
        abdomen_value = f"{data.get('Abdomen', 0):.2f}"
        pleth_value = f"{data.get('Pleth', 0):.2f}"
        pulse_value = f"{int(data.get('Pulse', 0))} BPM"
        
        return [
            ("SW (Sleep/Wake)", sw_status, "#27ae60"),
            ("Snore", snore_value, "#e74c3c"),
            ("Flow", flow_value, "#3498db"),
            ("SpO2 Events", spo2_events, "#9b59b6"),
            ("HR (Heart Rate)", hr_value, "#e67e22"),
            ("Position", position_value, "#1abc9c"),
            ("Activity", activity_value, "#f39c12"),
            ("SpO2", spo2_value, "#34495e"),
            ("Thorax", thorax_value, "#95a5a6"),
            ("Abdomen", abdomen_value, "#e74c3c"),
            ("Pleth", pleth_value, "#27ae60"),
            ("Pulse", pulse_value, "#3498db")
        ]
    
    def get_default_values(self):
        """Get default parameter values when no data is available"""
        return [
            ("SW (Sleep/Wake)", "No Data", "#27ae60"),
            ("Snore", "0.0", "#e74c3c"),
            ("Flow", "0.00 OCMHFR", "#3498db"),
            ("SpO2 Events", "0", "#9b59b6"),
            ("HR (Heart Rate)", "0.0 BPM", "#e67e22"),
            ("Position", "Unknown", "#1abc9c"),
            ("Activity", "0.0", "#f39c12"),
            ("SpO2", "0.0%", "#34495e"),
            ("Thorax", "0.00", "#95a5a6"),
            ("Abdomen", "0.00", "#e74c3c"),
            ("Pleth", "0.00", "#27ae60"),
            ("Pulse", "0 BPM", "#3498db")
        ]
    
    def refresh_data(self):
        """Refresh the data display"""
        if self.sleep_data:
            # Move to next data point (cycling through the data)
            self.current_data_index = (self.current_data_index + 1) % len(self.sleep_data)
            self.update_parameters_display()
            self.update_plots()
            self.update_footer_info()
    
    def update_parameters_display(self):
        """Update the parameters display with current values"""
        if hasattr(self, 'parameters_layout'):
            # Update time display
            if hasattr(self, 'time_display_label') and self.sleep_data:
                current_data = self.sleep_data[self.current_data_index]
                time_key = list(current_data.keys())[0] if current_data else 'N/A'
                self.time_display_label.setText(f"Time: {time_key}")
            
            # Clear existing parameters
            for i in reversed(range(self.parameters_layout.count() - 3)):  # Keep title, time display, and refresh button
                widget = self.parameters_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Add new parameters
            parameters = self.get_current_parameter_values()
            for param_name, value, color in parameters:
                param_widget = self.create_parameter_item(param_name, value, color)
                self.parameters_layout.insertWidget(2, param_widget)  # Insert after title and time display
    
    def create_common_graph_panel(self):
        """Create the right panel with common graph for all waves"""
        panel = QFrame()
        panel.setObjectName("graph-panel")
        panel.setStyleSheet("""
            #graph-panel {
                background: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("All Parameters - Combined View")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(title_label)
        
        # Create the common graph
        self.create_common_graph(layout)
        
        return panel
    
    def create_common_graph(self, layout):
        """Create a common graph showing all parameters"""
        # Create plot widget
        self.common_plot = pg.PlotWidget()
        self.common_plot.setBackground('w')
        self.common_plot.showGrid(x=True, y=True, alpha=0.3)
        self.common_plot.setLabel('left', 'Amplitude', color='#2c3e50', size='12pt')
        self.common_plot.setLabel('bottom', 'Data Points (0-841)', color='#2c3e50', size='12pt')
        self.common_plot.setTitle('All Medical Parameters - Real Data (842 Points)', size='14pt', color='#2c3e50')
        
        # Set plot size
        self.common_plot.setMinimumHeight(400)
        self.common_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Style the plot
        self.common_plot.getAxis('left').setTextPen(pg.mkPen(color='#2c3e50'))
        self.common_plot.getAxis('bottom').setTextPen(pg.mkPen(color='#2c3e50'))
        self.common_plot.getAxis('left').setPen(pg.mkPen(color='#bdc3c7', width=1))
        self.common_plot.getAxis('bottom').setPen(pg.mkPen(color='#bdc3c7', width=1))
        
        # Store curves for all parameters
        self.common_curves = {}
        
        # Add curves for each parameter with different colors
        parameter_colors = {
            'sw': '#27ae60',
            'snore': '#e74c3c', 
            'flow': '#3498db',
            'spo2_events': '#9b59b6',
            'hr': '#e67e22',
            'position': '#1abc9c',
            'activity': '#f39c12',
            'spo2': '#34495e',
            'thorax': '#95a5a6',
            'abdomen': '#e74c3c',
            'pleth': '#27ae60',
            'pulse': '#3498db'
        }
        
        for param_name, color in parameter_colors.items():
            curve = self.common_plot.plot(self.time_data, np.zeros_like(self.time_data), 
                                        pen=pg.mkPen(color, width=2), name=param_name)
            self.common_curves[param_name] = curve
        
        # Add legend
        self.common_plot.addLegend()
        
        layout.addWidget(self.common_plot)
    
    # Old channel plots methods removed - now using common graph
    
    def setup_footer(self, main_layout):
        """Setup the page footer"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        footer_layout = QHBoxLayout(footer_frame)
        
        # Status info
        status_label = QLabel("Monitoring Active - All Channels Online")
        status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Time info
        time_label = QLabel("Session: 00:05:23")
        time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        footer_layout.addWidget(status_label)
        footer_layout.addStretch()
        
        # Current data info
        if self.sleep_data:
            current_data = self.sleep_data[self.current_data_index]
            time_key = list(current_data.keys())[0] if current_data else 'N/A'
            data_info = f"Data: {self.current_data_index + 1}/{len(self.sleep_data)} | Time: {time_key}"
        else:
            data_info = "No data loaded"
        
        data_label = QLabel(data_info)
        data_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        self.footer_data_label = data_label  # Store reference for updates
        footer_layout.addWidget(data_label)
        
        footer_layout.addWidget(time_label)
        
        main_layout.addWidget(footer_frame)
    
    # Mock data generation removed - now using real sleep data from file
    
    def update_plots(self):
        """Update all plots with current data"""
        if not self.sleep_data:
            return
        
        # Create time series data for all 842 data points
        time_points = np.arange(len(self.sleep_data))
        
        # Extract actual data values from the sleep data
        sw_values = [1 if data.get('SW') == 'Sleep' else 0 for data in self.sleep_data]
        snore_values = [data.get('Snore', 0) for data in self.sleep_data]
        flow_values = [data.get('Flow', 0) for data in self.sleep_data]
        spo2_events_values = [data.get('SpO2_Events', 0) for data in self.sleep_data]
        hr_values = [data.get('HR', 0) for data in self.sleep_data]
        position_values = [0.5 for data in self.sleep_data]  # Neutral position for all
        activity_values = [data.get('Activity', 0) for data in self.sleep_data]
        spo2_values = [data.get('SpO2', 0) for data in self.sleep_data]
        thorax_values = [data.get('Thorax', 0) for data in self.sleep_data]
        abdomen_values = [data.get('Abdomen', 0) for data in self.sleep_data]
        pleth_values = [data.get('Pleth', 0) for data in self.sleep_data]
        pulse_values = [data.get('Pulse', 0) for data in self.sleep_data]
        
        # Update common graph with all parameters using real data
        if hasattr(self, 'common_curves'):
            parameter_data = {
                'sw': sw_values,
                'snore': snore_values,
                'flow': flow_values,
                'spo2_events': spo2_events_values,
                'hr': hr_values,
                'position': position_values,
                'activity': activity_values,
                'spo2': spo2_values,
                'thorax': thorax_values,
                'abdomen': abdomen_values,
                'pleth': pleth_values,
                'pulse': pulse_values
            }
            
            for param_name, data in parameter_data.items():
                if param_name in self.common_curves:
                    curve = self.common_curves[param_name]
                    curve.setData(time_points, data)
    
    def go_back_to_login(self):
        """Go back to the login page"""
        if hasattr(self.main_window, 'stacked_widget'):
            # Find the login page index and switch to it
            for i in range(self.main_window.stacked_widget.count()):
                widget = self.main_window.stacked_widget.widget(i)
                if hasattr(widget, 'auth_manager'):  # This is the login page
                    self.main_window.stacked_widget.setCurrentIndex(i)
                    break
