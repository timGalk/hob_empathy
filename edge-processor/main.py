"""
Edge Preprocessing Layer
Runs on mobile device or Raspberry Pi to process EEG signals
"""
import numpy as np
import time
import asyncio
import aiohttp
from filters.signal_filters import bandpass_filter, notch_filter
from features.feature_extraction import extract_features
from utils.config import Config

class EEGProcessor:
    def __init__(self, patient_id: str, backend_url: str):
        self.patient_id = patient_id
        self.backend_url = backend_url
        self.sampling_rate = 250  # Hz
        self.window_size = 2  # seconds
        self.samples_per_window = self.sampling_rate * self.window_size

    async def process_stream(self, eeg_data_generator):
        """
        Process continuous EEG stream

        Args:
            eeg_data_generator: Async generator yielding (timestamp, channels) tuples
        """
        buffer = []

        async for timestamp, channels in eeg_data_generator:
            # Add to buffer
            buffer.append(channels)

            # Process when we have a full window
            if len(buffer) >= self.samples_per_window:
                window_data = np.array(buffer[:self.samples_per_window])
                buffer = buffer[self.samples_per_window:]

                # Preprocess and extract features
                features = self.process_window(window_data)

                # Send to backend
                await self.send_to_backend(timestamp, features)

    def process_window(self, window_data: np.ndarray) -> dict:
        """
        Process a single window of EEG data

        Args:
            window_data: numpy array of shape (samples, channels)

        Returns:
            dict of extracted features
        """
        # Apply filters to each channel
        filtered_data = np.zeros_like(window_data)
        for ch in range(window_data.shape[1]):
            # Band-pass filter (1-40 Hz)
            filtered = bandpass_filter(window_data[:, ch], self.sampling_rate, 1, 40)
            # Notch filter (50 Hz for EU, 60 Hz for US)
            filtered = notch_filter(filtered, self.sampling_rate, 50)
            filtered_data[:, ch] = filtered

        # Extract features
        features = extract_features(filtered_data, self.sampling_rate)

        return features

    async def send_to_backend(self, timestamp: str, features: dict):
        """Send processed features to backend API"""
        payload = {
            "patient_id": self.patient_id,
            "window_start": timestamp,
            "features": features
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/v1/ingest",
                    json=payload
                ) as response:
                    if response.status == 201:
                        print(f"Features sent successfully for {timestamp}")
                    else:
                        print(f"Error sending features: {response.status}")
        except Exception as e:
            print(f"Failed to send features: {e}")
            # TODO: Implement offline queue

if __name__ == "__main__":
    # Demo mode - simulate EEG data
    async def simulate_eeg_data():
        """Generate simulated EEG data for testing"""
        while True:
            timestamp = time.time()
            # 8 channels of simulated data
            channels = np.random.randn(8) * 50  # microvolts
            yield timestamp, channels
            await asyncio.sleep(1/250)  # 250 Hz sampling

    processor = EEGProcessor(
        patient_id="patient_001",
        backend_url="http://localhost:8000"
    )

    asyncio.run(processor.process_stream(simulate_eeg_data()))
