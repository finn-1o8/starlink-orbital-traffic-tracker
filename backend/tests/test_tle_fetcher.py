from datetime import datetime, timedelta, timezone

from app.models.database import SessionLocal
from app.models.satellite import Satellite
from app.services.tle_fetcher import TLEFetcher, parse_tle_epoch, parse_tle_text, tle_checksum_ok
from tests.fixtures import ISS, STARLINK_TLE_TEXT


def test_checksums_of_real_elements_validate():
    assert tle_checksum_ok(ISS.line1)
    assert tle_checksum_ok(ISS.line2)
    corrupted = ISS.line1[:-1] + str((int(ISS.line1[-1]) + 1) % 10)
    assert not tle_checksum_ok(corrupted)


def test_parse_tle_epoch():
    epoch = parse_tle_epoch(ISS.line1)
    expected = datetime(2026, 9, 6, 3, 26, 51, 861120, tzinfo=timezone.utc)
    assert abs(epoch - expected) < timedelta(milliseconds=1)
    assert parse_tle_epoch("1 garbage") is None


def test_parse_tle_text():
    parsed = parse_tle_text(STARLINK_TLE_TEXT)
    assert [p["norad_id"] for p in parsed] == [44714, 44718, 44723]
    assert parsed[0]["name"] == "STARLINK-1008"
    assert parsed[1]["epoch"].date() == datetime(2026, 9, 5).date()


def test_parse_tle_text_skips_malformed_blocks():
    text = "BROKEN\nnot a line\nstill not\n" + STARLINK_TLE_TEXT
    assert len(parse_tle_text(text)) == 3


def test_update_database_upserts(client):
    db = SessionLocal()
    try:
        fetcher = TLEFetcher(db)
        rows = parse_tle_text(STARLINK_TLE_TEXT)
        assert fetcher.update_database(rows) == 3
        rows[0]["name"] = "STARLINK-1008 (RENAMED)"
        assert fetcher.update_database(rows) == 3
        assert db.query(Satellite).count() == 3
        assert db.query(Satellite).filter_by(norad_id=44714).one().name == "STARLINK-1008 (RENAMED)"
        rows[0]["name"] = "STARLINK-1008"
        fetcher.update_database(rows)
    finally:
        db.close()
