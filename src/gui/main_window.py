"""
Main window for SleepSense Pro
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QSplitter, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPainterPath

from .panels import LeftPanel, RightPanel
from .menus import MenuBar
from .plots import PlotManager
from ..config.settings import AppSettings
from ..data.data_loader import DataLoader
from ..data.signal_processor import SignalProcessor
from ..analysis.sleep_analysis import SleepAnalysis
from ..analysis.osa_analysis import OSAAnalysis
from ..analysis.pdf_generator import PDFGenerator


class SleepSenseMainWindow(QMainWindow):
    """Main window for SleepSense Pro application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SleepSense Pro - Professional Sleep Analysis System")
        
        # Initialize settings
        self.settings = AppSettings()
        
        # Initialize data management
        self.data_loader = DataLoader()
        self.signal_processor = SignalProcessor()
        
        # Initialize analysis modules
        self.sleep_analysis = SleepAnalysis()
        self.osa_analysis = OSAAnalysis()
        self.pdf_generator = PDFGenerator()
        
        # Initialize data
        self.signals = {}
        self.normalized_signals = {}
        
        # Initialize UI
        self.setup_ui()
        self.load_data()
        self.setup_connections()
        
        # Show welcome message
        self.show_welcome_message()
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Get screen dimensions for responsive design
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.settings.update_screen_dimensions(screen_geometry.width(), screen_geometry.height())
        
        # Set window geometry
        geometry = self.settings.get_window_geometry()
        self.setGeometry(*geometry)
        self.setMinimumSize(*self.settings.get_minimum_size())
        
        # Set responsive modern style
        self.setStyleSheet(self.get_stylesheet())
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create panels
        self.left_panel = LeftPanel(self.settings)
        self.right_panel = RightPanel(self.settings)
        
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        
        # Set splitter sizes
        if self.settings.is_small_screen:
            splitter.setSizes([250, self.width() - 280])
        else:
            splitter.setSizes([300, self.width() - 330])
        
        self.splitter = splitter
        
        # Create menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Create plot manager
        self.plot_manager = PlotManager(self.right_panel, self.settings)
        
        # Set status bar
        self.statusBar().showMessage("SleepSense Pro Ready | Press F1 for navigation help")
    
    def get_stylesheet(self):
        """Get the application stylesheet"""
        base_font_size = self.settings.get_font_size()
        button_height = self.settings.get_button_height()
        
        return f"""
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
        """
    
    def load_data(self):
        """Load and process data"""
        # Load raw data
        raw_data = self.data_loader.load_data()
        
        # Detect data format and extract signals
        self.signals = self.data_loader.detect_data_format(raw_data)
        
        # Compute sampling rate
        self.signal_processor.compute_sampling_rate(self.signals['time'])
        self.settings.sample_rate = self.signal_processor.sample_rate
        
        # Normalize signals
        self.normalized_signals = self.signal_processor.normalize_all_signals(self.signals)
        
        # Set window parameters
        self.settings.start_time = self.signals['time'].iloc[0]
        self.settings.end_time = self.signals['time'].iloc[-1]
        # Store absolute bounds for UI slider mapping
        self.settings.data_start_time = float(self.settings.start_time)
        self.settings.data_end_time = float(self.settings.end_time)
        self.settings.max_window_size = max(1.0, (self.settings.end_time - self.settings.start_time) / 2)
        
        # Initialize plot manager with data
        self.plot_manager.set_data(self.signals, self.normalized_signals)
        
        # Configure signal checkboxes
        self.left_panel.configure_signal_checkboxes()
    
    def setup_connections(self):
        """Setup signal connections between components"""
        # Connect left panel signals to plot updates
        self.left_panel.signal_toggled.connect(self.plot_manager.update_plot)
        self.left_panel.zoom_toggled.connect(self.plot_manager.toggle_zoom)
        self.left_panel.view_mode_changed.connect(self.plot_manager.set_view_mode)
        
        # Connect right panel signals
        self.right_panel.window_size_changed.connect(self.plot_manager.change_window_size)
        self.right_panel.time_changed.connect(self.plot_manager.set_time)
        self.right_panel.comparison_toggled.connect(self.plot_manager.toggle_comparison_mode)
        self.right_panel.osa_analysis_toggled.connect(self.plot_manager.toggle_osa_analysis)
        
        # Connect menu actions
        self.menu_bar.open_file_requested.connect(self.open_file)
        self.menu_bar.save_report_requested.connect(self.save_report)
        self.menu_bar.about_requested.connect(self.show_about)
    
    def show_welcome_message(self):
        """Display welcome message with SleepSense Pro branding"""
        try:
            # Look for image in project_root/assets (prefer Divyansh.png)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            assets_dir = os.path.join(project_root, 'assets')
            candidate_names = ['Divyansh.png', 'welcome.png', 'welcome_snoring.png']
            img_path = None
            for name in candidate_names:
                path = os.path.join(assets_dir, name)
                if os.path.exists(path):
                    img_path = path
                    break

            if os.path.exists(img_path):
                pix = QPixmap(img_path)
                if not pix.isNull():
                    # Create a circular-cropped avatar with a tuned focal point (person on right)
                    target_diameter = 220
                    crop_size = min(pix.width(), pix.height())
                    # Choose focal point slightly right of center and mid-height
                    focal_x_ratio = 0.68  # 0=left, 1=right
                    focal_y_ratio = 0.50  # 0=top,  1=bottom
                    center_x = int(pix.width() * focal_x_ratio)
                    center_y = int(pix.height() * focal_y_ratio)
                    x = max(0, min(pix.width() - crop_size, center_x - crop_size // 2))
                    y = max(0, min(pix.height() - crop_size, center_y - crop_size // 2))
                    square = pix.copy(x, y, crop_size, crop_size)
                    square = square.scaled(target_diameter, target_diameter, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    circular = QPixmap(target_diameter, target_diameter)
                    circular.fill(Qt.transparent)
                    painter = QPainter(circular)
                    painter.setRenderHint(QPainter.Antialiasing, True)
                    path = QPainterPath()
                    path.addEllipse(0, 0, target_diameter, target_diameter)
                    painter.setClipPath(path)
                    painter.drawPixmap(0, 0, square)
                    painter.end()

                    msg = QMessageBox(self)
                    msg.setWindowTitle("Welcome to SleepSense Pro")
                    msg.setIconPixmap(circular)
                    msg.setText("Professional Sleep Analysis System")
                    msg.setInformativeText("Ready to analyze your sleep data!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    return

            # Fallback to text-only message
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Welcome to SleepSense Pro")
            msg.setText("Welcome to SleepSense Pro")
            msg.setInformativeText("Professional Sleep Analysis System\n\nReady to analyze your sleep data!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except Exception:
            # Silent fallback
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Welcome to SleepSense Pro")
            msg.setText("Welcome to SleepSense Pro")
            msg.setInformativeText("Professional Sleep Analysis System\n\nReady to analyze your sleep data!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
    
    def show_about(self):
        """Show about dialog for SleepSense Pro"""
        QMessageBox.about(self, "About SleepSense Pro",
                          "<b>SleepSense Pro v2.0</b><br>"
                          "Professional Sleep Analysis System<br><br>"
                          "© 2024 SleepSense Pro<br>"
                          "Professional Edition")
    
    def open_file(self):
        """Open data file"""
        self.statusBar().showMessage("Open file functionality - Not implemented yet")
    
    def save_report(self):
        """Save PDF report"""
        try:
            # Get Downloads folder path
            downloads_path = self.settings.get_downloads_path()
            
            # Create default filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"SleepSense_Report_{timestamp}.pdf"
            default_path = os.path.join(downloads_path, default_filename)
            
            # Show file dialog
            from PyQt5.QtWidgets import QFileDialog
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(
                self, 
                "Save SleepSense Report", 
                default_path, 
                "PDF Files (*.pdf)", 
                options=options
            )
            
            if fileName:
                self.statusBar().showMessage("Generating report, please wait...")
                QApplication.setOverrideCursor(Qt.WaitCursor)
                
                # Analyze the study data
                analysis_results = self.sleep_analysis.analyze_full_study(self.normalized_signals)
                
                # Generate PDF report
                self.pdf_generator.generate_pdf_report(fileName, analysis_results, self.normalized_signals)
                
                # Verify file was created
                if os.path.exists(fileName):
                    file_size = os.path.getsize(fileName)
                    self.statusBar().showMessage(f"✅ Report successfully saved to {fileName} ({file_size} bytes)")
                    QMessageBox.information(self, "Success", f"Report saved successfully!\n\nLocation: {fileName}\nSize: {file_size} bytes")
                else:
                    raise Exception("File was not created")
                    
        except Exception as e:
            error_msg = f"An error occurred while generating the report: {e}"
            print(f"Report generation error: {e}")
            QMessageBox.critical(self, "Report Generation Error", error_msg)
            self.statusBar().showMessage("⚠️ Report generation failed.")
        finally:
            QApplication.restoreOverrideCursor()
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        if hasattr(self, 'plot_manager'):
            self.plot_manager.update_plot()
    
    def keyPressEvent(self, event):
        """Handle key press events for navigation"""
        if hasattr(self, 'plot_manager'):
            self.plot_manager.handle_key_press(event)
        else:
            super().keyPressEvent(event)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def maximize_plot_area(self):
        """Maximize plot area"""
        left_width = min(200, int(self.width() * 0.15))
        self.splitter.setSizes([left_width, self.width() - left_width])
        self.statusBar().showMessage("✅ Plot area maximized.")
    
    def toggle_compact_controls(self):
        """Toggle compact controls"""
        sizes = self.splitter.sizes()
        if sizes[0] > 250:
            self.maximize_plot_area()
        else:
            default_width = 300
            self.splitter.setSizes([default_width, self.width() - default_width])
            self.statusBar().showMessage("✅ Controls restored.")
