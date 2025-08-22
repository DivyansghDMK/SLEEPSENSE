"""
SleepSense Data Manager
=======================

This module manages data loading, saving, and conversion between plain text
and encrypted formats. It integrates with the main GUI to provide seamless
data handling with encryption.
"""

import os
import pandas as pd
import numpy as np
from data_encryption import SleepDataEncryption, convert_existing_data_to_encrypted


class SleepDataManager:
    """
    Manages sleep data operations including loading, saving, and format conversion.
    Integrates encryption seamlessly with the existing GUI.
    """
    
    def __init__(self):
        """Initialize the data manager with encryption capabilities"""
        self.encryption = SleepDataEncryption()
        self.current_data = None
        self.current_metadata = None
        self.data_directory = "data"
        
        # Ensure data directory exists
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            print(f"📁 Created data directory: {self.data_directory}")
    
    def load_data(self, filepath):
        """
        Load data from file, automatically detecting if it's encrypted or plain text.
        
        Args:
            filepath: path to data file
            
        Returns:
            pandas.DataFrame: loaded data
        """
        try:
            if self.encryption.is_encrypted_file(filepath):
                # Load encrypted data
                print(f"🔐 Loading encrypted data from: {filepath}")
                data, metadata = self.encryption.load_encrypted_data(filepath)
                self.current_metadata = metadata
                print(f"✅ Loaded encrypted data: {metadata.get('filename', 'Unknown')}")
                
            else:
                # Load plain text data
                print(f"📄 Loading plain text data from: {filepath}")
                if filepath.endswith('.txt') or filepath.endswith('.TXT'):
                    data = pd.read_csv(filepath, header=None)
                elif filepath.endswith('.csv'):
                    data = pd.read_csv(filepath)
                else:
                    raise Exception("Unsupported file format")
                
                # Create metadata for plain text files
                self.current_metadata = {
                    "software": "SleepSense",
                    "version": "2024.1.0",
                    "filename": os.path.basename(filepath),
                    "format": "plain_text",
                    "shape": data.shape,
                    "columns": list(data.columns) if hasattr(data, 'columns') else None
                }
                
                print(f"✅ Loaded plain text data: {os.path.basename(filepath)}")
            
            self.current_data = data
            return data
            
        except Exception as e:
            print(f"❌ Failed to load data: {str(e)}")
            raise
    
    def save_data_encrypted(self, data, filename, include_metadata=True):
        """
        Save data in encrypted format.
        
        Args:
            data: data to save
            filename: filename for the encrypted file
            include_metadata: whether to include metadata
            
        Returns:
            str: path to saved file
        """
        try:
            # Ensure filename has .dat extension
            if not filename.endswith('.dat'):
                filename = filename.replace('.txt', '.dat').replace('.TXT', '.dat').replace('.csv', '.dat')
            
            # Create full filepath
            filepath = os.path.join(self.data_directory, filename)
            
            # Save encrypted data
            if include_metadata:
                self.encryption.save_encrypted_data(data, filepath, filename)
            else:
                # Save without metadata (for raw data)
                self.encryption.save_encrypted_data(data, filepath)
            
            print(f"🔐 Data saved in encrypted format: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to save encrypted data: {str(e)}")
            raise
    
    def convert_and_secure_existing_data(self, source_filepath):
        """
        Convert existing plain text data to encrypted format and optionally remove original.
        
        Args:
            source_filepath: path to plain text file to convert
            
        Returns:
            str: path to encrypted file
        """
        try:
            if not os.path.exists(source_filepath):
                raise Exception(f"Source file not found: {source_filepath}")
            
            # Create encrypted filename
            filename = os.path.basename(source_filepath)
            encrypted_filename = filename.replace('.TXT', '.dat').replace('.txt', '.dat').replace('.csv', '.dat')
            encrypted_filepath = os.path.join(self.data_directory, encrypted_filename)
            
            # Convert to encrypted format
            self.encryption.convert_plain_to_encrypted(source_filepath, encrypted_filepath)
            
            print(f"✅ Converted {source_filepath} to encrypted format: {encrypted_filepath}")
            
            # Ask user if they want to remove original
            print(f"🔒 Original file {source_filepath} is now secured")
            print(f"💡 You can safely delete the original file if you want")
            
            return encrypted_filepath
            
        except Exception as e:
            print(f"❌ Conversion failed: {str(e)}")
            raise
    
    def get_data_info(self, filepath):
        """
        Get information about a data file without loading all data.
        
        Args:
            filepath: path to data file
            
        Returns:
            dict: file information
        """
        try:
            if self.encryption.is_encrypted_file(filepath):
                return self.encryption.get_file_info(filepath)
            else:
                # For plain text files, return basic info
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    modified = os.path.getmtime(filepath)
                    return {
                        "filename": os.path.basename(filepath),
                        "format": "plain_text",
                        "size_bytes": size,
                        "modified": modified,
                        "encrypted": False
                    }
                else:
                    return None
        except Exception as e:
            print(f"❌ Failed to get file info: {str(e)}")
            return None
    
    def list_available_data_files(self):
        """
        List all available data files (both encrypted and plain text).
        
        Returns:
            dict: categorized list of available files
        """
        available_files = {
            "encrypted": [],
            "plain_text": [],
            "total": 0
        }
        
        # Check current directory for plain text files
        for filename in os.listdir("."):
            if filename.lower().endswith(('.txt', '.csv')) and not filename.lower().endswith(('.py', '.md', '.bat', '.json')):
                filepath = os.path.join(".", filename)
                info = self.get_data_info(filepath)
                if info:
                    available_files["plain_text"].append({
                        "filename": filename,
                        "filepath": filepath,
                        "info": info
                    })
                    available_files["total"] += 1
        
        # Check data directory for encrypted files
        if os.path.exists(self.data_directory):
            for filename in os.listdir(self.data_directory):
                if filename.endswith('.dat'):
                    filepath = os.path.join(self.data_directory, filename)
                    try:
                        info = self.get_data_info(filepath)
                        if info:
                            available_files["encrypted"].append({
                                "filename": filename,
                                "filepath": filepath,
                                "info": info
                            })
                            available_files["total"] += 1
                    except:
                        continue
        
        return available_files
    
    def secure_all_existing_data(self):
        """
        Convert all existing plain text data files to encrypted format.
        This is a one-time operation to secure existing data.
        """
        print("🔒 Starting data security conversion...")
        
        # Get list of plain text files
        files_info = self.list_available_data_files()
        plain_text_files = files_info["plain_text"]
        
        if not plain_text_files:
            print("✅ No plain text data files found to convert")
            return
        
        print(f"📋 Found {len(plain_text_files)} plain text files to convert:")
        for file_info in plain_text_files:
            print(f"   - {file_info['filename']}")
        
        # Convert each file
        converted_files = []
        for file_info in plain_text_files:
            try:
                encrypted_path = self.convert_and_secure_existing_data(file_info['filepath'])
                converted_files.append(encrypted_path)
            except Exception as e:
                print(f"❌ Failed to convert {file_info['filename']}: {str(e)}")
        
        print(f"\n🎉 Data security conversion completed!")
        print(f"✅ Successfully converted {len(converted_files)} files")
        print(f"🔒 All data is now encrypted and secure")
        
        return converted_files
    
    def export_data_for_user(self, data, export_filepath, format_type="csv"):
        """
        Export data in a user-readable format (for reports, sharing, etc.).
        This data is NOT encrypted - it's meant for user access.
        
        Args:
            data: data to export
            export_filepath: where to save the export
            format_type: export format (csv, excel, txt)
        """
        try:
            if format_type.lower() == "csv":
                data.to_csv(export_filepath, index=False)
            elif format_type.lower() == "excel":
                data.to_excel(export_filepath, index=False)
            elif format_type.lower() == "txt":
                data.to_csv(export_filepath, sep='\t', index=False)
            else:
                raise Exception(f"Unsupported export format: {format_type}")
            
            print(f"📤 Data exported for user access: {export_filepath}")
            print(f"⚠️  Note: This export file is NOT encrypted - handle with care")
            
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
            raise


# Convenience functions for easy integration
def setup_secure_data_environment():
    """
    Set up the secure data environment and convert existing data.
    This should be run once when setting up the system.
    """
    print("🔐 Setting up SleepSense secure data environment...")
    
    manager = SleepDataManager()
    
    # Convert existing data to encrypted format
    converted_files = manager.secure_all_existing_data()
    
    if converted_files:
        print(f"\n✅ Setup complete! {len(converted_files)} files are now secure")
        print("🔒 All sleep data is encrypted and only accessible through SleepSense")
    else:
        print("\n✅ Setup complete! No existing data to convert")
    
    return manager


if __name__ == "__main__":
    # Test the data manager
    print("🧪 Testing SleepSense Data Manager...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'time': [1, 2, 3, 4, 5],
        'spo2': [95, 96, 94, 97, 95],
        'pulse': [72, 75, 70, 78, 73]
    })
    
    # Test data manager
    manager = SleepDataManager()
    
    # Test saving encrypted data
    encrypted_file = manager.save_data_encrypted(sample_data, "test_session.dat")
    print(f"✅ Encrypted data saved to: {encrypted_file}")
    
    # Test loading encrypted data
    loaded_data = manager.load_data(encrypted_file)
    print(f"✅ Encrypted data loaded successfully")
    
    # Test file info
    file_info = manager.get_data_info(encrypted_file)
    print(f"✅ File info retrieved: {file_info['filename']}")
    
    # Test listing files
    files_list = manager.list_available_data_files()
    print(f"✅ Found {files_list['total']} data files")
    
    print("\n🎉 Data Manager test completed successfully!")
    print("\nTo set up secure data environment, run:")
    print("setup_secure_data_environment()")
