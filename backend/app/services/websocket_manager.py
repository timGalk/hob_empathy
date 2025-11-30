"""
WebSocket Manager - Handles real-time connections and broadcasting
"""
from fastapi import WebSocket
from typing import Dict, List, Set
import json
from datetime import datetime


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Map of user_id -> set of websocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Map of patient_id -> set of user_ids monitoring this patient
        self.patient_monitors: Dict[str, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a new WebSocket for a user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        print(f"✓ WebSocket connected for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"✗ WebSocket disconnected for user {user_id}")

    def subscribe_to_patient(self, user_id: int, patient_id: str):
        """Subscribe a user to receive updates for a specific patient"""
        if patient_id not in self.patient_monitors:
            self.patient_monitors[patient_id] = set()
        self.patient_monitors[patient_id].add(user_id)
        print(f"User {user_id} subscribed to patient {patient_id}")

    def unsubscribe_from_patient(self, user_id: int, patient_id: str):
        """Unsubscribe a user from patient updates"""
        if patient_id in self.patient_monitors:
            self.patient_monitors[patient_id].discard(user_id)
            if not self.patient_monitors[patient_id]:
                del self.patient_monitors[patient_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user's connections"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection)

            # Clean up disconnected websockets
            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def broadcast_prediction(self, patient_id: str, prediction_data: dict):
        """
        Broadcast a new prediction to all users monitoring this patient

        Args:
            patient_id: Patient identifier
            prediction_data: Prediction data including risk, state, timestamp
        """
        message = {
            "type": "prediction",
            "patient_id": patient_id,
            "data": prediction_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Find all users monitoring this patient
        if patient_id in self.patient_monitors:
            for user_id in self.patient_monitors[patient_id]:
                await self.send_personal_message(message, user_id)

    async def broadcast_alert(self, patient_id: str, alert_data: dict):
        """
        Broadcast an alert to all users monitoring this patient

        Args:
            patient_id: Patient identifier
            alert_data: Alert data including severity, message, type
        """
        message = {
            "type": "alert",
            "patient_id": patient_id,
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Find all users monitoring this patient
        if patient_id in self.patient_monitors:
            for user_id in self.patient_monitors[patient_id]:
                await self.send_personal_message(message, user_id)

    async def send_heartbeat(self, user_id: int):
        """Send a heartbeat/ping message"""
        message = {
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(message, user_id)

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(conns) for conns in self.active_connections.values())

    def get_users_for_patient(self, patient_id: str) -> Set[int]:
        """Get all user IDs monitoring a specific patient"""
        return self.patient_monitors.get(patient_id, set()).copy()


# Global singleton instance
ws_manager = WebSocketManager()
