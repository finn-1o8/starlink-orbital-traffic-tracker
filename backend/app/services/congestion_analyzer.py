"""
Orbital congestion statistics: counts, density, spacing, closest approach.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import numpy as np
from sqlalchemy.orm import Session

from .satellite_tracker import SatelliteTracker

logger = logging.getLogger(__name__)

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km; accepts scalars or NumPy arrays."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def _to_cartesian_km(lat_deg: np.ndarray, lon_deg: np.ndarray, alt_km: np.ndarray) -> np.ndarray:
    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)
    r = EARTH_RADIUS_KM + alt_km
    return np.stack([r * np.cos(lat) * np.cos(lon), r * np.cos(lat) * np.sin(lon), r * np.sin(lat)], axis=1)


class CongestionAnalyzer:
    def __init__(self, db: Session, tracker: SatelliteTracker):
        self.db = db
        self.tracker = tracker

    def analyze_region(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        alt_min: float,
        alt_max: float,
        time: Optional[datetime] = None,
    ) -> dict:
        """
        Congestion inside a cylinder: a ground-projected disc of ``radius_km``
        around (lat, lon) between ``alt_min`` and ``alt_max``. The disc is treated
        as flat for the volume estimate, which is fine for radii up to a few
        thousand kilometres.
        """
        time = time or datetime.now(timezone.utc)
        positions = self.tracker.get_all_positions(time)
        if positions:
            arr_lat = np.array([p["lat"] for p in positions])
            arr_lon = np.array([p["lon"] for p in positions])
            arr_alt = np.array([p["alt_km"] for p in positions])
            mask = (arr_alt >= alt_min) & (arr_alt <= alt_max) & (haversine_km(lat, lon, arr_lat, arr_lon) <= radius_km)
            region_positions = [p for p, keep in zip(positions, mask) if keep]
        else:
            region_positions = []

        total = len(region_positions)
        result = {
            "total_satellites": total,
            "density_per_1000km3": 0.0,
            "mean_spacing_km": 0.0,
            "closest_approach_km": 0.0,
            "region": {"lat": lat, "lon": lon, "radius_km": radius_km},
            "altitude_band": {"min_km": alt_min, "max_km": alt_max},
            "timestamp": time.isoformat(),
        }
        if total == 0:
            return result

        volume_km3 = np.pi * radius_km**2 * (alt_max - alt_min)
        result["density_per_1000km3"] = round(total / volume_km3 * 1000.0, 4)
        result["mean_spacing_km"] = round((volume_km3 / total) ** (1.0 / 3.0), 2) if total > 1 else 0.0
        result["closest_approach_km"] = round(self._closest_approach(region_positions), 2)
        return result

    def get_global_density_map(
        self,
        alt_min: float,
        alt_max: float,
        grid_size: int = 5,
        time: Optional[datetime] = None,
    ) -> list[dict]:
        """Satellite counts per ``grid_size``-degree cell for the given altitude band."""
        time = time or datetime.now(timezone.utc)
        positions = self.tracker.get_all_positions(time)
        if not positions:
            return []
        arr = np.array([(p["lat"], p["lon"], p["alt_km"]) for p in positions])
        in_band = arr[(arr[:, 2] >= alt_min) & (arr[:, 2] <= alt_max)]
        if in_band.size == 0:
            return []
        lat_edges = np.arange(-90, 90 + grid_size, grid_size)
        lon_edges = np.arange(-180, 180 + grid_size, grid_size)
        counts, _, _ = np.histogram2d(in_band[:, 0], in_band[:, 1], bins=[lat_edges, lon_edges])
        cells = []
        for i, j in zip(*np.nonzero(counts)):
            cells.append(
                {
                    "lat": float(lat_edges[i] + grid_size / 2.0),
                    "lon": float(lon_edges[j] + grid_size / 2.0),
                    "count": int(counts[i, j]),
                }
            )
        return cells

    def get_altitude_distribution(self) -> dict:
        """Counts in the three Starlink shells plus everything else."""
        positions = self.tracker.get_all_positions()
        bands = {"340-360": 0, "500-570": 0, "1100-1325": 0, "other": 0}
        for p in positions:
            alt = p["alt_km"]
            if 340 <= alt <= 360:
                bands["340-360"] += 1
            elif 500 <= alt <= 570:
                bands["500-570"] += 1
            elif 1100 <= alt <= 1325:
                bands["1100-1325"] += 1
            else:
                bands["other"] += 1
        return {
            "altitude_bands": bands,
            "total": len(positions),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _closest_approach(positions: list[dict]) -> float:
        """Smallest straight-line distance between any two satellites, in km."""
        if len(positions) < 2:
            return 0.0
        xyz = _to_cartesian_km(
            np.array([p["lat"] for p in positions]),
            np.array([p["lon"] for p in positions]),
            np.array([p["alt_km"] for p in positions]),
        )
        dists = np.linalg.norm(xyz[:, None, :] - xyz[None, :, :], axis=-1)
        np.fill_diagonal(dists, np.inf)
        return float(dists.min())
