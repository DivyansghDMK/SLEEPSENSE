# SleepSense Pro - Modular Architecture

Professional Sleep Analysis System with a clean, modular architecture.

## 🏗️ Architecture Overview

This modular version of SleepSense Pro has been refactored into a clean, maintainable structure while preserving all original functionality and UI/UX.

### 📁 Project Structure

```
SleepSense_Modular/
├── main.py                          # Main entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── data/                           # Data files directory
├── logs/                           # Log files directory
└── src/                           # Source code
    ├── __init__.py
    ├── config/                     # Configuration and settings
    │   ├── __init__.py
    │   ├── constants.py           # Application constants
    │   └── settings.py            # Settings management
    ├── data/                      # Data management
    │   ├── __init__.py
    │   ├── data_loader.py         # Data loading and format detection
    │   ├── mock_data_generator.py # Mock data generation
    │   └── signal_processor.py    # Signal processing and normalization
    ├── gui/                       # User interface components
    │   ├── __init__.py
    │   ├── main_window.py         # Main application window
    │   ├── panels.py              # Left and right panels
    │   ├── menus.py               # Menu system
    │   └── plots.py               # Plot management
    ├── analysis/                  # Analysis modules
    │   ├── __init__.py
    │   ├── sleep_analysis.py      # Comprehensive sleep analysis
    │   ├── osa_analysis.py        # OSA event detection
    │   └── pdf_generator.py       # PDF report generation
    └── utils/                     # Utility functions
        ├── __init__.py
        └── helpers.py             # Helper functions
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone or download the project**
   ```bash
   cd SleepSense_Modular
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 🎯 Features

### Core Functionality
- **Professional Sleep Analysis**: Complete sleep study analysis with clinical-grade metrics
- **Multi-Signal Visualization**: Display of 16+ physiological signals including EEG, respiratory, and cardiovascular data
- **Interactive Navigation**: Time-based navigation with multiple view modes
- **Real-time Analysis**: Live signal processing and normalization
- **Clinical Reports**: Comprehensive PDF report generation

### View Modes
- **All Signals**: Complete overview of all physiological signals
- **EEG Waves Only**: Focused brain wave analysis
- **Respiratory Only**: Breathing pattern analysis
- **Comparison Mode**: Side-by-side signal comparison
- **OSA Analysis**: Obstructive Sleep Apnea detection and analysis

### Signal Types
- **Respiratory**: Airflow, Thorax, Abdomen, Snore
- **EEG**: C3-A2, C4-A1, F3-A2, F4-A1, O1-A2, O2-A1
- **Cardiovascular**: Pulse, SpO2, Plethysmography
- **Other**: Body Position, Activity

## 🔧 Architecture Benefits

### Modular Design
- **Separation of Concerns**: Each module has a single responsibility
- **Maintainability**: Easy to modify and extend individual components
- **Testability**: Each module can be tested independently
- **Reusability**: Components can be reused in other projects

### Key Modules

#### Configuration (`src/config/`)
- **constants.py**: Application-wide constants and configuration values
- **settings.py**: Dynamic settings management with responsive design

#### Data Management (`src/data/`)
- **data_loader.py**: Handles data loading from various sources with fallback
- **signal_processor.py**: Signal normalization and processing
- **mock_data_generator.py**: Generates realistic mock data for testing

#### User Interface (`src/gui/`)
- **main_window.py**: Main application window and coordination
- **panels.py**: Left control panel and right navigation panel
- **menus.py**: Complete menu system with all actions
- **plots.py**: Matplotlib-based plotting and visualization

#### Analysis (`src/analysis/`)
- **sleep_analysis.py**: Comprehensive sleep study analysis
- **osa_analysis.py**: OSA event detection and analysis
- **pdf_generator.py**: Professional PDF report generation

## 🎨 UI/UX Features

### Responsive Design
- **Adaptive Layout**: Automatically adjusts to different screen sizes
- **Touch-Friendly**: Optimized for both desktop and tablet use
- **Modern Styling**: Clean, professional interface with consistent theming

### Navigation Controls
- **Time Slider**: Smooth time-based navigation
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Frame Size Selection**: Quick time window adjustment (5s to 30m)
- **Zoom Controls**: Individual signal zoom functionality

### Interactive Features
- **Region Selection**: Mouse-based data region selection
- **Real-time Updates**: Live signal processing and display
- **Multiple Views**: Switch between different analysis modes
- **Export Options**: Save analysis results and reports

## 📊 Analysis Capabilities

### Sleep Metrics
- **Apnea-Hypopnea Index (AHI)**: Primary sleep apnea metric
- **Respiratory Disturbance Index (RDI)**: Comprehensive breathing analysis
- **Position Analysis**: Sleep position impact on breathing
- **REM/NREM Analysis**: Sleep stage-specific metrics

### Clinical Reports
- **Multi-page PDF**: Professional 4-page clinical report
- **Comprehensive Tables**: Detailed metrics and statistics
- **Data Visualization**: High-quality signal plots
- **Clinical Summary**: Professional interpretation guidelines

## 🔧 Development

### Adding New Features
1. **Identify the appropriate module** for your feature
2. **Create new classes or functions** following existing patterns
3. **Update module `__init__.py`** to export new components
4. **Add configuration** if needed in `src/config/`
5. **Update main window** to integrate new features

### Code Style
- **PEP 8 Compliance**: Follow Python style guidelines
- **Type Hints**: Use type annotations for better code clarity
- **Docstrings**: Document all classes and functions
- **Error Handling**: Implement proper exception handling

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path includes the `src` directory

2. **Data Loading Issues**
   - Place data files in the `data/` directory
   - Ensure data files are in supported format (CSV, TXT)

3. **Display Issues**
   - Check screen resolution and scaling settings
   - Try different view modes for better signal visibility

4. **Performance Issues**
   - Reduce time window size for better performance
   - Close other applications to free up memory

### Getting Help
- Check the console output for error messages
- Verify all dependencies are correctly installed
- Ensure data files are in the correct format

## 📝 License

© 2024 SleepSense Pro - Professional Edition

## 🤝 Contributing

This is a professional medical software system. For contributions or modifications, please contact the development team.

---

**Note**: This modular version maintains 100% compatibility with the original SleepSense Pro functionality while providing a clean, maintainable architecture for future development.
