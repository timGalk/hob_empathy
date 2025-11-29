import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import '../services/eeg_service.dart';

class DeviceList extends StatefulWidget {
  const DeviceList({super.key});

  @override
  State<DeviceList> createState() => _DeviceListState();
}

class _DeviceListState extends State<DeviceList> {
  @override
  void initState() {
    super.initState();
    _startScan();
  }

  void _startScan() {
    final eegService = context.read<EEGService>();
    eegService.startScan();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<EEGService>(
      builder: (context, eegService, child) {
        return Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Available EEG Devices',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  if (eegService.isScanning)
                    const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                ],
              ),
              const SizedBox(height: 16),
              if (eegService.availableDevices.isEmpty && !eegService.isScanning)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32.0),
                    child: Text(
                      'No devices found. Make sure your EEG device is turned on.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey),
                    ),
                  ),
                )
              else
                ...eegService.availableDevices.map(
                  (device) => _buildDeviceItem(device, eegService),
                ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: eegService.isScanning ? null : _startScan,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Scan Again'),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDeviceItem(BluetoothDevice device, EEGService eegService) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: const Icon(Icons.bluetooth, color: Colors.blue),
        title: Text(
          device.platformName.isNotEmpty ? device.platformName : 'Unknown Device',
        ),
        subtitle: Text(device.remoteId.toString()),
        trailing: ElevatedButton(
          onPressed: () async {
            await eegService.connectToDevice(device);
            if (mounted) {
              Navigator.pop(context);
            }
          },
          child: const Text('Connect'),
        ),
      ),
    );
  }
}
