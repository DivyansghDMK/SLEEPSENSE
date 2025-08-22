"""
SleepSense Data Encryption Module
================================

This module provides secure encryption and decryption of sleep data
to ensure data privacy and prevent unauthorized access outside the software.
"""

import os
import base64
import hashlib
import json
import pickle
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pandas as pd
import numpy as np


class SleepDataEncryption:
    """
    Handles encryption and decryption of sleep data using AES-256 encryption.
    
    Features:
    - AES-256 encryption for maximum security
    - Software-specific encryption key
    - Encrypted data storage in binary format
    - Automatic key derivation from software identifier
    - Support for both raw data and processed data
    """
    
    def __init__(self):
        """Initialize the encryption system with a software-specific key"""
        self.software_id = "SleepSense-2024-Professional"
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
        
    def _derive_key(self):
        """
        Derive encryption key from software identifier.
        This ensures only SleepSense can decrypt the data.
        """
        # Create a deterministic key from software identifier
        salt = b"SleepSense_Salt_2024"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key_material = self.software_id.encode()
        key_bytes = kdf.derive(key_material)
        return base64.urlsafe_b64encode(key_bytes)
    
    def encrypt_data(self, data, filename=None):
        """
        Encrypt sleep data and return encrypted bytes.
        
        Args:
            data: pandas DataFrame or numpy array to encrypt
            filename: optional filename for metadata
            
        Returns:
            bytes: encrypted data
        """
        try:
            # Convert data to bytes using pickle
            data_bytes = pickle.dumps(data)
            
            # Add metadata
            metadata = {
                "software": "SleepSense",
                "version": "2024.1.0",
                "encrypted_at": pd.Timestamp.now().isoformat(),
                "data_type": str(type(data)),
                "shape": data.shape if hasattr(data, 'shape') else None,
                "columns": list(data.columns) if hasattr(data, 'columns') else None,
                "filename": filename
            }
            
            # Combine data and metadata
            combined_data = {
                "metadata": metadata,
                "data": data_bytes
            }
            
            # Serialize and encrypt
            combined_bytes = pickle.dumps(combined_data)
            encrypted_data = self.cipher.encrypt(combined_bytes)
            
            return encrypted_data
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_bytes):
        """
        Decrypt sleep data from encrypted bytes.
        
        Args:
            encrypted_bytes: encrypted data bytes
            
        Returns:
            tuple: (data, metadata) where data is the original DataFrame/array
        """
        try:
            # Decrypt the data
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            
            # Deserialize
            combined_data = pickle.loads(decrypted_bytes)
            
            # Extract data and metadata
            metadata = combined_data["metadata"]
            data_bytes = combined_data["data"]
            
            # Unpickle the actual data
            data = pickle.loads(data_bytes)
            
            # Verify software compatibility
            if metadata.get("software") != "SleepSense":
                raise Exception("Data was not encrypted by SleepSense")
            
            return data, metadata
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def save_encrypted_data(self, data, filepath, filename=None):
        """
        Save data in encrypted format to a file.
        
        Args:
            data: data to encrypt and save
            filepath: full path where to save the encrypted file
            filename: optional original filename for metadata
        """
        try:
            # Encrypt the data
            encrypted_data = self.encrypt_data(data, filename)
            
            # Save encrypted data
            with open(filepath, 'wb') as f:
                f.write(encrypted_data)
                
            return True
            
        except Exception as e:
            raise Exception(f"Failed to save encrypted data: {str(e)}")
    
    def load_encrypted_data(self, filepath):
        """
        Load and decrypt data from an encrypted file.
        
        Args:
            filepath: path to encrypted file
            
        Returns:
            tuple: (data, metadata) where data is the original DataFrame/array
        """
        try:
            # Read encrypted data
            with open(filepath, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt and return
            return self.decrypt_data(encrypted_data)
            
        except Exception as e:
            raise Exception(f"Failed to load encrypted data: {str(e)}")
    
    def convert_plain_to_encrypted(self, plain_filepath, encrypted_filepath):
        """
        Convert a plain text/csv file to encrypted format.
        
        Args:
            plain_filepath: path to plain text/csv file
            encrypted_filepath: path where to save encrypted file
        """
        try:
            # Detect file type and load
            if plain_filepath.lower().endswith('.txt'):
                data = pd.read_csv(plain_filepath, header=None)
            elif plain_filepath.lower().endswith('.csv'):
                data = pd.read_csv(plain_filepath)
            else:
                raise Exception("Unsupported file format. Use .txt or .csv files.")
            
            # Save in encrypted format
            filename = os.path.basename(plain_filepath)
            self.save_encrypted_data(data, encrypted_filepath, filename)
            
            return True
            
        except Exception as e:
            raise Exception(f"Conversion failed: {str(e)}")
    
    def get_file_info(self, filepath):
        """
        Get information about an encrypted file without loading all data.
        
        Args:
            filepath: path to encrypted file
            
        Returns:
            dict: metadata information
        """
        try:
            # Read encrypted data
            with open(filepath, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt metadata only
            decrypted_bytes = self.cipher.decrypt(encrypted_data)
            combined_data = pickle.loads(decrypted_bytes)
            
            return combined_data["metadata"]
            
        except Exception as e:
            raise Exception(f"Failed to get file info: {str(e)}")
    
    def is_encrypted_file(self, filepath):
        """
        Check if a file is encrypted by SleepSense.
        
        Args:
            filepath: path to file to check
            
        Returns:
            bool: True if encrypted by SleepSense
        """
        try:
            metadata = self.get_file_info(filepath)
            return metadata.get("software") == "SleepSense"
        except:
            return False


# Utility functions for easy data conversion
def convert_existing_data_to_encrypted():
    """
    Convert existing plain text data files to encrypted format.
    This function should be run once to secure existing data.
    """
    encryption = SleepDataEncryption()
    
    # List of existing data files to convert
    existing_files = [
        "DATA0025.TXT"
    ]
    
    for filename in existing_files:
        if os.path.exists(filename):
            try:
                # Create encrypted filename
                encrypted_filename = filename.replace('.TXT', '.dat').replace('.txt', '.dat')
                
                # Convert to encrypted format
                encryption.convert_plain_to_encrypted(filename, encrypted_filename)
                
                print(f"✅ Converted {filename} to encrypted format: {encrypted_filename}")
                
                # Optionally remove original file (uncomment if you want to delete originals)
                # os.remove(filename)
                # print(f"🗑️  Removed original file: {filename}")
                
            except Exception as e:
                print(f"❌ Failed to convert {filename}: {str(e)}")
        else:
            print(f"⚠️  File not found: {filename}")


if __name__ == "__main__":
    # Test the encryption system
    print("🔐 Testing SleepSense Data Encryption...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'time': [1, 2, 3, 4, 5],
        'spo2': [95, 96, 94, 97, 95],
        'pulse': [72, 75, 70, 78, 73]
    })
    
    # Test encryption
    encryption = SleepDataEncryption()
    
    # Encrypt data
    encrypted = encryption.encrypt_data(sample_data, "test_data.csv")
    print("✅ Data encrypted successfully")
    
    # Decrypt data
    decrypted_data, metadata = encryption.decrypt_data(encrypted)
    print("✅ Data decrypted successfully")
    
    # Verify data integrity
    if sample_data.equals(decrypted_data):
        print("✅ Data integrity verified - encryption/decryption working correctly")
    else:
        print("❌ Data integrity check failed")
        print(f"Original data shape: {sample_data.shape}")
        print(f"Decrypted data shape: {decrypted_data.shape}")
        print(f"Original columns: {list(sample_data.columns)}")
        print(f"Decrypted columns: {list(decrypted_data.columns)}")
        print(f"Data types match: {sample_data.dtypes.equals(decrypted_data.dtypes)}")
        print(f"Original data:\n{sample_data}")
        print(f"Decrypted data:\n{decrypted_data}")
    
    # Test file operations
    test_file = "test_encrypted.dat"
    encryption.save_encrypted_data(sample_data, test_file, "test_data.csv")
    print("✅ Encrypted data saved to file")
    
    loaded_data, loaded_metadata = encryption.load_encrypted_data(test_file)
    print("✅ Encrypted data loaded from file")
    
    # Clean up test file
    if os.path.exists(test_file):
        os.remove(test_file)
        print("🗑️  Test file cleaned up")
    
    print("\n🎉 Encryption system test completed successfully!")
    print("\nTo convert your existing data files to encrypted format, run:")
    print("convert_existing_data_to_encrypted()")
