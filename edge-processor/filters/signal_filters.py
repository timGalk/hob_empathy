"""
Signal filtering functions for EEG preprocessing
"""
import numpy as np
from scipy import signal

def bandpass_filter(data: np.ndarray, fs: float, lowcut: float, highcut: float, order: int = 4) -> np.ndarray:
    """
    Apply Butterworth band-pass filter

    Args:
        data: Input signal
        fs: Sampling frequency
        lowcut: Low cutoff frequency
        highcut: High cutoff frequency
        order: Filter order

    Returns:
        Filtered signal
    """
    nyquist = fs / 2.0
    low = lowcut / nyquist
    high = highcut / nyquist

    b, a = signal.butter(order, [low, high], btype='band')
    filtered_data = signal.filtfilt(b, a, data)

    return filtered_data

def notch_filter(data: np.ndarray, fs: float, freq: float, quality: float = 30.0) -> np.ndarray:
    """
    Apply notch filter to remove power line interference

    Args:
        data: Input signal
        fs: Sampling frequency
        freq: Frequency to remove (50 Hz or 60 Hz)
        quality: Quality factor

    Returns:
        Filtered signal
    """
    nyquist = fs / 2.0
    freq_normalized = freq / nyquist

    b, a = signal.iirnotch(freq_normalized, quality)
    filtered_data = signal.filtfilt(b, a, data)

    return filtered_data

def normalize_signal(data: np.ndarray) -> np.ndarray:
    """
    Normalize signal to zero mean and unit variance

    Args:
        data: Input signal

    Returns:
        Normalized signal
    """
    mean = np.mean(data)
    std = np.std(data)

    if std > 0:
        normalized = (data - mean) / std
    else:
        normalized = data - mean

    return normalized
