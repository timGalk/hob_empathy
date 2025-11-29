"""
Prediction Engine for dementia episode risk assessment
"""
import numpy as np
from typing import Dict
import joblib
import os

class DementiaPredictor:
    def __init__(self, model_path: str = None):
        self.model = None
        self.model_version = "0.1.0"

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            # Use rule-based thresholding for MVP
            print("Using rule-based prediction (no trained model loaded)")

    def load_model(self, model_path: str):
        """Load trained ML model"""
        try:
            self.model = joblib.load(model_path)
            print(f"Model loaded from {model_path}")
        except Exception as e:
            print(f"Failed to load model: {e}")

    def predict(self, features: Dict[str, float]) -> Dict:
        """
        Predict dementia episode risk from EEG features

        Args:
            features: Dictionary of extracted EEG features

        Returns:
            Dictionary with risk score and state
        """
        if self.model is not None:
            # Use trained model
            risk = self._predict_with_model(features)
        else:
            # Use rule-based heuristic
            risk = self._predict_rule_based(features)

        # Determine state based on risk level
        state = self._classify_state(risk)

        return {
            "risk": float(risk),
            "state": state,
            "model_version": self.model_version
        }

    def _predict_with_model(self, features: Dict[str, float]) -> float:
        """Predict using trained ML model"""
        # Convert features to model input format
        feature_vector = self._features_to_vector(features)

        # Get prediction
        risk = self.model.predict_proba([feature_vector])[0][1]

        return risk

    def _predict_rule_based(self, features: Dict[str, float]) -> float:
        """
        Rule-based prediction for MVP
        Based on research indicating:
        - Increased theta/alpha ratio in dementia
        - Decreased beta power
        - Increased delta power
        - Lower spectral entropy
        """
        risk_score = 0.0

        # Theta/Alpha ratio (higher = more risk)
        theta_alpha_ratio = features.get('theta_power', 0) / max(features.get('alpha_power', 1), 0.001)
        if theta_alpha_ratio > 1.5:
            risk_score += 0.3

        # Low beta power (agitation indicator)
        if features.get('beta_power', 0) < 0.05:
            risk_score += 0.2

        # High delta power (drowsiness/confusion)
        if features.get('delta_power', 0) > 0.15:
            risk_score += 0.2

        # Low entropy (reduced cognitive complexity)
        if features.get('entropy', 1.0) < 0.5:
            risk_score += 0.15

        # High variance (signal instability)
        if features.get('variance', 0) > 100:
            risk_score += 0.15

        # Clip to [0, 1]
        risk_score = np.clip(risk_score, 0.0, 1.0)

        return risk_score

    def _classify_state(self, risk: float) -> str:
        """
        Classify risk into categorical state

        Risk levels:
        - 0.0-0.3: normal
        - 0.3-0.6: mild agitation
        - 0.6-1.0: elevated (high frustration episode risk)
        """
        if risk < 0.3:
            return "normal"
        elif risk < 0.6:
            return "mild"
        else:
            return "elevated"

    def _features_to_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dictionary to numpy array"""
        # Define feature order for model
        feature_names = [
            'delta_power', 'theta_power', 'alpha_power', 'beta_power',
            'entropy', 'mobility', 'complexity', 'variance'
        ]

        vector = np.array([features.get(name, 0.0) for name in feature_names])
        return vector

if __name__ == "__main__":
    # Demo usage
    predictor = DementiaPredictor()

    # Test features
    test_features = {
        'alpha_power': 0.12,
        'beta_power': 0.08,
        'theta_power': 0.15,
        'delta_power': 0.10,
        'entropy': 1.43,
        'mobility': 0.91,
        'complexity': 1.2,
        'variance': 45.3
    }

    result = predictor.predict(test_features)
    print(f"Prediction: {result}")
