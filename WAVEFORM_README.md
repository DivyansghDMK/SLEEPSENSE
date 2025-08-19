# SleepSense Waveform Viewer

A professional PySide6-based application for viewing sleep study data from DATA0025.TXT with parallel stacked wave display.

## Features

### 🎛️ Control Panel (Left Side)
- **Individual Wave Toggles**: Colored buttons to show/hide specific waves
- **Bulk Controls**: "Show All" and "Hide All" buttons
- **Time Navigation**: Slider to navigate through different time windows
- **Data Information**: Shows total data points and current time window
- **Professional Styling**: Dark theme with medical-grade appearance

### 📊 Wave Display (Right Side)
- **Parallel Stacking**: All waves displayed vertically with proper spacing
- **Color Coding**: Each parameter has distinct color for easy identification
- **Wave Labels**: Parameter names displayed on the right side
- **Grid Lines**: Professional plotting with grid overlay
- **Responsive Design**: Adapts to window size changes

## Data Mapping

The application reads DATA0025.TXT and maps the following columns:

| Column | Index | Parameter | Color | Description |
|--------|-------|-----------|-------|-------------|
| Col2 | 1 | Body Position | 🟢 Green | Sleep position (1-5) |
| Col3 | 2 | Pulse | 🔴 Red | Heart rate (65-120 bpm) |
| Col4 | 3 | SpO2 | 🔵 Blue | Blood oxygen (65-99%) |
| Col7 | 6 | Airflow | 🟠 Orange | Breathing flow (1-120) |

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python plot_waves.py
   ```

## Usage

### Basic Controls
1. **Launch**: Run `python plot_waves.py`
2. **View Waves**: All waves are visible by default
3. **Toggle Individual Waves**: Click colored buttons on the left
4. **Bulk Control**: Use "Show All" or "Hide All" buttons

### Time Navigation
- **Time Slider**: Move through different 10-second windows
- **Current Window**: Displayed above the slider (e.g., "Time: 0.0s - 10.0s")
- **Total Duration**: 158.4 minutes (95,062 data points at 10 Hz)

### Wave Management
- **Body Position**: Toggle green button to show/hide
- **Pulse**: Toggle red button to show/hide  
- **SpO2**: Toggle blue button to show/hide
- **Airflow**: Toggle orange button to show/hide

## Technical Details

### Data Specifications
- **File**: DATA0025.TXT
- **Format**: Comma-separated values (CSV)
- **Rows**: 95,062 data points
- **Columns**: 10 columns (only 4 used for plotting)
- **Sample Rate**: 10 Hz (10 samples per second)
- **Duration**: 158.4 minutes

### Wave Display
- **Spacing**: 100 units between each wave
- **Normalization**: Data scaled for optimal visibility
- **Stacking**: Vertical parallel layout
- **Colors**: Professional medical device color scheme

### Performance
- **Real-time**: Smooth wave display with PyQtGraph
- **Memory Efficient**: Optimized for large datasets
- **Responsive**: Fast toggle and navigation controls

## Troubleshooting

### Common Issues
1. **Missing Dependencies**: Run `pip install -r requirements.txt`
2. **File Not Found**: Ensure DATA0025.TXT is in the same directory
3. **Display Issues**: Check PySide6 and PyQtGraph installation

### Error Messages
- **"No module named 'pandas'"**: Install pandas with `pip install pandas`
- **"No module named 'pyqtgraph'"**: Install pyqtgraph with `pip install pyqtgraph`
- **Array Truth Value Error**: Fixed in current version

## File Structure

```
SleepSense/
├── plot_waves.py           # Main waveform viewer application
├── plot_data.py            # Simple matplotlib plotting script
├── DATA0025.TXT            # Sleep study data file
├── requirements.txt         # Python dependencies
└── WAVEFORM_README.md      # This documentation
```

## Dependencies

- **PySide6**: Modern Qt framework for Python
- **pyqtgraph**: Fast plotting library for real-time data
- **pandas**: Data loading and manipulation
- **numpy**: Numerical operations
- **matplotlib**: Additional plotting capabilities

## Future Enhancements

- [ ] Export functionality (PNG, PDF)
- [ ] Zoom and pan controls
- [ ] Data filtering options
- [ ] Statistical analysis tools
- [ ] Multiple file support
- [ ] Custom color schemes

## Support

For issues and questions:
1. Check this README for common solutions
2. Verify all dependencies are installed
3. Ensure DATA0025.TXT is in the correct location
4. Check Python version compatibility (3.8+)

---

**SleepSense Waveform Viewer** - Professional Sleep Study Data Visualization
