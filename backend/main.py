"""
EEG Dementia Monitoring - Backend API
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.database.db import init_db

app = FastAPI(
    title="EEG Dementia Monitoring API",
    description="Real-time EEG monitoring and dementia episode prediction",
    version="0.1.0"
)

# CORS middleware for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth_router)  # Auth routes already have /api/v1/auth prefix
app.include_router(admin_router)  # Admin routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

@app.get("/")
async def root():
    return {
        "message": "EEG Dementia Monitoring API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
