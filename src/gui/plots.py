"""
Plot management for SleepSense Pro
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeyEvent

from ..config.constants import SIGNAL_COLORS, SIGNAL_OFFSETS


class PlotManager:
    """Manages all plotting functionality"""
    
    def __init__(self, right_panel, settings):
        self.right_panel = right_panel
        self.settings = settings
        self.signals = {}
        self.normalized_signals = {}
        self.setup_plots()
    
    def setup_plots(self):
        """Setup the plot containers"""
        layout = QVBoxLayout(self.right_panel.plots_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Primary Matplotlib Canvas
        self.detailed_fig = Figure(figsize=(20, 14), dpi=100)
        self.detailed_canvas = FigureCanvas(self.detailed_fig)
        layout.addWidget(self.detailed_canvas, 1)
        
        # Secondary Matplotlib Canvas (for comparison mode)
        self.comparison_fig = Figure(figsize=(20, 7), dpi=100)
        self.comparison_canvas = FigureCanvas(self.comparison_fig)
        self.comparison_canvas.setVisible(False)
        layout.addWidget(self.comparison_canvas, 1)
        
        # OSA Analysis Widget
        self.setup_osa_analysis_widget(layout)
        
        # Initialize plot axes
        self.initialize_plot_axes()
        
        # Setup mouse events
        self.setup_mouse_events()
    
    def setup_osa_analysis_widget(self, parent_layout):
        """Setup OSA analysis widget"""
        self.osa_analysis_widget = QWidget()
        self.osa_analysis_layout = QVBoxLayout(self.osa_analysis_widget)
        self.osa_analysis_layout.setContentsMargins(0, 0, 0, 0)
        self.osa_analysis_layout.setSpacing(2)
        
        # OSA Analysis Header
        osa_header = QHBoxLayout()
        osa_header.setContentsMargins(5, 2, 5, 2)
        osa_header.setSpacing(8)
        
        osa_title = QLabel("🏥 OSA Analysis")
        osa_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #c0392b; padding: 2px;")
        osa_header.addWidget(osa_title)
        
        osa_header.addStretch()
        
        # Event detection controls
        self.detect_events_btn = QPushButton("🔍 Detect")
        self.detect_events_btn.setFixedSize(70, 26)
        self.detect_events_btn.setStyleSheet(self.get_osa_button_style("#27ae60"))
        self.detect_events_btn.setToolTip("Detect Apnea/Hypopnea Events")
        self.detect_events_btn.clicked.connect(self.detect_respiratory_events)
        osa_header.addWidget(self.detect_events_btn)
        
        self.clear_events_btn = QPushButton("🗑️")
        self.clear_events_btn.setFixedSize(26, 26)
        self.clear_events_btn.setStyleSheet(self.get_osa_button_style("#e74c3c"))
        self.clear_events_btn.setToolTip("Clear All Detected Events")
        self.clear_events_btn.clicked.connect(self.clear_detected_events)
        osa_header.addWidget(self.clear_events_btn)
        
        self.osa_analysis_layout.addLayout(osa_header)
        
        # Create OSA analysis plots
        self.setup_osa_plots()
        
        self.osa_analysis_widget.setVisible(False)
        parent_layout.addWidget(self.osa_analysis_widget, 1)
    
    def setup_osa_plots(self):
        """Setup OSA analysis plots"""
        from PyQt5.QtWidgets import QSplitter
        
        osa_plots_splitter = QSplitter(Qt.Vertical)
        
        # Airflow plot
        self.osa_airflow_fig = Figure(figsize=(18, 2.2), dpi=100)
        self.osa_airflow_canvas = FigureCanvas(self.osa_airflow_fig)
        self.osa_airflow_canvas.setMaximumHeight(180)
        osa_plots_splitter.addWidget(self.osa_airflow_canvas)
        
        # Thorax + Abdomen plot
        self.osa_effort_fig = Figure(figsize=(18, 2.2), dpi=100)
        self.osa_effort_canvas = FigureCanvas(self.osa_effort_fig)
        self.osa_effort_canvas.setMaximumHeight(180)
        osa_plots_splitter.addWidget(self.osa_effort_canvas)
        
        # SpO2 plot
        self.osa_spo2_fig = Figure(figsize=(18, 2.2), dpi=100)
        self.osa_spo2_canvas = FigureCanvas(self.osa_spo2_fig)
        self.osa_spo2_canvas.setMaximumHeight(180)
        osa_plots_splitter.addWidget(self.osa_spo2_canvas)
        
        # Heart Rate plot
        self.osa_hr_fig = Figure(figsize=(18, 2.2), dpi=100)
        self.osa_hr_canvas = FigureCanvas(self.osa_hr_fig)
        self.osa_hr_canvas.setMaximumHeight(180)
        osa_plots_splitter.addWidget(self.osa_hr_canvas)
        
        self.osa_analysis_layout.addWidget(osa_plots_splitter)
    
    def get_osa_button_style(self, color):
        """Get OSA button style"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.8)};
            }}
        """
    
    def darken_color(self, color, factor=0.9):
        """Darken a hex color"""
        # Simple color darkening - in a real app you'd use proper color manipulation
        color_map = {
            "#27ae60": "#229954",
            "#e74c3c": "#c0392b"
        }
        return color_map.get(color, color)
    
    def initialize_plot_axes(self):
        """Initialize plot axes"""
        # Main plot
        self.detailed_ax = self.detailed_fig.add_subplot(111)
        self.detailed_fig.subplots_adjust(left=0.05, right=0.98, top=0.96, bottom=0.06)
        self.detailed_ax.set_facecolor('#f8f9fa')
        
        # Comparison plot
        self.comparison_ax = self.comparison_fig.add_subplot(111)
        self.comparison_fig.subplots_adjust(left=0.05, right=0.98, top=0.94, bottom=0.08)
        self.comparison_ax.set_facecolor('#f0f8ff')
        
        # OSA analysis plots
        self.initialize_osa_axes()
    
    def initialize_osa_axes(self):
        """Initialize OSA analysis plot axes"""
        try:
            self.osa_airflow_ax = self.osa_airflow_fig.add_subplot(111)
            self.osa_airflow_fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.20)
            self.osa_airflow_ax.set_facecolor('#fff5f5')
            
            self.osa_effort_ax = self.osa_effort_fig.add_subplot(111)
            self.osa_effort_fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.20)
            self.osa_effort_ax.set_facecolor('#f0fff0')
            
            self.osa_spo2_ax = self.osa_spo2_fig.add_subplot(111)
            self.osa_spo2_fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.20)
            self.osa_spo2_ax.set_facecolor('#f0f8ff')
            
            self.osa_hr_ax = self.osa_hr_fig.add_subplot(111)
            self.osa_hr_fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.20)
            self.osa_hr_ax.set_facecolor('#fffaf0')
        except Exception as e:
            print(f"Warning: Could not initialize OSA plots: {e}")
    
    def setup_mouse_events(self):
        """Setup mouse events for region selection"""
        self.selected_regions = []
        self.is_selecting = False
        self.selection_start = None
        self.selection_rect = None
        
        # Connect mouse events
        self.detailed_canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.detailed_canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.detailed_canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
    
    def set_data(self, signals, normalized_signals):
        """Set data for plotting"""
        self.signals = signals
        self.normalized_signals = normalized_signals
        self.update_plot()
    
    def update_plot(self):
        """Update the main plot"""
        if not self.signals or not self.normalized_signals:
            return
        
        self.detailed_ax.clear()
        start_time = self.settings.start_time
        end_time = start_time + self.settings.window_size
        
        # Get time window data
        time_series = self.signals['time']
        start_idx = time_series.searchsorted(start_time, side='left')
        end_idx = time_series.searchsorted(end_time, side='right')
        
        time_window = time_series.iloc[start_idx:end_idx]
        if time_window.empty:
            return
        
        # Plot signals
        self.plot_signals(time_window, start_idx, end_idx)
        
        # Draw selected regions
        self.draw_selected_regions()
        
        # Configure plot appearance
        self.configure_plot_appearance(start_time, end_time)
        
        # Update time display
        self.right_panel.update_time_display(start_time, end_time)
        self.right_panel.update_slider_position(start_time)
        
        self.detailed_canvas.draw_idle()
    
    def plot_signals(self, time_window, start_idx, end_idx):
        """Plot all visible signals"""
        signal_config = self.get_signal_config()
        
        # Set view properties based on frame size
        if self.settings.window_size <= 30:
            line_width, grid_alpha = 1.0, 0.4
        elif self.settings.window_size <= 300:
            line_width, grid_alpha = 0.8, 0.3
        else:
            line_width, grid_alpha = 0.6, 0.2
        
        y_ticks, y_labels = [], []
        for label, config in signal_config.items():
            if config['cb'].isChecked():
                key = config['key']
                offset = self.settings.signal_offsets[key]
                scale = self.settings.signal_scales[key]
                
                data_slice = config['data'].iloc[start_idx:end_idx]
                y_data = (data_slice - 0.5) * scale + offset
                
                self.detailed_ax.plot(time_window, y_data, color=config['color'], 
                                    linewidth=line_width, label=label)
                y_ticks.append(offset)
                y_labels.append(label)
        
        # Set y-axis properties
        self.detailed_ax.set_yticks(y_ticks)
        self.detailed_ax.set_yticklabels(y_labels, fontsize=9)
        self.detailed_ax.set_ylim(-1, max(self.settings.signal_offsets.values()) + 1)
    
    def get_signal_config(self):
        """Get signal configuration for plotting"""
        # Create a simple mock checkbox class
        class MockCheckbox:
            def isChecked(self):
                return True
        
        mock_cb = MockCheckbox()
        
        return {
            'Position': {'data': self.normalized_signals.get('body_pos_n', pd.Series()), 'cb': mock_cb, 'color': '#9e9e9e', 'key': 'body_pos'},
            'Pulse': {'data': self.normalized_signals.get('pulse_n', pd.Series()), 'cb': mock_cb, 'color': '#f44336', 'key': 'pulse'},
            'SpO2': {'data': self.normalized_signals.get('spo2_n', pd.Series()), 'cb': mock_cb, 'color': '#2196f3', 'key': 'spo2'},
            'Airflow': {'data': self.normalized_signals.get('flow_plot', self.normalized_signals.get('flow_n', pd.Series())), 'cb': mock_cb, 'color': '#ff9800', 'key': 'flow'},
            'Snore': {'data': self.normalized_signals.get('snore_n', pd.Series()), 'cb': mock_cb, 'color': '#e91e63', 'key': 'snore'},
            'Thorax': {'data': self.normalized_signals.get('thorax_n', pd.Series()), 'cb': mock_cb, 'color': '#4caf50', 'key': 'thorax'},
            'Abdomen': {'data': self.normalized_signals.get('abdomen_n', pd.Series()), 'cb': mock_cb, 'color': '#cddc39', 'key': 'abdomen'},
            'Pleth': {'data': self.normalized_signals.get('pleth_n', pd.Series()), 'cb': mock_cb, 'color': '#9c27b0', 'key': 'pleth'},
            'Activity': {'data': self.normalized_signals.get('activity_n', pd.Series()), 'cb': mock_cb, 'color': '#ffeb3b', 'key': 'activity'},
            'C3-A2': {'data': self.normalized_signals.get('eeg_c3_n', pd.Series()), 'cb': mock_cb, 'color': '#00bcd4', 'key': 'eeg_c3'},
            'C4-A1': {'data': self.normalized_signals.get('eeg_c4_n', pd.Series()), 'cb': mock_cb, 'color': '#009688', 'key': 'eeg_c4'},
            'F3-A2': {'data': self.normalized_signals.get('eeg_f3_n', pd.Series()), 'cb': mock_cb, 'color': '#8bc34a', 'key': 'eeg_f3'},
            'F4-A1': {'data': self.normalized_signals.get('eeg_f4_n', pd.Series()), 'cb': mock_cb, 'color': '#ffc107', 'key': 'eeg_f4'},
            'O1-A2': {'data': self.normalized_signals.get('eeg_o1_n', pd.Series()), 'cb': mock_cb, 'color': '#795548', 'key': 'eeg_o1'},
            'O2-A1': {'data': self.normalized_signals.get('eeg_o2_n', pd.Series()), 'cb': mock_cb, 'color': '#607d8b', 'key': 'eeg_o2'},
        }
    
    def configure_plot_appearance(self, start_time, end_time):
        """Configure plot appearance"""
        if self.settings.window_size <= 30:
            title = 'High Detail View'
        elif self.settings.window_size <= 300:
            title = 'Balanced View'
        else:
            title = 'Compact Overview'
        
        self.detailed_ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.detailed_ax.set_title(f'SleepSense Pro - {title}', fontsize=14, fontweight='bold')
        self.detailed_ax.set_xlabel('Time (seconds)', fontsize=10)
        self.detailed_ax.set_xlim(start_time, end_time)
    
    def draw_selected_regions(self):
        """Draw selected regions on the plot"""
        for region in self.selected_regions:
            rect = plt.Rectangle(
                (region['start_time'], region['start_y']),
                region['duration'], region['end_y'] - region['start_y'],
                fill=True, alpha=0.2, color='blue'
            )
            self.detailed_ax.add_patch(rect)
    
    def change_window_size(self, new_size):
        """Change window size"""
        self.settings.window_size = float(new_size)
        self.update_plot()
    
    def set_time(self, start_time):
        """Set current time"""
        self.settings.start_time = start_time
        self.update_plot()
    
    def toggle_zoom(self, signal_key, zoomed_in):
        """Toggle zoom for a specific signal"""
        self.settings.signal_scales[signal_key] = 2.0 if zoomed_in else 1.0
        self.update_plot()
    
    def set_view_mode(self, mode):
        """Set view mode"""
        self.settings.current_view_mode = mode
        # This would need to be connected to the left panel to update checkboxes
        self.update_plot()
    
    def toggle_comparison_mode(self, enabled):
        """Toggle comparison mode"""
        self.settings.comparison_mode = enabled
        self.comparison_canvas.setVisible(enabled)
        
        if enabled:
            self.detailed_fig.set_size_inches(20, 6)
            self.comparison_fig.set_size_inches(20, 6)
            self.update_comparison_plot()
        else:
            self.detailed_fig.set_size_inches(20, 14)
    
    def toggle_osa_analysis(self, enabled):
        """Toggle OSA analysis mode"""
        self.settings.osa_analysis_mode = enabled
        
        if enabled:
            self.detailed_canvas.setVisible(False)
            self.comparison_canvas.setVisible(False)
            self.osa_analysis_widget.setVisible(True)
            self.update_osa_analysis_plots()
        else:
            self.detailed_canvas.setVisible(True)
            self.osa_analysis_widget.setVisible(False)
    
    def update_comparison_plot(self):
        """Update comparison plot"""
        if not self.settings.comparison_mode:
            return
        # Implementation for comparison plot
        pass
    
    def update_osa_analysis_plots(self):
        """Update OSA analysis plots"""
        if not self.settings.osa_analysis_mode:
            return
        # Implementation for OSA analysis plots
        pass
    
    def detect_respiratory_events(self):
        """Detect respiratory events"""
        # This would use the OSA analysis module
        pass
    
    def clear_detected_events(self):
        """Clear detected events"""
        # This would use the OSA analysis module
        pass
    
    def handle_key_press(self, event):
        """Handle key press events for navigation"""
        if isinstance(event, QKeyEvent):
            step = max(0.5, self.settings.window_size * 0.1)  # 10% jump, min 0.5s
            data_start = getattr(self.settings, 'data_start_time', self.settings.start_time)
            data_end = getattr(self.settings, 'data_end_time', self.settings.end_time)
            if event.key() == Qt.Key_Left:
                self.settings.start_time = max(data_start, self.settings.start_time - step)
            elif event.key() == Qt.Key_Right:
                max_start = data_end - self.settings.window_size
                self.settings.start_time = min(max_start, self.settings.start_time + step)
            elif event.key() == Qt.Key_Home:
                self.settings.start_time = data_start
            elif event.key() == Qt.Key_End:
                self.settings.start_time = max(data_start, data_end - self.settings.window_size)
            else:
                return
            self.update_plot()
    
    # Mouse event handlers
    def on_mouse_press(self, event):
        """Handle mouse press events"""
        if event.inaxes != self.detailed_ax or event.button != 1:
            return
        self.is_selecting = True
        self.selection_start = (event.xdata, event.ydata)
        self.selection_rect = plt.Rectangle((event.xdata, event.ydata), 0, 0,
                                          fill=True, alpha=0.2, color='cyan')
        self.detailed_ax.add_patch(self.selection_rect)
        self.detailed_canvas.draw_idle()
    
    def on_mouse_release(self, event):
        """Handle mouse release events"""
        if not self.is_selecting or event.button != 1:
            return
        self.is_selecting = False
        start_x, start_y = self.selection_start
        end_x, end_y = event.xdata, event.ydata
        x1, x2 = min(start_x, end_x), max(start_x, end_x)
        y1, y2 = min(start_y, end_y), max(start_y, end_y)
        
        # Add final region to list
        self.selected_regions.append({
            'start_time': x1, 'end_time': x2,
            'start_y': y1, 'end_y': y2,
            'duration': x2 - x1,
        })
        
        # Remove temporary rectangle and redraw plot
        self.selection_rect.remove()
        self.selection_rect = None
        self.update_plot()
    
    def on_mouse_move(self, event):
        """Handle mouse move events"""
        if not self.is_selecting or not self.selection_rect or not event.inaxes:
            return
        start_x, start_y = self.selection_start
        width = event.xdata - start_x
        height = event.ydata - start_y
        self.selection_rect.set_width(width)
        self.selection_rect.set_height(height)
        self.detailed_canvas.draw_idle()
