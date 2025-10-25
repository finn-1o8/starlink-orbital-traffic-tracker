"""
Orbital congestion analysis endpoints
"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..models import get_db
from ..services.satellite_tracker import SatelliteTracker
from ..services.congestion_analyzer import CongestionAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter()


class CongestionMetrics(BaseModel):
    total_satellites: int
    density_per_1000km3: float
    mean_spacing_km: float
    closest_approach_km: float
    region: Optional[dict] = None
    altitude_band: Optional[dict] = None
    timestamp: str


@router.get("/congestion", response_model=CongestionMetrics)
async def analyze_congestion(
    lat: float = Query(..., description="Latitude of region center", ge=-90, le=90),
    lon: float = Query(..., description="Longitude of region center", ge=-180, le=180),
    radius_km: float = Query(500, description="Region radius in km", ge=10, le=5000),
    alt_min: float = Query(500, description="Minimum altitude in km", ge=100, le=2000),
    alt_max: float = Query(600, description="Maximum altitude in km", ge=100, le=2000),
    time: Optional[str] = Query(None, description="ISO 8601 timestamp"),
    db: Session = Depends(get_db)
):
    """
    Analyze orbital congestion for a specific region and altitude band.
    
    Args:
        lat: Latitude of region center
        lon: Longitude of region center
        radius_km: Region radius in km
        alt_min: Minimum altitude in km
        alt_max: Maximum altitude in km
        time: Optional ISO 8601 timestamp
        
    Returns:
        Congestion metrics
    """
    try:
        # Validate altitude range
        if alt_min >= alt_max:
            raise HTTPException(status_code=400, detail="alt_min must be less than alt_max")
        
        # Parse time if provided
        target_time = None
        if time:
            try:
                target_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid time format. Use ISO 8601.")
        
        # Analyze congestion
        tracker = SatelliteTracker(db)
        analyzer = CongestionAnalyzer(db, tracker)
        
        metrics = analyzer.analyze_region(
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            alt_min=alt_min,
            alt_max=alt_max,
            time=target_time
        )
        
        logger.info(f"Congestion analysis complete: {metrics['total_satellites']} satellites in region")
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze congestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/congestion/heatmap")
async def get_density_heatmap(
    alt_min: float = Query(500, description="Minimum altitude in km"),
    alt_max: float = Query(600, description="Maximum altitude in km"),
    grid_size: int = Query(5, description="Grid cell size in degrees", ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    Get global satellite density heatmap data.
    
    Args:
        alt_min: Minimum altitude in km
        alt_max: Maximum altitude in km
        grid_size: Grid cell size in degrees
        
    Returns:
        Grid cells with density values
    """
    try:
        tracker = SatelliteTracker(db)
        analyzer = CongestionAnalyzer(db, tracker)
        
        heatmap_data = analyzer.get_global_density_map(
            alt_min=alt_min,
            alt_max=alt_max,
            grid_size=grid_size
        )
        
        logger.info(f"Generated heatmap with {len(heatmap_data)} grid cells")
        return {
            "grid_size": grid_size,
            "altitude_band": {"min_km": alt_min, "max_km": alt_max},
            "cells": heatmap_data
        }
        
    except Exception as e:
        logger.error(f"Failed to generate heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/congestion/altitude-distribution")
async def get_altitude_distribution(
    db: Session = Depends(get_db)
):
    """
    Get distribution of satellites across altitude bands.
    
    Returns:
        Satellite counts per altitude band
    """
    try:
        tracker = SatelliteTracker(db)
        analyzer = CongestionAnalyzer(db, tracker)
        
        distribution = analyzer.get_altitude_distribution()
        
        logger.info(f"Altitude distribution: {distribution['total']} total satellites")
        return distribution
        
    except Exception as e:
        logger.error(f"Failed to get altitude distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


