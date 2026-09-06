from app.services import eo_analyzer
from tests.fixtures import ANALYSIS_TIME, LANDSAT_8, SENTINEL_2A

TIME = ANALYSIS_TIME.isoformat().replace("+00:00", "Z")


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_catalogue_and_positions(client, seeded_db):
    response = client.get("/api/satellites")
    assert response.status_code == 200
    assert [s["norad_id"] for s in response.json()] == [44714, 44718, 44723]

    response = client.get("/api/satellites/positions", params={"time": TIME})
    assert response.status_code == 200
    positions = response.json()
    assert len(positions) == 3
    for p in positions:
        assert -90 <= p["lat"] <= 90 and -180 <= p["lon"] <= 180
        assert 300 < p["alt_km"] < 700
        assert 7.0 < p["velocity_km_s"] < 8.0

    # "now" may be far from the element epochs when this test runs later; only the contract is checked.
    response = client.get("/api/satellites/positions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_orbit_and_detail(client, seeded_db):
    response = client.get("/api/satellites/44714/orbit", params={"duration": 30})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "STARLINK-1008"
    assert len(body["orbit_points"]) <= 30

    response = client.get("/api/satellites/44714")
    assert response.status_code == 200
    assert response.json()["constellation"] == "STARLINK"

    assert client.get("/api/satellites/1/orbit").status_code == 404
    assert client.get("/api/satellites/1").status_code == 404


def test_congestion_endpoints(client, seeded_db):
    params = {"lat": 0, "lon": 0, "radius_km": 5000, "alt_min": 100, "alt_max": 3000, "time": TIME}
    response = client.get("/api/congestion", params=params)
    assert response.status_code == 200
    assert response.json()["total_satellites"] >= 0

    bad = client.get("/api/congestion", params={"lat": 0, "lon": 0, "alt_min": 600, "alt_max": 500})
    assert bad.status_code == 400

    response = client.get("/api/congestion/heatmap", params={"alt_min": 100, "alt_max": 3000, "grid_size": 10})
    assert response.status_code == 200
    assert response.json()["grid_size"] == 10

    response = client.get("/api/congestion/altitude-distribution")
    assert response.status_code == 200
    assert set(response.json()["altitude_bands"]) == {"340-360", "500-570", "1100-1325", "other"}


def test_eo_presets(client):
    response = client.get("/api/eo-analysis/presets")
    assert response.status_code == 200
    assert "sentinel-2a" in response.json()["presets"]


def test_eo_analysis_with_preset(client, seeded_db, monkeypatch):
    monkeypatch.setattr(eo_analyzer, "fetch_tle_by_catnr", lambda norad_id: SENTINEL_2A)
    response = client.post(
        "/api/eo-analysis",
        json={"eo_preset": "sentinel-2a", "duration_hours": 3, "start_time": TIME, "sample_seconds": 60},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["eo_tle_source"] == "celestrak"
    assert body["fov_degrees"] == 20.6
    assert body["total_passes"] == body["interfered_passes"] + body["clean_passes"] >= 1


def test_eo_analysis_with_custom_tle_and_region(client, seeded_db):
    response = client.post(
        "/api/eo-analysis",
        json={
            "eo_satellite_tle": {
                "name": "LANDSAT 8",
                "line1": LANDSAT_8.line1,
                "line2": LANDSAT_8.line2,
                "fov_degrees": 15,
            },
            "target_region": {"lat": 51.5, "lon": -0.1, "radius_km": 2000},
            "duration_hours": 24,
            "start_time": TIME,
            "sample_seconds": 60,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["eo_tle_source"] == "custom"
    assert body["target_region"]["radius_km"] == 2000
    assert body["total_passes"] >= 1


def test_eo_analysis_validation(client):
    assert client.post("/api/eo-analysis", json={"eo_preset": "sentinel-2a", "duration_hours": 1000}).status_code == 422
    assert client.post("/api/eo-analysis", json={}).status_code == 400
    assert client.post("/api/eo-analysis", json={"eo_preset": "hubble"}).status_code == 400
    bad_tle = {"eo_satellite_tle": {"line1": "x" * 69, "line2": "2 " + "0" * 67}}
    assert client.post("/api/eo-analysis", json=bad_tle).status_code == 422


def test_history_snapshots(client, seeded_db):
    from app.utils.scheduler_tasks import create_daily_snapshot

    create_daily_snapshot()
    response = client.get("/api/history/snapshots", params={"days": 7})
    assert response.status_code == 200
    snapshots = response.json()
    assert len(snapshots) == 1
    assert 0 <= snapshots[0]["total_satellites"] <= 3
