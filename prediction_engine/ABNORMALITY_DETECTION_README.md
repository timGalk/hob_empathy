# EEG Abnormality Detection System - Documentation

## Overview

This enhanced EEG abnormality detection system combines machine learning and rule-based approaches to identify abnormal EEG patterns in real-time. The system can detect various types of abnormalities including:

- **Spike-wave discharges** (typical in absence seizures)
- **High amplitude bursts**
- **Frequency anomalies**
- **Motion artifacts**
- **Amplitude suppression**
- **Baseline drift**

## System Components

### 1. EEG Simulator (`edge-processor/utils/eeg_simulator.py`)

Generates realistic EEG signals with configurable abnormalities for testing and development.

**Features:**
- Normal EEG with proper frequency band distribution (delta, theta, alpha, beta, gamma)
- Inter-channel variability (frontal vs occipital differences)
- Multiple abnormality types with realistic characteristics
- Accelerometer data simulation

**Usage:**
```python
from utils.eeg_simulator import EEGSimulator, AbnormalityType

# Create simulator
simulator = EEGSimulator(sampling_rate=250, n_channels=8)

# Generate normal EEG
normal_eeg = simulator.generate_normal_eeg(duration_samples=1000)

# Generate specific abnormality
spike_wave = simulator.generate_spike_wave_discharge(duration_samples=1000)

# Generate continuous stream with random abnormalities
eeg_sample, label = simulator.generate_sample(
    n_samples=1,
    abnormality_prob=0.2  # 20% chance of abnormality
)
```

### 2. Real-Time Anomaly Detector (`prediction_engine/realtime_detector.py`)

Rule-based detector that identifies abnormalities using statistical and spectral analysis.

**Detection Methods:**
- Amplitude-based detection (high/low amplitude)
- Spike detection (sharp transients)
- Spike-wave discharge detection (3 Hz pattern)
- Frequency anomaly detection (abnormal band dominance)
- Suppression detection (flat EEG)

**Usage:**
```python
from realtime_detector import StreamingAnomalyDetector, AnomalyLevel

# Create detector
detector = StreamingAnomalyDetector(
    sampling_rate=250,
    window_size=256,
    overlap=0.5
)

# Process samples one at a time
for i in range(n_samples):
    sample = eeg_data[i]  # Shape: (8,) for 8 channels

    # Add sample and get report when window is full
    report = detector.add_sample(sample, timestamp=i/250)

    if report:
        print(f"Level: {report.level.name}")
        print(f"Confidence: {report.confidence:.2%}")
        print(f"Types: {report.anomaly_types}")
```

### 3. Enhanced Real-Time Predictor (`prediction_engine/realtime_predictor.py`)

Combines XGBoost ML model with rule-based anomaly detection for comprehensive predictions.

**Usage:**
```bash
# Process a CSV file
python realtime_predictor.py --csv path/to/eeg_recording.csv

# With real-time simulation (adds delays)
python realtime_predictor.py --csv path/to/eeg_recording.csv --realtime

# Specify custom model paths
python realtime_predictor.py --csv data.csv \
    --model custom_model.pkl \
    --scaler custom_scaler.pkl
```

**Output:**
- Window-by-window predictions
- Combined risk score (ML + rule-based)
- Alert levels: normal, mild, moderate, severe
- Summary statistics

### 4. Edge Processor with Simulation (`edge-processor/main.py`)

Modified edge processor that uses the EEG simulator for testing.

**Usage:**
```bash
cd edge-processor
python main.py
```

The processor will:
1. Generate realistic EEG data with abnormalities
2. Apply filters (bandpass, notch)
3. Extract features
4. Send to backend for prediction

**Configuration:**
Edit `main.py` to adjust:
```python
ABNORMALITY_PROBABILITY = 0.2  # Adjust probability (0.0-1.0)
```

## Testing

### Comprehensive Test Suite (`prediction_engine/test_abnormality_detection.py`)

Runs end-to-end tests of the entire system.

**Usage:**
```bash
cd prediction_engine
python test_abnormality_detection.py
```

**What it does:**
1. Generates visualization of all abnormality types
2. Creates synthetic test dataset (60 seconds of EEG data)
3. Tests real-time anomaly detector performance
4. Tests combined predictor (ML + rule-based)
5. Provides performance metrics (accuracy, precision, recall, F1)

**Output files:**
- `eeg_abnormality_patterns.png` - Visualization of each abnormality type
- `test_data/synthetic_eeg_abnormalities.csv` - Test dataset with labeled abnormalities

## CSV File Format

The system expects CSV files with the following columns:

```
Time,F4,C4,P4,O2,O1,F3,C3,P3,AccZ,AccY,AccX,Obsense
```

- **Time**: Timestamp in seconds
- **F4, C4, P4, O2, O1, F3, C3, P3**: EEG channels (microvolts)
- **AccZ, AccY, AccX**: Accelerometer data
- **Obsense**: Ground truth label (0=normal, 1=abnormal) - optional

## Abnormality Types

### 1. Spike-Wave Discharge
**Characteristics:**
- 3 Hz frequency (typical absence seizure pattern)
- High amplitude (200+ μV)
- Rhythmic spike-and-wave pattern
- Generalized across channels

**Detection:** Spectral analysis for 2.5-3.5 Hz dominance + high amplitude

### 2. High Amplitude Burst
**Characteristics:**
- Sudden amplitude increase (3-5x baseline)
- Short duration (0.5-2 seconds)
- May include high-frequency components

**Detection:** Amplitude threshold relative to baseline

### 3. Frequency Shift
**Characteristics:**
- Abnormal dominance of single frequency band
- Usually beta (12-30 Hz) or delta (0.5-4 Hz)
- Sustained pattern

**Detection:** Band power ratio compared to baseline

### 4. Motion Artifact
**Characteristics:**
- High amplitude random noise
- Multiple sharp spikes
- Broadband frequency content

**Detection:** High derivative values + amplitude spikes

### 5. Suppression
**Characteristics:**
- Very low amplitude (<5 μV RMS)
- Flat or near-flat signal
- Minimal frequency content

**Detection:** RMS amplitude below threshold

## Performance Metrics

From test run on synthetic data:

**Real-Time Detector:**
- Recall: 100% (detects all abnormalities)
- Precision: 28% (conservative, high sensitivity)
- F1 Score: 44%

**Notes:**
- High recall is intentional for medical safety (better false positive than missed abnormality)
- Precision can be tuned by adjusting thresholds in `realtime_detector.py`
- Combined with ML model for improved specificity

## Configuration and Tuning

### Adjust Detection Sensitivity

Edit `prediction_engine/realtime_detector.py`:

```python
class RealtimeAnomalyDetector:
    def __init__(self, ...):
        # Adjust these thresholds
        self.amplitude_threshold_multiplier = 4.0  # Increase for less sensitivity
        self.spike_threshold = 150.0  # microvolts
        self.suppression_threshold = 5.0  # microvolts
        self.spike_wave_power_threshold = 0.4  # Relative power
```

### Adjust Abnormality Probability in Simulation

Edit `edge-processor/main.py`:

```python
ABNORMALITY_PROBABILITY = 0.2  # 20% chance - adjust as needed
```

### Adjust Window Size and Overlap

Edit detector initialization:

```python
detector = StreamingAnomalyDetector(
    sampling_rate=250,
    window_size=256,  # Samples (1.024 seconds at 250 Hz)
    overlap=0.5  # 50% overlap between windows
)
```

## Example Workflow

### 1. Generate Test Data
```bash
cd prediction_engine
python test_abnormality_detection.py
# Creates test_data/synthetic_eeg_abnormalities.csv
```

### 2. Analyze with Real-Time Predictor
```bash
python realtime_predictor.py --csv test_data/synthetic_eeg_abnormalities.csv
```

### 3. View Visualization
```bash
# Open eeg_abnormality_patterns.png to see examples of each abnormality type
```

### 4. Run Live Simulation
```bash
cd ../edge-processor
python main.py
# Watch for abnormality alerts in real-time
```

## Integration with Existing System

The new components integrate with your existing system:

1. **Training Data**: Use `eeg_simulator.py` to generate labeled training data
2. **Edge Processing**: Modified `edge-processor/main.py` uses simulator
3. **Backend**: Existing `prediction_service.py` works with new features
4. **Real-time**: New `realtime_predictor.py` combines ML + rule-based detection

## Files Created/Modified

**New Files:**
- `edge-processor/utils/eeg_simulator.py` - EEG signal generator
- `prediction_engine/realtime_detector.py` - Rule-based anomaly detector
- `prediction_engine/realtime_predictor.py` - Enhanced predictor
- `prediction_engine/test_abnormality_detection.py` - Comprehensive test suite
- `prediction_engine/ABNORMALITY_DETECTION_README.md` - This file

**Modified Files:**
- `edge-processor/main.py` - Added realistic EEG simulation

**Generated Files:**
- `prediction_engine/eeg_abnormality_patterns.png` - Visualization
- `prediction_engine/test_data/synthetic_eeg_abnormalities.csv` - Test data

## Next Steps

1. **Train ML Model**: Generate more training data and retrain XGBoost model
   ```bash
   cd prediction_engine
   # Generate training data
   python -c "from test_abnormality_detection import generate_test_dataset; \
              generate_test_dataset('training_data.csv', 3600, 0.3)"
   # Train model
   python predictor.py
   ```

2. **Tune Thresholds**: Adjust detection thresholds based on real-world data

3. **Connect Real Hardware**: Replace simulator with actual BrainAccess device connection

4. **Deploy**: Integrate with mobile app and cloud infrastructure

## Troubleshooting

**Issue: All windows detected as abnormal**
- Solution: Increase threshold multipliers in `realtime_detector.py`
- Or: Provide more normal data for calibration

**Issue: Missing abnormalities**
- Solution: Decrease threshold multipliers
- Or: Check if window size is appropriate for abnormality duration

**Issue: ML model not found**
- Solution: Train model first using `predictor.py` with training data
- Or: System will fall back to rule-based detection only

## References

- EEG frequency bands: Delta (0.5-4 Hz), Theta (4-8 Hz), Alpha (8-12 Hz), Beta (12-30 Hz), Gamma (30-45 Hz)
- Absence seizures: Characterized by 3 Hz spike-wave discharge
- Hjorth parameters: Activity, Mobility, Complexity
- Spectral entropy: Measure of signal irregularity

## Contact

For questions or issues, refer to the main project documentation or create an issue in the repository.
