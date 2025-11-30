"""EEG measurement with CSV export - BrainAccess MINI"""

import matplotlib
import numpy as np
import time
import threading
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt
from brainaccess import core
from brainaccess.core.eeg_manager import EEGManager
import brainaccess.core.eeg_channel as eeg_channel
from brainaccess.core.gain_mode import GainMode
from datetime import datetime
import csv
import os

matplotlib.use("TKAgg", force=True)


# === MAPOWANIE NUMERÓW KANAŁÓW NA NAZWY ELEKTROD (dla BrainAccess MINI) ===
# Sprawdź dokładnie swój model – poniżej standard dla 8-kanałowego MINI EEG

EEG_CHANNEL_NAMES = [
    "F4", "C4", "P4", "O2", "O1", "F3", "C3", "P3"
    # Jeśli masz inny model (np. 4-kanałowy), zmień tę listę!
    # Przykład dla 4-kanałowego: ["C3", "Cz", "C4", "Oz"]
]

def butter_bandpass(lowcut: float, highcut: float, fs: int, order: int = 2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], analog=False, btype="bandpass", output="sos")
    return sos

def butter_bandpass_filter(data: np.ndarray, lowcut: float, highcut: float, fs: int, order: int = 2):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfiltfilt(sos, data)
    return y

def _acq_closure(ch_number: int = 1, buffer_length: int = 1000):
    data = np.zeros((ch_number, buffer_length))
    mutex = threading.Lock()

    def _acq_callback(chunk: list, chunk_size: int) -> None:
        nonlocal data
        with mutex:
            data = np.roll(data, -chunk_size, axis=1)
            data[:, -chunk_size:] = chunk

    def get_data() -> np.ndarray:
        nonlocal data
        with mutex:
            return data.copy()

    return _acq_callback, get_data


if __name__ == "__main__":
    # ZMIEŃ NA SWOJĄ NAZWĘ URZĄDZENIA!
    device_name = "BA MINI 044"

    # Folder na zapis danych
    output_dir = "eeg_recordings"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(output_dir, f"eeg_recording_{device_name.replace(' ', '_')}_{timestamp}.csv")

    core.init()
    devices = core.scan()
    print(f"Znaleziono urządzeń: {len(devices)}")
    print(f"Nazwy: {[d.name for d in devices]}")

    with EEGManager() as mgr:
        print(f"Łączenie z: {device_name}")
        status = mgr.connect(device_name)
        if status == 2:
            raise Exception("Strumień niekompatybilny – zaktualizuj firmware!")
        elif status > 0:
            raise Exception("Nie udało się połączyć z urządzeniem")

        print(f"Poziom baterii: {mgr.get_battery_info().level}%")

        device_features = mgr.get_device_features()
        eeg_channels_number = device_features.electrode_count()
        print(f"Liczba kanałów EEG: {eeg_channels_number}")

        # === KONFIGURACJA KANAŁÓW ===
        enabled_channels = []  # do śledzenia kolejności w buforze
        channel_names = []     # nazwy do CSV

        # EEG
        for i in range(eeg_channels_number):
            ch_id = eeg_channel.ELECTRODE_MEASUREMENT + i
            mgr.set_channel_enabled(ch_id, True)
            mgr.set_channel_gain(ch_id, GainMode.X8)
            mgr.set_channel_bias(ch_id, True)

            enabled_channels.append(ch_id)
            # Dopasuj nazwę elektrody
            name = EEG_CHANNEL_NAMES[i] if i < len(EEG_CHANNEL_NAMES) else f"EEG_{i+1}"
            channel_names.append(name)

        eeg_enabled_nr = eeg_channels_number

        # Akcelerometr
        has_accel = device_features.has_accel()
        if has_accel:
            for axis in range(3):
                ch_id = eeg_channel.ACCELEROMETER + axis
                mgr.set_channel_enabled(ch_id, True)
                enabled_channels.append(ch_id)
                channel_names.append(["AccX", "AccY", "AccZ"][axis])

        # Numer próbki i status streamingu
        mgr.set_channel_enabled(eeg_channel.SAMPLE_NUMBER, True)
        enabled_channels.append(eeg_channel.SAMPLE_NUMBER)
        channel_names.append("SampleNumber")

        mgr.set_channel_enabled(eeg_channel.STREAMING, True)
        enabled_channels.append(eeg_channel.STREAMING)
        channel_names.append("StreamingStatus")

        total_channels = len(enabled_channels)

        sr = mgr.get_sample_frequency()
        print(f"Częstotliwość próbkowania: {sr} Hz")

        # Bufor na 15 sekund danych (możesz zmienić)
        duration_sec = 15
        buffer_samples = int(sr * duration_sec)

        _acq_callback, get_data = _acq_closure(ch_number=total_channels, buffer_length=buffer_samples)
        mgr.set_callback_chunk(_acq_callback)

        mgr.load_config()
        mgr.start_stream()
        print("Strumień uruchomiony – nagrywanie...")

        time.sleep(duration_sec + 3)  # trochę zapasu

        raw_data = get_data()  # shape: (total_channels, samples)

        mgr.stop_stream()
        print("Strumień zatrzymany")

    core.close()
    print("Rozłączono i zamknięto bibliotekę")

    # === ZAPIS DO CSV ===
    print(f"Zapisuję dane do: {csv_filename}")
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Nagłówek z metadanymi
        writer.writerow([f"# Nagranie nagrania EEG – BrainAccess {device_name}"])
        writer.writerow([f"# Data i godzina: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
        writer.writerow([f"# Częstotliwość próbkowania: {sr} Hz"])
        writer.writerow([f"# Czas nagrania: {duration_sec} s"])
        writer.writerow([f"# Liczba kanałów EEG: {eeg_channels_number}"])
        writer.writerow(["# Kolejność kolumn poniżej:"])

        # Nazwy kolumn
        writer.writerow(channel_names)

        # Dane (transponowane – każdy wiersz to jedna próbka czasowa)
        data_to_save = raw_data.T  # teraz: (samples, channels)
        for row in data_to_save:
            writer.writerow([f"{x:.6f}" if isinstance(x, float) else str(int(x)) for x in row])

    print(f"Zapisano {data_to_save.shape[0]} próbek do pliku CSV!")

    # === OPCJONALNIE: wykres (można zakomentować) ===
    plt.figure(figsize=(12, 8))
    time_axis = np.arange(buffer_samples) / sr

    # Filtrowane EEG z offsetem do wizualizacji
    eeg_raw = raw_data[:eeg_enabled_nr, :]
    eeg_filtered = butter_bandpass_filter(eeg_raw, 1, 40, sr)
    eeg_plot = eeg_filtered + np.arange(eeg_enabled_nr)[::-1][:, np.newaxis] * 100  # offset

    for i in range(eeg_enabled_nr):
        plt.plot(time_axis, eeg_plot[i], label=EEG_CHANNEL_NAMES[i] if i < len(EEG_CHANNEL_NAMES) else f"EEG_{i+1}")

    plt.xlabel("Czas [s]")
    plt.ylabel("Amplituda [µV] + offset")
    plt.title(f"EEG – {device_name} – {timestamp}")
    plt.legend()
    plt.tight_layout()
    plt.show()