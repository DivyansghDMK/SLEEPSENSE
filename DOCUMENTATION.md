# SleepSense Pro - Technical Documentation

## System Overview

SleepSense Pro is a professional-grade sleep analysis application designed for medical professionals, researchers, and sleep laboratories. It provides comprehensive analysis of multiple physiological signals during sleep, with a focus on performance, accuracy, and professional usability.

### Key Capabilities
- Multi-Signal Processing: Handle 15+ physiological signals simultaneously
- Real-Time Analysis: Live waveform visualization with smooth navigation
- Professional Interface: Medical device-grade UI/UX design
- Data Security: Built-in encryption and secure data handling
- Cross-Platform: Windows, macOS, and Linux support
- Large Dataset Support: Optimized for datasets with 100k+ samples

## Architecture & Design

### Core Components

#### 1. GUI Layer (PyQt5)
- Main Window: SleepSensePlot class extending QMainWindow
- Control Panels: Left panel for signal controls, right panel for visualization
- Responsive Layout: Dynamic sizing based on screen dimensions
- Professional Styling: Medical device-grade interface design

## Installation & Setup

### Quick Start
```bash
# Clone the repository
git clone https://github.com/DivyansghDMK/SLEEPSENSE.git
cd SLEEPSENSE

# Install dependencies
pip install -r requirements.txt

# Run SleepSense Pro
python3 guicopymain.py
```

## Key Features

### Signal Types Supported
- Cardiovascular: Pulse, SpO2, Plethysmography
- Respiratory: Airflow, Thorax Movement, Abdomen Movement, Snore
- Neurological: 6-Channel EEG (C3, C4, F3, F4, O1, O2)
- Activity: Sleep/Wake cycle detection
- Position: Body position tracking with visual indicators

## Performance Features

### Optimization Features
- Debounced Updates: Prevents excessive plot redraws
- Smart Plotting: Only plots visible data ranges
- Vectorized Processing: Optimized using NumPy operations
- Chunked Processing: Handles large datasets efficiently

## Usage Guide

### Getting Started
1. Launch: Run python3 guicopymain.py
2. Activation: Complete the activation process (first time only)
3. Load Data: Your sleep data will be automatically loaded
4. Analyze: Use left panel controls to toggle signals on/off
5. Navigate: Use time slider to move through sleep session
6. Zoom: Click ▲/▼ buttons to zoom individual signals
7. Select Regions: Click and drag in detailed view to mark events

### Keyboard Shortcuts
- Ctrl+M: Maximize plot area
- Ctrl+C: Toggle compact controls
- F11: Fullscreen mode
- Ctrl+R: Clear all selected regions

## Support

For support and questions:
- Create an issue in the GitHub repository
- Contact: support@sleepsense.pro
