"""
Test Abnormal Scenarios Against Prediction System

This script loads generated abnormal scenarios and tests them against
the real-time anomaly detector to verify they trigger predictions.
"""

import numpy as np
import pandas as pd
import sys
import os
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from realtime_detector import RealtimeAnomalyDetector, AnomalyLevel


def test_scenario(csv_path: str, detector: RealtimeAnomalyDetector) -> dict:
    """
    Test a scenario file against the detector
    
    Returns detection statistics
    """
    print(f"\n{'='*60}")
    print(f"Testing: {os.path.basename(csv_path)}")
    print(f"{'='*60}")
    
    # Load data
    df = pd.read_csv(csv_path, comment='#')
    
    eeg_cols = ['F4', 'C4', 'P4', 'O2', 'O1', 'F3', 'C3', 'P3']
    eeg_data = df[eeg_cols].values
    true_labels = df['Obsense'].values if 'Obsense' in df.columns else None
    anomaly_types = df['AnomalyType'].values if 'AnomalyType' in df.columns else None
    
    # Window-based detection
    window_size = 256
    n_windows = len(eeg_data) // window_size
    
    results = {
        'total_windows': n_windows,
        'detected_normal': 0,
        'detected_mild': 0,
        'detected_moderate': 0,
        'detected_severe': 0,
        'true_positive': 0,
        'false_positive': 0,
        'true_negative': 0,
        'false_negative': 0,
        'anomaly_types_detected': set(),
        'detections': []
    }
    
    # Reset detector calibration for fresh test
    detector.calibrated = False
    detector.baseline_buffer.clear()
    
    for i in range(n_windows):
        start_idx = i * window_size
        end_idx = start_idx + window_size
        
        window = eeg_data[start_idx:end_idx]
        timestamp = start_idx / 250.0  # Convert to seconds
        
        # Run detection
        report = detector.detect(window, timestamp)
        
        # Track detection level
        if report.level == AnomalyLevel.NORMAL:
            results['detected_normal'] += 1
        elif report.level == AnomalyLevel.MILD:
            results['detected_mild'] += 1
        elif report.level == AnomalyLevel.MODERATE:
            results['detected_moderate'] += 1
        elif report.level == AnomalyLevel.SEVERE:
            results['detected_severe'] += 1
        
        # Track anomaly types
        for atype in report.anomaly_types:
            results['anomaly_types_detected'].add(atype)
        
        # Compare with ground truth
        if true_labels is not None:
            window_labels = true_labels[start_idx:end_idx]
            has_true_abnormality = np.mean(window_labels) > 0.5
            detected_abnormality = report.level != AnomalyLevel.NORMAL
            
            if has_true_abnormality and detected_abnormality:
                results['true_positive'] += 1
            elif has_true_abnormality and not detected_abnormality:
                results['false_negative'] += 1
            elif not has_true_abnormality and detected_abnormality:
                results['false_positive'] += 1
            else:
                results['true_negative'] += 1
        
        # Log significant detections
        if report.level != AnomalyLevel.NORMAL:
            results['detections'].append({
                'time': timestamp,
                'level': report.level.name,
                'confidence': report.confidence,
                'types': report.anomaly_types,
                'details': report.details
            })
    
    # Print results
    print(f"\nDetection Summary:")
    print(f"  Total windows analyzed: {n_windows}")
    print(f"  Normal: {results['detected_normal']} ({100*results['detected_normal']/n_windows:.1f}%)")
    print(f"  Mild: {results['detected_mild']} ({100*results['detected_mild']/n_windows:.1f}%)")
    print(f"  Moderate: {results['detected_moderate']} ({100*results['detected_moderate']/n_windows:.1f}%)")
    print(f"  Severe: {results['detected_severe']} ({100*results['detected_severe']/n_windows:.1f}%)")
    
    if results['anomaly_types_detected']:
        print(f"\nAnomaly types detected: {', '.join(results['anomaly_types_detected'])}")
    
    if true_labels is not None:
        total = results['true_positive'] + results['false_positive'] + results['true_negative'] + results['false_negative']
        if total > 0:
            accuracy = (results['true_positive'] + results['true_negative']) / total
            if results['true_positive'] + results['false_positive'] > 0:
                precision = results['true_positive'] / (results['true_positive'] + results['false_positive'])
            else:
                precision = 0
            if results['true_positive'] + results['false_negative'] > 0:
                recall = results['true_positive'] / (results['true_positive'] + results['false_negative'])
            else:
                recall = 0
            
            print(f"\nClassification Metrics:")
            print(f"  Accuracy: {accuracy:.2%}")
            print(f"  Precision: {precision:.2%}")
            print(f"  Recall (Sensitivity): {recall:.2%}")
            print(f"  True Positives: {results['true_positive']}")
            print(f"  False Positives: {results['false_positive']}")
            print(f"  True Negatives: {results['true_negative']}")
            print(f"  False Negatives: {results['false_negative']}")
    
    # Show sample detections
    if results['detections']:
        print(f"\nSample Detections (first 5):")
        for det in results['detections'][:5]:
            print(f"  [{det['time']:.1f}s] {det['level']}: {det['details']} (conf: {det['confidence']:.2f})")
    
    return results


def main():
    """Test all generated scenarios"""
    
    print("=" * 80)
    print("ABNORMAL EEG SCENARIO TEST SUITE")
    print("Testing generated scenarios against real-time anomaly detector")
    print("=" * 80)
    
    # Initialize detector
    detector = RealtimeAnomalyDetector(sampling_rate=250, window_size=256)
    
    # Find scenario files
    scenario_dir = Path(__file__).parent / 'test_data' / 'abnormal_scenarios'
    
    if not scenario_dir.exists():
        print(f"\nError: Scenario directory not found: {scenario_dir}")
        print("Please run generate_abnormal_scenarios.py first:")
        print("  python generate_abnormal_scenarios.py --all")
        return
    
    scenario_files = list(scenario_dir.glob("*.csv"))
    
    if not scenario_files:
        print(f"\nNo scenario files found in {scenario_dir}")
        return
    
    print(f"\nFound {len(scenario_files)} scenario files")
    
    # Test each scenario
    all_results = {}
    
    for scenario_file in sorted(scenario_files):
        results = test_scenario(str(scenario_file), detector)
        all_results[scenario_file.stem] = results
    
    # Summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Scenario':<35} {'Windows':<10} {'Detected':<10} {'Rate':<10}")
    print("-" * 65)
    
    for scenario_name, results in all_results.items():
        total = results['total_windows']
        detected = results['detected_mild'] + results['detected_moderate'] + results['detected_severe']
        rate = detected / total * 100 if total > 0 else 0
        print(f"{scenario_name:<35} {total:<10} {detected:<10} {rate:.1f}%")
    
    # Scenarios that successfully triggered predictions
    triggered = [name for name, r in all_results.items() 
                 if (r['detected_mild'] + r['detected_moderate'] + r['detected_severe']) > 0]
    
    print(f"\n✓ Scenarios that triggered predictions: {len(triggered)}/{len(all_results)}")
    for name in triggered:
        print(f"  - {name}")
    
    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
