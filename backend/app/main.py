"""
FastAPI Main Application
Orbital Traffic Impact Analyzer Backend
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv

from .models import init_db
from .routers import satellites, congestion, eo_analysis, websocket
from .utils.scheduler_tasks import setup_scheduler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Orbital Traffic Impact Analyzer API")
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Setup and start scheduler
    global scheduler
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API")
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="Orbital Traffic Impact Analyzer API",
    description="Real-time satellite tracking and orbital congestion analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(satellites.router, prefix="/api", tags=["satellites"])
app.include_router(congestion.router, prefix="/api", tags=["congestion"])
app.include_router(eo_analysis.router, prefix="/api", tags=["eo-analysis"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Orbital Traffic Impact Analyzer API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running if scheduler else False
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


