/// EEG data sample model
class EEGSample {
  final DateTime timestamp;
  final List<double> channels; // 8 channels
  final int samplingRate;

  EEGSample({
    required this.timestamp,
    required this.channels,
    this.samplingRate = 250,
  });

  factory EEGSample.fromJson(Map<String, dynamic> json) {
    return EEGSample(
      timestamp: DateTime.parse(json['timestamp'] as String),
      channels: (json['channels'] as List).cast<double>(),
      samplingRate: json['sampling_rate'] as int? ?? 250,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp.toIso8601String(),
      'channels': channels,
      'sampling_rate': samplingRate,
    };
  }
}

/// Extracted features from EEG window
class EEGFeatures {
  final double deltaPower;
  final double thetaPower;
  final double alphaPower;
  final double betaPower;
  final double entropy;
  final double mobility;
  final double complexity;
  final double variance;

  EEGFeatures({
    required this.deltaPower,
    required this.thetaPower,
    required this.alphaPower,
    required this.betaPower,
    required this.entropy,
    required this.mobility,
    required this.complexity,
    required this.variance,
  });

  Map<String, dynamic> toJson() {
    return {
      'delta_power': deltaPower,
      'theta_power': thetaPower,
      'alpha_power': alphaPower,
      'beta_power': betaPower,
      'entropy': entropy,
      'mobility': mobility,
      'complexity': complexity,
      'variance': variance,
    };
  }
}

/// Payload sent to backend
class FeaturePayload {
  final String patientId;
  final DateTime windowStart;
  final EEGFeatures features;

  FeaturePayload({
    required this.patientId,
    required this.windowStart,
    required this.features,
  });

  Map<String, dynamic> toJson() {
    return {
      'patient_id': patientId,
      'window_start': windowStart.toIso8601String(),
      'features': features.toJson(),
    };
  }
}

/// Patient state from backend
class PatientState {
  final String patientId;
  final double risk;
  final String state;
  final DateTime timestamp;

  PatientState({
    required this.patientId,
    required this.risk,
    required this.state,
    required this.timestamp,
  });

  factory PatientState.fromJson(Map<String, dynamic> json) {
    return PatientState(
      patientId: json['patient_id'] as String,
      risk: (json['risk'] as num).toDouble(),
      state: json['state'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }

  String get riskLevel {
    if (risk < 0.3) return 'Normal';
    if (risk < 0.6) return 'Mild Agitation';
    return 'Elevated Risk';
  }

  Color get riskColor {
    if (risk < 0.3) return Colors.green;
    if (risk < 0.6) return Colors.orange;
    return Colors.red;
  }
}
