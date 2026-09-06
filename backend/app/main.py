"""FastAPI application: Orbital Traffic Impact Analyzer backend."""
import asyncio
import contextlib
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import init_db
from .routers import congestion, eo_analysis, history, satellites, websocket
from .utils.scheduler_tasks import setup_scheduler

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

API_VERSION = "1.1.0"


def _flag(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Orbital Traffic Impact Analyzer API")
    init_db()

    scheduler = None
    if _flag("SCHEDULER_ENABLED", True):
        scheduler = setup_scheduler()
        scheduler.start()
    app.state.scheduler = scheduler

    broadcaster = None
    if _flag("WS_BROADCAST_ENABLED", True):
        interval = float(os.getenv("WS_UPDATE_SECONDS", "5"))
        broadcaster = asyncio.create_task(websocket.broadcast_positions_forever(interval))

    try:
        yield
    finally:
        logger.info("Shutting down")
        if broadcaster:
            broadcaster.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await broadcaster
        if scheduler:
            scheduler.shutdown(wait=False)


app = FastAPI(
    title="Orbital Traffic Impact Analyzer API",
    description="Starlink tracking, orbital congestion statistics and EO field-of-view interference analysis",
    version=API_VERSION,
    lifespan=lifespan,
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173").split(",")
    if origin.strip()
]
logger.info("CORS allowed origins: %s", cors_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(satellites.router, prefix="/api", tags=["satellites"])
app.include_router(congestion.router, prefix="/api", tags=["congestion"])
app.include_router(eo_analysis.router, prefix="/api", tags=["eo-analysis"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])


@app.get("/")
async def root():
    return {"name": app.title, "version": API_VERSION, "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    scheduler = getattr(app.state, "scheduler", None)
    return {
        "status": "healthy",
        "version": API_VERSION,
        "scheduler_running": bool(scheduler and scheduler.running),
        "websocket_clients": websocket.manager.count,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=_flag("DEBUG", False),
        log_level="info",
    )
