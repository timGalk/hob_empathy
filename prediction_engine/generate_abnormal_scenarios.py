"""
Abnormal EEG Scenario Generator

Generates realistic abnormal EEG patterns designed to trigger the prediction system.
Includes various seizure types, artifacts, and anomalies for testing and demonstration.

Usage:
    python generate_abnormal_scenarios.py --scenario absence_seizure --duration 30 --output test_data/
    python generate_abnormal_scenarios.py --all --duration 60 --output test_data/
"""

import numpy as np
import pandas as pd
import os
import argparse
from datetime import datetime
from typing import Tuple, List, Dict, Optional
from enum import Enum


class AbnormalScenario(Enum):
    """Types of abnormal scenarios that can trigger predictions"""
    ABSENCE_SEIZURE = "absence_seizure"          # Classic 3 Hz spike-wave
    TONIC_CLONIC = "tonic_clonic"                # Generalized seizure pattern
    FOCAL_SEIZURE = "focal_seizure"              # Localized abnormality
    MYOCLONIC_JERK = "myoclonic_jerk"            # Brief muscle jerk pattern
    PROGRESSIVE_DETERIORATION = "progressive"    # Gradual worsening
    BURST_SUPPRESSION = "burst_suppression"      # ICU-like pattern
    STATUS_EPILEPTICUS = "status_epilepticus"    # Continuous seizure activity
    MIXED_ABNORMALITIES = "mixed"                # Various abnormalities combined


class AbnormalEEGGenerator:
    """
    Generates abnormal EEG scenarios for triggering prediction systems
    """
    
    def __init__(self, sampling_rate: int = 250, n_channels: int = 8):
        """
        Initialize the generator
        
        Args:
            sampling_rate: Sampling frequency in Hz
            n_channels: Number of EEG channels (F4, C4, P4, O2, O1, F3, C3, P3)
        """
        self.fs = sampling_rate
        self.n_channels = n_channels
        self.channel_names = ['F4', 'C4', 'P4', 'O2', 'O1', 'F3', 'C3', 'P3']
        
        # Normal EEG parameters
        self.normal_amplitude = {
            'delta': 30.0,   # 0.5-4 Hz
            'theta': 25.0,   # 4-8 Hz  
            'alpha': 40.0,   # 8-12 Hz
            'beta': 15.0,    # 12-30 Hz
            'gamma': 5.0     # 30-45 Hz
        }
    
    def _pink_noise(self, n_samples: int) -> np.ndarray:
        """Generate pink (1/f) noise"""
        white = np.random.randn(n_samples)
        fft_white = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(n_samples)
        pink_spectrum = fft_white / (np.sqrt(freqs + 1e-10))
        pink = np.fft.irfft(pink_spectrum, n=n_samples)
        return pink / (np.std(pink) + 1e-10)
    
    def generate_normal_baseline(self, duration_samples: int) -> np.ndarray:
        """Generate normal baseline EEG"""
        t = np.arange(duration_samples) / self.fs
        eeg = np.zeros((duration_samples, self.n_channels))
        
        for ch in range(self.n_channels):
            # Channel-specific variations
            alpha_amp = self.normal_amplitude['alpha'] * (1.5 if ch in [3, 4] else 1.0)  # O1, O2
            beta_amp = self.normal_amplitude['beta'] * (1.3 if ch in [0, 5] else 1.0)    # F4, F3
            
            # Generate frequency components with random phases
            signal = (
                self.normal_amplitude['delta'] * np.sin(2*np.pi*2*t + np.random.uniform(0, 2*np.pi)) +
                self.normal_amplitude['theta'] * np.sin(2*np.pi*6*t + np.random.uniform(0, 2*np.pi)) +
                alpha_amp * np.sin(2*np.pi*10*t + np.random.uniform(0, 2*np.pi)) +
                beta_amp * np.sin(2*np.pi*20*t + np.random.uniform(0, 2*np.pi)) +
                self.normal_amplitude['gamma'] * np.sin(2*np.pi*35*t + np.random.uniform(0, 2*np.pi))
            )
            
            eeg[:, ch] = signal + self._pink_noise(duration_samples) * 8.0
        
        return eeg
    
    def generate_absence_seizure(self, duration_seconds: int = 30) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generate classic absence seizure pattern (3 Hz spike-wave discharge)
        
        This is the most common pattern the model should detect.
        Typically lasts 5-30 seconds with abrupt onset and offset.
        """
        n_samples = duration_seconds * self.fs
        eeg = np.zeros((n_samples, self.n_channels))
        labels = ['normal'] * n_samples
        
        # Define seizure events (multiple brief seizures)
        seizure_events = [
            (2.0, 8.0),    # First seizure: 2-8 seconds
            (15.0, 22.0),  # Second seizure: 15-22 seconds
            (26.0, 29.0),  # Third seizure: 26-29 seconds
        ]
        
        for start_sec, end_sec in seizure_events:
            if end_sec > duration_seconds:
                continue
                
            start_idx = int(start_sec * self.fs)
            end_idx = int(end_sec * self.fs)
            seizure_duration = end_idx - start_idx
            
            t = np.arange(seizure_duration) / self.fs
            
            for ch in range(self.n_channels):
                # Classic 3 Hz spike-wave complex
                spike_amplitude = 200.0 + np.random.uniform(-20, 20)
                spike_wave = spike_amplitude * np.sin(2*np.pi*3.0*t)
                spike_wave += spike_amplitude * 0.3 * np.sin(2*np.pi*6.0*t)  # Harmonic
                spike_wave += spike_amplitude * 0.15 * np.sin(2*np.pi*9.0*t)  # Second harmonic
                
                # Make spikes sharper
                spike_wave = np.clip(spike_wave, -spike_amplitude*0.8, spike_amplitude)
                
                # Add slight background
                background = self._pink_noise(seizure_duration) * 10.0
                
                eeg[start_idx:end_idx, ch] = spike_wave + background
            
            # Label seizure samples
            for i in range(start_idx, end_idx):
                labels[i] = 'absence_seizure'
        
        # Fill non-seizure periods with normal EEG
        for i in range(n_samples):
            if labels[i] == 'normal':
                t = np.array([i / self.fs])
                for ch in range(self.n_channels):
                    eeg[i, ch] = (
                        30 * np.sin(2*np.pi*2*t + np.random.uniform(0, 2*np.pi)) +
                        25 * np.sin(2*np.pi*6*t + np.random.uniform(0, 2*np.pi)) +
                        40 * np.sin(2*np.pi*10*t + np.random.uniform(0, 2*np.pi)) +
                        15 * np.sin(2*np.pi*20*t + np.random.uniform(0, 2*np.pi)) +
                        np.random.randn() * 10
                    )[0]
        
        # Generate accelerometer data (head drops during absence)
        acc = self._generate_accelerometer(n_samples, seizure_events)
        
        return eeg, acc, labels
    
    def generate_tonic_clonic_seizure(self, duration_seconds: int = 60) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generate tonic-clonic seizure pattern (grand mal seizure)
        
        Phases:
        1. Tonic phase: High amplitude, high frequency (10-25 Hz)
        2. Clonic phase: Rhythmic spikes at 1-4 Hz with post-ictal slowing
        """
        n_samples = duration_seconds * self.fs
        eeg = np.zeros((n_samples, self.n_channels))
        labels = ['normal'] * n_samples
        
        # Single major seizure event
        pre_ictal_end = 10 * self.fs      # Normal until 10s
        tonic_start = 10 * self.fs
        tonic_end = 20 * self.fs          # Tonic phase: 10-20s
        clonic_start = 20 * self.fs
        clonic_end = 40 * self.fs         # Clonic phase: 20-40s  
        post_ictal_start = 40 * self.fs   # Post-ictal: 40-60s
        
        for ch in range(self.n_channels):
            # Pre-ictal (normal)
            t_pre = np.arange(pre_ictal_end) / self.fs
            eeg[:pre_ictal_end, ch] = self.generate_normal_baseline(pre_ictal_end)[:, ch]
            
            # Tonic phase - high amplitude, high frequency muscle artifact
            tonic_duration = tonic_end - tonic_start
            t_tonic = np.arange(tonic_duration) / self.fs
            tonic_signal = (
                250 * np.sin(2*np.pi*15*t_tonic) +  # Fast activity
                150 * np.sin(2*np.pi*22*t_tonic) +
                100 * np.random.randn(tonic_duration)  # Muscle noise
            )
            eeg[tonic_start:tonic_end, ch] = tonic_signal
            
            # Clonic phase - rhythmic jerks
            clonic_duration = clonic_end - clonic_start
            t_clonic = np.arange(clonic_duration) / self.fs
            
            # Decreasing frequency spikes (starts at ~4 Hz, slows to ~1 Hz)
            clonic_signal = np.zeros(clonic_duration)
            current_freq = 4.0
            for i, t in enumerate(t_clonic):
                # Gradually slow down
                freq = 4.0 - (3.0 * t / (clonic_duration / self.fs))
                freq = max(1.0, freq)
                
                # Generate spike with envelope
                spike_amp = 180 * (1.0 - 0.3 * t / (clonic_duration / self.fs))
                clonic_signal[i] = spike_amp * np.sin(2*np.pi*freq*t)
                
                # Add sharp spike components
                if np.sin(2*np.pi*freq*t) > 0.8:
                    clonic_signal[i] += np.random.uniform(50, 100)
            
            eeg[clonic_start:clonic_end, ch] = clonic_signal
            
            # Post-ictal suppression with slow recovery
            post_ictal_duration = n_samples - post_ictal_start
            t_post = np.arange(post_ictal_duration) / self.fs
            
            # Start suppressed, gradually recover
            recovery_envelope = 0.1 + 0.9 * (t_post / (post_ictal_duration / self.fs))
            post_signal = (
                50 * np.sin(2*np.pi*1*t_post) * recovery_envelope +  # Slow delta
                30 * np.sin(2*np.pi*3*t_post) * recovery_envelope +
                self._pink_noise(post_ictal_duration) * 15 * recovery_envelope
            )
            eeg[post_ictal_start:, ch] = post_signal
        
        # Labels
        for i in range(tonic_start, tonic_end):
            labels[i] = 'tonic_phase'
        for i in range(clonic_start, clonic_end):
            labels[i] = 'clonic_phase'
        for i in range(post_ictal_start, n_samples):
            labels[i] = 'post_ictal'
        
        # Accelerometer shows violent movement during clonic phase
        acc = self._generate_accelerometer_seizure(n_samples, clonic_start, clonic_end)
        
        return eeg, acc, labels
    
    def generate_focal_seizure(self, duration_seconds: int = 30) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generate focal seizure pattern (localized to specific channels)
        
        Shows abnormal activity primarily in one hemisphere or region.
        """
        n_samples = duration_seconds * self.fs
        eeg = np.zeros((n_samples, self.n_channels))
        labels = ['normal'] * n_samples
        
        # Affected channels (right hemisphere: F4, C4, P4, O2)
        affected_channels = [0, 1, 2, 3]
        
        # Seizure window
        seizure_start = int(8 * self.fs)
        seizure_end = int(22 * self.fs)
        
        for ch in range(self.n_channels):
            # Normal baseline for all
            eeg[:, ch] = self.generate_normal_baseline(n_samples)[:, ch]
            
            if ch in affected_channels:
                # Add focal seizure activity
                seizure_duration = seizure_end - seizure_start
                t = np.arange(seizure_duration) / self.fs
                
                # Rhythmic spike activity at ~8-12 Hz (beta range)
                focal_activity = (
                    120 * np.sin(2*np.pi*10*t) +
                    60 * np.sin(2*np.pi*20*t) +
                    40 * np.random.randn(seizure_duration)
                )
                
                # Apply smooth onset/offset envelope
                envelope = np.ones(seizure_duration)
                ramp_samples = int(0.5 * self.fs)  # 0.5 second ramp
                envelope[:ramp_samples] = np.linspace(0, 1, ramp_samples)
                envelope[-ramp_samples:] = np.linspace(1, 0, ramp_samples)
                
                eeg[seizure_start:seizure_end, ch] = focal_activity * envelope
        
        # Labels
        for i in range(seizure_start, seizure_end):
            labels[i] = 'focal_seizure'
        
        acc = self._generate_accelerometer(n_samples, [(8.0, 22.0)])
        
        return eeg, acc, labels
    
    def generate_myoclonic_jerks(self, duration_seconds: int = 30) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generate myoclonic jerk pattern (brief muscle jerks)
        
        Very short duration spikes (~50-100ms) occurring randomly.
        """
        n_samples = duration_seconds * self.fs
        eeg = self.generate_normal_baseline(n_samples)
        labels = ['normal'] * n_samples
        
        # Generate random jerk events
        n_jerks = np.random.randint(8, 15)
        jerk_times = sorted(np.random.uniform(2, duration_seconds - 1, n_jerks))
        
        for jerk_time in jerk_times:
            jerk_start = int(jerk_time * self.fs)
            jerk_duration = int(np.random.uniform(0.05, 0.15) * self.fs)  # 50-150ms
            jerk_end = min(jerk_start + jerk_duration, n_samples)
            
            # Generate sharp spike across all channels
            for ch in range(self.n_channels):
                spike_amp = np.random.uniform(200, 350)
                t_jerk = np.arange(jerk_end - jerk_start) / self.fs
                
                # Sharp spike with fast rise and slower decay
                spike = spike_amp * np.exp(-t_jerk * 20) * np.sin(2*np.pi*40*t_jerk)
                eeg[jerk_start:jerk_end, ch] += spike
            
            # Label
            for i in range(jerk_start, jerk_end):
                if i < n_samples:
                    labels[i] = 'myoclonic_jerk'
        
        acc = self._generate_accelerometer(n_samples, [(t, t + 0.1) for t in jerk_times])
        
        return eeg, acc, labels
    
    def generate_progressive_deterioration(self, duration_seconds: int = 60) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generate progressively worsening EEG pattern
        
        Starts normal, gradually increases abnormal activity.
        """
        n_samples = duration_seconds * self.fs
        eeg = np.zeros((n_samples, self.n_channels))
        labels = ['normal'] * n_samples
        
        for i in range(n_samples):
            t = i / self.fs
            progress = t / duration_seconds  # 0 to 1
            
            for ch in range(self.n_channels):
                # Normal component (decreasing)
                normal_weight = 1.0 - 0.8 * progress
                
                # Abnormal component (increasing)
                abnormal_weight = 0.8 * progress
                
                # Normal EEG
                normal = (
                    30 * np.sin(2*np.pi*2*t + ch) +
                    25 * np.sin(2*np.pi*6*t + ch*0.5) +
                    40 * np.sin(2*np.pi*10*t + ch*0.3) +
                    15 * np.sin(2*np.pi*20*t + ch*0.2) +
                    np.random.randn() * 10
                )
                
                # Abnormal pattern (spike-wave like)
                abnormal = (
                    150 * np.sin(2*np.pi*3*t) +
                    75 * np.sin(2*np.pi*6*t) +
                    np.random.randn() * 20
                )
                
                eeg[i, ch] = normal * normal_weight + abnormal * abnormal_weight
            
            # Update labels based on progress
            if progress < 0.3:
                labels[i] = 'normal'
            elif progress < 0.5:
                labels[i] = 'mild_abnormal'
            elif progress < 0.7:
                labels[i] = 'moderate_abnormal'
            else:
                labels[i] = 'severe_abnormal'
        
        acc = self._generate_accelerometer_progressive(n_samples, duration_seconds)
        
        return eeg, acc, labels
    
    def generate_burst_suppression(self, duration_seconds: int = 30) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generate burst-suppression pattern (seen in deep anesthesia, severe brain injury)
        
        Alternating periods of high-amplitude bursts and flat suppression.
        """
        n_samples = duration_seconds * self.fs
        eeg = np.zeros((n_samples, self.n_channels))
        labels = ['suppression'] * n_samples
        
        # Generate burst-suppression cycles
        i = 0
        while i < n_samples:
            # Suppression period (1-5 seconds)
            supp_duration = int(np.random.uniform(1, 5) * self.fs)
            supp_end = min(i + supp_duration, n_samples)
            
            for ch in range(self.n_channels):
                # Very low amplitude
                eeg[i:supp_end, ch] = np.random.randn(supp_end - i) * 5.0
            
            for j in range(i, supp_end):
                labels[j] = 'suppression'
            
            i = supp_end
            
            if i >= n_samples:
                break
            
            # Burst period (0.5-2 seconds)
            burst_duration = int(np.random.uniform(0.5, 2) * self.fs)
            burst_end = min(i + burst_duration, n_samples)
            
            t = np.arange(burst_end - i) / self.fs
            for ch in range(self.n_channels):
                # High amplitude polyspike activity
                burst = (
                    150 * np.sin(2*np.pi*8*t + np.random.uniform(0, 2*np.pi)) +
                    100 * np.sin(2*np.pi*15*t + np.random.uniform(0, 2*np.pi)) +
                    np.random.randn(len(t)) * 40
                )
                # Envelope
                envelope = np.sin(np.pi * np.arange(len(t)) / len(t))
                eeg[i:burst_end, ch] = burst * envelope
            
            for j in range(i, burst_end):
                labels[j] = 'burst'
            
            i = burst_end
        
        acc = self._generate_accelerometer(n_samples, [])
        
        return eeg, acc, labels
    
    def generate_status_epilepticus(self, duration_seconds: int = 60) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generate status epilepticus pattern (continuous seizure activity)
        
        Persistent, evolving seizure activity without return to baseline.
        """
        n_samples = duration_seconds * self.fs
        eeg = np.zeros((n_samples, self.n_channels))
        labels = ['status_epilepticus'] * n_samples
        
        for i in range(n_samples):
            t = i / self.fs
            
            # Evolving frequency (starts fast, gradually slows)
            base_freq = 8.0 - 5.0 * (t / duration_seconds)  # 8 Hz → 3 Hz
            base_freq = max(2.5, base_freq)
            
            # Evolving amplitude (starts high, fluctuates)
            amplitude_mod = 1.0 + 0.3 * np.sin(2*np.pi*0.05*t)
            
            for ch in range(self.n_channels):
                phase_offset = ch * 0.3
                
                seizure_signal = (
                    180 * amplitude_mod * np.sin(2*np.pi*base_freq*t + phase_offset) +
                    90 * np.sin(2*np.pi*base_freq*2*t + phase_offset) +  # Harmonic
                    np.random.randn() * 25
                )
                
                eeg[i, ch] = seizure_signal
        
        acc = self._generate_accelerometer(n_samples, [(0, duration_seconds)])
        
        return eeg, acc, labels
    
    def generate_mixed_abnormalities(self, duration_seconds: int = 60) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generate mixed pattern with various abnormality types
        
        Combines different seizure types in one recording.
        """
        n_samples = duration_seconds * self.fs
        eeg = np.zeros((n_samples, self.n_channels))
        labels = ['normal'] * n_samples
        
        # Schedule of events
        events = [
            ('normal', 0, 8),
            ('absence', 8, 15),
            ('normal', 15, 22),
            ('myoclonic', 22, 23),
            ('normal', 23, 30),
            ('focal', 30, 40),
            ('normal', 40, 45),
            ('spike_wave', 45, 52),
            ('normal', 52, 60),
        ]
        
        for event_type, start_sec, end_sec in events:
            if start_sec >= duration_seconds:
                continue
            end_sec = min(end_sec, duration_seconds)
            
            start_idx = int(start_sec * self.fs)
            end_idx = int(end_sec * self.fs)
            duration = end_idx - start_idx
            
            t = np.arange(duration) / self.fs
            
            for ch in range(self.n_channels):
                if event_type == 'normal':
                    signal = (
                        30 * np.sin(2*np.pi*2*t + ch) +
                        25 * np.sin(2*np.pi*6*t + ch*0.5) +
                        40 * np.sin(2*np.pi*10*t + ch*0.3) +
                        15 * np.sin(2*np.pi*20*t + ch*0.2) +
                        np.random.randn(duration) * 10
                    )
                elif event_type == 'absence':
                    signal = (
                        200 * np.sin(2*np.pi*3*t) +
                        60 * np.sin(2*np.pi*6*t) +
                        np.random.randn(duration) * 15
                    )
                elif event_type == 'myoclonic':
                    signal = np.random.randn(duration) * 10
                    # Add spike
                    spike_pos = duration // 2
                    spike_width = int(0.1 * self.fs)
                    spike_t = np.arange(spike_width) / self.fs
                    spike = 300 * np.exp(-spike_t * 20) * np.sin(2*np.pi*40*spike_t)
                    if spike_pos + spike_width <= duration:
                        signal[spike_pos:spike_pos+spike_width] += spike
                elif event_type == 'focal':
                    if ch in [0, 1, 2, 3]:  # Right hemisphere
                        signal = (
                            120 * np.sin(2*np.pi*10*t) +
                            60 * np.sin(2*np.pi*20*t) +
                            np.random.randn(duration) * 20
                        )
                    else:
                        signal = (
                            30 * np.sin(2*np.pi*10*t) +
                            np.random.randn(duration) * 10
                        )
                elif event_type == 'spike_wave':
                    signal = (
                        180 * np.sin(2*np.pi*3*t) +
                        90 * np.sin(2*np.pi*6*t) +
                        np.random.randn(duration) * 20
                    )
                else:
                    signal = np.random.randn(duration) * 10
                
                eeg[start_idx:end_idx, ch] = signal
            
            # Update labels
            label_map = {
                'normal': 'normal',
                'absence': 'absence_seizure',
                'myoclonic': 'myoclonic_jerk',
                'focal': 'focal_seizure',
                'spike_wave': 'spike_wave'
            }
            for i in range(start_idx, end_idx):
                labels[i] = label_map.get(event_type, event_type)
        
        acc = self._generate_accelerometer(n_samples, [(8, 15), (22, 23), (30, 40), (45, 52)])
        
        return eeg, acc, labels
    
    def _generate_accelerometer(self, n_samples: int, 
                                event_times: List[Tuple[float, float]]) -> np.ndarray:
        """Generate accelerometer data with movement during events"""
        acc = np.zeros((n_samples, 3))
        
        # Baseline (gravity + noise)
        acc[:, 0] = np.random.randn(n_samples) * 0.05  # X
        acc[:, 1] = np.random.randn(n_samples) * 0.05  # Y
        acc[:, 2] = 1.0 + np.random.randn(n_samples) * 0.05  # Z (gravity)
        
        # Add movement during events
        for start_sec, end_sec in event_times:
            start_idx = int(start_sec * self.fs)
            end_idx = int(end_sec * self.fs)
            
            if end_idx > n_samples:
                end_idx = n_samples
            
            duration = end_idx - start_idx
            if duration > 0:
                acc[start_idx:end_idx, 0] += np.random.randn(duration) * 0.3
                acc[start_idx:end_idx, 1] += np.random.randn(duration) * 0.3
                acc[start_idx:end_idx, 2] += np.random.randn(duration) * 0.2
        
        return acc
    
    def _generate_accelerometer_seizure(self, n_samples: int, 
                                        clonic_start: int, clonic_end: int) -> np.ndarray:
        """Generate accelerometer data for tonic-clonic seizure"""
        acc = np.zeros((n_samples, 3))
        
        # Baseline
        acc[:, 0] = np.random.randn(n_samples) * 0.05
        acc[:, 1] = np.random.randn(n_samples) * 0.05
        acc[:, 2] = 1.0 + np.random.randn(n_samples) * 0.05
        
        # Violent movement during clonic phase
        duration = clonic_end - clonic_start
        t = np.arange(duration) / self.fs
        
        # Rhythmic shaking
        acc[clonic_start:clonic_end, 0] += 2.0 * np.sin(2*np.pi*3*t) + np.random.randn(duration) * 0.5
        acc[clonic_start:clonic_end, 1] += 1.5 * np.sin(2*np.pi*3*t + 1) + np.random.randn(duration) * 0.5
        acc[clonic_start:clonic_end, 2] += 1.0 * np.cos(2*np.pi*3*t) + np.random.randn(duration) * 0.3
        
        return acc
    
    def _generate_accelerometer_progressive(self, n_samples: int, 
                                           duration_seconds: int) -> np.ndarray:
        """Generate accelerometer data with progressive movement increase"""
        acc = np.zeros((n_samples, 3))
        
        for i in range(n_samples):
            progress = i / n_samples
            noise_scale = 0.05 + 0.3 * progress
            
            acc[i, 0] = np.random.randn() * noise_scale
            acc[i, 1] = np.random.randn() * noise_scale
            acc[i, 2] = 1.0 + np.random.randn() * noise_scale * 0.5
        
        return acc
    
    def save_scenario(self, eeg: np.ndarray, acc: np.ndarray, labels: List[str],
                     output_path: str, scenario_name: str):
        """Save scenario to CSV file"""
        n_samples = len(labels)
        
        df = pd.DataFrame({
            'Time': np.arange(n_samples) / self.fs,
            'F4': eeg[:, 0],
            'C4': eeg[:, 1],
            'P4': eeg[:, 2],
            'O2': eeg[:, 3],
            'O1': eeg[:, 4],
            'F3': eeg[:, 5],
            'C3': eeg[:, 6],
            'P3': eeg[:, 7],
            'AccZ': acc[:, 2],
            'AccY': acc[:, 1],
            'AccX': acc[:, 0],
            'Obsense': [0 if l == 'normal' else 1 for l in labels],
            'AnomalyType': labels
        })
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Save with metadata
        with open(output_path, 'w') as f:
            f.write(f"# Abnormal EEG Scenario: {scenario_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Sampling Rate: {self.fs} Hz\n")
            f.write(f"# Duration: {n_samples / self.fs:.1f} seconds\n")
            f.write(f"# Channels: F4, C4, P4, O2, O1, F3, C3, P3\n")
            df.to_csv(f, index=False)
        
        # Print statistics
        label_counts = {}
        for l in labels:
            label_counts[l] = label_counts.get(l, 0) + 1
        
        print(f"\n✓ Saved {scenario_name} to {output_path}")
        print(f"  Duration: {n_samples / self.fs:.1f} seconds ({n_samples} samples)")
        print("  Label distribution:")
        for label, count in sorted(label_counts.items()):
            pct = count / n_samples * 100
            print(f"    {label:20s}: {count:6d} samples ({pct:5.1f}%)")


def generate_all_scenarios(output_dir: str, duration: int = 30):
    """Generate all abnormal scenarios"""
    generator = AbnormalEEGGenerator()
    
    scenarios = [
        (AbnormalScenario.ABSENCE_SEIZURE, generator.generate_absence_seizure, duration),
        (AbnormalScenario.TONIC_CLONIC, generator.generate_tonic_clonic_seizure, max(duration, 60)),
        (AbnormalScenario.FOCAL_SEIZURE, generator.generate_focal_seizure, duration),
        (AbnormalScenario.MYOCLONIC_JERK, generator.generate_myoclonic_jerks, duration),
        (AbnormalScenario.PROGRESSIVE_DETERIORATION, generator.generate_progressive_deterioration, max(duration, 60)),
        (AbnormalScenario.BURST_SUPPRESSION, generator.generate_burst_suppression, duration),
        (AbnormalScenario.STATUS_EPILEPTICUS, generator.generate_status_epilepticus, max(duration, 60)),
        (AbnormalScenario.MIXED_ABNORMALITIES, generator.generate_mixed_abnormalities, max(duration, 60)),
    ]
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("Generating All Abnormal EEG Scenarios")
    print("=" * 80)
    
    for scenario_enum, generate_func, dur in scenarios:
        eeg, acc, labels = generate_func(dur)
        output_path = os.path.join(output_dir, f"{scenario_enum.value}_scenario.csv")
        generator.save_scenario(eeg, acc, labels, output_path, scenario_enum.value)
    
    print("\n" + "=" * 80)
    print("All scenarios generated successfully!")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Generate abnormal EEG scenarios for testing predictions")
    parser.add_argument('--scenario', type=str, choices=[s.value for s in AbnormalScenario],
                       help='Specific scenario to generate')
    parser.add_argument('--all', action='store_true', help='Generate all scenarios')
    parser.add_argument('--duration', type=int, default=30, help='Duration in seconds')
    parser.add_argument('--output', type=str, default='test_data/', help='Output directory')
    
    args = parser.parse_args()
    
    if args.all:
        generate_all_scenarios(args.output, args.duration)
    elif args.scenario:
        generator = AbnormalEEGGenerator()
        
        scenario_map = {
            'absence_seizure': generator.generate_absence_seizure,
            'tonic_clonic': generator.generate_tonic_clonic_seizure,
            'focal_seizure': generator.generate_focal_seizure,
            'myoclonic_jerk': generator.generate_myoclonic_jerks,
            'progressive': generator.generate_progressive_deterioration,
            'burst_suppression': generator.generate_burst_suppression,
            'status_epilepticus': generator.generate_status_epilepticus,
            'mixed': generator.generate_mixed_abnormalities,
        }
        
        if args.scenario in scenario_map:
            eeg, acc, labels = scenario_map[args.scenario](args.duration)
            output_path = os.path.join(args.output, f"{args.scenario}_scenario.csv")
            generator.save_scenario(eeg, acc, labels, output_path, args.scenario)
        else:
            print(f"Unknown scenario: {args.scenario}")
    else:
        # Default: generate absence seizure scenario (most common trigger)
        print("No scenario specified. Generating default absence seizure scenario.")
        generator = AbnormalEEGGenerator()
        eeg, acc, labels = generator.generate_absence_seizure(30)
        output_path = os.path.join(args.output, "absence_seizure_scenario.csv")
        generator.save_scenario(eeg, acc, labels, output_path, "absence_seizure")
        
        print("\nTo generate other scenarios, use:")
        print("  python generate_abnormal_scenarios.py --scenario <name> --duration <seconds>")
        print("  python generate_abnormal_scenarios.py --all")
        print("\nAvailable scenarios:")
        for s in AbnormalScenario:
            print(f"  - {s.value}")


if __name__ == "__main__":
    main()
