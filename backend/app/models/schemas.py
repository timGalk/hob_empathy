"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class EEGFeatures(BaseModel):
    """Extracted EEG features from edge device"""
    alpha_power: float
    beta_power: float
    theta_power: float
    delta_power: float
    entropy: float
    mobility: Optional[float] = None
    complexity: Optional[float] = None

class FeaturePayload(BaseModel):
    """Payload from edge preprocessing layer"""
    patient_id: str
    window_start: str  # ISO timestamp
    features: EEGFeatures

class PredictionResponse(BaseModel):
    """Model prediction output"""
    risk: float  # 0.0 to 1.0
    state: str  # normal, mild, elevated
    model_version: str
    timestamp: str

class PatientState(BaseModel):
    """Current patient state"""
    patient_id: str
    risk: float
    state: str
    timestamp: str

class Alert(BaseModel):
    """Alert model"""
    id: Optional[int] = None
    patient_id: str
    timestamp: str
    alert_type: str
    message: str
    severity: str  # low, medium, high
