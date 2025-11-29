# EEG Monitor - Mobile App

Flutter mobile application for EEG dementia monitoring. Acts as the edge processor for real-time EEG signal acquisition, preprocessing, and feature extraction.

## Features

- BLE connectivity to EEG headsets
- Real-time signal processing and filtering
- Feature extraction (bandpower, entropy, Hjorth parameters)
- Live EEG visualization
- Risk level monitoring
- Backend synchronization via REST API and WebSocket
- Offline mode with data queuing
- Demo/simulation mode for testing

## Architecture

```
EEG Device (BLE)
    │
    ▼
EEG Service (data acquisition)
    │
    ▼
Processing Service (signal processing + feature extraction)
    │
    ▼
Backend Service (API communication)
    │
    ▼
Backend API
```

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── models/
│   └── eeg_data.dart        # Data models
├── services/
│   ├── eeg_service.dart     # EEG device management
│   ├── processing_service.dart  # Signal processing
│   └── backend_service.dart # API communication
├── screens/
│   └── home_screen.dart     # Main screen
├── widgets/
│   ├── connection_status.dart   # Status indicators
│   ├── risk_indicator.dart      # Risk gauge
│   ├── eeg_chart_widget.dart   # EEG visualization
│   └── device_list.dart         # BLE device list
└── utils/
    └── config.dart          # Configuration
```

## Getting Started

### Prerequisites

- Flutter SDK 3.0+
- Android Studio / Xcode
- EEG device with BLE support (or use demo mode)

### Installation

1. Install dependencies:
```bash
cd mobile-app
flutter pub get
```

2. Run the app:
```bash
# For Android
flutter run

# For iOS
flutter run

# For a specific device
flutter devices
flutter run -d <device-id>
```

### Configuration

Edit `lib/utils/config.dart` or use environment variables:

```dart
// Backend URLs
static const String backendUrl = 'http://your-backend-url:8000';
static const String wsUrl = 'ws://your-backend-url:8000';

// Patient ID
static const String patientId = 'patient_001';
```

Or run with environment variables:
```bash
flutter run --dart-define=BACKEND_URL=http://192.168.1.100:8000 \
            --dart-define=WS_URL=ws://192.168.1.100:8000 \
            --dart-define=PATIENT_ID=patient_001
```

## Usage

### Demo Mode

For testing without a real EEG device:

1. Launch the app
2. Tap "Start Demo" button
3. Simulated EEG data will be generated and processed
4. View real-time visualization and risk assessment

### Real EEG Device

1. Turn on your EEG headset
2. Tap the Bluetooth FAB button
3. Scan for available devices
4. Select your EEG device
5. Wait for connection
6. Data will automatically stream and process

## Features

### EEG Service

- Bluetooth LE device scanning
- Connection management
- Real-time data streaming
- Demo/simulation mode

### Processing Service

- Signal filtering (bandpass, notch)
- Windowing (2-second windows)
- Feature extraction:
  - Delta (1-4 Hz) power
  - Theta (4-8 Hz) power
  - Alpha (8-13 Hz) power
  - Beta (13-30 Hz) power
  - Spectral entropy
  - Hjorth mobility & complexity
  - Signal variance

### Backend Service

- REST API integration
- WebSocket for real-time updates
- Automatic retry on connection failure
- Offline queue (TODO)

## Supported EEG Devices

The app is designed to work with any BLE-enabled EEG headset. You may need to customize the data parsing in `eeg_service.dart` based on your specific device protocol.

Example compatible devices:
- OpenBCI Cyton/Ganglion
- Muse headband
- Emotiv EPOC
- NeuroSky MindWave
- Custom EEG devices with BLE

## Permissions

### Android

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.BLUETOOTH"/>
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN"/>
<uses-permission android:name="android.permission.BLUETOOTH_SCAN"/>
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.INTERNET"/>
```

### iOS

Add to `ios/Runner/Info.plist`:

```xml
<key>NSBluetoothAlwaysUsageDescription</key>
<string>This app needs Bluetooth to connect to EEG devices</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs location access to scan for Bluetooth devices</string>
```

## Building for Production

### Android

```bash
flutter build apk --release
# or
flutter build appbundle --release
```

APK location: `build/app/outputs/flutter-apk/app-release.apk`

### iOS

```bash
flutter build ios --release
```

Then open in Xcode to archive and distribute.

## Troubleshooting

### Bluetooth not working

- Ensure Bluetooth permissions are granted
- Check if Bluetooth is enabled on device
- Restart the app

### Cannot connect to backend

- Verify backend URL in config
- Check network connectivity
- For Android emulator, use `10.0.2.2` instead of `localhost`
- For iOS simulator, use your computer's IP address

### No EEG data showing

- Ensure device is properly connected
- Check device battery
- Verify signal quality
- Try demo mode to test the pipeline

## Development

### Adding New Features

1. Models: Add data structures to `models/`
2. Services: Implement business logic in `services/`
3. UI: Create widgets in `widgets/` and screens in `screens/`
4. Configuration: Update `utils/config.dart`

### Testing

```bash
flutter test
```

## Performance

- Sampling rate: 250 Hz
- Processing latency: <100ms
- Window size: 2 seconds (500 samples)
- UI update rate: 10 Hz

## Dependencies

Main packages:
- `provider` - State management
- `flutter_blue_plus` - BLE connectivity
- `http` - REST API
- `web_socket_channel` - WebSocket
- `fl_chart` - Data visualization
- `fftea` - FFT for signal processing

## License

MIT License

## Authors

MVP developed for 24-hour hackathon
