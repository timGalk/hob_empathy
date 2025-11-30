"""EEG measurement example

Example how to get measurements using brainaccess library

Change Bluetooth device name to your device name (line 68)
"""
import csv
import os
from datetime import datetime

import matplotlib
import numpy as np
import time
import threading
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt
from brainaccess import core
from brainaccess.core.eeg_manager import EEGManager
import brainaccess.core.eeg_channel as eeg_channel
from brainaccess.core.gain_mode import (
    GainMode,
)

####################################################################
duration = 40
durSec = 1

####################################################################

#matplotlib.use("TKAgg", force=True)


def butter_bandpass(
    lowcut: float, highcut: float, fs: int, order: int = 2
) -> np.ndarray:
    """Design a bandpass Butterworth filter."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], analog=False, btype="bandpass", output="sos")
    return sos


def butter_bandpass_filter(
    data: np.ndarray, lowcut: float, highcut: float, fs: int, order: int = 2
) -> np.ndarray:
    """Apply a bandpass Butterworth filter to the data."""
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfiltfilt(sos, data)
    return y


def _acq_closure(ch_number: int = 1, buffer_length: int = 1000) -> tuple:
    """Acquisition callback closure."""
    data = np.zeros((ch_number, buffer_length))
    mutex = threading.Lock()

    def _acq_callback(chunk: list, chunk_size: int) -> None:
        nonlocal data
        nonlocal mutex
        with mutex:
            data = np.roll(data, -chunk_size)
            data[:, -chunk_size:] = chunk

    def get_data() -> np.ndarray:
        nonlocal data
        with mutex:
            return data.copy()

    return _acq_callback, get_data


if __name__ == "__main__":
    # Change to your device name
    # Device name can be found on the back of the device
    device_name = "BA MINI 044"

    output_dir = "eeg_recordings/"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(output_dir, f"eeg_recording_{device_name.replace(' ', '_')}_{timestamp}.csv")

    # init the core
    core.init()

    # scan for devices
    devices = core.scan()
  #  print("Found devices:", len(devices))
  #  print(f"Devices: {[device.name for device in devices]}")

    # connect to the device
    with EEGManager() as mgr:
       # print("Connecting to device:", device_name)
        _status = mgr.connect(device_name)
        if _status == 2:
            raise Exception("Stream is incompatible. Update the firmware.")
        elif _status > 0:
            raise Exception("Connection failed")

        # battery info
       # print(f"battery level: {mgr.get_battery_info().level} %")

        # Get electrode count
        device_features = mgr.get_device_features()
        eeg_channels_number = device_features.electrode_count()
       # print(f"Device has {eeg_channels_number} EEG channels")

        # set the channels
        ch_nr = 0
        for i in range(0, eeg_channels_number):
            mgr.set_channel_enabled(eeg_channel.ELECTRODE_MEASUREMENT + i, True)  # noqa
            ch_nr += 1
            mgr.set_channel_gain(
                eeg_channel.ELECTRODE_MEASUREMENT + i, GainMode.X8
            )  # noqa
        mgr.set_channel_bias(eeg_channel.ELECTRODE_MEASUREMENT + i, True)

        # Keep track of enabled eeg channel number
        eeg_enabled_nr = ch_nr

        # check if the device has accelerometer
        has_accel = device_features.has_accel()
        if has_accel:
       #     print("Setting the accelerometer")
            mgr.set_channel_enabled(eeg_channel.ACCELEROMETER, True)
            ch_nr += 1
            mgr.set_channel_enabled(eeg_channel.ACCELEROMETER + 1, True)
            ch_nr += 1
            mgr.set_channel_enabled(eeg_channel.ACCELEROMETER + 2, True)
            ch_nr += 1


        mgr.set_channel_enabled(eeg_channel.SAMPLE_NUMBER, True)
        ch_nr += 1

        # set the streaming channel, shows 0 if Bluetooth connection
        # was lost and 0 was added to the data
        mgr.set_channel_enabled(eeg_channel.STREAMING, True)
        ch_nr += 1

        # get the sample rate
        sr = mgr.get_sample_frequency()

        # define the callback for the acquisition
        buffer_time = int(sr * duration)  # seconds
        _acq_callback, get_data = _acq_closure(
            ch_number=ch_nr, buffer_length=buffer_time
        )
        mgr.set_callback_chunk(_acq_callback)

        # load defined configuration
        mgr.load_config()

        sound = "/home/dmin/PycharmProjects/HeroesOfTheBrain/other/beep.wav"
        os.system(f"aplay {sound} >/dev/null 2>&1")

        # start the stream
        mgr.start_stream()
      #  print("Stream started")


        # collect data
        time.sleep(4)
        for i in range(duration):
            time.sleep(durSec)
      #      print(f"Collecting data {i + 1}/{duration}")

        # get the data
        dat = get_data()

        # stop the stream
        mgr.stop_stream()
     #   print("Stream stopped")
        sound = "/home/dmin/PycharmProjects/HeroesOfTheBrain/other/beep.wav"
        os.system(f"aplay {sound} >/dev/null 2>&1")
        time.sleep(1)

        # The EEGManager destructor calls mgr.disconnect()
        # so we don't need to call it here

    #print("Disconnected from the device")
    time.sleep(1)

    # close the core
    core.close()
    #print("Core closed")

    # plot the data
    #print("Plotting the data")

    # Apply bandpass filter to EEG data
    eeg_data = dat[1: eeg_enabled_nr + 1, :]

    eeg_data = eeg_data - np.mean(eeg_data, axis=1, keepdims=True)
    eeg_data = butter_bandpass_filter(eeg_data, 1, 40, sr)
    # Add offsets for visualization
    eeg_data = eeg_data + np.arange(eeg_enabled_nr)[:, np.newaxis]
    """
    # Create subplots
    fig, axs = plt.subplots(2, 1, figsize=(10, 10))

    # Plot the data
    axs[0].plot(eeg_data.T)
    axs[0].set_ylabel("EEG Channels")
    axs[0].set_xlim([0, 250 * duration])
    eeg_labels = ["F4", "C4", "F3", "O2", "O1", "F3", "C3", "P3"][:eeg_enabled_nr]

    # Add legend for EEG
    for idx, label in enumerate(eeg_labels):
        axs[0].plot([], [], label=label)

    axs[0].legend(loc="upper right")

    if has_accel:
        axs[1].plot(dat[-4:-1, :].T)
        axs[1].set_ylabel("Accelerometer")
    else:
        axs[1].axis("off")  # Hide the unused subplot
"""


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_filename = os.path.join(f"eeg_recordings/eeg_recording_{device_name.replace(' ', '_')}_{timestamp}.csv")

    data_to_save = []
    #print("len eeg data.T", len(eeg_data))
    #print("len eeg data.T elem", len(eeg_data.T[0]))
    count = 0
    for row in range(len(eeg_data.T)):
        data_to_save.append([])
        count += 1
        data_to_save[row].append(count/sr)
        for i in range(len(eeg_data.T[0])):
            data_to_save[row].append(eeg_data.T[row][i])

    for row in range(len(dat.T)):  # teraz: (samples, channels)
        if row >= sr * 20 and row <= 30 * sr:
            data_to_save[row].append(1)
        else:
            data_to_save[row].append(0)
        for i in dat[-4:-1, :].T[row]:
            data_to_save[row].append(i)



    # # === ZAPIS DO CSV ===
    print(f"Zapisuję dane do: {csv_filename}")
    with (open(csv_filename, mode='w', newline='', encoding='utf-8') as f):
        writer = csv.writer(f)

        # Nagłówek z metadanymi
        writer.writerow([f"# Nagranie nagrania EEG – BrainAccess {device_name}"])
        writer.writerow([f"# Data i godzina: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
        writer.writerow([f"# Częstotliwość próbkowania: {sr} Hz"])
        writer.writerow([f"# Czas nagrania: {duration} s"])
        writer.writerow([f"# Liczba kanałów EEG: {eeg_channels_number}"])
        writer.writerow(["# Kolejność kolumn poniżej:"])

        # Nazwy kolumn
        writer.writerow(
            ["Time", "F4", "C4", "P4", "O2", "O1", "F3", "C3", "P3", "Obsense", "AccZ", "AccY", "AccX"])

        # Dane (transponowane – każdy wiersz to jedna próbka czasowa)


        for row in data_to_save[400:]:
            writer.writerow([f"{x:.6f}" if isinstance(x, float) else str(int(x)) for x in row])

 #   plt.show()
