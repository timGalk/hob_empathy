"""
Prediction Service - Loads XGBoost model and performs inference
"""
import numpy as np
import joblib
import os
from typing import Dict, List, Tuple
from scipy.signal import welch
from scipy.stats import entropy
from ..models.schemas import EEGFeatures, PredictionResponse
from datetime import datetime

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../../prediction_engine")
MODEL_PATH = os.path.join(MODEL_DIR, "absence_detector_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "absence_detector_scaler.pkl")
MODEL_VERSION = "v1.0-xgboost-500"


class PredictionService:
    """Singleton service for model inference"""

    _instance = None
    _model = None
    _scaler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Load XGBoost model and scaler from disk"""
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
                self._model = joblib.load(MODEL_PATH)
                self._scaler = joblib.load(SCALER_PATH)
                print(f"✓ Loaded prediction model from {MODEL_PATH}")
                print(f"✓ Loaded scaler from {SCALER_PATH}")
            else:
                print(f"⚠ Model files not found at {MODEL_DIR}")
                print("  Run prediction_engine/main.py to train the model first")
                self._model = None
                self._scaler = None
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            self._model = None
            self._scaler = None

    def predict_from_features(self, features: EEGFeatures) -> PredictionResponse:
        """
        Predict absence event probability from extracted features

        Args:
            features: EEGFeatures object with delta, theta, alpha, beta power, entropy, mobility, complexity

        Returns:
            PredictionResponse with risk score (0.0-1.0) and state classification
        """
        if self._model is None or self._scaler is None:
            # Return default prediction if model not loaded
            return PredictionResponse(
                risk=0.0,
                state="unknown",
                model_version="none",
                timestamp=datetime.utcnow().isoformat()
            )

        # Convert features to numpy array (match the order expected by model)
        # The edge processor sends: delta, theta, alpha, beta, entropy, mobility, complexity
        # We need to match the feature order from the training script
        feature_vector = np.array([
            features.delta_power,
            features.theta_power,
            features.alpha_power,
            features.beta_power,
            features.entropy,
            features.mobility or 0.0,
            features.complexity or 0.0
        ]).reshape(1, -1)

        # Scale features
        feature_vector_scaled = self._scaler.transform(feature_vector)

        # Get probability prediction (0=Normal, 1=Absence)
        proba = self._model.predict_proba(feature_vector_scaled)[0]
        risk_score = float(proba[1])  # Probability of class 1 (Absence)

        # Classify state based on risk
        if risk_score < 0.3:
            state = "normal"
        elif risk_score < 0.6:
            state = "mild"
        else:
            state = "elevated"

        return PredictionResponse(
            risk=round(risk_score, 4),
            state=state,
            model_version=MODEL_VERSION,
            timestamp=datetime.utcnow().isoformat()
        )

    def batch_predict(self, feature_list: List[EEGFeatures]) -> List[PredictionResponse]:
        """
        Batch prediction for multiple feature sets

        Args:
            feature_list: List of EEGFeatures objects

        Returns:
            List of PredictionResponse objects
        """
        return [self.predict_from_features(feat) for feat in feature_list]

    def is_model_loaded(self) -> bool:
        """Check if model is successfully loaded"""
        return self._model is not None and self._scaler is not None

    def get_model_info(self) -> Dict:
        """Get model metadata"""
        return {
            "version": MODEL_VERSION,
            "loaded": self.is_model_loaded(),
            "model_path": MODEL_PATH,
            "scaler_path": SCALER_PATH,
            "model_type": "XGBoost Classifier" if self._model else None,
            "n_features": 7  # delta, theta, alpha, beta, entropy, mobility, complexity
        }


# Global singleton instance
prediction_service = PredictionService()
