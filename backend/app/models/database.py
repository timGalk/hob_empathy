from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Float, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="clinician")
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient_assignments = relationship("UserPatientAssignment", back_populates="user")


class UserPatientAssignment(Base):
    __tablename__ = "user_patient_assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    patient_id = Column(String(100), ForeignKey("patients.patient_id", ondelete="CASCADE"), index=True)
    assigned_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="patient_assignments")
    patient = relationship("Patient", back_populates="user_assignments")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255))
    age = Column(Integer)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_assignments = relationship("UserPatientAssignment", back_populates="patient")
    predictions = relationship("Prediction", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(100), ForeignKey("patients.patient_id", ondelete="CASCADE"), index=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    window_start = Column(TIMESTAMP, nullable=False)

    # Features
    delta_power = Column(Float)
    theta_power = Column(Float)
    alpha_power = Column(Float)
    beta_power = Column(Float)
    entropy = Column(Float)
    mobility = Column(Float)
    complexity = Column(Float)

    # Prediction results
    risk = Column(Float, nullable=False)  # 0.0 to 1.0
    state = Column(String(50), nullable=False)  # normal, mild, elevated
    model_version = Column(String(50))

    # Relationships
    patient = relationship("Patient", back_populates="predictions")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(100), ForeignKey("patients.patient_id", ondelete="CASCADE"), index=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    alert_type = Column(String(50), nullable=False)  # absence_detected, elevated_risk, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high
    message = Column(Text)
    risk_score = Column(Float)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(TIMESTAMP)
    acknowledged_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    patient = relationship("Patient", back_populates="alerts")
