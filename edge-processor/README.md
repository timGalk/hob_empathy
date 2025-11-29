# Edge Processor

Edge device preprocessing layer for EEG signal acquisition and feature extraction.

## Features

- Real-time signal filtering
- Bandpower extraction (Delta, Theta, Alpha, Beta)
- Spectral entropy calculation
- Hjorth parameters
- Automatic backend synchronization

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Configuration

Edit `utils/config.py` or use environment variables:

- `SAMPLING_RATE` - EEG sampling rate (default: 250 Hz)
- `NUM_CHANNELS` - Number of EEG channels (default: 8)
- `WINDOW_SIZE` - Processing window size in seconds (default: 2.0)
- `BACKEND_URL` - Backend API URL
- `PATIENT_ID` - Patient identifier

## Hardware Requirements

- Raspberry Pi 4 or Android/iOS device
- 8-channel EEG headset with BLE/WiFi connectivity
- Minimum 2GB RAM
