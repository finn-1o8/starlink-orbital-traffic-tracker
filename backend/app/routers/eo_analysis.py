"""
Earth Observation interference analysis endpoints
"""
import logging
from datetime import datetime
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..models import get_db
from ..services.satellite_tracker import SatelliteTracker
from ..services.eo_analyzer import EOInterferenceAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter()


class EOAnalysisRequest(BaseModel):
    eo_satellite_tle: Optional[Dict] = None
    eo_preset: Optional[str] = None
    target_region: Optional[Dict] = None
    start_time: Optional[str] = None
    duration_hours: int = 24
    fov_angle_degrees: float = 5.0


class EOAnalysisResponse(BaseModel):
    eo_satellite: str
    analysis_period: dict
    target_region: Optional[dict]
    total_passes: int
    interfered_passes: int
    clean_passes: int
    clean_windows: list
    interference_events: list
    interference_percentage: float


@router.post("/eo-analysis", response_model=EOAnalysisResponse)
async def analyze_eo_interference(
    request: EOAnalysisRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Analyze Starlink interference with EO satellite imaging operations.
    
    Args:
        request: Analysis parameters including EO satellite, target region, and timeframe
        
    Returns:
        Interference analysis results with clean imaging windows
    """
    try:
        # Parse start time if provided
        start_time = None
        if request.start_time:
            try:
                start_time = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid time format. Use ISO 8601.")
        
        # Validate request
        if not request.eo_satellite_tle and not request.eo_preset:
            raise HTTPException(
                status_code=400, 
                detail="Must provide either eo_satellite_tle or eo_preset"
            )
        
        if request.eo_preset and request.eo_preset not in EOInterferenceAnalyzer.PRESETS:
            available = ', '.join(EOInterferenceAnalyzer.PRESETS.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Invalid eo_preset. Available: {available}"
            )
        
        # Perform analysis
        tracker = SatelliteTracker(db)
        analyzer = EOInterferenceAnalyzer(db, tracker)
        
        result = analyzer.analyze_interference(
            eo_satellite_tle=request.eo_satellite_tle,
            eo_preset=request.eo_preset,
            target_region=request.target_region,
            start_time=start_time,
            duration_hours=request.duration_hours,
            fov_angle_degrees=request.fov_angle_degrees
        )
        
        logger.info(
            f"EO analysis complete: {result['interfered_passes']}/{result['total_passes']} "
            f"passes interfered ({result['interference_percentage']}%)"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze EO interference: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/eo-analysis/presets")
async def get_eo_presets():
    """
    Get available EO satellite presets.
    
    Returns:
        List of available preset names and their details
    """
    try:
        presets = {}
        for key, value in EOInterferenceAnalyzer.PRESETS.items():
            presets[key] = {
                'name': value['name'],
                'fov_degrees': value['fov_degrees']
            }
        
        return {
            "presets": presets,
            "count": len(presets)
        }
        
    except Exception as e:
        logger.error(f"Failed to get presets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


