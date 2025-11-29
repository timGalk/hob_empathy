import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import '../models/eeg_data.dart';

/// Service for managing EEG device connection and data acquisition
class EEGService extends ChangeNotifier {
  BluetoothDevice? _device;
  StreamSubscription? _deviceSubscription;
  bool _isConnected = false;
  bool _isScanning = false;
  List<BluetoothDevice> _availableDevices = [];

  final StreamController<EEGSample> _dataStreamController =
      StreamController<EEGSample>.broadcast();

  bool get isConnected => _isConnected;
  bool get isScanning => _isScanning;
  List<BluetoothDevice> get availableDevices => _availableDevices;
  Stream<EEGSample> get dataStream => _dataStreamController.stream;

  /// Scan for BLE EEG devices
  Future<void> startScan() async {
    _isScanning = true;
    _availableDevices.clear();
    notifyListeners();

    try {
      // Start scanning for BLE devices
      await FlutterBluePlus.startScan(timeout: const Duration(seconds: 10));

      FlutterBluePlus.scanResults.listen((results) {
        for (ScanResult result in results) {
          // Filter for EEG devices (customize based on your device)
          if (result.device.platformName.contains('EEG') ||
              result.device.platformName.contains('OpenBCI')) {
            if (!_availableDevices.contains(result.device)) {
              _availableDevices.add(result.device);
              notifyListeners();
            }
          }
        }
      });
    } catch (e) {
      debugPrint('Error scanning for devices: $e');
    } finally {
      await Future.delayed(const Duration(seconds: 10));
      _isScanning = false;
      notifyListeners();
    }
  }

  /// Connect to an EEG device
  Future<void> connectToDevice(BluetoothDevice device) async {
    try {
      await device.connect();
      _device = device;
      _isConnected = true;
      notifyListeners();

      // Discover services
      List<BluetoothService> services = await device.discoverServices();

      // Find the EEG data characteristic and subscribe
      // (This is device-specific - customize for your EEG headset)
      for (BluetoothService service in services) {
        for (BluetoothCharacteristic characteristic in service.characteristics) {
          if (characteristic.properties.notify) {
            await characteristic.setNotifyValue(true);

            _deviceSubscription = characteristic.lastValueStream.listen((value) {
              _processRawData(value);
            });
          }
        }
      }
    } catch (e) {
      debugPrint('Error connecting to device: $e');
      _isConnected = false;
      notifyListeners();
    }
  }

  /// Disconnect from device
  Future<void> disconnect() async {
    await _deviceSubscription?.cancel();
    await _device?.disconnect();
    _device = null;
    _isConnected = false;
    notifyListeners();
  }

  /// Process raw BLE data into EEG samples
  void _processRawData(List<int> rawData) {
    // Parse raw bytes into EEG channels
    // This is device-specific - customize based on your EEG device protocol

    // Example: Assuming 8 channels, 2 bytes per channel (16-bit values)
    if (rawData.length >= 16) {
      List<double> channels = [];
      for (int i = 0; i < 8; i++) {
        int value = (rawData[i * 2] << 8) | rawData[i * 2 + 1];
        // Convert to microvolts (adjust scaling based on device)
        double microvolts = value * 0.02235; // Example conversion factor
        channels.add(microvolts);
      }

      final sample = EEGSample(
        timestamp: DateTime.now(),
        channels: channels,
        samplingRate: 250,
      );

      _dataStreamController.add(sample);
    }
  }

  /// Simulate EEG data for testing (when no real device available)
  void startSimulation() {
    _isConnected = true;
    notifyListeners();

    Timer.periodic(const Duration(milliseconds: 4), (timer) {
      if (!_isConnected) {
        timer.cancel();
        return;
      }

      // Generate simulated 8-channel data
      final channels = List.generate(8, (_) {
        // Simulate realistic EEG signal (mixture of frequencies)
        final t = DateTime.now().millisecondsSinceEpoch / 1000.0;
        return 50.0 * (Math.sin(2 * Math.pi * 10 * t) + // Alpha
                Math.sin(2 * Math.pi * 20 * t) * 0.5 + // Beta
                Math.sin(2 * Math.pi * 5 * t) * 0.3);  // Theta
      });

      final sample = EEGSample(
        timestamp: DateTime.now(),
        channels: channels,
        samplingRate: 250,
      );

      _dataStreamController.add(sample);
    });
  }

  void stopSimulation() {
    _isConnected = false;
    notifyListeners();
  }

  @override
  void dispose() {
    _deviceSubscription?.cancel();
    _device?.disconnect();
    _dataStreamController.close();
    super.dispose();
  }
}

// Simple Math helper
class Math {
  static const pi = 3.14159265359;
  static double sin(double x) => x.sin();
}

extension _MathExtension on double {
  double sin() {
    // Simple sine approximation
    double x = this % (2 * Math.pi);
    if (x < 0) x += 2 * Math.pi;

    double result = x;
    double term = x;

    for (int i = 1; i <= 10; i++) {
      term *= -x * x / ((2 * i) * (2 * i + 1));
      result += term;
    }

    return result;
  }
}
