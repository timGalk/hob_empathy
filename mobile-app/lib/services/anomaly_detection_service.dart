import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/eeg_data.dart';

/// Service for detecting anomalies using the prediction engine
class AnomalyDetectionService extends ChangeNotifier {
  final StreamController<PatientState> _predictionController =
      StreamController<PatientState>.broadcast();

  Stream<PatientState> get predictionStream => _predictionController.stream;

  /// Analyze features for anomalies
  /// This method is called from home_screen when features are extracted
  /// The actual prediction happens in the backend, but this service
  /// manages the prediction state and alerts
  void analyzeFeatures(EEGFeatures features) {
    // Note: The actual prediction will be received via WebSocket
    // from the backend after features are sent via BackendService.sendFeatures()
    // This method can be used for local pre-processing or validation
    debugPrint('Features ready for analysis: delta=${features.deltaPower.toStringAsFixed(2)}');
  }

  /// Handle prediction result from backend
  void handlePrediction(PatientState prediction) {
    debugPrint('Prediction received: risk=${prediction.risk.toStringAsFixed(2)}, state=${prediction.state}');
    _predictionController.add(prediction);
    notifyListeners();
  }

  @override
  void dispose() {
    _predictionController.close();
    super.dispose();
  }
}
