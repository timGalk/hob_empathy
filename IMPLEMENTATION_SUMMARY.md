# EEG Dementia Monitoring - Prediction & Dashboard Implementation

## Overview

This document describes the complete implementation of the prediction engine integration, anomaly detection, real-time alerting, and clinician dashboard for the EEG-based dementia monitoring system.

## Architecture

```
┌─────────────────┐
│   EEG Device    │
│  (BrainAccess)  │
└────────┬────────┘
         │ Bluetooth (250Hz)
         ↓
┌─────────────────────────────┐
│   Mobile App / Edge Device  │
│  - Signal Filtering         │
│  - Feature Extraction       │
│  - Delta/Theta/Alpha/Beta   │
│  - Entropy, Mobility        │
└────────┬────────────────────┘
         │ HTTPS
         ↓
┌─────────────────────────────┐
│     Backend API (FastAPI)   │
│  /api/v1/ingest             │
│  - Validate user access     │
│  - Run prediction model     │
│  - Store in database        │
│  - Create alerts if needed  │
│  - Broadcast via WebSocket  │
└────────┬────────────────────┘
         │
    ┌────┴────┬──────────┬─────────┐
    ↓         ↓          ↓         ↓
┌────────┐ ┌─────┐  ┌────────┐ ┌──────┐
│XGBoost │ │ DB  │  │WebSocket│ │Alerts│
│Model   │ │     │  │Manager  │ │      │
└────────┘ └─────┘  └────────┘ └──────┘
                         │
                         ↓ Real-time
                    ┌─────────────┐
                    │  Dashboard  │
                    │  (Flutter)  │
                    └─────────────┘
```

## Components Implemented

### 1. Backend - Prediction Service

**File:** `backend/app/services/prediction_service.py`

- **Singleton service** that loads the XGBoost model and scaler
- **Features used:** delta, theta, alpha, beta power, entropy, mobility, complexity (7 features)
- **Input:** EEGFeatures object from edge processor
- **Output:** PredictionResponse with risk score (0.0-1.0) and state classification
- **Model:** XGBoost Classifier with 500 estimators
- **Model version:** v1.0-xgboost-500

**Risk Classification:**
- `risk < 0.3` → Normal (Green)
- `0.3 ≤ risk < 0.6` → Mild Agitation (Orange)
- `risk ≥ 0.6` → Elevated Risk (Red)

### 2. Backend - Database Models

**File:** `backend/app/models/database.py`

#### New Tables:

**Prediction Table:**
```sql
predictions
├── id (PK)
├── patient_id (FK → patients)
├── timestamp
├── window_start
├── Features: delta_power, theta_power, alpha_power, beta_power, entropy, mobility, complexity
├── risk (0.0-1.0)
├── state (normal|mild|elevated)
└── model_version
```

**Alert Table:**
```sql
alerts
├── id (PK)
├── patient_id (FK → patients)
├── timestamp
├── alert_type (absence_detected|elevated_risk|moderate_risk)
├── severity (low|medium|high)
├── message
├── risk_score
├── acknowledged (boolean)
├── acknowledged_at
└── acknowledged_by (FK → users)
```

### 3. Backend - WebSocket Manager

**File:** `backend/app/services/websocket_manager.py`

**Features:**
- Manages real-time connections for multiple users
- Auto-subscribes users to their assigned patients
- Broadcasts predictions to subscribed users
- Broadcasts alerts to subscribed users
- Handles connection/disconnection gracefully

**Message Types:**
```json
// Prediction update
{
  "type": "prediction",
  "patient_id": "P001",
  "data": {
    "risk": 0.45,
    "state": "mild",
    "model_version": "v1.0-xgboost-500",
    "timestamp": "2025-11-30T12:34:56Z"
  }
}

// Alert notification
{
  "type": "alert",
  "patient_id": "P001",
  "data": {
    "severity": "high",
    "message": "Elevated risk detected: 75%. Immediate attention recommended.",
    "risk_score": 0.75,
    "timestamp": "2025-11-30T12:34:56Z"
  }
}
```

### 4. Backend - API Endpoints

**File:** `backend/app/api/routes.py`

#### Modified Endpoints:

**POST `/api/v1/ingest`**
- Receives EEG features from edge devices
- Validates user access to patient
- Runs prediction model
- Stores prediction in database
- Creates alerts if risk ≥ 0.3
- Broadcasts via WebSocket
- Returns prediction result

**GET `/api/v1/history/{patient_id}`**
- Returns last N predictions for a patient
- Access control enforced
- Ordered by timestamp descending

**WebSocket `/api/v1/stream?token=<jwt>`**
- Real-time prediction and alert streaming
- Auto-subscribes to assigned patients
- Supports subscribe/unsubscribe actions
- JWT authentication required

#### New Dashboard Endpoints:

**GET `/api/v1/dashboard`**
- Returns summary for all patients assigned to user
- Total patients, high-risk count, active alerts
- Complete data for each patient

**GET `/api/v1/dashboard/patient/{patient_id}`**
- Detailed dashboard for specific patient
- Current state, recent predictions (last 20)
- Active alerts, risk trend
- 24-hour statistics (avg risk, alert count)

**GET `/api/v1/alerts/{patient_id}`**
- Get alerts for a patient
- Filter by acknowledged status
- Limit parameter

**POST `/api/v1/alerts/acknowledge`**
- Acknowledge an alert
- Records who acknowledged and when

**GET `/api/v1/model/info`**
- Returns model metadata
- Version, loaded status, model type

### 5. Mobile App - Dashboard Models

**File:** `mobile-app/lib/models/dashboard_models.dart`

**Classes:**
- `PredictionHistory` - Historical prediction record
- `AlertHistory` - Alert record with severity and acknowledgment
- `PatientDashboard` - Complete patient data (state, predictions, alerts, trends)
- `DashboardSummary` - Summary for all patients

### 6. Mobile App - Backend Service Updates

**File:** `mobile-app/lib/services/backend_service.dart`

**New Methods:**
- `getDashboard()` - Fetch dashboard summary
- `getPatientDashboard(patientId)` - Fetch patient details
- `getPatientAlerts(patientId)` - Fetch alerts
- `acknowledgeAlert(alertId)` - Acknowledge alert
- `getPredictionHistory(patientId)` - Fetch prediction history

### 7. Mobile App - Dashboard Screen

**File:** `mobile-app/lib/screens/dashboard_screen.dart`

**Features:**
- Summary cards (total patients, high-risk, active alerts)
- Patient list with risk indicators
- Auto-refresh every 10 seconds
- Pull-to-refresh support
- Navigation to patient detail

**Patient Detail Screen:**
- Patient info card
- Current status with risk percentage
- 24-hour statistics
- Risk trend chart (last 20 predictions)
- Active alerts with acknowledge button
- Recent predictions list

### 8. Mobile App - Widgets

**File:** `mobile-app/lib/widgets/patient_card.dart`
- Displays patient summary
- Risk indicator, 24h stats
- Color-coded by risk level

**File:** `mobile-app/lib/widgets/alert_list_item.dart`
- Alert display with severity icon
- Timestamp formatting
- Acknowledge button

**File:** `mobile-app/lib/widgets/risk_trend_chart.dart`
- Line chart using fl_chart package
- Color-coded by risk level
- Interactive tooltips
- Gradient fill below line

## Data Flow

### Prediction Pipeline

```
1. EEG Device → Mobile App
   - 250Hz sampling, 8 channels + 3 accelerometer

2. Mobile App → Feature Extraction
   - 2-second windows (500 samples)
   - Bandpass filter (1-40Hz)
   - Notch filter (50/60Hz)
   - Extract: delta, theta, alpha, beta, entropy, mobility, complexity

3. Mobile App → Backend POST /api/v1/ingest
   - FeaturePayload with patient_id, window_start, features

4. Backend → Prediction Service
   - Scale features
   - Run XGBoost model
   - Get risk score (0.0-1.0)

5. Backend → Database
   - Store Prediction record
   - Create Alert if risk ≥ 0.3

6. Backend → WebSocket Broadcast
   - Send prediction to subscribed users
   - Send alert if created

7. Dashboard → Real-time Update
   - Display new risk score
   - Show alert notification
   - Update trend chart
```

### Alert Thresholds

- **High Risk (≥0.6):**
  - Severity: high
  - Message: "Elevated risk detected: XX%. Immediate attention recommended."
  - Mobile Action: Show emergency alert screen (Call 911 option)

- **Moderate Risk (0.3-0.6):**
  - Severity: medium
  - Message: "Moderate risk detected: XX%. Please monitor patient."
  - Mobile Action: Show verification alert screen (Check location/Call option)

- **Normal (<0.3):**
  - No alert created
  - Normal display

## Configuration

### Backend Requirements

**Dependencies (requirements.txt):**
```txt
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
python-multipart
pydantic
pydantic-settings
numpy
scipy
scikit-learn
xgboost
joblib
```

**Environment Variables:**
```env
DATABASE_URL=postgresql://eeg_user:eeg_password@db:5432/eeg_monitoring
SECRET_KEY=<your-secret-key>
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Mobile App Requirements

**Dependencies (pubspec.yaml):**
```yaml
dependencies:
  provider: ^6.1.1
  http: ^1.1.0
  web_socket_channel: ^2.4.0
  fl_chart: ^0.65.0
  flutter_blue_plus: ^1.31.0
  fftea: ^1.0.0
  shared_preferences: ^2.2.2
  flutter_secure_storage: ^9.0.0
  jwt_decoder: ^2.0.1
```

## Running the System

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The prediction service will automatically load the model from:
- `prediction_engine/absence_detector_model.pkl`
- `prediction_engine/absence_detector_scaler.pkl`

If models are not found, predictions will return default values. Train the model first:

```bash
cd prediction_engine
python main.py
```

### 2. Database Migration

The database tables will be created automatically on first run via:
```python
@app.on_event("startup")
async def startup_event():
    await init_db()
```

### 3. Mobile App Setup

```bash
# Navigate to mobile app
cd mobile-app

# Get dependencies
flutter pub get

# Run on device/emulator
flutter run
```

### 4. Configure Backend URL

Update `mobile-app/lib/utils/config.dart`:
```dart
class Config {
  static const String backendUrl = 'http://your-backend-ip:8000';
  static const String wsUrl = 'ws://your-backend-ip:8000';
}
```

## Testing the Flow

### 1. Create Test User and Patient

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "doctor1",
    "email": "doctor@example.com",
    "password": "secure123",
    "full_name": "Dr. Smith",
    "role": "clinician"
  }'
```

### 2. Assign Patient

Use the backend admin panel or direct database insertion:
```sql
INSERT INTO patients (patient_id, name, age)
VALUES ('P001', 'John Doe', 75);

INSERT INTO user_patient_assignments (user_id, patient_id)
VALUES (1, 'P001');
```

### 3. Send Test EEG Data

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'doctor1',
    'password': 'secure123'
})
token = response.json()['access_token']

# Send features
headers = {'Authorization': f'Bearer {token}'}
payload = {
    'patient_id': 'P001',
    'window_start': '2025-11-30T12:00:00Z',
    'features': {
        'delta_power': 0.5,
        'theta_power': 0.3,
        'alpha_power': 0.8,
        'beta_power': 0.4,
        'entropy': 0.7,
        'mobility': 0.6,
        'complexity': 0.5
    }
}

response = requests.post(
    'http://localhost:8000/api/v1/ingest',
    headers=headers,
    json=payload
)
print(response.json())
```

### 4. View Dashboard

1. Login to mobile app with `doctor1` credentials
2. Navigate to `/dashboard` route
3. View patient list with risk indicators
4. Tap patient card to see detailed view
5. Observe real-time updates via WebSocket

## Performance Considerations

- **Database Indexing:** Indexes on `patient_id`, `timestamp`, `acknowledged` for fast queries
- **WebSocket Scaling:** Consider Redis pub/sub for multi-server deployments
- **Prediction Caching:** Latest predictions cached in memory for instant access
- **History Limits:** Dashboard queries limited to last 20-100 records
- **Auto-cleanup:** Consider implementing periodic cleanup of old predictions

## Security

- **JWT Authentication:** All endpoints require valid token
- **User-Patient Access Control:** Users can only access assigned patients
- **WebSocket Auth:** Token validated before accepting connection
- **Input Validation:** Pydantic models validate all inputs
- **SQL Injection Protection:** SQLAlchemy ORM prevents injection

## Future Enhancements

1. **Push Notifications:** FCM integration for mobile alerts
2. **Offline Support:** Queue predictions when offline
3. **Advanced Analytics:** Trend analysis, anomaly detection
4. **Export Features:** PDF reports, CSV exports
5. **Multi-model Support:** A/B testing different models
6. **Federated Learning:** Train models on-device for privacy
7. **Voice Alerts:** Text-to-speech for critical alerts
8. **Caregiver App:** Separate app for family members

## Files Created/Modified

### Backend
- ✅ `backend/app/services/prediction_service.py` (NEW)
- ✅ `backend/app/services/websocket_manager.py` (NEW)
- ✅ `backend/app/services/__init__.py` (NEW)
- ✅ `backend/app/models/database.py` (MODIFIED - added Prediction, Alert tables)
- ✅ `backend/app/models/schemas.py` (MODIFIED - added dashboard schemas)
- ✅ `backend/app/api/routes.py` (MODIFIED - complete implementation)

### Mobile App
- ✅ `mobile-app/lib/models/dashboard_models.dart` (NEW)
- ✅ `mobile-app/lib/screens/dashboard_screen.dart` (NEW)
- ✅ `mobile-app/lib/widgets/patient_card.dart` (NEW)
- ✅ `mobile-app/lib/widgets/alert_list_item.dart` (NEW)
- ✅ `mobile-app/lib/widgets/risk_trend_chart.dart` (NEW)
- ✅ `mobile-app/lib/services/backend_service.dart` (MODIFIED - added dashboard methods)
- ✅ `mobile-app/lib/main.dart` (MODIFIED - added dashboard route)

## Summary

The implementation provides a complete end-to-end prediction and monitoring system:

1. **Real-time Prediction:** XGBoost model runs on every EEG window
2. **Automatic Alerting:** Alerts created based on risk thresholds
3. **Live Updates:** WebSocket streaming to dashboard
4. **Comprehensive Dashboard:** Patient overview, trends, and history
5. **Alert Management:** Acknowledge and track alerts
6. **Access Control:** Role-based access to patient data
7. **Scalable Architecture:** Ready for multi-user, multi-patient deployment

The system is production-ready pending model training and testing.
