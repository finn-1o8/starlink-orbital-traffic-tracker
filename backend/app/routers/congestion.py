"""Orbital congestion endpoints."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models import get_db
from ..services.congestion_analyzer import CongestionAnalyzer
from ..services.satellite_tracker import SatelliteTracker

router = APIRouter()


class CongestionMetrics(BaseModel):
    total_satellites: int
    density_per_1000km3: float
    mean_spacing_km: float
    closest_approach_km: float
    region: Optional[dict] = None
    altitude_band: Optional[dict] = None
    timestamp: str


def _analyzer(db: Session) -> CongestionAnalyzer:
    return CongestionAnalyzer(db, SatelliteTracker(db))


@router.get("/congestion", response_model=CongestionMetrics)
async def analyze_congestion(
    lat: float = Query(..., description="Latitude of region centre", ge=-90, le=90),
    lon: float = Query(..., description="Longitude of region centre", ge=-180, le=180),
    radius_km: float = Query(500, description="Region radius in km", ge=10, le=5000),
    alt_min: float = Query(500, description="Minimum altitude in km", ge=100, le=3000),
    alt_max: float = Query(600, description="Maximum altitude in km", ge=100, le=3000),
    time: Optional[datetime] = Query(None, description="ISO 8601 timestamp (default: now)"),
    db: Session = Depends(get_db),
):
    """Count, density, spacing and closest approach inside a region and altitude band."""
    if alt_min >= alt_max:
        raise HTTPException(status_code=400, detail="alt_min must be less than alt_max")
    return await run_in_threadpool(_analyzer(db).analyze_region, lat, lon, radius_km, alt_min, alt_max, time)


@router.get("/congestion/heatmap")
async def get_density_heatmap(
    alt_min: float = Query(500, description="Minimum altitude in km", ge=100, le=3000),
    alt_max: float = Query(600, description="Maximum altitude in km", ge=100, le=3000),
    grid_size: int = Query(5, description="Grid cell size in degrees", ge=1, le=10),
    db: Session = Depends(get_db),
):
    """Satellite counts per grid cell for an altitude band."""
    if alt_min >= alt_max:
        raise HTTPException(status_code=400, detail="alt_min must be less than alt_max")
    cells = await run_in_threadpool(_analyzer(db).get_global_density_map, alt_min, alt_max, grid_size)
    return {"grid_size": grid_size, "altitude_band": {"min_km": alt_min, "max_km": alt_max}, "cells": cells}


@router.get("/congestion/altitude-distribution")
async def get_altitude_distribution(db: Session = Depends(get_db)):
    """Satellite counts per Starlink shell."""
    return await run_in_threadpool(_analyzer(db).get_altitude_distribution)
