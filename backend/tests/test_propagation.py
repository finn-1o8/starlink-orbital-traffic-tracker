"""Checks for the vectorised propagation helpers against Skyfield and synthetic geometry."""
from datetime import timedelta

import numpy as np
from skyfield.api import EarthSatellite, load, wgs84

from app.services import propagation as prop
from tests.fixtures import ISS, ISS_EPOCH


def test_geodetic_positions_match_skyfield():
    ts = load.timescale()
    sat = EarthSatellite(ISS.line1, ISS.line2, ISS.name, ts)
    for minutes in (0, 17, 45, 90):
        when = ISS_EPOCH + timedelta(minutes=minutes)
        ours = prop.geodetic_positions([ISS], when)
        assert len(ours) == 1
        sub = wgs84.subpoint(sat.at(ts.from_datetime(when)))
        assert abs(ours[0]["lat"] - sub.latitude.degrees) < 0.01
        dlon = (ours[0]["lon"] - sub.longitude.degrees + 180) % 360 - 180
        assert abs(dlon) < 0.01
        assert abs(ours[0]["alt_km"] - sub.elevation.km) < 1.0
        assert 7.0 < ours[0]["velocity_km_s"] < 8.0


def test_ground_track_is_continuous():
    times = [ISS_EPOCH + timedelta(seconds=60 * i) for i in range(10)]
    points = prop.ground_track(ISS, times)
    assert len(points) == 10
    for a, b in zip(points, points[1:]):
        assert abs(a["lat"] - b["lat"]) < 5.0  # a LEO ground track moves under 4 deg/min


def test_orbital_period_is_about_93_minutes():
    assert 92.0 < prop.orbital_period_minutes(ISS) < 94.0


def test_unparsable_tles_are_skipped():
    bad = prop.TLE(1, "BAD", "garbage", "garbage")
    assert prop.geodetic_positions([bad], ISS_EPOCH) == []
    assert prop.geodetic_positions([bad, ISS], ISS_EPOCH)[0]["norad_id"] == 25544


def test_satellite_set_is_reusable():
    sat_set = prop.SatelliteSet([ISS])
    first = sat_set.propagate([ISS_EPOCH])
    second = sat_set.propagate([ISS_EPOCH + timedelta(minutes=1)])
    assert first.ok.all() and second.ok.all()
    assert np.linalg.norm(first.r_teme[0, 0] - second.r_teme[0, 0]) > 400  # ~7.7 km/s for 60 s


def test_satellites_in_fov_geometry():
    sensor = np.array([[7000.0, 0.0, 0.0]])  # one time step, nadir points to -x
    targets = np.array(
        [
            [[6800.0, 0.0, 0.0]],  # directly below: angle 0
            [[6800.0, 500.0, 0.0]],  # below but ~68 deg off nadir
            [[-6800.0, 0.0, 0.0]],  # other side of the Earth: angle 180
            [[7200.0, 0.0, 0.0]],  # above the sensor
        ]
    )
    ok = np.ones((4, 1), dtype=bool)
    in_fov, angle, rng = prop.satellites_in_fov(sensor, targets, ok, half_angle_deg=10.0)
    assert in_fov[:, 0].tolist() == [True, False, False, False]
    assert abs(angle[0, 0]) < 1e-6
    assert abs(rng[0, 0] - 200.0) < 1e-6
    assert 67.0 < angle[1, 0] < 69.0
