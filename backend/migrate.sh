#!/bin/bash
# Database migration script using curl
# This script logs in and calls the migration endpoint

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-admin}"

echo "========================================"
echo "Database Migration Script"
echo "========================================"
echo ""

# Step 1: Login
echo "[1/2] Logging in as '$USERNAME'..."

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$ACCESS_TOKEN" ]; then
  echo "✗ Login failed!"
  echo "Response: $LOGIN_RESPONSE"
  echo ""
  echo "Please ensure:"
  echo "  1. Backend is running at $BASE_URL"
  echo "  2. Admin user exists with correct credentials"
  exit 1
fi

echo "✓ Successfully logged in"
echo ""

# Step 2: Run migration
echo "[2/2] Running database migration..."

MIGRATION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/migrate-schema" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "$MIGRATION_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MIGRATION_RESPONSE"

echo ""
echo "========================================"
echo "Migration complete!"
echo "Please restart the backend service."
echo "========================================"
