# EEG Dementia Monitoring System - MVP

A real-time EEG monitoring system for detecting and predicting dementia episodes and agitation in elderly patients.

## Overview

This 24-hour hackathon MVP streams 8-channel EEG data at 250 Hz, performs on-device preprocessing, and uses machine learning to predict frustration and dementia episodes. A web-based dashboard provides real-time visualization for clinicians.

## Architecture

```
EEG Device (8ch @ 250Hz)
    │
    ▼
Edge Processor (Mobile/Raspberry Pi)
    │
    ▼
Backend API (FastAPI)
    │
    ▼
Prediction Engine (ML Model)
    │
    ▼
Dashboard (React)
```

## Project Structure

```
.
├── backend/                  # FastAPI backend service
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── models/          # Pydantic schemas
│   │   └── database/        # Database connection & schema
│   ├── main.py              # Application entry point
│   └── requirements.txt
│
├── edge-processor/          # Edge device preprocessing
│   ├── filters/            # Signal filtering
│   ├── features/           # Feature extraction
│   ├── utils/              # Configuration
│   ├── main.py             # Edge processor main
│   └── requirements.txt
│
├── prediction-engine/       # ML prediction service
│   ├── models/             # Trained models
│   ├── training/           # Training scripts
│   ├── predictor.py        # Prediction logic
│   └── requirements.txt
│
├── dashboard/              # React web dashboard
│   ├── src/
│   │   ├── components/    # React components
│   │   └── App.jsx        # Main application
│   └── package.json
│
├── docker-compose.yml      # Docker orchestration
└── ARCHITECTURE.md         # Detailed architecture docs
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Running with Docker (Recommended)

1. Clone the repository:
```bash
git clone <repo-url>
cd hob-empathy
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the services:
   - Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Database: localhost:5432

### Running Locally (Development)

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Dashboard

```bash
cd dashboard
npm install
npm run dev
```

#### Edge Processor

```bash
cd edge-processor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

#### Prediction Engine

```bash
cd prediction-engine
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python predictor.py
```

## API Endpoints

- `POST /api/v1/ingest` - Receive EEG features from edge device
- `GET /api/v1/patient/{id}/state` - Get latest patient state
- `GET /api/v1/history/{id}` - Get historical data
- `WS /api/v1/stream` - WebSocket for real-time updates

## Features

### Edge Preprocessing
- Band-pass filter (1-40 Hz)
- Notch filter (50/60 Hz)
- Feature extraction:
  - Bandpower (Delta, Theta, Alpha, Beta)
  - Spectral entropy
  - Hjorth parameters
  - Signal variance

### Prediction Engine
- Rule-based risk assessment (MVP)
- Support for ML models (Random Forest, LightGBM)
- Risk levels:
  - 0.0-0.3: Normal
  - 0.3-0.6: Mild agitation
  - 0.6-1.0: Elevated risk

### Dashboard
- Real-time EEG visualization
- Risk gauge
- Alert notifications
- Patient information
- Historical trends

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- Database credentials
- Backend URL
- Sampling rate and filter settings
- Patient ID

## Development

### Adding New Features

1. Backend routes: `backend/app/api/routes.py`
2. Data models: `backend/app/models/schemas.py`
3. Signal processing: `edge-processor/filters/` and `edge-processor/features/`
4. ML models: `prediction-engine/training/`
5. UI components: `dashboard/src/components/`

### Database Schema

See `backend/app/database/schema.sql` for the complete schema.

Tables:
- `patients` - Patient information
- `features` - EEG feature history
- `predictions` - Risk predictions
- `alerts` - Alert history

## Deployment

### Production Considerations

- Set up proper authentication (JWT)
- Configure HTTPS/WSS
- Use production database (managed PostgreSQL)
- Enable CORS properly
- Set up monitoring and logging
- Use environment-specific configs

### Cloud Deployment Options

- Backend: Docker (AWS ECS, GCP Cloud Run, Azure Container Instances)
- Database: AWS RDS, GCP Cloud SQL, Azure Database for PostgreSQL
- Dashboard: Vercel, Netlify, AWS Amplify
- Edge: Android/iOS app or Raspberry Pi

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd dashboard
npm test
```

## Troubleshooting

### Docker Issues

```bash
# Clean up and restart
docker-compose down -v
docker-compose up --build
```

### Database Connection

Check if PostgreSQL is running:
```bash
docker-compose ps
docker-compose logs db
```

### WebSocket Connection

Ensure backend is running and accessible. Check browser console for errors.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Authors

MVP developed for 24-hour hackathon

## Acknowledgments

- EEG signal processing based on research in dementia detection
- Frontend UI inspired by clinical monitoring systems
