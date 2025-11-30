"""
Admin endpoints for database maintenance
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.db import get_db
from ..models.database import User
from ..api.auth import get_current_user

router = APIRouter(prefix="/api/admin")


@router.post("/migrate-schema")
async def migrate_schema(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run database schema migration to add missing columns

    This endpoint should only be called by administrators.
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    migration_statements = [
        # Add missing columns to predictions table
        """ALTER TABLE predictions
        ADD COLUMN IF NOT EXISTS window_start TIMESTAMP,
        ADD COLUMN IF NOT EXISTS delta_power FLOAT,
        ADD COLUMN IF NOT EXISTS theta_power FLOAT,
        ADD COLUMN IF NOT EXISTS alpha_power FLOAT,
        ADD COLUMN IF NOT EXISTS beta_power FLOAT,
        ADD COLUMN IF NOT EXISTS entropy FLOAT,
        ADD COLUMN IF NOT EXISTS mobility FLOAT,
        ADD COLUMN IF NOT EXISTS complexity FLOAT""",

        # Rename ts to timestamp in predictions if it exists
        """DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'predictions'
                AND column_name = 'ts'
            ) THEN
                ALTER TABLE predictions RENAME COLUMN ts TO timestamp;
            END IF;
        END $$""",

        # Add timestamp column if it doesn't exist
        """ALTER TABLE predictions
        ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP""",

        # Update index
        """DROP INDEX IF EXISTS idx_patient_pred_ts""",

        """CREATE INDEX IF NOT EXISTS idx_predictions_timestamp
        ON predictions (patient_id, timestamp DESC)""",

        # Update alerts table
        """ALTER TABLE alerts
        ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ADD COLUMN IF NOT EXISTS risk_score FLOAT,
        ADD COLUMN IF NOT EXISTS acknowledged_at TIMESTAMP,
        ADD COLUMN IF NOT EXISTS acknowledged_by INTEGER""",

        # Rename ts to timestamp in alerts if it exists
        """DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'alerts'
                AND column_name = 'ts'
            ) THEN
                ALTER TABLE alerts RENAME COLUMN ts TO timestamp;
            END IF;
        END $$""",

        # Add foreign key constraint
        """DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'alerts_acknowledged_by_fkey'
            ) THEN
                ALTER TABLE alerts
                ADD CONSTRAINT alerts_acknowledged_by_fkey
                FOREIGN KEY (acknowledged_by) REFERENCES users(id);
            END IF;
        END $$""",
    ]

    results = []
    errors = []

    for i, statement in enumerate(migration_statements):
        try:
            await db.execute(text(statement))
            await db.commit()
            results.append(f"Statement {i+1}: Success")
        except Exception as e:
            errors.append(f"Statement {i+1}: {str(e)}")
            # Continue with other statements

    if errors:
        return {
            "status": "completed_with_errors",
            "results": results,
            "errors": errors
        }

    return {
        "status": "success",
        "message": "Schema migration completed successfully",
        "results": results
    }
