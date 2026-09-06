"""
Satellite position engine.

Thin layer between the database and the vectorised propagation helpers. A
tracker instance reads the catalogue once and reuses the parsed TLEs for every
call, so a request that needs several propagations only pays for one query.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models.satellite import Satellite
from . import propagation as prop

logger = logging.getLogger(__name__)


def _utc_now_or(time: Optional[datetime]) -> datetime:
    if time is None:
        return datetime.now(timezone.utc)
    return time if time.tzinfo else time.replace(tzinfo=timezone.utc)


class SatelliteTracker:
    def __init__(self, db: Session):
        self.db = db
        self._satellite_set: Optional[prop.SatelliteSet] = None

    def load_tles(self) -> list[prop.TLE]:
        return self.satellite_set().tles

    def satellite_set(self) -> prop.SatelliteSet:
        """Parsed catalogue, read from the database once per tracker instance."""
        if self._satellite_set is None:
            rows = self.db.query(Satellite).order_by(Satellite.norad_id).all()
            tles = [prop.TLE(r.norad_id, r.name, r.tle_line1, r.tle_line2) for r in rows]
            self._satellite_set = prop.SatelliteSet(tles)
            if len(self._satellite_set) != len(rows):
                logger.warning("%d of %d TLEs could not be parsed", len(rows) - len(self._satellite_set), len(rows))
        return self._satellite_set

    def get_all_positions(self, time: Optional[datetime] = None) -> list[dict]:
        """Geodetic position of every tracked satellite at ``time`` (default: now)."""
        time = _utc_now_or(time)
        positions = prop.geodetic_positions(self.satellite_set(), time)
        logger.debug("Computed %d positions at %s", len(positions), time.isoformat())
        return positions

    def _tle_for(self, norad_id: int) -> Optional[prop.TLE]:
        sat = self.db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
        if sat is None:
            return None
        return prop.TLE(sat.norad_id, sat.name, sat.tle_line1, sat.tle_line2)

    def get_position(self, norad_id: int, time: Optional[datetime] = None) -> Optional[dict]:
        tle = self._tle_for(norad_id)
        if tle is None:
            return None
        positions = prop.geodetic_positions([tle], _utc_now_or(time))
        return positions[0] if positions else None

    def get_orbit_path(self, norad_id: int, duration_minutes: int = 90, interval_seconds: int = 60) -> Optional[dict]:
        """Ground-track points for one satellite starting now."""
        tle = self._tle_for(norad_id)
        if tle is None:
            return None
        start = datetime.now(timezone.utc)
        count = max(2, (duration_minutes * 60) // interval_seconds)
        times = [start + timedelta(seconds=i * interval_seconds) for i in range(count)]
        return {
            "norad_id": tle.norad_id,
            "name": tle.name,
            "orbit_points": prop.ground_track(tle, times),
            "duration_minutes": duration_minutes,
        }
