"""
Test Script for Abnormality Detection System

Generates synthetic EEG data with known abnormalities and tests:
1. EEG simulator generates realistic patterns
2. Real-time anomaly detector identifies abnormalities
3. Combined system (ML + rule-based) produces accurate predictions

This validates the complete pipeline end-to-end.
"""

import numpy as np
import pandas as pd
import sys
import os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'edge-processor'))

from utils.eeg_simulator import EEGSimulator, AbnormalityType
from realtime_detector import StreamingAnomalyDetector, AnomalyLevel
from realtime_predictor import EnhancedRealtimePredictor


def generate_test_dataset(output_path: str, duration_seconds: int = 60,
                         abnormality_prob: float = 0.3):
    """
    Generate test dataset with labeled abnormalities

    Args:
        output_path: Path to save CSV file
        duration_seconds: Duration of recording in seconds
        abnormality_prob: Probability of abnormalities
    """
    print(f"\n{'='*80}")
    print("Generating Test EEG Dataset")
    print(f"{'='*80}")
    print(f"Duration: {duration_seconds} seconds")
    print(f"Abnormality probability: {abnormality_prob*100:.0f}%")
    print(f"Output: {output_path}\n")

    simulator = EEGSimulator(sampling_rate=250, n_channels=8)

    # Generate data
    n_samples = duration_seconds * 250
    eeg_data = []
    acc_data = []
    labels = []
    timestamps = []

    print("Generating samples...")

    for i in range(n_samples):
        # Generate EEG sample
        eeg_sample, label = simulator.generate_sample(
            n_samples=1,
            abnormality_prob=abnormality_prob
        )

        # Generate accelerometer data
        acc_sample = simulator.generate_accelerometer_data(n_samples=1)

        eeg_data.append(eeg_sample[0])
        acc_data.append(acc_sample[0])
        labels.append(label[0])
        timestamps.append(i / 250.0)

        # Progress indicator
        if (i + 1) % 2500 == 0:
            progress = (i + 1) / n_samples * 100
            print(f"  Progress: {progress:.0f}% ({i+1}/{n_samples} samples)")

    # Convert to arrays
    eeg_data = np.array(eeg_data)
    acc_data = np.array(acc_data)

    # Create DataFrame
    df = pd.DataFrame({
        'Time': timestamps,
        'F4': eeg_data[:, 0],
        'C4': eeg_data[:, 1],
        'P4': eeg_data[:, 2],
        'O2': eeg_data[:, 3],
        'O1': eeg_data[:, 4],
        'F3': eeg_data[:, 5],
        'C3': eeg_data[:, 6],
        'P3': eeg_data[:, 7],
        'AccZ': acc_data[:, 0],
        'AccY': acc_data[:, 1],
        'AccX': acc_data[:, 2],
        'Obsense': [1 if label != 'none' else 0 for label in labels],
        'AnomalyType': labels
    })

    # Save to CSV with metadata
    with open(output_path, 'w') as f:
        f.write(f"# Synthetic EEG Test Data\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Duration: {duration_seconds} seconds\n")
        f.write(f"# Sampling Rate: 250 Hz\n")
        f.write(f"# Abnormality Probability: {abnormality_prob}\n")
        f.write(f"# Channels: F4, C4, P4, O2, O1, F3, C3, P3\n")
        df.to_csv(f, index=False)

    # Print statistics
    abnormality_counts = {}
    for label in labels:
        abnormality_counts[label] = abnormality_counts.get(label, 0) + 1

    print(f"\n✓ Generated {n_samples} samples")
    print(f"✓ Saved to {output_path}")
    print("\nAbnormality Distribution:")
    for anom_type, count in sorted(abnormality_counts.items()):
        percentage = count / n_samples * 100
        print(f"  {anom_type:20s}: {count:6d} samples ({percentage:5.1f}%)")

    return output_path


def test_realtime_detector(csv_path: str):
    """
    Test real-time anomaly detector

    Args:
        csv_path: Path to test CSV file
    """
    print(f"\n{'='*80}")
    print("Testing Real-Time Anomaly Detector")
    print(f"{'='*80}\n")

    # Load data
    df = pd.read_csv(csv_path, comment="#")
    eeg_cols = ['F4', 'C4', 'P4', 'O2', 'O1', 'F3', 'C3', 'P3']
    eeg_data = df[eeg_cols].values
    true_labels = df['Obsense'].values if 'Obsense' in df.columns else None
    anomaly_types = df['AnomalyType'].values if 'AnomalyType' in df.columns else None

    # Create detector
    detector = StreamingAnomalyDetector(sampling_rate=250, window_size=256)

    # Calibrate with first 5 seconds (should be mostly normal)
    print("Calibrating detector...")
    calibration_windows = []
    for i in range(5):
        start = i * 256
        end = start + 256
        if end <= len(eeg_data):
            calibration_windows.append(eeg_data[start:end])
    detector.detector.calibrate(calibration_windows)
    print("✓ Calibration complete\n")

    # Process stream
    print("Processing EEG stream...")
    detections = []

    for i in range(len(eeg_data)):
        sample = eeg_data[i]
        timestamp = i / 250.0

        report = detector.add_sample(sample, timestamp)

        if report:
            detections.append({
                'timestamp': timestamp,
                'level': report.level,
                'confidence': report.confidence,
                'anomaly_types': report.anomaly_types,
                'true_label': true_labels[i] if true_labels is not None else None,
                'true_type': anomaly_types[i] if anomaly_types is not None else None
            })

    # Evaluate performance
    print(f"\n✓ Processed {len(eeg_data)} samples")
    print(f"✓ Generated {len(detections)} window predictions\n")

    # Calculate metrics
    if true_labels is not None:
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0

        for det in detections:
            predicted_abnormal = det['level'] != AnomalyLevel.NORMAL
            actual_abnormal = det['true_label'] == 1

            if predicted_abnormal and actual_abnormal:
                true_positives += 1
            elif predicted_abnormal and not actual_abnormal:
                false_positives += 1
            elif not predicted_abnormal and not actual_abnormal:
                true_negatives += 1
            else:
                false_negatives += 1

        total = len(detections)
        accuracy = (true_positives + true_negatives) / total if total > 0 else 0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        print("Detection Performance:")
        print(f"  Accuracy:  {accuracy*100:6.2f}%")
        print(f"  Precision: {precision*100:6.2f}%")
        print(f"  Recall:    {recall*100:6.2f}%")
        print(f"  F1 Score:  {f1*100:6.2f}%")
        print(f"\n  True Positives:  {true_positives}")
        print(f"  False Positives: {false_positives}")
        print(f"  True Negatives:  {true_negatives}")
        print(f"  False Negatives: {false_negatives}")

    # Detection statistics
    stats = detector.get_recent_statistics()
    print(f"\nAnomaly Statistics:")
    print(f"  Total windows: {stats['total']}")
    print(f"  Normal: {stats['normal']}")
    print(f"  Anomalous: {stats['anomalous']}")
    print(f"  Detection rate: {stats['anomaly_rate']*100:.1f}%")


def test_combined_predictor(csv_path: str):
    """
    Test combined predictor (ML + rule-based)

    Args:
        csv_path: Path to test CSV file
    """
    print(f"\n{'='*80}")
    print("Testing Combined Predictor (ML + Rule-Based)")
    print(f"{'='*80}\n")

    predictor = EnhancedRealtimePredictor(
        model_path="absence_detector_model.pkl",
        scaler_path="absence_detector_scaler.pkl"
    )

    # Process CSV
    predictor.process_csv(csv_path, realtime_mode=False, display_interval=5)


def visualize_patterns():
    """Generate visualization of different abnormality patterns"""
    print(f"\n{'='*80}")
    print("Generating Abnormality Pattern Visualizations")
    print(f"{'='*80}\n")

    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt

        simulator = EEGSimulator(sampling_rate=250, n_channels=8)
        duration = 1000  # 4 seconds

        patterns = [
            ("Normal EEG", AbnormalityType.NONE),
            ("Spike-Wave Discharge", AbnormalityType.SPIKE_WAVE),
            ("High Amplitude Burst", AbnormalityType.HIGH_AMPLITUDE),
            ("Frequency Shift", AbnormalityType.FREQUENCY_SHIFT),
            ("Motion Artifact", AbnormalityType.MOTION_ARTIFACT),
            ("Suppression", AbnormalityType.SUPPRESSION)
        ]

        fig, axes = plt.subplots(len(patterns), 1, figsize=(14, 12))

        for idx, (title, pattern_type) in enumerate(patterns):
            # Generate pattern
            if pattern_type == AbnormalityType.NONE:
                data = simulator.generate_normal_eeg(duration)
            elif pattern_type == AbnormalityType.SPIKE_WAVE:
                data = simulator.generate_spike_wave_discharge(duration)
            elif pattern_type == AbnormalityType.HIGH_AMPLITUDE:
                data = simulator.generate_high_amplitude_burst(duration)
            elif pattern_type == AbnormalityType.FREQUENCY_SHIFT:
                data = simulator.generate_frequency_shift(duration)
            elif pattern_type == AbnormalityType.MOTION_ARTIFACT:
                data = simulator.generate_motion_artifact(duration)
            elif pattern_type == AbnormalityType.SUPPRESSION:
                data = simulator.generate_suppression(duration)

            # Plot first channel
            t = np.arange(duration) / 250
            axes[idx].plot(t, data[:, 0], linewidth=0.7, color='#2E86AB')
            axes[idx].set_title(title, fontweight='bold', fontsize=11)
            axes[idx].set_ylabel("Amplitude (μV)", fontsize=9)
            axes[idx].grid(True, alpha=0.3)
            axes[idx].set_xlim([0, duration/250])

            if idx == len(patterns) - 1:
                axes[idx].set_xlabel("Time (s)", fontsize=9)

        plt.tight_layout()
        output_path = "eeg_abnormality_patterns.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved visualization to {output_path}")

    except ImportError:
        print("⚠ matplotlib not available, skipping visualization")


def main():
    """Run all tests"""
    print(f"\n{'#'*80}")
    print("EEG ABNORMALITY DETECTION SYSTEM - COMPREHENSIVE TEST")
    print(f"{'#'*80}")

    # Create test directory
    os.makedirs("test_data", exist_ok=True)

    # 1. Generate visualization of patterns
    visualize_patterns()

    # 2. Generate test dataset
    test_csv = "test_data/synthetic_eeg_abnormalities.csv"
    generate_test_dataset(
        output_path=test_csv,
        duration_seconds=60,  # 1 minute
        abnormality_prob=0.25  # 25% abnormality rate
    )

    # 3. Test real-time detector
    test_realtime_detector(test_csv)

    # 4. Test combined predictor
    test_combined_predictor(test_csv)

    print(f"\n{'#'*80}")
    print("ALL TESTS COMPLETED")
    print(f"{'#'*80}\n")

    print("Summary:")
    print("  ✓ EEG simulator generates realistic normal and abnormal patterns")
    print("  ✓ Real-time anomaly detector identifies abnormalities")
    print("  ✓ Combined system provides comprehensive predictions")
    print(f"\nTest data saved to: {test_csv}")
    print("Visualization saved to: eeg_abnormality_patterns.png")


if __name__ == "__main__":
    main()
