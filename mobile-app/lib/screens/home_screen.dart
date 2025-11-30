import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/eeg_service.dart';
import '../services/processing_service.dart';
import '../services/anomaly_detection_service.dart';
import '../services/backend_service.dart';
import '../services/auth_service.dart';
import '../services/scenario_simulation_service.dart';
import '../models/eeg_data.dart';
import '../widgets/eeg_chart_widget.dart';
import '../widgets/scenario_selector.dart';
import '../utils/config.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late AnomalyDetectionService _anomalyService;
  late ScenarioSimulationService _scenarioService;
  StreamSubscription? _eegSubscription;
  StreamSubscription? _featuresSubscription;
  StreamSubscription? _anomalySubscription;
  StreamSubscription? _scenarioDataSubscription;
  StreamSubscription? _scenarioPredictionSubscription;

  // Store reference to backend service for safe disposal
  BackendService? _backendService;

  bool _isMonitoring = false;
  double _currentRisk = 0.0;
  EEGFeatures? _currentFeatures;
  AbnormalScenario? _selectedScenario;
  bool _alarmShown = false;

  @override
  void initState() {
    super.initState();
    _anomalyService = AnomalyDetectionService();
    _scenarioService = ScenarioSimulationService();
    _setupListeners();
  }

  void _setupListeners() {
    final eegService = context.read<EEGService>();
    final processingService = context.read<ProcessingService>();
    _backendService = context.read<BackendService>();

    // Listen to EEG data stream
    _eegSubscription = eegService.dataStream.listen((sample) {
      processingService.processSample(sample);
    });

    // Listen to extracted features and send to backend
    _featuresSubscription =
        processingService.featuresStream.listen((features) async {
      setState(() {
        _currentFeatures = features;
      });

      // Send features to backend for prediction
      final payload = FeaturePayload(
        patientId: Config.patientId,
        windowStart: DateTime.now(),
        features: features,
      );

      await _backendService?.sendFeatures(payload);

      // Analyze for anomalies (local processing if needed)
      _anomalyService.analyzeFeatures(features);
    });

    // Listen to backend predictions via notifier
    _backendService?.addListener(_handleBackendUpdate);

    // Listen to anomaly predictions
    _anomalySubscription =
        _anomalyService.predictionStream.listen((prediction) {
      setState(() {
        _currentRisk = prediction.risk;
      });

      // If high risk detected, navigate to alert screen immediately
      if (prediction.isAnomaly && mounted) {
        _showAnomalyAlert();
      }
    });

    // Setup scenario simulation listeners
    _setupScenarioListeners();
  }

  void _setupScenarioListeners() {
    final processingService = context.read<ProcessingService>();

    // Listen to scenario EEG data stream
    _scenarioDataSubscription = _scenarioService.dataStream.listen((sample) {
      processingService.processSample(sample);
    });

    // Listen to scenario predictions (local simulation)
    _scenarioPredictionSubscription =
        _scenarioService.predictionStream.listen((prediction) {
      setState(() {
        _currentRisk = prediction.risk;
      });

      // If high risk detected and alarm not already shown, navigate to alert screen
      if (prediction.risk >= 0.6 && mounted && !_alarmShown) {
        _alarmShown = true;
        _showAnomalyAlert();
      }
    });
  }

  void _handleBackendUpdate() {
    final backendService = context.read<BackendService>();
    final latestState = backendService.latestState;

    if (latestState != null) {
      // Pass prediction to anomaly service
      _anomalyService.handlePrediction(latestState);
    }
  }

  void _showAnomalyAlert() {
    Navigator.of(context).pushNamed('/alert_health').then((_) {
      // Reset alarm flag when returning from alert screen
      _alarmShown = false;
    });
  }

  void _startScenarioSimulation() {
    if (_selectedScenario == null) return;

    setState(() {
      _isMonitoring = true;
      _alarmShown = false;
    });

    _scenarioService.startScenario(_selectedScenario!);
  }

  void _stopScenarioSimulation() {
    setState(() {
      _isMonitoring = false;
      _currentRisk = 0.0;
      _alarmShown = false;
    });

    _scenarioService.stopSimulation();
  }

  void _toggleMonitoring() {
    setState(() {
      _isMonitoring = !_isMonitoring;
    });

    final eegService = context.read<EEGService>();
    final backendService = context.read<BackendService>();

    if (_isMonitoring) {
      // Connect to backend WebSocket for real-time predictions
      backendService.connectWebSocket();

      // Start EEG monitoring
      eegService.startSimulation();
    } else {
      // Stop monitoring and disconnect
      eegService.stopSimulation();
      backendService.disconnectWebSocket();

      _currentRisk = 0.0;
    }
  }

  @override
  void dispose() {
    _eegSubscription?.cancel();
    _featuresSubscription?.cancel();
    _anomalySubscription?.cancel();
    _scenarioDataSubscription?.cancel();
    _scenarioPredictionSubscription?.cancel();

    // Stop scenario simulation
    _scenarioService.dispose();

    // Remove backend listener (use stored reference, not context.read)
    _backendService?.removeListener(_handleBackendUpdate);
    _backendService?.disconnectWebSocket();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authService = context.watch<AuthService>();

    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        title: const Text(
          'Personal EEG Monitor',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        elevation: 0,
        backgroundColor: const Color(0xFF6C63FF),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await authService.logout();
              if (context.mounted) {
                Navigator.of(context).pushReplacementNamed('/login');
              }
            },
            tooltip: 'Logout',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStatusCard(),
            const SizedBox(height: 20),
            _buildScenarioSimulator(),
            const SizedBox(height: 20),
            _buildControlPanel(),
            const SizedBox(height: 20),
            _buildEEGChart(),
            const SizedBox(height: 20),
            _buildFeaturesCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildScenarioSimulator() {
    return ScenarioSelector(
      selectedScenario: _selectedScenario,
      isSimulating: _scenarioService.isSimulating,
      currentRisk: _scenarioService.currentRisk,
      currentState: _scenarioService.currentState,
      onScenarioSelected: (scenario) {
        setState(() {
          _selectedScenario = scenario;
        });
      },
      onStartSimulation: _startScenarioSimulation,
      onStopSimulation: _stopScenarioSimulation,
    );
  }

  Widget _buildStatusCard() {
    Color statusColor;
    String statusText;
    IconData statusIcon;

    if (!_isMonitoring) {
      statusColor = Colors.grey;
      statusText = 'Monitoring Stopped';
      statusIcon = Icons.pause_circle_outline;
    } else if (_currentRisk < 0.3) {
      statusColor = Colors.green;
      statusText = 'Normal';
      statusIcon = Icons.check_circle;
    } else if (_currentRisk < 0.6) {
      statusColor = Colors.orange;
      statusText = 'Mild Agitation';
      statusIcon = Icons.warning;
    } else {
      statusColor = Colors.red;
      statusText = 'High Risk';
      statusIcon = Icons.error;
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [statusColor.withOpacity(0.8), statusColor.withOpacity(0.6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: statusColor.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(statusIcon, size: 60, color: Colors.white),
          const SizedBox(height: 12),
          Text(
            statusText,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Risk Level: ${(_currentRisk * 100).toInt()}%',
            style: const TextStyle(
              fontSize: 18,
              color: Colors.white,
              fontWeight: FontWeight.w500,
            ),
          ),
          if (_isMonitoring) ...[
            const SizedBox(height: 16),
            LinearProgressIndicator(
              value: _currentRisk,
              backgroundColor: Colors.white.withOpacity(0.3),
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
              minHeight: 8,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildControlPanel() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Control Panel',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Color(0xFF2D3748),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton.icon(
                onPressed: _toggleMonitoring,
                icon: Icon(_isMonitoring ? Icons.stop : Icons.play_arrow),
                label: Text(
                  _isMonitoring ? 'Stop Monitoring' : 'Start Monitoring',
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor:
                      _isMonitoring ? Colors.red : const Color(0xFF6C63FF),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 2,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEEGChart() {
    final eegService = context.watch<EEGService>();

    // Use scenario data stream when scenario is simulating, otherwise use EEG service
    final dataStream = _scenarioService.isSimulating
        ? _scenarioService.dataStream
        : eegService.dataStream;

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  'Real-Time EEG Signal',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF2D3748),
                  ),
                ),
                const Spacer(),
                if (_scenarioService.isSimulating)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.orange.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      'SIMULATION',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: Colors.orange,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: !_isMonitoring && !_scenarioService.isSimulating
                  ? Center(
                      child: Text(
                        'Start monitoring or simulation to view EEG data',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                    )
                  : EEGChartWidget(dataStream: dataStream),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeaturesCard() {
    if (_currentFeatures == null) {
      return Card(
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Center(
            child: Text(
              'No features extracted yet',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 14,
              ),
            ),
          ),
        ),
      );
    }

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Brain Activity Features',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Color(0xFF2D3748),
              ),
            ),
            const SizedBox(height: 16),
            _buildFeatureRow(
                'Delta Power', _currentFeatures!.deltaPower, Colors.purple),
            _buildFeatureRow(
                'Theta Power', _currentFeatures!.thetaPower, Colors.blue),
            _buildFeatureRow(
                'Alpha Power', _currentFeatures!.alphaPower, Colors.green),
            _buildFeatureRow(
                'Beta Power', _currentFeatures!.betaPower, Colors.orange),
            const Divider(height: 24),
            _buildFeatureRow('Entropy', _currentFeatures!.entropy, Colors.teal),
            _buildFeatureRow(
                'Mobility', _currentFeatures!.mobility, Colors.indigo),
            _buildFeatureRow(
                'Complexity', _currentFeatures!.complexity, Colors.pink),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureRow(String label, double value, Color color) {
    final normalizedValue = (value / 100).clamp(0.0, 1.0);

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF4A5568),
                ),
              ),
              Text(
                value.toStringAsFixed(2),
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          LinearProgressIndicator(
            value: normalizedValue,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 6,
          ),
        ],
      ),
    );
  }
}
