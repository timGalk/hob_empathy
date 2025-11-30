"""
Script to make a user an admin
"""
import asyncio
import sys
from sqlalchemy import select
from app.database.db import async_session_maker
from app.models.database import User


async def make_admin(username: str):
    """Make a user an admin"""
    async with async_session_maker() as db:
        # Find the user
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            print(f"✗ User '{username}' not found")
            return False

        # Update role to admin
        if user.role == "admin":
            print(f"✓ User '{username}' is already an admin")
            return True

        user.role = "admin"
        await db.commit()

        print(f"✓ User '{username}' is now an admin (was: {user.role})")
        return True


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    print(f"Making '{username}' an admin...\n")

    success = asyncio.run(make_admin(username))

    if success:
        print("\n✓ Done! You can now run the migration script.")
    else:
        print("\n✗ Failed to make user admin")
        sys.exit(1)
