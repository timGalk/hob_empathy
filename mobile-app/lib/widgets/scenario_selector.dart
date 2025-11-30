import 'package:flutter/material.dart';
import '../services/scenario_simulation_service.dart';

/// Widget for selecting and starting abnormal EEG scenarios
class ScenarioSelector extends StatelessWidget {
  final AbnormalScenario? selectedScenario;
  final bool isSimulating;
  final double currentRisk;
  final String currentState;
  final ValueChanged<AbnormalScenario> onScenarioSelected;
  final VoidCallback onStartSimulation;
  final VoidCallback onStopSimulation;

  const ScenarioSelector({
    super.key,
    required this.selectedScenario,
    required this.isSimulating,
    required this.currentRisk,
    required this.currentState,
    required this.onScenarioSelected,
    required this.onStartSimulation,
    required this.onStopSimulation,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.science,
                  color: Theme.of(context).primaryColor,
                ),
                const SizedBox(width: 8),
                const Text(
                  'Scenario Simulation',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                if (isSimulating)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: Colors.green,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 4),
                        const Text(
                          'LIVE',
                          style: TextStyle(
                            color: Colors.green,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'Select a scenario to simulate abnormal EEG patterns:',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 12),

            // Scenario dropdown
            DropdownButtonFormField<AbnormalScenario>(
              value: selectedScenario,
              isExpanded: true,
              decoration: InputDecoration(
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
              hint: const Text('Select scenario...'),
              items: AbnormalScenario.values.map((scenario) {
                return DropdownMenuItem(
                  value: scenario,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _getScenarioIcon(scenario),
                        size: 20,
                        color: _getScenarioColor(scenario),
                      ),
                      const SizedBox(width: 8),
                      Flexible(
                        child: Text(
                          scenario.displayName,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
              onChanged: isSimulating
                  ? null
                  : (scenario) {
                      if (scenario != null) {
                        onScenarioSelected(scenario);
                      }
                    },
            ),

            // Scenario description
            if (selectedScenario != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _getScenarioColor(selectedScenario!).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color:
                        _getScenarioColor(selectedScenario!).withOpacity(0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      selectedScenario!.description,
                      style: const TextStyle(fontSize: 13),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Text(
                          'Expected Risk: ',
                          style: TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                        Text(
                          '${(selectedScenario!.expectedRisk * 100).toInt()}%',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: _getScenarioColor(selectedScenario!),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Icon(
                          selectedScenario!.shouldTriggerAlarm
                              ? Icons.warning_amber_rounded
                              : Icons.check_circle_outline,
                          size: 16,
                          color: selectedScenario!.shouldTriggerAlarm
                              ? Colors.orange
                              : Colors.green,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          selectedScenario!.shouldTriggerAlarm
                              ? 'Will trigger alarm'
                              : 'No alarm',
                          style: TextStyle(
                            fontSize: 12,
                            color: selectedScenario!.shouldTriggerAlarm
                                ? Colors.orange
                                : Colors.green,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 16),

            // Current simulation status
            if (isSimulating) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Current State',
                            style: TextStyle(fontSize: 11, color: Colors.grey),
                          ),
                          Text(
                            currentState.replaceAll('_', ' ').toUpperCase(),
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Risk Level',
                            style: TextStyle(fontSize: 11, color: Colors.grey),
                          ),
                          Row(
                            children: [
                              Text(
                                '${(currentRisk * 100).toInt()}%',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                  color: _getRiskColor(currentRisk),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: LinearProgressIndicator(
                                  value: currentRisk,
                                  backgroundColor: Colors.grey.shade300,
                                  valueColor: AlwaysStoppedAnimation(
                                    _getRiskColor(currentRisk),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],

            // Start/Stop buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: isSimulating || selectedScenario == null
                        ? null
                        : onStartSimulation,
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Start'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: isSimulating ? onStopSimulation : null,
                    icon: const Icon(Icons.stop),
                    label: const Text('Stop'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  IconData _getScenarioIcon(AbnormalScenario scenario) {
    switch (scenario) {
      case AbnormalScenario.normal:
        return Icons.favorite;
      case AbnormalScenario.absenceSeizure:
        return Icons.waves;
      case AbnormalScenario.tonicClonic:
        return Icons.flash_on;
      case AbnormalScenario.focalSeizure:
        return Icons.location_on;
      case AbnormalScenario.myoclonicJerk:
        return Icons.bolt;
      case AbnormalScenario.progressiveDeterioration:
        return Icons.trending_up;
      case AbnormalScenario.burstSuppression:
        return Icons.graphic_eq;
      case AbnormalScenario.statusEpilepticus:
        return Icons.warning;
      case AbnormalScenario.mixedAbnormalities:
        return Icons.shuffle;
    }
  }

  Color _getScenarioColor(AbnormalScenario scenario) {
    switch (scenario) {
      case AbnormalScenario.normal:
        return Colors.green;
      case AbnormalScenario.absenceSeizure:
        return Colors.orange;
      case AbnormalScenario.tonicClonic:
        return Colors.red;
      case AbnormalScenario.focalSeizure:
        return Colors.deepOrange;
      case AbnormalScenario.myoclonicJerk:
        return Colors.amber;
      case AbnormalScenario.progressiveDeterioration:
        return Colors.purple;
      case AbnormalScenario.burstSuppression:
        return Colors.indigo;
      case AbnormalScenario.statusEpilepticus:
        return Colors.red.shade900;
      case AbnormalScenario.mixedAbnormalities:
        return Colors.teal;
    }
  }

  Color _getRiskColor(double risk) {
    if (risk < 0.3) return Colors.green;
    if (risk < 0.6) return Colors.orange;
    return Colors.red;
  }
}
