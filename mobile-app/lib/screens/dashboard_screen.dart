import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/dashboard_models.dart';
import '../services/backend_service.dart';
import '../services/auth_service.dart';
import '../widgets/patient_card.dart';
import '../widgets/risk_trend_chart.dart';
import '../widgets/alert_list_item.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  DashboardSummary? _dashboardData;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
    _startAutoRefresh();
  }

  void _startAutoRefresh() {
    // Auto-refresh every 10 seconds
    Future.delayed(const Duration(seconds: 10), () {
      if (mounted) {
        _loadDashboard(silent: true);
        _startAutoRefresh();
      }
    });
  }

  Future<void> _loadDashboard({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }

    final backendService = context.read<BackendService>();
    final dashboard = await backendService.getDashboard();

    if (!mounted) return;

    setState(() {
      if (dashboard != null) {
        _dashboardData = dashboard;
        _error = null;
      } else {
        _error = 'Failed to load dashboard';
      }
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final authService = context.watch<AuthService>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Patient Monitoring Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDashboard,
            tooltip: 'Refresh',
          ),
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
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _dashboardData == null) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_error != null && _dashboardData == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(_error!, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadDashboard,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_dashboardData == null) {
      return const Center(
        child: Text('No data available'),
      );
    }

    return RefreshIndicator(
      onRefresh: () => _loadDashboard(),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSummaryCards(),
            const SizedBox(height: 24),
            _buildPatientsSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCards() {
    return Row(
      children: [
        Expanded(
          child: _buildSummaryCard(
            'Total Patients',
            '${_dashboardData!.totalPatients}',
            Icons.people,
            Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildSummaryCard(
            'High Risk',
            '${_dashboardData!.highRiskPatients}',
            Icons.warning,
            Colors.red,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildSummaryCard(
            'Active Alerts',
            '${_dashboardData!.activeAlerts}',
            Icons.notifications_active,
            Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryCard(String label, String value, IconData icon, Color color) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPatientsSection() {
    if (_dashboardData!.patients.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Text(
            'No patients assigned',
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Patients',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ...(_dashboardData!.patients.map((patient) => Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: PatientCard(
            patient: patient,
            onTap: () => _navigateToPatientDetail(patient),
          ),
        ))),
      ],
    );
  }

  void _navigateToPatientDetail(PatientDashboard patient) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => PatientDetailScreen(patient: patient),
      ),
    );
  }
}

/// Patient detail screen with charts and history
class PatientDetailScreen extends StatefulWidget {
  final PatientDashboard patient;

  const PatientDetailScreen({super.key, required this.patient});

  @override
  State<PatientDetailScreen> createState() => _PatientDetailScreenState();
}

class _PatientDetailScreenState extends State<PatientDetailScreen> {
  PatientDashboard? _patientData;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _patientData = widget.patient;
    _loadPatientDetail();
  }

  Future<void> _loadPatientDetail() async {
    setState(() => _isLoading = true);

    final backendService = context.read<BackendService>();
    final data = await backendService.getPatientDashboard(widget.patient.patientId);

    if (!mounted) return;

    setState(() {
      if (data != null) {
        _patientData = data;
      }
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_patientData!.displayName),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadPatientDetail,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadPatientDetail,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildPatientInfo(),
              const SizedBox(height: 24),
              _buildCurrentStatus(),
              const SizedBox(height: 24),
              _buildRiskTrend(),
              const SizedBox(height: 24),
              _buildActiveAlerts(),
              const SizedBox(height: 24),
              _buildRecentPredictions(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPatientInfo() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const CircleAvatar(
              radius: 30,
              child: Icon(Icons.person, size: 32),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _patientData!.displayName,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'ID: ${_patientData!.patientId}',
                    style: const TextStyle(color: Colors.grey),
                  ),
                  if (_patientData!.age != null)
                    Text(
                      'Age: ${_patientData!.age}',
                      style: const TextStyle(color: Colors.grey),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentStatus() {
    final state = _patientData!.currentState;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Current Status',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    children: [
                      Container(
                        width: 100,
                        height: 100,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: state.riskColor.withOpacity(0.2),
                        ),
                        child: Center(
                          child: Text(
                            '${(state.risk * 100).toInt()}%',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: state.riskColor,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        state.riskLevel,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: state.riskColor,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildStat('24h Avg Risk', '${(_patientData!.avgRisk24h * 100).toInt()}%'),
                      const SizedBox(height: 8),
                      _buildStat('24h Alerts', '${_patientData!.alerts24h}'),
                      const SizedBox(height: 8),
                      _buildStat('Active Alerts', '${_patientData!.activeAlerts.length}'),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStat(String label, String value) {
    return Row(
      children: [
        Text(
          '$label: ',
          style: const TextStyle(color: Colors.grey),
        ),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget _buildRiskTrend() {
    if (_patientData!.riskTrend.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Risk Trend (Last 20 Predictions)',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: RiskTrendChart(riskData: _patientData!.riskTrend),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActiveAlerts() {
    if (_patientData!.activeAlerts.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Active Alerts',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...(_patientData!.activeAlerts.map((alert) => AlertListItem(
              alert: alert,
              onAcknowledge: () async {
                final backendService = context.read<BackendService>();
                final success = await backendService.acknowledgeAlert(alert.id);
                if (success && mounted) {
                  setState(() {
                    _patientData!.activeAlerts.remove(alert);
                  });
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Alert acknowledged')),
                  );
                }
              },
            ))),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentPredictions() {
    if (_patientData!.recentPredictions.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Recent Predictions',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _patientData!.recentPredictions.length,
              separatorBuilder: (context, index) => const Divider(),
              itemBuilder: (context, index) {
                final prediction = _patientData!.recentPredictions[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: prediction.riskColor.withOpacity(0.2),
                    child: Text(
                      '${(prediction.risk * 100).toInt()}%',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: prediction.riskColor,
                      ),
                    ),
                  ),
                  title: Text(prediction.state.toUpperCase()),
                  subtitle: Text(
                    _formatTimestamp(prediction.timestamp),
                    style: const TextStyle(fontSize: 12),
                  ),
                  trailing: Text(
                    'Risk: ${(prediction.risk * 100).toInt()}%',
                    style: TextStyle(color: prediction.riskColor),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final diff = now.difference(timestamp);

    if (diff.inMinutes < 1) {
      return 'Just now';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}h ago';
    } else {
      return '${diff.inDays}d ago';
    }
  }
}
