"""
API Routes for EEG monitoring system
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from typing import List
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from ..models.schemas import (
    FeaturePayload, PredictionResponse, PatientState,
    PredictionHistory, AlertHistory, PatientDashboard, DashboardSummary,
    AlertAcknowledge, Alert as AlertSchema
)
from ..models.database import User, Prediction, Alert, Patient, UserPatientAssignment
from ..api.auth import get_current_user
from ..database.db import get_db
from ..services.prediction_service import prediction_service
from ..services.websocket_manager import ws_manager

router = APIRouter(prefix="/api/v1")

# In-memory storage for latest state (fast access)
predictions_cache = {}

@router.post("/ingest", status_code=201)
async def ingest_features(
    payload: FeaturePayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Receive windowed EEG features from edge device

    1. Validates user has access to patient
    2. Runs prediction model
    3. Stores prediction in database
    4. Creates alert if needed
    5. Broadcasts to WebSocket subscribers

    Requires authentication.
    """
    # Check user has access to this patient
    stmt = select(UserPatientAssignment).where(
        and_(
            UserPatientAssignment.user_id == current_user.id,
            UserPatientAssignment.patient_id == payload.patient_id
        )
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(status_code=403, detail="User does not have access to this patient")

    # Run prediction engine
    prediction_result = prediction_service.predict_from_features(payload.features)

    # Parse window_start timestamp
    try:
        window_start_dt = datetime.fromisoformat(payload.window_start.replace('Z', '+00:00'))
    except:
        window_start_dt = datetime.utcnow()

    # Store prediction in database
    prediction_record = Prediction(
        patient_id=payload.patient_id,
        window_start=window_start_dt,
        delta_power=payload.features.delta_power,
        theta_power=payload.features.theta_power,
        alpha_power=payload.features.alpha_power,
        beta_power=payload.features.beta_power,
        entropy=payload.features.entropy,
        mobility=payload.features.mobility,
        complexity=payload.features.complexity,
        risk=prediction_result.risk,
        state=prediction_result.state,
        model_version=prediction_result.model_version
    )
    db.add(prediction_record)

    # Check if we need to create an alert
    alert_created = False
    if prediction_result.risk >= 0.6:
        # High risk - create critical alert
        alert = Alert(
            patient_id=payload.patient_id,
            alert_type="elevated_risk",
            severity="high",
            message=f"Elevated risk detected: {prediction_result.risk:.2%}. Immediate attention recommended.",
            risk_score=prediction_result.risk
        )
        db.add(alert)
        alert_created = True
    elif prediction_result.risk >= 0.3:
        # Moderate risk - create warning alert
        alert = Alert(
            patient_id=payload.patient_id,
            alert_type="moderate_risk",
            severity="medium",
            message=f"Moderate risk detected: {prediction_result.risk:.2%}. Please monitor patient.",
            risk_score=prediction_result.risk
        )
        db.add(alert)
        alert_created = True

    await db.commit()

    # Update cache for fast access
    predictions_cache[payload.patient_id] = {
        "patient_id": payload.patient_id,
        "risk": prediction_result.risk,
        "state": prediction_result.state,
        "timestamp": prediction_result.timestamp
    }

    # Broadcast prediction via WebSocket
    await ws_manager.broadcast_prediction(
        patient_id=payload.patient_id,
        prediction_data={
            "risk": prediction_result.risk,
            "state": prediction_result.state,
            "model_version": prediction_result.model_version,
            "timestamp": prediction_result.timestamp
        }
    )

    # Broadcast alert if created
    if alert_created:
        await ws_manager.broadcast_alert(
            patient_id=payload.patient_id,
            alert_data={
                "severity": alert.severity,
                "message": alert.message,
                "risk_score": alert.risk_score,
                "timestamp": alert.timestamp.isoformat()
            }
        )

    return {
        "status": "processed",
        "patient_id": payload.patient_id,
        "timestamp": payload.window_start,
        "prediction": {
            "risk": prediction_result.risk,
            "state": prediction_result.state
        },
        "alert_created": alert_created
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

@router.get("/history/{patient_id}", response_model=List[PredictionHistory])
async def get_history(
    patient_id: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get feature & prediction time-series

    Requires authentication and user must have access to patient.
    """
    # Check user has access to this patient
    stmt_access = select(UserPatientAssignment).where(
        and_(
            UserPatientAssignment.user_id == current_user.id,
            UserPatientAssignment.patient_id == patient_id
        )
    )
    result = await db.execute(stmt_access)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="User does not have access to this patient")

    # Query historical predictions
    stmt = select(Prediction).where(
        Prediction.patient_id == patient_id
    ).order_by(desc(Prediction.timestamp)).limit(limit)

    result = await db.execute(stmt)
    predictions = result.scalars().all()

    return predictions

@router.websocket("/stream")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket for real-time event push to dashboard

    Requires authentication via token query parameter.
    Example: ws://host/api/v1/stream?token=<jwt_token>

    Client can send JSON messages:
    - {"action": "subscribe", "patient_id": "P001"} - Subscribe to patient updates
    - {"action": "unsubscribe", "patient_id": "P001"} - Unsubscribe from patient
    - {"action": "ping"} - Heartbeat
    """
    # Validate token before accepting connection
    from ..utils.auth import decode_access_token
    from ..database.db import async_session_maker
    from ..api.auth import get_user_by_username
    import json

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

        user_id = user.id

        # Get all patients assigned to this user and auto-subscribe
        stmt = select(UserPatientAssignment).where(
            UserPatientAssignment.user_id == user_id
        )
        result = await db.execute(stmt)
        assignments = result.scalars().all()

    # Connect WebSocket
    await ws_manager.connect(websocket, user_id)

    # Auto-subscribe to all assigned patients
    for assignment in assignments:
        ws_manager.subscribe_to_patient(user_id, assignment.patient_id)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "user": username,
            "subscribed_patients": [a.patient_id for a in assignments],
            "timestamp": datetime.utcnow().isoformat()
        })

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")

                if action == "subscribe":
                    patient_id = message.get("patient_id")
                    if patient_id:
                        ws_manager.subscribe_to_patient(user_id, patient_id)
                        await websocket.send_json({
                            "type": "subscribed",
                            "patient_id": patient_id
                        })

                elif action == "unsubscribe":
                    patient_id = message.get("patient_id")
                    if patient_id:
                        ws_manager.unsubscribe_from_patient(user_id, patient_id)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "patient_id": patient_id
                        })

                elif action == "ping":
                    await ws_manager.send_heartbeat(user_id)

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
        print(f"Client disconnected: {username}")


# Dashboard Endpoints

@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete dashboard summary for all patients assigned to user

    Returns:
        - Total patient count
        - High risk patient count
        - Active alert count
        - Detailed data for each patient
    """
    # Get all patients assigned to this user
    stmt = select(UserPatientAssignment).where(
        UserPatientAssignment.user_id == current_user.id
    )
    result = await db.execute(stmt)
    assignments = result.scalars().all()
    patient_ids = [a.patient_id for a in assignments]

    if not patient_ids:
        return DashboardSummary(
            total_patients=0,
            high_risk_patients=0,
            active_alerts=0,
            patients=[]
        )

    # Build dashboard for each patient
    patient_dashboards = []
    high_risk_count = 0
    total_active_alerts = 0

    for patient_id in patient_ids:
        dashboard = await _build_patient_dashboard(db, patient_id)
        patient_dashboards.append(dashboard)

        if dashboard.current_state.risk >= 0.6:
            high_risk_count += 1

        total_active_alerts += len(dashboard.active_alerts)

    return DashboardSummary(
        total_patients=len(patient_ids),
        high_risk_patients=high_risk_count,
        active_alerts=total_active_alerts,
        patients=patient_dashboards
    )


@router.get("/dashboard/patient/{patient_id}", response_model=PatientDashboard)
async def get_patient_dashboard(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed dashboard for a specific patient

    Includes:
        - Current state (risk, classification)
        - Recent predictions (last 20)
        - Active alerts
        - Risk trend
        - 24-hour statistics
    """
    # Check access
    stmt_access = select(UserPatientAssignment).where(
        and_(
            UserPatientAssignment.user_id == current_user.id,
            UserPatientAssignment.patient_id == patient_id
        )
    )
    result = await db.execute(stmt_access)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="User does not have access to this patient")

    return await _build_patient_dashboard(db, patient_id)


@router.get("/alerts/{patient_id}", response_model=List[AlertHistory])
async def get_patient_alerts(
    patient_id: str,
    limit: int = 50,
    include_acknowledged: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get alerts for a patient

    Args:
        patient_id: Patient identifier
        limit: Maximum number of alerts to return
        include_acknowledged: Include acknowledged alerts (default: False)
    """
    # Check access
    stmt_access = select(UserPatientAssignment).where(
        and_(
            UserPatientAssignment.user_id == current_user.id,
            UserPatientAssignment.patient_id == patient_id
        )
    )
    result = await db.execute(stmt_access)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="User does not have access to this patient")

    # Query alerts
    stmt = select(Alert).where(Alert.patient_id == patient_id)

    if not include_acknowledged:
        stmt = stmt.where(Alert.acknowledged == False)

    stmt = stmt.order_by(desc(Alert.timestamp)).limit(limit)

    result = await db.execute(stmt)
    alerts = result.scalars().all()

    return alerts


@router.post("/alerts/acknowledge")
async def acknowledge_alert(
    ack: AlertAcknowledge,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Acknowledge an alert

    Marks an alert as acknowledged by the current user
    """
    stmt = select(Alert).where(Alert.id == ack.alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Check user has access to this patient
    stmt_access = select(UserPatientAssignment).where(
        and_(
            UserPatientAssignment.user_id == current_user.id,
            UserPatientAssignment.patient_id == alert.patient_id
        )
    )
    result = await db.execute(stmt_access)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="User does not have access to this patient")

    # Acknowledge the alert
    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = current_user.id

    await db.commit()

    return {
        "status": "acknowledged",
        "alert_id": ack.alert_id,
        "acknowledged_by": current_user.username,
        "acknowledged_at": alert.acknowledged_at.isoformat()
    }


@router.get("/model/info")
async def get_model_info(current_user: User = Depends(get_current_user)):
    """
    Get prediction model information

    Returns model version, status, and configuration
    """
    return prediction_service.get_model_info()


# Helper function to build patient dashboard
async def _build_patient_dashboard(db: AsyncSession, patient_id: str) -> PatientDashboard:
    """Build complete dashboard data for a patient"""

    # Get patient info
    stmt_patient = select(Patient).where(Patient.patient_id == patient_id)
    result = await db.execute(stmt_patient)
    patient = result.scalar_one_or_none()

    # Get current state (latest prediction)
    stmt_latest = select(Prediction).where(
        Prediction.patient_id == patient_id
    ).order_by(desc(Prediction.timestamp)).limit(1)
    result = await db.execute(stmt_latest)
    latest_prediction = result.scalar_one_or_none()

    if latest_prediction:
        current_state = PatientState(
            patient_id=patient_id,
            risk=latest_prediction.risk,
            state=latest_prediction.state,
            timestamp=latest_prediction.timestamp.isoformat()
        )
    else:
        current_state = PatientState(
            patient_id=patient_id,
            risk=0.0,
            state="unknown",
            timestamp=datetime.utcnow().isoformat()
        )

    # Get recent predictions (last 20)
    stmt_recent = select(Prediction).where(
        Prediction.patient_id == patient_id
    ).order_by(desc(Prediction.timestamp)).limit(20)
    result = await db.execute(stmt_recent)
    recent_predictions = result.scalars().all()

    # Get active alerts
    stmt_alerts = select(Alert).where(
        and_(
            Alert.patient_id == patient_id,
            Alert.acknowledged == False
        )
    ).order_by(desc(Alert.timestamp)).limit(10)
    result = await db.execute(stmt_alerts)
    active_alerts = result.scalars().all()

    # Calculate 24h statistics
    time_24h_ago = datetime.utcnow() - timedelta(hours=24)

    # Average risk in last 24h
    stmt_24h = select(func.avg(Prediction.risk)).where(
        and_(
            Prediction.patient_id == patient_id,
            Prediction.timestamp >= time_24h_ago
        )
    )
    result = await db.execute(stmt_24h)
    avg_risk_24h = result.scalar() or 0.0

    # Alert count in last 24h
    stmt_alerts_24h = select(func.count(Alert.id)).where(
        and_(
            Alert.patient_id == patient_id,
            Alert.timestamp >= time_24h_ago
        )
    )
    result = await db.execute(stmt_alerts_24h)
    alerts_24h = result.scalar() or 0

    # Risk trend (last 20 predictions)
    risk_trend = [p.risk for p in recent_predictions]
    risk_trend.reverse()  # Chronological order

    return PatientDashboard(
        patient_id=patient_id,
        name=patient.name if patient else None,
        age=patient.age if patient else None,
        current_state=current_state,
        recent_predictions=recent_predictions,
        active_alerts=active_alerts,
        risk_trend=risk_trend,
        avg_risk_24h=round(float(avg_risk_24h), 4),
        alerts_24h=alerts_24h
    )
