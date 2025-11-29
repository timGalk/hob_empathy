# Authentication Setup Guide

This guide explains how to set up and use the JWT-based authentication system for the EEG Dementia Monitoring application.

## Overview

The authentication system includes:
- **Backend**: FastAPI with JWT token-based authentication
- **Mobile App**: Flutter app with secure token storage
- **Features**: User registration, login, token refresh, and protected API endpoints

## Architecture

```
Mobile App (Flutter)
    ↓ JWT Token
Backend API (FastAPI)
    ↓ Authenticated
Database (PostgreSQL)
```

## Backend Setup

### 1. Database Schema

The authentication system adds the following tables:

```sql
-- Users table
CREATE TABLE users (
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

-- User-Patient assignments
CREATE TABLE user_patient_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    patient_id VARCHAR(100) REFERENCES patients(patient_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, patient_id)
);
```

### 2. Environment Variables

Update your `.env` file with these authentication settings:

```bash
# Database
DATABASE_URL=postgresql://eeg_user:eeg_password@db:5432/eeg_monitoring

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: Generate a strong SECRET_KEY using:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Install Backend Dependencies

The required packages are already in `requirements.txt`:
```
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
```

Install them:
```bash
cd backend
pip install -r requirements.txt
```

### 4. Apply Database Schema

Run the schema migration:
```bash
docker-compose up -d db
docker exec -i <postgres-container> psql -U eeg_user -d eeg_monitoring < backend/app/database/schema.sql
```

Or if using Docker Compose:
```bash
docker-compose exec db psql -U eeg_user -d eeg_monitoring < /docker-entrypoint-initdb.d/schema.sql
```

### 5. Start Backend

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 6. API Endpoints

Authentication endpoints:

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info (requires authentication)

Protected endpoints (require JWT token):

- `POST /api/v1/ingest` - Send EEG features
- `GET /api/v1/patient/{patient_id}/state` - Get patient state
- `GET /api/v1/history/{patient_id}` - Get patient history
- `WS /api/v1/stream?token=<jwt>` - WebSocket stream

## Mobile App Setup

### 1. Install Dependencies

```bash
cd mobile-app
flutter pub get
```

New dependencies added:
- `flutter_secure_storage: ^9.0.0` - Secure token storage
- `jwt_decoder: ^2.0.1` - JWT token decoding

### 2. Configure Backend URL

Update `lib/utils/config.dart` if needed:

```dart
class Config {
  static String backendUrl = const String.fromEnvironment(
    'BACKEND_URL',
    defaultValue: 'http://10.0.2.2:8000', // Android emulator
  );

  static String wsUrl = const String.fromEnvironment(
    'WS_URL',
    defaultValue: 'ws://10.0.2.2:8000',
  );

  static String patientId = const String.fromEnvironment(
    'PATIENT_ID',
    defaultValue: 'patient_001',
  );
}
```

For physical devices, use your computer's IP address:
```dart
defaultValue: 'http://192.168.1.100:8000'
```

### 3. Platform-Specific Setup

#### Android
No additional setup required.

#### iOS
Add to `ios/Runner/Info.plist`:
```xml
<key>NSFaceIDUsageDescription</key>
<string>We use Face ID to secure your authentication credentials</string>
```

#### macOS
Add to `macos/Runner/DebugProfile.entitlements` and `Release.entitlements`:
```xml
<key>keychain-access-groups</key>
<array>
    <string>$(AppIdentifierPrefix)com.example.eegMonitor</string>
</array>
```

#### Linux
No additional setup required.

### 4. Run the App

```bash
flutter run
```

## Usage

### Creating the First User

#### Via API (cURL)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "clinician1",
    "email": "clinician1@example.com",
    "password": "SecurePass123",
    "full_name": "Dr. Jane Smith",
    "role": "clinician"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "clinician1",
    "email": "clinician1@example.com",
    "full_name": "Dr. Jane Smith",
    "role": "clinician",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00"
  }
}
```

#### Via Mobile App

1. Launch the app
2. On the login screen, tap "Don't have an account? Register"
3. Fill in the registration form:
   - Username
   - Email
   - Password (min 6 characters)
   - Full Name (optional)
4. Tap "Register"
5. You'll be automatically logged in

### Logging In

#### Via API

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=clinician1&password=SecurePass123"
```

#### Via Mobile App

1. Launch the app
2. Enter username and password
3. Tap "Login"

### Using Protected Endpoints

Include the JWT token in the Authorization header:

```bash
curl -X GET "http://localhost:8000/api/v1/patient/patient_001/state" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### WebSocket Authentication

WebSocket connections require the token as a query parameter:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/stream?token=<your-jwt-token>');
```

The mobile app handles this automatically.

## Security Features

### Backend Security

1. **Password Hashing**: Passwords are hashed using bcrypt
2. **JWT Tokens**: Tokens expire after 30 minutes (configurable)
3. **Token Validation**: All protected endpoints verify token validity
4. **User Status**: Inactive users cannot authenticate
5. **HTTPS Ready**: Use HTTPS in production

### Mobile App Security

1. **Secure Storage**: Tokens stored in OS keychain/keystore
2. **Token Expiry**: Automatic logout when token expires
3. **No Plain Passwords**: Passwords never stored locally
4. **HTTPS Support**: Configure for production SSL/TLS

## User Roles

The system supports role-based access control:

- `clinician` - Default role for healthcare providers
- `admin` - For administrative users (future use)
- `edge_device` - For IoT devices (future use)

## Troubleshooting

### Backend Issues

**Problem**: "Could not validate credentials"
- Check if token is expired
- Verify SECRET_KEY matches between token creation and validation
- Ensure Authorization header format: `Bearer <token>`

**Problem**: "Username already registered"
- Username must be unique
- Try a different username

**Problem**: Database connection error
- Verify DATABASE_URL is correct
- Ensure PostgreSQL is running
- Check database exists and schema is applied

### Mobile App Issues

**Problem**: "Network error"
- Verify backend is running
- Check BACKEND_URL configuration
- For Android emulator, use `10.0.2.2` instead of `localhost`
- For physical devices, use computer's IP address

**Problem**: Login screen doesn't appear
- Clear app data and restart
- Check AuthService initialization in logs

**Problem**: Token storage fails on iOS
- Verify Info.plist has NSFaceIDUsageDescription
- Check keychain access permissions

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

### Test User Creation

```python
import requests

url = "http://localhost:8000/api/v1/auth/register"
data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User",
    "role": "clinician"
}

response = requests.post(url, json=data)
print(response.json())
```

### Test Protected Endpoint

```python
import requests

# Login first
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "testuser", "password": "TestPass123"}
)
token = login_response.json()["access_token"]

# Access protected endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/v1/patient/patient_001/state",
    headers=headers
)
print(response.json())
```

## Production Deployment

### Backend

1. **Use strong SECRET_KEY**:
   ```bash
   export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   ```

2. **Enable HTTPS**: Use reverse proxy (nginx/Traefik) with SSL certificates

3. **Configure CORS**: Update allowed origins in `main.py`

4. **Database security**: Use strong passwords and restrict access

5. **Token expiry**: Adjust `ACCESS_TOKEN_EXPIRE_MINUTES` based on requirements

### Mobile App

1. **Update backend URL**: Point to production HTTPS endpoint

2. **Enable SSL pinning**: Add certificate pinning for extra security

3. **Code obfuscation**: Build with `--obfuscate` flag

4. **Environment variables**: Use build-time variables for configuration

## Next Steps

- [ ] Implement token refresh mechanism
- [ ] Add password reset functionality
- [ ] Implement multi-factor authentication
- [ ] Add role-based endpoint permissions
- [ ] Add user management endpoints (admin only)
- [ ] Implement patient-user assignment management
- [ ] Add audit logging for authentication events

## Support

For issues or questions:
1. Check the logs: Backend logs in console, mobile logs in `flutter logs`
2. Review this documentation
3. Check API documentation at `/docs`
4. Open an issue in the project repository
