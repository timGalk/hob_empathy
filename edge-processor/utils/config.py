"""
Configuration for edge processor
"""
import os

class Config:
    # EEG acquisition settings
    SAMPLING_RATE = int(os.getenv("SAMPLING_RATE", "250"))  # Hz
    NUM_CHANNELS = int(os.getenv("NUM_CHANNELS", "8"))
    WINDOW_SIZE = float(os.getenv("WINDOW_SIZE", "2.0"))  # seconds

    # Filter settings
    BANDPASS_LOW = float(os.getenv("BANDPASS_LOW", "1.0"))  # Hz
    BANDPASS_HIGH = float(os.getenv("BANDPASS_HIGH", "40.0"))  # Hz
    NOTCH_FREQ = float(os.getenv("NOTCH_FREQ", "50.0"))  # Hz (50 EU / 60 US)

    # Backend settings
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    PATIENT_ID = os.getenv("PATIENT_ID", "patient_001")

    # Offline mode
    ENABLE_OFFLINE_QUEUE = os.getenv("ENABLE_OFFLINE_QUEUE", "true").lower() == "true"
    MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "1000"))
