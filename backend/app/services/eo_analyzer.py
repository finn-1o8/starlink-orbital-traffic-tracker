"""
Earth-observation interference analysis.

Model
-----
An EO satellite images the ground through a nadir-pointed cone whose full
opening angle is the sensor's field of view. Starlink shells (340-570 km) sit
below the usual EO altitudes (600-800 km), so a Starlink satellite that passes
through that cone lies between the sensor and the scene and can appear in the
image. The analyser propagates the EO satellite and the whole Starlink
catalogue with SGP4 at a fixed sampling step and flags every sample at which a
Starlink satellite is inside the cone.

Simplifications, stated so the numbers are read correctly:

* The cone is always nadir-pointed. Side-looking instruments such as SAR are
  approximated as nadir cones.
* Crossings shorter than ``sample_seconds`` can be missed.
* The metric is purely geometric: no sun geometry, glint, or whether the
  sensor would actually resolve the object.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import numpy as np
from skyfield.api import EarthSatellite, load, wgs84
from sqlalchemy.orm import Session

from . import propagation as prop
from .eo_presets import PRESETS
from .satellite_tracker import SatelliteTracker
from .tle_fetcher import fetch_tle_by_catnr

logger = logging.getLogger(__name__)

EARTH_RADIUS_KM = 6371.0


@dataclass
class PassWindow:
    start: datetime
    end: datetime
    max_elevation_deg: Optional[float]

    @property
    def duration_minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60.0


class EOInterferenceAnalyzer:
    """Flags EO imaging passes during which Starlink satellites cross the sensor cone."""

    MAX_SAMPLES_PER_PASS = 120

    def __init__(self, db: Session, tracker: SatelliteTracker):
        self.db = db
        self.tracker = tracker
        self.ts = load.timescale()

    @staticmethod
    def presets() -> dict:
        return {
            key: {
                "name": preset.name,
                "norad_id": preset.norad_id,
                "fov_degrees": preset.fov_degrees,
                "note": preset.note,
            }
            for key, preset in PRESETS.items()
        }

    def resolve_eo_satellite(
        self,
        eo_preset: Optional[str] = None,
        eo_satellite_tle: Optional[dict] = None,
        fov_override: Optional[float] = None,
    ) -> tuple[prop.TLE, float, str]:
        """Return (tle, fov_degrees, source) where source is 'celestrak', 'fallback' or 'custom'."""
        if eo_preset:
            preset = PRESETS.get(eo_preset)
            if preset is None:
                raise ValueError(f"Unknown preset {eo_preset!r}. Available: {', '.join(PRESETS)}")
            live = fetch_tle_by_catnr(preset.norad_id)
            if live is not None:
                tle = prop.TLE(preset.norad_id, preset.name, live.line1, live.line2)
                source = "celestrak"
            else:
                tle = prop.TLE(preset.norad_id, preset.name, preset.fallback_line1, preset.fallback_line2)
                source = "fallback"
            fov = fov_override if fov_override is not None else preset.fov_degrees
            return tle, fov, source
        if eo_satellite_tle:
            tle = prop.TLE(
                int(eo_satellite_tle.get("norad_id") or 0),
                eo_satellite_tle.get("name") or "Custom EO satellite",
                eo_satellite_tle["line1"],
                eo_satellite_tle["line2"],
            )
            fov = fov_override if fov_override is not None else float(eo_satellite_tle.get("fov_degrees") or 5.0)
            return tle, fov, "custom"
        raise ValueError("Provide either eo_preset or eo_satellite_tle")

    def analyze_interference(
        self,
        *,
        eo_satellite_tle: Optional[dict] = None,
        eo_preset: Optional[str] = None,
        target_region: Optional[dict] = None,
        start_time: Optional[datetime] = None,
        duration_hours: int = 24,
        fov_angle_degrees: Optional[float] = None,
        sample_seconds: int = 20,
    ) -> dict:
        start_time = start_time or datetime.now(timezone.utc)
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        tle, fov, source = self.resolve_eo_satellite(eo_preset, eo_satellite_tle, fov_angle_degrees)
        try:
            eo_sat = EarthSatellite(tle.line1, tle.line2, tle.name, self.ts)
        except Exception as exc:
            raise ValueError(f"Invalid TLE data: {exc}") from exc

        passes = self._passes(eo_sat, tle, fov, target_region, start_time, duration_hours)
        starlink = self.tracker.satellite_set()
        eo_set = prop.SatelliteSet([tle])

        events: list[dict] = []
        clean: list[dict] = []
        for window in passes:
            hits = self._check_pass(eo_set, starlink, window, fov, sample_seconds)
            base = {
                "start": window.start.isoformat(),
                "end": window.end.isoformat(),
                "duration_minutes": round(window.duration_minutes, 1),
                "max_elevation": window.max_elevation_deg,
            }
            if hits:
                events.append({**base, "time": base["start"], "interfering_satellites": hits, "severity": len(hits)})
            else:
                clean.append(base)

        return {
            "eo_satellite": tle.name,
            "eo_tle_source": source,
            "fov_degrees": fov,
            "model": "nadir-cone",
            "sample_seconds": sample_seconds,
            "analysis_period": {
                "start": start_time.isoformat(),
                "end": (start_time + timedelta(hours=duration_hours)).isoformat(),
                "duration_hours": duration_hours,
            },
            "target_region": target_region,
            "total_passes": len(passes),
            "interfered_passes": len(events),
            "clean_passes": len(clean),
            "clean_windows": clean,
            "interference_events": events,
            "interference_percentage": round(len(events) / len(passes) * 100.0, 2) if passes else 0.0,
        }

    def _passes(
        self,
        eo_sat: EarthSatellite,
        tle: prop.TLE,
        fov_degrees: float,
        target_region: Optional[dict],
        start: datetime,
        duration_hours: int,
    ) -> list[PassWindow]:
        """
        Imaging windows within the analysis period.

        Without a target region every orbit is one window. With a region, a
        window is the contiguous time during which the sensor swath reaches the
        region: the sub-satellite point is within ``radius_km`` plus half the
        swath width of the region centre.
        """
        end = start + timedelta(hours=duration_hours)
        if not target_region:
            period = timedelta(minutes=prop.orbital_period_minutes(tle))
            windows: list[PassWindow] = []
            t = start
            while t < end:
                t_next = min(t + period, end)
                windows.append(PassWindow(t, t_next, None))
                t = t_next
            return windows

        location = wgs84.latlon(float(target_region["lat"]), float(target_region["lon"]))
        radius_km = float(target_region.get("radius_km") or 100.0)
        minutes = int(duration_hours * 60)
        times = [start + timedelta(minutes=i) for i in range(minutes + 1)]
        t_arr = self.ts.from_datetimes(times)

        geocentric = eo_sat.at(t_arr)
        subpoint = wgs84.subpoint(geocentric)
        swath_half_km = subpoint.elevation.km * np.tan(np.deg2rad(fov_degrees / 2.0))
        ground_km = _haversine_km(
            subpoint.latitude.degrees, subpoint.longitude.degrees, location.latitude.degrees, location.longitude.degrees
        )
        elevation = (eo_sat - location).at(t_arr).altaz()[0].degrees
        covered = ground_km <= radius_km + swath_half_km

        windows = []
        in_pass = False
        i0 = 0
        for i, inside in enumerate(covered):
            if inside and not in_pass:
                in_pass, i0 = True, i
            elif not inside and in_pass:
                in_pass = False
                windows.append(PassWindow(times[i0], times[i], float(np.max(elevation[i0:i]))))
        if in_pass:
            windows.append(PassWindow(times[i0], times[-1], float(np.max(elevation[i0:]))))
        return windows

    def _check_pass(
        self,
        eo_set: prop.SatelliteSet,
        starlink: prop.SatelliteSet,
        window: PassWindow,
        fov_degrees: float,
        sample_seconds: int,
    ) -> list[dict]:
        """Starlink satellites that enter the sensor cone at any sample within the window."""
        seconds = max((window.end - window.start).total_seconds(), float(sample_seconds))
        n = int(min(self.MAX_SAMPLES_PER_PASS, max(2, seconds // sample_seconds + 1)))
        times = [window.start + timedelta(seconds=seconds * k / (n - 1)) for k in range(n)]

        eo = eo_set.propagate(times)
        if not eo.tles or not eo.ok.all():
            raise ValueError("The EO satellite TLE cannot be propagated over the requested period")
        if len(starlink) == 0:
            return []
        sl = starlink.propagate(times)
        in_fov, angle, rng = prop.satellites_in_fov(eo.r_teme[0], sl.r_teme, sl.ok, fov_degrees / 2.0)

        hits = []
        for s in np.flatnonzero(in_fov.any(axis=1)):
            masked = np.where(in_fov[s], angle[s], np.inf)
            k = int(np.argmin(masked))
            hits.append(
                {
                    "norad_id": sl.tles[s].norad_id,
                    "name": sl.tles[s].name,
                    "min_angle_deg": round(float(angle[s, k]), 3),
                    "range_km": round(float(rng[s, k]), 1),
                    "at": times[k].isoformat(),
                }
            )
        hits.sort(key=lambda h: h["min_angle_deg"])
        return hits


def _haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))
