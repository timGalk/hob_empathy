-- Migration script to update predictions table schema
-- Run this to align the database with the current SQLAlchemy models

-- Add missing columns to predictions table
ALTER TABLE predictions
ADD COLUMN IF NOT EXISTS window_start TIMESTAMP,
ADD COLUMN IF NOT EXISTS delta_power FLOAT,
ADD COLUMN IF NOT EXISTS theta_power FLOAT,
ADD COLUMN IF NOT EXISTS alpha_power FLOAT,
ADD COLUMN IF NOT EXISTS beta_power FLOAT,
ADD COLUMN IF NOT EXISTS entropy FLOAT,
ADD COLUMN IF NOT EXISTS mobility FLOAT,
ADD COLUMN IF NOT EXISTS complexity FLOAT;

-- Rename ts column to timestamp (if ts column exists)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'predictions'
        AND column_name = 'ts'
    ) THEN
        ALTER TABLE predictions RENAME COLUMN ts TO timestamp;
    END IF;
END $$;

-- Add timestamp column if it doesn't exist
ALTER TABLE predictions
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create index on timestamp if it doesn't exist
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions (patient_id, timestamp DESC);

-- Update alerts table to match model
ALTER TABLE alerts
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS risk_score FLOAT,
ADD COLUMN IF NOT EXISTS acknowledged_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS acknowledged_by INTEGER REFERENCES users(id);

-- Rename ts to timestamp in alerts if ts exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'alerts'
        AND column_name = 'ts'
    ) THEN
        ALTER TABLE alerts RENAME COLUMN ts TO timestamp;
    END IF;
END $$;

-- Remove created_at columns that are not in the models
-- (The models use timestamp instead of created_at)
