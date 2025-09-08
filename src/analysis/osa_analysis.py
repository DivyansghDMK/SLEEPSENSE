"""
OSA (Obstructive Sleep Apnea) analysis for SleepSense Pro
"""

import pandas as pd
import numpy as np


class OSAAnalysis:
    """Handles OSA analysis and event detection"""
    
    def __init__(self, sample_rate=10.0):
        self.sample_rate = sample_rate
        self.detected_events = []
    
    def detect_respiratory_events(self, signals, start_time, end_time):
        """Detect apnea and hypopnea events using clinical criteria"""
        self.detected_events.clear()
        
        # Get data indices
        time_series = signals['time']
        start_idx = time_series.searchsorted(start_time, side='left')
        end_idx = time_series.searchsorted(end_time, side='right')
        
        flow_data = signals['flow_n'].iloc[start_idx:end_idx]
        time_data = time_series.iloc[start_idx:end_idx]
        
        # Detect periods of reduced/absent airflow
        flow_threshold_apnea = 0.1  # 90% reduction = apnea
        flow_threshold_hypopnea = 0.3  # 70% reduction = hypopnea
        min_duration = 10.0  # Minimum 10 seconds for clinical significance
        
        in_event = False
        event_start = None
        event_type = None
        
        for i, (time_val, flow_val) in enumerate(zip(time_data, flow_data)):
            if not in_event:
                if flow_val < flow_threshold_apnea:
                    in_event = True
                    event_start = time_val
                    event_type = 'Apnea'
                elif flow_val < flow_threshold_hypopnea:
                    in_event = True
                    event_start = time_val
                    event_type = 'Hypopnea'
            else:
                if flow_val > flow_threshold_hypopnea:
                    # Event ended
                    event_duration = time_val - event_start
                    if event_duration >= min_duration:
                        self.detected_events.append({
                            'type': event_type,
                            'start_time': event_start,
                            'end_time': time_val,
                            'duration': event_duration
                        })
                    in_event = False
                    event_start = None
                    event_type = None
        
        return self.detected_events
    
    def clear_detected_events(self):
        """Clear all detected events"""
        self.detected_events.clear()
    
    def get_event_summary(self):
        """Get summary of detected events"""
        event_count = len(self.detected_events)
        apnea_count = len([e for e in self.detected_events if e['type'] == 'Apnea'])
        hypopnea_count = len([e for e in self.detected_events if e['type'] == 'Hypopnea'])
        
        return {
            'total_events': event_count,
            'apnea_count': apnea_count,
            'hypopnea_count': hypopnea_count
        }
    
    def get_events_in_timeframe(self, start_time, end_time):
        """Get events within a specific timeframe"""
        return [event for event in self.detected_events 
                if event['start_time'] >= start_time and event['end_time'] <= end_time]
