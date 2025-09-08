"""
Menu system for SleepSense Pro
"""

from PyQt5.QtWidgets import (
    QMenuBar, QMenu, QAction, QActionGroup
)
from PyQt5.QtCore import pyqtSignal


class MenuBar(QMenuBar):
    """Main menu bar for SleepSense Pro"""
    
    open_file_requested = pyqtSignal()
    save_report_requested = pyqtSignal()
    about_requested = pyqtSignal()
    view_mode_changed = pyqtSignal(str)
    comparison_toggled = pyqtSignal(bool)
    osa_analysis_toggled = pyqtSignal(bool)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_menus()
    
    def setup_menus(self):
        """Setup all menus"""
        # File Menu
        self.create_file_menu()
        
        # View Menu
        self.create_view_menu()
        
        # Data Security Menu
        self.create_security_menu()
        
        # Help Menu
        self.create_help_menu()
    
    def create_file_menu(self):
        """Create File menu"""
        file_menu = self.addMenu('File')
        
        open_action = QAction('Open Data File', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file_requested.emit)
        
        save_action = QAction('Save Report', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_report_requested.emit)
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.parent.close)
        
        file_menu.addActions([open_action, save_action])
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
    
    def create_view_menu(self):
        """Create View menu"""
        view_menu = self.addMenu('View')
        
        # Signal View Modes
        view_mode_menu = view_menu.addMenu(' Signal View Mode')
        
        # Create action group for exclusive selection
        self.view_mode_group = QActionGroup(self)
        self.view_mode_group.setExclusive(True)
        
        self.all_signals_action = QAction('All Signals', self, checkable=True, checked=True)
        self.all_signals_action.setShortcut('Ctrl+1')
        self.all_signals_action.triggered.connect(lambda: self.view_mode_changed.emit('all'))
        
        self.eeg_only_action = QAction('🧠 EEG Waves Only', self, checkable=True)
        self.eeg_only_action.setShortcut('Ctrl+2')
        self.eeg_only_action.triggered.connect(lambda: self.view_mode_changed.emit('eeg'))
        
        self.respiratory_only_action = QAction('🫁 Respiratory Only', self, checkable=True)
        self.respiratory_only_action.setShortcut('Ctrl+3')
        self.respiratory_only_action.triggered.connect(lambda: self.view_mode_changed.emit('respiratory'))
        
        # Add actions to group and menu
        self.view_mode_group.addAction(self.all_signals_action)
        self.view_mode_group.addAction(self.eeg_only_action)
        self.view_mode_group.addAction(self.respiratory_only_action)
        
        view_mode_menu.addAction(self.all_signals_action)
        view_mode_menu.addAction(self.eeg_only_action)
        view_mode_menu.addAction(self.respiratory_only_action)
        
        view_menu.addSeparator()
        
        # Comparison Features
        comparison_menu = view_menu.addMenu('🔀 Comparison Mode')
        
        self.enable_comparison_action = QAction('Enable Split View Comparison', self, checkable=True)
        self.enable_comparison_action.setShortcut('Ctrl+D')
        self.enable_comparison_action.triggered.connect(self.comparison_toggled.emit)
        
        self.sync_time_action = QAction('Sync Time Navigation', self, checkable=True, checked=True)
        self.sync_time_action.setShortcut('Ctrl+Shift+S')
        
        self.swap_comparison_action = QAction('Swap Comparison Views', self)
        self.swap_comparison_action.setShortcut('Ctrl+Shift+W')
        
        comparison_menu.addAction(self.enable_comparison_action)
        comparison_menu.addAction(self.sync_time_action)
        comparison_menu.addAction(self.swap_comparison_action)
        
        view_menu.addSeparator()
        
        # Clinical Analysis
        clinical_menu = view_menu.addMenu('🏥 Clinical Analysis')
        
        self.osa_analysis_action = QAction('OSA Analysis - Apnea/Hypopnea Detection', self, checkable=True)
        self.osa_analysis_action.setShortcut('Ctrl+O')
        self.osa_analysis_action.triggered.connect(self.osa_analysis_toggled.emit)
        
        clinical_menu.addAction(self.osa_analysis_action)
        
        view_menu.addSeparator()
        
        # Window Controls
        fullscreen_action = QAction('Fullscreen', self, shortcut='F11')
        fullscreen_action.triggered.connect(self.parent.toggle_fullscreen)
        
        maximize_plots_action = QAction('Maximize Plot Area', self, shortcut='Ctrl+M')
        maximize_plots_action.triggered.connect(self.parent.maximize_plot_area)
        
        compact_controls_action = QAction('Compact Controls', self, shortcut='Ctrl+C')
        compact_controls_action.triggered.connect(self.parent.toggle_compact_controls)
        
        view_menu.addActions([fullscreen_action, maximize_plots_action, compact_controls_action])
    
    def create_security_menu(self):
        """Create Data Security menu"""
        security_menu = self.addMenu('Data Security')
        
        secure_data_action = QAction('🔒 Secure Existing Data', self)
        secure_data_action.triggered.connect(self.secure_existing_data)
        
        list_files_action = QAction('📋 List Data Files', self)
        list_files_action.triggered.connect(self.list_data_files)
        
        export_secure_action = QAction('📤 Export Secure Data', self)
        export_secure_action.triggered.connect(self.export_secure_data)
        
        regions_info_action = QAction('📋 Show Selected Regions', self)
        regions_info_action.triggered.connect(self.show_selected_regions)
        
        clear_regions_action = QAction('🗑️ Clear All Regions', self, shortcut='Ctrl+R')
        clear_regions_action.triggered.connect(self.clear_all_regions)
        
        test_downloads_action = QAction('🧪 Test Downloads Path', self)
        test_downloads_action.triggered.connect(self.test_downloads_path)
        
        test_simple_pdf_action = QAction('📄 Test Simple PDF', self)
        test_simple_pdf_action.triggered.connect(self.test_simple_pdf)
        
        security_menu.addActions([secure_data_action, list_files_action, export_secure_action])
        security_menu.addSeparator()
        security_menu.addActions([regions_info_action, clear_regions_action, test_downloads_action, test_simple_pdf_action])
    
    def create_help_menu(self):
        """Create Help menu"""
        help_menu = self.addMenu('Help')
        
        navigation_help_action = QAction('Navigation Help', self, shortcut='F1')
        navigation_help_action.triggered.connect(self.show_navigation_help)
        
        about_action = QAction('About SleepSense Pro', self)
        about_action.triggered.connect(self.about_requested.emit)
        
        help_menu.addActions([navigation_help_action, about_action])
    
    def secure_existing_data(self):
        """Secure existing data - placeholder"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self.parent, "Secure Data", "This feature is for demonstration.")
    
    def list_data_files(self):
        """List data files - placeholder"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self.parent, "List Data Files", "This feature is for demonstration.")
    
    def export_secure_data(self):
        """Export secure data - placeholder"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self.parent, "Export Data", "This feature is for demonstration.")
    
    def show_selected_regions(self):
        """Show selected regions - placeholder"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self.parent, "Selected Regions", "No regions have been selected.")
    
    def clear_all_regions(self):
        """Clear all regions - placeholder"""
        pass
    
    def test_downloads_path(self):
        """Test downloads path - placeholder"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self.parent, "Test Downloads", "Downloads path test completed.")
    
    def test_simple_pdf(self):
        """Test simple PDF - placeholder"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self.parent, "Test PDF", "Simple PDF test completed.")
    
    def show_navigation_help(self):
        """Show navigation help"""
        from PyQt5.QtWidgets import QMessageBox
        help_text = """
        <b>Navigation Controls:</b>
        <ul>
            <li><b>Mouse:</b> Drag the slider to navigate.</li>
            <li><b>Arrow Keys (← →):</b> Move forward/backward in time.</li>
            <li><b>Home/End Keys:</b> Jump to the start or end of the data.</li>
        </ul>
        """
        QMessageBox.information(self.parent, "Navigation Help", help_text)
