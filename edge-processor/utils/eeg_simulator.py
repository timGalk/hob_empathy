"""
EEG Signal Simulator with Abnormal Pattern Generation

Generates realistic EEG signals with various types of abnormalities:
- Spike-wave discharges (typical in absence seizures)
- High amplitude bursts
- Frequency anomalies
- Amplitude anomalies
- Baseline drift
- Motion artifacts
"""

import numpy as np
from typing import Tuple, Dict, List
from enum import Enum


class AbnormalityType(Enum):
    """Types of EEG abnormalities that can be simulated"""
    NONE = "none"
    SPIKE_WAVE = "spike_wave"  # 3 Hz spike-wave discharge (absence seizure)
    HIGH_AMPLITUDE = "high_amplitude"  # Sudden amplitude increase
    FREQUENCY_SHIFT = "frequency_shift"  # Abnormal frequency dominance
    BASELINE_DRIFT = "baseline_drift"  # Low frequency drift
    MOTION_ARTIFACT = "motion_artifact"  # High amplitude noise
    SUPPRESSION = "suppression"  # Amplitude suppression (flat EEG)


class EEGSimulator:
    """
    Generates realistic EEG signals with configurable abnormalities
    """

    def __init__(self, sampling_rate: int = 250, n_channels: int = 8):
        """
        Initialize EEG simulator

        Args:
            sampling_rate: Sampling frequency in Hz (default: 250)
            n_channels: Number of EEG channels (default: 8)
        """
        self.fs = sampling_rate
        self.n_channels = n_channels
        self.time_counter = 0

        # Normal EEG parameters (microvolts)
        self.delta_amplitude = 30.0  # 0.5-4 Hz (sleep)
        self.theta_amplitude = 25.0  # 4-8 Hz (drowsiness)
        self.alpha_amplitude = 40.0  # 8-12 Hz (relaxed, eyes closed)
        self.beta_amplitude = 15.0   # 12-30 Hz (active thinking)
        self.gamma_amplitude = 5.0   # 30-45 Hz (cognitive processing)

        # Abnormality parameters
        self.abnormality_active = False
        self.abnormality_start = 0
        self.abnormality_duration = 0
        self.current_abnormality = AbnormalityType.NONE

    def generate_normal_eeg(self, duration_samples: int,
                           channel_variation: bool = True) -> np.ndarray:
        """
        Generate normal baseline EEG signal

        Args:
            duration_samples: Number of samples to generate
            channel_variation: Add inter-channel variability

        Returns:
            EEG data of shape (duration_samples, n_channels)
        """
        t = np.arange(duration_samples) / self.fs
        eeg = np.zeros((duration_samples, self.n_channels))

        for ch in range(self.n_channels):
            # Channel-specific amplitude variation (frontal vs occipital)
            if channel_variation:
                # Occipital channels (O1, O2) have stronger alpha
                alpha_amp = self.alpha_amplitude * 1.5 if ch in [3, 4] else self.alpha_amplitude
                # Frontal channels (F3, F4) have more beta
                beta_amp = self.beta_amplitude * 1.3 if ch in [0, 5] else self.beta_amplitude
            else:
                alpha_amp = self.alpha_amplitude
                beta_amp = self.beta_amplitude

            # Random phase offsets for each channel
            phase_delta = np.random.uniform(0, 2*np.pi)
            phase_theta = np.random.uniform(0, 2*np.pi)
            phase_alpha = np.random.uniform(0, 2*np.pi)
            phase_beta = np.random.uniform(0, 2*np.pi)
            phase_gamma = np.random.uniform(0, 2*np.pi)

            # Generate frequency components
            delta = self.delta_amplitude * np.sin(2*np.pi*2*t + phase_delta)
            theta = self.theta_amplitude * np.sin(2*np.pi*6*t + phase_theta)
            alpha = alpha_amp * np.sin(2*np.pi*10*t + phase_alpha)
            beta = beta_amp * np.sin(2*np.pi*20*t + phase_beta)
            gamma = self.gamma_amplitude * np.sin(2*np.pi*35*t + phase_gamma)

            # Combine frequency bands
            signal = delta + theta + alpha + beta + gamma

            # Add pink noise (1/f noise characteristic of EEG)
            noise = self._generate_pink_noise(duration_samples) * 8.0

            eeg[:, ch] = signal + noise

        return eeg

    def _generate_pink_noise(self, n_samples: int) -> np.ndarray:
        """Generate pink (1/f) noise using the Voss-McCartney algorithm"""
        # Simple pink noise generation using spectral shaping
        # Generate white noise
        white = np.random.randn(n_samples)

        # Apply 1/f filter in frequency domain
        fft_white = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(n_samples)

        # Shape spectrum as 1/f (avoid division by zero)
        pink_spectrum = fft_white / (np.sqrt(freqs + 1e-10))

        # Convert back to time domain
        pink = np.fft.irfft(pink_spectrum, n=n_samples)

        # Normalize
        return pink / (np.std(pink) + 1e-10)

    def generate_spike_wave_discharge(self, duration_samples: int) -> np.ndarray:
        """
        Generate 3 Hz spike-wave discharge pattern (typical absence seizure)

        Args:
            duration_samples: Number of samples to generate

        Returns:
            EEG data with spike-wave pattern
        """
        t = np.arange(duration_samples) / self.fs
        eeg = np.zeros((duration_samples, self.n_channels))

        # 3 Hz spike-wave complex
        spike_freq = 3.0
        spike_amplitude = 200.0  # High amplitude spikes

        for ch in range(self.n_channels):
            # Spike component (sharp wave)
            spike = spike_amplitude * np.sin(2*np.pi*spike_freq*t)

            # Add harmonics for sharper spikes
            spike += (spike_amplitude * 0.3) * np.sin(2*np.pi*spike_freq*2*t)
            spike += (spike_amplitude * 0.1) * np.sin(2*np.pi*spike_freq*3*t)

            # Make it more spike-like with clipping
            spike = np.clip(spike, -spike_amplitude*0.8, spike_amplitude)

            # Add some background activity
            background = self.generate_normal_eeg(duration_samples, False)[:, ch] * 0.3

            eeg[:, ch] = spike + background

        return eeg

    def generate_high_amplitude_burst(self, duration_samples: int) -> np.ndarray:
        """
        Generate high amplitude burst (sudden amplitude increase)

        Args:
            duration_samples: Number of samples to generate

        Returns:
            EEG data with high amplitude burst
        """
        # Start with normal EEG
        eeg = self.generate_normal_eeg(duration_samples, True)

        # Multiply by burst envelope
        t = np.arange(duration_samples) / self.fs
        burst_envelope = 1.0 + 4.0 * np.exp(-((t - t.max()/2)**2) / (0.2**2))

        # Add random high-frequency component
        for ch in range(self.n_channels):
            high_freq = 80.0 * np.sin(2*np.pi*15*t) * burst_envelope
            eeg[:, ch] = eeg[:, ch] * burst_envelope + high_freq

        return eeg

    def generate_frequency_shift(self, duration_samples: int,
                                dominant_freq: float = 25.0) -> np.ndarray:
        """
        Generate EEG with abnormal frequency dominance

        Args:
            duration_samples: Number of samples to generate
            dominant_freq: Dominant frequency in Hz

        Returns:
            EEG data with frequency anomaly
        """
        t = np.arange(duration_samples) / self.fs
        eeg = np.zeros((duration_samples, self.n_channels))

        for ch in range(self.n_channels):
            # Abnormally strong single frequency
            dominant = 120.0 * np.sin(2*np.pi*dominant_freq*t + np.random.uniform(0, 2*np.pi))

            # Weak background
            background = self.generate_normal_eeg(duration_samples, False)[:, ch] * 0.2

            eeg[:, ch] = dominant + background

        return eeg

    def generate_baseline_drift(self, duration_samples: int) -> np.ndarray:
        """
        Generate EEG with baseline drift (low-frequency artifact)

        Args:
            duration_samples: Number of samples to generate

        Returns:
            EEG data with baseline drift
        """
        t = np.arange(duration_samples) / self.fs
        eeg = self.generate_normal_eeg(duration_samples, True)

        # Add slow drift
        drift_freq = 0.5  # Hz
        drift_amplitude = 80.0
        drift = drift_amplitude * np.sin(2*np.pi*drift_freq*t)

        eeg += drift[:, np.newaxis]

        return eeg

    def generate_motion_artifact(self, duration_samples: int) -> np.ndarray:
        """
        Generate motion artifact (high amplitude random noise)

        Args:
            duration_samples: Number of samples to generate

        Returns:
            EEG data with motion artifact
        """
        eeg = self.generate_normal_eeg(duration_samples, True)

        # Add large random spikes
        n_spikes = np.random.randint(5, 15)
        for _ in range(n_spikes):
            spike_pos = np.random.randint(0, duration_samples)
            spike_width = np.random.randint(10, 50)
            spike_amplitude = np.random.uniform(150, 300)

            start = max(0, spike_pos - spike_width//2)
            end = min(duration_samples, spike_pos + spike_width//2)

            for ch in range(self.n_channels):
                eeg[start:end, ch] += spike_amplitude * np.random.randn(end-start)

        return eeg

    def generate_suppression(self, duration_samples: int) -> np.ndarray:
        """
        Generate amplitude suppression (very low amplitude, flat EEG)

        Args:
            duration_samples: Number of samples to generate

        Returns:
            Suppressed EEG data
        """
        eeg = self.generate_normal_eeg(duration_samples, True)

        # Suppress amplitude
        eeg *= 0.1

        # Add minimal noise
        eeg += np.random.randn(duration_samples, self.n_channels) * 2.0

        return eeg

    def generate_sample(self, n_samples: int = 1,
                       abnormality_prob: float = 0.2,
                       abnormality_type: AbnormalityType = None) -> Tuple[np.ndarray, List[str]]:
        """
        Generate EEG samples with optional abnormalities

        Args:
            n_samples: Number of samples (each sample = 1 timepoint across all channels)
            abnormality_prob: Probability of introducing abnormality
            abnormality_type: Specific abnormality to inject (None = random)

        Returns:
            (eeg_data, labels) tuple where:
                - eeg_data: shape (n_samples, n_channels)
                - labels: list of abnormality labels for each sample
        """
        eeg_data = np.zeros((n_samples, self.n_channels))
        labels = []

        # Check if we should start a new abnormality
        if not self.abnormality_active:
            if np.random.random() < abnormality_prob / 250:  # Adjust for sampling rate
                self.abnormality_active = True
                self.abnormality_start = 0
                self.abnormality_duration = np.random.randint(250, 1000)  # 1-4 seconds

                if abnormality_type is None:
                    # Random abnormality type
                    abnormality_types = [
                        AbnormalityType.SPIKE_WAVE,
                        AbnormalityType.HIGH_AMPLITUDE,
                        AbnormalityType.FREQUENCY_SHIFT,
                        AbnormalityType.MOTION_ARTIFACT,
                        AbnormalityType.SUPPRESSION
                    ]
                    self.current_abnormality = np.random.choice(abnormality_types)
                else:
                    self.current_abnormality = abnormality_type

        # Generate data based on current state
        if self.abnormality_active:
            # Generate abnormal pattern
            if self.current_abnormality == AbnormalityType.SPIKE_WAVE:
                chunk = self.generate_spike_wave_discharge(n_samples)
            elif self.current_abnormality == AbnormalityType.HIGH_AMPLITUDE:
                chunk = self.generate_high_amplitude_burst(n_samples)
            elif self.current_abnormality == AbnormalityType.FREQUENCY_SHIFT:
                chunk = self.generate_frequency_shift(n_samples)
            elif self.current_abnormality == AbnormalityType.BASELINE_DRIFT:
                chunk = self.generate_baseline_drift(n_samples)
            elif self.current_abnormality == AbnormalityType.MOTION_ARTIFACT:
                chunk = self.generate_motion_artifact(n_samples)
            elif self.current_abnormality == AbnormalityType.SUPPRESSION:
                chunk = self.generate_suppression(n_samples)
            else:
                chunk = self.generate_normal_eeg(n_samples)

            eeg_data = chunk
            labels = [self.current_abnormality.value] * n_samples

            # Check if abnormality should end
            self.abnormality_start += n_samples
            if self.abnormality_start >= self.abnormality_duration:
                self.abnormality_active = False
                self.current_abnormality = AbnormalityType.NONE
        else:
            # Generate normal EEG
            eeg_data = self.generate_normal_eeg(n_samples)
            labels = [AbnormalityType.NONE.value] * n_samples

        self.time_counter += n_samples

        return eeg_data, labels

    def generate_accelerometer_data(self, n_samples: int,
                                   with_movement: bool = False) -> np.ndarray:
        """
        Generate simulated accelerometer data

        Args:
            n_samples: Number of samples to generate
            with_movement: Whether to include movement artifacts

        Returns:
            Accelerometer data of shape (n_samples, 3) for X, Y, Z axes
        """
        # Baseline (gravity + small variations)
        acc_data = np.zeros((n_samples, 3))
        acc_data[:, 0] = 0.0 + np.random.randn(n_samples) * 0.05  # X
        acc_data[:, 1] = 0.0 + np.random.randn(n_samples) * 0.05  # Y
        acc_data[:, 2] = 1.0 + np.random.randn(n_samples) * 0.05  # Z (gravity)

        if with_movement:
            # Add movement artifacts
            t = np.arange(n_samples) / self.fs
            movement_freq = 2.0  # Hz (head nodding frequency)
            movement_amp = 0.3

            acc_data[:, 0] += movement_amp * np.sin(2*np.pi*movement_freq*t)
            acc_data[:, 1] += movement_amp * np.sin(2*np.pi*movement_freq*1.5*t)
            acc_data[:, 2] += movement_amp * np.cos(2*np.pi*movement_freq*t)

        return acc_data


if __name__ == "__main__":
    # Demo: Generate and visualize different abnormality types
    import matplotlib.pyplot as plt

    simulator = EEGSimulator(sampling_rate=250, n_channels=8)

    # Generate 4 seconds of different patterns
    duration = 1000  # samples (4 seconds at 250 Hz)

    fig, axes = plt.subplots(6, 1, figsize=(12, 12))

    patterns = [
        ("Normal EEG", simulator.generate_normal_eeg(duration)),
        ("Spike-Wave Discharge", simulator.generate_spike_wave_discharge(duration)),
        ("High Amplitude Burst", simulator.generate_high_amplitude_burst(duration)),
        ("Frequency Shift", simulator.generate_frequency_shift(duration)),
        ("Motion Artifact", simulator.generate_motion_artifact(duration)),
        ("Suppression", simulator.generate_suppression(duration))
    ]

    for idx, (title, data) in enumerate(patterns):
        # Plot first channel only for clarity
        t = np.arange(duration) / 250
        axes[idx].plot(t, data[:, 0], linewidth=0.5)
        axes[idx].set_title(title)
        axes[idx].set_ylabel("Amplitude (μV)")
        if idx == len(patterns) - 1:
            axes[idx].set_xlabel("Time (s)")
        axes[idx].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("eeg_patterns.png", dpi=150)
    print("Saved visualization to eeg_patterns.png")
