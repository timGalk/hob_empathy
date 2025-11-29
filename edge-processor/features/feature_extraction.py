"""
Feature extraction from EEG signals
"""
import numpy as np
from scipy import signal
from scipy.stats import entropy

def extract_features(data: np.ndarray, fs: float) -> dict:
    """
    Extract features from windowed EEG data

    Args:
        data: EEG data array of shape (samples, channels)
        fs: Sampling frequency

    Returns:
        Dictionary of extracted features
    """
    features = {}

    # Average across all channels
    avg_signal = np.mean(data, axis=1)

    # Compute power spectral density
    freqs, psd = signal.welch(avg_signal, fs=fs, nperseg=min(256, len(avg_signal)))

    # Extract bandpower for different frequency bands
    features['delta_power'] = bandpower(psd, freqs, 1, 4)
    features['theta_power'] = bandpower(psd, freqs, 4, 8)
    features['alpha_power'] = bandpower(psd, freqs, 8, 13)
    features['beta_power'] = bandpower(psd, freqs, 13, 30)

    # Spectral entropy
    features['entropy'] = spectral_entropy(psd)

    # Hjorth parameters
    mobility, complexity = hjorth_parameters(avg_signal)
    features['mobility'] = float(mobility)
    features['complexity'] = float(complexity)

    # Signal variance
    features['variance'] = float(np.var(avg_signal))

    return features

def bandpower(psd: np.ndarray, freqs: np.ndarray, low: float, high: float) -> float:
    """
    Compute average power in a frequency band

    Args:
        psd: Power spectral density
        freqs: Frequency bins
        low: Lower frequency bound
        high: Upper frequency bound

    Returns:
        Average power in the band
    """
    idx = np.logical_and(freqs >= low, freqs <= high)
    power = np.trapz(psd[idx], freqs[idx])
    return float(power)

def spectral_entropy(psd: np.ndarray) -> float:
    """
    Compute spectral entropy

    Args:
        psd: Power spectral density

    Returns:
        Spectral entropy value
    """
    # Normalize PSD
    psd_norm = psd / np.sum(psd)

    # Compute entropy
    se = entropy(psd_norm)

    return float(se)

def hjorth_parameters(signal_data: np.ndarray) -> tuple:
    """
    Compute Hjorth mobility and complexity

    Args:
        signal_data: Input signal

    Returns:
        (mobility, complexity) tuple
    """
    # First derivative
    first_deriv = np.diff(signal_data)

    # Second derivative
    second_deriv = np.diff(first_deriv)

    # Variance
    var_signal = np.var(signal_data)
    var_first = np.var(first_deriv)
    var_second = np.var(second_deriv)

    # Mobility
    mobility = np.sqrt(var_first / var_signal) if var_signal > 0 else 0

    # Complexity
    complexity = (np.sqrt(var_second / var_first) / mobility) if (var_first > 0 and mobility > 0) else 0

    return mobility, complexity
