"""
Background jobs: periodic TLE refresh and a daily statistics snapshot.
"""
import logging
import os
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

from ..models.database import SessionLocal
from ..models.satellite import HistoricalSnapshot
from ..services.satellite_tracker import SatelliteTracker
from ..services.tle_fetcher import TLEFetcher
from ..utils.cache import invalidate_cache

load_dotenv()

logger = logging.getLogger(__name__)

TLE_UPDATE_INTERVAL_HOURS = int(os.getenv("TLE_UPDATE_INTERVAL_HOURS", "6"))


def update_tle_data() -> bool:
    """Refresh the Starlink catalogue from CelesTrak and drop the position cache."""
    logger.info("Starting scheduled TLE update")
    db = SessionLocal()
    try:
        ok = TLEFetcher(db).fetch_and_update()
        if ok:
            invalidate_cache()
            logger.info("TLE update completed")
        else:
            logger.error("TLE update failed")
        return ok
    except Exception:
        logger.exception("Error in TLE update task")
        return False
    finally:
        db.close()


def create_daily_snapshot() -> None:
    """Store how many satellites sit in each Starlink shell today."""
    logger.info("Creating daily historical snapshot")
    db = SessionLocal()
    try:
        positions = SatelliteTracker(db).get_all_positions()
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        snapshot = db.query(HistoricalSnapshot).filter(HistoricalSnapshot.snapshot_date == today).first()
        if snapshot is None:
            snapshot = HistoricalSnapshot(snapshot_date=today, total_satellites=0)
            db.add(snapshot)
        snapshot.total_satellites = len(positions)
        snapshot.altitude_band_340_360 = sum(1 for p in positions if 340 <= p["alt_km"] <= 360)
        snapshot.altitude_band_500_570 = sum(1 for p in positions if 500 <= p["alt_km"] <= 570)
        snapshot.altitude_band_1100_1325 = sum(1 for p in positions if 1100 <= p["alt_km"] <= 1325)
        db.commit()
        logger.info("Daily snapshot stored: %d satellites", len(positions))
    except Exception:
        logger.exception("Error creating daily snapshot")
        db.rollback()
    finally:
        db.close()


def setup_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        update_tle_data,
        trigger=IntervalTrigger(hours=TLE_UPDATE_INTERVAL_HOURS),
        id="tle_update",
        name="Update TLE data from CelesTrak",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(timezone.utc),  # run once immediately on startup
    )
    scheduler.add_job(
        create_daily_snapshot,
        trigger=CronTrigger(hour=0, minute=0, timezone="UTC"),
        id="daily_snapshot",
        name="Create daily historical snapshot",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("Scheduler configured: TLE refresh every %dh, snapshot daily at 00:00 UTC", TLE_UPDATE_INTERVAL_HOURS)
    return scheduler
