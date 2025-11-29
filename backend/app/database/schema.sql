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
    patient_id VARCHAR(100) REFERENCES patients(patient_id),
    ts TIMESTAMP NOT NULL,
    risk FLOAT NOT NULL,
    state VARCHAR(50) NOT NULL,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patient_pred_ts ON predictions (patient_id, ts DESC);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) REFERENCES patients(patient_id),
    ts TIMESTAMP NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    message TEXT,
    severity VARCHAR(20),
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patient_alerts ON alerts (patient_id, ts DESC);

-- Insert demo patient
INSERT INTO patients (patient_id, name, age, notes)
VALUES ('patient_001', 'Demo Patient', 75, 'Test patient for MVP demo')
ON CONFLICT (patient_id) DO NOTHING;
