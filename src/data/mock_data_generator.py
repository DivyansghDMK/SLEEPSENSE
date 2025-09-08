"""
Mock data generation for SleepSense Pro
"""

import pandas as pd
import numpy as np


class MockDataGenerator:
    """Generates realistic mock sleep data for testing and demonstration"""
    
    def generate_8_hour_mock_data(self):
        """Generate 8 hours of mock sleep data"""
        duration_s, fs = 8 * 3600, 10
        n_samples = duration_s * fs
        t = np.arange(n_samples) / fs
        time_ms = t * 1000
        
        data = np.zeros((n_samples, 16))
        data[:, 0] = time_ms
        data[:, 1] = 0.5 * np.sin(2 * np.pi * 0.1 * t)  # Snore
        data[:, 2] = 0.8 * np.sin(2 * np.pi * 0.3 * t)  # Flow
        data[:, 3] = data[:, 2]  # Thorax
        data[:, 4] = data[:, 2]  # Abdomen
        data[:, 5] = 98 - 2 * (np.sin(2 * np.pi * 0.0001 * t) > 0.8)  # SpO2
        data[:, 6] = 0.9 * np.sin(2 * np.pi * 1.2 * t)  # Pleth
        data[:, 7] = 75 - 10 * np.sin(2 * np.pi * 0.0002 * t)  # Pulse
        data[:, 8] = np.floor(t / 3600) % 4  # Body Pos
        data[:, 9] = 0.1 + 0.8 * (np.sin(2 * np.pi * 0.0005 * t) > 0.95)  # Activity
        data[:, 10] = 0.8 * np.sin(2 * np.pi * 10 * t)  # EEG C3
        data[:, 11] = 0.7 * np.sin(2 * np.pi * 12 * t)  # EEG C4
        data[:, 12] = 0.6 * np.sin(2 * np.pi * 6 * t)  # EEG F3
        data[:, 13] = 0.5 * np.sin(2 * np.pi * 8 * t)  # EEG F4
        data[:, 14] = 0.9 * np.sin(2 * np.pi * 11 * t)  # EEG O1
        data[:, 15] = 0.9 * np.sin(2 * np.pi * 11 * t)  # EEG O2
        
        return pd.DataFrame(data)
    
    def create_emergency_fallback_data(self):
        """Create emergency fallback data"""
        print("Creating emergency fallback data...")
        return self.generate_8_hour_mock_data()
    
    def generate_snore_wave(self, time):
        """Generate realistic snore waveform with random bursts"""
        base_freq = 0.5
        snore = np.sin(2 * np.pi * base_freq * time) * 0.3
        burst_interval = max(200, len(time) // 20)
        for i in range(0, len(time), burst_interval):
            if np.random.random() > 0.8:
                burst_start = i
                burst_duration = min(100, len(time) - i)
                burst_end = burst_start + burst_duration
                if burst_end <= len(time):
                    burst_time = time[burst_start:burst_end] - time[burst_start]
                    burst_freq = np.random.uniform(0.8, 1.5)
                    burst_amp = np.random.uniform(0.5, 1.0)
                    snore[burst_start:burst_end] += burst_amp * np.sin(2 * np.pi * burst_freq * burst_time)
        return pd.Series(snore, name='snore')
    
    def generate_thorax_wave(self, time):
        """Generate realistic thorax movement (breathing pattern)"""
        breathing_freq = np.random.uniform(0.2, 0.33)
        thorax = np.sin(2 * np.pi * breathing_freq * time)
        depth_variation = 0.3 * np.sin(2 * np.pi * 0.05 * time)
        thorax *= (1 + depth_variation)
        thorax += 0.1 * np.random.randn(len(time))
        return pd.Series(thorax, name='thorax')
    
    def generate_abdomen_wave(self, time):
        """Generate realistic abdomen movement (slightly different from thorax)"""
        breathing_freq = np.random.uniform(0.2, 0.33)
        phase_diff = np.random.uniform(0.1, 0.3)
        abdomen = np.sin(2 * np.pi * breathing_freq * time + phase_diff)
        depth_variation = 0.25 * np.sin(2 * np.pi * 0.04 * time)
        abdomen *= (1 + depth_variation)
        abdomen += 0.08 * np.random.randn(len(time))
        return pd.Series(abdomen, name='abdomen')
    
    def generate_pleth_wave(self, time):
        """Generate realistic plethysmography waveform (blood volume changes)"""
        heart_freq = np.random.uniform(1.0, 1.67)
        pleth = np.sin(2 * np.pi * heart_freq * time)
        resp_freq = np.random.uniform(0.2, 0.33)
        resp_mod = 0.4 * np.sin(2 * np.pi * resp_freq * time)
        pleth *= (1 + resp_mod)
        pleth += 0.3 * np.sin(2 * np.pi * 2 * heart_freq * time)
        pleth += 0.1 * np.sin(2 * np.pi * 3 * heart_freq * time)
        pleth += 0.05 * np.random.randn(len(time))
        return pd.Series(pleth, name='pleth')
    
    def generate_activity_wave(self, time):
        """Generate realistic activity pattern (sleep/wake cycles)"""
        activity = np.zeros_like(time)
        check_interval = max(300, len(time) // 15)
        for i in range(0, len(time), check_interval):
            if np.random.random() > 0.9:
                wake_start = i
                wake_duration = min(200, len(time) - i)
                wake_end = wake_start + wake_duration
                if wake_end <= len(time):
                    transition_length = min(30, wake_duration // 2)
                    if transition_length > 0:
                        activity[wake_start:wake_start + transition_length] = np.linspace(0, 1, transition_length)
                    if wake_duration > 2 * transition_length:
                        activity[wake_start + transition_length:wake_end - transition_length] = 1.0
                    if transition_length > 0:
                        activity[wake_end - transition_length:wake_end] = np.linspace(1, 0, transition_length)
        activity += 0.05 * np.random.randn(len(time))
        activity = np.clip(activity, 0, 1)
        return pd.Series(activity, name='activity')
    
    def generate_eeg_wave(self, time, channel):
        """Generate realistic EEG waveform for different channels"""
        alpha_freq = np.random.uniform(8, 13)
        if channel in ['c3', 'c4']:
            beta_freq = np.random.uniform(15, 25)
            eeg = (0.6 * np.sin(2 * np.pi * alpha_freq * time) + 0.4 * np.sin(2 * np.pi * beta_freq * time))
        elif channel in ['f3', 'f4']:
            theta_freq = np.random.uniform(5, 7)
            eeg = (0.5 * np.sin(2 * np.pi * alpha_freq * time) + 0.5 * np.sin(2 * np.pi * theta_freq * time))
        elif channel in ['o1', 'o2']:
            eeg = 0.8 * np.sin(2 * np.pi * alpha_freq * time)
        else:
            eeg = np.sin(2 * np.pi * alpha_freq * time)
        
        delta_freq = np.random.uniform(0.5, 2)
        eeg += 0.3 * np.sin(2 * np.pi * delta_freq * time)
        eeg += 0.1 * np.random.randn(len(time))
        
        return pd.Series(eeg, name=f'eeg_{channel}')
    
    def generate_all_eeg(self, time_series):
        """Helper to generate all 6 mock EEG signals at once"""
        return (
            self.generate_eeg_wave(time_series, 'c3'),
            self.generate_eeg_wave(time_series, 'c4'),
            self.generate_eeg_wave(time_series, 'f3'),
            self.generate_eeg_wave(time_series, 'f4'),
            self.generate_eeg_wave(time_series, 'o1'),
            self.generate_eeg_wave(time_series, 'o2')
        )
