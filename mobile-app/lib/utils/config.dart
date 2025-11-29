/// Application configuration
class Config {
  // Backend URLs
  static const String backendUrl = String.fromEnvironment(
    'BACKEND_URL',
    defaultValue: 'http://10.0.2.2:8000', // Android emulator localhost
  );

  static const String wsUrl = String.fromEnvironment(
    'WS_URL',
    defaultValue: 'ws://10.0.2.2:8000',
  );

  // Patient configuration
  static const String patientId = String.fromEnvironment(
    'PATIENT_ID',
    defaultValue: 'patient_001',
  );

  // EEG configuration
  static const int samplingRate = 250; // Hz
  static const int numChannels = 8;
  static const double windowSize = 2.0; // seconds

  // Filter settings
  static const double bandpassLow = 1.0; // Hz
  static const double bandpassHigh = 40.0; // Hz
  static const double notchFreq = 50.0; // Hz (50 EU / 60 US)

  // UI settings
  static const int maxChartPoints = 500;
  static const Duration updateInterval = Duration(milliseconds: 100);
}
