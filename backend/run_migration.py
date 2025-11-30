"""
Migration script to update the predictions table schema
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database.db import engine


async def run_migration():
    """Run the migration script"""

    migration_sql = """
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

-- Check if ts column exists and rename to timestamp
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

-- Create index on timestamp
DROP INDEX IF EXISTS idx_patient_pred_ts;
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions (patient_id, timestamp DESC);

-- Update alerts table
ALTER TABLE alerts
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS risk_score FLOAT,
ADD COLUMN IF NOT EXISTS acknowledged_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS acknowledged_by INTEGER;

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

-- Add foreign key constraint for acknowledged_by if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'alerts_acknowledged_by_fkey'
    ) THEN
        ALTER TABLE alerts
        ADD CONSTRAINT alerts_acknowledged_by_fkey
        FOREIGN KEY (acknowledged_by) REFERENCES users(id);
    END IF;
END $$;
"""

    print("Running migration...")

    async with engine.begin() as conn:
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

        for statement in statements:
            try:
                print(f"Executing: {statement[:100]}...")
                await conn.execute(statement)
                print("✓ Success")
            except Exception as e:
                print(f"✗ Error: {e}")
                # Continue with other statements

    print("\nMigration completed!")
    print("Please restart the backend service for changes to take effect.")


if __name__ == "__main__":
    asyncio.run(run_migration())
