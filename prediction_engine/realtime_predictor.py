"""
Enhanced Real-Time EEG Prediction Engine

Combines:
1. XGBoost ML model for absence seizure detection
2. Real-time anomaly detector for immediate alerts
3. Streaming data processing with sliding windows

Usage:
    python realtime_predictor.py --csv <path_to_eeg_csv>
    python realtime_predictor.py --stream  # For live simulation
"""

import numpy as np
import pandas as pd
import joblib
import argparse
import time
import sys
import os
from scipy.signal import welch
from scipy.stats import entropy
from xgboost import XGBClassifier
from typing import Dict, List, Tuple
from collections import deque

# Import real-time detector
from realtime_detector import StreamingAnomalyDetector, AnomalyLevel


class EnhancedRealtimePredictor:
    """
    Enhanced predictor combining ML model and rule-based anomaly detection
    """

    def __init__(self, model_path: str = "absence_detector_model.pkl",
                 scaler_path: str = "absence_detector_scaler.pkl"):
        """
        Initialize enhanced predictor

        Args:
            model_path: Path to trained XGBoost model
            scaler_path: Path to trained scaler
        """
        self.window_size = 256
        self.fs = 250

        # Load ML model
        self.model_loaded = False
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.model_loaded = True
                print(f"✓ Loaded ML model from {model_path}")
            except Exception as e:
                print(f"⚠ Could not load ML model: {e}")
                print("  Continuing with rule-based detection only")
        else:
            print(f"⚠ Model files not found")
            print("  Continuing with rule-based detection only")

        # Initialize real-time anomaly detector
        self.anomaly_detector = StreamingAnomalyDetector(
            sampling_rate=self.fs,
            window_size=self.window_size,
            overlap=0.5
        )

        # Prediction history
        self.prediction_history = deque(maxlen=100)
        self.ml_predictions = deque(maxlen=100)

        # EEG channel names
        self.eeg_cols = ["F4", "C4", "P4", "O2", "O1", "F3", "C3", "P3"]
        self.acc_cols = ["AccZ", "AccY", "AccX"]

    def extract_features(self, eeg_win: np.ndarray, acc_win: np.ndarray) -> np.ndarray:
        """
        Extract features for ML model prediction

        Args:
            eeg_win: EEG window of shape (samples, channels)
            acc_win: Accelerometer window of shape (samples, 3)

        Returns:
            Feature vector
        """
        feats = []

        for ch in range(eeg_win.shape[1]):
            x = eeg_win[:, ch]

            # Time domain features
            feats += [x.mean(), x.std(), np.var(x), np.sum(x**2)]

            # Frequency domain features
            feats += self._bandpower(x)
            feats.append(self._spectral_entropy(x))

            # Hjorth parameters
            feats += self._hjorth_params(x)

        # Accelerometer features
        for ch in range(acc_win.shape[1]):
            x = acc_win[:, ch]
            feats += [x.mean(), x.std(), np.var(x)]

        return np.array(feats)

    def _bandpower(self, x: np.ndarray) -> List[float]:
        """Compute band power for delta, theta, alpha, beta, gamma"""
        bands = {
            "delta": (0.5, 4),
            "theta": (4, 8),
            "alpha": (8, 12),
            "beta": (12, 30),
            "gamma": (30, 45),
        }
        freqs, psd = welch(x, fs=self.fs, nperseg=256)
        return [np.trapz(psd[(freqs >= low) & (freqs <= high)],
                        freqs[(freqs >= low) & (freqs <= high)])
                for low, high in bands.values()]

    def _spectral_entropy(self, x: np.ndarray) -> float:
        """Compute spectral entropy"""
        freqs, psd = welch(x, fs=self.fs, nperseg=256)
        psd_norm = psd / np.sum(psd)
        return entropy(psd_norm)

    def _hjorth_params(self, x: np.ndarray) -> List[float]:
        """Compute Hjorth parameters"""
        dx = np.diff(x)
        ddx = np.diff(dx)

        var_x = np.var(x)
        var_dx = np.var(dx)
        var_ddx = np.var(ddx)

        activity = var_x
        mobility = np.sqrt(var_dx / var_x) if var_x > 0 else 0
        complexity = (np.sqrt(var_ddx / var_dx) / mobility) if var_dx > 0 and mobility > 0 else 0

        return [activity, mobility, complexity]

    def predict_window(self, eeg_win: np.ndarray, acc_win: np.ndarray,
                      timestamp: float) -> Dict:
        """
        Make prediction for a single window combining ML and rule-based detection

        Args:
            eeg_win: EEG window of shape (samples, channels)
            acc_win: Accelerometer window of shape (samples, 3)
            timestamp: Timestamp of the window

        Returns:
            Dictionary with prediction results
        """
        result = {
            'timestamp': timestamp,
            'ml_prediction': None,
            'ml_probability': None,
            'anomaly_report': None,
            'combined_risk': 0.0,
            'alert_level': 'normal'
        }

        # 1. ML Model Prediction (if available)
        if self.model_loaded:
            try:
                features = self.extract_features(eeg_win, acc_win)
                features_scaled = self.scaler.transform(features.reshape(1, -1))

                # Get prediction and probability
                prediction = self.model.predict(features_scaled)[0]
                probability = self.model.predict_proba(features_scaled)[0][1]

                result['ml_prediction'] = int(prediction)
                result['ml_probability'] = float(probability)

                self.ml_predictions.append(probability)
            except Exception as e:
                print(f"⚠ ML prediction error: {e}")

        # 2. Rule-based Anomaly Detection
        # Process sample by sample for real-time detection
        for i in range(eeg_win.shape[0]):
            sample = eeg_win[i, :]
            anomaly_report = self.anomaly_detector.add_sample(sample, timestamp + i/self.fs)

        # Get the last report
        if self.anomaly_detector.recent_anomalies:
            result['anomaly_report'] = self.anomaly_detector.recent_anomalies[-1]

        # 3. Combine predictions
        ml_risk = result['ml_probability'] if result['ml_probability'] is not None else 0.0
        anomaly_confidence = result['anomaly_report'].confidence if result['anomaly_report'] else 0.0
        anomaly_level = result['anomaly_report'].level if result['anomaly_report'] else AnomalyLevel.NORMAL

        # Combined risk score (weighted average)
        ml_weight = 0.6
        anomaly_weight = 0.4
        result['combined_risk'] = ml_weight * ml_risk + anomaly_weight * anomaly_confidence

        # Determine alert level
        if anomaly_level == AnomalyLevel.SEVERE or result['combined_risk'] > 0.8:
            result['alert_level'] = 'severe'
        elif anomaly_level == AnomalyLevel.MODERATE or result['combined_risk'] > 0.6:
            result['alert_level'] = 'moderate'
        elif anomaly_level == AnomalyLevel.MILD or result['combined_risk'] > 0.4:
            result['alert_level'] = 'mild'
        else:
            result['alert_level'] = 'normal'

        self.prediction_history.append(result)

        return result

    def process_csv(self, csv_path: str, realtime_mode: bool = True,
                   display_interval: int = 5):
        """
        Process EEG data from CSV file

        Args:
            csv_path: Path to CSV file
            realtime_mode: If True, simulate real-time processing with delays
            display_interval: Show summary every N windows
        """
        print(f"\n{'='*80}")
        print(f"Processing: {csv_path}")
        print(f"{'='*80}\n")

        # Load CSV
        df = pd.read_csv(csv_path, comment="#")

        # Check required columns
        required_cols = self.eeg_cols + self.acc_cols
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"⚠ Missing columns: {missing_cols}")
            return

        # Extract data
        eeg_data = df[self.eeg_cols].values
        acc_data = df[self.acc_cols].values

        # Calibrate anomaly detector with first few windows
        print("Calibrating anomaly detector with initial data...")
        calibration_windows = []
        for i in range(min(5, len(df) // self.window_size)):
            start = i * self.window_size
            end = start + self.window_size
            calibration_windows.append(eeg_data[start:end])
        self.anomaly_detector.detector.calibrate(calibration_windows)
        print("✓ Calibration complete\n")

        # Process windows
        n_windows = (len(df) - self.window_size) // (self.window_size // 2) + 1
        print(f"Processing {n_windows} windows...")
        print(f"{'Window':<10} {'Time(s)':<10} {'ML Prob':<12} {'Anomaly':<20} {'Combined':<12} {'Alert':<10}")
        print("-" * 80)

        window_count = 0
        hop_size = self.window_size // 2  # 50% overlap

        for start in range(0, len(df) - self.window_size, hop_size):
            end = start + self.window_size

            eeg_win = eeg_data[start:end]
            acc_win = acc_data[start:end]
            timestamp = start / self.fs

            # Make prediction
            result = self.predict_window(eeg_win, acc_win, timestamp)

            window_count += 1

            # Display result
            if window_count % display_interval == 0 or result['alert_level'] in ['severe', 'moderate']:
                ml_prob_str = f"{result['ml_probability']:.3f}" if result['ml_probability'] is not None else "N/A"

                anomaly_str = "Normal"
                if result['anomaly_report']:
                    if result['anomaly_report'].anomaly_types:
                        anomaly_str = result['anomaly_report'].anomaly_types[0][:18]

                alert_icon = {
                    'normal': '✓',
                    'mild': '⚠',
                    'moderate': '⚠⚠',
                    'severe': '🚨'
                }.get(result['alert_level'], '')

                print(f"{window_count:<10} {timestamp:<10.2f} {ml_prob_str:<12} "
                      f"{anomaly_str:<20} {result['combined_risk']:<12.3f} "
                      f"{alert_icon} {result['alert_level']:<10}")

            # Simulate real-time processing
            if realtime_mode:
                time.sleep(0.1)

        # Summary
        self._print_summary()

    def _print_summary(self):
        """Print processing summary"""
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")

        if not self.prediction_history:
            print("No predictions made")
            return

        total = len(self.prediction_history)
        alert_counts = {
            'normal': 0,
            'mild': 0,
            'moderate': 0,
            'severe': 0
        }

        for pred in self.prediction_history:
            alert_counts[pred['alert_level']] += 1

        print(f"Total windows analyzed: {total}")
        print(f"  Normal: {alert_counts['normal']} ({alert_counts['normal']/total*100:.1f}%)")
        print(f"  Mild alerts: {alert_counts['mild']} ({alert_counts['mild']/total*100:.1f}%)")
        print(f"  Moderate alerts: {alert_counts['moderate']} ({alert_counts['moderate']/total*100:.1f}%)")
        print(f"  Severe alerts: {alert_counts['severe']} ({alert_counts['severe']/total*100:.1f}%)")

        if self.ml_predictions:
            avg_ml_prob = np.mean(list(self.ml_predictions))
            print(f"\nAverage ML absence probability: {avg_ml_prob:.3f}")

        anomaly_stats = self.anomaly_detector.get_recent_statistics()
        print(f"Anomaly detection rate: {anomaly_stats.get('anomaly_rate', 0)*100:.1f}%")


def main():
    parser = argparse.ArgumentParser(description='Enhanced Real-Time EEG Predictor')
    parser.add_argument('--csv', type=str, help='Path to EEG CSV file')
    parser.add_argument('--stream', action='store_true', help='Run live simulation mode')
    parser.add_argument('--model', type=str, default='absence_detector_model.pkl',
                       help='Path to ML model')
    parser.add_argument('--scaler', type=str, default='absence_detector_scaler.pkl',
                       help='Path to scaler')
    parser.add_argument('--realtime', action='store_true',
                       help='Simulate real-time processing with delays')

    args = parser.parse_args()

    # Create predictor
    predictor = EnhancedRealtimePredictor(
        model_path=args.model,
        scaler_path=args.scaler
    )

    if args.csv:
        # Process CSV file
        predictor.process_csv(args.csv, realtime_mode=args.realtime)

    elif args.stream:
        # Run live simulation
        print("Live simulation mode not yet implemented")
        print("Use: python realtime_predictor.py --csv <path_to_csv>")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
