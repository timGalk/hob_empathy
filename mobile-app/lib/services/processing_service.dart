import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/foundation.dart';
import '../models/eeg_data.dart';

/// Service for processing EEG signals and extracting features
class ProcessingService extends ChangeNotifier {
  final int _samplingRate = 250; // Hz
  final int _windowSize = 2; // seconds
  late final int _samplesPerWindow;

  final List<EEGSample> _buffer = [];
  final StreamController<EEGFeatures> _featuresStreamController =
      StreamController<EEGFeatures>.broadcast();

  Stream<EEGFeatures> get featuresStream => _featuresStreamController.stream;

  ProcessingService() {
    _samplesPerWindow = _samplingRate * _windowSize;
  }

  /// Add sample to buffer and process when window is full
  void processSample(EEGSample sample) {
    _buffer.add(sample);

    if (_buffer.length >= _samplesPerWindow) {
      final windowData = _buffer.sublist(0, _samplesPerWindow);
      _buffer.removeRange(0, _samplesPerWindow);

      final features = _extractFeatures(windowData);
      _featuresStreamController.add(features);
    }
  }

  /// Extract features from a window of EEG data
  EEGFeatures _extractFeatures(List<EEGSample> window) {
    // Average across all channels
    List<double> avgSignal = [];
    for (var sample in window) {
      double avg = sample.channels.reduce((a, b) => a + b) / sample.channels.length;
      avgSignal.add(avg);
    }

    // Apply filtering (simplified - in production use proper DSP)
    final filtered = _bandpassFilter(avgSignal, _samplingRate, 1.0, 40.0);

    // Compute PSD using simplified method
    final psd = _computePSD(filtered, _samplingRate);

    // Extract bandpower
    final deltaPower = _bandpower(psd, 1, 4);
    final thetaPower = _bandpower(psd, 4, 8);
    final alphaPower = _bandpower(psd, 8, 13);
    final betaPower = _bandpower(psd, 13, 30);

    // Spectral entropy
    final entropy = _spectralEntropy(psd);

    // Hjorth parameters
    final hjorth = _hjorthParameters(filtered);

    // Variance
    final variance = _variance(filtered);

    return EEGFeatures(
      deltaPower: deltaPower,
      thetaPower: thetaPower,
      alphaPower: alphaPower,
      betaPower: betaPower,
      entropy: entropy,
      mobility: hjorth['mobility']!,
      complexity: hjorth['complexity']!,
      variance: variance,
    );
  }

  /// Simplified bandpass filter (IIR approximation)
  List<double> _bandpassFilter(List<double> signal, int fs, double lowcut, double highcut) {
    // Simplified filtering - in production use proper DSP library
    // This is a basic implementation for demonstration
    return signal; // TODO: Implement proper filtering
  }

  /// Compute Power Spectral Density (simplified)
  List<double> _computePSD(List<double> signal, int fs) {
    // Simplified PSD computation
    // In production, use FFT library (fftea package)
    final n = signal.length;
    final psd = List<double>.filled(n ~/ 2, 0.0);

    for (int k = 0; k < n ~/ 2; k++) {
      double real = 0.0;
      double imag = 0.0;

      for (int i = 0; i < n; i++) {
        final angle = -2 * math.pi * k * i / n;
        real += signal[i] * math.cos(angle);
        imag += signal[i] * math.sin(angle);
      }

      psd[k] = (real * real + imag * imag) / n;
    }

    return psd;
  }

  /// Calculate bandpower in frequency range
  double _bandpower(List<double> psd, double lowFreq, double highFreq) {
    final freqResolution = _samplingRate / (psd.length * 2);
    final lowIdx = (lowFreq / freqResolution).floor();
    final highIdx = (highFreq / freqResolution).ceil();

    double power = 0.0;
    for (int i = lowIdx; i < highIdx && i < psd.length; i++) {
      power += psd[i];
    }

    return power / (highIdx - lowIdx);
  }

  /// Calculate spectral entropy
  double _spectralEntropy(List<double> psd) {
    final total = psd.reduce((a, b) => a + b);
    if (total == 0) return 0.0;

    double entropy = 0.0;
    for (var p in psd) {
      final prob = p / total;
      if (prob > 0) {
        entropy -= prob * math.log(prob);
      }
    }

    return entropy;
  }

  /// Calculate Hjorth parameters
  Map<String, double> _hjorthParameters(List<double> signal) {
    // First derivative
    final firstDeriv = <double>[];
    for (int i = 1; i < signal.length; i++) {
      firstDeriv.add(signal[i] - signal[i - 1]);
    }

    // Second derivative
    final secondDeriv = <double>[];
    for (int i = 1; i < firstDeriv.length; i++) {
      secondDeriv.add(firstDeriv[i] - firstDeriv[i - 1]);
    }

    final varSignal = _variance(signal);
    final varFirst = _variance(firstDeriv);
    final varSecond = _variance(secondDeriv);

    final mobility = varSignal > 0 ? math.sqrt(varFirst / varSignal) : 0.0;
    final complexity = (varFirst > 0 && mobility > 0)
        ? (math.sqrt(varSecond / varFirst) / mobility)
        : 0.0;

    return {
      'mobility': mobility,
      'complexity': complexity,
    };
  }

  /// Calculate variance
  double _variance(List<double> signal) {
    if (signal.isEmpty) return 0.0;

    final mean = signal.reduce((a, b) => a + b) / signal.length;
    double variance = 0.0;

    for (var value in signal) {
      variance += (value - mean) * (value - mean);
    }

    return variance / signal.length;
  }

  @override
  void dispose() {
    _featuresStreamController.close();
    super.dispose();
  }
}
