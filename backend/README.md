# Backend API

FastAPI-based backend service for EEG dementia monitoring system.

## Features

- RESTful API for feature ingestion
- WebSocket support for real-time streaming
- PostgreSQL database integration
- Pydantic models for validation
- OpenAPI/Swagger documentation

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
uvicorn main:app --reload
```

API documentation available at: http://localhost:8000/docs

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `BACKEND_PORT` - Server port (default: 8000)
