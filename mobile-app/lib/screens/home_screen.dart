import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/eeg_service.dart';
import '../services/processing_service.dart';
import '../services/backend_service.dart';
import '../services/auth_service.dart';
import '../widgets/connection_status.dart';
import '../widgets/risk_indicator.dart';
import '../widgets/eeg_chart_widget.dart';
import '../widgets/device_list.dart';
import '../utils/config.dart';
import '../models/eeg_data.dart';

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
        title: Consumer<AuthService>(
          builder: (context, authService, child) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('EEG Monitor'),
                if (authService.currentUser != null)
                  Text(
                    authService.currentUser!.username,
                    style: const TextStyle(fontSize: 12),
                  ),
              ],
            );
          },
        ),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'logout') {
                _handleLogout();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout),
                    SizedBox(width: 8),
                    Text('Logout'),
                  ],
                ),
              ),
            ],
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

  Future<void> _handleLogout() async {
    final authService = context.read<AuthService>();
    final backendService = context.read<BackendService>();
    final eegService = context.read<EEGService>();

    // Disconnect all services
    backendService.disconnectWebSocket();
    if (eegService.isConnected) {
      eegService.disconnect();
    }

    // Logout
    await authService.logout();
  }

  @override
  void dispose() {
    final backendService = context.read<BackendService>();
    backendService.disconnectWebSocket();
    super.dispose();
  }
}
