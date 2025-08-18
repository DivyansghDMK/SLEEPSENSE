"""
Signal processing utilities for SleepSense application
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Tuple, List, Optional

class SignalProcessor:
    """Signal processing utilities for sleep monitoring"""
    
    def __init__(self, sample_rate: int = 256):
        self.sample_rate = sample_rate
        self.nyquist = sample_rate / 2
    
    def apply_bandpass_filter(self, data: np.ndarray, low_freq: float, high_freq: float) -> np.ndarray:
        """Apply bandpass filter to signal data"""
        if low_freq >= high_freq:
            raise ValueError("Low frequency must be less than high frequency")
        
        if high_freq >= self.nyquist:
            raise ValueError(f"High frequency must be less than Nyquist frequency ({self.nyquist} Hz)")
        
        # Design Butterworth filter
        b, a = signal.butter(4, [low_freq / self.nyquist, high_freq / self.nyquist], btype='band')
        
        # Apply filter
        filtered_data = signal.filtfilt(b, a, data)
        
        return filtered_data
    
    def apply_notch_filter(self, data: np.ndarray, notch_freq: float = 50.0, quality_factor: float = 30.0) -> np.ndarray:
        """Apply notch filter to remove power line interference"""
        # Design notch filter
        b, a = signal.iirnotch(notch_freq, quality_factor, self.sample_rate)
        
        # Apply filter
        filtered_data = signal.filtfilt(b, a, data)
        
        return filtered_data
    
    def compute_fft(self, data: np.ndarray, window_length: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Compute FFT of signal data"""
        if window_length is None:
            window_length = len(data)
        
        # Apply window function
        windowed_data = data[:window_length] * signal.hann(window_length)
        
        # Compute FFT
        fft_data = fft(windowed_data)
        freqs = fftfreq(window_length, 1 / self.sample_rate)
        
        # Return only positive frequencies
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = np.abs(fft_data[:len(fft_data)//2])
        
        return positive_freqs, positive_fft
    
    def compute_power_spectral_density(self, data: np.ndarray, window_length: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Compute power spectral density"""
        freqs, fft_data = self.compute_fft(data, window_length)
        psd = np.abs(fft_data) ** 2
        
        return freqs, psd
    
    def detect_artifacts(self, data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """Detect artifacts using statistical thresholding"""
        # Compute moving average and standard deviation
        window_size = min(100, len(data) // 10)
        if window_size < 10:
            window_size = 10
        
        # Moving statistics
        mean_data = np.convolve(data, np.ones(window_size)/window_size, mode='same')
        std_data = np.sqrt(np.convolve((data - mean_data)**2, np.ones(window_size)/window_size, mode='same'))
        
        # Detect outliers
        artifacts = np.abs(data - mean_data) > (threshold * std_data)
        
        return artifacts
    
    def compute_rms(self, data: np.ndarray) -> float:
        """Compute Root Mean Square of signal"""
        return np.sqrt(np.mean(data**2))
    
    def compute_peak_to_peak(self, data: np.ndarray) -> float:
        """Compute peak-to-peak amplitude"""
        return np.max(data) - np.min(data)
    
    def compute_zero_crossings(self, data: np.ndarray) -> int:
        """Compute number of zero crossings"""
        return np.sum(np.diff(np.sign(data)) != 0)
    
    def extract_features(self, data: np.ndarray) -> dict:
        """Extract basic signal features"""
        features = {
            'rms': self.compute_rms(data),
            'peak_to_peak': self.compute_peak_to_peak(data),
            'zero_crossings': self.compute_zero_crossings(data),
            'mean': np.mean(data),
            'std': np.std(data),
            'min': np.min(data),
            'max': np.max(data)
        }
        
        return features
    
    def segment_signal(self, data: np.ndarray, segment_length: int) -> List[np.ndarray]:
        """Segment signal into fixed-length segments"""
        segments = []
        num_segments = len(data) // segment_length
        
        for i in range(num_segments):
            start_idx = i * segment_length
            end_idx = start_idx + segment_length
            segment = data[start_idx:end_idx]
            segments.append(segment)
        
        return segments
    
    def remove_baseline_wander(self, data: np.ndarray, window_size: int = 100) -> np.ndarray:
        """Remove baseline wander using moving average"""
        if window_size >= len(data):
            window_size = len(data) // 4
        
        # Compute baseline using moving average
        baseline = np.convolve(data, np.ones(window_size)/window_size, mode='same')
        
        # Remove baseline
        corrected_data = data - baseline
        
        return corrected_data
    
    def normalize_signal(self, data: np.ndarray, method: str = 'zscore') -> np.ndarray:
        """Normalize signal data"""
        if method == 'zscore':
            return (data - np.mean(data)) / np.std(data)
        elif method == 'minmax':
            return (data - np.min(data)) / (np.max(data) - np.min(data))
        elif method == 'rms':
            return data / self.compute_rms(data)
        else:
            raise ValueError("Method must be 'zscore', 'minmax', or 'rms'")

class SleepStageAnalyzer:
    """Basic sleep stage analysis utilities"""
    
    def __init__(self, sample_rate: int = 256):
        self.sample_rate = sample_rate
        self.signal_processor = SignalProcessor(sample_rate)
    
    def compute_alpha_power(self, data: np.ndarray) -> float:
        """Compute alpha wave power (8-13 Hz)"""
        filtered_data = self.signal_processor.apply_bandpass_filter(data, 8.0, 13.0)
        return self.signal_processor.compute_rms(filtered_data)
    
    def compute_beta_power(self, data: np.ndarray) -> float:
        """Compute beta wave power (13-30 Hz)"""
        filtered_data = self.signal_processor.apply_bandpass_filter(data, 13.0, 30.0)
        return self.signal_processor.compute_rms(filtered_data)
    
    def compute_theta_power(self, data: np.ndarray) -> float:
        """Compute theta wave power (4-8 Hz)"""
        filtered_data = self.signal_processor.apply_bandpass_filter(data, 4.0, 8.0)
        return self.signal_processor.compute_rms(filtered_data)
    
    def compute_delta_power(self, data: np.ndarray) -> float:
        """Compute delta wave power (0.5-4 Hz)"""
        filtered_data = self.signal_processor.apply_bandpass_filter(data, 0.5, 4.0)
        return self.signal_processor.compute_rms(filtered_data)
    
    def classify_sleep_stage(self, eeg_data: np.ndarray) -> str:
        """Basic sleep stage classification"""
        # Compute power in different frequency bands
        alpha_power = self.compute_alpha_power(eeg_data)
        beta_power = self.compute_beta_power(eeg_data)
        theta_power = self.compute_theta_power(eeg_data)
        delta_power = self.compute_delta_power(eeg_data)
        
        # Simple classification logic (this is a basic example)
        total_power = alpha_power + beta_power + theta_power + delta_power
        
        if total_power == 0:
            return "Unknown"
        
        alpha_ratio = alpha_power / total_power
        beta_ratio = beta_power / total_power
        theta_ratio = theta_power / total_power
        delta_ratio = delta_power / total_power
        
        # Basic classification rules
        if delta_ratio > 0.5:
            return "Deep Sleep (N3)"
        elif theta_ratio > 0.4:
            return "Light Sleep (N2)"
        elif alpha_ratio > 0.3:
            return "Light Sleep (N1)"
        elif beta_ratio > 0.4:
            return "Wake"
        else:
            return "REM Sleep"
    
    def analyze_sleep_architecture(self, eeg_data: np.ndarray, segment_length: int = 30) -> dict:
        """Analyze sleep architecture over time"""
        # Segment the signal
        segments = self.signal_processor.segment_signal(eeg_data, segment_length * self.sample_rate)
        
        # Analyze each segment
        stages = []
        for segment in segments:
            stage = self.classify_sleep_stage(segment)
            stages.append(stage)
        
        # Count stages
        stage_counts = {}
        for stage in stages:
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        # Compute percentages
        total_segments = len(stages)
        stage_percentages = {stage: (count / total_segments) * 100 for stage, count in stage_counts.items()}
        
        return {
            'stages': stages,
            'stage_counts': stage_counts,
            'stage_percentages': stage_percentages,
            'total_time_minutes': total_segments * segment_length / 60
        }
