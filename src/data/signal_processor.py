"""
Signal processing and normalization for SleepSense Pro
"""

import pandas as pd
import numpy as np


class SignalProcessor:
    """Handles signal processing, normalization, and analysis"""
    
    def __init__(self):
        self.sample_rate = 10.0
    
    def compute_sampling_rate(self, time_series):
        """Estimate sampling rate (Hz) from time series in seconds"""
        try:
            t = time_series.values
            if len(t) < 3:
                self.sample_rate = 10.0
                return
            dt = np.median(np.diff(t))
            if dt <= 0:
                self.sample_rate = 10.0
            else:
                self.sample_rate = float(1.0 / dt)
        except Exception:
            self.sample_rate = 10.0
    
    def normalize(self, series):
        """Normalize signal data to prevent extreme values"""
        try:
            if series is None or len(series) == 0:
                return pd.Series([0.5] * 100)  # Return default values
            
            if not pd.api.types.is_numeric_dtype(series):
                series = pd.to_numeric(series, errors='coerce')
            
            series = series.replace([np.inf, -np.inf], np.nan)
            
            if series.isna().any():
                median_val = series.median()
                if pd.isna(median_val): 
                    median_val = 0.0
                series = series.fillna(median_val)
            
            min_val, max_val = series.min(), series.max()
            
            if min_val == max_val:
                return pd.Series([0.5] * len(series))
            
            normalized = (series - min_val) / (max_val - min_val)
            return np.clip(normalized, 0.0, 1.0)
            
        except Exception as e:
            print(f"Error normalizing signal: {e}")
            return pd.Series([0.5] * 100)
    
    def apply_moving_average(self, series, window_samples):
        """Centered moving average for smoothing (plotting only)"""
        try:
            w = int(window_samples)
            if w < 3:
                w = 3
            if w % 2 == 0:
                w += 1  # make it odd to center better
            kernel = np.ones(w) / w
            arr = series.values.astype(float)
            smoothed = np.convolve(arr, kernel, mode='same')
            # Re-normalize to [0,1] to keep plotting consistent
            mn, mx = np.min(smoothed), np.max(smoothed)
            if mx - mn <= 0:
                return pd.Series(np.full_like(smoothed, 0.5), index=series.index)
            return pd.Series((smoothed - mn) / (mx - mn), index=series.index)
        except Exception:
            return series
    
    def normalize_all_signals(self, signals):
        """Normalize all available signals and create fallback if error occurs"""
        try:
            normalized_signals = {}
            
            # Normalize each signal
            for key, signal in signals.items():
                if key != 'time':  # Don't normalize time
                    normalized_signals[f"{key}_n"] = self.normalize(signal)
                else:
                    normalized_signals[key] = signal
            
            # Create smoothed airflow for plotting
            if 'flow_n' in normalized_signals:
                normalized_signals['flow_plot'] = self.apply_moving_average(
                    normalized_signals['flow_n'], 
                    max(3, int(self.sample_rate * 0.5))
                )
            
            return normalized_signals
            
        except Exception as e:
            print(f"Error in signal normalization: {e}")
            return self.create_normalized_fallback_signals(signals)
    
    def create_normalized_fallback_signals(self, signals):
        """Create normalized fallback signals if normalization fails"""
        print("Creating normalized fallback signals...")
        # Create zero series if normalization fails
        zero_series = pd.Series(np.zeros(len(signals.get('time', pd.Series([0])))))
        fallback_signals = {}
        
        for key in signals.keys():
            if key == 'time':
                fallback_signals[key] = signals[key]
            else:
                fallback_signals[f"{key}_n"] = zero_series
        
        return fallback_signals
