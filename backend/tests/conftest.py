"""Shared fixtures: an isolated SQLite database, no scheduler, no broadcaster, no Redis."""
import os
import pathlib
import tempfile

_TMP = pathlib.Path(tempfile.mkdtemp(prefix="orbital-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'test.db').as_posix()}"
os.environ["SCHEDULER_ENABLED"] = "false"
os.environ["WS_BROADCAST_ENABLED"] = "false"
os.environ["REDIS_URL"] = "redis://127.0.0.1:6399/0"  # nothing listens here, so caching is disabled

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session")
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def seeded_db(client):
    """Load the three Starlink fixtures into the catalogue once per session."""
    from app.models.database import SessionLocal
    from app.services.tle_fetcher import TLEFetcher, parse_tle_text
    from tests.fixtures import STARLINK_TLE_TEXT

    db = SessionLocal()
    try:
        assert TLEFetcher(db).update_database(parse_tle_text(STARLINK_TLE_TEXT)) == 3
    finally:
        db.close()
    return True
