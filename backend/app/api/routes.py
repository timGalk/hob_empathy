"""
API Routes for EEG monitoring system
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from typing import List
from ..models.schemas import FeaturePayload, PredictionResponse, PatientState
from ..models.database import User
from ..api.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/v1")

# In-memory storage for demo (replace with DB in production)
predictions_cache = {}

@router.post("/ingest", status_code=201)
async def ingest_features(
    payload: FeaturePayload,
    current_user: User = Depends(get_current_user)
):
    """
    Receive windowed EEG features from edge device

    Requires authentication.
    """
    # TODO: Store features in database
    # TODO: Trigger prediction engine
    # TODO: Check user has access to this patient

    return {
        "status": "received",
        "patient_id": payload.patient_id,
        "timestamp": payload.window_start
    }

@router.get("/patient/{patient_id}/state", response_model=PatientState)
async def get_patient_state(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get latest prediction for a patient

    Requires authentication.
    """
    # TODO: Check user has access to this patient
    if patient_id not in predictions_cache:
        raise HTTPException(status_code=404, detail="Patient not found")

    return predictions_cache.get(patient_id, {
        "patient_id": patient_id,
        "risk": 0.0,
        "state": "normal",
        "timestamp": datetime.utcnow().isoformat()
    })

@router.get("/history/{patient_id}")
async def get_history(
    patient_id: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Get feature & prediction time-series

    Requires authentication.
    """
    # TODO: Query database for historical data
    # TODO: Check user has access to this patient
    return {
        "patient_id": patient_id,
        "history": []
    }

@router.websocket("/stream")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket for real-time event push to dashboard

    Requires authentication via token query parameter.
    Example: ws://host/api/v1/stream?token=<jwt_token>
    """
    # Validate token before accepting connection
    from ..utils.auth import decode_access_token
    from ..database.db import async_session_maker
    from ..api.auth import get_user_by_username

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid authentication token")
        return

    username = payload.get("sub")
    if not username:
        await websocket.close(code=1008, reason="Invalid token payload")
        return

    # Verify user exists
    async with async_session_maker() as db:
        user = await get_user_by_username(db, username)
        if not user or not user.is_active:
            await websocket.close(code=1008, reason="User not found or inactive")
            return

    await websocket.accept()
    try:
        while True:
            # TODO: Stream real-time predictions and alerts
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat(),
                "user": username
            })
    except WebSocketDisconnect:
        print(f"Client disconnected: {username}")
