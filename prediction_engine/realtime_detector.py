
"""
Real-Time EEG Anomaly Detector

Provides immediate detection of abnormal EEG patterns using:
- Statistical thresholds
- Spectral analysis
- Pattern recognition
- Multi-criteria decision making

Works alongside ML models for comprehensive abnormality detection.
"""

import numpy as np
from scipy.signal import welch
from scipy.stats import entropy
from typing import Dict, List, Tuple
from collections import deque
from dataclasses import dataclass
from enum import Enum


class AnomalyLevel(Enum):
    """Severity levels for detected anomalies"""
    NORMAL = 0
    MILD = 1
    MODERATE = 2
    SEVERE = 3


@dataclass
class AnomalyReport:
    """Report of detected anomaly"""
    level: AnomalyLevel
    confidence: float  # 0.0-1.0
    anomaly_types: List[str]
    metrics: Dict[str, float]
    timestamp: float
    details: str


class RealtimeAnomalyDetector:
    """
    Detects EEG abnormalities in real-time using multiple criteria
    """

    def __init__(self, sampling_rate: int = 250, window_size: int = 256):
        """
        Initialize real-time anomaly detector

        Args:
            sampling_rate: Sampling frequency in Hz
            window_size: Number of samples per detection window
        """
        self.fs = sampling_rate
        self.window_size = window_size

        # Baseline statistics (learned from initial normal data)
        self.baseline_mean = None
        self.baseline_std = None
        self.baseline_alpha_power = None
        self.baseline_beta_power = None

        # Rolling window for baseline estimation
        self.baseline_buffer = deque(maxlen=10)  # Store 10 windows for baseline
        self.calibrated = False

        # Detection thresholds (conservative defaults)
        self.amplitude_threshold_multiplier = 4.0  # std deviations
        self.spike_threshold = 150.0  # microvolts
        self.suppression_threshold = 5.0  # microvolts (RMS)
        self.frequency_shift_threshold = 2.5  # ratio

        # Spike-wave detection parameters
        self.spike_wave_freq_range = (2.5, 3.5)  # Hz (typical absence seizure)
        self.spike_wave_power_threshold = 0.4  # Relative power

    def calibrate(self, normal_eeg_windows: List[np.ndarray]):
        """
        Calibrate detector using known normal EEG data

        Args:
            normal_eeg_windows: List of normal EEG windows for baseline estimation
        """
        if not normal_eeg_windows:
            return

        all_data = np.concatenate(normal_eeg_windows, axis=0)

        # Compute baseline statistics
        self.baseline_mean = np.mean(all_data, axis=0)
        self.baseline_std = np.std(all_data, axis=0)

        # Compute baseline spectral features
        alpha_powers = []
        beta_powers = []

        for window in normal_eeg_windows:
            for ch in range(window.shape[1]):
                bands = self._compute_band_powers(window[:, ch])
                alpha_powers.append(bands['alpha'])
                beta_powers.append(bands['beta'])

        self.baseline_alpha_power = np.mean(alpha_powers)
        self.baseline_beta_power = np.mean(beta_powers)

        self.calibrated = True
        print(f"✓ Anomaly detector calibrated with {len(normal_eeg_windows)} normal windows")

    def detect(self, eeg_window: np.ndarray, timestamp: float = None) -> AnomalyReport:
        """
        Detect anomalies in an EEG window

        Args:
            eeg_window: EEG data of shape (samples, channels)
            timestamp: Optional timestamp of the window

        Returns:
            AnomalyReport with detection results
        """
        if timestamp is None:
            timestamp = 0.0

        anomaly_types = []
        metrics = {}
        max_confidence = 0.0

        # Update baseline if not calibrated
        if not self.calibrated:
            self.baseline_buffer.append(eeg_window)
            if len(self.baseline_buffer) >= 5:
                self.calibrate(list(self.baseline_buffer))

        # 1. Amplitude-based detection
        amplitude_anomaly, amplitude_conf, amplitude_metrics = self._detect_amplitude_anomaly(eeg_window)
        if amplitude_anomaly:
            anomaly_types.append(amplitude_anomaly)
            max_confidence = max(max_confidence, amplitude_conf)
        metrics.update(amplitude_metrics)

        # 2. Spike detection
        spike_detected, spike_conf, spike_metrics = self._detect_spikes(eeg_window)
        if spike_detected:
            anomaly_types.append("spike")
            max_confidence = max(max_confidence, spike_conf)
        metrics.update(spike_metrics)

        # 3. Spike-wave discharge detection (absence seizure)
        spike_wave, sw_conf, sw_metrics = self._detect_spike_wave(eeg_window)
        if spike_wave:
            anomaly_types.append("spike_wave_discharge")
            max_confidence = max(max_confidence, sw_conf)
        metrics.update(sw_metrics)

        # 4. Frequency anomaly detection
        freq_anomaly, freq_conf, freq_metrics = self._detect_frequency_anomaly(eeg_window)
        if freq_anomaly:
            anomaly_types.append(freq_anomaly)
            max_confidence = max(max_confidence, freq_conf)
        metrics.update(freq_metrics)

        # 5. Suppression detection
        suppression, supp_conf, supp_metrics = self._detect_suppression(eeg_window)
        if suppression:
            anomaly_types.append("suppression")
            max_confidence = max(max_confidence, supp_conf)
        metrics.update(supp_metrics)

        # Determine overall anomaly level
        level = self._determine_level(anomaly_types, max_confidence)

        # Generate details string
        if anomaly_types:
            details = f"Detected: {', '.join(anomaly_types)}"
        else:
            details = "Normal EEG activity"

        return AnomalyReport(
            level=level,
            confidence=max_confidence,
            anomaly_types=anomaly_types,
            metrics=metrics,
            timestamp=timestamp,
            details=details
        )

    def _detect_amplitude_anomaly(self, eeg_window: np.ndarray) -> Tuple[str, float, Dict]:
        """Detect amplitude-based anomalies"""
        metrics = {}

        # Compute RMS amplitude for each channel
        rms = np.sqrt(np.mean(eeg_window**2, axis=0))
        max_rms = np.max(rms)
        mean_rms = np.mean(rms)

        metrics['rms_max'] = float(max_rms)
        metrics['rms_mean'] = float(mean_rms)

        # High amplitude detection
        if self.calibrated and self.baseline_std is not None:
            threshold = self.baseline_std.mean() * self.amplitude_threshold_multiplier
            if max_rms > threshold:
                confidence = min(1.0, (max_rms - threshold) / threshold)
                return "high_amplitude", confidence, metrics

        # Absolute threshold (if not calibrated)
        if max_rms > 200.0:
            confidence = min(1.0, max_rms / 300.0)
            return "high_amplitude", confidence, metrics

        return None, 0.0, metrics

    def _detect_spikes(self, eeg_window: np.ndarray) -> Tuple[bool, float, Dict]:
        """Detect sharp spikes in the signal"""
        metrics = {}

        # Compute derivative (rate of change)
        derivatives = np.diff(eeg_window, axis=0)
        max_derivative = np.max(np.abs(derivatives))

        metrics['max_derivative'] = float(max_derivative)

        # Spike detection based on sharp transitions
        spike_threshold = 50.0  # microvolts per sample
        if max_derivative > spike_threshold:
            confidence = min(1.0, max_derivative / (spike_threshold * 3))
            return True, confidence, metrics

        return False, 0.0, metrics

    def _detect_spike_wave(self, eeg_window: np.ndarray) -> Tuple[bool, float, Dict]:
        """Detect 3 Hz spike-wave discharge (absence seizure pattern)"""
        metrics = {}

        # Average across channels
        mean_signal = np.mean(eeg_window, axis=1)

        # Compute power spectral density
        bands = self._compute_band_powers(mean_signal)

        # Check for dominant 3 Hz activity
        freqs, psd = welch(mean_signal, fs=self.fs, nperseg=min(256, len(mean_signal)))

        # Power in spike-wave range (2.5-3.5 Hz)
        sw_mask = (freqs >= self.spike_wave_freq_range[0]) & (freqs <= self.spike_wave_freq_range[1])
        sw_power = np.trapz(psd[sw_mask], freqs[sw_mask])
        total_power = np.trapz(psd, freqs)

        sw_relative_power = sw_power / total_power if total_power > 0 else 0.0

        metrics['spike_wave_power'] = float(sw_power)
        metrics['spike_wave_relative_power'] = float(sw_relative_power)

        # Detect if 3 Hz power is abnormally high
        if sw_relative_power > self.spike_wave_power_threshold:
            # Additional check: high amplitude
            if np.max(np.abs(mean_signal)) > 100.0:
                confidence = min(1.0, sw_relative_power / 0.5)
                return True, confidence, metrics

        return False, 0.0, metrics

    def _detect_frequency_anomaly(self, eeg_window: np.ndarray) -> Tuple[str, float, Dict]:
        """Detect abnormal frequency distribution"""
        metrics = {}

        # Average across channels
        mean_signal = np.mean(eeg_window, axis=1)
        bands = self._compute_band_powers(mean_signal)

        metrics.update({f'{k}_power': float(v) for k, v in bands.items()})

        if not self.calibrated:
            return None, 0.0, metrics

        # Check for abnormal beta dominance
        if self.baseline_beta_power is not None:
            beta_ratio = bands['beta'] / self.baseline_beta_power if self.baseline_beta_power > 0 else 0.0
            metrics['beta_ratio'] = float(beta_ratio)

            if beta_ratio > self.frequency_shift_threshold:
                confidence = min(1.0, (beta_ratio - self.frequency_shift_threshold) / self.frequency_shift_threshold)
                return "frequency_shift_beta", confidence, metrics

        # Check for abnormal delta dominance (suppression/slow waves)
        delta_relative = bands['delta'] / (bands['alpha'] + bands['beta'] + 1e-6)
        metrics['delta_dominance'] = float(delta_relative)

        if delta_relative > 3.0:
            confidence = min(1.0, delta_relative / 5.0)
            return "frequency_shift_delta", confidence, metrics

        return None, 0.0, metrics

    def _detect_suppression(self, eeg_window: np.ndarray) -> Tuple[bool, float, Dict]:
        """Detect amplitude suppression (flat EEG)"""
        metrics = {}

        # Compute RMS amplitude
        rms = np.sqrt(np.mean(eeg_window**2, axis=0))
        mean_rms = np.mean(rms)

        metrics['suppression_rms'] = float(mean_rms)

        # Very low amplitude indicates suppression
        if mean_rms < self.suppression_threshold:
            confidence = min(1.0, (self.suppression_threshold - mean_rms) / self.suppression_threshold)
            return True, confidence, metrics

        return False, 0.0, metrics

    def _compute_band_powers(self, signal: np.ndarray) -> Dict[str, float]:
        """Compute power in each frequency band"""
        bands = {
            "delta": (0.5, 4),
            "theta": (4, 8),
            "alpha": (8, 12),
            "beta": (12, 30),
            "gamma": (30, 45),
        }

        freqs, psd = welch(signal, fs=self.fs, nperseg=min(256, len(signal)))

        band_powers = {}
        for band_name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs <= high)
            power = np.trapz(psd[mask], freqs[mask])
            band_powers[band_name] = power

        return band_powers

    def _determine_level(self, anomaly_types: List[str], confidence: float) -> AnomalyLevel:
        """Determine overall anomaly severity level"""
        if not anomaly_types:
            return AnomalyLevel.NORMAL

        # Severe anomalies
        severe_types = ["spike_wave_discharge", "spike"]
        if any(t in severe_types for t in anomaly_types):
            return AnomalyLevel.SEVERE

        # Moderate anomalies
        if confidence > 0.7:
            return AnomalyLevel.MODERATE

        # Mild anomalies
        if confidence > 0.4:
            return AnomalyLevel.MILD

        return AnomalyLevel.NORMAL


class StreamingAnomalyDetector:
    """
    Wrapper for continuous stream processing with sliding windows
    """

    def __init__(self, sampling_rate: int = 250, window_size: int = 256, overlap: float = 0.5):
        """
        Initialize streaming detector

        Args:
            sampling_rate: Sampling frequency in Hz
            window_size: Window size in samples
            overlap: Window overlap fraction (0.0-1.0)
        """
        self.detector = RealtimeAnomalyDetector(sampling_rate, window_size)
        self.window_size = window_size
        self.hop_size = int(window_size * (1 - overlap))
        self.buffer = deque(maxlen=window_size)
        self.sample_count = 0

        # Anomaly tracking
        self.recent_anomalies = deque(maxlen=20)
        self.current_anomaly_active = False

    def add_sample(self, sample: np.ndarray, timestamp: float = None) -> AnomalyReport:
        """
        Add a single sample and detect anomalies when window is full

        Args:
            sample: EEG sample of shape (n_channels,)
            timestamp: Optional timestamp

        Returns:
            AnomalyReport if detection performed, None otherwise
        """
        self.buffer.append(sample)
        self.sample_count += 1

        if timestamp is None:
            timestamp = self.sample_count / self.detector.fs

        # Detect when we have a full window and it's time to process
        if len(self.buffer) >= self.window_size and self.sample_count % self.hop_size == 0:
            window = np.array(list(self.buffer))
            report = self.detector.detect(window, timestamp)

            # Track anomalies
            self.recent_anomalies.append(report)

            # Print alerts for new severe/moderate anomalies
            if report.level in [AnomalyLevel.SEVERE, AnomalyLevel.MODERATE]:
                if not self.current_anomaly_active:
                    print(f"\n🚨 ANOMALY ALERT ({report.level.name}): {report.details}")
                    print(f"   Confidence: {report.confidence:.2%}")
                    print(f"   Timestamp: {timestamp:.2f}s")
                    self.current_anomaly_active = True
            else:
                if self.current_anomaly_active:
                    print(f"✓ Anomaly resolved at {timestamp:.2f}s\n")
                self.current_anomaly_active = False

            return report

        return None

    def get_recent_statistics(self) -> Dict:
        """Get statistics about recent detections"""
        if not self.recent_anomalies:
            return {"total": 0, "normal": 0, "anomalous": 0}

        total = len(self.recent_anomalies)
        anomalous = sum(1 for r in self.recent_anomalies if r.level != AnomalyLevel.NORMAL)

        return {
            "total": total,
            "normal": total - anomalous,
            "anomalous": anomalous,
            "anomaly_rate": anomalous / total if total > 0 else 0.0
        }


if __name__ == "__main__":
    # Demo: Test detector with synthetic data
    import sys
    sys.path.append('..')

    from utils.eeg_simulator import EEGSimulator, AbnormalityType

    print("Real-Time Anomaly Detector Demo")
    print("=" * 80)

    # Create simulator and detector
    simulator = EEGSimulator(sampling_rate=250, n_channels=8)
    streaming_detector = StreamingAnomalyDetector(sampling_rate=250, window_size=256)

    # Generate and process data
    n_samples = 5000  # 20 seconds at 250 Hz

    print("Processing simulated EEG stream...")
    print("Generating normal baseline for calibration...")

    # First, calibrate with normal data
    normal_windows = []
    for _ in range(5):
        window, _ = simulator.generate_sample(n_samples=256, abnormality_prob=0.0)
        normal_windows.append(window)
    streaming_detector.detector.calibrate(normal_windows)

    print("Calibration complete. Now processing stream with abnormalities...\n")

    # Now process stream with abnormalities
    for i in range(n_samples):
        # Generate sample with 30% abnormality probability
        sample, label = simulator.generate_sample(n_samples=1, abnormality_prob=0.3)
        timestamp = i / 250

        # Add to detector
        report = streaming_detector.add_sample(sample[0], timestamp)

    # Print summary
    print("\n" + "=" * 80)
    print("Detection Summary:")
    stats = streaming_detector.get_recent_statistics()
    print(f"Total windows analyzed: {stats['total']}")
    print(f"Normal windows: {stats['normal']}")
    print(f"Anomalous windows: {stats['anomalous']}")
    print(f"Anomaly rate: {stats['anomaly_rate']:.1%}")
