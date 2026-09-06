"""
WebSocket position feed.

Positions are computed once per interval by a single background task (in a
worker thread, so the event loop never blocks) and fanned out to every
connected client. Clients only receive; anything they send is ignored.
"""
import asyncio
import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool

from ..models.database import SessionLocal
from ..services.satellite_tracker import SatelliteTracker
from ..utils.cache import get_cached_positions, set_cached_positions

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173").split(",")
    if origin.strip()
]


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()

    @property
    def count(self) -> int:
        return len(self.active_connections)

    async def connect(self, websocket: WebSocket) -> bool:
        """Accept the socket unless it comes from a browser origin that is not allowed."""
        origin = websocket.headers.get("origin")
        if origin and origin not in ALLOWED_ORIGINS:
            logger.warning("Rejected WebSocket from origin %s", origin)
            await websocket.close(code=1008, reason="Origin not allowed")
            return False
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("WebSocket client connected (%d total)", self.count)
        return True

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        logger.info("WebSocket client disconnected (%d total)", self.count)

    async def broadcast(self, message: dict) -> None:
        dead = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:  # noqa: BLE001 - a failed send means the client is gone
                dead.append(connection)
        for connection in dead:
            self.disconnect(connection)


manager = ConnectionManager()


def _compute_positions() -> list[dict]:
    db = SessionLocal()
    try:
        positions = SatelliteTracker(db).get_all_positions()
        set_cached_positions(positions)
        return positions
    finally:
        db.close()


def _message(positions: list[dict]) -> dict:
    return {
        "type": "positions",
        "data": positions,
        "timestamp": positions[0]["timestamp"] if positions else datetime.now(timezone.utc).isoformat(),
    }


async def broadcast_positions_forever(interval_seconds: float) -> None:
    """Background task started from the application lifespan."""
    logger.info("Position broadcaster running every %.1fs", interval_seconds)
    while True:
        try:
            if manager.count:
                positions = await run_in_threadpool(_compute_positions)
                await manager.broadcast(_message(positions))
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("Position broadcast failed")
        await asyncio.sleep(interval_seconds)


@router.websocket("/ws/positions")
async def websocket_positions(websocket: WebSocket):
    """Send the latest positions immediately, then every broadcast interval."""
    if not await manager.connect(websocket):
        return
    try:
        positions = get_cached_positions() or await run_in_threadpool(_compute_positions)
        await websocket.send_json(_message(positions))
        while True:
            await websocket.receive_text()  # keeps the connection open until the client leaves
    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001
        logger.exception("WebSocket error")
    finally:
        manager.disconnect(websocket)


@router.get("/ws/stats")
async def websocket_stats():
    return {"active_connections": manager.count}
