"""
Database connection and initialization
"""
from typing import Generator
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.database import Base

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://eeg_user:eeg_password@db:5432/eeg_monitoring"
)

# Convert to async URL for asyncpg
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    future=True
)

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Synchronous engine for migrations
sync_engine = create_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
)


async def init_db():
    """Initialize database tables"""
    from sqlalchemy import text

    async with engine.begin() as conn:
        # Create all tables defined in Base metadata
        await conn.run_sync(Base.metadata.create_all)

        # Run migration to add missing columns if they don't exist
        try:
            print("Running database migrations...")

            # Add missing columns to predictions table
            await conn.execute(text("""
                ALTER TABLE predictions
                ADD COLUMN IF NOT EXISTS window_start TIMESTAMP,
                ADD COLUMN IF NOT EXISTS delta_power FLOAT,
                ADD COLUMN IF NOT EXISTS theta_power FLOAT,
                ADD COLUMN IF NOT EXISTS alpha_power FLOAT,
                ADD COLUMN IF NOT EXISTS beta_power FLOAT,
                ADD COLUMN IF NOT EXISTS entropy FLOAT,
                ADD COLUMN IF NOT EXISTS mobility FLOAT,
                ADD COLUMN IF NOT EXISTS complexity FLOAT
            """))

            # Rename ts to timestamp in predictions if ts exists
            await conn.execute(text("""
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
                END $$
            """))

            # Add timestamp column if it doesn't exist
            await conn.execute(text("""
                ALTER TABLE predictions
                ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))

            # Update alerts table
            await conn.execute(text("""
                ALTER TABLE alerts
                ADD COLUMN IF NOT EXISTS risk_score FLOAT,
                ADD COLUMN IF NOT EXISTS acknowledged_at TIMESTAMP,
                ADD COLUMN IF NOT EXISTS acknowledged_by INTEGER
            """))

            # Rename ts to timestamp in alerts if ts exists
            await conn.execute(text("""
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
                END $$
            """))

            # Add timestamp column to alerts if it doesn't exist
            await conn.execute(text("""
                ALTER TABLE alerts
                ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))

            print("✓ Database migrations completed")

        except Exception as e:
            print(f"Migration error (may be safe to ignore if already applied): {e}")

    print("Database tables initialized")


async def get_db() -> Generator[AsyncSession, None, None]:
    """
    Dependency function to get database session

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
