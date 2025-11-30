"""
Seed database with initial patient data and assignments
Run this script to set up patient_001 and assign all users to it
"""
import asyncio
from sqlalchemy import select
from app.database.db import async_session_maker
from app.models.database import Patient, User, UserPatientAssignment


async def seed_database():
    """Seed the database with initial data"""
    async with async_session_maker() as db:
        try:
            # Check if patient_001 already exists
            stmt = select(Patient).where(Patient.patient_id == "patient_001")
            result = await db.execute(stmt)
            existing_patient = result.scalar_one_or_none()

            if not existing_patient:
                # Create patient_001
                patient = Patient(
                    patient_id="patient_001",
                    name="Demo Patient",
                    age=65,
                    notes="Default patient for testing and development"
                )
                db.add(patient)
                await db.commit()
                print("✓ Created patient_001")
            else:
                print("✓ patient_001 already exists")

            # Get all users
            stmt = select(User)
            result = await db.execute(stmt)
            users = result.scalars().all()

            if not users:
                print("⚠ No users found. Please register a user first.")
                return

            # Assign all users to patient_001
            assigned_count = 0
            for user in users:
                # Check if assignment already exists
                stmt = select(UserPatientAssignment).where(
                    UserPatientAssignment.user_id == user.id,
                    UserPatientAssignment.patient_id == "patient_001"
                )
                result = await db.execute(stmt)
                existing_assignment = result.scalar_one_or_none()

                if not existing_assignment:
                    assignment = UserPatientAssignment(
                        user_id=user.id,
                        patient_id="patient_001"
                    )
                    db.add(assignment)
                    assigned_count += 1
                    print(f"✓ Assigned patient_001 to user '{user.username}'")

            if assigned_count > 0:
                await db.commit()
                print(f"\n✓ Successfully assigned {assigned_count} user(s) to patient_001")
            else:
                print("\n✓ All users already have access to patient_001")

        except Exception as e:
            print(f"✗ Error seeding database: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    print("Seeding database with patient_001...\n")
    asyncio.run(seed_database())
    print("\n✓ Database seeding complete!")
