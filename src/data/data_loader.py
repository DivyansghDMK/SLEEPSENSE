"""
Data loading and file handling for SleepSense Pro
"""

import os
import pandas as pd
import numpy as np
from .mock_data_generator import MockDataGenerator


class DataLoader:
    """Handles data loading from various sources"""
    
    def __init__(self):
        self.data_manager = None
        self.mock_generator = MockDataGenerator()
        
        # Try to use external data manager if available
        try:
            from data_manager import SleepDataManager
            self.data_manager = SleepDataManager()
        except Exception:
            self.data_manager = None
    
    def load_data(self, file_path="DATA0025.TXT"):
        """Load data from file with fallback to mock data"""
        self.data = None
        
        if os.path.exists(file_path):
            if self.data_manager is not None:
                try:
                    self.data = self.data_manager.load_data(file_path)
                    print("Successfully loaded encrypted data.")
                except Exception as e:
                    print(f"Failed to load encrypted data: {e}. Trying as CSV.")
            
            if self.data is None:
                try:
                    self.data = pd.read_csv(file_path, header=None)
                    print("Successfully loaded as plain CSV data.")
                except Exception as e2:
                    print(f"Failed to read as CSV: {e2}. Fallback data will be generated.")
        
        min_required_samples = 3600 * 10  # 1 hour at 10 Hz
        if self.data is None or len(self.data) < min_required_samples:
            if self.data is not None:
                print(f"Insufficient data ({len(self.data)} samples), generating mock data...")
            else:
                print(f"Data file '{file_path}' not found or failed to load, generating mock data...")
            try:
                self.data = self.mock_generator.generate_8_hour_mock_data()
                print(f"Generated mock data with shape: {self.data.shape}")
            except Exception as e:
                print(f"Failed to generate mock data: {e}. Using emergency fallback.")
                self.data = self.mock_generator.create_emergency_fallback_data()
        
        # Final check to ensure data is a DataFrame
        if not isinstance(self.data, pd.DataFrame):
            self.data = pd.DataFrame(self.data)
        
        return self.data
    
    def detect_data_format(self, data):
        """Detect data format and extract signals accordingly"""
        try:
            num_columns = len(data.columns)
            
            if num_columns == 10:  # Current format
                return self._extract_current_format(data)
            elif num_columns >= 12:  # Future format or mock data
                return self._extract_future_format(data)
            else:
                raise ValueError(f"Unknown data format with {num_columns} columns.")
                
        except Exception as e:
            print(f"Error in data format detection: {e}")
            return self._create_emergency_signals()
    
    def _extract_current_format(self, data):
        """Extract signals from current 10-column format"""
        signals = {}
        signals['time'] = pd.Series(data[0].astype(float) / 1000, name='time')  # ms to s
        signals['body_pos'] = pd.Series(data[1].astype(int), name='body_pos')
        signals['pulse'] = pd.Series(data[2].astype(float), name='pulse')
        signals['spo2'] = pd.Series(data[3].astype(float), name='spo2')
        signals['flow'] = pd.Series(data[7].astype(float), name='flow')
        
        # Generate realistic mock waveforms for future signals
        signals['snore'] = self.mock_generator.generate_snore_wave(signals['time'])
        signals['thorax'] = self.mock_generator.generate_thorax_wave(signals['time'])
        signals['abdomen'] = self.mock_generator.generate_abdomen_wave(signals['time'])
        signals['pleth'] = self.mock_generator.generate_pleth_wave(signals['time'])
        signals['activity'] = self.mock_generator.generate_activity_wave(signals['time'])
        
        eeg_signals = self.mock_generator.generate_all_eeg(signals['time'])
        signals['eeg_c3'], signals['eeg_c4'], signals['eeg_f3'], signals['eeg_f4'], signals['eeg_o1'], signals['eeg_o2'] = eeg_signals
        
        return signals
    
    def _extract_future_format(self, data):
        """Extract signals from future 12+ column format"""
        signals = {}
        signals['time'] = pd.Series(data[0].astype(float) / 1000, name='time')  # ms to s
        signals['snore'] = pd.Series(data[1].astype(float), name='snore')
        signals['flow'] = pd.Series(data[2].astype(float), name='flow')
        signals['thorax'] = pd.Series(data[3].astype(float), name='thorax')
        signals['abdomen'] = pd.Series(data[4].astype(float), name='abdomen')
        signals['spo2'] = pd.Series(data[5].astype(float), name='spo2')
        signals['pleth'] = pd.Series(data[6].astype(float), name='pleth')
        signals['pulse'] = pd.Series(data[7].astype(float), name='pulse')
        signals['body_pos'] = pd.Series(data[8].astype(int), name='body_pos')
        signals['activity'] = pd.Series(data[9].astype(float), name='activity')
        
        # Handle EEG signals if available
        if len(data.columns) >= 16:
            signals['eeg_c3'] = pd.Series(data[10].astype(float), name='eeg_c3')
            signals['eeg_c4'] = pd.Series(data[11].astype(float), name='eeg_c4')
            signals['eeg_f3'] = pd.Series(data[12].astype(float), name='eeg_f3')
            signals['eeg_f4'] = pd.Series(data[13].astype(float), name='eeg_f4')
            signals['eeg_o1'] = pd.Series(data[14].astype(float), name='eeg_o1')
            signals['eeg_o2'] = pd.Series(data[15].astype(float), name='eeg_o2')
        else:
            eeg_signals = self.mock_generator.generate_all_eeg(signals['time'])
            signals['eeg_c3'], signals['eeg_c4'], signals['eeg_f3'], signals['eeg_f4'], signals['eeg_o1'], signals['eeg_o2'] = eeg_signals
        
        return signals
    
    def _create_emergency_signals(self):
        """Create emergency fallback signals"""
        print("Creating emergency signals...")
        data = self.mock_generator.create_emergency_fallback_data()
        signals = {}
        signals['time'] = pd.Series(data[0] / 1000)
        signals['snore'] = pd.Series(data[1])
        signals['flow'] = pd.Series(data[2])
        # Add other signals as needed
        return signals
