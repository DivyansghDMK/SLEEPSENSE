#!/usr/bin/env python3
"""
Test script for SleepSense Pro Modular Architecture
This script tests the basic functionality without starting the GUI
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing module imports...")
    
    try:
        # Test config imports
        from src.config.constants import SIGNAL_OFFSETS, SIGNAL_COLORS
        print("✅ Config modules imported successfully")
        
        # Test data imports
        from src.data.data_loader import DataLoader
        from src.data.signal_processor import SignalProcessor
        from src.data.mock_data_generator import MockDataGenerator
        print("✅ Data modules imported successfully")
        
        # Test analysis imports
        from src.analysis.sleep_analysis import SleepAnalysis
        from src.analysis.osa_analysis import OSAAnalysis
        from src.analysis.pdf_generator import PDFGenerator
        print("✅ Analysis modules imported successfully")
        
        # Test GUI imports (without creating widgets)
        from src.gui.main_window import SleepSenseMainWindow
        from src.gui.panels import LeftPanel, RightPanel
        from src.gui.menus import MenuBar
        from src.gui.plots import PlotManager
        print("✅ GUI modules imported successfully")
        
        # Test utils imports
        from src.utils.helpers import get_downloads_path, format_time
        print("✅ Utils modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_data_loading():
    """Test data loading functionality"""
    print("\nTesting data loading...")
    
    try:
        from src.data.data_loader import DataLoader
        from src.data.signal_processor import SignalProcessor
        
        # Create data loader
        loader = DataLoader()
        processor = SignalProcessor()
        
        # Test loading data
        data = loader.load_data("data/DATA0025.TXT")
        print(f"✅ Data loaded successfully: {data.shape}")
        
        # Test data format detection
        signals = loader.detect_data_format(data)
        print(f"✅ Data format detected: {len(signals)} signals")
        
        # Test signal processing
        normalized_signals = processor.normalize_all_signals(signals)
        print(f"✅ Signals normalized successfully: {len(normalized_signals)} signals")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def test_analysis():
    """Test analysis functionality"""
    print("\nTesting analysis...")
    
    try:
        from src.analysis.sleep_analysis import SleepAnalysis
        from src.analysis.osa_analysis import OSAAnalysis
        
        # Create analysis modules
        sleep_analysis = SleepAnalysis()
        osa_analysis = OSAAnalysis()
        
        print("✅ Analysis modules created successfully")
        
        # Test mock data generation for analysis
        from src.data.mock_data_generator import MockDataGenerator
        generator = MockDataGenerator()
        mock_data = generator.generate_8_hour_mock_data()
        print(f"✅ Mock data generated: {mock_data.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def test_configuration():
    """Test configuration system"""
    print("\nTesting configuration...")
    
    try:
        from src.config.settings import AppSettings
        from src.config.constants import SIGNAL_OFFSETS, FRAME_SIZES
        
        # Create settings
        settings = AppSettings()
        print(f"✅ Settings created: window_size={settings.window_size}")
        
        # Test constants
        print(f"✅ Signal offsets: {len(SIGNAL_OFFSETS)} signals")
        print(f"✅ Frame sizes: {len(FRAME_SIZES)} options")
        
        # Test responsive settings
        settings.update_screen_dimensions(1920, 1080)
        geometry = settings.get_window_geometry()
        print(f"✅ Responsive geometry: {geometry}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("SleepSense Pro - Modular Architecture Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_data_loading,
        test_analysis,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The modular architecture is working correctly.")
        print("\nTo run the full application:")
        print("  python main.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
