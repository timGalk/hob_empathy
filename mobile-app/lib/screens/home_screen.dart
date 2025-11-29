import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/eeg_service.dart';
import '../services/processing_service.dart';
import '../services/backend_service.dart';
import '../widgets/connection_status.dart';
import '../widgets/risk_indicator.dart';
import '../widgets/eeg_chart_widget.dart';
import '../widgets/device_list.dart';
import '../utils/config.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    _setupDataPipeline();
  }

  void _setupDataPipeline() {
    final eegService = context.read<EEGService>();
    final processingService = context.read<ProcessingService>();
    final backendService = context.read<BackendService>();

    // Pipeline: EEG -> Processing -> Backend
    eegService.dataStream.listen((sample) {
      processingService.processSample(sample);
    });

    processingService.featuresStream.listen((features) {
      // Send to backend
      backendService.sendFeatures(
        FeaturePayload(
          patientId: Config.patientId,
          windowStart: DateTime.now(),
          features: features,
        ),
      );
    });

    // Connect to WebSocket for real-time updates
    backendService.connectWebSocket();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('EEG Monitor'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: Navigate to settings
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Connection status banner
          const ConnectionStatus(),

          // Risk indicator
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Consumer<BackendService>(
              builder: (context, backendService, child) {
                return RiskIndicator(
                  patientState: backendService.latestState,
                );
              },
            ),
          ),

          // EEG Chart
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Consumer<EEGService>(
                builder: (context, eegService, child) {
                  return EEGChartWidget(
                    dataStream: eegService.dataStream,
                  );
                },
              ),
            ),
          ),

          // Control buttons
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: _buildControlButtons(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showDeviceList,
        tooltip: 'Connect Device',
        child: const Icon(Icons.bluetooth),
      ),
    );
  }

  Widget _buildControlButtons() {
    return Consumer<EEGService>(
      builder: (context, eegService, child) {
        return Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            ElevatedButton.icon(
              onPressed: eegService.isConnected
                  ? () => eegService.disconnect()
                  : () => eegService.startSimulation(),
              icon: Icon(eegService.isConnected ? Icons.stop : Icons.play_arrow),
              label: Text(eegService.isConnected ? 'Stop' : 'Start Demo'),
              style: ElevatedButton.styleFrom(
                backgroundColor: eegService.isConnected ? Colors.red : Colors.green,
                foregroundColor: Colors.white,
              ),
            ),
            ElevatedButton.icon(
              onPressed: () => _refreshPatientState(),
              icon: const Icon(Icons.refresh),
              label: const Text('Refresh'),
            ),
          ],
        );
      },
    );
  }

  void _showDeviceList() {
    showModalBottomSheet(
      context: context,
      builder: (context) => const DeviceList(),
    );
  }

  Future<void> _refreshPatientState() async {
    final backendService = context.read<BackendService>();
    await backendService.getPatientState(Config.patientId);
  }

  @override
  void dispose() {
    final backendService = context.read<BackendService>();
    backendService.disconnectWebSocket();
    super.dispose();
  }
}
