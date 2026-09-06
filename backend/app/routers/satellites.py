"""Satellite catalogue and position endpoints."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from ..models import Satellite, get_db
from ..services.satellite_tracker import SatelliteTracker
from ..utils.cache import get_cached_positions, set_cached_positions

router = APIRouter()


class SatelliteInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    norad_id: int
    name: str
    constellation: str
    last_updated: Optional[datetime] = None


class SatellitePosition(BaseModel):
    norad_id: int
    name: str
    lat: float
    lon: float
    alt_km: float
    velocity_km_s: float
    timestamp: str


class OrbitPoint(BaseModel):
    lat: float
    lon: float
    alt_km: float
    timestamp: str


class OrbitPath(BaseModel):
    norad_id: int
    name: str
    orbit_points: list[OrbitPoint]
    duration_minutes: int


class SatelliteDetail(SatelliteInfo):
    epoch: Optional[datetime] = None
    current_position: Optional[SatellitePosition] = None


@router.get("/satellites", response_model=list[SatelliteInfo])
async def get_satellites(
    db: Session = Depends(get_db),
    constellation: Optional[str] = Query(None, description="Filter by constellation name"),
):
    """All tracked satellites with their metadata."""
    query = db.query(Satellite)
    if constellation:
        query = query.filter(Satellite.constellation == constellation.upper())
    return query.order_by(Satellite.norad_id).all()


@router.get("/satellites/positions", response_model=list[SatellitePosition])
async def get_satellite_positions(
    time: Optional[datetime] = Query(None, description="ISO 8601 timestamp (default: now)"),
    db: Session = Depends(get_db),
):
    """Geodetic position of every satellite. Current positions are served from cache when available."""
    if time is None:
        cached = get_cached_positions()
        if cached:
            return cached
    tracker = SatelliteTracker(db)
    positions = await run_in_threadpool(tracker.get_all_positions, time)
    if time is None:
        set_cached_positions(positions)
    return positions


@router.get("/satellites/{norad_id}/orbit", response_model=OrbitPath)
async def get_satellite_orbit(
    norad_id: int,
    duration: int = Query(90, description="Orbit duration in minutes", ge=10, le=180),
    db: Session = Depends(get_db),
):
    """Ground-track points for one satellite, starting now."""
    orbit = await run_in_threadpool(SatelliteTracker(db).get_orbit_path, norad_id, duration)
    if not orbit:
        raise HTTPException(status_code=404, detail=f"Satellite {norad_id} not found")
    return orbit


@router.get("/satellites/{norad_id}", response_model=SatelliteDetail)
async def get_satellite_info(norad_id: int, db: Session = Depends(get_db)):
    """Catalogue entry plus current position for one satellite."""
    satellite = db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
    if not satellite:
        raise HTTPException(status_code=404, detail=f"Satellite {norad_id} not found")
    position = await run_in_threadpool(SatelliteTracker(db).get_position, norad_id)
    return SatelliteDetail(
        norad_id=satellite.norad_id,
        name=satellite.name,
        constellation=satellite.constellation,
        last_updated=satellite.last_updated,
        epoch=satellite.epoch,
        current_position=position,
    )
