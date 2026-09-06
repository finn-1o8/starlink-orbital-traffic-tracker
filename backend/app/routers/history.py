"""Historical constellation statistics."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from ..models import HistoricalSnapshot, get_db

router = APIRouter()


class SnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    snapshot_date: datetime
    total_satellites: int
    altitude_band_340_360: Optional[int] = 0
    altitude_band_500_570: Optional[int] = 0
    altitude_band_1100_1325: Optional[int] = 0


@router.get("/history/snapshots", response_model=list[SnapshotOut])
async def get_snapshots(
    days: int = Query(30, ge=1, le=365, description="How many days back to return"),
    db: Session = Depends(get_db),
):
    """Daily snapshots of satellite counts per shell, oldest first."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    return (
        db.query(HistoricalSnapshot)
        .filter(HistoricalSnapshot.snapshot_date >= since)
        .order_by(HistoricalSnapshot.snapshot_date)
        .all()
    )
