#!/usr/bin/env python3
"""
Script to run database schema migration via HTTP endpoint
This script calls the /api/admin/migrate-schema endpoint
"""
import requests
import sys


def run_migration(base_url="http://localhost:8000", username="admin", password="admin"):
    """
    Run the database migration

    Args:
        base_url: Base URL of the backend API
        username: Admin username
        password: Admin password
    """
    print("="*60)
    print("Database Migration Script")
    print("="*60)

    # Step 1: Login to get access token
    print(f"\n[1/2] Logging in as '{username}'...")

    login_url = f"{base_url}/api/v1/auth/login"
    login_data = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(login_url, data=login_data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            print("✗ Failed to get access token")
            sys.exit(1)

        print(f"✓ Successfully logged in as {token_data.get('user', {}).get('username')}")
        print(f"  Role: {token_data.get('user', {}).get('role')}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Login failed: {e}")
        print("\nPlease ensure:")
        print("  1. The backend service is running")
        print("  2. The admin user exists with the correct password")
        print("  3. The backend is accessible at", base_url)
        sys.exit(1)

    # Step 2: Call migration endpoint
    print(f"\n[2/2] Running database migration...")

    migrate_url = f"{base_url}/api/admin/migrate-schema"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.post(migrate_url, headers=headers)
        response.raise_for_status()
        result = response.json()

        print(f"\n✓ Migration completed!")
        print(f"  Status: {result.get('status')}")

        if result.get('results'):
            print("\nResults:")
            for r in result.get('results', []):
                print(f"  ✓ {r}")

        if result.get('errors'):
            print("\nErrors:")
            for err in result.get('errors', []):
                print(f"  ✗ {err}")

        if result.get('message'):
            print(f"\n{result.get('message')}")

        print("\n" + "="*60)
        print("Migration complete! Please restart the backend service.")
        print("="*60)

    except requests.exceptions.HTTPException as e:
        if hasattr(e, 'response') and e.response.status_code == 403:
            print("✗ Access denied - Admin role required")
            sys.exit(1)
        else:
            print(f"✗ Migration failed: {e}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run database schema migration")
    parser.add_argument("--url", default="http://localhost:8000", help="Backend API URL")
    parser.add_argument("--username", default="admin", help="Admin username")
    parser.add_argument("--password", default="admin", help="Admin password")

    args = parser.parse_args()

    run_migration(args.url, args.username, args.password)
