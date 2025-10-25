"""
WebSocket endpoint for real-time satellite position updates
"""
import logging
import asyncio
import json
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from ..models import get_db
from ..services.satellite_tracker import SatelliteTracker

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws/positions")
async def websocket_positions(websocket: WebSocket):
    """
    WebSocket endpoint for real-time satellite position updates.
    Sends position updates every 30 seconds.
    """
    await manager.connect(websocket)
    
    try:
        # Send initial positions immediately
        from ..models.database import SessionLocal
        db = SessionLocal()
        
        try:
            tracker = SatelliteTracker(db)
            positions = tracker.get_all_positions()
            
            await websocket.send_json({
                'type': 'positions',
                'data': positions,
                'timestamp': positions[0]['timestamp'] if positions else None
            })
            
            logger.info(f"Sent initial positions to client: {len(positions)} satellites")
            
        finally:
            db.close()
        
        # Keep connection alive and send updates periodically
        while True:
            try:
                # Wait for 30 seconds
                await asyncio.sleep(30)
                
                # Get fresh database session for updates
                db = SessionLocal()
                try:
                    tracker = SatelliteTracker(db)
                    positions = tracker.get_all_positions()
                    
                    await websocket.send_json({
                        'type': 'positions',
                        'data': positions,
                        'timestamp': positions[0]['timestamp'] if positions else None
                    })
                    
                    logger.info(f"Sent position update: {len(positions)} satellites")
                    
                finally:
                    db.close()
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket update loop: {e}")
                break
    
    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


@router.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics."""
    return {
        "active_connections": len(manager.active_connections)
    }


