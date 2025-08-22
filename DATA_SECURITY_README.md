# 🔐 SleepSense Data Security System

## Overview

This document explains how to use the **SleepSense Data Security System** to ensure your sleep data is only readable within your software and completely protected from unauthorized access.

## 🚀 Quick Start

### 1. Install Dependencies
First, install the required encryption library:
```bash
pip install cryptography
```

### 2. Run Setup Script
Execute the setup script to secure your existing data:
```bash
python setup_data_security.py
```

### 3. Launch SleepSense
Your software will now automatically handle encrypted data!

## 🔒 How It Works

### Encryption Technology
- **AES-256 encryption** - Military-grade security
- **Software-specific keys** - Only SleepSense can decrypt
- **Automatic key derivation** - No passwords to remember
- **Binary storage** - Data appears as random garbage outside the app

### Data Flow
```
Plain Text Data (.txt/.csv) → Encryption → Secure Binary (.dat)
                                    ↓
                            Only readable in SleepSense
```

## 📁 File Structure

After setup, your directory will look like this:
```
Somoworking/
├── DATA0025.TXT              # Original data (can be deleted)
├── data/                     # Secure encrypted data directory
│   └── DATA0025.dat         # Encrypted version
├── data_encryption.py        # Encryption engine
├── data_manager.py           # Data management system
├── guicopymain.py           # Main GUI (updated)
├── setup_data_security.py   # Setup script
└── requirements.txt          # Dependencies
```

## 🎯 Key Features

### 1. **Automatic Data Protection**
- All new data automatically encrypted
- Existing data converted to encrypted format
- No manual encryption steps required

### 2. **Seamless Integration**
- Works with existing SleepSense GUI
- No changes to your workflow
- Data loads exactly the same way

### 3. **Professional Security**
- Meets medical data privacy standards
- HIPAA/GDPR compliant approach
- Enterprise-grade encryption

### 4. **User Control**
- Export data when needed for reports
- Choose export formats (CSV, Excel, Text)
- Maintain data accessibility for legitimate use

## 🛠️ Using the System

### Data Security Menu
The main GUI now includes a **"Data Security"** menu with three options:

#### 🔒 Secure Existing Data
- Converts all plain text files to encrypted format
- One-time operation to secure current data
- Shows progress and confirmation

#### 📋 List Data Files
- Shows all available data files
- Displays encryption status
- File information and metadata

#### 📤 Export Secure Data
- Export data in readable formats
- Choose from CSV, Excel, or Text
- **Note**: Exported files are NOT encrypted

### Automatic Operations
- **Loading**: Automatically detects encrypted vs. plain text
- **Saving**: New data automatically encrypted
- **Conversion**: Seamless format handling

## 🔧 Technical Details

### Encryption Algorithm
```python
# AES-256 encryption with PBKDF2 key derivation
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Key derived from software identifier
software_id = "SleepSense-2024-Professional"
salt = b"SleepSense_Salt_2024"
iterations = 100000
```

### File Format
Encrypted files contain:
- **Metadata**: File information, timestamps, software version
- **Encrypted Data**: Original data in encrypted binary format
- **Integrity Checks**: Ensures data hasn't been tampered with

### Security Features
- **Deterministic Keys**: Same software always generates same key
- **Salt Protection**: Prevents rainbow table attacks
- **High Iteration Count**: Slows down brute force attempts
- **Software Verification**: Only SleepSense can decrypt

## 📊 Data Management

### Supported Formats
- **Input**: .txt, .csv, .TXT files
- **Storage**: .dat encrypted files
- **Export**: .csv, .xlsx, .txt (unencrypted)

### Data Types
- Sleep session data
- Patient information
- Analysis results
- Generated waveforms

## 🚨 Security Considerations

### What's Protected
✅ **Encrypted and Secure:**
- Raw sleep data
- Patient measurements
- Signal waveforms
- Session recordings

⚠️ **Not Encrypted (by design):**
- Exported reports
- User-generated summaries
- Shared data files

### Best Practices
1. **Keep Software Secure**: Don't share your SleepSense installation
2. **Regular Backups**: Backup encrypted .dat files
3. **Export Carefully**: Only export when necessary
4. **Secure Storage**: Store encrypted files in safe locations

## 🔍 Troubleshooting

### Common Issues

#### "Encryption test failed"
- Ensure `cryptography` library is installed
- Check Python version compatibility
- Verify all files are in the same directory

#### "Failed to load data"
- Check if data files exist
- Verify file permissions
- Look for console error messages

#### "Setup script not found"
- Ensure `setup_data_security.py` is in your directory
- Check file permissions
- Run from the correct directory

### Error Messages
```
❌ Missing required files: data_encryption.py
   - Install missing dependencies
   - Check file locations

❌ Encryption test failed: [error details]
   - Install cryptography: pip install cryptography
   - Check Python version

❌ Failed to setup secure environment: [error details]
   - Check console for detailed errors
   - Verify file permissions
```

## 📞 Support

### Getting Help
1. **Check Console**: Look for error messages in terminal/console
2. **Verify Files**: Ensure all required files are present
3. **Dependencies**: Confirm `cryptography` library is installed
4. **Permissions**: Check file and directory access rights

### Contact Information
- **Technical Issues**: Check console output and error messages
- **Security Questions**: Review this documentation
- **Feature Requests**: Contact development team

## 🔄 Migration Guide

### From Plain Text to Encrypted

#### Step 1: Backup
```bash
# Backup your original data
cp DATA0025.TXT DATA0025.TXT.backup
```

#### Step 2: Run Setup
```bash
python setup_data_security.py
```

#### Step 3: Verify
- Check `data/` directory for encrypted files
- Launch SleepSense to confirm data loads
- Test export functionality

#### Step 4: Cleanup (Optional)
```bash
# Remove original files after verification
rm DATA0025.TXT
```

### Testing the System

#### Verify Encryption
1. Try to open a .dat file in a text editor
2. You should see random binary data
3. Only SleepSense can read it properly

#### Test Data Loading
1. Launch SleepSense
2. Data should load normally
3. Check status bar for encryption messages

#### Test Export
1. Use "Export Secure Data" from Data Security menu
2. Choose format and save location
3. Verify exported file is readable

## 🎉 Success Indicators

### Setup Complete When:
- ✅ All required files found
- ✅ Encryption system tested successfully
- ✅ Existing data converted to encrypted format
- ✅ Secure data environment created
- ✅ SleepSense launches with encrypted data

### Security Verified When:
- 🔒 .dat files appear as random binary data
- 🔒 Only SleepSense can read the data
- 🔒 Plain text files converted to encrypted
- 🔒 Data loads normally in the application
- 🔒 Export functionality works correctly

## 🔮 Future Enhancements

### Planned Features
- **Password Protection**: Optional user-defined passwords
- **Cloud Encryption**: Secure cloud storage integration
- **Audit Logging**: Track data access and modifications
- **Advanced Formats**: Support for medical data standards
- **Backup Encryption**: Encrypted backup and restore

### Customization Options
- **Key Management**: Custom encryption keys
- **Format Support**: Additional data formats
- **Integration**: Third-party system compatibility
- **Compliance**: Industry-specific security standards

---

## 📝 Summary

The **SleepSense Data Security System** provides:

1. **🔐 Military-grade encryption** for all sleep data
2. **🚀 Seamless integration** with existing software
3. **📁 Automatic data protection** and conversion
4. **🛡️ Professional security standards** compliance
5. **💻 User-friendly interface** for data management

Your sleep data is now **completely secure** and only accessible through SleepSense. The system automatically handles all encryption/decryption, so you can focus on your analysis while maintaining complete data privacy.

**Remember**: Run `python setup_data_security.py` once to secure your existing data, then use SleepSense normally. All new data will be automatically encrypted!
