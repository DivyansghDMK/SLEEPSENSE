# SleepSense - Medical Device GUI Application

A comprehensive, modular Python GUI application for sleep monitoring and analysis, similar to SomnoMedics medical devices. Built with PySide6 for a professional medical device interface.

## Features

### 🔐 Authentication System
- Secure user login with encrypted passwords
- Session management with automatic timeout
- Role-based access control (Admin/User)
- SQLite database for user management

### 🔐 Authentication
- Secure user login and registration
- Role-based access control (Admin/User)
- SQLite database for user management
- Success confirmation popup after authentication

### 📊 Medical Data Monitoring
- Real-time display of 12 medical parameters
- SW (Sleep/Wake), Snore, Flow, SpO2 Events, HR (Heart Rate), Position, Activity, SpO2, Thorax, Abdomen, Pleth, Pulse
- Static mock wave data for demonstration
- Professional medical device interface design
- Left panel: Parameter list with current values
- Right panel: Common graph showing all waves combined

### 🌊 Waveform Analysis
- Multi-channel signal display (EEG, EOG, EMG, ECG)
- Real-time waveform plotting with pyqtgraph
- Channel selection and individual settings
- Recording controls with start/stop functionality
- Time window and amplitude controls
- Auto-scaling and filter options
- Analysis tools (FFT, Sleep Stage Analysis)

### 🎨 Professional UI
- Medical device-grade interface design
- Dark/light theme support
- Responsive layout with proper spacing
- Professional color scheme and typography
- Intuitive navigation and controls

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
src/
├── auth/           # Authentication and user management
├── config/         # Application settings and configuration
├── gui/            # User interface components
├── utils/          # Utility functions and logging
└── data/           # Data handling and processing (future)
```

## Requirements

- Python 3.8+
- PySide6
- numpy
- matplotlib
- scipy
- pyqtgraph
- cryptography
- pillow

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd SleepSenseDivyansh
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

```bash
python main.py
```

### Default Login Credentials

- **Username:** `admin`
- **Password:** `admin123`

**⚠️ Important:** Change these credentials in production!

### Navigation

1. **Login Page:** Enter credentials to access the system
2. **Authentication Success:** Confirmation popup after successful login
3. **Medical Data Page:** Real-time monitoring of medical channels (snore, flow, thorax, abdomen, SpO2, pleth, pulse, activity, body position)
4. **Waveforms:** Real-time signal analysis and recording (accessible via menu)

### Recording Waveforms

1. Navigate to the Waveforms page
2. Select desired channels (EEG, EOG, EMG, ECG)
3. Adjust time window and amplitude settings
4. Click "Start Recording" to begin
5. Monitor real-time signals
6. Click "Stop Recording" when finished

## Configuration

The application uses a JSON-based configuration system. Key settings include:

- **Sample Rate:** 256 Hz (configurable)
- **Channels:** EEG, EOG, EMG, ECG
- **Recording Duration:** 3600 seconds (1 hour)
- **Session Timeout:** 1800 seconds (30 minutes)

## Development

### Project Structure

```
SleepSenseDivyansh/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── __init__.py
│   ├── auth/             # Authentication module
│   ├── config/           # Configuration module
│   ├── gui/              # GUI components
│   └── utils/            # Utilities
├── data/                  # Data storage (created at runtime)
├── logs/                  # Application logs (created at runtime)
└── assets/                # Images and resources
```

### Adding New Features

1. **New Page:** Create a new widget in `src/gui/`
2. **New Module:** Add to appropriate package in `src/`
3. **Configuration:** Extend `src/config/settings.py`
4. **Authentication:** Modify `src/auth/authentication.py`

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document all public methods and classes
- Maintain consistent naming conventions

## Security Features

- Password hashing with SHA-256
- Secure session token generation
- Automatic session timeout
- SQL injection protection
- Input validation and sanitization

## Medical Device Compliance

This application is designed to meet medical device interface requirements:

- **User Authentication:** Secure access control
- **Audit Trail:** Activity logging and session management
- **Data Integrity:** Secure data handling and storage
- **Professional Interface:** Medical-grade UI/UX design
- **Real-time Processing:** Live signal monitoring and analysis

## Future Enhancements

- [ ] Data export to EDF format
- [ ] Advanced signal processing filters
- [ ] Sleep stage classification algorithms
- [ ] Patient database management
- [ ] Report generation and printing
- [ ] Network connectivity for remote monitoring
- [ ] Mobile application companion
- [ ] Cloud data synchronization

## Troubleshooting

### Common Issues

1. **Import Errors:** Ensure all dependencies are installed
2. **Display Issues:** Check PySide6 installation and display drivers
3. **Performance:** Adjust update frequency in timer settings
4. **Database Errors:** Check file permissions for SQLite database

### Logs

Application logs are stored in the `logs/` directory with timestamps for debugging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation and logs

## Disclaimer

This software is for educational and development purposes. For medical use, ensure compliance with relevant regulations and standards.

---

**SleepSense** - Professional Sleep Monitoring Interface
*Built with Python and PySide6*
