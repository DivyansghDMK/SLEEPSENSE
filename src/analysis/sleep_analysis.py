"""
Comprehensive sleep analysis for SleepSense Pro
"""

import pandas as pd
import numpy as np


class SleepAnalysis:
    """Handles comprehensive sleep study analysis"""
    
    def __init__(self, sample_rate=10.0):
        self.sample_rate = sample_rate
    
    def analyze_full_study(self, signals):
        """Analyzes the entire dataset to calculate statistics for the report"""
        results = {}
        
        # Basic study info
        time_series = signals['time']
        tib_duration_seconds = (pd.to_datetime(time_series.iloc[-1], unit='s') - 
                               pd.to_datetime(time_series.iloc[0], unit='s')).total_seconds()
        results['tib_hours'] = tib_duration_seconds / 3600.0
        results['patient_id'] = "11"
        results['recording_date'] = "25-08-2025"
        
        # --- Comprehensive Respiratory Analysis ---
        flow = signals['flow_n']
        body_pos = signals['body_pos_n']
        
        # Define thresholds
        is_apnea = flow < 0.1  # 90% reduction
        is_hypopnea = (flow >= 0.1) & (flow < 0.3)  # 70-90% reduction
        is_flow_limitation = (flow >= 0.3) & (flow < 0.5)  # 50-70% reduction
        
        # Event detection with detailed tracking
        apneas, hypopneas, flow_limitations = 0, 0, 0
        apnea_durations, hypopnea_durations = [], []
        max_apnea_duration, max_hypopnea_duration = 0, 0
        in_event = False
        min_samples = int(10 * self.sample_rate)  # 10 seconds minimum
        
        # Position analysis - handle any position values dynamically
        position_counts = {}  # Will be populated dynamically
        position_events = {'supine': {'apneas': 0, 'hypopneas': 0}, 
                          'non_supine': {'apneas': 0, 'hypopneas': 0}}
        
        # REM/NREM analysis (simplified based on activity and position patterns)
        rem_periods = signals['activity_n'] < 0.2  # Low activity periods
        nrem_periods = signals['activity_n'] >= 0.2  # Higher activity periods
        
        rem_apneas, rem_hypopneas = 0, 0
        nrem_apneas, nrem_hypopneas = 0, 0
        
        # Detailed event analysis
        for i in range(len(flow)):
            # Position tracking - handle any position value
            pos = int(body_pos.iloc[i]) if i < len(body_pos) else 0
            if pos not in position_counts:
                position_counts[pos] = 0
            position_counts[pos] += 1
            
            # Event detection
            if not in_event and (is_apnea[i] or is_hypopnea[i]):
                in_event = True
                event_start_index = i
                event_type = 'apnea' if is_apnea[i] else 'hypopnea'
            elif in_event and not (is_apnea[i] or is_hypopnea[i]):
                in_event = False
                event_duration = (i - event_start_index) / self.sample_rate
                
                if (i - event_start_index) >= min_samples:
                    if event_type == 'apnea':
                        apneas += 1
                        apnea_durations.append(event_duration)
                        max_apnea_duration = max(max_apnea_duration, event_duration)
                        
                        # Position-based apnea counting
                        if pos == 0:  # Supine
                            position_events['supine']['apneas'] += 1
                        else:
                            position_events['non_supine']['apneas'] += 1
                            
                        # REM/NREM apnea counting
                        if rem_periods.iloc[i]:
                            rem_apneas += 1
                        else:
                            nrem_apneas += 1
                    else:
                        hypopneas += 1
                        hypopnea_durations.append(event_duration)
                        max_hypopnea_duration = max(max_hypopnea_duration, event_duration)
                        
                        # Position-based hypopnea counting
                        if pos == 0:  # Supine
                            position_events['supine']['hypopneas'] += 1
                        else:
                            position_events['non_supine']['hypopneas'] += 1
                            
                        # REM/NREM hypopnea counting
                        if rem_periods.iloc[i]:
                            rem_hypopneas += 1
                        else:
                            nrem_hypopneas += 1
            
            # Flow limitation detection
            if is_flow_limitation[i]:
                flow_limitations += 1
        
        # Calculate averages
        avg_apnea_duration = np.mean(apnea_durations) if apnea_durations else 0
        avg_hypopnea_duration = np.mean(hypopnea_durations) if hypopnea_durations else 0
        
        # Position percentages - handle dynamic position values
        total_samples = len(body_pos)
        supine_percent = (position_counts.get(0, 0) / total_samples) * 100 if total_samples > 0 else 0
        left_percent = (position_counts.get(1, 0) / total_samples) * 100 if total_samples > 0 else 0
        right_percent = (position_counts.get(2, 0) / total_samples) * 100 if total_samples > 0 else 0
        prone_percent = (position_counts.get(3, 0) / total_samples) * 100 if total_samples > 0 else 0
        
        # Handle any additional positions (4, 5, etc.)
        other_positions = {}
        for pos, count in position_counts.items():
            if pos > 3:  # Any position beyond the standard 4
                other_positions[pos] = (count / total_samples) * 100 if total_samples > 0 else 0
        
        # REM/NREM percentages
        rem_percent = (rem_periods.sum() / len(rem_periods)) * 100
        nrem_percent = 100 - rem_percent
        
        # Calculate indices
        total_events = apneas + hypopneas
        results['ahi'] = total_events / results['tib_hours'] if results['tib_hours'] > 0 else 0
        results['rdi'] = (total_events + flow_limitations) / results['tib_hours'] if results['tib_hours'] > 0 else 0
        
        # Store detailed results
        results['obstructive_apneas'] = int(apneas * 0.75)
        results['central_apneas'] = apneas - results['obstructive_apneas']
        results['hypopneas'] = hypopneas
        results['total_apneas'] = apneas
        results['flow_limitations'] = flow_limitations
        
        # Duration metrics
        results['max_apnea_duration'] = max_apnea_duration
        results['max_hypopnea_duration'] = max_hypopnea_duration
        results['avg_apnea_duration'] = avg_apnea_duration
        results['avg_hypopnea_duration'] = avg_hypopnea_duration
        
        # Position analysis
        results['supine_percent'] = supine_percent
        results['left_percent'] = left_percent
        results['right_percent'] = right_percent
        results['prone_percent'] = prone_percent
        results['other_positions'] = other_positions
        results['supine_apneas'] = position_events['supine']['apneas']
        results['supine_hypopneas'] = position_events['supine']['hypopneas']
        results['non_supine_apneas'] = position_events['non_supine']['apneas']
        results['non_supine_hypopneas'] = position_events['non_supine']['hypopneas']
        
        # REM/NREM analysis
        results['rem_percent'] = rem_percent
        results['nrem_percent'] = nrem_percent
        results['rem_apneas'] = rem_apneas
        results['rem_hypopneas'] = rem_hypopneas
        results['nrem_apneas'] = nrem_apneas
        results['nrem_hypopneas'] = nrem_hypopneas
        results['rem_ahi'] = (rem_apneas + rem_hypopneas) / (results['tib_hours'] * rem_percent / 100) if rem_percent > 0 else 0
        results['nrem_ahi'] = (nrem_apneas + nrem_hypopneas) / (results['tib_hours'] * nrem_percent / 100) if nrem_percent > 0 else 0
        
        # Artifact detection (simplified)
        artifacts = (flow > 0.95).sum() + (flow < 0.05).sum()  # Extreme values
        results['artifact_percent'] = (artifacts / len(flow)) * 100
        
        # --- Oximetry Analysis ---
        spo2_original = 85 + (signals['spo2_n'] * 15)
        results['min_spo2'] = spo2_original.min()
        results['avg_spo2'] = spo2_original.mean()
        results['baseline_spo2'] = np.median(spo2_original)
        
        desaturations = (spo2_original.diff() < -3).sum()  # Drop of >3%
        results['desat_count'] = desaturations
        results['desat_index'] = desaturations / results['tib_hours'] if results['tib_hours'] > 0 else 0
        results['time_below_90'] = (spo2_original < 90).sum() / len(spo2_original) * 100
        
        # --- Snore Analysis ---
        snore_events = (signals['snore_n'] > 0.7).sum()
        results['snore_index'] = snore_events / results['tib_hours'] if results['tib_hours'] > 0 else 0
        
        # --- Heart Rate Analysis ---
        pulse_original = 50 + (signals['pulse_n'] * 70)
        results['min_hr'] = pulse_original.min()
        results['max_hr'] = pulse_original.max()
        results['avg_hr'] = pulse_original.mean()
        
        return results
