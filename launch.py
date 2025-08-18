#!/usr/bin/env python3
"""
SleepSense Launcher Script
Simple launcher with error handling and dependency checking
"""

import sys
import os
import subprocess
import importlib.util

def check_dependency(module_name, package_name=None):
    """Check if a Python module is available"""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.util.find_spec(module_name)
        return True
    except ImportError:
        return False

def install_dependency(package_name):
    """Install a Python package using pip"""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}")
        return False

def check_dependencies():
    """Check and install required dependencies"""
    required_packages = [
        ('PySide6', 'PySide6'),
        ('numpy', 'numpy'),
        ('matplotlib', 'matplotlib'),
        ('scipy', 'scipy'),
        ('pyqtgraph', 'pyqtgraph'),
        ('cryptography', 'cryptography'),
        ('PIL', 'pillow')
    ]
    
    missing_packages = []
    
    for module_name, package_name in required_packages:
        if not check_dependency(module_name):
            missing_packages.append(package_name)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        
        print("\nAttempting to install missing packages...")
        
        for package in missing_packages:
            if not install_dependency(package):
                print(f"\nError: Could not install {package}")
                print("Please install it manually using:")
                print(f"  pip install {package}")
                return False
        
        print("All dependencies installed successfully!")
    
    return True

def main():
    """Main launcher function"""
    print("SleepSense Medical Device Interface")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\nDependency check failed. Please install missing packages manually.")
        input("Press Enter to exit...")
        return
    
    # Check if main.py exists
    if not os.path.exists('main.py'):
        print("Error: main.py not found!")
        print("Please ensure you're running this script from the SleepSense directory.")
        input("Press Enter to exit...")
        return
    
    # Launch the application
    try:
        print("\nLaunching SleepSense...")
        print("Default credentials: admin / admin123")
        print("\n" + "=" * 40)
        
        # Import and run main
        from main import main as app_main
        app_main()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please check that all dependencies are properly installed.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please check the logs for more details.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
