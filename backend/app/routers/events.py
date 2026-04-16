"""
Events router - CleanGrid Phase 1
Server-Sent Events for real-time incident updates
"""

import asyncio
import json
import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import structlog

from app.core.database import get_db
from app.models.incident import Incident

logger = structlog.get_logger()
router = APIRouter(prefix="/api/events", tags=["Events"])


class EventManager:
    """Manages SSE connections and event broadcasting"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
    
    def add_connection(self, connection_id: str, connection: Any):
        """Add new SSE connection"""
        self.connections[connection_id] = connection
        logger.info("SSE connection added", connection_id=connection_id)
    
    def remove_connection(self, connection_id: str):
        """Remove SSE connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            logger.info("SSE connection removed", connection_id=connection_id)
    
    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast event to all connected clients"""
        if not self.connections:
            return
        
        event_data = {
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        message = f"data: {json.dumps(event_data)}\n\n"
        
        # Send to all connections
        disconnected = []
        for connection_id, connection in self.connections.items():
            try:
                await connection.send(message)
            except Exception as e:
                logger.warning(
                    "Failed to send SSE event",
                    connection_id=connection_id,
                    error=str(e)
                )
                disconnected.append(connection_id)
        
        # Remove disconnected connections
        for connection_id in disconnected:
            self.remove_connection(connection_id)


# Global event manager
event_manager = EventManager()


@router.get("/incidents")
async def incident_events_stream():
    """
    SSE stream for incident events
    Real-time updates for map without page refresh
    """
    async def event_stream():
        """Generate SSE events"""
        connection_id = str(uuid.uuid4())
        
        # Add connection to manager
        event_manager.add_connection(connection_id, event_stream)
        
        yield f"id: {connection_id}\n"
        yield f"event: connected\ndata: {json.dumps({'connection_id': connection_id})}\n\n"
        
        # Send initial ping
        yield f"event: ping\ndata: {json.dumps({'timestamp': asyncio.get_event_loop().time()})}\n\n"
        
        try:
            # Keep connection alive with periodic pings
            while True:
                await asyncio.sleep(30)  # Ping every 30 seconds
                yield f"event: ping\ndata: {json.dumps({'timestamp': asyncio.get_event_loop().time()})}\n\n"
        except asyncio.CancelledError:
            logger.info("SSE connection closed", connection_id=connection_id)
            event_manager.remove_connection(connection_id)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )


async def broadcast_incident_created(incident: Incident):
    """Broadcast new incident event"""
    await event_manager.broadcast_event(
        "incident_created",
        {
            "incident_id": str(incident.id),
            "status": incident.status,
            "severity": incident.severity,
            "location": {
                "lat": float(incident.location.ST_Y),
                "lng": float(incident.location.ST_X)
            } if incident.location else None
        }
    )


async def broadcast_incident_updated(incident: Incident):
    """Broadcast incident update event"""
    await event_manager.broadcast_event(
        "incident_updated",
        {
            "incident_id": str(incident.id),
            "status": incident.status,
            "severity": incident.severity,
            "location": {
                "lat": float(incident.location.ST_Y),
                "lng": float(incident.location.ST_X)
            } if incident.location else None
        }
    )
