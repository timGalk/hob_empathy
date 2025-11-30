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
import '../theme/theme_provider.dart';

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
      backendService.sendFeatures(
        FeaturePayload(
          patientId: Config.patientId,
          windowStart: DateTime.now(),
          features: features,
        ),
      );
    });

    backendService.connectWebSocket();
  }

  @override
  Widget build(BuildContext context) {

    final themeProvider = context.watch<ThemeProvider>();
    final bool isDark = themeProvider.isDark;

    // Increased contrast: slightly darker start, lighter end
    final Color bgGradientStart = const Color.fromARGB(255, 110, 140, 200);
    final Color bgGradientEnd = const Color.fromARGB(255, 180, 210, 255);

    // Dark mode gradient colors (darker blueish)
    // Dark mode adjusted for clearer separation
    final Color darkBgGradientStart = const Color.fromARGB(255, 40, 55, 95);
    final Color darkBgGradientEnd = const Color.fromARGB(255, 18, 30, 60);

    return Scaffold(
      backgroundColor: isDark ? darkBgGradientStart : bgGradientStart,
      appBar: AppBar(
        title: Consumer<AuthService>(
          builder: (context, authService, child) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'EmpathyApp',
                  style: TextStyle(
                    fontFamily: 'Montserrat',
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (authService.currentUser != null)
                  Text(
                    authService.currentUser!.username,
                    style: const TextStyle(
                      fontFamily: 'Montserrat',
                      fontSize: 12,
                    ),
                  ),
              ],
            );
          },
        ),
        backgroundColor: const Color(0xFF325498), // тёмно-синяя панель
        actions: [
          IconButton(
            tooltip: 'Check Alert',
            onPressed: () => Navigator.of(context).pushNamed('/alert_check'),
            icon: const Icon(Icons.warning, color: Colors.white),
          ),
          IconButton(
            tooltip: 'Health Alert',
            onPressed: () => Navigator.of(context).pushNamed('/alert_health'),
            icon: const Icon(Icons.help, color: Colors.white),
          ),
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
                    Text(
                      'Logout',
                      style: TextStyle(fontFamily: 'Montserrat'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: isDark
                ? [darkBgGradientStart, darkBgGradientEnd]
                : [bgGradientStart, bgGradientEnd],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Column(
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
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: _buildControlButtons(),
          ),

          // Theme switcher button
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Consumer<ThemeProvider>(
              builder: (context, theme, child) {
                return ElevatedButton.icon(
                  onPressed: () => theme.toggleTheme(),
                  icon: Icon(
                    theme.isDark ? Icons.dark_mode : Icons.light_mode,
                    color: Colors.white,
                  ),
                  label: const Text(
                    "Switch Theme",
                    style: TextStyle(
                      fontFamily: 'Montserrat',
                      color: Colors.white,
                      fontSize: 16,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF325498),
                    minimumSize: const Size(double.infinity, 50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showDeviceList,
        tooltip: 'Connect Device',
        backgroundColor: const Color(0xFF325498),
        child: const Icon(Icons.bluetooth, color: Colors.white),
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
              icon: Icon(
                eegService.isConnected ? Icons.stop : Icons.play_arrow,
                color: Colors.white,
              ),
              label: Text(
                eegService.isConnected ? 'Stop' : 'Start Demo',
                style: const TextStyle(
                  fontFamily: 'Montserrat',
                  color: Colors.white,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: eegService.isConnected ? Colors.red : Colors.green,
              ),
            ),
            ElevatedButton.icon(
              onPressed: () => _refreshPatientState(),
              icon: const Icon(Icons.refresh, color: Colors.white),
              label: const Text(
                'Refresh',
                style: TextStyle(
                  fontFamily: 'Montserrat',
                  color: Colors.white,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF325498),
              ),
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

    backendService.disconnectWebSocket();
    if (eegService.isConnected) {
      eegService.disconnect();
    }

    await authService.logout();
  }

  @override
  void dispose() {
    final backendService = context.read<BackendService>();
    backendService.disconnectWebSocket();
    super.dispose();
  }
}
