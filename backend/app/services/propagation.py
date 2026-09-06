"""
Vectorised SGP4 propagation and field-of-view geometry.

All heavy lifting is delegated to ``sgp4.api.SatrecArray`` (C++), which
propagates N satellites x M times in a single call. SGP4 returns positions in
the TEME frame; they are rotated to an Earth-fixed frame with Greenwich Mean
Sidereal Time and converted to WGS84 geodetic coordinates with NumPy.

The GMST-only rotation ignores polar motion and nutation. The resulting error
is on the order of tens of metres at LEO, far below what matters for
visualisation, density statistics, or sensor field-of-view geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Sequence

import numpy as np
from sgp4.api import Satrec, SatrecArray, jday

WGS84_A_KM = 6378.137
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)
MEAN_EARTH_RADIUS_KM = 6371.0

# Positions outside this band almost always come from stale TLEs of decayed
# objects and are dropped rather than plotted.
MIN_VALID_ALT_KM = 100.0
MAX_VALID_ALT_KM = 3000.0


@dataclass(frozen=True)
class TLE:
    """A two-line element set plus the identifiers the API exposes."""

    norad_id: int
    name: str
    line1: str
    line2: str


@dataclass
class PropagationResult:
    """Raw propagation output for a set of satellites over a set of times."""

    tles: list[TLE]  # row order of the arrays below
    r_teme: np.ndarray  # (n_sat, n_times, 3) km
    v_teme: np.ndarray  # (n_sat, n_times, 3) km/s
    ok: np.ndarray  # (n_sat, n_times) bool; False where SGP4 reported an error
    jd: np.ndarray  # (n_times,) Julian day (whole part)
    fr: np.ndarray  # (n_times,) Julian day (fraction)


def _as_utc(t: datetime) -> datetime:
    if t.tzinfo is None:
        return t.replace(tzinfo=timezone.utc)
    return t.astimezone(timezone.utc)


def julian_dates(times: Sequence[datetime]) -> tuple[np.ndarray, np.ndarray]:
    """Split datetimes into the (jd, fr) pair sgp4 expects."""
    jd = np.empty(len(times))
    fr = np.empty(len(times))
    for i, t in enumerate(times):
        t = _as_utc(t)
        jd[i], fr[i] = jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond * 1e-6)
    return jd, fr


def gmst_radians(jd: np.ndarray, fr: np.ndarray) -> np.ndarray:
    """Greenwich Mean Sidereal Time (IAU 1982, Vallado eq. 3-45), treating UTC as UT1."""
    t_ut1 = ((jd - 2451545.0) + fr) / 36525.0
    gmst_sec = (
        67310.54841
        + (876600.0 * 3600.0 + 8640184.812866) * t_ut1
        + 0.093104 * t_ut1**2
        - 6.2e-6 * t_ut1**3
    )
    return np.deg2rad((gmst_sec % 86400.0) / 240.0)


def teme_to_ecef(r_teme: np.ndarray, gmst: np.ndarray) -> np.ndarray:
    """Rotate TEME vectors of shape (..., n_times, 3) about z by GMST into an Earth-fixed frame."""
    c = np.cos(gmst)
    s = np.sin(gmst)
    x, y, z = r_teme[..., 0], r_teme[..., 1], r_teme[..., 2]
    return np.stack([c * x + s * y, -s * x + c * y, z], axis=-1)


def ecef_to_geodetic(r_ecef: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert Earth-fixed km vectors (..., 3) to WGS84 (lat_deg, lon_deg, alt_km)."""
    x, y, z = r_ecef[..., 0], r_ecef[..., 1], r_ecef[..., 2]
    lon = np.arctan2(y, x)
    p = np.hypot(x, y)
    lat = np.arctan2(z, p * (1.0 - WGS84_E2))
    alt = np.zeros_like(p)
    for _ in range(6):  # converges to sub-millimetre in a handful of iterations
        sin_lat = np.sin(lat)
        n = WGS84_A_KM / np.sqrt(1.0 - WGS84_E2 * sin_lat**2)
        near_pole = np.abs(lat) > np.deg2rad(89.9)
        with np.errstate(divide="ignore", invalid="ignore"):
            alt = np.where(near_pole, z / sin_lat - n * (1.0 - WGS84_E2), p / np.cos(lat) - n)
        lat = np.arctan2(z, p * (1.0 - WGS84_E2 * n / (n + alt)))
    return np.rad2deg(lat), np.rad2deg(lon), alt


def orbital_period_minutes(tle: TLE) -> float:
    """Orbital period derived from the TLE mean motion."""
    rec = Satrec.twoline2rv(tle.line1, tle.line2)
    return float(2.0 * np.pi / rec.no_kozai)  # no_kozai is rad/min


class SatelliteSet:
    """A parsed collection of TLEs that can be propagated repeatedly without re-parsing."""

    def __init__(self, tles: Iterable[TLE]):
        recs: list[Satrec] = []
        kept: list[TLE] = []
        for tle in tles:
            if not (tle.line1.startswith("1 ") and tle.line2.startswith("2 ")):
                continue
            try:
                recs.append(Satrec.twoline2rv(tle.line1, tle.line2))
            except Exception:  # sgp4 raises on malformed lines
                continue
            kept.append(tle)
        self.tles = kept
        self._array = SatrecArray(recs) if recs else None

    def __len__(self) -> int:
        return len(self.tles)

    def propagate(self, times: Sequence[datetime]) -> PropagationResult:
        """Propagate every satellite to every time. Rows with SGP4 errors are flagged in ``ok``."""
        jd, fr = julian_dates(times)
        n_t = len(times)
        if self._array is None:
            empty = np.zeros((0, n_t, 3))
            return PropagationResult([], empty, empty.copy(), np.zeros((0, n_t), dtype=bool), jd, fr)
        err, r, v = self._array.sgp4(jd, fr)
        ok = (err == 0) & np.isfinite(r).all(axis=-1)
        return PropagationResult(self.tles, r, v, ok, jd, fr)


def propagate(tles: Iterable[TLE], times: Sequence[datetime]) -> PropagationResult:
    """One-shot convenience wrapper around :class:`SatelliteSet`."""
    return SatelliteSet(tles).propagate(times)


def geodetic_positions(tles: Iterable[TLE] | SatelliteSet, time: datetime) -> list[dict]:
    """
    Position dictionaries for every satellite at one instant.

    This is the payload the REST endpoint and the WebSocket broadcaster send.
    """
    time = _as_utc(time)
    sat_set = tles if isinstance(tles, SatelliteSet) else SatelliteSet(tles)
    res = sat_set.propagate([time])
    if not res.tles:
        return []
    gmst = gmst_radians(res.jd, res.fr)
    r_ecef = teme_to_ecef(res.r_teme, gmst)[:, 0, :]
    lat, lon, alt = ecef_to_geodetic(r_ecef)
    speed = np.linalg.norm(res.v_teme[:, 0, :], axis=-1)
    valid = res.ok[:, 0] & (alt > MIN_VALID_ALT_KM) & (alt < MAX_VALID_ALT_KM)
    stamp = time.isoformat()
    return [
        {
            "norad_id": tle.norad_id,
            "name": tle.name,
            "lat": float(lat[i]),
            "lon": float(lon[i]),
            "alt_km": float(alt[i]),
            "velocity_km_s": float(speed[i]),
            "timestamp": stamp,
        }
        for i, tle in enumerate(res.tles)
        if valid[i]
    ]


def ground_track(tle: TLE, times: Sequence[datetime]) -> list[dict]:
    """Geodetic points of one satellite over a list of times (used for orbit paths)."""
    res = propagate([tle], times)
    if not res.tles:
        return []
    gmst = gmst_radians(res.jd, res.fr)
    r_ecef = teme_to_ecef(res.r_teme, gmst)[0]
    lat, lon, alt = ecef_to_geodetic(r_ecef)
    return [
        {
            "lat": float(lat[i]),
            "lon": float(lon[i]),
            "alt_km": float(alt[i]),
            "timestamp": _as_utc(t).isoformat(),
        }
        for i, t in enumerate(times)
        if res.ok[0, i]
    ]


def satellites_in_fov(
    r_sensor: np.ndarray,
    r_targets: np.ndarray,
    ok: np.ndarray,
    half_angle_deg: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Which targets sit inside a nadir-pointed sensor cone, per time step.

    Args:
        r_sensor:  (n_times, 3) sensor position, any inertial frame.
        r_targets: (n_sat, n_times, 3) target positions in the same frame.
        ok:        (n_sat, n_times) validity mask for the targets.
        half_angle_deg: half of the sensor's full field-of-view angle.

    A target is inside the cone when the angle between the nadir vector and the
    sensor-to-target vector is at most ``half_angle_deg`` and the target is
    closer than the point where that line of sight meets the Earth's surface,
    so it sits between the sensor and the scene rather than behind the planet.

    Returns:
        (in_fov, angle_deg, range_km), each of shape (n_sat, n_times).
    """
    sensor_radius = np.linalg.norm(r_sensor, axis=-1)  # (n_times,)
    nadir = -r_sensor / sensor_radius[:, None]
    d = r_targets - r_sensor[None, :, :]
    rng = np.linalg.norm(d, axis=-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        unit = d / rng[..., None]
        cos_angle = np.einsum("stk,tk->st", unit, nadir)
    angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    # Distance along the line of sight to the Earth's surface (smaller root of |S + t*u| = R).
    s_dot_u = np.einsum("tk,stk->st", r_sensor, unit)
    discriminant = s_dot_u**2 - (sensor_radius[None, :] ** 2 - MEAN_EARTH_RADIUS_KM**2)
    with np.errstate(invalid="ignore"):
        range_to_ground = -s_dot_u - np.sqrt(discriminant)
    hits_ground = discriminant >= 0

    in_fov = ok & np.isfinite(rng) & (angle <= half_angle_deg) & hits_ground & (rng < range_to_ground)
    return in_fov, angle, rng
