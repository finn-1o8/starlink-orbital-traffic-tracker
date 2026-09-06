"""
TLE data from CelesTrak.

Starlink elements are pulled as one group file and upserted into the
database. Individual objects (the EO satellites used by the interference
analysis) are fetched by catalogue number and cached, so the analysis runs on
current orbits rather than hard-coded elements.
"""
from __future__ import annotations

import logging
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
from sqlalchemy.orm import Session

from ..models.satellite import Satellite
from ..utils.cache import cache_custom, get_cached
from .propagation import TLE

logger = logging.getLogger(__name__)

CELESTRAK_GP_URL = "https://celestrak.org/NORAD/elements/gp.php"
USER_AGENT = "starlink-orbital-traffic-tracker/1.0 (https://github.com/finn-1o8/starlink-orbital-traffic-tracker)"
EO_TLE_CACHE_SECONDS = 6 * 3600


def tle_checksum_ok(line: str) -> bool:
    """Validate the modulo-10 checksum in the last column of a TLE line."""
    if len(line) < 2 or not line[-1].isdigit():
        return False
    total = 0
    for ch in line[:-1]:
        if ch.isdigit():
            total += int(ch)
        elif ch == "-":
            total += 1
    return total % 10 == int(line[-1])


def parse_tle_epoch(line1: str) -> Optional[datetime]:
    """Epoch from TLE line 1 (YYDDD.DDDDDDDD in columns 19-32), or None if unreadable."""
    try:
        epoch_str = line1[18:32].strip()
        year = int(epoch_str[:2])
        year += 2000 if year < 57 else 1900
        day_of_year = float(epoch_str[2:])
        return datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)
    except (ValueError, IndexError):
        return None


def parse_tle_text(tle_text: str) -> list[dict]:
    """Parse three-line TLE text into dicts with name, norad_id, line1, line2 and epoch."""
    lines = [ln.rstrip() for ln in tle_text.splitlines() if ln.strip()]
    parsed: list[dict] = []
    for i in range(0, len(lines) - 2, 3):
        name, line1, line2 = lines[i].strip(), lines[i + 1].strip(), lines[i + 2].strip()
        if not (line1.startswith("1 ") and line2.startswith("2 ")):
            logger.warning("Skipping malformed TLE block for %r", name)
            continue
        try:
            norad_id = int(line1[2:7])
        except ValueError:
            logger.warning("Skipping TLE with unreadable catalogue number: %r", name)
            continue
        if not (tle_checksum_ok(line1) and tle_checksum_ok(line2)):
            logger.warning("TLE checksum mismatch for %s (NORAD %s); keeping it", name, norad_id)
        parsed.append(
            {
                "name": name,
                "norad_id": norad_id,
                "line1": line1,
                "line2": line2,
                "epoch": parse_tle_epoch(line1),
            }
        )
    return parsed


def _get(params: dict, timeout: float = 30.0) -> str:
    response = requests.get(CELESTRAK_GP_URL, params=params, timeout=timeout, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return response.text


def fetch_group(group: str = "starlink", retries: int = 3, retry_delay: float = 5.0) -> Optional[list[dict]]:
    """Download a CelesTrak group (for example ``starlink``) as parsed TLE dicts."""
    for attempt in range(1, retries + 1):
        try:
            logger.info("Fetching %s TLEs from CelesTrak (attempt %d/%d)", group, attempt, retries)
            tles = parse_tle_text(_get({"GROUP": group, "FORMAT": "tle"}))
            if not tles:
                raise ValueError("CelesTrak returned no parsable TLEs")
            logger.info("Fetched %d %s TLEs", len(tles), group)
            return tles
        except (requests.RequestException, ValueError) as exc:
            logger.error("TLE fetch failed (attempt %d): %s", attempt, exc)
            if attempt < retries:
                time.sleep(retry_delay)
    return None


def fetch_tle_by_catnr(norad_id: int) -> Optional[TLE]:
    """Current TLE for one catalogue number, cached for six hours. None if unavailable."""
    key = f"tle:{norad_id}"
    cached = get_cached(key)
    if cached:
        return TLE(**cached)
    try:
        parsed = parse_tle_text(_get({"CATNR": norad_id, "FORMAT": "tle"}, timeout=15.0))
    except requests.RequestException as exc:
        logger.warning("Could not fetch TLE for NORAD %s: %s", norad_id, exc)
        return None
    if not parsed:
        logger.warning("CelesTrak has no TLE for NORAD %s", norad_id)
        return None
    row = parsed[0]
    tle = TLE(norad_id=row["norad_id"], name=row["name"], line1=row["line1"], line2=row["line2"])
    cache_custom(key, asdict(tle), expiry=EO_TLE_CACHE_SECONDS)
    return tle


class TLEFetcher:
    """Fetches the Starlink catalogue and upserts it into the ``satellites`` table."""

    def __init__(self, db: Session):
        self.db = db

    def fetch_starlink_tles(self) -> Optional[list[dict]]:
        return fetch_group("starlink")

    def update_database(self, tles: list[dict]) -> int:
        """Insert new satellites and refresh existing ones in a single transaction."""
        existing = {sat.norad_id: sat for sat in self.db.query(Satellite).all()}
        now = datetime.now(timezone.utc)
        for tle in tles:
            sat = existing.get(tle["norad_id"])
            if sat is None:
                self.db.add(
                    Satellite(
                        norad_id=tle["norad_id"],
                        name=tle["name"],
                        constellation="STARLINK",
                        tle_line1=tle["line1"],
                        tle_line2=tle["line2"],
                        epoch=tle["epoch"],
                        last_updated=now,
                    )
                )
            else:
                sat.name = tle["name"]
                sat.tle_line1 = tle["line1"]
                sat.tle_line2 = tle["line2"]
                sat.epoch = tle["epoch"]
                sat.last_updated = now
        try:
            self.db.commit()
        except Exception:
            logger.exception("Database commit failed while updating TLEs")
            self.db.rollback()
            return 0
        logger.info("Updated %d satellites", len(tles))
        return len(tles)

    def fetch_and_update(self) -> bool:
        tles = self.fetch_starlink_tles()
        if not tles:
            logger.error("TLE fetch failed; keeping the existing catalogue")
            return False
        return self.update_database(tles) > 0
