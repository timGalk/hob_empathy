"""
API Routes for EEG monitoring system
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
from ..models.schemas import FeaturePayload, PredictionResponse, PatientState
from datetime import datetime

router = APIRouter()

# In-memory storage for demo (replace with DB in production)
predictions_cache = {}

@router.post("/ingest", status_code=201)
async def ingest_features(payload: FeaturePayload):
    """
    Receive windowed EEG features from edge device
    """
    # TODO: Store features in database
    # TODO: Trigger prediction engine

    return {
        "status": "received",
        "patient_id": payload.patient_id,
        "timestamp": payload.window_start
    }

@router.get("/patient/{patient_id}/state", response_model=PatientState)
async def get_patient_state(patient_id: str):
    """
    Get latest prediction for a patient
    """
    if patient_id not in predictions_cache:
        raise HTTPException(status_code=404, detail="Patient not found")

    return predictions_cache.get(patient_id, {
        "patient_id": patient_id,
        "risk": 0.0,
        "state": "normal",
        "timestamp": datetime.utcnow().isoformat()
    })

@router.get("/history/{patient_id}")
async def get_history(patient_id: str, limit: int = 100):
    """
    Get feature & prediction time-series
    """
    # TODO: Query database for historical data
    return {
        "patient_id": patient_id,
        "history": []
    }

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time event push to dashboard
    """
    await websocket.accept()
    try:
        while True:
            # TODO: Stream real-time predictions and alerts
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        print("Client disconnected")
