import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/foundation.dart';
import '../models/eeg_data.dart';

/// Types of abnormal EEG scenarios that can trigger predictions
enum AbnormalScenario {
  normal,
  absenceSeizure,
  tonicClonic,
  focalSeizure,
  myoclonicJerk,
  progressiveDeterioration,
  burstSuppression,
  statusEpilepticus,
  mixedAbnormalities,
}

extension AbnormalScenarioExtension on AbnormalScenario {
  String get displayName {
    switch (this) {
      case AbnormalScenario.normal:
        return 'Normal EEG';
      case AbnormalScenario.absenceSeizure:
        return 'Absence Seizure (3Hz Spike-Wave)';
      case AbnormalScenario.tonicClonic:
        return 'Tonic-Clonic Seizure';
      case AbnormalScenario.focalSeizure:
        return 'Focal Seizure';
      case AbnormalScenario.myoclonicJerk:
        return 'Myoclonic Jerks';
      case AbnormalScenario.progressiveDeterioration:
        return 'Progressive Deterioration';
      case AbnormalScenario.burstSuppression:
        return 'Burst-Suppression';
      case AbnormalScenario.statusEpilepticus:
        return 'Status Epilepticus';
      case AbnormalScenario.mixedAbnormalities:
        return 'Mixed Abnormalities';
    }
  }

  String get description {
    switch (this) {
      case AbnormalScenario.normal:
        return 'Normal baseline EEG activity';
      case AbnormalScenario.absenceSeizure:
        return 'Classic 3 Hz spike-wave discharge pattern';
      case AbnormalScenario.tonicClonic:
        return 'Grand mal seizure with tonic and clonic phases';
      case AbnormalScenario.focalSeizure:
        return 'Localized abnormal activity in one hemisphere';
      case AbnormalScenario.myoclonicJerk:
        return 'Brief, sharp muscle jerk spikes';
      case AbnormalScenario.progressiveDeterioration:
        return 'Gradually worsening abnormal patterns';
      case AbnormalScenario.burstSuppression:
        return 'Alternating bursts and suppression periods';
      case AbnormalScenario.statusEpilepticus:
        return 'Continuous seizure activity';
      case AbnormalScenario.mixedAbnormalities:
        return 'Various abnormality types combined';
    }
  }

  /// Risk level this scenario should trigger (0.0 - 1.0)
  double get expectedRisk {
    switch (this) {
      case AbnormalScenario.normal:
        return 0.1;
      case AbnormalScenario.absenceSeizure:
        return 0.85;
      case AbnormalScenario.tonicClonic:
        return 0.95;
      case AbnormalScenario.focalSeizure:
        return 0.75;
      case AbnormalScenario.myoclonicJerk:
        return 0.7;
      case AbnormalScenario.progressiveDeterioration:
        return 0.6; // Starts low, increases
      case AbnormalScenario.burstSuppression:
        return 0.8;
      case AbnormalScenario.statusEpilepticus:
        return 0.98;
      case AbnormalScenario.mixedAbnormalities:
        return 0.75;
    }
  }

  /// Whether this scenario should trigger the alarm screen
  bool get shouldTriggerAlarm => expectedRisk >= 0.6;
}

/// Service for simulating abnormal EEG scenarios to test predictions
class ScenarioSimulationService extends ChangeNotifier {
  static const int samplingRate = 250; // Hz
  static const int numChannels = 8;

  Timer? _simulationTimer;
  AbnormalScenario _currentScenario = AbnormalScenario.normal;
  bool _isSimulating = false;
  double _simulationTime = 0.0;
  double _currentRisk = 0.0;
  String _currentState = 'normal';

  final StreamController<EEGSample> _dataStreamController =
      StreamController<EEGSample>.broadcast();
  final StreamController<PatientState> _predictionController =
      StreamController<PatientState>.broadcast();

  final math.Random _random = math.Random();

  AbnormalScenario get currentScenario => _currentScenario;
  bool get isSimulating => _isSimulating;
  double get currentRisk => _currentRisk;
  String get currentState => _currentState;
  Stream<EEGSample> get dataStream => _dataStreamController.stream;
  Stream<PatientState> get predictionStream => _predictionController.stream;

  /// Start simulating a specific scenario
  void startScenario(AbnormalScenario scenario) {
    stopSimulation();

    _currentScenario = scenario;
    _isSimulating = true;
    _simulationTime = 0.0;
    _currentRisk = 0.0;
    _currentState = 'normal';
    notifyListeners();

    debugPrint('Starting scenario simulation: ${scenario.displayName}');

    // Generate samples at 250 Hz (every 4ms)
    _simulationTimer = Timer.periodic(
      const Duration(milliseconds: 4),
      (_) => _generateSample(),
    );
  }

  /// Stop simulation
  void stopSimulation() {
    _simulationTimer?.cancel();
    _simulationTimer = null;
    _isSimulating = false;
    _currentRisk = 0.0;
    _currentState = 'normal';
    notifyListeners();
  }

  /// Generate a single EEG sample based on current scenario
  void _generateSample() {
    _simulationTime += 1.0 / samplingRate;

    List<double> channels;
    double risk;
    String state;

    switch (_currentScenario) {
      case AbnormalScenario.normal:
        channels = _generateNormalEEG();
        risk = 0.1 + _random.nextDouble() * 0.1;
        state = 'normal';
        break;

      case AbnormalScenario.absenceSeizure:
        final result = _generateAbsenceSeizure();
        channels = result['channels'] as List<double>;
        risk = result['risk'] as double;
        state = result['state'] as String;
        break;

      case AbnormalScenario.tonicClonic:
        final result = _generateTonicClonic();
        channels = result['channels'] as List<double>;
        risk = result['risk'] as double;
        state = result['state'] as String;
        break;

      case AbnormalScenario.focalSeizure:
        final result = _generateFocalSeizure();
        channels = result['channels'] as List<double>;
        risk = result['risk'] as double;
        state = result['state'] as String;
        break;

      case AbnormalScenario.myoclonicJerk:
        final result = _generateMyoclonicJerks();
        channels = result['channels'] as List<double>;
        risk = result['risk'] as double;
        state = result['state'] as String;
        break;

      case AbnormalScenario.progressiveDeterioration:
        final result = _generateProgressiveDeterioration();
        channels = result['channels'] as List<double>;
        risk = result['risk'] as double;
        state = result['state'] as String;
        break;

      case AbnormalScenario.burstSuppression:
        final result = _generateBurstSuppression();
        channels = result['channels'] as List<double>;
        risk = result['risk'] as double;
        state = result['state'] as String;
        break;

      case AbnormalScenario.statusEpilepticus:
        final result = _generateStatusEpilepticus();
        channels = result['channels'] as List<double>;
        risk = result['risk'] as double;
        state = result['state'] as String;
        break;

      case AbnormalScenario.mixedAbnormalities:
        final result = _generateMixedAbnormalities();
        channels = result['channels'] as List<double>;
        risk = result['risk'] as double;
        state = result['state'] as String;
        break;
    }

    // Update current state
    _currentRisk = risk;
    _currentState = state;

    // Emit EEG sample
    final sample = EEGSample(
      timestamp: DateTime.now(),
      channels: channels,
      samplingRate: samplingRate,
    );
    _dataStreamController.add(sample);

    // Emit prediction updates every 500ms (2 Hz)
    if ((_simulationTime * 2).floor() >
        ((_simulationTime - 1.0 / samplingRate) * 2).floor()) {
      _emitPrediction(risk, state);
    }

    notifyListeners();
  }

  void _emitPrediction(double risk, String state) {
    final prediction = PatientState(
      patientId: 'simulation',
      risk: risk,
      state: state,
      timestamp: DateTime.now(),
    );
    _predictionController.add(prediction);
  }

  /// Generate normal baseline EEG
  List<double> _generateNormalEEG() {
    final t = _simulationTime;
    return List.generate(numChannels, (ch) {
      final phaseOffset = ch * 0.5;
      // Typical EEG frequency bands
      final delta = 30.0 * math.sin(2 * math.pi * 2 * t + phaseOffset);
      final theta = 25.0 * math.sin(2 * math.pi * 6 * t + phaseOffset);
      final alpha = 40.0 * math.sin(2 * math.pi * 10 * t + phaseOffset);
      final beta = 15.0 * math.sin(2 * math.pi * 20 * t + phaseOffset);
      final noise = (_random.nextDouble() - 0.5) * 20;
      return delta + theta + alpha + beta + noise;
    });
  }

  /// Generate absence seizure (3 Hz spike-wave)
  Map<String, dynamic> _generateAbsenceSeizure() {
    final t = _simulationTime;

    // Seizure occurs in cycles: 2-8s seizure, 5s normal, repeat
    final cycleTime = t % 15.0;
    final inSeizure = cycleTime >= 2.0 && cycleTime < 10.0;

    if (inSeizure) {
      // Classic 3 Hz spike-wave discharge
      final spikeAmplitude = 200.0;
      final channels = List.generate(numChannels, (ch) {
        final spike = spikeAmplitude * math.sin(2 * math.pi * 3.0 * t);
        final harmonic = spikeAmplitude * 0.3 * math.sin(2 * math.pi * 6.0 * t);
        final noise = (_random.nextDouble() - 0.5) * 20;
        return spike + harmonic + noise;
      });

      return {
        'channels': channels,
        'risk': 0.85 + _random.nextDouble() * 0.1,
        'state': 'absence_seizure',
      };
    } else {
      return {
        'channels': _generateNormalEEG(),
        'risk': 0.15 + _random.nextDouble() * 0.1,
        'state': 'normal',
      };
    }
  }

  /// Generate tonic-clonic seizure pattern
  Map<String, dynamic> _generateTonicClonic() {
    final t = _simulationTime;

    // Phases: Pre-ictal (0-5s), Tonic (5-15s), Clonic (15-35s), Post-ictal (35+)
    String state;
    double risk;
    List<double> channels;

    if (t < 5.0) {
      // Pre-ictal - normal
      channels = _generateNormalEEG();
      risk = 0.2 + t * 0.05;
      state = 'pre_ictal';
    } else if (t < 15.0) {
      // Tonic phase - high amplitude, high frequency
      channels = List.generate(numChannels, (ch) {
        final tonicSignal = 250.0 * math.sin(2 * math.pi * 15 * t) +
            150.0 * math.sin(2 * math.pi * 22 * t) +
            (_random.nextDouble() - 0.5) * 100;
        return tonicSignal;
      });
      risk = 0.9 + _random.nextDouble() * 0.08;
      state = 'tonic_phase';
    } else if (t < 35.0) {
      // Clonic phase - rhythmic jerks, slowing frequency
      final clonicT = t - 15.0;
      final freq = 4.0 - (3.0 * clonicT / 20.0); // 4 Hz -> 1 Hz
      final amplitude = 180.0 * (1.0 - 0.3 * clonicT / 20.0);

      channels = List.generate(numChannels, (ch) {
        final clonic = amplitude * math.sin(2 * math.pi * freq * t);
        final noise = (_random.nextDouble() - 0.5) * 30;
        return clonic + noise;
      });
      risk = 0.95 - (clonicT / 20.0) * 0.1;
      state = 'clonic_phase';
    } else {
      // Post-ictal suppression with slow recovery
      final postT = t - 35.0;
      final recovery = math.min(1.0, postT / 30.0);

      channels = List.generate(numChannels, (ch) {
        final slow = 50.0 * recovery * math.sin(2 * math.pi * 1 * t);
        final noise = (_random.nextDouble() - 0.5) * 15 * recovery;
        return slow + noise;
      });
      risk = 0.6 - recovery * 0.4;
      state = 'post_ictal';
    }

    return {'channels': channels, 'risk': risk, 'state': state};
  }

  /// Generate focal seizure pattern
  Map<String, dynamic> _generateFocalSeizure() {
    final t = _simulationTime;

    // Seizure in right hemisphere (channels 0-3) from 5-20 seconds
    final inSeizure = t >= 5.0 && t < 20.0;

    final channels = List.generate(numChannels, (ch) {
      if (inSeizure && ch < 4) {
        // Affected channels - rhythmic spikes
        final focal = 120.0 * math.sin(2 * math.pi * 10 * t) +
            60.0 * math.sin(2 * math.pi * 20 * t) +
            (_random.nextDouble() - 0.5) * 40;
        return focal;
      } else {
        // Normal channels
        final normal = 30.0 * math.sin(2 * math.pi * 10 * t) +
            (_random.nextDouble() - 0.5) * 15;
        return normal;
      }
    });

    return {
      'channels': channels,
      'risk': inSeizure ? 0.75 + _random.nextDouble() * 0.1 : 0.15,
      'state': inSeizure ? 'focal_seizure' : 'normal',
    };
  }

  /// Generate myoclonic jerks
  Map<String, dynamic> _generateMyoclonicJerks() {
    final t = _simulationTime;

    // Random jerks every 2-4 seconds
    final jerkPattern = (t * 0.4).floor();
    final jerkTime = t - jerkPattern / 0.4;
    final inJerk = jerkTime < 0.1; // 100ms jerk

    if (inJerk) {
      final spikeAmplitude = 250.0 + _random.nextDouble() * 100;
      final channels = List.generate(numChannels, (ch) {
        final spike = spikeAmplitude *
            math.exp(-jerkTime * 20) *
            math.sin(2 * math.pi * 40 * jerkTime);
        return spike;
      });

      return {
        'channels': channels,
        'risk': 0.7 + _random.nextDouble() * 0.15,
        'state': 'myoclonic_jerk',
      };
    } else {
      return {
        'channels': _generateNormalEEG(),
        'risk': 0.2 + _random.nextDouble() * 0.1,
        'state': 'normal',
      };
    }
  }

  /// Generate progressive deterioration
  Map<String, dynamic> _generateProgressiveDeterioration() {
    final t = _simulationTime;
    final progress =
        math.min(1.0, t / 30.0); // Full progression over 30 seconds

    final normalWeight = 1.0 - 0.8 * progress;
    final abnormalWeight = 0.8 * progress;

    final channels = List.generate(numChannels, (ch) {
      // Normal component
      final normal = 30.0 * math.sin(2 * math.pi * 10 * t) +
          15.0 * math.sin(2 * math.pi * 20 * t);

      // Abnormal component (spike-wave like)
      final abnormal = 150.0 * math.sin(2 * math.pi * 3 * t) +
          75.0 * math.sin(2 * math.pi * 6 * t);

      final noise = (_random.nextDouble() - 0.5) * 20;
      return normal * normalWeight + abnormal * abnormalWeight + noise;
    });

    String state;
    if (progress < 0.3) {
      state = 'normal';
    } else if (progress < 0.5) {
      state = 'mild_abnormal';
    } else if (progress < 0.7) {
      state = 'moderate_abnormal';
    } else {
      state = 'severe_abnormal';
    }

    return {
      'channels': channels,
      'risk': 0.1 + progress * 0.8,
      'state': state,
    };
  }

  /// Generate burst-suppression pattern
  Map<String, dynamic> _generateBurstSuppression() {
    final t = _simulationTime;

    // Alternating 2s burst, 3s suppression
    final cycleTime = t % 5.0;
    final inBurst = cycleTime < 2.0;

    if (inBurst) {
      // High amplitude polyspike burst
      final channels = List.generate(numChannels, (ch) {
        final burst = 150.0 * math.sin(2 * math.pi * 8 * t) +
            100.0 * math.sin(2 * math.pi * 15 * t) +
            (_random.nextDouble() - 0.5) * 60;
        // Envelope
        final envelope = math.sin(math.pi * cycleTime / 2.0);
        return burst * envelope;
      });

      return {
        'channels': channels,
        'risk': 0.8 + _random.nextDouble() * 0.1,
        'state': 'burst',
      };
    } else {
      // Suppression - very low amplitude
      final channels = List.generate(numChannels, (_) {
        return (_random.nextDouble() - 0.5) * 10;
      });

      return {
        'channels': channels,
        'risk': 0.5 + _random.nextDouble() * 0.1,
        'state': 'suppression',
      };
    }
  }

  /// Generate status epilepticus (continuous seizure)
  Map<String, dynamic> _generateStatusEpilepticus() {
    final t = _simulationTime;

    // Evolving frequency (starts at 8 Hz, slows to 3 Hz over 30 seconds)
    final progress = math.min(1.0, t / 30.0);
    final freq = 8.0 - 5.0 * progress;
    final amplitudeMod = 1.0 + 0.3 * math.sin(2 * math.pi * 0.05 * t);

    final channels = List.generate(numChannels, (ch) {
      final seizure =
          180.0 * amplitudeMod * math.sin(2 * math.pi * freq * t + ch * 0.3) +
              90.0 * math.sin(2 * math.pi * freq * 2 * t + ch * 0.3) +
              (_random.nextDouble() - 0.5) * 30;
      return seizure;
    });

    return {
      'channels': channels,
      'risk': 0.95 + _random.nextDouble() * 0.04,
      'state': 'status_epilepticus',
    };
  }

  /// Generate mixed abnormalities
  Map<String, dynamic> _generateMixedAbnormalities() {
    final t = _simulationTime;

    // Cycle through different patterns
    final cycleTime = t % 30.0;

    if (cycleTime < 8.0) {
      return {
        'channels': _generateNormalEEG(),
        'risk': 0.15 + _random.nextDouble() * 0.1,
        'state': 'normal',
      };
    } else if (cycleTime < 15.0) {
      // Absence-like
      final channels = List.generate(numChannels, (ch) {
        return 180.0 * math.sin(2 * math.pi * 3.0 * t) +
            60.0 * math.sin(2 * math.pi * 6.0 * t) +
            (_random.nextDouble() - 0.5) * 20;
      });
      return {
        'channels': channels,
        'risk': 0.8 + _random.nextDouble() * 0.1,
        'state': 'spike_wave',
      };
    } else if (cycleTime < 22.0) {
      return {
        'channels': _generateNormalEEG(),
        'risk': 0.2 + _random.nextDouble() * 0.1,
        'state': 'normal',
      };
    } else {
      // Focal-like
      final channels = List.generate(numChannels, (ch) {
        if (ch < 4) {
          return 120.0 * math.sin(2 * math.pi * 10 * t) +
              60.0 * math.sin(2 * math.pi * 20 * t) +
              (_random.nextDouble() - 0.5) * 30;
        }
        return 30.0 * math.sin(2 * math.pi * 10 * t) +
            (_random.nextDouble() - 0.5) * 15;
      });
      return {
        'channels': channels,
        'risk': 0.75 + _random.nextDouble() * 0.1,
        'state': 'focal_seizure',
      };
    }
  }

  @override
  void dispose() {
    stopSimulation();
    _dataStreamController.close();
    _predictionController.close();
    super.dispose();
  }
}
