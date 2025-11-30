-- PostgreSQL Schema for EEG Dementia Monitoring System

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255),
    age INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- EEG Features table
CREATE TABLE IF NOT EXISTS features (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) REFERENCES patients(patient_id),
    ts TIMESTAMP NOT NULL,
    feature_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patient_ts ON features (patient_id, ts DESC);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) REFERENCES patients(patient_id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    window_start TIMESTAMP NOT NULL,
    -- EEG Features
    delta_power FLOAT,
    theta_power FLOAT,
    alpha_power FLOAT,
    beta_power FLOAT,
    entropy FLOAT,
    mobility FLOAT,
    complexity FLOAT,
    -- Prediction results
    risk FLOAT NOT NULL,
    state VARCHAR(50) NOT NULL,
    model_version VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions (patient_id, timestamp DESC);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) REFERENCES patients(patient_id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    risk_score FLOAT,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by INTEGER REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_patient_alerts ON alerts (patient_id, timestamp DESC);

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'clinician',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_email ON users (email);

-- User-Patient assignments (for clinicians to access specific patients)
CREATE TABLE IF NOT EXISTS user_patient_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    patient_id VARCHAR(100) REFERENCES patients(patient_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, patient_id)
);

CREATE INDEX IF NOT EXISTS idx_user_assignments ON user_patient_assignments (user_id);
CREATE INDEX IF NOT EXISTS idx_patient_assignments ON user_patient_assignments (patient_id);

-- Insert demo patient
INSERT INTO patients (patient_id, name, age, notes)
VALUES ('patient_001', 'Demo Patient', 75, 'Test patient for MVP demo')
ON CONFLICT (patient_id) DO NOTHING;
