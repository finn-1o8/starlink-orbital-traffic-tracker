from datetime import timedelta

import pytest
from skyfield.api import EarthSatellite, load

from app.models.database import SessionLocal
from app.services import eo_analyzer
from app.services.eo_analyzer import EOInterferenceAnalyzer
from app.services.satellite_tracker import SatelliteTracker
from tests.fixtures import ANALYSIS_TIME, LANDSAT_8, SENTINEL_2A


@pytest.fixture
def analyzer(seeded_db):
    db = SessionLocal()
    try:
        yield EOInterferenceAnalyzer(db, SatelliteTracker(db))
    finally:
        db.close()


def test_presets_expose_fov_and_catalogue_number():
    presets = EOInterferenceAnalyzer.presets()
    assert presets["sentinel-2a"]["norad_id"] == 40697
    assert presets["landsat-8"]["fov_degrees"] == 15.0


def test_preset_falls_back_when_celestrak_is_unreachable(analyzer, monkeypatch):
    monkeypatch.setattr(eo_analyzer, "fetch_tle_by_catnr", lambda norad_id: None)
    tle, fov, source = analyzer.resolve_eo_satellite(eo_preset="sentinel-2a")
    assert source == "fallback"
    assert tle.norad_id == 40697
    assert fov == 20.6


def test_preset_uses_live_elements_and_fov_override(analyzer, monkeypatch):
    monkeypatch.setattr(eo_analyzer, "fetch_tle_by_catnr", lambda norad_id: SENTINEL_2A)
    tle, fov, source = analyzer.resolve_eo_satellite(eo_preset="sentinel-2a", fov_override=12.5)
    assert source == "celestrak"
    assert tle.line1 == SENTINEL_2A.line1
    assert fov == 12.5


def test_unknown_preset_is_rejected(analyzer):
    with pytest.raises(ValueError):
        analyzer.resolve_eo_satellite(eo_preset="hubble")


def test_global_mode_has_one_window_per_orbit(analyzer):
    ts = load.timescale()
    eo_sat = EarthSatellite(LANDSAT_8.line1, LANDSAT_8.line2, LANDSAT_8.name, ts)
    windows = analyzer._passes(eo_sat, LANDSAT_8, 15.0, None, ANALYSIS_TIME, duration_hours=3)
    assert len(windows) == 2  # Landsat 8 orbits in ~99 min; 3 h holds one full orbit plus a partial one
    assert windows[0].end == windows[1].start
    assert windows[-1].end == ANALYSIS_TIME + timedelta(hours=3)


def test_region_mode_finds_passes_within_reach(analyzer):
    ts = load.timescale()
    eo_sat = EarthSatellite(LANDSAT_8.line1, LANDSAT_8.line2, LANDSAT_8.name, ts)
    region = {"lat": 51.5, "lon": -0.1, "radius_km": 2000}
    windows = analyzer._passes(eo_sat, LANDSAT_8, 15.0, region, ANALYSIS_TIME, duration_hours=24)
    assert windows, "a sun-synchronous imager reaches within 2000 km of London every day"
    for w in windows:
        assert w.end > w.start
        assert w.max_elevation_deg is not None


def test_full_analysis_reports_consistent_counts(analyzer):
    result = analyzer.analyze_interference(
        eo_satellite_tle={"name": "LANDSAT 8", "line1": LANDSAT_8.line1, "line2": LANDSAT_8.line2, "fov_degrees": 15.0},
        start_time=ANALYSIS_TIME,
        duration_hours=6,
        sample_seconds=30,
    )
    assert result["model"] == "nadir-cone"
    assert result["eo_tle_source"] == "custom"
    assert result["total_passes"] == result["interfered_passes"] + result["clean_passes"]
    assert result["total_passes"] >= 3
    for event in result["interference_events"]:
        for hit in event["interfering_satellites"]:
            assert hit["min_angle_deg"] <= 7.5
            assert hit["range_km"] > 0
