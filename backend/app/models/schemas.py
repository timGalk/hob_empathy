"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, List
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


# Authentication Schemas

class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    role: Optional[str] = "clinician"


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class PatientAssignment(BaseModel):
    """Patient assignment schema"""
    user_id: int
    patient_id: str


class PatientAssignmentResponse(BaseModel):
    """Patient assignment response"""
    id: int
    user_id: int
    patient_id: str
    assigned_at: datetime

    class Config:
        from_attributes = True
