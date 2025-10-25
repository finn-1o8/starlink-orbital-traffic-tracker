"""
Satellite tracking endpoints
"""
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..models import get_db, Satellite
from ..services.satellite_tracker import SatelliteTracker
from ..utils.cache import get_cached_positions, set_cached_positions

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class SatelliteInfo(BaseModel):
    norad_id: int
    name: str
    constellation: str
    last_updated: datetime
    
    class Config:
        from_attributes = True


class SatellitePosition(BaseModel):
    satellite_id: int
    norad_id: int
    name: str
    lat: float
    lon: float
    alt_km: float
    velocity_km_s: float
    timestamp: str


class OrbitPath(BaseModel):
    norad_id: int
    name: str
    orbit_points: List[dict]
    duration_minutes: int


@router.get("/satellites", response_model=List[SatelliteInfo])
async def get_satellites(
    db: Session = Depends(get_db),
    constellation: Optional[str] = Query(None, description="Filter by constellation")
):
    """
    Get list of all tracked satellites with metadata.
    
    Args:
        constellation: Optional filter by constellation name
        
    Returns:
        List of satellite information
    """
    try:
        query = db.query(Satellite)
        
        if constellation:
            query = query.filter(Satellite.constellation == constellation.upper())
        
        satellites = query.all()
        
        logger.info(f"Retrieved {len(satellites)} satellites")
        return satellites
        
    except Exception as e:
        logger.error(f"Failed to retrieve satellites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/satellites/positions", response_model=List[SatellitePosition])
async def get_satellite_positions(
    time: Optional[str] = Query(None, description="ISO 8601 timestamp"),
    db: Session = Depends(get_db)
):
    """
    Get current positions of all satellites.
    
    Args:
        time: Optional ISO 8601 timestamp (default: now)
        
    Returns:
        List of satellite positions
    """
    try:
        # Parse time if provided
        target_time = None
        if time:
            try:
                target_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid time format. Use ISO 8601.")
        
        # Check cache first (only for current time)
        if target_time is None:
            cached = get_cached_positions()
            if cached:
                logger.info("Returning cached positions")
                return cached
        
        # Calculate positions
        tracker = SatelliteTracker(db)
        positions = tracker.get_all_positions(target_time)
        
        # Cache if current time
        if target_time is None:
            set_cached_positions(positions)
        
        logger.info(f"Calculated {len(positions)} satellite positions")
        return positions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/satellites/{norad_id}/orbit", response_model=OrbitPath)
async def get_satellite_orbit(
    norad_id: int,
    duration: int = Query(90, description="Orbit duration in minutes", ge=10, le=180),
    db: Session = Depends(get_db)
):
    """
    Get orbit path points for a specific satellite.
    
    Args:
        norad_id: NORAD catalog number
        duration: Orbit duration in minutes (default: 90)
        
    Returns:
        Orbit path with position points
    """
    try:
        tracker = SatelliteTracker(db)
        orbit_data = tracker.get_orbit_path(norad_id, duration_minutes=duration)
        
        if not orbit_data:
            raise HTTPException(status_code=404, detail=f"Satellite {norad_id} not found")
        
        logger.info(f"Calculated orbit for satellite {norad_id}")
        return orbit_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get orbit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/satellites/{norad_id}")
async def get_satellite_info(
    norad_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific satellite.
    
    Args:
        norad_id: NORAD catalog number
        
    Returns:
        Satellite information including current position
    """
    try:
        # Get satellite from database
        satellite = db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
        
        if not satellite:
            raise HTTPException(status_code=404, detail=f"Satellite {norad_id} not found")
        
        # Get current position
        tracker = SatelliteTracker(db)
        position = tracker.propagate_position(satellite.id)
        
        return {
            "norad_id": satellite.norad_id,
            "name": satellite.name,
            "constellation": satellite.constellation,
            "epoch": satellite.epoch.isoformat() if satellite.epoch else None,
            "last_updated": satellite.last_updated.isoformat() if satellite.last_updated else None,
            "current_position": position
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get satellite info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


