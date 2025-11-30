import 'package:flutter/material.dart';
import 'eeg_data.dart';

/// Prediction history record
class PredictionHistory {
  final int id;
  final String patientId;
  final DateTime timestamp;
  final DateTime windowStart;
  final double risk;
  final String state;
  final String? modelVersion;

  PredictionHistory({
    required this.id,
    required this.patientId,
    required this.timestamp,
    required this.windowStart,
    required this.risk,
    required this.state,
    this.modelVersion,
  });

  factory PredictionHistory.fromJson(Map<String, dynamic> json) {
    return PredictionHistory(
      id: json['id'] as int,
      patientId: json['patient_id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      windowStart: DateTime.parse(json['window_start'] as String),
      risk: (json['risk'] as num).toDouble(),
      state: json['state'] as String,
      modelVersion: json['model_version'] as String?,
    );
  }

  Color get riskColor {
    if (risk < 0.3) return Colors.green;
    if (risk < 0.6) return Colors.orange;
    return Colors.red;
  }
}

/// Alert history record
class AlertHistory {
  final int id;
  final String patientId;
  final DateTime timestamp;
  final String alertType;
  final String severity;
  final String message;
  final double? riskScore;
  final bool acknowledged;
  final DateTime? acknowledgedAt;

  AlertHistory({
    required this.id,
    required this.patientId,
    required this.timestamp,
    required this.alertType,
    required this.severity,
    required this.message,
    this.riskScore,
    required this.acknowledged,
    this.acknowledgedAt,
  });

  factory AlertHistory.fromJson(Map<String, dynamic> json) {
    return AlertHistory(
      id: json['id'] as int,
      patientId: json['patient_id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      alertType: json['alert_type'] as String,
      severity: json['severity'] as String,
      message: json['message'] as String,
      riskScore: json['risk_score'] != null ? (json['risk_score'] as num).toDouble() : null,
      acknowledged: json['acknowledged'] as bool,
      acknowledgedAt: json['acknowledged_at'] != null
          ? DateTime.parse(json['acknowledged_at'] as String)
          : null,
    );
  }

  Color get severityColor {
    switch (severity) {
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      case 'low':
        return Colors.yellow;
      default:
        return Colors.grey;
    }
  }

  IconData get severityIcon {
    switch (severity) {
      case 'high':
        return Icons.error;
      case 'medium':
        return Icons.warning;
      case 'low':
        return Icons.info;
      default:
        return Icons.notifications;
    }
  }
}

/// Patient dashboard data
class PatientDashboard {
  final String patientId;
  final String? name;
  final int? age;
  final PatientState currentState;
  final List<PredictionHistory> recentPredictions;
  final List<AlertHistory> activeAlerts;
  final List<double> riskTrend;
  final double avgRisk24h;
  final int alerts24h;

  PatientDashboard({
    required this.patientId,
    this.name,
    this.age,
    required this.currentState,
    required this.recentPredictions,
    required this.activeAlerts,
    required this.riskTrend,
    required this.avgRisk24h,
    required this.alerts24h,
  });

  factory PatientDashboard.fromJson(Map<String, dynamic> json) {
    return PatientDashboard(
      patientId: json['patient_id'] as String,
      name: json['name'] as String?,
      age: json['age'] as int?,
      currentState: PatientState.fromJson(json['current_state'] as Map<String, dynamic>),
      recentPredictions: (json['recent_predictions'] as List)
          .map((e) => PredictionHistory.fromJson(e as Map<String, dynamic>))
          .toList(),
      activeAlerts: (json['active_alerts'] as List)
          .map((e) => AlertHistory.fromJson(e as Map<String, dynamic>))
          .toList(),
      riskTrend: (json['risk_trend'] as List).map((e) => (e as num).toDouble()).toList(),
      avgRisk24h: (json['avg_risk_24h'] as num).toDouble(),
      alerts24h: json['alerts_24h'] as int,
    );
  }

  String get displayName => name ?? 'Patient $patientId';
}

/// Dashboard summary
class DashboardSummary {
  final int totalPatients;
  final int highRiskPatients;
  final int activeAlerts;
  final List<PatientDashboard> patients;

  DashboardSummary({
    required this.totalPatients,
    required this.highRiskPatients,
    required this.activeAlerts,
    required this.patients,
  });

  factory DashboardSummary.fromJson(Map<String, dynamic> json) {
    return DashboardSummary(
      totalPatients: json['total_patients'] as int,
      highRiskPatients: json['high_risk_patients'] as int,
      activeAlerts: json['active_alerts'] as int,
      patients: (json['patients'] as List)
          .map((e) => PatientDashboard.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
