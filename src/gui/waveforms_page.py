"""
Simple Waveforms page for SleepSense application
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
import os

class WaveformsPage(QWidget):
    """Simple Waveforms page widget"""
    
    def __init__(self, auth_manager: JSONUserManager, settings, main_window):
        super().__init__()
        self.auth_manager = auth_manager
        self.settings = settings
        self.main_window = main_window
        self.logger = get_logger(__name__)
        
        # Initialize data
        self.sample_rate = 10  # 10 samples per second
        self.recording_duration = 300  # 5 minutes
        self.time_data = np.linspace(0, self.recording_duration, self.recording_duration * self.sample_rate)
        
        # Parameter definitions - matching DATA0025.TXT columns for SleepSense software
        self.parameters = {
            'body_position': {'name': 'Body Position', 'color': '#2ecc71', 'unit': ''},
            'pulse': {'name': 'Pulse', 'color': '#3498db', 'unit': 'bpm'},
            'spo2': {'name': 'SpO2', 'color': '#e74c3c', 'unit': '%'},
            'airflow': {'name': 'Airflow', 'color': '#2980b9', 'unit': 'L/min'},
            'unknown1': {'name': 'Unknown 1', 'color': '#9b59b6', 'unit': ''},
            'unknown2': {'name': 'Unknown 2', 'color': '#16a085', 'unit': ''},
            'unknown3': {'name': 'Unknown 3', 'color': '#f39c12', 'unit': ''}
        }
        
        # Data storage
        self.parameter_data = {}
        self.main_plot = None
        self.plot_curves = {}
        self.loaded_data = []
        
        self.setup_ui()
        self.load_data_from_file()
        self.setup_main_plot()
        
        # Initialize time slider after data is loaded
        if hasattr(self, 'time_slider') and hasattr(self, 'loaded_data'):
            max_pos = max(0, len(self.loaded_data) - 10)
            self.time_slider.setMaximum(max_pos)
            self.time_slider.setValue(0)
            self.update_time_window()  # Show first 1-second window
        
        # Log the final state
        if hasattr(self, 'loaded_data') and len(self.loaded_data) > 0:
            self.logger.info(f"✅ Initialization complete: {len(self.loaded_data):,} real data points loaded")
        else:
            self.logger.warning("⚠️ Initialization complete: No real data loaded, using dummy data")
    
    def setup_ui(self):
        """Setup the waveforms page user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title
        title = QLabel("SleepSense - Sleep Study Waveforms (DATA0025.TXT)")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; text-align: center;")
        main_layout.addWidget(title)
        
        # Control panel
        self.create_control_panel(main_layout)
        
        # Main plot area
        self.create_main_plot_area(main_layout)
        
        # Footer
        self.create_footer(main_layout)
    
    def create_control_panel(self, main_layout):
        """Create the control panel"""
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        control_layout = QHBoxLayout(control_frame)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Real Data")
        refresh_button.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        refresh_button.clicked.connect(self.refresh_data)
        control_layout.addWidget(refresh_button)
        
        # Force real data button
        real_data_button = QPushButton("Show Real Data")
        real_data_button.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        real_data_button.clicked.connect(self.force_real_data_display)
        control_layout.addWidget(real_data_button)
        
        # Generate dummy data button
        dummy_button = QPushButton("Generate Dummy Data")
        dummy_button.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        dummy_button.clicked.connect(self.generate_dummy_data)
        control_layout.addWidget(dummy_button)
        
        control_layout.addStretch()
        main_layout.addWidget(control_frame)
    
    def create_main_plot_area(self, main_layout):
        """Create the main plot area with all waves"""
        plot_frame = QFrame()
        plot_frame.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        # Use horizontal layout to put plot and toggle buttons side by side
        plot_layout = QHBoxLayout(plot_frame)
        
        # Left side: Plot
        plot_left = QVBoxLayout()
        
        # Plot title
        plot_title = QLabel("SleepSense - DATA0025.TXT Parameters - Parallel Display")
        plot_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        plot_left.addWidget(plot_title)
        
        # Create main plot widget
        self.main_plot = pg.PlotWidget()
        self.main_plot.setMinimumHeight(600)
        self.main_plot.setMinimumWidth(800)
        self.main_plot.setBackground('w')
        self.main_plot.showGrid(x=True, y=True, alpha=0.3)
        self.main_plot.setLabel('left', 'Amplitude')
        self.main_plot.setLabel('bottom', 'Time (seconds)')
        self.main_plot.setTitle('SleepSense - DATA0025.TXT Sleep Study Parameters - Parallel Waves', size='14pt')
        
        plot_left.addWidget(self.main_plot)
        plot_layout.addLayout(plot_left)
        
        # Right side: Toggle buttons
        toggle_frame = QFrame()
        toggle_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        toggle_frame.setMaximumWidth(200)
        toggle_layout = QVBoxLayout(toggle_frame)
        
        # Toggle buttons title
        toggle_title = QLabel("Wave Controls")
        toggle_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-align: center;")
        toggle_layout.addWidget(toggle_title)
        
        # Create toggle buttons for each parameter
        self.parameter_toggles = {}
        for param_key, param_info in self.parameters.items():
            toggle_btn = QPushButton(param_info['name'])
            toggle_btn.setCheckable(True)  # Make it a toggle button
            toggle_btn.setChecked(True)    # Start with all waves visible
            toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {param_info['color']};
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 6px;
                    font-weight: bold;
                    margin: 5px 0px;
                }}
                QPushButton:checked {{
                    background: {param_info['color']};
                    border: 2px solid #2c3e50;
                }}
                QPushButton:!checked {{
                    background: #95a5a6;
                    border: 2px solid #7f8c8d;
                }}
                QPushButton:hover {{
                    background: {param_info['color']};
                    opacity: 0.8;
                }}
            """)
            
            # Connect toggle to wave visibility
            toggle_btn.clicked.connect(lambda checked, key=param_key: self.toggle_wave_visibility(key, checked))
            
            self.parameter_toggles[param_key] = toggle_btn
            toggle_layout.addWidget(toggle_btn)
        
        # Add show all/hide all buttons
        toggle_layout.addSpacing(20)
        
        show_all_btn = QPushButton("Show All")
        show_all_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        show_all_btn.clicked.connect(self.show_all_waves)
        toggle_layout.addWidget(show_all_btn)
        
        hide_all_btn = QPushButton("Hide All")
        hide_all_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        hide_all_btn.clicked.connect(self.hide_all_waves)
        toggle_layout.addWidget(hide_all_btn)
        
        toggle_layout.addStretch()
        plot_layout.addWidget(toggle_frame)
        
        # Time window controls
        time_controls_layout = QHBoxLayout()
        
        # Time window label
        time_label = QLabel("Time Window: 1 second (10 samples)")
        time_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        time_controls_layout.addWidget(time_label)
        
        # Time slider
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(max(0, len(self.loaded_data) - 10))  # Max position to show last 10 samples
        self.time_slider.setValue(0)
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
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #3498db;
                border-radius: 4px;
            }
        """)
        self.time_slider.valueChanged.connect(self.update_time_window)
        time_controls_layout.addWidget(self.time_slider)
        
        # Current time display
        self.current_time_label = QLabel("Time: 0.0s - 1.0s")
        self.current_time_label.setStyleSheet("font-weight: bold; color: #2c3e50; min-width: 150px;")
        time_controls_layout.addWidget(self.current_time_label)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        # Previous 1 second button
        prev_btn = QPushButton("⏮ Previous 1s")
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        prev_btn.clicked.connect(self.previous_second)
        nav_layout.addWidget(prev_btn)
        
        # Next 1 second button
        next_btn = QPushButton("Next 1s ⏭")
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        next_btn.clicked.connect(self.next_second)
        nav_layout.addWidget(next_btn)
        
        # Jump to start button
        start_btn = QPushButton("⏹ Start")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        start_btn.clicked.connect(self.jump_to_start)
        nav_layout.addWidget(start_btn)
        
        # Jump to end button
        end_btn = QPushButton("End ⏹")
        end_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        end_btn.clicked.connect(self.jump_to_end)
        nav_layout.addWidget(end_btn)
        
        time_controls_layout.addLayout(nav_layout)
        main_layout.addLayout(time_controls_layout)
        
        main_layout.addWidget(plot_frame)
    
    def create_footer(self, main_layout):
        """Create the footer section"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background: #2c3e50;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        footer_layout = QHBoxLayout(footer_frame)
        
        # Data info
        data_info = QLabel("Data Points: 0")
        data_info.setStyleSheet("color: white; font-size: 12px;")
        self.data_info_label = data_info
        footer_layout.addWidget(data_info)
        
        # Status
        status = QLabel("Status: Ready")
        status.setStyleSheet("color: white; font-size: 12px;")
        self.status_label = status
        footer_layout.addWidget(status)
        
        # Time info
        time_info = QLabel("Duration: 0 min")
        time_info.setStyleSheet("color: white; font-size: 12px;")
        self.time_info_label = time_info
        footer_layout.addWidget(time_info)
        
        footer_layout.addStretch()
        main_layout.addWidget(footer_frame)
    
    def load_data_from_file(self):
        """Load data from DATA0025.TXT file"""
        try:
            # Try to load DATA0025.TXT file
            file_path = "DATA0025.TXT"
            if not os.path.exists(file_path):
                self.logger.error("DATA0025.TXT file not found, generating dummy data")
                self.generate_dummy_data()
                return
            
            self.logger.info(f"Loading data from {file_path}")
            
            # Read the file using pandas for better performance
            import pandas as pd
            df = pd.read_csv(file_path, header=None, sep=',')
            
            # Map columns from DATA0025.TXT to our parameters
            # DATA0025.TXT has 10 columns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            # User specification: Col1=Unknown, Col2=Body Position, Col3=Pulse, Col4=SpO2, Col7=Airflow
            self.loaded_data = []
            
            for index, row in df.iterrows():
                try:
                    data_point = {
                        'body_position': int(row[1]),    # Column 1: Body Position
                        'pulse': int(row[2]),            # Column 2: Pulse (bpm)
                        'spo2': int(row[3]),             # Column 3: SpO2 (%)
                        'airflow': int(row[6]),          # Column 6: Airflow (L/min)
                        'unknown1': int(row[0]),         # Column 0: Unknown 1
                        'unknown2': int(row[4]),         # Column 4: Unknown 2
                        'unknown3': int(row[5])          # Column 5: Unknown 3
                    }
                    self.loaded_data.append(data_point)
                except (ValueError, IndexError):
                    continue  # Skip lines with invalid data
            
            self.logger.info(f"Loaded {len(self.loaded_data)} data points from {file_path}")
            
            # Extract data for each parameter
            if self.loaded_data:
                self.extract_parameter_data()
            else:
                self.logger.warning("No valid data loaded, using dummy data")
                self.generate_dummy_data()
                
        except Exception as e:
            self.logger.error(f"Error loading data file: {e}")
            self.generate_dummy_data()
    
    def extract_parameter_data(self):
        """Extract data for each parameter from loaded data"""
        if not self.loaded_data:
            self.logger.warning("No loaded data available")
            return
        
        self.logger.info(f"Extracting data from {len(self.loaded_data)} loaded data points")
        
        # Create smooth time points: 10 data points per second
        total_data_points = len(self.loaded_data)
        total_seconds = total_data_points / 10  # 10 samples per second
        
        # Create evenly spaced time points
        self.time_data = np.linspace(0, total_seconds, total_data_points)
        self.logger.info(f"Created time data: {len(self.time_data)} points from 0 to {total_seconds:.2f} seconds")
        
        # Extract data for each parameter
        for param_key in self.parameters.keys():
            if param_key == 'body_position':
                values = [data['body_position'] for data in self.loaded_data]
            elif param_key == 'pulse':
                values = [data['pulse'] for data in self.loaded_data]
            elif param_key == 'spo2':
                values = [data['spo2'] for data in self.loaded_data]
            elif param_key == 'airflow':
                values = [data['airflow'] for data in self.loaded_data]
            elif param_key == 'unknown1':
                values = [data['unknown1'] for data in self.loaded_data]
            elif param_key == 'unknown2':
                values = [data['unknown2'] for data in self.loaded_data]
            elif param_key == 'unknown3':
                values = [data['unknown3'] for data in self.loaded_data]
            
            # Convert to numpy array for plotting
            self.parameter_data[param_key] = np.array(values)
            
            # Log data ranges
            if values:
                min_val = min(values)
                max_val = max(values)
                self.logger.info(f"{param_key}: {min_val} to {max_val} (array shape: {self.parameter_data[param_key].shape})")
            else:
                self.logger.warning(f"No values extracted for {param_key}")
        
        self.logger.info(f"Extracted data for {len(self.parameter_data)} parameters")
        self.logger.info(f"Time range: 0.00 to {total_seconds:.2f} seconds")
        self.logger.info(f"Data rate: 10 samples per second")
        self.logger.info(f"Total data points from DATA0025.TXT: {total_data_points:,}")
        
        # Update footer info
        self.update_footer_info()
    
    def generate_dummy_data(self):
        """Generate realistic dummy data for all parameters"""
        # Check if we already have real data loaded
        if hasattr(self, 'loaded_data') and len(self.loaded_data) > 0:
            self.logger.info("Real data already loaded, skipping dummy data generation")
            return
        
        self.logger.info("Generating dummy data...")
        
        # Create time data (5 minutes)
        self.time_data = np.linspace(0, 300, 3000)  # 300 seconds, 10 samples per second
        
        # Generate data for each parameter
        for param_key, param_info in self.parameters.items():
            if param_key == 'spo2':
                # SpO2: 95-100% with realistic variation
                base_value = 98
                variation = np.random.normal(0, 0.5, len(self.time_data))
                # Add some periodic drops (apnea events)
                apnea_events = np.zeros_like(self.time_data)
                for i in range(5):  # 5 apnea events
                    start_idx = np.random.randint(0, len(self.time_data) - 100)
                    duration = np.random.randint(20, 60)  # 20-60 seconds
                    apnea_events[start_idx:start_idx + duration] = np.random.normal(-3, 1, min(duration, len(self.time_data) - start_idx))
                
                self.parameter_data[param_key] = np.clip(base_value + variation + apnea_events, 90, 100)
                
            elif param_key == 'pulse':
                # Pulse: 60-100 bpm with realistic variation
                base_value = 75
                variation = np.random.normal(0, 3, len(self.time_data))
                # Add some heart rate variability
                hrv = np.sin(2 * np.pi * 0.1 * self.time_data) * 5
                self.parameter_data[param_key] = np.clip(base_value + variation + hrv, 55, 105)
                
            elif param_key == 'body_position':
                # Position: discrete values (0=Supine, 1=Left, 2=Right, 3=Upright)
                positions = np.random.choice([0, 1, 2, 3], len(self.time_data), p=[0.6, 0.15, 0.15, 0.1])
                # Make positions change less frequently
                for i in range(1, len(positions)):
                    if np.random.random() > 0.99:  # 1% chance to change
                        positions[i] = positions[i-1]
                self.parameter_data[param_key] = positions
                
            elif param_key == 'airflow':
                # Airflow: respiratory pattern with some obstruction
                base_freq = 0.2  # 12 breaths per minute
                amplitude = 50
                base_flow = amplitude * np.sin(2 * np.pi * base_freq * self.time_data)
                
                # Add some obstruction events
                obstruction = np.zeros_like(self.time_data)
                for i in range(3):  # 3 obstruction events
                    start_idx = np.random.randint(0, len(self.time_data) - 80)
                    duration = np.random.randint(30, 80)  # 30-80 seconds
                    obstruction[start_idx:start_idx + duration] = np.random.normal(-20, 5, min(duration, len(self.time_data) - start_idx))
                
                self.parameter_data[param_key] = base_flow + obstruction + np.random.normal(0, 3, len(self.time_data))
                
            elif param_key == 'abdomen':
                # Abdomen: respiratory movement
                base_freq = 0.2  # 12 breaths per minute
                amplitude = 30
                base_movement = amplitude * np.sin(2 * np.pi * base_freq * self.time_data)
                self.parameter_data[param_key] = base_movement + np.random.normal(0, 2, len(self.time_data))
                
            elif param_key == 'snoring':
                # Snoring: intermittent events
                snoring = np.zeros_like(self.time_data)
                for i in range(8):  # 8 snoring episodes
                    start_idx = np.random.randint(0, len(self.time_data) - 40)
                    duration = np.random.randint(10, 40)  # 10-40 seconds
                    snoring[start_idx:start_idx + duration] = np.random.uniform(10, 40, min(duration, len(self.time_data) - start_idx))
                self.parameter_data[param_key] = snoring + np.random.normal(0, 1, len(self.time_data))
                
            elif param_key == 'body_move':
                # Body movement: occasional events
                movement = np.zeros_like(self.time_data)
                for i in range(6):  # 6 movement events
                    start_idx = np.random.randint(0, len(self.time_data) - 20)
                    duration = np.random.randint(5, 20)  # 5-20 seconds
                    movement[start_idx:start_idx + duration] = np.random.uniform(15, 35, min(duration, len(self.time_data) - start_idx))
                self.parameter_data[param_key] = movement + np.random.normal(0, 0.5, len(self.time_data))
        
        self.logger.info("Dummy data generated successfully")
        self.update_footer_info()
    
    def setup_main_plot(self):
        """Setup the main plot with all waves"""
        self.logger.info("Setting up main plot...")
        
        if not self.main_plot:
            self.logger.error("Main plot widget not available")
            return
        
        # Check if we have data
        if not self.parameter_data:
            self.logger.error("No parameter data available for plotting")
            return
        
        if len(self.time_data) == 0:
            self.logger.error("No time data available for plotting")
            return
        
        self.logger.info(f"Available parameters: {list(self.parameter_data.keys())}")
        self.logger.info(f"Time data shape: {self.time_data.shape}")
        
        # Clear existing curves
        self.main_plot.clear()
        self.plot_curves.clear()
        
        # Calculate offsets for parallel display - waves stacked vertically
        offsets = {}
        
        # Calculate offsets to stack waves with proper spacing
        current_offset = 0
        spacing = 100  # Space between waves for clear separation
        
        for param_key in self.parameters.keys():
            if param_key in self.parameter_data:
                data = self.parameter_data[param_key]
                
                # Handle different data types with appropriate scaling
                if param_key in ['body_position', 'unknown1', 'unknown2', 'unknown3']:
                    # Discrete or small range data - scale directly
                    scaled_data = data * 20 + current_offset  # 20 units height
                elif param_key == 'pulse':
                    # Pulse: typically 40-200 bpm - normalize to reasonable range
                    data_min = np.min(data)
                    data_max = np.max(data)
                    if data_max > data_min:
                        normalized_data = (data - data_min) / (data_max - data_min)
                        scaled_data = normalized_data * 80 + current_offset  # 80 units height
                    else:
                        scaled_data = np.full_like(data, current_offset + 40)
                elif param_key == 'spo2':
                    # SpO2: typically 70-100% - normalize to reasonable range
                    data_min = np.min(data)
                    data_max = np.max(data)
                    if data_max > data_min:
                        normalized_data = (data - data_min) / (data_max - data_min)
                        scaled_data = normalized_data * 80 + current_offset  # 80 units height
                    else:
                        scaled_data = np.full_like(data, current_offset + 40)
                elif param_key == 'airflow':
                    # Airflow: respiratory data - normalize to reasonable range
                    data_min = np.min(data)
                    data_max = np.max(data)
                    if data_max > data_min:
                        normalized_data = (data - data_min) / (data_max - data_min)
                        scaled_data = normalized_data * 80 + current_offset  # 80 units height
                    else:
                        scaled_data = np.full_like(data, current_offset + 40)
                else:
                    # Default case - normalize to 0-1 then scale
                    data_min = np.min(data)
                    data_max = np.max(data)
                    if data_max > data_min:
                        normalized_data = (data - data_min) / (data_max - data_min)
                        scaled_data = normalized_data * 80 + current_offset  # 80 units height
                    else:
                        # Handle constant data
                        scaled_data = np.full_like(data, current_offset + 40)
                
                self.parameter_data[param_key] = scaled_data
                offsets[param_key] = current_offset
                current_offset += spacing  # Move to next parallel line
        
        # Plot each parameter as a continuous wave parallel to others
        for param_key, param_info in self.parameters.items():
            if param_key in self.parameter_data:
                data = self.parameter_data[param_key]
                color = param_info['color']
                
                # Debug logging
                self.logger.info(f"Plotting {param_key}: data range {np.min(data):.2f} to {np.max(data):.2f}")
                
                # Create smooth curve - plot all data points as one continuous wave
                curve = self.main_plot.plot(self.time_data, data, 
                                          pen=pg.mkPen(color, width=2), 
                                          name=param_info['name'])
                self.plot_curves[param_key] = curve
                
                # Add label for the wave at the right side
                text = pg.TextItem(text=param_info['name'], color=color)
                text.setPos(self.time_data[-1] + 0.5, offsets[param_key] + 30)
                self.main_plot.addItem(text)
        
        # Set plot ranges for parallel wave display
        self.main_plot.setXRange(0, self.time_data[-1])
        self.main_plot.setYRange(-20, current_offset + 20)
        
        # Debug logging for plot ranges
        self.logger.info(f"Plot X range: 0 to {self.time_data[-1]:.2f}")
        self.logger.info(f"Plot Y range: -20 to {current_offset + 20}")
        
        # Update plot
        self.main_plot.update()
        
        self.logger.info("Main plot setup completed with parallel waves")
        self.logger.info(f"Plotting {len(self.time_data)} data points as {len(self.parameters)} parallel waves")
        self.logger.info(f"Wave spacing: {spacing} units between each wave")
    
    def toggle_wave_visibility(self, param_key, visible):
        """Toggle visibility of a specific wave"""
        if param_key in self.plot_curves:
            curve = self.plot_curves[param_key]
            if visible:
                curve.show()
                self.logger.info(f"Showing {param_key} wave")
            else:
                curve.hide()
                self.logger.info(f"Hiding {param_key} wave")
    
    def show_all_waves(self):
        """Show all waves"""
        for param_key, toggle_btn in self.parameter_toggles.items():
            toggle_btn.setChecked(True)
            if param_key in self.plot_curves:
                self.plot_curves[param_key].show()
        self.logger.info("Showing all waves")
    
    def hide_all_waves(self):
        """Hide all waves"""
        for param_key, toggle_btn in self.parameter_toggles.items():
            toggle_btn.setChecked(False)
            if param_key in self.plot_curves:
                self.plot_curves[param_key].hide()
        self.logger.info("Hiding all waves")
    
    def update_footer_info(self):
        """Update footer information"""
        if hasattr(self, 'data_info_label'):
            num_points = len(self.time_data) if hasattr(self, 'time_data') else 0
            self.data_info_label.setText(f"Data Points: {num_points:,}")
        
        if hasattr(self, 'time_info_label'):
            duration = self.time_data[-1] if hasattr(self, 'time_data') and len(self.time_data) > 0 else 0
            self.time_info_label.setText(f"Duration: {duration:.1f} sec | Rate: 10 Hz")
        
        if hasattr(self, 'status_label'):
            self.status_label.setText("Status: DATA0025.TXT Loaded")
    
    def refresh_data(self):
        """Refresh data from file and update display"""
        self.logger.info("Refreshing data...")
        self.load_data_from_file()
        self.extract_parameter_data()
        
        # Update time slider for new data
        if hasattr(self, 'time_slider') and hasattr(self, 'loaded_data'):
            max_pos = max(0, len(self.loaded_data) - 10)
            self.time_slider.setMaximum(max_pos)
            self.time_slider.setValue(0)
            self.update_time_window()  # Show first 1-second window
        
        self.logger.info("Data refresh completed")
    
    def force_real_data_display(self):
        """Force display of real data from DATA0025.TXT"""
        self.logger.info("Forcing display of real DATA0025.TXT data...")
        self.load_data_from_file()
        self.setup_main_plot()
        self.logger.info("Real data display forced")

    def update_time_window(self):
        """Update the time window display based on slider position"""
        if not hasattr(self, 'loaded_data') or len(self.loaded_data) == 0:
            return
            
        current_pos = self.time_slider.value()
        start_time = current_pos / 10.0  # 10 samples per second
        end_time = (current_pos + 10) / 10.0
        
        # Update time label
        self.current_time_label.setText(f"Time: {start_time:.1f}s - {end_time:.1f}s")
        
        # Update plot to show only the current 1-second window
        self.update_plot_window(current_pos)
        
        self.logger.info(f"Time window updated: {start_time:.1f}s to {end_time:.1f}s (position {current_pos})")
    
    def update_plot_window(self, start_index):
        """Update the plot to show only the specified time window"""
        if not hasattr(self, 'main_plot') or not hasattr(self, 'parameter_data'):
            return
            
        # Calculate the end index (1 second = 10 samples)
        end_index = min(start_index + 10, len(self.loaded_data))
        
        # Extract time data for the window
        window_time = self.time_data[start_index:end_index]
        
        # Clear existing plots
        self.main_plot.clear()
        
        # Plot each parameter for the current time window
        current_offset = 0
        for param_key in self.parameters.keys():
            if param_key not in self.parameter_data:
                continue
                
            # Get data for the current window
            window_data = self.parameter_data[param_key][start_index:end_index]
            
            if len(window_data) == 0:
                continue
                
            # Scale the data appropriately
            if param_key in ['body_position', 'unknown1', 'unknown2', 'unknown3']:
                scaled_data = window_data * 20 + current_offset
            elif param_key == 'pulse':
                data_min = np.min(window_data)
                data_max = np.max(window_data)
                if data_max > data_min:
                    normalized_data = (window_data - data_min) / (data_max - data_min)
                    scaled_data = normalized_data * 80 + current_offset
                else:
                    scaled_data = np.full_like(window_data, current_offset + 40)
            elif param_key == 'spo2':
                data_min = np.min(window_data)
                data_max = np.max(window_data)
                if data_max > data_min:
                    normalized_data = (window_data - data_min) / (data_max - data_min)
                    scaled_data = normalized_data * 80 + current_offset
                else:
                    scaled_data = np.full_like(window_data, current_offset + 40)
            elif param_key == 'airflow':
                data_min = np.min(window_data)
                data_max = np.max(window_data)
                if data_max > data_min:
                    normalized_data = (window_data - data_min) / (data_max - data_min)
                    scaled_data = normalized_data * 80 + current_offset
                else:
                    scaled_data = np.full_like(window_data, current_offset + 40)
            else:
                data_min = np.min(window_data)
                data_max = np.max(window_data)
                if data_max > data_min:
                    normalized_data = (window_data - data_min) / (data_max - data_min)
                    scaled_data = normalized_data * 80 + current_offset
                else:
                    scaled_data = np.full_like(window_data, current_offset + 40)
            
            # Plot the parameter
            param_name = self.parameters[param_key]['name']
            color = self.parameters[param_key]['color']
            
            # Create plot item
            plot_item = pg.PlotDataItem(
                x=window_time,
                y=scaled_data,
                pen=pg.mkPen(color=color, width=2),
                name=param_name
            )
            
            self.main_plot.addItem(plot_item)
            
            # Add legend item
            legend_item = pg.PlotDataItem(
                pen=pg.mkPen(color=color, width=3),
                name=f"{param_name}: {np.mean(window_data):.1f}"
            )
            
            current_offset += 100  # Space between waves
        
        # Update plot ranges for the window
        self.main_plot.setXRange(0, 1.0)  # 1 second window
        self.main_plot.setYRange(-20, current_offset + 20)
        
        # Update plot title to show current window
        start_time = start_index / 10.0
        end_time = end_index / 10.0
        self.main_plot.setTitle(f'SleepSense - DATA0025.TXT: {start_time:.1f}s to {end_time:.1f}s', size='14pt')
        
        self.logger.info(f"Plot window updated: showing {len(window_time)} samples from position {start_index}")
    
    def previous_second(self):
        """Move to previous 1-second window"""
        current_pos = self.time_slider.value()
        new_pos = max(0, current_pos - 10)  # Move back 10 samples (1 second)
        self.time_slider.setValue(new_pos)
    
    def next_second(self):
        """Move to next 1-second window"""
        current_pos = self.time_slider.value()
        max_pos = max(0, len(self.loaded_data) - 10)
        new_pos = min(max_pos, current_pos + 10)  # Move forward 10 samples (1 second)
        self.time_slider.setValue(new_pos)
    
    def jump_to_start(self):
        """Jump to the beginning of the recording"""
        self.time_slider.setValue(0)
    
    def jump_to_end(self):
        """Jump to the end of the recording"""
        max_pos = max(0, len(self.loaded_data) - 10)
        self.time_slider.setValue(max_pos)
