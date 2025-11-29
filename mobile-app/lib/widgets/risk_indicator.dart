import 'package:flutter/material.dart';
import '../models/eeg_data.dart';

class RiskIndicator extends StatelessWidget {
  final PatientState? patientState;

  const RiskIndicator({super.key, this.patientState});

  @override
  Widget build(BuildContext context) {
    if (patientState == null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Icon(Icons.info_outline, size: 48, color: Colors.grey[400]),
              const SizedBox(height: 8),
              Text(
                'No data available',
                style: TextStyle(color: Colors.grey[600]),
              ),
            ],
          ),
        ),
      );
    }

    final risk = patientState!.risk;
    final riskPercentage = (risk * 100).toInt();

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            const Text(
              'Current Risk Level',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 150,
                  height: 150,
                  child: CircularProgressIndicator(
                    value: risk,
                    strokeWidth: 12,
                    backgroundColor: Colors.grey[300],
                    valueColor: AlwaysStoppedAnimation<Color>(
                      patientState!.riskColor,
                    ),
                  ),
                ),
                Column(
                  children: [
                    Text(
                      '$riskPercentage%',
                      style: const TextStyle(
                        fontSize: 36,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      patientState!.riskLevel,
                      style: TextStyle(
                        fontSize: 16,
                        color: patientState!.riskColor,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 20),
            _buildRiskScale(),
          ],
        ),
      ),
    );
  }

  Widget _buildRiskScale() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildScaleItem('Normal', Colors.green, 0.0, 0.3),
        _buildScaleItem('Mild', Colors.orange, 0.3, 0.6),
        _buildScaleItem('Elevated', Colors.red, 0.6, 1.0),
      ],
    );
  }

  Widget _buildScaleItem(String label, Color color, double min, double max) {
    final isActive = patientState != null &&
        patientState!.risk >= min &&
        patientState!.risk < max;

    return Column(
      children: [
        Container(
          width: 40,
          height: 8,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
            color: isActive ? color : Colors.grey[600],
          ),
        ),
      ],
    );
  }
}
