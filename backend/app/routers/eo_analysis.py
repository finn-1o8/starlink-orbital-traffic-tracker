"""Earth-observation interference endpoints."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from ..models import get_db
from ..services.eo_analyzer import EOInterferenceAnalyzer
from ..services.satellite_tracker import SatelliteTracker

router = APIRouter()


class TargetRegion(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(100, ge=1, le=2000)


class CustomTLE(BaseModel):
    name: str = Field("Custom EO satellite", max_length=100)
    norad_id: Optional[int] = Field(None, ge=1)
    line1: str = Field(..., min_length=60, max_length=80)
    line2: str = Field(..., min_length=60, max_length=80)
    fov_degrees: Optional[float] = Field(None, gt=0, le=60)

    @field_validator("line1")
    @classmethod
    def _line1(cls, v: str) -> str:
        if not v.startswith("1 "):
            raise ValueError("line1 must start with '1 '")
        return v

    @field_validator("line2")
    @classmethod
    def _line2(cls, v: str) -> str:
        if not v.startswith("2 "):
            raise ValueError("line2 must start with '2 '")
        return v


class EOAnalysisRequest(BaseModel):
    eo_preset: Optional[str] = Field(None, description="One of the presets from /eo-analysis/presets")
    eo_satellite_tle: Optional[CustomTLE] = None
    target_region: Optional[TargetRegion] = None
    start_time: Optional[datetime] = Field(None, description="ISO 8601; default now")
    duration_hours: int = Field(24, ge=1, le=72)
    fov_angle_degrees: Optional[float] = Field(None, gt=0, le=60, description="Override the preset field of view")
    sample_seconds: int = Field(20, ge=5, le=120, description="Sampling step inside each pass")


class EOAnalysisResponse(BaseModel):
    eo_satellite: str
    eo_tle_source: str
    fov_degrees: float
    model: str
    sample_seconds: int
    analysis_period: dict
    target_region: Optional[dict]
    total_passes: int
    interfered_passes: int
    clean_passes: int
    clean_windows: list
    interference_events: list
    interference_percentage: float


@router.post("/eo-analysis", response_model=EOAnalysisResponse)
async def analyze_eo_interference(request: EOAnalysisRequest = Body(...), db: Session = Depends(get_db)):
    """
    Flag imaging passes during which Starlink satellites cross the EO sensor's
    nadir-pointed field-of-view cone. See the EOInterferenceAnalyzer docstring
    for the model and its simplifications.
    """
    if not request.eo_satellite_tle and not request.eo_preset:
        raise HTTPException(status_code=400, detail="Provide either eo_satellite_tle or eo_preset")
    if request.eo_preset and request.eo_preset not in EOInterferenceAnalyzer.presets():
        available = ", ".join(EOInterferenceAnalyzer.presets())
        raise HTTPException(status_code=400, detail=f"Unknown eo_preset. Available: {available}")

    tracker = SatelliteTracker(db)
    analyzer = EOInterferenceAnalyzer(db, tracker)
    try:
        return await run_in_threadpool(
            lambda: analyzer.analyze_interference(
                eo_satellite_tle=request.eo_satellite_tle.model_dump() if request.eo_satellite_tle else None,
                eo_preset=request.eo_preset,
                target_region=request.target_region.model_dump() if request.target_region else None,
                start_time=request.start_time,
                duration_hours=request.duration_hours,
                fov_angle_degrees=request.fov_angle_degrees,
                sample_seconds=request.sample_seconds,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/eo-analysis/presets")
async def get_eo_presets():
    """Available EO satellite presets."""
    presets = EOInterferenceAnalyzer.presets()
    return {"presets": presets, "count": len(presets)}
